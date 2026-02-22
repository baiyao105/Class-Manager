"""
数据存储抽象接口。

提供统一的数据存储和加载接口，支持多种实现（如旧版Chunk和PydanticLoader）。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

if TYPE_CHECKING:
    from .basetype import ClassDataType, ClassDataTypeUUID
    from .objects.history import History
    from .classdataset import UserDataBase

T = TypeVar("T", bound=ClassDataType)


class DataChunk(ABC):
    """
    数据存储抽象接口。

    提供统一的数据存储和加载接口，支持多种实现。
    """


    loading_info: ClassVar[dict[str, Any]] = {}
    """
    加载信息字典。

    用于存储加载/保存进度信息，供UI显示进度。

    包含以下字段：
    - history_stage: 当前保存阶段描述
    - current_saving_obj_name: 当前保存的对象类型名称
    - current_saving_obj_current: 当前保存的对象索引
    - current_saving_obj_total: 当前保存的对象总数
    - total_percentage: 总进度百分比
    """

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

