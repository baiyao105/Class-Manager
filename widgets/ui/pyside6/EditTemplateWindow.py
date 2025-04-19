# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'EditTemplateWindow.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialogButtonBox, QDoubleSpinBox,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(445, 245)
        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(110, 60, 191, 21))
        self.lineEdit_3 = QLineEdit(Form)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setGeometry(QRect(110, 90, 191, 21))
        self.doubleSpinBox = QDoubleSpinBox(Form)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setGeometry(QRect(110, 120, 191, 22))
        self.doubleSpinBox.setMinimum(-114514.000000000000000)
        self.doubleSpinBox.setMaximum(114514.000000000000000)
        self.doubleSpinBox.setValue(2.000000000000000)
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(30, 60, 71, 16))
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(30, 120, 71, 16))
        self.label_3.setAlignment(Qt.AlignCenter)
        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(30, 90, 71, 16))
        self.label_4.setAlignment(Qt.AlignCenter)
        self.label_6 = QLabel(Form)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(20, 20, 81, 21))
        self.label_6.setAlignment(Qt.AlignCenter)
        self.buttonBox = QDialogButtonBox(Form)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(110, 200, 156, 24))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(320, 60, 75, 24))
        self.pushButton_2 = QPushButton(Form)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(320, 120, 75, 24))
        self.pushButton_3 = QPushButton(Form)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(320, 90, 75, 24))
        self.pushButton_4 = QPushButton(Form)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(320, 200, 75, 24))
        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(30, 150, 71, 16))
        self.label_5.setAlignment(Qt.AlignCenter)
        self.label_7 = QLabel(Form)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(110, 150, 191, 20))
        self.label_7.setAlignment(Qt.AlignCenter)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u9009\u62e9\u6a21\u677f", None))
        self.lineEdit.setText(QCoreApplication.translate("Form", u"\u5982\u679c\u4f60\u770b\u5230\u4e86\u8fd9\u6bb5\u6587\u672c", None))
        self.lineEdit_3.setText(QCoreApplication.translate("Form", u"\u90a3\u6211\u7684\u7a0b\u5e8f\u5927\u6982\u7387\u662f\u70b8\u4e86", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u539f\u56e0", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u5206\u6570", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u63cf\u8ff0", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\u4fee\u6539\u6a21\u677f", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"\u91cd\u7f6e", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"\u91cd\u7f6e", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"\u91cd\u7f6e", None))
        self.pushButton_4.setText(QCoreApplication.translate("Form", u"\u5220\u9664\u6a21\u677f", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\u5185\u90e8id", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"\u6211\u4e0d\u5230\u554a", None))
    # retranslateUi

