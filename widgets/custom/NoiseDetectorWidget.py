"""
噪音信息窗口所在模块
"""

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError as unused:
    HAS_PYAUDIO = False
import numpy as np
from utils import Thread
from typing import Optional
from utils import ClassObj
from widgets.basic import *
from widgets.ui.pyside6.NoiseDetector import Ui_Form


__all__ = ["NoiseDetectorWidget"]
class NoiseDetectorWidget(Ui_Form, MyWidget):
    """噪音检测器"""

    # 定义音频参数

    try:
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNKSIZE = 1024
        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNKSIZE,
        )
    except BaseException as unused:  # pylint: disable=broad-exception-caught
        p = None
        stream = None

    @staticmethod
    def caculate_db(data):
        try:
            samples = np.frombuffer(data, dtype=np.int16)
            peak_amplitude = np.abs(samples).max()
            if peak_amplitude == 0:
                return -np.inf
            else:
                return 20 * np.log10(peak_amplitude / 32768.0)
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            return -np.inf

    @staticmethod
    def caculate_abs(data):
        samples = np.frombuffer(data, dtype=np.int16)
        peak_amplitude = np.abs(samples).max()
        return peak_amplitude / 32768

    def __init__(
        self, master: Optional[WidgetType] = None, main_window: Optional[ClassObj] = None
    ):
        """
        构造新窗口

        :param master: 父窗口
        :param main_window: 主窗口
        """
        super().__init__(master)
        self.setupUi(self)
        self.main_window = main_window
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_window)
        self.update_timer.start(100)
        self.read_data_thread = Thread(target=self.read_data)
        self.last_length = 0
        self.pushButton.clicked.connect(lambda: play_sound("audio/sounds/boom.mp3"))
        self.pushButton_2.clicked.connect(lambda: play_sound("audio/sounds/gl.mp3"))
        self.pushButton_3.clicked.connect(self.call_my_army)
        self.destroyed.connect(self.update_timer.stop)
        self.read_data_thread.start()

    def read_data(self):
        if not HAS_PYAUDIO:
            return
        while True:
            try:
                self.data = self.stream.read(self.CHUNKSIZE)
            except BaseException as unused:  # pylint: disable=broad-exception-caught
                if self.stream is not None:
                    self.data = b"wdnmd"  # 抽象的音频信号
                else:
                    p = pyaudio.PyAudio()
                    self.stream = p.open(
                        format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNKSIZE,
                    )

    def update_window(self):
        data = self.data
        db = self.caculate_db(data)
        abs_d = self.caculate_abs(data)
        try:
            label_len = 350 * abs_d
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            label_len = 350

        if label_len >= 350:
            self.label.setStyleSheet(
                "background-color: rgb(232, 99, 99); border-radius: 6px; border: 2px solid rgb(0, 0, 0);"
            )
        elif 350 > label_len >= 200:
            self.label.setStyleSheet(
                "background-color: rgb(232, 172, 99); border-radius: 6px; border: 2px solid rgb(0, 0, 0);"
            )
        elif 190 > label_len >= 110:
            self.label.setStyleSheet(
                "background-color: rgb(232, 232, 99); border-radius: 6px; border: 2px solid rgb(0, 0, 0);"
            )
        elif 110 > label_len >= 60:
            self.label.setStyleSheet(
                "background-color: rgb(172, 232, 99); border-radius: 6px; border: 2px solid rgb(0, 0, 0);"
            )
        elif 60 > label_len >= 30:
            self.label.setStyleSheet(
                "background-color: rgb(99, 232, 172); border-radius: 6px; border: 2px solid rgb(0, 0, 0);"
            )
        elif 30 > label_len >= 0:
            self.label.setStyleSheet(
                "background-color: rgb(99, 232, 232); border-radius: 6px; border: 2px solid rgb(0, 0, 0);"
            )

        self.label_3.setText(
            f"当前噪音：{db:.2f}db （{int(abs_d * 65536)}, {int(label_len)}）"
        )
        start = QSize(self.last_length, 21)
        end = QSize(min(label_len + 20, 350), 21)
        self.last_length = end.width()
        self.anim = QPropertyAnimation(self.label, b"size")
        self.anim.setDuration(33)
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.setEasingCurve(QEasingCurve.Type.Linear)
        self.anim.setLoopCount(1)
        self.anim.start()

    def call_my_army(self):
        "呼叫班主任"
        teacher_ip = "172.62.114.51"
        teacher_email = "1145141919@qq.com"
        Base.log(
            "I",
            f"准备呼叫班主任，班主任设备IP：{teacher_ip}, 邮箱：{teacher_email}",
            "NoiseDetectorWidget.call_my_army",
        )