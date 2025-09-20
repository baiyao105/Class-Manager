"""数据库管理器

提供混合架构数据库连接、初始化和会话管理
支持总库（班级索引）+ 子库（班级数据）的架构
"""

from collections.abc import Generator
from pathlib import Path
from typing import Optional

from sqlmodel import Session, SQLModel, create_engine

from .models import *  # 导入所有模型以确保表创建


class DatabaseManager:
    """混合架构数据库管理器

    管理总库（班级索引）和多个子库（班级数据）的连接
    """

    def __init__(self, master_db_url: Optional[str] = None, data_dir: Optional[Path] = None):
        # 数据目录
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)

        # 总库连接（班级索引和统计）
        if master_db_url is None:
            master_db_path = self.data_dir / "master.db"
            master_db_url = f"sqlite:///{master_db_path}"

        self.master_engine = create_engine(
            master_db_url,
            echo=False,
            connect_args={"check_same_thread": False} if "sqlite" in master_db_url else {},
        )

        # 子库连接池（按班级UUID索引）
        self.sub_engines: dict[str, any] = {}
        self._initialized = False

    def initialize_database(self):
        """初始化数据库架构"""
        if not self._initialized:
            # 创建总库表结构
            from .models.base import MasterDBModel
            from .models.master import DataRegistry, DataStatistics

            # 只为总库模型创建表
            master_metadata = SQLModel.metadata
            master_tables = [
                table
                for table in master_metadata.tables.values()
                if any(isinstance(model(), MasterDBModel) for model in [DataRegistry, DataStatistics])
            ]

            master_metadata.create_all(self.master_engine, tables=master_tables)
            self._initialized = True
            print("✅ 总库初始化完成")

    def get_master_session(self) -> Generator[Session, None, None]:
        """获取总库会话"""
        with Session(self.master_engine) as session:
            yield session

    def get_sub_engine(self, class_uuid: str):
        """获取或创建子库引擎"""
        if class_uuid not in self.sub_engines:
            sub_db_path = self.data_dir / f"class_{class_uuid}.db"
            sub_db_url = f"sqlite:///{sub_db_path}"

            engine = create_engine(
                sub_db_url,
                echo=False,
                connect_args={"check_same_thread": False},
            )

            # 创建子库表结构
            sub_metadata = SQLModel.metadata
            sub_tables = [
                table
                for table in sub_metadata.tables.values()
                if table.name
                in ["classrooms", "students", "tags", "score_templates", "score_records", "student_tag_links"]
            ]

            sub_metadata.create_all(engine, tables=sub_tables)
            self.sub_engines[class_uuid] = engine
            print(f"✅ 子库 {class_uuid} 初始化完成")

        return self.sub_engines[class_uuid]

    def get_sub_session(self, class_uuid: str) -> Generator[Session, None, None]:
        """获取子库会话"""
        engine = self.get_sub_engine(class_uuid)
        with Session(engine) as session:
            yield session

    def create_sample_data(self):
        """创建混合架构示例数据"""
        from uuid import uuid4

        print("🌱 创建混合架构示例数据...")

        # 在总库中创建班级索引
        with next(self.get_master_session()) as master_session:
            from .models.master import DataRegistry

            # 检查是否已有数据
            existing = master_session.query(DataRegistry).first()
            if existing:
                print("📊 总库已有数据, 跳过示例数据创建")
                return

            # 创建班级索引
            class1_uuid = str(uuid4())
            class2_uuid = str(uuid4())

            registry1 = DataRegistry(
                class_name="高三(1)班",
                class_type="理科班",
                grade="高三",
                school_year="2024-2025",
                db_path=f"class_{class1_uuid}.db",
                db_name=f"class_{class1_uuid}",
                teacher_name="张老师",
                student_count=0,
                is_active=True,
            )
            registry2 = DataRegistry(
                class_name="高三(2)班",
                class_type="文科班",
                grade="高三",
                school_year="2024-2025",
                db_path=f"class_{class2_uuid}.db",
                db_name=f"class_{class2_uuid}",
                teacher_name="李老师",
                student_count=0,
                is_active=True,
            )

            master_session.add(registry1)
            master_session.add(registry2)
            master_session.commit()

            print("✅ 总库示例数据创建完成：2个班级索引")

            # 在子库中创建班级和学生数据
            self._create_class_data(class1_uuid, "高三(1)班", registry1.uuid)
            self._create_class_data(class2_uuid, "高三(2)班", registry2.uuid)

    def _create_class_data(self, class_uuid: str, class_name: str, registry_uuid):
        """在子库中创建班级数据"""
        with next(self.get_sub_session(class_uuid)) as sub_session:
            import uuid

            from .models.class_ import Classroom
            from .models.student import Student

            # 创建班级
            classroom = Classroom(
                registry_uuid=uuid.UUID(str(registry_uuid)),
                name=class_name,
                description=f"{class_name}的详细信息",
                class_type="高中班级",
                max_students=50,
                current_students=2,
            )
            sub_session.add(classroom)
            sub_session.commit()

            # 创建学生
            students = [
                Student(
                    registry_uuid=uuid.UUID(str(registry_uuid)),
                    name="张三" if "1" in class_name else "王五",
                    student_number=2024001 if "1" in class_name else 2024003,
                    classroom_id=classroom.id,
                    current_score=85.5,
                    total_score=85.5,
                ),
                Student(
                    registry_uuid=uuid.UUID(str(registry_uuid)),
                    name="李四" if "1" in class_name else "赵六",
                    student_number=2024002 if "1" in class_name else 2024004,
                    classroom_id=classroom.id,
                    current_score=92.0,
                    total_score=92.0,
                ),
            ]

            for student in students:
                sub_session.add(student)
            sub_session.commit()

            print(f"✅ 子库 {class_name} 示例数据创建完成：1个班级, 2名学生")

    def get_active_classes(self):
        """获取活跃班级列表 - 临时方法"""
        try:
            with next(self.get_master_session()) as session:
                from .models.master import DataRegistry
                from sqlmodel import select
                
                query = select(DataRegistry).where(DataRegistry.is_active == True)
                result = session.exec(query)
                return result.all()
        except Exception:
            return []  # 返回空列表避免崩溃

    def get_active_students(self, registry_uuid=None) -> list:
        """获取活跃学生 - 临时方法
        
        Returns:
            空列表（暂时移除统计功能）
        """
        return []


# 全局数据库管理器实例
db_manager = DatabaseManager()
