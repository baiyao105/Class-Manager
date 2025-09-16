"""班级仓储类 - 混合架构实现

支持总库索引和子库数据的统一访问
"""

from typing import Any, Optional

from sqlmodel import Session, select

from ..models.class_ import Classroom
from ..models.master import DataRegistry
from .base_repository import BaseRepository


class ClassRepository(BaseRepository[DataRegistry]):
    """班级仓储类 - 混合架构实现

    管理总库班级索引(DataRegistry)和子库班级详情(Classroom)
    提供统一的班级数据访问接口
    """

    def __init__(self, master_session: Session, sub_session_factory=None):
        """初始化班级仓储

        Args:
            master_session: 总库会话
            sub_session_factory: 子库会话工厂函数
        """
        super().__init__(master_session, DataRegistry)
        self.master_session = master_session
        self.sub_session_factory = sub_session_factory

    def create(self, entity_data: dict[str, Any]) -> DataRegistry:
        """创建班级 - 同时创建总库索引和子库数据

        Args:
            entity_data: 班级数据，包含基本信息和配置

        Returns:
            创建的DataRegistry对象
        """
        # 创建总库索引记录
        registry_data = {
            "class_name": entity_data["name"],
            "class_type": entity_data.get("class_type", "regular"),
            "grade": entity_data.get("grade"),
            "school_year": entity_data.get("school_year"),
            "db_path": entity_data.get("db_path", ""),
            "description": entity_data.get("description"),
        }

        registry = self._create_entity(registry_data)
        self.session.add(registry)
        self.session.commit()
        self.session.refresh(registry)

        # 创建子库班级详情
        if self.sub_session_factory:
            classroom_data = {
                "registry_uuid": registry.id,  # 关联总库ID
                "name": entity_data["name"],
                "teacher_name": entity_data.get("teacher_name", ""),
                "teacher_contact": entity_data.get("teacher_contact"),
                "description": entity_data.get("description"),
            }

            sub_session = self.sub_session_factory(registry.db_path)
            try:
                classroom = Classroom(**classroom_data)
                sub_session.add(classroom)
                sub_session.commit()
            finally:
                sub_session.close()

        return registry

    def get_by_id(self, entity_id: str) -> Optional[DataRegistry]:
        """根据ID获取班级索引

        Args:
            entity_id: 班级ID

        Returns:
            DataRegistry对象或None
        """
        query = select(DataRegistry).where(DataRegistry.id == entity_id)
        if hasattr(DataRegistry, "is_deleted"):
            query = query.where(not DataRegistry.is_deleted)

        result = self.session.exec(query)
        return result.first()

    def update(self, entity_id: str, update_data: dict[str, Any]) -> Optional[DataRegistry]:
        """更新班级信息

        Args:
            entity_id: 班级ID
            update_data: 更新数据

        Returns:
            更新后的DataRegistry对象
        """
        registry = self.get_by_id(entity_id)
        if not registry:
            return None

        # 更新总库索引
        registry = self._update_entity(registry, update_data)
        self.session.add(registry)
        self.session.commit()
        self.session.refresh(registry)

        # 同步更新子库数据
        if self.sub_session_factory and registry.db_path:
            sub_session = self.sub_session_factory(registry.db_path)
            try:
                classroom_query = select(Classroom).where(Classroom.registry_uuid == registry.id)
                classroom = sub_session.exec(classroom_query).first()

                if classroom:
                    # 更新子库班级信息
                    classroom_updates = {
                        "name": update_data.get("class_name", classroom.name),
                        "teacher_name": update_data.get("teacher_name", classroom.teacher_name),
                        "teacher_contact": update_data.get("teacher_contact", classroom.teacher_contact),
                        "description": update_data.get("description", classroom.description),
                    }

                    for field, value in classroom_updates.items():
                        if hasattr(classroom, field):
                            setattr(classroom, field, value)

                    sub_session.add(classroom)
                    sub_session.commit()
            finally:
                sub_session.close()

        return registry

    def delete(self, entity_id: str, soft_delete: bool = True) -> bool:
        """删除班级

        Args:
            entity_id: 班级ID
            soft_delete: 是否软删除

        Returns:
            删除是否成功
        """
        if soft_delete:
            return self.soft_delete(entity_id)
        return self.hard_delete(entity_id)

    def get_by_name(self, name: str) -> Optional[DataRegistry]:
        """根据班级名称获取班级

        Args:
            name: 班级名称

        Returns:
            DataRegistry对象或None
        """
        query = select(DataRegistry).where(DataRegistry.class_name == name)
        if hasattr(DataRegistry, "is_deleted"):
            query = query.where(not DataRegistry.is_deleted)

        result = self.session.exec(query)
        return result.first()

    def search_by_name(self, query_text: str) -> list[DataRegistry]:
        """根据名称搜索班级

        Args:
            query_text: 搜索关键词

        Returns:
            匹配的班级列表
        """
        query = select(DataRegistry).where(DataRegistry.class_name.contains(query_text))
        if hasattr(DataRegistry, "is_deleted"):
            query = query.where(not DataRegistry.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_active_classes(self) -> list[DataRegistry]:
        """获取活跃的班级

        Returns:
            活跃班级列表
        """
        query = select(DataRegistry).where(DataRegistry.is_active)
        if hasattr(DataRegistry, "is_deleted"):
            query = query.where(not DataRegistry.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_classroom_details(self, registry_id: str) -> Optional[Classroom]:
        """获取班级详细信息（从子库）

        Args:
            registry_id: 班级索引ID

        Returns:
            Classroom对象或None
        """
        registry = self.get_by_id(registry_id)
        if not registry or not self.sub_session_factory:
            return None

        sub_session = self.sub_session_factory(registry.db_path)
        try:
            query = select(Classroom).where(Classroom.registry_uuid == registry.id)
            result = sub_session.exec(query)
            return result.first()
        finally:
            sub_session.close()

    def get_class_statistics(self, registry_id: str) -> dict[str, Any]:
        """获取班级统计信息

        Args:
            registry_id: 班级索引ID

        Returns:
            统计信息字典
        """
        registry = self.get_by_id(registry_id)
        if not registry:
            return {}

        # 从总库缓存获取基础统计
        stats = {
            "student_count": registry.student_count,
            "active_student_count": registry.active_student_count,
            "total_score": registry.total_score,
            "avg_score": registry.avg_score,
            "last_sync_at": registry.last_sync_at,
        }

        # 如果需要实时统计，可以查询子库
        if self.sub_session_factory and registry.db_path:
            sub_session = self.sub_session_factory(registry.db_path)
            try:
                # 这里可以添加实时统计查询逻辑
                # 例如：学生数量、成绩统计等
                pass
            finally:
                sub_session.close()

        return stats

    def update_statistics(self, registry_id: str, stats: dict[str, Any]) -> bool:
        """更新班级统计信息

        Args:
            registry_id: 班级索引ID
            stats: 统计数据

        Returns:
            更新是否成功
        """
        registry = self.get_by_id(registry_id)
        if not registry:
            return False

        # 更新统计字段
        update_fields = {
            "student_count": stats.get("student_count", registry.student_count),
            "active_student_count": stats.get("active_student_count", registry.active_student_count),
            "total_score": stats.get("total_score", registry.total_score),
            "avg_score": stats.get("avg_score", registry.avg_score),
            "last_sync_at": stats.get("last_sync_at"),
        }

        return self.update(registry_id, update_fields) is not None

    def get_classes_by_grade(self, grade: str) -> list[DataRegistry]:
        """根据年级获取班级列表

        Args:
            grade: 年级

        Returns:
            班级列表
        """
        query = select(DataRegistry).where(DataRegistry.grade == grade)
        if hasattr(DataRegistry, "is_deleted"):
            query = query.where(not DataRegistry.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def get_classes_by_school_year(self, school_year: str) -> list[DataRegistry]:
        """根据学年获取班级列表

        Args:
            school_year: 学年

        Returns:
            班级列表
        """
        query = select(DataRegistry).where(DataRegistry.school_year == school_year)
        if hasattr(DataRegistry, "is_deleted"):
            query = query.where(not DataRegistry.is_deleted)

        result = self.session.exec(query)
        return result.all()

    def create_class_database(self, registry_id: str, db_path: str) -> bool:
        """为班级创建子数据库

        Args:
            registry_id: 班级索引ID
            db_path: 数据库路径

        Returns:
            创建是否成功
        """
        registry = self.get_by_id(registry_id)
        if not registry:
            return False

        try:
            # 更新数据库路径
            registry.db_path = db_path
            self.session.add(registry)
            self.session.commit()

            # 这里可以添加创建数据库表结构的逻辑
            # 例如：调用数据库管理器创建子库

            return True
        except Exception:
            self.session.rollback()
            return False
