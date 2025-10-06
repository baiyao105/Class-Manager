"""全局配置模型扩展
"""

import json
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .settings import AppSettings


class SystemConfig(BaseModel):
    """系统配置"""
    language: str = Field(default="zh_CN", description="语言设置")
    auto_start: bool = Field(default=False, description="开机自启动")
    auto_update: bool = Field(default=True, description="自动检查更新")
    update_channel: str = Field(default="stable", description="更新通道")
    theme: str = Field(default="auto", description="主题模式")


class DataManagementConfig(BaseModel):
    """数据管理配置"""
    enable_database_splitting: bool = Field(default=True, description="启用数据库拆分")
    max_database_size_mb: int = Field(default=100, ge=10, le=1000, description="数据库最大大小(MB)")
    split_threshold_records: int = Field(default=10000, ge=1000, description="拆分阈值记录数")


class DebugConfig(BaseModel):
    """调试配置"""

    enable_auto_archive: bool = Field(default=False, description="启用自动归档(调试)")
    archive_threshold_records: int = Field(default=50000, ge=10000, description="归档阈值记录数")
    archive_old_data_days: int = Field(default=365, ge=30, description="归档旧数据天数")
    enable_log_writing: bool = Field(default=True, description="启用日志写入")
    log_cleanup_days: int = Field(default=30, ge=7, description="定时删除日志天数")
    debug_log_level: str = Field(default="INFO", description="调试日志级别")
    hot_reload: bool = Field(default=False, description="热重载")


class SecurityConfig(BaseModel):
    """安全配置"""

    enable_data_encryption: bool = Field(default=False, description="启用数据加密")
    encryption_algorithm: str = Field(default="AES-256", description="加密算法")
    backup_encryption: bool = Field(default=True, description="备份加密")
    backup_password_required: bool = Field(default=False, description="备份密码保护")


class GlobalConfig(BaseSettings):
    """全局配置模型"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__", case_sensitive=False, extra="allow"
    )

    # 继承原有配置
    app: AppSettings = Field(default_factory=AppSettings)

    # 新增配置模块
    system: SystemConfig = Field(default_factory=SystemConfig)
    data_management: DataManagementConfig = Field(default_factory=DataManagementConfig)
    debug: DebugConfig = Field(default_factory=DebugConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    # 自定义全局配置
    custom_settings: dict[str, str | int | float | bool] = Field(default_factory=dict, description="自定义全局配置")

    def save_to_file(self, file_path: Path | None = None) -> None:
        """保存配置到文件"""
        if file_path is None:
            file_path = Path("./data/config.json")

        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def load_from_file(cls, file_path: Path | None = None) -> "GlobalConfig":
        """从文件加载配置"""
        if file_path is None:
            file_path = Path("./data/config.json")

        if not file_path.exists():
            # 如果文件不存在，创建默认配置
            config = cls()
            config.save_to_file(file_path)
            return config

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        return cls.model_validate(data)

    def update_setting(self, key_path: str, value: str | int | float | bool) -> None:
        """更新配置项

        Args:
            key_path: 配置路径，如 "system.language" 或 "custom_global_settings.my_key"
            value: 新值
        """
        keys = key_path.split(".")
        obj = self

        # 导航到目标对象
        for key in keys[:-1]:
            if hasattr(obj, key):
                obj = getattr(obj, key)
            elif isinstance(obj, dict):
                obj = obj[key]
            else:
                raise ValueError(f"无效的配置路径: {key_path}")

        # 设置值
        final_key = keys[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
        elif isinstance(obj, dict):
            obj[final_key] = value
        else:
            raise ValueError(f"无效的配置路径: {key_path}")

    def get_setting(self, key_path: str, default=None):
        """获取配置项"""
        keys = key_path.split(".")
        obj = self

        try:
            for key in keys:
                if hasattr(obj, key):
                    obj = getattr(obj, key)
                elif isinstance(obj, dict):
                    obj = obj[key]
                else:
                    return default
            return obj
        except (KeyError, AttributeError):
            return default


# 全局配置管理器
class GlobalConfigManager:
    """全局配置管理器"""

    _config: GlobalConfig | None = None

    @classmethod
    def get_config(cls) -> GlobalConfig:
        """获取全局配置"""
        if cls._config is None:
            cls._config = GlobalConfig.load_from_file()
        return cls._config

    @classmethod
    def reload_config(cls) -> GlobalConfig:
        """重新加载全局配置"""
        cls._config = None
        return cls.get_config()

    @classmethod
    def save_config(cls) -> None:
        """保存全局配置"""
        if cls._config is not None:
            cls._config.save_to_file()

    @classmethod
    def update_setting(cls, key_path: str, value: str | int | float | bool) -> None:
        """更新配置项并保存"""
        config = cls.get_config()
        config.update_setting(key_path, value)
        cls.save_config()

    @classmethod
    def get_setting(cls, key_path: str, default=None):
        """获取配置项"""
        config = cls.get_config()
        return config.get_setting(key_path, default)
