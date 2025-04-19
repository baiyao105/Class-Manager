"""
算法文件
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
