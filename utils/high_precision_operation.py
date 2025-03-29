import os, sys, random, math

"""
NoneColdWind做的一个高精度运算类
"""
from typing import Union
class HighPrecisionOperation:
    def __init__(self, basic_num: Union[int, float] = 0):
        sys.set_int_max_str_digits(2147483647)
        self.basic_num = basic_num
    
    def Addition(self, other_num: Union[int, float] = 0):
        if "." in str(self.basic_num) or "." in str(other_num):
            str_1 = str(self.basic_num).split(".")[-1]
            str_2 = str(other_num).split(".")[-1]
            len_1 = len(str_1)
            len_2 = len(str_2)
            if len_1 > len_2:
                a_power_of_ten = int(10 ** len_1)
            else:
                a_power_of_ten = int(10 ** len_2)
            provisional_figure_1 = int(self.basic_num * a_power_of_ten)
            provisional_figure_2 = int(other_num * a_power_of_ten)
            provisional_result = provisional_figure_1 + provisional_figure_2
            result = provisional_result / a_power_of_ten
            return HighPrecisionOperation(result)
        else:
            result = self.basic_num + other_num
            return HighPrecisionOperation(result)
        
    def Subtraction(self, other_num: Union[int, float] = 0):
        if "." in str(self.basic_num) or "." in str(other_num):
            str_1 = str(self.basic_num).split(".")[-1]
            str_2 = str(other_num).split(".")[-1]
            len_1 = len(str_1)
            len_2 = len(str_2)
            if len_1 > len_2:
                a_power_of_ten = int(10 ** len_1)
            else:
                a_power_of_ten = int(10 ** len_2)
            provisional_figure_1 = int(self.basic_num * a_power_of_ten)
            provisional_figure_2 = int(other_num * a_power_of_ten)
            provisional_result = provisional_figure_1 - provisional_figure_2
            result = provisional_result / a_power_of_ten
            return HighPrecisionOperation(result)
        else:
            result = self.basic_num - other_num
            return HighPrecisionOperation(result)
        
    def Multiplication(self, other_num: Union[int, float] = 0):
        if "." in str(self.basic_num) or "." in str(other_num):
            str_1 = str(self.basic_num).split(".")[-1]
            str_2 = str(other_num).split(".")[-1]
            len_1 = len(str_1)
            len_2 = len(str_2)
            if len_1 > len_2:
                a_power_of_ten = int(10 ** len_1)
            else:
                a_power_of_ten = int(10 ** len_2)
            provisional_figure_1 = int(self.basic_num * a_power_of_ten)
            provisional_figure_2 = int(other_num * a_power_of_ten)
            provisional_result = provisional_figure_1 * provisional_figure_2
            result = provisional_result / (a_power_of_ten ** 2)
            return HighPrecisionOperation(result)
        else:
            result = self.basic_num * other_num
            return HighPrecisionOperation(result)
        
    def Division(self, other_num: Union[int, float] = 0):
        if "." in str(self.basic_num) or "." in str(other_num):
            str_1 = str(self.basic_num).split(".")[-1]
            str_2 = str(other_num).split(".")[-1]
            len_1 = len(str_1)
            len_2 = len(str_2)
            if len_1 > len_2:
                a_power_of_ten = int(10 ** len_1)
            else:
                a_power_of_ten = int(10 ** len_2)
            provisional_figure_1 = int(self.basic_num * a_power_of_ten)
            provisional_figure_2 = int(other_num * a_power_of_ten)
            result = provisional_figure_1 / provisional_figure_2
            return HighPrecisionOperation(result)
        else:
            result = self.basic_num / other_num
            return HighPrecisionOperation(result)

    def nThRoot(self, n: int = 3):
        string = ""
        rest = 0
        basic = float(self.basi)
        
    def involution(self, index: int = 1):
        result = self.basic_num ** index
        return HighPrecisionOperation(result)
    
    def HighPrecisionOperationType_conversion_number(self):
        return self.basic_num
    

class HighPrecision:
    def __init__(self, basic_num):
        self.basic_num = basic_num

    def is_integer(self):
        return bool(self.basic_num % 1 == 0)

    def __int__(self):
        return int(self.basic_num)
    
    def __float__(self):
        return float(self.basic_num)
        
    def __add__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        if "." in str(self.basic_num) or "." in str(other_num.basic_num):
            str_1 = str(self.basic_num).split(".")[-1]
            str_2 = str(other_num.basic_num).split(".")[-1]
            len_1 = len(str_1)
            len_2 = len(str_2)
            if len_1 > len_2:
                a_power_of_ten = int(10 ** len_1)
            else:
                a_power_of_ten = int(10 ** len_2)
            provisional_figure_1 = int(self.basic_num * a_power_of_ten)
            provisional_figure_2 = int(other_num.basic_num * a_power_of_ten)
            provisional_result = provisional_figure_1 + provisional_figure_2
            result = provisional_result / a_power_of_ten
            return HighPrecision(result)
        else:
            result = self.basic_num + other_num.basic_num
            return HighPrecision(result)
        
    def __sub__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        if "." in str(self.basic_num) or "." in str(other_num.basic_num):
            str_1 = str(self.basic_num).split(".")[-1]
            str_2 = str(other_num.basic_num).split(".")[-1]
            len_1 = len(str_1)
            len_2 = len(str_2)
            if len_1 > len_2:
                a_power_of_ten = int(10 ** len_1)
            else:
                a_power_of_ten = int(10 ** len_2)
            provisional_figure_1 = int(self.basic_num * a_power_of_ten)
            provisional_figure_2 = int(other_num.basic_num * a_power_of_ten)
            provisional_result = provisional_figure_1 - provisional_figure_2
            result = provisional_result / a_power_of_ten
            return HighPrecision(result)
        else:
            result = self.basic_num - other_num.basic_num
            return HighPrecision(result)
        
    def __mul__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        if "." in str(self.basic_num) or "." in str(other_num.basic_num):
            str_1 = str(self.basic_num).split(".")[-1]
            str_2 = str(other_num.basic_num).split(".")[-1]
            len_1 = len(str_1)
            len_2 = len(str_2)
            if len_1 > len_2:
                a_power_of_ten = int(10 ** len_1)
            else:
                a_power_of_ten = int(10 ** len_2)
            provisional_figure_1 = int(self.basic_num * a_power_of_ten)
            provisional_figure_2 = int(other_num.basic_num * a_power_of_ten)
            provisional_result = provisional_figure_1 * provisional_figure_2
            result = provisional_result / (a_power_of_ten ** 2)
            return HighPrecision(result)
        else:
            result = self.basic_num * other_num.basic_num
            return HighPrecision(result)
        
    def __truediv__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        if "." in str(self.basic_num) or "." in str(other_num.basic_num):
            str_1 = str(self.basic_num).split(".")[-1]
            str_2 = str(other_num.basic_num).split(".")[-1]
            len_1 = len(str_1)
            len_2 = len(str_2)
            if len_1 > len_2:
                a_power_of_ten = int(10 ** len_1)
            else:
                a_power_of_ten = int(10 ** len_2)
            provisional_figure_1 = int(self.basic_num * a_power_of_ten)
            provisional_figure_2 = int(other_num.basic_num * a_power_of_ten)
            result = provisional_figure_1 / provisional_figure_2
            return HighPrecision(result)
        else:
            result = self.basic_num / other_num.basic_num
            return HighPrecision(result)
        

    # 后面的暂且这么写着，等NCW来写具体实现就行

    def __mod__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        return HighPrecision(self.basic_num % other_num.basic_num)
    
    def __pow__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        return HighPrecision(self.basic_num ** other_num.basic_num)
        
    def __div__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        return self.__truediv__(other_num)
    
    def __floordiv__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        return HighPrecision(self.basic_num // other_num.basic_num)
        
    def __pos__(self):
        return HighPrecision(self.basic_num)
    
    def __neg__(self):
        return HighPrecision(-self.basic_num)
    
    def __abs__(self):
        return HighPrecision(abs(self.basic_num))
    
    def __str__(self):
        return str(self.basic_num)
    
    def __repr__(self):
        return F"{self.__class__.__name__}({repr(self.basic_num)})"
    
    def __len__(self):
        return len(str(self.basic_num))
    
    def __lshift__(self, other_num: int):
        if not isinstance(other_num, int):
            other_num = int(other_num)
        is_int = self.basic_num % 1 == 0

        if is_int:
            return HighPrecision(int(self.basic_num) << other_num)
        else:
            raise TypeError(f"无法对浮点数进行位移操作（{self.basic_num}）")
        
    def __rshift__(self, other_num: int):
        if not isinstance(other_num, int):
            other_num = int(other_num)
        is_int = self.basic_num % 1 == 0

        if is_int:
            return HighPrecision(int(self.basic_num) >> other_num)
        else:
            raise TypeError(f"无法对浮点数进行位移操作（{self.basic_num}）")
        
    def __invert__(self):
        is_int = self.basic_num % 1 == 0

        if is_int:
            return HighPrecision(~int(self.basic_num))
        else:
            raise TypeError(f"无法对浮点数进行按位取反操作（{self.basic_num}）")
        
    def __and__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        is_int = self.basic_num % 1 == 0 and other_num.basic_num % 1 == 0

        if is_int:
            return HighPrecision(int(self.basic_num) & int(other_num.basic_num))
        else:
            raise TypeError(f"无法对浮点数进行按位与操作（{self.basic_num}）")
        
    def __or__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        is_int = self.basic_num % 1 == 0 and other_num.basic_num % 1 == 0

        if is_int:
            return HighPrecision(int(self.basic_num) | int(other_num.basic_num))
        else:
            raise TypeError(f"无法对浮点数进行按位或操作（{self.basic_num}）")
        
    def __xor__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        is_int = self.basic_num % 1 == 0 and other_num.basic_num % 1 == 0

        if is_int:
            return HighPrecision(int(self.basic_num) ^ int(other_num.basic_num))
        else:
            raise TypeError(f"无法对浮点数进行按位异或操作（{self.basic_num}）")
    
    def __iadd__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        res = self.__add__(other_num)
        self.basic_num = res.basic_num
        return self
    
    def __isub__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        res = self.__sub__(other_num)
        self.basic_num = res.basic_num
        return self
    
    def __imul__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        res = self.__mul__(other_num)
        self.basic_num = res.basic_num
        return self
    
    def __itruediv__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)

        res = self.__truediv__(other_num)
        self.basic_num = res.basic_num
        return self
    
    def __ifloordiv__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        res = self.__floordiv__(other_num)
        self.basic_num = res.basic_num
        return self
    
    def __imod__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        res = self.__mod__(other_num)
        self.basic_num = res.basic_num
        return self
    
    def __ipow__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        res = self.__pow__(other_num)
        self.basic_num = res.basic_num
        return self
    
    def __iand__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        if not self.is_integer() or not other_num.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        res = self.__and__(other_num)
        self.basic_num = res.basic_num
        return self

    def __ior__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        if not self.is_integer() or not other_num.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        res = self.__or__(other_num)
        self.basic_num = res.basic_num
        return self
    
    def __ixor__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        if not self.is_integer() or not other_num.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        res = self.__xor__(other_num)
        self.basic_num = res.basic_num
        return self
    
    def __ilshift__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        if not self.is_integer() or not other_num.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        res = self.__lshift__(other_num)
        self.basic_num = res.basic_num
        return self

    def __irshift__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        if not self.is_integer() or not other_num.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        res = self.__rshift__(other_num)
        self.basic_num = res.basic_num
        return self
    
    def __radd__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        return self.__add__(other_num)

    def __rsub__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        return self.__sub__(other_num)

    def __rmul__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        return self.__mul__(other_num)
    
    def __rtruediv__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        return other_num.__truediv__(self)
    
    def __rmod__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        return other_num.__mod__(self)
    
    def __rfloordiv__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        return other_num.__floordiv__(self)
    
    def __rpow__(self, other_num: "HighPrecision"):
        if not isinstance(other_num, HighPrecision):
            other_num = HighPrecision(other_num)
        return other_num.__pow__(self)
    
    def __rlshift__(self, other_num: Union["HighPrecision", int]):
        if not self.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        if isinstance(other_num, HighPrecision):
            if not other_num.is_integer():
                raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
            other_num = int(other_num)
        elif isinstance(other_num, float) and not other_num.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        return other_num.__lshift__(int(self))
    
    def __rrshift__(self, other_num: Union["HighPrecision", int]):
        if not self.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        if isinstance(other_num, HighPrecision):
            if not other_num.is_integer():
                raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
            other_num = int(other_num)
        elif isinstance(other_num, float) and not other_num.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        return other_num.__rshift__(int(self))
    
    def __ror__(self, other_num: Union["HighPrecision", int]):
        if not self.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        if isinstance(other_num, HighPrecision):
            if not other_num.is_integer():
                raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
            other_num = int(other_num)
        elif isinstance(other_num, float) and not other_num.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        return other_num.__or__(int(self))
    
    def __rxor__(self, other_num: Union["HighPrecision", int]):
        if not self.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        if isinstance(other_num, HighPrecision):
            if not other_num.is_integer():
                raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
            other_num = int(other_num)
        elif isinstance(other_num, float) and not other_num.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        return other_num.__xor__(int(self))
            
    def __rand__(self, other_num: Union["HighPrecision", int]):
        if not self.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        if isinstance(other_num, HighPrecision):
            if not other_num.is_integer():
                raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
            other_num = int(other_num)
        elif isinstance(other_num, float) and not other_num.is_integer():
            raise TypeError(f"不能对浮点数进行按位运算（{other_num} 和 {self}）")
        return other_num.__and__(int(self))
    
    def nThRoot(self, n: int = 3):
        raise NotImplementedError("还没写完")
        # string = ""
        # rest = 0
        # basic = float(self.basic_num)
        # list_1 = []
        # fpl = 2
        # if n < 0:
        #     basic = 1 / basic
        # elif n == 0:
        #     class MathematicsError(Exception):...
        #     raise MathematicsError("不被允许的数[0次根无法运算]")
        
        # if len(str(int(basic))) % n:
        #     zeros = "0" * (n - (len(str(int(basic))) % n))
        #     basic_num = zeros + str(int(basic))

        # if len(basic_num.split(".")[-1]) % n:
        #     zeros = "0" * (len(basic_num.split(".")[-1]))
        #     basic_num = basic_num + zeros

        # if len(basic_num.split(".")[-1]) / n <= fpl:
        #     t = fpl - len(basic_num.split(".")[-1]) / n
        #     zeros = "0" * (int(t) * 3)
        #     basic_num = basic_num + zeros

        # else:
        #     lfd = [c for c in range(len(basic_num))]
        #     nd = len(str(basic_num.split(".")[-1])) - 3 * fpl
        #     lfd = lfd[:-nd]
        #     basic_num = ""
        #     for i in lfd:
        #         basic_num += i

        # need_td = 10 ** (len(basic_num.split(".")[-1]) / n)
        # basic_str = basic_num.replace(".", "")




    

    
if __name__ == "__main__":
    print(HighPrecision(114.5) + HighPrecision(1.4))
