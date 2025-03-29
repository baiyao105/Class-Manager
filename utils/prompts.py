import random
from PySide6.QtWidgets import QWidget, QMessageBox, QPushButton
from PySide6.QtGui import QPixmap
from typing import Optional, Literal

def button_ok_text():
    return random.choice([
        "知道了知道了",
        "哦",
        "确认",
        "收到",
        "好的",
    ])

def button_accept_text():
    return random.choice([
        "确定",
        "好",
        "OK",
        "行吧",
        "好的",

    ])

def button_reject_text():
    return random.choice([
        "取消",
        "算了算了",
        "但是我拒绝",
        "不要",
        "下辈子再说",
    ])

def question_yes_no(master:Optional[QWidget], 
                    title:str, text:str, 
                    default:bool=True, 
                    type:Literal["question", "information", "warning", "critical"]="question", 
                    pixmap: Optional[QPixmap] = None) -> bool:
    if type == "question":
        box = QMessageBox(QMessageBox.Icon.Question, title, text, parent=master)
        box.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-help.png"))
    elif type == "information":
        box = QMessageBox(QMessageBox.Icon.Information, title, text, parent=master)
        box.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-main.png"))
    elif type == "warning":
        box = QMessageBox(QMessageBox.Icon.Warning, title, text, parent=master)
        box.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-warn.png"))
    elif type == "critical":
        box = QMessageBox(QMessageBox.Icon.Critical, title, text, parent=master)
        box.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-error.png"))

    
    box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    box.setDefaultButton(QMessageBox.StandardButton.No if not default else QMessageBox.StandardButton.Yes)
    button_y = box.button(QMessageBox.StandardButton.Yes)
    button_y.setText(button_accept_text())
    button_n = box.button(QMessageBox.StandardButton.No)
    button_n.setText(button_reject_text())
    return box.exec() == QMessageBox.StandardButton.Yes
