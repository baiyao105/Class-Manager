"""应用设置管理

基于Pydantic的现代化配置系统，支持：
- 类型验证
- 环境变量读取
- 配置文件加载
- 默认值管理
"""

import os
from pathlib import Path
from typing import Literal, Tuple, Optional
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class UISettings(BaseSettings):
    """UI相关设置"""
    
    # 窗口设置
    opacity: float = Field(default=0.82, ge=0.1, le=1.0, description="窗口不透明度")
    animation_speed: float = Field(default=1.0, ge=0.1, le=5.0, description="动画速度")
    max_framerate: int = Field(default=60, ge=10, le=144, description="最大帧率")
    use_animate_background: bool = Field(default=False, description="启用动态背景")
    
    # 子窗口偏移
    subwindow_x_offset: int = Field(default=0, description="子窗口X偏移")
    subwindow_y_offset: int = Field(default=0, description="子窗口Y偏移")
    
    # 分数变化颜色设置
    score_up_color_begin: Tuple[int, int, int] = Field(
        default=(0xCA, 0xFF, 0xCA), description="分数上升开始颜色"
    )
    score_up_color_end: Tuple[int, int, int] = Field(
        default=(0x33, 0xCF, 0x6C), description="分数上升结束颜色"
    )
    score_down_color_begin: Tuple[int, int, int] = Field(
        default=(0xFC, 0xB5, 0xB5), description="分数下降开始颜色"
    )
    score_down_color_end: Tuple[int, int, int] = Field(
        default=(0xA9, 0x00, 0x00), description="分数下降结束颜色"
    )
    
    # 闪烁效果设置
    flash_duration_base: int = Field(default=300, ge=100, le=5000, description="基础闪烁时长(ms)")
    flash_duration_step: int = Field(default=100, ge=50, le=1000, description="闪烁时长步进(ms)")
    flash_duration_max: int = Field(default=2000, ge=500, le=10000, description="最大闪烁时长(ms)")
    
    @field_validator('score_up_color_begin', 'score_up_color_end', 'score_down_color_begin', 'score_down_color_end')
    @classmethod
    def validate_color(cls, v):
        """验证颜色值范围"""
        if not all(0 <= c <= 255 for c in v):
            raise ValueError('颜色值必须在0-255范围内')
        return v


class LogSettings(BaseSettings):
    """日志相关设置"""
    
    log_file_path: str = Field(default="class_manager.log", description="日志文件路径")
    log_format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {module}:{function}:{line} - {message}",
        description="日志格式"
    )
    log_keep_linecount: int = Field(default=1000, ge=100, le=10000, description="保留日志行数")
    log_update_interval: float = Field(default=0.5, ge=0.1, le=5.0, description="日志更新间隔(秒)")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="日志级别"
    )


class DatabaseSettings(BaseSettings):
    """数据库相关设置"""
    
    database_url: str = Field(
        default="sqlite:///./class_manager.db", 
        description="数据库连接URL"
    )
    database_echo: bool = Field(default=False, description="是否输出SQL语句")
    pool_size: int = Field(default=5, ge=1, le=20, description="连接池大小")
    max_overflow: int = Field(default=10, ge=0, le=50, description="连接池最大溢出")
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v):
        """验证数据库URL格式"""
        if not v.startswith(('sqlite:///', 'postgresql://', 'mysql://')):
            raise ValueError('不支持的数据库类型')
        return v


class BackupSettings(BaseSettings):
    """备份相关设置"""
    
    auto_save_enabled: bool = Field(default=True, description="启用自动保存")
    auto_save_interval: int = Field(default=300, ge=60, le=3600, description="自动保存间隔(秒)")
    auto_save_path: Literal["folder", "user"] = Field(default="user", description="自动保存路径类型")
    auto_backup_scheme: Literal["none", "only_data", "all"] = Field(
        default="only_data", description="自动备份方案"
    )
    backup_keep_count: int = Field(default=10, ge=1, le=100, description="保留备份数量")


class AppSettings(BaseSettings):
    """应用程序主配置"""
    
    # 应用信息
    app_name: str = Field(default="Class Manager", description="应用名称")
    app_version: str = Field(default="2.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    
    # 用户设置
    current_user: str = Field(default="default_user", description="当前用户")
    
    # 各模块设置
    ui: UISettings = Field(default_factory=UISettings)
    log: LogSettings = Field(default_factory=LogSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    backup: BackupSettings = Field(default_factory=BackupSettings)
    
    # 数据目录
    data_dir: Path = Field(default_factory=lambda: Path("./data"), description="数据目录")
    config_dir: Path = Field(default_factory=lambda: Path("./config"), description="配置目录")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"  # 支持嵌套配置，如 UI__OPACITY=0.9
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保目录存在
        self.data_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
    
    @field_validator('data_dir', 'config_dir')
    @classmethod
    def validate_directories(cls, v):
        """验证目录路径"""
        if isinstance(v, str):
            v = Path(v)
        return v.resolve()
    
    def save_to_file(self, file_path: Optional[Path] = None) -> None:
        """保存配置到文件"""
        if file_path is None:
            file_path = self.config_dir / "settings.json"
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.model_dump_json(indent=2))
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> 'AppSettings':
        """从文件加载配置"""
        if not file_path.exists():
            # 如果文件不存在，返回默认配置并保存
            settings = cls()
            settings.save_to_file(file_path)
            return settings
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read().strip()
        
        if not data:
            # 如果文件为空，创建默认配置
            settings = cls()
            settings.save_to_file(file_path)
            return settings
        
        return cls.model_validate_json(data)


# 全局设置实例
_settings: Optional[AppSettings] = None


@lru_cache()
def get_settings() -> AppSettings:
    """获取全局设置实例（单例模式）"""
    global _settings
    if _settings is None:
        config_file = Path("./config/settings.json")
        _settings = AppSettings.load_from_file(config_file)
    return _settings


def reload_settings() -> AppSettings:
    """重新加载设置"""
    global _settings
    get_settings.cache_clear()
    _settings = None
    return get_settings()