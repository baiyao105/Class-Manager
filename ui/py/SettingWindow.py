# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SettingWindow.ui'
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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QDoubleSpinBox, QGroupBox, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QSlider, QSpinBox,
    QTabWidget, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(747, 489)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 20, 54, 16))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.tabWidget = QTabWidget(Form)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(0, 50, 801, 381))
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.scrollArea_2 = QScrollArea(self.tab_3)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setGeometry(QRect(0, 0, 711, 350))
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 692, 1000))
        self.scrollAreaWidgetContents_2.setMinimumSize(QSize(0, 1000))
        self.groupBox = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(0, 0, 641, 171))
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(30, 40, 71, 16))
        self.score_up_color_r = QSpinBox(self.groupBox)
        self.score_up_color_r.setObjectName(u"score_up_color_r")
        self.score_up_color_r.setGeometry(QRect(120, 40, 42, 22))
        self.score_up_color_r.setMaximum(255)
        self.score_up_color_r.setValue(202)
        self.score_up_color_g = QSpinBox(self.groupBox)
        self.score_up_color_g.setObjectName(u"score_up_color_g")
        self.score_up_color_g.setGeometry(QRect(180, 40, 42, 22))
        self.score_up_color_g.setMaximum(255)
        self.score_up_color_g.setValue(255)
        self.score_up_color_b = QSpinBox(self.groupBox)
        self.score_up_color_b.setObjectName(u"score_up_color_b")
        self.score_up_color_b.setGeometry(QRect(240, 40, 42, 22))
        self.score_up_color_b.setMaximum(255)
        self.score_up_color_b.setValue(202)
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(30, 70, 91, 16))
        self.score_up_color_mixin_start = QDoubleSpinBox(self.groupBox)
        self.score_up_color_mixin_start.setObjectName(u"score_up_color_mixin_start")
        self.score_up_color_mixin_start.setGeometry(QRect(120, 70, 62, 22))
        self.score_up_color_mixin_start.setMaximum(114514.000000000000000)
        self.score_up_color_mixin_start.setSingleStep(1.000000000000000)
        self.score_up_color_mixin_start.setValue(2.000000000000000)
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(30, 100, 71, 16))
        self.score_up_color_end_r = QSpinBox(self.groupBox)
        self.score_up_color_end_r.setObjectName(u"score_up_color_end_r")
        self.score_up_color_end_r.setGeometry(QRect(120, 100, 42, 22))
        self.score_up_color_end_r.setMaximum(255)
        self.score_up_color_end_r.setValue(51)
        self.score_up_color_end_g = QSpinBox(self.groupBox)
        self.score_up_color_end_g.setObjectName(u"score_up_color_end_g")
        self.score_up_color_end_g.setGeometry(QRect(180, 100, 42, 22))
        self.score_up_color_end_g.setMaximum(255)
        self.score_up_color_end_g.setValue(207)
        self.score_up_color_end_b = QSpinBox(self.groupBox)
        self.score_up_color_end_b.setObjectName(u"score_up_color_end_b")
        self.score_up_color_end_b.setGeometry(QRect(240, 100, 42, 22))
        self.score_up_color_end_b.setMaximum(255)
        self.score_up_color_end_b.setValue(108)
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(30, 130, 91, 16))
        self.score_up_color_step = QDoubleSpinBox(self.groupBox)
        self.score_up_color_step.setObjectName(u"score_up_color_step")
        self.score_up_color_step.setGeometry(QRect(120, 130, 62, 22))
        self.score_up_color_step.setMaximum(114514.000000000000000)
        self.score_up_color_step.setSingleStep(1.000000000000000)
        self.score_up_color_step.setValue(12.000000000000000)
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(190, 130, 54, 16))
        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(190, 70, 54, 16))
        self.groupBox_2 = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(0, 170, 641, 171))
        self.label_14 = QLabel(self.groupBox_2)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(30, 40, 71, 16))
        self.score_down_color_r = QSpinBox(self.groupBox_2)
        self.score_down_color_r.setObjectName(u"score_down_color_r")
        self.score_down_color_r.setGeometry(QRect(120, 40, 42, 22))
        self.score_down_color_r.setMaximum(255)
        self.score_down_color_r.setValue(202)
        self.score_down_color_g = QSpinBox(self.groupBox_2)
        self.score_down_color_g.setObjectName(u"score_down_color_g")
        self.score_down_color_g.setGeometry(QRect(180, 40, 42, 22))
        self.score_down_color_g.setMaximum(255)
        self.score_down_color_g.setValue(255)
        self.score_down_color_b = QSpinBox(self.groupBox_2)
        self.score_down_color_b.setObjectName(u"score_down_color_b")
        self.score_down_color_b.setGeometry(QRect(240, 40, 42, 22))
        self.score_down_color_b.setMaximum(255)
        self.score_down_color_b.setValue(202)
        self.label_15 = QLabel(self.groupBox_2)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(30, 70, 91, 16))
        self.score_down_color_mixin_start = QDoubleSpinBox(self.groupBox_2)
        self.score_down_color_mixin_start.setObjectName(u"score_down_color_mixin_start")
        self.score_down_color_mixin_start.setGeometry(QRect(120, 70, 62, 22))
        self.score_down_color_mixin_start.setMaximum(114514.000000000000000)
        self.score_down_color_mixin_start.setSingleStep(1.000000000000000)
        self.score_down_color_mixin_start.setValue(2.000000000000000)
        self.label_16 = QLabel(self.groupBox_2)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setGeometry(QRect(30, 100, 71, 16))
        self.score_down_color_end_r = QSpinBox(self.groupBox_2)
        self.score_down_color_end_r.setObjectName(u"score_down_color_end_r")
        self.score_down_color_end_r.setGeometry(QRect(120, 100, 42, 22))
        self.score_down_color_end_r.setMaximum(255)
        self.score_down_color_end_r.setValue(51)
        self.score_down_color_end_g = QSpinBox(self.groupBox_2)
        self.score_down_color_end_g.setObjectName(u"score_down_color_end_g")
        self.score_down_color_end_g.setGeometry(QRect(180, 100, 42, 22))
        self.score_down_color_end_g.setMaximum(255)
        self.score_down_color_end_g.setValue(207)
        self.score_down_color_end_b = QSpinBox(self.groupBox_2)
        self.score_down_color_end_b.setObjectName(u"score_down_color_end_b")
        self.score_down_color_end_b.setGeometry(QRect(240, 100, 42, 22))
        self.score_down_color_end_b.setMaximum(255)
        self.score_down_color_end_b.setValue(108)
        self.label_17 = QLabel(self.groupBox_2)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setGeometry(QRect(30, 130, 91, 16))
        self.score_down_color_step = QDoubleSpinBox(self.groupBox_2)
        self.score_down_color_step.setObjectName(u"score_down_color_step")
        self.score_down_color_step.setGeometry(QRect(120, 130, 62, 22))
        self.score_down_color_step.setMaximum(114514.000000000000000)
        self.score_down_color_step.setSingleStep(1.000000000000000)
        self.score_down_color_step.setValue(12.000000000000000)
        self.label_18 = QLabel(self.groupBox_2)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(190, 130, 54, 16))
        self.label_19 = QLabel(self.groupBox_2)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setGeometry(QRect(190, 70, 54, 16))
        self.groupBox_3 = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(0, 340, 641, 131))
        self.label_20 = QLabel(self.groupBox_3)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setGeometry(QRect(30, 40, 71, 16))
        self.opacity = QDoubleSpinBox(self.groupBox_3)
        self.opacity.setObjectName(u"opacity")
        self.opacity.setGeometry(QRect(90, 40, 62, 22))
        self.opacity.setMaximum(1.000000000000000)
        self.opacity.setSingleStep(0.100000000000000)
        self.label_8 = QLabel(self.groupBox_3)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(160, 40, 101, 16))
        self.label_25 = QLabel(self.groupBox_3)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setGeometry(QRect(30, 90, 71, 16))
        self.horizontalSlider = QSlider(self.groupBox_3)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setGeometry(QRect(89, 90, 171, 20))
        self.horizontalSlider.setMinimum(2)
        self.horizontalSlider.setMaximum(19)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setPageStep(0)
        self.horizontalSlider.setValue(2)
        self.horizontalSlider.setSliderPosition(2)
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.label_26 = QLabel(self.groupBox_3)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setGeometry(QRect(280, 90, 54, 16))
        self.groupBox_4 = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setGeometry(QRect(0, 480, 641, 111))
        self.label_21 = QLabel(self.groupBox_4)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setGeometry(QRect(30, 40, 71, 16))
        self.label_22 = QLabel(self.groupBox_4)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setGeometry(QRect(30, 70, 71, 16))
        self.log_keep = QSpinBox(self.groupBox_4)
        self.log_keep.setObjectName(u"log_keep")
        self.log_keep.setGeometry(QRect(110, 40, 61, 22))
        self.log_keep.setMaximum(65535)
        self.log_keep.setValue(50)
        self.log_update = QDoubleSpinBox(self.groupBox_4)
        self.log_update.setObjectName(u"log_update")
        self.log_update.setGeometry(QRect(110, 70, 62, 22))
        self.log_update.setDecimals(3)
        self.log_update.setMaximum(10.000000000000000)
        self.log_update.setSingleStep(0.100000000000000)
        self.log_update.setValue(0.500000000000000)
        self.label_9 = QLabel(self.groupBox_4)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(180, 40, 54, 16))
        self.label_10 = QLabel(self.groupBox_4)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(180, 70, 54, 16))
        self.groupBox_7 = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.groupBox_7.setGeometry(QRect(0, 600, 641, 111))
        self.checkBox = QCheckBox(self.groupBox_7)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setGeometry(QRect(30, 40, 131, 20))
        self.checkBox.setChecked(True)
        self.label_30 = QLabel(self.groupBox_7)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setEnabled(True)
        self.label_30.setGeometry(QRect(30, 70, 161, 16))
        self.spinBox_3 = QSpinBox(self.groupBox_7)
        self.spinBox_3.setObjectName(u"spinBox_3")
        self.spinBox_3.setEnabled(True)
        self.spinBox_3.setGeometry(QRect(190, 70, 42, 22))
        self.spinBox_3.setMinimum(1)
        self.spinBox_3.setMaximum(360)
        self.spinBox_3.setValue(60)
        self.label_32 = QLabel(self.groupBox_7)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setGeometry(QRect(250, 70, 161, 16))
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.scrollArea = QScrollArea(self.tab)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setGeometry(QRect(0, 0, 781, 400))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 762, 1000))
        self.scrollAreaWidgetContents.setMinimumSize(QSize(0, 1000))
        self.groupBox_6 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setGeometry(QRect(10, 10, 711, 101))
        self.label_27 = QLabel(self.groupBox_6)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setGeometry(QRect(20, 30, 201, 16))
        self.label_28 = QLabel(self.groupBox_6)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setGeometry(QRect(30, 50, 54, 16))
        self.label_29 = QLabel(self.groupBox_6)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setGeometry(QRect(140, 50, 54, 16))
        self.spinBox = QSpinBox(self.groupBox_6)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setGeometry(QRect(50, 50, 71, 22))
        self.spinBox.setMinimum(-3840)
        self.spinBox.setMaximum(3840)
        self.spinBox.setSingleStep(10)
        self.spinBox_2 = QSpinBox(self.groupBox_6)
        self.spinBox_2.setObjectName(u"spinBox_2")
        self.spinBox_2.setGeometry(QRect(170, 50, 71, 22))
        self.spinBox_2.setReadOnly(False)
        self.spinBox_2.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.spinBox_2.setMinimum(-2160)
        self.spinBox_2.setMaximum(2160)
        self.spinBox_2.setSingleStep(10)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.scrollArea_3 = QScrollArea(self.tab_2)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setGeometry(QRect(0, 0, 721, 351))
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 702, 1000))
        self.scrollAreaWidgetContents_3.setMinimumSize(QSize(500, 1000))
        self.groupBox_5 = QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setGeometry(QRect(0, 10, 671, 181))
        self.autosave = QCheckBox(self.groupBox_5)
        self.autosave.setObjectName(u"autosave")
        self.autosave.setGeometry(QRect(80, 20, 79, 20))
        self.autosave.setChecked(True)
        self.label_11 = QLabel(self.groupBox_5)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(20, 20, 51, 16))
        self.autosavetime = QDoubleSpinBox(self.groupBox_5)
        self.autosavetime.setObjectName(u"autosavetime")
        self.autosavetime.setGeometry(QRect(80, 50, 62, 22))
        self.autosavetime.setMinimum(10.000000000000000)
        self.autosavetime.setMaximum(86400.000000000000000)
        self.label_12 = QLabel(self.groupBox_5)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(20, 50, 51, 16))
        self.label_13 = QLabel(self.groupBox_5)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(150, 50, 51, 16))
        self.label_23 = QLabel(self.groupBox_5)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setGeometry(QRect(20, 100, 71, 16))
        self.savepath = QComboBox(self.groupBox_5)
        self.savepath.setObjectName(u"savepath")
        self.savepath.setEnabled(False)
        self.savepath.setGeometry(QRect(80, 100, 221, 22))
        self.savepath.setEditable(False)
        self.label_24 = QLabel(self.groupBox_5)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setGeometry(QRect(0, 130, 81, 16))
        self.savepath_2 = QComboBox(self.groupBox_5)
        self.savepath_2.setObjectName(u"savepath_2")
        self.savepath_2.setGeometry(QRect(80, 130, 221, 22))
        self.savepath_2.setEditable(False)
        self.label_31 = QLabel(self.groupBox_5)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setGeometry(QRect(340, 100, 71, 16))
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)
        self.tabWidget.addTab(self.tab_2, "")
        self.save = QPushButton(Form)
        self.save.setObjectName(u"save")
        self.save.setGeometry(QRect(10, 450, 75, 24))
        self.cancel = QPushButton(Form)
        self.cancel.setObjectName(u"cancel")
        self.cancel.setGeometry(QRect(100, 450, 75, 24))
        self.reset = QPushButton(Form)
        self.reset.setObjectName(u"reset")
        self.reset.setGeometry(QRect(190, 450, 75, 24))

        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u8bbe\u7f6e", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u8bbe\u7f6e", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"\u5206\u6570\u4e0a\u5347", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u6700\u5c0f\u95ea\u70c1\u989c\u8272", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u6e10\u53d8\u5206\u6570\u8d77\u59cb\u503c", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u6700\u5927\u95ea\u70c1\u989c\u8272", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\u6e10\u53d8\u6700\u5927\u6b65\u957f", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\u5206", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"\u5206", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"\u5206\u6570\u4e0b\u964d", None))
        self.label_14.setText(QCoreApplication.translate("Form", u"\u6700\u5c0f\u95ea\u70c1\u989c\u8272", None))
        self.label_15.setText(QCoreApplication.translate("Form", u"\u6e10\u53d8\u5206\u6570\u8d77\u59cb\u503c", None))
        self.label_16.setText(QCoreApplication.translate("Form", u"\u6700\u5927\u95ea\u70c1\u989c\u8272", None))
        self.label_17.setText(QCoreApplication.translate("Form", u"\u6e10\u53d8\u6700\u5927\u6b65\u957f", None))
        self.label_18.setText(QCoreApplication.translate("Form", u"\u5206", None))
        self.label_19.setText(QCoreApplication.translate("Form", u"\u5206", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Form", u"\u7a97\u53e3", None))
        self.label_20.setText(QCoreApplication.translate("Form", u"\u4e0d\u900f\u660e\u5ea6", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"\uff08\u91cd\u542f\u540e\u751f\u6548\uff09", None))
        self.label_25.setText(QCoreApplication.translate("Form", u"\u52a8\u753b\u901f\u5ea6", None))
        self.label_26.setText(QCoreApplication.translate("Form", u"\u5173\u95ed", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("Form", u"\u65e5\u5fd7\u7a97\u53e3\uff08\u6bd4\u8f83\u70b8\u6027\u80fd\uff09", None))
        self.label_21.setText(QCoreApplication.translate("Form", u"\u4fdd\u7559\u65e5\u5fd7\u884c\u6570", None))
        self.label_22.setText(QCoreApplication.translate("Form", u"\u65e5\u5fd7\u5237\u65b0\u95f4\u9694", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"\u884c", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"\u79d2/\u6b21", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("Form", u"\u80cc\u666f\u663e\u793a", None))
        self.checkBox.setText(QCoreApplication.translate("Form", u"\u542f\u7528\u52a8\u6001\u80cc\u666f", None))
        self.label_30.setText(QCoreApplication.translate("Form", u"\u9650\u5236\u6700\u5927\u5e27\u7387", None))
        self.label_32.setText(QCoreApplication.translate("Form", u"\uff08\u89c9\u5f97\u52a8\u6001\u80cc\u666f\u5361\u5c31\u6539\u4f4e\u70b9\uff09", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("Form", u"\u663e\u793a", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("Form", u"\u521b\u5efa\u65b0\u7a97\u53e3", None))
        self.label_27.setText(QCoreApplication.translate("Form", u"\u65b0\u7a97\u53e3\u57fa\u4e8e\u7236\u7a97\u53e3\u4e2d\u5fc3\u5750\u6807\u7684\u504f\u79fb\u91cf", None))
        self.label_28.setText(QCoreApplication.translate("Form", u"x", None))
        self.label_29.setText(QCoreApplication.translate("Form", u"y", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Form", u"\u64cd\u4f5c", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("Form", u"\u4fdd\u5b58\u8bbe\u7f6e\uff08\u91cd\u542f\u540e\u751f\u6548\uff09", None))
        self.autosave.setText("")
        self.label_11.setText(QCoreApplication.translate("Form", u"\u81ea\u52a8\u4fdd\u5b58", None))
        self.label_12.setText(QCoreApplication.translate("Form", u"\u4fdd\u5b58\u95f4\u9694", None))
        self.label_13.setText(QCoreApplication.translate("Form", u"\u79d2", None))
        self.label_23.setText(QCoreApplication.translate("Form", u"\u4fdd\u5b58\u8def\u5f84", None))
        self.savepath.setPlaceholderText("")
        self.label_24.setText(QCoreApplication.translate("Form", u"\u5b58\u6863\u5907\u4efd\u9014\u5f84", None))
        self.savepath_2.setPlaceholderText(QCoreApplication.translate("Form", u"\u65e0", None))
        self.label_31.setText(QCoreApplication.translate("Form", u"\uff08\u61d2\u5f97\u505a\u4e86\uff09", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Form", u"\u5b58\u50a8", None))
        self.save.setText(QCoreApplication.translate("Form", u"\u4fdd\u5b58", None))
        self.cancel.setText(QCoreApplication.translate("Form", u"\u53d6\u6d88", None))
        self.reset.setText(QCoreApplication.translate("Form", u"\u91cd\u7f6e\u8bbe\u7f6e", None))
    # retranslateUi

