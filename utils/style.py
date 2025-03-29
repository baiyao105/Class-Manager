import cv2
import time
import numpy as np
from typing            import List, Tuple, Dict, Literal, Optional, Iterable
from threading         import Thread
from utils.functions   import mat_to_pixmap
from PySide6.QtGui     import QPixmap, QImage
from PySide6.QtCore    import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsPixmapItem, QGraphicsItemGroup

class Background:
    """背景管理类，用于处理和显示应用程序的背景图像或视频"""

    def __init__(self, type: Literal["image", "video"], path: str, max_fr: Optional[int] = None, loop: bool = True):
        self.type   = type
        self.path   = path
        self.loop   = loop
        self.max_fr = max_fr
        if self.type == "image":
            self._image = mat_to_pixmap(cv2.imread(self.path))
        elif self.type == "video":
            _cap   = cv2.VideoCapture(self.path)
            self._image = mat_to_pixmap(_cap.read()[1])
            _cap.release()
    
    @property
    def image(self) -> QImage:
        return self._image
    
    @property
    def pixmap(self) -> QPixmap:
        return QPixmap.fromImage(self._image)
    
    @property
    def mat(self) -> cv2.Mat:
        return cv2.cvtColor(self._image.convertToFormat(QImage.Format.Format_RGB888).copy(), cv2.COLOR_RGB2BGR)
    
    @property
    def array(self) -> np.ndarray:
        return np.array(self._image.convertToFormat(QImage.Format.Format_RGB888).copy())
    
        
    def _start(self):
        if self.type == "video":
            self._reading = True
            self._cap = cv2.VideoCapture(self.path)
            last_frame_time = time.time()
            video_fps = self._cap.get(cv2.CAP_PROP_FPS)
            while self._reading:    
                if time.time() - self._video_framerate_update_time >= 1:
                    self.video_framerate = self._video_framecount
                    self._video_framecount = 0
                    self._video_framerate_update_time = time.time()
                if time.time() - last_frame_time <  (1 / min(self.max_fr, video_fps)):
                    time.sleep(max(1 / min(self.max_fr, video_fps) - (time.time() - last_frame_time), 0))
                last_frame_time = time.time()
                ret, frame = self._cap.read()
                if not ret:
                    if not self.loop:
                        self._reading = False
                        return
                    self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self._cap.read()
                h, w, _ = frame.shape
                self._image = QImage(frame.data, w, h, 3 * w, QImage.Format.Format_BGR888)
                self._video_framecount += 1
            self._cap.release()

    def start(self):
        Thread(target=self._start).start()

    def stop(self):
        if self.type == "video":
            self._reading = False
            self._cap.release()



def arr_to_img(arr: np.ndarray) -> QImage:
    return QImage(arr.data, arr.shape[1], arr.shape[0], 3 * arr.shape[1], QImage.Format.Format_RGB888)

def img_to_arr(img: QImage) -> np.ndarray:
    return np.array(img.convertToFormat(QImage.Format.Format_RGB888).copy())


class BackgroundDisplayItem:
    def __init__(self, background: Background, duration: float = -1, fade_in: float = 2):
        self.background = background
        self.duration   = duration
        self.fade_in    = fade_in


class BackgroundScheme:
    """背景方案类，用于管理多个背景的切换和过渡效果"""

    fade_curve = QEasingCurve.Type.OutCubic

    def __init__(self, name: str, backgrounds: Iterable[BackgroundDisplayItem]):
        self.name        = name
        self.backgrounds = backgrounds
        self._array      = None

    @property
    def array(self) -> np.ndarray:
        if self._array is None:
            self._array = np.array(self.backgrounds[0].background.array)
        return self._array
    
    @property
    def pixmap(self) -> QPixmap:
        return QPixmap.fromImage(arr_to_img(self.array))
    
    @property
    def image(self) -> QImage:
        return arr_to_img(self.array)
    


    def start(self):
        self._running = True
        last_frame = None
        while self._running:
            for bg in self.backgrounds:
                first_frame_time = time.time()
                last_frame = bg.background.array * 0 if last_frame is None else last_frame
                bg.background.start()
                while time.time() - first_frame_time < bg.fade_in:
                    progress = (time.time() - first_frame_time) / bg.fade_in
                    self._array = (last_frame * (1 - progress)) + (bg.background.array * progress)
                    time.sleep(0.01)
                show_time = time.time()
                while time.time() - show_time < bg.duration:
                    self._array = bg.background.array
                    time.sleep(0.01)
                bg.background.stop()
                last_frame = bg.background.array  




bs = BackgroundScheme(
    "default",
    [
        BackgroundDisplayItem(Background("background.jpg"), duration=10, fade_in=2),
        BackgroundDisplayItem(Background("background2.jpg"), duration=10, fade_in=2),
    ]
)