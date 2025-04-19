# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GroupWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QSizePolicy, QTextBrowser, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(530, 356)
        self.listWidget = QListWidget(Form)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setGeometry(QRect(280, 40, 241, 151))
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 71, 16))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 50, 54, 16))
        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 140, 54, 16))
        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 110, 54, 16))
        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 80, 54, 16))
        self.label_6 = QLabel(Form)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(70, 50, 151, 16))
        self.label_7 = QLabel(Form)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(70, 140, 201, 16))
        self.label_8 = QLabel(Form)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(70, 110, 201, 31))
        self.label_8.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label_9 = QLabel(Form)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(70, 80, 201, 16))
        self.label_10 = QLabel(Form)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(10, 170, 54, 16))
        self.label_11 = QLabel(Form)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(70, 170, 201, 16))
        self.label_12 = QLabel(Form)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(280, 10, 71, 16))
        self.label_12.setFont(font)
        self.label_13 = QLabel(Form)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(10, 200, 54, 16))
        self.textBrowser = QTextBrowser(Form)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(0, 230, 531, 121))
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(290, 200, 75, 21))
        self.pushButton_2 = QPushButton(Form)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(410, 200, 75, 21))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u5c0f\u7ec4\u4fe1\u606f", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u5c0f\u7ec4\u4fe1\u606f", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u540d\u79f0", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u6240\u5c5e\u73ed\u7ea7", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u603b\u5206\u6570", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\u603b\u4eba\u6570", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"1145\u56e2", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"1145\u73ed", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"114", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"1", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"\u5f53\u524d\u7ec4\u957f", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"\u6211\u4e0d\u5230\u554a", None))
        self.label_12.setText(QCoreApplication.translate("Form", u"\u5c0f\u7ec4\u6210\u5458", None))
        self.label_13.setText(QCoreApplication.translate("Form", u"\u4ecb\u7ecd", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u7ec4\u5458", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"\u5168\u56e2\u70b9\u8bc4", None))
    # retranslateUi

