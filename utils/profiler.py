"""
性能分析工具
"""
import functools
import time
import threading
from collections import defaultdict
from typing import Callable, Literal, TypeVar
from typing_extensions import ParamSpec
from dataclasses import dataclass
from utils.consts import inf
from utils.logger import Logger


_P = ParamSpec("_P")
_R = TypeVar("_R")


@dataclass
class FunctionStats:
    """函数统计信息"""
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = inf
    max_time: float = 0.0
    last_call_time: float = 0.0
    
    @property
    def avg_time(self) -> float:
        """平均耗时"""
        return self.total_time / self.call_count if self.call_count > 0 else 0.0


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self, name: str = "Profiler"):
        self.name = name
        self._stats: dict[str, FunctionStats] = defaultdict(FunctionStats)

        self._lock = threading.Lock()
        self._enabled = True
        self._display_thread: threading.Thread | None = None
        self._display_interval: float = 5.0
        self._should_stop = False
    
    def enable(self):
        """启用性能分析"""
        self._enabled = True
        Logger.log("I", f"性能分析器{self.name}已启用", "PerformanceProfiler")
    
    def disable(self):
        """禁用性能分析"""
        self._enabled = False
        Logger.log("I", f"性能分析器{self.name}已禁用", "PerformanceProfiler")
    
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self._enabled
    
    def profile(self, func_name: str | None = None):
        """
        装饰器，分析函数性能。
        
        :param func_name: 自定义函数名称（默认使用函数名）
        """
        def decorator(func: Callable[_P, _R]) -> Callable[_P, _R]:
            name = func_name or f"{func.__module__}.{func.__qualname__}"
            
            @functools.wraps(func)
            def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                if not self._enabled:
                    return func(*args, **kwargs)
                
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    elapsed = time.perf_counter() - start_time
                    self._record_call(name, elapsed)
            
            return wrapper
        return decorator
    
    def _record_call(self, name: str, elapsed: float):
        """记录函数调用"""
        with self._lock:
            stats = self._stats[name]
            stats.call_count += 1
            stats.total_time += elapsed
            stats.min_time = min(stats.min_time, elapsed)
            stats.max_time = max(stats.max_time, elapsed)
            stats.last_call_time = elapsed
    
    def get_stats(self, sort_by: Literal["total_time", "call_count", "avg_time", "max_time"] = "total_time") -> list[tuple[str, FunctionStats]]:
        """
        获取统计信息
        
        :param sort_by: 排序方式，可选 "total_time", "call_count", "avg_time", "max_time"
        """
        with self._lock:
            items = list(self._stats.items())
            
            if sort_by == "total_time":
                items.sort(key=lambda x: x[1].total_time, reverse=True)
            elif sort_by == "call_count":
                items.sort(key=lambda x: x[1].call_count, reverse=True)
            elif sort_by == "avg_time":
                items.sort(key=lambda x: x[1].avg_time, reverse=True)
            elif sort_by == "max_time":
                items.sort(key=lambda x: x[1].max_time, reverse=True)
            
            return items
    
    def print_stats(self, limit: int = 20, sort_by: Literal["total_time", "call_count", "avg_time", "max_time"] = "total_time"):
        """
        打印统计信息。
        
        :param limit: 显示的函数数量
        :param sort_by: 排序方式，可选 "total_time", "call_count", "avg_time", "max_time"
        """
        stats = self.get_stats(sort_by)[:limit]
        
        Logger.log("I", f"\n{'='*80}", "PerformanceProfiler")
        Logger.log("I", f"性能分析器 '{self.name}' 统计信息 (按 {sort_by} 排序)", "PerformanceProfiler")
        Logger.log("I", f"{'='*80}", "PerformanceProfiler")
        Logger.log("I", f"{'函数名':<50} {'调用次数':>10} {'总耗时(ms)':>12} {'平均耗时(ms)':>12} {'最大耗时(ms)':>12}", "PerformanceProfiler")
        Logger.log("I", f"{'-'*80}", "PerformanceProfiler")
        
        for name, stat in stats:
            total_ms = stat.total_time * 1000
            avg_ms = stat.avg_time * 1000
            max_ms = stat.max_time * 1000
            Logger.log("I", f"{name:<50} {stat.call_count:>10} {total_ms:>12.2f} {avg_ms:>12.2f} {max_ms:>12.2f}", "PerformanceProfiler")
        
        Logger.log("I", f"{'='*80}\n", "PerformanceProfiler")
    
    def reset(self):
        """重置统计信息"""
        with self._lock:
            self._stats.clear()
        Logger.log("I", f"性能分析器{self.name}的统计信息已重置", "PerformanceProfiler")
    
    def start_auto_display(self, interval: float = 5.0):
        """
        启动自动显示统计信息。
        
        :param interval: 显示间隔（秒）
        """
        if self._display_thread and self._display_thread.is_alive():
            Logger.log("W", f"性能分析器{self.name}的自动显示已在运行", "PerformanceProfiler")
            return
        
        self._display_interval = interval
        self._should_stop = False
        self._display_thread = threading.Thread(target=self._auto_display_loop, daemon=True)
        self._display_thread.start()
        Logger.log("I", f"性能分析器{self.name}的自动显示已启动（间隔: {interval}秒）", "PerformanceProfiler")
    
    def stop_auto_display(self):
        """停止自动显示"""
        self._should_stop = True
        if self._display_thread:
            self._display_thread.join(timeout=2.0)
        Logger.log("I", f"性能分析器 '{self.name}' 自动显示已停止", "PerformanceProfiler")
    
    def _auto_display_loop(self):
        """自动显示循环"""
        while not self._should_stop:
            time.sleep(self._display_interval)
            if not self._should_stop:
                self.print_stats(sort_by="total_time")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop_auto_display()
        self.print_stats()


# 全局性能分析器实例
_global_profiler = PerformanceProfiler("Global")



def profile(func_name: str | None = None):
    """
    全局性能分析装饰器
    
    :param func_name: 自定义函数名称
    """
    return _global_profiler.profile(func_name)


def get_global_profiler() -> PerformanceProfiler:
    """获取全局性能分析器"""
    return _global_profiler


def enable_global_profiler():
    """启用全局性能分析器"""
    _global_profiler.enable()


def disable_global_profiler():
    """禁用全局性能分析器"""
    _global_profiler.disable()


def print_global_stats(limit: int = 20, sort_by: Literal["total_time", "call_count", "avg_time", "max_time"] = "total_time"):
    """打印全局统计信息"""
    _global_profiler.print_stats(limit, sort_by)


def reset_global_stats():
    """重置全局统计信息"""
    _global_profiler.reset()


def start_auto_display(interval: float = 5.0):
    """启动自动显示"""
    _global_profiler.start_auto_display(interval)


def stop_auto_display():
    """停止自动显示"""
    _global_profiler.stop_auto_display()
