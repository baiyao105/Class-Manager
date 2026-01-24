import random
import time
from typing import Union, Tuple, Optional, Callable
from qfluentwidgets import InfoBarIcon, InfoBarPosition, InfoBar

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from utils.classobjects import Student, Group
from utils.functions.sounds import play_sound


class ObjectButton(QPushButton):
    """学生按钮类，用于在界面上显示学生信息的交互按钮"""

    def _set_color(self, col: QColor):
        """
        设置按钮的背景颜色

        :param col: 要设置的颜色对象
        """

        self.setStyleSheet(
            """\
    QPushButton {
        font: 8pt;
        background-color: rgba(%d, %d, %d, %d);
        border-radius: 4px;
        border: 1px solid rgb(0, 0, 0);
    }
"""
            % (col.red(), col.green(), col.blue(), self.opacity)
        )

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, opacity: int):
        self._opacity = opacity
        self._set_color(self.background_color)

    color = Property(QColor, fset=_set_color)

    def __init__(
        self,
        text: str,
        parent=None,
        icon: Union[QIcon, QPixmap] = None,
        object: Union[Student, Group] = None,
    ):
        """
        初始化学生按钮

        :param text: 按钮显示的文字
        :param parent: 父窗口对象
        :param icon: 按钮图标
        :param object: 按钮关联的学生或小组对象
        """
        if icon is not None:
            super().__init__(icon=icon, text=text, parent=parent)
        else:
            super().__init__(text=text, parent=parent)
        self.object = object
        self.anim_border: QPropertyAnimation = None
        self.background_color = QColor(255, 255, 255)
        self._opacity = 162
        self.setStyleSheet(
            QCoreApplication.translate(
                "Form",
                """\
    QPushButton {
        font: 8pt;
        background-color: rgba(255, 255, 255, %d);
        border-radius: 4px;
        border: 1px solid rgb(0, 0, 0);
    }
"""
                % self._opacity,
            )
        )

    def setOpacity(self, opacity: float):
        op = QGraphicsOpacityEffect()
        op.setOpacity(opacity)
        self.setGraphicsEffect(op)
        self.setAutoFillBackground(True)

    def flash(self, start: Tuple[int, int, int], end: Tuple[int, int, int], duration):
        """
        创建按钮颜色闪烁动画效果

        :param start: 起始颜色RGB元组
        :param end: 结束颜色RGB元组
        :param duration: 动画持续时间(毫秒)
        """
        self.anim = QPropertyAnimation(self, b"color")
        self.anim.setDuration(duration)
        self.anim.setStartValue(QColor(*start))
        self.anim.setEndValue(QColor(*end))
        self.anim.start()

    def get_flash_anim(self, start: Tuple[int, int, int], end: Tuple[int, int, int], duration: int,
                       from_self: bool = True):
        """
        创建按钮颜色闪烁动画效果

        :param start: 起始颜色RGB元组
        :param end: 结束颜色RGB元组
        :param duration: 动画持续时间(毫秒)
        """
        if from_self:
            self.anim = QPropertyAnimation(self, b"color")
            self.anim.setDuration(duration)
            self.anim.setStartValue(QColor(*start))
            self.anim.setEndValue(QColor(*end))
            return self.anim
        else:
            anim = QPropertyAnimation(self, b"color")
            anim.setDuration(duration)
            anim.setStartValue(QColor(*start))
            anim.setEndValue(QColor(*end))
            return anim


# 进度条动画控件
class ProgressAnimatedItem(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self._progress = 0.0
        self._color = QColor(0, 255, 0)
        self._text = text
        self.setAutoFillBackground(True)
        self._is_selected = False  # 选中状态标志
        self._hovered = False  # 鼠标悬浮状态标志

    @Property(QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, value: QColor):
        self._color = value

    @Property(float)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.update()  # 进度改变时，通知重绘

    def setSelected(self, selected: bool):
        """
        设置控件的选中状态

        :param selected: 是否选中
        """
        self._is_selected = selected
        self.update()

    def startProgressAnimation(
        self, start1, stop1, start2, stop2, duration, curve, loopCount
    ):
        self._progress = start1
        self._color = start2
        # 创建 QPropertyAnimation 对象并绑定动画
        self._animation = QPropertyAnimation(self, b"progress")
        self._animation.setStartValue(start1)
        self._animation.setEndValue(stop1)
        self._animation.setDuration(duration)
        self._animation.setEasingCurve(curve)
        self._animation.setLoopCount(loopCount)
        if stop2:
            self._animation2 = QPropertyAnimation(self, b"color")
            self._animation2.setStartValue(start2)
            self._animation2.setEndValue(stop2)
            self._animation2.setDuration(duration)
            self._animation2.setEasingCurve(curve)
            self._animation2.setLoopCount(loopCount)
            self._animation2.start()
        self._animation.start()

    def enterEvent(self, event: QMouseEvent):
        """
        处理鼠标进入控件区域的事件

        :param event: 鼠标事件对象
        """
        self._hovered = True
        self.update()

    def leaveEvent(self, event: QMouseEvent):
        """
        处理鼠标离开控件区域的事件

        :param event: 鼠标事件对象
        """
        self._hovered = False
        self.update()

    def paintEvent(self, event: QPaintEvent):
        """
        绘制控件的外观

        :param event: 绘制事件对象
        """
        self._color = QColor(
            self._color.red(),
            self._color.green(),
            self._color.blue(),
            min(192, self._color.alpha()),
        )
        painter = QPainter(self)
        rect = self.rect()

        if self._hovered:
            painter.setBrush(QColor(235, 235, 255))
        elif self._is_selected:
            painter.setBrush(QColor(220, 220, 255))
        else:
            painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)

        progress_width = rect.width() * self._progress
        fill_rect = QRectF(rect.left(), rect.top(), progress_width, rect.height())
        painter.setBrush(self._color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(fill_rect)

        painter.setPen(QPen(Qt.GlobalColor.black))
        text_rect = rect
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft, self._text)


class ProgressAnimatedListWidgetItem(QListWidgetItem):
    def __init__(self, text):
        super().__init__(text)
        self.animated_item = ProgressAnimatedItem(text)

    def startProgressAnimation(
        self,
        startprogress: float,
        stopprogress: float,
        startcolor: QColor = QColor(100, 255, 100, 127),
        endcolor: Optional[QColor] = None,
        duration: int = 1500,
        curve: QEasingCurve = QEasingCurve.Type.OutCubic,
        loopCount: int = 1,
    ):
        """
        启动进度条动画效果

        :param startprogress: 起始进度值(0.0-1.0)
        :param stopprogress: 结束进度值(0.0-1.0)
        :param startcolor: 起始颜色
        :param endcolor: 结束颜色，None表示不变色
        :param duration: 动画持续时间(毫秒)
        :param curve: 动画缓动曲线
        :param loopCount: 动画循环次数
        """
        self.animated_item.startProgressAnimation(
            startprogress,
            stopprogress,
            startcolor,
            endcolor,
            duration,
            curve,
            loopCount,
        )

    def getWidget(self):
        return self.animated_item

    def setSelected(self, selected: bool):
        super().setSelected(selected)
        self.animated_item.setSelected(selected)


class ProgressAnimationTest(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 400, 300)

        widget = QWidget()
        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        items = ["项目 " + str(i) for i in range(1, 500 + 1)]
        self.selected_item = None  # 用来记录当前选中的 item
        for text in items:
            if random.choice([True, False]):
                item = ProgressAnimatedListWidgetItem(text)
                self.list_widget.addItem(item)
                item.startProgressAnimation(
                    startprogress=random.randint(0, 1000) / 1000,
                    stopprogress=random.randint(0, 1000) / 1000,
                    startcolor=QColor(
                        random.randint(160, 255),
                        random.randint(160, 255),
                        random.randint(160, 255),
                        127,
                    ),
                    duration=random.randint(1000, 5000),
                    curve=QEasingCurve.Type.OutExpo,
                    loopCount=1,
                )

        # 双击事件
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def on_item_double_clicked(self, item: QListWidgetItem):
        text = item.text()
        QMessageBox.information(
            self, "选中项目", f"选中{text}，索引：{self.list_widget.row(item)}"
        )


from qfluentwidgets import InfoBar, InfoBarPosition


class SideNotice:
    """侧边栏通知类，用于在界面边缘显示临时通知信息"""

    total = 0
    current = 0
    waiting: int = 0
    showing: int = 0

    def __init__(
        self,
        title: str = "提示",
        content: str = "这是一个提示",
        master: Optional[Union[QMainWindow, QWidget]] = None,
        icon: Optional[Union[InfoBarIcon, QIcon, str]] = None,
        sound: Optional[str] = None,
        duration: int = 5000,
        closeable: bool = True,
        click_command: Optional[Callable] = None,
        further_info: str = "该提示没有详细信息。",
    ):
        """
        初始化侧边栏通知

        :param text: 通知显示的文本内容
        :param master: 父窗口对象
        :param icon: 通知图标
        :param sound: 通知出现时播放的声音文件
        :param duration: 通知显示持续时间(毫秒)
        :param closeable: 是否允许用户关闭通知
        :param click_command: 点击通知时的回调函数
        """

        self.index = SideNotice.total
        self.slot = -1
        SideNotice.total += 1
        self.sound = sound
        self.click_command = click_command
        self.icon = icon
        self.title = title
        self.content = content
        self.duration = duration
        self.closeable = closeable
        self.master = master
        self.finished = False
        self.destroy_command = lambda: None
        self.further_info = further_info
        self.waiting += 1
        self.create_time = time.time()

    def show(self):
        self.waiting -= 1
        self.showing += 1

        def _decrease():
            self.showing -= 1

        QTimer.singleShot(self.duration + 200, _decrease)
        infobar = InfoBar.new(
            self.icon or InfoBarIcon.INFORMATION,
            self.title,
            self.content,
            Qt.Horizontal,
            self.closeable,
            self.duration,
            InfoBarPosition.BOTTOM_RIGHT,
            self.master,
        )
        # self.infobar.contentLabel.setWordWrap(True)
        # self.infobar.contentLabel.setStyleSheet("color: black; font-size: 12px; padding: 0px 0px 0px 0px;")
        # self.infobar.titleLabel.setStyleSheet("color: black; font-size: 14px; padding: 0px 0px 0px 0px;")
        # self.infobar.contentLabel.setFixedWidth(300)

        if self.sound:
            play_sound(self.sound)
        infobar.closeButton.clicked.connect(self.closebutton_clicked)

    def closebutton_clicked(self):
        if self.click_command:
            self.click_command()

    def is_finished(self):
        return self.finished

    def __repr__(self):
        return f"SideNotice(title={self.title!r}, content={self.content!r}, index={self.index}, slot={self.slot})"


if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ProgressAnimationTest()
    window.show()
    sys.exit(app.exec_())