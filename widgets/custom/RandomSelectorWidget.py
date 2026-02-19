"""
随机点名窗口所在模块
"""
from __future__ import annotations

from utils import ClassDataSet, Student

from utils.basetypes import Base
from utils.qtconfig import QWidget, QListWidgetItem

from widgets.custom.StudentWidget import StudentWidget
from widgets.custom.StudentSelectorWidget import StudentSelectorWidget
from widgets.basic import MyWidget, UIError
from widgets.templates import RandomSelector

class TargetClassNotSetError(UIError):
    "没有设置目标班级。"

class RandomSelectWidget(RandomSelector.Ui_Form, MyWidget):
    """
    随机点名窗口
    """

    def __init__(
        self, 
        dataset: ClassDataSet, master: QWidget | None = None
    ):
        super().__init__(master)
        self.dataset = dataset
        self.master = master
        self.setupUi(self) # pyright: ignore[reportUnknownMemberType]
        if not dataset.target_class:
            raise TargetClassNotSetError("在还没有设置班级的时候尝试构造了随即点名窗口")
        self.target_class = dataset.target_class
        self.from_students: list[Student] = list(
            self.target_class.students.values()
        )
        self.includes_students: list[Student] = []
        self.excludes_students: list[Student] = []
        self.result: list[Student] = []
        self.pushButton.clicked.connect(self.start)
        self.pushButton_2.clicked.connect(self.select_source)
        self.pushButton_3.clicked.connect(self.select_include)
        self.pushButton_4.clicked.connect(self.handle_from_item_clicked)
        self.listWidget_2.itemDoubleClicked.connect(self.handle_include_item_clicked)
        self.listWidget_3.itemDoubleClicked.connect(self.handle_exclude_item_clicked)
        self.listWidget_4.itemDoubleClicked.connect(self.handle_result_item_clicked)
        self.select_window: StudentSelectorWidget | None = None
        self.update_widgets()

    def handle_from_item_clicked(self, item: QListWidgetItem):
        self.show_stu_info(self.from_students[self.listWidget.row(item)])

    def handle_include_item_clicked(self, item: QListWidgetItem):
        self.show_stu_info(self.includes_students[self.listWidget_2.row(item)])
    
    def handle_exclude_item_clicked(self, item: QListWidgetItem):
        self.show_stu_info(self.excludes_students[self.listWidget_3.row(item)])
    
    def handle_result_item_clicked(self, item: QListWidgetItem):
        self.show_stu_info(self.result[self.listWidget_4.row(item)])

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
            self.dataset,
            self,
            self.target_class.students.values(),
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
            self.dataset,
            self,
            self.target_class.students.values(),
            self.includes_students
        )
        self.includes_students = self.select_window.exec(allow_none=True)
        self.listWidget_2.clear()
        for s in self.includes_students:
            self.listWidget_2.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))
        self.result = []
        self.update_widgets()

    def select_exclude(self):
        self.select_window = StudentSelectorWidget(
            self.dataset,
            self,
            self.target_class.students.values(),
            self.excludes_students,
        )
        self.excludes_students = self.select_window.exec(allow_none=True)
        self.listWidget_3.clear()
        for s in self.excludes_students:
            self.listWidget_3.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))
        self.result = []
        self.update_widgets()

    def start(self):
        result = self.dataset.random_choose_stu(
            min(
                self.spinBox.value(),
                (len(self.from_students) - len(self.excludes_students)),
            ),
            self.from_students,
            self.includes_students,
            self.excludes_students,
        )
        if not isinstance(result, list):
            self.result = [result]
        else:
            self.result = result
        self.listWidget_4.clear()
        for s in self.result:
            self.listWidget_4.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))
        self.update_widgets()

    def show_stu_info(self, stu: Student):
        Base.log("I", f"显示学生信息：{stu.name}", "RandomSelectWindow.show_stu_info")
        self.stu_info_window = StudentWidget(dataset=self.dataset, master=self, student=stu)
        self.stu_info_window.show()

__all__ = ["RandomSelectWidget"]
