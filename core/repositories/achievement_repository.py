"""成就仓储类 - 混合架构实现

提供子库成就数据访问操作，支持统计查询和积分计算
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlmodel import Session, and_, func, select

from ..models.achievement import Achievement, AchievementLevel, AchievementType
from .base_repository import BaseRepository


class AchievementRepository(BaseRepository[Achievement]):
    """成就仓储类 - 子库数据访问

    专门处理子库中的成就数据，支持统计查询、积分计算等功能
    """

    def __init__(self, session: Session):
        """初始化成就仓储

        Args:
            session: 子库数据库会话
        """
        super().__init__(session, Achievement)

    def create(self, entity_data: dict[str, Any]) -> Achievement:
        """创建成就记录

        Args:
            entity_data: 成就数据

        Returns:
            创建的Achievement对象
        """
        # 设置默认值
        if "earned_at" not in entity_data:
            entity_data["earned_at"] = datetime.utcnow()
        if "points" not in entity_data:
            entity_data["points"] = 0.0

        achievement = self._create_entity(entity_data)
        self.session.add(achievement)
        self.session.commit()
        self.session.refresh(achievement)
        return achievement

    def get_by_id(self, entity_id: str) -> Optional[Achievement]:
        """根据ID获取成就

        Args:
            entity_id: 成就ID

        Returns:
            Achievement对象或None
        """
        query = select(Achievement).where(Achievement.id == entity_id)
        if hasattr(Achievement, "is_deleted"):
            query = query.where(not Achievement.is_deleted)

        result = self.session.exec(query)
        return result.first()

    def update(self, entity_id: str, update_data: dict[str, Any]) -> Optional[Achievement]:
        """更新成就信息

        Args:
            entity_id: 成就ID
            update_data: 更新数据

        Returns:
            更新后的Achievement对象
        """
        achievement = self.get_by_id(entity_id)
        if not achievement:
            return None

        achievement = self._update_entity(achievement, update_data)
        self.session.add(achievement)
        self.session.commit()
        self.session.refresh(achievement)
        return achievement

    def delete(self, entity_id: str, soft_delete: bool = True) -> bool:
        """删除成就

        Args:
            entity_id: 成就ID
            soft_delete: 是否软删除

        Returns:
            删除是否成功
        """
        if soft_delete:
            return self.soft_delete(entity_id)
        return self.hard_delete(entity_id)

    def get_by_student_id(self, student_id: int, registry_uuid: Optional[UUID] = None) -> list[Achievement]:
        """根据学生ID获取成就列表

        Args:
            student_id: 学生ID
            registry_uuid: 班级UUID（可选）

        Returns:
            成就列表
        """
        query = select(Achievement).where(Achievement.student_id == student_id)

        if registry_uuid:
            query = query.where(Achievement.registry_uuid == registry_uuid)

        if hasattr(Achievement, "is_deleted"):
            query = query.where(not Achievement.is_deleted)

        query = query.order_by(Achievement.earned_at.desc())
        result = self.session.exec(query)
        return result.all()

    def get_by_template_key(self, template_key: str, registry_uuid: Optional[UUID] = None) -> list[Achievement]:
        """根据成就模板键获取成就列表

        Args:
            template_key: 成就模板键
            registry_uuid: 班级UUID（可选）

        Returns:
            成就列表
        """
        query = select(Achievement).where(Achievement.template_key == template_key)

        if registry_uuid:
            query = query.where(Achievement.registry_uuid == registry_uuid)

        if hasattr(Achievement, "is_deleted"):
            query = query.where(not Achievement.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def search_by_title(self, title: str, registry_uuid: Optional[UUID] = None) -> list[Achievement]:
        """根据成就标题搜索

        Args:
            title: 搜索关键词
            registry_uuid: 班级UUID（可选）

        Returns:
            匹配的成就列表
        """
        query = select(Achievement).where(Achievement.title.contains(title))

        if registry_uuid:
            query = query.where(Achievement.registry_uuid == registry_uuid)

        if hasattr(Achievement, "is_deleted"):
            query = query.where(not Achievement.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_by_type(self, achievement_type: AchievementType, registry_uuid: Optional[UUID] = None) -> list[Achievement]:
        """根据成就类型获取成就列表

        Args:
            achievement_type: 成就类型
            registry_uuid: 班级UUID（可选）

        Returns:
            指定类型的成就列表
        """
        query = select(Achievement).where(Achievement.achievement_type == achievement_type)

        if registry_uuid:
            query = query.where(Achievement.registry_uuid == registry_uuid)

        if hasattr(Achievement, "is_deleted"):
            query = query.where(not Achievement.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_by_level(self, level: AchievementLevel, registry_uuid: Optional[UUID] = None) -> list[Achievement]:
        """根据成就等级获取成就列表

        Args:
            level: 成就等级
            registry_uuid: 班级UUID（可选）

        Returns:
            指定等级的成就列表
        """
        query = select(Achievement).where(Achievement.level == level)

        if registry_uuid:
            query = query.where(Achievement.registry_uuid == registry_uuid)

        if hasattr(Achievement, "is_deleted"):
            query = query.where(not Achievement.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_high_value_achievements(
        self, min_points: float = 50.0, registry_uuid: Optional[UUID] = None
    ) -> list[Achievement]:
        """获取高价值成就

        Args:
            min_points: 最低积分
            registry_uuid: 班级UUID（可选）

        Returns:
            高价值成就列表
        """
        query = select(Achievement).where(Achievement.points >= min_points)

        if registry_uuid:
            query = query.where(Achievement.registry_uuid == registry_uuid)

        if hasattr(Achievement, "is_deleted"):
            query = query.where(not Achievement.is_deleted)

        query = query.order_by(Achievement.points.desc())
        result = self.session.exec(query)
        return result.all()

    def get_recent_achievements(self, limit: int = 10, registry_uuid: Optional[UUID] = None) -> list[Achievement]:
        """获取最近的成就

        Args:
            limit: 返回数量
            registry_uuid: 班级UUID（可选）

        Returns:
            最近的成就列表
        """
        query = select(Achievement).order_by(Achievement.earned_at.desc()).limit(limit)

        if registry_uuid:
            query = query.where(Achievement.registry_uuid == registry_uuid)

        if hasattr(Achievement, "is_deleted"):
            query = query.where(not Achievement.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_achievements_by_date_range(
        self, start_date: datetime, end_date: datetime, registry_uuid: Optional[UUID] = None
    ) -> list[Achievement]:
        """根据日期范围获取成就

        Args:
            start_date: 开始日期
            end_date: 结束日期
            registry_uuid: 班级UUID（可选）

        Returns:
            日期范围内的成就列表
        """
        query = select(Achievement).where(and_(Achievement.earned_at >= start_date, Achievement.earned_at <= end_date))

        if registry_uuid:
            query = query.where(Achievement.registry_uuid == registry_uuid)

        if hasattr(Achievement, "is_deleted"):
            query = query.where(not Achievement.is_deleted)

        query = query.order_by(Achievement.earned_at.desc())
        result = self.session.exec(query)
        return result.all()

    def get_student_points_total(self, student_id: int, registry_uuid: Optional[UUID] = None) -> float:
        """获取学生总积分

        Args:
            student_id: 学生ID
            registry_uuid: 班级UUID（可选）

        Returns:
            学生总积分
        """
        query = select(func.sum(Achievement.points)).where(Achievement.student_id == student_id)

        if registry_uuid:
            query = query.where(Achievement.registry_uuid == registry_uuid)

        if hasattr(Achievement, "is_deleted"):
            query = query.where(not Achievement.is_deleted)

        result = self.session.exec(query).first()
        return float(result or 0.0)

    def get_student_achievement_count(self, student_id: int, registry_uuid: Optional[UUID] = None) -> int:
        """获取学生成就数量

        Args:
            student_id: 学生ID
            registry_uuid: 班级UUID（可选）

        Returns:
            成就数量
        """
        query = select(func.count(Achievement.id)).where(Achievement.student_id == student_id)

        if registry_uuid:
            query = query.where(Achievement.registry_uuid == registry_uuid)

        if hasattr(Achievement, "is_deleted"):
            query = query.where(not Achievement.is_deleted)

        result = self.session.exec(query).first()
        return int(result or 0)

    def get_top_students_by_points(self, limit: int = 10, registry_uuid: Optional[UUID] = None) -> list[dict[str, Any]]:
        """获取积分排行榜

        Args:
            limit: 返回数量
            registry_uuid: 班级UUID（可选）

        Returns:
            积分排行榜列表
        """
        query = (
            select(
                Achievement.student_id,
                func.sum(Achievement.points).label("total_points"),
                func.count(Achievement.id).label("achievement_count"),
            )
            .group_by(Achievement.student_id)
            .order_by(func.sum(Achievement.points).desc())
            .limit(limit)
        )

        if registry_uuid:
            query = query.where(Achievement.registry_uuid == registry_uuid)

        if hasattr(Achievement, "is_deleted"):
            query = query.where(not Achievement.is_deleted)

        result = self.session.exec(query)
        return [
            {
                "student_id": row.student_id,
                "total_points": float(row.total_points or 0.0),
                "achievement_count": int(row.achievement_count or 0),
            }
            for row in result
        ]

    def get_achievement_statistics(self, registry_uuid: Optional[UUID] = None) -> dict[str, Any]:
        """获取成就统计信息

        Args:
            registry_uuid: 班级UUID（可选）

        Returns:
            统计信息字典
        """
        base_query = select(Achievement)

        if registry_uuid:
            base_query = base_query.where(Achievement.registry_uuid == registry_uuid)

        if hasattr(Achievement, "is_deleted"):
            base_query = base_query.where(not Achievement.is_deleted)

        # 总成就数量
        total_count = len(self.session.exec(base_query).all())

        # 总积分
        total_points_query = select(func.sum(Achievement.points))
        if registry_uuid:
            total_points_query = total_points_query.where(Achievement.registry_uuid == registry_uuid)
        if hasattr(Achievement, "is_deleted"):
            total_points_query = total_points_query.where(not Achievement.is_deleted)

        total_points = self.session.exec(total_points_query).first() or 0.0

        # 平均积分
        avg_points = float(total_points) / total_count if total_count > 0 else 0.0

        # 按类型统计
        type_stats = {}
        for achievement_type in AchievementType:
            type_query = select(func.count(Achievement.id)).where(Achievement.achievement_type == achievement_type)
            if registry_uuid:
                type_query = type_query.where(Achievement.registry_uuid == registry_uuid)
            if hasattr(Achievement, "is_deleted"):
                type_query = type_query.where(not Achievement.is_deleted)

            count = self.session.exec(type_query).first() or 0
            type_stats[achievement_type.value] = int(count)

        # 按等级统计
        level_stats = {}
        for level in AchievementLevel:
            level_query = select(func.count(Achievement.id)).where(Achievement.level == level)
            if registry_uuid:
                level_query = level_query.where(Achievement.registry_uuid == registry_uuid)
            if hasattr(Achievement, "is_deleted"):
                level_query = level_query.where(not Achievement.is_deleted)

            count = self.session.exec(level_query).first() or 0
            level_stats[level.value] = int(count)

        return {
            "total_count": total_count,
            "total_points": float(total_points),
            "avg_points": avg_points,
            "type_distribution": type_stats,
            "level_distribution": level_stats,
        }

    def batch_create_achievements(self, achievements_data: list[dict[str, Any]]) -> list[Achievement]:
        """批量创建成就

        Args:
            achievements_data: 成就数据列表

        Returns:
            创建的成就列表
        """
        achievements = []

        with self.transaction():
            for achievement_data in achievements_data:
                achievement = self._create_entity(achievement_data)
                achievements.append(achievement)
                self.session.add(achievement)

        return achievements

    def delete_student_achievements(self, student_id: int, registry_uuid: Optional[UUID] = None) -> int:
        """删除学生的所有成就

        Args:
            student_id: 学生ID
            registry_uuid: 班级UUID（可选）

        Returns:
            删除的成就数量
        """
        achievements = self.get_by_student_id(student_id, registry_uuid)
        deleted_count = 0

        with self.transaction():
            for achievement in achievements:
                if self.soft_delete(str(achievement.id)):
                    deleted_count += 1

        return deleted_count
