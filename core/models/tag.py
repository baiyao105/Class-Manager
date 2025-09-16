"""子库标签数据模型"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import field_validator
from sqlmodel import Column, Field, Relationship, Text

from .base import SubDBModel

if TYPE_CHECKING:
    from .student import Student


class TagType(str, Enum):
    """标签类型枚举"""

    BEHAVIOR = "behavior"  # 行为标签
    ACADEMIC = "academic"  # 学术标签
    SKILL = "skill"  # 技能标签
    PERSONALITY = "personality"  # 性格标签
    CUSTOM = "custom"  # 自定义标签


class TagColor(str, Enum):
    """标签颜色枚举"""

    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    PINK = "pink"
    GRAY = "gray"


class Tag(SubDBModel, table=True):
    """标签模型 - 用于学生标签管理"""

    __tablename__ = "tags"

    # 主键
    id: Optional[int] = Field(default=None, primary_key=True)

    # 关联总库基本信息
    name: str = Field(max_length=50, description="标签名称")
    description: Optional[str] = Field(default=None, max_length=200, description="标签描述")

    # 标签属性
    tag_type: TagType = Field(description="标签类型")
    color: TagColor = Field(default=TagColor.BLUE, description="标签颜色")

    # 积分影响
    score_impact: float = Field(default=0.0, description="积分影响值")
    is_positive: bool = Field(default=True, description="是否为正面标签")

    # 使用统计
    usage_count: int = Field(default=0, description="使用次数")

    # 状态控制
    is_active: bool = Field(default=True, description="是否激活")
    is_system: bool = Field(default=False, description="是否为系统标签")

    # 排序权重
    sort_order: int = Field(default=0, description="排序权重")

    # 元数据
    metadata_json: Optional[str] = Field(default=None, sa_column=Column(Text), description="元数据JSON")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证标签名称"""
        if not v or not v.strip():
            raise ValueError("标签名称不能为空")
        if len(v.strip()) > 50:
            raise ValueError("标签名称不能超过50个字符")
        return v.strip()

    @field_validator("score_impact")
    @classmethod
    def validate_score_impact(cls, v: float) -> float:
        """验证积分影响值"""
        if v < -100 or v > 100:
            raise ValueError("积分影响值必须在-100到100之间")
        return v


class StudentTagLink(SubDBModel, table=True):
    """学生标签关联表 - 记录学生标签关系"""

    __tablename__ = "student_tag_links"

    # 主键
    id: Optional[int] = Field(default=None, primary_key=True)

    # 关联字段
    student_id: int = Field(foreign_key="students.id", description="学生ID")
    tag_id: int = Field(foreign_key="tags.id", description="标签ID")

    # 标签详情
    reason: Optional[str] = Field(default=None, max_length=200, description="添加原因")
    score_applied: float = Field(default=0.0, description="已应用的积分")

    # 时效性
    expires_at: Optional[datetime] = Field(default=None, description="过期时间")
    is_permanent: bool = Field(default=True, description="是否永久有效")

    # 操作记录
    added_by: Optional[str] = Field(default=None, max_length=50, description="添加人")

    # 关系
    student: "Student" = Relationship(back_populates="tag_links")
    tag: "Tag" = Relationship()

    class Config:
        # 复合唯一索引
        indexes = [
            ("student_id", "tag_id"),
        ]
