"""
点评模板选择窗口
"""

from __future__ import __annotations__

from typing import TypeAlias

from utils.basetypes import Base
from utils.classobjects import ClassDataSet, ScoreModificationTemplate
from utils.functions import wait_until
from utils.qtconfig import Signal, QWidget, QCloseEvent, Slot

from widgets.templates import SelectTemplateWindow
from widgets.basic import MyWidget

SelectResultType: TypeAlias = tuple[str | None, str | None, str | None, float | None]

class SelectTemplateWidget(MyWidget, SelectTemplateWindow.Ui_Form):
    "选择模板窗口"

    return_result = Signal(tuple)
    "返回信号：(模板key，修改标题，修改描述，修改分数) (tuple[str, str, str, float])"

    def __init__(
        self, dataset: ClassDataSet, master: QWidget | None = None
    ):
        """
        初始化窗口。

        :param dataset: 数据集
        :param master: 父窗口
        """
        super().__init__(master=master)
        self.setupUi(self) # pyright: ignore[reportUnknownMemberType]
        self.setWindowTitle("选择模板")
        index = 0
        self.index_map: dict[int, ScoreModificationTemplate] = {}
        self.data_obj = dataset
        self.master_widget = master
        self.show()
        self.comboBox.clear()
        for key in self.data_obj.modify_templates:
            template = self.data_obj.modify_templates[key]
            if template.is_visible:
                self.comboBox.addItem(template.title)
                self.index_map[index] = key
                index += 1
        self.select_finished = False
        self.return_title = None
        self.return_desc = None
        self.return_mod = None
        self.selected = None
        self.buttonBox.accepted.connect(self.finish)
        self.buttonBox.rejected.connect(self.close)
        self.comboBox.currentIndexChanged.connect(self.update_edit)
        self.result: SelectResultType | None = None

    def show(self):
        self.update_edit()
        super().show()
        
    def update_edit(self):
        index = self.comboBox.currentIndex()
        try:
            template = self.data_obj.modify_templates[self.index_map[index]]
            self.lineEdit.setText(template.title)
            self.lineEdit_3.setText(template.desc)
            self.doubleSpinBox.setValue(template.mod)

        except KeyError:
            pass

    def select(self):
        index = 0
        self.comboBox.clear()
        self.index_map = {}
        for key in self.data_obj.modify_templates:
            template = self.data_obj.modify_templates[key]
            if template.is_visible:
                self.comboBox.addItem(template.title)
                self.index_map[index] = key
                index += 1
        self.update_edit()

    def destroy(self, /,  destroyWindow: bool = True, destroySubWindows: bool = True):
        Base.log(
            "I",
            f"选择结果：{repr((self.selected, self.return_title, self.return_desc, self.return_mod))}",
            "SelectTemplateWidget",
        )
        self.select_finished = True
        Base.log("I", "选择模板窗口关闭", "SelectTemplateWidget")
        super().destroy(destroyWindow=destroyWindow, destroySubWindows=destroySubWindows)


    def closeEvent(self, event: QCloseEvent):
        Base.log("I", "选择模板窗口关闭（通过关闭事件）", "SelectTemplateWidget")
        super().closeEvent(event)

    @Slot()
    def cancel(self):
        Base.log("I", "选择已取消", "SelectTemplateWidget")
        self.return_title = None
        self.return_desc = None
        self.return_mod = None
        self.select_finished = True
        self.close()

    def finish(self):
        self.selected_index = self.comboBox.currentIndex()
        self.selected = self.data_obj.modify_templates[
            self.index_map[self.selected_index]
        ]
        if self.lineEdit.text() != self.selected.title:
            self.return_title = self.lineEdit.text()
        if self.lineEdit_3.text() != self.selected.desc:
            self.return_desc = self.lineEdit_3.text()
        if self.doubleSpinBox.value() != self.selected.mod:
            self.return_mod = self.doubleSpinBox.value()
        if not self.select_finished:  # 防止重复调用
            self.select_finished = True
            self.return_result.emit(
                (
                    self.selected.key,
                    self.return_title,
                    self.return_desc,
                    self.return_mod,
                )
            )
            self.result = (
                self.selected.key,
                self.return_title,
                self.return_desc,
                self.return_mod,
            )
        self.select_finished = True
        self.close()

    def exec(self) -> SelectResultType:
        """
        阻塞调用，返回 (key, title, desc, mod)，如果取消了会是四个None
        """
        self.show()
        wait_until(lambda: self.select_finished)
        assert self.result, "按道理来说选择完了result就不应该是None了啊"
        return self.result


__all__ = ["SelectTemplateWidget"]
