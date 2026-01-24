"""
作业分结算窗口所在模块
"""

from typing import (
    Optional, 
    Dict, 
    List
)
from utils import ( 
    Class, 
    ClassObj, 
    ScoreModificationTemplate, 
    HomeworkRule, 
    ScoreModification, 
    question_yes_no
)
from widgets.custom.ListView import ListView
from widgets.basic import *
from widgets.ui.pyside6.HomeworkScoreSumUp import Ui_Form

__all__ = ["HomeworkScoreSumUpWidget"]

class HomeworkScoreSumUpWidget(Ui_Form, MyWidget):
    """
    作业分结算窗口
    """

    def __init__(
        self,
        master: Optional[WidgetType] = None,
        main_window: Optional[ClassObj] = None,
        target_class: Class = None,
        target_students: Dict[int, Student] = None,
    ):
        super().__init__(master)
        self.setupUi(self)
        self.main_window = main_window
        self.master = master
        self.target_class = target_class
        self.target_students = target_students
        self.mapping: Dict[int, Student] = {}
        self.buttons: Dict[int, ObjectButton] = {}
        self.comboBox_3.clear()
        self.comboBox_3.addItems(
            [
                str(8),
                str(9),
                str(10),
                str(11),
                str(12),
            ]
        )
        self.homework_rules = target_class.homework_rules
        self.comboBox_4.clear()
        self.comboBox_4.addItems(["添加一项", "删除一项", "查看信息", "全部删除"])
        self.comboBox.clear()
        self.sent_list: Dict[int, List[ScoreModification]] = {}
        "已经发送的列表"
        error_template = ScoreModificationTemplate(
            "error",
            0,
            "没有内置的作业常规分方案",
            "请完善default.py中Class的homework_rule",
        )
        self.subject_list: Dict[int, HomeworkRule] = {
            -1: HomeworkRule("error", "列表为空", "", {"列表为空": error_template})
        }
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_buttons)
        self.update_timer.start(100)
        self.destroyed.connect(self.update_timer.stop)
        self.current_template: Optional[ScoreModificationTemplate] = None
        for index, rule in enumerate(self.homework_rules.values()):
            self.subject_list[index] = rule
            self.comboBox.addItem(rule.subject_name)

        self.pushButton.clicked.connect(
            lambda: QMessageBox.information(
                self, "emm", "懒得写，要不你帮我写吧\n（不要用奇怪的眼神看我）"
            )
        )
        self.optional_template_mapping: Dict[int, ScoreModificationTemplate] = {
            -1: error_template
        }
        self.comboBox_13.clear()
        for t in [
            _t for _t in self.main_window.modify_templates.values() if _t.is_visible
        ]:
            self.comboBox_13.addItem(t.title)
            # -1的原因：有一个是error_template
            self.optional_template_mapping[len(self.optional_template_mapping) - 1] = t

        self.anims: Dict[int, QPropertyAnimation] = {}

        self.comboBox.setCurrentIndex(0)
        self.comboBox_3.setCurrentIndex(2)
        self.comboBox_4.setCurrentIndex(0)
        self.comboBox_13.setCurrentIndex(0)

        self.subject_changed()
        self.modification_changed()
        self.width_changed()

        self.comboBox.currentIndexChanged.connect(self.subject_changed)
        self.comboBox_2.currentIndexChanged.connect(self.modification_changed)
        self.comboBox_3.currentIndexChanged.connect(self.width_changed)
        self.comboBox_13.currentIndexChanged.connect(self.modification_changed)
        self.tabWidget_2.currentChanged.connect(self.modification_changed)

    def subject_changed(self):

        index = self.comboBox.currentIndex()
        Base.log("I", f"选中项目：{index}", "HomeworkSumpWidget.subject_changed")

        self.current_subject = self.subject_list[index]
        Base.log(
            "I",
            f"对应科目：{self.current_subject.subject_name}",
            "HomeworkSumpWidget.subject_changed",
        )

        self.current_modifacion_list: Dict[int, ScoreModificationTemplate] = {
            -1: ScoreModificationTemplate("error", 0, "出错了", "出错了")
        }
        Base.log("I", "清空列表", "HomeworkSumpWidget.subject_changed")

        self.comboBox_2.clear()
        Base.log("I", "清空comboBox", "HomeworkSumpWidget.subject_changed")

        for index, (subject, template) in enumerate(
            self.current_subject.rule_mapping.items()
        ):
            self.current_modifacion_list[index] = template
            self.comboBox_2.addItem(subject)

        Base.log(
            "I",
            f"多选窗口规则列表长度：{len(self.current_modifacion_list)}",
            "HomeworkSumpWidget.subject_changed",
        )

        self.comboBox_2.setCurrentIndex(0)

        self.modification_changed()

    def modification_changed(self):
        if self.tabWidget_2.currentIndex() == 0:
            Base.log(
                "I",
                f"作业等第模式模板更换，index = {self.comboBox_2.currentIndex()}",
                "HomeworkSumpWidget.modification_changed",
            )
            index = self.comboBox_2.currentIndex()
            self.current_template = self.current_modifacion_list[index]
            self.lineEdit.setText(str(self.current_template.title))
            self.lineEdit_2.setText(str(self.current_template.desc))
            self.doubleSpinBox.setValue(self.current_template.mod)
        else:
            Base.log(
                "I",
                f"自定义模板模式模板更换，index = {self.comboBox_13.currentIndex()}",
                "HomeworkSumpWidget.modification_changed",
            )
            index = self.comboBox_13.currentIndex()
            self.current_template = self.optional_template_mapping[index]
            self.lineEdit.setText(str(self.current_template.title))
            self.lineEdit_2.setText(str(self.current_template.desc))
            self.doubleSpinBox.setValue(self.current_template.mod)

    def width_changed(self):
        Base.log(
            "I",
            f"多选窗口宽度设置为：{self.comboBox_3.currentText()}",
            "HomeworkSumpWidget.width_changed",
        )
        for i in range(self.widget.count()):
            if isinstance(self.widget.itemAt(i).widget(), ObjectButton):
                self.widget.itemAt(i).widget().deleteLater()
        row = 0
        col = 0
        for num, stu in self.target_students.items():
            if num not in self.sent_list:
                self.sent_list[num] = []
            self.mapping[num] = stu
            button = ObjectButton(f"{stu.num}号 {stu.name}\n{stu.score}分", self.tab)
            self.widget.addWidget(button, row, col, 1, 1)
            self.buttons[num] = button
            self.buttons[num].clicked.connect(
                lambda _=None, num=num: self.do_action(num)
            )
            self.buttons[num].setFixedSize(QSize(81, 51))
            col += 1
            if col > self.comboBox_3.currentIndex() + 8 - 1:
                col = 0
                row += 1

    def update_buttons(self):
        for num, button in self.buttons.items():
            button.setText(
                f"{self.mapping[num].num}号 "
                + self.mapping[num].name
                + f"\n{self.mapping[num].score}分"
            )

    def do_action(self, num: int):
        Base.log(
            "I",
            f"进行操作：学生学号为{num}",
            "HomeworkSumpWidget.show_stu_homework_info",
        )
        mode = self.comboBox_4.currentIndex()
        if mode == 0:
            mode = "add"
        elif mode == 1:
            mode = "sub"
        elif mode == 2:
            mode = "info"
        elif mode == 3:
            mode = "clear"

        Base.log("I", "操作模式：" + mode, "HomeworkSumpWidget.show_stu_homework_info")
        if mode == "add":
            self.sent_list[num].append(
                ScoreModification(
                    self.current_template,
                    self.target_students[num],
                    (
                        self.lineEdit.text()
                        if self.lineEdit.text() != self.current_template.title
                        else None
                    ),
                    (
                        self.lineEdit_2.text()
                        if self.lineEdit_2.text() != self.current_template.desc
                        else None
                    ),
                    (
                        self.doubleSpinBox.value()
                        if self.doubleSpinBox.value() != self.current_template.mod
                        else None
                    ),
                )
            )
            self.main_window.send_modify_instance(self.sent_list[num][-1], "<作业登分>")
            self.anims[num] = QPropertyAnimation(self.buttons[num], b"color")
            self.anims[num].setDuration(300)
            self.anims[num].setStartValue(
                QColor(216, 255, 216)
                if self.sent_list[num][-1].mod > 0
                else (
                    QColor(255, 216, 216)
                    if self.sent_list[num][-1].mod < 0
                    else QColor(216, 244, 255)
                )
            )
            self.anims[num].setEndValue(QColor(255, 255, 255))
            self.anims[num].start()

        if mode == "sub":
            self.list_view = ListView(
                self.main_window, self, "已发送的作业等第点评", None
            )

            self.list_view.setData(
                [
                    (text, func, args)
                    for text, func, args in [
                        (
                            f"{m.title} {m.execute_time.split('.')[0]} {m.mod:+.1f}",
                            lambda m=m: (
                                self.main_window.retract_modify(m, "<作业登分>"),
                                self.sent_list[num].remove(m),
                                self.list_view.close(),
                            ),
                            (
                                (
                                    QColor(202, 255, 222)
                                    if m.mod > 0
                                    else (
                                        QColor(255, 202, 202)
                                        if m.mod < 0
                                        else QColor(201, 232, 255)
                                    )
                                ),
                                (
                                    QColor(232, 255, 232)
                                    if m.mod > 0
                                    else (
                                        QColor(255, 232, 232)
                                        if m.mod < 0
                                        else QColor(233, 244, 255)
                                    )
                                ),
                            ),
                        )
                        for m in reversed(self.sent_list[num])
                        if m.executed
                    ]
                ]
            )

            self.list_view.show()

        if mode == "info":
            self.list_view = ListView(
                self.main_window, self, "已发送的作业等第点评", None
            )
            self.list_view.setData(
                [
                    (text, func, args)
                    for text, func, args in [
                        (
                            f"{m.title} {m.execute_time.split('.')[0]} {m.mod:+.1f}",
                            lambda m=m, index=index: (
                                self.main_window.history_window(
                                    m, index, self.list_view, master=self
                                ),
                            ),
                            (
                                (
                                    QColor(202, 255, 222)
                                    if m.mod > 0
                                    else (
                                        QColor(255, 202, 202)
                                        if m.mod < 0
                                        else QColor(201, 232, 255)
                                    )
                                ),
                                (
                                    QColor(232, 255, 232)
                                    if m.mod > 0
                                    else (
                                        QColor(255, 232, 232)
                                        if m.mod < 0
                                        else QColor(233, 244, 255)
                                    )
                                ),
                            ),
                        )
                        for index, m in enumerate(reversed(self.sent_list[num]))
                        if m.executed
                    ]
                ]
            )

            self.list_view.show()

        if mode == "clear":
            if not len([m for m in self.sent_list[num] if m.executed]):
                QMessageBox.information(
                    self.main_window,
                    "提示",
                    f"烫知识：你选择的{num}号并没有发送任何作业等第点评",
                )
                return
            if question_yes_no(
                self.main_window,
                "确认",
                f"确定要把刚刚所有的作业等第点评全部删除吗？\n（选中了{num}号，已经发送了{len([m for m in self.sent_list[num] if m.executed])}个）",
                False,
                "warning",
            ):
                self.main_window.retract_modify(
                    [m for m in self.sent_list[num] if m.executed], "<作业登分>"
                )
                self.sent_list[num] = []