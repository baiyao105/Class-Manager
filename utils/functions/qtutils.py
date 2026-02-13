"""
关于Qt的函数
"""
from __future__ import annotations
import time
from typing import Callable, Literal, TYPE_CHECKING
from ..qtconfig import QPixmap, QImage
from ..qtconfig import QTimer, QEventLoop

if TYPE_CHECKING:
    import cv2  # 导入要卡好一会，所以只在类型检查的时候导入


def mat_to_pixmap(mat: cv2.Mat) -> QPixmap:
    """
    将OpenCV图像矩阵转换为Qt像素图

    :param mat: OpenCV图像矩阵
    :return: 转换后的QPixmap对象
    """
    height, width, channels = mat.shape
    bytes_per_line = channels * width
    qimage = QImage(mat.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
    return QPixmap.fromImage(qimage)


def wait_until(
    condition: Callable[[], bool],
    check_interval: int = 33,
    timeout: int | None = None,
    timeout_handling: Literal["ignore", "raise"] = "raise",
) -> bool:
    """
    等待直到条件为真

    :param condition: 条件函数，返回True表示条件满足
    :param check_interval: 检查间隔时间（ms）
    :param timeout: 超时时间（ms），如果为None则无限等待
    :param timeout_handling: 超时处理方式，"ignore"表示忽略超时，"raise"表示抛出异常
    :return: 条件是否满足
    """
    start_time = time.time()
    timer = QTimer()
    loop = QEventLoop()
    result: bool = False

    def _check_if_done():
        nonlocal result
        if condition():
            loop.quit()
            result = True
        elif timeout is not None and time.time() - start_time > timeout / 1000:
            loop.quit()
            result = False

    timer.timeout.connect(_check_if_done)
    timer.start(check_interval)
    loop.exec()
    timer.stop()
    if timeout_handling == "raise" and not result:
        raise TimeoutError(f"等待超时 ({(time.time() - start_time) * 1000:.0f} / {timeout} ms)")
    return result
