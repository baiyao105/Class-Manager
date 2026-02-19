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

    warnings.warn(
        "当前没有配置默认数据和登录模块，正在使用默认数据，"
        "可以参考一下utils/classobjects/bak/default.py和"
        "utils/classobjects/bak/login.py后"
        "在classdatatypes下配置自己的login和default模块",
        stacklevel=2,
        category=RuntimeWarning
    )

from .classdataset import *
from .dataloader import *
from .observers import *  # 一定要放在default后面，observers依赖classdataset，classdataset依赖default
