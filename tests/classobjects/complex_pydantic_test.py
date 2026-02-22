"""
Pydantic复杂转换测试。

测试复合数据类型的序列化和反序列化，包括：
- 嵌套引用（Group包含Student引用）
- 多层嵌套（Class包含Students和Groups）
- 循环引用处理
- JSON序列化/反序列化
"""

import json
import unittest

from utils.classobjects import *
from utils.classobjects.objects.dayrecord import DayRecord
from utils.classobjects.objects.history import History
from utils.classobjects.objects.homeworkrule import HomeworkRule
from utils.classobjects.dataloaders.pydantic_loader.loader import PydanticLoader
from utils.classobjects.dataloaders.pydantic_loader.cache import get_cache
from utils.classobjects.dataloaders.pydantic_loader.base import PydanticReference


class ComplexPydanticTest(unittest.TestCase):
    "复合数据类型Pydantic转换测试"

    def setUp(self):
        "每个测试前的准备工作"
        self.loader = PydanticLoader()
        self.loader.register_models()
        self.cache = get_cache()
        self.cache.clear()

    def tearDown(self):
        "每个测试后的清理工作"
        self.cache.clear()

    def test_group_with_student_refs(self):
        "测试Group包含Student引用的序列化"
        leader = Student("组长", 1, 0, "test_class")
        member1 = Student("成员1", 2, 0, "test_class")
        member2 = Student("成员2", 3, 0, "test_class")

        group = Group(
            key="test_group",
            name="测试小组",
            leader=leader,
            members=[leader, member1, member2],
            belongs_to="test_class"
        )

        model = group.to_pydantic()

        self.assertEqual(str(model.leader_ref.uuid), str(leader.uuid), "组长引用UUID应该正确")
        self.assertEqual(len(model.member_refs), 3, "成员引用数量应该正确")
        self.assertEqual(str(model.member_refs[0].uuid), str(leader.uuid), "第一个成员应该是组长")
        self.assertEqual(str(model.member_refs[1].uuid), str(member1.uuid), "第二个成员应该正确")
        self.assertEqual(str(model.member_refs[2].uuid), str(member2.uuid), "第三个成员应该正确")

        json_data = model.model_dump(mode="json")
        json_str = json.dumps(json_data, ensure_ascii=False)
        self.assertIn(str(leader.uuid), json_str, "JSON中应该包含组长的UUID")

    def test_class_with_students_and_groups(self):
        "测试Class包含多个Student和Group的序列化"
        cls = Class(
            name="测试班级",
            owner="班主任",
            key="test_class",
            students={},
            groups={}
        )

        stu1 = Student("学生1", 1, 0, "test_class")
        stu2 = Student("学生2", 2, 0, "test_class")
        stu3 = Student("学生3", 3, 0, "test_class")

        cls.students[stu1.num] = stu1
        cls.students[stu2.num] = stu2
        cls.students[stu3.num] = stu3

        group = Group(
            key="group1",
            name="第一组",
            leader=stu1,
            members=[stu1, stu2, stu3],
            belongs_to="test_class"
        )
        cls.groups[group.key] = group

        model = cls.to_pydantic()

        self.assertEqual(len(model.student_refs), 3, "学生引用数量应该正确")
        self.assertEqual(len(model.group_refs), 1, "小组引用数量应该正确")

        json_data = model.model_dump(mode="json")
        json_str = json.dumps(json_data, ensure_ascii=False)

        self.assertIn(str(stu1.uuid), json_str, "JSON中应该包含学生1的UUID")
        self.assertIn(str(group.uuid), json_str, "JSON中应该包含小组的UUID")

    def test_score_modification_with_template_ref(self):
        "测试ScoreModification包含模板引用"
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

        model = sm.to_pydantic()
        self.assertIsNotNone(model.template_ref, "模板引用应该存在")
        assert model.template_ref is not None
        self.assertEqual(str(model.template_ref.uuid), str(template.uuid), "模板引用应该正确")
        self.assertEqual(str(model.target_ref.uuid), str(stu.uuid), "目标学生引用应该正确")

        json_data = model.model_dump(mode="json")
        self.assertIn("template_ref", json_data, "JSON中应该有template_ref字段")
        self.assertIn("target_ref", json_data, "JSON中应该有target_ref字段")

    def test_achievement_with_template_and_student(self):
        "测试Achievement包含模板和学生引用"
        template = AchievementTemplate(
            key="star",
            name="星级成就",
            desc="获得星级"
        )

        stu = Student("获奖学生", 1, 0, "test_class")

        achievement = Achievement(
            template=template,
            target=stu,
            reach_time="2024-01-01"
        )

        model = achievement.to_pydantic()

        self.assertEqual(str(model.template_ref.uuid), str(template.uuid), "模板引用应该正确")
        self.assertEqual(str(model.target_ref.uuid), str(stu.uuid), "目标学生引用应该正确")

        json_data = model.model_dump(mode="json")
        json_str = json.dumps(json_data, ensure_ascii=False)
        self.assertIn(str(template.uuid), json_str, "JSON中应该包含模板UUID")
        self.assertIn(str(stu.uuid), json_str, "JSON中应该包含学生UUID")

    def test_homework_rule_with_template_refs(self):
        "测试HomeworkRule包含模板引用映射"
        template1 = ScoreModificationTemplate(
            key="homework_done",
            modification=1.0,
            title="完成作业"
        )
        template2 = ScoreModificationTemplate(
            key="homework_excellent",
            modification=2.0,
            title="优秀作业"
        )

        rule = HomeworkRule(
            key="math_homework",
            subject_name="数学",
            ruler="数学老师",
            rule_mapping={
                "done": template1,
                "excellent": template2
            }
        )

        model = rule.to_pydantic()

        self.assertEqual(model.key, "math_homework", "key应该正确")
        self.assertEqual(model.subject_name, "数学", "科目名称应该正确")
        self.assertEqual(len(model.rule_mapping), 2, "规则映射数量应该正确")
        self.assertIn("done", model.rule_mapping, "应该包含done规则")
        self.assertIn("excellent", model.rule_mapping, "应该包含excellent规则")

        json_data = model.model_dump(mode="json")
        self.assertIn("rule_mapping", json_data, "JSON中应该有rule_mapping字段")

    def test_dayrecord_with_class_ref(self):
        "测试DayRecord包含Class引用"
        cls = Class(
            name="测试班级",
            owner="班主任",
            key="test_class",
            students={},
            groups={}
        )

        attendance = AttendanceInfo(
            target_class="test_class"
        )

        record = DayRecord(
            target_class=cls,
            weekday=1,
            create_utc=1704067200.0,
            attendance_info=attendance
        )

        model = record.to_pydantic()

        self.assertEqual(str(model.target_class_ref.uuid), str(cls.uuid), "班级引用应该正确")

        json_data = model.model_dump(mode="json")
        self.assertIn("target_class_ref", json_data, "JSON中应该有target_class_ref字段")

    def test_history_with_classes(self):
        "测试History包含多个Class"
        cls1 = Class(
            name="班级1",
            owner="班主任1",
            key="class1",
            students={},
            groups={}
        )
        cls2 = Class(
            name="班级2",
            owner="班主任2",
            key="class2",
            students={},
            groups={}
        )

        history = History(
            classes={"class1": cls1, "class2": cls2},
            weekdays={}
        )
        history.time = 1704067200.0

        model = history.to_pydantic()

        self.assertEqual(len(model.class_refs), 2, "班级引用数量应该正确")
        self.assertEqual(model.time, 1704067200.0, "时间戳应该正确")

        json_data = model.model_dump(mode="json")
        json_str = json.dumps(json_data, ensure_ascii=False)
        self.assertIn(str(cls1.uuid), json_str, "JSON中应该包含班级1的UUID")
        self.assertIn(str(cls2.uuid), json_str, "JSON中应该包含班级2的UUID")

    def test_json_round_trip_complex(self):
        "测试复杂对象的JSON往返序列化"
        cls = Class(
            name="往返测试班级",
            owner="测试班主任",
            key="round_trip_class",
            students={},
            groups={}
        )

        stu1 = Student("学生A", 101, 50.0, "round_trip_class")
        stu2 = Student("学生B", 102, 60.0, "round_trip_class")
        cls.students[stu1.num] = stu1
        cls.students[stu2.num] = stu2

        group = Group(
            key="group_a",
            name="A组",
            leader=stu1,
            members=[stu1, stu2],
            belongs_to="round_trip_class"
        )
        cls.groups[group.key] = group

        model = cls.to_pydantic()

        json_data = model.model_dump(mode="json")
        json_str = json.dumps(json_data, ensure_ascii=False)

        parsed_data = json.loads(json_str)

        from utils.classobjects.dataloaders.pydantic_loader.models.classtype import ClassModel
        restored_model = ClassModel.model_validate(parsed_data)

        self.assertEqual(str(restored_model.uuid), str(cls.uuid), "往返后UUID应该一致")
        self.assertEqual(restored_model.name, "往返测试班级", "往返后名称应该一致")
        self.assertEqual(len(restored_model.student_refs), 2, "往返后学生引用数量应该正确")
        self.assertEqual(len(restored_model.group_refs), 1, "往返后小组引用数量应该正确")

    def test_pydantic_reference_from_object(self):
        "测试PydanticReference从对象创建"
        stu = Student("引用测试", 1, 0, "test_class")

        ref = PydanticReference.from_object(stu)

        self.assertEqual(str(ref.uuid), str(stu.uuid), "引用UUID应该与对象UUID一致")
        self.assertEqual(ref.dtype, Student, "引用类型应该是Student")

    def test_nested_reference_chain(self):
        "测试嵌套引用链"
        cls = Class(
            name="嵌套测试班级",
            owner="班主任",
            key="nested_class",
            students={},
            groups={}
        )

        stu = Student("嵌套学生", 1, 0, "nested_class")
        cls.students[stu.num] = stu

        template = ScoreModificationTemplate(
            key="bonus",
            modification=5.0,
            title="加分"
        )

        sm = ScoreModification(
            template=template,
            target=stu,
            title="嵌套加分",
            desc="测试嵌套引用",
            mod=5.0,
            create_time="2024-01-01",
            executed=True
        )

        cls_model = cls.to_pydantic()
        sm_model = sm.to_pydantic()

        self.assertEqual(len(cls_model.student_refs), 1, "班级应该有一个学生引用")

        sm_json = sm_model.model_dump(mode="json")
        self.assertEqual(sm_json["target_ref"]["uuid"]["uuid"], str(stu.uuid), "加分记录的目标引用应该正确")
        self.assertEqual(sm_json["template_ref"]["uuid"]["uuid"], str(template.uuid), "加分记录的模板引用应该正确")

    def runTest(self):
        "运行所有测试"
        self.test_group_with_student_refs()
        self.test_class_with_students_and_groups()
        self.test_score_modification_with_template_ref()
        self.test_achievement_with_template_and_student()
        self.test_homework_rule_with_template_refs()
        self.test_dayrecord_with_class_ref()
        self.test_history_with_classes()
        self.test_json_round_trip_complex()
        self.test_pydantic_reference_from_object()
        self.test_nested_reference_chain()


__all__ = ["ComplexPydanticTest"]
