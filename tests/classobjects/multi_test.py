import unittest

from utils.classobjects import *
from utils.classobjects.dataloader import DataObject

test_chunk = Chunk("chunks/_test_chunk", UserDataBase())
test_chunk.save_data()
test_chunk.load_data()


class MultiTest(unittest.TestCase):
    def test_default_data(self):
        self.assertGreater(len(DEFAULT_SCORE_TEMPLATES), 0)
        self.assertGreater(len(DEFAULT_ACHIEVEMENTS), 0)
        self.assertGreater(len(DEFAULT_CLASSES), 0)

    def test_student(self):
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

    def test_score_mods(self):
        template_1 = ScoreModificationTemplate("template_1", 2, "模板1", "大概就是我不知道该写啥了")
        template_2 = ScoreModificationTemplate("template_2", 3, "模板2")
        self.assertEqual(template_1.key, "template_1", "模板标识符应当符合原设置")
        self.assertEqual(template_1.mod, 2, "模板分数应当符合原设置")
        self.assertEqual(template_1.title, "模板1", "模板名称应当符合原设置")
        self.assertEqual(template_1.desc, "大概就是我不知道该写啥了", "模板描述应当符合原设置")

        stu1 = Student("名称1", 1145, 1, "class_id")

        action_1 = ScoreModification(template_1, stu1, "修改过的名称", "修改过的描述", 114514)
        action_2 = ScoreModification(template_2, stu1)

        action_1.execute()
        time.sleep(0.02)
        action_2.execute()

        executed_action_1 = next(iter(stu1.history.values()))
        executed_action_2 = list(stu1.history.values())[1]

        self.assertIs(executed_action_1, action_1, "执行过的操作应当与原操作为同一个对象")
        self.assertIs(executed_action_2, action_2, "执行过的操作应当与原操作为同一个对象")

        self.assertEqual(executed_action_1.title, "修改过的名称", "实际操作名称应当符合过修改过的设置")
        self.assertEqual(executed_action_1.desc, "修改过的描述", "实际操作描述应当符合过修改过的设置")
        self.assertEqual(executed_action_1.mod, 114514, "实际操作分数应当符合经过修改过的设置")

        self.assertEqual(executed_action_2.title, template_2.title, "实际操作名称应当符合原设置")
        self.assertEqual(executed_action_2.desc, template_2.desc, "实际操作描述应当符合原设置")
        self.assertEqual(executed_action_2.mod, template_2.mod, "实际操作分数应当符合原设置")

        self.assertEqual(stu1.score, 1 + 114514 + 3, "操作应当影响学生的分数")

        action_1.retract()

        self.assertEqual(stu1.score, 1 + 3, "撤销操作应当影响学生的分数")

        data = action_1.to_string()

        DataObject.static_save(stu1, test_chunk)
        DataObject.static_save(action_1, test_chunk)
        DataObject.static_save(action_2, test_chunk)
        DataObject.static_save(template_1, test_chunk)
        DataObject.static_save(template_2, test_chunk)

        action_3 = ScoreModification.from_string(data)

        for attr in action_1.__dict__:
            if isinstance(getattr(action_1, attr), ClassDataType):
                self.assertEqual(getattr(action_1, attr).uuid, getattr(action_3, attr).uuid)
                continue
            self.assertEqual(
                getattr(action_1, attr),
                getattr(action_3, attr),
                "字符串序列化与反序列化应当不会影响对象属性; "
                f"当前不同的属性：{attr}, action1的为{getattr(action_1, attr)!r}, action3的为{getattr(action_3, attr)!r}",
            )

    def runTest(self):
        self.test_default_data()
        self.test_student()
        self.test_score_mods()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(MultiTest())
    return suite


def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())
