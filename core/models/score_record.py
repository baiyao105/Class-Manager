"""子库评分记录数据模型"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import field_validator
from sqlmodel import Column, Field, Relationship, Text

from .base import SubDBModel

if TYPE_CHECKING:
    from .score_template import ScoreTemplate
    from .student import Student


class RecordStatus(str, Enum):
    """记录状态枚举"""

    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已审核
    REJECTED = "rejected"  # 已拒绝
    CANCELLED = "cancelled"  # 已取消
    APPLIED = "applied"  # 已应用


class RecordSource(str, Enum):
    """记录来源枚举"""

    MANUAL = "manual"  # 手动录入
    SYSTEM = "system"  # 系统自动
    IMPORT = "import"  # 批量导入
    API = "api"  # API接口
    MOBILE = "mobile"  # 移动端


class ScoreRecord(SubDBModel, table=True):
    """子库评分记录表 - 记录所有评分操作"""

    __tablename__ = "score_records"

    # 主键
    id: Optional[int] = Field(default=None, primary_key=True)

    # 关联字段
    student_id: int = Field(foreign_key="students.id", description="学生ID")
    template_id: Optional[int] = Field(default=None, foreign_key="score_templates.id", description="评分模板ID")

    # 评分信息
    score_value: float = Field(description="分值")
    original_score: Optional[float] = Field(default=None, description="原始分值")
    final_score: float = Field(description="最终分值")

    # 记录详情
    title: str = Field(max_length=200, description="评分标题")
    description: Optional[str] = Field(default=None, max_length=1000, description="详细描述")
    reason: Optional[str] = Field(default=None, max_length=500, description="评分原因")

    # 分类信息
    category: str = Field(max_length=50, description="评分类别")
    subcategory: Optional[str] = Field(default=None, max_length=50, description="子类别")
    tags: Optional[str] = Field(default=None, max_length=200, description="标签列表")

    # 状态控制
    status: RecordStatus = Field(default=RecordStatus.PENDING, description="记录状态")
    source: RecordSource = Field(default=RecordSource.MANUAL, description="记录来源")

    # 时间信息
    occurred_at: datetime = Field(description="发生时间")
    recorded_at: datetime = Field(default_factory=datetime.now, description="记录时间")
    applied_at: Optional[datetime] = Field(default=None, description="应用时间")

    # 操作人员
    recorder: str = Field(max_length=50, description="记录人")
    approver: Optional[str] = Field(default=None, max_length=50, description="审核人")

    # 审核信息
    approval_note: Optional[str] = Field(default=None, max_length=500, description="审核备注")
    rejection_reason: Optional[str] = Field(default=None, max_length=500, description="拒绝原因")

    # 关联信息
    related_record_id: Optional[int] = Field(default=None, description="关联记录ID")
    batch_id: Optional[str] = Field(default=None, max_length=50, description="批次ID")

    # 扩展数据
    metadata_json: Optional[str] = Field(default=None, sa_column=Column(Text), description="元数据JSON")
    attachments: Optional[str] = Field(default=None, sa_column=Column(Text), description="附件信息JSON")

    # 统计字段
    view_count: int = Field(default=0, description="查看次数")

    # 关系
    student: "Student" = Relationship(back_populates="score_records")
    template: Optional["ScoreTemplate"] = Relationship(back_populates="score_records")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """验证评分标题"""
        if not v or not v.strip():
            raise ValueError("评分标题不能为空")
        if len(v.strip()) > 200:
            raise ValueError("评分标题不能超过200个字符")
        return v.strip()

    @field_validator("score_value", "final_score")
    @classmethod
    def validate_scores(cls, v: float) -> float:
        """验证分值"""
        if abs(v) > 10000:
            raise ValueError("分值不能超过±10000")
        return round(v, 2)

    @field_validator("occurred_at")
    @classmethod
    def validate_occurred_at(cls, v: datetime) -> datetime:
        """验证发生时间"""
        if v > datetime.now():
            raise ValueError("发生时间不能晚于当前时间")
        return v

    def can_be_modified(self) -> bool:
        """检查是否可以修改"""
        return self.status in [RecordStatus.PENDING, RecordStatus.REJECTED]

    def can_be_approved(self) -> bool:
        """检查是否可以审核"""
        return self.status == RecordStatus.PENDING

    def can_be_applied(self) -> bool:
        """检查是否可以应用"""
        return self.status == RecordStatus.APPROVED and self.applied_at is None

    def approve(self, approver: str, note: Optional[str] = None) -> None:
        """审核通过"""
        if not self.can_be_approved():
            raise ValueError("当前状态不允许审核")

        self.status = RecordStatus.APPROVED
        self.approver = approver
        self.approval_note = note
        self.updated_at = datetime.now()

    def reject(self, approver: str, reason: str) -> None:
        """审核拒绝"""
        if not self.can_be_approved():
            raise ValueError("当前状态不允许审核")

        self.status = RecordStatus.REJECTED
        self.approver = approver
        self.rejection_reason = reason
        self.updated_at = datetime.now()

    def apply_score(self) -> None:
        """应用分数"""
        if not self.can_be_applied():
            raise ValueError("当前状态不允许应用分数")

        self.status = RecordStatus.APPLIED
        self.applied_at = datetime.now()
        self.updated_at = datetime.now()

    class Config:
        # 索引配置
        indexes = [
            ("student_id", "occurred_at"),
            ("status", "created_at"),
            ("category", "occurred_at"),
            ("recorder", "created_at"),
            ("batch_id",),
        ]
