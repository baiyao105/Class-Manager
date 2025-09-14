"""成就仓储类

提供成就数据访问操作
"""

from typing import List, Optional
from sqlmodel import Session, select, func
from .base_repository import BaseRepository
from ..models.achievement import Achievement


class AchievementRepository(BaseRepository):
    """成就仓储类"""
    
    def __init__(self, session: Session):
        super().__init__(session, Achievement)
    
    def get_by_student_id(self, student_id: int) -> List[Achievement]:
        """根据学生ID获取成就列表"""
        statement = select(Achievement).where(Achievement.student_id == student_id)
        return list(self.session.exec(statement).all())
    
    def get_by_title(self, title: str) -> List[Achievement]:
        """根据成就标题搜索"""
        statement = select(Achievement).where(Achievement.title.contains(title))
        return list(self.session.exec(statement).all())
    
    def get_high_value_achievements(self, min_points: int = 50) -> List[Achievement]:
        """获取高价值成就"""
        statement = select(Achievement).where(Achievement.points >= min_points)
        return list(self.session.exec(statement).all())
    
    def get_recent_achievements(self, limit: int = 10) -> List[Achievement]:
        """获取最近的成就"""
        statement = select(Achievement).order_by(Achievement.created_at.desc()).limit(limit)
        return list(self.session.exec(statement).all())
    
    def get_student_points_total(self, student_id: int) -> int:
        """获取学生总积分"""
        statement = select(func.sum(Achievement.points)).where(Achievement.student_id == student_id)
        result = self.session.exec(statement).first()
        return result or 0
    
    def get_top_students_by_points(self, limit: int = 10) -> List[dict]:
        """获取积分排行榜"""
        statement = select(
            Achievement.student_id,
            func.sum(Achievement.points).label('total_points')
        ).group_by(Achievement.student_id).order_by(
            func.sum(Achievement.points).desc()
        ).limit(limit)
        
        results = self.session.exec(statement).all()
        return [{'student_id': r[0], 'total_points': r[1]} for r in results]