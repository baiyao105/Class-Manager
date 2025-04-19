# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'NewTemplateWindow.ui'
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
    QLabel, QLineEdit, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(442, 182)
        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(20, 80, 71, 16))
        self.label_4.setAlignment(Qt.AlignCenter)
        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 110, 71, 16))
        self.label_3.setAlignment(Qt.AlignCenter)
        self.lineEdit_3 = QLineEdit(Form)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setGeometry(QRect(100, 80, 271, 21))
        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(100, 50, 271, 21))
        self.doubleSpinBox = QDoubleSpinBox(Form)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setGeometry(QRect(100, 110, 131, 22))
        self.doubleSpinBox.setMinimum(-114514.000000000000000)
        self.doubleSpinBox.setMaximum(114514.000000000000000)
        self.doubleSpinBox.setValue(114514.000000000000000)
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 50, 71, 16))
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(240, 110, 191, 20))
        self.label_5.setAlignment(Qt.AlignCenter)
        self.label_6 = QLabel(Form)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(10, 10, 81, 21))
        self.label_6.setAlignment(Qt.AlignCenter)
        self.buttonBox = QDialogButtonBox(Form)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 150, 156, 24))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u65b0\u5efa\u6a21\u677f", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u63cf\u8ff0", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u5206\u6570", None))
        self.lineEdit_3.setText(QCoreApplication.translate("Form", u"\u6240\u4ee5\u5c31\u968f\u4fbf\u586b\u5427", None))
        self.lineEdit.setText(QCoreApplication.translate("Form", u"\u6211\u4e5f\u4e0d\u77e5\u9053\u586b\u4ec0\u4e48", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u539f\u56e0", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\uff08\u8fd9\u4e1c\u897f\u597d\u554a\uff0c\u9632\u6b62\u8f93\u5165\u62bd\u8c61\u6570\u5b57\uff09", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\u65b0\u5efa\u6a21\u677f", None))
    # retranslateUi

