"""
所有的窗口文件
"""

from typing import Union

from .basic.MyMainWindow import MyMainWindow
from .basic.MyWidget import MyWidget
from .custom.AboutWidget import AboutWidget
from .custom.AchievementWidget import AchievementWidget
from .custom.AttendanceInfoViewWidget import AttendanceInfoViewWidget
from .custom.AttendanceInfoWidget import AttendanceInfoWidget
from .custom.CleaningScoreSumUpWidget import CleaningScoreSumUpWidget
from .custom.DebugWidget import DebugWidget
from .custom.EditTemplateWidget import EditTemplateWidget
from .custom.GroupWidget import GroupWidget
from .custom.HistoryWidget import HistoryWidget
from .custom.HomeworkScoreSumUpWidget import HomeworkScoreSumUpWidget
from .custom.ListView import ListView
from .custom.NewTemplateWidget import NewTemplateWidget
from .custom.NoiseDetectorWidget import NoiseDetectorWidget
from .custom.RandomSelectorWidget import RandomSelectWidget
from .custom.SelectTemplateWidget import SelectTemplateWidget
from .custom.SettingWidget import SettingWidget
from .custom.StudentSelectorWidget import StudentSelectorWidget
from .custom.SelectTemplateWidget import SelectTemplateWidget
from .custom.SettingWidget import SettingWidget
from .custom.StudentWidget import StudentWidget
from .custom.WTFWidget import WTFWidget
from .custom.LoadingScreen import LoadingScreenWidget
from .custom.ExceptionHandler import ExceptionHandler

from .basic import *

WidgetType = Union[
    QMainWindow, QWidget, QFrame, QStackedWidget, QScrollArea, MyMainWindow, MyWidget
]