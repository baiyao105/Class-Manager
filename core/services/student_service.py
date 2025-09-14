"""学生管理服务层

提供学生相关的业务逻辑操作
"""

from typing import List, Optional
from sqlmodel import Session
from ..models.student import Student
from ..repositories.student_repository import StudentRepository


class StudentService:
    """学生服务类"""
    
    def __init__(self, session: Session):
        self.session = session
        self.repository = StudentRepository(session)
    
    def create_student(self, name: str, student_number: str, class_id: int, 
                      email: Optional[str] = None) -> Student:
        """创建新学生"""
        student_data = {
            "name": name,
            "student_number": student_number,
            "class_id": class_id,
            "email": email
        }
        return self.repository.create(student_data)
    
    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """根据ID获取学生"""
        return self.repository.get_by_id(student_id)
    
    def get_students_by_class(self, class_id: int) -> List[Student]:
        """获取指定班级的所有学生"""
        return self.repository.get_by_class_id(class_id)
    
    def get_all_students(self) -> List[Student]:
        """获取所有学生"""
        return self.repository.get_all()
    
    def update_student(self, student_id: int, **kwargs) -> Optional[Student]:
        """更新学生信息"""
        return self.repository.update(student_id, kwargs)
    
    def delete_student(self, student_id: int) -> bool:
        """删除学生"""
        return self.repository.delete(student_id)
    
    def search_students(self, query: str) -> List[Student]:
        """搜索学生"""
        return self.repository.search_by_name_or_id(query)
    
    def get_student_stats(self) -> dict:
        """获取学生统计信息"""
        students = self.get_all_students()
        
        return {
            "total_students": len(students),
            "active_students": len([s for s in students if s.is_active]),
            "inactive_students": len([s for s in students if not s.is_active])
        }