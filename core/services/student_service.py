"""学生管理服务层 - Repository模式重构

提供学生相关的业务逻辑操作，使用Repository模式进行数据访问
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from ..models.student import Student, StudentStatus
from ..repositories.class_repository import ClassRepository
from ..repositories.student_repository import StudentRepository


class StudentService:
    """学生服务类 - 使用Repository模式

    负责学生相关的业务逻辑，通过StudentRepository进行数据访问
    """

    def __init__(self, student_repository: StudentRepository, class_repository: ClassRepository = None):
        """初始化学生服务

        Args:
            student_repository: 学生仓储实例
            class_repository: 班级仓储实例（可选，用于验证班级信息）
        """
        self.student_repository = student_repository
        self.class_repository = class_repository

    def create_student(
        self,
        name: str,
        student_number: int,
        registry_uuid: UUID,
        classroom_id: Optional[int] = None,
        group_id: Optional[int] = None,
        base_score: float = 100.0,
        status: StudentStatus = StudentStatus.ACTIVE,
    ) -> Student:
        """创建新学生

        Args:
            name: 学生姓名
            student_number: 学号
            registry_uuid: 班级UUID
            classroom_id: 班级ID（可选）
            group_id: 小组ID（可选）
            base_score: 基础积分
            status: 学生状态

        Returns:
            创建的学生对象

        Raises:
            ValueError: 当学号已存在或班级不存在时
        """
        # 检查学号是否已存在
        existing_student = self.student_repository.get_by_student_number(student_number, registry_uuid)
        if existing_student:
            raise ValueError(f"学号 {student_number} 在该班级中已存在")

        # 验证班级是否存在（如果提供了class_repository）
        if self.class_repository:
            class_registry = self.class_repository.get_by_id(str(registry_uuid))
            if not class_registry:
                raise ValueError(f"班级 {registry_uuid} 不存在")

        # 准备学生数据
        student_data = {
            "name": name,
            "student_number": student_number,
            "registry_uuid": registry_uuid,
            "classroom_id": classroom_id,
            "group_id": group_id,
            "base_score": base_score,
            "current_score": base_score,
            "total_score": base_score,
            "highest_score": base_score,
            "lowest_score": base_score,
            "status": status,
        }

        # 通过Repository创建学生
        student = self.student_repository.create(student_data)

        # 更新班级统计信息（如果提供了class_repository）
        if self.class_repository:
            self._update_class_student_count(registry_uuid)

        return student

    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """根据ID获取学生

        Args:
            student_id: 学生ID

        Returns:
            学生对象或None
        """
        return self.student_repository.get_by_id(student_id)

    def get_student_by_number(self, student_number: int, registry_uuid: Optional[UUID] = None) -> Optional[Student]:
        """根据学号获取学生

        Args:
            student_number: 学号
            registry_uuid: 班级UUID（可选）

        Returns:
            学生对象或None
        """
        return self.student_repository.get_by_student_number(student_number, registry_uuid)

    def get_students_by_class(self, registry_uuid: UUID) -> list[Student]:
        """获取指定班级的所有学生

        Args:
            registry_uuid: 班级UUID

        Returns:
            学生列表
        """
        return self.student_repository.get_by_class_uuid(registry_uuid)

    def get_students_by_classroom(self, classroom_id: int) -> list[Student]:
        """根据班级ID获取学生列表

        Args:
            classroom_id: 班级ID

        Returns:
            学生列表
        """
        return self.student_repository.get_by_classroom_id(classroom_id)

    def search_students(self, query: str, registry_uuid: Optional[UUID] = None) -> list[Student]:
        """搜索学生

        Args:
            query: 搜索关键词（姓名或学号）
            registry_uuid: 班级UUID（可选）

        Returns:
            匹配的学生列表
        """
        return self.student_repository.search_by_name_or_number(query, registry_uuid)

    def get_active_students(self, registry_uuid: Optional[UUID] = None) -> list[Student]:
        """获取活跃学生

        Args:
            registry_uuid: 班级UUID（可选）

        Returns:
            活跃学生列表
        """
        return self.student_repository.get_active_students(registry_uuid)

    def update_student(
        self,
        student_id: str,
        name: Optional[str] = None,
        student_number: Optional[int] = None,
        classroom_id: Optional[int] = None,
        group_id: Optional[int] = None,
        status: Optional[StudentStatus] = None,
        base_score: Optional[float] = None,
    ) -> Optional[Student]:
        """更新学生信息

        Args:
            student_id: 学生ID
            name: 新姓名
            student_number: 新学号
            classroom_id: 新班级ID
            group_id: 新小组ID
            status: 新状态
            base_score: 新基础积分

        Returns:
            更新后的学生对象或None

        Raises:
            ValueError: 当新学号已存在时
        """
        # 检查学生是否存在
        existing_student = self.student_repository.get_by_id(student_id)
        if not existing_student:
            return None

        # 如果要更新学号，检查新学号是否已被其他学生使用
        if student_number and student_number != existing_student.student_number:
            number_conflict = self.student_repository.get_by_student_number(
                student_number, existing_student.registry_uuid
            )
            if number_conflict and str(number_conflict.id) != student_id:
                raise ValueError(f"学号 {student_number} 在该班级中已被其他学生使用")

        # 准备更新数据
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if student_number is not None:
            update_data["student_number"] = student_number
        if classroom_id is not None:
            update_data["classroom_id"] = classroom_id
        if group_id is not None:
            update_data["group_id"] = group_id
        if status is not None:
            update_data["status"] = status
        if base_score is not None:
            update_data["base_score"] = base_score

        # 执行更新
        return self.student_repository.update(student_id, update_data)

    def delete_student(self, student_id: str, soft_delete: bool = True) -> bool:
        """删除学生

        Args:
            student_id: 学生ID
            soft_delete: 是否软删除

        Returns:
            删除是否成功
        """
        # 获取学生信息用于更新班级统计
        student = self.student_repository.get_by_id(student_id)
        if not student:
            return False

        # 删除学生
        success = self.student_repository.delete(student_id, soft_delete)

        # 更新班级统计信息
        if success and self.class_repository:
            self._update_class_student_count(student.registry_uuid)

        return success

    def update_student_score(
        self, student_id: str, score_change: float, reason: Optional[str] = None
    ) -> Optional[Student]:
        """更新学生积分

        Args:
            student_id: 学生ID
            score_change: 积分变化（正数为加分，负数为扣分）
            reason: 变更原因

        Returns:
            更新后的学生对象或None
        """
        return self.student_repository.update_student_score(student_id, score_change, reason)

    def batch_update_scores(self, score_updates: list[dict[str, Any]]) -> list[Student]:
        """批量更新学生积分

        Args:
            score_updates: 积分更新列表

        Returns:
            更新后的学生列表
        """
        return self.student_repository.batch_update_scores(score_updates)

    def reset_class_scores(self, registry_uuid: UUID, reset_to_base: bool = True) -> int:
        """重置班级所有学生积分

        Args:
            registry_uuid: 班级UUID
            reset_to_base: 是否重置到基础积分

        Returns:
            重置的学生数量
        """
        return self.student_repository.reset_student_scores(registry_uuid, reset_to_base)

    def get_students_by_group(self, group_id: int) -> list[Student]:
        """根据小组ID获取学生

        Args:
            group_id: 小组ID

        Returns:
            小组学生列表
        """
        return self.student_repository.get_students_by_group(group_id)

    def get_students_by_score_range(
        self, min_score: float, max_score: float, registry_uuid: Optional[UUID] = None
    ) -> list[Student]:
        """根据分数范围获取学生

        Args:
            min_score: 最低分数
            max_score: 最高分数
            registry_uuid: 班级UUID（可选）

        Returns:
            分数范围内的学生列表
        """
        return self.student_repository.get_students_by_score_range(min_score, max_score, registry_uuid)

    def get_top_students(self, limit: int = 10, registry_uuid: Optional[UUID] = None) -> list[Student]:
        """获取积分排名前N的学生

        Args:
            limit: 返回数量
            registry_uuid: 班级UUID（可选）

        Returns:
            排名前N的学生列表
        """
        return self.student_repository.get_top_students(limit, registry_uuid)

    def get_class_statistics(self, registry_uuid: UUID) -> dict[str, Any]:
        """获取班级学生统计信息

        Args:
            registry_uuid: 班级UUID

        Returns:
            统计信息字典
        """
        return self.student_repository.get_class_statistics(registry_uuid)

    def activate_student(self, student_id: str) -> bool:
        """激活学生

        Args:
            student_id: 学生ID

        Returns:
            激活是否成功
        """
        result = self.student_repository.update(student_id, {"status": StudentStatus.ACTIVE})
        return result is not None

    def deactivate_student(self, student_id: str) -> bool:
        """停用学生

        Args:
            student_id: 学生ID

        Returns:
            停用是否成功
        """
        result = self.student_repository.update(student_id, {"status": StudentStatus.INACTIVE})
        return result is not None

    def graduate_student(self, student_id: str) -> bool:
        """学生毕业

        Args:
            student_id: 学生ID

        Returns:
            操作是否成功
        """
        result = self.student_repository.update(student_id, {"status": StudentStatus.GRADUATED})
        return result is not None

    def _update_class_student_count(self, registry_uuid: UUID) -> None:
        """更新班级学生数量统计

        Args:
            registry_uuid: 班级UUID
        """
        if not self.class_repository:
            return

        # 获取班级学生统计
        stats = self.get_class_statistics(registry_uuid)

        # 更新班级统计信息
        self.class_repository.update_statistics(
            str(registry_uuid),
            {
                "student_count": stats["total_count"],
                "active_student_count": stats["active_count"],
                "total_score": stats["total_score"],
                "avg_score": stats["avg_score"],
                "last_sync_at": datetime.utcnow(),
            },
        )
