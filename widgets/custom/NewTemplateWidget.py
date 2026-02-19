"""
创建模板窗口
"""

from __future__ import annotations

from utils import Base, ClassDataSet, utc
from utils.qtconfig import QWidget, Slot, QMessageBox, QCloseEvent


from widgets.basic import MyWidget
from widgets.templates import NewTemplateWindow


class NewTemplateWidget(NewTemplateWindow.Ui_Form, MyWidget):
    """创建新模板的窗口"""

    def __init__(
        self, dataset: ClassDataSet, master: QWidget | None = None
    ):
        """
        __init__ 的 Docstring
        
        :param self: 说明
        :param dataset: 数据集
        :type dataset: ClassDataSet
        :param master: 父窗口
        :type master: QWidget | None
        """
        super().__init__(master=master)
        self.setupUi(self) # type: ignore
        self.show()
        self.main_window = dataset
        self.master_widget = master
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
            "userset_" + str(utc()),
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

__all__ = ["NewTemplateWidget"]
