"""基础数据模型

定义所有数据模型的基类和通用字段
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """时间戳混入类"""

    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间", nullable=False)
    updated_at: Optional[datetime] = Field(default=None, description="更新时间", nullable=True)

    def update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.utcnow()


class UUIDMixin(SQLModel):
    """UUID混入类"""

    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), description="唯一标识符", unique=True, index=True)

    @field_validator("uuid")
    @classmethod
    def validate_uuid(cls, v):
        """验证UUID格式"""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("无效的UUID格式")


class SoftDeleteMixin(SQLModel):
    """软删除混入类"""

    is_deleted: bool = Field(default=False, description="是否已删除", nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, description="删除时间", nullable=True)

    def soft_delete(self):
        """软删除"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """恢复"""
        self.is_deleted = False
        self.deleted_at = None


class MasterDBModel(UUIDMixin, TimestampMixin, SQLModel):
    """总库模型基类 - 用于班级索引和统计缓存"""

    model_config = ConfigDict(from_attributes=True)


class SubDBModel(UUIDMixin, TimestampMixin, SoftDeleteMixin, SQLModel):
    """子库模型基类 - 用于班级业务数据"""

    model_config = ConfigDict(from_attributes=True)


class BaseModel(TimestampMixin, UUIDMixin, SoftDeleteMixin, SQLModel):
    """基础数据模型

    所有数据模型的基类, 包含：
    - 时间戳字段 (created_at, updated_at)
    - UUID字段 (uuid)
    - 软删除字段 (is_deleted, deleted_at)
    """

    class Config:
        # 允许从ORM对象创建
        from_attributes = True
        # 验证赋值
        validate_assignment = True
        # 使用枚举值
        use_enum_values = True
        # JSON编码器
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}

    def dict_without_relations(self, **kwargs):
        """获取不包含关系字段的字典"""
        exclude = kwargs.get("exclude", set())
        if isinstance(exclude, (list, tuple)):
            exclude = set(exclude)

        # 添加常见的关系字段到排除列表
        relation_fields = {"students", "classes", "achievements", "groups", "modifications"}
        exclude.update(relation_fields)

        kwargs["exclude"] = exclude
        return self.dict(**kwargs)

    def __repr__(self):
        """字符串表示"""
        class_name = self.__class__.__name__
        if hasattr(self, "name"):
            return f"{class_name}(name='{self.name}', uuid='{self.uuid}')"
        if hasattr(self, "id"):
            return f"{class_name}(id={self.id}, uuid='{self.uuid}')"
        return f"{class_name}(uuid='{self.uuid}')"


class ArchiveMixin(SQLModel):
    """归档混入类"""

    archive_uuid: Optional[str] = Field(default=None, description="归档UUID, 用于数据重置时的版本管理", nullable=True)

    def set_archive_uuid(self, archive_uuid: str):
        """设置归档UUID"""
        self.archive_uuid = archive_uuid


class OrderMixin(SQLModel):
    """排序混入类"""

    sort_order: int = Field(default=0, description="排序顺序", nullable=False)

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        """验证排序顺序"""
        if v < 0:
            raise ValueError("排序顺序不能为负数")
        return v
