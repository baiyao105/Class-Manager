"""
随机点名窗口所在模块
"""

from typing import Optional, List
from utils import ClassObj
from widgets.custom.StudentWidget import StudentWidget
from widgets.custom.StudentSelectorWidget import StudentSelectorWidget
from widgets.basic import *
from widgets.ui.pyside6.RandomSelector import Ui_Form


__all__ = ["RandomSelectWidget"]
class RandomSelectWidget(Ui_Form, MyWidget):


    """随机点名窗口"""

    def __init__(
        self, master: Optional[WidgetType] = None, main_window: Optional[ClassObj] = None
    ):
        super().__init__(master)
        self.main_window = main_window
        self.master = master
        self.setupUi(self)
        self.from_students: List[Student] = list(
            main_window.target_class.students.values()
        )
        self.includes_students: List[Student] = []
        self.excludes_students: List[Student] = []
        self.result: List[Student] = []
        self.pushButton.clicked.connect(self.start)
        self.pushButton_2.clicked.connect(self.select_source)
        self.pushButton_3.clicked.connect(self.select_include)
        self.pushButton_4.clicked.connect(self.select_exclude)
        self.listWidget.itemDoubleClicked.connect(
            lambda item: self.show_stu_info(
                self.from_students[self.listWidget.row(item)]
            )
        )
        self.listWidget_2.itemDoubleClicked.connect(
            lambda item: self.show_stu_info(
                self.includes_students[self.listWidget_2.row(item)]
            )
        )
        self.listWidget_3.itemDoubleClicked.connect(
            lambda item: self.show_stu_info(
                self.excludes_students[self.listWidget_3.row(item)]
            )
        )
        self.listWidget_4.itemDoubleClicked.connect(
            lambda item: self.show_stu_info(self.result[self.listWidget_4.row(item)])
        )
        self.select_window: Optional[StudentSelectorWidget] = None
        self.update_widgets()

    def update_widgets(self):
        self.listWidget.clear()
        for s in self.from_students:
            self.listWidget.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))

        self.listWidget_2.clear()
        for s in self.includes_students:
            self.listWidget_2.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))

        self.listWidget_3.clear()
        for s in self.excludes_students:
            self.listWidget_3.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))

    def select_source(self):
        self.select_window = StudentSelectorWidget(
            self,
            self,
            self.main_window.target_class.students.values(),
            self.from_students,
        )
        self.from_students = self.select_window.exec()
        self.listWidget.clear()
        for s in self.from_students:
            self.listWidget.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))
        self.result = []
        self.update_widgets()

    def select_include(self):
        self.select_window = StudentSelectorWidget(
            self,
            self,
            self.main_window.target_class.students.values(),
            self.includes_students,
        )
        self.includes_students = self.select_window.exec(allow_none=True)
        self.listWidget_2.clear()
        for s in self.includes_students:
            self.listWidget_2.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))
        self.result = []
        self.update_widgets()

    def select_exclude(self):
        self.select_window = StudentSelectorWidget(
            self,
            self,
            self.main_window.target_class.students.values(),
            self.excludes_students,
        )
        self.excludes_students = self.select_window.exec(allow_none=True)
        self.listWidget_3.clear()
        for s in self.excludes_students:
            self.listWidget_3.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))
        self.result = []
        self.update_widgets()

    def start(self):
        self.result = self.main_window.random_choose_stu(
            min(
                self.spinBox.value(),
                (len(self.from_students) - len(self.excludes_students)),
            ),
            self.from_students,
            self.includes_students,
            self.excludes_students,
        )
        if not isinstance(self.result, list):
            self.result = [self.result]
        self.listWidget_4.clear()
        for s in self.result:
            self.listWidget_4.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))
        self.update_widgets()

    def show_stu_info(self, stu: Student):
        Base.log("I", f"显示学生信息：{stu.name}", "RandomSelectWindow.show_stu_info")
        self.stu_info_window = StudentWidget(self.main_window, self, stu)
        self.stu_info_window.show()