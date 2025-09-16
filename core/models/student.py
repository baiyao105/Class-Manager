"""学生数据模型

定义学生相关的数据模型和业务逻辑
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import field_validator, model_validator
from sqlmodel import Field, Relationship, SQLModel

from config.constants import StudentConstants

from .base import ArchiveMixin, BaseModel, OrderMixin


class StudentStatus(str, Enum):
    """学生状态枚举"""

    ACTIVE = StudentConstants.STATUS_ACTIVE
    INACTIVE = StudentConstants.STATUS_INACTIVE
    GRADUATED = StudentConstants.STATUS_GRADUATED


class Student(BaseModel, ArchiveMixin, OrderMixin, table=True):
    """学生数据模型

    核心字段：
    - 基本信息：姓名、学号、所属班级
    - 分数信息：当前分数、历史最高/最低分
    - 状态信息：学生状态、所属小组
    - 统计信息：总分、排名相关
    """

    __tablename__ = "cm_students"

    # 基本信息
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="学生姓名", max_length=50, nullable=False)
    student_number: int = Field(description="学号", nullable=False, index=True)

    # 班级关联
    class_id: Optional[int] = Field(default=None, foreign_key="cm_classes.id", description="所属班级ID")

    # 小组关联
    group_id: Optional[int] = Field(default=None, foreign_key="cm_groups.id", description="所属小组ID")

    # 分数信息
    current_score: float = Field(default=StudentConstants.DEFAULT_SCORE, description="当前分数")
    total_score: float = Field(default=StudentConstants.DEFAULT_SCORE, description="总分(包含历史分数)")
    highest_score: float = Field(default=StudentConstants.DEFAULT_SCORE, description="历史最高分")
    lowest_score: float = Field(default=StudentConstants.DEFAULT_SCORE, description="历史最低分")

    # 分数变化时间记录
    highest_score_time: Optional[datetime] = Field(default=None, description="最高分达成时间")
    lowest_score_time: Optional[datetime] = Field(default=None, description="最低分产生时间")

    # 重置相关
    last_reset_time: Optional[datetime] = Field(default=None, description="上次重置时间")

    # 状态信息
    status: StudentStatus = Field(default=StudentStatus.ACTIVE, description="学生状态")

    # 关系字段
    class_: Optional["Class"] = Relationship(back_populates="students", sa_relationship_kwargs={"lazy": "select"})
    group: Optional["Group"] = Relationship(
        back_populates="members", sa_relationship_kwargs={"lazy": "select", "foreign_keys": "[Student.group_id]"}
    )
    # score_modifications: List["ScoreModification"] = Relationship(
    #     back_populates="student",
    #     sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"}
    # )
    achievements: list["Achievement"] = Relationship(
        back_populates="student", sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"}
    )
    # attendance_records: List["AttendanceRecord"] = Relationship(
    #     back_populates="student",
    #     sa_relationship_kwargs={"lazy": "select"}
    # )

    # 验证器
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """验证姓名"""
        if not v or not v.strip():
            raise ValueError("学生姓名不能为空")
        if len(v.strip()) > 50:
            raise ValueError("学生姓名长度不能超过50个字符")
        return v.strip()

    @field_validator("student_number")
    @classmethod
    def validate_student_number(cls, v):
        """验证学号"""
        if not (StudentConstants.MIN_STUDENT_NUMBER <= v <= StudentConstants.MAX_STUDENT_NUMBER):
            raise ValueError(
                f"学号必须在{StudentConstants.MIN_STUDENT_NUMBER}-{StudentConstants.MAX_STUDENT_NUMBER}范围内"
            )
        return v

    @field_validator("current_score", "total_score", "highest_score", "lowest_score")
    @classmethod
    def validate_scores(cls, v):
        """验证分数范围"""
        if not (StudentConstants.MIN_SCORE <= v <= StudentConstants.MAX_SCORE):
            raise ValueError(f"分数必须在{StudentConstants.MIN_SCORE}-{StudentConstants.MAX_SCORE}范围内")
        return v

    @model_validator(mode="before")
    @classmethod
    def validate_score_consistency(cls, values):
        """验证分数一致性"""
        if isinstance(values, dict):
            current = values.get("current_score", 0)
            highest = values.get("highest_score", 0)
            lowest = values.get("lowest_score", 0)

            # 确保最高分不小于当前分数
            if highest < current:
                values["highest_score"] = current
                values["highest_score_time"] = datetime.utcnow()

            # 确保最低分不大于当前分数
            if lowest > current:
                values["lowest_score"] = current
                values["lowest_score_time"] = datetime.utcnow()

        return values

    # 业务方法
    def add_score(self, score_change: float, reason: str = "") -> float:
        """增加分数

        Args:
            score_change: 分数变化量
            reason: 变化原因

        Returns:
            新的当前分数
        """
        old_score = self.current_score
        new_score = old_score + score_change

        # 限制分数范围
        new_score = max(StudentConstants.MIN_SCORE, min(StudentConstants.MAX_SCORE, new_score))

        self.current_score = new_score
        self.total_score += score_change

        # 更新最高分记录
        if new_score > self.highest_score:
            self.highest_score = new_score
            self.highest_score_time = datetime.utcnow()

        # 更新最低分记录
        if new_score < self.lowest_score:
            self.lowest_score = new_score
            self.lowest_score_time = datetime.utcnow()

        self.update_timestamp()
        return new_score

    def reset_scores(self, keep_achievements: bool = False) -> dict[str, Any]:
        """重置分数

        Args:
            keep_achievements: 是否保留成就

        Returns:
            重置前的数据快照
        """
        snapshot = {
            "current_score": self.current_score,
            "total_score": self.total_score,
            "highest_score": self.highest_score,
            "lowest_score": self.lowest_score,
            "reset_time": datetime.utcnow(),
        }

        # 重置分数
        self.current_score = StudentConstants.DEFAULT_SCORE
        self.total_score = StudentConstants.DEFAULT_SCORE
        self.highest_score = StudentConstants.DEFAULT_SCORE
        self.lowest_score = StudentConstants.DEFAULT_SCORE
        self.last_reset_time = datetime.utcnow()

        # 清除时间记录
        self.highest_score_time = None
        self.lowest_score_time = None

        self.update_timestamp()
        return snapshot

    def get_rank_in_class(self) -> Optional[int]:
        """获取在班级中的排名

        Returns:
            排名(1开始), 如果没有班级则返回None
        """
        if not self.class_:
            return None

        # 获取班级中所有活跃学生, 按分数降序排列
        active_students = [s for s in self.class_.students if s.status == StudentStatus.ACTIVE and not s.is_deleted]
        active_students.sort(key=lambda s: s.current_score, reverse=True)

        try:
            return active_students.index(self) + 1
        except ValueError:
            return None

    def get_score_history_summary(self) -> dict[str, Any]:
        """获取分数历史摘要"""
        return {
            "current_score": self.current_score,
            "total_score": self.total_score,
            "highest_score": self.highest_score,
            "lowest_score": self.lowest_score,
            "highest_score_time": self.highest_score_time,
            "lowest_score_time": self.lowest_score_time,
            "last_reset_time": self.last_reset_time,
            "modification_count": len(self.score_modifications) if self.score_modifications else 0,
            "achievement_count": len(self.achievements) if self.achievements else 0,
        }

    @property
    def display_name(self) -> str:
        """显示名称(包含学号)"""
        return f"{self.name}({self.student_number})"

    @property
    def is_active(self) -> bool:
        """是否为活跃学生"""
        return self.status == StudentStatus.ACTIVE and not self.is_deleted


class StudentCreate(SQLModel):
    """创建学生的数据模型"""

    name: str = Field(description="学生姓名", max_length=50)
    student_number: int = Field(description="学号")
    class_id: Optional[int] = Field(default=None, description="所属班级ID")
    group_id: Optional[int] = Field(default=None, description="所属小组ID")
    current_score: float = Field(default=StudentConstants.DEFAULT_SCORE, description="初始分数")


class StudentUpdate(SQLModel):
    """更新学生的数据模型"""

    name: Optional[str] = Field(default=None, description="学生姓名", max_length=50)
    student_number: Optional[int] = Field(default=None, description="学号")
    class_id: Optional[int] = Field(default=None, description="所属班级ID")
    group_id: Optional[int] = Field(default=None, description="所属小组ID")
    status: Optional[StudentStatus] = Field(default=None, description="学生状态")


class StudentRead(SQLModel):
    """读取学生的数据模型"""

    id: int
    uuid: str
    name: str
    student_number: int
    current_score: float
    total_score: float
    highest_score: float
    lowest_score: float
    status: StudentStatus
    class_id: Optional[int]
    group_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
