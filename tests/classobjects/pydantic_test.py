"""
Pydantic转换测试。
"""

import unittest

from utils.classobjects import *
from utils.classobjects.objects.datatag import DataTag
from utils.classobjects.pydantic_loader.loader import PydanticLoader
from utils.classobjects.pydantic_loader.cache import get_cache


class PydanticConversionTest(unittest.TestCase):
    "Pydantic转换测试类"

    def setUp(self):
        "每个测试前的准备工作"
        self.loader = PydanticLoader()
        self.loader.register_models()
        self.cache = get_cache()
        self.cache.clear()

    def tearDown(self):
        "每个测试后的清理工作"
        self.cache.clear()

    def test_student_to_pydantic(self):
        "测试Student转换为Pydantic模型"
        stu = Student("测试学生", 1145, 10.0, "test_class", belongs_to_group="test_group")
        
        model = stu.to_pydantic()
        
        self.assertEqual(str(model.uuid), str(stu.uuid), "UUID应该一致")
        self.assertEqual(model.name, "测试学生", "姓名应该一致")
        self.assertEqual(model.num, 1145, "学号应该一致")
        self.assertEqual(model.score, 10.0, "分数应该一致")
        self.assertEqual(model.belongs_to, "test_class", "所属班级应该一致")
        self.assertEqual(model.belongs_to_group, "test_group", "所属小组应该一致")

    def test_datatag_to_pydantic(self):
        "测试DataTag转换为Pydantic模型"
        DataTag.register("test_tag", "测试标签")
        tag = DataTag("test_tag", data="测试数据")
        
        model = tag.to_pydantic()
        
        self.assertEqual(str(model.uuid), str(tag.uuid), "UUID应该一致")
        self.assertEqual(model.key, "test_tag", "key应该一致")
        self.assertEqual(model.data, "测试数据", "数据应该一致")

    def test_group_to_pydantic(self):
        "测试Group转换为Pydantic模型"
        leader = Student("组长", 1, 0, "test_class")
        member1 = Student("成员1", 2, 0, "test_class")
        member2 = Student("成员2", 3, 0, "test_class")
        
        group = Group(
            key="test_group",
            name="测试小组",
            leader=leader,
            members=[leader, member1, member2],
            belongs_to="test_class",
            further_desc="这是一个测试小组"
        )
        
        model = group.to_pydantic()
        
        self.assertEqual(str(model.uuid), str(group.uuid), "UUID应该一致")
        self.assertEqual(model.key, "test_group", "key应该一致")
        self.assertEqual(model.name, "测试小组", "名称应该一致")
        self.assertEqual(model.belongs_to, "test_class", "所属班级应该一致")
        self.assertEqual(model.description, "这是一个测试小组", "描述应该一致")
        self.assertEqual(model.leader_ref.uuid, leader.uuid, "组长引用应该正确")
        self.assertEqual(len(model.member_refs), 3, "成员引用数量应该正确")

    def test_class_to_pydantic(self):
        "测试Class转换为Pydantic模型"
        cls = Class(
            name="测试班级",
            owner="测试班主任",
            key="test_class",
            students={},
            groups={}
        )
        
        model = cls.to_pydantic()
        
        self.assertEqual(str(model.uuid), str(cls.uuid), "UUID应该一致")
        self.assertEqual(model.name, "测试班级", "名称应该一致")
        self.assertEqual(model.owner, "测试班主任", "班主任应该一致")
        self.assertEqual(model.key, "test_class", "key应该一致")

    def test_score_modification_to_pydantic(self):
        "测试ScoreModification转换为Pydantic模型"
        template = ScoreModificationTemplate(
            key="test_template",
            modification=5.0,
            title="测试模板"
        )
        stu = Student("测试学生", 1, 0, "test_class")
        
        sm = ScoreModification(
            template=template,
            target=stu,
            title="测试修改",
            desc="测试描述",
            mod=5.0,
            create_time="2024-01-01",
            executed=True
        )
        
        model = sm.to_pydantic()
        
        self.assertEqual(str(model.uuid), str(sm.uuid), "UUID应该一致")
        self.assertEqual(model.title, "测试修改", "标题应该一致")
        self.assertEqual(model.description, "测试描述", "描述应该一致")
        self.assertEqual(model.modification, 5.0, "修改值应该一致")
        self.assertTrue(model.executed, "执行状态应该一致")

    def test_achievement_template_to_pydantic(self):
        "测试AchievementTemplate转换为Pydantic模型"
        template = AchievementTemplate(
            key="test_achievement",
            name="测试成就",
            desc="这是一个测试成就"
        )
        
        model = template.to_pydantic()
        
        self.assertEqual(str(model.uuid), str(template.uuid), "UUID应该一致")
        self.assertEqual(model.key, "test_achievement", "key应该一致")
        self.assertEqual(model.name, "测试成就", "名称应该一致")
        self.assertEqual(model.description, "这是一个测试成就", "描述应该一致")

    def test_round_trip_student(self):
        "测试Student的往返转换"
        stu = Student("往返测试", 999, 100.0, "test_class")
        
        model = stu.to_pydantic()
        self.cache.clear()
        restored = model.to_class_data()
        
        self.assertEqual(str(restored.uuid), str(stu.uuid), "往返转换后UUID应该一致")
        self.assertEqual(restored.name, "往返测试", "往返转换后姓名应该一致")
        self.assertEqual(restored.num, 999, "往返转换后学号应该一致")
        self.assertEqual(restored.score, 100.0, "往返转换后分数应该一致")

    def test_model_dump_for_db(self):
        "测试模型导出为数据库格式"
        stu = Student("导出测试", 123, 50.0, "test_class")
        model = stu.to_pydantic()
        
        db_data = model.model_dump_for_db()
        
        self.assertIsInstance(db_data["uuid"], str, "UUID应该被转换为字符串")
        self.assertEqual(db_data["name"], "导出测试", "姓名应该保留")
        self.assertEqual(db_data["num"], 123, "学号应该保留")

    def runTest(self):
        "运行所有测试"
        self.test_student_to_pydantic()
        self.test_datatag_to_pydantic()
        self.test_group_to_pydantic()
        self.test_class_to_pydantic()
        self.test_score_modification_to_pydantic()
        self.test_achievement_template_to_pydantic()
        self.test_round_trip_student()
        self.test_model_dump_for_db()


__all__ = ["PydanticConversionTest"]
