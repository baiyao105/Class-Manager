"""总库数据模型 - 用于班级索引和统计缓存"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Column, Field, Text

from .base import MasterDBModel


class DataRegistry(MasterDBModel, table=True):
    """班级数据索引表 - 总库核心表"""

    __tablename__ = "data_registry"

    # 主键
    id: Optional[int] = Field(default=None, primary_key=True)

    # 班级基本信息
    class_name: str = Field(max_length=100, description="班级名称")
    class_type: str = Field(max_length=50, description="班级类型")
    grade: Optional[str] = Field(default=None, max_length=20, description="年级")
    school_year: Optional[str] = Field(default=None, max_length=20, description="学年")

    # 数据库连接信息
    db_path: str = Field(description="子库数据库路径")
    db_name: Optional[str] = Field(default=None, max_length=100, description="数据库名称")

    # 状态信息
    is_active: bool = Field(default=True, description="是否激活")
    last_sync_at: Optional[datetime] = Field(default=None, description="最后同步时间")

    # 统计信息缓存
    student_count: int = Field(default=0, description="学生总数")
    active_student_count: int = Field(default=0, description="活跃学生数")
    total_score: float = Field(default=0.0, description="总积分")
    avg_score: float = Field(default=0.0, description="平均积分")

    # 元数据
    description: Optional[str] = Field(default=None, max_length=500, description="班级描述")
    config_json: Optional[str] = Field(default=None, sa_column=Column(Text), description="配置JSON")


class DataStatistics(MasterDBModel, table=True):
    """统计数据缓存表 - 用于跨班级统计分析"""

    __tablename__ = "data_statistics"

    # 主键
    id: Optional[int] = Field(default=None, primary_key=True)

    # 关联信息
    class_uuid: UUID = Field(foreign_key="data_registry.uuid", description="班级UUID")
    stat_type: str = Field(max_length=50, description="统计类型")
    stat_key: str = Field(max_length=100, description="统计键")

    # 统计数据
    stat_value: float = Field(description="统计值")
    stat_count: int = Field(default=0, description="统计计数")

    # 时间维度
    stat_date: datetime = Field(description="统计日期")
    period_type: str = Field(max_length=20, description="周期类型(daily/weekly/monthly)")

    # 元数据
    metadata_json: Optional[str] = Field(default=None, sa_column=Column(Text), description="元数据JSON")

    class Config:
        # 复合索引
        indexes = [
            ("class_uuid", "stat_type", "stat_date"),
            ("stat_type", "period_type", "stat_date"),
        ]
