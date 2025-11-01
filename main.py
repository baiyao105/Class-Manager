"""班级管理系统主入口

现代化的班级管理系统, 基于Rinui框架和PySide6构建
"""

import sys
import time
from pathlib import Path
import uuid
import shutil

from loguru import logger
from PySide6.QtCore import Property, QObject, QSize, Signal, Slot
from PySide6.QtQml import qmlRegisterType
from PySide6.QtWidgets import QApplication
from RinUI import RinUIWindow

from config.class_config import ClassConfigManager
from config.global_config import GlobalConfigManager
from config.constants import APP_DESCRIPTION, APP_NAME, APP_VERSION
from core.models.achievement import Achievement
from core.database import db_manager
from core.models.student import Student, StudentStatus
from utils.basic_dirs import DATA, ensure_dirs

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"{APP_NAME}_{time.strftime('%Y%m%d_%H%M%S')}.log"
logger.add(
    str(log_file),
    retention=5,
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
)


class ClassManagerController(QObject):
    """班级管理系统控制器"""

    # 信号定义
    statsChanged = Signal()
    studentsChanged = Signal()
    classesChanged = Signal()
    achievementsChanged = Signal()
    scoresChanged = Signal()
    creditsChanged = Signal()

    def __init__(self):
        super().__init__()

        # 内存数据
        self._stats = {"total_students": 0, "total_classes": 0, "total_achievements": 0, "avg_score": 0}
        self._students = []
        self._classes = []
        self._achievements = []
        self._scores = []
        self._credits = []

        # 启动目录与默认班级
        ensure_dirs()
        self._current_class_id = self._select_default_class()

        # 不使用文件存储，数据来源统一为数据库

        # 加载数据
        self._load_data()

    def _select_default_class(self) -> str:
        """选择默认班级：优先使用全局配置；若不存在则创建一个演示班级"""
        try:
            default_id = GlobalConfigManager.get_setting("custom_settings.default_class_id", None)
            # 已配置且存在
            if isinstance(default_id, str):
                d = DATA / f"Class_{default_id}"
                if d.exists():
                    return default_id
            # 扫描已有班级
            ids = self._scan_class_ids()
            if ids:
                GlobalConfigManager.update_setting("custom_settings.default_class_id", ids[0])
                return ids[0]
            # 无班级 -> 创建演示班级
            new_id = str(uuid.uuid4())
            ClassConfigManager.create_config(new_id, class_name="演示班级", teacher_name="未设置")
            GlobalConfigManager.update_setting("custom_settings.default_class_id", new_id)
            return new_id
        except Exception as e:
            print(f"⚠️ 选择默认班级失败: {e}")
            # 兜底：仍然创建一个
            new_id = str(uuid.uuid4())
            ClassConfigManager.create_config(new_id, class_name="演示班级", teacher_name="未设置")
            GlobalConfigManager.update_setting("custom_settings.default_class_id", new_id)
            return new_id

    def _scan_class_ids(self) -> list[str]:
        """扫描 DATA 目录，返回所有有效的班级ID"""
        result: list[str] = []
        try:
            base = DATA
            if not base.exists():
                return result
            for p in base.iterdir():
                if p.is_dir() and p.name.startswith("Class_"):
                    cid = p.name.replace("Class_", "", 1)
                    if (p / "config.json").exists():
                        result.append(cid)
        except Exception as e:
            print(f"⚠️ 扫描班级目录失败: {e}")
        return result

    

    def _achievement_to_dict(self, achievement: Achievement) -> dict:
        """将数据库成就对象转换为字典（QML友好）"""
        tpl = getattr(achievement, "template", None)
        title = getattr(tpl, "name", "") if tpl is not None else ""
        desc = getattr(achievement, "notes", None) or (getattr(tpl, "description", "") if tpl is not None else "")
        pts = getattr(tpl, "reward_score", 0.0) if tpl is not None else 0.0
        try:
            pts = round(float(pts), 2)
        except Exception:
            pts = 0
        dt = getattr(achievement, "achieved_at", None)
        if dt is not None:
            try:
                created_at = dt.strftime("%Y-%m-%d")
            except Exception:
                created_at = str(dt)
        else:
            created_at = ""
        return {
            "id": getattr(achievement, "id", None),
            "student_id": getattr(achievement, "student_id", None),
            "title": title,
            "description": desc,
            "points": pts,
            "created_at": created_at,
        }

    def _compute_students_and_stats(self) -> None:
        """聚合所有班级的学生/成就数据，并计算统计值（学生优先从子库读取）"""
        class_ids = self._scan_class_ids()
        classes_list: list[dict] = []
        students_list: list[dict] = []
        achievements_list: list[dict] = []
        total_students = 0
        total_achievements = 0
        total_points = 0
        credits_map: dict[str, int] = {}

        for cid in class_ids:
            cfg = ClassConfigManager.get_config(cid)
            # 从子库读取成就（仅数据库，不使用文件存储）
            achievements = []
            try:
                with db_manager.get_sub_session_by_class_id(cid) as ss:
                    try:
                        from sqlmodel import select
                        achievements = ss.exec(
                            select(Achievement).where(Achievement.is_deleted == False)
                        ).all()
                    except Exception:
                        try:
                            achievements = (
                                ss.query(Achievement)
                                .filter(Achievement.is_deleted == False)
                                .all()
                            )
                        except Exception:
                            achievements = ss.query(Achievement).all()
            except Exception as e:
                logger.warning(f"⚠️ 读取子库成就失败（忽略）: {e}")

            # 成就统计（积分不再通过成就累加）
            for a in achievements:
                total_achievements += 1
                points = getattr(getattr(a, "template", None), "reward_score", 0) or 0
                try:
                    points = float(points)
                except Exception:
                    points = 0.0
                total_points += points

            # 积分汇总：读取子库 ScoreRecord 中已应用(APPLIED)且未软删除的记录
            try:
                from core.models.score_record import ScoreRecord, RecordStatus
            except Exception:
                ScoreRecord = None
                RecordStatus = None
            try:
                with db_manager.get_sub_session_by_class_id(cid) as ss:
                    records = []
                    try:
                        from sqlmodel import select
                        if ScoreRecord:
                            # 统一过滤：只统计未软删除且状态为 APPLIED 的记录
                            records = ss.exec(
                                select(ScoreRecord).where(
                                    ScoreRecord.is_deleted == False,
                                    ScoreRecord.status == RecordStatus.APPLIED,
                                )
                            ).all()
                    except Exception:
                        if ScoreRecord:
                            # 兼容不同 ORM：降级查询并至少过滤未软删除
                            try:
                                records = (
                                    ss.query(ScoreRecord)
                                    .filter(ScoreRecord.is_deleted == False)
                                    .all()
                                )
                            except Exception:
                                records = ss.query(ScoreRecord).all()
                    for r in records:
                        status = str(getattr(r, "status", ""))
                        applied_flag = False
                        try:
                            applied_flag = (status == str(RecordStatus.APPLIED))
                        except Exception:
                            # 不同ORM类型时直接字符串比较
                            applied_flag = (status.endswith("APPLIED"))
                        if not applied_flag:
                            continue
                        # 统一过滤：忽略已软删除的记录
                        if getattr(r, "is_deleted", False):
                            continue
                        sid_val = getattr(r, "student_id", None)
                        if sid_val is None:
                            continue
                        v = getattr(r, "final_score", None)
                        if v is None:
                            v = getattr(r, "score_value", 0) or 0
                        try:
                            v = round(float(v), 2)
                        except Exception:
                            v = 0
                        key = str(sid_val)
                        credits_map[key] = credits_map.get(key, 0) + v
            except Exception as e:
                logger.warning(f"⚠️ 读取子库积分记录失败（忽略）: {e}")

            # 读取学生（仅子库）
            student_count = 0
            try:
                with db_manager.get_sub_session_by_class_id(cid) as ss:
                    try:
                        from sqlmodel import select
                        db_students = ss.exec(select(Student)).all()
                    except Exception:
                        db_students = ss.query(Student).all()
                    student_count = len(db_students)

                    for s in db_students:
                        s_num = getattr(s, "student_number", None)
                        sid_str = str(s_num) if s_num is not None else str(getattr(s, "id", ""))
                        students_list.append({
                            "id": sid_str,
                            "uuid": str(getattr(s, "uuid", "")),
                            "name": getattr(s, "name", ""),
                            "student_id": sid_str,
                            "class_id": cid,
                            "class_name": cfg.class_name,
                            "className": cfg.class_name,
                            "is_active": getattr(s, "status", None) == StudentStatus.ACTIVE,
                            "created_at": str(getattr(s, "created_at", "")),
                            "credits": int(credits_map.get(str(getattr(s, "id", "")), 0)),
                        })
                        total_students += 1
            except Exception as db_e:
                logger.warning(f"⚠️ 读取子库学生失败（忽略）: {db_e}")

            # 班级统计
            class_points = 0.0
            for a in achievements:
                p = getattr(getattr(a, "template", None), "reward_score", 0) or 0
                try:
                    p = float(p)
                except Exception:
                    p = 0.0
                class_points += p
            class_avg = round(class_points / len(achievements), 2) if achievements else 0.0
            classes_list.append({
                "id": cid,
                "value": cid,                 # ComboBox.currentValue 兼容
                "name": cfg.class_name,
                "description": cfg.description or "",
                "is_active": cfg.is_active,
                "studentCount": student_count,
                "avgScore": class_avg,
            })

            # 成就映射
            achievements_list.extend([self._achievement_to_dict(a) for a in achievements])

        avg_overall = round(total_points / total_achievements, 2) if total_achievements else 0.0
        self._stats = {
            "total_students": total_students,
            "total_classes": len(class_ids),
            "total_achievements": total_achievements,
            "avg_score": avg_overall,
        }
        self._classes = classes_list
        self._students_all = students_list[:]  # 保留一份未过滤的副本
        self._students = students_list
        self._achievements = achievements_list

    def _compute_scores(self) -> None:
        """聚合所有班级的评分记录，映射为QML友好结构"""
        from core.models.score_record import ScoreRecord
        score_items: list[dict] = []
        class_ids = self._scan_class_ids()

        category_map = {
            "academic": "考试成绩",
            "homework": "作业成绩",
            "participation": "课堂表现",
            "behavior": "平时成绩",
            "attendance": "出勤",
            "discipline": "纪律",
            "teamwork": "团队协作",
            "leadership": "领导力",
            "creativity": "创造力",
            "custom": "其他",
        }

        for cid in class_ids:
            cfg = ClassConfigManager.get_config(cid)
            try:
                with db_manager.get_sub_session_by_class_id(cid) as ss:
                    try:
                        from sqlmodel import select
                        records = ss.exec(select(ScoreRecord)).all()
                    except Exception:
                        records = ss.query(ScoreRecord).all()

                    student_name_cache: dict[int, str] = {}

                    for r in records:
                        s_name = None
                        try:
                            sid = getattr(r, "student_id", None)
                            if sid is not None:
                                if sid in student_name_cache:
                                    s_name = student_name_cache[sid]
                                else:
                                    s_obj = None
                                    try:
                                        s_obj = ss.get(Student, sid)
                                    except Exception:
                                        try:
                                            from sqlmodel import select as _select
                                            s_obj = ss.exec(_select(Student).where(Student.id == sid)).first()
                                        except Exception:
                                            s_obj = ss.query(Student).filter(Student.id == sid).first()
                                    s_name = getattr(s_obj, "name", None) if s_obj is not None else None
                                    if s_name:
                                        student_name_cache[sid] = s_name
                        except Exception:
                            s_name = None

                        score_val = (
                            getattr(r, "final_score", None)
                            if getattr(r, "final_score", None) is not None
                            else getattr(r, "score_value", None)
                        )
                        if score_val is None:
                            score_val = getattr(r, "original_score", 0) or 0
                        try:
                            score_val = round(float(score_val), 2)
                        except Exception:
                            score_val = 0

                        dt = getattr(r, "occurred_at", None) or getattr(r, "recorded_at", None) or getattr(r, "applied_at", None)
                        if dt is not None:
                            try:
                                date_str = dt.strftime("%Y-%m-%d")
                            except Exception:
                                date_str = str(dt)
                        else:
                            date_str = ""

                        subject = getattr(r, "subcategory", None) or "综合"
                        cat = str(getattr(r, "category", "") or "").lower()
                        exam_type = category_map.get(cat, "其他")

                        score_items.append({
                            "id": getattr(r, "id", None),
                            "uuid": str(getattr(r, "uuid", "")),
                            "studentId": getattr(r, "student_id", None),
                            "studentName": s_name or "",
                            "classId": cid,
                            "className": cfg.class_name,
                            "subject": subject,
                            "examType": exam_type,
                            "score": score_val,
                            "date": date_str,
                            "note": getattr(r, "description", None) or getattr(r, "reason", None) or "",
                        })
            except Exception as e:
                logger.warning(f"⚠️ 读取班级({cid})评分记录失败（忽略）: {e}")
                continue

        self._scores = score_items

    def _compute_credits(self) -> None:
        """聚合所有班级的积分记录（ScoreRecord），映射为 QML 友好结构"""
        from core.models.score_record import ScoreRecord, RecordStatus
        credit_items: list[dict] = []
        class_ids = self._scan_class_ids()

        for cid in class_ids:
            cfg = ClassConfigManager.get_config(cid)
            try:
                with db_manager.get_sub_session_by_class_id(cid) as ss:
                    try:
                        from sqlmodel import select
                        # 统一过滤：仅加载未软删除的记录
                        records = ss.exec(
                            select(ScoreRecord).where(ScoreRecord.is_deleted == False)
                        ).all()
                    except Exception:
                        try:
                            records = (
                                ss.query(ScoreRecord)
                                .filter(ScoreRecord.is_deleted == False)
                                .all()
                            )
                        except Exception:
                            records = ss.query(ScoreRecord).all()

                    student_name_cache: dict[int, str] = {}

                    for r in records:
                        # 学生姓名缓存查找
                        s_name = None
                        try:
                            sid = getattr(r, "student_id", None)
                            if sid is not None:
                                if sid in student_name_cache:
                                    s_name = student_name_cache[sid]
                                else:
                                    s_obj = None
                                    try:
                                        s_obj = ss.get(Student, sid)
                                    except Exception:
                                        try:
                                            from sqlmodel import select as _select
                                            s_obj = ss.exec(_select(Student).where(Student.id == sid)).first()
                                        except Exception:
                                            s_obj = ss.query(Student).filter(Student.id == sid).first()
                                    s_name = getattr(s_obj, "name", None) if s_obj is not None else None
                                    if s_name:
                                        student_name_cache[sid] = s_name
                        except Exception:
                            s_name = None

                        # 计算积分值
                        val = (
                            getattr(r, "final_score", None)
                            if getattr(r, "final_score", None) is not None
                            else getattr(r, "score_value", None)
                        )
                        if val is None:
                            val = getattr(r, "original_score", 0) or 0
                        try:
                            val = round(float(val), 2)
                        except Exception:
                            val = 0

                        # 时间格式化
                        dt = getattr(r, "occurred_at", None) or getattr(r, "recorded_at", None) or getattr(r, "applied_at", None)
                        if dt is not None:
                            try:
                                date_str = dt.strftime("%Y-%m-%d")
                            except Exception:
                                date_str = str(dt)
                        else:
                            date_str = ""

                        credit_items.append({
                            "id": getattr(r, "id", None),
                            "studentId": getattr(r, "student_id", None),
                            "studentName": s_name or "",
                            "classId": cid,
                            "className": cfg.class_name,
                            "category": getattr(r, "category", "") or "",
                            "subcategory": getattr(r, "subcategory", "") or "",
                            "title": getattr(r, "title", "") or "",
                            "description": getattr(r, "description", "") or getattr(r, "reason", "") or "",
                            "points": val,
                            "status": str(getattr(r, "status", RecordStatus.PENDING)),
                            "date": date_str,
                        })
            except Exception as e:
                logger.warning(f"⚠️ 读取班级({cid})积分记录失败（忽略）: {e}")
                continue

        self._credits = credit_items

    def _load_data(self):
        """加载数据（文件存储版）"""
        try:
            self._compute_students_and_stats()
            self._compute_scores()
            # 刷新积分列表以保持前端一致
            self._compute_credits()
            self.statsChanged.emit()
            self.studentsChanged.emit()
            self.classesChanged.emit()
            self.achievementsChanged.emit()
            self.scoresChanged.emit()
            self.creditsChanged.emit()
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")

    # 已替换为文件存储版映射方法：_map_student_record、_achievement_to_dict


    # 属性定义
    @Property("QVariant", notify=statsChanged)
    def stats(self):
        return self._stats

    @Property("QVariant", notify=studentsChanged)
    def students(self):
        return self._students

    @Property("QVariant", notify=classesChanged)
    def classes(self):
        return self._classes

    @Property("QVariant", notify=achievementsChanged)
    def achievements(self):
        return self._achievements

    @Property("QVariant", notify=scoresChanged)
    def scores(self):
        return self._scores

    @Property("QVariant", notify=creditsChanged)
    def credits(self):
        return self._credits

    @Property(int, notify=statsChanged)
    def totalStudents(self):
        return int(self._stats.get("total_students", 0))

    @Property(int, notify=statsChanged)
    def totalClasses(self):
        return int(self._stats.get("total_classes", 0))

    @Property(int, notify=classesChanged)
    def activeClasses(self):
        try:
            return sum(1 for c in (self._classes or []) if c.get("is_active"))
        except Exception:
            return 0

    @Property(str, constant=True)
    def appName(self):
        return APP_NAME

    @Property(str, constant=True)
    def appVersion(self):
        return APP_VERSION

    @Property(str, constant=True)
    def appDescription(self):
        return APP_DESCRIPTION

    # 槽函数定义
    @Slot()
    def refreshStats(self):
        """刷新统计数据"""
        try:
            self._compute_students_and_stats()
            # 刷新积分列表以保持前端一致
            self._compute_credits()
            self.statsChanged.emit()
            self.studentsChanged.emit()
            self.classesChanged.emit()
            self.achievementsChanged.emit()
            self.creditsChanged.emit()
            print("✅ 统计已刷新")
        except Exception as e:
            print(f"❌ 刷新统计失败: {e}")

    @Slot()
    def refreshScores(self):
        try:
            self._compute_scores()
            self.scoresChanged.emit()
            print("✅ 成绩列表已刷新")
        except Exception as e:
            print(f"❌ 刷新成绩失败: {e}")

    @Slot()
    def refreshCredits(self):
        try:
            self._compute_credits()
            self.creditsChanged.emit()
            print("✅ 积分列表已刷新")
        except Exception as e:
            print(f"❌ 刷新积分失败: {e}")

    def _resolve_student_pk(self, ss, student_ident):
        """解析学生主键ID（支持 student_number 或 主键ID）"""
        try:
            from sqlmodel import select
        except Exception:
            select = None
        try:
            if student_ident is None:
                return None
            s_val = str(student_ident)
            # 优先按学号
            if s_val.isdigit():
                num = int(s_val)
                try:
                    if select:
                        stu = ss.exec(select(Student).where(Student.student_number == num)).first()
                    else:
                        stu = ss.query(Student).filter(Student.student_number == num).first()
                except Exception:
                    stu = ss.query(Student).filter(Student.student_number == num).first()
                if stu:
                    return int(getattr(stu, "id"))
                # 如果没有匹配学号，当作主键ID
                return num
            else:
                # 非纯数字，尝试作为主键ID
                try:
                    return int(s_val)
                except Exception:
                    return None
        except Exception:
            return None

    @Slot("QVariant")
    def addCreditRecord(self, data):
        """新增积分记录（写入子库 ScoreRecord）
        data 字段示例：{
          classId, studentId|studentNumber, points, title, description, category, subcategory, occurredAt, recorder
        }
        """
        try:
            from datetime import datetime
            from core.models.score_record import ScoreRecord, RecordStatus, RecordSource

            class_id = str(data.get("classId") or self._current_class_id)
            if not class_id:
                print("❌ 未选择班级")
                return
            with db_manager.get_sub_session_by_class_id(class_id) as ss:
                # 解析学生主键
                student_ident = data.get("studentId") or data.get("studentNumber")
                student_pk = self._resolve_student_pk(ss, student_ident)
                if student_pk is None:
                    print("❌ 找不到学生，无法新增积分记录")
                    return

                # 规范化分值
                pts = data.get("points")
                try:
                    pts = round(float(pts or 0), 2)
                except Exception:
                    pts = 0.0

                # 发生时间
                occurred_at = data.get("occurredAt")
                if isinstance(occurred_at, str) and occurred_at:
                    try:
                        occurred_dt = datetime.strptime(occurred_at[:19], "%Y-%m-%d%H:%M:%S")
                    except Exception:
                        try:
                            occurred_dt = datetime.strptime(occurred_at[:10], "%Y-%m-%d")
                        except Exception:
                            occurred_dt = datetime.now()
                elif isinstance(occurred_at, datetime):
                    occurred_dt = occurred_at
                else:
                    occurred_dt = datetime.now()

                record = ScoreRecord(
                    student_id=int(student_pk),
                    template_id=None,
                    score_value=pts,
                    original_score=None,
                    final_score=pts,
                    title=str(data.get("title") or "积分调整"),
                    description=(data.get("description") or None),
                    reason=None,
                    category=str(data.get("category") or "custom"),
                    subcategory=(data.get("subcategory") or None),
                    tags=None,
                    status=RecordStatus.PENDING,
                    source=RecordSource.MANUAL,
                    occurred_at=occurred_dt,
                    recorded_at=datetime.now(),
                    applied_at=None,
                    recorder=str(data.get("recorder") or "system"),
                    approver=None,
                    approval_note=None,
                    rejection_reason=None,
                    related_record_id=None,
                    batch_id=None,
                    metadata_json=None,
                    attachments=None,
                    view_count=0,
                )
                ss.add(record)
                ss.commit()
                print(f"✅ 积分记录已新增: 学生ID={student_pk}, 分值={pts}")

            # 刷新内存数据
            self._compute_credits()
            self.creditsChanged.emit()
        except Exception as e:
            print(f"❌ 新增积分记录失败: {e}")

    @Slot("QVariant")
    def editCreditRecord(self, data):
        """编辑积分记录（仅在可修改状态下）
        data: { id, classId, title?, description?, category?, subcategory?, points?, occurredAt? }
        """
        try:
            from datetime import datetime
            from core.models.score_record import ScoreRecord
            class_id = str(data.get("classId") or self._current_class_id)
            rec_id = data.get("id")
            if not class_id or rec_id is None:
                print("❌ 编辑积分记录缺少参数")
                return
            with db_manager.get_sub_session_by_class_id(class_id) as ss:
                obj = None
                try:
                    obj = ss.get(ScoreRecord, int(rec_id))
                except Exception:
                    try:
                        from sqlmodel import select
                        obj = ss.exec(select(ScoreRecord).where(ScoreRecord.id == int(rec_id))).first()
                    except Exception:
                        obj = ss.query(ScoreRecord).filter(ScoreRecord.id == int(rec_id)).first()
                if obj is None:
                    print("❌ 记录不存在")
                    return
                if not obj.can_be_modified():
                    print("❌ 当前状态不允许修改")
                    return
                # 更新字段
                if "title" in data:
                    obj.title = str(data.get("title") or obj.title)
                if "description" in data:
                    v = data.get("description")
                    obj.description = v if v is not None else obj.description
                if "category" in data:
                    obj.category = str(data.get("category") or obj.category)
                if "subcategory" in data:
                    v = data.get("subcategory")
                    obj.subcategory = v if v is not None else obj.subcategory
                if "points" in data:
                    try:
                        pts = round(float(data.get("points")), 2)
                        obj.score_value = pts
                        obj.final_score = pts
                    except Exception:
                        pass
                if "occurredAt" in data:
                    v = data.get("occurredAt")
                    if isinstance(v, str) and v:
                        try:
                            obj.occurred_at = datetime.strptime(v[:19], "%Y-%m-%d%H:%M:%S")
                        except Exception:
                            try:
                                obj.occurred_at = datetime.strptime(v[:10], "%Y-%m-%d")
                            except Exception:
                                pass
                obj.update_timestamp()
                ss.add(obj)
                ss.commit()
                print("✅ 积分记录已更新")
            self._compute_credits()
            self.creditsChanged.emit()
        except Exception as e:
            print(f"❌ 编辑积分记录失败: {e}")

    @Slot("QVariant")
    def deleteCreditRecord(self, data):
        """删除积分记录（仅在可修改状态下）
        data: { id, classId }
        """
        try:
            from core.models.score_record import ScoreRecord
            class_id = str(data.get("classId") or self._current_class_id)
            rec_id = data.get("id")
            if not class_id or rec_id is None:
                print("❌ 删除积分记录缺少参数")
                return
            with db_manager.get_sub_session_by_class_id(class_id) as ss:
                obj = None
                try:
                    obj = ss.get(ScoreRecord, int(rec_id))
                except Exception:
                    try:
                        from sqlmodel import select
                        obj = ss.exec(select(ScoreRecord).where(ScoreRecord.id == int(rec_id))).first()
                    except Exception:
                        obj = ss.query(ScoreRecord).filter(ScoreRecord.id == int(rec_id)).first()
                if obj is None:
                    print("⚠️ 记录不存在")
                    return
                if not obj.can_be_modified():
                    print("❌ 当前状态不允许删除")
                    return
                # 统一删除策略：软删除而不是物理删除
                try:
                    obj.soft_delete()
                    ss.add(obj)
                except Exception:
                    # 兼容没有混入方法的情况，直接标记字段
                    setattr(obj, "is_deleted", True)
                    ss.add(obj)
                ss.commit()
                print("✅ 积分记录已软删除")
            self._compute_credits()
            self.creditsChanged.emit()
        except Exception as e:
            print(f"❌ 删除积分记录失败: {e}")

    @Slot(int, "QVariant", str, "QVariant")
    def approveCreditRecord(self, recordId, classId, approver, note):
        """审核通过积分记录"""
        try:
            from core.models.score_record import ScoreRecord
            class_id = str(classId or self._current_class_id)
            if not class_id:
                print("❌ 未选择班级")
                return
            with db_manager.get_sub_session_by_class_id(class_id) as ss:
                obj = None
                try:
                    obj = ss.get(ScoreRecord, int(recordId))
                except Exception:
                    try:
                        from sqlmodel import select
                        obj = ss.exec(select(ScoreRecord).where(ScoreRecord.id == int(recordId))).first()
                    except Exception:
                        obj = ss.query(ScoreRecord).filter(ScoreRecord.id == int(recordId)).first()
                if obj is None:
                    print("⚠️ 记录不存在")
                    return
                from core.models.score_record import RecordStatus
                if not obj.can_be_approved():
                    print("❌ 当前状态不允许审核")
                    return
                obj.approve(str(approver or "approver"), note if note is not None else None)
                ss.add(obj)
                ss.commit()
                print("✅ 已审核通过")
            self._compute_credits()
            self.creditsChanged.emit()
        except Exception as e:
            print(f"❌ 审核通过失败: {e}")

    @Slot(int, "QVariant", str)
    def rejectCreditRecord(self, recordId, classId, reason):
        """审核拒绝积分记录"""
        try:
            from core.models.score_record import ScoreRecord
            class_id = str(classId or self._current_class_id)
            if not class_id:
                print("❌ 未选择班级")
                return
            with db_manager.get_sub_session_by_class_id(class_id) as ss:
                obj = None
                try:
                    obj = ss.get(ScoreRecord, int(recordId))
                except Exception:
                    try:
                        from sqlmodel import select
                        obj = ss.exec(select(ScoreRecord).where(ScoreRecord.id == int(recordId))).first()
                    except Exception:
                        obj = ss.query(ScoreRecord).filter(ScoreRecord.id == int(recordId)).first()
                if obj is None:
                    print("⚠️ 记录不存在")
                    return
                if not obj.can_be_approved():
                    print("❌ 当前状态不允许审核拒绝")
                    return
                obj.reject(str("approver"), str(reason or ""))
                ss.add(obj)
                ss.commit()
                print("✅ 已审核拒绝")
            self._compute_credits()
            self.creditsChanged.emit()
        except Exception as e:
            print(f"❌ 审核拒绝失败: {e}")

    @Slot(int, "QVariant")
    def applyCreditRecord(self, recordId, classId):
        """应用积分记录（会同步更新学生当前分数）"""
        try:
            from core.models.score_record import ScoreRecord
            class_id = str(classId or self._current_class_id)
            if not class_id:
                print("❌ 未选择班级")
                return
            with db_manager.get_sub_session_by_class_id(class_id) as ss:
                obj = None
                try:
                    obj = ss.get(ScoreRecord, int(recordId))
                except Exception:
                    try:
                        from sqlmodel import select
                        obj = ss.exec(select(ScoreRecord).where(ScoreRecord.id == int(recordId))).first()
                    except Exception:
                        obj = ss.query(ScoreRecord).filter(ScoreRecord.id == int(recordId)).first()
                if obj is None:
                    print("⚠️ 记录不存在")
                    return
                if not obj.can_be_applied():
                    print("❌ 当前状态不允许应用")
                    return
                # 应用积分记录
                obj.apply_score()
                ss.add(obj)
                # 同步更新学生当前分数
                try:
                    stu = ss.get(Student, int(obj.student_id))
                except Exception:
                    stu = None
                if stu is not None:
                    val = obj.final_score if obj.final_score is not None else obj.score_value
                    try:
                        change = round(float(val or 0), 2)
                    except Exception:
                        change = 0.0
                    stu.add_score(change, reason=obj.title or "积分调整")
                    ss.add(stu)
                ss.commit()
                print("✅ 积分记录已应用，并同步学生分数")
            # 刷新汇总与积分列表
            self._compute_students_and_stats()
            self._compute_credits()
            self.studentsChanged.emit()
            self.statsChanged.emit()
            self.creditsChanged.emit()
        except Exception as e:
            print(f"❌ 应用积分记录失败: {e}")

    @Slot(str, str, "QVariant")
    def addStudent(self, name, studentNumber, registryId):
        """添加学生（仅数据库）"""
        try:
            class_id = str(registryId) if registryId is not None else self._current_class_id
            if not class_id:
                print("❌ 未选择班级")
                return
            if not str(studentNumber).isdigit():
                print("❌ 学号必须为数字")
                return
            student_num = int(studentNumber)
            cfg = ClassConfigManager.get_config(class_id)
            from uuid import UUID
            registry_uuid = UUID(class_id)
            with db_manager.get_sub_session_by_class_id(class_id) as ss:
                # 检查学号是否重复（未软删除）
                existing = None
                try:
                    from sqlmodel import select
                    existing = ss.exec(
                        select(Student).where(
                            Student.is_deleted == False,
                            Student.student_number == student_num,
                        )
                    ).first()
                except Exception:
                    existing = (
                        ss.query(Student)
                        .filter(Student.is_deleted == False, Student.student_number == student_num)
                        .first()
                    )
                if existing is not None:
                    print(f"❌ 学号重复，已存在: {student_num}")
                    return
                db_student = Student(
                    name=name,
                    student_number=student_num,
                    registry_uuid=registry_uuid,
                    status=StudentStatus.ACTIVE,
                )
                ss.add(db_student)
                ss.commit()
            # 重新计算并同步到QML
            self._compute_students_and_stats()
            self.studentsChanged.emit()
            self.classesChanged.emit()
            self.statsChanged.emit()
            print(f"✅ 学生添加成功: {name}({student_num}) -> {cfg.class_name}")
        except ValueError as ve:
            print(f"❌ 添加学生失败: {ve}")
        except Exception as e:
            print(f"❌ 添加学生时出错: {e}")

    @Slot(str, str)
    def addClass(self, name, teacherName=""):
        """添加班级（仅数据库/配置，预创建子库）"""
        try:
            class_id = str(uuid.uuid4())
            ClassConfigManager.create_config(class_id, class_name=name, teacher_name=teacherName)

            # 预创建每班级子库文件并建表
            try:
                with db_manager.get_sub_session_by_class_id(class_id) as ss:
                    # 仅通过获取会话触发建表，无需插入记录
                    pass
            except Exception as db_e:
                logger.warning(f"⚠️ 预创建子库失败（忽略，不影响文件存储）: {db_e}")

            # 如果没有默认班级，则设置为新班级
            if not self._current_class_id:
                self._current_class_id = class_id

            self._compute_students_and_stats()
            self.classesChanged.emit()
            self.statsChanged.emit()
            print(f"✅ 班级创建成功: {name}（ID: {class_id}）")
        except Exception as e:
            print(f"❌ 添加班级时出错: {e}")

    @Slot("QVariant")
    def deleteStudent(self, student):
        """删除学生（仅数据库，优先软删除）"""
        try:
            # 支持传入对象或UUID
            student_uuid = None
            class_id = None
            if isinstance(student, dict):
                student_uuid = student.get("uuid") or student.get("id")
                class_id = student.get("class_id") or self._current_class_id
            else:
                student_uuid = str(student)
                class_id = self._current_class_id

            if not student_uuid or not class_id:
                print("❌ 删除学生缺少必要信息")
                return
            with db_manager.get_sub_session_by_class_id(class_id) as ss:
                db_obj = None
                # 尝试按UUID删除
                try:
                    from sqlmodel import select
                    db_obj = ss.exec(select(Student).where(Student.uuid == str(student_uuid))).first()
                except Exception:
                    try:
                        db_obj = ss.query(Student).filter(Student.uuid == str(student_uuid)).first()
                    except Exception:
                        db_obj = None
                # 若未找到，尝试按学号删除
                if db_obj is None and str(student_uuid).isdigit():
                    num = int(student_uuid)
                    try:
                        from sqlmodel import select as _select
                        db_obj = ss.exec(_select(Student).where(Student.student_number == num)).first()
                    except Exception:
                        db_obj = ss.query(Student).filter(Student.student_number == num).first()
                if db_obj is None:
                    print(f"⚠️ 未找到学生，无法删除: {student_uuid}")
                    return
                # 软删除（优先）
                try:
                    db_obj.soft_delete()
                    ss.add(db_obj)
                    ss.commit()
                except Exception:
                    # 回退为硬删除
                    try:
                        ss.delete(db_obj)
                        ss.commit()
                    except Exception as db_e:
                        logger.warning(f"⚠️ 删除学生失败: {db_e}")
                        print(f"❌ 删除学生失败: {student_uuid}")
                        return
            self._compute_students_and_stats()
            self.studentsChanged.emit()
            self.classesChanged.emit()
            self.statsChanged.emit()
            print(f"✅ 学生删除成功: {student_uuid}")
        except Exception as e:
            print(f"❌ 删除学生时出错: {e}")

    @Slot("QVariant")
    def deleteClass(self, registryId):
        """删除班级（文件存储）"""
        try:
            class_id = str(registryId)
            p = DATA / f"Class_{class_id}"
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)

            # 从缓存移除
            try:
                ClassConfigManager.reload_config(class_id)
            except Exception:
                pass

            # 如果删除的是默认班级，重新选择
            default_id = GlobalConfigManager.get_setting("custom_settings.default_class_id", None)
            if default_id == class_id:
                new_default = self._select_default_class()
                GlobalConfigManager.update_setting("custom_settings.default_class_id", new_default)
                self._current_class_id = new_default

            self._compute_students_and_stats()
            self.classesChanged.emit()
            self.studentsChanged.emit()
            self.statsChanged.emit()
            print(f"✅ 班级删除成功，ID: {class_id}")
        except Exception as e:
            print(f"❌ 删除班级时出错: {e}")

    @Slot()
    def exportData(self):
        """导出数据"""
        print("导出数据功能")

    @Slot(str, "QVariant")
    def saveSettings(self, key, value):
        """保存设置（全局配置）"""
        try:
            GlobalConfigManager.update_setting(key, value)
            # 切换默认班级时，刷新当前数据
            if key == "custom_settings.default_class_id":
                self._current_class_id = str(value)
                # 不再使用文件存储，只需重新计算并刷新
                self._compute_students_and_stats()
                self.studentsChanged.emit()
                self.classesChanged.emit()
                self.statsChanged.emit()
            print(f"✅ 设置已保存: {key} = {value}")
        except Exception as e:
            print(f"❌ 保存设置失败: {e}")

    @Slot(str)
    def filterStudents(self, text):
        """按名称/学号过滤学生"""
        try:
            t = (text or "").strip().lower()
            if not t:
                self._students = self._students_all[:]
                self.studentsChanged.emit()
                return
            self._students = [
                s for s in self._students_all
                if t in (s.get("name", "").lower())
                or t in (s.get("student_id", "").lower())
                or t in (str(s.get("className", "")).lower())
            ]
            self.studentsChanged.emit()
        except Exception as e:
            print(f"❌ 过滤学生失败: {e}")


def main():
    """主函数"""
    print(f"启动 {APP_NAME} v{APP_VERSION}...")

    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # 注册自定义类型
    qmlRegisterType(ClassManagerController, "ClassManager", 1, 0, "ClassManagerController")

    # 创建控制器实例
    controller = ClassManagerController()

    # 创建主窗口
    main_window = RinUIWindow()

    # 设置QML上下文属性
    try:
        # 尝试通过引擎设置context属性
        if hasattr(main_window, "engine") and main_window.engine:
            main_window.engine.rootContext().setContextProperty("controller", controller)
        elif hasattr(main_window, "rootContext"):
            main_window.rootContext().setContextProperty("controller", controller)
        else:
            print("⚠️ 无法设置QML上下文属性, controller可能无法在QML中访问")
    except Exception as e:
        print(f"⚠️ 设置QML上下文属性失败: {e}")

    # 加载QML文件
    main_window.load("ui/qml/main.qml")

    # 设置窗口属性
    main_window.setTitle(f"{APP_NAME} v{APP_VERSION}")
    main_window.setMinimumSize(QSize(1000, 700))
    main_window.resize(1200, 800)

    # 显示窗口
    main_window.show()

    print("应用程序已启动")
    print("使用Rinui框架构建的现代化界面")

    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
