from __future__ import annotations

from collections import OrderedDict
import time
import uuid
from typing import TYPE_CHECKING, TypeVar
from uuid import UUID

from utils.basetypes import Object

from .basetype import ClassDataType, ClassDataTypeUUID
from .objects import *

if TYPE_CHECKING:
    from .default import *
    # 这里先别导入，不然会循环
    # （default依赖于objects，objects依赖于observers，observers又依赖于default）
    # 不过最后还是会导入的，放心


default_user = "default"


current_archive_uuid: UUID | None = None
"当前存档的UUID，全局的"



UUIDDataType = TypeVar("UUIDDataType", bound=ClassDataType)


class ClassDataLoader:
    class OperationalError(RuntimeError):
        "操作错误。"

    class ObserverError(RuntimeError):
        "侦测器错误。"

    class UUIDLoaderNotSet(OperationalError):
        "没有设置UUID加载器。"

    @staticmethod
    def LoadUUID(uuid: ClassDataTypeUUID[UUIDDataType] | None, type: type[UUIDDataType]) -> UUIDDataType | None:
        "以一个ClassDataTypeUUID加载数据类型。"
        raise ClassDataLoader.UUIDLoaderNotSet \
                ("ClassDataLoader.LoadUUID在没有被设置的时候被调用了") 
                # 防止我自己看不懂这个信息

    @staticmethod
    def get_archive_uuid():
        "获取当前存档的UUID。"
        global current_archive_uuid
        if current_archive_uuid is None:
            current_archive_uuid = uuid.uuid4()
        return current_archive_uuid

    @staticmethod
    def set_archive_uuid(value: UUID):
        "设置当前存档的UUID。"
        global current_archive_uuid
        current_archive_uuid = value



class UserDataBase(Object):
  "用户数据库"

  def __init__(
    self,
    user: str | None = None,
    save_time: float | None = None,
    version: str | None = None,
    version_code: int | None = None,
    last_reset: float | None = None,
    history_data: dict[float, History] | None = None,
    classes: dict[str, Class] | None = None,
    templates: OrderedDict[str, ScoreModificationTemplate] | dict[str, ScoreModificationTemplate] | None = None,
    achievements: dict[str, AchievementTemplate] | None = None,
    last_start_time: float | None = None,
    weekday_record: dict[str, dict[float, DayRecord]] | None = None,
    current_day_attendance: dict[str, AttendanceInfo] | None = None,
  ):
    """
    构建一个数据库对象。

    :param user: 用户名
    :param save_time: 保存时间
    :param version: 算法核心版本
    :param version_code: 算法核心版本号
    :param last_reset: 上次重置时间戳
    :param history_data: 历史数据
    :param classes: 当前班级列表
    :param templates: 当前分数模板
    :param achievements: 当前成就模板
    :param last_start_time: 上次启动时间
    :param weekday_record: 每周出勤记录
    :param current_day_attendance: 每个班级的今日出勤状况
    """
    self.loaded = False
    self.user = user or "unknown"
    self.save_time = save_time or time.time()
    self.version = version or "unknown"
    self.version_code = version_code or 0
    self.last_reset = last_reset or time.time()
    self.history_data = history_data or {}
    self.classes = classes or {}
    self.templates = OrderedDict(templates or {})
    self.achievements = achievements or {}
    self.last_start_time = last_start_time or time.time()
    self.weekday_record = weekday_record or {}
    self.current_day_attendance = current_day_attendance or {}
    self.loaded = user is not None  # 任一参数非空即视为已加载

  def set(
    self,
    user: str | None = None,
    save_time: float | None = None,
    version: str | None = None,
    version_code: int | None = None,
    last_reset: float | None = None,
    history_data: dict[float, History] | None = None,
    classes: dict[str, Class] | None = None,
    templates: OrderedDict[str, ScoreModificationTemplate] | dict[str, ScoreModificationTemplate] | None = None,
    achievements: dict[str, AchievementTemplate] | None = None,
    last_start_time: float | None = None,
    weekday_record: dict[str, dict[float, DayRecord]] | None = None,
    current_day_attendance: dict[str, AttendanceInfo] | None = None,
  ):
    """
    构建一个数据库对象。

    :param user: 用户名
    :param save_time: 保存时间
    :param version: 算法核心版本
    :param version_code: 算法核心版本号
    :param last_reset: 上次重置时间戳
    :param history_data: 历史数据
    :param class: 当前班级列表
    :param templates: 当前分数模板
    :param achievements: 当前成就模板
    :param last_start_time: 上次启动时间
    :param current_day_attendance: 今日出勤状况
    """
    self.user = user or "unknown"
    self.save_time = save_time or time.time()
    self.version = version or "unknown"
    self.version_code = version_code or 0
    self.last_reset = last_reset or time.time()
    self.history_data = history_data or {}
    self.classes = classes or {}
    self.templates = OrderedDict(templates or {})
    self.achievements = achievements or {}
    self.last_start_time = last_start_time or time.time()
    self.weekday_record = weekday_record or {}
    self.current_day_attendance = current_day_attendance or {}
    self.loaded = user is not None  # 任一参数非空即视为已加载

  def __contains__(self, key: str) -> bool:
    return key in self.__dict__ and self.__dict__[key] is not None and self.__dict__[key] is not None

