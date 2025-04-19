# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AttendanceInfoEdit.ui'
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
    QRadioButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(975, 472)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 0, 71, 16))
        font = QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 20, 291, 16))
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 40, 171, 191))
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 20, 101, 16))
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(20, 40, 101, 16))
        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(20, 70, 121, 16))
        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(20, 90, 121, 16))
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(20, 130, 121, 16))
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(20, 150, 121, 16))
        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(20, 170, 121, 16))
        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(20, 110, 121, 16))
        self.groupBox_2 = QGroupBox(Form)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 240, 171, 181))
        font1 = QFont()
        font1.setPointSize(7)
        self.groupBox_2.setFont(font1)
        self.radioButton = QRadioButton(self.groupBox_2)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setGeometry(QRect(10, 20, 95, 20))
        font2 = QFont()
        font2.setPointSize(9)
        self.radioButton.setFont(font2)
        self.radioButton_2 = QRadioButton(self.groupBox_2)
        self.radioButton_2.setObjectName(u"radioButton_2")
        self.radioButton_2.setGeometry(QRect(10, 40, 95, 20))
        self.radioButton_2.setFont(font2)
        self.radioButton_3 = QRadioButton(self.groupBox_2)
        self.radioButton_3.setObjectName(u"radioButton_3")
        self.radioButton_3.setGeometry(QRect(10, 60, 95, 20))
        self.radioButton_3.setFont(font2)
        self.radioButton_4 = QRadioButton(self.groupBox_2)
        self.radioButton_4.setObjectName(u"radioButton_4")
        self.radioButton_4.setGeometry(QRect(10, 80, 95, 20))
        self.radioButton_4.setFont(font2)
        self.radioButton_5 = QRadioButton(self.groupBox_2)
        self.radioButton_5.setObjectName(u"radioButton_5")
        self.radioButton_5.setGeometry(QRect(10, 100, 95, 20))
        self.radioButton_5.setFont(font2)
        self.radioButton_6 = QRadioButton(self.groupBox_2)
        self.radioButton_6.setObjectName(u"radioButton_6")
        self.radioButton_6.setGeometry(QRect(10, 120, 95, 20))
        self.radioButton_6.setFont(font2)
        self.radioButton_7 = QRadioButton(self.groupBox_2)
        self.radioButton_7.setObjectName(u"radioButton_7")
        self.radioButton_7.setGeometry(QRect(10, 140, 95, 20))
        self.radioButton_7.setFont(font2)
        self.radioButton_8 = QRadioButton(self.groupBox_2)
        self.radioButton_8.setObjectName(u"radioButton_8")
        self.radioButton_8.setGeometry(QRect(10, 160, 95, 20))
        self.radioButton_8.setFont(font2)
        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(200, 40, 771, 391))
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(30, 430, 91, 24))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u8003\u52e4", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u8003\u52e4\u4fe1\u606f", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"1145/1/4 \u661f\u671f\u516b", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"\u4fe1\u606f", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u5e94\u5230\uff1a114", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\u5b9e\u5230\uff1a114", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"\u65e9\u5230\uff1a514", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"\u8fdf\u5230\uff1a1919", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\u4e34\u65f6\u8bf7\u5047\uff1a810", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u65e9\u9000\uff1a810", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"\u665a\u9000\uff1a810", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"\u8bf7\u5047\uff1a810", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"\u66f4\u6539\u4e3a\u6307\u5b9a\u72b6\u6001\uff08\u9009\u5b9a\u540e\u70b9\u51fb\u5b66\u751f\uff09", None))
        self.radioButton.setText(QCoreApplication.translate("Form", u"\u5e38\u89c4\u5230\u6821", None))
        self.radioButton_2.setText(QCoreApplication.translate("Form", u"7:20\u524d\u5230\u6821", None))
        self.radioButton_3.setText(QCoreApplication.translate("Form", u"7:25-7:30\u5230\u6821", None))
        self.radioButton_4.setText(QCoreApplication.translate("Form", u"7:30\u540e\u5230\u6821", None))
        self.radioButton_5.setText(QCoreApplication.translate("Form", u"\u8bf7\u5047", None))
        self.radioButton_6.setText(QCoreApplication.translate("Form", u"\u4e34\u65f6\u8bf7\u5047", None))
        self.radioButton_7.setText(QCoreApplication.translate("Form", u"\u65e9\u9000", None))
        self.radioButton_8.setText(QCoreApplication.translate("Form", u"\u665a\u9000", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"\u67e5\u770b\u672c\u5468\u5386\u53f2", None))
    # retranslateUi

