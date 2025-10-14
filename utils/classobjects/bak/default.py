"""
默认数据。
"""
import os
import copy
from math import inf
from typing import Dict

from ..objects import *

from utils.algorithm import OrderedKeyList
from utils.consts import sound_file_path

# 因为这个是最后一个导入的，所以要控制一下，不然会出现莫名其妙的未导入
__all__ = [
    "DEFAULT_CLASS_KEY",
    "DEFAULT_SCORE_TEMPLATES",
    "DEFAULT_CLASSES",
    "DEFAULT_ACHIEVEMENTS",
]

DEFAULT_CLASS_KEY = "CLASS_TEST"

DEFAULT_SCORE_TEMPLATES: OrderedKeyList[ScoreModificationTemplate] = OrderedKeyList(
    [
        ScoreModificationTemplate(
            "go_to_school_early", 1.0, "7:20前到校", "早起的鸟儿有虫吃"
        ),
        ScoreModificationTemplate(
            "go_to_school_late", -1.0, "7:25后到校", "早起的虫儿被鸟吃"
        ),
        ScoreModificationTemplate(
            "go_to_school_late_more", -2.0, "7:30后到校", "哥们为什么不睡死在家里？"
        ),
        ScoreModificationTemplate(
            "Chinese_class_good", 2.0, "语文课堂表扬", "王の表扬"
        ),
        ScoreModificationTemplate(
            "Chinese_class_bad", -2.0, "语文课堂批评", "霸道晶晶对你使用了锁定技！"
        ),
        ScoreModificationTemplate(
            "Chinese_homework_best", 4.0, "语文作业A++", "全！体！起！立！！！"
        ),
        ScoreModificationTemplate(
            "Chinese_homework_good", 2.0, "语文作业A+", " 噫！好！我中了！"
        ),
        ScoreModificationTemplate(
            "Chinese_homework_normal", 0.0, "语文作业A", "这并不好笑"
        ),
        ScoreModificationTemplate(
            "Chinese_homework_bad", -2.0, "语文作业B", "你感觉到前所未有的危机感"
        ),
        ScoreModificationTemplate(
            "Chinese_homework_worst", -3.0, "语文作业C", '"留下来！"'
        ),
        ScoreModificationTemplate(
            "Chinese_homework_missing",
            -4.0,
            "语文作业未完成",
            "你感觉到前所未有的危机感",
        ),
        ScoreModificationTemplate("math_class_good", 2.0, "数学课堂表扬", "坤之嘉奖"),
        ScoreModificationTemplate("math_class_bad", -2.0, "数学课堂批评", "坤哥发飙"),
        ScoreModificationTemplate(
            "math_homework_good", 2.0, "数学作业100", "热知识：0.1+0.2=0.3"
        ),
        ScoreModificationTemplate(
            "math_homework_bad",
            -2.0,
            "数学作业缺交/未写",
            "冷知识：0.1+0.2=0.30000000000000004",
        ),
        ScoreModificationTemplate(
            "English_reading_good", 2.0, "英语背诵提前完成", "难道你不是临时背的？"
        ),
        ScoreModificationTemplate(
            "English_reading_last_for_week",
            -20.0,
            "英语背诵未完成<7天>",
            "孩子，该去背你的2b了！",
        ),  # 扣20分？！！这合理吗...
        ScoreModificationTemplate("English_class_good", 2.0, "英语课堂表扬", "English"),
        ScoreModificationTemplate(
            "English_class_bad", -2.0, "英语课堂批评", "E那个历史"
        ),
        ScoreModificationTemplate(
            "English_homework_best", 4.0, "英语作业A++", "OHHHHHHHHHHHHHH"
        ),
        ScoreModificationTemplate(
            "English_homework_good", 2.0, "英语作业A+", "Pass（赏析在此处的文学效果）"
        ),
        ScoreModificationTemplate(
            "English_homework_normal",
            0.0,
            "英语作业A",
            "没用小寄巧：多写笔记能提升等第",
        ),
        ScoreModificationTemplate("English_homework_bad", -2.0, "英语作业B", "Bruh"),
        ScoreModificationTemplate(
            "English_homework_worst", -3.0, "英语作业C", "Cinema（音译）"
        ),
        ScoreModificationTemplate(
            "English_homework_missing",
            -4.0,
            "英语作业未完成",
            "孩子，该去写你的英语作业了！",
        ),
        ScoreModificationTemplate(
            "physics_homework_best", 4.0, "物理作业A++", '"这不有手就行吗？"'
        ),
        ScoreModificationTemplate(
            "physics_homework_better", 3.0, "物理作业A+", '"这不有手就行吗？"'
        ),
        ScoreModificationTemplate(
            "physics_homework_good",
            2.0,
            "物理作业A",
            "烫知识：物理是唯一一名A也加分的学科",
        ),
        ScoreModificationTemplate(
            "physics_homework_little_good", 1.0, "物理作业A-", "够仁慈了吧A-也加分"
        ),
        ScoreModificationTemplate(
            "physics_homework_normal", 0.0, "物理作业B+", "孩子你很危险"
        ),
        ScoreModificationTemplate(
            "physics_homework_bad", -2.0, "物理作业B", "死了啦都你害的啦"
        ),
        ScoreModificationTemplate(
            "physics_homework_worst", -3.0, "物理作业C", "小心刘老师用p=F/S压缩你"
        ),
        ScoreModificationTemplate(
            "physics_homework_missing",
            -4.0,
            "物理作业未完成",
            "孩子，该去写你的物理作业了！",
        ),
        ScoreModificationTemplate(
            "physics_class_good", 2.0, "物理课堂表扬", "不知道填什么，如题吧"
        ),
        ScoreModificationTemplate(
            "physics_class_bad", -2.0, "物理课堂批评", "秉公执法（bushi）"
        ),
        ScoreModificationTemplate(
            "history_homework_good", 2.0, "历史作业A+", '"黄玲老师怎么突然变这么好？"'
        ),
        ScoreModificationTemplate(
            "history_homework_normal", 0.0, "历史作业A", "中规中矩，但容易趋势"
        ),
        ScoreModificationTemplate(
            "history_homework_little_bad",
            -1.0,
            "历史作业A-",
            "黄玲老师怎么突然变这么__？",
        ),
        ScoreModificationTemplate(
            "history_homework_bad", -2.0, "历史作业B", "路易十六快乐台"
        ),
        ScoreModificationTemplate(
            "history_homework_worst",
            -3.0,
            "历史作业C",
            "你猜商鞅为什么不爱看小马宝莉？ ",
        ),
        ScoreModificationTemplate(
            "history_homework_missing",
            -4.0,
            "历史作业未完成",
            "你获得了<历史>星神的凝视！（*脖子发凉*）",
        ),
        ScoreModificationTemplate(
            "history_class_good", 2.0, "历史课堂表扬", "孩子，你有至高无上的勇气"
        ),
        ScoreModificationTemplate(
            "history_class_bad", -2.0, "历史课堂批评", '"生命因何而沉睡？"'
        ),
        ScoreModificationTemplate(
            "biology_class_good", 2.0, "生物课堂表扬", "获得成就：我从哪里来？"
        ),
        ScoreModificationTemplate(
            "biology_class_bad", 2.0, "生物课堂批评", "获得成就：亲身见到达尔文"
        ),
        ScoreModificationTemplate(
            "biology_homework_good", 2.0, "生物作业A+", "所以我们得到这两种性状是1:31"
        ),
        ScoreModificationTemplate(
            "biology_homework_bad",
            -2.0,
            "生物作业缺交/不合格",
            "所以我们得到做对题目的概率是1:31",
        ),
        ScoreModificationTemplate(
            "geography_class_good", 2.0, "地理课堂表扬", "死去的回忆又开始攻击我"
        ),
        ScoreModificationTemplate(
            "geography_class_bad",
            -2.0,
            "地理课堂批评",
            '"后面那位，对，就是你，你上来连线"',
        ),
        ScoreModificationTemplate(
            "geography_homework_good",
            2.0,
            "地理作业A+",
            "推导得澳大利亚房车多是因为地广人稀",
        ),
        ScoreModificationTemplate(
            "geography_homework_bad",
            -2.0,
            "地理作业缺交/不合格",
            "地理老师开着房车马上就到你家门口",
        ),
        ScoreModificationTemplate(
            "chemistry_class_good", 2.0, "化学课堂表扬", "高锰酸钾制氧气"
        ),
        ScoreModificationTemplate(
            "chemistry_class_bad", -2.0, "化学课堂批评", "高锰酸钾加白糖"
        ),
        ScoreModificationTemplate(
            "chemistry_homework_good", -2.0, "化学作业100", "错误示范：用火柴点燃酒精灯"
        ),
        ScoreModificationTemplate(
            "chemistry_homework_bad",
            -4.0,
            "化学作业缺交/不合格",
            "正确示范：用酒精灯点燃化学老师",
        ),
        ScoreModificationTemplate(
            "laws_homework_best", 4.0, "道法作业A++", "能抓好老鼠的就是好猫"
        ),
        ScoreModificationTemplate(
            "laws_homework_good", 2.0, "道法作业A+", "能抓老鼠的就是好猫"
        ),
        ScoreModificationTemplate(
            "laws_homework_normal", 0.0, "道法作业A", "能抓老鼠的就是猫"
        ),  # 为什么是laws？？
        ScoreModificationTemplate(
            "laws_homework_bad", -2.0, "道法作业B", "不换思想就换人"
        ),
        ScoreModificationTemplate(
            "laws_homework_worst", -3.0, "道法作业C", '"遵纪守法"好公民'
        ),
        ScoreModificationTemplate(
            "laws_homework_missing", -4.0, "道法作业缺交", "发逐出境"
        ),
        ScoreModificationTemplate(
            "laws_class_best", 2.0, "道法课堂回答问题表扬", "遵纪守法好公民"
        ),
        ScoreModificationTemplate(
            "laws_class_good", 1.0, "道法课堂回答问题参与奖", "（赞美太阳）"
        ),
        ScoreModificationTemplate("laws_class_bad", -2.0, "道法课堂批评", "缺德与犯法"),
        ScoreModificationTemplate(
            "attendance_bad", -1.0, "考勤待改进", "please思考你的人生"
        ),
        ScoreModificationTemplate(
            "wearing_bad", -1.0, "着装待改进", "cjsy的校服我爱死你个呜呜伯"
        ),
        ScoreModificationTemplate("reading_good", 2.0, "朗读表扬", "扩音器转世认证"),
        ScoreModificationTemplate(
            "reading_bad", -2.0, "朗读批评", "不会开口的话建议学一下手语"
        ),
        ScoreModificationTemplate(
            "eye_exercise_bad", -1.0, "眼操批评", "近视：亻尔 女子"
        ),
        ScoreModificationTemplate(
            "eye_exercise_good", 1.0, "眼操表扬", "近视：亻尔 女马"
        ),
        ScoreModificationTemplate(
            "exercise_bad", -2.0, "大课间批评", "文明其体魄野蛮其精神"
        ),
        ScoreModificationTemplate(
            "exercise_good", 2.0, "大课间表扬", "文明其精神野蛮其体魄"
        ),
        ScoreModificationTemplate(
            "school_life_bad", -2.0, "校园纪律批评", "我也不知道你干了啥"
        ),
        ScoreModificationTemplate(
            "seriously_criticized", -5.0, "严重批评", '"你，给我出去！"'
        ),
        ScoreModificationTemplate(
            "cleaning_5.0_leader",
            4.0,
            "卫生5.0（组长）",
            "金牌保洁团队！",
            is_visible=False,
            cant_replace=True,
        ),
        ScoreModificationTemplate(
            "cleaning_5.0_member",
            3.0,
            "卫生5.0（组员）",
            "金牌保洁团队！",
            is_visible=False,
            cant_replace=True,
        ),
        ScoreModificationTemplate(
            "cleaning_4.9_leader",
            3.0,
            "卫生4.9（组长）",
            "银牌保洁团队（或者是老师看走眼了）",
            is_visible=False,
            cant_replace=True,
        ),
        ScoreModificationTemplate(
            "cleaning_4.9_member",
            2.0,
            "卫生4.9（组员）",
            "银牌保洁团队（或者是老师看走眼了）",
            is_visible=False,
            cant_replace=True,
        ),
        ScoreModificationTemplate(
            "cleaning_4.8_leader",
            0.0,
            "卫生4.8（组长）",
            "也还好吧",
            is_visible=False,
            cant_replace=True,
        ),
        ScoreModificationTemplate(
            "cleaning_4.8_member",
            0.0,
            "卫生4.8（组员）",
            "也还好吧",
            is_visible=False,
            cant_replace=True,
        ),
        ScoreModificationTemplate(
            "cleaning_4.7_leader",
            -3.0,
            "卫生4.7（组长）",
            "无牌照保洁团队",
            is_visible=False,
            cant_replace=True,
        ),
        ScoreModificationTemplate(
            "cleaning_4.7_member",
            -2.0,
            "卫生4.7（组员）",
            "无牌照保洁团队",
            is_visible=False,
            cant_replace=True,
        ),
        ScoreModificationTemplate(
            "cleaning_4.6_and_lower_leader",
            -4.0,
            "卫生4.6及以下（组长）",
            "建议把自己打扫出教室",
            is_visible=False,
            cant_replace=True,
        ),
        ScoreModificationTemplate(
            "cleaning_4.6_and_lower_member",
            -3.0,
            "卫生4.6及以下（组员）",
            "建议把自己打扫出教室",
            is_visible=False,
            cant_replace=True,
        ),
    ]
)
"""默认模板"""


DEFAULT_CLASSES: OrderedKeyList[Class] = OrderedKeyList(
    [
        Class(
            "测试班级",
            "王老师",
            {
                1: Student(
                    "1号学生",
                    1,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_3",
                ),
                2: Student(
                    "2号学生",
                    2,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_7",
                ),
                3: Student(
                    "3号学生",
                    3,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_7",
                ),
                4: Student(
                    "4号学生",
                    4,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_5",
                ),
                5: Student(
                    "5号学生",
                    5,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_2",
                ),
                6: Student(
                    "6号学生",
                    6,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_2",
                ),
                7: Student(
                    "7号学生",
                    7,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_6",
                ),
                8: Student(
                    "8号学生",
                    8,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_1",
                ),
                9: Student(
                    "9号学生",
                    9,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_3",
                ),
                10: Student(
                    "10号学生",
                    10,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_2",
                ),
                11: Student(
                    "11号学生",
                    11,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_7",
                ),
                12: Student(
                    "12号学生",
                    12,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_4",
                ),
                13: Student(
                    "13号学生",
                    13,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_6",
                ),
                14: Student(
                    "14号学生",
                    14,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_4",
                ),
                15: Student(
                    "15号学生",
                    15,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_4",
                ),
                16: Student(
                    "16号学生",
                    16,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_5",
                ),
                17: Student(
                    "17号学生",
                    17,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_3",
                ),
                21: Student(
                    "21号学生",
                    21,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_1",
                ),
                22: Student(
                    "22号学生",
                    22,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_2",
                ),
                23: Student(
                    "23号学生",
                    23,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_7",
                ),
                24: Student(
                    "24号学生",
                    24,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_3",
                ),
                25: Student(
                    "25号学生",
                    25,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_3",
                ),
                26: Student(
                    "26号学生",
                    26,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_3",
                ),
                28: Student(
                    "28号学生",
                    28,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_5",
                ),
                29: Student(
                    "29号学生",
                    29,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_5",
                ),
                30: Student(
                    "30号学生",
                    30,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_6",
                ),
                31: Student(
                    "31号学生",
                    31,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_6",
                ),
                32: Student(
                    "32号学生",
                    32,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_3",
                ),
                33: Student(
                    "33号学生",
                    33,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_7",
                ),
                34: Student(
                    "34号学生",
                    34,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_2",
                ),
                35: Student(
                    "35号学生",
                    35,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_5",
                ),
                36: Student(
                    "36号学生",
                    36,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_1",
                ),
                37: Student(
                    "37号学生",
                    37,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_1",
                ),
                38: Student(
                    "38号学生",
                    38,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_2",
                ),
                40: Student(
                    "40号学生",
                    40,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_6",
                ),
                41: Student(
                    "41号学生",
                    41,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_7",
                ),
                42: Student(
                    "42号学生",
                    42,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_4",
                ),
                43: Student(
                    "43号学生",
                    43,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_1",
                ),
                44: Student(
                    "44号学生",
                    44,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_5",
                ),
                45: Student(
                    "45号学生",
                    45,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_4",
                ),
                46: Student(
                    "46号学生",
                    46,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_5",
                ),
                47: Student(
                    "47号学生",
                    47,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_7",
                ),
                49: Student(
                    "49号学生",
                    49,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_4",
                ),
                50: Student(
                    "50号学生",
                    50,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_1",
                ),
                51: Student(
                    "51号学生",
                    51,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_1",
                ),
                52: Student(
                    "52号学生",
                    52,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_6",
                ),
                53: Student(
                    "53号学生",
                    53,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_6",
                ),
                54: Student(
                    "54号学生",
                    54,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_2",
                ),
                55: Student(
                    "55号学生",
                    55,
                    0.0,
                    "CLASS_TEST",
                    {},
                    achievements={},
                    belongs_to_group="group_4",
                ),
            },
            "CLASS_TEST",
            {},
            {},
            {
                "Chinese": HomeworkRule(
                    "Chinese",
                    "语文",
                    "创建者",
                    {
                        "A++": DEFAULT_SCORE_TEMPLATES["Chinese_homework_best"],
                        "A+": DEFAULT_SCORE_TEMPLATES["Chinese_homework_good"],
                        "A": DEFAULT_SCORE_TEMPLATES["Chinese_homework_normal"],
                        "B": DEFAULT_SCORE_TEMPLATES["Chinese_homework_bad"],
                        "C/缺交/未写": DEFAULT_SCORE_TEMPLATES[
                            "Chinese_homework_worst"
                        ],
                    },
                ),
                "math": HomeworkRule(
                    "math",
                    "数学",
                    "创建者",
                    {
                        "100": DEFAULT_SCORE_TEMPLATES["math_homework_good"],
                        "不合格/缺交/未写": DEFAULT_SCORE_TEMPLATES[
                            "math_homework_bad"
                        ],
                    },
                ),
                "English": HomeworkRule(
                    "English",
                    "英语",
                    "创建者",
                    {
                        "A++": DEFAULT_SCORE_TEMPLATES["English_homework_best"],
                        "A+": DEFAULT_SCORE_TEMPLATES["English_homework_good"],
                        "A": DEFAULT_SCORE_TEMPLATES["English_homework_normal"],
                        "B": DEFAULT_SCORE_TEMPLATES["English_homework_bad"],
                        "C/缺交/未写": DEFAULT_SCORE_TEMPLATES[
                            "English_homework_worst"
                        ],
                    },
                ),
                "physics": HomeworkRule(
                    "physics",
                    "物理",
                    "创建者",
                    {
                        "A++": DEFAULT_SCORE_TEMPLATES["physics_homework_best"],
                        "A+": DEFAULT_SCORE_TEMPLATES["physics_homework_better"],
                        "A": DEFAULT_SCORE_TEMPLATES["physics_homework_good"],
                        "A-": DEFAULT_SCORE_TEMPLATES["physics_homework_little_good"],
                        "B+": DEFAULT_SCORE_TEMPLATES["physics_homework_normal"],
                        "B": DEFAULT_SCORE_TEMPLATES["physics_homework_bad"],
                        "C/缺交/未写": DEFAULT_SCORE_TEMPLATES[
                            "physics_homework_worst"
                        ],
                    },
                ),
                "chemistry": HomeworkRule(
                    "chemistry",
                    "化学",
                    "创建者",
                    {
                        "100": DEFAULT_SCORE_TEMPLATES["chemistry_homework_good"],
                        "不合格/缺交/未写": DEFAULT_SCORE_TEMPLATES[
                            "chemistry_homework_bad"
                        ],
                    },
                ),
                "politics": HomeworkRule(
                    "politics",
                    "政治",
                    "创建者",
                    {
                        "A+": DEFAULT_SCORE_TEMPLATES["laws_homework_good"],
                        "B": DEFAULT_SCORE_TEMPLATES["laws_homework_bad"],
                        "C/缺交/未写": DEFAULT_SCORE_TEMPLATES["laws_homework_worst"],
                    },
                ),
                "history": HomeworkRule(
                    "history",
                    "历史",
                    "创建者",
                    {
                        "A+": DEFAULT_SCORE_TEMPLATES["history_homework_good"],
                        "A": DEFAULT_SCORE_TEMPLATES["history_homework_normal"],
                        "B": DEFAULT_SCORE_TEMPLATES["history_homework_bad"],
                        "C/缺交/未写": DEFAULT_SCORE_TEMPLATES[
                            "history_homework_worst"
                        ],
                    },
                ),
            },
        )
    ]
)
"""默认班级"""

DEFAULT_CLASSES["CLASS_TEST"].cleaning_mapping = {
    1: {
        "member": [
            DEFAULT_CLASSES["CLASS_TEST"].students[12],
            DEFAULT_CLASSES["CLASS_TEST"].students[13],
            DEFAULT_CLASSES["CLASS_TEST"].students[55],
            DEFAULT_CLASSES["CLASS_TEST"].students[43],
            DEFAULT_CLASSES["CLASS_TEST"].students[31],
            DEFAULT_CLASSES["CLASS_TEST"].students[29],
            DEFAULT_CLASSES["CLASS_TEST"].students[11],
            DEFAULT_CLASSES["CLASS_TEST"].students[32],
            DEFAULT_CLASSES["CLASS_TEST"].students[5],
        ],
        "leader": [DEFAULT_CLASSES["CLASS_TEST"].students[26]],
    },
    2: {
        "member": [
            DEFAULT_CLASSES["CLASS_TEST"].students[51],
            DEFAULT_CLASSES["CLASS_TEST"].students[22],
            DEFAULT_CLASSES["CLASS_TEST"].students[24],
            DEFAULT_CLASSES["CLASS_TEST"].students[4],
            DEFAULT_CLASSES["CLASS_TEST"].students[42],
            DEFAULT_CLASSES["CLASS_TEST"].students[45],
            DEFAULT_CLASSES["CLASS_TEST"].students[1],
            DEFAULT_CLASSES["CLASS_TEST"].students[30],
        ],
        "leader": [DEFAULT_CLASSES["CLASS_TEST"].students[7]],
    },
    3: {
        "member": [
            DEFAULT_CLASSES["CLASS_TEST"].students[21],
            DEFAULT_CLASSES["CLASS_TEST"].students[33],
            DEFAULT_CLASSES["CLASS_TEST"].students[53],
            DEFAULT_CLASSES["CLASS_TEST"].students[16],
            DEFAULT_CLASSES["CLASS_TEST"].students[2],
            DEFAULT_CLASSES["CLASS_TEST"].students[8],
            DEFAULT_CLASSES["CLASS_TEST"].students[44],
            DEFAULT_CLASSES["CLASS_TEST"].students[25],
            DEFAULT_CLASSES["CLASS_TEST"].students[50],
        ],
        "leader": [DEFAULT_CLASSES["CLASS_TEST"].students[34]],
    },
    4: {
        "member": [
            DEFAULT_CLASSES["CLASS_TEST"].students[35],
            DEFAULT_CLASSES["CLASS_TEST"].students[6],
            DEFAULT_CLASSES["CLASS_TEST"].students[54],
            DEFAULT_CLASSES["CLASS_TEST"].students[17],
            DEFAULT_CLASSES["CLASS_TEST"].students[37],
            DEFAULT_CLASSES["CLASS_TEST"].students[40],
            DEFAULT_CLASSES["CLASS_TEST"].students[15],
            DEFAULT_CLASSES["CLASS_TEST"].students[3],
            DEFAULT_CLASSES["CLASS_TEST"].students[52],
        ],
        "leader": [DEFAULT_CLASSES["CLASS_TEST"].students[46]],
    },
    5: {
        "member": [
            DEFAULT_CLASSES["CLASS_TEST"].students[49],
            DEFAULT_CLASSES["CLASS_TEST"].students[10],
            DEFAULT_CLASSES["CLASS_TEST"].students[23],
            DEFAULT_CLASSES["CLASS_TEST"].students[28],
            DEFAULT_CLASSES["CLASS_TEST"].students[14],
            DEFAULT_CLASSES["CLASS_TEST"].students[9],
            DEFAULT_CLASSES["CLASS_TEST"].students[36],
            DEFAULT_CLASSES["CLASS_TEST"].students[47],
        ],
        "leader": [DEFAULT_CLASSES["CLASS_TEST"].students[41]],
    },
}
"""打扫卫生对应人选"""


DEFAULT_CLASSES["CLASS_TEST"].groups = {
    "group_1": Group(
        "group_1",
        "一团",
        DEFAULT_CLASSES["CLASS_TEST"].students[51],
        [
            DEFAULT_CLASSES["CLASS_TEST"].students[51],
            DEFAULT_CLASSES["CLASS_TEST"].students[21],
            DEFAULT_CLASSES["CLASS_TEST"].students[36],
            DEFAULT_CLASSES["CLASS_TEST"].students[37],
            DEFAULT_CLASSES["CLASS_TEST"].students[43],
            DEFAULT_CLASSES["CLASS_TEST"].students[50],
            DEFAULT_CLASSES["CLASS_TEST"].students[8],
        ],
        "CLASS_TEST",
    ),
    "group_2": Group(
        "group_2",
        "二团",
        DEFAULT_CLASSES["CLASS_TEST"].students[10],
        [
            DEFAULT_CLASSES["CLASS_TEST"].students[5],
            DEFAULT_CLASSES["CLASS_TEST"].students[6],
            DEFAULT_CLASSES["CLASS_TEST"].students[10],
            DEFAULT_CLASSES["CLASS_TEST"].students[22],
            DEFAULT_CLASSES["CLASS_TEST"].students[34],
            DEFAULT_CLASSES["CLASS_TEST"].students[41],
            DEFAULT_CLASSES["CLASS_TEST"].students[54],
        ],
        "CLASS_TEST",
    ),
    "group_3": Group(
        "group_3",
        "三团",
        DEFAULT_CLASSES["CLASS_TEST"].students[25],
        [
            DEFAULT_CLASSES["CLASS_TEST"].students[1],
            DEFAULT_CLASSES["CLASS_TEST"].students[9],
            DEFAULT_CLASSES["CLASS_TEST"].students[17],
            DEFAULT_CLASSES["CLASS_TEST"].students[24],
            DEFAULT_CLASSES["CLASS_TEST"].students[25],
            DEFAULT_CLASSES["CLASS_TEST"].students[26],
            DEFAULT_CLASSES["CLASS_TEST"].students[32],
        ],
        "CLASS_TEST",
        """对团员十分包容 比如包容肘晋吃垃圾 这件事只有我们团知道😉✌ 
团长十分善良美丽大方 特别表扬团员鸭爱 也十分的善良温柔大方 
对文鸡进行批评 因为他一点都不大方 不给鸭爱和美丽的团长安鸡讲题 必须大大的批评 体现了团长憎恶分明 公平正直
还有我们十分活泼可爱的艾吃鸡""",
    ),
    "group_4": Group(
        "group_4",
        "四团",
        DEFAULT_CLASSES["CLASS_TEST"].students[49],
        [
            DEFAULT_CLASSES["CLASS_TEST"].students[49],
            DEFAULT_CLASSES["CLASS_TEST"].students[12],
            DEFAULT_CLASSES["CLASS_TEST"].students[14],
            DEFAULT_CLASSES["CLASS_TEST"].students[45],
            DEFAULT_CLASSES["CLASS_TEST"].students[15],
            DEFAULT_CLASSES["CLASS_TEST"].students[42],
            DEFAULT_CLASSES["CLASS_TEST"].students[55],
        ],
        "CLASS_TEST",
    ),
    "group_5": Group(
        "group_5",
        "五团",
        DEFAULT_CLASSES["CLASS_TEST"].students[29],
        [
            DEFAULT_CLASSES["CLASS_TEST"].students[4],
            DEFAULT_CLASSES["CLASS_TEST"].students[16],
            DEFAULT_CLASSES["CLASS_TEST"].students[28],
            DEFAULT_CLASSES["CLASS_TEST"].students[35],
            DEFAULT_CLASSES["CLASS_TEST"].students[44],
            DEFAULT_CLASSES["CLASS_TEST"].students[46],
            DEFAULT_CLASSES["CLASS_TEST"].students[29],
        ],
        "CLASS_TEST",
    ),
    "group_6": Group(
        "group_6",
        "六团",
        DEFAULT_CLASSES["CLASS_TEST"].students[40],
        [
            DEFAULT_CLASSES["CLASS_TEST"].students[7],
            DEFAULT_CLASSES["CLASS_TEST"].students[13],
            DEFAULT_CLASSES["CLASS_TEST"].students[30],
            DEFAULT_CLASSES["CLASS_TEST"].students[31],
            DEFAULT_CLASSES["CLASS_TEST"].students[52],
            DEFAULT_CLASSES["CLASS_TEST"].students[53],
            DEFAULT_CLASSES["CLASS_TEST"].students[40],
        ],
        "CLASS_TEST",
    ),
    "group_7": Group(
        "group_7",
        "七团",
        DEFAULT_CLASSES["CLASS_TEST"].students[2],
        [
            DEFAULT_CLASSES["CLASS_TEST"].students[2],
            DEFAULT_CLASSES["CLASS_TEST"].students[3],
            DEFAULT_CLASSES["CLASS_TEST"].students[11],
            DEFAULT_CLASSES["CLASS_TEST"].students[23],
            DEFAULT_CLASSES["CLASS_TEST"].students[33],
            DEFAULT_CLASSES["CLASS_TEST"].students[38],
            DEFAULT_CLASSES["CLASS_TEST"].students[47],
        ],
        "CLASS_TEST",
    ),
}
"默认小组"


DEFAULT_ACHIEVEMENTS: Dict[str, AchievementTemplate] = {
    "beyond_life_and_death": AchievementTemplate(
        "beyond_life_and_death",
        "超越生死",
        "经历了人生的大波折，我已看淡生死了",
        lowest_score_range=(-inf, -20),
        score_range=(1, inf),
        sound=os.path.join(sound_file_path, "bruh.ogg"),
        icon="img/tips/beyond_life_and_death.jpg",
        condition_info="一周分数达到-20后回正",
        further_info="""其实我们做出来就好奇会不会真的有人会达成这个成就""",
    ),
    "early_bird": AchievementTemplate(
        "early_bird",
        "早起的鸟儿",
        "不用我说了",
        modify_key_range=("go_to_school_early", 3, inf),
        condition_info="一周早到3次",
        further_info="""这个成就应该挺简单的...?""",
    ),
    "top_of_life": AchievementTemplate(
        "top_of_life",
        "人生巅峰",
        "我无敌辣！",
        score_range=(50, inf),
        score_rank_range=(1, 1),
        highest_score_range=(50, inf),
        condition_info="分数>=50，获得班上分数第一",
        further_info="""稳定发挥啊""",
    ),
    "top_of_life_2": AchievementTemplate(
        "top_of_life_2",
        "人生癫疯",
        "这次是真的无敌辣！",
        score_range=(-inf, -20),
        score_rank_range=(-1, -1),
        highest_score_range=(-inf, 20),
        icon="img/tips/top_of_life_2.jpg",
        condition_info="分数<=-20，获得班上分数倒数第一",
        further_info="""从某种意义上也算是稳定发挥了""",
    ),
    "bad_starting": AchievementTemplate(
        "bad_starting",
        "开幕雷击",
        "美好的一天从扣分开始",
        score_range=(-inf, -1),
        highest_score_range=(0, 0),
        lowest_score_range=(-inf, -5),
        condition_info="刚开局就一直扣分（大于等于5分）",
        further_info="""你真棒，又为你们的小组做出了巨大贡献""",
    ),
    "do_nothing": AchievementTemplate(
        "do_nothing",
        "一事无成",
        "bro分数很稳定啊",
        score_range=(-5, 5),
        highest_score_range=(0, 5),
        lowest_score_range=(-5, 0),
        others=lambda d: len(
            [history for history in d.student.history.values() if history.executed]
        )
        >= 10,
        condition_info="在接受超过10次点评的情况下分数始终在-5到5之间",
        further_info="""我有种不祥的预感""",
    ),
    "do_nothing_2": AchievementTemplate(
        "do_nothing_2",
        "一事无成 - 进阶",
        "bro分数不是一般的稳定啊",
        score_range=(-5, 5),
        highest_score_range=(0, 5),
        lowest_score_range=(-5, 0),
        others=lambda d: len(
            [history for history in d.student.history.values() if history.executed]
        )
        >= 15,
        condition_info="在接受超过15次点评的情况下分数始终在-5到5之间",
        further_info="""丸辣，这周又是0分""",
    ),
    "producer": AchievementTemplate(
        "producer",
        "终极奉献",
        "你所在的小组应该感谢你的",
        score_range=(30, inf),
        others=lambda d: d.student.score
        >= d.student.get_group(d.class_obs).total_score * 0.5,
        condition_info="分数>=30，且分数大于全团的一半",
        further_info="""\"包带飞的！\"\n\"黑子说话！\"""",
    ),
    "extremal_dodge": AchievementTemplate(
        "extremal_dodge",
        "极限闪避",
        "哥们是跟潘周聃学过吗？",
        others=lambda data: len(data.student.history) >= 15
        and all([m.mod > 0 for m in data.student.history.values() if m.executed]),
        condition_info="在连续15次计分中没有任何扣分",
        further_info="""看来你对班级规则倒背如流了""",
    ),
    "extremal_dodge_2": AchievementTemplate(
        "extremal_dodge_2",
        "极限闪避 - 进阶",
        "哥们开了吧？",
        others=lambda data: len(data.student.history) >= 25
        and all([m.mod > 0 for m in data.student.history.values() if m.executed]),
        condition_info="在连续25次计分中没有任何扣分",
        further_info="""不懂就问，班级规则是您定的吗？\n（不过他们计分能有这么勤快，一周25条？）""",
    ),
    "exercise_good": AchievementTemplate(
        "exercise_good",
        "身强体健",
        "计算题：我们一周需要跑多少米",
        others=lambda data: sum(
            s.mod
            for s in data.student.history.values()
            if s.temp.key == "exercise_good"
        )
        >= 15,
        modify_key_range=("exercise_good", 5, inf),
        condition_info="一周大课间的得分>=15且表扬次数>=5",
        further_info="下次物资搬运就找你了",
    ),
    "exercise_bad": AchievementTemplate(
        "exercise_bad",
        "身弱体衰",
        "计算题：你一周可以偷懒多少米",
        others=lambda data: sum(
            s.mod for s in data.student.history.values() if s.temp.key == "exercise_bad"
        )
        <= -3,
        modify_key_range=("exercise_bad", 2, inf),
        condition_info="一周大课间的扣分>=3且批评次数>=2",
        further_info="下次物资搬运就别找你了",
    ),
    "score_too_high": AchievementTemplate(
        "score_too_high",
        "天人合一",
        '"______, 我已登神！"',
        others=lambda data: data.student.score >= 80,
        condition_info="分数>=80",
        further_info="老师们的宠儿",
    ),
    "score_too_low": AchievementTemplate(
        "score_too_low",
        "人神共愤",
        " -- 你是来搞笑的吧？\n -- 您所拨打的用户已离开地球",
        others=lambda data: data.student.score <= -40,
        condition_info="分数<=-40",
        further_info="团队的噩梦",
    ),
    "developer_main": AchievementTemplate(
        "developer_main",
        "开发者 - 代码贡献者",
        "写代码实在是太有意思啦",
        num_equals=[7],
        condition_info="成为这个工具的开发者",
        further_info="哇这代码写得真的是太太太太太太太太太太太太太太太太太太太太太太太太太太太太太太好了\n"
        "哇0.1+0.2=0.30000000000000004\n哇pyqt你tm怎么又卡住了\n\n"
        "python: ZeroDivisionError: division by zero\n我：animoac\n\n"
        "（一个被出错还不提示直接似掉的SB一样的pyside6玩爆的程序员的遗言）",
    ),
    "developer_login": AchievementTemplate(
        "developer_login",
        "开发者 - 登陆模块开发者",
        "笑死登录模块至今还没做",
        num_equals=[9],
        condition_info="成为这个工具的开发者",
        further_info='"不是，我登录模块去哪了？"\n"被你覆盖掉了？"\n"我上早八"\n（地狱笑话：其实我多用户的接口已经炸了）',
    ),
    "developer_vpn": AchievementTemplate(
        "developer_vpn",
        "开发者 - God uses the VPN",
        "佛跳墙实在是太好吃啦",
        num_equals=[14],
        condition_info="成为这个工具的开发者",
        further_info="问ChatGPT怎么写代码，ChatGPT：佛跳墙，佛跳墙（由AI生成）\n"
        "（真的是AI自己写的吗？）",
    ),
    "mascot_normaltype": AchievementTemplate(
        "mascot_normaltype",
        "吉祥物 - 真正的吉祥物",
        "这是真的吉祥物了",
        num_equals=[3],
        condition_info="成为这个工具的开发者\n（实际这个项目动都没动）",
        further_info=("但是你真的不干点什么吗？\n" + "但是你真的参加这个项目吗（?）"),
    ),
    "mascot_writer": AchievementTemplate(
        "mascot_writer",
        "吉祥物 - 文学创作师",
        "程序中抽象文案的提供者\n (至少是99%的)",
        num_equals=[41],
        condition_info="成为这个工具的开发者\n（文学创作也算开发吧）",
        further_info=(
            "特别鸣谢：语文老师\n"
            "（7：尝试分析这句话的多重意蕴）\n"
            "（...）\n"
            "（出现异常：java.lang.NullPointerException）"
        ),
    ),
    "finally_returns": AchievementTemplate(
        "finally_returns",
        "回归原点",
        "所以这周我干了啥？",
        condition_info="努力了一周分数还是0",
        further_info="忙活了一周，终于把自己忙活死了\n"
        "（说实话这是我最有自信能拿到的成就）",
        others=[
            lambda data: data.student.last_reset_info.score == 0,
            lambda data: data.student.last_reset_info.highest_score != 0
            or data.student.last_reset_info.lowest_score != 0,
        ],
    ),
    "just_a_little": AchievementTemplate(
        "just_a_little",
        "我没事，我很好",
        "这个成就怎么这么费脑子啊",
        condition_info="分数>=20, 在距离常规分第一仅有2分时就被扣分",
        score_range=(20, inf),
        others=[
            lambda d: d.student.highest_score > d.student.score,
            # 达到最高分之后扣过分了
            lambda d: len(d.student.history) > 0
            and (
                d.class_obs.rank_non_dumplicate[0][1].score
                - (d.student.score - list(d.student.history.values())[-1].mod)
                <= 2
            ),
            # 排名第一的人的分数减去学生上一次的分数小于等于2
        ],
        further_info="也就几分而已了...",
    ),
    "group_savior": AchievementTemplate(
        "group_savior",
        "力挽狂澜",
        "总有人敢于直面常规分的威光",
        condition_info="在本团有>=2个负分成员时仍然依靠自己>=40的分数带领小组获得团总分前4",
        further_info="这是真神，让我猜猜，是不是擦脚布（？",
        score_range=(40, inf),
        others=[
            lambda d: sorted(
                [
                    g.total_score
                    for g in d.groups.values()
                    if g.belongs_to == d.student.belongs_to
                ],
                reverse=True,
            )[min(len(d.groups) - 1, 3)]
            <= d.student.get_group(d.class_obs).total_score,
            lambda d: len(
                [s for s in d.student.get_group(d.class_obs).members if s.score < 0]
            )
            >= 2,
        ],
    ),
    "the_real_center": AchievementTemplate(
        "the_real_center",
        "吉祥物体验卡",
        "全团的中心！",
        condition_info="本人分数四舍五入刚好等于团均分",
        score_range=[(5, inf), (-inf, -5)],
        others=[
            lambda d: round(d.student.score)
            == round(d.student.get_group(d.class_obs).average_score)
        ],
    ),
    "chosen_one": AchievementTemplate(
        "chosen_one",
        "天选之子",
        "这东西真就是随机给的",
        condition_info="每周随机选一个人给",
        further_info="幸运，但没用",
        others=[
            lambda d: d.student.num
            == int(d.class_obs.base.last_reset) % len(d.class_obs.target_class.students)
        ],
    ),
    "interrupts_cast": AchievementTemplate(
        "interrupts_cast",
        "打断施法",
        "孩子们这并不好笑",
        condition_info='在得到了"极限闪避"之后被扣分',
        further_info="See you again",
        others=[
            lambda d: any(
                [m.mod < 0 for m in d.student.history.values() if m.executed]
            ),
            lambda d: "extremal_dodge"
            in [a.temp.key for a in d.student.achievements.values()],
        ],
    ),
    "interrupts_cast_2": AchievementTemplate(
        "interrupts_cast_2",
        "沉重打击",
        "孩子们这并不好笑",
        condition_info='在得到了"极限闪避 - 进阶"之后被扣分',
        further_info="啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊",
        others=[
            lambda d: any(
                [m.mod < 0 for m in d.student.history.values() if m.executed]
            ),
            lambda d: "extremal_dodge_2"
            in [a.temp.key for a in d.student.achievements.values()],
        ],
    ),
    "without_backward": AchievementTemplate(
        "without_backward",
        "岿然不动",
        "从某种意义上这是一事无成的变种",
        condition_info="扣分次数>10, 但分数仍>10",
        score_range=(10, inf),
        further_info="小伤而已",
        others=[
            lambda d: len([m for m in d.student.history.values() if m.mod < 0]) > 10
        ],
    ),
    "turned_back": AchievementTemplate(
        "turned_back",
        "浪子回头",
        "______, 退钱！",
        condition_info="最低分<=-20后开始加分",
        further_info="浪子回头......？",
        lowest_score_range=(-20, -inf),
        score_range=(-19, inf),
    ),
    "I_dont_know_what_is_this": AchievementTemplate(
        "I_dont_know_what_is_this",
        "整风の运动",
        "至于你干啥了就不得而知了",
        condition_info='被"严肃批评"一次',
        further_info="无限制格斗（雾",
        others=[
            lambda d: "seriously_criticized"
            in [a.temp.key for a in d.student.achievements.values()]
        ],
    ),
    # 这个key值也是非常直白啊
    "breaking_upscore": AchievementTemplate(
        "breaking_upscore",
        "摧枯拉朽",
        "booooooooom",
        condition_info="一次加分15分",
        further_info="你真棒",
        others=[
            lambda d: len(d.student.history.values()) > 0
            and list(d.student.history.values())[-1].mod >= 15
        ],
    ),
    "stone_age": AchievementTemplate(
        "stone_age",
        "石器时代",
        "石器时代",
        condition_info="分数达到20",
        score_range=(20, inf),
        further_info="下一步是什么？",
    ),
    "going_down": AchievementTemplate(
        "going_down",
        "勇往直下",
        "GOGOGO!!!",
        condition_info="分数达到-10",
        score_range=(-inf, -10),
        further_info='"这下面的风景不错！"',
    ),
}

"""默认成就（基本没写多少）"""


# 为防止里面的key填错手动改的

a = copy.deepcopy(DEFAULT_ACHIEVEMENTS).values()
for achievement in a:
    DEFAULT_ACHIEVEMENTS[achievement.key] = achievement

t = copy.deepcopy(DEFAULT_SCORE_TEMPLATES).values()
for template in t:
    DEFAULT_SCORE_TEMPLATES[template.key] = template

c = copy.deepcopy(DEFAULT_CLASSES).values()
for _class in c:
    DEFAULT_CLASSES[_class.key] = _class
