"""班级管理服务层

提供班级相关的业务逻辑操作
"""

from typing import List, Optional
from sqlmodel import Session, select
from ..models.class_ import Class
from ..repositories.class_repository import ClassRepository


class ClassService:
    """班级服务类"""
    
    def __init__(self, session: Session):
        self.session = session
        self.repository = ClassRepository(session)
    
    def create_class(self, name: str, description: Optional[str] = None, teacher_name: Optional[str] = None) -> Class:
        """创建新班级"""
        class_data = {
            "name": name,
            "description": description or f"{name}班级",
            "teacher_name": teacher_name or "待分配"
        }
        return self.repository.create(class_data)
    
    def get_class_by_id(self, class_id: int) -> Optional[Class]:
        """根据ID获取班级"""
        return self.repository.get_by_id(class_id)
    
    def get_all_classes(self) -> List[Class]:
        """获取所有班级"""
        return self.repository.get_all()
    
    def update_class(self, class_id: int, **kwargs) -> Optional[Class]:
        """更新班级信息"""
        return self.repository.update(class_id, kwargs)
    
    def delete_class(self, class_id: int) -> bool:
        """删除班级"""
        return self.repository.delete(class_id)
    
    def get_class_stats(self) -> dict:
        """获取班级统计信息"""
        classes = self.get_all_classes()
        total_students = sum(len(cls.students) for cls in classes)
        
        return {
            "total_classes": len(classes),
            "total_students": total_students,
            "avg_students_per_class": total_students / len(classes) if classes else 0
        }