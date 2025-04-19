# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SelectTemplateWindow.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialogButtonBox,
    QDoubleSpinBox, QLabel, QLineEdit, QSizePolicy,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(377, 219)
        self.comboBox = QComboBox(Form)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(40, 30, 281, 22))
        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(100, 60, 231, 21))
        self.lineEdit_3 = QLineEdit(Form)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setGeometry(QRect(100, 90, 231, 21))
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 60, 71, 16))
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 120, 71, 16))
        self.label_3.setAlignment(Qt.AlignCenter)
        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(20, 90, 71, 16))
        self.label_4.setAlignment(Qt.AlignCenter)
        self.doubleSpinBox = QDoubleSpinBox(Form)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setGeometry(QRect(100, 120, 91, 22))
        self.doubleSpinBox.setDecimals(1)
        self.doubleSpinBox.setMinimum(-114514.000000000000000)
        self.doubleSpinBox.setMaximum(114514.000000000000000)
        self.doubleSpinBox.setValue(114514.000000000000000)
        self.buttonBox = QDialogButtonBox(Form)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(100, 170, 156, 24))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 10, 61, 21))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u9009\u62e9\u6a21\u677f", None))
        self.lineEdit.setText(QCoreApplication.translate("Form", u"\u5982\u679c\u4f60\u770b\u5230\u4e86\u8fd9\u4e00\u6bb5\u6587\u672c", None))
        self.lineEdit_3.setText(QCoreApplication.translate("Form", u"\u90a3\u6211\u7684\u7a0b\u5e8f\u5927\u6982\u7387\u662f\u70b8\u4e86", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u539f\u56e0", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u5206\u6570", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u63cf\u8ff0", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u6a21\u677f", None))
    # retranslateUi

