from .class_config import ClassConfig, ClassConfigManager, QuickBarConfig, SortingConfig

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

# 统一配置接口
from .conf import (
    ConfigManager,
    get_config,
    get_merged_config,
    get_conf_manager,
    reload_conf_manager,
    set_config,
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
    "QuickBarConfig",
    "ScoreTemplateConfig",
    "SecurityConfig",
    "SortingConfig",
    "SystemConfig",
    "TemplateManager",
    "UISettings",
    "clear_template_manager_cache",
    "get_config",
    "get_merged_config",
    "get_settings",
    "get_template_manager",
    "get_conf_manager",
    "reload_settings",
    "reload_conf_manager",
    "set_config",
]
