"""
PydanticLoader集成测试。
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
from utils.classobjects.dataloaders.pydantic_loader.loader import (
    PydanticLoader,
    get_loader,
)


class PydanticLoaderTest(unittest.TestCase):
    "PydanticLoader集成测试类"

    test_dir: str
    loader: PydanticLoader

    def setUp(self):
        "每个测试前的准备工作"
        self.test_dir = tempfile.mkdtemp(prefix="pydantic_loader_test_")
        self.loader = get_loader()
        self.loader.register_models()
        self.loader.close_connections()
        self.loader.database_connections.clear()
        self.loader.loaded_models.clear()
        self.loader.loaded_objects.clear()
        self.loader.loading_set.clear()
        self.loader.clear_pending_saves()
        self.loader.set_path(self.test_dir)
        self.loader.set_uuid_loader(None)

    def tearDown(self):
        "每个测试后的清理工作"
        self.loader.close_connections()
        self.loader.database_connections.clear()
        self.loader.loaded_models.clear()
        self.loader.loaded_objects.clear()
        self.loader.loading_set.clear()
        self.loader.clear_pending_saves()
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_and_load_student(self):
        "测试保存和加载学生对象"
        stu = Student("测试学生", 1, 100.0, "test_class")

        self.loader.save_object(stu)

        self.loader.loaded_objects.clear()
        self.loader.loaded_models.clear()
        loaded = self.loader.load_object(stu.uuid, Student)

        self.assertEqual(loaded.name, "测试学生", "学生名称应该一致")
        self.assertEqual(loaded.num, 1, "学生编号应该一致")
        self.assertEqual(loaded.score, 100.0, "学生分数应该一致")
        self.assertEqual(str(loaded.uuid), str(stu.uuid), "UUID应该一致")

    def test_batch_save(self):
        "测试批量保存"
        students = [
            Student(f"学生{i}", i, float(i * 10), "test_class")
            for i in range(1, 11)
        ]

        self.loader.save_objects(students)

        self.loader.loaded_objects.clear()
        self.loader.loaded_models.clear()
        loaded = self.loader.load_all_of_type(Student)
        self.assertEqual(len(loaded), 10, "应该加载10个学生")

        loaded_nums = {s.num for s in loaded}
        expected_nums = set(range(1, 11))
        self.assertEqual(loaded_nums, expected_nums, "学生编号应该一致")

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

        self.loader.clear_cache()

        loaded_cls = self.loader.load_object(cls.uuid, Class)
        self.assertEqual(loaded_cls.name, "测试班级", "班级名称应该一致")
        self.assertEqual(len(loaded_cls.students), 2, "班级应该有2个学生")

    def test_save_and_load_group_with_members(self):
        "测试保存和加载包含成员的小组"
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

        group = Group(
            key="group1",
            name="第一组",
            leader=stu1,
            members=[stu1, stu2],
            belongs_to="test_class"
        )
        cls.groups[group.key] = group

        with self.loader.batch_mode():
            self.loader.save_object(stu1)
            self.loader.save_object(stu2)
            self.loader.save_object(group)
            self.loader.save_object(cls)

        self.loader.clear_cache()

        loaded_group = self.loader.load_object(group.uuid, Group)
        self.assertEqual(loaded_group.name, "第一组", "小组名称应该一致")
        self.assertEqual(len(loaded_group.members), 2, "小组应该有2个成员")

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

        self.loader.clear_cache()

        loaded_sm = self.loader.load_object(sm.uuid, ScoreModification)
        self.assertEqual(loaded_sm.title, "加分记录", "标题应该一致")
        self.assertEqual(loaded_sm.mod, 5.0, "修改值应该一致")
        self.assertTrue(loaded_sm.executed, "执行状态应该一致")

    def test_delete_object(self):
        "测试删除对象"
        stu = Student("待删除学生", 999, 0, "test_class")

        self.loader.save_object(stu)

        loaded = self.loader.load_object(stu.uuid, Student)
        self.assertIsNotNone(loaded, "对象应该存在")

        result = self.loader.delete_object(stu.uuid, Student)
        self.assertTrue(result, "删除应该成功")

        self.loader.clear_cache()

        all_students = self.loader.load_all_of_type(Student)
        self.assertEqual(len(all_students), 0, "删除后应该没有学生")

    def test_create_and_list_histories(self):
        "测试创建和列出历史记录"
        history_uuid = self.loader.create_history()

        histories = self.loader.list_histories()
        self.assertEqual(len(histories), 1, "应该有1个历史记录")
        self.assertEqual(str(histories[0]), str(history_uuid), "UUID应该一致")

    def test_stats(self):
        "测试统计信息"
        stu = Student("统计测试", 1, 0, "test_class")
        self.loader.save_object(stu)

        stats = self.loader.get_stats()
        self.assertEqual(stats["registered_models"], 12, "应该注册了12个模型")
        self.assertGreater(stats["database_connections"], 0, "应该有数据库连接")

    def test_uuid_loader_callback(self):
        "测试UUID加载回调"
        stu = Student("回调测试", 1, 100.0, "test_class")
        self.loader.save_object(stu)

        self.loader.clear_cache()
        self.loader.set_uuid_loader(None)

        from utils.classobjects.classdataloader import ClassDataLoader
        loaded = ClassDataLoader.LoadUUID(stu.uuid, Student)

        self.assertIsNotNone(loaded, "通过回调加载的对象不应该为None")
        if loaded:
            self.assertEqual(loaded.name, "回调测试", "名称应该一致")

    def test_update_existing_object(self):
        "测试更新已存在的对象"
        stu = Student("原始名称", 1, 50.0, "test_class")
        self.loader.save_object(stu)

        stu.name = "更新后名称"
        stu.score = 100.0
        self.loader.save_object(stu)

        self.loader.clear_cache()
        loaded = self.loader.load_object(stu.uuid, Student)

        self.assertEqual(loaded.name, "更新后名称", "名称应该已更新")
        self.assertEqual(loaded.score, 100.0, "分数应该已更新")

    def runTest(self):
        tests = [
            self.test_save_and_load_student,
            self.test_batch_save,
            self.test_save_and_load_class_with_students,
            self.test_save_and_load_group_with_members,
            self.test_save_and_load_score_modification,
            self.test_delete_object,
            self.test_create_and_list_histories,
            self.test_stats,
            self.test_uuid_loader_callback,
            self.test_update_existing_object,
        ]
        for test in tests:
            self.setUp()
            try:
                test()
            finally:
                self.tearDown()


__all__ = ["PydanticLoaderTest"]
