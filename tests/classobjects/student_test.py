import unittest

from utils.basetypes import Base
from utils.classobjects import *
from utils.classobjects.dataloader import DataObject
from utils.classobjects.objects import DataTag


class ClassObjectStudentTest(unittest.TestCase):

    def test_construct_and_basic_operation(self):
        stu1 = Student("名称1", 1145, 0.1, "class_id", belongs_to_group="group_id")
        stu2 = Student("名称2", 1919, 0.2, "class_id", belongs_to_group="group_id")
        self.assertNotEqual(
            stu1.uuid, stu2.uuid, f"每个学生对象应该有唯一的uuid当前uuid1为{stu1.uuid!r}, uuid2为{stu2.uuid!r}"
        )
        self.assertEqual(stu1.archive_uuid, stu2.archive_uuid, "每个学生对象的归档uuid应当相同")

        self.assertEqual(stu1.name, "名称1", "学生姓名应当符合原设置")
        self.assertEqual(stu1.num, 1145, "学生学号应当符合原设置")
        self.assertEqual(stu1.score, 0.1, "学生成绩应当符合原设置")
        self.assertEqual(stu1.belongs_to, "class_id", "学生班级应当符合原设置")
        self.assertEqual(stu1.belongs_to_group, "group_id", "学生小组应当符合原设置")

        stu3 = stu2.copy()
        stu3.name = "名称3"
        self.assertEqual(stu3.name, "名称3", "拷贝之后的对象应当是可独立操作的")
        self.assertEqual(stu2.name, "名称2", "深拷贝应该不会影响原对象")

        data = stu1.to_string()

        stu4 = Student.from_string(data)

        for attr in stu1.__dict__:
            self.assertEqual(
                getattr(stu1, attr),
                getattr(stu4, attr),
                "字符串序列化与反序列化应当不会影响对象属性; "
                f"当前不同的属性：{attr}, stu的为{getattr(stu1, attr)!r}, stu4的为{getattr(stu4, attr)!r}",
            )

        stu1.highest_score = 114514
        stu1.reset()
        self.assertEqual(stu1.score, 0.0, "重置之后应分数当恢复默认值")
        self.assertEqual(stu1.highest_score, 0, "重置之后本周最高分应当恢复默认值")

    def test_tag(self):
        stu1 = Student("名称1", 1145, 0.1, "class_id", belongs_to_group="group_id")
        stu2 = Student("名称2", 1919, 0.2, "class_id", belongs_to_group="group_id")
        DataTag.register("a_simple_tag", "一个啥也不是的标签")
        DataTag.register("a_simple_tag_2", "一个啥也不是的标签，但是带有类型数据和校验器", 
                            lambda d, dt: d == dt["target"] if dt else False,
                            {"target": "我是目标数据"}
                        )

        tag1 = DataTag("a_simple_tag")
        stu1.add_tag(tag1)
        self.assertTrue(stu1.has_tag(tag1), "添加标签后应当能够检测到标签")
        self.assertTrue(stu1.has_tag("a_simple_tag"), "添加标签后应当能够检测到标签")
        stu1.remove_tag(tag1)
        self.assertFalse(stu1.has_tag(tag1), "移除标签后应当检测不到标签")
        self.assertFalse(stu1.has_tag("a_simple_tag"), "移除标签后应当检测不到标签")

        with self.assertRaises(ValueError, msg="添加带有校验器的标签时，不符合校验器条件的标签添加操作应当抛出异常"):
            tag2 = DataTag("a_simple_tag_2", "我是目标数据不一样的数据")
            stu1.add_tag(tag2)

        tag3 = DataTag("a_simple_tag_2", "我是目标数据")
        stu1.add_tag(tag3)
        self.assertTrue(stu1.has_tag(tag3), "添加带有校验器的标签时，符合校验器条件的标签添加操作应当成功")
        self.assertTrue(stu1.has_tag("a_simple_tag_2"), "添加带有校验器的标签时，符合校验器条件的标签添加操作应当成功")

        DataObject.static_save(stu1, self.test_chunk)
        self.test_chunk.set_uuid_loader(None)
        Base.config.log_level = "D"
        stu2 = ClassDataLoader.LoadUUID(stu1.uuid, Student)
        self.assertTrue(stu2.has_tag(tag3), "从数据中加载对象后，标签应当被正确加载")


    def __init__(self):
        super().__init__()
        self.test_chunk = Chunk("chunks/_test_chunk", UserDataBase())
        self.test_chunk.save_data()
        self.test_chunk.load_data()

    def runTest(self):
        self.test_construct_and_basic_operation()
        self.test_tag()



__all__ = ["ClassObjectStudentTest"]