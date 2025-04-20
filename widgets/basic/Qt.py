"""
Qt处理模块，用来做多版本Qt适配
"""
# pylint: disable=E

from utils.consts import qt_version

if qt_version == "PyQt5":
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtCore import (
        pyqtSignal as Signal, 
        pyqtSlot as Slot,
        pyqtProperty as Property
    )
    from PyQt5 import QtCore
    from PyQt5 import QtGui
    from PyQt5 import QtWidgets


elif qt_version == "PyQt6":
    from PyQt6.QtWidgets import *
    from PyQt6.QtGui import *
    from PyQt6.QtCore import *
    from PyQt6 import QtCore
    from PyQt6 import QtGui
    from PyQt6 import QtWidgets

elif qt_version == "PySide2":
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2 import QtCore
    from PySide2 import QtGui
    from PySide2 import QtWidgets

elif qt_version == "PySide6":
    from PySide6.QtWidgets import *
    from PySide6.QtGui import *
    from PySide6.QtCore import *
    from PySide6 import QtCore
    from PySide6 import QtGui
    from PySide6 import QtWidgets


# from PySide6.QtWidgets import *
# from PySide6.QtGui import *
# from PySide6.QtCore import *

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *