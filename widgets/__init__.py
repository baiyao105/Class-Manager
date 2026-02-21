"""
所有的窗口文件
"""


from .basic.MyMainWindow import MyMainWindow
from .basic.MyWidget import MyWidget
from .basic.widgets import ObjectButton, ProgressAnimatedListWidgetItem, SideNotice
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
from .custom.StudentWidget import StudentWidget
from .custom.WTFWidget import WTFWidget
from .custom.LoadingScreen import LoadingScreenWidget
from .custom.ExceptionHandler import ExceptionHandlerWidget

from .basic import *

__all__ = [
    "MyMainWindow", "MyWidget", "AboutWidget", "AchievementWidget",
    "AttendanceInfoViewWidget", "AttendanceInfoWidget", "CleaningScoreSumUpWidget",
    "DebugWidget", "EditTemplateWidget",  "GroupWidget", "HistoryWidget",
    "HomeworkScoreSumUpWidget", "ListView", "NewTemplateWidget",
    "NoiseDetectorWidget", "RandomSelectWidget", "SelectTemplateWidget",
    "SettingWidget", "StudentSelectorWidget", "StudentWidget", "WTFWidget",
    "LoadingScreenWidget", "ExceptionHandlerWidget",
    "ObjectButton", "ProgressAnimatedListWidgetItem", "SideNotice"
]
