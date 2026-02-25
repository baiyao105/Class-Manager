from __future__ import annotations

import json
import time
import traceback
from typing import TYPE_CHECKING, Self, override
from uuid import UUID

from ...algorithm.types import update_object_mapping

from ...basetypes import Base
from ...consts import debug

from ..basetype import ClassDataType, ClassDataTypeUUID, DataProperty, StringObjectDataKind
from ..classdataloader import ClassDataLoader
from .scoremodtemplate import ScoreModificationTemplate

if TYPE_CHECKING:
    from .student import Student


class ScoreModification(ClassDataType):
    "分数修改记录。"

    chunk_type_name: str = "ScoreModification"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    @classmethod
    def new_dummy(cls) -> Self:
        "返回一个空的分数加减操作"
        from .student import Student

        return cls(ScoreModificationTemplate.new_dummy(), Student.new_dummy())

    def __init__(
        self,
        template: ScoreModificationTemplate,
        target: Student,
        title: str | None = None,
        desc: str | None = None,
        mod: float | None = None,
        execute_time: str | None = None,
        create_time: str | None = None,
        executed: bool = False,
    ):
        """
        分数加减操作的构造函数。

        :param template: 模板
        :param target: 目标学生
        :param title: 标题
        :param desc: 描述
        :param mod: 修改分数
        :param execute_time: 执行时间
        :param create_time: 创建时间
        :param executed: 是否已执行
        """
        super().__init__()
        if create_time is None:
            create_time = Base.gettime()
        self.temp = template

        if title == self.temp.title or title is None:
            self.title = self.temp.title
        else:
            self.title = title

        if desc == self.temp.desc or desc is None:
            self.desc = self.temp.desc
        else:
            self.desc = desc

        if mod == self.temp.mod or mod is None:
            self.mod = self.temp.mod
        else:
            self.mod = mod
        self.target = target
        self._execute_time = execute_time
        self.create_time = create_time
        self._executed = executed
        self.archive_uuid = ClassDataLoader.get_archive_uuid()
        self.execute_time_key = 0

    @DataProperty
    def executed(self):
        "是否已执行"
        return self._executed

    @executed.setter
    def executed(self, value: bool):
        self._executed = value

    @DataProperty
    def execute_time(self):
        "执行时间"
        return self._execute_time

    @execute_time.setter
    def execute_time(self, value: str | None):
        self._execute_time = value

    def __repr__(self):
        return (
            f"ScoreModification(template={self.temp!r}, "
            f"target={self.target!r}, title={self.title!r}, "
            f"desc={self.desc!r}, mod={self.mod!r}, "
            f"execute_time={self.execute_time!r}, create_time={self.create_time!r}, "
            f"executed={self.executed!r})"
        )

    def execute(self) -> bool:
        "执行当前的操作"
        if self.executed:
            Base.log(
                "W",
                "执行已经完成，无需再次执行，如需重新执行请创建新的ScoreModification对象",
                "ScoreModification.execute",
            )
            return False

        try:
            self.execute_time = Base.gettime()
            self.execute_time_key = int(time.time() * 1000)
            if self.target.highest_score < self.target.score + self.mod:
                self.target.highest_score = self.target.score + self.mod
                self.target.highest_score_cause_time = self.execute_time_key

            if self.target.lowest_score > self.target.score + self.mod:
                self.target.lowest_score = self.target.score + self.mod
                self.target.lowest_score_cause_time = self.execute_time_key

            self.target.score += self.mod
            self.executed = True
            self.target.history[self.execute_time_key] = self
            return True

        except (
            KeyError,
            MemoryError,
            TypeError,
            ValueError,
            OverflowError,
            ZeroDivisionError,
        ) as exception:
            if debug:
                raise ClassDataLoader.OperationalError("执行加减分操作时发生错误") from exception
            Base.log(
                "E",
                "执行时出现错误：\n\t\t" + ("\t" * 2).join(str(traceback.format_exc()).splitlines(True)).strip(),
                "ScoreModification.execute",
            )
            return False

    def retract(self) -> tuple[bool, str]:
        """撤销执行的操作

        :return: 是否执行成功（bool: 结果, str: 成功/失败原因）
        """
        if self not in self.target.history.values():
            Base.log("W", "当前操作未执行，无法撤回", "ScoreModification.retract")
            return False, "并不在本周历史中"
        if self.executed:
            try:
                if self.mod < 0:
                    findscore = 0.0
                    lowestscore = 0.0
                    lowesttimekey = 0
                    # 重新计算最高分和最低分
                    for i in self.target.history:
                        tmp = self.target.history[i]

                        if tmp.execute_time_key != self.execute_time_key and tmp.executed:  # 排除自身
                            findscore += tmp.mod

                        if lowestscore > findscore and tmp.execute_time_key != self.execute_time_key:
                            lowesttimekey = tmp.execute_time_key
                            lowestscore = findscore

                    if self.execute_time_key == lowesttimekey:
                        lowestscore = 0

                    if self.target.lowest_score_cause_time != lowesttimekey:
                        self.target.lowest_score_cause_time = lowesttimekey

                    if self.target.lowest_score != lowestscore:
                        self.target.lowest_score = lowestscore

                else:
                    findscore = 0.0
                    highestscore = 0.0
                    highesttimekey = 0
                    for i in self.target.history:
                        tmp = self.target.history[i]
                        if tmp.execute_time_key != self.execute_time_key and tmp.executed:
                            findscore += tmp.mod

                        if highestscore < findscore and tmp.execute_time_key != self.execute_time_key:
                            highesttimekey = tmp.execute_time_key
                            highestscore = findscore
                    if self.execute_time_key == highesttimekey:
                        highestscore = 0
                    if self.target.highest_score_cause_time != highesttimekey:
                        self.target.highest_score_cause_time = highesttimekey

                    if self.target.highest_score != highestscore:
                        self.target.highest_score = highestscore

                self.target.score -= self.mod
                self.executed = False
                self.execute_time = None
                del self
                return True, "操作成功完成"
            except (
                KeyError,
                MemoryError,
                TypeError,
                AttributeError,
                ValueError,
                OverflowError,
                ZeroDivisionError
            ):
                if debug:
                    raise
                Base.log(
                    "E",
                    "执行时出现错误：\n\t\t" + ("\t" * 2).join(str(traceback.format_exc()).splitlines(True)).strip(),
                    "ScoreModification.retract",
                )
                return False, "执行时出现不可预测的错误"
        else:
            Base.log("W", "操作并未执行，无需撤回", "ScoreModification.retract")
            return False, "操作并未执行, 无需撤回"

    @staticmethod
    def load_template(template_uuid: str) -> ScoreModificationTemplate:
        "从UUID字符串加载分数修改模板。"
        from .scoremodtemplate import ScoreModificationTemplate
        template = ClassDataLoader.LoadUUID(
            ClassDataTypeUUID(ScoreModificationTemplate, UUID(template_uuid)), ScoreModificationTemplate
        )
        assert template is not None, f"目标模板{template_uuid}加载失败"
        return template
    
    @staticmethod
    def load_target(target_uuid: str) -> Student:
        "从UUID字符串加载分数修改记录的目标学生。"
        from .student import Student
        target = ClassDataLoader.LoadUUID(
            ClassDataTypeUUID(Student, UUID(target_uuid)), Student
        )
        assert target is not None, f"目标学生{target_uuid}加载失败"
        return target

    def to_string(self) -> StringObjectDataKind[Self]:
        "将分数修改记录对象转为字符串。"
        return StringObjectDataKind(json.dumps(
            {
                "type": self.chunk_type_name,
                "template": str(self.temp.uuid),
                "target": str(self.target.uuid),
                "title": self.title,
                "mod": self.mod,
                "desc": self.desc,
                "executed": self.executed,
                "create_time": self.create_time,
                "execute_time": self.execute_time,
                "execute_time_key": self.execute_time_key,
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        ))

    @classmethod
    def from_string(cls, string: str) -> Self:
        "将字符串转换为分数修改对象。"

        d = json.loads(string)
        if d["type"] != cls.chunk_type_name:
            raise ValueError(f"类型不匹配：{d['type']} != {cls.chunk_type_name}")
        obj = cls(
            template=cls.load_template(d["template"]),
            target=cls.load_target(d["target"]),
            title=d["title"],
            mod=d["mod"],
            execute_time=d["execute_time"],
            create_time=d["create_time"],
            executed=d["executed"],
            desc=d["desc"],
        )
        obj.uuid = d["uuid"]
        obj.archive_uuid = d["archive_uuid"]
        obj.execute_time_key = d["execute_time_key"]
        return obj

    def inst_from_string(self, string: str):
        "将字符串加载与本身。"
        obj = self.from_string(string)
        update_object_mapping(self, obj.__dict__)
        return self

    @override
    def to_pydantic(self):
        """
        转换为Pydantic模型。

        :return: Pydantic模型实例
        """
        from ..dataloaders.pydantic_loader.models.score_modification import ScoreModificationModel
        return ScoreModificationModel.from_class_data(self)

