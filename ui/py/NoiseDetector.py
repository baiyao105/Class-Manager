# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'NoiseDetector.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QLabel, QPushButton,
    QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(439, 194)
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 10, 81, 16))
        font = QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(20, 40, 381, 80))
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 20, 371, 16))
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 40, 351, 21))
        self.label.setStyleSheet(u"background-color:rgb(232,232,255);\n"
"border-radius: 6px; \n"
"border: 2px solid rgb(0, 0, 0);")
        self.groupBox_2 = QGroupBox(Form)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(20, 130, 381, 51))
        self.pushButton = QPushButton(self.groupBox_2)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(10, 20, 81, 24))
        self.pushButton_2 = QPushButton(self.groupBox_2)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(100, 20, 81, 24))
        self.pushButton_3 = QPushButton(self.groupBox_2)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(220, 20, 151, 24))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u566a\u97f3\u6d4b\u8bd5", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u566a\u97f3\u6d4b\u8bd5", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"\u4fe1\u606f", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u5f53\u524d\u566a\u97f3\uff1a114.5dbm", None))
        self.label.setText("")
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"\u62bd\u8c61\u529f\u80fd", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"\u53d1\u51fa\u67d0\u79cd\u566a\u58f0", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"\u53e4\u795e\u4f4e\u8bed", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"\u547c\u53eb\u73ed\u4e3b\u4efb\uff08\u540e\u7eed\u505a\uff09", None))
    # retranslateUi

