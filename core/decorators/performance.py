"""性能监控装饰器

提供性能监控、缓存和限流等功能装饰器
"""

import hashlib
import json
import logging
import time
from collections import defaultdict, deque
from functools import wraps
from threading import Lock
from typing import Any, Callable, Optional

# 性能统计存储
performance_stats = defaultdict(list)
stats_lock = Lock()

# 缓存存储
cache_storage = {}
cache_lock = Lock()

# 限流存储
rate_limit_storage = defaultdict(lambda: deque())
rate_limit_lock = Lock()


def monitor_performance(
    log_slow_calls: bool = True, slow_threshold: float = 1.0, collect_stats: bool = True, log_all_calls: bool = False
):
    """性能监控装饰器

    Args:
        log_slow_calls: 是否记录慢调用
        slow_threshold: 慢调用阈值（秒）
        collect_stats: 是否收集统计信息
        log_all_calls: 是否记录所有调用

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                raise
            finally:
                end_time = time.time()
                duration = end_time - start_time

                # 记录日志
                logger = logging.getLogger(f"Performance.{func.__name__}")

                if log_all_calls or (log_slow_calls and duration > slow_threshold):
                    if success:
                        logger.info(f"函数执行完成: {func.__name__} - 耗时: {duration:.3f}秒")
                    else:
                        logger.warning(f"函数执行失败: {func.__name__} - 耗时: {duration:.3f}秒 - 错误: {error}")

                # 收集统计信息
                if collect_stats:
                    with stats_lock:
                        performance_stats[func.__name__].append(
                            {"timestamp": start_time, "duration": duration, "success": success, "error": error}
                        )

                        # 保持最近1000条记录
                        if len(performance_stats[func.__name__]) > 1000:
                            performance_stats[func.__name__] = performance_stats[func.__name__][-1000:]

            return result

        return wrapper

    return decorator


def cache_result(
    ttl: Optional[float] = None,
    max_size: int = 128,
    key_func: Optional[Callable] = None,
    ignore_args: Optional[list] = None,
):
    """结果缓存装饰器

    Args:
        ttl: 缓存生存时间（秒），None表示永不过期
        max_size: 最大缓存条目数
        key_func: 自定义缓存键生成函数
        ignore_args: 忽略的参数索引列表

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 过滤忽略的参数
                filtered_args = args
                if ignore_args:
                    filtered_args = tuple(arg for i, arg in enumerate(args) if i not in ignore_args)

                # 生成哈希键
                key_data = {"func_name": func.__name__, "args": filtered_args, "kwargs": kwargs}
                key_str = json.dumps(key_data, sort_keys=True, default=str)
                cache_key = hashlib.md5(key_str.encode()).hexdigest()

            current_time = time.time()

            with cache_lock:
                # 检查缓存
                if cache_key in cache_storage:
                    cache_entry = cache_storage[cache_key]

                    # 检查是否过期
                    if ttl is None or (current_time - cache_entry["timestamp"]) < ttl:
                        logger = logging.getLogger(f"Cache.{func.__name__}")
                        logger.debug(f"缓存命中: {func.__name__}")
                        return cache_entry["result"]
                    # 过期，删除缓存
                    del cache_storage[cache_key]

                # 缓存未命中，执行函数
                result = func(*args, **kwargs)

                # 存储结果
                cache_storage[cache_key] = {"result": result, "timestamp": current_time}

                # 检查缓存大小限制
                if len(cache_storage) > max_size:
                    # 删除最旧的条目
                    oldest_key = min(cache_storage.keys(), key=lambda k: cache_storage[k]["timestamp"])
                    del cache_storage[oldest_key]

                logger = logging.getLogger(f"Cache.{func.__name__}")
                logger.debug(f"缓存存储: {func.__name__}")

                return result

        return wrapper

    return decorator


def rate_limit(max_calls: int, time_window: float, per_user: bool = False, key_func: Optional[Callable] = None):
    """限流装饰器

    Args:
        max_calls: 时间窗口内最大调用次数
        time_window: 时间窗口（秒）
        per_user: 是否按用户限流
        key_func: 自定义限流键生成函数

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()

            # 生成限流键
            if key_func:
                limit_key = key_func(*args, **kwargs)
            elif per_user:
                # 假设第一个参数包含用户信息
                user_id = getattr(args[0], "user_id", "anonymous") if args else "anonymous"
                limit_key = f"{func.__name__}:{user_id}"
            else:
                limit_key = func.__name__

            with rate_limit_lock:
                call_times = rate_limit_storage[limit_key]

                # 清理过期的调用记录
                while call_times and current_time - call_times[0] > time_window:
                    call_times.popleft()

                # 检查是否超过限制
                if len(call_times) >= max_calls:
                    logger = logging.getLogger(f"RateLimit.{func.__name__}")
                    logger.warning(f"限流触发: {func.__name__} - 键: {limit_key}")

                    from ..exceptions.custom_exceptions import BusinessLogicException

                    raise BusinessLogicException(
                        f"调用频率过高，请稍后再试。限制: {max_calls}次/{time_window}秒", "RATE_LIMIT_EXCEEDED"
                    )

                # 记录本次调用
                call_times.append(current_time)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def timeout(seconds: float):
    """超时装饰器

    Args:
        seconds: 超时时间（秒）

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal

            def timeout_handler(signum, frame):
                from ..exceptions.custom_exceptions import BusinessLogicException

                raise BusinessLogicException(f"函数执行超时: {func.__name__} (>{seconds}秒)", "EXECUTION_TIMEOUT")

            # 设置超时信号
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds))

            try:
                result = func(*args, **kwargs)
            finally:
                # 恢复原信号处理器
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            return result

        return wrapper

    return decorator


def async_execute(executor=None):
    """异步执行装饰器

    Args:
        executor: 线程池执行器

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from concurrent.futures import ThreadPoolExecutor

            if executor:
                future = executor.submit(func, *args, **kwargs)
            else:
                with ThreadPoolExecutor(max_workers=1) as default_executor:
                    future = default_executor.submit(func, *args, **kwargs)

            return future

        return wrapper

    return decorator


# 性能统计工具函数
def get_performance_stats(func_name: Optional[str] = None) -> dict[str, Any]:
    """获取性能统计信息

    Args:
        func_name: 函数名称，None表示获取所有函数的统计

    Returns:
        性能统计字典
    """
    with stats_lock:
        if func_name:
            if func_name not in performance_stats:
                return {}

            stats = performance_stats[func_name]
        else:
            stats = []
            for func_stats in performance_stats.values():
                stats.extend(func_stats)

        if not stats:
            return {}

        # 计算统计信息
        durations = [s["duration"] for s in stats]
        success_count = sum(1 for s in stats if s["success"])

        return {
            "total_calls": len(stats),
            "success_calls": success_count,
            "error_calls": len(stats) - success_count,
            "success_rate": success_count / len(stats) if stats else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "total_duration": sum(durations),
        }


def clear_performance_stats(func_name: Optional[str] = None) -> None:
    """清除性能统计信息

    Args:
        func_name: 函数名称，None表示清除所有统计
    """
    with stats_lock:
        if func_name:
            performance_stats.pop(func_name, None)
        else:
            performance_stats.clear()


def clear_cache(func_name: Optional[str] = None) -> None:
    """清除缓存

    Args:
        func_name: 函数名称，None表示清除所有缓存
    """
    with cache_lock:
        if func_name:
            # 清除特定函数的缓存
            keys_to_remove = [k for k in cache_storage if func_name in k]
            for key in keys_to_remove:
                del cache_storage[key]
        else:
            cache_storage.clear()


def get_cache_stats() -> dict[str, Any]:
    """获取缓存统计信息

    Returns:
        缓存统计字典
    """
    with cache_lock:
        current_time = time.time()

        return {
            "total_entries": len(cache_storage),
            "cache_size_bytes": sum(len(str(entry)) for entry in cache_storage.values()),
            "oldest_entry_age": current_time
            - min((entry["timestamp"] for entry in cache_storage.values()), default=current_time),
            "newest_entry_age": current_time
            - max((entry["timestamp"] for entry in cache_storage.values()), default=current_time),
        }
