"""配置模块

提供应用程序的配置管理功能, 包括：
- 应用设置管理
- 常量定义
- 数据库配置
"""

from .constants import *
from .settings import AppSettings, get_settings

__all__ = [
    "AppSettings",
    "get_settings",
    # 常量会通过 * 导入
]
