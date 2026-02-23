"""
PydanticSQLiteLoader 集成测试。
"""

import os
import shutil
import tempfile
import unittest

from utils.classobjects.objects.student import Student
from utils.classobjects.objects.classtype import Class
from utils.classobjects.objects.group import Group
from utils.classobjects.objects.scoremodtemplate import ScoreModificationTemplate
from utils.classobjects.objects.scoremod import ScoreModification
from utils.classobjects.objects.achievementtemp import AchievementTemplate
from utils.classobjects.objects.achievement import Achievement
from utils.classobjects.objects.datatag import DataTag
from utils.classobjects.dataloaders.pydantic_sqlite import PydanticSQLiteLoader
from utils.classobjects.dataloaders.pydantic_sqlite.schema import TableSchema


class PydanticSQLiteLoaderTest(unittest.TestCase):
    "PydanticSQLiteLoader 集成测试类"

    test_dir: str
    loader: PydanticSQLiteLoader

    def setUp(self):
        "每个测试前的准备工作"
        self.test_dir = tempfile.mkdtemp(prefix="pydantic_sqlite_test_")
        self.loader = PydanticSQLiteLoader(self.test_dir)
        self.loader.register_models()

    def tearDown(self):
        "每个测试后的清理工作"
        self.loader.close_connections()
        import gc
        import time
        gc.collect()
        time.sleep(0.1)
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_schema_initialization(self):
        "测试表结构初始化"
        conn = self.loader.get_connection("main")
        version = TableSchema.get_schema_version(conn)
        self.assertGreater(version, 0, "数据库版本应该大于0")

        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t["name"] for t in tables]

        self.assertIn("students", table_names)
        self.assertIn("classes", table_names)
        self.assertIn("groups", table_names)
        self.assertIn("score_modifications", table_names)
        self.assertIn("score_templates", table_names)

    def test_save_and_load_student(self):
        "测试保存和加载学生对象"
        stu = Student("测试学生", 1, 100.0, "test_class")

        self.loader.save_object(stu)

        self.loader.loaded_objects.clear()
        loaded = self.loader.load_object(stu.uuid, Student)

        assert loaded is not None, "加载的学生不应该为None"
        self.assertEqual(loaded.name, "测试学生", "学生名称应该一致")
        self.assertEqual(loaded.num, 1, "学生编号应该一致")
        self.assertEqual(loaded.score, 100.0, "学生分数应该一致")
        self.assertEqual(str(loaded.uuid), str(stu.uuid), "UUID应该一致")

    def test_student_serialization_full(self):
        "测试学生完整序列化和反序列化"
        stu = Student("完整测试学生", 42, 85.5, "test_class")
        stu.total_score = 500.0
        stu.highest_score = 100.0
        stu.lowest_score = 50.0
        stu.highest_score_cause_time = 1700000000.0
        stu.lowest_score_cause_time = 1700001000.0
        stu.belongs_to_group = "group1"
        stu.last_reset = 1700002000.0

        tag1 = DataTag("excellent")
        tag2 = DataTag("active")
        stu.tags = [tag1, tag2]

        self.loader.save_object(tag1)
        self.loader.save_object(tag2)
        self.loader.save_object(stu)

        self.loader.loaded_objects.clear()
        loaded = self.loader.load_object(stu.uuid, Student)

        assert loaded is not None, "加载的学生不应该为None"
        self.assertEqual(loaded.name, "完整测试学生")
        self.assertEqual(loaded.num, 42)
        self.assertEqual(loaded.score, 85.5)
        self.assertEqual(loaded.total_score, 500.0)
        self.assertEqual(loaded.highest_score, 100.0)
        self.assertEqual(loaded.lowest_score, 50.0)
        self.assertEqual(loaded.belongs_to_group, "group1")
        self.assertEqual(len(loaded.tags), 2, "应该有2个标签")

    def test_batch_save(self):
        "测试批量保存"
        students = [
            Student(f"学生{i}", i, float(i * 10), "test_class")
            for i in range(1, 11)
        ]

        with self.loader.batch_mode():
            for stu in students:
                self.loader.save_object(stu)

        self.loader.loaded_objects.clear()

        conn = self.loader.get_connection("current")
        count = conn.execute("SELECT COUNT(*) as cnt FROM students").fetchone()["cnt"]
        self.assertEqual(count, 10, "应该保存10个学生")

    def test_save_and_load_class_with_students(self):
        "测试保存和加载包含学生的班级"
        cls = Class(
            name="测试班级",
            owner="班主任",
            key="test_class",
            students={},
            groups={}
        )

        stu1 = Student("学生1", 1, 50.0, "test_class")
        stu2 = Student("学生2", 2, 60.0, "test_class")
        cls.students[stu1.num] = stu1
        cls.students[stu2.num] = stu2

        with self.loader.batch_mode():
            self.loader.save_object(stu1)
            self.loader.save_object(stu2)
            self.loader.save_object(cls)

        self.loader.loaded_objects.clear()

        loaded_cls = self.loader.load_object(cls.uuid, Class)
        assert loaded_cls is not None, "加载的班级不应该为None"
        self.assertEqual(loaded_cls.name, "测试班级", "班级名称应该一致")
        self.assertEqual(len(loaded_cls.students), 2, "班级应该有2个学生")

    def test_save_and_load_group_with_members(self):
        "测试保存和加载包含成员的小组"
        stu1 = Student("学生1", 1, 50.0, "test_class")
        stu2 = Student("学生2", 2, 60.0, "test_class")

        group = Group(
            key="group1",
            name="第一组",
            leader=stu1,
            members=[stu1, stu2],
            belongs_to="test_class"
        )

        with self.loader.batch_mode():
            self.loader.save_object(stu1)
            self.loader.save_object(stu2)
            self.loader.save_object(group)

        self.loader.loaded_objects.clear()

        loaded_group = self.loader.load_object(group.uuid, Group)
        assert loaded_group is not None, "加载的小组不应该为None"
        self.assertEqual(loaded_group.name, "第一组", "小组名称应该一致")
        self.assertEqual(len(loaded_group.members), 2, "小组应该有2个成员")
        assert loaded_group.leader is not None, "小组应该有组长"

    def test_save_and_load_score_template(self):
        "测试保存和加载分数模板"
        template = ScoreModificationTemplate(
            key="bonus",
            modification=5.0,
            title="加分模板",
            description="表现优秀加分",
            is_visible=True,
            cant_replace=False
        )

        self.loader.save_object(template)

        self.loader.loaded_objects.clear()
        loaded = self.loader.load_object(template.uuid, ScoreModificationTemplate)

        assert loaded is not None, "加载的模板不应该为None"
        self.assertEqual(loaded.key, "bonus", "模板key应该一致")
        self.assertEqual(loaded.mod, 5.0, "修改值应该一致")
        self.assertEqual(loaded.title, "加分模板", "标题应该一致")
        self.assertTrue(loaded.is_visible, "应该可见")

    def test_save_and_load_score_modification(self):
        "测试保存和加载分数修改记录"
        template = ScoreModificationTemplate(
            key="bonus",
            modification=5.0,
            title="加分模板"
        )

        stu = Student("测试学生", 1, 0, "test_class")
        sm = ScoreModification(
            template=template,
            target=stu,
            title="加分记录",
            desc="表现优秀",
            mod=5.0,
            create_time="2024-01-01",
            executed=True
        )

        with self.loader.batch_mode():
            self.loader.save_object(template)
            self.loader.save_object(stu)
            self.loader.save_object(sm)

        self.loader.loaded_objects.clear()

        loaded_sm = self.loader.load_object(sm.uuid, ScoreModification)
        assert loaded_sm is not None, "加载的记录不应该为None"
        self.assertEqual(loaded_sm.title, "加分记录", "标题应该一致")
        self.assertEqual(loaded_sm.mod, 5.0, "修改值应该一致")
        self.assertTrue(loaded_sm.executed, "执行状态应该一致")

    def test_save_and_load_achievement_template(self):
        "测试保存和加载成就模板"
        template = AchievementTemplate(
            key="first_place",
            name="第一名",
            desc="获得班级第一名",
            when_triggered="any",
            sound="victory.mp3",
            icon="trophy.png",
        )

        self.loader.save_object(template)

        self.loader.loaded_objects.clear()
        loaded = self.loader.load_object(template.uuid, AchievementTemplate)

        assert loaded is not None, "加载的模板不应该为None"
        self.assertEqual(loaded.key, "first_place", "模板key应该一致")
        self.assertEqual(loaded.name, "第一名", "名称应该一致")
        self.assertEqual(loaded.sound, "victory.mp3", "音效应该一致")

    def test_save_and_load_achievement(self):
        "测试保存和加载成就"
        template = AchievementTemplate(
            key="first_place",
            name="第一名",
            desc="获得班级第一名",
        )

        stu = Student("测试学生", 1, 100, "test_class")

        ach = Achievement(
            template=template,
            target=stu,
            reach_time="2024-01-01",
            reach_time_key=1700000000,
        )

        with self.loader.batch_mode():
            self.loader.save_object(template)
            self.loader.save_object(stu)
            self.loader.save_object(ach)

        self.loader.loaded_objects.clear()

        loaded_ach = self.loader.load_object(ach.uuid, Achievement)
        assert loaded_ach is not None, "加载的成就不应该为None"
        self.assertEqual(loaded_ach.time, "2024-01-01", "时间应该一致")
        self.assertEqual(loaded_ach.time_key, 1700000000, "时间键应该一致")

    def test_sql_query_capability(self):
        "测试 SQL 查询能力"
        students = [
            Student(f"学生{i}", i, float(i * 10), "test_class")
            for i in range(1, 11)
        ]

        with self.loader.batch_mode():
            for stu in students:
                self.loader.save_object(stu)

        conn = self.loader.get_connection("current")

        high_score = conn.execute(
            "SELECT * FROM students WHERE score >= ?", (50,)
        ).fetchall()
        self.assertEqual(len(high_score), 6, "应该有6个学生分数>=50")

        by_name = conn.execute(
            "SELECT * FROM students WHERE name = ?", ("学生5",)
        ).fetchone()
        self.assertIsNotNone(by_name, "应该找到学生5")
        assert by_name is not None
        self.assertEqual(by_name["score"], 50, "学生5的分数应该是50")

        by_num_range = conn.execute(
            "SELECT * FROM students WHERE num BETWEEN ? AND ?", (3, 7)
        ).fetchall()
        self.assertEqual(len(by_num_range), 5, "应该有5个学号在3-7之间的学生")

    def test_update_existing_object(self):
        "测试更新已存在的对象"
        stu = Student("原始名称", 1, 50.0, "test_class")
        self.loader.save_object(stu)

        stu.name = "更新后名称"
        stu.score = 100.0
        self.loader.save_object(stu)

        self.loader.loaded_objects.clear()
        loaded = self.loader.load_object(stu.uuid, Student)

        assert loaded is not None, "加载的学生不应该为None"
        self.assertEqual(loaded.name, "更新后名称", "名称应该已更新")
        self.assertEqual(loaded.score, 100.0, "分数应该已更新")

    def test_complex_object_graph(self):
        "测试复杂对象图的序列化和反序列化"
        cls = Class(
            name="复杂测试班级",
            owner="测试老师",
            key="complex_class",
            students={},
            groups={}
        )

        students: dict[int, Student] = {}
        for i in range(1, 6):
            stu = Student(f"学生{i}", i, 60.0 + i * 5, "complex_class")
            students[i] = stu
            cls.students[i] = stu

        group1 = Group(
            key="group1",
            name="第一组",
            leader=students[1],
            members=[students[1], students[2]],
            belongs_to="complex_class"
        )
        group2 = Group(
            key="group2",
            name="第二组",
            leader=students[3],
            members=[students[3], students[4], students[5]],
            belongs_to="complex_class"
        )
        cls.groups["group1"] = group1
        cls.groups["group2"] = group2

        template = ScoreModificationTemplate(
            key="bonus",
            modification=5.0,
            title="加分"
        )

        sm = ScoreModification(
            template=template,
            target=students[1],
            title="表现优秀",
            desc="课堂表现好",
            mod=5.0,
            create_time="2024-01-01",
            executed=True
        )
        students[1].history[sm.execute_time_key] = sm

        with self.loader.batch_mode():
            self.loader.save_object(template)
            self.loader.save_object(cls)

        self.loader.loaded_objects.clear()

        loaded_cls = self.loader.load_object(cls.uuid, Class)
        assert loaded_cls is not None, "加载的班级不应该为None"
        self.assertEqual(loaded_cls.name, "复杂测试班级")
        self.assertEqual(len(loaded_cls.students), 5)
        self.assertEqual(len(loaded_cls.groups), 2)

        loaded_group1 = loaded_cls.groups.get("group1")
        assert loaded_group1 is not None
        self.assertEqual(len(loaded_group1.members), 2)

        loaded_stu1 = loaded_cls.students.get(1)
        assert loaded_stu1 is not None
        self.assertEqual(loaded_stu1.name, "学生1")

    def test_save_and_load_data(self):
        "测试 save_data 和 load_data"

        cls = Class(
            name="数据测试班级",
            owner="测试老师",
            key="data_class",
            students={},
            groups={}
        )

        for i in range(1, 4):
            stu = Student(f"学生{i}", i, 70.0 + i * 5, "data_class")
            cls.students[i] = stu

        template = ScoreModificationTemplate(
            key="test_template",
            modification=10.0,
            title="测试模板"
        )

        ach_template = AchievementTemplate(
            key="test_achievement",
            name="测试成就",
            desc="测试成就描述"
        )

        self.loader.bound_db.classes["data_class"] = cls
        self.loader.bound_db.templates["test_template"] = template
        self.loader.bound_db.achievements["test_achievement"] = ach_template
        self.loader.bound_db.user = "测试用户"
        self.loader.bound_db.version = "1.0.0"
        self.loader.bound_db.version_code = 1

        self.loader.save_data()

        loader2 = PydanticSQLiteLoader(self.test_dir)
        loader2.register_models()
        data = loader2.load_data()

        self.assertEqual(data.user, "测试用户")
        self.assertEqual(data.version, "1.0.0")
        self.assertIn("data_class", data.classes)
        self.assertIn("test_template", data.templates)
        self.assertIn("test_achievement", data.achievements)

        loader2.close_connections()

    def runTest(self):
        tests = [
            self.test_schema_initialization,
            self.test_save_and_load_student,
            self.test_student_serialization_full,
            self.test_batch_save,
            self.test_save_and_load_class_with_students,
            self.test_save_and_load_group_with_members,
            self.test_save_and_load_score_template,
            self.test_save_and_load_score_modification,
            self.test_save_and_load_achievement_template,
            self.test_save_and_load_achievement,
            self.test_sql_query_capability,
            self.test_update_existing_object,
            self.test_complex_object_graph,
            self.test_save_and_load_data,
        ]
        for test in tests:
            self.setUp()
            try:
                test()
            finally:
                self.tearDown()


__all__ = ["PydanticSQLiteLoaderTest"]
