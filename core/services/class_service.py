"""班级管理服务层 - Repository模式重构

提供班级相关的业务逻辑操作，使用Repository模式进行数据访问
"""

import uuid
from typing import Any, Optional

from ..models.class_ import Classroom
from ..models.master import DataRegistry
from ..repositories.class_repository import ClassRepository


class ClassService:
    """班级服务类 - 使用Repository模式

    负责班级相关的业务逻辑，通过ClassRepository进行数据访问
    """

    def __init__(self, class_repository: ClassRepository):
        """初始化班级服务

        Args:
            class_repository: 班级仓储实例
        """
        self.class_repository = class_repository

    def create_class(
        self,
        name: str,
        description: Optional[str] = None,
        teacher_name: Optional[str] = None,
        teacher_contact: Optional[str] = None,
        class_type: str = "regular",
        grade: Optional[str] = None,
        school_year: Optional[str] = None,
    ) -> DataRegistry:
        """创建新班级

        Args:
            name: 班级名称
            description: 班级描述
            teacher_name: 班主任姓名
            teacher_contact: 班主任联系方式
            class_type: 班级类型
            grade: 年级
            school_year: 学年

        Returns:
            创建的班级索引对象

        Raises:
            ValueError: 当班级名称已存在时
        """
        # 检查班级名称是否已存在
        existing_class = self.class_repository.get_by_name(name)
        if existing_class:
            raise ValueError(f"班级名称 '{name}' 已存在")

        # 生成班级UUID和数据库路径
        class_uuid = uuid.uuid4()
        db_path = f"data/class_{class_uuid}.db"

        # 准备班级数据
        class_data = {
            "name": name,
            "description": description,
            "teacher_name": teacher_name or "待分配",
            "teacher_contact": teacher_contact,
            "class_type": class_type,
            "grade": grade or "未设置",
            "school_year": school_year or "2024-2025",
            "db_path": db_path,
        }

        # 通过Repository创建班级
        return self.class_repository.create(class_data)

    def get_class_by_id(self, class_id: str) -> Optional[DataRegistry]:
        """根据ID获取班级

        Args:
            class_id: 班级ID

        Returns:
            班级索引对象或None
        """
        return self.class_repository.get_by_id(class_id)

    def get_class_by_name(self, name: str) -> Optional[DataRegistry]:
        """根据名称获取班级

        Args:
            name: 班级名称

        Returns:
            班级索引对象或None
        """
        return self.class_repository.get_by_name(name)

    def get_all_classes(self, include_inactive: bool = False) -> list[DataRegistry]:
        """获取所有班级

        Args:
            include_inactive: 是否包含非活跃班级

        Returns:
            班级列表
        """
        if include_inactive:
            return self.class_repository.get_all()
        return self.class_repository.get_active_classes()

    def search_classes(self, query: str) -> list[DataRegistry]:
        """搜索班级

        Args:
            query: 搜索关键词

        Returns:
            匹配的班级列表
        """
        return self.class_repository.search_by_name(query)

    def update_class(
        self,
        class_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        teacher_name: Optional[str] = None,
        teacher_contact: Optional[str] = None,
        class_type: Optional[str] = None,
        grade: Optional[str] = None,
        school_year: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[DataRegistry]:
        """更新班级信息

        Args:
            class_id: 班级ID
            name: 新班级名称
            description: 新描述
            teacher_name: 新班主任姓名
            teacher_contact: 新班主任联系方式
            class_type: 新班级类型
            grade: 新年级
            school_year: 新学年
            is_active: 是否活跃

        Returns:
            更新后的班级对象或None

        Raises:
            ValueError: 当新班级名称已存在时
        """
        # 检查班级是否存在
        existing_class = self.class_repository.get_by_id(class_id)
        if not existing_class:
            return None

        # 如果要更新名称，检查新名称是否已被其他班级使用
        if name and name != existing_class.class_name:
            name_conflict = self.class_repository.get_by_name(name)
            if name_conflict and str(name_conflict.id) != class_id:
                raise ValueError(f"班级名称 '{name}' 已被其他班级使用")

        # 准备更新数据
        update_data = {}
        if name is not None:
            update_data["class_name"] = name
        if description is not None:
            update_data["description"] = description
        if teacher_name is not None:
            update_data["teacher_name"] = teacher_name
        if teacher_contact is not None:
            update_data["teacher_contact"] = teacher_contact
        if class_type is not None:
            update_data["class_type"] = class_type
        if grade is not None:
            update_data["grade"] = grade
        if school_year is not None:
            update_data["school_year"] = school_year
        if is_active is not None:
            update_data["is_active"] = is_active

        # 执行更新
        return self.class_repository.update(class_id, update_data)

    def delete_class(self, class_id: str, soft_delete: bool = True) -> bool:
        """删除班级

        Args:
            class_id: 班级ID
            soft_delete: 是否软删除

        Returns:
            删除是否成功
        """
        return self.class_repository.delete(class_id, soft_delete)

    def activate_class(self, class_id: str) -> bool:
        """激活班级

        Args:
            class_id: 班级ID

        Returns:
            激活是否成功
        """
        result = self.class_repository.update(class_id, {"is_active": True})
        return result is not None

    def deactivate_class(self, class_id: str) -> bool:
        """停用班级

        Args:
            class_id: 班级ID

        Returns:
            停用是否成功
        """
        result = self.class_repository.update(class_id, {"is_active": False})
        return result is not None

    def get_class_details(self, class_id: str) -> Optional[Classroom]:
        """获取班级详细信息（从子库）

        Args:
            class_id: 班级ID

        Returns:
            班级详细信息或None
        """
        return self.class_repository.get_classroom_details(class_id)

    def get_class_stats(self) -> dict[str, Any]:
        """获取班级统计信息
        
        Returns:
            包含班级统计信息的字典
        """
        try:
            all_classes = self.get_all_classes()
            total_classes = len(all_classes)
            
            # 计算其他统计信息
            active_classes = sum(1 for cls in all_classes if cls.is_active)
            
            return {
                "total_classes": total_classes,
                "active_classes": active_classes,
                "inactive_classes": total_classes - active_classes,
            }
        except Exception as e:
            print(f"获取班级统计失败: {e}")
            return {
                "total_classes": 0,
                "active_classes": 0,
                "inactive_classes": 0,
            }

    def get_class_statistics(self, class_id: str) -> dict[str, Any]:
        """获取班级统计信息

        Args:
            class_id: 班级ID

        Returns:
            统计信息字典
        """
        return self.class_repository.get_class_statistics(class_id)

    def update_class_statistics(self, class_id: str, stats: dict[str, Any]) -> bool:
        """更新班级统计信息

        Args:
            class_id: 班级ID
            stats: 统计数据

        Returns:
            更新是否成功
        """
        return self.class_repository.update_statistics(class_id, stats)

    def get_classes_by_grade(self, grade: str) -> list[DataRegistry]:
        """根据年级获取班级列表

        Args:
            grade: 年级

        Returns:
            班级列表
        """
        return self.class_repository.get_classes_by_grade(grade)

    def get_classes_by_school_year(self, school_year: str) -> list[DataRegistry]:
        """根据学年获取班级列表

        Args:
            school_year: 学年

        Returns:
            班级列表
        """
        return self.class_repository.get_classes_by_school_year(school_year)

    def create_class_database(self, class_id: str, db_path: str) -> bool:
        """为班级创建数据库

        Args:
            class_id: 班级ID
            db_path: 数据库路径

        Returns:
            创建是否成功
        """
        return self.class_repository.create_class_database(class_id, db_path)
