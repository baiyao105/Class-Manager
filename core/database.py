"""数据库管理器

提供数据库连接、初始化和会话管理
"""

from collections.abc import Generator
from pathlib import Path
from typing import Optional

from sqlmodel import Session, SQLModel, create_engine

from .models.base import *  # 导入所有模型以确保表创建


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, database_url: Optional[str] = None):
        if database_url is None:
            # 默认使用项目根目录下的SQLite数据库
            db_path = Path(__file__).parent.parent / "data" / "class_manager.db"
            db_path.parent.mkdir(exist_ok=True)
            database_url = f"sqlite:///{db_path}"

        self.engine = create_engine(
            database_url,
            echo=False,  # 设为True可以看到SQL语句
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
        )
        self._initialized = False

    def initialize_database(self):
        """初始化数据库, 创建所有表"""
        if not self._initialized:
            SQLModel.metadata.create_all(self.engine)
            self._initialized = True
            print("✅ 数据库初始化完成")

    def get_session(self) -> Generator[Session, None, None]:
        """获取数据库会话"""
        with Session(self.engine) as session:
            yield session

    def create_sample_data(self):
        """创建示例数据"""
        from .services import AchievementService, ClassService, StudentService

        with Session(self.engine) as session:
            class_service = ClassService(session)
            student_service = StudentService(session)
            achievement_service = AchievementService(session)

            # 检查是否已有数据
            if class_service.get_all_classes():
                print("📊 数据库已有数据, 跳过示例数据创建")
                return

            print("🌱 创建示例数据...")

            # 创建示例班级
            class1 = class_service.create_class("高三(1)班", "理科重点班", "张老师")
            class2 = class_service.create_class("高三(2)班", "文科重点班", "李老师")

            # 创建示例学生
            students = [
                student_service.create_student("张三", "2024001", class1.id, "zhangsan@school.edu"),
                student_service.create_student("李四", "2024002", class1.id, "lisi@school.edu"),
                student_service.create_student("王五", "2024003", class2.id, "wangwu@school.edu"),
                student_service.create_student("赵六", "2024004", class2.id, "zhaoliu@school.edu"),
            ]

            # 创建示例成就
            achievements = [
                achievement_service.create_achievement(
                    students[0].id, "数学竞赛一等奖", "在全国数学竞赛中获得一等奖", 100
                ),
                achievement_service.create_achievement(students[0].id, "优秀学生干部", "担任班长期间表现优秀", 50),
                achievement_service.create_achievement(
                    students[1].id, "英语演讲比赛冠军", "在校英语演讲比赛中获得冠军", 80
                ),
                achievement_service.create_achievement(students[2].id, "文学创作奖", "在校文学创作比赛中获奖", 60),
            ]

            print(
                f"✅ 示例数据创建完成：{len(class_service.get_all_classes())}个班级, {len(student_service.get_all_students())}名学生, {len(achievement_service.get_all_achievements())}项成就"
            )


# 全局数据库管理器实例
db_manager = DatabaseManager()
