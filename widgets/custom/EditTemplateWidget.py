"""
模板编辑器所在模块
"""
from __future__ import annotations

from utils import ScoreModificationTemplate, ClassDataSet, question_yes_no, Base
from utils.qtconfig import QWidget, Slot, QMessageBox, QCloseEvent


from widgets.custom.ListView import ListView
from widgets.basic import MyWidget
from widgets.templates import EditTemplateWindow



class EditTemplateWidget(EditTemplateWindow.Ui_Form, MyWidget):
    """
    编辑模板的窗口
    """

    def __init__(
        self,
        dataset: ClassDataSet,
        template: ScoreModificationTemplate,
        listview: ListView,
        listview_index: int,
        master_widget: QWidget | None = None
    ):
        """
        初始化

        :param dataset: 数据集
        :param master: 这个窗口的父窗口
        :param template: 要修改的模板
        :param listview: 模板所在的listview
        :param listview_index: 模板在listview中的位置
        """
        super().__init__(master=master_widget)
        self.setupUi(self) # pyright: ignore[reportUnknownMemberType]
        self.show()
        self.dataset = dataset
        self.master_widget = master_widget
        self.template = template
        self.listview = listview
        self.listview_index = listview_index
        self.buttonBox.accepted.connect(self.commit)
        self.buttonBox.rejected.connect(self.cancel)
        self.pushButton_4.clicked.connect(self.delete)
        self.lineEdit.setText(self.template.title)
        self.lineEdit_3.setText(self.template.desc)
        self.doubleSpinBox.setValue(self.template.mod)
        self.label_7.setText(self.template.key)
        self.pushButton.clicked.connect(
            lambda: self.lineEdit.setText(self.template.title)
        )
        self.pushButton_3.clicked.connect(
            lambda: self.lineEdit_3.setText(self.template.desc)
        )
        self.pushButton_2.clicked.connect(
            lambda: self.doubleSpinBox.setValue(self.template.mod)
        )
        self.setWindowTitle(self.template.title)

    @Slot()
    def commit(self):
        Base.log("I", "提交修改模板窗口", "EditTemplateWidget.commit")
        if self.lineEdit.text() == "":
            Base.log("W", "提交新模板窗口时，模板名称为空", "EditTemplateWidget.commit")
            QMessageBox.warning(self, "警告", "模板名称不能为空")
            return

        if self.lineEdit_3.text() == "":
            Base.log("W", "提交新模板窗口时，模板描述为空", "EditTemplateWidget.commit")
            QMessageBox.warning(self, "警告", "模板描述不能为空")
            return

        self.dataset.add_template(
            self.template.key,
            self.lineEdit.text(),
            self.doubleSpinBox.value(),
            self.lineEdit_3.text(),
            "修改原模版",
        )
        self.listview.setText(self.listview_index, self.lineEdit.text())
        self.closeEvent(QCloseEvent())
        self.destroy()

    @Slot()
    def cancel(self):
        Base.log("I", "取消创建新模板", "NewTemplateWidget.cancel")
        self.closeEvent(QCloseEvent())
        self.destroy()

    def delete(self):
        Base.log("I", "询问是否删除模板", "EditTemplateWidget.delete")
        if question_yes_no(self, "警告", "确认删除模板？", False, "warning"):
            Base.log("I", "删除模板", "EditTemplateWidget.delete")
            self.dataset.del_template(self.template.key, "模板编辑器中删除")
            self.listview.setText(self.listview_index, "(已删除)")
            self.listview.setCallable(self.listview_index, lambda: None)
            self.closeEvent(QCloseEvent())
            self.destroy()

__all__ = ["EditTemplateWidget"]
