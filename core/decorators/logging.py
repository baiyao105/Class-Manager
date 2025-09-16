"""日志装饰器

提供函数调用日志和审计日志功能装饰器
"""

import logging
import time
from datetime import datetime
from functools import wraps
from typing import Callable, Optional

from ..events.event_bus import event_bus
from ..events.event_types import Event, EventFactory, EventType


def log_calls(
    level: int = logging.INFO,
    include_args: bool = True,
    include_kwargs: bool = True,
    include_result: bool = False,
    max_arg_length: int = 200,
    logger_name: Optional[str] = None,
):
    """函数调用日志装饰器

    Args:
        level: 日志级别
        include_args: 是否包含位置参数
        include_kwargs: 是否包含关键字参数
        include_result: 是否包含返回结果
        max_arg_length: 参数最大长度
        logger_name: 日志记录器名称

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取日志记录器
            logger = logging.getLogger(logger_name or f"CallLog.{func.__name__}")

            # 准备日志信息
            log_data = {
                "function": func.__name__,
                "timestamp": datetime.utcnow().isoformat(),
                "module": func.__module__,
            }

            # 添加参数信息
            if include_args and args:
                args_str = str(args)
                if len(args_str) > max_arg_length:
                    args_str = args_str[:max_arg_length] + "..."
                log_data["args"] = args_str

            if include_kwargs and kwargs:
                kwargs_str = str(kwargs)
                if len(kwargs_str) > max_arg_length:
                    kwargs_str = kwargs_str[:max_arg_length] + "..."
                log_data["kwargs"] = kwargs_str

            # 记录调用开始
            start_time = time.time()
            logger.log(level, f"调用开始: {func.__name__}", extra=log_data)

            try:
                result = func(*args, **kwargs)

                # 记录调用成功
                end_time = time.time()
                duration = end_time - start_time

                success_data = {**log_data, "duration": duration, "status": "success"}

                if include_result:
                    result_str = str(result)
                    if len(result_str) > max_arg_length:
                        result_str = result_str[:max_arg_length] + "..."
                    success_data["result"] = result_str

                logger.log(level, f"调用成功: {func.__name__} - 耗时: {duration:.3f}秒", extra=success_data)

                return result

            except Exception as e:
                # 记录调用失败
                end_time = time.time()
                duration = end_time - start_time

                error_data = {
                    **log_data,
                    "duration": duration,
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                }

                logger.exception(f"调用失败: {func.__name__} - 耗时: {duration:.3f}秒 - 错误: {e!s}", extra=error_data)

                raise

        return wrapper

    return decorator


def audit_log(
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    user_getter: Optional[Callable] = None,
    resource_id_getter: Optional[Callable] = None,
    include_changes: bool = True,
    publish_event: bool = True,
):
    """审计日志装饰器

    Args:
        action: 操作类型（如：create, update, delete）
        resource_type: 资源类型（如：student, class, achievement）
        user_getter: 用户获取函数
        resource_id_getter: 资源ID获取函数
        include_changes: 是否包含变更信息
        publish_event: 是否发布审计事件

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取审计日志记录器
            logger = logging.getLogger(f"AuditLog.{func.__name__}")

            # 确定操作类型
            actual_action = action or _infer_action_from_function_name(func.__name__)

            # 确定资源类型
            actual_resource_type = resource_type or _infer_resource_type_from_function_name(func.__name__)

            # 获取用户信息
            user_info = None
            if user_getter:
                user_info = user_getter(*args, **kwargs)
            elif args and hasattr(args[0], "current_user"):
                user_info = args[0].current_user

            # 获取资源ID
            resource_id = None
            if resource_id_getter:
                resource_id = resource_id_getter(*args, **kwargs)
            elif args:
                # 尝试从参数中推断资源ID
                for arg in args[1:]:  # 跳过self参数
                    if isinstance(arg, (str, int)) and str(arg).isdigit():
                        resource_id = str(arg)
                        break

            # 记录操作前状态（用于变更追踪）
            before_state = None
            if include_changes and actual_action in ["update", "delete"]:
                try:
                    # 这里可以添加获取操作前状态的逻辑
                    # before_state = get_resource_state(actual_resource_type, resource_id)
                    pass
                except Exception:
                    pass

            # 准备审计日志数据
            audit_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "action": actual_action,
                "resource_type": actual_resource_type,
                "resource_id": resource_id,
                "user": str(user_info) if user_info else "system",
                "function": func.__name__,
                "module": func.__module__,
            }

            try:
                result = func(*args, **kwargs)

                # 记录操作后状态
                after_state = None
                if include_changes and actual_action in ["create", "update"]:
                    try:
                        # 这里可以添加获取操作后状态的逻辑
                        # after_state = get_resource_state(actual_resource_type, resource_id or result.id)
                        pass
                    except Exception:
                        pass

                # 添加变更信息
                if include_changes:
                    audit_data["changes"] = {"before": before_state, "after": after_state}

                # 添加结果信息
                if hasattr(result, "id"):
                    audit_data["result_id"] = str(result.id)

                audit_data["status"] = "success"

                # 记录审计日志
                logger.info(
                    f"审计: {actual_action} {actual_resource_type} - 用户: {audit_data['user']} - 资源: {resource_id}",
                    extra=audit_data,
                )

                # 发布审计事件
                if publish_event:
                    audit_event = Event(
                        type=EventType.USER_ACTION,
                        data=audit_data,
                        source="AuditLog",
                        user_id=str(user_info) if user_info else None,
                    )
                    event_bus.publish(audit_event)

                return result

            except Exception as e:
                # 记录失败的操作
                audit_data.update({"status": "failed", "error": str(e), "error_type": type(e).__name__})

                logger.exception(
                    f"审计: {actual_action} {actual_resource_type} 失败 - 用户: {audit_data['user']} - 错误: {e!s}",
                    extra=audit_data,
                )

                # 发布失败事件
                if publish_event:
                    error_event = EventFactory.create_error_event(
                        f"操作失败: {actual_action} {actual_resource_type}", audit_data, "AuditLog"
                    )
                    event_bus.publish(error_event)

                raise

        return wrapper

    return decorator


def debug_log(include_locals: bool = False, include_stack: bool = False, max_depth: int = 3):
    """调试日志装饰器

    Args:
        include_locals: 是否包含局部变量
        include_stack: 是否包含调用栈
        max_depth: 最大调用栈深度

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(f"Debug.{func.__name__}")

            if not logger.isEnabledFor(logging.DEBUG):
                return func(*args, **kwargs)

            debug_data = {
                "function": func.__name__,
                "module": func.__module__,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # 添加调用栈信息
            if include_stack:
                import traceback

                stack = traceback.extract_stack()[:-1]  # 排除当前帧
                debug_data["call_stack"] = [
                    f"{frame.filename}:{frame.lineno} in {frame.name}" for frame in stack[-max_depth:]
                ]

            # 添加局部变量信息
            if include_locals:
                import inspect

                frame = inspect.currentframe()
                try:
                    caller_locals = frame.f_back.f_locals
                    debug_data["locals"] = {
                        k: str(v)[:100] + ("..." if len(str(v)) > 100 else "")
                        for k, v in caller_locals.items()
                        if not k.startswith("_")
                    }
                finally:
                    del frame

            logger.debug(f"调试: 进入 {func.__name__}", extra=debug_data)

            try:
                result = func(*args, **kwargs)
                logger.debug(f"调试: 退出 {func.__name__} - 成功")
                return result
            except Exception as e:
                logger.debug(f"调试: 退出 {func.__name__} - 异常: {e!s}")
                raise

        return wrapper

    return decorator


def performance_log(slow_threshold: float = 1.0, include_memory: bool = False):
    """性能日志装饰器

    Args:
        slow_threshold: 慢调用阈值（秒）
        include_memory: 是否包含内存使用信息

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(f"Performance.{func.__name__}")

            # 记录开始时间和内存
            start_time = time.time()
            start_memory = None

            if include_memory:
                try:
                    import os

                    import psutil

                    process = psutil.Process(os.getpid())
                    start_memory = process.memory_info().rss
                except ImportError:
                    pass

            try:
                result = func(*args, **kwargs)

                # 计算执行时间
                end_time = time.time()
                duration = end_time - start_time

                # 计算内存使用
                memory_delta = None
                if include_memory and start_memory:
                    try:
                        end_memory = process.memory_info().rss
                        memory_delta = end_memory - start_memory
                    except:
                        pass

                # 准备性能数据
                perf_data = {
                    "function": func.__name__,
                    "duration": duration,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                if memory_delta is not None:
                    perf_data["memory_delta"] = memory_delta
                    perf_data["memory_delta_mb"] = memory_delta / 1024 / 1024

                # 根据执行时间选择日志级别
                if duration > slow_threshold:
                    logger.warning(f"慢调用: {func.__name__} - 耗时: {duration:.3f}秒", extra=perf_data)
                else:
                    logger.debug(f"性能: {func.__name__} - 耗时: {duration:.3f}秒", extra=perf_data)

                return result

            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time

                logger.exception(f"性能: {func.__name__} 执行失败 - 耗时: {duration:.3f}秒 - 错误: {e!s}")
                raise

        return wrapper

    return decorator


def _infer_action_from_function_name(func_name: str) -> str:
    """从函数名推断操作类型

    Args:
        func_name: 函数名

    Returns:
        操作类型
    """
    func_name_lower = func_name.lower()

    if func_name_lower.startswith(("create", "add", "insert", "new")):
        return "create"
    if func_name_lower.startswith(("update", "modify", "edit", "change")):
        return "update"
    if func_name_lower.startswith(("delete", "remove", "del")):
        return "delete"
    if func_name_lower.startswith(("get", "find", "search", "list", "query")):
        return "read"
    return "unknown"


def _infer_resource_type_from_function_name(func_name: str) -> str:
    """从函数名推断资源类型

    Args:
        func_name: 函数名

    Returns:
        资源类型
    """
    func_name_lower = func_name.lower()

    if "student" in func_name_lower:
        return "student"
    if "class" in func_name_lower:
        return "class"
    if "achievement" in func_name_lower:
        return "achievement"
    if "score" in func_name_lower:
        return "score"
    if "user" in func_name_lower:
        return "user"
    return "unknown"
