"""
Qt配置文件（为了防止反复导入卡程序）
"""

from ..consts import qt_version

if qt_version == "PyQt5":
    from PyQt5.QtWidgets import *     # type: ignore
    from PyQt5.QtCore import *        # type: ignore
    from PyQt5.QtGui import *         # type: ignore
    Signal = pyqtSignal               # type: ignore
    Property = pyqtProperty           # type: ignore

elif qt_version == "PyQt6":
    from PyQt6.QtWidgets import *     # type: ignore
    from PyQt6.QtCore import *        # type: ignore
    from PyQt6.QtGui import *         # type: ignore


elif qt_version == "PySide2":
    from PySide2.QtWidgets import *     # type: ignore
    from PySide2.QtCore import *        # type: ignore
    from PySide2.QtGui import *         # type: ignore

elif qt_version == "PySide6":
    from PySide6.QtWidgets import *     # type: ignore
    from PySide6.QtCore import *        # type: ignore
    from PySide6.QtGui import *         # type: ignore
    from PySide6.QtQml import *         # type: ignore

