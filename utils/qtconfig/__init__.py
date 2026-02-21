"""
Qt配置文件（为了防止反复导入卡程序）
"""

from ..consts import qt_version

if qt_version == "PyQt5": # type: ignore
    from PyQt5.QtWidgets import *     # type: ignore
    from PyQt5.QtCore import *        # type: ignore
    from PyQt5.QtGui import *         # type: ignore
    Signal = pyqtSignal               # type: ignore
    Property = pyqtProperty           # type: ignore

elif qt_version == "PyQt6": # type: ignore
    from PyQt6.QtWidgets import *     # type: ignore
    from PyQt6.QtCore import *        # type: ignore
    from PyQt6.QtGui import *         # type: ignore


elif qt_version == "PySide2": # type: ignore
    from PySide2.QtWidgets import *     # type: ignore
    from PySide2.QtCore import *        # type: ignore
    from PySide2.QtGui import *         # type: ignore

elif qt_version == "PySide6":
    from PySide6.QtWidgets import *     # type: ignore
    from PySide6.QtCore import *        # type: ignore
    from PySide6.QtGui import *         # type: ignore
    from PySide6.QtQml import *         # type: ignore


from qfluentwidgets.common import *     # type: ignore
from qfluentwidgets.components import * # type: ignore
from qfluentwidgets.window import *     # type: ignore
from qfluentwidgets.multimedia import * # type: ignore

