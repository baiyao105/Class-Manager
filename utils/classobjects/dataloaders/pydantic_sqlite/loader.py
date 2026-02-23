"""
PydanticSQLiteLoader - 使用标准化表结构的加载器。

复用 pydantic_loader 的模型，但使用标准化表结构存储数据。
"""

from __future__ import annotations

import os
import json
import base64
import pickle
import dill as pickle # type: ignore
import sqlite3
from collections import OrderedDict
from typing import Any, TypeVar, cast
from uuid import UUID

from utils.basetypes import Base

from ...basetype import ClassDataType, ClassDataTypeUUID
from ...classdataloader import UserDataBase
from ...datachunk import DataChunk
from ..pydantic_loader.base import PydanticModelBase, register_type
from .schema import TableSchema

from ...objects import (
    Achievement,
    AchievementTemplate,
    AttendanceInfo,
    Class,
    DataTag,
    Group,
    History,
    ScoreModification,
    ScoreModificationTemplate,
    Student,
)

T = TypeVar("T", bound="ClassDataType")

IDENTIFIER_FILE = ".pydantic_sqlite_data"
IDENTIFIER_VERSION = 1


class PydanticSQLiteLoader(DataChunk):
    """
    使用标准化表结构的 Pydantic 加载器。
    
    与 PydanticLoader 的区别：
    - PydanticLoader: 使用 JSON 列存储数据
    - PydanticSQLiteLoader: 使用标准化表结构，每个类型对应专门的表
    
    优势：
    - 支持 SQL 查询字段
    - 支持索引加速
    - 支持外键约束
    - 更好的数据完整性
    """

    _instance: PydanticSQLiteLoader | None = None
    _current_path: str = ""

    model_registry: dict[str, type[PydanticModelBase[Any]]] = {}
    type_registry: dict[str, type[ClassDataType]] = {}
    loaded_objects: dict[tuple[ClassDataTypeUUID[History] | None, str, UUID], ClassDataType] = {}
    loading_set: set[tuple[ClassDataTypeUUID[History] | None, str, UUID]] = set()

    def __new__(cls, path: str = "", database: UserDataBase | None = None) -> PydanticSQLiteLoader:
        if cls._instance is None or path != cls._current_path:
            cls._instance = super().__new__(cls)
            cls._current_path = path
        return cls._instance

    def __init__(self, path: str = "", database: UserDataBase | None = None):
        if hasattr(self, "initialized") and self.initialized:
            if path and path != self.current_path:
                self.set_path(path)
            if database:
                self.bound_db = database
            return

        self.current_path = path
        self.bound_db = database or UserDataBase()
        self.operating_history_uuid: ClassDataTypeUUID[History] | None = None
        self.is_batch_mode = False
        self.pending_saves: list[tuple[str, Any]] = []
        self.initialized = True
        self.connections: dict[str, sqlite3.Connection] = {}

        if path:
            os.makedirs(path, exist_ok=True)

        self.register_models()

    @classmethod
    def register_models(cls) -> None:
        """
        注册所有Pydantic模型。
        """
        from ...objects.datatag import DataTag
        from ...objects.student import Student
        from ...objects.scoremodtemplate import ScoreModificationTemplate
        from ...objects.scoremod import ScoreModification
        from ...objects.group import Group
        from ...objects.classtype import Class
        from ...objects.achievementtemp import AchievementTemplate
        from ...objects.achievement import Achievement
        from ...objects.attendanceinfo import AttendanceInfo
        from ...objects.dayrecord import DayRecord
        from ...objects.history import History
        from ...objects.homeworkrule import HomeworkRule

        from ..pydantic_loader.models import (
            DataTagModel,
            StudentModel,
            ScoreTemplateModel,
            ScoreModificationModel,
            GroupModel,
            ClassModel,
            AchievementTemplateModel,
            AchievementModel,
            AttendanceInfoModel,
            DayRecordModel,
            HistoryModel,
            HomeworkRuleModel,
        )

        model_mapping = {
            DataTag: DataTagModel,
            Student: StudentModel,
            ScoreModificationTemplate: ScoreTemplateModel,
            ScoreModification: ScoreModificationModel,
            Group: GroupModel,
            Class: ClassModel,
            AchievementTemplate: AchievementTemplateModel,
            Achievement: AchievementModel,
            AttendanceInfo: AttendanceInfoModel,
            DayRecord: DayRecordModel,
            History: HistoryModel,
            HomeworkRule: HomeworkRuleModel,
        }

        for obj_type, model_cls in model_mapping.items():
            cls.model_registry[obj_type.chunk_type_name] = model_cls
            cls.type_registry[obj_type.chunk_type_name] = obj_type
            register_type(obj_type)

    @property
    def current_path(self) -> str:
        return self._current_path

    @current_path.setter
    def current_path(self, value: str) -> None:
        if self._current_path and self._current_path != value:
            self.close_all_connections()
        self._current_path = value

    def close_all_connections(self) -> None:
        """
        关闭所有数据库连接。
        """
        import gc
        for _, conn in list(self.connections.items()):
            try:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                conn.close()
            except Exception:
                pass
        self.connections.clear()
        self.loaded_objects.clear()
        self.loading_set.clear()
        gc.collect()

    def write_identifier(self) -> None:
        """
        写入标识符文件。
        """
        identifier_path = os.path.join(self.current_path, IDENTIFIER_FILE)
        identifier_data = {
            "version": IDENTIFIER_VERSION,
            "type": "pydantic_sqlite",
        }
        with open(identifier_path, "w", encoding="utf-8") as f:
            json.dump(identifier_data, f)

    def _check_identifier(self) -> bool:
        """
        检查标识符文件是否存在。
        
        :return: 如果标识符文件存在返回 True，否则返回 False
        """
        identifier_path = os.path.join(self.current_path, IDENTIFIER_FILE)
        if not os.path.isfile(identifier_path):
            return False

        try:
            with open(identifier_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("type") == "pydantic_sqlite"
        except (json.JSONDecodeError, OSError):
            return False

    def get_connection(self, db_name: str = "main") -> sqlite3.Connection:
        """
        获取数据库连接。
        """
        if db_name not in self.connections:
            db_path = os.path.join(self.current_path, f"{db_name}.db")
            os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else self.current_path, exist_ok=True)
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            TableSchema.initialize_database(conn)
            self.connections[db_name] = conn
        return self.connections[db_name]

    def get_history_connection(self, history_uuid: ClassDataTypeUUID[History] | None) -> sqlite3.Connection:
        """
        获取历史记录数据库连接。
        """
        if history_uuid is None:
            return self.get_connection("current")
        return self.get_connection(f"history_{str(history_uuid)[:2]}")

    def set_path(self, path: str) -> None:
        """设置数据路径"""
        self.current_path = path
        os.makedirs(path, exist_ok=True)

    def set_uuid_loader(self, history_uuid: ClassDataTypeUUID[History] | None) -> None:
        """
        设置UUID加载器。
        """
        from ... import ClassDataLoader

        def _load_object(
            uuid: ClassDataTypeUUID[T] | None,
            type: type[T],
        ) -> T | None:
            if uuid is None:
                Base.log("W", "加载对象时UUID为None", "PydanticSQLiteLoader._load_object")
                return None

            cache_key = (history_uuid, type.chunk_type_name, uuid)

            if cache_key in self.loaded_objects:
                return cast(T, self.loaded_objects[cache_key])

            if cache_key in self.loading_set:
                if hasattr(type, 'new_dummy'):
                    return type.new_dummy()
                return None

            self.loading_set.add(cache_key)

            try:
                obj = self._load_from_db(uuid, type, history_uuid)
                self.loaded_objects[cache_key] = obj
                return obj
            except Exception as e:
                Base.log_exc(f"加载对象失败: {type.chunk_type_name}({uuid})", "PydanticSQLiteLoader._load_object", "E", e)
                if hasattr(type, 'new_dummy'):
                    dummy = type.new_dummy()
                    dummy.uuid = uuid
                    dummy.archive_uuid = history_uuid
                    self.loaded_objects[cache_key] = dummy
                    return dummy
                return None
            finally:
                self.loading_set.discard(cache_key)

        ClassDataLoader.LoadUUID = _load_object  # type: ignore[assignment]

    def _load_from_db(
        self,
        uuid: ClassDataTypeUUID[T],
        data_type: type[T],
        history_uuid: ClassDataTypeUUID[History] | None,
    ) -> T:
        """从数据库加载对象"""
        from typing import cast
        type_name = data_type.chunk_type_name
        conn = self.get_history_connection(history_uuid)

        if type_name == "Student":
            return cast(T, self._load_student(
                cast(ClassDataTypeUUID[Student], uuid), conn))
        elif type_name == "Class":
            return cast(T, self._load_class(
                cast(ClassDataTypeUUID[Class], uuid), conn))
        elif type_name == "Group":
            return cast(T, self._load_group(
                cast(ClassDataTypeUUID[Group], uuid), conn))
        elif type_name == "ScoreModification":
            return cast(T, self._load_score_modification(
                cast(ClassDataTypeUUID[ScoreModification], uuid), conn))
        elif type_name == "ScoreModificationTemplate":
            return cast(T, self._load_score_template(
                cast(ClassDataTypeUUID[ScoreModificationTemplate], uuid), conn))
        elif type_name == "Achievement":
            return cast(T, self._load_achievement(
                cast(ClassDataTypeUUID[Achievement], uuid), conn))
        elif type_name == "AchievementTemplate":
            return cast(T, self._load_achievement_template(
                cast(ClassDataTypeUUID[AchievementTemplate], uuid), conn))
        elif type_name == "DataTag":
            return cast(T, self._load_data_tag(
                cast(ClassDataTypeUUID[DataTag], uuid), conn))
        else:
            raise ValueError(f"未知的类型: {type_name}")

    def _load_student(self, uuid: ClassDataTypeUUID[Student], conn: sqlite3.Connection) -> Student:
        """
        从数据库加载学生。
        """
        from ...objects import Student

        row = conn.execute(
            "SELECT * FROM students WHERE uuid = ?", (str(uuid),)
        ).fetchone()

        if not row:
            raise FileNotFoundError(f"学生不存在: {uuid}")

        student = Student(
            name=row["name"],
            num=row["num"],
            score=row["score"],
            belongs_to=row["class_key"],
            total_score=row["total_score"],
            highest_score=row["highest_score"],
            lowest_score=row["lowest_score"],
            highest_score_cause_time=row["highest_score_cause_time"],
            lowest_score_cause_time=row["lowest_score_cause_time"],
            belongs_to_group=row["group_key"],
            last_reset=row["last_reset"],
        )
        student.uuid = uuid

        tags = conn.execute(
            "SELECT tag_uuid FROM student_tags WHERE student_uuid = ?", (str(uuid),)
        ).fetchall()
        for tag_row in tags:
            from ...objects import DataTag
            tag_uuid = ClassDataTypeUUID(DataTag, UUID(tag_row["tag_uuid"]))
            tag = self.load_object(tag_uuid, DataTag)
            if tag:
                student.tags.append(tag)

        achievements = conn.execute(
            "SELECT achievement_uuid FROM student_achievements WHERE student_uuid = ?", (str(uuid),)
        ).fetchall()
        for ach_row in achievements:
            from ...objects import Achievement
            ach_uuid = ClassDataTypeUUID(Achievement, UUID(ach_row["achievement_uuid"]))
            ach = self.load_object(ach_uuid, Achievement)
            if ach:
                student.achievements[ach.time_key] = ach

        score_mods = conn.execute(
            "SELECT score_mod_uuid FROM student_score_mods WHERE student_uuid = ?", (str(uuid),)
        ).fetchall()
        for sm_row in score_mods:
            from ...objects import ScoreModification
            sm_uuid = ClassDataTypeUUID(ScoreModification, UUID(sm_row["score_mod_uuid"]))
            sm = self.load_object(sm_uuid, ScoreModification)
            if sm:
                student.history[sm.execute_time_key] = sm

        return student

    def _load_class(self, uuid: ClassDataTypeUUID[Class], conn: sqlite3.Connection) -> Class:
        """
        从数据库加载班级。
        """
        from ...objects import Class, Group, Student

        row = conn.execute(
            "SELECT * FROM classes WHERE uuid = ?", (str(uuid),)
        ).fetchone()

        if not row:
            raise FileNotFoundError(f"班级不存在: {uuid}")

        cleaning_mapping = None
        if row["cleaning_mapping"]:
            cleaning_mapping = json.loads(row["cleaning_mapping"])

        homework_rules: list[tuple[str, str]] = []
        if row["homework_rules"]:
            homework_rules = json.loads(row["homework_rules"])


        obj = Class(
            name=row["name"],
            owner=row["owner"],
            key=row["key"],
            students={},
            groups={},
            cleaning_mapping=Class.load_cleaning_mapping(cleaning_mapping),
            homework_rules=Class.load_homework_rules(homework_rules),
        )
        obj.uuid = uuid

        students = conn.execute(
            "SELECT student_num, student_uuid FROM class_students WHERE class_uuid = ?", (str(uuid),)
        ).fetchall()
        for stu_row in students:
            stu_uuid = ClassDataTypeUUID(Student, UUID(stu_row["student_uuid"]))
            stu = self.load_object(stu_uuid, Student)
            if stu:
                obj.students[stu_row["student_num"]] = stu

        groups = conn.execute(
            "SELECT group_key, group_uuid FROM class_groups WHERE class_uuid = ?", (str(uuid),)
        ).fetchall()
        for grp_row in groups:
            grp_uuid = ClassDataTypeUUID(Group, UUID(grp_row["group_uuid"]))
            grp = self.load_object(grp_uuid, Group)
            if grp:
                obj.groups[grp_row["group_key"]] = grp

        return obj

    def _load_group(self, uuid: ClassDataTypeUUID[Group], conn: sqlite3.Connection) -> Group:
        """
        从数据库加载小组。
        """
        from ...objects import Group, Student

        row = conn.execute(
            "SELECT * FROM groups WHERE uuid = ?", (str(uuid),)
        ).fetchone()

        if not row:
            raise FileNotFoundError(f"小组不存在: {uuid}")

        leader = None
        if row["leader_uuid"]:
            leader_uuid = ClassDataTypeUUID(Student, UUID(row["leader_uuid"]))
            leader = self.load_object(leader_uuid, Student)

        members: list[Student] = []
        member_rows = conn.execute(
            "SELECT student_uuid FROM group_members WHERE group_uuid = ?", (str(uuid),)
        ).fetchall()
        for m_row in member_rows:
            m_uuid = ClassDataTypeUUID(Student, UUID(m_row["student_uuid"]))
            m = self.load_object(m_uuid, Student)
            if m:
                members.append(m)

        assert leader, f"小组{uuid}没有指定组长"
        
        obj = Group(
            key=row["key"],
            name=row["name"],
            leader=leader,
            members=members,
            belongs_to=row["class_key"],
            further_desc=row["description"],
        )
        obj.uuid = uuid

        tags = conn.execute(
            "SELECT tag_uuid FROM group_tags WHERE group_uuid = ?", (str(uuid),)
        ).fetchall()
        for tag_row in tags:
            from ...objects import DataTag
            tag_uuid = ClassDataTypeUUID(DataTag, UUID(tag_row["tag_uuid"]))
            tag = self.load_object(tag_uuid, DataTag)
            if tag:
                obj.tags.append(tag)

        return obj

    def _load_score_modification(self, uuid: ClassDataTypeUUID[ScoreModification], conn: sqlite3.Connection) -> ScoreModification:
        """
        从数据库加载分数修改记录。
        """
        from ...objects import ScoreModification, ScoreModificationTemplate, Student

        row = conn.execute(
            "SELECT * FROM score_modifications WHERE uuid = ?", (str(uuid),)
        ).fetchone()

        if not row:
            raise FileNotFoundError(f"分数修改记录不存在: {uuid}")

        template = None
        if row["template_uuid"]:
            template_uuid = ClassDataTypeUUID(ScoreModificationTemplate, UUID(row["template_uuid"]))
            template = self.load_object(template_uuid, ScoreModificationTemplate)

        target = None
        if row["student_uuid"]:
            target_uuid = ClassDataTypeUUID(Student, UUID(row["student_uuid"]))
            target = self.load_object(target_uuid, Student)

        assert template, f"分数修改记录{uuid}没有指定模板"
        assert target, f"分数修改记录{uuid}没有指定目标学生"

        obj = ScoreModification(
            template=template,
            target=target,
            title=row["title"],
            desc=row["description"],
            mod=row["modification"],
            execute_time=row["execute_time"],
            create_time=row["create_time"],
            executed=bool(row["executed"]),
        )
        obj.uuid = uuid
        obj.execute_time_key = row["execute_time_key"]

        return obj

    def _load_score_template(self, uuid: ClassDataTypeUUID[ScoreModificationTemplate], conn: sqlite3.Connection) -> ScoreModificationTemplate:
        """
        从数据库加载分数模板。
        """
        from ...objects import ScoreModificationTemplate

        row = conn.execute(
            "SELECT * FROM score_templates WHERE uuid = ?", (str(uuid),)
        ).fetchone()

        if not row:
            raise FileNotFoundError(f"分数模板不存在: {uuid}")

        obj = ScoreModificationTemplate(
            key=row["key"],
            modification=row["modification"],
            title=row["title"],
            description=row["description"],
            cant_replace=bool(row["cant_replace"]),
            is_visible=bool(row["is_visible"]),
        )
        obj.uuid = uuid

        return obj

    def _load_achievement(self, uuid: ClassDataTypeUUID[Achievement], conn: sqlite3.Connection) -> Achievement:
        """从数据库加载成就"""
        from ...objects import Achievement, AchievementTemplate, Student

        row = conn.execute(
            "SELECT * FROM achievements WHERE uuid = ?", (str(uuid),)
        ).fetchone()

        if not row:
            raise FileNotFoundError(f"成就不存在: {uuid}")

        template_uuid = ClassDataTypeUUID(AchievementTemplate, UUID(row["template_uuid"]))
        template = self.load_object(template_uuid, AchievementTemplate)

        target_uuid = ClassDataTypeUUID(Student, UUID(row["student_uuid"]))
        target = self.load_object(target_uuid, Student)

        assert template, f"成就{uuid}没有指定模板"
        assert target, f"成就{uuid}没有指定目标学生"

        obj = Achievement(
            template=template,
            target=target,
            reach_time=row["time"],
            reach_time_key=row["time_key"],
        )
        obj.uuid = uuid
        obj.sound = row["sound"]

        return obj

    def _load_achievement_template(self, uuid: ClassDataTypeUUID[AchievementTemplate], conn: sqlite3.Connection) -> AchievementTemplate:
        """
        从数据库加载成就模板。
        """
        from ...objects import AchievementTemplate
        from utils.basetypes import Base

        row = conn.execute(
            "SELECT * FROM achievement_templates WHERE uuid = ?", (str(uuid),)
        ).fetchone()

        if not row:
            raise FileNotFoundError(f"成就模板不存在: {uuid}")

        kwargs: dict[str, Any] = {
            "key": row["key"],
            "name": row["name"],
            "desc": row["description"],
            "when_triggered": json.loads(row["when_triggered"]) if row["when_triggered"] else ["any"],
            "sound": row["sound"],
            "icon": row["icon"],
            "condition_info": row["condition_info"],
            "further_info": row["further_info"],
        }

        if row["name_equals"]:
            kwargs["name_equals"] = json.loads(row["name_equals"])
        if row["name_not_equals"]:
            kwargs["name_not_equals"] = json.loads(row["name_not_equals"])
        if row["num_equals"]:
            kwargs["num_equals"] = json.loads(row["num_equals"])
        if row["num_not_equals"]:
            kwargs["num_not_equals"] = json.loads(row["num_not_equals"])
        if row["score_range"]:
            score_range_data = json.loads(row["score_range"])
            if score_range_data:
                kwargs["score_range"] = [tuple(x) for x in score_range_data]
        if row["score_rank_range"]:
            score_rank_data = json.loads(row["score_rank_range"])
            if score_rank_data:
                kwargs["score_rank_range"] = tuple(score_rank_data)
        if row["highest_score_range"]:
            highest_score_data = json.loads(row["highest_score_range"])
            if highest_score_data:
                kwargs["highest_score_range"] = tuple(highest_score_data)
        if row["lowest_score_range"]:
            lowest_score_data = json.loads(row["lowest_score_range"])
            if lowest_score_data:
                kwargs["lowest_score_range"] = tuple(lowest_score_data)
        if row["highest_score_cause_range"]:
            highest_cause_data = json.loads(row["highest_score_cause_range"])
            if highest_cause_data:
                kwargs["highest_score_cause_range"] = tuple(highest_cause_data)
        if row["lowest_score_cause_range"]:
            lowest_cause_data = json.loads(row["lowest_score_cause_range"])
            if lowest_cause_data:
                kwargs["lowest_score_cause_range"] = tuple(lowest_cause_data)
        if row["modify_key_range"]:
            modify_key_data = json.loads(row["modify_key_range"])
            if modify_key_data:
                kwargs["modify_key_range"] = [tuple(x) for x in modify_key_data]
        if row["others"]:
            try:
                kwargs["others"] = pickle.loads(base64.b64decode(row["others"])) # type: ignore
            except SystemError as e:
                if e.args[0] == "unknown opcode":
                    Base.log(
                        "E",
                        "由于版本变化，无法加载lambda，请手动修改",
                        "PydanticSQLiteLoader._load_achievement_template",
                    )
                else:
                    raise

        obj = AchievementTemplate(**kwargs)
        obj.uuid = uuid
        obj.active = bool(row["active"])

        return obj

    def _load_data_tag(self, uuid: ClassDataTypeUUID[DataTag], conn: sqlite3.Connection) -> DataTag:
        """
        从数据库加载数据标签。
        """
        from ...objects import DataTag

        row = conn.execute(
            "SELECT * FROM data_tags WHERE uuid = ?", (str(uuid),)
        ).fetchone()

        if not row:
            raise FileNotFoundError(f"数据标签不存在: {uuid}")

        obj = DataTag(
            key=row["key"],
            data=json.loads(row["data"]) if row["data"] else None,
        )
        obj.uuid = uuid

        return obj

    def load_object(
        self,
        uuid: ClassDataTypeUUID[T],
        data_type: type[T],
        history_uuid: ClassDataTypeUUID[History] | None = None,
    ) -> T | None:
        """
        加载单个对象。
        """
        cache_key = (history_uuid, data_type.chunk_type_name, uuid)

        if cache_key in self.loaded_objects:
            return cast(T, self.loaded_objects[cache_key])

        if cache_key in self.loading_set:
            if hasattr(data_type, 'new_dummy'):
                return data_type.new_dummy()
            return None

        self.loading_set.add(cache_key)

        old_history_uuid = self.operating_history_uuid
        if history_uuid:
            self.operating_history_uuid = history_uuid

        try:
            self.set_uuid_loader(self.operating_history_uuid)
            obj = self._load_from_db(uuid, data_type, self.operating_history_uuid)
            self.loaded_objects[cache_key] = obj
            return obj
        except Exception as e:
            Base.log_exc(f"加载对象失败: {data_type.chunk_type_name}({uuid})", "PydanticSQLiteLoader.load_object", "E", e)
            if hasattr(data_type, 'new_dummy'):
                dummy = data_type.new_dummy()
                dummy.uuid = uuid
                self.loaded_objects[cache_key] = dummy
                return dummy
            return None
        finally:
            self.loading_set.discard(cache_key)
            self.operating_history_uuid = old_history_uuid

    def save_object(self, obj: ClassDataType) -> None:
        """保存对象到数据库"""
        type_name = obj.chunk_type_name

        if self.is_batch_mode:
            self.pending_saves.append((type_name, obj))
            return

        conn = self.get_history_connection(self.operating_history_uuid)
        self._save_to_db(conn, obj)
        conn.commit()

    def _save_to_db(self, conn: sqlite3.Connection, obj: ClassDataType) -> None:
        """保存对象到数据库"""
        type_name = obj.chunk_type_name

        if type_name == "Student":
            self._save_student(conn, cast(Student, obj))
        elif type_name == "Class":
            self._save_class(conn, cast(Class, obj))
        elif type_name == "Group":
            self._save_group(conn, cast(Group, obj))
        elif type_name == "ScoreModification":
            self._save_score_modification(conn, cast(ScoreModification, obj))
        elif type_name == "ScoreModificationTemplate":
            self._save_score_template(conn, cast(ScoreModificationTemplate, obj))
        elif type_name == "Achievement":
            self._save_achievement(conn, cast(Achievement, obj))    
        elif type_name == "AchievementTemplate":
            self._save_achievement_template(conn, cast(AchievementTemplate, obj))
        elif type_name == "DataTag":
            self._save_data_tag(conn, cast(DataTag, obj))

    def _find_parent_class_uuid(self, obj: ClassDataType) -> UUID | None:
        """查找对象所属的班级UUID"""
        row = self.get_connection("current").execute(
            "SELECT class_uuid FROM class_students WHERE student_uuid = ?",
            (str(obj.uuid),)
        ).fetchone()
        if row:
            return UUID(row["class_uuid"])
        
        row = self.get_connection("current").execute(
            "SELECT class_uuid FROM class_groups WHERE group_uuid = ?",
            (str(obj.uuid),)
        ).fetchone()
        if row:
            return UUID(row["class_uuid"])
        
        return None

    def _find_class_uuid_by_key(self, class_key: str) -> UUID | None:
        """通过班级key查找班级UUID"""
        row = self.get_connection("current").execute(
            "SELECT uuid FROM classes WHERE key = ?",
            (class_key,)
        ).fetchone()
        if row:
            return UUID(row["uuid"])
        return None

    def _save_data_tag(self, conn: sqlite3.Connection, tag: DataTag) -> None:
        """
        保存数据标签到数据库。
        """
        conn.execute("""
            INSERT OR REPLACE INTO data_tags (uuid, key, data, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            str(tag.uuid),
            tag.key,
            json.dumps(tag.data) if tag.data else None,
        ))

    def _save_student(self, conn: sqlite3.Connection, student: Student) -> None:
        """
        保存学生到数据库。
        """

        conn.execute("""
            INSERT OR REPLACE INTO students 
            (uuid, class_uuid, class_key, name, num, score, total_score, 
             highest_score, lowest_score, highest_score_cause_time, lowest_score_cause_time,
             group_uuid, group_key, last_reset, last_reset_info_uuid, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            str(student.uuid),
            str(student.uuid),
            student.belongs_to,
            student.name,
            student.num,
            student.score,
            student.total_score,
            student.highest_score,
            student.lowest_score,
            student.highest_score_cause_time,
            student.lowest_score_cause_time,
            None,
            student.belongs_to_group,
            student.last_reset,
            str(student.last_reset_info.uuid) if student.last_reset_info else None,
        ))

        conn.execute("DELETE FROM student_tags WHERE student_uuid = ?", (str(student.uuid),))
        for tag in student.tags:
            conn.execute(
                "INSERT OR IGNORE INTO student_tags (student_uuid, tag_uuid) VALUES (?, ?)",
                (str(student.uuid), str(tag.uuid))
            )
            self.save_object(tag)

        conn.execute("DELETE FROM student_achievements WHERE student_uuid = ?", (str(student.uuid),))
        for ach in student.achievements.values():
            conn.execute(
                "INSERT OR IGNORE INTO student_achievements (student_uuid, achievement_uuid) VALUES (?, ?)",
                (str(student.uuid), str(ach.uuid))
            )
            self.save_object(ach)

        conn.execute("DELETE FROM student_score_mods WHERE student_uuid = ?", (str(student.uuid),))
        for sm in student.history.values():
            conn.execute(
                "INSERT OR IGNORE INTO student_score_mods (student_uuid, score_mod_uuid) VALUES (?, ?)",
                (str(student.uuid), str(sm.uuid))
            )
            self.save_object(sm)

    def _save_class(self, conn: sqlite3.Connection, cls: Class) -> None:
        """
        保存班级到数据库。
        """
        cleaning_mapping_json = json.dumps(cls.dump_cleaning_mapping()) if cls.cleaning_mapping else None
        homework_rules_json = json.dumps(cls.dump_homework_rules()) if cls.homework_rules else None

        conn.execute("""
            INSERT OR REPLACE INTO classes 
            (uuid, name, owner, key, cleaning_mapping, homework_rules, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            str(cls.uuid),
            cls.name,
            cls.owner,
            cls.key,
            cleaning_mapping_json,
            homework_rules_json,
        ))

        conn.execute("DELETE FROM class_students WHERE class_uuid = ?", (str(cls.uuid),))
        for num, student in cls.students.items():
            conn.execute(
                "INSERT OR REPLACE INTO class_students (class_uuid, student_num, student_uuid) VALUES (?, ?, ?)",
                (str(cls.uuid), num, str(student.uuid))
            )
            self.save_object(student)

        conn.execute("DELETE FROM class_groups WHERE class_uuid = ?", (str(cls.uuid),))
        for key, group in cls.groups.items():
            conn.execute(
                "INSERT OR REPLACE INTO class_groups (class_uuid, group_key, group_uuid) VALUES (?, ?, ?)",
                (str(cls.uuid), key, str(group.uuid))
            )
            self.save_object(group)

    def _save_group(self, conn: sqlite3.Connection, group: Group) -> None:
        """保存小组到数据库"""
        class_uuid = self._find_class_uuid_by_key(group.belongs_to)
        
        conn.execute("""
            INSERT OR REPLACE INTO groups 
            (uuid, class_uuid, class_key, key, name, leader_uuid, description, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            str(group.uuid),
            str(class_uuid) if class_uuid else None,
            group.belongs_to,
            group.key,
            group.name,
            str(group.leader.uuid) if group.leader else None,
            group.further_desc,
        ))

        conn.execute("DELETE FROM group_members WHERE group_uuid = ?", (str(group.uuid),))
        for member in group.members:
            conn.execute(
                "INSERT OR IGNORE INTO group_members (group_uuid, student_uuid) VALUES (?, ?)",
                (str(group.uuid), str(member.uuid))
            )

        conn.execute("DELETE FROM group_tags WHERE group_uuid = ?", (str(group.uuid),))
        for tag in group.tags:
            conn.execute(
                "INSERT OR IGNORE INTO group_tags (group_uuid, tag_uuid) VALUES (?, ?)",
                (str(group.uuid), str(tag.uuid))
            )

    def _save_score_modification(self, conn: sqlite3.Connection, sm: ScoreModification) -> None:
        """
        保存分数修改记录到数据库。
        """
        conn.execute("""
            INSERT OR REPLACE INTO score_modifications 
            (uuid, student_uuid, template_uuid, title, description, modification, 
             executed, execute_time, execute_time_key, create_time, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            str(sm.uuid),
            str(sm.target.uuid) if sm.target else None,
            str(sm.temp.uuid) if sm.temp else None,
            sm.title,
            sm.desc,
            sm.mod,
            1 if sm.executed else 0,
            sm.execute_time,
            sm.execute_time_key,
            sm.create_time,
        ))

    def _save_score_template(self, conn: sqlite3.Connection, template: ScoreModificationTemplate, order_index: int = 0) -> None:
        """
        保存分数模板到数据库。
        """
        conn.execute("""
            INSERT OR REPLACE INTO score_templates 
            (uuid, key, title, description, modification, is_visible, cant_replace, order_index, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            str(template.uuid),
            template.key,
            template.title,
            template.desc,
            template.mod,
            1 if template.is_visible else 0,
            1 if template.cant_replace else 0,
            order_index,
        ))

    def _save_achievement(self, conn: sqlite3.Connection, ach: Achievement) -> None:
        """
        保存成就到数据库。
        """
        conn.execute("""
            INSERT OR REPLACE INTO achievements 
            (uuid, student_uuid, template_uuid, time, time_key, sound, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            str(ach.uuid),
            str(ach.target.uuid) if ach.target else None,
            str(ach.temp.uuid) if ach.temp else None,
            ach.time,
            ach.time_key,
            ach.sound,
        ))

    def _save_achievement_template(self, conn: sqlite3.Connection, template: AchievementTemplate) -> None:
        """
        保存成就模板到数据库。
        """
        score_rank_range = None
        if template.score_rank_down_limit is not None and template.score_rank_up_limit is not None:
            score_rank_range = [template.score_rank_down_limit, template.score_rank_up_limit]

        highest_score_range = None
        if template.highest_score_down_limit is not None and template.highest_score_up_limit is not None:
            highest_score_range = [template.highest_score_down_limit, template.highest_score_up_limit]

        lowest_score_range = None
        if template.lowest_score_down_limit is not None and template.lowest_score_up_limit is not None:
            lowest_score_range = [template.lowest_score_down_limit, template.lowest_score_up_limit]

        highest_score_cause_range = None
        if template.highest_score_cause_range_down_limit is not None and template.highest_score_cause_range_up_limit is not None:
            highest_score_cause_range = [template.highest_score_cause_range_down_limit, template.highest_score_cause_range_up_limit]

        lowest_score_cause_range = None
        if template.lowest_score_cause_range_down_limit is not None and template.lowest_score_cause_range_up_limit is not None:
            lowest_score_cause_range = [template.lowest_score_cause_range_down_limit, template.lowest_score_cause_range_up_limit]

        others_serialized = None
        if template.other:
            others_serialized = base64.b64encode(
                pickle.dumps(template.other, protocol=pickle.HIGHEST_PROTOCOL) # type: ignore
            ).decode()

        conn.execute("""
            INSERT OR REPLACE INTO achievement_templates 
            (uuid, key, name, description, active, when_triggered, sound, icon,
             condition_info, further_info, name_equals, name_not_equals,
             num_equals, num_not_equals, score_range, score_rank_range,
             highest_score_range, lowest_score_range, highest_score_cause_range,
             lowest_score_cause_range, modify_key_range, others, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            str(template.uuid),
            template.key,
            template.name,
            template.desc,
            1 if template.active else 0,
            json.dumps(template.when_triggered),
            template.sound,
            template.icon,
            template.condition_info,
            template.further_info,
            json.dumps(template.name_eq) if template.name_eq else None,
            json.dumps(template.name_ne) if template.name_ne else None,
            json.dumps(template.num_eq) if template.num_eq else None,
            json.dumps(template.num_ne) if template.num_ne else None,
            json.dumps(template.score_range) if template.score_range else None,
            json.dumps(score_rank_range),
            json.dumps(highest_score_range),
            json.dumps(lowest_score_range),
            json.dumps(highest_score_cause_range),
            json.dumps(lowest_score_cause_range),
            json.dumps(template.modify_ranges_orig) if template.modify_ranges_orig else None,
            others_serialized,
        ))

    def batch_mode(self) -> BatchContextManager:
        """
        进入批量保存模式。
        """
        return BatchContextManager(self)

    def flush_pending_saves(self) -> None:
        """
        刷新待保存的对象。
        """
        if not self.pending_saves:
            return

        conn = self.get_history_connection(self.operating_history_uuid)
        try:
            for _, obj in self.pending_saves:
                self._save_to_db(conn, obj)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e

        self.pending_saves.clear()

    def load_data(self, load_all: bool = False) -> UserDataBase:
        """
        加载数据。

        :param load_all: 是否加载所有历史记录，默认为False
        """
        if not self._check_identifier():
            raise FileNotFoundError(
                f"数据目录不存在或不是有效的 PydanticSQLite 数据目录: {self.current_path}"
            )

        from ...objects import AchievementTemplate, ScoreModificationTemplate

        self.set_uuid_loader(None)
        conn = self.get_connection("current")

        current_record = self._load_history(None, conn)

        templates: list[ScoreModificationTemplate] = []
        template_rows = conn.execute("SELECT uuid FROM score_templates ORDER BY order_index").fetchall()
        for row in template_rows:
            from ...objects import ScoreModificationTemplate
            template_uuid = ClassDataTypeUUID(ScoreModificationTemplate, UUID(row["uuid"]))
            template = self.load_object(template_uuid, ScoreModificationTemplate)
            if template:
                templates.append(template)

        achievements: list[AchievementTemplate] = []
        achievement_rows = conn.execute("SELECT uuid FROM achievement_templates").fetchall()
        for row in achievement_rows:
            from ...objects import AchievementTemplate
            ach_uuid = ClassDataTypeUUID(AchievementTemplate, UUID(row["uuid"]))
            ach = self.load_object(ach_uuid, AchievementTemplate)
            if ach:
                achievements.append(ach)

        current_day_attendance: dict[str, AttendanceInfo] = {}

        info_row = conn.execute(
            "SELECT * FROM meta WHERE key IN ('user', 'save_time', 'version', 'version_code', 'last_reset', 'last_start_time')"
        ).fetchall()
        info = {row["key"]: row["value"] for row in info_row}

        histories: dict[float, History] = {}
        if load_all:
            history_rows = conn.execute("SELECT uuid FROM histories").fetchall()
            for row in history_rows:
                from ...objects import History
                history_uuid = ClassDataTypeUUID(History, UUID(row["uuid"]))
                h = self._load_history(history_uuid, self.get_history_connection(history_uuid))
                while h.time in histories:
                    h.time += 0.000001
                histories[h.time] = h

            histories = dict(sorted(histories.items(), key=lambda i: i[0]))

        return UserDataBase(
            info.get("user", ""),
            float(info.get("save_time", 0)),
            info.get("version", ""),
            int(info.get("version_code", 0)),
            float(info.get("last_reset", 0)),
            histories,
            current_record.classes,
            OrderedDict({t.key: t for t in templates}),
            {a.key: a for a in achievements},
            float(info.get("last_start_time", 0)),
            current_record.weekdays,
            current_day_attendance,
        )

    def _load_history(
        self,
        history_uuid: ClassDataTypeUUID[History] | None,
        conn: sqlite3.Connection,
    ) -> History:
        """
        加载历史记录。

        :param history_uuid: 历史记录UUID
        :param conn: 数据库连接
        :return: 历史记录对象
        """
        from ...objects import Class, History

        if history_uuid is None:
            history = History({}, {})
            history.uuid = None

            class_rows = conn.execute(
                "SELECT key AS class_key, uuid AS class_uuid FROM classes"
            ).fetchall()
        else:
            row = conn.execute(
                "SELECT * FROM histories WHERE uuid = ?", (str(history_uuid),)
            ).fetchone()

            if not row:
                history = History({}, {})
                history.uuid = history_uuid
                return history

            history = History({}, {}, row["time"])
            history.uuid = history_uuid

            class_rows = conn.execute(
                "SELECT class_key, class_uuid FROM history_classes WHERE history_uuid = ?",
                (str(history_uuid),)
            ).fetchall()

        for cls_row in class_rows:
            cls_uuid = ClassDataTypeUUID(Class, UUID(cls_row["class_uuid"]))
            cls = self.load_object(cls_uuid, Class, history_uuid)
            if cls:
                history.classes[cls_row["class_key"]] = cls

        return history

    def save_data(
        self,
        save_history: bool = True,
        save_only_if_not_exist: bool = True,
        clear_current: bool = False,
        clear_histories: bool = False,
    ) -> None:
        """
        保存数据。

        :param save_history: 是否保存历史记录，默认为True
        :param save_only_if_not_exist: 是否仅在不存在时保存，默认为True
        :param clear_current: 是否清空当前状态，默认为False
        :param clear_histories: 是否清空所有历史记录，默认为False
        """
        if clear_histories:
            for db_file in os.listdir(self.current_path):
                if db_file.startswith("history_") and db_file.endswith(".db"):
                    os.remove(os.path.join(self.current_path, db_file))

        conn = self.get_connection("current")

        if save_history:
            self.save_history(conn)

        self._save_main_info(conn)

        with self.batch_mode():
            for idx, template in enumerate(self.bound_db.templates.values()):
                self._save_score_template(conn, template, idx)
            for achievement in self.bound_db.achievements.values():
                self.save_object(achievement)

        conn.commit()

        self.write_identifier()

    def save_history(self, conn: sqlite3.Connection) -> None:
        """
        保存当前状态为历史记录。
        """
        from ...objects import History

        history = History(self.bound_db.classes, self.bound_db.weekday_record)
        if history.uuid is None:
            return

        conn.execute(
            "INSERT OR REPLACE INTO histories (uuid, time) VALUES (?, ?)",
            (str(history.uuid), history.time)
        )

        for cls_key, cls in history.classes.items():
            conn.execute(
                "INSERT OR REPLACE INTO history_classes (history_uuid, class_key, class_uuid) VALUES (?, ?, ?)",
                (str(history.uuid), cls_key, str(cls.uuid))
            )
            self.save_object(cls)

    def _save_main_info(self, conn: sqlite3.Connection) -> None:
        """
        保存主数据库信息。
        """
        info_items = [
            ("user", self.bound_db.user),
            ("save_time", str(self.bound_db.save_time)),
            ("version", self.bound_db.version),
            ("version_code", str(self.bound_db.version_code)),
            ("last_reset", str(self.bound_db.last_reset)),
            ("last_start_time", str(self.bound_db.last_start_time)),
        ]

        for key, value in info_items:
            conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                (key, value)
            )

    def create_history(self) -> ClassDataTypeUUID[History]:
        """
        创建历史记录存档。
        """
        from ...objects import History

        history = History(self.bound_db.classes, self.bound_db.weekday_record)
        if history.uuid is None:
            raise RuntimeError("历史记录UUID不能为None")

        conn = self.get_history_connection(history.uuid)
        conn.execute(
            "INSERT OR REPLACE INTO histories (uuid, time) VALUES (?, ?)",
            (str(history.uuid), history.time)
        )

        for cls_key, cls in history.classes.items():
            conn.execute(
                "INSERT OR REPLACE INTO history_classes (history_uuid, class_key, class_uuid) VALUES (?, ?, ?)",
                (str(history.uuid), cls_key, str(cls.uuid))
            )
            self.save_object(cls)

        conn.commit()
        return history.uuid

    def list_histories(self) -> list[ClassDataTypeUUID[History]]:
        """
        列出所有历史记录。

        :return: 所有历史记录UUID列表
        """
        from ...objects import History

        conn = self.get_connection("current")
        rows = conn.execute("SELECT uuid FROM histories").fetchall()
        return [ClassDataTypeUUID(History, UUID(row["uuid"])) for row in rows]

    def del_history(self, history_uuid: ClassDataTypeUUID[History]) -> bool:
        """
        删除历史记录。

        :param history_uuid: 要删除的历史记录UUID
        :return: 是否成功删除（其实是Literal[True]）
        """
        conn = self.get_connection("current")
        conn.execute("DELETE FROM histories WHERE uuid = ?", (str(history_uuid),))
        conn.commit()
        return True

    def close_connections(self) -> None:
        """
        关闭所有数据库连接。
        """
        self.close_all_connections()

    def get_current_save_dir(self) -> str:
        """
        获取当前保存目录。

        :return: 当前保存目录路径
        """
        return self.current_path

    def load_history(
        self,
        history_uuid: ClassDataTypeUUID[History] | None = None,
    ) -> History:
        """
        加载历史记录。

        :param history_uuid: 历史记录UUID，None表示当前存档
        :return: 历史记录对象
        """
        from ...objects import Class, History

        if history_uuid is None:
            conn = self.get_connection("current")
            time_val: float | None = None
        else:
            conn = self.get_history_connection(history_uuid)
            row = conn.execute(
                "SELECT * FROM histories WHERE uuid = ?", (str(history_uuid),)
            ).fetchone()
            if row is None:
                raise FileNotFoundError(f"历史记录不存在: {history_uuid}")
            time_val = row["time"] if row else None

        self.set_uuid_loader(history_uuid)

        classes: dict[str, Class] = {}
        if history_uuid is None:
            class_rows = conn.execute(
                "SELECT key AS class_key, uuid AS class_uuid FROM classes"
            ).fetchall()
        else:
            class_rows = conn.execute(
                "SELECT class_key, class_uuid FROM history_classes WHERE history_uuid = ?",
                (str(history_uuid),)
            ).fetchall()

        for cls_row in class_rows:
            cls_uuid = ClassDataTypeUUID(Class, UUID(cls_row["class_uuid"]))
            cls = self.load_object(cls_uuid, Class, history_uuid)
            if cls:
                classes[cls_row["class_key"]] = cls

        if history_uuid is None:
            history = History(classes, {})
        else:
            history = History(classes, {}, float(time_val) if time_val else None)
            history.uuid = history_uuid
            history.archive_uuid = history_uuid

        return history

    @staticmethod
    def get_chunk(path: str, database: UserDataBase | None = None) -> PydanticSQLiteLoader:
        """
        获取加载器实例。

        :param path: 数据库文件路径
        :param database: 用户数据数据库实例，None表示默认数据库
        :return: 加载器实例
        """
        loader = PydanticSQLiteLoader(path, database)
        loader.register_models()
        return loader

    @staticmethod
    def get_instance() -> PydanticSQLiteLoader:
        """
        获取单例实例。

        :return: 单例加载器实例
        """
        if PydanticSQLiteLoader._instance is None:
            raise RuntimeError("PydanticSQLiteLoader 尚未初始化")
        return PydanticSQLiteLoader._instance

    @staticmethod
    def commit_changes(clear_dataobj_connections: bool = True) -> None:
        """
        提交所有更改。

        :param clear_dataobj_connections: 是否清除数据对象连接，默认True
        """
        loader = PydanticSQLiteLoader.get_instance()
        loader.flush_pending_saves()
        for conn in loader.connections.values():
            conn.commit()


class BatchContextManager:
    """
    批量操作上下文管理器。

    用于在批量操作中临时开启批量模式，批量模式下所有操作都不会立即执行，
    而是在退出上下文管理器时统一提交。
    """

    def __init__(self, loader: PydanticSQLiteLoader):
        """
        初始化批量操作上下文管理器。

        :param loader: 加载器实例
        """
        self.loader = loader

    def __enter__(self) -> PydanticSQLiteLoader:
        """
        进入上下文管理器，开启批量模式。

        :return: 加载器实例
        """
        self.loader.is_batch_mode = True
        return self.loader

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        退出上下文管理器，关闭批量模式。

        :param exc_type: 异常类型
        :param exc_val: 异常值
        :param exc_tb: 异常跟踪
        """
        self.loader.is_batch_mode = False
        if exc_type is None:
            self.loader.flush_pending_saves()
        else:
            self.loader.pending_saves.clear()
