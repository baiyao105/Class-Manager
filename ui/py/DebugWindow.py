# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DebugWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QLabel,
    QPushButton, QSizePolicy, QTextBrowser, QTextEdit,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(721, 432)
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 10, 471, 411))
        self.textBrowser = QTextBrowser(self.groupBox)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(10, 20, 421, 192))
        self.pushButton = QPushButton(self.groupBox)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(360, 220, 75, 24))
        self.textEdit = QTextEdit(self.groupBox)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(10, 220, 341, 161))
        self.pushButton_2 = QPushButton(self.groupBox)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(360, 280, 75, 24))
        self.pushButton_3 = QPushButton(self.groupBox)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(360, 310, 75, 24))
        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(350, 390, 81, 16))
        self.label_9.setAlignment(Qt.AlignCenter)
        self.pushButton_4 = QPushButton(self.groupBox)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(360, 250, 75, 24))
        self.comboBox = QComboBox(self.groupBox)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(360, 340, 68, 21))
        self.comboBox.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.groupBox_2 = QGroupBox(Form)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(480, 10, 201, 341))
        self.groupBox_3 = QGroupBox(self.groupBox_2)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(10, 20, 181, 101))
        self.label = QLabel(self.groupBox_3)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 20, 61, 16))
        self.label_2 = QLabel(self.groupBox_3)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 40, 61, 16))
        self.label_3 = QLabel(self.groupBox_3)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 60, 61, 16))
        self.label_4 = QLabel(self.groupBox_3)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 80, 61, 16))
        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(110, 20, 54, 16))
        self.label_6 = QLabel(self.groupBox_3)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(110, 40, 61, 16))
        self.label_7 = QLabel(self.groupBox_3)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(110, 60, 61, 16))
        self.label_8 = QLabel(self.groupBox_3)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(110, 80, 61, 16))
        self.groupBox_4 = QGroupBox(self.groupBox_2)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setGeometry(QRect(10, 130, 181, 181))
        self.label_17 = QLabel(self.groupBox_4)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setGeometry(QRect(10, 20, 101, 16))
        self.label_18 = QLabel(self.groupBox_4)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(10, 40, 101, 16))
        self.label_19 = QLabel(self.groupBox_4)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setGeometry(QRect(10, 60, 101, 16))
        self.label_20 = QLabel(self.groupBox_4)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setGeometry(QRect(10, 80, 61, 16))
        self.label_21 = QLabel(self.groupBox_4)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setGeometry(QRect(110, 20, 54, 16))
        self.label_22 = QLabel(self.groupBox_4)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setGeometry(QRect(110, 40, 61, 16))
        self.label_23 = QLabel(self.groupBox_4)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setGeometry(QRect(110, 60, 61, 16))
        self.label_24 = QLabel(self.groupBox_4)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setGeometry(QRect(110, 80, 61, 16))
        self.label_25 = QLabel(self.groupBox_4)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setGeometry(QRect(10, 100, 101, 16))
        self.label_26 = QLabel(self.groupBox_4)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setGeometry(QRect(10, 120, 101, 16))
        self.label_27 = QLabel(self.groupBox_4)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setGeometry(QRect(110, 100, 54, 16))
        self.label_28 = QLabel(self.groupBox_4)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setGeometry(QRect(110, 120, 54, 16))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u8c03\u8bd5\u83dc\u5355", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"\u5185\u90e8\u7ec8\u7aef", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"\u8fd0\u884c", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"\u4e0a\u4e00\u6761", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"\u4e0b\u4e00\u6761", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"0/0", None))
        self.pushButton_4.setText(QCoreApplication.translate("Form", u"\u65b0\u7ebf\u7a0b\u8fd0\u884c", None))
        self.comboBox.setCurrentText("")
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"\u5185\u90e8\u4fe1\u606f", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Form", u"\u4fa7\u8fb9\u680f\u63d0\u793a...", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u961f\u5217\u957f\u5ea6", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u663e\u793a\u4e2d\u6570\u91cf", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u6392\u961f\u4e2d\u6570\u91cf", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u603b\u5e8f\u5217\u7d22\u5f15", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"1", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"11", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"45", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("Form", u"\u7b97\u6cd5\u6838\u5fc3...", None))
        self.label_17.setText(QCoreApplication.translate("Form", u"\u73ed\u7ea7\u4fa6\u6d4b\u5668\u66f4\u65b0\u7387", None))
        self.label_18.setText(QCoreApplication.translate("Form", u"\u6210\u5c31\u4fa6\u6d4b\u5668\u66f4\u65b0\u7387", None))
        self.label_19.setText(QCoreApplication.translate("Form", u"\u603b\u8fd0\u884c\u65f6\u95f4", None))
        self.label_20.setText(QCoreApplication.translate("Form", u"\u6210\u5c31\u961f\u5217", None))
        self.label_21.setText(QCoreApplication.translate("Form", u"1", None))
        self.label_22.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_23.setText(QCoreApplication.translate("Form", u"11", None))
        self.label_24.setText(QCoreApplication.translate("Form", u"45", None))
        self.label_25.setText(QCoreApplication.translate("Form", u"\u73ed\u7ea7\u4fa6\u6d4b\u5668\u5e27\u65f6\u95f4", None))
        self.label_26.setText(QCoreApplication.translate("Form", u"\u6210\u5c31\u4fa6\u6d4b\u5668\u5e27\u65f6\u95f4", None))
        self.label_27.setText(QCoreApplication.translate("Form", u"14", None))
        self.label_28.setText(QCoreApplication.translate("Form", u"19", None))
    # retranslateUi

