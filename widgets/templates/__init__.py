"""
存取所有界面模板的模块。
"""


from utils.consts import qt_version

if qt_version == "PySide6":
    from .pyside6 import (
        About, AchievementWindow, AttendanceInfoEdit, AttendanceInfoView,
        CleaingScoreSumUp, DebugWindow, EditTemplateWindow, ExceptionHandler,
        GroupWindow, HomeworkScoreSumUp, ListBoxView, LoadingScreen, 
        MainClassWindow, ModifyHistoryWindow, MultiSelectWindow, NewTemplateWindow,
        NoiseDetector, NoticeViewer, RandomSelector, SelectTemplateWindow, 
        SettingWindow, StudentView, StudentWindow, WTF
    )

elif qt_version == "PyQt5":
    raise NotImplementedError("我好像把以前转换的文件弄丢了。。。")

elif qt_version == "PySide2":
    raise NotImplementedError("没转换，你们自己去玩去吧（雾")

elif qt_version == "PyQt6":
    raise NotImplementedError("这个版本我也没转换（不过怎么好像很少看到用这个版本的人）")



__all__ = ["About", "AchievementWindow", "AttendanceInfoEdit", "AttendanceInfoView",
        "CleaingScoreSumUp", "DebugWindow", "EditTemplateWindow", "ExceptionHandler",
        "GroupWindow", "HomeworkScoreSumUp", "ListBoxView", "LoadingScreen", 
        "MainClassWindow", "ModifyHistoryWindow", "MultiSelectWindow", "NewTemplateWindow",
        "NoiseDetector", "NoticeViewer", "RandomSelector", "SelectTemplateWindow", 
        "SettingWindow", "StudentView", "StudentWindow", "WTF"]