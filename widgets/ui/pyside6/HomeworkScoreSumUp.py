# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'HomeworkScoreSumUp.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QGridLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTabWidget, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1075, 546)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 10, 91, 16))
        font = QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.comboBox_3 = QComboBox(Form)
        self.comboBox_3.setObjectName(u"comboBox_3")
        self.comboBox_3.setGeometry(QRect(830, 10, 101, 22))
        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(770, 10, 54, 16))
        self.tabWidget = QTabWidget(Form)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(0, 90, 1071, 461))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayoutWidget = QWidget(self.tab)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 1061, 431))
        self.widget = QGridLayout(self.gridLayoutWidget)
        self.widget.setObjectName(u"widget")
        self.widget.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(500, 10, 251, 20))
        self.lineEdit_2 = QLineEdit(Form)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setGeometry(QRect(500, 40, 251, 20))
        self.doubleSpinBox = QDoubleSpinBox(Form)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setGeometry(QRect(500, 70, 111, 22))
        self.doubleSpinBox.setDecimals(1)
        self.doubleSpinBox.setMinimum(-114514.000000000000000)
        self.doubleSpinBox.setMaximum(114514.000000000000000)
        self.label_6 = QLabel(Form)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(460, 10, 54, 16))
        self.label_7 = QLabel(Form)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(460, 40, 54, 16))
        self.label_8 = QLabel(Form)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(460, 70, 54, 16))
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(780, 70, 121, 24))
        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(770, 40, 54, 16))
        self.comboBox_4 = QComboBox(Form)
        self.comboBox_4.setObjectName(u"comboBox_4")
        self.comboBox_4.setGeometry(QRect(830, 40, 101, 22))
        self.tabWidget_2 = QTabWidget(Form)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.tabWidget_2.setGeometry(QRect(210, 0, 241, 101))
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.comboBox_2 = QComboBox(self.tab_3)
        self.comboBox_2.setObjectName(u"comboBox_2")
        self.comboBox_2.setGeometry(QRect(70, 30, 151, 22))
        self.comboBox = QComboBox(self.tab_3)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(70, 0, 151, 22))
        self.label_2 = QLabel(self.tab_3)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(0, 0, 54, 16))
        self.label_3 = QLabel(self.tab_3)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 30, 54, 16))
        self.tabWidget_2.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.label_17 = QLabel(self.tab_4)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setGeometry(QRect(10, 20, 50, 15))
        self.comboBox_13 = QComboBox(self.tab_4)
        self.comboBox_13.setObjectName(u"comboBox_13")
        self.comboBox_13.setGeometry(QRect(80, 20, 141, 22))
        self.tabWidget_2.addTab(self.tab_4, "")

        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u4f5c\u4e1a\u5206\u6570\u7ed3\u7b97", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u4f5c\u4e1a\u7ed3\u7b97", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\u5217\u8868\u5bbd\u5ea6", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Form", u"\u4f5c\u4e1a\u7b49\u7b2c\u6dfb\u52a0", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Form", u"\u67e5\u770b\u4fe1\u606f", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\u4fe1\u606f", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"\u63cf\u8ff0", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"\u5206\u6570", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"\u89c4\u5219\u660e\u7ec6", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u64cd\u4f5c\u7c7b\u578b", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u5b66\u79d1\u540d\u79f0", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u7b49\u7b2c", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), QCoreApplication.translate("Form", u"\u6309\u4f5c\u4e1a\u89c4\u5219", None))
        self.label_17.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u6a21\u677f", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), QCoreApplication.translate("Form", u"\u81ea\u9009\u6a21\u677f", None))
    # retranslateUi

