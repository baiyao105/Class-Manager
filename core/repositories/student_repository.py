"""学生仓储类 - 混合架构实现

提供子库学生数据访问操作，支持按班级查询和批量操作
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlmodel import Session, and_, or_, select

from ..models.student import Student, StudentStatus
from .base_repository import BaseRepository


class StudentRepository(BaseRepository[Student]):
    """学生仓储类 - 子库数据访问

    专门处理子库中的学生数据，支持按班级查询、批量操作等功能
    """

    def __init__(self, session: Session):
        """初始化学生仓储

        Args:
            session: 子库数据库会话
        """
        super().__init__(session, Student)

    def create(self, entity_data: dict[str, Any]) -> Student:
        """创建学生

        Args:
            entity_data: 学生数据

        Returns:
            创建的Student对象
        """
        # 设置默认值
        if "current_score" not in entity_data:
            entity_data["current_score"] = 100.0
        if "base_score" not in entity_data:
            entity_data["base_score"] = 100.0
        if "total_score" not in entity_data:
            entity_data["total_score"] = entity_data["current_score"]
        if "highest_score" not in entity_data:
            entity_data["highest_score"] = entity_data["current_score"]
        if "lowest_score" not in entity_data:
            entity_data["lowest_score"] = entity_data["current_score"]

        student = self._create_entity(entity_data)
        self.session.add(student)
        self.session.commit()
        self.session.refresh(student)
        return student

    def get_by_id(self, entity_id: str) -> Optional[Student]:
        """根据ID获取学生

        Args:
            entity_id: 学生ID

        Returns:
            Student对象或None
        """
        query = select(Student).where(Student.id == entity_id)
        if hasattr(Student, "is_deleted"):
            query = query.where(not Student.is_deleted)

        result = self.session.exec(query)
        return result.first()

    def update(self, entity_id: str, update_data: dict[str, Any]) -> Optional[Student]:
        """更新学生信息

        Args:
            entity_id: 学生ID
            update_data: 更新数据

        Returns:
            更新后的Student对象
        """
        student = self.get_by_id(entity_id)
        if not student:
            return None

        # 更新最后积分更新时间
        if any(field in update_data for field in ["current_score", "total_score"]):
            update_data["last_score_update"] = datetime.utcnow()

        student = self._update_entity(student, update_data)
        self.session.add(student)
        self.session.commit()
        self.session.refresh(student)
        return student

    def delete(self, entity_id: str, soft_delete: bool = True) -> bool:
        """删除学生

        Args:
            entity_id: 学生ID
            soft_delete: 是否软删除

        Returns:
            删除是否成功
        """
        if soft_delete:
            return self.soft_delete(entity_id)
        return self.hard_delete(entity_id)

    def get_by_student_number(self, student_number: int, registry_uuid: Optional[UUID] = None) -> Optional[Student]:
        """根据学号获取学生

        Args:
            student_number: 学号
            registry_uuid: 班级UUID（可选，用于精确查找）

        Returns:
            Student对象或None
        """
        query = select(Student).where(Student.student_number == student_number)

        if registry_uuid:
            query = query.where(Student.registry_uuid == registry_uuid)

        if hasattr(Student, "is_deleted"):
            query = query.where(not Student.is_deleted)

        result = self.session.exec(query)
        return result.first()

    def get_by_class_uuid(self, registry_uuid: UUID) -> list[Student]:
        """根据班级UUID获取学生列表

        Args:
            registry_uuid: 班级UUID

        Returns:
            学生列表
        """
        query = select(Student).where(Student.registry_uuid == registry_uuid)

        if hasattr(Student, "is_deleted"):
            query = query.where(not Student.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_by_classroom_id(self, classroom_id: int) -> list[Student]:
        """根据班级ID获取学生列表

        Args:
            classroom_id: 班级ID

        Returns:
            学生列表
        """
        query = select(Student).where(Student.classroom_id == classroom_id)

        if hasattr(Student, "is_deleted"):
            query = query.where(not Student.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def search_by_name_or_number(self, query_text: str, registry_uuid: Optional[UUID] = None) -> list[Student]:
        """根据姓名或学号搜索学生

        Args:
            query_text: 搜索关键词
            registry_uuid: 班级UUID（可选）

        Returns:
            匹配的学生列表
        """
        # 尝试将查询文本转换为数字（学号）
        try:
            student_number = int(query_text)
            query = select(Student).where(
                or_(Student.name.contains(query_text), Student.student_number == student_number)
            )
        except ValueError:
            # 如果不是数字，只按姓名搜索
            query = select(Student).where(Student.name.contains(query_text))

        if registry_uuid:
            query = query.where(Student.registry_uuid == registry_uuid)

        if hasattr(Student, "is_deleted"):
            query = query.where(not Student.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_active_students(self, registry_uuid: Optional[UUID] = None) -> list[Student]:
        """获取活跃学生

        Args:
            registry_uuid: 班级UUID（可选）

        Returns:
            活跃学生列表
        """
        query = select(Student).where(Student.status == StudentStatus.ACTIVE)

        if registry_uuid:
            query = query.where(Student.registry_uuid == registry_uuid)

        if hasattr(Student, "is_deleted"):
            query = query.where(not Student.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_students_by_group(self, group_id: int) -> list[Student]:
        """根据小组ID获取学生

        Args:
            group_id: 小组ID

        Returns:
            小组学生列表
        """
        query = select(Student).where(Student.group_id == group_id)

        if hasattr(Student, "is_deleted"):
            query = query.where(not Student.is_deleted)

        result = self.session.exec(query)
        return result.all()

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
        query = select(Student).where(and_(Student.current_score >= min_score, Student.current_score <= max_score))

        if registry_uuid:
            query = query.where(Student.registry_uuid == registry_uuid)

        if hasattr(Student, "is_deleted"):
            query = query.where(not Student.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_top_students(self, limit: int = 10, registry_uuid: Optional[UUID] = None) -> list[Student]:
        """获取积分排名前N的学生

        Args:
            limit: 返回数量
            registry_uuid: 班级UUID（可选）

        Returns:
            排名前N的学生列表
        """
        query = select(Student).order_by(Student.current_score.desc()).limit(limit)

        if registry_uuid:
            query = query.where(Student.registry_uuid == registry_uuid)

        if hasattr(Student, "is_deleted"):
            query = query.where(not Student.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def update_student_score(
        self, student_id: str, score_change: float, reason: Optional[str] = None
    ) -> Optional[Student]:
        """更新学生积分

        Args:
            student_id: 学生ID
            score_change: 积分变化（正数为加分，负数为扣分）
            reason: 变更原因

        Returns:
            更新后的Student对象
        """
        student = self.get_by_id(student_id)
        if not student:
            return None

        # 计算新分数
        new_score = student.current_score + score_change

        # 更新统计信息
        update_data = {
            "current_score": new_score,
            "total_score": student.total_score + score_change,
            "last_score_update": datetime.utcnow(),
        }

        # 更新最高分记录
        if new_score > student.highest_score:
            update_data["highest_score"] = new_score
            update_data["highest_score_time"] = datetime.utcnow()

        # 更新最低分记录
        if new_score < student.lowest_score:
            update_data["lowest_score"] = new_score
            update_data["lowest_score_time"] = datetime.utcnow()

        # 更新累计获得/扣除积分
        if score_change > 0:
            update_data["total_earned"] = student.total_earned + score_change
        else:
            update_data["total_deducted"] = student.total_deducted + abs(score_change)

        return self.update(student_id, update_data)

    def batch_update_scores(self, score_updates: list[dict[str, Any]]) -> list[Student]:
        """批量更新学生积分

        Args:
            score_updates: 积分更新列表，每个字典包含student_id和score_change

        Returns:
            更新后的学生列表
        """
        updated_students = []

        with self.transaction():
            for update in score_updates:
                student_id = update["student_id"]
                score_change = update["score_change"]
                reason = update.get("reason")

                student = self.update_student_score(student_id, score_change, reason)
                if student:
                    updated_students.append(student)

        return updated_students

    def reset_student_scores(self, registry_uuid: UUID, reset_to_base: bool = True) -> int:
        """重置班级所有学生积分

        Args:
            registry_uuid: 班级UUID
            reset_to_base: 是否重置到基础积分

        Returns:
            重置的学生数量
        """
        students = self.get_by_class_uuid(registry_uuid)
        reset_count = 0

        with self.transaction():
            for student in students:
                reset_score = student.base_score if reset_to_base else 100.0

                update_data = {
                    "current_score": reset_score,
                    "last_reset_time": datetime.utcnow(),
                    "last_score_update": datetime.utcnow(),
                }

                if self.update(str(student.id), update_data):
                    reset_count += 1

        return reset_count

    def get_class_statistics(self, registry_uuid: UUID) -> dict[str, Any]:
        """获取班级学生统计信息

        Args:
            registry_uuid: 班级UUID

        Returns:
            统计信息字典
        """
        students = self.get_by_class_uuid(registry_uuid)

        if not students:
            return {
                "total_count": 0,
                "active_count": 0,
                "avg_score": 0.0,
                "max_score": 0.0,
                "min_score": 0.0,
                "total_score": 0.0,
            }

        active_students = [s for s in students if s.status == StudentStatus.ACTIVE]
        scores = [s.current_score for s in students]

        return {
            "total_count": len(students),
            "active_count": len(active_students),
            "avg_score": sum(scores) / len(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0,
            "min_score": min(scores) if scores else 0.0,
            "total_score": sum(scores),
        }
