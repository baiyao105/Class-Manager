import cv2
import time
import numpy as np
from typing import Literal, Optional, Iterable
from threading import Thread
from utils.functions.decorators import mat_to_pixmap
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QEasingCurve


class Background:
    """背景管理类，用于处理和显示应用程序的背景图像或视频"""

    def __init__(
        self,
        type: Literal["image", "video"],
        path: str,
        max_fr: Optional[int] = None,
        loop: bool = True,
    ):
        self.type = type
        self.path = path
        self.loop = loop
        self.max_fr = max_fr
        self._image = None
        self._frame_ready_callbacks = []
        self._reading = False
        if self.type == "image":
            self._image = mat_to_pixmap(cv2.imread(self.path))
        elif self.type == "video":
            _cap = cv2.VideoCapture(self.path)
            self._image = mat_to_pixmap(_cap.read()[1])
            _cap.release()

    def add_frame_ready_callback(self, callback):
        self._frame_ready_callbacks.append(callback)

    def _emit_frame_ready(self, frame):
        for cb in self._frame_ready_callbacks:
            cb(frame)

    @property
    def image(self) -> QImage:
        return self._image

    @property
    def pixmap(self) -> QPixmap:
        return QPixmap.fromImage(self._image)

    @property
    def mat(self) -> cv2.Mat:
        return cv2.cvtColor(
            self._image.convertToFormat(QImage.Format.Format_RGB888).copy(),
            cv2.COLOR_RGB2BGR,
        )

    @property
    def array(self) -> np.ndarray:
        if not hasattr(self, "_array_cache") or self._array_cache is None:
            # 缓存QImage转np.ndarray
            img = self._image
            if isinstance(img, QImage):
                ptr = img.bits()
                ptr.setsize(img.width() * img.height() * 3)
                arr = np.array(ptr, dtype=np.uint8).reshape((img.height(), img.width(), 3))
                self._array_cache = arr.copy()
            else:
                self._array_cache = np.array(img.convertToFormat(QImage.Format.Format_RGB888).copy())
        return self._array_cache

    def _start(self):
        if self.type == "video":
            self._reading = True
            self._cap = cv2.VideoCapture(self.path)
            last_frame_time = time.time()
            video_fps = self._cap.get(cv2.CAP_PROP_FPS)
            interval = 1 / (min(self.max_fr, video_fps) if self.max_fr and video_fps else (video_fps if video_fps else 25))
            while self._reading:
                now = time.time()
                if now - last_frame_time < interval:
                    time.sleep(interval - (now - last_frame_time))
                last_frame_time = time.time()
                ret, frame = self._cap.read()
                if not ret:
                    if not self.loop:
                        self._reading = False
                        break
                    self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self._cap.read()
                h, w, _ = frame.shape
                img = QImage(frame.data, w, h, 3 * w, QImage.Format.Format_BGR888)
                self._image = img
                # 只在帧内容变化时更新缓存
                arr = np.array(img.convertToFormat(QImage.Format.Format_RGB888).copy())
                if not hasattr(self, "_array_cache") or not np.array_equal(self._array_cache, arr):
                    self._array_cache = arr
                    self._emit_frame_ready(img)
            self._cap.release()

    def start(self):
        if self.type == "video":
            Thread(target=self._start, daemon=True).start()

    def stop(self):
        if self.type == "video":
            self._reading = False
            if hasattr(self, "_cap"):
                self._cap.release()


def arr_to_img(arr: np.ndarray) -> QImage:
    return QImage(
        arr.data,
        arr.shape[1],
        arr.shape[0],
        3 * arr.shape[1],
        QImage.Format.Format_RGB888,
    )


def img_to_arr(img: QImage) -> np.ndarray:
    return np.array(img.convertToFormat(QImage.Format.Format_RGB888).copy())


class BackgroundDisplayItem:
    def __init__(
        self, background: Background, duration: float = -1, fade_in: float = 2
    ):
        self.background = background
        self.duration = duration
        self.fade_in = fade_in


class BackgroundScheme:
    """背景方案类，用于管理多个背景的切换和过渡效果"""

    fade_curve = QEasingCurve.Type.OutCubic

    def __init__(self, name: str, backgrounds: Iterable[BackgroundDisplayItem]):
        self.name = name
        self.backgrounds = backgrounds
        self._array = None
        self._running = False
        self._current_bg = None
        self._frame_ready_callbacks = []

    def add_frame_ready_callback(self, callback):
        self._frame_ready_callbacks.append(callback)

    def _emit_frame_ready(self, frame):
        for cb in self._frame_ready_callbacks:
            cb(frame)

    @property
    def array(self) -> np.ndarray:
        if self._array is None and self.backgrounds:
            self._array = np.array(self.backgrounds[0].background.array)
        return self._array

    @property
    def pixmap(self) -> QPixmap:
        return QPixmap.fromImage(arr_to_img(self.array))

    @property
    def image(self) -> QImage:
        return arr_to_img(self.array)

    def _run(self):
        self._running = True
        last_frame = None
        target_fps = 30  # 目标帧率
        frame_interval = 1.0 / target_fps
        while self._running:
            for bg in self.backgrounds:
                first_frame_time = time.time()
                last_frame = (bg.background.array * 0 if last_frame is None else last_frame)
                bg.background.add_frame_ready_callback(self._emit_frame_ready)
                bg.background.start()
                prev_array = None
                prev_emit_time = 0
                bg_array_cache = bg.background.array.copy()
                # fade_in阶段
                while time.time() - first_frame_time < bg.fade_in:
                    frame_start_time = time.time()
                    progress = (frame_start_time - first_frame_time) / bg.fade_in
                    self._array = (last_frame * (1 - progress)) + (bg_array_cache * progress)
                    arr_uint8 = self._array.astype(np.uint8)
                    now = time.time()
                    if prev_array is None or not np.array_equal(arr_uint8, prev_array):
                        if now - prev_emit_time >= frame_interval:
                            self._emit_frame_ready(arr_to_img(arr_uint8))
                            prev_array = arr_uint8.copy()
                            prev_emit_time = now
                    frame_end_time = time.time()
                    sleep_time = frame_interval - (frame_end_time - frame_start_time)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                show_time = time.time()
                prev_array = None
                prev_emit_time = 0
                bg_array_cache = bg.background.array.copy()
                # duration阶段
                while time.time() - show_time < bg.duration:
                    frame_start_time = time.time()
                    self._array = bg_array_cache
                    arr_uint8 = self._array.astype(np.uint8)
                    now = time.time()
                    if prev_array is None or not np.array_equal(arr_uint8, prev_array):
                        if now - prev_emit_time >= frame_interval:
                            self._emit_frame_ready(arr_to_img(arr_uint8))
                            prev_array = arr_uint8.copy()
                            prev_emit_time = now
                    frame_end_time = time.time()
                    sleep_time = frame_interval - (frame_end_time - frame_start_time)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                bg.background.stop()
                last_frame = bg_array_cache

    def start(self):
        Thread(target=self._run, daemon=True).start()

    def stop(self):
        self._running = False


bs = BackgroundScheme(
    "default",
    [
        BackgroundDisplayItem(Background("background.jpg"), duration=10, fade_in=2),
        BackgroundDisplayItem(Background("background2.jpg"), duration=10, fade_in=2),
    ],
)
