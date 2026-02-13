"""
一堆有用的装饰器
"""

import functools
from threading import Thread
from typing import Any, Callable

from ..logger import Logger as Base

__all__ = [
    "canbe",
    "skip_exceptions",
    "repeat",
    "run_async",
]


def repeat(count: int):
    """
    装饰器，用于重复执行函数指定次数

    :param count: 重复执行的次数
    :return: 装饰后的函数
    Tip: 如果被装饰的函数有返回值，则返回最后一次执行的结果

    Demo:
    >>> @repeat(3)
    ... def func():
    ...     print("hello")
    >>> func()
    hello
    hello
    hello
    """

    def executor(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            res = None
            for _ in range(count):
                res = func(*args, **kwargs)
            return res
        return wrapper  # type: ignore
    return executor # type: ignore


def run_async(func: Callable[..., Any]) -> Callable[..., None]:
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
    def wrapper(*args: Any, **kwargs: Any) -> None:
        Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper # type: ignore


def canbe(value: Any, _class: type):
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
    except Exception:  # pylint: disable=unused-argument, broad-exception-caught
        return False


def skip_exceptions(func: Callable[..., Any]) -> Callable[..., Any]:
    """装饰器，用于捕获函数执行过程中抛出的异常

    :param func: 要装饰的函数
    :return: 装饰后的函数

    示例:
    >>> @skip_exceptions
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
     at __main__.skip_exceptions.<locals>.wrapper(main.py:114514)
    -----------------------------------------------------------------------
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception:  # pylint: disable=broad-exception-caught
            Base.log_exc(
                f"执行函数{repr(func.__name__)}时捕获到异常",
                f"pass_exceptions -> {func.__name__}",
            )
    return wrapper


