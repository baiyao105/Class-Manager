"""
学生选择器所在模块
"""

from typing import Optional, List, Dict
from utils import ClassObj
from widgets.basic import *
from widgets.ui.pyside6.MultiSelectWindow import Ui_Form

__all__ = ["StudentSelectorWidget"]

class StudentSelectorWidget(Ui_Form, MyWidget):
    """多选学生窗口"""

    return_result = Signal(list)
    "返回结果信号"

    def __init__(
        self,
        main_window: ClassObj = None,
        master: Optional[WidgetType] = None,
        target_students: List[Student] = None,
        default_selection: List[Student] = None,
        allow_none: bool = False,
        title: str = "选择学生",
    ):
        """
        学生选择器

        :param main_window: 主窗口
        :param master_widget: 父窗口
        :param target_students: 目标学生列表
        :param default_selection: 默认选择的学生
        :param allow_none: 是否允许选择空列表
        :param title: 窗口标题
        """
        super().__init__(master=main_window)
        if target_students is None:
            target_students = []
        self.setupUi(self)
        self.setWindowTitle("学生选择器")
        self.label.setText(title)
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.main_window = main_window
        self.master_widget = master
        self.target_students = target_students
        self.default_selection = (
            default_selection if default_selection is not None else []
        )
        self.mapping = {}
        self.allow_none = allow_none
        row = 0
        col = 0
        self.checkbuttons: Dict[int, QCheckBox] = {}
        self.select_result: Optional[List[Student]] = None
        for num, stu in [(stu.num, stu) for stu in target_students]:
            self.mapping[num] = stu
            checkbox = QCheckBox(f"{stu.num}号 " + stu.name + f"\n{stu.score}分")
            checkbox.setGeometry(QRect(0, 0, 60, 60))
            checkbox.setChecked(stu in self.default_selection)
            self.gridLayout.addWidget(checkbox, row, col)
            self.checkbuttons[num] = self.gridLayout.itemAtPosition(row, col).widget()
            col += 1
            if col > 9:
                col = 0
                row += 1
        self.gridLayout.setSpacing(10)
        self.pushButton.clicked.connect(self.commit)
        self.pushButton_2.clicked.connect(self.cancel)
        self.pushButton_3.clicked.connect(self.select_opposite)
        self.pushButton_4.clicked.connect(self.select_all)
        self.pushButton_5.clicked.connect(self.select_none)
        self.comboBox.clear()
        self.comboBox.addItems(
            [
                str(8),
                str(9),
                str(10),
                str(11),
                str(12),
            ]
        )
        self.comboBox.setCurrentIndex(2)
        self.comboBox.currentIndexChanged.connect(self.width_changed)

    def exec(self, allow_none: bool = False) -> List[Student]:
        """
        执行当前的多选操作。

        :param allow_none: 允许不选学生
        """
        Base.log("I", "多选窗口开始执行", "MultiSelectWidget")
        self.allow_none = allow_none
        self.show()
        loop = QEventLoop(self)
        timer = QTimer(self)
        def _check_if_finished():
            if self.select_result is not None:
                loop.quit()
                timer.stop()
        timer.timeout.connect(_check_if_finished)
        timer.start(50)
        loop.exec()
        timer.stop()
        Base.log(
            "I",
            f"多选窗口执行结束，结果：{repr(self.select_result)}",
            "MultiSelectWidget",
        )
        return self.select_result

    @Slot()
    def width_changed(self):
        Base.log(
            "I",
            f"多选窗口宽度设置为：{self.comboBox.currentText()}",
            "MultiSelectWidget.width_changed",
        )
        for i in range(self.gridLayout.count()):
            if isinstance(self.gridLayout.itemAt(i).widget(), QCheckBox):
                self.gridLayout.itemAt(i).widget().deleteLater()
        row = 0
        col = 0
        for num, stu in [(stu.num, stu) for stu in self.target_students]:
            self.mapping[num] = stu
            checkbox = QCheckBox(f"{stu.num}号 " + stu.name + f"\n{stu.score}分")
            checkbox.setGeometry(QRect(0, 0, 60, 60))
            self.gridLayout.addWidget(checkbox, row, col)
            self.checkbuttons[num] = checkbox
            col += 1
            if col > self.comboBox.currentIndex() + 8 - 1:
                col = 0
                row += 1
        self.gridLayout.setSpacing(0)

    @Slot()
    def commit(self):
        if (
            not len(
                [
                    self.mapping[num]
                    for num, checkbutton in self.checkbuttons.items()
                    if checkbutton.isChecked()
                ]
            )
            and not self.allow_none
        ):
            Base.log("W", "提交多选窗口，未选择任何学生", "MultiSelectWidget.commit")
            QMessageBox.warning(self, "警告", "虽然但是，你真的不选点什么吗？")
            return
        Base.log(
            "I",
            f"提交多选窗口，结果：{repr([num for num, checkbutton in self.checkbuttons.items() if checkbutton.isChecked()])}",
            "MultiSelectWidget.commit",
        )
        self.return_result.emit(
            [
                self.mapping[num]
                for num, checkbutton in self.checkbuttons.items()
                if checkbutton.isChecked()
            ]
        )
        self.select_result = [
            self.mapping[num]
            for num, checkbutton in self.checkbuttons.items()
            if checkbutton.isChecked()
        ]
        self.closeEvent(QCloseEvent())
        self.destroy()

    @Slot()
    def cancel(self):
        Base.log("I", "取消多选窗口", "MultiSelectWidget.cancel")
        self.closeEvent(QCloseEvent())
        self.destroy()

    @Slot()
    def select_opposite(self):
        Base.log("I", "反选多选窗口", "MultiSelectWidget.select_opposite")
        for checkbutton in self.checkbuttons.values():
            checkbutton.setChecked(not checkbutton.isChecked())

    @Slot()
    def select_all(self):
        Base.log("I", "全选多选窗口", "MultiSelectWidget.select_all")
        for checkbutton in self.checkbuttons.values():
            checkbutton.setChecked(True)

    @Slot()
    def select_none(self):
        Base.log("I", "全不选多选窗口", "MultiSelectWidget.select_none")
        for checkbutton in self.checkbuttons.values():
            checkbutton.setChecked(False)

    def closeEvent(self, event):
        Base.log("I", "关闭多选窗口（通过closeEvent）", "MultiSelectWidget")
        super().closeEvent(event)