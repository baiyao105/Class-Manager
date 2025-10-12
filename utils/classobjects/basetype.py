
import copy
from uuid import UUID, uuid4
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Union, Optional



_DataType = TypeVar("_DataType")

class ClassDataTypeUUID(UUID, Generic[_DataType]):
    """
    班级数据类型的唯一标识符。
    """

    def __init__(self, dt: _DataType, _uuid: Optional[UUID] = None):
        super().__init__(int=_uuid.int if _uuid else uuid4().int)
        self.dtype = dt


    def __repr__(self) -> str:
        return f"ClassObjUUID(value={super(UUID, self).__repr__()}, dtype={self.dtype.__name__})"
    
    def __setattr__(self, name, value): # 为了去掉UUID的限制
        return object.__setattr__(self, name, value)
    
    def __eq__(self, other: object) -> bool:
        if self.__class__ != other.__class__:
            return False
        if not super(UUID, self).__eq__(other):
            return False
        return True
    
    def __getitem__(self, item):
        return str(self).replace("-", "")[item]
    
    def __hash__(self) -> int:
        return hash(self.dtype.__qualname__ + "_" + str(self)) # 防止不同类但UUID相同的情况



class ClassDataType(ABC):
    """
    所有班级数据类型的基类。
    """

    chunk_type_name: str
    "该班级数据类型的数据库名称。"

    is_unrelated_dtype: bool
    "该班级数据类型是否与其它班级数据类型无关。"

    def __init__(self, uuid: Union[UUID, ClassDataTypeUUID] = None):
        if uuid is None:
            # 作为一个全新的对象被构建
            self._uuid = ClassDataTypeUUID(self.__class__, uuid4())
            self._loaded = True
        else:
            # 是根据UUID从数据库中加载的对象，并且刚刚被初始化
            self._uuid = uuid
            self._loaded = False


    @property
    def uuid(self) -> ClassDataTypeUUID:
        """
        该班级数据类型的唯一标识符。
        """
        if not hasattr(self, "_uuid"):
            self._uuid = ClassDataTypeUUID(self.__class__)
        return self._uuid
    
    @uuid.setter
    def uuid(self, value: Union[UUID, ClassDataTypeUUID, str, None]):
        if isinstance(value, UUID):
            self._uuid = ClassDataTypeUUID(self.__class__, value)
            self._loaded = False
            
        elif isinstance(value, ClassDataTypeUUID):
            self._uuid = value
            self._loaded = False
        
        elif isinstance(value, str):
            self._uuid = ClassDataTypeUUID(self.__class__, UUID(value.replace("-", "")))
            self._loaded = False

        elif value is None:
            self._uuid = None
            self._loaded = False
        
        else:
            raise TypeError(f"uuid.setter需要提供UUID，ClassDataTypeUUID或者str， 但提供了{type(value)}")

    def refresh_uuid(self):
        self.uuid = uuid4()

    @property
    def archive_uuid(self) -> ClassDataTypeUUID:
        """
        该班级数据类型的对应的存档标识符。
        """
        if not hasattr(self, "_archive_uuid"):
            self._archive_uuid = ClassDataTypeUUID(self.__class__)
        return self._archive_uuid
    
    @archive_uuid.setter
    def archive_uuid(self, value: Union[UUID, ClassDataTypeUUID, str, None]):
        if isinstance(value, UUID):
            self._archive_uuid = ClassDataTypeUUID(self.__class__, value)
            
        elif isinstance(value, ClassDataTypeUUID):
            self._archive_uuid = value
        
        elif isinstance(value, str):
            if value == str(None):
                self._archive_uuid = None
            else:
                self._archive_uuid = ClassDataTypeUUID(self.__class__, UUID(value.replace("-", "")))

        elif value is None:
            self._archive_uuid = None

        else:
            raise TypeError(f"archive_uuid.setter需要提供UUID，ClassDataTypeUUID或者str， 但提供了{type(value)}")


    def copy(self) -> "ClassDataType":
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
    def from_string(self, string: str) -> "ClassDataType":
        """
        从字符串解析该班级数据类型。
        """

    @abstractmethod
    def to_string(self) -> str:
        """
        将该班级数据类型转换为字符串。
        """

    def to_dict(self) -> dict:
        """
        将该班级数据类型转换为字典。
        """
        raise NotImplementedError(F"该数据类型({self.__class__.__name__})的to_dict方法未实现")

    def from_dict(self, data: dict) -> "ClassDataType":
        """
        从字典解析该班级数据类型。
        """
        raise NotImplementedError(F"该数据类型({self.__class__.__name__})的from_dict方法未实现")
    
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
            return
        return super().__set__(instance, value)

    def __delete__(self, instance):
        if instance is None:
            return
        return super().__delete__(instance)
    
