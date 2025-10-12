"""
所有和算法，数据类型，信息处理，日志记录，系统操作相关的模块

（现在还加了一些数据处理的工具）

这里面都是一堆乱七八糟的东西，感觉__init__也没啥好写的
"""


from .data_ops import *
from .file_ops import *
from .time_ops import *

from .consts import *
from .algorithm import *
from .basetypes import *
from .classobjects import *
from .logger import *
from .settings import *
from .system import *
from .update_check import *
from .functions import *

if __name__ == "__main__":
    Base.log("W", "亻尔女子", "utils.__init__")