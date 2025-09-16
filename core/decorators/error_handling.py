"""错误处理装饰器

提供服务层和仓储层的统一错误处理装饰器
"""

import logging
import traceback
from functools import wraps
from typing import Any, Callable, Optional, Union

from ..events.event_bus import event_bus
from ..events.event_types import EventFactory
from ..exceptions.custom_exceptions import (
    BusinessLogicException,
    ClassManagerException,
    DatabaseException,
    RepositoryException,
    ServiceException,
    ValidationException,
)
from ..exceptions.exception_handler import exception_handler


def handle_service_errors(
    reraise: bool = True,
    return_error_info: bool = False,
    log_errors: bool = True,
    publish_events: bool = True,
    service_name: Optional[str] = None,
):
    """服务层错误处理装饰器

    Args:
        reraise: 是否重新抛出异常
        return_error_info: 是否返回错误信息而不是抛出异常
        log_errors: 是否记录错误日志
        publish_events: 是否发布错误事件
        service_name: 服务名称（用于日志和事件）

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 确定服务名称
            actual_service_name = service_name or (
                args[0].__class__.__name__ if args and hasattr(args[0], "__class__") else func.__name__
            )

            try:
                return func(*args, **kwargs)

            except ClassManagerException as e:
                # 处理自定义异常
                error_info = exception_handler.handle_exception(
                    e,
                    {
                        "service_name": actual_service_name,
                        "method_name": func.__name__,
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200],
                    },
                )

                if log_errors:
                    logger = logging.getLogger(f"ServiceError.{actual_service_name}")
                    logger.exception(f"服务方法执行失败: {func.__name__} - {e.message}")

                if publish_events:
                    error_event = EventFactory.create_error_event(
                        f"服务错误: {e.message}", error_info, actual_service_name
                    )
                    event_bus.publish(error_event)

                if return_error_info:
                    return error_info
                if reraise:
                    raise
                return None

            except Exception as e:
                # 处理系统异常，转换为服务异常
                service_error = ServiceException(
                    f"服务方法执行失败: {e!s}", "SERVICE_METHOD_FAILED", actual_service_name, func.__name__
                )

                error_info = exception_handler.handle_exception(
                    service_error,
                    {
                        "service_name": actual_service_name,
                        "method_name": func.__name__,
                        "original_error": str(e),
                        "traceback": traceback.format_exc(),
                    },
                )

                if log_errors:
                    logger = logging.getLogger(f"ServiceError.{actual_service_name}")
                    logger.error(f"服务方法执行异常: {func.__name__} - {e!s}", exc_info=True)

                if publish_events:
                    error_event = EventFactory.create_error_event(f"服务异常: {e!s}", error_info, actual_service_name)
                    event_bus.publish(error_event)

                if return_error_info:
                    return error_info
                if reraise:
                    raise service_error
                return None

        return wrapper

    return decorator


def handle_repository_errors(
    reraise: bool = True,
    return_error_info: bool = False,
    log_errors: bool = True,
    publish_events: bool = True,
    repository_name: Optional[str] = None,
):
    """仓储层错误处理装饰器

    Args:
        reraise: 是否重新抛出异常
        return_error_info: 是否返回错误信息而不是抛出异常
        log_errors: 是否记录错误日志
        publish_events: 是否发布错误事件
        repository_name: 仓储名称（用于日志和事件）

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 确定仓储名称
            actual_repository_name = repository_name or (
                args[0].__class__.__name__ if args and hasattr(args[0], "__class__") else func.__name__
            )

            try:
                return func(*args, **kwargs)

            except ClassManagerException as e:
                # 处理自定义异常
                error_info = exception_handler.handle_exception(
                    e,
                    {
                        "repository_name": actual_repository_name,
                        "method_name": func.__name__,
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200],
                    },
                )

                if log_errors:
                    logger = logging.getLogger(f"RepositoryError.{actual_repository_name}")
                    logger.exception(f"仓储方法执行失败: {func.__name__} - {e.message}")

                if publish_events:
                    error_event = EventFactory.create_error_event(
                        f"仓储错误: {e.message}", error_info, actual_repository_name
                    )
                    event_bus.publish(error_event)

                if return_error_info:
                    return error_info
                if reraise:
                    raise
                return None

            except Exception as e:
                # 处理系统异常，转换为仓储异常
                repository_error = RepositoryException(
                    f"仓储方法执行失败: {e!s}", "REPOSITORY_METHOD_FAILED", actual_repository_name, func.__name__
                )

                error_info = exception_handler.handle_exception(
                    repository_error,
                    {
                        "repository_name": actual_repository_name,
                        "method_name": func.__name__,
                        "original_error": str(e),
                        "traceback": traceback.format_exc(),
                    },
                )

                if log_errors:
                    logger = logging.getLogger(f"RepositoryError.{actual_repository_name}")
                    logger.error(f"仓储方法执行异常: {func.__name__} - {e!s}", exc_info=True)

                if publish_events:
                    error_event = EventFactory.create_error_event(
                        f"仓储异常: {e!s}", error_info, actual_repository_name
                    )
                    event_bus.publish(error_event)

                if return_error_info:
                    return error_info
                if reraise:
                    raise repository_error
                return None

        return wrapper

    return decorator


def handle_exceptions(
    exception_types: Union[type[Exception], tuple] = Exception,
    reraise: bool = True,
    return_error_info: bool = False,
    log_errors: bool = True,
    publish_events: bool = False,
    context_name: Optional[str] = None,
):
    """通用异常处理装饰器

    Args:
        exception_types: 要处理的异常类型
        reraise: 是否重新抛出异常
        return_error_info: 是否返回错误信息而不是抛出异常
        log_errors: 是否记录错误日志
        publish_events: 是否发布错误事件
        context_name: 上下文名称（用于日志和事件）

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 确定上下文名称
            actual_context_name = context_name or (
                args[0].__class__.__name__ if args and hasattr(args[0], "__class__") else func.__name__
            )

            try:
                return func(*args, **kwargs)

            except exception_types as e:
                # 处理指定类型的异常
                if isinstance(e, ClassManagerException):
                    error_info = exception_handler.handle_exception(e)
                else:
                    # 转换为通用异常
                    generic_error = ClassManagerException(f"方法执行失败: {e!s}", "METHOD_EXECUTION_FAILED")
                    error_info = exception_handler.handle_exception(
                        generic_error,
                        {
                            "context_name": actual_context_name,
                            "method_name": func.__name__,
                            "original_error": str(e),
                            "traceback": traceback.format_exc(),
                        },
                    )

                if log_errors:
                    logger = logging.getLogger(f"Error.{actual_context_name}")
                    logger.error(f"方法执行失败: {func.__name__} - {e!s}", exc_info=True)

                if publish_events:
                    error_event = EventFactory.create_error_event(f"执行异常: {e!s}", error_info, actual_context_name)
                    event_bus.publish(error_event)

                if return_error_info:
                    return error_info
                if reraise:
                    raise
                return None

        return wrapper

    return decorator


def safe_execute(default_return: Any = None, log_errors: bool = True, context_name: Optional[str] = None):
    """安全执行装饰器

    确保函数执行不会抛出异常，失败时返回默认值

    Args:
        default_return: 异常时的默认返回值
        log_errors: 是否记录错误日志
        context_name: 上下文名称

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    actual_context_name = context_name or func.__name__
                    logger = logging.getLogger(f"SafeExecute.{actual_context_name}")
                    logger.warning(f"安全执行失败，返回默认值: {func.__name__} - {e!s}")

                return default_return

        return wrapper

    return decorator


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exception_types: Union[type[Exception], tuple] = Exception,
    log_retries: bool = True,
):
    """失败重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff_factor: 退避因子
        exception_types: 需要重试的异常类型
        log_retries: 是否记录重试日志

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time

            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exception_types as e:
                    last_exception = e

                    if attempt < max_retries:
                        if log_retries:
                            logger = logging.getLogger(f"Retry.{func.__name__}")
                            logger.warning(f"第{attempt + 1}次尝试失败，{current_delay}秒后重试: {e!s}")

                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        # 最后一次尝试失败，抛出异常
                        if log_retries:
                            logger = logging.getLogger(f"Retry.{func.__name__}")
                            logger.exception(f"重试{max_retries}次后仍然失败: {e!s}")
                        raise

            # 理论上不会到达这里
            raise last_exception

        return wrapper

    return decorator


# 预定义的常用装饰器
def handle_database_errors(func: Callable) -> Callable:
    """数据库错误处理装饰器"""
    return handle_exceptions(
        exception_types=(DatabaseException, Exception),
        reraise=True,
        log_errors=True,
        publish_events=True,
        context_name="Database",
    )(func)


def handle_validation_errors(func: Callable) -> Callable:
    """验证错误处理装饰器"""
    return handle_exceptions(
        exception_types=ValidationException,
        reraise=True,
        log_errors=True,
        publish_events=False,
        context_name="Validation",
    )(func)


def handle_business_errors(func: Callable) -> Callable:
    """业务逻辑错误处理装饰器"""
    return handle_exceptions(
        exception_types=BusinessLogicException,
        reraise=True,
        log_errors=True,
        publish_events=True,
        context_name="Business",
    )(func)
