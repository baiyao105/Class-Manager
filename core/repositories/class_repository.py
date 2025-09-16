"""班级仓储类

提供班级数据访问操作
"""

from typing import Optional

from sqlmodel import Session, select

from ..models.class_ import Class
from .base_repository import BaseRepository


class ClassRepository(BaseRepository):
    """班级仓储类"""

    def __init__(self, session: Session):
        super().__init__(session, Class)

    def get_by_name(self, name: str) -> Optional[Class]:
        """根据班级名称获取班级"""
        statement = select(Class).where(Class.name == name)
        return self.session.exec(statement).first()

    def search_by_name(self, query: str) -> list[Class]:
        """根据名称搜索班级"""
        statement = select(Class).where(Class.name.contains(query))
        return list(self.session.exec(statement).all())

    def get_classes_with_students(self) -> list[Class]:
        """获取包含学生信息的班级列表"""
        # 这里可以添加预加载学生信息的逻辑
        return self.get_all()

    def get_active_classes(self) -> list[Class]:
        """获取活跃的班级"""
        statement = select(Class).where(Class.is_active)
        return list(self.session.exec(statement).all())
