# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'NoticeViewer.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QLabel, QSizePolicy,
    QTextBrowser, QWidget)

class Ui_widget(object):
    def setupUi(self, widget):
        if not widget.objectName():
            widget.setObjectName(u"widget")
        widget.resize(466, 323)
        self.label = QLabel(widget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 0, 101, 31))
        font = QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.textBrowser = QTextBrowser(widget)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(20, 140, 411, 151))
        self.textBrowser.setStyleSheet(u"background: transparent; border: 1px")
        self.groupBox = QGroupBox(widget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(280, 40, 141, 91))
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 20, 31, 16))
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(80, 20, 61, 16))
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 40, 51, 16))
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(80, 40, 61, 16))
        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 60, 51, 16))
        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(80, 60, 51, 16))
        self.label_3 = QLabel(widget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 30, 54, 16))
        font1 = QFont()
        font1.setPointSize(10)
        self.label_3.setFont(font1)
        self.textBrowser_2 = QTextBrowser(widget)
        self.textBrowser_2.setObjectName(u"textBrowser_2")
        self.textBrowser_2.setGeometry(QRect(20, 60, 231, 71))
        self.textBrowser_2.setStyleSheet(u"background: transparent; border: 1px")

        self.retranslateUi(widget)

        QMetaObject.connectSlotsByName(widget)
    # setupUi

    def retranslateUi(self, widget):
        widget.setWindowTitle(QCoreApplication.translate("widget", u"\u6d88\u606f\u67e5\u770b", None))
        self.label.setText(QCoreApplication.translate("widget", u"\u63d0\u793a\u67e5\u770b", None))
        self.groupBox.setTitle(QCoreApplication.translate("widget", u"\u4fe1\u606f", None))
        self.label_2.setText(QCoreApplication.translate("widget", u"\u65f6\u95f4", None))
        self.label_4.setText(QCoreApplication.translate("widget", u"11:45:14", None))
        self.label_5.setText(QCoreApplication.translate("widget", u"\u63d0\u793a\u65f6\u957f", None))
        self.label_6.setText(QCoreApplication.translate("widget", u"1145", None))
        self.label_7.setText(QCoreApplication.translate("widget", u"\u5141\u8bb8\u5173\u95ed", None))
        self.label_8.setText(QCoreApplication.translate("widget", u"\u662f", None))
        self.label_3.setText(QCoreApplication.translate("widget", u"\u63d0\u793a\u6807\u9898", None))
    # retranslateUi

