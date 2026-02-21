"""
班级数据模型和UI对接有关的模型。
"""

from __future__ import annotations

import os
import time
from typing import Any

import pyqtgraph as pg # type: ignore

from control.classwindow.ui_model.class_ui_model import ClassUIModel
from utils.algorithm import Thread
from utils.basetypes import Base, SysMemTracer
from utils.classobjects import Student
from utils.consts import (
    qt_version, app_style, app_stylesheet, 
    enable_memory_tracing
)
from utils.functions.qtutils import wait_until
from utils.qtconfig import (
    QApplication, QStyleFactory, QWidget, Signal, QMessageBox, QIcon, QPixmap,
    QLabel, QCloseEvent, Qt, Slot
)

from .template_manage_model import TemplateManageModel
from .action_history_model import ActionHistoryModel
from .animated_background_model import AnimatedBackgroundModel
from .fast_cmd_model import FastCommandModel
from .log_display_model import LogDisplayModel
from .operation_model import OperationModel
from .tip_viewer_model import TipViewerModel
from .update_widget_model import UpdateWidgetModel
from .user_display_model import UserDisplayModel
from .object_info_model import ObjectInfoModel
from ..ui_model.basic_models.basic_ui import BasicUIModel


sys_mem_tracer = SysMemTracer(record_data=True)
if enable_memory_tracing:
    sys_mem_tracer.start()

class ClassWindowModel(
    UpdateWidgetModel, 
    OperationModel, 
    ObjectInfoModel,
    TemplateManageModel, 
    TipViewerModel,
    ActionHistoryModel,
    AnimatedBackgroundModel,
    FastCommandModel,
    LogDisplayModel,
    UserDisplayModel,
    ClassUIModel
):

    signal_exiting: Signal = Signal()
    "即将退出的信号"

    def __init__(self, 
            app: QApplication, 
            current_user: str, 
            class_name: str, 
            class_key: str, 
            save_path: str | None = None
        ):
        """
        窗口初始化
        :param app: QApplication
        :param args: 命令行参数
        :param class_name: 班级名称
        :param current_user: 当前用户
        :param class_key: 班级键
        """
        Base.log("D", "初始化ClassWindowModel", "ClassWindowModel.__init__")

        self.app = app
        "应用程序对象"

        if qt_version in ("PySide6", "PyQt6"):
            style = QStyleFactory.create(app_style)
            if style:
                self.app.setStyle(style)
            self.app.setStyleSheet(app_stylesheet)

        kwargs: dict[str, Any] = {
            "self": self, 
            "current_user": current_user, 
            "class_name": class_name, 
            "class_key": class_key, 
            "save_path": save_path
        }
        
        super_classes: list[type] = [
            ClassUIModel,
            UpdateWidgetModel,
            OperationModel,
            ObjectInfoModel,
            TemplateManageModel,
            TipViewerModel,
            ActionHistoryModel,
            AnimatedBackgroundModel,
            FastCommandModel,
            LogDisplayModel,
            UserDisplayModel,
        ]
        for cls in super_classes:
            cls.__init__(**kwargs) # type: ignore
      
        self.exit_action_finished: bool = False
        "退出动作是否完成"

        assert self.target_class, "设置过班级了应该就不会为None了"

        self.icon: QIcon | None = None
        "窗口图标"

        self.create_time = time.time()
        "程序创建时间"

        self.action.triggered.connect(self.student_rank)
        self.action_2.triggered.connect(self.manage_templates)
        self.action_3.triggered.connect(self.open_setting_window)
        self.action_5.triggered.connect(self.scoring_select)
        self.action_7.triggered.connect(self.retract_lastest)
        self.action_8.triggered.connect(lambda: self.tabWidget_2.setCurrentIndex(1))
        self.action_9.triggered.connect(lambda: self.tabWidget_2.setCurrentIndex(0))
        self.action_10.triggered.connect(self.save)
        self.action_12.triggered.connect(self.reset_scores)
        self.action_13.triggered.connect(self.show_all_history)
        self.action_14.triggered.connect(self.save_data_as)
        self.action_15.triggered.connect(self.music_selector)
        self.action_16.triggered.connect(self.show_recover_points)
        self.action_17.triggered.connect(self.create_recover_point)
        self.action_18.triggered.connect(self.cleaning_score_sum_up)
        self.action_19.triggered.connect(self.show_attendance)
        self.action_20.triggered.connect(self.show_noise_detector)
        self.action_21.triggered.connect(self.random_select)
        self.action_22.triggered.connect(self.homework_score_sum_up)
        self.action_23.triggered.connect(self.about_this)
        self.action_24.triggered.connect(self.show_update_log)
        self.action_25.triggered.connect(
            lambda: Thread(
                target=lambda: self.updator_thread.detect_new_version()
            ).start()
        )
        self.action_26.triggered.connect(self.refresh_window)
        self.action_28.triggered.connect(self.show_debug_window)
        self.actionNew_Template.triggered.connect(self.new_template)  # 笑死唯一一个不是默认名字的action控件
        
        self.setFixedSize(self.width(), self.height())
        self.signal_exiting.connect(self.slot_exiting)
        self.setWindowTitle(f"班寄管理 - {self.target_class.name}")

    def on_start_up_finished(self):
        """
        窗口启动完成
        """

    def on_exit(self):
        """
        窗口准备退出
        """
        self.signal_exiting.emit()

    @Slot()
    def slot_exiting(self):
        Base.log("I", "开始执行退出操作", "ClassWindowModel._on_exit")
        self.stop()
        self.exit_action_finished = True

    def closeEvent(self, event: QCloseEvent, tip: bool = True):
        """
        关闭事件，这里是覆写的MyClassWindowModel.closeEvent

        :param event: 传来的QCloseEvent
        """
        Base.log("I", "准备关闭程序", "ClassWindowModel.closeEvent")
        if super(BasicUIModel, self).requestExit(event):
            self.setEnabled(False)
            self.exit_tip = QLabel(self)
            self.exit_tip.setText("正在保存数据...")
            self.exit_tip.setStyleSheet(
                "background-color: rgb(197, 197, 197); border-radius: 8px"
            )
            self.exit_tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.exit_tip.setGeometry(
                self.width() // 2 - 70, self.height() // 2 - 20, 140, 40
            )
            self.exit_tip.show()
            self.exit_action_finished = False
            self.signal_exiting.emit()
            wait_until(lambda: self.exit_action_finished)
            self.hide()
            if enable_memory_tracing:
                Base.log("I", "绘制内存使用记录", "ClassWindowModel.closeEvent")
                sys_mem_tracer_widget = pg.PlotWidget()
                sys_mem_tracer_widget = pg.plot(title="内存使用记录", clear=True) # type: ignore
                sys_mem_tracer_widget.plot(
                    list(sys_mem_tracer.data.keys()), 
                    list(sys_mem_tracer.data.values()), 
                    pen=(255, 0, 0)
                )
                sys_mem_tracer_widget.show()
                wait_until(lambda: sys_mem_tracer_widget.isHidden())
            Base.log("I", "执行app.quit()", "ClassWindowModel.closeEvent")
            self.app.quit()

    def stop(self):
        super().stop()
    
    def mainloop(self) -> int:
        """
        主循环，跟tk的差不多
        """
        Base.log("I", "mainloop启动中...", "ClassWindowModel.mainloop")
        self.is_running = True
        self.insert_action_history_info(
            "双击这种列表项目可查看信息",
            lambda: QMessageBox.information(self, "。", "孩子真棒"),
        )
        self.icon = QIcon()
        self.icon.addPixmap(
            QPixmap(os.path.join(self.img_path, "facicon.ico")), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.setWindowIcon(self.icon)
        self.on_start_up_finished()
        self.refresh_hint_widget()
        self.show()
        self.updator_thread.start()
        Base.log("I", "线程启动完成，exec()", "ClassWindowModel.mainloop")
        status = self.app.exec()
        Base.log("I", f"主循环返回值：{status}", "ClassWindowModel.mainloop")
        self.app.quit()
        self.updator_thread.terminate()
        self.tip_handler.terminate()
        Base.log("I", "线程已终止，退出mainloop", "ClassWindowModel")
        return status
    
    @Slot()
    def edit_fast_command_btns(self):
        return super().edit_fast_command_btns()
    
    @Slot()
    def update_recent_command_btns(self):
        return super().update_recent_command_btns()
    
    @Slot(int)
    def dont_click(self, style: int | None = 0):
        return super().dont_click(style)

    @Slot()
    @FastCommandModel.as_method_command("about_this", "关于工具")
    def about_this(self):
        return super().about_this()
    
    @Slot()
    @FastCommandModel.as_method_command("open_setting_window", "设置窗口")
    def open_setting_window(self):
        return super().open_setting_window()

    @Slot()
    @FastCommandModel.as_method_command("student_rank", "学生排名")
    def student_rank(self):
        return super().student_rank()
    
    @Slot()
    @FastCommandModel.as_method_command("manage_templates", "管理模板")
    def manage_templates(self):
        return super().manage_templates()
    
    @Slot() # 也算是 Slot() 吧。。。
    @FastCommandModel.as_method_command("scoring_select", "多选学生")
    def scoring_select(self, *, students: list[Student] | None = None):
        return super().scoring_select(students=students)

    @Slot()
    @FastCommandModel.as_method_command("retract_lastest", "撤回上步")
    def retract_lastest(self):
        return super().retract_lastest()
    
    @Slot()
    @FastCommandModel.as_method_command("save", "保存数据")
    def save(self):
        return super().save()
        
    @Slot()
    @FastCommandModel.as_method_command("reset_scores", "重置分数")
    def reset_scores(self):
        return super().reset_scores()
    
    @Slot()
    @FastCommandModel.as_method_command("show_all_history", "历史记录")
    def show_all_history(self) -> None:
        return super().show_all_history()

    @Slot()
    @FastCommandModel.as_method_command("show_recover_points", "显示还原点")
    def show_recover_points(self):
        return super().show_recover_points()
    
    @FastCommandModel.as_method_command("create_recover_point", "创建还原点")
    def create_recover_point(self):
        return super().create_recover_point()
    
    @FastCommandModel.as_method_command("cleaning_score_sum_up", "卫生分结算")
    def cleaning_score_sum_up(self):
        return super().cleaning_score_sum_up()
    
    @Slot()
    @FastCommandModel.as_method_command("music_selector", "播放音乐")
    def music_selector(self):
        return super().music_selector()
    
    @Slot()
    @FastCommandModel.as_method_command("show_noise_detector", "噪声检测器")    
    def show_noise_detector(self):
        return super().show_noise_detector()
    
    @Slot()
    @FastCommandModel.as_method_command("random_select", "随机选取")
    def random_select(self):
        return super().random_select()
    
    @Slot()
    @FastCommandModel.as_method_command("homework_score_sum_up", "作业分结算")
    def homework_score_sum_up(self):
        return super().homework_score_sum_up()

    @Slot()
    @FastCommandModel.as_method_command("show_debug_window", "调试窗口")
    def show_debug_window(self):
        return super().show_debug_window()
    
    @Slot()
    @FastCommandModel.as_method_command("refresh_window", "刷新窗口")
    def refresh_window(self):
        return super().refresh_window()
    
    @Slot()
    @FastCommandModel.as_method_command("save_data_as", "另存为")
    def save_data_as(self):
        return super().save_data_as()
    
    @Slot()
    @FastCommandModel.as_method_command("detect_new_version", "检测新版本")
    def detect_new_version(self):
        return super().detect_new_version()
    
    @Slot()
    @FastCommandModel.as_method_command("show_update_log", "更新日志")
    def show_update_log(self):
        return super().show_update_log()
    
    @Slot()
    @FastCommandModel.as_method_command("show_attendance", "考勤记录")
    def show_attendance(self, *, master: QWidget | None = None) -> None:
        return super().show_attendance(master=master)
    
    @Slot()
    @FastCommandModel.as_method_command("new_template", "新建模板")
    def new_template(self):
        return super().new_template()
        
