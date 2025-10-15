"""
算法包。

目前里面没有什么很复杂的算法...就是纯应用
"""

# try:
from .datatypes import *
from .high_precision import *
from .keyorder import *
from .numeric import *

# except ImportError:
#     from datatypes import *
#     from high_precision import *
#     from keyorder import *
#     from numeric import *

if __name__ == "__main__":
    print(Int8(127) + Int8(1))
