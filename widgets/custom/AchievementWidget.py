"""
成就信息展示窗口所在模块
"""

from __future__ import annotations

from utils.basetypes import Base
from utils.classobjects import Achievement, AchievementTemplate, ClassDataSet
from utils.qtconfig import QWidget

from widgets.basic import MyWidget
from widgets.templates import AchievementWindow



class AchievementWidget(AchievementWindow.Ui_Form, MyWidget):
    "成就信息展示窗口"
    def __init__(
        self,
        dataset: ClassDataSet,
        achievement: Achievement | AchievementTemplate,
        master: QWidget | None = None
    ):
        """
        初始化

        :param master_widget: 这个窗口的父窗口
        :param main_window: 程序的主窗口，方便传参
        """
        super().__init__(master=master)
        self.dataset = dataset
        self.master_widget = master
        self.achievement_temp = achievement
        self.setupUi(self) # type: ignore
        self.show()
        self.setWindowTitle("成就详情")
        if isinstance(self.achievement_temp, Achievement):
            self.label_11.setText(self.achievement_temp.target.name)
            self.label_13.setText(str(self.achievement_temp.target.score))
            self.label_15.setText("不到啊，可能是侦测器爆了")
            self.label_7.setText(str(self.achievement_temp.time))

            if self.dataset.class_obs:
                for i, s in self.dataset.class_obs.rank_non_dumplicate:
                    if (
                        s.num == self.achievement_temp.target.num
                        and s.belongs_to == self.achievement_temp.target.belongs_to
                    ):
                        self.label_15.setText(str(i))
                        break
                
            else:
                Base.log("W", "在尝试设置成就窗口时发现dataset.classobs为None", "AcheievementWidget.__init__")
            self.achievement_temp = self.achievement_temp.temp


        self.label_5.setText(self.achievement_temp.name)
        self.label_6.setText(self.achievement_temp.desc)
        if self.dataset.class_obs:
            self.textBrowser.setPlainText(
                self.achievement_temp.condition_desc(self.dataset.class_obs)
            )
        else:
            self.textBrowser.setPlainText("班级侦测器爆掉了！")
            
        
        self.textBrowser_2.setPlainText(self.achievement_temp.further_info)


__all__ = ["AchievementWidget"]
