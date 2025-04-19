"""
完整班级数据处理对象的模块。
"""

import os
import enum
import copy
import time
import errno
import signal
import base64
import random
import warnings
import traceback
from queue import Queue
from abc import abstractmethod
from types import TracebackType, FrameType
from typing import *  # pylint: disable=wildcard-import, unused-wildcard-import


import pickle as pickle_orig
import pickle  # pylint: disable=reimported
import dill as pickle  # pylint: disable=shadowed-import
from PySide6.QtGui import *  # pylint: disable=wildcard-import, unused-wildcard-import
from PySide6.QtWidgets import QMessageBox


from utils.basetypes import Object, Base
from utils.basetypes import sys, gen_uuid
from utils.update_check import (
    VERSION_INFO,
    CLIENT_UPDATE_LOG,
)  # pylint: disable=unused-import
from utils.classdtypes import (
    Student,
    StrippedStudent,
    Group,
    Class,  # pylint: disable=unused-import
    ScoreModificationTemplate,
    ScoreModification,
    Achievement,
    AchievementTemplate,
    AttendanceInfo,
    DayRecord,
    History,
    ClassObj as OrigClassObj,
    HomeworkRule,
    dummy_student,
)
from utils.algorithm.datatypes import Stack, Thread
from utils.algorithm.keyorder import OrderedKeyList
from utils.functions.sounds import (
    stop_music,
    play_sound,
    play_music,
)  # pylint: disable=unused-import
from utils.functions.numbers import addrof
from utils.dataloader import (
    Chunk,
    UserDataBase,
    DataObject,
)  # pylint: disable=unused-import
from utils.functions.prompts import question_yes_no
from utils.consts import default_user


CORE_VERSION = VERSION_INFO["core_version"]
"""核心版本号"""

CORE_VERSION_CODE = VERSION_INFO["core_version_code"]
"""核心版本号代码，用于版本比较"""


try:
    from utils.default import (
        DEFAULT_ACHIEVEMENTS,
        DEFAULT_CLASSES,
        DEFAULT_SCORE_TEMPLATES,
        DEFAULT_CLASS_KEY,
    )
except ImportError as unused:  # pylint: disable=unused-variable
    from utils.bak.default import (
        DEFAULT_ACHIEVEMENTS,
        DEFAULT_CLASSES,
        DEFAULT_SCORE_TEMPLATES,
        DEFAULT_CLASS_KEY,
    )

    warnings.warn(
        "没有检测到utils/default.py，"
        "建议将自己班级的数据根据utils/bak/default.py进行修改后"
        "复制到utils/default.py，就可以用自己的数据了"
    )


ctrlc_times = 0  # pylint: disable=invalid-name
"""Ctrl+C按下计数器"""

sys.stdout = Base.captured_stdout
sys.stderr = Base.captured_stderr


def sigint_handler(sigval: Optional[int], frame: Optional[FrameType]):
    """Ctrl+C信号处理函数"""
    global ctrlc_times  # pylint: disable=global-statement
    assert (
        sigval == signal.SIGINT
    ), f"这怎么和我预想中的不一样呢（sigval={sigval}, signal.SIGINT={signal.SIGINT}）"
    ctrlc_times += 1
    addr = addrof(frame)
    if ctrlc_times >= 500:
        Base.log(
            "W",
            f"要不我自己raise一个RuntimeError吧（帧地址：{addr}）",
            "sigint_handler",
        )
    elif ctrlc_times >= 30:
        Base.log(
            "W", f"你再按别把程序玩出RuntimeError了（帧地址：{addr}）", "sigint_handler"
        )
    elif ctrlc_times >= 10:
        # 处理Ctrl+C中断信号
        Base.log("W", f"你真是够了（帧地址：{addr}）", "sigint_handler")
    else:
        Base.log(
            "W",
            f"收到了SIGINT信号，没事别瞎按Ctrl+C\n帧:{repr(frame)}",
            "sigint_handler",
        )


signal.signal(signal.SIGINT, sigint_handler)


def utc(precision: int = 3):
    """返回当前时间戳

    :param precision: 时间戳精度，表示小数点后的位数，默认为3
    :return: 指定精度的时间戳整数
    """
    return int(time.time() * pow(10, precision))


class ClassObj(OrigClassObj):
    "班级对象类"

    def __init__(self, user: str = default_user, save_path: Optional[str] = None):
        """
        构造一个新的用户班级对象。

        :param user: 用户名
        :param saving_path: 保存路径
        """
        super().__init__()
        self.class_name = None
        self.class_id = None
        self.current_user = user
        if save_path is None:
            save_path = os.path.join(os.getcwd(), "chunks", user)

        self.config_data(save_path)

        self.target_class = None
        "目标班级"
        self.achievement_obs: AchievementStatusObserver
        "成就侦测器"
        self.class_obs: ClassStatusObserver
        "班级侦测器"
        self.default_achievements = DEFAULT_ACHIEVEMENTS
        "默认成就"
        self.default_score_templates = DEFAULT_SCORE_TEMPLATES
        "默认分数模板"
        self.last_reset: float
        "上次重置时间"
        self.history_data: Dict[float, ClassObj.History]
        "历史数据"
        self.save_path: str = save_path
        "保存路径"
        self.modify_templates: Dict[str, ClassObj.ScoreModificationTemplate]
        "分数修改模板"
        self.achievement_templates: Dict[str, ClassObj.AchievementTemplate]
        "成就模板"
        self.current_day_attendance: ClassObj.AttendanceInfo
        "当前日考勤信息"
        self.classes: Dict[str, ClassObj.Class]
        "班级"
        self.weekday_record: List[ClassObj.DayRecord]
        "每日记录"
        self.auto_saving: bool = False
        "是否正在进行自动保存"
        Base.log(
            "W",
            "警告：当前仅加载完成数据，需具体设置详细用户/班级信息（self.init_class_data）",
            "ClassObjects",
        )

    def init_class_data(
        self,
        current_user: str = None,
        class_name: str = None,
        class_id: str = None,
        class_obs_tps: int = 10,
        achievement_obs_tps: int = 10,
    ):
        """
        初始化班级和用户信息，为了防止直接访问类成员爆炸写的

        :param current_user: 当前用户
        :param class_name: 班级名
        :param class_id: 班级id
        :param class_obs_tps: 班级侦测器刻速率
        :param achievement_obs_tps: 成就侦测器刻速率
        """
        self.current_user = current_user
        self.class_name = class_name
        self.class_id = class_id
        self.target_class = self.classes[self.class_id]
        self.class_obs = ClassStatusObserver(self, class_id, class_obs_tps)
        self.achievement_obs = AchievementStatusObserver(
            self, class_id, tps=achievement_obs_tps
        )
        self.class_obs.start()
        self.achievement_obs.start()
        if self.current_day_attendance is None:
            self.current_day_attendance = ClassObj.AttendanceInfo(self.target_class.key)
        Base.log(
            "I",
            f"初始化完成：用户[{current_user}], "
            f"班级名[{class_name}], 班级id[{class_id}]\n"
            f"当前班级：{self.target_class.name}，"
            f"班级侦测器刻速率：{class_obs_tps}，"
            f"成就侦测器刻速率：{achievement_obs_tps}",
            "ClassObjects.init_class_data",
        )

    @staticmethod
    def load_data(
        path: str = os.getcwd() + os.sep + f"chunks/{default_user}/",
        silent: bool = False,
        strict: bool = True,
        method: Literal["pickle", "sqlite", "auto"] = "sqlite",
        load_full_histories: bool = False,
    ) -> UserDataBase:
        """
        从文件加载存档。（只是返回数据！！）

        :param path: 文件路径
        :param silent: 是否静默加载
        :param strict: 是否抛出错误
        :param method: 加载方法，可以是"pickle"，"sqlite"或"auto"
        :param load_full_histories: 是否加载完整历史记录，只在method="sqlite"时有效
        :return: 存档数据
        """
        start = time.time()
        if not silent:
            Base.log("I", "从" + path + "加载数据...", "MainThread.save_data")
        if method == "auto":
            dirpath = os.path.dirname(path)
            if os.path.exists(os.path.join(dirpath, "info.json")):
                path = dirpath
                method = "sqlite"
            else:
                method = "pickle"

        try:
            if method == "pickle":
                b = base64.b85decode(open(path, "r", encoding="utf-8").read())
                f = open(path + ".tmp", "wb")
                f.write(b)
                f.close()
                try:
                    data = pickle.load(open(path + ".tmp", "rb"))
                except AttributeError:
                    data = pickle_orig.load(open(path + ".tmp", "rb"))
                try:
                    os.remove(path + ".tmp")
                except (
                    Exception
                ) as unused:  # pylint: disable=unused-variable, broad-exception-caught
                    pass
                if not silent:
                    Base.log(
                        "I", f"耗时：{time.time()-start:.2f}", "MainThread.load_data"
                    )
                return UserDataBase(**data)

            elif method == "sqlite":
                path = os.path.dirname(path) if path.endswith(".datas") else path
                data_chunk = Chunk(path)
                data = data_chunk.load_data(load_full_histories)
                if not silent:
                    Base.log(
                        "I", f"耗时：{time.time()-start:.2f}", "MainThread.load_data"
                    )
                return data

        except FileNotFoundError as exception:
            if strict:
                raise exception
            Base.log(
                "W", "存档" + path + "不存在，重置所有数据", "MainThread.load_data"
            )
            ClassObj.reset_data(path)
            Base.log("I", f"耗时：{time.time()-start:.2f}", "MainThread.load_data")
            Base.log("I", "重新加载...", "MainThread.load_data")

            return ClassObj.load_data(path, strict=True)

        except Exception as e:  # pylint: disable=broad-exception-caught
            if strict:
                raise e
            Base.log_exc("读取存档" + path + "失败：", "Mainhread.load_data")
            Base.log("I", f"耗时：{time.time()-start:.2f}", "MainThread.load_data")

            if isinstance(e, OSError):
                if e.errno == errno.EACCES:
                    QMessageBox.critical(
                        None,
                        "出错了！",
                        f"没有权限读取文件[{path}]，请检查文件权限"
                        + f"\n[{e.__class__.__name__}] {e}",
                    )
                    os._exit(1)
                elif e.errno == errno.EPERM:
                    QMessageBox.critical(
                        None,
                        "出错了！",
                        f"没有权限读文件[{path}]，请检查文件权限"
                        + f"\n[{e.__class__.__name__}] {e}",
                    )
                    os._exit(1)

                elif e.errno == errno.EISDIR:
                    QMessageBox.critical(
                        None,
                        "出错了！",
                        f"文件[{path}]是一个目录，请检查文件路径"
                        + f"\n[{e.__class__.__name__}] {e}",
                    )
                    os._exit(1)

                elif e.errno == errno.ENOSPC:
                    QMessageBox.critical(
                        None,
                        "出错了！",
                        f"磁盘空间不足，无法读取文件[{path}]，请清理后重新尝试"
                        + f"\n[{e.__class__.__name__}] {e}",
                    )
                    os._exit(1)

                elif e.errno == errno.ENOENT:
                    Base.log(
                        "W",
                        "文件不存在，可能是首次加载，重置所有数据",
                        "MainThread.load_data",
                    )

                elif e.errno == errno.EMFILE:
                    QMessageBox.critical(
                        None,
                        "出错了！",
                        f"打开文件过多，无法读取文件[{path}]"
                        + f"\n[{e.__class__.__name__}] {e}",
                    )
                    os._exit(1)

                elif e.errno == errno.EIO:
                    QMessageBox.critical(
                        None,
                        "出错了！",
                        f"读取文件[{path}]时发生I/O错误"
                        + f"\n[{e.__class__.__name__}] {e}",
                    )
                    os._exit(1)

                elif e.errno == errno.EBADF:
                    QMessageBox.critical(
                        None,
                        "出错了！",
                        f"文件[{path}]是一个无效的文件描述符"
                        + f"\n[{e.__class__.__name__}] {e}",
                    )
                    os._exit(1)

                else:
                    QMessageBox.critical(
                        None,
                        "出错了！",
                        f"读取文件[{path}]时发生未知错误：\n{traceback.format_exc()}"
                        f"\n[{e.__class__.__name__}] {e}",
                    )
                    os._exit(1)

            result = question_yes_no(
                None,
                "出错了！",
                f"从[{path}]加载文件出错：\n{traceback.format_exc()}\n"
                "是否尝试重新加载？\n\n（你没有忘记建还原点，对吧？）",
                msg_type="critical",
            )
            if not result:
                ClassObj.reset_data(path)

            return ClassObj.load_data(path, strict=True)

    def reset_missing(self):
        "把默认数据（比如当前不存在的模板和成就）加入到现有数据中"
        for _class in DEFAULT_CLASSES.values():
            for default_group in _class.groups.values():
                if (
                    default_group.key not in _class.groups
                ):  # 如果默认小组不存在就给他加回去
                    _class.groups[default_group.key] = default_group
                self.classes[_class.key].groups[
                    default_group.key
                ].further_desc = default_group.further_desc
                # 复原默认描述，满足他们的文学创作

        for (
            default_achievement
        ) in DEFAULT_ACHIEVEMENTS.values():  # 补齐存档中缺失的默认成就
            if default_achievement.key not in self.achievement_templates:
                self.achievement_templates[default_achievement.key] = (
                    default_achievement
                )

        for (
            default_template
        ) in DEFAULT_SCORE_TEMPLATES.values():  # 补齐存档中缺失的默认模板
            if default_template.key not in self.modify_templates:
                self.modify_templates[default_template.key] = default_template

    def reset_all_defaults(self):
        "重置所有默认模板"
        for a in copy.deepcopy(self.achievement_templates).keys():  # 重置成就模板
            if a in DEFAULT_ACHIEVEMENTS:
                self.achievement_templates[a] = DEFAULT_ACHIEVEMENTS[a]

        for a in copy.deepcopy(self.modify_templates).keys():  # 重置分数模板
            if a in DEFAULT_SCORE_TEMPLATES.keys():
                self.modify_templates[a] = DEFAULT_SCORE_TEMPLATES[a]

        for c in copy.deepcopy(self.classes).keys():  # 重置班级信息
            if c in DEFAULT_CLASSES:
                # 恢复默认卫生打扫规则
                self.classes[c].cleaning_mapping = DEFAULT_CLASSES[c].cleaning_mapping
                # 恢复作业规则
                self.classes[c].homework_rules = DEFAULT_CLASSES[c].homework_rules
                self.classes[c].name = DEFAULT_CLASSES[c].name  # 恢复班级名
                self.classes[c].owner = DEFAULT_CLASSES[c].owner  # 恢复班主任信息
                default_students = DEFAULT_CLASSES[c].students.copy()

                # 重置这个班级的学生信息
                for s in copy.deepcopy(self.classes[c].students).keys():
                    if s in default_students:
                        # 恢复学生姓名
                        self.classes[c].students[s].name = default_students[s].name
                        # 恢复学号
                        self.classes[c].students[s].num = default_students[s].num
                        self.classes[c].students[s].belongs_to_group = default_students[
                            s
                        ].belongs_to_group  # 恢复所属小组

        for _class in self.classes.values():
            for g in copy.deepcopy(_class.groups).keys():  # 重置小组信息
                if g in DEFAULT_CLASSES[_class.key].groups.keys():

                    _class.groups[g].further_desc = (
                        DEFAULT_CLASSES[_class.key].groups[g].further_desc
                    )  # 恢复默认描述

                    _class.groups[g].name = (
                        DEFAULT_CLASSES[_class.key].groups[g].name
                    )  # 恢复小组名

                    _class.groups[g].belongs_to = (
                        DEFAULT_CLASSES[_class.key].groups[g].belongs_to
                    )  # 恢复所属班级

    def reset_all_data(self, reset_students_and_groups: bool = False):
        "重置所有数据"
        self.modify_templates = copy.deepcopy(DEFAULT_SCORE_TEMPLATES)
        self.achievement_templates = copy.deepcopy(DEFAULT_ACHIEVEMENTS)
        if reset_students_and_groups:
            self.classes = copy.deepcopy(DEFAULT_CLASSES)
        else:
            self.reset_all_defaults()

    def clear_history(self):
        "清空所有历史数据"
        self.history_data = {}

    def config_data(
        self,
        path: str = os.getcwd() + os.sep + f"chunks/{default_user}/",
        silent: bool = False,
        strict=False,
        reset_missing=False,
        mode: Literal["sqlite", "pickle", "auto"] = "sqlite",
        load_full_histories=False,
        reset_current=True,
    ) -> UserDataBase:
        """
        从文件加载存档并设置数据。

        :param path: 文件路径
        :param silent: 是否静默加载
        :param strict: 是否抛出错误
        :param reset_existing: 是否把默认数据（比如当前不存在的模板和成就）加入到现有数据中
        :param load_full_histories: 加载全部历史记录
        :param reset_current: 加载数据时覆盖本周的数据
        """
        data = ClassObj.load_data(path, silent, strict, mode, load_full_histories)
        self.save_version = data.version
        self.save_version_code = data.version_code
        self.currrent_core_version = CORE_VERSION
        self.current_core_version_code = CORE_VERSION_CODE

        if self.save_version_code > self.current_core_version_code:
            Base.log(
                "I",
                "尝试加载新版本的存档，多余数据可能部分丢失",
                "ClassObjects.config_data",
            )

        elif self.save_version_code < self.current_core_version_code:
            Base.log(
                "I",
                "尝试加载旧版本的存档，缺失的数据已经用默认代替",
                "ClassObjects.config_data",
            )

        if reset_current:

            self.classes: Dict[str, "ClassObj.Class"] = data.classes
            if isinstance(self.classes, OrderedKeyList):
                self.classes = self.classes.to_dict()  # 转换为字典解决类型问题

            if hasattr(self, "target_class") and self.target_class is not None:
                self.target_class = self.classes[self.target_class.key]
            else:
                self.target_class = None

            self.achievement_templates: Dict[str, ClassObj.AchievementTemplate] = (
                OrderedKeyList(data.achievements).to_dict()
            )  # 转换为字典
            self.modify_templates: Dict[str, ClassObj.ScoreModificationTemplate] = (
                OrderedKeyList(data.templates).to_dict()
            )

            achievements = copy.deepcopy(self.achievement_templates)
            for key, achievement in achievements.items():
                for attr, default in [
                    ("icon", None),
                    ("when_triggered", "any"),
                    (
                        "further_info",
                        "因为这是老版本迁移过来的存档，所以这条信息是空缺的",
                    ),
                    (
                        "condition_info",
                        "因为这是老版本迁移过来的存档，所以暂时没有详细条件信息",
                    ),
                ]:
                    # 补齐老版本缺失的属性

                    if not hasattr(achievement, attr):
                        try:
                            setattr(
                                self.achievement_templates[key],
                                attr,
                                getattr(DEFAULT_ACHIEVEMENTS[key], attr),
                            )
                        except (AttributeError, KeyError):
                            setattr(self.achievement_templates[key], attr, default)

            if not isinstance(self.modify_templates, OrderedKeyList):
                self.modify_templates = OrderedKeyList(self.modify_templates)
                # 因为老版本用的是dict，所以需要转换一下

            templates = copy.deepcopy(self.modify_templates)

            for key, template in templates.items():
                for attr, default in [
                    ("is_visible", True),
                ]:
                    if not hasattr(template, attr):
                        try:
                            setattr(
                                self.modify_templates[key],
                                attr,
                                getattr(DEFAULT_SCORE_TEMPLATES[key], attr),
                            )
                        except (AttributeError, KeyError):
                            setattr(self.modify_templates[key], attr, default)

            for key_class, _class in self.classes.items():
                for attr, default in [
                    (
                        "homework_rules",
                        (
                            (DEFAULT_CLASSES[key_class].homework_rules)
                            if key_class in DEFAULT_CLASSES
                            else {}
                        ),
                    ),
                    (
                        "cleaning_mapping",
                        (
                            getattr(
                                _class,
                                "cleaing_mapping",
                                getattr(_class, "cleaning_mapping", {}),
                            )
                        ),
                    ),
                    # 因为以前的版本是写错了的，所以这里需要特殊处理
                ]:
                    if not hasattr(_class, attr):
                        try:
                            setattr(
                                self.classes[key_class],
                                attr,
                                getattr(DEFAULT_CLASSES[key_class], attr),
                            )
                        except (AttributeError, KeyError):
                            setattr(self.classes[key_class], attr, default)

                for (
                    key,
                    student,
                ) in _class.students.items():  # 性能优化点：当前为O(n^3)复杂度(?)
                    for attr, default in [("last_reset_info", Student.new_dummy())]:
                        if not hasattr(student, attr):
                            try:
                                setattr(student, attr, default)
                            except (AttributeError, KeyError):
                                setattr(student, attr, default)
                if not hasattr(_class, "groups"):
                    if _class.key in DEFAULT_CLASSES:
                        _class.groups = copy.deepcopy(
                            DEFAULT_CLASSES[_class.key].groups
                        )
                    else:
                        _class.groups = {}
                for key, group in _class.groups.items():
                    index = 0
                    for member in group.members:
                        group.members[index] = self.classes[member.belongs_to].students[
                            member.num
                        ]
                        index += 1

            if "current_day_attendance" in data:
                self.current_day_attendance = data.current_day_attendance
            else:
                self.current_day_attendance = (
                    ClassObj.AttendanceInfo(
                        self.target_class.key, [], [], [], [], [], [], []
                    )
                    if self.target_class is not None
                    else None
                )

            if "weekday_record" in data:
                self.weekday_record: List[ClassObj.DayRecord] = [
                    day for day in data.weekday_record if day.utc > 1000000000
                ]
            else:
                self.weekday_record = []

        if reset_missing:  # 如果需要重置，则重置
            self.reset_missing()

        if "last_reset" in data:
            self.last_reset = data.last_reset
        else:
            self.last_reset = 0.0

        if "history_data" in data:
            self.history_data = data.history_data
        else:
            self.history_data = {}

        if "last_start_time" in data:
            self.last_start_time = data.last_start_time
        else:
            self.last_start_time = time.time()

        Base.log(
            "I",
            f"数据加载完成：{len(self.classes)}个班级，"
            f"{len(self.achievement_templates)}个成就模板，"
            f"{len(self.modify_templates)}个修改模板",
            "ClassObjects.config_data",
        )
        self.load_succeed = True

        return data

    @staticmethod
    def save_data_strict(
        user: str,
        save_time: float,
        version: str,
        version_code: int,
        last_reset: float,
        history_data: Dict[float, History],
        classes: Dict[str, Class],
        templates: Dict[str, "ClassObj.ScoreModificationTemplate"],
        achievements: Dict[str, AchievementTemplate],
        last_start_time: float,
        weekday_record: List[DayRecord],
        current_day_attendance: AttendanceInfo,
        *,
        path: str = os.getcwd() + os.sep + f"chunks/{default_user}/",
        mode: Literal["pickle", "sqlite"] = "sqlite",
    ):
        """强制以指定数据保存存档。

        :param path: 文件路径
        """

        Base.log("I", "保存数据到" + path + "...", "MainThread.save_data_strict")
        st = time.time()
        try:
            if not os.path.isdir(os.path.dirname(path)):
                Base.log("I", "路径不存在，尝试创建...", "MainThread.save_data_strict")
                p = os.path.dirname(path)
                os.makedirs(p, exist_ok=True)
            obj = {
                "user": user,
                "time": save_time,
                "version": version,
                "version_code": version_code,
                "last_reset": last_reset,
                "history_data": history_data,
                "classes": classes,
                "templates": templates,
                "achievements": achievements,
                "last_start_time": last_start_time,
                "weekday_record": weekday_record,
                "current_day_attendance": current_day_attendance,
            }
            database = UserDataBase(
                user,
                save_time,
                version,
                version_code,
                last_reset,
                history_data,
                classes,
                templates,
                achievements,
                last_start_time,
                weekday_record,
                current_day_attendance,
            )
            if mode == "sqlite":
                path = os.path.dirname(path) if path.endswith(".datas") else path
                chunk = Chunk(path, database)
                t = time.time()
                chunk.save()
                Base.log(
                    "I",
                    f"写入文件完成 ({time.time()-t:.3f}s)",
                    "MainThread.save_data_strict",
                )
                Base.log(
                    "I",
                    "保存数据到" + path + f"完成，总时间：{time.time()-st:.3f}",
                    "MainThread.save_data_strict",
                )
                return database

            elif mode == "pickle":
                t = time.time()
                b = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
                Base.log(
                    "I",
                    f"读取内存完成 ({time.time()-t:.3f}s)",
                    "MainThread.save_data_strict",
                )

                t = time.time()
                b2 = base64.b85encode(b)
                Base.log(
                    "I",
                    f"编码完成 ({time.time()-t:.3f}s)",
                    "MainThread.save_data_strict",
                )

                t = time.time()
                b = open(path, "wb")
                b.write(b2)
                b.close()
                Base.log(
                    "I",
                    f"写入文件完成 ({time.time()-t:.3f}s)",
                    "MainThread.save_data_strict",
                )

                Base.log(
                    "I",
                    "保存数据到" + path + f"完成，总时间：{time.time()-st:.3f}",
                    "MainThread.save_data_strict",
                )
                return database

        except (
            Exception
        ) as unused:  # pylint: disable=unused-variable, broad-exception-caught
            Base.log_exc("保存存档" + path + "失败：", "Mainhread.save_data_strict")
            raise

    def save_data(self, path: str = None, mode: Literal["pickle", "sqlite"] = "sqlite"):
        """保存当前存档。

        :param path: 文件路径
        """
        if path is None:
            path = self.save_path
        return self.save_data_strict(
            default_user,
            time.time(),
            CORE_VERSION,
            CORE_VERSION_CODE,
            self.last_reset,
            self.history_data,
            self.classes,
            self.modify_templates,
            self.achievement_templates,
            self.last_start_time,
            self.weekday_record,
            self.current_day_attendance,
            path=path,
            mode=mode,
        )

    @property
    def database(self) -> UserDataBase:
        "返回一个新的数据库对象"
        return UserDataBase(
            self.current_user,
            time.time(),
            CORE_VERSION,
            CORE_VERSION_CODE,
            self.last_reset,
            self.history_data,
            self.classes,
            self.modify_templates,
            self.achievement_templates,
            self.last_start_time,
            self.weekday_record,
            self.current_day_attendance,
        )

    @staticmethod
    def reset_data(
        path: str = os.getcwd() + os.sep + f"chunks/{default_user}/",
        mode: Literal["pickle", "sqlite"] = "sqlite",
    ):
        """
        重置存档。

        :param path: 存档路径
        """
        Base.log("E", "重置数据到" + path + "...", "MainThread.reset_data")
        import shutil

        shutil.rmtree(os.path.join(path, "Histories"), ignore_errors=True)

        ClassObj.save_data_strict(
            default_user,
            time.time(),
            CORE_VERSION,
            CORE_VERSION_CODE,
            time.time(),
            {},
            DEFAULT_CLASSES.copy(),
            DEFAULT_SCORE_TEMPLATES.copy(),
            DEFAULT_ACHIEVEMENTS.copy(),
            time.time(),
            [],
            ClassObj.AttendanceInfo(DEFAULT_CLASS_KEY).copy(),
            path=path,
            mode=mode,
        )

    def stop(self):
        "停止自己"
        Base.log("I", "停止所有侦测器...", "MainThread.stop")
        self.class_obs.stop()
        self.achievement_obs.stop()
        Base.log("I", "保存最后的数据....", "MainThread.stop")
        self.save_data()

    class ObserverError(RuntimeError):
        "侦测器出现错误"

    achievement_obs: "AchievementStatusObserver"
    "成就侦测器"

    class_obs: "ClassStatusObserver"
    "班级侦测器"

    class EditingError(Exception):
        "编辑列表出现错误"

    class TemplateExistsError(EditingError):
        "模板已存在且无法覆盖"

    class TemplateNotExistError(EditingError):
        "模板不存在"

    class ClassNotExistError(EditingError):
        "班级不存在"

    class ClassExistsError(EditingError):
        "班级已存在"

    class StudentExistsError(EditingError):
        "学生已存在"

    class StudentNotExistError(EditingError):
        "学生不存在"

    class EditErrInfo:
        "执行错误信息"

        class FindStudent(enum.IntEnum):
            ClassNotExists = 1
            "班级不存在。"
            StudentNotExists = 2
            "学生不存在。"

        class AddTemplate(enum.IntEnum):
            TargetUnreplaceable = 3
            "尝试覆盖无法覆盖的模板。"
            SystemError = 4
            "系统内部错误。"

        class DeleteTemplate(enum.IntEnum):
            TargetNotExists = 5
            "目标不存在。"
            TargetUnreplaceable = 6
            "目标无法替换。"
            SystemError = 7
            "系统内部错误。"

        class AddClass(enum.IntEnum):
            TargetExists = 8
            "目标已存在。"
            SystemError = 9
            "系统内部错误。"

    def findstu(
        self,
        identifier: Union[int, str],
        from_class: str = DEFAULT_CLASS_KEY,
        *,
        strict: bool = False,
    ) -> Union[Student, int]:
        """
        在from_class中找到一个匹配identifier（可以是学号或者名字）的人

        :param identifier: 学号或者名字
        :param from_class: 班级名
        :return Union[Student, int]: 学生/错误信息
        :raise StudentNotExistError: 没找到
        :raise ClassNotExistError: 班级不存在
        """
        try:
            real_class = self.classes[from_class]
        except KeyError as e:
            if not strict:
                return ClassObj.EditErrInfo.FindStudent.ClassNotExists
            raise ClassObj.ClassNotExistError(f"班级{repr(from_class)}不存在") from e
        if isinstance(identifier, int):
            for k in real_class.students.keys():
                if real_class.students[k].num == identifier:
                    s = real_class.students[k]
                    Base.log(
                        "D",
                        f"寻找到了该学生，信息：来自{real_class.name} "
                        f"(班主任：{real_class.owner})"
                        f"\n{str(s)}".replace("\n", ", "),
                        "MainThread.findstu",
                    )
                    return s
            if not strict:
                return ClassObj.EditErrInfo.FindStudent.StudentNotExists
            raise ClassObj.StudentNotExistError("没有找到指定的学生")
        elif isinstance(identifier, str):
            for k in real_class.students.keys():
                if real_class.students[k].name == identifier:
                    s = real_class.students[k]
                    return s
            if not strict:
                return ClassObj.EditErrInfo.FindStudent.ClassNotExists
            raise ClassObj.StudentNotExistError("没有找到指定的学生")
        raise TypeError("传参错误")

    def student_exists(
        self, identifier: Union[int, str], from_class: str = DEFAULT_CLASS_KEY
    ):
        """
        检测一个学生是否存在

        :param identifier: 学号或者名字
        :param from_class: 班级名
        :return: 是否存在
        :raise ClassNotExistError: 班级不存在
        """
        try:
            self.findstu(identifier, from_class)
            return True
        except ClassObj.EditingError as unused:  # pylint: disable=unused-variable
            return False

    def add_template(
        self,
        key: str,
        title: str,
        value: float,
        description: str,
        reason: str = "创建原因未知",
        *,
        strict: bool = False,
    ) -> Union[ScoreModificationTemplate, int]:
        """
        新建模板。

        :param key: 模板key
        :param title: 模板标题
        :param value: 模板修改值
        :param description: 模板描述
        :param reason: 创建原因
        :return Union[ScoreModificationTemplate, int]: 新建的模板/错误信息
        :raise TemplateExistsError: 模板存在了且无法覆盖（指的是key重复）
        """
        Base.log("I", f"正在新建模板{key}, 原因：{reason}", "MainThread.add_template")

        if key in self.modify_templates.keys():
            Base.log(
                "W", f"尝试覆盖已经存在的模板,key={key!r} :", "MainThread.add_template"
            )
            if self.modify_templates[key].cant_replace:
                Base.log(
                    "E",
                    "尝试覆盖一个无法修改的模板"
                    + (", raise TemplateExistsError" if strict else ""),
                    "MainThread.add_template",
                )
                if not strict:
                    return ClassObj.EditErrInfo.AddTemplate.TargetUnreplaceable
                raise ClassObj.TemplateExistsError(
                    f'模板"{self.modify_templates[key].title}"({key})被设置为无法替换!'
                )
            self.modify_templates[key].title = title
            self.modify_templates[key].mod = value
            self.modify_templates[key].desc = description
            Base.log("I", "覆盖成功", "MainThread.add_template")
            return self.modify_templates[key]
        try:
            self.modify_templates[key] = ClassObj.ScoreModificationTemplate(
                key, value, title, description
            )
            Base.log("I", "新建成功", "MainThread.add_template")
            return self.modify_templates[key]

        except Exception as e:  # pylint: disable=broad-exception-caught
            Base.log_exc("新建模板失败:", "MainThread.add_template")
            if strict:
                raise ClassObj.EditingError(f"新建模板{key!r}失败") from e
            return ClassObj.EditErrInfo.AddTemplate.SystemError

    def del_template(
        self, key: str, reason: str = "删除原因未知", *, strict: bool = False
    ) -> Union[ScoreModificationTemplate, int]:
        """
        删除模板。

        :param key: 模板key
        :param reason: 删除原因
        :return Union[ScoreModificationTemplate, int]:
        被删除的模板/错误信息
        :raise TemplateNotExistError: 模板不存在
        :raise TemplateExistsError: 模板存在了且无法覆盖（指的是key重复）
        """
        Base.log("I", f"正在删除模板{key}, 原因：{reason}", "MainThread.del_template")
        if key not in self.modify_templates.keys():
            Base.log(
                "E" if strict else "W",
                f"模板{key}本就不存在"
                + (", raise TemplateNotExistError" if strict else ""),
                "MainThread.del_template",
            )
            if not strict:
                return ClassObj.EditErrInfo.DeleteTemplate.TargetNotExists
            raise ClassObj.TemplateNotExistError("模版本不存在，无需操作")

        if self.modify_templates[key].cant_replace:
            Base.log(
                "E" if strict else "W",
                "尝试覆盖一个无法修改的模板"
                + (", raise TemplateExistsError" if strict else ""),
                "MainThread.del_template",
            )
            if not strict:
                return ClassObj.EditErrInfo.DeleteTemplate.TargetUnreplaceable
            raise ClassObj.TemplateExistsError(
                f'模板"{self.modify_templates[key].title}"' f"({key})被设置为无法替换!"
            )
        try:
            orig = self.modify_templates[key]
            del self.modify_templates[key]
            Base.log("I", f"模板{key}删除完毕!", "MainThread.del_template")
            return orig

        except (KeyError, RuntimeError) as e:  # pylint: disable=broad-exception-caught
            Base.log_exc("删除模板失败:", "MainThread.del_template")
            if not strict:
                return ClassObj.EditErrInfo.DeleteTemplate.SystemError
            raise ClassObj.EditingError(f"删除模板{key!r}发生错误") from e

    def add_class(
        self,
        key: str,
        name: str,
        owner: str,
        students: Dict[int, Student],
        reason: str = "创建原因未知",
        *,
        strict: bool = False,
    ) -> Union[Class, int]:
        """
        新建班级。

        :param key: 班级key
        :param name: 班级名称
        :param owner: 班主任
        :param students: 学生列表
        :param reason: 创建原因
        :return Union[Class, int]:
        新建的班级/错误信息
        :raise ClassExistsError: 班级已存在
        :raise EditingError: 出现其他错误
        """
        Base.log(
            "I",
            f"正在新建班级{name}(所属老师{owner},标识符{key}), 原因：{reason}",
            "MainThread.add_class",
        )
        if key in self.classes.keys():
            Base.log("E", "指定的班级已存在!", "MainThread.add_class")
            if not strict:
                return ClassObj.EditErrInfo.AddClass.TargetExists
            raise ClassObj.ClassExistsError(f"指定班级{name}已存在! (标识: {key})")

        try:
            self.classes[key] = ClassObj.Class(name, owner, students, key, {})
            Base.log("I", f"班级{name}新建完毕!", "MainThread.add_class")
            return self.classes[key]

        except Exception as e:  # pylint: disable=broad-exception-caught

            Base.log_exc("新建班级失败:", "MainThread.class")
            if not strict:
                return ClassObj.EditErrInfo.AddClass.SystemError
            raise ClassObj.EditingError(f"新建班级失败{key!r}失败") from e

    def del_class(
        self, key: str, reason: str = "删除原因未知", *, strict: bool = False
    ) -> Union[Class, bool]:
        """
        删除班级。

        :param key: 班级key
        :param reason: 删除原因
        :return Union[Class, bool]: 被删除的班级/True(不存在，无需删除)/False(出现错误)
        :raise ClassNotExistError: 班级不存在
        """
        class_orig = self.classes[key]
        Base.log(
            "I", f"正在删除班级(标识符{key}), 原因：{reason}", "MainThread.del_class"
        )

        if key not in self.classes.keys():
            Base.log("E", "指定的班级不存在,无需操作!", "MainThread.del_class")
            if not strict:
                return True
        try:
            del self.classes[key]
            Base.log("I", f"班级{key}删除完毕!", "MainThread.del_class")
            return class_orig
        except Exception as e:  # pylint: disable=broad-exception-caught
            Base.log_exc("新建班级失败:", "MainThread.del_class")
            if not strict:
                return False
            raise ClassObj.EditingError(f"删除班级{key!r}失败") from e

    def add_student(
        self,
        name: str,
        to_class: str,
        num: int,
        init_score: float = 0.0,
        reason: str = "创建原因未知",
        *,
        strict: bool = False,
    ) -> bool:
        """
        新建学生。

        :param name: 学生姓名
        :param to_class: 所属班级
        :param num: 学号
        :param init_score: 初始分数
        :param reason: 创建原因
        :param strict: 是否直接报错
        :return bool: 是否成功
        :raise ClassNotExistError: 指定的班级不存在
        :raise StudentExistsError: 指定的学生已存在
        """
        Base.log(
            "I", f"正在新建学生{name!r}, 原因：{reason!r}", "MainThread.add_student"
        )
        if to_class not in self.classes.keys():
            Base.log("E", "指定的班级不存在!", "MainThread.add_student")
            if not strict:
                return False
            raise ClassObj.ClassNotExistError(f"指定班级{to_class!r}不存在!")
        if num in self.classes[to_class].students:
            Base.log(
                "E",
                f"指定学生{name!r}已存在! (学号{num!r}已占用)",
                "MainThread.add_student",
            )
            if not strict:
                return False
            raise ClassObj.StudentExistsError(
                f"指定学生{name!r}已存在! (学号{num!r}已占用)"
            )
        try:
            self.classes[to_class].students[num] = ClassObj.Student(
                name, num, init_score, to_class, {}
            )
            Base.log("I", f"学生{name}新建完毕!", "MainThread.add_student")
            return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            Base.log_exc("新建学生失败:", "MainThread.add_student")
            if not strict:
                return False
            raise ClassObj.EditingError(f"新建学生{name!r}失败") from e

    def del_student(
        self,
        identifier: Union[str, int],
        from_class: str = DEFAULT_CLASS_KEY,
        reason: str = "删除原因未知",
    ) -> Union[Optional[Student], Exception]:
        """删除学生。

        :param identifier: 学号或姓名
        :param from_class: 所属班级
        :param reason: 删除原因
        :return: 被删除的学生
        :raise Exception: 我也不知道这东西会怎么炸，忘了
        """
        Base.log(
            "I", f"正在删除学生{identifier}, 原因：{reason}", "MainThread.del_student"
        )
        try:
            stuobj = self.findstu(identifier, from_class)
        except ClassObj.EditingError as unused:
            Base.log(
                "W",
                "指定的学生不存在, 无需操作! 信息：" + repr(sys.exc_info()[1]),
                "MainThread.del_student",
            )
            return
        try:
            orig = self.classes[from_class].students[stuobj.num]
            del self.classes[from_class].students[stuobj.num]
            Base.log("I", f"学生{stuobj.name}删除完毕!", "MainThread.del_student")
            return orig
        except KeyError as e:  # pylint: disable=broad-exception-caught
            Base.log_exc("删除学生失败:", "MainThread.del_student")
            raise ClassObj.EditingError(
                f"从{from_class!r}删除学生{identifier!r}失败"
            ) from e

    class SendModifyError(RuntimeError):
        "发送点评出现错误"

    def send_modify(
        self,
        key: str,
        send_to: Union[List[Student], Student],
        extra_title: Optional[str] = None,
        extra_desc: Optional[str] = None,
        extra_mod: Optional[Union[float]] = None,
        info: str = None,
    ) -> Optional[List[ScoreModification]]:
        """发送点评。

        :param key: 模板标识符
        :param send_to: 发送至的学生
        :param extra_title: 额外标题
        :param extra_desc: 额外描述
        :param extra_mod: 额外分数
        :param info: 信息，会记在主界面的侧边栏的ListWidget里
        :return: 发送的所有点评的实例
        :raise SendModifyError: 发送点评出现错误
        """

        if isinstance(send_to, Student):
            send_to = [send_to]

        if send_to is None:
            Base.log("W", "传参为None，疑似初始化，return", "MainThread.send_modify")
            return

        elif send_to == []:
            Base.log("W", "传参为空，疑似初始化，return", "MainThread.send_modify")
            return

        elif send_to == [None]:
            Base.log("W", "传参为[None]，疑似初始化，return", "MainThread.send_modify")
            return

        if key is None:
            Base.log(
                "W", "key为None，疑似模板选择时取消，return", "MainThread.send_modify"
            )
            return

        send_to: List[Student]

        Base.log(
            "I",
            f"开始发送点评\n模板： {self.modify_templates[key].__repr__()}\n"
            f"发送至：\n---------------------",
            "MainThread.send_modify",
        )
        result = []
        succeed: List[ClassObj.ScoreModification] = []

        for stu in send_to:
            a = ClassObj.ScoreModification(
                self.modify_templates[key], stu, extra_title, extra_desc, extra_mod
            )
            success = a.execute()
            if not success:
                for m in succeed:
                    m.retract()
                Base.log(
                    "E",
                    f"---------------------\n发送失败，" f"总数:{len(send_to)}",
                    "MainThread.send_modify",
                )
                raise ClassObj.SendModifyError(f"向学生{stu.name}发送点评出现错误")
            Base.log("I", f"对象 -> {repr(ClassObj.SimpleStudent(stu))}")
            succeed.append(a)
            result.append(a)

        Base.log(
            "I",
            f"---------------------\n发送完成，总数:{len(send_to)}",
            "MainThread.send_modify",
        )
        self.class_obs.opreation_record.push(succeed)
        info_list: List[Tuple[str, Callable]] = []
        index = 0
        for s in succeed:
            info_list.append(
                (
                    f"{s.target.name} {s.temp.title} {s.execute_time.rsplit('.')[0]} {s.mod:+.1f}",
                    lambda s=s, index=index: self.history_window(
                        s, index, None, False, None, False
                    ),
                    (
                        (
                            QColor(202, 255, 222)
                            if s.mod > 0
                            else (
                                QColor(255, 202, 202)
                                if s.mod < 0
                                else QColor(201, 232, 255)
                            )
                        ),
                        (
                            QColor(232, 255, 232)
                            if s.mod > 0
                            else (
                                QColor(255, 232, 232)
                                if s.mod < 0
                                else QColor(233, 244, 255)
                            )
                        ),
                    ),
                )
            )
            index += 1
        self.insert_action_history_info(
            "发送了点评"
            + " "
            + (
                f"成功{len(succeed)}"
                + f" [{succeed[0].target.num}号{'等' if len(succeed) > 1 else ''}] "
                if len(succeed) != 0
                else ""
            )
            + (
                f"失败{len(send_to)-len(succeed)}"
                + f" [{send_to[0].num}号{'等' if len(send_to) > 1 else ''}] "
                if len(send_to) != len(succeed)
                else ""
            )
            + f"<{a.title} {a.mod:.1f}分>"
            + (" " + info if info is not None else ""),
            lambda: self.list_view(
                info_list, "点评记录" + (" " + info if info is not None else "")
            ),
            (127, 225, 195, 224, 255, 255),
        )
        return result.copy()

    def send_modify_instance(
        self,
        modify: Union[List[ScoreModification], ScoreModification],
        info: str = None,
    ) -> Optional[List[ScoreModification]]:
        """
        发送点评。

        :param modify: 点评实例
        :param info: 信息，会记在主界面的侧边栏的ListWidget里
        :return: 发送的点评的实例
        :raise SendModifyError: 发送点评出现错误

        """
        if isinstance(modify, ClassObj.ScoreModification):
            modify = [modify]

        succeed: List[ClassObj.ScoreModification] = []
        for m in modify:
            success = m.execute()
            if not success:
                Base.log(
                    "W",
                    f"发送{m.target.name}的点评失败，已经撤回所有",
                    "MainThread.send_modify_instance",
                )
                for m in succeed:
                    m.retract()
                Base.log(
                    "E",
                    f"---------------------\n发送失败，总数:{len(modify)}",
                    "MainThread.send_modify_instance",
                )

                raise ClassObj.SendModifyError(f"向学生{m.target.name}发送点评出现错误")

            else:
                Base.log(
                    "I",
                    f"发送了{m.target.name}的点评",
                    "MainThread.send_modify_instance",
                )
                succeed.append(m)
            lastest = m

        Base.log(
            "I",
            f"---------------------\n发送完成，总数:{len(modify)}",
            "MainThread.send_modify",
        )
        self.class_obs.opreation_record.push(succeed)
        info_list: List[Tuple[str, Callable]] = []
        index = 0
        for s in succeed:
            info_list.append(
                (
                    f"{s.target.name} {s.temp.title} "
                    f"{s.execute_time.rsplit('.')[0]} {s.mod:+.1f}",
                    lambda s=s, index=index: self.history_window(
                        s, index, None, False, None, False
                    ),
                    (
                        (
                            QColor(202, 255, 222)
                            if s.mod > 0
                            else (
                                QColor(255, 202, 202)
                                if s.mod < 0
                                else QColor(201, 232, 255)
                            )
                        ),
                        (
                            QColor(232, 255, 232)
                            if s.mod > 0
                            else (
                                QColor(255, 232, 232)
                                if s.mod < 0
                                else QColor(233, 244, 255)
                            )
                        ),
                    ),
                )
            )
            index += 1

        self.insert_action_history_info(
            "发送了点评"
            + " "
            + (
                (
                    f"成功{len(succeed)}"
                    + f" [{repr(succeed[0].target.num)}号{'等' if len(succeed) > 1 else ''}] "
                )
                if len(succeed) != 0
                else ""
            )
            + (
                (
                    f"失败{len(modify)-len(succeed)}"
                    + f" [{repr(modify[0].target.num)}号{'等' if len(succeed) > 1 else ''}] "
                )
                if len(modify) != len(succeed)
                else ""
            )
            + (
                "<多项类型可能不一>"
                if len(modify) > 1
                else f"<{lastest.title} {lastest.mod:.1f}分>"
            )
            + (" " + info if info is not None else ""),
            lambda: self.list_view(
                info_list, "点评记录" + (" " + info if info is not None else "")
            ),
            (127, 225, 195, 224, 255, 255),
        )
        return modify.copy()

    def retract_modify(
        self,
        modify: Union[List[ScoreModification], ScoreModification],
        info: str = None,
    ) -> Tuple[bool, str]:
        """撤回点评。

        :param modify: 撤回的点评
        :param info: 信息，会记在主界面的侧边栏的ListWidget里
        :return: None
        """
        if isinstance(modify, ClassObj.ScoreModification):
            modify = [modify]
        if len(modify) == 0:
            Base.log("I", "没有需要撤回的点评", "MainThread.retract_modify")
            return False, "没有需要撤回的点评"

        succeed: List[ClassObj.ScoreModification] = []
        failure: List[ClassObj.ScoreModification] = []
        failure_result: List[str] = []
        return_result = "操作成功完成"
        for m in modify:
            success, result = m.retract()
            if not success:
                Base.log(
                    "W", f"撤回{m.target.name}的点评失败", "MainThread.retract_modify"
                )
                failure.append(m)
                failure_result.append(result)
                return_result = result
            else:
                Base.log(
                    "I", f"撤回了{m.target.name}的点评", "MainThread.retract_modify"
                )
                succeed.append(m)
        index = 0
        info_list = []
        if len(succeed):
            if len(failure):
                info_list += [("撤回成功的...", lambda: None)]
            index += 1
            for s in succeed:
                info_list.append(
                    (
                        f"{s.target.name} {s.temp.title} {s.create_time.rsplit('.')[0]} {s.mod:+.1f}",
                        lambda s=s, index=index: self.history_window(
                            s, index, None, False, None, False
                        ),
                        (
                            (
                                QColor(202, 255, 222)
                                if s.mod > 0
                                else (
                                    QColor(255, 202, 202)
                                    if s.mod < 0
                                    else QColor(201, 232, 255)
                                )
                            ),
                            (
                                QColor(232, 255, 232)
                                if s.mod > 0
                                else (
                                    QColor(255, 232, 232)
                                    if s.mod < 0
                                    else QColor(233, 244, 255)
                                )
                            ),
                        ),
                    )
                )
                index += 1

        if len(failure):
            if len(succeed):
                info_list += [("", lambda: None)]
            info_list += [("撤回失败的...", lambda: None)]
            index += 1
            index_2 = 0
            for f in failure:
                info_list.append(
                    (
                        f"{f.target.name} {f.temp.title} {f.mod:+.1f} ({failure_result[index_2]})",
                        lambda f=f, index=index: self.history_window(
                            f, index, None, False, None, False
                        ),
                        (
                            (
                                QColor(172, 225, 192)
                                if f.mod > 0
                                else (
                                    QColor(225, 172, 172)
                                    if f.mod < 0
                                    else QColor(171, 202, 225)
                                )
                            ),
                            (
                                QColor(202, 225, 202)
                                if f.mod > 0
                                else (
                                    QColor(225, 202, 202)
                                    if f.mod < 0
                                    else QColor(203, 214, 225)
                                )
                            ),
                        ),
                    )
                )
                index += 1
                index_2 += 1

        self.insert_action_history_info(
            "撤回了点评 "
            + (
                f"成功{len(succeed)} "
                f"[{repr(succeed[0].target.num)}号{'等' if len(succeed) > 1 else ''}] "
                if len(succeed)
                else ""
            )
            + (
                f"失败{len(modify)-len(succeed)} "
                f"[{repr(failure[0].target.num)}号{'等' if len(failure) > 1 else ''}] "
                if len(modify) != len(succeed)
                else ""
            )
            + (" " + info if info is not None else ""),
            lambda: self.list_view(
                info_list, "撤回记录" + (" " + info if info is not None else "")
            ),
            (
                (0xEC, 0xC9, 0x7C, 0xF3, 0xF1, 0xA7)
                if len(failure)
                else (127, 192, 245, 224, 234, 255)
            ),
        )

        return len(failure) == 0, (
            ("操作成功完成" if len(succeed) == 1 else "操作全部成功完成")
            if len(failure) == 0
            else (
                ("对于其中一个：" if len(modify) > 1 else "") + return_result
                if len(failure) <= 1
                else f"共{len(failure)}个操作执行失败，请看左上信息栏"
            )
        )

    def retract_lastest(self) -> Tuple[bool, str]:
        """
        撤销上一步操作

        :return Tuple[bool, str]: 是否成功，执行信息
        """
        if self.class_obs.opreation_record.is_empty():
            Base.log("W", "没有可撤回的点评", "MainThread.retract_last")
            return True, "没有需要的点评"

        lastest = self.class_obs.opreation_record.pop()

        Base.log(
            "I",
            "开始撤回点评\n撤回的对象：\n---------------------",
            "MainThread.retract_last",
        )
        for item in lastest:
            item: ClassObj.ScoreModification
            Base.log("I", f" -> {repr(item)}", "MainThread.retract_last")
        result, info = self.retract_modify(lastest, "<一键撤回>")
        Base.log("I", "---------------------\n撤回完成", "MainThread.retract_last")
        return result, info

    def reset_scores(self) -> Dict[str, Class]:
        "结算所有数据"
        history = ClassObj.History(
            copy.deepcopy(self.classes), self.weekday_record, time.time()
        )
        Base.log("W", "正在重置所有班级...", "ClassObjects.reset")

        for _class in self.classes.values():
            _class.reset()

        Base.log("I", "重置完成", "ClassObjects.reset")
        self.insert_action_history_info(
            "分数结算", self.show_all_history, (216, 112, 112, 255, 202, 202), 40
        )
        self.history_data[time.time()] = history
        self.class_obs.opreation_record.clear()
        self.last_reset = time.time()
        self.weekday_record = []
        self.current_day_attendance = ClassObj.AttendanceInfo(self.target_class.key)
        ClassObj.archive_uuid = gen_uuid()
        return self.classes

    def random_choose_stu(
        self,
        count: int = 1,
        from_students: List[Student] = None,
        includes: List[Student] = None,
        excludes: List[Student] = None,
    ) -> Union[List[Student], Student]:
        """随机选择学生

        :param count: 要选择的数量
        :param from_students: 从这些学生中选择
        :param includes: 必须包含的学生
        :param excludes: 必须排除的学生
        :return: 学生列表
        :raises ValueError: 要选择的数量小于1/必选项的长度大于了要选择的数量
        """
        stus = (
            list(from_students)
            if from_students
            else list(self.classes[self.target_class.key].students.values())
        )
        if count < 1:
            raise ValueError(f"要选择的数量 ({count}) 不能小于1")
        if includes is None:
            includes = []
        if excludes is None:
            excludes = []
        if len(includes) > count:
            raise ValueError(
                f"必选项的长度 ({len(includes)}) 大于了要选择的数量 ({count})"
            )
        result = list(includes)
        for _ in range(count - len(includes)):
            while True:
                stu = random.choice(
                    list([s for s in stus if s not in excludes and s not in includes])
                )
                if stu not in result:
                    result.append(stu)
                    break
        result.sort(key=lambda s: s.num)
        return result if len(result) > 1 else result[0]

    @abstractmethod
    def show_all_history(self, history: History = None):
        "展示所有历史记录（接口，没实现）"

    @abstractmethod
    def insert_action_history_info(
        self,
        text: str,
        func: Callable,
        color: Tuple[int, int, int, int],
        stepcount: int = 0,
    ):
        """
        插入一个操作记录

        :param name: 文本
        :param func: 指令
        :param color: 颜色
        :param stepcount: 步数
        """

    @abstractmethod
    def history_window(
        self,
        modify: ScoreModification,
        listbox_index: int,
        listbox_widget=None,
        readonly: bool = False,
        master=None,
        remove_in_listbox_when_retracted=True,
    ):
        """
        展示一个历史记录。

        :param modify: 历史记录对象
        :param listbox_index: 在listbox中的索引
        :param listbox_widget: 所在的listbox
        :param readonly: 是否为只读模式
        :param master: 父窗口
        :param remove_in_listbox_when_retracted: 撤回时在listbox中移除它
        """

    @abstractmethod
    def list_view(
        self,
        data: List[Tuple[str, Callable]],
        title: str,
        master=None,
        commands: List[Tuple[str, Callable]] = None,
    ):
        """
        展示一个列表视图。

        :param data: 数据，格式为[显示信息，回调函数]
        :param title: 列表视图的标题
        :param master: 父窗口
        :param commands: 在列表视图右侧的命令列表，格式为[显示信息，回调函数]
        """

    def on_auto_save_failure(
        self, exc_info: Tuple[Type[BaseException], BaseException, TracebackType]
    ):
        """
        当自动保存失败时执行的操作。

        :param exc_info: 错误信息
        """
        Base.log_exc("自动保存失败", "class_window.auto_save", "W", exc=exc_info)

    def auto_save(self, timeout: int = 60):
        """
        自动保存的执行函数，会阻塞

        timeout:自动保存间隔时间，单位为秒
        """
        self.auto_saving = False
        try:
            while self.class_obs.on_active:
                for _ in range(timeout * 10):
                    if not self.class_obs.on_active:
                        return
                    time.sleep(0.1)
                self.auto_saving = True
                Base.log("I", f"自动保存到{self.save_path}", "class_window.auto_save")

                try:
                    self.save_data(self.save_path)
                    Base.log("I", "自动保存完成", "class_window.auto_save")

                except (
                    Exception
                ) as unused:  # pylint: disable=broad-exception-caught, broad-exception-caught
                    exc_info = sys.exc_info()
                    self.on_auto_save_failure(exc_info)

                self.auto_saving = False

        except (
            Exception
        ) as unused:  # pylint: disable=broad-exception-caught, broad-exception-caught
            Base.log_exc("自动保存因错误而停止", "class_window.auto_save", "W")

    def find_with_uuid(
        self,
        uuid: str,
        find_class: Literal[
            "modify",
            "modify_template",
            "achievement",
            "achievement_template",
            "student",
            "group",
            "any",
        ],
    ) -> Union[
        "ClassObj.ScoreModification",
        "ClassObj.ScoreModificationTemplate",
        "ClassObj.Student",
        "ClassObj.Group",
        "ClassObj.Achievement",
        "ClassObj.AchievementTemplate",
    ]:

        def find_in_modify(uuid: str):
            for _class in self.classes.values():
                for student in _class.students.values():
                    for modify in student.history.values():
                        if modify.uuid == uuid:
                            return modify
            raise ValueError(f"找不到对应的分数记录，uuid: {uuid}")

        def find_in_modify_template(uuid: str):
            for template in self.modify_templates:
                if template.uuid == uuid:
                    return template
            raise ValueError(f"找不到对应的分数模板，uuid: {uuid}")

        def find_in_achievement(uuid: str):
            for _class in self.classes.values():
                for student in _class.students.values():
                    for achievement in student.achievements.values():
                        if achievement.uuid == uuid:
                            return achievement
            raise ValueError(f"找不到对应的成就，uuid: {uuid}")

        def find_in_achievement_template(uuid: str):
            for template in self.achievement_templates.values():
                if template.uuid == uuid:
                    return template
            raise ValueError(f"找不到对应的成就模板，uuid: {uuid}")

        def find_in_student(uuid: str):
            for _class in self.classes.values():
                for student in _class.students.values():
                    if student.uuid == uuid:
                        return student
            raise ValueError(f"找不到对应的学生，uuid: {uuid}")

        def find_in_group(uuid: str):
            for _class in self.classes.values():
                for group in _class.groups.values():
                    if group.uuid == uuid:
                        return group
            raise ValueError(f"找不到对应的小组，uuid: {uuid}")

        if find_class == "modify":
            return find_in_modify(uuid)
        elif find_class == "modify_template":
            return find_in_modify_template(uuid)
        elif find_class == "achievement":
            return find_in_achievement(uuid)
        elif find_class == "achievement_template":
            return find_in_achievement_template(uuid)
        elif find_class == "student":
            return find_in_student(uuid)
        elif find_class == "group":
            return find_in_group(uuid)
        else:
            try:
                return find_in_modify(uuid)
            except ValueError:
                try:
                    return find_in_modify_template(uuid)
                except ValueError:
                    try:
                        return find_in_achievement(uuid)
                    except ValueError:
                        try:
                            return find_in_achievement_template(uuid)
                        except ValueError:
                            try:
                                return find_in_student(uuid)
                            except ValueError:
                                try:
                                    return find_in_group(uuid)
                                except ValueError as e:
                                    raise ValueError(
                                        f"找不到对应的数据，uuid: {uuid}"
                                    ) from e


ClassDataObjType = Union[
    Student,
    Class,
    ScoreModification,
    ScoreModificationTemplate,
    Achievement,
    AchievementTemplate,
    Group,
]


class ClassStatusObserver(Object):
    "班级状态侦测器"

    def __init__(self, base: ClassObj, class_id: str, tps: int = 20):
        """构造一个新的侦测器

        :param base: 班级数据 (self.classes)
        :param class_id: 班级id
        :param templates: 所有的分数修改模板
        """
        try:
            self.on_active: bool = False
            "侦测器是否正在运行"
            self.class_id: str = class_id
            "班级id"
            self.stu_score_ord: dict = {}
            "学生分数排序，不去重"
            self.classes = base.classes
            "班级数据"
            self.target_class = base.classes[self.class_id]
            "目标班级"
            self.templates = base.modify_templates
            "所有的分数修改模板"
            self.opreation_record: Stack[Iterable[ScoreModification]] = Stack()
            "操作记录"
            self.base = base
            "算法基层"
            self.last_update = time.time()
            "上次更新时间"
            self.limited_tps = tps
            "侦测器最大刷新率"
            self.mspt: float = 0
            "侦测器每帧耗时"
            self.tps: float = 0
            "侦测器每秒帧数"
        except (
            KeyError,
            ValueError,
            AttributeError,
            TypeError,
        ) as unused:  # pylint: disable=unused-variable
            Base.log_exc("获取班级信息失败", "ClassStatusObserver.__init__")
            raise ClassObj.ObserverError("获取班级信息失败")

    def _start(self):
        "内部用来启动侦测器的函数"
        if not self.on_active:
            self.on_active = True
            last_frame_time = time.time()
            while self.on_active:
                last_opreate_time = time.time()
                if self.limited_tps:
                    time.sleep(
                        max((1 / self.limited_tps) - (time.time() - last_frame_time), 0)
                    )
                last_frame_time = time.time()
                if time.time() - self.last_update > 1:
                    self.last_update = time.time()
                for k, s in self.target_class.students.items():
                    if s.num != k:
                        orig = s.num
                        s.num = k
                        Base.log(
                            "I",
                            f"学生 {s.name} 的学号已"
                            f"从 {orig} 变为 {s.num}（二者不同步）",
                            "ClassStatusObserver._start",
                        )
                self.stu_score_ord = dict(
                    enumerate(
                        sorted(
                            list(self.classes[self.class_id].students.values()),
                            key=lambda a: a.score,
                        ),
                        start=1,
                    )
                )
                self.mspt = (time.time() - last_frame_time) * 1000
                self.tps = 1 / max((time.time() - last_opreate_time), 0.001)

        else:
            Base.log("I", "已经有存在的侦测线程了，无需再次启动")

    @property
    def student_total_score(self) -> int:
        """班级总分"""
        return self.target_class.student_total_score

    @property
    def student_count(self) -> int:
        """班级人数"""
        return self.target_class.student_count

    @property
    def rank_non_dumplicate(self) -> List[Tuple[int, ClassObj.Student]]:
        """学生分数排序，去重

        至于去重是个什么概念，举个例子
        >>> target_class.rank_non_dumplicate
        [
            (1, Student(name="某个学生", score=114, ...)),
            (2, Student(name="某个学生", score=51,  ...)),
            (2, Student(name="某个学生", score=51,  ...)),
            (4, Student(name="某个学生", score=41,  ...)),
            (5, Student(name="某个学生", score=9,   ...)),
            (5, Student(name="某个学生", score=9,   ...)),
            (7, Student(name="某个学生", score=1,   ...))
        ]"""
        return self.target_class.rank_non_dumplicate

    @property
    def rank_dumplicate(self) -> List[Tuple[int, ClassObj.Student]]:
        """学生分数排序，不去重

        也举个例子
        >>> target_class.rank_non_dumplicate
        [
            (1, Student(name="某个学生", score=114, ...)),
            (2, Student(name="某个学生", score=51,  ...)),
            (3, Student(name="某个学生", score=51,  ...)),
            (4, Student(name="某个学生", score=41,  ...)),
            (5, Student(name="某个学生", score=9,   ...)),
            (6, Student(name="某个学生", score=9,   ...)),
            (7, Student(name="某个学生", score=1,   ...))
        ]"""
        return self.target_class.rank_dumplicate

    def start(self):
        "启动侦测器"
        a = Thread(target=self._start, name="ClassStatusObserverThread", daemon=True)
        a.start()

    def stop(self):
        "停止侦测器"
        self.on_active = False


class AchievementStatusObserver(Object):
    "成就侦测器"

    def __init__(
        self,
        base: ClassObj,
        class_key: str,
        achievement_display: Callable[[str, ClassObj.Student], Any] = None,
        tps: int = 20,
    ):
        """
        构造新的成就侦测器

        :param base_classes: 班级信息
        :param base_templates: 成就模板
        :param class_name: 班级名称
        :param class_obs: 班级信息侦测器（因为不想去各种奇怪的地方获取所以直接传参吧）

        """
        self.on_active: bool = False
        "侦测器是否在运行"
        self.class_id = class_key
        "班级id"
        self.classes = base.classes
        "班级信息（Dict[班级id, Class]）"
        self.achievement_templates = base.achievement_templates
        "成就模板（Dict[成就模板key, 成就模板]）"
        self.class_obs = base.class_obs
        "班级信息侦测器"
        self.display_achievement_queue = Queue()
        "成就显示队列"
        self.achievement_displayer: Callable[[str, ClassObj.Student], Any] = (
            achievement_display
        )
        "成就显示器，传参是一个成就模板的key和一个学生"
        self.class_obs = base.class_obs
        "班级信息侦测器"
        self.last_update = time.time()
        "上次更新时间"
        self.base = base
        "算法基层"
        self.limited_tps = tps
        "侦测器帧率"
        self.mspt = 0
        "侦测器每帧耗时"
        self.overload_ratio = 0.15
        """侦测器过载比例

        当一帧实际耗时大于 (1s/帧率)*过载比例 就视为过载，会减小侦测器tps
        
        设置这个的目的是防止在处理过大数据的时候系统把时间花在计算成就上导致界面卡顿"""
        self.overloaded = False
        "侦测器是否过载"
        self.tps: float = 0
        "侦测器帧率"
        self.total_frame_count = 0
        "运行总帧数"
        self.overload_warning_frame_limit = 2
        "超载警告帧数阈值，连续超载的帧数大于这个数就会有提示"
        self.achievement_displayer = achievement_display or (lambda a, s: None)

    def on_observer_overloaded(
        self,
        last_fr_time: float,  # pylint: disable=unused-argument
        last_op_time: float,  # pylint: disable=unused-argument
        cur_mspt: float,
    ) -> None:
        "侦测器过载时调用"
        Base.log(
            "W",
            "侦测器过载，当前帧耗时：" f"{round(cur_mspt, 3)}" "ms, 将会适当减小tps",
            "AchievementStatusObserver._start",
        )

    def _start(self):
        "内部启动用函数"
        if not self.on_active:
            self.total_frame_count = 0
            self.on_active = True
            t = Thread(
                target=self._display_thread, name="DisplayAchievement", daemon=True
            )
            t.start()
            start_time = time.time()
            last_frame_time = time.time()
            overload_count = 0
            while self.on_active:
                self.total_frame_count += 1
                last_opreate_time = time.time()

                if time.time() - self.last_update > 1:
                    self.last_update = time.time()
                if self.limited_tps:
                    time.sleep(
                        max((1 / self.limited_tps) - (time.time() - last_frame_time), 0)
                    )
                last_frame_time = time.time()
                opreated = False
                # 性能优化点：O(n²)复杂度(?)
                for s in list(self.classes[self.class_id].students.values()):

                    for a in list(self.achievement_templates.keys()):

                        if self.achievement_templates[a].achieved_by(
                            s, self.class_obs
                        ) and (
                            self.achievement_templates[a].key
                            not in [  # 判断成就是否已经达成过
                                a.temp.key
                                for a in self.classes[self.class_id]
                                .students[s.num]
                                .achievements.values()
                            ]
                        ):
                            opreated = True
                            time.sleep(0.1)  # 等待操作完成，避免竞态条件
                            if self.achievement_templates[a].achieved_by(
                                s, self.class_obs
                            ):
                                Base.log(
                                    "I",
                                    f"[{s.name}] 达成了成就 [{self.achievement_templates[a].name}]",
                                )
                                a2 = ClassObj.Achievement(
                                    self.achievement_templates[a], s
                                )
                                a2.give()
                                self.display_achievement_queue.put(
                                    {"achievement": a, "student": s}
                                )

                cur_time = time.time()
                self.mspt = (cur_time - last_frame_time) * 1000
                overload_before = self.overloaded
                if not opreated:  # 只在空扫描的时候才检测是否过载
                    if self.mspt > 1000 / self.limited_tps * self.overload_ratio:
                        self.overloaded = True
                        overload_count += 1
                    else:
                        self.overloaded = False
                        overload_count = 0
                    if (
                        self.overloaded
                        and overload_count > self.overload_warning_frame_limit
                        and (cur_time - start_time) > 1
                        and not overload_before
                    ):
                        # 刚才才开始过载并且已经开了有一段时间了
                        self.on_observer_overloaded(
                            last_frame_time, last_opreate_time, self.mspt
                        )
                    time.sleep((self.mspt * (1 / self.overload_ratio)) / 1000)
                self.tps = 1 / max((time.time() - last_opreate_time), 0.001)

        else:
            Base.log("I", "已经有存在的侦测线程了，无需再次启动")

    def _display_thread(self):
        "显示成就的线程"
        while self.on_active:
            try:
                if not self.display_achievement_queue.empty():
                    item = self.display_achievement_queue.get()
                    self.achievement_displayer(item["achievement"], item["student"])
                time.sleep(0.1)  # 每一行代码都有它存在的意义，不信删了试试
            except Exception as e:  # pylint: disable=broad-exception-caught
                Base.log(
                    "E",
                    f"成就显示线程出错: [{sys.exc_info()[1].__class__.__name__}]{e}",
                )
                break

    def start(self):
        "启动侦测器"
        a = Thread(target=self._start, name="AchievementObserverThread", daemon=True)
        a.start()

    def stop(self):
        "停止侦测器"
        self.on_active = False
