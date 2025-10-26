"""
文件型数据存储（班级/学生/成就最小实现）

目标：用 JSON 文件替代原数据库主库+子库结构，存放于 utils.basic_dirs.DATA/Class_{class_id} 目录下。

约定的文件结构：
- data/
  - config.json                 # 全局配置（GlobalConfig）
  - Class_{class_id}/
    - config.json               # 班级配置（ClassConfig）
    - students.json             # 学生列表（数组）
    - achievements.json         # 成就列表（数组，可选）
    - Template/
      - Score/*.json            # 积分模板
      - Achievement/*.json      # 成就模板
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from utils.basic_dirs import DATA


# -------------------------------
# 学生与成就简化数据模型
# -------------------------------
@dataclass
class StudentRecord:
    id: str
    name: str
    student_id: str
    class_id: str
    class_name: str | None = None
    is_active: bool = True
    created_at: str = ""

    @classmethod
    def create(cls, name: str, student_id: str, class_id: str, class_name: str | None = None) -> "StudentRecord":
        now = datetime.now().isoformat()
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            student_id=student_id,
            class_id=class_id,
            class_name=class_name,
            is_active=True,
            created_at=now,
        )


@dataclass
class AchievementRecord:
    id: str
    student_id: str
    title: str
    description: str | None = None
    points: int = 0
    created_at: str = ""

    @classmethod
    def create(cls, student_id: str, title: str, description: str | None = None, points: int = 0) -> "AchievementRecord":
        now = datetime.now().isoformat()
        return cls(id=str(uuid.uuid4()), student_id=student_id, title=title, description=description, points=points, created_at=now)


# -------------------------------
# 通用文件存取
# -------------------------------

def _class_dir(class_id: str) -> Path:
    return DATA / f"Class_{class_id}"


def _json_file(base: Path, filename: str) -> Path:
    p = base / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _read_json_array(file_path: Path) -> list[dict[str, Any]]:
    if not file_path.exists():
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        # 容错：如果文件是空对象或其他结构，返回空列表
        return []
    except Exception:
        return []


def _write_json_array(file_path: Path, items: Iterable[dict[str, Any]]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(list(items), f, indent=2, ensure_ascii=False)


# -------------------------------
# 学生文件存储
# -------------------------------
class StudentFileStore:
    def __init__(self, class_id: str):
        self.class_id = class_id
        self.base = _class_dir(class_id)
        self.file = _json_file(self.base, "students.json")

    def list(self) -> list[StudentRecord]:
        raw = _read_json_array(self.file)
        return [StudentRecord(**item) for item in raw if isinstance(item, dict) and "student_id" in item]

    def save_all(self, students: list[StudentRecord]) -> None:
        _write_json_array(self.file, [asdict(s) for s in students])

    def add(self, name: str, student_id: str, class_name: str | None = None) -> StudentRecord:
        students = self.list()
        # 学号去重（在同一班级内）
        for s in students:
            if s.student_id == student_id:
                raise ValueError(f"学号已存在: {student_id}")
        rec = StudentRecord.create(name=name, student_id=student_id, class_id=self.class_id, class_name=class_name)
        students.append(rec)
        self.save_all(students)
        return rec

    def delete(self, student_uuid: str) -> bool:
        students = self.list()
        new_list = [s for s in students if s.id != student_uuid]
        if len(new_list) == len(students):
            return False
        self.save_all(new_list)
        return True

    def update(self, student_uuid: str, **fields: Any) -> bool:
        students = self.list()
        updated = False
        for s in students:
            if s.id == student_uuid:
                for k, v in fields.items():
                    if hasattr(s, k):
                        setattr(s, k, v)
                updated = True
                break
        if updated:
            self.save_all(students)
        return updated


# -------------------------------
# 成就文件存储（可选）
# -------------------------------
class AchievementFileStore:
    def __init__(self, class_id: str):
        self.class_id = class_id
        self.base = _class_dir(class_id)
        self.file = _json_file(self.base, "achievements.json")

    def list(self) -> list[AchievementRecord]:
        raw = _read_json_array(self.file)
        return [AchievementRecord(**item) for item in raw if isinstance(item, dict) and "student_id" in item]

    def save_all(self, records: list[AchievementRecord]) -> None:
        _write_json_array(self.file, [asdict(a) for a in records])

    def add(self, student_id: str, title: str, description: str | None = None, points: int = 0) -> AchievementRecord:
        records = self.list()
        rec = AchievementRecord.create(student_id=student_id, title=title, description=description, points=points)
        records.append(rec)
        self.save_all(records)
        return rec


__all__ = [
    "StudentRecord",
    "AchievementRecord",
    "StudentFileStore",
    "AchievementFileStore",
]