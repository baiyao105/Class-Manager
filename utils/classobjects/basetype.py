"""
所有班级数据类型的基类。

（类型检查写的我炸掉了）
"""
from __future__ import annotations
import copy
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, Optional, Self, TypeVar
from uuid import UUID, uuid4

from pydantic_core import core_schema

from utils.logger import Logger
from utils.profiler import profile

if TYPE_CHECKING:
  from .classdataloader import UserDataBase
  from .classdataset import ClassDataSet


_StringDataType = TypeVar("_StringDataType", covariant=True)


class StringObjectDataKind(str, Generic[_StringDataType]):
    "对象数据类型, ObjectDataDataKind[Student]代表这个字符串可以加载出一个学牲"



_DataType = TypeVar("_DataType", bound="ClassDataType", covariant=True)


class ClassDataTypeUUID(UUID, Generic[_DataType]):
    """
    班级数据类型的唯一标识符。
    """

    def __new__(cls, 
        dt: type[_DataType] | None = None, # 有的时候python会直接调用cls.__new__()，比如deepcopy时
        _uuid: UUID | None = None
    ):
        obj = super().__new__(cls)
        obj.dtype = dt # type: ignore
        return obj

    def __init__(self, dt: type[_DataType], _uuid: UUID | None = None): # type: ignore
        self.dtype: type[ClassDataType] = dt

        super().__init__(str(_uuid) if _uuid else str(uuid4()))

    def __deepcopy__(self, memo: dict[int, Any] | None) -> Self:
        return ClassDataTypeUUID(self.dtype, UUID(str(self)))  # type: ignore[return-value]

    def __reduce__(self) -> tuple[type[Self], tuple[type[ClassDataType], UUID]]:
        return (ClassDataTypeUUID, (self.dtype, UUID(str(self))))  # type: ignore[return-value]

    def __setattr__(self, name: str, value: Any):  # pyright: ignore[reportIncompatibleMethodOverride]，为了去掉UUID的限制
        val = object.__setattr__(self, name, value)
        Logger.log("T", f"setattr: {name} = {value!r} ({self!r})")
        return val

    def __eq__(self, other: object) -> bool:
        if self.__class__ != other.__class__:
            return False
        return str(self) == str(other)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __getitem__(self, item: int | slice) -> str:
        s = str(self)
        if isinstance(item, slice):
            return s[item]
        return s[item]

    def __hash__(self) -> int:
        return hash(self.dtype.__qualname__ + "_" + str(self))  # 防止不同类但UUID相同的情况

    def __repr__(self) -> str:
        return f"ClassDataTypeUUID(value={super(UUID, self).__repr__()}, dtype={self.dtype.__name__})"

    def __str__(self) -> str:
        return super().__str__().replace("-", "")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        """
        Pydantic核心模式生成。

        将ClassDataTypeUUID作为包含类型信息的字典处理。
        """
        python_schema = core_schema.with_info_plain_validator_function(
            cls._validate_pydantic,
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize_pydantic,
                return_schema=core_schema.dict_schema(
                    core_schema.str_schema(),
                    core_schema.any_schema()
                ),
                when_used="json"
            )
        )
        return python_schema

    @classmethod
    def _serialize_pydantic(cls, value: ClassDataTypeUUID[Any]) -> dict[str, str]:
        """
        Pydantic序列化函数。

        :param value: ClassDataTypeUUID实例
        :return: 包含UUID和类型信息的字典
        """
        if not hasattr(value, 'dtype'):
            raise ValueError(f"ClassDataTypeUUID实例没有dtype属性: {value}")
        return {
            "uuid": str(value),
            "type_name": value.dtype.chunk_type_name
        }

    @classmethod
    def _validate_pydantic(cls, value: Any, _info: Any) -> ClassDataTypeUUID[Any]:
        """
        Pydantic验证函数。

        :param value: 输入值
        :param _info: 验证信息
        :return: ClassDataTypeUUID实例
        """
        if isinstance(value, ClassDataTypeUUID):
            return value # type: ignore
        if isinstance(value, dict) and "uuid" in value and "type_name" in value:
            from .dataloaders.pydantic_loader.base import get_type_by_name
            type_name: str = str(value["type_name"])  # type: ignore
            uuid: str = str(value["uuid"])  # type: ignore
            dtype = get_type_by_name(type_name)
            if dtype is None:
                raise ValueError(f"未知的类型名称: {type_name}")
            return ClassDataTypeUUID(dtype, UUID(uuid.replace("-", "")))
        raise ValueError(f"无法将{type(value).__name__}转换为ClassDataTypeUUID")  # type: ignore


class ClassDataType(ABC):
    """
    所有班级数据类型的基类。
    """

    class DataTypeError(RuntimeError):
        "数据类型的错误"

    chunk_type_name: str
    "该班级数据类型的数据库名称。"

    is_unrelated_dtype: bool
    "该班级数据类型是否与其它班级数据类型无关。"

    def __init__(self, uuid: ClassDataTypeUUID[Self] | UUID | None = None):
        self._user_db_ref: Optional[UserDataBase] = None
        self._uuid: ClassDataTypeUUID[Self]
        if uuid is None:
            self._uuid = ClassDataTypeUUID(self.__class__, uuid4())

        elif isinstance(uuid, ClassDataTypeUUID):
            self._uuid = uuid
        
        elif isinstance(uuid, str):
            self._uuid = ClassDataTypeUUID(self.__class__, UUID(uuid.replace("-", "")))

        else:
            raise TypeError(f"uuid参数需要是UUID, ClassDataTypeUUID, str或None，但提供了{type(uuid)}")

        self._user_db_ref = None

    @property
    def uuid(self) -> ClassDataTypeUUID[Self]:
        """
        该班级数据类型的唯一标识符。
        """
        if not hasattr(self, "_uuid"):
            self._uuid = ClassDataTypeUUID(self.__class__)
        return self._uuid

    @uuid.setter
    def uuid(self, value: UUID | ClassDataTypeUUID[Self] | str):
        if isinstance(value, ClassDataTypeUUID):
            self._uuid = value

        elif isinstance(value, UUID):
            self._uuid = ClassDataTypeUUID(self.__class__, value)

        elif type(value) is str:
            self._uuid = ClassDataTypeUUID(self.__class__, UUID(value.replace("-", "")))

        else:
            raise TypeError(f"uuid.setter需要提供UUID，ClassDataTypeUUID或者str， 但提供了{type(value)}")

    def refresh_uuid(self):
        self.uuid = uuid4()

    @property
    def archive_uuid(self) -> UUID | None:
        """
        该班级数据类型的对应的存档标识符。
        """
        if not hasattr(self, "_archive_uuid"):
            self._archive_uuid = uuid4()
        return self._archive_uuid

    @archive_uuid.setter
    def archive_uuid(self, value: UUID | str | None):
        if isinstance(value, UUID):
            self._archive_uuid = value

        elif isinstance(value, str):
            if value == str(None):
                # 这里要注意下，一个对象的archive_uuid可能为None
                # 因为大多数地方都用的是str(uuid)，所以这里要特判uuid为"None"的情况
                self._archive_uuid = None
            else:
                self._archive_uuid = UUID(value.replace("-", ""))

        elif value is None:
            self._archive_uuid = None

        else:
            raise TypeError(f"archive_uuid.setter需要提供UUID，ClassDataTypeUUID或者str， 但提供了{type(value)}")

    def copy(self) -> Self:
        """
        返回该班级数据类型的副本。
        """
        return copy.deepcopy(self)

    def __repr__(self):
        """
        返回这个对象的表达式。
        """
        return (
            f"{self.__class__.__name__}"
            f"({', '.join([f'{k}={v!r}' for k, v in self.__dict__.items() if not k.startswith('_')])})"
        )

    @classmethod
    @abstractmethod
    def from_string(cls, string: str) -> Self:
        """
        从字符串解析该班级数据类型，并返回该类型的对象。
        """

    @abstractmethod
    def to_string(self) -> StringObjectDataKind[Self]:
        """
        将该班级数据类型转换为字符串。
        """

    def to_dict(self) -> Dict[str, Any]:
        """
        将该班级数据类型转换为字典。

        允许这个方法不被实现。

        """
        raise NotImplementedError(f"该数据类型({self.__class__.__name__})的to_dict方法未实现")

    def from_dict(self, data: Dict[str, Any]) -> Self:
        """
        从字典解析该班级数据类型。

        允许这个方法不被实现。
        """
        raise NotImplementedError(f"该数据类型({self.__class__.__name__})的from_dict方法未实现")

    @abstractmethod
    def inst_from_string(self, string: str) -> Self:
        """
        从字符串解析该班级数据类型，并加载至本身。
        """

    @classmethod
    @abstractmethod
    def new_dummy(cls) -> Self:
        """
        返回该班级数据类型的空对象。
        """

    def get_class_data_Set(self) -> Optional[ClassDataSet]:
        """
        通过单例模式获取ClassDataSet引用。
        """
        from .classdataset import ClassDataSet
        return ClassDataSet.get_current_instance()
    
    @abstractmethod
    def to_pydantic(self) -> Any:
        """
        将该班级数据类型转换为Pydantic模型。

        :return: Pydantic模型实例
        """


class DataProperty(property):
    """
    数据属性，用于ClassDataType的属性。

    打上这个标签的属性在值变化时会依照设置触发数据变化事件。
    """

    def __init__(
        self,
        fget: Optional[Callable[..., Any]] = None,
        fset: Optional[Callable[..., Any]] = None,
        fdel: Optional[Callable[..., Any]] = None,
        doc: Optional[str] = None,
        trigger_event: bool = True,
        event_name_override: Optional[str] = None
    ):
        """
        构造函数
        
        :param fget: getter函数
        :param fset: setter函数
        :param fdel: deleter函数
        :param doc: 文档字符串
        :param trigger_event: 是否在值变化时触发数据变化事件
        :param event_name_override: 自定义事件名称（覆盖默认命名）
        """
        super().__init__(fget, fset, fdel, doc)
        
        self.trigger_event = trigger_event
        self.event_name_override = event_name_override

    def __get__(self, instance: Optional[ClassDataType], owner: Optional[type[ClassDataType]] = None) -> Any:
        return super().__get__(instance, owner)

    def __set__(self, instance: ClassDataType, value: Any):
        old_value = None
        try:
            old_value = super().__get__(instance, type(instance))
        except (AttributeError, TypeError):
            pass
        super().__set__(instance, value)
        new_value = value
        if old_value != new_value:
            self.on_value_changed(instance, old_value, new_value)


    def __delete__(self, instance: ClassDataType):
        raise AttributeError("不能删除数据属性")

    def get_full_event_name(self) -> str:
        """
        获取完整的事件名称
        
        :param instance: 实例对象
        :return: 完整事件名称
        """
        if self.event_name_override is not None:
            return self.event_name_override
        property_name =  self.fget.__qualname__
        return f"DATA_CHANGED_{property_name}"

    @profile("DataProperty._on_value_changed")
    def on_value_changed(self, instance: ClassDataType, old_value: Any, new_value: Any):
        """
        值变化时的处理
        """
        if not self.trigger_event:
            return
        start_time = time.perf_counter()
        class_obj = instance.get_class_data_Set()
        if class_obj is None:
            return
        event_key = self.get_full_event_name()
        class_obj.broadcast_data_changed(event_key)
        elapsed = time.perf_counter() - start_time
        if elapsed > 0.001:
            Logger.log("W", f"DataProperty._on_value_changed发送数据变更事件{event_key}时耗费了{elapsed*1000:.2f}ms")
