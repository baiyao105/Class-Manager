from __future__ import annotations

import time
from collections.abc import Iterable
from typing import TYPE_CHECKING

from utils.algorithm import Stack, Thread
from utils.basetypes import Base

from ..classdataobj import ClassDataObj

if TYPE_CHECKING:
    from ..classobj import ClassObj
    from ..objects.scoremod import ScoreModification
    from ..objects.student import Student


class ClassStatusObserver:
    "班级状态侦测器"

    def __init__(self, base: ClassObj, class_id: str, tps: int = 20):
        """
        构造一个新的侦测器

        :param base: 班级数据 (self.classes)
        :param class_id: 班级id
        :param templates: 所有的分数修改模板
        """
        try:
            self.on_active: bool = False
            "侦测器是否正在运行"
            self.class_id: str = class_id
            "班级id"
            self.stu_score_ord: dict = {}
            "学生分数排序，不去重"
            self.classes = base.classes
            "班级数据"
            self.target_class = base.classes[self.class_id]
            "目标班级"
            self.templates = base.modify_templates
            "所有的分数修改模板"
            self.opreation_record: Stack[Iterable[ScoreModification]] = Stack([])
            "操作记录"
            self.base = base
            "算法基层"
            self.last_update = time.time()
            "上次更新时间"
            self.limited_tps = tps
            "侦测器最大刷新率"
            self.mspt: float = 0
            "侦测器每帧耗时"
            self.tps: float = 0
            "侦测器每秒帧数"
        except (
            KeyError,
            ValueError,
            AttributeError,
            TypeError,
        ) as unused:  # pylint: disable=unused-variable
            Base.log_exc("获取班级信息失败", "ClassStatusObserver.__init__")
            raise ClassDataObj.ObserverError("获取班级信息失败")

    def run(self):
        "内部用来启动侦测器的函数"
        self.on_active = True
        last_frame_time = time.time()
        while self.on_active:
            last_opreate_time = time.time()
            if self.limited_tps:
                time.sleep(max((1 / self.limited_tps) - (time.time() - last_frame_time), 0))
            last_frame_time = time.time()
            if time.time() - self.last_update > 1:
                self.last_update = time.time()
            for k, s in self.target_class.students.items():
                if s.num != k:
                    orig = s.num
                    s.num = k
                    Base.log(
                        "I",
                        f"学生 {s.name} 的学号已从 {orig} 变为 {s.num}（二者不同步）",
                        "ClassStatusObserver._start",
                    )
            self.stu_score_ord = dict(
                enumerate(
                    sorted(
                        list(self.classes[self.class_id].students.values()),
                        key=lambda a: a.score,
                    ),
                    start=1,
                )
            )
            self.mspt = (time.time() - last_frame_time) * 1000
            self.tps = 1 / max((time.time() - last_opreate_time), 0.001)

    @property
    def student_total_score(self) -> float:
        """班级总分"""
        return self.target_class.student_total_score

    @property
    def student_count(self) -> int:
        """班级人数"""
        return self.target_class.student_count

    @property
    def rank_non_dumplicate(self) -> list[tuple[int, Student]]:
        """
        学生分数排序，去重

        至于去重是个什么概念，举个例子
        >>> target_class.rank_non_dumplicate
        [
            (1, Student(name="某个学生", score=114, ...)),
            (2, Student(name="某个学生", score=51,  ...)),
            (2, Student(name="某个学生", score=51,  ...)),
            (4, Student(name="某个学生", score=41,  ...)),
            (5, Student(name="某个学生", score=9,   ...)),
            (5, Student(name="某个学生", score=9,   ...)),
            (7, Student(name="某个学生", score=1,   ...))
        ]

        （即List[Tuple[排名数，学生对象]]，同分排名数相同，但是下一个分数段继承上一个分数的人次数）
        """
        return self.target_class.rank_non_dumplicate

    @property
    def rank_dumplicate(self) -> list[tuple[int, Student]]:
        """
        学生分数排序，不去重

        也举个例子
        >>> target_class.rank_non_dumplicate
        [
            (1, Student(name="某个学生", score=114, ...)),
            (2, Student(name="某个学生", score=51,  ...)),
            (2, Student(name="某个学生", score=51,  ...)),
            (3, Student(name="某个学生", score=41,  ...)),
            (4, Student(name="某个学生", score=9,   ...)),
            (4, Student(name="某个学生", score=9,   ...)),
            (5, Student(name="某个学生", score=1,   ...))
        ]
        （即List[Tuple[排名数，学生对象]]，同分排名数相同，但是下一个分数段不会继承上一个分数的人次数）
        """
        return self.target_class.rank_dumplicate

    def start(self):
        "启动侦测器"
        self.on_active = True
        Thread(target=self.run, name="ClassStatusObserver", daemon=True).start()

    def stop(self):
        "停止侦测器"
        self.on_active = False
