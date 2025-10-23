"""
关于格式化异常信息的函数。

特别地，这个包被从functions包独立出来了，目的是防止循环调用

（utils.logger调用了这个，但是我们还是不希望logger有任何依赖）

（后续想想怎么改吧）
"""

import inspect
from collections.abc import Callable

# 还是type: ignore 大神（


def get_function_namespace(func) -> str:
    """
    获取函数的命名空间

    :param func: 函数对象
    :return: 函数的命名空间字符串
    """
    module = inspect.getmodule(func)
    if not hasattr(func, "__module__"):
        try:
            return func.__qualname__  # type: ignore
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            try:
                return func.__name__  # type: ignore
            except BaseException as unused:  # pylint: disable=broad-exception-caught
                if isinstance(func, property):
                    return str(func.fget.__qualname__)
                if isinstance(func, classmethod):
                    return str(func.__func__.__qualname__)  # type: ignore
                try:
                    return func.__class__.__qualname__  # type: ignore
                except BaseException as unused_2:  # pylint: disable=broad-exception-caught
                    return func.__class__.__name__  # type: ignore
    if module is None:
        module_name = (  # type: ignore
            func.__self__.__module__ if hasattr(func, "__self__") else func.__module__  # type: ignore
        )
    else:
        module_name = module.__name__

    return f"{module_name}.{func.__qualname__}"  # type: ignore


def format_exc_like_java(exc: BaseException) -> list[str]:
    "不是我做这东西有啥用啊"
    result = [
        f"{get_function_namespace(exc.__class__)}: " + (str(exc) if str(exc).strip() else "no further information"),
        "Stacktrace:",
    ]
    tb = exc.__traceback__
    while tb is not None:
        frame = tb.tb_frame
        filename = frame.f_code.co_filename
        filename_strip = filename
        lineno = tb.tb_lineno
        funcname = frame.f_code.co_name
        _locals = frame.f_locals.copy()
        instance = None
        method_obj = None
        for i in _locals.values():
            if isinstance(i, object) and hasattr(i, "__class__"):
                instance = i
                class_obj = instance.__class__
                method_obj = getattr(class_obj, funcname, None)
                if method_obj:
                    break
        if instance and method_obj:
            full_path = get_function_namespace(method_obj)
            result.append(f"  at {full_path}({filename_strip}:{lineno})")
        else:
            func_obj = frame.f_globals.get(funcname) or frame.f_locals.get(funcname)
            if func_obj:
                qualname = get_function_namespace(func_obj)
                result.append(f"  at {qualname}({filename_strip}:{lineno})")
        tb = tb.tb_next
    return result


def get_function_module(func: object | Callable) -> str:
    "获取函数的模块"
    module = inspect.getmodule(func)
    if module is None:
        module_name = (  # type: ignore
            func.__self__.__module__ if hasattr(func, "__self__") else func.__module__  # type: ignore
        )
    else:
        module_name = module.__name__
    return module_name  # type: ignore
