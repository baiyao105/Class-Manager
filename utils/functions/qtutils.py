import cv2
import time
from typing import Callable, Optional, Literal
from widgets.basic.Qt import *  # pylint: disable=wildcard-import, unused-wildcard-import



def mat_to_pixmap(mat: cv2.Mat) -> QPixmap:
    """
    将OpenCV图像矩阵转换为Qt像素图

    :param mat: OpenCV图像矩阵
    :return: 转换后的QPixmap对象
    """
    height, width, channels = mat.shape
    bytes_per_line = channels * width
    qimage = QImage(
        mat.data, width, height, bytes_per_line, QImage.Format.Format_BGR888
    )
    pixmap = QPixmap.fromImage(qimage)
    return pixmap

def wait_until(
        condition: Callable[[], bool], 
        check_interval: int = 33,
        timeout: Optional[int] = None,
        timeout_handling: Literal["ignore", "raise"] = "raise"
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
    if timeout_handling == "raise" and not result:
        raise TimeoutError(f"等待超时 ({(time.time() - start_time) * 1000: d} /{timeout} ms)")
    return result

