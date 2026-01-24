from typing import Optional, List

import pyqtgraph as pg

from widgets.ui.pyside6.StudentWindow import Ui_Form
from widgets.basic import *
from widgets.custom.ListView import ListView
from widgets.custom.SelectTemplateWidget import SelectTemplateWidget
from widgets.custom.HistoryWidget import HistoryWidget
from widgets.custom.AchievementWidget import AchievementWidget
from utils import Student, ClassObj, ScoreModification

__all__ = ["StudentWidget"]

class StudentWidget(Ui_Form, MyWidget):
    """学生信息窗口实例化"""

    def __init__(
        self,
        main_window: ClassObj = None,
        master_widget: Optional[WidgetType] = None,
        student: Student = None,
        readonly: bool = False,
    ):
        """
        初始化

        :param main_window: 程序的主窗口，方便传参
        :param master_widget: 这个学生窗口的父窗口
        :param student: 这个学生窗口对应的学生
        """
        super().__init__(master=master_widget)
        self.setupUi(self)
        self.student = student
        self.readonly = readonly
        self.show()
        self.mainLayout = QVBoxLayout()
        self.setWindowTitle("学生信息 - " + str(student.name))
        self.setLayout(self.mainLayout)
        self.main_window = main_window
        self.master_widget = master_widget
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(100)
        self.pushButton_3.clicked.connect(self.select_and_send)
        self.pushButton.clicked.connect(self.load_history)
        self.pushButton_2.clicked.connect(self.load_achievement)
        self.history_data: List[Tuple[str, Callable]] = []
        self.achievement_data: List[Tuple[str, Callable]] = []
        self.history_list_window: Optional[ListView] = None
        "历史记录详情窗口"
        self.achievement_list_window: Optional[ListView] = None
        "成就详情窗口"
        self.history_detail_window: Optional[HistoryWidget] = None
        "历史记录详情窗口"
        self.achievement_detail_window: Optional[AchievementWidget] = None
        "成就详情窗口"
        self.template_selector: Optional[SelectTemplateWidget] = None
        "模板选择窗口"
        self.destroyed.connect(self.update_timer.stop)
        if readonly:
            self.pushButton_3.setEnabled(False)

    def show(self, readonly=False):
        self.readonly = readonly
        Base.log(
            "I",
            f"学生信息窗口打开，目标学生：{repr(self.student)}，"
            f"只读模式：{self.readonly}",
            "StudentWidget",
        )
        self.setWindowTitle("学生信息 - " + str(self.student.name))
        super().show()
        self.pushButton_3.setDisabled(readonly)

    def update(self):
        self.label_11.setText(str(self.student.name))
        self.label_6.setText(str(self.student.num))
        self.label_12.setText(str(self.student.score))
        self.label_13.setText(
            str(self.main_window.classes[self.student.belongs_to].name)
        )
        self.label_8.setText(
            str(round(self.student.highest_score, 1))
            + "/"
            + str(round(self.student.lowest_score, 1))
        )
        self.label_7.setText(str(self.student.total_score))
        for i, s in self.main_window.class_obs.rank_non_dumplicate:
            if s.num == self.student.num and s.belongs_to == self.student.belongs_to:
                self.label_16.setText(str(i))
                break

    def send(self, result: Tuple[str, str, str, float]):
        "连接了SelectTemplateWidget.return_result的函数，用来发送点评"
        if not result[0]:
            Base.log("I", "未选择模板", "StudentWidget.send")
            return
        Base.log(
            "I",
            f"发送：{repr((result[0], self.student, result[1], result[2], result[3]))}",
            "StudentWidget.send",
        )
        self.main_window.send_modify(
            result[0], self.student, result[1], result[2], result[3]
        )

    @Slot()
    def load_history(self):
        "加载这个学生的历史记录"
        Base.log(
            "I",
            f"加载历史记录，只读模式：{self.readonly}",
            "StudentWidget.load_history",
        )
        self.history_data = []
        index = 0
        for key in reversed(self.student.history):
            history = self.student.history[key]
            if history.executed:
                try:
                    text = f"{history.title} {history.execute_time.rsplit('.', 1)[0]} {history.mod:+.1f}"
                except (
                    AttributeError,
                    TypeError,
                ) as unused:  # pylint: disable=unused-variable
                    try:
                        text = f"{history.title} {history.create_time.rsplit('.', 1)[0]} {history.mod:+.1f}"
                    except (AttributeError, TypeError) as unused_2:  # NOSONAR
                        text = f"{history.title} <时间信息丢失>   {history.mod:+.1f}"

                def _callable(history=history, index=index, readonly=self.readonly):
                    return self.history_detail(history, index, readonly)

                flash_args = (
                    (
                        QColor(202, 255, 222)
                        if history.mod > 0
                        else (
                            QColor(255, 202, 202)
                            if history.mod < 0
                            else QColor(201, 232, 255)
                        )
                    ),
                    (
                        QColor(232, 255, 232)
                        if history.mod > 0
                        else (
                            QColor(255, 232, 232)
                            if history.mod < 0
                            else QColor(233, 244, 255)
                        )
                    ),
                )

                self.history_data.append((text, _callable, flash_args))

                index += 1
        self.history_list_window = ListView(
            self.main_window,
            self,
            f"历史记录 - {self.student.name}",
            self.history_data,
            {"readonly": self.readonly},
            [("查看分数折线图", self.show_score_graph)],
            allow_pre_action=True,
        )
        self.history_list_window.show()

    class ScoreGraphWindow(QMainWindow):

        def __init__(self, parent: MyWidget, student: Student):
            super().__init__(parent)
            self.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.graphWidget = pg.PlotWidget()
            self.setCentralWidget(self.graphWidget)
            self.master = parent
            self.history_data = student.history
            self.student = student
            self.setWindowTitle(f"分数折线图 - {self.student.name}")
            self.resize(600, 400)
            self.graphWidget.setBackground("w")
            self.graphWidget.setTitle(f"分数折线图 - {self.student.name}")
            self.graphWidget.setLabel("left", "分数")
            self.graphWidget.setLabel("bottom", "次数")
            self.graphWidget.showGrid(x=True, y=True)
            self.graphWidget.addLegend()
            self._x = [0]
            self._y = [0]
            score = Student.score_dtype(0)
            for index, history in enumerate(self.history_data.values(), start=1):
                if history.executed:
                    score += history.mod
                    self._x.append(index)
                    self._y.append(float(score))
            self.graphWidget.plot(self._x, self._y, pen=(255, 0, 0), name="分数")

        def show(self):
            self.move(self.master.geometry().center() - self.geometry().center())
            super().show()

    def show_score_graph(self):
        Base.log("I", "显示分数折线图", "StudentWidget.show_score_graph")
        if not len([m for m in self.student.history.values() if m.executed]):
            Base.log("I", "没有历史记录", "StudentWidget.show_score_graph")
            self.main_window.information("?", "可是都没有记录你点进来干嘛")
            return
        window = StudentWidget.ScoreGraphWindow(self.history_list_window, self.student)
        window.show()

    @Slot()
    def load_achievement(self):
        "加载这个学生的成就"
        index = 0
        Base.log("I", "加载成就", "StudentWidget.load_achievement")
        for key in reversed(self.student.achievements):
            achievement = self.student.achievements[key]
            self.achievement_data.append(
                (
                    achievement.temp.name,
                    lambda achievement=achievement, index=index: self.achievement_detail(
                        achievement, index
                    ),
                )
            )
            index += 1
        self.achievement_list_window = ListView(
            self.main_window, self, f"成就 - {self.student.name}", self.achievement_data
        )
        self.achievement_list_window.show()

    def history_detail(self, history: ScoreModification, index: int, readonly=False):
        """查看历史纪录的详细信息

        :param history: 记录
        :param index: 在listView中的索引"""
        Base.log(
            "I",
            f"选中历史记录： {history}，只读模式：{readonly}",
            "StudentWidget.history_detail",
        )
        self.history_detail_window = HistoryWidget(
            self.main_window,
            self.history_list_window,
            history,
            self.history_list_window,
            index,
            readonly,
        )
        self.history_detail_window.show(readonly)

    def achievement_detail(self, achievement: ScoreModification, index: int):
        """查看成就的详细信息

        :param achievement: 记录
        :param index: 在listView中的索引"""
        Base.log("I", f"选中成就： {achievement}", "StudentWidget.achievement_detail")
        self.achievement_detail_window = AchievementWidget(
            self.achievement_list_window, self.main_window, achievement
        )
        self.achievement_detail_window.show()

    @Slot()
    def select_and_send(self):
        "选择模板并发送点评"
        self.template_selector = SelectTemplateWidget(self.main_window, self)
        self.template_selector.show()
        self.template_selector.return_result.connect(self.send)
        self.template_selector.select()

    def set_student(self, student: Student):
        """设置学生信息

        :param student: 学生对象"""
        if self.isEnabled():
            self.student = student
        else:
            Base.log(
                "I", "学生信息窗口未启用，无法设置学生", "StudentWidget.set_student"
            )

    def close(self):
        """关闭"""
        self.is_running = False
        super().close()