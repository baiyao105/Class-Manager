# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LoadingScreen.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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
from PySide6.QtWidgets import (QApplication, QLabel, QProgressBar, QSizePolicy,
    QWidget)

from qfluentwidgets import (IndeterminateProgressRing, ProgressBar, ProgressRing)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(369, 283)
        self.ProgressRing = ProgressRing(Form)
        self.ProgressRing.setObjectName(u"ProgressRing")
        self.ProgressRing.setGeometry(QRect(140, 90, 100, 100))
        self.ProgressRing.setMinimumSize(QSize(80, 80))
        self.ProgressRing.setValue(20)
        self.IndeterminateProgressRing = IndeterminateProgressRing(Form)
        self.IndeterminateProgressRing.setObjectName(u"IndeterminateProgressRing")
        self.IndeterminateProgressRing.setGeometry(QRect(150, 100, 80, 80))
        self.IndeterminateProgressRing.setTextVisible(True)
        self.IndeterminateProgressRing.setTextDirection(QProgressBar.TopToBottom)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(80, 210, 54, 16))
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(163, 133, 54, 16))
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(150, 40, 181, 51))
        font = QFont()
        font.setPointSize(15)
        self.label_3.setFont(font)
        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(80, 230, 54, 16))
        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(80, 250, 54, 16))
        self.label_6 = QLabel(Form)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(140, 210, 191, 16))
        self.label_6.setAlignment(Qt.AlignCenter)
        self.label_7 = QLabel(Form)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(140, 230, 191, 16))
        self.label_7.setAlignment(Qt.AlignCenter)
        self.label_8 = QLabel(Form)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(140, 250, 191, 16))
        self.label_8.setAlignment(Qt.AlignCenter)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u6b65\u9aa4\u4fe1\u606f", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"114%", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u52a0\u8f7d\u4e2d...", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u9636\u6bb5\u8fdb\u5ea6", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\u9884\u8ba1\u65f6\u95f4", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\u6211\u4e0d\u5230\u554a", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"114%/514%", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"\u4e0b\u8f88\u5b50", None))
    # retranslateUi

