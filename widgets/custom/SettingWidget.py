"""
设置窗口
"""

from typing import Optional
from utils import ClassObj, question_yes_no, SettingsInfo
from widgets.custom.ListView import ListView
from widgets.basic import *
from widgets.ui.pyside6.SettingWindow import Ui_Form


__all__ = ["SettingWidget"]

class SettingWidget(Ui_Form, MyWidget):
    """设置窗口"""

    def __init__(
        self, master_widget: Optional[WidgetType] = None, main_window: Optional[SettingsInfo] = None
    ):
        """初始化

        :param master_widget: 这个窗口的父窗口
        :param main_window: 程序的主窗口，方便传参"""
        super().__init__(master=master_widget)
        self.setting_obj = main_window
        self.master_widget = master_widget
        self.setupUi(self)
        self.show()
        self.save.clicked.connect(self.accept_save)
        self.cancel.clicked.connect(self.cancel_save)
        self.reset.clicked.connect(self.reset_settings)
        self.setWindowTitle("设置")
        self.init()
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(66)
        self.destroyed.connect(self.update_timer.stop)

    def reset_settings(self):
        if question_yes_no(self, "警告", "确认重置设置？", False, "warning"):
            Base.log("I", "重置设置", "SettingWidget.reset")
            self.setting_obj.reset_settings()
            self.init()

    def init(self):
        # 哇，是shitcode，我们有救了
        self.score_up_color_r.setValue(self.setting_obj.score_up_color_mixin_begin[0])
        self.score_up_color_g.setValue(self.setting_obj.score_up_color_mixin_begin[1])
        self.score_up_color_b.setValue(self.setting_obj.score_up_color_mixin_begin[2])

        self.score_down_color_r.setValue(
            self.setting_obj.score_down_color_mixin_begin[0]
        )
        self.score_down_color_g.setValue(
            self.setting_obj.score_down_color_mixin_begin[1]
        )
        self.score_down_color_b.setValue(
            self.setting_obj.score_down_color_mixin_begin[2]
        )

        self.score_up_color_end_r.setValue(self.setting_obj.score_up_color_mixin_end[0])
        self.score_up_color_end_g.setValue(self.setting_obj.score_up_color_mixin_end[1])
        self.score_up_color_end_b.setValue(self.setting_obj.score_up_color_mixin_end[2])

        self.score_down_color_end_r.setValue(
            self.setting_obj.score_down_color_mixin_end[0]
        )
        self.score_down_color_end_g.setValue(
            self.setting_obj.score_down_color_mixin_end[1]
        )
        self.score_down_color_end_b.setValue(
            self.setting_obj.score_down_color_mixin_end[2]
        )

        self.score_up_color_mixin_start.setValue(
            self.setting_obj.score_up_color_mixin_start
        )
        self.score_down_color_mixin_start.setValue(
            self.setting_obj.score_down_color_mixin_start
        )

        self.score_up_color_step.setValue(self.setting_obj.score_up_color_mixin_step)
        self.score_down_color_step.setValue(self.setting_obj.score_down_color_mixin_step)

        self.opacity.setValue(self.setting_obj.opacity)

        self.autosave.setChecked(self.setting_obj.auto_save_enabled)
        self.autosavetime.setValue(self.setting_obj.auto_save_interval)

        self.savepath.clear()
        self.savepath.addItem("工具箱目录下")
        self.savepath.addItem("用户目录下")
        self.savepath_2.clear()
        self.savepath_2.addItem("无")
        self.savepath_2.addItem("仅保存存档")
        self.savepath_2.addItem("把整个工具备份了（NCW式暴力备份）")

        self.log_keep.setValue(self.setting_obj.log_keep_linecount)
        self.log_update.setValue(self.setting_obj.log_update_interval)
        self.savepath.setCurrentIndex(int(self.setting_obj.auto_save_path != "folder"))

        self.savepath_2.setCurrentIndex(
            0
            if self.setting_obj.auto_backup_scheme == "none"
            else (1 if self.setting_obj.auto_backup_scheme == "only_data" else 2)
        )
        self.horizontalSlider.setValue(
            self.speed_to_index(self.setting_obj.animation_speed)
        )
        self.horizontalSlider.actionTriggered.connect(
            lambda: self.label_26.setText(
                self.update_animation_speed_desc(self.horizontalSlider.value())[1]
            )
        )
        self.label_26.setText(
            self.update_animation_speed_desc(self.horizontalSlider.value())[1]
        )
        self.spinBox.setValue(self.setting_obj.subwindow_x_offset)
        self.spinBox_2.setValue(self.setting_obj.subwindow_y_offset)
        self.spinBox_3.setValue(self.setting_obj.max_framerate)
        self.checkBox.setChecked(self.setting_obj.use_animate_background)

    def update(self):
        self.label_26.setText(
            self.update_animation_speed_desc(self.horizontalSlider.value())[1]
        )
        super().update()

    def update_animation_speed_desc(self, num) -> Tuple[int, str]:
        if num == 1:
            return (0.1, "0.1倍")
        if num == 2:
            return (0.1, "0.1倍")
        if num == 3:
            return (0.2, "0.2倍")
        if num == 4:
            return (0.5, "0.5倍")
        if num == 5:
            return (0.6, "0.6倍")
        if num == 6:
            return (0.8, "0.8倍")
        if num == 7:
            return (0.9, "0.9倍")
        if num == 8:
            return (1, "1倍")
        if num == 9:
            return (1.1, "1.1倍")
        if num == 10:
            return (1.2, "1.2倍")
        if num == 11:
            return (1.5, "1.5倍")
        if num == 12:
            return (1.8, "1.8倍")
        if num == 13:
            return (2, "2倍")
        if num == 14:
            return (3, "3倍")
        if num == 15:
            return (4, "4倍")
        if num == 16:
            return (6, "6倍")
        if num == 17:
            return (8, "8倍")
        if num == 18:
            return (10, "10倍")
        if num == 19:
            return (float("inf"), "关闭")
        if num == 20:
            return (float("inf"), "关闭")

    def speed_to_index(self, animationspeed: float):
        if 0.05 <= animationspeed <= 0.15:
            return 2
        if 0.15 <= animationspeed <= 0.25:
            return 3
        if 0.45 <= animationspeed <= 0.55:
            return 4
        if 0.55 <= animationspeed <= 0.65:
            return 5
        if 0.75 <= animationspeed <= 0.85:
            return 6
        if 0.85 <= animationspeed <= 0.95:
            return 7
        if 0.95 <= animationspeed <= 1.05:
            return 8
        if 1.09 <= animationspeed <= 1.11:
            return 9
        if 1.15 <= animationspeed <= 1.25:
            return 10
        if 1.45 <= animationspeed <= 1.55:
            return 11
        if 1.75 <= animationspeed <= 1.85:
            return 12
        if animationspeed == 2:
            return 13
        if animationspeed == 3:
            return 14
        if animationspeed == 4:
            return 15
        if animationspeed == 6:
            return 16
        if animationspeed == 8:
            return 17
        if animationspeed == 10:
            return 18
        if animationspeed > 114514:
            return 19

    def closeEvent(self, event: QCloseEvent, tip=True):
        if tip:
            if question_yes_no(self, "警告", "退出前保存？", True, "warning"):
                self.accept_save()
        else:
            super().closeEvent(event)

    @Slot()
    def accept_save(self):
        self.setting_obj.score_up_color_mixin_begin = (
            self.score_up_color_r.value(),
            self.score_up_color_g.value(),
            self.score_up_color_b.value(),
        )
        self.setting_obj.score_down_color_mixin_begin = (
            self.score_down_color_r.value(),
            self.score_down_color_g.value(),
            self.score_down_color_b.value(),
        )
        self.setting_obj.score_up_color_mixin_end = (
            self.score_up_color_end_r.value(),
            self.score_up_color_end_g.value(),
            self.score_up_color_end_b.value(),
        )
        self.setting_obj.score_down_color_mixin_end = (
            self.score_down_color_end_r.value(),
            self.score_down_color_end_g.value(),
            self.score_down_color_end_b.value(),
        )
        self.setting_obj.score_up_color_mixin_step = self.score_up_color_step.value()

        self.setting_obj.score_down_color_mixin_step = self.score_down_color_step.value()

        self.setting_obj.score_up_color_mixin_start = (
            self.score_up_color_mixin_start.value()
        )

        self.setting_obj.score_down_color_mixin_start = (
            self.score_down_color_mixin_start.value()
        )

        self.setting_obj.opacity = self.opacity.value()

        self.setting_obj.log_keep_linecount = self.log_keep.value()
        self.setting_obj.log_update_interval = self.log_update.value()

        self.setting_obj.auto_save_enabled = self.autosave.isChecked()
        self.setting_obj.auto_save_interval = self.autosavetime.value()
        self.setting_obj.auto_save_path = (
            "folder" if self.savepath.currentIndex() == 0 else "user"
        )
        self.setting_obj.auto_backup_scheme = (
            "none"
            if self.savepath_2.currentIndex() == 0
            else "only_data" if self.savepath_2.currentIndex() == 1 else "all"
        )

        self.setting_obj.animation_speed = self.update_animation_speed_desc(
            self.horizontalSlider.value()
        )[0]

        self.setting_obj.subwindow_x_offset = self.spinBox.value()
        self.setting_obj.subwindow_y_offset = self.spinBox_2.value()
        self.setting_obj.max_framerate = self.spinBox_3.value()
        self.setting_obj.use_animate_background = self.checkBox.isChecked()
        self.setting_obj.save_current_settings()    # XXX 这里其实有点逻辑问题的
        self.closeEvent(QCloseEvent(), tip=False)

    @Slot()
    def cancel_save(self):
        Base.log("I", "取消保存", "SettingWidget.cancel_save")
        self.closeEvent(QCloseEvent(), tip=False)