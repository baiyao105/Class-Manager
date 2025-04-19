# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'RandomSelector.ui'
##
## Created by: Qt User Interface Compiler version 6.6.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSpinBox,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(924, 329)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 71, 16))
        font = QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 50, 111, 16))
        self.listWidget = QListWidget(Form)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setGeometry(QRect(10, 80, 131, 192))
        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(170, 50, 111, 16))
        self.listWidget_2 = QListWidget(Form)
        self.listWidget_2.setObjectName(u"listWidget_2")
        self.listWidget_2.setGeometry(QRect(170, 80, 131, 192))
        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(330, 50, 111, 16))
        self.listWidget_3 = QListWidget(Form)
        self.listWidget_3.setObjectName(u"listWidget_3")
        self.listWidget_3.setGeometry(QRect(330, 80, 131, 192))
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(530, 180, 75, 24))
        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(510, 160, 178, 2))
        self.line.setStyleSheet(u"background: black")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line_2 = QFrame(Form)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setGeometry(QRect(510, 170, 178, 2))
        self.line_2.setStyleSheet(u"background: black")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(480, 130, 91, 16))
        self.spinBox = QSpinBox(Form)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setGeometry(QRect(550, 130, 81, 22))
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(114514)
        self.pushButton_2 = QPushButton(Form)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(40, 280, 75, 24))
        self.pushButton_3 = QPushButton(Form)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(200, 280, 75, 24))
        self.pushButton_4 = QPushButton(Form)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(370, 280, 75, 24))
        self.listWidget_4 = QListWidget(Form)
        self.listWidget_4.setObjectName(u"listWidget_4")
        self.listWidget_4.setGeometry(QRect(700, 20, 211, 301))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u968f\u673a\u62bd\u4eba", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u4ece\u8fd9\u4e9b\u5b66\u751f", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u5fc5\u987b\u5305\u62ec...", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u5fc5\u987b\u6392\u9664...", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"GO !", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\u62bd\u53d6\u4eba\u6570", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"\u9009\u62e9", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"\u9009\u62e9", None))
        self.pushButton_4.setText(QCoreApplication.translate("Form", u"\u9009\u62e9", None))
    # retranslateUi

