"""
创建模板窗口
"""

from widgets.basic import *
from widgets.ui.pyside6.WTF import Ui_Form

__all__ = ["WTFWidget"]


class WTFWidget(Ui_Form, MyWidget):
    "我愿称之为世界上最抽象的UI"

    def __init__(self, master_widget: WidgetType = None):
        """
        初始化

        :param main_window: 程序的主窗口，方便传参
        :param master_widget: 这个窗口的父窗口
        """
        super().__init__(master=master_widget)
        self.setupUi(self)
        self.pushButton_18.clicked.connect(
            lambda: QMessageBox.information(self, "6", "恭喜你发现了一个没什么用的彩蛋")
        )
        self.setWindowTitle("1145141919810")
        self.show()