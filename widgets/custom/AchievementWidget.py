"""
成就信息展示窗口所在模块
"""

from typing import Optional
from utils import Achievement, AchievementTemplate, ClassObj
from widgets.custom.ListView import ListView
from widgets.basic import *
from widgets.ui.pyside6.AchievementWindow import Ui_Form

__all__ = ["AchievementWidget"]


class AchievementWidget(Ui_Form, MyWidget):
    "成就信息展示窗口"
    def __init__(
        self,
        master_widget: Optional[WidgetType] = None,
        main_window: Optional[ClassObj] = None,
        achievement: Union[Achievement, AchievementTemplate] = None,
    ):
        """
        初始化

        :param master_widget: 这个窗口的父窗口
        :param main_window: 程序的主窗口，方便传参
        """
        super().__init__(master=master_widget)
        self.main_window = main_window
        self.master_widget = master_widget
        self.achievement = achievement
        self.setupUi(self)
        self.show()
        self.setWindowTitle("成就详情")
        if isinstance(self.achievement, Achievement):
            self.label_11.setText(self.achievement.target.name)
            self.label_13.setText(str(self.achievement.target.score))
            self.label_15.setText("不到啊，可能是侦测器爆了")
            self.label_7.setText(str(self.achievement.time))

            for i, s in self.main_window.class_obs.rank_non_dumplicate:
                if (
                    s.num == self.achievement.target.num
                    and s.belongs_to == self.achievement.target.belongs_to
                ):
                    self.label_15.setText(str(i))
                    break
            self.achievement = self.achievement.temp

        self.label_5.setText(self.achievement.name)
        self.label_6.setText(self.achievement.desc)
        self.textBrowser.setPlainText(
            self.achievement.condition_desc(self.main_window.class_obs)
        )
        self.textBrowser_2.setPlainText(self.achievement.further_info)

