"""
Pydantic模型加载器。

参考现有 dataloader.py 的设计，提供基于 Pydantic 的数据加载和缓存机制。

核心设计：
1. PydanticLoader.loaded_model_list: 全局缓存，类似 DataObject.loaded_object_list
2. set_uuid_loader(): 设置加载回调，类似 Chunk.set_uuid_loader()
3. 加载流程: JSON → Pydantic Model → ClassDataType
4. 保存流程: ClassDataType → Pydantic Model → JSON
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from typing import Any, TypeVar, cast
from uuid import UUID

from pydantic import BaseModel

from utils.basetypes import Base
from utils.classobjects.pydantic_loader import PydanticModelBase
from ..classdataloader import ClassDataLoader

from ..basetype import ClassDataType, ClassDataTypeUUID
from ..objects.history import History


T = TypeVar("T", bound=ClassDataType)


class PydanticLoaderError(RuntimeError):
    "Pydantic加载器错误"


class ModelNotFoundError(PydanticLoaderError):
    "模型未找到"


class PydanticLoader:
    """
    Pydantic模型加载器。

    类似于 DataObject + Chunk 的组合，提供：
    1. 全局模型缓存
    2. 数据库连接管理
    3. UUID加载回调设置
    4. 加载/保存操作
    """

    _instance: PydanticLoader | None = None
    _lock = threading.Lock()

    loaded_models: dict[
        tuple[ClassDataTypeUUID[History] | None, str, UUID],
        BaseModel
    ] = {}
    "已加载的模型缓存，key=(history_uuid, type_name, uuid)"

    loaded_objects: dict[
        tuple[ClassDataTypeUUID[History] | None, str, UUID],
        ClassDataType
    ] = {}
    "已加载的对象缓存，key=(history_uuid, type_name, uuid)"

    loading_set: set[tuple[ClassDataTypeUUID[History] | None, str, UUID]] = set()
    "正在加载的模型UUID集合，用于防止循环引用"

    database_connections: dict[
        tuple[ClassDataTypeUUID[History] | None, str],
        sqlite3.Connection
    ] = {}
    "数据库连接池"

    model_registry: dict[str, type[PydanticModelBase[Any]]] = {}
    "模型类型注册表，type_name -> ModelClass"

    type_registry: dict[str, type[ClassDataType]] = {}
    "数据类型注册表，type_name -> ClassDataType"

    operating_history_uuid: ClassDataTypeUUID[History] | None = None
    "当前操作的存档UUID，None表示当前存档"

    current_path: str = ""
    "当前数据路径"

    def __new__(cls) -> PydanticLoader:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @classmethod
    def get_instance(cls) -> PydanticLoader:
        "获取单例实例。"
        return cls()

    def register_models(self) -> None:
        """
        注册所有Pydantic模型类型。

        建立类型名称与模型类的映射关系。
        """
        from ..objects.datatag import DataTag
        from ..objects.student import Student
        from ..objects.scoremodtemplate import ScoreModificationTemplate
        from ..objects.scoremod import ScoreModification
        from ..objects.group import Group
        from ..objects.classtype import Class
        from ..objects.achievementtemp import AchievementTemplate
        from ..objects.achievement import Achievement
        from ..objects.attendanceinfo import AttendanceInfo
        from ..objects.dayrecord import DayRecord
        from ..objects.history import History
        from ..objects.homeworkrule import HomeworkRule

        from .models import (
            DataTagModel,
            StudentModel,
            ScoreTemplateModel,
            ScoreModificationModel,
            GroupModel,
            ClassModel,
            AchievementTemplateModel,
            AchievementModel,
            AttendanceInfoModel,
            DayRecordModel,
            HistoryModel,
            HomeworkRuleModel
        )
        from .base import register_type

        model_mapping = {
            DataTag: DataTagModel,
            Student: StudentModel,
            ScoreModificationTemplate: ScoreTemplateModel,
            ScoreModification: ScoreModificationModel,
            Group: GroupModel,
            Class: ClassModel,
            AchievementTemplate: AchievementTemplateModel,
            Achievement: AchievementModel,
            AttendanceInfo: AttendanceInfoModel,
            DayRecord: DayRecordModel,
            History: HistoryModel,
            HomeworkRule: HomeworkRuleModel
        }

        for obj_type, model_cls in model_mapping.items():
            self.model_registry[obj_type.chunk_type_name] = model_cls
            self.type_registry[obj_type.chunk_type_name] = obj_type
            register_type(obj_type)

    def set_path(self, path: str) -> None:
        """
        设置数据存储路径。

        :param path: 数据路径
        """
        self.current_path = path

    def get_current_save_dir(self) -> str:
        """
        获取当前操作的保存目录。

        :return: 保存目录路径
        """
        history_uuid = self.operating_history_uuid
        if history_uuid is None:
            return os.path.join(self.current_path, "Current")
        else:
            return os.path.join(self.current_path, "Histories", history_uuid[:2], history_uuid[2:])

    def set_uuid_loader(self, history_uuid: ClassDataTypeUUID[History] | None = None) -> None:
        """
        设置UUID加载回调。

        类似于 Chunk.set_uuid_loader()，设置 ClassDataLoader.LoadUUID 回调。

        :param history_uuid: 历史记录UUID，None表示当前存档
        """
        self.operating_history_uuid = history_uuid
        path = self.get_current_save_dir()

        def _load_object(
            uuid: ClassDataTypeUUID[T] | None,
            type: type[T],
        ) -> T | None:
            """
            加载对象。

            :param uuid: 对象UUID
            :param type: 对象类型
            :return: 加载的对象或None
            """
            if uuid is None:
                Base.log("W", "加载时遇到uuid为None，返回None", "PydanticLoader._load_object")
                return None

            type_name = type.chunk_type_name
            cache_key = (history_uuid, type_name, uuid)

            if cache_key in self.loaded_objects:
                return cast(T, self.loaded_objects[cache_key])

            if cache_key in self.loading_set:
                if cache_key in self.loaded_objects:
                    return cast(T, self.loaded_objects[cache_key])
                return type.new_dummy()

            self.loading_set.add(cache_key)

            try:
                conn = self._get_connection(history_uuid, type_name, path)
                result = conn.execute(
                    f"SELECT data FROM datas_{uuid[:1]} WHERE uuid = ?",
                    (str(uuid),)
                ).fetchone()

                if result is None:
                    Base.log("W", f"数据不存在: {type_name}({uuid})", "PydanticLoader._load_object")
                    dummy = type.new_dummy()
                    dummy.uuid = uuid
                    dummy.archive_uuid = history_uuid
                    self.loaded_objects[cache_key] = dummy
                    return dummy

                model_cls = self.model_registry.get(type_name)
                if model_cls is None:
                    raise ModelNotFoundError(f"未注册的模型类型: {type_name}")

                json_data = json.loads(result[0])
                model = model_cls.model_validate(json_data)
                self.loaded_models[cache_key] = model

                dummy = type.new_dummy()
                self.loaded_objects[cache_key] = dummy

                obj = model.to_class_data()
                self.loaded_objects[cache_key] = obj

                return cast(T, obj)

            except Exception as e:
                Base.log_exc(f"加载对象失败: {type_name}({uuid})", "PydanticLoader._load_object", "E", e)
                dummy = type.new_dummy()
                dummy.uuid = uuid
                dummy.archive_uuid = history_uuid
                self.loaded_objects[cache_key] = dummy
                return dummy

            finally:
                self.loading_set.discard(cache_key)

        ClassDataLoader.LoadUUID = _load_object

    def _get_connection(
        self,
        history_uuid: ClassDataTypeUUID[History] | None,
        type_name: str,
        path: str
    ) -> sqlite3.Connection:
        """
        获取数据库连接。

        :param history_uuid: 历史记录UUID
        :param type_name: 类型名称
        :param path: 数据路径
        :return: 数据库连接
        """
        cache_key = (history_uuid, type_name)
        if cache_key not in self.database_connections:
            db_path = os.path.join(path, f"{type_name}.db")
            conn = sqlite3.connect(db_path, check_same_thread=False)
            self.database_connections[cache_key] = conn
        return self.database_connections[cache_key]

    def save_object(self, obj: ClassDataType, path: str | None = None) -> None:
        """
        保存对象到数据库。

        :param obj: 要保存的对象
        :param path: 保存路径，None使用当前路径
        """
        path = path or self.get_current_save_dir()
        type_name = obj.chunk_type_name
        uuid = obj.uuid

        if isinstance(obj, History) and obj.uuid is None:
            raise PydanticLoaderError("无法保存uuid为None的历史记录")

        model_cls = self.model_registry.get(type_name)
        if model_cls is None:
            raise ModelNotFoundError(f"未注册的模型类型: {type_name}")

        model = obj.to_pydantic()
        json_data = json.dumps(model.model_dump(mode="json"), ensure_ascii=False)

        conn = self._get_connection(self.operating_history_uuid, type_name, path)

        for i in range(16):
            prefix = f"{i:01x}"
            conn.execute(
                f"""CREATE TABLE IF NOT EXISTS datas_{prefix} (
                    uuid   text     primary key,
                    class  text,
                    data   text
                )"""
            )
        conn.commit()

        existing = conn.execute(
            f"SELECT class FROM datas_{uuid[:1]} WHERE uuid = ?",
            (str(uuid),)
        ).fetchone()

        if existing:
            conn.execute(
                f"UPDATE datas_{uuid[:1]} SET class = ?, data = ? WHERE uuid = ?",
                (type_name, json_data, str(uuid))
            )
        else:
            conn.execute(
                f"INSERT INTO datas_{uuid[:1]} (uuid, class, data) VALUES (?, ?, ?)",
                (str(uuid), type_name, json_data)
            )

        conn.commit()

    def clear_cache(self) -> None:
        "清空所有缓存。"
        self.loaded_models.clear()
        self.loaded_objects.clear()
        self.loading_set.clear()

    def close_connections(self) -> None:
        "关闭所有数据库连接。"
        for conn in self.database_connections.values():
            try:
                conn.commit()
                conn.close()
            except sqlite3.Error:
                pass
        self.database_connections.clear()


def get_loader() -> PydanticLoader:
    """
    获取全局加载器实例。

    :return: PydanticLoader实例
    """
    return PydanticLoader.get_instance()


def clear_cache() -> None:
    "清空全局缓存。"
    get_loader().clear_cache()
