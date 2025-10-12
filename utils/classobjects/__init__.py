"""
班级数据类型包。

虽然分片了，但是调用依赖还是有点抽象（）

目前事件总线还没改，后面打算用pydispatch来做（？
"""


import warnings

from .objects import *
try:
    from .default import *
    from .login import *
except:
    from .bak.default import *
    from .bak.login import *
    warnings.warn("当前没有配置默认数据和登录模块，正在使用默认数据，"
                    "可以参考一下classdatatypes/bak/default.py和"
                    "classdatatypes/bak/login.py后"
                    "在进行classdatatypes下配置自己的login和default模块",
                    category=RuntimeWarning)

from .observers import * # 一定要放在default后面，observers依赖classobj，classobj依赖default
from .classobj import *
from .dataloader import *
