"""成就管理服务层 - Repository模式重构

提供成就系统相关的业务逻辑操作，使用Repository模式进行数据访问
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

from ..models.achievement import Achievement, AchievementLevel, AchievementType
from ..repositories.achievement_repository import AchievementRepository
from ..repositories.student_repository import StudentRepository


class AchievementService:
    """成就服务类 - 使用Repository模式

    负责成就系统相关的业务逻辑，通过AchievementRepository进行数据访问
    """

    def __init__(self, achievement_repository: AchievementRepository, student_repository: StudentRepository = None):
        """初始化成就服务

        Args:
            achievement_repository: 成就仓储实例
            student_repository: 学生仓储实例（可选，用于验证学生信息）
        """
        self.achievement_repository = achievement_repository
        self.student_repository = student_repository

    def create_achievement(
        self,
        student_id: int,
        registry_uuid: UUID,
        title: str,
        description: str,
        points: float = 10.0,
        achievement_type: AchievementType = AchievementType.BEHAVIOR,
        level: AchievementLevel = AchievementLevel.BRONZE,
        template_key: Optional[str] = None,
    ) -> Achievement:
        """创建新成就

        Args:
            student_id: 学生ID
            registry_uuid: 班级UUID
            title: 成就标题
            description: 成就描述
            points: 积分
            achievement_type: 成就类型
            level: 成就等级
            template_key: 成就模板键（可选）

        Returns:
            创建的成就对象

        Raises:
            ValueError: 当学生不存在时
        """
        # 验证学生是否存在（如果提供了student_repository）
        if self.student_repository:
            student = self.student_repository.get_by_id(str(student_id))
            if not student:
                raise ValueError(f"学生 {student_id} 不存在")

        # 准备成就数据
        achievement_data = {
            "student_id": student_id,
            "registry_uuid": registry_uuid,
            "title": title,
            "description": description,
            "points": points,
            "achievement_type": achievement_type,
            "level": level,
            "template_key": template_key,
            "earned_at": datetime.utcnow(),
        }

        # 通过Repository创建成就
        achievement = self.achievement_repository.create(achievement_data)

        # 更新学生积分（如果提供了student_repository）
        if self.student_repository and points > 0:
            self.student_repository.update_student_score(str(student_id), points, f"获得成就: {title}")

        return achievement

    def get_achievement_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """根据ID获取成就

        Args:
            achievement_id: 成就ID

        Returns:
            成就对象或None
        """
        return self.achievement_repository.get_by_id(achievement_id)

    def get_student_achievements(self, student_id: int, registry_uuid: Optional[UUID] = None) -> list[Achievement]:
        """获取学生的所有成就

        Args:
            student_id: 学生ID
            registry_uuid: 班级UUID（可选）

        Returns:
            成就列表
        """
        return self.achievement_repository.get_by_student_id(student_id, registry_uuid)

    def get_achievements_by_template(
        self, template_key: str, registry_uuid: Optional[UUID] = None
    ) -> list[Achievement]:
        """根据模板键获取成就列表

        Args:
            template_key: 成就模板键
            registry_uuid: 班级UUID（可选）

        Returns:
            成就列表
        """
        return self.achievement_repository.get_by_template_key(template_key, registry_uuid)

    def search_achievements(self, title: str, registry_uuid: Optional[UUID] = None) -> list[Achievement]:
        """搜索成就

        Args:
            title: 搜索关键词
            registry_uuid: 班级UUID（可选）

        Returns:
            匹配的成就列表
        """
        return self.achievement_repository.search_by_title(title, registry_uuid)

    def get_achievements_by_type(
        self, achievement_type: AchievementType, registry_uuid: Optional[UUID] = None
    ) -> list[Achievement]:
        """根据类型获取成就

        Args:
            achievement_type: 成就类型
            registry_uuid: 班级UUID（可选）

        Returns:
            指定类型的成就列表
        """
        return self.achievement_repository.get_by_type(achievement_type, registry_uuid)

    def get_achievements_by_level(
        self, level: AchievementLevel, registry_uuid: Optional[UUID] = None
    ) -> list[Achievement]:
        """根据等级获取成就

        Args:
            level: 成就等级
            registry_uuid: 班级UUID（可选）

        Returns:
            指定等级的成就列表
        """
        return self.achievement_repository.get_by_level(level, registry_uuid)

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
        return self.achievement_repository.get_high_value_achievements(min_points, registry_uuid)

    def get_recent_achievements(self, limit: int = 10, registry_uuid: Optional[UUID] = None) -> list[Achievement]:
        """获取最近的成就

        Args:
            limit: 返回数量
            registry_uuid: 班级UUID（可选）

        Returns:
            最近的成就列表
        """
        return self.achievement_repository.get_recent_achievements(limit, registry_uuid)

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
        return self.achievement_repository.get_achievements_by_date_range(start_date, end_date, registry_uuid)

    def update_achievement(
        self,
        achievement_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        points: Optional[float] = None,
        achievement_type: Optional[AchievementType] = None,
        level: Optional[AchievementLevel] = None,
    ) -> Optional[Achievement]:
        """更新成就信息

        Args:
            achievement_id: 成就ID
            title: 新标题
            description: 新描述
            points: 新积分
            achievement_type: 新类型
            level: 新等级

        Returns:
            更新后的成就对象或None
        """
        # 准备更新数据
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if points is not None:
            update_data["points"] = points
        if achievement_type is not None:
            update_data["achievement_type"] = achievement_type
        if level is not None:
            update_data["level"] = level

        # 执行更新
        return self.achievement_repository.update(achievement_id, update_data)

    def delete_achievement(self, achievement_id: str, soft_delete: bool = True) -> bool:
        """删除成就

        Args:
            achievement_id: 成就ID
            soft_delete: 是否软删除

        Returns:
            删除是否成功
        """
        # 获取成就信息用于回退积分
        achievement = self.achievement_repository.get_by_id(achievement_id)
        if not achievement:
            return False

        # 删除成就
        success = self.achievement_repository.delete(achievement_id, soft_delete)

        # 回退学生积分（如果提供了student_repository）
        if success and self.student_repository and achievement.points > 0:
            self.student_repository.update_student_score(
                str(achievement.student_id), -achievement.points, f"删除成就: {achievement.title}"
            )

        return success

    def get_student_points_total(self, student_id: int, registry_uuid: Optional[UUID] = None) -> float:
        """获取学生总积分

        Args:
            student_id: 学生ID
            registry_uuid: 班级UUID（可选）

        Returns:
            学生总积分
        """
        return self.achievement_repository.get_student_points_total(student_id, registry_uuid)

    def get_student_achievement_count(self, student_id: int, registry_uuid: Optional[UUID] = None) -> int:
        """获取学生成就数量

        Args:
            student_id: 学生ID
            registry_uuid: 班级UUID（可选）

        Returns:
            成就数量
        """
        return self.achievement_repository.get_student_achievement_count(student_id, registry_uuid)

    def get_leaderboard(self, limit: int = 10, registry_uuid: Optional[UUID] = None) -> list[dict[str, Any]]:
        """获取积分排行榜

        Args:
            limit: 返回数量
            registry_uuid: 班级UUID（可选）

        Returns:
            积分排行榜列表
        """
        return self.achievement_repository.get_top_students_by_points(limit, registry_uuid)

    def get_achievement_statistics(self, registry_uuid: Optional[UUID] = None) -> dict[str, Any]:
        """获取成就统计信息

        Args:
            registry_uuid: 班级UUID（可选）

        Returns:
            统计信息字典
        """
        return self.achievement_repository.get_achievement_statistics(registry_uuid)

    def batch_create_achievements(self, achievements_data: list[dict[str, Any]]) -> list[Achievement]:
        """批量创建成就

        Args:
            achievements_data: 成就数据列表

        Returns:
            创建的成就列表
        """
        # 为每个成就数据添加默认的earned_at时间
        for data in achievements_data:
            if "earned_at" not in data:
                data["earned_at"] = datetime.utcnow()

        achievements = self.achievement_repository.batch_create_achievements(achievements_data)

        # 批量更新学生积分（如果提供了student_repository）
        if self.student_repository:
            score_updates = []
            for achievement in achievements:
                if achievement.points > 0:
                    score_updates.append(
                        {
                            "student_id": str(achievement.student_id),
                            "score_change": achievement.points,
                            "reason": f"获得成就: {achievement.title}",
                        }
                    )

            if score_updates:
                self.student_repository.batch_update_scores(score_updates)

        return achievements

    def delete_student_achievements(self, student_id: int, registry_uuid: Optional[UUID] = None) -> int:
        """删除学生的所有成就

        Args:
            student_id: 学生ID
            registry_uuid: 班级UUID（可选）

        Returns:
            删除的成就数量
        """
        return self.achievement_repository.delete_student_achievements(student_id, registry_uuid)

    def get_daily_achievements(
        self, date: Optional[datetime] = None, registry_uuid: Optional[UUID] = None
    ) -> list[Achievement]:
        """获取指定日期的成就

        Args:
            date: 指定日期（默认为今天）
            registry_uuid: 班级UUID（可选）

        Returns:
            当日成就列表
        """
        if date is None:
            date = datetime.now().date()

        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())

        return self.get_achievements_by_date_range(start_date, end_date, registry_uuid)

    def get_weekly_achievements(
        self, week_start: Optional[datetime] = None, registry_uuid: Optional[UUID] = None
    ) -> list[Achievement]:
        """获取指定周的成就

        Args:
            week_start: 周开始日期（默认为本周一）
            registry_uuid: 班级UUID（可选）

        Returns:
            本周成就列表
        """
        if week_start is None:
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())

        start_date = datetime.combine(week_start, datetime.min.time())
        end_date = start_date + timedelta(days=7)

        return self.get_achievements_by_date_range(start_date, end_date, registry_uuid)

    def get_monthly_achievements(
        self, year: Optional[int] = None, month: Optional[int] = None, registry_uuid: Optional[UUID] = None
    ) -> list[Achievement]:
        """获取指定月份的成就

        Args:
            year: 年份（默认为当前年）
            month: 月份（默认为当前月）
            registry_uuid: 班级UUID（可选）

        Returns:
            当月成就列表
        """
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month

        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

        return self.get_achievements_by_date_range(start_date, end_date, registry_uuid)

    def get_achievement_stats(self) -> dict[str, Any]:
        """获取成就统计信息 - 临时方法
        
        Returns:
            包含成就统计信息的字典
        """
        try:
            return {
                "total_achievements": 0,
                "recent_achievements": 0,
                "achievement_points": 0,
                "achievement_types": {},
            }
        except Exception as e:
            print(f"获取成就统计失败: {e}")
            return {
                "total_achievements": 0,
                "recent_achievements": 0,
                "achievement_points": 0,
                "achievement_types": {},
            }
