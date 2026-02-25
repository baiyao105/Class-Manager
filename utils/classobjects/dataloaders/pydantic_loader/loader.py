"""
Pydantic模型加载器。

提供基于Pydantic的高效数据加载和缓存机制。

核心设计：
1. 单例模式：全局唯一的加载器实例
2. 多级缓存：模型缓存 + 对象缓存
3. 批量操作：事务批处理提高性能
4. 引用解析：自动解析对象间引用

存储格式：
- 每个类型一个数据库文件（{type_name}.db）
- 每个数据库分16个表（datas_0 到 datas_f），按UUID首字符分片
- 表结构：uuid (主键), class (类型名), data (JSON字符串), updated_at (时间戳)
- 历史记录存储在 Histories/{uuid[:2]}/{uuid[2:]}/ 目录下
- 当前存档存储在 Current/ 目录下
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
import threading
import time
from collections import OrderedDict
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterator, Sequence, TypeVar, cast
from uuid import UUID

from pydantic import BaseModel

from utils.basetypes import Base
from ...basetype import ClassDataType, ClassDataTypeUUID
from ...classdataloader import ClassDataLoader, UserDataBase
from ...objects.history import History
from . import PydanticModelBase
from ...datachunk import DataChunk

T = TypeVar("T", bound=ClassDataType)


class PydanticLoaderError(RuntimeError):
    "Pydantic加载器错误"


class ModelNotFoundError(PydanticLoaderError):
    "模型未找到"


class DataNotFoundError(PydanticLoaderError):
    "数据不存在"


class PydanticLoader(DataChunk):
    """
    Pydantic模型加载器。

    提供数据加载、缓存、保存的完整功能。
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

    bound_db: UserDataBase
    "绑定的数据库对象"

    _batch_mode: bool = False
    "批量模式标志"

    _pending_saves: list[tuple[str, UUID, str, str]] = []
    "待保存的数据列表，(type_name, uuid, class_name, json_data)"

    def __new__(cls) -> PydanticLoader:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.bound_db = UserDataBase()
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
        from ...objects.datatag import DataTag
        from ...objects.student import Student
        from ...objects.scoremodtemplate import ScoreModificationTemplate
        from ...objects.scoremod import ScoreModification
        from ...objects.group import Group
        from ...objects.classtype import Class
        from ...objects.achievementtemp import AchievementTemplate
        from ...objects.achievement import Achievement
        from ...objects.attendanceinfo import AttendanceInfo
        from ...objects.dayrecord import DayRecord
        from ...objects.history import History
        from ...objects.homeworkrule import HomeworkRule

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
        if self.current_path != path:
            self.close_connections()
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
                obj = self._load_from_db(uuid, type, history_uuid, path)
                self.loaded_objects[cache_key] = obj
                return obj
            except DataNotFoundError:
                Base.log("W", f"数据不存在: {type_name}({uuid})", "PydanticLoader._load_object")
                dummy = type.new_dummy()
                dummy.uuid = uuid
                dummy.archive_uuid = history_uuid
                self.loaded_objects[cache_key] = dummy
                return dummy
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

    def _load_from_db(
        self,
        uuid: ClassDataTypeUUID[T],
        data_type: type[T],
        history_uuid: ClassDataTypeUUID[History] | None,
        path: str
    ) -> T:
        """
        从数据库加载对象。

        :param uuid: 对象UUID
        :param data_type: 对象类型
        :param history_uuid: 历史记录UUID
        :param path: 数据路径
        :return: 加载的对象
        :raise DataNotFoundError: 数据不存在
        """
        type_name = data_type.chunk_type_name
        cache_key = (history_uuid, type_name, uuid)

        conn = self._get_connection(history_uuid, type_name, path)
        result = conn.execute(
            f"SELECT data FROM datas_{str(uuid)[:1]} WHERE uuid = ?",
            (str(uuid),)
        ).fetchone()

        if result is None:
            raise DataNotFoundError(f"数据不存在: {type_name}({uuid})")

        model_cls = self.model_registry.get(type_name)
        if model_cls is None:
            raise ModelNotFoundError(f"未注册的模型类型: {type_name}")

        json_data = json.loads(result[0])
        model = model_cls.model_validate(json_data)
        self.loaded_models[cache_key] = model

        obj = model.to_class_data()
        return cast(T, obj)

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
            os.makedirs(path, exist_ok=True)
            db_path = os.path.join(path, f"{type_name}.db")
            conn = sqlite3.connect(db_path, check_same_thread=False)
            self._init_database(conn)
            self.database_connections[cache_key] = conn
        return self.database_connections[cache_key]

    def _init_database(self, conn: sqlite3.Connection) -> None:
        """
        初始化数据库表结构。

        :param conn: 数据库连接
        """
        for i in range(16):
            prefix = f"{i:01x}"
            conn.execute(
                f"""CREATE TABLE IF NOT EXISTS datas_{prefix} (
                    uuid       text     primary key,
                    class      text     not null,
                    data       text     not null,
                    updated_at real
                )"""
            )
            conn.execute(
                f"""CREATE INDEX IF NOT EXISTS idx_{prefix}_class 
                    ON datas_{prefix}(class)"""
            )
            conn.execute(
                f"""CREATE INDEX IF NOT EXISTS idx_{prefix}_updated 
                    ON datas_{prefix}(updated_at)"""
            )
        conn.commit()

    @contextmanager
    def batch_mode(self) -> Iterator[None]:
        """
        批量模式上下文管理器。

        在批量模式下，所有保存操作会延迟到上下文退出时统一提交。

        用法：
            with loader.batch_mode():
                for obj in objects:
                    loader.save_object(obj)
        """
        self._batch_mode = True
        self._pending_saves.clear()
        try:
            yield
            self._flush_pending_saves()
        finally:
            self._batch_mode = False
            self._pending_saves.clear()

    def clear_pending_saves(self) -> None:
        """
        清除待保存的数据和批量模式状态。
        """
        self._pending_saves.clear()
        self._batch_mode = False

    def _flush_pending_saves(self) -> None:
        """
        刷新待保存的数据到数据库。

        按类型分组，使用事务批量提交。
        """
        if not self._pending_saves:
            return

        grouped: dict[str, list[tuple[UUID, str, str]]] = {}
        for type_name, uuid, class_name, json_data in self._pending_saves:
            if type_name not in grouped:
                grouped[type_name] = []
            grouped[type_name].append((uuid, class_name, json_data))

        path = self.get_current_save_dir()
        history_uuid = self.operating_history_uuid

        for type_name, items in grouped.items():
            conn = self._get_connection(history_uuid, type_name, path)
            try:
                for uuid, class_name, json_data in items:
                    self._save_to_conn(conn, uuid, type_name, json_data)
                conn.commit()
            except sqlite3.Error as e:
                conn.rollback()
                raise PydanticLoaderError(f"批量保存失败: {type_name}") from e

        self._pending_saves.clear()

    def _save_to_conn(
        self,
        conn: sqlite3.Connection,
        uuid: UUID,
        type_name: str,
        json_data: str
    ) -> None:
        """
        保存数据到数据库连接。

        :param conn: 数据库连接
        :param uuid: 对象UUID
        :param type_name: 类型名称
        :param json_data: JSON数据
        """
        uuid_str = str(uuid)
        table = f"datas_{uuid_str[:1]}"
        now = time.time()

        existing = conn.execute(
            f"SELECT class FROM {table} WHERE uuid = ?",
            (uuid_str,)
        ).fetchone()

        if existing:
            if existing[0] != type_name:
                raise PydanticLoaderError(
                    f"UUID冲突: {uuid_str} 已存在类型 {existing[0]}，"
                    f"无法保存为 {type_name}"
                )
            conn.execute(
                f"UPDATE {table} SET data = ?, updated_at = ? WHERE uuid = ?",
                (json_data, now, uuid_str)
            )
        else:
            conn.execute(
                f"INSERT INTO {table} (uuid, class, data, updated_at) VALUES (?, ?, ?, ?)",
                (uuid_str, type_name, json_data, now)
            )

    def save_object(self, obj: ClassDataType, path: str | None = None) -> None:
        """
        保存对象到数据库。

        :param obj: 要保存的对象
        :param path: 保存路径，None使用当前路径
        """
        type_name = obj.chunk_type_name
        uuid = obj.uuid

        if isinstance(obj, History) and obj.uuid is None:
                raise PydanticLoaderError("无法保存uuid为None的历史记录")

        model_cls = self.model_registry.get(type_name)
        if model_cls is None:
            raise ModelNotFoundError(f"未注册的模型类型: {type_name}")

        model = obj.to_pydantic()
        json_data = json.dumps(model.model_dump(mode="json"), ensure_ascii=False)

        if self._batch_mode:
            self._pending_saves.append((type_name, uuid, type_name, json_data))
            return

        save_path = path or self.get_current_save_dir()
        history_uuid = self.operating_history_uuid

        conn = self._get_connection(history_uuid, type_name, save_path)
        self._save_to_conn(conn, uuid, type_name, json_data)
        conn.commit()

    def save_objects(self, objects: Sequence[ClassDataType]) -> None:
        """
        批量保存对象到数据库。

        使用事务批量提交，提高性能。

        :param objects: 要保存的对象列表
        """
        with self.batch_mode():
            for obj in objects:
                self.save_object(obj)

    def load_object(
        self,
        uuid: ClassDataTypeUUID[T],
        data_type: type[T],
        history_uuid: ClassDataTypeUUID[History] | None = None
    ) -> T:
        """
        加载单个对象。

        :param uuid: 对象UUID
        :param data_type: 对象类型
        :param history_uuid: 历史记录UUID
        :return: 加载的对象
        """
        cache_key = (history_uuid, data_type.chunk_type_name, uuid)

        if cache_key in self.loaded_objects:
            return cast(T, self.loaded_objects[cache_key])

        path = self.get_current_save_dir() if history_uuid is None else \
            os.path.join(self.current_path, "Histories", history_uuid[:2], history_uuid[2:])

        if history_uuid != self.operating_history_uuid:
            self.set_uuid_loader(history_uuid)

        return self._load_from_db(uuid, data_type, history_uuid, path)

    def load_all_of_type(
        self,
        data_type: type[T],
        history_uuid: ClassDataTypeUUID[History] | None = None
    ) -> list[T]:
        """
        加载指定类型的所有对象。

        :param data_type: 对象类型
        :param history_uuid: 历史记录UUID
        :return: 对象列表
        """
        type_name = data_type.chunk_type_name
        path = self.get_current_save_dir() if history_uuid is None else \
            os.path.join(self.current_path, "Histories", history_uuid[:2], history_uuid[2:])

        conn = self._get_connection(history_uuid, type_name, path)
        results: list[T] = []

        for i in range(16):
            table = f"datas_{i:01x}"
            for row in conn.execute(f"SELECT uuid, data FROM {table} WHERE class = ?", (type_name,)):
                uuid = ClassDataTypeUUID(data_type, UUID(row[0]))
                cache_key = (history_uuid, type_name, uuid)

                if cache_key in self.loaded_objects:
                    results.append(cast(T, self.loaded_objects[cache_key]))
                    continue

                json_data = json.loads(row[1])
                model_cls = self.model_registry.get(type_name)
                if model_cls is None:
                    continue

                model = model_cls.model_validate(json_data)
                self.loaded_models[cache_key] = model

                obj = model.to_class_data()
                self.loaded_objects[cache_key] = obj
                results.append(cast(T, obj))

        return results

    def delete_object(
        self,
        uuid: UUID,
        data_type: type[ClassDataType],
        history_uuid: ClassDataTypeUUID[History] | None = None
    ) -> bool:
        """
        删除对象。

        :param uuid: 对象UUID
        :param data_type: 对象类型
        :param history_uuid: 历史记录UUID
        :return: 是否成功删除
        """
        type_name = data_type.chunk_type_name
        path = self.get_current_save_dir() if history_uuid is None else \
            os.path.join(self.current_path, "Histories", history_uuid[:2], history_uuid[2:])

        conn = self._get_connection(history_uuid, type_name, path)
        uuid_str = str(uuid)
        table = f"datas_{uuid_str[:1]}"

        cursor = conn.execute(f"DELETE FROM {table} WHERE uuid = ?", (uuid_str,))
        conn.commit()

        cache_key = (history_uuid, type_name, uuid)
        self.loaded_objects.pop(cache_key, None)
        self.loaded_models.pop(cache_key, None)

        return cursor.rowcount > 0

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

    def load_history(
        self,
        history_uuid: ClassDataTypeUUID[History] | None = None,
    ) -> History:
        """
        加载历史记录。

        :param history_uuid: 历史记录UUID，None表示当前存档
        :return: 历史记录对象
        """
        from ...objects import Class, DayRecord, History

        if history_uuid is None:
            path = os.path.join(self.current_path, "Current")
        else:
            path = os.path.join(self.current_path, "Histories", str(history_uuid)[:2], str(history_uuid)[2:])

        if not os.path.isdir(path):
            if history_uuid is None:
                os.makedirs(path, exist_ok=True)
                history = History({}, {})
                return history
            raise FileNotFoundError(f"历史记录不存在: {path}")

        self.set_uuid_loader(history_uuid)

        info_file = os.path.join(path, "info.json")
        classes_file = os.path.join(path, "classes.json")
        weekdays_file = os.path.join(path, "weekdays.json")

        if not all(os.path.isfile(f) for f in [info_file, classes_file, weekdays_file]):
            if history_uuid is None:
                history = History({}, {})
                return history
            raise FileNotFoundError(f"历史记录文件不完整: {path}")

        try:
            info = json.load(open(info_file, encoding="utf-8"))
            class_uuids: list[tuple[str, str]] = json.load(open(classes_file, encoding="utf-8"))
            weekday_uuids: dict[str, dict[str, str]] = json.load(open(weekdays_file, encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            if history_uuid is None:
                history = History({}, {})
                return history
            raise FileNotFoundError(f"历史记录文件损坏: {path}") from e

        classes: dict[str, Class] = {}
        for _, class_uuid_str in class_uuids:
            class_uuid = ClassDataTypeUUID(Class, UUID(class_uuid_str))
            _class = self.load_object(class_uuid, Class)
            if _class:
                classes[_class.key] = _class

        weekdays: dict[str, dict[float, DayRecord]] = {}
        for target_class, items in weekday_uuids.items():
            weekdays[target_class] = {}
            for time_key, weekday_uuid_str in items.items():
                weekday_uuid = ClassDataTypeUUID(DayRecord, UUID(weekday_uuid_str))
                weekday = self.load_object(weekday_uuid, DayRecord)
                if weekday:
                    weekdays[target_class][float(time_key)] = weekday

        history = History(
            classes,
            weekdays,
            info.get("create_time", info.get("time")),
        )
        if history_uuid:
            history.uuid = history_uuid
            history.archive_uuid = history_uuid

        return history

    def create_history(self) -> ClassDataTypeUUID[History]:
        """
        创建历史记录存档。

        :return: 新创建的历史记录UUID
        """
        history = History(self.bound_db.classes, self.bound_db.weekday_record)
        if history.uuid is None:
            raise PydanticLoaderError("历史记录UUID不能为None")

        history_path = os.path.join(
            self.current_path,
            "Histories",
            str(history.uuid)[:2],
            str(history.uuid)[2:]
        )
        os.makedirs(history_path, exist_ok=True)

        info = {
            "uuid": str(history.uuid),
            "time": history.time,
            "created_at": datetime.now().isoformat(),
            "python_version": [
                __import__("sys").version_info.major,
                __import__("sys").version_info.minor,
                __import__("sys").version_info.micro,
            ]
        }
        with open(os.path.join(history_path, "info.json"), "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        old_history_uuid = self.operating_history_uuid
        self.operating_history_uuid = history.uuid

        try:
            self.save_object(history)
        finally:
            self.operating_history_uuid = old_history_uuid

        return history.uuid

    def list_histories(self) -> list[ClassDataTypeUUID[History]]:
        """
        列出所有历史记录。

        :return: 历史记录UUID列表
        """
        histories_dir = os.path.join(self.current_path, "Histories")
        if not os.path.isdir(histories_dir):
            return []

        results: list[ClassDataTypeUUID[History]] = []
        for prefix_dir in os.listdir(histories_dir):
            prefix_path = os.path.join(histories_dir, prefix_dir)
            if not os.path.isdir(prefix_path) or len(prefix_dir) != 2:
                continue

            for history_dir in os.listdir(prefix_path):
                history_path = os.path.join(prefix_path, history_dir)
                info_path = os.path.join(history_path, "info.json")
                if not os.path.isdir(history_path):
                    continue

                if os.path.isfile(info_path):
                    try:
                        with open(info_path, encoding="utf-8") as f:
                            info = json.load(f)
                        uuid_str = info.get("uuid", prefix_dir + history_dir)
                        results.append(ClassDataTypeUUID(History, UUID(uuid_str)))
                    except (json.JSONDecodeError, OSError, ValueError):
                        try:
                            results.append(ClassDataTypeUUID(History, UUID(prefix_dir + history_dir)))
                        except ValueError:
                            continue

        return results

    def del_history(self, history_uuid: ClassDataTypeUUID[History]) -> bool:
        """
        删除历史记录。

        :param history_uuid: 要删除的历史记录UUID
        :return: 是否删除成功
        """
        try:
            history_path = os.path.join(
                self.current_path,
                "Histories",
                str(history_uuid)[:2],
                str(history_uuid)[2:]
            )
            shutil.rmtree(history_path)
            return True
        except OSError:
            return False

    @staticmethod
    def get_chunk(path: str, database: UserDataBase) -> PydanticLoader:
        """
        获取Chunk对象。

        :param path: 数据存储路径
        :param database: 绑定的数据库对象
        :return: PydanticLoader实例
        """
        loader = PydanticLoader.get_instance()
        loader.set_path(path)
        loader.register_models()
        loader.bound_db = database
        return loader

    def load_data(self, load_all: bool = False) -> UserDataBase:
        """
        加载数据。

        :param load_all: 是否加载所有历史记录
        :return: 加载的数据库对象
        """
        from ...objects import (
            AchievementTemplate,
            AttendanceInfo,
            ScoreModificationTemplate,
        )
        from ...classdataloader import UserDataBase

        self.set_uuid_loader(None)

        current_record = self.load_history(None)

        current_path = os.path.join(self.current_path, "Current")
        
        templates: list[ScoreModificationTemplate] = []
        achievements: list[AchievementTemplate] = []
        current_day_attendance: dict[str, AttendanceInfo] = {}

        templates_file = os.path.join(current_path, "templates.json")
        if os.path.isfile(templates_file):
            template_uuids: list[tuple[str, ClassDataTypeUUID[ScoreModificationTemplate]]] = json.load(
                open(templates_file, encoding="utf-8")
            )
            for _, template_uuid in template_uuids:
                template = self.load_object(template_uuid, ScoreModificationTemplate)
                if template:
                    templates.append(template)
        else:
            Base.log("W", "当前模板记录文件不存在", "PydanticLoader.load_data")

        achievements_file = os.path.join(current_path, "achievements.json")
        if os.path.isfile(achievements_file):
            achievement_uuids: list[tuple[str, ClassDataTypeUUID[AchievementTemplate]]] = json.load(
                open(achievements_file, encoding="utf-8")
            )
            for _, achievement_uuid in achievement_uuids:
                achievement = self.load_object(achievement_uuid, AchievementTemplate)
                if achievement:
                    achievements.append(achievement)
        else:
            Base.log("W", "当前成就记录文件不存在", "PydanticLoader.load_data")

        attendance_file = os.path.join(current_path, "current_day_attendance.json")
        if os.path.isfile(attendance_file):
            current_day_attendance_uuids: list[tuple[str, ClassDataTypeUUID[AttendanceInfo]]] = json.load(
                open(attendance_file, encoding="utf-8")
            )
            for target_class, attendance_uuid in current_day_attendance_uuids:
                attendance = self.load_object(attendance_uuid, AttendanceInfo)
                if attendance:
                    current_day_attendance[target_class] = attendance
        else:
            Base.log("W", "当前日出勤记录文件不存在", "PydanticLoader.load_data")

        info_file = os.path.join(self.current_path, "info.json")
        if os.path.isfile(info_file):
            info = json.load(open(info_file, encoding="utf-8"))
        else:
            raise FileNotFoundError(f"信息文件不存在: {info_file}")

        histories: dict[float, History] = {}
        if load_all:
            for history_uuid_str in info.get("histories", []):
                try:
                    history_uuid = ClassDataTypeUUID(History, UUID(history_uuid_str))
                    h = self.load_history(history_uuid)
                    while h.time in histories:
                        h.time += 0.000001
                    histories[h.time] = h
                except Exception as e:
                    Base.log_exc(f"历史记录{history_uuid_str}加载失败，将跳过", "PydanticLoader.load_data", "W", e)
                    continue

            histories = dict(sorted(histories.items(), key=lambda i: i[0]))

        return UserDataBase(
            info["user"],
            info["save_time"],
            info["version"],
            info["version_code"],
            info["last_reset"],
            histories,
            current_record.classes,
            OrderedDict({t.key: t for t in templates}),
            {a.key: a for a in achievements},
            info["last_start_time"],
            current_record.weekdays,
            current_day_attendance,
        )

    def save_data(
        self,
        save_history: bool = True,
        save_only_if_not_exist: bool = True,
        clear_current: bool = False,
        clear_histories: bool = False,
    ) -> None:
        """
        保存数据。

        :param save_history: 是否保存历史记录
        :param save_only_if_not_exist: 是否只保存不存在的数据
        :param clear_current: 是否清理当前数据
        :param clear_histories: 是否清理历史数据
        """
        from ...datachunk import DataChunk

        DataChunk.reset_progress()

        if clear_histories:
            shutil.rmtree(self.current_path, ignore_errors=True)

        os.makedirs(self.current_path, exist_ok=True)
        os.makedirs(os.path.join(self.current_path, "Histories"), exist_ok=True)

        history = History(self.bound_db.classes, self.bound_db.weekday_record)
        save_tasks: list[tuple[ClassDataTypeUUID[History] | None, History, bool]] = [
            (None, history, clear_current)
        ]

        if save_history:
            for v in self.bound_db.history_data.values():
                if v.uuid is None:
                    continue
                history_path = os.path.join(
                    self.current_path,
                    "Histories",
                    str(v.uuid)[:2],
                    str(v.uuid)[2:],
                    "info.json"
                )
                if save_only_if_not_exist and os.path.isfile(history_path):
                    continue
                os.makedirs(
                    os.path.join(self.current_path, "Histories", str(v.uuid)[:2], str(v.uuid)[2:]),
                    exist_ok=True
                )
                save_tasks.append((v.uuid, v, clear_histories))

        total_history_count = len(save_tasks)
        history_percentage = 100 / max(1, total_history_count)

        for index, (history_uuid, current_history, clear) in enumerate(save_tasks):
            self._save_history_part(history_uuid, current_history, clear, index, total_history_count, history_percentage)

        self._save_main_info()

    def _save_history_part(
        self,
        history_uuid: ClassDataTypeUUID[History] | None,
        current_history: History,
        clear: bool,
        index: int,
        total_count: int,
        history_percentage: float,
    ) -> None:
        """
        保存历史记录的一部分。

        :param history_uuid: 历史记录UUID
        :param current_history: 历史记录对象
        :param clear: 是否清理
        :param index: 当前索引
        :param total_count: 总数
        :param history_percentage: 进度百分比
        """
        from ...objects import (
            Achievement,
            AchievementTemplate,
            Class,
            DayRecord,
            Group,
            ScoreModification,
            ScoreModificationTemplate,
            Student,
        )

        DataChunk.update_progress(stage=f"保存历史记录（{index + 1}/{total_count}）")

        if history_uuid:
            path = os.path.join(self.current_path, "Histories", str(history_uuid)[:2], str(history_uuid)[2:])
        else:
            path = os.path.join(self.current_path, "Current")

        if clear:
            shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path, exist_ok=True)

        modify_templates: list[ScoreModificationTemplate] = list(self.bound_db.templates.values())
        day_records: list[DayRecord] = []
        achievement_templates: list[AchievementTemplate] = list(self.bound_db.achievements.values())

        for c, records in current_history.weekdays.items():
            for r in records.values():
                day_records.append(r)

        students: list[Student] = []
        modifies: list[ScoreModification] = []
        achievements: list[Achievement] = []
        groups: list[Group] = []
        classes: list[Class] = []

        for _class in current_history.classes.values():
            for homework_rule in _class.homework_rules:
                for template in homework_rule.rule_mapping.values():
                    modify_templates.append(template)
            classes.append(_class)
            for student in _class.students.values():
                students.append(student)
                modifies.extend(student.history.values())
                achievements.extend(student.achievements.values())
            groups.extend(_class.groups.values())

        total_objects = (
            len(classes) + len(students) + len(groups) + len(modifies) +
            len(achievements) + len(modify_templates) + len(day_records) +
            len(achievement_templates) + len(self.bound_db.current_day_attendance)
        )
        object_percentage = history_percentage / max(total_objects, 1)

        old_history_uuid = self.operating_history_uuid
        self.operating_history_uuid = history_uuid

        try:
            with self.batch_mode():
                self._save_objects_batch(classes, "班级信息", object_percentage)
                self._save_objects_batch(students, "学生信息", object_percentage)
                self._save_objects_batch(groups, "小组信息", object_percentage)
                self._save_objects_batch(modifies, "分数修改记录", object_percentage)
                self._save_objects_batch(achievements, "成就记录", object_percentage)
                self._save_objects_batch(modify_templates, "分数修改模板", object_percentage)
                self._save_objects_batch(achievement_templates, "成就模板", object_percentage)
                self._save_objects_batch(day_records, "每日记录", object_percentage)
                self._save_objects_batch(list(self.bound_db.current_day_attendance.values()), "当前出勤", object_percentage)
        finally:
            self.operating_history_uuid = old_history_uuid

        info = {
            "uuid": str(history_uuid) if history_uuid else None,
            "create_time": current_history.time,
            "save_time": self.bound_db.save_time,
            "python_version": [sys.version_info.major, sys.version_info.minor, sys.version_info.micro],
        }
        with open(os.path.join(path, "info.json"), "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        class_uuids = [(c.key, str(c.uuid)) for c in classes]
        with open(os.path.join(path, "classes.json"), "w", encoding="utf-8") as f:
            json.dump(class_uuids, f, ensure_ascii=False, indent=2)

        weekday_uuids: dict[str, dict[str, str]] = {}
        for c, records in current_history.weekdays.items():
            weekday_uuids[c] = {str(k): str(v.uuid) for k, v in records.items()}
        with open(os.path.join(path, "weekdays.json"), "w", encoding="utf-8") as f:
            json.dump(weekday_uuids, f, ensure_ascii=False, indent=2)

    def _save_objects_batch(
        self,
        objects: Sequence[ClassDataType],
        name: str,
        percentage: float,
    ) -> None:
        """
        批量保存对象。

        :param objects: 对象列表
        :param name: 对象类型名称
        :param percentage: 进度百分比
        """
        from ...datachunk import DataChunk

        total = len(objects)
        DataChunk.update_progress(
            obj_name=name,
            total=total,
        )

        for i, obj in enumerate(objects):
            DataChunk.update_progress(current=i + 1)
            self.save_object(obj)

    def _save_main_info(self) -> None:
        """
        保存主信息文件。
        """
        info = {
            "user": self.bound_db.user,
            "save_time": self.bound_db.save_time,
            "version": self.bound_db.version,
            "version_code": self.bound_db.version_code,
            "last_reset": self.bound_db.last_reset,
            "last_start_time": self.bound_db.last_start_time,
            "histories": [str(h) for h in self.list_histories()],
            "python_version": [sys.version_info.major, sys.version_info.minor, sys.version_info.micro],
        }
        with open(os.path.join(self.current_path, "info.json"), "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        template_uuids = [(t.key, str(t.uuid)) for t in self.bound_db.templates.values()]
        with open(os.path.join(self.current_path, "Current", "templates.json"), "w", encoding="utf-8") as f:
            json.dump(template_uuids, f, ensure_ascii=False, indent=2)

        achievement_uuids = [(a.key, str(a.uuid)) for a in self.bound_db.achievements.values()]
        with open(os.path.join(self.current_path, "Current", "achievements.json"), "w", encoding="utf-8") as f:
            json.dump(achievement_uuids, f, ensure_ascii=False, indent=2)

        attendance_uuids = [(c, str(a.uuid)) for c, a in self.bound_db.current_day_attendance.items()]
        with open(os.path.join(self.current_path, "Current", "current_day_attendance.json"), "w", encoding="utf-8") as f:
            json.dump(attendance_uuids, f, ensure_ascii=False, indent=2)

    @staticmethod
    def commit_changes(clear_dataobj_connections: bool = True) -> None:
        """
        提交所有更改并释放连接。

        :param clear_dataobj_connections: 是否同时清理DataObject的连接（兼容旧接口，暂未使用）
        """
        loader = PydanticLoader.get_instance()
        loader.close_connections()
        loader.clear_cache()

    def get_stats(self) -> dict[str, Any]:
        """
        获取加载器统计信息。

        :return: 统计信息字典
        """
        return {
            "loaded_models": len(self.loaded_models),
            "loaded_objects": len(self.loaded_objects),
            "loading_set": len(self.loading_set),
            "database_connections": len(self.database_connections),
            "registered_models": len(self.model_registry),
            "batch_mode": self._batch_mode,
            "pending_saves": len(self._pending_saves),
        }


def get_loader() -> PydanticLoader:
    """
    获取全局加载器实例。

    :return: PydanticLoader实例
    """
    return PydanticLoader.get_instance()


def clear_cache() -> None:
    "清空全局缓存。"
    get_loader().clear_cache()


__all__ = [
    "PydanticLoader",
    "PydanticLoaderError",
    "ModelNotFoundError",
    "DataNotFoundError",
    "get_loader",
    "clear_cache",
]
