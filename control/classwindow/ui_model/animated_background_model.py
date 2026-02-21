"""
和动态背景相关的模型。
"""

from __future__ import annotations

import os
import cv2
import time
import shutil


from utils.algorithm import Thread
from utils.basetypes import Base
from utils.functions.qtutils import wait_until
from utils.qtconfig import QPaintEvent, QImage, QPixmap, QPainter

from .class_ui_model import MixinSuperType

class AnimatedBackgroundModel(MixinSuperType):
    """
    动态背景模型。
    """

    def __init__(self, 
        current_user: str, 
        class_name: str, 
        class_key: str, 
        save_path: str | None = None
    ):
        Base.log("D", "初始化AnimatedBackgroundModel", "AnimatedBackgroundModel.__init__")

        self.current_video_frame: QPixmap | None = None
        "当前的动态背景视频帧"
        self.capture: cv2.VideoCapture | None = None
        "视频捕获对象"
        self.lastest_pixmap_update_time: float = 0.0
        "上次更新背景图片的时间"
        self.img_path = os.path.join("img")
        "图片路径"
        self.default_bg_img_path = os.path.join(self.img_path, "main", "default", "background.jpg")
        "默认背景图片路径"
        self.bg_img_path = os.path.join(self.img_path, "main", "background.jpg")
        "背景图片路径"
        self.background_pixmap: QPixmap | QImage | None = None
        "背景图片"
        self.framerate_update_time: float = 0.0
        "帧率更新时间"
        self.framerate: float = 0.0
        "帧率"
        self.framecount: int = 0
        "帧计数"
        self.read_video_thread = Thread(
            target=self.read_video_while_alive, 
            daemon=True, 
            name="VideoReaderThread"
        )
        "读取视频内容的线程"
        self.read_video_thread.start()
        self.bg_video_path = "background.mp4"
        "背景视频路径"
        self.default_bg_video_path = os.path.join("audio", "video", "default", "background.mp4")
        "默认背景视频路径"

    def read_video_while_alive(self):
        """
        读取并处理背景视频文件，用于实现动态背景效果。
        """

        if not os.path.isfile("background.mp4"):
            Base.log(
                "W", "没有找到视频文件，将使用默认动态背景", "ObjectInfoModel.read_video"
            )
            if os.path.isfile(self.default_bg_video_path):
                if os.path.isdir(self.default_bg_video_path):
                    os.rmdir(self.default_bg_video_path)    # 以防有人真的这么干了
                shutil.copy(self.default_bg_video_path, self.bg_video_path)

                self.warning(
                    "提示",
                    "动态背景需要要视频文件（background.mp4），请检查文件是否存在\n"
                    "当前已经复制默认视频文件到根目录，如果需要使用其他动态背景直接替换background.mp4即可",
                )
            else:
                self.warning(
                    "提示",
                    "动态背景需要要视频文件（background.mp4），请检查文件是否存在\n"
                    "如果需要使用动态背景将background.mp4复制到工具的根目录即可",
                )
            self.use_animate_background = False
            while not os.path.isfile(self.bg_video_path) and not self.should_stop:
                time.sleep(5)
    
        while self.is_running and not self.should_stop:
            self.capture = cv2.VideoCapture(self.bg_video_path)
            last_frame_time = time.time()
            video_fps = self.capture.get(cv2.CAP_PROP_FPS)
            Base.log("I", f"视频解析完成，帧率：{video_fps}", "ObjectInfoModel.read_video")
            while self.is_running and self.use_animate_background:

                if time.time() - self.video_framerate_update_time >= 1:
                    self.video_framerate = self.video_framecount
                    self.video_framecount = 0
                    self.video_framerate_update_time = time.time()
                fd = 1 / max(1, min(self.max_framerate, video_fps))
                if time.time() - last_frame_time < fd:
                    time.sleep(max(fd - (time.time() - last_frame_time), 0))
                last_frame_time = time.time()

                ret, frame = self.capture.read()

                if not ret:
                    self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.capture.read()
                h, w, _ = frame.shape
                self.current_video_frame = QPixmap(
                    QImage(
                        frame.data, w, h, 3 * w, QImage.Format.Format_BGR888
                    )
                )

                self.video_framecount += 1

            self.video_framerate = 0
            wait_until(lambda: self.use_animate_background)

        if self.should_stop:
            Base.log("I", "self.should_stop = True，将停止读取视频流", "ObjectInfoModel.read_video")
    
    
    def paintEvent(self, event: QPaintEvent):
        """
        处理窗口绘制事件，渲染背景图像或视频帧
        """
        
        event.accept()

        t = time.time()
        if time.time() - self.framerate_update_time >= 1:
            self.framerate = self.framecount
            self.framecount = 0
            self.framerate_update_time = time.time()
        self.framecount += 1

        padding = 15
        t2 = time.time()
        
        if self.current_video_frame and self.use_animate_background:
            self.background_pixmap = self.current_video_frame
    
        else:
                
            if not self.background_pixmap:
                # 尝试加载默认背景图片
                if os.path.exists(self.img_path):
                    self.background_pixmap = QPixmap(self.img_path)
                else:
                    # 如果默认图片不存在，复制默认背景
                    if os.path.exists(self.default_bg_img_path):
                        os.makedirs(os.path.dirname(self.img_path), exist_ok=True)
                        shutil.copy(self.default_bg_img_path, self.img_path)
                        self.background_pixmap = QPixmap(self.img_path)

            # 距离上一次更新差了一秒以上就更新
            if time.time() - self.lastest_pixmap_update_time >= 1:
                self.lastest_pixmap_update_time = time.time()
                if os.path.exists(self.img_path):
                    self.background_pixmap = QPixmap(self.img_path)
                if not os.path.exists(self.img_path):
                    # 为了防止更新的时候给原有的background.jpg覆盖了
                    if os.path.exists(self.default_bg_img_path):
                        os.makedirs(os.path.dirname(self.img_path), exist_ok=True)
                        shutil.copy(
                            self.default_bg_img_path, 
                            self.img_path
                        )

        t3 = time.time()

        # 确保有有效的背景图片
        if not self.background_pixmap:
            # 如果还是没有背景图片，尝试加载默认图片
            if os.path.exists(self.default_bg_img_path):
                self.background_pixmap = QPixmap(self.default_bg_img_path)
            else:
                # 如果连默认图片都没有，直接返回
                return

        # 直接使用QPainter构造函数
        painter = QPainter(self)
        
        t4 = time.time()

        painter.drawPixmap(-padding, -padding, self.width(), self.height(), self.background_pixmap)
        painter.end()
        
        t5 = time.time()

        t6 = time.time()

        v = self.window_info.video.last_paint_event
        v.data_reading = t2 - t
        v.background_dealing = t3 - t2
        v.painter_constructing = t4 - t3
        v.pixmap_drawing = t5 - t4
        v.event_accepting = t6 - t5
        v.total_time = t6 - t