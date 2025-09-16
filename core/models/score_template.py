"""子库评分模板数据模型"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import field_validator
from sqlmodel import Column, Field, Relationship, Text

from .base import SubDBModel

if TYPE_CHECKING:
    from .score_record import ScoreRecord


class ScoreCategory(str, Enum):
    """评分类别枚举"""

    BEHAVIOR = "behavior"  # 行为表现
    ACADEMIC = "academic"  # 学术成绩
    PARTICIPATION = "participation"  # 参与度
    HOMEWORK = "homework"  # 作业完成
    ATTENDANCE = "attendance"  # 出勤情况
    DISCIPLINE = "discipline"  # 纪律表现
    TEAMWORK = "teamwork"  # 团队合作
    LEADERSHIP = "leadership"  # 领导能力
    CREATIVITY = "creativity"  # 创新能力
    CUSTOM = "custom"  # 自定义


class ScoreType(str, Enum):
    """评分类型枚举"""

    POSITIVE = "positive"  # 加分
    NEGATIVE = "negative"  # 扣分
    NEUTRAL = "neutral"  # 中性记录


class ScoreTemplate(SubDBModel, table=True):
    """子库评分模板表 - 定义评分规则和模板"""

    __tablename__ = "score_templates"

    # 主键
    id: Optional[int] = Field(default=None, primary_key=True)

    # 基本信息
    name: str = Field(max_length=100, description="模板名称")
    description: Optional[str] = Field(default=None, max_length=500, description="模板描述")

    # 评分属性
    category: ScoreCategory = Field(description="评分类别")
    score_type: ScoreType = Field(description="评分类型")

    # 分值设置
    default_score: float = Field(description="默认分值")
    min_score: Optional[float] = Field(default=None, description="最小分值")
    max_score: Optional[float] = Field(default=None, description="最大分值")

    # 权重和倍数
    weight: float = Field(default=1.0, description="权重系数")
    multiplier: float = Field(default=1.0, description="倍数系数")

    # 使用限制
    daily_limit: Optional[int] = Field(default=None, description="每日使用限制")
    weekly_limit: Optional[int] = Field(default=None, description="每周使用限制")
    monthly_limit: Optional[int] = Field(default=None, description="每月使用限制")

    # 适用范围
    applicable_grades: Optional[str] = Field(default=None, max_length=100, description="适用年级")
    applicable_subjects: Optional[str] = Field(default=None, max_length=200, description="适用科目")

    # 状态控制
    is_active: bool = Field(default=True, description="是否激活")
    is_system: bool = Field(default=False, description="是否为系统模板")
    requires_approval: bool = Field(default=False, description="是否需要审批")

    # 时效性
    valid_from: Optional[datetime] = Field(default=None, description="生效开始时间")
    valid_until: Optional[datetime] = Field(default=None, description="生效结束时间")

    # 使用统计
    usage_count: int = Field(default=0, description="使用次数")
    last_used_at: Optional[datetime] = Field(default=None, description="最后使用时间")

    # 排序和分组
    sort_order: int = Field(default=0, description="排序权重")
    group_name: Optional[str] = Field(default=None, max_length=50, description="分组名称")

    # 扩展配置
    config_json: Optional[str] = Field(default=None, sa_column=Column(Text), description="配置JSON")

    # 关系
    score_records: list["ScoreRecord"] = Relationship(back_populates="template")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证模板名称"""
        if not v or not v.strip():
            raise ValueError("模板名称不能为空")
        if len(v.strip()) > 100:
            raise ValueError("模板名称不能超过100个字符")
        return v.strip()

    @field_validator("default_score")
    @classmethod
    def validate_default_score(cls, v: float) -> float:
        """验证默认分值"""
        if abs(v) > 1000:
            raise ValueError("默认分值不能超过±1000")
        return v

    @field_validator("weight", "multiplier")
    @classmethod
    def validate_coefficients(cls, v: float) -> float:
        """验证系数"""
        if v <= 0:
            raise ValueError("权重和倍数必须大于0")
        if v > 10:
            raise ValueError("权重和倍数不能超过10")
        return v

    def calculate_final_score(self, base_score: Optional[float] = None) -> float:
        """计算最终分值"""
        score = base_score if base_score is not None else self.default_score
        final_score = score * self.weight * self.multiplier

        # 应用最值限制
        if self.min_score is not None:
            final_score = max(final_score, self.min_score)
        if self.max_score is not None:
            final_score = min(final_score, self.max_score)

        return round(final_score, 2)

    def is_valid_at(self, check_time: Optional[datetime] = None) -> bool:
        """检查在指定时间是否有效"""
        if check_time is None:
            check_time = datetime.now()

        if self.valid_from and check_time < self.valid_from:
            return False
        if self.valid_until and check_time > self.valid_until:
            return False

        return self.is_active and not self.is_deleted
