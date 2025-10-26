"""数据库管理模块

提供主库与子库的统一管理：
- 主库引擎/会话（索引与统计）
- 子库会话工厂（按班级路径）
- 初始化建表与示例数据
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict
from uuid import UUID, uuid4

from loguru import logger
from sqlmodel import Session, create_engine, select

from utils.basic_dirs import DATA, ensure_dirs

# 模型导入（主库）
from core.models.master import DataRegistry, DataStatistics
# 模型导入（子库）
from core.models.class_ import Classroom
from core.models.student import Student, StudentStatus
from core.models.score_template import ScoreTemplate
from core.models.score_record import ScoreRecord
from core.models.tag import Tag, StudentTagLink
from core.models.achievement import Achievement, AchievementTemplate


class DatabaseManager:
    """数据库管理器：统一管理主库与子库"""

    def __init__(self, master_db: Path | None = None):
        ensure_dirs()
        self.master_db_path = Path(master_db or DATA / "master.db").resolve()
        self.master_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.master_engine = create_engine(f"sqlite:///{self.master_db_path}", echo=False)
        self._sub_engines: Dict[str, any] = {}
        logger.debug(f"Master DB at: {self.master_db_path}")

    # ---------- 主库 ----------
    def initialize_database(self) -> None:
        """初始化主库表结构（仅主库模型）"""
        try:
            logger.info("Initializing master database tables...")
            # 仅创建主库模型表
            DataRegistry.__table__.create(self.master_engine, checkfirst=True)
            DataStatistics.__table__.create(self.master_engine, checkfirst=True)
            logger.info("Master database initialized.")
        except Exception as e:
            logger.error(f"Initialize master database failed: {e}")
            raise

    def get_master_session(self):
        """提供一个生成器样式的会话获取（与现有 main.py 兼容）"""
        session = Session(self.master_engine)
        try:
            yield session
        finally:
            # 交由调用方决定关闭时机
            pass

    # ---------- 子库 ----------
    def _ensure_sub_tables(self, engine) -> None:
        """在指定子库引擎上创建子库相关表（checkfirst）"""
        # 建表顺序尽量保证外键存在
        ScoreTemplate.__table__.create(engine, checkfirst=True)
        Classroom.__table__.create(engine, checkfirst=True)
        Student.__table__.create(engine, checkfirst=True)
        AchievementTemplate.__table__.create(engine, checkfirst=True)
        Achievement.__table__.create(engine, checkfirst=True)
        ScoreRecord.__table__.create(engine, checkfirst=True)
        Tag.__table__.create(engine, checkfirst=True)
        StudentTagLink.__table__.create(engine, checkfirst=True)

    def get_sub_session(self, db_path: str | Path) -> Session:
        """获取子库会话，必要时创建引擎与表

        Args:
            db_path: 子库数据库文件路径
        """
        p = Path(db_path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        key = str(p)
        engine = self._sub_engines.get(key)
        if engine is None:
            engine = create_engine(f"sqlite:///{p}", echo=False)
            self._ensure_sub_tables(engine)
            self._sub_engines[key] = engine
            logger.debug(f"Sub DB ready at: {p}")
        return Session(engine)

    # 新增：根据班级UUID获取规范化的子库路径与会话
    def get_class_db_path(self, class_uuid: str) -> Path:
        """返回规范化的每班级数据库文件路径: data/Class_{uuid}/Class_{uuid}.db"""
        base = DATA / f"Class_{class_uuid}"
        base.mkdir(parents=True, exist_ok=True)
        return base / f"Class_{class_uuid}.db"

    def get_sub_session_by_class_id(self, class_uuid: str) -> Session:
        """根据班级UUID获取子库会话，路径为 Class_{uuid}/Class_{uuid}.db"""
        return self.get_sub_session(self.get_class_db_path(class_uuid))

    # ---------- 示例数据 ----------
    def create_sample_data(self) -> None:
        """如主库为空，则创建一个示例班级与若干学生"""
        try:
            with Session(self.master_engine) as ms:
                count = ms.exec(select(DataRegistry)).all()
                if count:
                    logger.info("Master registry already has data. Skip sample creation.")
                    return

                # 创建一个示例班级
                cls_uuid = uuid4()
                class_dir = DATA / f"Class_{cls_uuid}"
                sub_db_path = class_dir / f"Class_{cls_uuid}.db"  # 统一命名
                registry = DataRegistry(
                    class_name="示例班级",
                    class_type="regular",
                    grade=None,
                    school_year=None,
                    db_path=str(sub_db_path.resolve()),
                    description="用于演示的数据",
                    is_active=True,
                )
                ms.add(registry)
                ms.commit()
                ms.refresh(registry)

                # 子库：创建 Classroom 与学生
                with self.get_sub_session(registry.db_path) as ss:
                    classroom = Classroom(registry_uuid=UUID(registry.uuid), base_score=100.0)
                    ss.add(classroom)
                    ss.commit()
                    ss.refresh(classroom)

                    # 三个示例学生
                    s1 = Student(
                        name="张三",
                        student_number=1001,
                        registry_uuid=UUID(registry.uuid),
                        classroom_id=classroom.id,
                        status=StudentStatus.ACTIVE,
                    )
                    s2 = Student(
                        name="李四",
                        student_number=1002,
                        registry_uuid=UUID(registry.uuid),
                        classroom_id=classroom.id,
                        status=StudentStatus.ACTIVE,
                    )
                    s3 = Student(
                        name="王五",
                        student_number=1003,
                        registry_uuid=UUID(registry.uuid),
                        classroom_id=classroom.id,
                        status=StudentStatus.ACTIVE,
                    )
                    ss.add(s1)
                    ss.add(s2)
                    ss.add(s3)
                    ss.commit()
                logger.info("Sample data created: 1 class, 3 students.")
        except Exception as e:
            logger.error(f"Create sample data failed: {e}")
            # 不抛出，避免阻断启动

    def migrate_legacy_db_name(self, class_uuid: str) -> Path | None:
        """将旧版子库文件名 class.db 迁移为 Class_{uuid}.db。
        
        返回迁移后的路径（或 None 表示不需要迁移）。
        """
        legacy = DATA / f"Class_{class_uuid}" / "class.db"
        target = self.get_class_db_path(class_uuid)
        try:
            if legacy.exists() and not target.exists():
                legacy.rename(target)
                logger.info(f"Legacy sub db renamed: {legacy} -> {target}")
                return target
        except Exception as e:
            logger.warning(f"迁移旧版子库文件名失败: {e}")
        return None

# 提供一个模块级单例，兼容现有 main.py 的导入方式
db_manager = DatabaseManager()