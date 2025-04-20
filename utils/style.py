import cv2
import time
import numpy as np
from typing import Literal, Optional, Iterable
from threading import Thread, Lock
from utils.functions.decorators import mat_to_pixmap
from PySide6.QtGui import QPixmap, QImage, QOpenGLContext, QSurfaceFormat
from PySide6.QtCore import QEasingCurve
from PySide6.QtOpenGL import QOpenGLBuffer, QOpenGLFramebufferObject


class Background:
    """背景管理类，用于处理和显示应用程序的背景图像或视频"""

    def __init__(
        self,
        type: Literal["image", "video"],
        path: str,
        max_fr: Optional[int] = None,
        loop: bool = True,
        max_size: Optional[tuple[int, int]] = None,
    ):
        self.type = type
        self.path = path
        self.loop = loop
        self.max_fr = max_fr
        self._image = None
        self._frame_ready_callbacks = []
        self._reading = False
        self.max_size = max_size
        self._cap = None
        if self.type == "image":
            img = cv2.imread(self.path)
            if self.max_size:
                img = cv2.resize(img, self.max_size, interpolation=cv2.INTER_LINEAR)
            self._image = mat_to_pixmap(img)

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
            if not self._cap:
                self._cap = cv2.VideoCapture(self.path)
                if not self._cap.isOpened():
                    return
                ret, frame = self._cap.read()
                if ret and self.max_size:
                    frame = cv2.resize(frame, self.max_size, interpolation=cv2.INTER_LINEAR)
                if ret:
                    h, w, _ = frame.shape
                    self._image = QImage(frame.data, w, h, 3 * w, QImage.Format.Format_BGR888)
            
            self._reading = True
            last_frame_time = time.time()
            video_fps = self._cap.get(cv2.CAP_PROP_FPS) if self._cap else 25
            use_fps_limit = self.max_fr is not None
            interval = 1 / min(self.max_fr, video_fps) if use_fps_limit else 1 / video_fps
            
            while self._reading:
                now = time.time()
                if use_fps_limit and now - last_frame_time < interval:
                    time.sleep(interval - (now - last_frame_time))
                last_frame_time = time.time()
                
                ret, frame = self._cap.read()
                if not ret:
                    if not self.loop:
                        self._reading = False
                        break
                    self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self._cap.read()
                    if not ret:
                        break
                        
                if self.max_size:
                    frame = cv2.resize(frame, self.max_size, interpolation=cv2.INTER_LINEAR)
                h, w, _ = frame.shape
                img = QImage(frame.data, w, h, 3 * w, QImage.Format.Format_BGR888)
                self._image = img
                
                if not hasattr(self, "_array_cache"):
                    self._array_cache = np.array(img.bits()).reshape(h, w, 3).copy()
                    self._emit_frame_ready(img)
                else:
                    new_arr = np.array(img.bits()).reshape(h, w, 3)
                    if not np.array_equal(self._array_cache, new_arr):
                        self._array_cache = new_arr.copy()
                        self._emit_frame_ready(img)
            
            if self._cap:
                self._cap.release()
                self._cap = None

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
        self._buffer_lock = Lock()
        self._front_buffer = None
        self._back_buffer = None
        
        # 初始化OpenGL上下文和帧缓冲对象
        self._gl_context = QOpenGLContext()
        format = QSurfaceFormat()
        format.setVersion(3, 3)
        format.setProfile(QSurfaceFormat.CoreProfile)
        self._gl_context.setFormat(format)
        self._fbo = None

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
        last_update_time = time.time()
        target_fps = 60  # 目标帧率
        frame_interval = 1.0 / target_fps
        
        # 初始化双缓冲
        if not self._front_buffer or not self._back_buffer:
            for bg in self.backgrounds:
                shape = bg.background.array.shape
                self._front_buffer = np.zeros((shape[0], shape[1], 3), dtype=np.uint8)
                self._back_buffer = np.zeros((shape[0], shape[1], 3), dtype=np.uint8)
                break
        
        while self._running:
            for bg in self.backgrounds:
                if last_frame is None:
                    last_frame = np.zeros_like(self._front_buffer)
                
                bg.background.add_frame_ready_callback(self._emit_frame_ready)
                bg.background.start()
                
                # 预加载背景
                if not hasattr(bg, '_cached_array'):
                    with self._buffer_lock:
                        bg._cached_array = cv2.resize(bg.background.array, None, fx=0.5, fy=0.5,
                                                    interpolation=cv2.INTER_LINEAR)
                bg_array_cache = bg._cached_array
                
                # fade_in阶段优化
                fade_start = time.time()
                while self._running and time.time() - fade_start < bg.fade_in:
                    current_time = time.time()
                    elapsed = current_time - last_update_time
                    
                    if elapsed >= frame_interval:
                        progress = min((current_time - fade_start) / bg.fade_in, 1.0)
                        
                        # OpenGL图像混合
                        with self._buffer_lock:
                            cv2.addWeighted(last_frame, 1 - progress, bg_array_cache, progress, 0, self._back_buffer)
                            self._back_buffer, self._front_buffer = self._front_buffer, self._back_buffer
                            self._array = self._front_buffer
                            self._emit_frame_ready(arr_to_img(self._array))
                        
                        last_update_time = current_time
                    else:
                        time.sleep(max(0, frame_interval - elapsed))
                
                # duration阶段
                if bg.duration > 0:
                    duration_start = time.time()
                    with self._buffer_lock:
                        self._array = bg_array_cache.copy()
                    
                    while self._running and time.time() - duration_start < bg.duration:
                        current_time = time.time()
                        elapsed = current_time - last_update_time
                        
                        if elapsed >= frame_interval:
                            self._emit_frame_ready(arr_to_img(self._array))
                            last_update_time = current_time
                        else:
                            time.sleep(max(0, frame_interval - elapsed))
                
                bg.background.stop()
                last_frame = bg_array_cache.copy()

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
