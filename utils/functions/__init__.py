"""
函数功能模块
"""

from .decorators import *
from .excinfo import *
from .prompts import *
from .numbers import *
from .qtutils import *
from .sounds import *

if __name__ == "__main__":

    @repeat(3)
    def f(x):
        print(x**2)

    f(2)
