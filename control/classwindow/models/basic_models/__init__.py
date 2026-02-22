"""
数据模型。
"""

from __future__ import annotations

from utils.qtconfig import QGraphicsOpacityEffect
from .recover_model import RecoverModel, RecoveryPoint

class DataUIModel(RecoverModel):
    "一个已经实现基本数据处理和界面功能的模型。"

    def __init__(
        self,
        current_user: str,
        class_name: str,
        class_key: str,
        save_path: str | None = None
    ): 
        super().__init__(current_user=current_user, class_name=class_name, class_key=class_key, save_path=save_path)
        self.should_stop = False


    def stop(self):
        "停止运行并保存数据"
        self.should_stop = True
        super().stop()


__all__ = ["RecoveryPoint", "DataUIModel"]