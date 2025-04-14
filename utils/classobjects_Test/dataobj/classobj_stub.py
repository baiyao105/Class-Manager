"""
班级数据类型的预加载
"""
from abc import ABC
from typing import Any, Callable, Dict, List, Tuple, Type
from queue import Queue
from utils.algorithm import Stack

class ClassObj(ABC):

    archive_uuid: str
    "归档uuid"

    Student: Type
    "学生类型"

    Group: Type
    "小组类型"

    Class: Type
    "班级类型"

    ScoreModification: Type
    "分数修改类型"

    ScoreModificationTemplate: Type
    "分数修改模板类型"

    Achievement: Type
    "成就类型"

    AchievementTemplate: Type
    "成就模板类型"

    HomeWorkRule: Type
    "作业规则类型"

    AttendanceInfo: Type
    "考勤信息类型"

    DayRecord: Type
    "每日记录类型"

    History: Type
    "历史记录类型"

class ClassStatusObserver(ABC):
    "班级状态侦测器"

    on_active:                 bool
    "是否激活"
    student_count:             int
    "学生人数"
    student_total_score:       float
    "学生总分"
    class_id:                  str
    "班级ID"
    stu_score_ord:             dict
    "学生分数排序"
    classes:                   Dict[str, ClassObj.Class]
    "所有班级，是一个字典（ID, 班级对象）"
    target_class:              ClassObj.Class
    "目标班级"
    templates:                 Dict[str, ClassObj.ScoreModificationTemplate]
    "所有模板"
    opreation_record:          Stack
    "操作记录"
    groups:                    Dict[str, ClassObj.Group]
    "所有小组"
    base:                     "ClassObj"
    "后面用到的ClassObjects，算法基层"
    last_update:               float
    "上次更新时间"
    tps:                       int
    "最大每秒更新次数"
    rank_non_dumplicate:       List[Tuple[int, ClassObj.Student]]
    "去重排名"              
    rank_dumplicate:           List[Tuple[int, ClassObj.Student]]
    "不去重排名"



class AchievementStatusObserver(ABC):
    "成就状态侦测器"

    on_active:                  bool
    "是否激活"
    class_id:                   str
    "班级ID"
    classes:                    Dict[str, ClassObj.Class]
    "所有班级"
    achievement_templates:      Dict[str, ClassObj.AchievementTemplate]
    "所有成就模板"
    class_obs:                  ClassStatusObserver
    "班级状态侦测器"
    display_achievement_queue:  Queue
    "成就显示队列"
    achievement_displayer:      Callable[[str, ClassObj.Student], Any]
    "成就显示函数"
    last_update:                float
    "上次更新时间"
    base:                       "ClassObj.ClassObjects"
    "算法基层"
    tps:                        int
    "最大每秒更新次数"
