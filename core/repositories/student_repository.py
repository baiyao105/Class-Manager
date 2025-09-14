"""学生仓储类

提供学生数据访问操作
"""

from typing import List, Optional
from sqlmodel import Session, select, or_
from .base_repository import BaseRepository
from ..models.student import Student


class StudentRepository(BaseRepository):
    """学生仓储类"""
    
    def __init__(self, session: Session):
        super().__init__(session, Student)
    
    def get_by_student_id(self, student_id: str) -> Optional[Student]:
        """根据学号获取学生"""
        statement = select(Student).where(Student.student_id == student_id)
        return self.session.exec(statement).first()
    
    def get_by_class_id(self, class_id: int) -> List[Student]:
        """根据班级ID获取学生列表"""
        statement = select(Student).where(Student.class_id == class_id)
        return list(self.session.exec(statement).all())
    
    def search_by_name_or_id(self, query: str) -> List[Student]:
        """根据姓名或学号搜索学生"""
        statement = select(Student).where(
            or_(
                Student.name.contains(query),
                Student.student_id.contains(query)
            )
        )
        return list(self.session.exec(statement).all())
    
    def get_active_students(self) -> List[Student]:
        """获取活跃学生"""
        statement = select(Student).where(Student.is_active == True)
        return list(self.session.exec(statement).all())
    
    def get_students_by_email_domain(self, domain: str) -> List[Student]:
        """根据邮箱域名获取学生"""
        statement = select(Student).where(Student.email.contains(f"@{domain}"))
        return list(self.session.exec(statement).all())