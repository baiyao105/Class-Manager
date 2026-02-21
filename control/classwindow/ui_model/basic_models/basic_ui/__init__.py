"""
基本UI模型。
"""

from __future__ import annotations

from utils.qtconfig import QWidget
from utils.typecheck import AutoSlotMeta

from widgets.basic import MyMainWindow

from .message_box_model import MessageBoxModel
from .side_notice_model import SideNoticeModel
from .exception_handler_model import ExceptionHandlerModel
from .view_model import ViewModel

class BasicUIModel( # pyright: ignore[reportIncompatibleMethodOverride]
    MyMainWindow,
    ViewModel,
    ExceptionHandlerModel,
    SideNoticeModel, 
    MessageBoxModel, 
    metaclass=AutoSlotMeta
):
    """
    基础UI模型类。
    """

    def __init__(self, master: QWidget | None = None):
        """
        初始化UI模型。

        :param master: 父窗口，但一般不用填
        """
        MyMainWindow.__init__(self, master)
        ExceptionHandlerModel.__init__(self, master)
        SideNoticeModel.__init__(self, master)
        MessageBoxModel.__init__(self, master)
        ViewModel.__init__(self, master)


    def stop(self):
        super().stop()
