"""
历史记录窗口模块
"""

from __future__ import annotations


from utils.basetypes import Base
from utils.classobjects import ScoreModification, ClassDataSet
from utils.qtconfig import QVBoxLayout, QWidget, QCloseEvent, QColor

from widgets.custom.ListView import ListView
from widgets.basic import MyWidget
from widgets.templates import ModifyHistoryWindow



class HistoryWidget(MyWidget, ModifyHistoryWindow.Ui_Form):
    """历史记录窗口"""

    def __init__(
        self,
        dataset: ClassDataSet,
        history: ScoreModification,
        listview_widget: ListView | None = None,
        listview_index: int | None  = None,
        master: QWidget | None = None,
        readonly: bool = False
    ):
        """
        初始化一个分数修改历史记录窗口。

        :param dataset: 班级数据集
        :param master: 父窗口
        :param history: 分数修改历史记录
        :param listview_widget: 所属的ListView
        :param listview_index: 在ListView中的索引
        :param readonly: 是否只读
        """

        super().__init__(master=master)
        self.setupUi(self) # pyright: ignore[reportUnknownMemberType]

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.dataset = dataset
        self.master = master
        self.history = history
        self.listview_index = listview_index
        self.listview_widget = listview_widget
        self.readonly = readonly or (not history.executed)
        self.setWindowTitle(
            f"历史记录 - {self.history.target.name} {self.history.title}"
        )
        self.label_11.setText(str(self.history.title))
        self.label_6.setText(str(self.history.desc))
        self.label_12.setText(str(self.history.mod))
        self.label_13.setText(
            str(self.history.target.name + f" ({self.history.target.num})")
        )
        self.label_8.setText(str(self.history.create_time))
        self.label_7.setText(
            (
                ("已执行（" + str(self.history.execute_time) + "）")
                if self.history.executed
                else "未执行"
            )
        )
        self.pushButton_3.clicked.connect(self.retract)
        self.update_status()

    def update_status(self):
        if not self.history.executed:
            self.pushButton_3.setEnabled(False)
            self.label_15.setText("无法撤回（未执行）")
        elif self.readonly:
            self.pushButton_3.setEnabled(False)
            self.label_15.setText("无法撤回（只读）")
        elif (
            self.history
            not in self.dataset.classes[self.history.target.belongs_to]
            .students[self.history.target.num]
            .history.values()
        ):
            self.pushButton_3.setEnabled(False)
            self.label_15.setText("无法撤回（不在历史记录中）")
        else:
            self.pushButton_3.setEnabled(True)
            self.label_15.setText("")

    def retract(self):
        Base.log("I", f"撤销：{repr(self.history)}", "HistoryWidget.retract")
        status, result = self.dataset.retract_modify(self.history)
        Base.log("I", f"撤销结果：{repr((status, result))}", "HistoryWidget.retract")

        if status and self.listview_widget is not None and self.listview_index is not None:
            self.listview_widget.setText(
                self.listview_index,
                (str(self.listview_widget.getText(self.listview_index)) or "") + "（已撤回）")
            self.listview_widget.getItem(self.listview_index).setBackground(
                QColor(202, 202, 202)
            )

        self.pushButton_3.setEnabled(False)
        self.closeEvent(QCloseEvent())
        self.destroy()

    def closeEvent(self, event: QCloseEvent):
        Base.log("I", "关闭历史记录窗口（通过closeEvent）", "HistoryWidget.closeEvent")
        super().closeEvent(event)

    def show(self, readonly: bool = False):
        Base.log("I", "显示历史记录窗口", "HistoryWidget.show")
        self.readonly = readonly or (not self.history.executed)
        self.update_status()
        super().show()

__all__ = ["HistoryWidget"]
