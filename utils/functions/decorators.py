"""
一堆有用的装饰器
"""

import sys
import functools
from threading import Thread
from typing import Literal, Union, List


from utils.logger import Logger as Base





def repeat(count):
    """
    装饰器，用于重复执行函数指定次数

    :param count: 重复执行的次数
    :return: 装饰后的函数

    Demo:
    >>> @repeat(3)
    ... def func():
    ...     print("hello")
    >>> func()
    hello
    hello
    hello
    """
    def executor(func):
        def wrapper(*args, **kwargs):
            for _ in range(count):
                func(*args, **kwargs)
        return wrapper
    return executor


def run_async(func):
    """
    装饰器，用于将函数异步执行

    :param func: 要装饰的函数
    :return: 装饰后的函数

    Demo:
    >>> @run_async
    ... def func():
    ...     print("hello")
    >>> func()
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper



def canbe(value, _class:type):
    """
    检查一个值是否可以转换为指定类型
    
    :param value: 要检查的值
    :param _class: 目标类型
    :return: 如果可以转换则返回True，否则返回False
    
    示例: canbe("11.4514", float) == True
    """
    try:
        _class(value)
        return True
    except Exception as unused: # pylint: disable=unused-argument, broad-exception-caught
        return False



def pass_exceptions(func):
    """装饰器，用于捕获函数执行过程中抛出的异常
    
    :param func: 要装饰的函数
    :return: 装饰后的函数
    
    示例:
    >>> @pass_exceptions
    ... def func():
    ...     raise Exception("错误示例")

    >>> func()
    ---------------------------ExceptionCaught-----------------------------
    执行函数'func'时捕获到异常
    -----------------------------------------------------------------------
    Traceback (most recent call last):
     __错误信息__
       return func(*args, **kwargs)
     __错误信息__
       raise Exception("错误示例")
    Exception: 错误示例
    -----------------------------------------------------------------------
    builtins.Exception: 错误示例
    Stacktrace:
     at __main__.pass_exceptions.<locals>.wrapper(main.py:114514)
    -----------------------------------------------------------------------
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseException as unused:    # pylint: disable=broad-exception-caught, broad-exception-caught
            Base.log_exc(f"执行函数{repr(func.__name__)}时捕获到异常", f"pass_exceptions -> {func.__name__}")

    return wrapper

def exc_info_short(desc:str="出现了错误：", level:Literal["I", "W", "E"]="E"):
    "简单报一句错"
    Base.log(level, f"{desc}  "
                    f"[{sys.exc_info()[1].__class__.__name__}] "
                    f"{sys.exc_info()[1].args[0] if sys.exc_info()[1].args else ''}")
