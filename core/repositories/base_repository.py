import uuid
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from sqlmodel import Session, SQLModel, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(ABC, Generic[T]):
    """Repository基础接口

    提供通用的CRUD操作、事务支持、软删除功能
    所有具体Repository都应继承此类
    """

    def __init__(self, session: Session, model_class: type[T]):
        self.session = session
        self.model_class = model_class

    @abstractmethod
    def create(self, entity_data: dict[str, Any]) -> T:
        """创建实体

        Args:
            entity_data: 实体数据字典

        Returns:
            创建的实体对象
        """

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """根据ID获取实体

        Args:
            entity_id: 实体ID

        Returns:
            实体对象或None
        """

    @abstractmethod
    def update(self, entity_id: str, update_data: dict[str, Any]) -> Optional[T]:
        """更新实体

        Args:
            entity_id: 实体ID
            update_data: 更新数据字典

        Returns:
            更新后的实体对象或None
        """

    @abstractmethod
    def delete(self, entity_id: str, soft_delete: bool = True) -> bool:
        """删除实体

        Args:
            entity_id: 实体ID
            soft_delete: 是否软删除

        Returns:
            删除是否成功
        """

    def get_all(self, include_deleted: bool = False) -> list[T]:
        """获取所有实体

        Args:
            include_deleted: 是否包含已删除的实体

        Returns:
            实体列表
        """
        query = select(self.model_class)

        # 如果模型支持软删除且不包含已删除项
        if hasattr(self.model_class, "is_deleted") and not include_deleted:
            query = query.where(not self.model_class.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_by_field(self, field_name: str, field_value: Any, include_deleted: bool = False) -> list[T]:
        """根据字段值获取实体列表

        Args:
            field_name: 字段名
            field_value: 字段值
            include_deleted: 是否包含已删除的实体

        Returns:
            匹配的实体列表
        """
        if not hasattr(self.model_class, field_name):
            raise ValueError(f"模型 {self.model_class.__name__} 没有字段 {field_name}")

        field = getattr(self.model_class, field_name)
        query = select(self.model_class).where(field == field_value)

        # 软删除过滤
        if hasattr(self.model_class, "is_deleted") and not include_deleted:
            query = query.where(not self.model_class.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_paginated(self, page: int = 1, page_size: int = 20, include_deleted: bool = False) -> dict[str, Any]:
        """分页获取实体

        Args:
            page: 页码（从1开始）
            page_size: 每页大小
            include_deleted: 是否包含已删除的实体

        Returns:
            包含数据和分页信息的字典
        """
        offset = (page - 1) * page_size

        # 构建查询
        query = select(self.model_class)
        if hasattr(self.model_class, "is_deleted") and not include_deleted:
            query = query.where(not self.model_class.is_deleted)

        # 获取总数
        total_query = query
        total_count = len(self.session.exec(total_query).all())

        # 分页查询
        paginated_query = query.offset(offset).limit(page_size)
        items = self.session.exec(paginated_query).all()

        return {
            "items": items,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size,
        }

    def count(self, include_deleted: bool = False) -> int:
        """统计实体数量

        Args:
            include_deleted: 是否包含已删除的实体

        Returns:
            实体数量
        """
        query = select(self.model_class)
        if hasattr(self.model_class, "is_deleted") and not include_deleted:
            query = query.where(not self.model_class.is_deleted)

        result = self.session.exec(query)
        return len(result.all())

    def exists(self, entity_id: str) -> bool:
        """检查实体是否存在

        Args:
            entity_id: 实体ID

        Returns:
            是否存在
        """
        return self.get_by_id(entity_id) is not None

    def soft_delete(self, entity_id: str) -> bool:
        """软删除实体

        Args:
            entity_id: 实体ID

        Returns:
            删除是否成功
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            return False

        if hasattr(entity, "is_deleted"):
            entity.is_deleted = True
            if hasattr(entity, "deleted_at"):
                entity.deleted_at = datetime.utcnow()

            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)
            return True

        return False

    def hard_delete(self, entity_id: str) -> bool:
        """硬删除实体

        Args:
            entity_id: 实体ID

        Returns:
            删除是否成功
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            return False

        self.session.delete(entity)
        self.session.commit()
        return True

    def restore(self, entity_id: str) -> bool:
        """恢复软删除的实体

        Args:
            entity_id: 实体ID

        Returns:
            恢复是否成功
        """
        # 查询包含已删除的实体
        query = select(self.model_class)
        if hasattr(self.model_class, "id"):
            query = query.where(self.model_class.id == entity_id)

        result = self.session.exec(query)
        entity = result.first()

        if not entity or not hasattr(entity, "is_deleted"):
            return False

        entity.is_deleted = False
        if hasattr(entity, "deleted_at"):
            entity.deleted_at = None

        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return True

    @contextmanager
    def transaction(self):
        """事务上下文管理器

        使用方式:
            with repository.transaction():
                # 数据库操作
                pass
        """
        try:
            yield self.session
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise

    def batch_create(self, entities_data: list[dict[str, Any]]) -> list[T]:
        """批量创建实体

        Args:
            entities_data: 实体数据列表

        Returns:
            创建的实体列表
        """
        entities = []

        with self.transaction():
            for entity_data in entities_data:
                entity = self._create_entity(entity_data)
                entities.append(entity)
                self.session.add(entity)

        return entities

    def batch_update(self, updates: list[dict[str, Any]]) -> list[T]:
        """批量更新实体

        Args:
            updates: 更新数据列表，每个字典应包含'id'和更新字段

        Returns:
            更新后的实体列表
        """
        entities = []

        with self.transaction():
            for update_data in updates:
                entity_id = update_data.pop("id")
                entity = self.update(entity_id, update_data)
                if entity:
                    entities.append(entity)

        return entities

    def _create_entity(self, entity_data: dict[str, Any]) -> T:
        """创建实体对象的内部方法

        Args:
            entity_data: 实体数据

        Returns:
            实体对象
        """
        # 添加默认字段
        if "id" not in entity_data:
            entity_data["id"] = str(uuid.uuid4())

        if hasattr(self.model_class, "created_at") and "created_at" not in entity_data:
            entity_data["created_at"] = datetime.utcnow()

        if hasattr(self.model_class, "updated_at"):
            entity_data["updated_at"] = datetime.utcnow()

        if hasattr(self.model_class, "is_deleted") and "is_deleted" not in entity_data:
            entity_data["is_deleted"] = False

        return self.model_class(**entity_data)

    def _update_entity(self, entity: T, update_data: dict[str, Any]) -> T:
        """更新实体对象的内部方法

        Args:
            entity: 要更新的实体
            update_data: 更新数据

        Returns:
            更新后的实体
        """
        # 更新时间戳
        if hasattr(entity, "updated_at"):
            update_data["updated_at"] = datetime.utcnow()

        # 更新字段
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)

        return entity
