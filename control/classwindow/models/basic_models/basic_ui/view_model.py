"""
与视图有关的模型。
"""

from __future__ import annotations


from typing import TYPE_CHECKING, Sequence

from utils.basetypes import Base
from utils.qtconfig import QWidget

from widgets import ListView
from widgets.custom.ListView import ListViewItemDataType, ListViewCommandDataType

if TYPE_CHECKING:
    _BaseClass = QWidget
else:
    _BaseClass = object


class ViewModel(_BaseClass):
    """
    视图模型。
    
    是一个Mixin类。
    """

    def __init__(self, master: QWidget | None = None):
        Base.log("D", "初始化ViewModel", "ViewModel.__init__")
        # 不调用super().__init__()
        self.lastest_listview: ListView | None = None

    def list_view(
        self,
        data: Sequence[ListViewItemDataType],
        title: str,
        master: QWidget | None = None,
        commands: Sequence[ListViewCommandDataType] | None = None,
        select_once_then_exit: bool = False
    ):
        """
        显示一个列表框。

        :param data: 数据
        :param title: 标题
        :param master: 父窗口
        :param commands: 命令
        """
        self.lastest_listview = ListView(
            master=master or self,
            data=data,
            title=title,
            commands=commands,
            select_once_then_exit=select_once_then_exit
        )
        self.lastest_listview.show()

    
    def stop(self):
        if self.lastest_listview:
            self.lastest_listview.close()


