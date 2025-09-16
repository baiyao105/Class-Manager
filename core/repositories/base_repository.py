"""基础仓储类

提供通用的数据访问操作
"""

from typing import Any, Optional, TypeVar

from sqlmodel import Session, SQLModel, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository:
    """基础仓储类"""

    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model

    def create(self, data: dict[str, Any]) -> T:
        """创建新记录"""
        instance = self.model(**data)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def get_by_id(self, id: int) -> Optional[T]:
        """根据ID获取记录"""
        return self.session.get(self.model, id)

    def get_all(self) -> list[T]:
        """获取所有记录"""
        statement = select(self.model)
        return list(self.session.exec(statement).all())

    def update(self, id: int, data: dict[str, Any]) -> Optional[T]:
        """更新记录"""
        instance = self.get_by_id(id)
        if not instance:
            return None

        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def delete(self, id: int) -> bool:
        """删除记录"""
        instance = self.get_by_id(id)
        if not instance:
            return False

        self.session.delete(instance)
        self.session.commit()
        return True

    def count(self) -> int:
        """获取记录总数"""
        statement = select(self.model)
        return len(list(self.session.exec(statement).all()))
