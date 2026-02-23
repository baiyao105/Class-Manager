"""
数据库表结构定义。

每种数据类型对应一个专门的表，充分利用 SQLite 的索引和外键功能。
"""

from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 1


def create_students_table(conn: sqlite3.Connection) -> None:
    """
    创建学生表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            uuid TEXT PRIMARY KEY,
            class_uuid TEXT NOT NULL,
            class_key TEXT NOT NULL,
            name TEXT NOT NULL,
            num INTEGER NOT NULL,
            score REAL DEFAULT 0,
            total_score REAL DEFAULT 0,
            highest_score REAL DEFAULT 0,
            lowest_score REAL DEFAULT 0,
            highest_score_cause_time REAL,
            lowest_score_cause_time REAL,
            group_uuid TEXT,
            group_key TEXT,
            last_reset REAL,
            last_reset_info_uuid TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_students_class_uuid ON students(class_uuid)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_students_class_key ON students(class_key)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_students_group_uuid ON students(group_uuid)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_students_name ON students(name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_students_num ON students(num)")


def create_classes_table(conn: sqlite3.Connection) -> None:
    """
    创建班级表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            uuid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            owner TEXT,
            key TEXT UNIQUE NOT NULL,
            cleaning_mapping TEXT,
            homework_rules TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_classes_key ON classes(key)")


def create_groups_table(conn: sqlite3.Connection) -> None:
    """
    创建小组表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            uuid TEXT PRIMARY KEY,
            class_uuid TEXT,
            class_key TEXT NOT NULL,
            key TEXT NOT NULL,
            name TEXT NOT NULL,
            leader_uuid TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_groups_class_uuid ON groups(class_uuid)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_groups_class_key ON groups(class_key)")


def create_score_modifications_table(conn: sqlite3.Connection) -> None:
    """
    创建分数修改记录表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS score_modifications (
            uuid TEXT PRIMARY KEY,
            student_uuid TEXT NOT NULL,
            template_uuid TEXT,
            title TEXT NOT NULL,
            description TEXT,
            modification REAL NOT NULL,
            executed INTEGER DEFAULT 0,
            execute_time TEXT,
            execute_time_key INTEGER DEFAULT 0,
            create_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_score_mods_student ON score_modifications(student_uuid)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_score_mods_template ON score_modifications(template_uuid)")


def create_score_templates_table(conn: sqlite3.Connection) -> None:
    """
    创建分数模板表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS score_templates (
            uuid TEXT PRIMARY KEY,
            key TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            modification REAL NOT NULL,
            is_visible INTEGER DEFAULT 1,
            cant_replace INTEGER DEFAULT 0,
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_score_templates_key ON score_templates(key)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_score_templates_order ON score_templates(order_index)")


def create_achievements_table(conn: sqlite3.Connection) -> None:
    """
    创建成就实例表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            uuid TEXT PRIMARY KEY,
            student_uuid TEXT NOT NULL,
            template_uuid TEXT NOT NULL,
            time TEXT,
            time_key INTEGER,
            sound TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_achievements_student ON achievements(student_uuid)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_achievements_template ON achievements(template_uuid)")


def create_achievement_templates_table(conn: sqlite3.Connection) -> None:
    """
    创建成就模板表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS achievement_templates (
            uuid TEXT PRIMARY KEY,
            key TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            active INTEGER DEFAULT 1,
            when_triggered TEXT,
            sound TEXT,
            icon TEXT,
            condition_info TEXT,
            further_info TEXT,
            name_equals TEXT,
            name_not_equals TEXT,
            num_equals TEXT,
            num_not_equals TEXT,
            score_range TEXT,
            score_rank_range TEXT,
            highest_score_range TEXT,
            lowest_score_range TEXT,
            highest_score_cause_range TEXT,
            lowest_score_cause_range TEXT,
            modify_key_range TEXT,
            others TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_achievement_templates_key ON achievement_templates(key)")


def create_data_tags_table(conn: sqlite3.Connection) -> None:
    """
    创建数据标签表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS data_tags (
            uuid TEXT PRIMARY KEY,
            key TEXT NOT NULL,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_data_tags_key ON data_tags(key)")


def create_day_records_table(conn: sqlite3.Connection) -> None:
    """
    创建每日记录表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS day_records (
            uuid TEXT PRIMARY KEY,
            class_key TEXT NOT NULL,
            date TEXT NOT NULL,
            records TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_day_records_class ON day_records(class_key)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_day_records_date ON day_records(date)")


def create_attendance_info_table(conn: sqlite3.Connection) -> None:
    """
    创建考勤信息表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance_info (
            uuid TEXT PRIMARY KEY,
            class_key TEXT NOT NULL,
            date TEXT NOT NULL,
            records TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_attendance_class ON attendance_info(class_key)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance_info(date)")


def create_histories_table(conn: sqlite3.Connection) -> None:
    """
    创建历史记录表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS histories (
            uuid TEXT PRIMARY KEY,
            time REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_histories_time ON histories(time)")


def create_history_classes_table(conn: sqlite3.Connection) -> None:
    """
    创建历史记录和班级的关联表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history_classes (
            history_uuid TEXT NOT NULL,
            class_key TEXT NOT NULL,
            class_uuid TEXT NOT NULL,
            PRIMARY KEY (history_uuid, class_key)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_history_classes_history ON history_classes(history_uuid)")


def create_history_weekdays_table(conn: sqlite3.Connection) -> None:
    """
    创建历史记录和每日记录的关联表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history_weekdays (
            history_uuid TEXT NOT NULL,
            class_key TEXT NOT NULL,
            time_key REAL NOT NULL,
            day_record_uuid TEXT NOT NULL,
            PRIMARY KEY (history_uuid, class_key, time_key)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_history_weekdays_history ON history_weekdays(history_uuid)")


def create_student_tags_table(conn: sqlite3.Connection) -> None:
    """
    创建学生和标签的关联表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_tags (
            student_uuid TEXT NOT NULL,
            tag_uuid TEXT NOT NULL,
            PRIMARY KEY (student_uuid, tag_uuid)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_student_tags_student ON student_tags(student_uuid)")


def create_student_achievements_table(conn: sqlite3.Connection) -> None:
    """
    创建学生和成就的关联表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_achievements (
            student_uuid TEXT NOT NULL,
            achievement_uuid TEXT NOT NULL,
            PRIMARY KEY (student_uuid, achievement_uuid)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_student_achievements_student ON student_achievements(student_uuid)")


def create_student_score_mods_table(conn: sqlite3.Connection) -> None:
    """
    创建学生和分数修改的关联表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_score_mods (
            student_uuid TEXT NOT NULL,
            score_mod_uuid TEXT NOT NULL,
            PRIMARY KEY (student_uuid, score_mod_uuid)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_student_score_mods_student ON student_score_mods(student_uuid)")


def create_group_members_table(conn: sqlite3.Connection) -> None:
    """
    创建小组和学生的关联表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS group_members (
            group_uuid TEXT NOT NULL,
            student_uuid TEXT NOT NULL,
            PRIMARY KEY (group_uuid, student_uuid)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_group_members_group ON group_members(group_uuid)")


def create_group_tags_table(conn: sqlite3.Connection) -> None:
    """
    创建小组和标签的关联表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS group_tags (
            group_uuid TEXT NOT NULL,
            tag_uuid TEXT NOT NULL,
            PRIMARY KEY (group_uuid, tag_uuid)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_group_tags_group ON group_tags(group_uuid)")


def create_class_students_table(conn: sqlite3.Connection) -> None:
    """
    创建班级和学生的关联表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS class_students (
            class_uuid TEXT NOT NULL,
            student_num INTEGER NOT NULL,
            student_uuid TEXT NOT NULL,
            PRIMARY KEY (class_uuid, student_num)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_class_students_class ON class_students(class_uuid)")


def create_class_groups_table(conn: sqlite3.Connection) -> None:
    """
    创建班级和小组的关联表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS class_groups (
            class_uuid TEXT NOT NULL,
            group_key TEXT NOT NULL,
            group_uuid TEXT NOT NULL,
            PRIMARY KEY (class_uuid, group_key)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_class_groups_class ON class_groups(class_uuid)")


def create_meta_table(conn: sqlite3.Connection) -> None:
    """
    创建元数据表。
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)


class TableSchema:
    """
    表结构管理类。
    """

    TABLE_CREATORS = [
        create_meta_table,
        create_students_table,
        create_classes_table,
        create_groups_table,
        create_score_modifications_table,
        create_score_templates_table,
        create_achievements_table,
        create_achievement_templates_table,
        create_data_tags_table,
        create_day_records_table,
        create_attendance_info_table,
        create_histories_table,
        create_history_classes_table,
        create_history_weekdays_table,
        create_student_tags_table,
        create_student_achievements_table,
        create_student_score_mods_table,
        create_group_members_table,
        create_group_tags_table,
        create_class_students_table,
        create_class_groups_table,
    ]

    @classmethod
    def create_all_tables(cls, conn: sqlite3.Connection) -> None:
        """
        创建所有表。
        """
        for creator in cls.TABLE_CREATORS:
            creator(conn)
        conn.commit()

    @classmethod
    def get_schema_version(cls, conn: sqlite3.Connection) -> int:
        """
        获取数据库版本。
        """
        try:
            row = conn.execute(
                "SELECT value FROM meta WHERE key = 'schema_version'"
            ).fetchone()
            return int(row[0]) if row else 0
        except sqlite3.OperationalError:
            return 0

    @classmethod
    def set_schema_version(cls, conn: sqlite3.Connection, version: int) -> None:
        """
        设置数据库版本。
        """
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('schema_version', ?)",
            (str(version),)
        )

    @classmethod
    def initialize_database(cls, conn: sqlite3.Connection) -> None:
        """
        初始化数据库。
        """
        current_version = cls.get_schema_version(conn)
        if current_version < SCHEMA_VERSION:
            cls.create_all_tables(conn)
            cls.set_schema_version(conn, SCHEMA_VERSION)
            conn.commit()
