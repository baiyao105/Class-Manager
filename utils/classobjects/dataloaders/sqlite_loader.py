"""
数据加载模块
"""
from __future__ import annotations

# 神人类型检查一夜之间又给我报了一堆错
# 关键是他没解析到DataProperty（后面用来写触发式更新）的返回值
# 然后给我报一堆 "(某成员名) 不是 DataObject 的成员"
# 关键是一个星期前还没这个问题
# 而且它解析不到 if not object ... 的判None语法

# 然后就给我报了一堆

# 无法将"Student | None"类型的参数分配给函数"append"中类型为"Student"的参数"object"
#   类型"Student | None"不可分配给类型"Student"
#     "None"不可分配给"Student"

# 密码的我改了几个小时的注释啊
# 另外, 因为看着太难受了我给空格缩进改成两格了

# JustNothing只是用了继承property的一个自己写的类做类成员
# 就被Pylance的类型检查打断了双腿

import json
import math
import os
import shutil
import sqlite3
import sys
import time
import uuid
from collections import OrderedDict
from collections.abc import Iterable
from typing import Any, Dict, Optional, TypeVar, Union

from ...algorithm import Mutex
from ...basetypes import Base
from ...classobjects import *
from ...consts import runtime_flags
from ...functions.prompts import question_yes_no

from ..basetype import ClassDataType, ClassDataTypeUUID, StringObjectDataKind
from ..classdataloader import *
from ..datachunk import DataChunk


BaseDataType = Union[int, float, bool, str]

class LoaderError(RuntimeError):
  "加载器出现错误"

class UserCanceledError(LoaderError):
  "用户取消加载"

class ObjectDataNotFoundError(LoaderError):
  "数据在存档中不存在"

class IdentifierDumplicatedError(LoaderError):
  "UUID重复了"


class DataObject:
  "数据对象"

  loaded_objects = 0
  "加载了的对象数量"

  saved_objects = 0
  "保存了的对象数量"

  cur_list: dict[str, sqlite3.Cursor] = {}
  "连接列表，conn_list[数据类型名称]=光标"

  save_task_running = False
  "保存任务是否正在运行"

  loaded_object_list: dict[
    tuple[ClassDataTypeUUID[History] | None, str, ClassDataTypeUUID[ClassDataType]], ClassDataType
  ] = {}
  "加载目标列表"

  load_tasks: list[tuple[ClassDataTypeUUID[History] | None, str, ClassDataTypeUUID[Any]]] = []
  "加载任务列表"

  @staticmethod
  def clear_tasks():
    "清空加载任务列表"
    DataObject.load_tasks.clear()

  @staticmethod
  def clear_loaded_objects():
    "清空加载对象列表"
    DataObject.loaded_object_list.clear()

  @staticmethod
  def commit_changes(clear_chunk_connections: bool = True):
    "释放所有连接并保存更改."
    for cur in DataObject.cur_list.values():
      try:
        cur.close()
        cur.connection.commit()
        cur.connection.close()
      except sqlite3.Error:
        pass
    DataObject.cur_list.clear()
    if clear_chunk_connections:
      Chunk.commit_changes(False)
    DataObject.save_task_running = False

  def __init__(
    self,
    data: ClassDataType,
    chunk: "Chunk",
  ):
    self.object = data
    self.chunk = chunk

  @staticmethod
  def static_save(obj: ClassDataType, chunk: "Chunk", path: str | None = None) -> ClassDataType:
    path = path or chunk.get_current_save_dir()
    dobj = DataObject(obj, chunk)
    dobj.save(path)
    return obj

  def save(self, path: str | None = None, max_retry: int = 3):
    "在数据分组中保存这个对象。"
    DataObject.save_task_running = True
    uuid = self.object.uuid
    assert uuid is not None, "无法保存uuid为None的对象，是不是把不应该保存的History也传进来了？"
    string = self.object.to_string()
    if isinstance(self.object, TagSigned):
      for tag in self.object.tags:
        DataObject.static_save(tag, self.chunk)

    type_name = self.object.chunk_type_name
    path = path or self.chunk.path
    conn: Optional[sqlite3.Connection] = None
    while max_retry:
      max_retry -= 1
      if type_name not in self.cur_list:
        conn = sqlite3.connect(os.path.join(path, f"{type_name}.db"), check_same_thread=False)
        cur = conn.cursor()
        for i in range(16):
          prefix = f"{i:01x}"
          cur.execute(
            f"""CREATE TABLE IF NOT EXISTS datas_{prefix} (
                    uuid   text     primary key,  -- 数据UUID
                    class  text,                  -- 数据类型
                    data   text                   -- 数据
            )"""
          )
        conn.commit()
        conn.close()
        conn = sqlite3.connect(os.path.join(path, f"{type_name}.db"), check_same_thread=False)  # 重新连接
        self.cur_list[type_name] = conn.cursor()

      cursor = self.cur_list[type_name]

      for i in range(3):
        try:
          cursor.execute(f"SELECT class FROM datas_{uuid[:1]} WHERE uuid = ?", (str(uuid),))
          existing_class = cursor.fetchone()

          if existing_class:
            if existing_class[0] == type_name:
              cursor.execute(
                f"""
                UPDATE datas_{uuid[:1]}
                SET class = ?, data = ?
                WHERE uuid = ?
                """,
                (
                  type_name,
                  string,
                  str(uuid),
                ),
              )
            else:
              raise IdentifierDumplicatedError(
                f"对于uuid={uuid!r}的对象，数据库中已经存在一个不同类型的对象！"
                f"（当前为{type_name!r}，数据库中为{existing_class[0]!r}）\n"
                "如果你看见了这个错误，你可能碰见了"
                "1/340282366920938463463374607431768211456的概率"
                "（不知道该恭喜你还是感到遗憾）"
              )
          else:
            cursor.execute(
              f"""
              INSERT INTO datas_{uuid[:1]} (uuid, class, data)
              VALUES (?, ?, ?)
              """,
              (str(uuid), type_name, string),
            )

          DataObject.saved_objects += 1
          return
        except sqlite3.Error as e:
          Base.log_exc_short(
            f"处理数据出现错误，对象：{self.object.__class__.__name__}({self.object.uuid})，0.1秒后重试",
            "DataObject.save",
            "W",
            exc=e
          )
          try:
            if conn: conn.rollback()
          except sqlite3.Error:
            self.commit_changes()
            Base.log("W", "操作回滚失败，已重置所有连接，将会重试", "DataObject.save")
          time.sleep(0.1)
          continue
      Base.log_exc(
        f"处理数据时出现错误，对象：{self.object!r}，重试3次后仍然失败；已重置所有连接，将会重试",
        "DataObject.save", "E")
      self.commit_changes()


_LT = TypeVar("_LT")


def spilt_list(
  lst: Iterable[_LT],
  slices: int,
  max_size: int | None = None,
  min_size: int | None = None,
) -> list[list[_LT]]:
  """
  将列表按指定数量分组。

  :param lst: 列表
  :param slices: 分组数量
  :param max_size: 最大分组大小
  :param min_size: 最小分组大小
  :return: 分组后的列表
  """
  lst = list(lst)
  size = math.ceil(len(lst) / slices)
  if max_size is not None:
    size = min(size, max_size)
  if min_size is not None:
    size = max(size, min_size)
  result: list[list[_LT]] = []
  while len(lst) > 0:
    result.append(lst[:size])
    lst = lst[size:]
  return result


_DT = TypeVar("_DT", bound=ClassDataType)


class Chunk(DataChunk):
  """
  数据分组.

  绑定一个UserDataBase, 并对这个UserDataBase进行数据存储和读取操作.

  当然也可以利用这里面的一些函数实现自定义的数据存储和读取.
  """

  database_connections: dict[tuple[ClassDataTypeUUID[History] | None, str], sqlite3.Connection] = {}
  "数据库连接池，database_connection[(历史记录uuid,数据类型名)] = sqlite3.Connection"

  save_task_mutex: Mutex = Mutex()
  "保存任务互斥锁"

  def __init__(self, path: str, bound_database: UserDataBase | None = None):
    self.path = path
    self.bound_db = bound_database or UserDataBase()
    self.is_saving = False
    self.operating_history_uuid: ClassDataTypeUUID[History] | None = None
    "正在操作的存档UUID，None表示为当前存档"
    os.makedirs(
      self.path if not path.endswith(".datas") else os.path.dirname(self.path),
      exist_ok=True,
    )

  @staticmethod
  def get_chunk(path: str, database: UserDataBase) -> Chunk:
    """
    获取Chunk对象。

    :param path: 数据存储路径
    :param database: 绑定的数据库对象
    :return: Chunk对象
    """
    return Chunk(path, database)

  def load_object(
    self,
    uuid: ClassDataTypeUUID[_DT],
    data_type: type[_DT],
  ) -> _DT | None:
    """
    加载单个对象。

    :param uuid: 对象UUID
    :param data_type: 对象类型
    :return: 加载的对象，不存在则返回None
    """
    return ClassDataLoader.LoadUUID(uuid, data_type)

  def save_object(self, obj: ClassDataType) -> None:
    """
    保存单个对象。

    :param obj: 要保存的对象
    """
    DataObject(obj, self).save(self.get_current_save_dir())

  def create_history(self) -> ClassDataTypeUUID[History]:
    """
    创建历史记录存档。

    :return: 新创建的历史记录UUID
    """
    history = History(self.bound_db.classes, self.bound_db.weekday_record)
    self._save_history_internal(history)
    if history.uuid is None:
      raise LoaderError("历史记录UUID不能为None")
    return history.uuid

  def _save_history_internal(self, history: History) -> None:
    """
    内部方法：保存历史记录。

    :param history: 历史记录对象
    """
    if history.uuid is None:
      return
    history_path = os.path.join(self.path, "Histories", str(history.uuid)[:2], str(history.uuid)[2:])
    os.makedirs(history_path, exist_ok=True)
    info = {
      "uuid": str(history.uuid),
      "create_time": history.time,
      "save_time": self.bound_db.save_time,
    }
    with open(os.path.join(history_path, "info.json"), "w", encoding="utf-8") as f:
      json.dump(info, f, ensure_ascii=False, indent=2)

  def list_histories(self) -> list[ClassDataTypeUUID[History]]:
    """
    列出所有历史记录。

    :return: 历史记录UUID列表
    """
    histories_dir = os.path.join(self.path, "Histories")
    if not os.path.isdir(histories_dir):
      return []

    results: list[ClassDataTypeUUID[History]] = []
    for prefix_dir in os.listdir(histories_dir):
      prefix_path = os.path.join(histories_dir, prefix_dir)
      if not os.path.isdir(prefix_path) or len(prefix_dir) != 2:
        continue

      for history_dir in os.listdir(prefix_path):
        history_path = os.path.join(prefix_path, history_dir)
        info_path = os.path.join(history_path, "info.json")
        if not os.path.isdir(history_path):
          continue

        if os.path.isfile(info_path):
          try:
            with open(info_path, encoding="utf-8") as f:
              info = json.load(f)
            uuid_str = info.get("uuid", prefix_dir + history_dir)
            results.append(ClassDataTypeUUID(History, uuid.UUID(uuid_str)))
          except (json.JSONDecodeError, OSError, ValueError):
            try:
              results.append(ClassDataTypeUUID(History, uuid.UUID(prefix_dir + history_dir)))
            except ValueError:
              continue

    return results

  def close_connections(self) -> None:
    """
    关闭所有数据库连接。
    """
    for conn in self.database_connections.values():
      try:
        conn.commit()
        conn.close()
      except sqlite3.Error:
        pass
    self.database_connections.clear()

  def get_object_rdata(
    self,
    history_uuid: ClassDataTypeUUID[History] | None,
    uuid: ClassDataTypeUUID[_DT],
    data_type: str,
  ) -> StringObjectDataKind[_DT]:
    """
    获取对象数据。

    :param history_uuid: 历史记录uuid，None为此周（还未重置的存档）
    :param uuid: 对象uuid
    :param data_type: 数据类型名
    :return: 对象数据
    :raise ObjectDataNotFoundError: 数据不存在
    """
    try:
      conn = self.database_connections[(history_uuid, data_type)]
    except KeyError:
      conn = sqlite3.connect(os.path.join(self.path, f"{data_type}.db"), check_same_thread=False)
      self.database_connections[(history_uuid, data_type)] = conn
    result = conn.execute(f"SELECT data FROM datas_{uuid[:1]} WHERE uuid = ?", (str(uuid),)).fetchone()
    if result is None:
      raise ObjectDataNotFoundError("数据不存在")
    return result[0]
  
  def get_current_save_dir(self):
    "根据当前的操作uuid获取数据库的存储路径。"
    history_uuid = self.operating_history_uuid
    if history_uuid is None:
      path = os.path.join(self.path, "Current")
    else:
      path = os.path.join(self.path, "Histories", history_uuid[:2], history_uuid[2:])
    return path
  
  def set_uuid_loader(self, history_uuid: ClassDataTypeUUID[History] | None):
    """
    设置uuid加载器。

    :param uuid: uuid
    """
    self.operating_history_uuid = history_uuid
    if history_uuid is None:
      path = os.path.join(self.path, "Current")
    else:
      path = os.path.join(self.path, "Histories", history_uuid[:2], history_uuid[2:])
    def _load_object(
      uuid: ClassDataTypeUUID[ClassDataType] | None,
      data_type: type[ClassDataType],
      history_uuid: ClassDataTypeUUID[History] | None = history_uuid,
    ) -> ClassDataType | None:
      "加载对象"
      if DataObject.save_task_running:
        Base.log("W", "正在保存数据，将会结束当前保存数据的会话", "Chunk.load_history._load_object")
        DataObject.commit_changes()
      DataObject.loaded_objects += 1

      if uuid is None:
        if "noticed_uuid_is_none" not in runtime_flags:
          Base.log("W", "加载时遇到uuid为None，将会返回None", "Chunk.load_history._load_object")
          call_fr = sys._getframe(2) # pyright: ignore[reportPrivateUsage]
          Base.log(
            "W",
            f"调用者：{call_fr.f_code.co_name}({call_fr.f_code.co_filename}:{call_fr.f_lineno})",
            "Chunk.load_history._load_object",
          )
          runtime_flags["noticed_uuid_is_none"] = True

          if runtime_flags["noticed_uuid_is_none"]:
            Base.log("W", "将不会再次展示此警告", "Chunk.load_history._load_object")
        return None

      _id = (history_uuid, data_type.chunk_type_name, uuid)

      DataObject.load_tasks.append(_id)
      try:
        # 尝试直接从缓存中获取
        obj = DataObject.loaded_object_list[_id]
        DataObject.load_tasks.remove(_id)
        return obj

      except KeyError:
        # 如果不存在的话就从数据库读取
        try:
          # 从连接池获取连接
          conn = self.database_connections[(history_uuid, data_type.chunk_type_name)]
        except KeyError:
          # 如果没连接就直接开一个新的连接放连接池，不用反复开开关关的节约性能
          # （加载完记得relase_connections，清理内存）
          conn = sqlite3.connect(
            os.path.join(path, f"{data_type.chunk_type_name}.db"),
            check_same_thread=False,
          )

          self.database_connections[(history_uuid, data_type.chunk_type_name)] = conn

        try:
          result = conn.execute(f"SELECT data FROM datas_{uuid[:1]} WHERE uuid = ?", (str(uuid),)).fetchone()
        except sqlite3.Error:
          Base.log(
            "W",
            f"数据不存在，将会返回默认\n数据：{data_type.__qualname__}({uuid})",
            "Chunk.load_history",
          )
          DataObject.load_tasks.remove(_id)
          self.last_failures.append(_id)
          obj = data_type.new_dummy()
          obj.archive_uuid = _id[0]
          obj.uuid = _id[2]
          return obj

        if result is None:
          Base.log(
            "W",
            f"数据不存在，将会返回默认\n数据：{data_type.__qualname__}({uuid})",
            "Chunk.load_history",
          )
          DataObject.load_tasks.remove(_id)
          self.last_failures.append(_id)
          obj = data_type.new_dummy()
          obj.archive_uuid = _id[0]
          obj.uuid = _id[2]
          return obj

        obj_shallow_loaded = data_type.new_dummy()
        # 先浅层加载一下，防止触发无限递归
        DataObject.loaded_object_list[_id] = obj_shallow_loaded
        # 再深层处理，这样就不用担心了
        DataObject.loaded_object_list[_id].inst_from_string(result[0])
        obj = DataObject.loaded_object_list[_id]
        DataObject.load_tasks.remove(_id)
        return obj

    ClassDataLoader.LoadUUID = lambda uuid, type: _load_object(uuid, type)

  def load_history(
    self,
    history_uuid: ClassDataTypeUUID[History] | None = None,
    request_uuid: uuid.UUID | None = None,
  ) -> History:
    """
    加载历史记录。

    :param history_uuid: 历史记录uuid
    :param request_uuid: 请求uuid，只是用来做数据加载的标识的
    :return: 历史记录
    :raise FileNotFoundError: 历史记录不存在
    :raise UserCanceledError: 用户取消加载
    """
    self.last_failures: list[tuple[ClassDataTypeUUID[History] | None, str, ClassDataTypeUUID[ClassDataType]]] = []
    start_time = time.time()
    start_obj = DataObject.loaded_objects

    
    if history_uuid is None:
      path = os.path.join(self.path, "Current")
    else:
      path = os.path.join(self.path, "Histories", history_uuid[:2], history_uuid[2:])
    if not os.path.isdir(path):
      raise FileNotFoundError("历史记录不存在")
    
    self.set_uuid_loader(history_uuid)

    info = json.load(open(os.path.join(path, "info.json"), encoding="utf-8"))
    if "python_version" in info:
      data_python_ver = info["python_version"]
      current_ver = [
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
      ]
      if data_python_ver != current_ver:
        if "noticed_version_changed" not in runtime_flags:
          runtime_flags["noticed_version_changed"] = set()
        if request_uuid is not None and request_uuid not in runtime_flags["noticed_version_changed"]:
          Base.log(
            "W",
            f"历史记录的Python版本为{data_python_ver}，当前版本为{current_ver}，可能存在兼容性问题",
          )
          if not question_yes_no(
            None,
            "警告",
            f"检测到存档的Python版本({data_python_ver[0]}.{data_python_ver[1]}.{data_python_ver[2]})"
            f"与当前版本({current_ver[0]}.{current_ver[1]}.{current_ver[2]})不一致，\n"
            "如果继续加载，可能导致加载存档失败甚至闪退。\n"
            "是否继续加载数据？",
          ):
            raise UserCanceledError("用户取消加载")
          runtime_flags["noticed_version_changed"].add(request_uuid)  # type: ignore

    else:
      Base.log(
        "W",
        "历史记录的Python版本信息缺失，可能存在兼容性问题",
        "Chunk.load_history",
      )
    class_uuids: list[tuple[str, ClassDataTypeUUID[Class]]] = json.load(
      open(os.path.join(path, "classes.json"), encoding="utf-8")
    )

    weekday_uuids: dict[str, dict[float, ClassDataTypeUUID[DayRecord]]] = json.load(
      open(os.path.join(path, "weekdays.json"), encoding="utf-8")
    )

    # index = 0
    # for item in weekday_uuids:
    #   if len(item) <= 2:
    #     weekday_uuids[index] = [DEFAULT_CLASS_KEY, *item]
    #   index += 1

    classes: Dict[str, Class] = {}
    for _, class_uuid in class_uuids:
      _class: Class | None = ClassDataLoader.LoadUUID(class_uuid, Class)
      assert _class is not None, f"班级{class_uuid}加载失败"
      classes[_class.key] = _class

    for target_class, item in weekday_uuids.items():
      for _time_key, weekday_uuid in item.items():
        weekday: DayRecord | None = ClassDataLoader.LoadUUID(weekday_uuid, DayRecord)
        if target_class not in self.bound_db.weekday_record:
          self.bound_db.weekday_record[target_class] = {}
        assert weekday is not None, f"星期{_time_key}的记录{weekday_uuid}加载失败"
        self.bound_db.weekday_record[target_class][weekday.utc] = weekday

    history = History(
      classes,
      self.bound_db.weekday_record,
      json.load(open(os.path.join(path, "info.json"), encoding="utf-8"))["create_time"],
    )

    history.uuid = history_uuid
    history.archive_uuid = history_uuid

    total_time = time.time() - start_time
    total_obj = DataObject.loaded_objects - start_obj
    Base.log(
      "I",
      f"历史记录{history_uuid}加载完成，总数据处理数：{total_obj}, 警告数量：{len(self.last_failures)}, 耗时：{total_time:.3f}s, 平均速度：{total_obj / max(total_time, 0.001):.3f}个/秒",
    )
    return history

  def del_history(self, history_uuid: ClassDataTypeUUID[History]) -> bool:
    """
    删除历史记录
    """
    try:
      shutil.rmtree(os.path.join(self.path, "Histories", history_uuid[:2], history_uuid[2:]))
      return True
    except OSError:  # pylint: disable=broad-exception-caught
      return False

  def load_data(self, load_all: bool = False) -> UserDataBase:
    """
    加载数据。

    :return: 对象数据
    :param load_all: 是否加载所有数据
    """
    req_uuid = uuid.uuid4()
    current_record = self.load_history(None, req_uuid)

    templates: list[ScoreModificationTemplate] = []
    achievements: list[AchievementTemplate] = []
    current_day_attendance: dict[str, AttendanceInfo] = {}

    # 有个细节，这里的LoadUUID是刚刚加载完这周的，所以不用填默认参数
    template_uuids: list[tuple[str, ClassDataTypeUUID[ScoreModificationTemplate]]] = json.load(
      open(
        os.path.join(self.path, "Current", "templates.json"),
        encoding="utf-8",
      )
    )

    for _, template_uuid in template_uuids:
      template = ClassDataLoader.LoadUUID(template_uuid, ScoreModificationTemplate)
      assert template is not None, f"模板{template_uuid}加载失败"
      templates.append(template)

    achievement_uuids: list[tuple[str, ClassDataTypeUUID[AchievementTemplate]]] = json.load(
      open(
        os.path.join(self.path, "Current", "achievements.json"),
        encoding="utf-8",
      )
    )
    for _, achievement_uuid in achievement_uuids:
      achievement = ClassDataLoader.LoadUUID(achievement_uuid, AchievementTemplate)
      assert achievement is not None, f"成就{achievement_uuid}加载失败"
      achievements.append(achievement)


    current_day_attendance_uuids: list[tuple[str, ClassDataTypeUUID[AttendanceInfo]]] = json.load(
      open(
        os.path.join(self.path, "Current", "current_day_attendance.json"),
        encoding="utf-8",
      )
    )
    for target_class, history_uuid in current_day_attendance_uuids:
      attendance = ClassDataLoader.LoadUUID(history_uuid, AttendanceInfo)
      assert attendance is not None, f"出勤记录{history_uuid}加载失败"
      current_day_attendance[target_class] = attendance

    info = json.load(open(os.path.join(self.path, "info.json"), encoding="utf-8"))
    self.bound_db.save_time = info["save_time"]
    self.bound_db.version = info["version"]
    self.bound_db.version_code = info["version_code"]
    self.bound_db.last_reset = info["last_reset"]
    self.bound_db.last_start_time = info["last_start_time"]
    histories: dict[float, History] = {}
    if load_all:
      for history_uuid in info["histories"]:
        try:
          h = self.load_history(history_uuid, req_uuid)
          while h.time in histories:
            h.time += 0.000001 # 这个是真没招了
          histories[h.time] = h
        except Exception as e:  # pylint: disable=broad-exception-caught
          Base.log_exc(f"历史记录{history_uuid}加载失败，将跳过", "Chunk.load_data", "W", e)
          continue

      h2 = sorted(histories.items(), key=lambda i: i[0])
      histories = dict(h2)
    
    
    return UserDataBase(
      info["user"],
      info["save_time"],
      info["version"],
      info["version_code"],
      info["last_reset"],
      histories,
      current_record.classes,
      OrderedDict({t.key: t for t in templates}),
      {a.key: a for a in achievements},
      info["last_start_time"],
      current_record.weekdays,
      current_day_attendance,
    )


  @staticmethod
  def commit_changes(clear_dataobj_connections: bool = True) -> None:
    """
    释放所有连接并保存更改。
    """
    for v in Chunk.database_connections.values():
      v.commit()
      v.close()
    Chunk.database_connections.clear()
    if clear_dataobj_connections:
      DataObject.commit_changes(False)

  def save_data(
    self,
    save_history: bool = True,
    save_only_if_not_exist: bool = True,
    clear_current: bool = False,
    clear_histories: bool = False,
  ) -> None:
    """
    保存数据。

    :param save_history: 是否保存历史记录
    :param save_only_if_not_exist: 是否只保存不存在的数据
    :param clear_current: 是否清理当前数据
    :param clear_histories: 是否清理历史数据
    """
    with Chunk.save_task_mutex:
      DataObject.commit_changes(False)
      Chunk.reset_progress()

      try:
        if self.is_saving:
          Base.log("W", "当前分块正在处理数据", "Chunk.save")
        self.is_saving = True
        Base.log("I", "开始保存数据", "Chunk.save")
        if clear_histories:
          shutil.rmtree(self.path, ignore_errors=True)
        os.makedirs(self.path, exist_ok=True)
        os.makedirs(os.path.join(self.path, "Histories"), exist_ok=True)
        history = History(self.bound_db.classes, self.bound_db.weekday_record)
        save_tasks: list[tuple[ClassDataTypeUUID[History] | None, History, bool]] = [
          (None, history, clear_current)
        ]
        if save_history:
          for v in self.bound_db.history_data.values():
            if save_only_if_not_exist:
              if not os.path.isfile(
                os.path.join(
                  self.path,
                  "Histories",
                  str(v.uuid)[:2],
                  str(v.uuid)[2:],
                  "info.json",
                )
              ):
                os.makedirs(
                  os.path.join(self.path, "Histories", str(v.uuid)[:2], str(v.uuid)[2:]),
                  exist_ok=True,
                )
                save_tasks.append((v.uuid, v, clear_histories))
            else:
              os.makedirs(
                os.path.join(self.path, "Histories", str(v.uuid)[:2], str(v.uuid)[2:]),
                exist_ok=True,
              )
              save_tasks.append((v.uuid, v, clear_histories))
        i = 0
        total_history_count = len(save_tasks)
        history_percentage = 100 / max(1, total_history_count)

        def save_part(
          history_uuid: ClassDataTypeUUID[History] | None, current_history: History, clear: bool, index: int
        ) -> None:
          """
          保存历史记录的一部分。

          :param history_uuid: 历史记录的UUID，None则为当前周
          :param current_history: 历史记录
          :param clear: 是否清理历史记录
          :param index: 当前保存的历史记录索引
          """
          Chunk.update_progress(stage=f"保存历史记录（{index}/{total_history_count}）")
          if history_uuid:
            path = os.path.join(self.path, "Histories", history_uuid[:2], history_uuid[2:])
          else:
            path = os.path.join(self.path, "Current")
          if clear:
            shutil.rmtree(path, ignore_errors=True)
          os.makedirs(path, exist_ok=True)
          total_saved_objects = 0
          t = time.time()
          modify_templates: list[ScoreModificationTemplate] = list(self.bound_db.templates.values())
          day_records: list[DayRecord] = []
          achivement_templates: list[AchievementTemplate] = list(self.bound_db.achievements.values())

          for c, records in current_history.weekdays.items():
            for r in records.values():
              day_records.append(r)

          students: list[Student] = []
          modifies: list[ScoreModification] = []
          achievements: list[Achievement] = []
          groups: list[Group] = []
          classes: list[Class] = []

          for _class in current_history.classes.values():
            for homework_rule in _class.homework_rules:
              for template in homework_rule.rule_mapping.values():
                modify_templates.append(template)
            classes.append(_class)
            for student in _class.students.values():
              students.append(student)
              s = student
              for _ in range(Student.last_reset_info_keep_turns):  # 保留最近几次的重置信息
                # TODO: 把这个废性能的方法改一下，last_reset_info改成动态查询
                if s._last_reset_info: # pyright: ignore[reportPrivateUsage]
                  students.append(student.last_reset_info)
                  modifies.extend(student.last_reset_info.history.values())
                  achievements.extend(student.last_reset_info.achievements.values())
                  s = s.last_reset_info
              modifies.extend(student.history.values())
              achievements.extend(student.achievements.values())
              i = 0
              while student.last_reset_info:
                students.append(student.last_reset_info)
                modifies.extend(student.last_reset_info.history.values())
                achievements.extend(student.last_reset_info.achievements.values())
                i += 1
                student.last_reset_info = None
                if i > Student.last_reset_info_keep_turns:
                  break

            groups.extend(_class.groups.values())
          Base.log(
            "D",
            f"历史记录中的{history_uuid}的数据汇总完成，耗时{time.time() - t: .5f}秒",
            "Chunk.save",
          )
          total_objects = (
            len(classes)
            + len(students)
            + len(groups)
            + len(modifies)
            + len(achievements)
            + len(modify_templates)
            + len(day_records)
            + len(achivement_templates)
            + len(self.bound_db.current_day_attendance)
          )
          object_percentage = history_percentage / max(total_objects, 1)
          t = time.time()
          c = 0
          total = max(len(classes), 1)
          Chunk.update_progress(obj_name="班级信息", total=total)
          for _class in classes:
            Chunk.update_progress(current=c)
            Chunk.update_progress(percentage=total_saved_objects * object_percentage)
            DataObject(_class, self).save(path)
            c += 1
            total_saved_objects += 1
          c = max(1, c)
          Base.log(
            "D",
            f"历史记录中的{history_uuid}的班级保存完成，"
            f"耗时{time.time() - t: .5f}秒，共{c}个，"
            f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
            "Chunk.save",
          )
          t = time.time()
          c = 0
          total = max(len(students), 1)
          Chunk.update_progress(obj_name="学生信息", total=total)
          for student in students:
            Chunk.update_progress(current=c)
            Chunk.update_progress(percentage=total_saved_objects * object_percentage)
            DataObject(student, self).save(path)
            c += 1
            total_saved_objects += 1
          c = max(1, c)
          Base.log(
            "D",
            f"历史记录中的{history_uuid}的学生保存完成，"
            f"耗时{time.time() - t: .5f}秒，共{c}个，"
            f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
            "Chunk.save",
          )
          t = time.time()
          c = 0
          total = max(len(groups), 1)
          Chunk.update_progress(obj_name="小组信息", total=total)
          for group in groups:
            Chunk.update_progress(current=c)
            Chunk.update_progress(percentage=total_saved_objects * object_percentage)
            DataObject(group, self).save(path)
            c += 1
            total_saved_objects += 1
          c = max(1, c)
          Base.log(
            "D",
            f"历史记录中的{history_uuid}的小组保存完成，"
            f"耗时{time.time() - t: .5f}秒，共{c}个，"
            f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
            "Chunk.save",
          )
          t = time.time()
          c = 0
          total = max(len(modifies), 1)
          self.commit_changes()
          Chunk.update_progress(obj_name="分数修改记录", total=total)
          for modify in modifies:
            Chunk.update_progress(current=c)
            Chunk.update_progress(percentage=total_saved_objects * object_percentage)
            DataObject(modify, self).save(path)
            c += 1
            total_saved_objects += 1
          c = max(1, c)
          Base.log(
            "D",
            f"历史记录中的{history_uuid}的分数修改记录保存完成，"
            f"耗时{time.time() - t: .5f}秒，共{c}个，"
            f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
            "Chunk.save",
          )
          t = time.time()
          c = 0
          total = max(len(day_records), 1)
          Chunk.update_progress(obj_name="成就记录", total=total)
          for achievement in achievements:
            Chunk.update_progress(current=c)
            Chunk.update_progress(percentage=total_saved_objects * object_percentage)
            DataObject(achievement, self).save(path)
            c += 1
            total_saved_objects += 1
          c = max(1, c)
          Base.log(
            "D",
            f"历史记录中的{history_uuid}的成就记录保存完成，"
            f"耗时{time.time() - t: .5f}秒，共{c}个，"
            f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
            "Chunk.save",
          )
          t = time.time()
          c = 0
          Chunk.update_progress(obj_name="分数修改模板", total=total)
          for template in modify_templates:
            Chunk.update_progress(current=c)
            Chunk.update_progress(percentage=total_saved_objects * object_percentage)
            DataObject(template, self).save(path)
            c += 1
            total_saved_objects += 1
          c = max(1, c)
          Base.log(
            "D",
            f"历史记录中的{history_uuid}的分数修改模板保存完成，"
            f"耗时{time.time() - t: .5f}秒，共{c}个，"
            f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
            "Chunk.save",
          )
          t = time.time()
          c = 0
          total = max(len(achivement_templates), 1)
          Chunk.update_progress(obj_name="成就模板", total=total)
          for template in achivement_templates:
            Chunk.update_progress(current=c)
            Chunk.update_progress(percentage=total_saved_objects * object_percentage)
            DataObject(template, self).save(path)
            c += 1
            total_saved_objects += 1
          c = max(1, c)
          Base.log(
            "D",
            f"历史记录中的{history_uuid}的成就模板保存完成，"
            f"耗时{time.time() - t: .5f}秒，共{c}个，"
            f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
            "Chunk.save",
          )
          t = time.time()
          c = 0
          total = max(len(day_records), 1)
          Chunk.update_progress(obj_name="每日记录", total=total)
          for record in day_records:
            Chunk.update_progress(current=c)
            Chunk.update_progress(percentage=total_saved_objects * object_percentage)
            DataObject(record, self).save(path)
            c += 1
            total_saved_objects += 1
          c = max(1, c)
          Base.log(
            "D",
            f"历史记录中的{history_uuid}的每日记录保存完成，"
            f"耗时{time.time() - t: .5f}秒，共{c}个，"
            f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
            "Chunk.save",
          )
          t = time.time()
          c = 0
          total = max(len(self.bound_db.current_day_attendance.values()), 1)
          Chunk.update_progress(obj_name="当前出勤", total=total)
          for attendance_info in self.bound_db.current_day_attendance.values():
            Chunk.update_progress(current=c)
            Chunk.update_progress(percentage=total_saved_objects * object_percentage)
            DataObject(attendance_info, self).save(path)
            total_saved_objects += 1
            c += 1
          Base.log(
            "D",
            f"历史记录中的{history_uuid}的当前出勤保存完成，时间耗时{time.time() - t}秒",
            "Chunk.save",
          )

          DataObject.commit_changes()
          DataObject.cur_list = {}
          Base.log("D", "当前数据库连接已关闭", "Chunk.save")
          Base.log("D", "保存基本信息", "Chunk.save")
          json.dump(
            {
              "uuid": str(history_uuid) if history_uuid else None,
              "create_time": current_history.time,
              "save_time": self.bound_db.save_time,
              "version": self.bound_db.version,
              "version_code": self.bound_db.version_code,
              "last_start_time": self.bound_db.last_start_time,
              "last_reset": self.bound_db.last_reset,
              "user": self.bound_db.user,
              "total_objects": total_saved_objects,  # 这个可以在后面用来做加载进度条
              "python_version": (
                sys.version_info.major,
                sys.version_info.minor,
                sys.version_info.micro,
              ),
            },
            open(os.path.join(path, "info.json"), "w", encoding="utf-8"),
            indent=4,
          )
          json.dump(
            [(c.key, str(c.uuid)) for c in current_history.classes.values()],
            open(os.path.join(path, "classes.json"), "w", encoding="utf-8"),
            indent=4,
          )

          json.dump(
            {
              _class: {k: str(v.uuid) for k, v in item.items()}
              for _class, item in current_history.weekdays.items()
            },
            open(os.path.join(path, "weekdays.json"), "w", encoding="utf-8"),
            indent=4,
          )

          json.dump(
            [(a.target_class, str(a.uuid)) for a in self.bound_db.current_day_attendance.values()],
            open(os.path.join(path, "current_day_attendance.json"), "w", encoding="utf-8"),
          )

          json.dump(
            [(t.key, str(t.uuid)) for t in self.bound_db.templates.values()],
            open(os.path.join(path, "templates.json"), "w", encoding="utf-8"),
            indent=4,
          )

          json.dump(
            [(a.key, str(a.uuid)) for a in self.bound_db.achievements.values()],
            open(os.path.join(path, "achievements.json"), "w", encoding="utf-8"),
            indent=4,
          )

          Base.log("I", f"{history_uuid}的存档信息保存完成({index}/{total})", "Chunk.save")

        i = 1
        for uuid, current_history, clear in save_tasks:
          save_part(uuid, current_history, clear, i)
          i += 1

        Base.log("D", "所有数据保存完成", "Chunk.save")

        history_uuids: list[str] = []
        for dir_1 in os.listdir(os.path.join(self.path, "Histories")):
          for dir_2 in os.listdir(os.path.join(self.path, "Histories", dir_1)):
            history_uuids.append(dir_1 + dir_2)
            
        json.dump(
          {
            "user": self.bound_db.user,
            "create_time": time.time(),
            "save_time": self.bound_db.save_time,
            "version": self.bound_db.version,
            "version_code": self.bound_db.version_code,
            "last_start_time": self.bound_db.last_start_time,
            "last_reset": self.bound_db.last_reset,
            "histories": history_uuids,
            "python_version": (
              sys.version_info.major,
              sys.version_info.minor,
              sys.version_info.micro,
            ),
          },
          open(os.path.join(self.path, "info.json"), "w", encoding="utf-8"),
          indent=4,
        )
      except Exception:
        Base.log_exc("保存数据时出现未处理的错误，保存操作中断", "Chunk.save", "E")
        self.commit_changes()
        self.is_saving = False
        raise

      else:
        self.commit_changes()
        self.is_saving = False

      finally:
        self.commit_changes()
        self.is_saving = False
