"""
点评模板选择窗口
"""

from typing import Optional
from utils import ClassObj
from widgets.ui.pyside6.SelectTemplateWindow import Ui_Form
from widgets.basic import *

__all__ = ["SelectTemplateWidget"]

class SelectTemplateWidget(MyWidget, Ui_Form):
    "选择模板窗口"

    return_result = Signal(tuple)
    "返回信号：(模板key，修改标题，修改描述，修改分数) (Tuple[str, str, str, float])"

    def __init__(
        self, main_window: Optional[ClassObj] = None, master_widget: Optional[WidgetType] = None
    ):
        """
        初始化

        :main_window: 主窗口
        :master_widget: 父窗口
        """
        super().__init__(master=master_widget)
        self.setupUi(self)
        self.setWindowTitle("选择模板")
        index = 0
        self.index_map = {}
        self.data_obj = main_window
        self.master_widget = master_widget
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
        self.result: Optional[Tuple[str, str, str, float]] = None

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

        except KeyError as unused:
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

    def close(self):
        Base.log(
            "I",
            f"选择结果：{repr((self.selected, self.return_title, self.return_desc, self.return_mod))}",
            "SelectTemplateWidget",
        )
        self.select_finished = True
        Base.log("I", "选择模板窗口关闭", "SelectTemplateWidget")
        super(MyWidget, self).close()

    def closeEvent(self, event: QEvent):
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

    def finish(
        self,
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[float]]:
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

    def exec(self) -> Optional[Tuple[str, str, str, float]]:
        """阻塞调用，返回 (key, title, desc, mod)"""
        self.show()
        loop = QEventLoop(self)
        timer = QTimer(self)
        def _check_if_finished():
            if self.select_finished:
                loop.quit()
                timer.stop()
        timer.timeout.connect(_check_if_finished)
        timer.start(50)
        loop.exec()
        timer.stop()
        return self.result
