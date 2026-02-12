"""
数字类型
"""
from __future__ import annotations
import time
import math
import random
from typing import Union, Optional, Type, SupportsInt, Any
from ctypes import (
    c_int,
    c_int8,
    c_int16,
    c_int32,
    c_int64,
    c_uint,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
    c_float,
    c_double,
    c_longdouble)


inf = math.inf
nan = math.nan



CData = Union[
    c_int,
    c_uint,
    c_int8,
    c_int16,
    c_int32,
    c_int64,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
    c_float,
    c_double,
    c_longdouble
]

CDataType = Type[CData]


class OverridedCData:
    "重写过的CData类型"
    _dtype: CDataType
    _data: CData
    _tpname: str

BasicData = Union[int, float, bool]
Numbers = Union[int, float]


# 偶遇Pylance类型检查解析错误，拼尽全力无法战胜
# （只能用type: ignore了，但太多了根本打不过来）

def cdatatype(dtype: CDataType, name: Optional[str] = None):
    """
    自定义C整数类型包装器(抽象)

    :param dtype: 要继承的数据类型
    :param name:  类名
    :return: 继承了cint类型的类
    """
    if name is None:
        name = dtype.__name__

    class _CIntType(OverridedCData, SupportsInt):
        "继承cint类型的类"

        def __init__(self, value: Union[CData, int, float]):
            if isinstance(value, CData):
                value = value.value

            self._dtype: CDataType = dtype
            self._data: CData = self._dtype(value) # type: ignore
            self._tpname: str = name

        def __str__(self):
            return str(self._data.value)

        def __repr__(self):
            return f"{self._tpname}({self._data.value!r})"

        def __int__(self):
            return int(self._data.value)

        def __float__(self):
            return float(self._data.value)

        def __bool__(self):
            return bool(self._data.value)

        def __hash__(self):
            return hash(self._data.value)

        def __eq__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, Numbers):
                if other == inf:
                    return False
                if other == -inf:
                    return False
                if math.isnan(other):
                    return False
            return self._data.value == other

        def __ne__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, Numbers):
                if other == inf:
                    return True
                if other == -inf:
                    return True
                if math.isnan(other):
                    return True
            return self._data.value != other

        def __lt__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            if not isinstance(other, Numbers):
                raise TypeError(f"{self.__class__.__name__} 与 {type(other).__name__} 不支持大小比较")
            if other == inf:
                return True
            if other == -inf:
                return False
            if math.isnan(other):
                return False
            return self._data.value < other

        def __le__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            if not isinstance(other, Numbers):
                raise TypeError(f"{self.__class__.__name__} 与 {type(other).__name__} 不支持大小比较")
            if other == inf:
                return True
            if other == -inf:
                return False
            if math.isnan(other):
                return False
            return self._data.value <= other

        def __gt__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            if not isinstance(other, Numbers):
                raise TypeError(f"{self.__class__.__name__} 与 {type(other).__name__} 不支持大小比较")
            if other == inf:
                return False
            if other == -inf:
                return True
            if math.isnan(other):
                return False
            return self._data.value > other

        def __ge__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            if not isinstance(other, Numbers):
                raise TypeError(f"{self.__class__.__name__} 与 {type(other).__name__} 不支持大小比较")
            if other == inf:
                return False
            if other == -inf:
                return True
            if math.isnan(other):
                return False
            return self._data.value >= other
        

        def _check_datatypes(self, other: Union[OverridedCData, Numbers]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            if (not isinstance(self._data.value, Numbers)) or (not isinstance(other, Numbers)):
                raise TypeError(f"类型 {self.__class__.__name__} 与 {other.__class__.__name__} 不支持运算操作")
            
        def _check_int_datatypes(self, other: Union[OverridedCData, Numbers]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            if (not isinstance(self._data.value, int)) or (not isinstance(other, int)):
                raise TypeError(f"类型 {self.__class__.__name__} 与 {other.__class__.__name__} 不支持位运算操作")

        def __abs__(self):
            return cdatatype(self._dtype, self._tpname)(abs(self._data.value))

        def __neg__(self):
            return cdatatype(self._dtype, self._tpname)(-self._data.value)

        def __pos__(self):
            return cdatatype(self._dtype, self._tpname)(+self._data.value)

        def __round__(self, ndigits = None):
            return cdatatype(self._dtype, self._tpname)(round(self._data.value, ndigits))

        def __add__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(self._data.value + other)

        def __sub__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(self._data.value - other)

        def __mul__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(self._data.value * other)

        def __truediv__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(self._data.value / other)

        def __floordiv__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(self._data.value // other)
        
        def __mod__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(self._data.value % other)

        def __pow__(self, other: Union[OverridedCData, BasicData]):
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(self._data.value ** other)

        def __lshift__(self, other: Union[OverridedCData, BasicData]):
            if not isinstance(self._data.value, int):
                raise TypeError(f"原数字类型 {self.__class__.__name__} 对应的数据类型为{self._dtype.__name__}, 不支持左移操作")
            if isinstance(other, OverridedCData):
                other = other._data.value
            if not isinstance(other, int):
                raise TypeError(f"位移数类型 {self.__class__.__name__} 对应的数据类型为 {self._dtype.__name__}, 为非法左移操作数")
            return cdatatype(self._dtype, self._tpname)(self._data.value << other)

        def __rshift__(self, other: Union[OverridedCData, BasicData]):
            if not isinstance(self._data.value, int):
                raise TypeError(f"原数字类型 {self.__class__.__name__} 对应的数据类型为{self._dtype.__name__}, 不支持右移操作")
            if isinstance(other, OverridedCData):
                other = other._data.value
            if not isinstance(other, int):
                raise TypeError(f"位移数类型 {self.__class__.__name__} 对应的数据类型为 {self._dtype.__name__}, 为非法右移操作数")
            return cdatatype(self._dtype, self._tpname)(self._data.value >> other)

        def __and__(self, other: Union[OverridedCData, BasicData]):
            if not isinstance(self._data.value, int):
                raise TypeError(f"位与左值类型 {self.__class__.__name__} 对应的数据类型为 {self._dtype.__name__}, 不支持按位与操作")
            if isinstance(other, OverridedCData):
                other = other._data.value
            if not isinstance(other, int):
                raise TypeError(f"位与右值类型 {self.__class__.__name__} 对应的数据类型为 {self._dtype.__name__}, 为非法按位与操作数")
            return cdatatype(self._dtype, self._tpname)(self._data.value & other)
        

        def __or__(self, other: Union[OverridedCData, BasicData]):
            if not isinstance(self._data.value, int):
                raise TypeError(f"位或左值类型 {self.__class__.__name__} 对应的数据类型为 {self._dtype.__name__}, 不支持按位或操作")
            if isinstance(other, OverridedCData):
                other = other._data.value
            if not isinstance(other, int):
                raise TypeError(f"位或右值类型 {self.__class__.__name__} 对应的数据类型为 {self._dtype.__name__}, 为非法按位或操作数")
            return cdatatype(self._dtype, self._tpname)(self._data.value & other)
        

        def __xor__(self, other: Union[OverridedCData, BasicData]):
            if not isinstance(self._data.value, int):
                raise TypeError(f"位异或左值类型 {self.__class__.__name__} 对应的数据类型为 {self._dtype.__name__}, 不支持按位异或操作")
            if isinstance(other, OverridedCData):
                other = other._data.value
            if not isinstance(other, int):
                raise TypeError(f"位异或右值类型 {self.__class__.__name__} 对应的数据类型为 {self._dtype.__name__}, 为非法按位异或操作数")
            return cdatatype(self._dtype, self._tpname)(self._data.value ^ other)

        def __invert__(self):
            if not isinstance(self._data.value, int):
                raise TypeError(f"{self.__class__.__name__}对应的数据类型为 {self._dtype.__name__}, 不支持按位取反操作")
            return cdatatype(self._dtype, self._tpname)(~self._data.value)

        def __iadd__(self, other: Union[OverridedCData, Numbers]):
            self._check_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            self._data.value += other
            return cdatatype(self._dtype, self._tpname)(self._data.value)

        def __isub__(self, other: Union[OverridedCData, Numbers]):
            self._check_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            self._data.value -= other
            return cdatatype(self._dtype, self._tpname)(self._data.value)

        def __imul__(self, other: Union[OverridedCData, Numbers]):
            self._check_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            self._data.value *= other
            return cdatatype(self._dtype, self._tpname)(self._data.value)

        def __itruediv__(self, other: Union[OverridedCData, BasicData]):
            self._check_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            self._data.value /= other
            return cdatatype(self._dtype, self._tpname)(self._data.value)

        def __ifloordiv__(self, other: Union[OverridedCData, Numbers]):
            self._check_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            self._data.value //= other
            return cdatatype(self._dtype, self._tpname)(self._data.value)

        def __imod__(self, other: Union[OverridedCData, Numbers]):
            self._check_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            self._data.value %= other
            return cdatatype(self._dtype, self._tpname)(self._data.value)

        def __ipow__(self, other: Union[OverridedCData, Numbers]):
            self._check_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            self._data.value **= other
            return cdatatype(self._dtype, self._tpname)(self._data.value)

        

        def __ilshift__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            self._data.value <<= other  # type: ignore
            return cdatatype(self._dtype, self._tpname)(self._data.value)

        def __irshift__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            self._data.value >>= other  # type: ignore
            return cdatatype(self._dtype, self._tpname)(self._data.value)

        def __iand__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            self._data.value &= other  # type: ignore
            return cdatatype(self._dtype, self._tpname)(self._data.value)

        def __ior__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            self._data.value |= other  # type: ignore
            return cdatatype(self._dtype, self._tpname)(self._data.value)

        def __ixor__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            self._data.value ^= other  # type: ignore
            return cdatatype(self._dtype, self._tpname)(self._data.value)

        # 懒得写了（）

        def __radd__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(other) + cdatatype(self._dtype, self._tpname)(self._data.value)
        
        def __rsub__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(other) - cdatatype(self._dtype, self._tpname)(self._data.value)
        
        def __rmul__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(other) * cdatatype(self._dtype, self._tpname)(self._data.value)

        def __rtruediv__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(other) / cdatatype(self._dtype, self._tpname)(self._data.value)
        
        def __rfloordiv__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(other) // cdatatype(self._dtype, self._tpname)(self._data.value)
        
        def __rmod__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(other) % cdatatype(self._dtype, self._tpname)(self._data.value)
        
        def __rpow__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(other) ** cdatatype(self._dtype, self._tpname)(self._data.value)
        
        def __rlshift__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(other) << cdatatype(self._dtype, self._tpname)(self._data.value)
        
        def __rrshift__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(other) >> cdatatype(self._dtype, self._tpname)(self._data.value)
        
        def __rand__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(other) & cdatatype(self._dtype, self._tpname)(self._data.value)
        
        def __rxor__(self, other: Union[OverridedCData, Numbers]):
            self._check_int_datatypes(other)
            if isinstance(other, OverridedCData):
                other = other._data.value
            return cdatatype(self._dtype, self._tpname)(other) ^ cdatatype(self._dtype, self._tpname)(self._data.value)
        



    return _CIntType



Int8 = cdatatype(c_int8, "Byte")
"8bit整数"
Byte = Int8
"字节长整数(8bit)"
Int16 = cdatatype(c_int16, "Short")
"16bit整数"
Short = Int16
"16bit整数"
Int32 = cdatatype(c_int32, "Integer")
"32bit整数"
Integer = Int32
"32bit整数"
Int64 = cdatatype(c_int64, "Qword")
"64bit整数"
QWord = Int64
"64bit整数"
UInt8 = cdatatype(c_uint8, "UnsignedByte")
"8bit无符号整数"
UnsignedByte = UInt8
"8bit无符号整数"
UInt16 = cdatatype(c_uint16, "UnsignedShort")
"16bit无符号整数"
UnsignedShort = UInt16
"16bit无符号整数"
UInt32 = cdatatype(c_uint32, "UnsignedInteger")
"32bit无符号整数"
UnsignedInteger = UInt32
"32bit无符号整数"
UInt64 = cdatatype(c_uint64, "UnsignedQWord")
"64bit无符号整数"
UnsignedQWord = UInt64
"64bit无符号整数"


def utc(prec: int = 3):
    """获取当前UTC时间戳

    :param prec: 精度，表示小数点后的位数
    :return: 指定精度的UTC时间戳
    """
    return int(time.time() * (10**prec))


def steprange(start: int | float, stop: int | float, step: int) -> list[float]:
    """生成step步长的从start到stop的列表

    :param start: 起始值
    :param stop: 结束值
    :param step: 步数
    :return: 从start到stop的列表

    举个例子

    >>> steprange(0, 10, 5)
    [0, 2.5, 5.0, 7.5, 10]
    """
    diff = (stop - start) / (step - 1)
    return [start + diff * i for i in range(step)]


def addrof(obj: Any) -> str:
    """获取对象的内存地址

    :param obj: 任意Python对象
    :return: 十六进制格式的内存地址字符串
    """
    return "0x" + hex(id(obj))[2:].zfill(16).upper()


def gen_uuid(length: int = 32) -> str:
    "生成一个长32位的uuid"
    return "".join([str(random.choice("0123456789abcdef")) for _ in range(length)])


def get_time():
    "获得当前时间"
    lt = time.localtime()
    return (
        f"{lt.tm_year}-{lt.tm_mon:02}-{lt.tm_mday:02} "
        + f"{lt.tm_hour:02}:{lt.tm_min:02}:{lt.tm_sec:02}"
        + f".{int((time.time() % 1) * 1000):03}"
    )
