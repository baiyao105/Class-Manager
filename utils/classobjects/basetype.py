"""
所有班级数据类型的基类。

（类型检查写的我炸掉了）
"""
from __future__ import annotations
import copy
from abc import ABC, abstractmethod
from typing import Generic, Self, TypeVar
from uuid import UUID, uuid4

_StringDataType = TypeVar("_StringDataType")


class StringObjectDataKind(Generic[_StringDataType], str):
    "对象数据类型, ObjectDataKind[Student]代表这个字符串可以加载出一个学牲"


_DataType = TypeVar("_DataType")


class ClassDataTypeUUID(UUID, Generic[_DataType]):
    """
    班级数据类型的唯一标识符。
    """

    def __init__(self, dt: type[_DataType], _uuid: UUID | None = None):
        super().__init__(str(_uuid) if _uuid else str(uuid4()))
        self.dtype = dt

    def __setattr__(self, name, value):  # 为了去掉UUID的限制
        return object.__setattr__(self, name, value)

    def __eq__(self, other: object) -> bool:
        if self.__class__ != other.__class__:
            return False
        return str(self) == str(other)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __getitem__(self, item):
        return str(self).replace("-", "")[item]

    def __hash__(self) -> int:
        return hash(self.dtype.__qualname__ + "_" + str(self))  # 防止不同类但UUID相同的情况

    def __repr__(self) -> str:
        return f"ClassDataTypeUUID(value={super().__repr__()}, dtype={self.dtype.__name__})"

    def __str__(self) -> str:
        return super().__str__()


class ClassDataType(ABC):
    """
    所有班级数据类型的基类。
    """

    chunk_type_name: str
    "该班级数据类型的数据库名称。"

    is_unrelated_dtype: bool
    "该班级数据类型是否与其它班级数据类型无关。"

    def __init__(self, uuid: ClassDataTypeUUID[Self] | UUID | None = None):
        self._uuid: ClassDataTypeUUID[Self]
        if uuid is None:
            self._uuid = ClassDataTypeUUID(self.__class__, uuid4())

        elif isinstance(uuid, ClassDataTypeUUID):
            self._uuid = uuid

        elif isinstance(uuid, UUID):
            self._uuid = ClassDataTypeUUID(self.__class__, uuid)

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

        elif isinstance(value, str):
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

    @abstractmethod
    def from_string(self, string: str) -> StringObjectDataKind[Self]:
        """
        从字符串解析该班级数据类型。
        """

    @abstractmethod
    def to_string(self) -> StringObjectDataKind[Self]:
        """
        将该班级数据类型转换为字符串。
        """

    def to_dict(self) -> dict:
        """
        将该班级数据类型转换为字典。

        允许这个方法不被实现。

        """
        raise NotImplementedError(f"该数据类型({self.__class__.__name__})的to_dict方法未实现")

    def from_dict(self, data: dict) -> "ClassDataType":
        """
        从字典解析该班级数据类型。

        允许这个方法不被实现。
        """
        raise NotImplementedError(f"该数据类型({self.__class__.__name__})的from_dict方法未实现")

    @abstractmethod
    def inst_from_string(self, string: str) -> "ClassDataType":
        """
        从字符串解析该班级数据类型，并加载至本身。
        """

    @staticmethod
    @abstractmethod
    def new_dummy() -> "ClassDataType":
        """
        返回该班级数据类型的空对象。
        """


class DataProperty(property):
    "数据属性，用于ClassDataType的属性"

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        super().__init__(fget, fset, fdel, doc)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return super().__get__(instance, owner)

    def __set__(self, instance, value):
        if instance is None:
            return None
        return super().__set__(instance, value)

    def __delete__(self, instance):
        if instance is None:
            return None
        return super().__delete__(instance)
