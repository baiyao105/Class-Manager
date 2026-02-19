"""
考勤信息展示窗口所在模块
"""

from __future__ import annotations

import time
import copy

from utils.basetypes import Base
from utils.classobjects import  ClassDataSet, Student
from utils.qtconfig import QWidget, QListWidgetItem, QCloseEvent, Slot

from widgets.basic import UIError, MyWidget
from widgets.templates import CleaingScoreSumUp



class TargetClassNotSetError(UIError):
    "还没有设置目标班级。"    

class CleaningMappingNotSetError(UIError):
    "还没有设置卫生人员表。"


class CleaningScoreSumUpWidget(CleaingScoreSumUp.Ui_Form, MyWidget):
    def __init__(
        self, 
        dataset: ClassDataSet,
        master: QWidget | None = None,
    ):
        """
        初始化

        :param dataset: 数据库
        :param master: 这个窗口的父窗口
        """
        super().__init__(master=master)
        self.dataset = dataset
        self.setupUi(self) # pyright: ignore[reportUnknownMemberType]
        self.finished = False
        self.leader: list[Student] = []
        self.member = []
        self.comboBox.clear()
        self.comboBox.addItems(["星期一", "星期二", "星期三", "星期四", "星期五"])
        self.comboBox_2.clear()
        self.comboBox_2.addItems(["5.0", "4.9", "4.8", "4.7", "4.6及以下"])
        self.mod_leader = [
            "cleaning_5.0_leader",
            "cleaning_4.9_leader",
            "cleaning_4.8_leader",
            "cleaning_4.7_leader",
            "cleaning_4.6_and_lower_leader",
        ]
        "适用于组长的分数模板"


        self.mod_member = [
            "cleaning_5.0_member",
            "cleaning_4.9_member",
            "cleaning_4.8_member",
            "cleaning_4.7_member",
            "cleaning_4.6_and_lower_member",
        ]
        "适用于成员的分数模板"

        self.comboBox.setCurrentIndex(
            min((time.localtime().tm_wday + 7 - 1) % 7, 4)
        )  # 因为第二天才会出分数所以要减1（会人性化很多）
        self.comboBox_2.setCurrentIndex(1)
        self.update_students()
        self.buttonBox.accepted.connect(self.commit)
        self.buttonBox.rejected.connect(self.cancel)
        self.comboBox.currentIndexChanged.connect(
            lambda: self.update_students(refresh_stu=True)
        )
        self.comboBox_2.currentIndexChanged.connect(
            lambda: self.update_students(refresh_stu=False)
        )

        self.listWidget.itemDoubleClicked.connect(self.remove_from_list)
        self.show()

    def show(self):
        super().show()
        self.finished = False
        self.update_students()

    def update_students(self, refresh_stu: bool = True):
        "更新学生"
        if self.dataset.target_class is None:
            raise TargetClassNotSetError("还没设置目标班级就尝试更新学生")
        if self.dataset.target_class.cleaning_mapping is None:
            raise CleaningMappingNotSetError("请先设置一下卫生人员表")
        
        self.label_5.setText(
            self.dataset.modify_templates[
                self.mod_member[self.comboBox_2.currentIndex()]
            ].desc
        )
        selected = self.comboBox.currentIndex() + 1
        if refresh_stu:
            self.leader = copy.deepcopy(
                self.dataset.target_class.cleaning_mapping[selected]["leader"]
            )
            self.member = copy.deepcopy(
                self.dataset.target_class.cleaning_mapping[selected]["member"]
            )

        self.listWidget.clear()
        for s in self.leader:
            index = self.comboBox_2.currentIndex()
            if index == 0:
                score = self.dataset.modify_templates["cleaning_5.0_leader"].mod
            elif index == 1:
                score = self.dataset.modify_templates["cleaning_4.9_leader"].mod
            elif index == 2:
                score = self.dataset.modify_templates["cleaning_4.8_leader"].mod
            elif index == 3:
                score = self.dataset.modify_templates["cleaning_4.7_leader"].mod
            else:
                score = self.dataset.modify_templates[
                    "cleaning_4.6_and_lower_leader"
                ].mod
            self.listWidget.addItem(
                QListWidgetItem(f"{s.num}号 {s.name} ({score:+.1f}) <组长>")
            )

        for s in self.member:
            index = self.comboBox_2.currentIndex()
            if index == 0:
                score = self.dataset.modify_templates["cleaning_5.0_member"].mod
            elif index == 1:
                score = self.dataset.modify_templates["cleaning_4.9_member"].mod
            elif index == 2:
                score = self.dataset.modify_templates["cleaning_4.8_member"].mod
            elif index == 3:
                score = self.dataset.modify_templates["cleaning_4.7_member"].mod
            else:
                score = self.dataset.modify_templates[
                    "cleaning_4.6_and_lower_member"
                ].mod
            self.listWidget.addItem(
                QListWidgetItem(f"{s.num}号 {s.name} ({score:+.1f})")
            )

    def remove_from_list(self):
        "从列表中移除"
        if self.listWidget.currentRow() == 0 and self.leader != []:
            s = self.leader.pop(0)
            Base.log(
                "I",
                f"从组长列表移除{s.num}，"
                f"当前列表：{[s.num for s in self.leader]}",
                "CleaningScoreSumUpWidget.remove_from_list",
            )
            self.update_students(refresh_stu=False)
        else:
            s = self.member.pop(
                self.listWidget.currentRow() - (1 if self.leader != [] else 0)
            )
            Base.log(
                "I",
                f"从成员列表移除{s.num}，"
                f"当前列表：{[s.num for s in self.member]}",
                "CleaningScoreSumUpWidget.remove_from_list",
            )
            self.update_students(refresh_stu=False)

    @Slot()
    def commit(self):
        "提交按钮"
        Base.log(
            "I",
            f"提交按钮被点击，结果：组长{[s.num for s in self.leader]} 成员{[s.num for s in self.member]}",
            "CleaningScoreSumUpWidget.commit",
        )
        if not self.finished:
            self.finished = True

            self.dataset.send_modify(
                self.mod_leader[self.comboBox_2.currentIndex()],
                [
                    self.dataset.classes[l.belongs_to].students[l.num]
                    for l in self.leader
                ],
            )

            self.dataset.send_modify(
                self.mod_member[self.comboBox_2.currentIndex()],
                [
                    self.dataset.classes[m.belongs_to].students[m.num]
                    for m in self.member
                ],
            )

            self.closeEvent(QCloseEvent())

    @Slot()
    def cancel(self):
        "取消按钮"
        self.closeEvent(QCloseEvent())




__all__ = ["CleaningScoreSumUpWidget"]

