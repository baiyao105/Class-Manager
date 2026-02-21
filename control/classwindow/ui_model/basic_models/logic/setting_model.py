"""
和设置存储有关的模型。
"""

from __future__ import annotations

import os
import time
from typing import Literal, Any

from utils.update_check import CLIENT_VERSION_CODE
from utils.basetypes import Base
from utils.settings import SettingsInfo
from utils.update_check import CLIENT_VERSION

from utils.qtconfig import Slot



settings = SettingsInfo.get_global_settings()

class SettingModel:

    def __init__(self, current_user: str):
        """
        构造函数。
        
        :param current_user: 当前的用户名
        """

        self.create_time = time.time()
        "程序创建时间"
        self.framerate_update_time = 0
        "帧率上次更新时间"
        self.framecount = 0
        "自上一秒以来的更新帧数"
        self.framerate = 0
        "帧率"
        self.video_framecount = 0
        "动态背景帧数"
        self.video_framerate = 0
        "动态背景帧率"
        self.video_framerate_update_time = 0
        "动态背景帧数上次更新时间"
        self.displayed_on_the_log_window = 0
        "在小日志窗口上已经体现的日志条数，用来判断是否刷新"
        self.last_save_from_action = time.time()
        "上次手动保存的时间"
        self.auto_save_last_time = time.time()
        "上次自动保存的时间"

        self.opacity = 0.88
        "背景透明度"
        self.current_user = current_user
        "当前用户"
        self.backup_path = "backups/"
        "备份路径"

        # 初始化设置信息
        self.client_version = CLIENT_VERSION
        "客户端版本号"
        self.client_version_code = CLIENT_VERSION_CODE
        "客户端版本号"
        self.opacity: float = 0.88
        "窗口透明度"
        self.score_up_color_mixin_begin: tuple[int, int, int] = (0xCA, 0xFF, 0xCA)
        "加分动画颜色渐变开始颜色"
        self.score_up_color_mixin_end: tuple[int, int, int] = (0x33, 0xCF, 0x6C)
        "加分动画颜色渐变结束颜色"
        self.score_up_color_mixin_start: float = 2
        "加分动画颜色渐变开始值（分）"
        self.score_up_color_mixin_step: float = 15
        "加分动画颜色渐变开始值（分）"
        self.score_up_flash_framelength_base: int = 300
        "加分动画基础持续时间（毫秒）"
        self.score_up_flash_framelength_step: int = 100
        "加分动画每多加一分增加动画时间（毫秒）"
        self.score_up_flash_framelength_max: int = 2000
        "加分动画基础持续时间（毫秒）"

        self.score_down_color_mixin_begin: tuple[int, int, int] = (0xFC, 0xB5, 0xB5)
        "扣分动画颜色渐变开始颜色"
        self.score_down_color_mixin_end: tuple[int, int, int] = (0xA9, 0x00, 0x00)
        "扣分动画颜色渐变结束颜色"
        self.score_down_color_mixin_start: float = 2
        "扣分动画颜色渐变开始值（分）"
        self.score_down_color_mixin_step: float = 15
        "扣分动画颜色渐变总步长（分）"
        self.score_down_flash_framelength_base: int = 300
        "扣分动画基础持续时间（毫秒）"
        self.score_down_flash_framelength_step: int = 100
        "扣分动画每多扣一分增加动画时间（毫秒）"
        self.score_down_flash_framelength_max: int = 2000
        "扣分动画最长持续时间（毫秒）"
        self.log_keep_linecount: int = 100
        "日志窗口保留行数"
        self.log_update_interval: float = 0.1
        "日志窗口更新间隔（秒）"
        self.auto_save_enabled: bool = False
        "是否启用自动保存"
        self.auto_save_interval: float = 120
        "自动保存间隔（秒）"
        self.auto_save_path: Literal["folder", "user"] = "folder"
        "自动保存路径"
        self.auto_backup_scheme: Literal["none", "only_data", "all"] = "only_data"
        "自动备份方案"
        self.animation_speed: float = 1.0
        "动画速度"
        self.subwindow_x_offset: int = 0
        "子窗口x偏移量"
        self.subwindow_y_offset: int = 0
        "子窗口y偏移量"
        self.use_animate_background: bool = False
        "是否使用动态背景"
        self.max_framerate: int = 60
        "动态背景最大帧率"

        self.load_settings()
    


    def save_settings(self):
        """
        保存当前的全局设置对象到设置存档文件。
        """
        Base.log("I", "保存设置到文件", "SettingsModel.save_settings")
        os.makedirs(os.path.abspath(f"chunks/{self.current_user}"), exist_ok=True)
        settings.save_to(
            os.path.abspath(f"chunks/{self.current_user}/settings.dat")
        )

    @Slot()
    def reset_settings(self):
        """
        重置全局设置，并将主窗口的设置重置为全局设置当前的默认值。
        """
        settings.reset_settings()
        version = self.client_version
        version_code = self.client_version_code
        self.set_settings(**settings.get_dict())
        self.set_settings(client_version_code=version_code, client_version=version)
        self.save_settings()

    def load_settings(self) -> SettingsInfo:
        """
        加载设置存档文件到全局设置对象后应用在主窗口。
        """
        Base.log("I", "从文件中加载设置", "SettingsModel.load_settings")
        settings.load_from(
            os.path.abspath(f"chunks/{self.current_user}/settings.dat")
        )
        self.set_settings(**settings.get_dict())
        return settings

    def set_settings(self, **kwargs: Any):
        """
        依照kwargs设置全局设置对象和主窗口的设置信息并保存当前设置到文件。
        
        （调用save_settings）
        """
        Base.log("I", "设置设置信息", "SettingsModel.set_settings")
        for key, value in kwargs.items():
            if settings.get(key) != kwargs[key]:
                Base.log(
                    "I",
                    f"{key} 变更： "
                    f"{settings.get(key)} "
                    f"-> {repr(getattr(self, key, None))} (self) "
                    f"/ {repr(kwargs[key])} (kwargs)",
                    "SettingsModel.set_settings",
                )
            setattr(self, key, value)
            setattr(settings, key, value)
        self.save_settings()

    def save_current_settings(self):
        """
        保存此窗口当前的设置到全局设置对象并保存设置。
        """
        Base.log("I", "保存当前设置", "SettingsModel.save_settings")
        self.set_settings(
            client_version=self.client_version,
            client_version_code=self.client_version_code,
            opacity=self.opacity,
            score_up_color_mixin_begin=self.score_up_color_mixin_begin,
            score_up_color_mixin_end=self.score_up_color_mixin_end,
            score_up_color_mixin_step=self.score_up_color_mixin_step,
            score_up_color_mixin_start=self.score_up_color_mixin_start,
            score_up_flash_framelength_base=self.score_up_flash_framelength_base,
            score_up_flash_framelength_step=self.score_up_flash_framelength_step,
            score_up_flash_framelength_max=self.score_up_flash_framelength_max,
            score_down_color_mixin_begin=self.score_down_color_mixin_begin,
            score_down_color_mixin_end=self.score_down_color_mixin_end,
            score_down_color_mixin_step=self.score_down_color_mixin_step,
            score_down_color_mixin_start=self.score_down_color_mixin_start,
            score_down_flash_framelength_base=self.score_down_flash_framelength_base,
            score_down_flash_framelength_step=self.score_down_flash_framelength_step,
            score_down_flash_framelength_max=self.score_down_flash_framelength_max,
            log_keep_linecount=self.log_keep_linecount,
            log_update_interval=self.log_update_interval,
            auto_save_enabled=self.auto_save_enabled,
            auto_save_interval=self.auto_save_interval,
            auto_save_path=self.auto_save_path,
            auto_backup_scheme=self.auto_backup_scheme,
            animation_speed=self.animation_speed,
            subwindow_x_offset=self.subwindow_x_offset,
            subwindow_y_offset=self.subwindow_y_offset,
            use_animate_background=self.use_animate_background,
            max_framerate=self.max_framerate,
        )