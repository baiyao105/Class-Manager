"""成就管理服务层

提供成就系统相关的业务逻辑操作
"""

from typing import Optional

from sqlmodel import Session

from ..models.achievement import Achievement
from ..repositories.achievement_repository import AchievementRepository


class AchievementService:
    """成就服务类"""

    def __init__(self, session: Session):
        self.session = session
        self.repository = AchievementRepository(session)

    def create_achievement(self, student_id: int, title: str, description: str, points: int = 10) -> Achievement:
        """创建新成就"""
        achievement_data = {"student_id": student_id, "title": title, "description": description, "points": points}
        return self.repository.create(achievement_data)

    def get_achievement_by_id(self, achievement_id: int) -> Optional[Achievement]:
        """根据ID获取成就"""
        return self.repository.get_by_id(achievement_id)

    def get_achievements_by_student(self, student_id: int) -> list[Achievement]:
        """获取学生的所有成就"""
        return self.repository.get_by_student_id(student_id)

    def get_all_achievements(self) -> list[Achievement]:
        """获取所有成就"""
        return self.repository.get_all()

    def update_achievement(self, achievement_id: int, **kwargs) -> Optional[Achievement]:
        """更新成就信息"""
        return self.repository.update(achievement_id, kwargs)

    def delete_achievement(self, achievement_id: int) -> bool:
        """删除成就"""
        return self.repository.delete(achievement_id)

    def get_student_total_points(self, student_id: int) -> int:
        """获取学生总积分"""
        achievements = self.get_achievements_by_student(student_id)
        return sum(achievement.points for achievement in achievements)

    def get_achievement_stats(self) -> dict:
        """获取成就统计信息"""
        achievements = self.get_all_achievements()

        return {
            "total_achievements": len(achievements),
            "total_points": sum(a.points for a in achievements),
            "avg_points_per_achievement": sum(a.points for a in achievements) / len(achievements)
            if achievements
            else 0,
        }
