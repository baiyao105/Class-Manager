"""
配置模块
提供统一的配置管理功能
"""

# 原有配置
# 班级配置
from .class_config import ClassConfig, ClassConfigManager, QuickBarConfig, SortingConfig

# 统一配置接口
from .conf import (
    ConfigManager,
    get_conf_manager,
    get_config,
    get_merged_config,
    reload_conf_manager,
    set_config,
)

# 全局配置
from .global_config import (
    DataManagementConfig,
    DebugConfig,
    GlobalConfig,
    GlobalConfigManager,
    SecurityConfig,
    SystemConfig,
)
from .settings import (
    AppSettings,
    BackupSettings,
    DatabaseSettings,
    LogSettings,
    UISettings,
    get_settings,
    reload_settings,
)

# 模板配置
from .template_config import (
    AchievementTemplateConfig,
    ScoreTemplateConfig,
    TemplateManager,
    clear_template_manager_cache,
    get_template_manager,
)

__all__ = [
    "AchievementTemplateConfig",
    # 原有配置
    "AppSettings",
    "BackupSettings",
    "ClassConfig",
    "ClassConfigManager",
    "DataManagementConfig",
    "DatabaseSettings",
    "DebugConfig",
    "GlobalConfig",
    "GlobalConfigManager",
    "LogSettings",
    # 班级配置
    "QuickBarConfig",
    # 模板配置
    "ScoreTemplateConfig",
    "SecurityConfig",
    "SortingConfig",
    # 全局配置
    "SystemConfig",
    "TemplateManager",
    "UISettings",
    # 统一配置接口
    "UnifiedConfigManager",
    "clear_template_manager_cache",
    "get_conf_manager",
    "get_config",
    "get_merged_config",
    "get_settings",
    "get_template_manager",
    "reload_conf_manager",
    "reload_settings",
    "set_config",
]
