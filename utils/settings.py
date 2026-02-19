"""
设置对象。
"""
from __future__ import annotations

import os
import pickle
import dill as pickle # pyright: ignore[reportMissingTypeStubs, reportDuplicateImport]
from typing import Any, Literal, Dict
from types import FunctionType, MethodType

from .basetypes import Base
from .update_check import CLIENT_VERSION, CLIENT_VERSION_CODE


class SettingsInfo:
    """设置信息类，用于管理和存储应用程序的配置参数"""

    glob: "SettingsInfo"

    def __init__(self, **kwargs: Dict[str, Any]):
        """初始化设置信息对象

        :param kwargs: 键值对形式的初始设置参数
        """
        self.reset_settings()
        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def get_global_settings():
        if not SettingsInfo.glob:
            SettingsInfo.glob = SettingsInfo()
        return SettingsInfo.glob

    def reset_settings(self) -> "SettingsInfo":
        """重置所有设置参数为默认值

        :return: 重置后的设置信息对象
        """

        if not hasattr(self, "client_version"):
            self.client_version = CLIENT_VERSION
            self.client_version_code = CLIENT_VERSION_CODE

        self.opacity = 0.82
        self.score_up_color_mixin_begin: tuple[int, int, int] = (0xCA, 0xFF, 0xCA)
        self.score_up_color_mixin_end: tuple[int, int, int] = (0x33, 0xCF, 0x6C)
        self.score_up_color_mixin_step: int = 15
        self.score_up_color_mixin_start: int = 2
        self.score_up_flash_framelength_base: int = 300
        self.score_up_flash_framelength_step: int = 100
        self.score_up_flash_framelength_max: int = 2000

        self.score_down_color_mixin_begin: tuple[int, int, int] = (0xFC, 0xB5, 0xB5)
        self.score_down_color_mixin_end: tuple[int, int, int] = (0xA9, 0x00, 0x00)
        self.score_down_color_mixin_step: int = 15
        self.score_down_color_mixin_start: int = 2
        self.score_down_flash_framelength_base: int = 300
        self.score_down_flash_framelength_step: int = 100
        self.score_down_flash_framelength_max: int = 2000

        self.log_file_path: str = "class_manager.log"
        self.log_format: str = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {module}:{function}:{line} - {message}"
        self.log_keep_linecount: int = 100
        self.log_update_interval: float = 0.1

        self.auto_save_enabled: bool = True
        self.auto_save_interval: float = 300.0
        self.auto_save_path: Literal["folder", "user"] = "folder"
        self.auto_backup_scheme: Literal["none", "only_data", "all"] = "none"

        self.animation_speed: float = 1.0
        self.subwindow_x_offset: int = 0
        self.subwindow_y_offset: int = 0
        self.use_animate_background: bool = False
        self.max_framerate: int = 60
        return self

    def save_to(self, file_path: str) -> SettingsInfo:
        """将当前设置保存到指定文件

        :param file_path: 保存设置的文件路径
        :return: 当前设置信息对象
        """
        Base.log("I", f"保存设置到{file_path}", "SettingsInfo.save_to")
        if not os.path.isdir(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except (FileNotFoundError, PermissionError) as e:
                Base.log_exc("删除旧设置文件失败", "SettingsInfo.save_to", exc=e)
        try:
            with open(file_path, "wb") as f:
                pickle.dump(self, f) # pyright: ignore[reportUnknownMemberType]
        except (OSError, pickle.PickleError, EOFError) as e:
            Base.log_exc("保存设置失败", "SettingsInfo.save_to", exc=e)
        return self

    def load_from(self, file_path: str) -> SettingsInfo:
        """
        从指定文件加载设置

        :param file_path: 设置文件的路径
        :return: 加载后的设置信息对象
        """
        try:
            with open(file_path, "rb") as f:
                obj: SettingsInfo = pickle.load(f) # pyright: ignore[reportUnknownMemberType]
            self.__dict__.update(obj.get_dict())
        except Exception as e:
            Base.log_exc("加载设置失败，将会返回默认", "SettingsInfo.load_from", exc=e)
            self.reset_settings()
            self.save_to(file_path)
        return self

    def set(self, **kwargs: Dict[str, Any]) -> "SettingsInfo":
        """批量设置多个配置参数

        :param kwargs: 键值对形式的设置参数
        :return: 当前设置信息对象
        """
        Base.log("I", "设置设置", "SettingsInfo.set")
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    def get(self, key: str) -> Any:
        """
        获取指定键名的设置值

        :param key: 设置参数的键名
        :return: 对应的设置值
        """
        return getattr(self, key)

    def get_dict(self):
        """
        返回所有设置参数的字典表示

        :return: 包含所有设置的字典
        """
        return dict(
            (k, v)
            for k, v in self.__dict__.items()
            if (not k.startswith("__")) and (not isinstance(v, (FunctionType, MethodType)))
        )

    def __repr__(self):
        "返回设置信息"
        return f"SettingsInfo({dict((k, v) for k, v in self.__dict__.items() if not k.startswith('__'))!r})"


SettingsInfo.glob = SettingsInfo()
