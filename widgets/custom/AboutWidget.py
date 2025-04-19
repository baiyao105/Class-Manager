
"""
"关于"窗口所在模块
"""

from typing import Optional
from utils import (
    ClassObj, 
    CLIENT_VERSION, 
    CLIENT_VERSION_CODE, 
    CORE_VERSION, 
    CORE_VERSION_CODE
)
from widgets.custom.ListView import ListView
from widgets.basic import *
from widgets.ui.pyside6.About import Ui_Form

__all__ = ["AboutWidget"]

class AboutWidget(Ui_Form, MyWidget):
    """ "关于"窗口

    做的最轻松的一个
    """

    def __init__(
        self, master: Optional[WidgetType] = None, mainwindow: Optional[ClassObj] = None
    ):

        super().__init__(master)
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.master = master
        self.versioninfo.setText(
            f"客户端版本：{CLIENT_VERSION} ({CLIENT_VERSION_CODE})       核心版本: {CORE_VERSION} ({CORE_VERSION_CODE})"
        )
        self.pushButton.clicked.connect(lambda: QMessageBox.aboutQt(self))