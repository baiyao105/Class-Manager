"""
所有和算法，数据类型，信息处理，日志记录，系统操作相关的模块

这里面都是一堆乱七八糟的东西，感觉__init__也没啥好写的
"""

from .consts import *
from .algorithm import *
from .basetypes import *
from .classdatatypes import *
from .classobjects import *
from .logger import *
from .settings import *
from .dataloader import *
from .system import *
from .update_check import *
from .functions import *

if __name__ == "__main__":
    Base.log("W", "亻尔女子", "utils.__init__")