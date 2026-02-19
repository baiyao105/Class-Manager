
"""
"关于"窗口所在模块
"""

from __future__ import annotations

from utils.qtconfig import QWidget, QMessageBox
from utils.update_check import (
    CLIENT_VERSION, 
    CLIENT_VERSION_CODE, 
    CORE_VERSION, 
    CORE_VERSION_CODE
)

from widgets.basic import MyWidget
from widgets.templates import About


class AboutWidget(About.Ui_Form, MyWidget):
    """ 
    "关于"窗口。

    （做的最轻松的一个）
    """

    def __init__(
        self, master: QWidget | None = None
    ):

        super().__init__(master)
        self.setupUi(self) # type: ignore
        self.master = master
        self.versioninfo.setText(
            f"客户端版本：{CLIENT_VERSION} ({CLIENT_VERSION_CODE})       核心版本: {CORE_VERSION} ({CORE_VERSION_CODE})"
        )
        self.pushButton.clicked.connect(lambda: QMessageBox.aboutQt(self))


__all__ = ["AboutWidget"]
