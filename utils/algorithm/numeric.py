"""
数字类型
"""

import math
from typing import Union, Optional, Any
from ctypes import (c_int, c_int8, c_int16, c_int32, c_int64, 
                    c_uint, c_uint8, c_uint16, c_uint32, c_uint64)



inf = math.inf
nan = math.nan

CIntegerType = Union[int, c_int, c_uint,
                c_int8, c_int16, c_int32, c_int64, 
                c_uint8, c_uint16, c_uint32, c_uint64]

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
            except (ValueError, TypeError) as unused:
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


Int8 = cinttype(c_int8,   "Byte")
"8bit整数"
Byte = Int8
"字节长整数(8bit)"
Int16 = cinttype(c_int16,  "Short")
"16bit整数"
Short = Int16
"16bit整数"
Int32 = cinttype(c_int32,  "Integer")
"32bit整数"
Integer = Int32
"32bit整数"
Int64 = cinttype(c_int64,  "Qword")
"64bit整数"
QWord = Int64
"64bit整数"
UInt8 = cinttype(c_uint8,  "UnsignedByte")
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


