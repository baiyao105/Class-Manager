"""数据库管理模块

仅管理子库（每班级独立数据库）：
- 子库会话工厂（按班级路径）
- 子库建表初始化（checkfirst）
- 旧版文件名迁移（class.db -> Class_{uuid}.db）
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict
from uuid import UUID, uuid4

from loguru import logger
from sqlmodel import Session, create_engine, select

from utils.basic_dirs import DATA, ensure_dirs
# 模型导入（子库）
from core.models.class_ import Classroom
from core.models.student import Student, StudentStatus
from core.models.score_template import ScoreTemplate
from core.models.score_record import ScoreRecord
from core.models.tag import Tag, StudentTagLink
from core.models.achievement import Achievement, AchievementTemplate


class DatabaseManager:
    """数据库管理器：仅管理子库（已移除主库逻辑）"""

    def __init__(self):
        ensure_dirs()
        self._sub_engines: Dict[str, any] = {}

    # 已移除主库相关接口：initialize_database、get_master_session

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

    # 已移除示例数据创建（主库依赖）

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