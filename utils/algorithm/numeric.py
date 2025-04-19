"""
数字类型
"""

import math
import time
import random
from typing import Union, Optional, Any, List
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
)


inf = math.inf
nan = math.nan

CIntegerType = Union[
    int,
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
]


def cinttype(dtype: CIntegerType, name: Optional[str] = None):
    """
    自定义C整数类型包装器(抽象)

    :param dtype: 要继承的数据类型
    :param name:  类名
    :return: 继承了cint类型的类
    """
    if name is None:
        name = dtype.__name__

    class _CIntType:
        "继承cint类型的类"

        def __init__(self, value: CIntegerType):
            try:
                value = int(value)
            except (ValueError, TypeError):
                value = int(value.value)

            self._dtype: CIntegerType = dtype
            self._data: CIntegerType = self._dtype(value)
            self._tpname: str = name

        def __str__(self):
            return str(self._data.value)

        def __repr__(self):
            return f"{self._tpname}({repr(self._data.value)})"

        def __int__(self):
            return int(self._data.value)

        def __float__(self):
            return float(self._data.value)

        def __bool__(self):
            return bool(self._data.value)

        def __hash__(self):
            return hash(self._data.value)

        def __eq__(self, other):
            if other == inf:
                return False
            if other == -inf:
                return False
            if math.isnan(other):
                return False
            return self._data.value == int(other)

        def __ne__(self, other):
            if other == inf:
                return True
            if other == -inf:
                return True
            if math.isnan(other):
                return True
            return self._data.value != int(other)

        def __lt__(self, other):
            if other == inf:
                return True
            if other == -inf:
                return False
            if math.isnan(other):
                return False
            return self._data.value < int(other)

        def __le__(self, other):
            if other == inf:
                return True
            if other == -inf:
                return False
            if math.isnan(other):
                return False
            return self._data.value <= int(other)

        def __gt__(self, other):
            if other == inf:
                return False
            if other == -inf:
                return True
            if math.isnan(other):
                return False
            return self._data.value > int(other)

        def __ge__(self, other):
            if other == inf:
                return False
            if other == -inf:
                return True
            if math.isnan(other):
                return False
            return self._data.value >= int(other)

        def __abs__(self):
            return cinttype(self._dtype, self._tpname)(abs(self._data.value))

        def __neg__(self):
            return cinttype(self._dtype, self._tpname)(-self._data.value)

        def __pos__(self):
            return cinttype(self._dtype, self._tpname)(+self._data.value)

        def __round__(self, ndigits=None):
            return cinttype(self._dtype, self._tpname)(round(self._data.value, ndigits))

        def __add__(self, other: Any):
            return cinttype(self._dtype, self._tpname)(self._data.value + int(other))

        def __sub__(self, other):
            return cinttype(self._dtype, self._tpname)(self._data.value - int(other))

        def __mul__(self, other):
            return cinttype(self._dtype, self._tpname)(self._data.value * int(other))

        def __truediv__(self, other):
            return cinttype(self._dtype, self._tpname)(self._data.value / int(other))

        def __floordiv__(self, other):
            return cinttype(self._dtype, self._tpname)(self._data.value // int(other))

        def __mod__(self, other):
            return cinttype(self._dtype, self._tpname)(self._data.value % int(other))

        def __pow__(self, other):
            return cinttype(self._dtype, self._tpname)(self._data.value ** int(other))

        def __lshift__(self, other):
            return cinttype(self._dtype, self._tpname)(self._data.value << int(other))

        def __rshift__(self, other):
            return cinttype(self._dtype, self._tpname)(self._data.value >> int(other))

        def __and__(self, other):
            return cinttype(self._dtype, self._tpname)(self._data.value & int(other))

        def __or__(self, other):
            return cinttype(self._dtype, self._tpname)(self._data.value | int(other))

        def __xor__(self, other):
            return cinttype(self._dtype, self._tpname)(self._data.value ^ int(other))

        def __invert__(self):
            return cinttype(self._dtype, self._tpname)(~self._data.value)

        def __iadd__(self, other):
            self._data.value += int(other)
            return cinttype(self._dtype, self._tpname)(self._data.value)

        def __isub__(self, other):
            self._data.value -= int(other)
            return cinttype(self._dtype, self._tpname)(self._data.value)

        def __imul__(self, other):
            self._data.value *= int(other)
            return cinttype(self._dtype, self._tpname)(self._data.value)

        def __itruediv__(self, other):
            self._data.value /= int(other)
            return cinttype(self._dtype, self._tpname)(self._data.value)

        def __ifloordiv__(self, other):
            self._data.value //= int(other)
            return cinttype(self._dtype, self._tpname)(self._data.value)

        def __imod__(self, other):
            self._data.value %= int(other)
            return cinttype(self._dtype, self._tpname)(self._data.value)

        def __ipow__(self, other):
            self._data.value **= int(other)
            return cinttype(self._dtype, self._tpname)(self._data.value)

        def __ilshift__(self, other):
            self._data.value <<= int(other)
            return cinttype(self._dtype, self._tpname)(self._data.value)

        def __irshift__(self, other):
            self._data.value >>= int(other)
            return cinttype(self._dtype, self._tpname)(self._data.value)

        def __iand__(self, other):
            self._data.value &= int(other)
            return cinttype(self._dtype, self._tpname)(self._data.value)

        def __ior__(self, other):
            self._data.value |= int(other)
            return cinttype(self._dtype, self._tpname)(self._data.value)

        def __ixor__(self, other):
            self._data.value ^= int(other)
            return cinttype(self._dtype, self._tpname)(self._data.value)

        def __radd__(self, other):
            return cinttype(self._dtype, self._tpname)(int(other) + self._data.value)

        def __rsub__(self, other):
            return cinttype(self._dtype, self._tpname)(int(other) - self._data.value)

        def __rmul__(self, other):

            return cinttype(self._dtype, self._tpname)(int(other) * self._data.value)

        def __rtruediv__(self, other):
            return cinttype(self._dtype, self._tpname)(int(other) / self._data.value)

        def __rfloordiv__(self, other):
            return cinttype(self._dtype, self._tpname)(int(other) // self._data.value)

        def __rmod__(self, other):
            return cinttype(self._dtype, self._tpname)(int(other) % self._data.value)

        def __rpow__(self, other):
            return cinttype(self._dtype, self._tpname)(int(other) ** self._data.value)

        def __rlshift__(self, other):
            return cinttype(self._dtype, self._tpname)(int(other) << self._data.value)

        def __rrshift__(self, other):
            return cinttype(self._dtype, self._tpname)(int(other) >> self._data.value)

        def __rand__(self, other):
            return cinttype(self._dtype, self._tpname)(int(other) & self._data.value)

        def __rxor__(self, other):
            return cinttype(self._dtype, self._tpname)(int(other) ^ self._data.value)

    return _CIntType


Int8 = cinttype(c_int8, "Byte")
"8bit整数"
Byte = Int8
"字节长整数(8bit)"
Int16 = cinttype(c_int16, "Short")
"16bit整数"
Short = Int16
"16bit整数"
Int32 = cinttype(c_int32, "Integer")
"32bit整数"
Integer = Int32
"32bit整数"
Int64 = cinttype(c_int64, "Qword")
"64bit整数"
QWord = Int64
"64bit整数"
UInt8 = cinttype(c_uint8, "UnsignedByte")
"8bit无符号整数"
UnsignedByte = UInt8
"8bit无符号整数"
UInt16 = cinttype(c_uint16, "UnsignedShort")
"16bit无符号整数"
UnsignedShort = UInt16
"16bit无符号整数"
UInt32 = cinttype(c_uint32, "UnsignedInteger")
"32bit无符号整数"
UnsignedInteger = UInt32
"32bit无符号整数"
UInt64 = cinttype(c_uint64, "UnsignedQWord")
"64bit无符号整数"
UnsignedQWord = UInt64
"64bit无符号整数"


def utc(prec: int = 3):
    """获取当前UTC时间戳

    :param prec: 精度，表示小数点后的位数
    :return: 指定精度的UTC时间戳
    """
    return int(time.time() * (10**prec))


def steprange(
    start: Union[int, float], stop: Union[int, float], step: int
) -> List[float]:
    """生成step步长的从start到stop的列表

    :param start: 起始值
    :param stop: 结束值
    :param step: 步长
    :return: 从start到stop的列表

    举个例子

    >>> steprange(0, 10, 5)
    [0, 2.5, 5.0, 7.5, 10]
    """
    if (stop - start) % step != 0:
        return [start + i * (int(stop - start) / step) for i in range(step)][:-1] + [
            stop
        ]
    else:
        return [start + i * (int(stop - start) / (step - 1)) for i in range(step)]


def addrof(obj) -> str:
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
        + f".{int((time.time()%1)*1000):03}"
    )
