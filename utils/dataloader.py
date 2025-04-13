
"""
数据加载模块
"""
import os
import sys
import math
import shutil
import sqlite3

from utils.functions.prompts     import question_yes_no
from utils.classdtypes import * # pylint: disable=unused-wildcard-import, wildcard-import
from utils.classobjects import gen_uuid

# 数据加载器



BaseDataType = Union[int, float, bool, str]






_RT = TypeVar("_RT", Student, Class, Group,
                      AttendanceInfo,
                      ScoreModification, ScoreModificationTemplate,
                      Achievement, AchievementTemplate,
                      DayRecord)


class DataKind(Generic[_RT], str):
    "数据类型, DataKind[Student]代表这个对象在被访问之后会变成一个对象"

    def __init__(self, instance: _RT, bound_chunk: "Chunk",
                history_uuid: Union[UUIDKind[History], Literal["Current"]]) \
                    -> Union["DataKind[_RT]", _RT]:
        """
        根据数据类型生成一个未加载的数据类型。
        
        :param instance: 数据实例
        :param bound_chunk: 数据所在分块
        :return: 数据类型

        - 注意，``Union["DataKind[_RT]", _RT]``中的``_RT``只是用来给类成员提示的，实际上**并不会返回原来的数据类型！**
        """
        self.data_type: Type[ClassDataType] = instance.__class__
        self.instance = instance
        self.chunk = bound_chunk
        self.history_uuid = history_uuid

    def __getattr__(self, item: str) -> Any:
        value = getattr(self.instance, item)
        if isinstance(value, UUIDKind):
            try:
                return DataObject.loaded_object_list[(self.history_uuid,
                                                    self.data_type.chunk_type_name,
                                                    value.uuid)]
            except KeyError:
                obj = self.data_type.from_string(
                    self.chunk.get_object_rdata(self.history_uuid, value.uuid,
                                                self.data_type.chunk_type_name))
                DataObject.loaded_object_list[(self.history_uuid, self.data_type.chunk_type_name,
                                            value.uuid)] = obj
                setattr(self.instance, item, obj)
                return obj
        else:
            return value



_RDT = TypeVar("_RDT", Student, Class, Group,
                      AttendanceInfo,
                      ScoreModification, ScoreModificationTemplate,
                      Achievement, AchievementTemplate,
                      DayRecord)



_NT = TypeVar("_NT")
class StringObjectDataKind(Generic[_NT], str):
    "对象数据类型, ObjectDataKind[Student]代表这个字符串可以加载出一个学牲"

class UserDataBase(Object):
    "用户数据库"

    def __init__(self,
                user:                   Optional[str] = None,
                save_time:              Optional[float] = None,
                version:                Optional[str] = None,
                version_code:           Optional[int] = None,
                last_reset:             Optional[float] = None,
                history_data:           Optional[Dict[float, History]] = None,
                classes:                Optional[Dict[str, Class]] = None,
                templates:              Optional[Dict[str,
                                        "ClassObj.ScoreModificationTemplate"]] = None,
                achievements:           Optional[Dict[str, AchievementTemplate]] = None,
                last_start_time:        Optional[float] = None,
                weekday_record:         Optional[List[DayRecord]] = None,
                current_day_attendance: Optional[AttendanceInfo] = None):
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
        :param current_day_attendance: 今日出勤状况
        """
        self.loaded = False
        self.user = user or "unknown"
        self.save_time = save_time or time.time()
        self.version = version or "unknown"
        self.version_code = version_code or 0
        self.last_reset = last_reset or time.time()
        self.history_data = history_data or {}
        self.classes = classes or {}
        self.templates = templates or {}
        self.achievements = achievements or {}
        self.last_start_time = last_start_time or time.time()
        self.weekday_record = weekday_record or []
        self.current_day_attendance = current_day_attendance or AttendanceInfo()
        self.loaded = user is not None # 任一参数非空即视为已加载

    def set(self,
            user:                   Optional[str] = None,
            save_time:              Optional[float] = None,
            version:                Optional[str] = None,
            version_code:           Optional[int] = None,
            last_reset:             Optional[float] = None,
            history_data:           Optional[Dict[float, History]] = None,
            classes:                Optional[Dict[str, Class]] = None,
            templates:              Optional[Dict[str, "ClassObj.ScoreModificationTemplate"]]= None,
            achievements:           Optional[Dict[str, AchievementTemplate]] = None,
            last_start_time:        Optional[float] = None,
            weekday_record:         Optional[List[DayRecord]] = None,
            current_day_attendance: Optional[AttendanceInfo] = None):
        """构建一个数据库对象。
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
        :param current_day_attendance: 今日出勤状况"""
        self.user = user or "unknown"
        self.save_time = save_time or time.time()
        self.version = version or "unknown"
        self.version_code = version_code or 0
        self.last_reset = last_reset or time.time()
        self.history_data = history_data or {}
        self.classes = classes or {}
        self.templates = templates or {}
        self.achievements = achievements or {}
        self.last_start_time = last_start_time or time.time()
        self.weekday_record = weekday_record or []
        self.current_day_attendance = current_day_attendance or AttendanceInfo()
        self.loaded = user is not None # 任一参数非空即视为已加载

    def __contains__(self, key):
        return key in self.__dict__ and \
            self.__dict__[key] is not None and self.__dict__[key] is not None





class DataObject:
    "数据对象"

    loaded_objects = 0
    "加载了的对象数量"

    saved_objects = 0
    "保存了的对象数量"

    cur_list: Dict[str, sqlite3.Cursor] = {}
    "连接列表，conn_list[数据类型名称]=光标"

    loaded_object_list: Dict[Tuple[UUIDKind[History],
                                str, UUIDKind[ClassDataType]], ClassDataType] = {}
    "加载目标列表"

    load_tasks: List[Tuple[UUIDKind[History], str, UUIDKind[ClassDataType]]] = []
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
    def relase_connections(clear_chunk_connections: bool = True):
        "释放所有连接"
        for cur in DataObject.cur_list.values():
            try:
                cur.close()
                cur.connection.commit()
                cur.connection.close()
            except sqlite3.Error:
                pass
        DataObject.cur_list.clear()
        if clear_chunk_connections:
            Chunk.relase_connections(False)




    def __init__(self, data: ClassDataType, chunk: "Chunk",
                state: Literal["none", "detached", "normal"] = "normal"):
        self.object = data
        self.chunk = chunk
        self.object_load_state: Literal["none", "detached", "normal"] = state
        # 这些是加载的属性，后面有的可能会有
        self.student_history = None
        self.student_achievements = None
        self.group_leader = None
        self.group_members = None
        self.class_cleaning_mapping = None
        self.class_groups = None
        self.class_homework_rules = None
        self.class_students = None
        self.modify_temp = None
        self.modify_execute_time_key = None
        self.modify_target = None
        self.achievement_target = None
        self.achievement_template = None
        self.atdinfo_is_absent = None
        self.atdinfo_is_early = None
        self.atdinfo_is_late = None
        self.atdinfo_is_late_more = None
        self.atdinfo_is_leave_early = None
        self.atdinfo_is_leave = None
        self.atdinfo_is_leave_late = None
        self.homeworkrule_rule_mapping = None
        self.dayrecord_target_class = None
        self.dayrecord_attendance_info = None
        self.history_weekdays = None
        self.history_classes = None
        self.archive_uuid = None





    def save(self, path: Optional[str] = None, max_retry: int = 3):
        "在数据分组中保存这个对象。"
        uuid = self.object.uuid
        string = self.object.to_string()
        type_name = self.object.chunk_type_name
        path = path or self.chunk.path
        while max_retry:
            max_retry -= 1
            if type_name not in self.cur_list:
                conn = sqlite3.connect(os.path.join(path, f"{type_name}.db"),
                                    check_same_thread=False)
                cur = conn.cursor()
                for i in range(16):
                    prefix = f"{i:01x}"
                    cur.execute(f"""CREATE TABLE IF NOT EXISTS datas_{prefix} (
                                                uuid   text       primary key,    -- 数据UUID
                                                class  text,                      -- 数据类型
                                                data   text                       -- 数据
                                        )""")
                conn.commit()
                conn.close()
                conn = sqlite3.connect(os.path.join(path, f"{type_name}.db"),
                                    check_same_thread=False)  # 重新连接
                self.cur_list[type_name] = conn.cursor()

            cursor = self.cur_list[type_name]

            for i in range(3):
                try:

                    cursor.execute(f"SELECT class FROM datas_{uuid[:1]} WHERE uuid = ?", (uuid,))
                    existing_class = cursor.fetchone()

                    if existing_class:
                        if existing_class[0] == type_name:
                            cursor.execute(f"""
                                UPDATE datas_{uuid[:1]}
                                SET class = ?, data = ?
                                WHERE uuid = ?
                            """, (type_name, string, uuid))
                        else:
                            raise ValueError(f"对于{uuid!r}的对象，数据库中已经存在一个不同类型的对象！"
                                            f"（当前为{type_name!r}，数据库中为{existing_class[0]!r}）\n"
                                            "如果你看见了这个错误，你可能碰见了"
                                            "1/340282366920938463463374607431768211456的概率"
                                            "（不知道该恭喜你还是感到遗憾）")
                    else:
                        cursor.execute(f"""
                            INSERT INTO datas_{uuid[:1]} (uuid, class, data)
                            VALUES (?, ?, ?)
                        """, (uuid, type_name, string))

                    DataObject.saved_objects += 1
                    return
                except sqlite3.Error as e:
                    Base.log_exc_short(f"处理数据出现错误，"
                                        f"对象：{self.object.__class__.__name__}({self.object.uuid})，"
                                        "0.1秒后重试", "DataObject.save", "W", exc=e)
                    try:
                        conn.rollback()
                    except sqlite3.Error:
                        self.relase_connections()
                        Base.log("W", "操作回滚失败，已重置所有连接，将会重试", "DataObject.save")
                    time.sleep(0.1)
                    continue
            Base.log_exc(f"处理数据时出现错误，对象：{self.object!r}，重试3次后仍然失败；"
                        "已重置所有连接，将会重试", "DataObject.save", "E")
            self.relase_connections()



    def load_stage1(self, data: str) -> ClassDataType:
        "从某个文件加载这个对象，阶段1 - 只加载基本数据"

        data: Dict[str, Any] = json.loads(data)

        try:
            data_type = data.pop("type")        # 移除类型信息避免参数错误
        except KeyError as e:
            raise KeyError("对象没有具体的数据类型！") from e

        uuid = data.pop("uuid")
        archive_uuid = data.pop("archive_uuid")

        if data_type == Student.chunk_type_name:
            self.student_history: List[UUIDKind[ScoreModification]] = data.pop("history")
            self.student_achievements: List[UUIDKind[Achievement]] = data.pop("achievements")
            data["history"] = {}
            data["achievements"] = {}
            data["score"] = Student.score_dtype(data["score"])
            self.object = Student(**data)
            self.object_load_state = "detached"

        elif data_type == Group.chunk_type_name:
            self.group_leader: UUIDKind[Student] = data.pop("leader")
            self.group_members: List[UUIDKind[Student]] = data.pop("members")
            data["leader"] = default_student
            data["members"] = []
            self.object = Group(**data)
            self.object_load_state = "detached"

        elif data_type == ScoreModificationTemplate.chunk_type_name:
            self.object = ScoreModificationTemplate(**data)
            self.object_load_state = "normal" # 默认加载状态，无需手动连接

        elif data_type == ScoreModification.chunk_type_name:
            self.modify_temp: UUIDKind[ScoreModificationTemplate] = data.pop("template")
            self.modify_target: UUIDKind[Student] = data.pop("target")
            self.modify_execute_time_key: int = data.pop("execute_time_key")
            data["template"] = default_score_template
            data["target"] = default_student
            self.object = ScoreModification(**data)
            self.object.execute_time_key = self.modify_execute_time_key
            self.object_load_state = "detached"

        elif data_type == HomeworkRule.chunk_type_name:
            self.homeworkrule_rule_mapping: \
                Dict[str, UUIDKind[ScoreModificationTemplate]] = data.pop("rule_mapping")
            data["rule_mapping"] = {}
            self.object = HomeworkRule(**data)
            self.object_load_state = "detached"

        elif data_type == Class.chunk_type_name:
            self.class_students: List[UUIDKind[Student]] = data.pop("students")
            self.class_groups: List[UUIDKind[Group]] = data.pop("groups")
            self.class_cleaning_mapping: \
                List[Tuple[int, List[Tuple[Literal["member", "leader"],
                        List[UUIDKind[Student]]]]]] = data.pop("cleaning_mapping")
            # 复杂数据处理逻辑
            # 其实我的意思是这个类型注释过于幽默了
            self.class_homework_rules: Dict[str, UUIDKind[HomeworkRule]] \
                = data.pop("homework_rules")
            data["students"] = {}
            data["groups"] = {}
            data["cleaning_mapping"] = {}
            data["homework_rules"] = {}
            self.object = Class(**data)
            self.object_load_state = "detached"

        elif data_type == AchievementTemplate.chunk_type_name:
            if "other" in data:
                data["other"] = pickle.loads(data[["other"]])
            self.object = AchievementTemplate(**data)
            self.object_load_state = "normal"

        elif data_type == Achievement.chunk_type_name:
            self.achievement_template: UUIDKind[AchievementTemplate] = data.pop("template")
            self.achievement_target: UUIDKind[Student] = data.pop("target")
            data["template"] = default_achievement_template
            data["target"] = default_student
            self.object = Achievement(**data)
            self.object_load_state = "detached"

        elif data_type == AttendanceInfo.chunk_type_name:
            self.atdinfo_is_early: List[UUIDKind[Student]] = data.pop("is_early")
            self.atdinfo_is_late: List[UUIDKind[Student]] = data.pop("is_late")
            self.atdinfo_is_late_more: List[UUIDKind[Student]] = data.pop("is_late_more")
            self.atdinfo_is_absent: List[UUIDKind[Student]] = data.pop("is_absent")
            self.atdinfo_is_leave: List[UUIDKind[Student]] = data.pop("is_leave")
            self.atdinfo_is_leave_early: List[UUIDKind[Student]] = data.pop("is_leave_early")
            self.atdinfo_is_leave_late: List[UUIDKind[Student]] = data.pop("is_leave_late")
            data["is_early"] = []
            data["is_late"] = []
            data["is_late_more"] = []
            data["is_absent"] = []
            data["is_leave"] = []
            data["is_leave_early"] = []
            data["is_leave_late"] = []
            self.object = AttendanceInfo(**data)

        elif data_type == DayRecord.chunk_type_name:
            self.dayrecord_target_class: UUIDKind[Class] = data.pop("target_class")
            self.dayrecord_attendance_info: UUIDKind[AttendanceInfo] = data.pop("attendance_info")
            data["target_class"] = None
            data["attendance_info"] = None
            self.object = DayRecord(**data)
            self.object_load_state = "detached"

        elif data_type == History.chunk_type_name:
            self.history_classes: Dict[str, UUIDKind[Class]] = data.pop("classes")
            self.history_weekdays: Dict[int, UUIDKind[DayRecord]] = data.pop("weekdays")
            data["classes"] = {}
            data["weekdays"] = {}
            self.object = History(**data)
            self.object_load_state = "detached"

        self.object.uuid = uuid
        self.archive_uuid = archive_uuid
        return self


_LT = TypeVar("_LT")
def spilt_list(lst: Iterable[_LT], slices: int,
            max_size: Optional[int] = None, min_size: Optional[int] = None) -> List[List[_LT]]:
    """
    将列表按指定数量分组。

    :param lst: 列表
    :param slices: 分组数量
    :param max_size: 最大分组大小
    :param min_size: 最小分组大小
    :return: 分组后的列表
    """
    size = math.ceil(len(lst) / slices)
    if max_size is not None:
        size = min(size, max_size)
    if min_size is not None:
        size = max(size, min_size)
    result = []
    lst = list(lst)
    while len(lst) > 0:
        result.append(lst[:size])
        lst = lst[size:]
    return result


_DT = TypeVar("_DT")

class Chunk:
    "数据分组"

    database_connections: Dict[Tuple[Union[UUIDKind[History], Literal["Current"]], str],
                            sqlite3.Connection] = {}
    "数据库连接池，database_connection[(历史记录uuid,数据类型名)] = sqlite3.Connection"


    def __init__(self, path: str, bound_database: Optional[UserDataBase] = None):
        self.path = path
        self.bound_db = bound_database or UserDataBase(path)
        self.is_saving = False
        os.makedirs(self.path if not path.endswith(".datas")
                    else os.path.dirname(self.path), exist_ok=True)


    def get_object_rdata(self, history_uuid:Union[UUIDKind[History], Literal["Current"]],
                                uuid: UUIDKind[_DT], data_type: str) -> StringObjectDataKind[_DT]:
        """
        获取对象数据。
        
        :param history_uuid: 历史记录uuid，Current为此周（还未重置的存档
        :param uuid: 对象uuid
        :param data_type: 数据类型名
        :return: 对象数据
        :raise ValueError: 数据不存在
        """
        try:
            conn = self.database_connections[(history_uuid, data_type)]
        except KeyError:
            conn = sqlite3.connect(os.path.join(self.path, f"{data_type}.db"),
                                    check_same_thread=False)
            self.database_connections[(history_uuid, data_type)] = conn
        result = conn.execute(f"SELECT data FROM datas_{uuid[:1]} WHERE uuid = ?",
                                (uuid,)).fetchone()
        if result is None:
            raise ValueError("数据不存在")
        return result[0]


    def load_history(self, 
                    history_uuid: Union[UUIDKind[History],
                                            Literal["Current"]] = "Current",
                    request_uuid: Optional[UUIDKind[Type[None]]] = None) -> History:
        """
        加载历史记录。

        :param history_uuid: 历史记录uuid
        :param request_uuid: 请求uuid，只是用来做数据加载的标识的
        :return: 历史记录
        :raise FileNotFoundError: 历史记录不存在
        """
        failures = []
        def _load_object(uuid: UUIDKind[_DT], data_type: ClassDataType,
                        history_uuid: UUIDKind[History] = history_uuid) -> _DT:
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
                    # 如果没连接就直接开一个新的连接放连接池，不用反复开开关关的节约性能（加载完记得relase_connections，清理内存）
                    conn = sqlite3.connect(
                        os.path.join(path, f"{data_type.chunk_type_name}.db"),
                        check_same_thread=False)

                    self.database_connections[(history_uuid, data_type.chunk_type_name)] = conn

                try:
                    result = conn.execute(f"SELECT data FROM datas_{uuid[:1]} WHERE uuid = ?",
                                    (uuid,)).fetchone()
                except sqlite3.OperationalError:

                    Base.log("W", f"数据不存在，将会返回默认\n数据：{data_type.__qualname__}({uuid})",
                            "Chunk.load_history")
                    DataObject.load_tasks.remove(_id)
                    failures.append(_id)
                    return data_type.new_dummy()

                if result is None:
                    Base.log("W", f"数据不存在，将会返回默认\n数据：{data_type.__qualname__}({uuid})",
                            "Chunk.load_history")
                    DataObject.load_tasks.remove(_id)
                    failures.append(_id)
                    return data_type.new_dummy()

                obj_shallow_loaded = data_type.new_dummy()
                # 先浅层加载一下，防止触发无限递归
                DataObject.loaded_object_list[_id] = obj_shallow_loaded
                # 再深层处理，这样就不用担心了
                DataObject.loaded_object_list[_id].inst_from_string(result[0])
                obj = DataObject.loaded_object_list[_id]
                DataObject.load_tasks.remove(_id)
                return obj
        ClassObj.LoadUUID = _load_object
        if history_uuid == "Current":
            path = os.path.join(self.path, "Current")
        else:
            path = os.path.join(self.path, "Histories", history_uuid[:2], history_uuid[2:])
        if not os.path.isdir(path):
            raise FileNotFoundError("历史记录不存在")
        info = json.load(open(os.path.join(path, "info.json"), "r", encoding="utf-8"))
        if "python_version" in info:
            data_python_ver = info["python_version"]
            current_ver = [sys.version_info.major, sys.version_info.minor, sys.version_info.micro]
            if data_python_ver != current_ver:
                if "noticed_version_changed" not in runtime_flags:
                    runtime_flags["noticed_version_changed"] = set()
                if request_uuid is not None and request_uuid not in runtime_flags["noticed_version_changed"]:

                    Base.log("W", f"历史记录的Python版本为{data_python_ver}，当前版本为{current_ver}，可能存在兼容性问题")
                    if not question_yes_no(None, "警告", F"检测到存档的Python版本({data_python_ver[0]}.{data_python_ver[1]}.{data_python_ver[2]})"
                                    f"与当前版本({current_ver[0]}.{current_ver[1]}.{current_ver[2]})不一致，\n"
                                    "如果继续加载，可能导致加载存档失败甚至闪退。\n"
                                    "是否继续加载数据？"):
                        raise RuntimeError("用户取消加载")
                    runtime_flags["noticed_version_changed"].add(request_uuid)

        else:
            Base.log("W", "历史记录的Python版本信息缺失，可能存在兼容性问题", "Chunk.load_history")
        class_uuids = json.load(open(os.path.join(path, "classes.json"), "r", encoding="utf-8"))
        weekday_uuids = json.load(open(os.path.join(path, "weekdays.json"), "r", encoding="utf-8"))
        classes = {}
        for _, class_uuid in class_uuids:
            _class: Class = ClassObj.LoadUUID(class_uuid, Class)
            classes[_class.key] = _class

        for _, weekday_uuid in weekday_uuids:
            weekday: DayRecord = ClassObj.LoadUUID(weekday_uuid, DayRecord)
            self.bound_db.weekday_record.append(weekday)

        history = History(classes, self.bound_db.weekday_record,
                        json.load(open(os.path.join(path, "info.json"),
                                    "r", encoding="utf-8"))["create_time"])
        history.uuid = history_uuid
        history.archive_uuid = history_uuid
        Base.log("I", f"历史记录{history_uuid}加载完成，警告数量：{len(failures)}")
        return history

    def del_history(self, history_uuid: str) -> bool:
        """
        删除历史记录
        """
        try:
            shutil.rmtree(os.path.join(self.path, "Histories", history_uuid[:2], history_uuid[2:]))
            return True
        except Exception as unused: # pylint: disable=broad-exception-caught
            return False

    def load_data(self, load_all: bool = False) -> UserDataBase:
        """
        加载数据。

        :return: 对象数据
        :param load_all: 是否加载所有数据
        """
        req_uuid = gen_uuid()
        current_record = self.load_history("Current", req_uuid)

        templates = []
        achievements = []
        current_day_attendance = AttendanceInfo()

        # 有个细节，这里的LoadUUID是纲刚刚加载完这周的，所以不用填默认参数
        template_uuids = json.load(open(os.path.join(self.path, "Current", "templates.json"),
                                    "r", encoding="utf-8"))

        for _, template_uuid in template_uuids:
            templates.append(ClassObj.LoadUUID(template_uuid, ScoreModificationTemplate))

        achievement_uuids = json.load(open(os.path.join(self.path, "Current", "achievements.json"),
                                        "r", encoding="utf-8"))
        for _, achievement_uuid in achievement_uuids:
            achievements.append(ClassObj.LoadUUID(achievement_uuid, AchievementTemplate))

        info = json.load(open(os.path.join(self.path, "info.json"), "r", encoding="utf-8"))
        self.bound_db.uuid = info["uuid"]
        self.bound_db.save_time = info["save_time"]
        self.bound_db.version = info["version"]
        self.bound_db.version_code = info["version_code"]
        self.bound_db.last_reset = info["last_reset"]
        self.bound_db.last_start_time = info["last_start_time"]
        histories = {}
        if load_all:
            for uuid in info["histories"]:
                try:
                    h = self.load_history(uuid, req_uuid)
                    while h.time in histories:
                        h.time += 0.001
                    histories[h.time] = h
                except FileNotFoundError as e:
                    Base.log_exc(F"历史记录{uuid}加载失败，将跳过", "Chunk.load_data", "E", e)
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
            templates,
            achievements,
            info["last_start_time"],
            list(current_record.weekdays.values()),
            current_day_attendance,
        )


    @staticmethod
    def relase_connections(clear_dataobj_connections: bool = True) -> None:
        """释放所有连接"""
        for v in Chunk.database_connections.values():
            v.commit()
            v.close()
        Chunk.database_connections.clear()
        if clear_dataobj_connections:
            DataObject.relase_connections(False)

    def save(self,
            save_history: bool = True,
            save_only_if_not_exist: bool = True,
            clear_current: bool = False,
            clear_histories: bool = False) -> None:
        """
        保存数据。

        :param save_history: 是否保存历史记录
        :param save_only_if_not_exist: 是否只保存不存在的数据
        :param clear_current: 是否清理当前数据
        :param clear_histories: 是否清理历史数据
        """
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
            save_tasks: List[Tuple[str, History, bool]] = [("Current", history, clear_current)]
            if save_history:
                for v in self.bound_db.history_data.values():
                    if save_only_if_not_exist:
                        if not os.path.isfile(os.path.join(self.path,
                                                "Histories", v.uuid[:2], v.uuid[2:], "info.json")):
                            os.makedirs(os.path.join(self.path, "Histories",
                                                v.uuid[:2], v.uuid[2:]), exist_ok=True)
                            save_tasks.append((v.uuid, v, clear_histories))
                    else:
                        os.makedirs(os.path.join(self.path, "Histories",
                                                v.uuid[:2], v.uuid[2:]), exist_ok=True)
                        save_tasks.append((v.uuid, v, clear_histories))
            i = 0
            total = len(save_tasks)
            def save_part(uuid: str, current_history: History, clear: bool, index: int) -> None:
                if uuid != "Current":
                    path = os.path.join(self.path, "Histories", uuid[:2], uuid[2:])
                else:
                    path = os.path.join(self.path, "Current")
                if clear:
                    shutil.rmtree(path, ignore_errors=True)
                os.makedirs(path, exist_ok=True)
                total_objects = 0
                t = time.time()
                modify_templates: List[ScoreModificationTemplate] \
                    = list(self.bound_db.templates.values())
                achivement_templates: List[AchievementTemplate] \
                    = list(self.bound_db.achievements.values())
                day_records: List[DayRecord] = list(self.bound_db.weekday_record)
                day_records.append(self.bound_db.current_day_attendance)
                students: List[Student] = []
                modifies: List[ScoreModification] = []
                achievements: List[Achievement] = []
                groups: List[Group] = []
                classes: List[Class] = []

                for _class in current_history.classes.values():
                    for homework_rule in _class.homework_rules:
                        for template in homework_rule.rule_mapping.values():
                            modify_templates.append(template)
                    classes.append(_class)
                    for student in _class.students.values():
                        students.append(student)
                        s = student
                        for _ in range(Student.last_reset_info_keep_turns): # 保留最近几次的重置信息
                            # TODO: 把这个废性能的方法改一下，last_reset_info改成动态查询
                            if s.last_reset_info:
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
                Base.log("D", F"历史记录中的{uuid}的数据汇总完成，耗时{time.time() - t: .5f}秒", "Chunk.save")
                t = time.time()
                c = 0
                for _class in classes:
                    DataObject(_class, self).save(path)
                    c += 1
                    total_objects += 1
                c = max(1, c)
                Base.log("D", F"历史记录中的{uuid}的班级保存完成，"
                        f"耗时{time.time() - t: .5f}秒，共{c}个，"
                        f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
                        "Chunk.save")
                t = time.time()
                c = 0
                for student in students:
                    DataObject(student, self).save(path)
                    c += 1
                    total_objects += 1
                c = max(1, c)
                Base.log("D", f"历史记录中的{uuid}的学生保存完成，"
                        f"耗时{time.time() - t: .5f}秒，共{c}个，"
                        f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
                        "Chunk.save")
                t = time.time()
                c = 0
                for group in groups:
                    DataObject(group, self).save(path)
                    c += 1
                    total_objects += 1
                c = max(1, c)
                Base.log("D", F"历史记录中的{uuid}的小组保存完成，"
                        f"耗时{time.time() - t: .5f}秒，共{c}个，"
                        f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
                        "Chunk.save")
                t = time.time()
                c = 0
                self.relase_connections()
                for modify in modifies:
                    DataObject(modify, self).save(path)
                    c += 1
                    total_objects += 1
                c = max(1, c)
                Base.log("D", F"历史记录中的{uuid}的分数修改记录保存完成，"
                        f"耗时{time.time() - t: .5f}秒，共{c}个，"
                        F"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
                        "Chunk.save")
                t = time.time()
                c = 0
                for achievement in achievements:
                    DataObject(achievement, self).save(path)
                    c += 1
                    total_objects += 1
                c = max(1, c)
                Base.log("D", F"历史记录中的{uuid}的成就记录保存完成，"
                        f"耗时{time.time() - t: .5f}秒，共{c}个，"
                        f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
                        "Chunk.save")
                t = time.time()
                c = 0
                for template in modify_templates:
                    DataObject(template, self).save(path)
                    c += 1
                    total_objects += 1
                c = max(1, c)
                Base.log("D", F"历史记录中的{uuid}的分数修改模板保存完成，"
                        f"耗时{time.time() - t: .5f}秒，共{c}个，"
                        f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
                        "Chunk.save")
                t = time.time()
                c = 0
                for template in achivement_templates:
                    DataObject(template, self).save(path)
                    c += 1
                    total_objects += 1
                c = max(1, c)
                Base.log("D", F"历史记录中的{uuid}的成就模板保存完成，"
                        f"耗时{time.time() - t: .5f}秒，共{c}个，"
                        f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
                        "Chunk.save")
                t = time.time()
                c = 0
                for record in day_records:
                    DataObject(record, self).save(path)
                    c += 1
                    total_objects += 1
                c = max(1, c)
                Base.log("D", F"历史记录中的{uuid}的每日记录保存完成，"
                        f"耗时{time.time() - t: .5f}秒，共{c}个，"
                        f"速率{c / (time.time() - t if (time.time() - t) > 0 else 1): .3f}个/秒",
                        "Chunk.save")
                t = time.time()
                Base.log("D", F"历史记录中的{uuid}的当前出勤保存完成，"
                        f"时间耗时{time.time() - t}秒",
                        "Chunk.save")

                DataObject.relase_connections()
                DataObject.cur_list = {}
                Base.log("D", "当前数据库连接已关闭", "Chunk.save")
                Base.log("D", "保存基本信息", "Chunk.save")
                json.dump(
                    {
                        "uuid": uuid if uuid != "Current" else None,
                        "create_time": current_history.time,
                        "save_time": self.bound_db.save_time,
                        "version": self.bound_db.version,
                        "version_code": self.bound_db.version_code,
                        "last_start_time": self.bound_db.last_start_time,
                        "last_reset": self.bound_db.last_reset,
                        "user": self.bound_db.user,
                        "total_objects": total_objects,          # 这个可以在后面用来做加载进度条
                        "python_version": (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
                        },
                    open(os.path.join(path, "info.json"), "w", encoding="utf-8"),
                    indent=4
                )
                json.dump([(c.key, c.uuid) for c in current_history.classes.values()],
                        open(os.path.join(path, "classes.json"),
                            "w", encoding="utf-8"), indent=4)

                json.dump([(d.utc, d.uuid) for d in current_history.weekdays.values()],
                        open(os.path.join(path, "weekdays.json"),
                            "w", encoding="utf-8"), indent=4)

                json.dump([(t.key, t.uuid) for t in self.bound_db.templates.values()],
                        open(os.path.join(path, "templates.json"),
                            "w", encoding="utf-8"), indent=4)

                json.dump([(a.key, a.uuid) for a in self.bound_db.achievements.values()],
                        open(os.path.join(path, "achievements.json"),
                            "w", encoding="utf-8"), indent=4)


                Base.log("I", f"{uuid}的存档信息保存完成({index}/{total})", "Chunk.save")
            i = 1
            for uuid, current_history, clear in save_tasks:
                save_part(uuid, current_history, clear, i)
                i += 1


            Base.log("D", "所有数据保存完成", "Chunk.save")

            history_uuids = []
            for dir_1 in os.listdir(os.path.join(self.path, "Histories")):
                for dir_2 in os.listdir(os.path.join(self.path, "Histories", dir_1)):
                    history_uuids.append(dir_1 + dir_2)

            json.dump(
                {
                    "uuid": uuid if uuid != "Current" else None,
                    "user": self.bound_db.user,
                    "create_time": time.time(),
                    "save_time": self.bound_db.save_time,
                    "version": self.bound_db.version,
                    "version_code": self.bound_db.version_code,
                    "last_start_time": self.bound_db.last_start_time,
                    "last_reset": self.bound_db.last_reset,
                    "histories": history_uuids,
                    "python_version": (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
                },
                open(os.path.join(self.path, "info.json"), "w", encoding="utf-8"),
                indent=4
            )
        except Exception as e:
            self.relase_connections()
            self.is_saving = False
            raise e

        else:
            self.relase_connections()
            self.is_saving = False

        finally:
            self.relase_connections()
            self.is_saving = False
