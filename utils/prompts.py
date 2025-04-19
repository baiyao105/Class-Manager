import random
from typing import Optional, Literal

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtGui import QPixmap


def button_ok_text():
    "返回一个随机的按钮文本"
    return random.choice(
        [
            "知道了知道了",
            "哦",
            "确认",
            "收到",
            "好的",
        ]
    )


def button_accept_text():
    "返回一个随机的按钮确定文本"
    return random.choice(
        [
            "确定",
            "好",
            "OK",
            "行吧",
            "好的",
        ]
    )


def button_reject_text():
    "返回一个随机的取消按钮文本"
    return random.choice(
        [
            "取消",
            "算了算了",
            "但是我拒绝",
            "不要",
            "下辈子再说",
        ]
    )


def question_yes_no(
    master: Optional[QWidget],
    title: str,
    text: str,
    default: bool = True,
    msg_type: Literal["question", "information", "warning", "critical"] = "question",
    pixmap: Optional[QPixmap] = None,
) -> bool:
    """
    显示一个询问对话框

    :param master: 父窗口
    :param title: 标题
    :param text: 内容
    :param default: 默认按钮
    :param type: 消息类型
    :param pixmap: 图标
    :return: 是否确定
    """
    if msg_type == "question":
        box = QMessageBox(QMessageBox.Icon.Question, title, text, parent=master)
        box.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-help.png"))
    elif msg_type == "information":
        box = QMessageBox(QMessageBox.Icon.Information, title, text, parent=master)
        box.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-main.png"))
    elif msg_type == "warning":
        box = QMessageBox(QMessageBox.Icon.Warning, title, text, parent=master)
        box.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-warn.png"))
    elif msg_type == "critical":
        box = QMessageBox(QMessageBox.Icon.Critical, title, text, parent=master)
        box.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-error.png"))

    box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    box.setDefaultButton(
        QMessageBox.StandardButton.No if not default else QMessageBox.StandardButton.Yes
    )
    button_y = box.button(QMessageBox.StandardButton.Yes)
    button_y.setText(button_accept_text())
    button_n = box.button(QMessageBox.StandardButton.No)
    button_n.setText(button_reject_text())
    return box.exec() == QMessageBox.StandardButton.Yes


def send_notice(
    title: str, content: str, msg_type: Literal["info", "warn", "error"] = "info"
):
    """
    发送通知

    :param title: 标题
    :param content: 内容
    :param msg_type: 消息类型
    """
