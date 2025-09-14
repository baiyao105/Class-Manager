"""日志工具模块

基于loguru实现的日志系统，提供统一的日志配置和管理。
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

# 默认日志配置
DEFAULT_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

DEFAULT_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} - "
    "{message}"
)

class LoggerManager:
    """日志管理器"""
    
    def __init__(self):
        self._configured = False
        self._handlers = {}
    
    def setup_logger(
        self,
        name: str = "class_manager",
        level: str = "INFO",
        log_dir: Optional[Path] = None,
        console_output: bool = True,
        file_output: bool = True,
        rotation: str = "10 MB",
        retention: str = "30 days",
        compression: str = "zip",
        **kwargs
    ) -> None:
        """配置日志系统
        
        Args:
            name: 日志器名称
            level: 日志级别
            log_dir: 日志文件目录
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            rotation: 日志轮转大小
            retention: 日志保留时间
            compression: 压缩格式
        """
        if self._configured:
            return
            
        # 移除默认处理器
        logger.remove()
        
        # 控制台输出
        if console_output:
            console_level = kwargs.get('console_level', level)
            logger.add(
                sys.stderr,
                format=DEFAULT_LOG_FORMAT,
                level=console_level,
                colorize=True,
                backtrace=True,
                diagnose=True
            )
            self._handlers['console'] = True
        
        # 文件输出
        if file_output:
            if log_dir is None:
                log_dir = Path("logs")
            
            log_dir = Path(log_dir)
            log_dir.mkdir(exist_ok=True)
            
            # 普通日志文件
            log_file = log_dir / f"{name}.log"
            logger.add(
                str(log_file),
                format=DEFAULT_FILE_FORMAT,
                level=level,
                rotation=rotation,
                retention=retention,
                compression=compression,
                encoding="utf-8",
                backtrace=True,
                diagnose=True
            )
            
            # 错误日志文件
            error_file = log_dir / f"{name}_error.log"
            logger.add(
                str(error_file),
                format=DEFAULT_FILE_FORMAT,
                level="ERROR",
                rotation=rotation,
                retention=retention,
                compression=compression,
                encoding="utf-8",
                backtrace=True,
                diagnose=True
            )
            
            self._handlers['file'] = str(log_file)
            self._handlers['error_file'] = str(error_file)
        
        self._configured = True
        logger.info(f"日志系统初始化完成 - 名称: {name}, 级别: {level}")
    
    def get_logger(self, name: Optional[str] = None):
        """获取日志器实例
        
        Args:
            name: 日志器名称
            
        Returns:
            配置好的日志器实例
        """
        if not self._configured:
            self.setup_logger()
        
        if name:
            return logger.bind(name=name)
        return logger
    
    def add_file_handler(
        self,
        file_path: str,
        level: str = "INFO",
        format_str: Optional[str] = None,
        **kwargs
    ) -> None:
        """添加文件处理器
        
        Args:
            file_path: 文件路径
            level: 日志级别
            format_str: 格式字符串
        """
        if format_str is None:
            format_str = DEFAULT_FILE_FORMAT
            
        logger.add(
            file_path,
            format=format_str,
            level=level,
            encoding="utf-8",
            **kwargs
        )
        
        self._handlers[f'custom_{file_path}'] = file_path
        logger.info(f"添加文件处理器: {file_path}")
    
    def remove_handler(self, handler_id: int) -> None:
        """移除处理器
        
        Args:
            handler_id: 处理器ID
        """
        logger.remove(handler_id)
    
    def get_handlers_info(self) -> Dict[str, Any]:
        """获取处理器信息
        
        Returns:
            处理器信息字典
        """
        return self._handlers.copy()

# 全局日志管理器实例
_logger_manager = LoggerManager()

# 便捷函数
def setup_logger(**kwargs) -> None:
    """设置日志系统
    
    Args:
        **kwargs: 传递给LoggerManager.setup_logger的参数
    """
    _logger_manager.setup_logger(**kwargs)

def get_logger(name: Optional[str] = None):
    """获取日志器实例
    
    Args:
        name: 日志器名称
        
    Returns:
        配置好的日志器实例
    """
    return _logger_manager.get_logger(name)

def add_file_handler(file_path: str, **kwargs) -> None:
    """添加文件处理器
    
    Args:
        file_path: 文件路径
        **kwargs: 其他参数
    """
    _logger_manager.add_file_handler(file_path, **kwargs)

# 创建默认日志器
app_logger = get_logger("class_manager")

# 导出的函数和类
__all__ = [
    "LoggerManager",
    "setup_logger",
    "get_logger",
    "add_file_handler",
    "app_logger",
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_FILE_FORMAT"
]