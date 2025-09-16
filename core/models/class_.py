"""子库班级数据模型

定义子库班级相关的数据模型和业务逻辑
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import field_validator
from sqlmodel import Column, Field, Relationship, SQLModel, Text

from config.constants import ClassConstants

from .base import ArchiveMixin, OrderMixin, SubDBModel


class ClassType(str, Enum):
    """班级类型枚举"""

    REGULAR = ClassConstants.TYPE_REGULAR
    HONOR = ClassConstants.TYPE_HONOR
    SPECIAL = ClassConstants.TYPE_SPECIAL


class Classroom(SubDBModel, ArchiveMixin, OrderMixin, table=True):
    """子库班级表 - 存储班级业务数据

    核心字段：
    - 关联信息：总库班级索引UUID
    - 基本信息：班级名称、班主任、班级类型
    - 积分设置：基础积分、积分规则
    - 统计信息：学生数量、总分、平均分
    - 管理信息：创建时间、状态等
    """

    __tablename__ = "classrooms"

    # 主键
    id: Optional[int] = Field(default=None, primary_key=True)

    # 关联总库
    registry_uuid: UUID = Field(description="总库班级索引UUID")
    name: str = Field(description="班级名称", max_length=100, nullable=False, index=True)
    description: Optional[str] = Field(default=None, description="班级描述", max_length=500)

    # 班主任信息
    teacher_name: str = Field(description="班主任姓名", max_length=50, nullable=False)
    teacher_contact: Optional[str] = Field(default=None, description="班主任联系方式", max_length=100)

    # 班级类型和状态
    class_type: str = Field(max_length=50, description="班级类型")
    is_active: bool = Field(default=True, description="是否活跃")

    # 学期信息
    academic_year: str = Field(description="学年", max_length=20, default="2024-2025")
    semester: int = Field(description="学期(1或2)", default=1)

    # 班级设置
    max_students: int = Field(default=ClassConstants.MAX_CLASS_SIZE, description="最大学生数量")

    # 积分设置
    base_score: float = Field(default=100.0, description="基础积分")
    score_rules: Optional[str] = Field(default=None, sa_column=Column(Text), description="积分规则JSON")

    # 状态信息
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")

    # 关系字段
    students: list["Student"] = Relationship(
        back_populates="classroom", sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"}
    )
    groups: list["Group"] = Relationship(
        back_populates="classroom", sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"}
    )
    # attendance_infos: List["AttendanceInfo"] = Relationship(
    #     back_populates="class_",
    #     sa_relationship_kwargs={"lazy": "select"}
    # )

    # 验证器
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """验证班级名称"""
        if not v or not v.strip():
            raise ValueError("班级名称不能为空")
        if len(v.strip()) > 100:
            raise ValueError("班级名称长度不能超过100个字符")
        return v.strip()

    @field_validator("teacher_name")
    @classmethod
    def validate_teacher_name(cls, v):
        """验证班主任姓名"""
        if not v or not v.strip():
            raise ValueError("班主任姓名不能为空")
        if len(v.strip()) > 50:
            raise ValueError("班主任姓名长度不能超过50个字符")
        return v.strip()

    @field_validator("max_students")
    @classmethod
    def validate_max_students(cls, v):
        """验证最大学生数量"""
        if not (ClassConstants.MIN_CLASS_SIZE <= v <= ClassConstants.MAX_CLASS_SIZE):
            raise ValueError(f"班级最大人数必须在{ClassConstants.MIN_CLASS_SIZE}-{ClassConstants.MAX_CLASS_SIZE}范围内")
        return v

    @field_validator("semester")
    @classmethod
    def validate_semester(cls, v):
        """验证学期"""
        if v not in [1, 2]:
            raise ValueError("学期只能是1或2")
        return v

    # 统计属性
    @property
    def student_count(self) -> int:
        """学生总数"""
        if not self.students:
            return 0
        return len([s for s in self.students if not s.is_deleted])

    @property
    def active_student_count(self) -> int:
        """活跃学生数量"""
        if not self.students:
            return 0
        return len([s for s in self.students if s.is_active])

    @property
    def total_score(self) -> float:
        """班级总分"""
        if not self.students:
            return 0.0
        return sum(s.current_score for s in self.students if s.is_active)

    @property
    def average_score(self) -> float:
        """班级平均分"""
        active_count = self.active_student_count
        if active_count == 0:
            return 0.0
        return self.total_score / active_count

    @property
    def group_count(self) -> int:
        """小组数量"""
        if not self.groups:
            return 0
        return len([g for g in self.groups if not g.is_deleted])

    # 业务方法
    def add_student(self, student: "Student") -> bool:
        """添加学生到班级

        Args:
            student: 学生对象

        Returns:
            是否添加成功
        """
        if self.student_count >= self.max_students:
            return False

        # 检查学号是否重复
        if any(s.student_number == student.student_number for s in self.students if not s.is_deleted):
            return False

        student.class_id = self.id
        if not self.students:
            self.students = []
        self.students.append(student)
        self.update_timestamp()
        return True

    def remove_student(self, student_id: int) -> bool:
        """从班级移除学生

        Args:
            student_id: 学生ID

        Returns:
            是否移除成功
        """
        if not self.students:
            return False

        for student in self.students:
            if student.id == student_id:
                student.soft_delete()
                self.update_timestamp()
                return True
        return False

    def get_student_rankings(self, include_inactive: bool = False) -> list[dict[str, Any]]:
        """获取学生排名列表

        Args:
            include_inactive: 是否包含非活跃学生

        Returns:
            排名列表, 包含学生信息和排名
        """
        if not self.students:
            return []

        # 筛选学生
        students = self.students
        if not include_inactive:
            students = [s for s in students if s.is_active]
        else:
            students = [s for s in students if not s.is_deleted]

        # 按分数降序排序
        students.sort(key=lambda s: s.current_score, reverse=True)

        # 生成排名(处理并列情况)
        rankings = []
        current_rank = 1
        last_score = None

        for i, student in enumerate(students):
            if last_score is not None and student.current_score < last_score:
                current_rank = i + 1

            rankings.append(
                {
                    "rank": current_rank,
                    "student_id": student.id,
                    "student_name": student.name,
                    "student_number": student.student_number,
                    "score": student.current_score,
                    "is_active": student.is_active,
                }
            )

            last_score = student.current_score

        return rankings

    def get_top_students(self, limit: int = 10) -> list["Student"]:
        """获取成绩前N名的学生

        Args:
            limit: 返回学生数量限制

        Returns:
            成绩前N名的学生列表
        """
        if not self.students:
            return []

        active_students = [s for s in self.students if s.is_active]
        active_students.sort(key=lambda s: s.current_score, reverse=True)
        return active_students[:limit]

    def reset_all_scores(self, keep_achievements: bool = False) -> dict[str, Any]:
        """重置所有学生分数

        Args:
            keep_achievements: 是否保留成就

        Returns:
            重置操作的统计信息
        """
        if not self.students:
            return {"reset_count": 0, "total_students": 0}

        reset_count = 0
        snapshots = []

        for student in self.students:
            if student.is_active:
                snapshot = student.reset_scores(keep_achievements)
                snapshots.append({"student_id": student.id, "student_name": student.name, "snapshot": snapshot})
                reset_count += 1

        self.update_timestamp()

        return {
            "reset_count": reset_count,
            "total_students": self.active_student_count,
            "snapshots": snapshots,
            "reset_time": datetime.utcnow(),
        }

    def get_class_statistics(self) -> dict[str, Any]:
        """获取班级统计信息"""
        if not self.students:
            return {
                "student_count": 0,
                "active_student_count": 0,
                "total_score": 0.0,
                "average_score": 0.0,
                "highest_score": 0.0,
                "lowest_score": 0.0,
                "group_count": self.group_count,
            }

        active_students = [s for s in self.students if s.is_active]
        if not active_students:
            return {
                "student_count": self.student_count,
                "active_student_count": 0,
                "total_score": 0.0,
                "average_score": 0.0,
                "highest_score": 0.0,
                "lowest_score": 0.0,
                "group_count": self.group_count,
            }

        scores = [s.current_score for s in active_students]

        return {
            "student_count": self.student_count,
            "active_student_count": len(active_students),
            "total_score": sum(scores),
            "average_score": sum(scores) / len(scores),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "group_count": self.group_count,
        }

    @property
    def display_name(self) -> str:
        """显示名称"""
        return f"{self.name} ({self.academic_year}学年第{self.semester}学期)"


class Group(SubDBModel, ArchiveMixin, OrderMixin, table=True):
    """子库小组数据模型"""

    __tablename__ = "groups"

    # 主键
    id: Optional[int] = Field(default=None, primary_key=True)

    # 基本信息
    name: str = Field(description="小组名称", max_length=50, nullable=False)
    description: Optional[str] = Field(default=None, description="小组描述", max_length=200)

    # 班级关联
    classroom_id: int = Field(foreign_key="classrooms.id", description="所属班级ID")

    # 组长
    leader_id: Optional[int] = Field(default=None, foreign_key="students.id", description="组长ID")

    # 小组设置
    max_members: int = Field(default=8, description="最大成员数量")

    # 关系字段
    classroom: "Classroom" = Relationship(back_populates="groups", sa_relationship_kwargs={"lazy": "select"})
    leader: Optional["Student"] = Relationship(
        sa_relationship_kwargs={"lazy": "select", "foreign_keys": "[Group.leader_id]"}
    )
    members: list["Student"] = Relationship(
        back_populates="group", sa_relationship_kwargs={"lazy": "select", "foreign_keys": "[Student.group_id]"}
    )

    # 验证器
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """验证小组名称"""
        if not v or not v.strip():
            raise ValueError("小组名称不能为空")
        if len(v.strip()) > 50:
            raise ValueError("小组名称长度不能超过50个字符")
        return v.strip()

    @field_validator("max_members")
    @classmethod
    def validate_max_members(cls, v):
        """验证最大成员数量"""
        if not (1 <= v <= 20):
            raise ValueError("小组最大成员数量必须在1-20范围内")
        return v

    # 统计属性
    @property
    def member_count(self) -> int:
        """成员数量"""
        if not self.members:
            return 0
        return len([m for m in self.members if m.is_active])

    @property
    def total_score(self) -> float:
        """小组总分"""
        if not self.members:
            return 0.0
        return sum(m.current_score for m in self.members if m.is_active)

    @property
    def average_score(self) -> float:
        """小组平均分"""
        member_count = self.member_count
        if member_count == 0:
            return 0.0
        return self.total_score / member_count

    # 业务方法
    def add_member(self, student: "Student") -> bool:
        """添加成员"""
        if self.member_count >= self.max_members:
            return False

        student.group_id = self.id
        if not self.members:
            self.members = []
        self.members.append(student)
        self.update_timestamp()
        return True

    def remove_member(self, student_id: int) -> bool:
        """移除成员"""
        if not self.members:
            return False

        for member in self.members:
            if member.id == student_id:
                member.group_id = None
                # 如果移除的是组长, 清除组长设置
                if self.leader_id == student_id:
                    self.leader_id = None
                self.update_timestamp()
                return True
        return False

    def set_leader(self, student_id: int) -> bool:
        """设置组长"""
        # 检查学生是否在小组中
        if not any(m.id == student_id for m in self.members if m.is_active):
            return False

        self.leader_id = student_id
        self.update_timestamp()
        return True


# 数据传输对象
class ClassroomCreate(SQLModel):
    """创建子库班级的数据模型"""

    registry_uuid: UUID = Field(description="总库班级索引UUID")
    name: str = Field(description="班级名称", max_length=100)
    description: Optional[str] = Field(default=None, description="班级描述", max_length=500)
    teacher_name: str = Field(description="班主任姓名", max_length=50)
    teacher_contact: Optional[str] = Field(default=None, description="班主任联系方式", max_length=100)
    class_type: str = Field(max_length=50, description="班级类型")
    academic_year: str = Field(default="2024-2025", description="学年", max_length=20)
    semester: int = Field(default=1, description="学期")
    max_students: int = Field(default=ClassConstants.MAX_CLASS_SIZE, description="最大学生数量")
    base_score: float = Field(default=100.0, description="基础积分")
    score_rules: Optional[str] = Field(default=None, description="积分规则JSON")


class ClassroomUpdate(SQLModel):
    """更新子库班级的数据模型"""

    name: Optional[str] = Field(default=None, description="班级名称", max_length=100)
    description: Optional[str] = Field(default=None, description="班级描述", max_length=500)
    teacher_name: Optional[str] = Field(default=None, description="班主任姓名", max_length=50)
    teacher_contact: Optional[str] = Field(default=None, description="班主任联系方式", max_length=100)
    class_type: Optional[str] = Field(default=None, max_length=50, description="班级类型")
    is_active: Optional[bool] = Field(default=None, description="是否活跃")
    max_students: Optional[int] = Field(default=None, description="最大学生数量")
    base_score: Optional[float] = Field(default=None, description="基础积分")
    score_rules: Optional[str] = Field(default=None, description="积分规则JSON")


class ClassroomRead(SQLModel):
    """读取子库班级的数据模型"""

    id: int
    uuid: str
    registry_uuid: UUID
    name: str
    description: Optional[str]
    teacher_name: str
    teacher_contact: Optional[str]
    class_type: str
    is_active: bool
    academic_year: str
    semester: int
    max_students: int
    base_score: float
    score_rules: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class GroupCreate(SQLModel):
    """创建小组的数据模型"""

    name: str = Field(description="小组名称", max_length=50)
    description: Optional[str] = Field(default=None, description="小组描述", max_length=200)
    classroom_id: int = Field(description="所属班级ID")
    leader_id: Optional[int] = Field(default=None, description="组长ID")
    max_members: int = Field(default=8, description="最大成员数量")


class GroupUpdate(SQLModel):
    """更新小组的数据模型"""

    name: Optional[str] = Field(default=None, description="小组名称", max_length=50)
    description: Optional[str] = Field(default=None, description="小组描述", max_length=200)
    leader_id: Optional[int] = Field(default=None, description="组长ID")
    max_members: Optional[int] = Field(default=None, description="最大成员数量")


class GroupRead(SQLModel):
    """读取小组的数据模型"""

    id: int
    uuid: str
    name: str
    description: Optional[str]
    classroom_id: int
    leader_id: Optional[int]
    max_members: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
