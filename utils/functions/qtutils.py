import cv2
from PySide6.QtGui import QPixmap, QImage


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
