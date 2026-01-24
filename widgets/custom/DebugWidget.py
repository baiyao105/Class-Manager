
"""
调试窗口所在模块
"""


import traceback
from widgets.basic import *
from utils import (
    ClassObj,
    format_exc_like_java, 
    Thread,
    output_list
)
from widgets.ui.pyside6.DebugWindow import Ui_Form

__all__ = ["DebugWidget"]


class DebugWidget(Ui_Form, MyWidget):
    """调试窗口"""

    output_lines = []
    last_line = 0
    command_history = []

    def __init__(
        self, master: Optional[WidgetType] = None, main_window: Optional[ClassObj] = None
    ):
        super().__init__(master)
        self.setupUi(self)
        self.main_window = main_window
        self.master = master
        self.pushButton.clicked.connect(self.send_command)
        self.pushButton_4.clicked.connect(self.send_command_in_thread)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(100)
        self.textbroser_last = DebugWidget.last_line
        # self.textBrowser.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.last_text = ""
        self.history_index = len(self.command_history) - 1
        self.pushButton_2.clicked.connect(self.prev_history)
        self.pushButton_3.clicked.connect(self.next_history)
        self.textEdit.installEventFilter(self)
        self.textEdit.setTabChangesFocus(False)
        self.textEdit.setTabStopDistance(
            self.fontMetrics().size(0, " " * 4).width()
        )  # 把tab设为4个空格
        self.textBrowser.setTabStopDistance(self.fontMetrics().size(0, " " * 4).width())
        self.textEdit.setAcceptRichText(False)
        self.textEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.textEdit.setPlaceholderText("输入命令...")
        self.textEdit.setFocus()
        self.comboBox.currentIndexChanged.connect(self.change_command)
        cmds = [
            ("self.findstu()", "查找学生"),
            ("os._exit(0)", "原地爆炸"),
            ('os.system("shutdown -s -f -t 114514")', "原地爆炸升级版"),
            ("self.reset_scores()", "重置"),
            (
                """\
[ s.num for s in
self.random_choose_stu(
    5,
    includes=[self.findstu(9)],
    excludes=[self.findstu(7)]
)]""",
                "随机抽学生",
            ),
            (
                """\
import math
print(math.sqrt(114514))""",
                "计算114514的平方根",
            ),
            (
                """\
DataObject.saved_objects = 0
c = Chunk("chunks/test_chunk/example", self.database)
t = time.time()
c.save()
print("时间:", time.time() - t)
print("数量:", DataObject.saved_objects)
print("速率:", (DataObject.saved_objects / (time.time() - t)))""",
                "测试保存数据分组",
            ),
            (
                """\
self.achievement_obs.stop()
for i in range(15):
    for _ in range(114):
        self.send_modify("wearing_bad", list(self.target_class.students.values()))
""",
                "大数据测试",
            ),
            (
                """\
c = Chunk("chunks/test_chunk/example", self.database)
t = time.time()
c.load_history()
print("时间:", time.time() - t)
""",
                "测试数据保存",
            ),
            (
                """
for i in range(100):
    self.add_student(
    f"{max(*self.target_class.students) + 1}号学生",
    default_class_key,
    max(*self.target_class.students) + 1
)
""",
                "添加学生",
            ),
        ]
        self.comboBox.clear()
        self.comboBox.addItem("快捷命令")
        for cmd, name in cmds:
            self.comboBox.addItem(name, cmd)
        self.comboBox.setCurrentIndex(0)
        if self.command_history:
            self.textEdit.setText(self.command_history[self.history_index])
        self.destroyed.connect(self.update_timer.stop)
        self.update()

    def show(self):
        super().show()
        self.output_lines = []

    def change_command(self):
        "切换快捷命令"
        index = self.comboBox.currentIndex()
        if (
            index <= 0
        ):  # 一定要 <= 0，因为clear()的时候可能会传过来一个-1让程序爆掉，别问我怎么知道的
            return
        self.textEdit.setText(self.comboBox.itemData(index))
        self.comboBox.setCurrentIndex(0)
        self.textEdit.setFocus()

    def update(self):
        self.label_5.setText(str(self.main_window.sidenotice_waiting_order.qsize()))
        self.label_6.setText(str(SideNotice.showing))
        self.label_7.setText(str(SideNotice.waiting))
        self.label_8.setText(str(SideNotice.current))
        self.label_21.setText(str(round(self.main_window.class_obs.tps, 3)))
        self.label_22.setText(str(round(self.main_window.achievement_obs.tps, 3)))
        self.label_23.setText(str(round(time.time() - self.main_window.create_time, 3)))
        self.label_24.setText(
            str(self.main_window.achievement_obs.display_achievement_queue.qsize())
        )
        self.label_27.setText(str(round(self.main_window.class_obs.mspt, 3)))
        self.label_28.setText(str(round(self.main_window.achievement_obs.mspt, 3)))

        self.textbroser_last = len(output_list)
        self.label_9.setText(
            str(f"{self.history_index + 1}/{len(DebugWidget.command_history)}")
        )
        text = "\n".join(output_list[DebugWidget.last_line :])
        if text != self.last_text:
            self.textBrowser.setText(text)
            self.last_text = text
            self.textBrowser.verticalScrollBar().setValue(
                self.textBrowser.verticalScrollBar().maximum()
            )
        super().update()

    def closeEvent(self, event):
        super().closeEvent(event)
        DebugWidget.last_line = self.textbroser_last
        self.update_timer.stop()

    def prev_history(self):
        "上一条历史命令"
        if len(DebugWidget.command_history) == 0 or self.history_index == 0:
            return
        self.history_index = max(0, self.history_index - 1)
        if not (self.history_index == 0 and not self.textEdit.toPlainText().strip()):
            self.textEdit.setText(DebugWidget.command_history[self.history_index])

    def next_history(self):
        "下一条历史命令"
        if len(DebugWidget.command_history) == 0:
            return
        self.history_index = min(
            len(DebugWidget.command_history) - 1, self.history_index + 1
        )
        if not (
            self.history_index == len(DebugWidget.command_history) - 1
            and not self.textEdit.toPlainText().strip()
        ):
            self.textEdit.setText(DebugWidget.command_history[self.history_index])

    @Slot()
    def send_command(self):
        "发送当前命令"
        if not self.textEdit.toPlainText().strip():
            return
        cmd = self.textEdit.toPlainText()
        if len(cmd.splitlines()) > 1:
            sys.stdout.write(">> " + cmd.splitlines()[0] + "\n")
            for l in cmd.splitlines()[1:]:
                sys.stdout.write(">> " + l + "\n")
        else:
            sys.stdout.write(">> " + cmd + "\n")
        self.pushButton.setEnabled(True)
        self.pushButton_4.setEnabled(True)
        ret = None
        try:
            ret = self.main_window.exec_command(cmd)
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            sys.stderr.write(traceback.format_exc() + "\n")
            sys.stderr.write("-----------------------------------------" + "\n")
            sys.stderr.write("\n".join(format_exc_like_java(sys.exc_info()[1])) + "\n")
        else:
            if ret is not None:
                sys.stdout.write(repr(ret) + "\n")
        self.command_history.append(cmd)
        self.history_index = len(self.command_history) - 1
        self.pushButton.setEnabled(True)
        self.pushButton_4.setEnabled(True)

    @Slot()
    def send_command_in_thread(self):
        "在一个新线程中发送当前命令"
        self.pushButton.setEnabled(False)
        cmd = self.textEdit.toPlainText()
        if not cmd.strip():
            return
        if len(cmd.splitlines()) > 1:
            sys.stdout.write(">> " + cmd.splitlines()[0] + "\n")
            for l in cmd.splitlines()[1:]:
                sys.stdout.write(">> " + l + "\n")
        else:
            sys.stdout.write(">> " + cmd + "\n")
        self.pushButton.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        ret = None
        finished = False

        def _send():
            nonlocal ret, finished
            try:
                ret = self.main_window.exec_command(cmd) # XXX 这里也有逻辑问题
            except BaseException as unused:  # pylint: disable=broad-exception-caught
                sys.stderr.write(traceback.format_exc() + "\n")
                sys.stderr.write("-----------------------------------------" + "\n")
                sys.stderr.write(
                    "\n".join(format_exc_like_java(sys.exc_info()[1])) + "\n"
                )
            else:
                if ret is not None:
                    sys.stdout.write(repr(ret) + "\n")
            finished = True


        loop = QEventLoop(self)
        timer = QTimer(self)
        def _check_if_finished():
            if finished:
                loop.quit()
                timer.stop()
        timer.timeout.connect(_check_if_finished)
        timer.start(50)
        Thread(target=_send).start()
        loop.exec()
        timer.stop()
        self.command_history.append(cmd)
        self.history_index = len(self.command_history) - 1
        self.pushButton.setEnabled(True)
        self.pushButton_4.setEnabled(True)
