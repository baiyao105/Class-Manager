"""数据仓储层

提供数据访问和持久化操作
"""

from .achievement_repository import AchievementRepository
from .base_repository import BaseRepository
from .student_repository import StudentRepository

__all__ = ["AchievementRepository", "BaseRepository", "StudentRepository"]
