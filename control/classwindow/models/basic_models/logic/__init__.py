"""
和逻辑有关的模型。
"""

from __future__ import annotations


from .cmd_model import CommandModel
from .setting_model import SettingModel




class LogicModel(CommandModel, SettingModel):
    "负责基本逻辑的模型。"

    def __init__(self, user: str):
        CommandModel.__init__(self)
        SettingModel.__init__(self, current_user=user) # type: ignore
