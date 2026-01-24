"""
创建模板窗口
"""

from utils import Base, ClassObj as ClassWindow
from widgets.basic import *
from widgets.ui.pyside6.NewTemplateWindow import Ui_Form

__all__ = ["NewTemplateWidget"]

class NewTemplateWidget(Ui_Form, MyWidget):
    """创建新模板的窗口"""

    def __init__(
        self, main_window: ClassWindow = None, master_widget: Optional[WidgetType] = None
    ):
        """
        初始化

        :param main_window: 程序的主窗口，方便传参
        :param master_widget: 这个窗口的父窗口
        :param student: 这个学生窗口对应的学生
        """
        super().__init__(master=master_widget)
        self.setupUi(self)
        self.show()
        self.main_window = main_window
        self.master_widget = master_widget
        self.buttonBox.accepted.connect(self.commit)
        self.buttonBox.rejected.connect(self.cancel)
        self.lineEdit.setText("")
        self.lineEdit_3.setText("")
        self.setWindowTitle("创建新模板")

    @Slot()
    def commit(self):
        Base.log("I", "提交新模板窗口", "NewTemplateWidget.commit")
        if self.lineEdit.text() == "":
            Base.log("W", "提交新模板窗口时，模板名称为空", "NewTemplateWidget.commit")
            QMessageBox.warning(self, "警告", "模板名称不能为空")
            return

        if self.lineEdit_3.text() == "":
            Base.log("W", "提交新模板窗口时，模板描述为空", "NewTemplateWidget.commit")
            QMessageBox.warning(self, "警告", "模板描述不能为空")
            return

        self.main_window.add_template(
            "userset_" + str(Base.utc()),
            self.lineEdit.text(),
            self.doubleSpinBox.value(),
            self.lineEdit_3.text(),
            "为用户创建",
        )
        self.closeEvent(QCloseEvent())
        self.destroy()

    @Slot()
    def cancel(self):
        Base.log("I", "取消创建新模板", "NewTemplateWidget.cancel")
        self.closeEvent(QCloseEvent())
        self.destroy()