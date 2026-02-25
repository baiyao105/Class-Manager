"""
数据存储抽象接口。

提供统一的数据存储和加载接口，支持多种实现（如旧版Chunk和PydanticLoader）。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar

from .basetype import ClassDataType, ClassDataTypeUUID
from .objects.history import History
from .classdataset import UserDataBase

T = TypeVar("T", bound=ClassDataType)


@dataclass
class SaveLoadStat:
    """保存/加载进度信息"""
    history_stage: str = ""
    current_saving_obj_name: str = ""
    current_saving_obj_current: int = 0
    current_saving_obj_total: int = 0
    total_percentage: float = 0.0
    
    def __repr__(self) -> str:
        return f"SaveLoadStat(stage={self.history_stage!r}, obj_name={self.current_saving_obj_name!r}, current={self.current_saving_obj_current}/{self.current_saving_obj_total}, percentage={self.total_percentage})"


_progress_stat: SaveLoadStat = SaveLoadStat()


class DataChunk(ABC):
    """
    数据存储抽象接口。

    提供统一的数据存储和加载接口，支持多种实现。
    """

    @classmethod
    def update_progress(
        cls,
        stage: str | None = None,
        obj_name: str | None = None,
        current: int | None = None,
        total: int | None = None,
        percentage: float | None = None,
    ) -> None:
        """
        更新进度信息。

        只更新显式传递的参数，未传递的参数保持不变。

        :param stage: 当前阶段描述
        :param obj_name: 当前对象类型名称
        :param current: 当前对象索引
        :param total: 当前对象总数
        :param percentage: 总进度百分比（如果为None，则不更新）
        """
        global _progress_stat
        if stage is not None:
            _progress_stat.history_stage = stage
        if obj_name is not None:
            _progress_stat.current_saving_obj_name = obj_name
        if current is not None:
            _progress_stat.current_saving_obj_current = current
        if total is not None:
            _progress_stat.current_saving_obj_total = total
        if percentage is not None:
            _progress_stat.total_percentage = percentage
        

    @classmethod
    def get_progress(cls) -> SaveLoadStat:
        """
        获取当前进度信息。

        :return: 当前进度信息
        """
        global _progress_stat
        return _progress_stat

    @classmethod
    def reset_progress(cls) -> None:
        """
        重置进度信息。
        """
        global _progress_stat
        _progress_stat = SaveLoadStat()

    @staticmethod
    @abstractmethod
    def get_chunk(path: str, database: UserDataBase) -> DataChunk:
        """
        获取Chunk对象。

        :param path: 数据存储路径
        :param database: 绑定的数据库对象
        :return: Chunk对象
        """
        ...

    @abstractmethod
    def set_uuid_loader(self, history_uuid: ClassDataTypeUUID[History] | None) -> None:
        """
        设置UUID加载器。

        更改当前加载的历史记录UUID，用于在历史记录之间切换。

        :param history_uuid: 历史记录UUID，None表示当前存档
        """
        ...

    @abstractmethod
    def load_data(self, load_all: bool = False) -> UserDataBase:
        """
        加载数据。

        :param load_all: 是否加载所有历史记录
        :return: 加载的数据库对象
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def load_history(
        self,
        history_uuid: ClassDataTypeUUID[History] | None = None,
    ) -> History:
        """
        加载历史记录。

        :param history_uuid: 历史记录UUID，None表示当前存档
        :return: 历史记录对象
        """
        ...

    @abstractmethod
    def create_history(self) -> ClassDataTypeUUID[History]:
        """
        创建历史记录。

        将当前存档归档为历史记录。

        :return: 新创建的历史记录UUID
        """
        ...

    @abstractmethod
    def del_history(self, history_uuid: ClassDataTypeUUID[History]) -> bool:
        """
        删除历史记录。

        :param history_uuid: 要删除的历史记录UUID
        :return: 是否删除成功
        """
        ...

    @abstractmethod
    def list_histories(self) -> list[ClassDataTypeUUID[History]]:
        """
        列出所有历史记录。

        :return: 历史记录UUID列表
        """
        ...

    @abstractmethod
    def get_current_save_dir(self) -> str:
        """
        获取当前保存目录。

        :return: 当前保存目录路径
        """
        ...

    @abstractmethod
    def load_object(
        self,
        uuid: ClassDataTypeUUID[T],
        data_type: type[T],
    ) -> T | None:
        """
        加载单个对象。

        :param uuid: 对象UUID
        :param data_type: 对象类型
        :return: 加载的对象，不存在则返回None
        """
        ...

    @abstractmethod
    def save_object(self, obj: ClassDataType) -> None:
        """
        保存单个对象。

        :param obj: 要保存的对象
        """
        ...

    @abstractmethod
    def close_connections(self) -> None:
        """
        关闭所有数据库连接。
        """
        ...

    @staticmethod
    def commit_changes(clear_dataobj_connections: bool = True) -> None:
        """
        提交所有更改并释放连接。

        :param clear_dataobj_connections: 是否同时清理DataObject的连接
        """
        ...

