#!/usr/bin/env python3
"""数据迁移脚本 - 将班级基础信息从数据库迁移到配置文件

此脚本用于将现有的班级基础信息从数据库迁移到新的配置文件存储结构中
"""

import json
import sqlite3
from pathlib import Path


def migrate_class_data():
    """执行班级数据迁移"""
    print("开始班级数据迁移...")

    # 查找所有班级数据库文件
    data_dir = Path("data")
    if not data_dir.exists():
        print("数据目录不存在，无需迁移")
        return

    class_db_files = list(data_dir.glob("class_*.db"))
    if not class_db_files:
        print("未找到班级数据库文件，无需迁移")
        return

    migrated_count = 0

    for db_file in class_db_files:
        try:
            # 从文件名提取班级ID
            class_id = db_file.stem.replace("class_", "")
            print(f"处理班级: {class_id}")

            # 连接数据库
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 查询班级基础信息
            cursor.execute("""
                SELECT name, description, teacher_name, teacher_contact,
                       class_type, is_active, academic_year, semester,
                       max_students, start_date, end_date
                FROM classrooms
                LIMIT 1
            """)

            row = cursor.fetchone()
            if not row:
                print(f"  班级 {class_id} 无数据，跳过")
                conn.close()
                continue

            # 准备配置数据
            config_data = {
                "class_id": class_id,
                "class_name": row["name"] or f"班级_{class_id[:8]}",
                "description": row["description"] or "",
                "teacher_name": row["teacher_name"] or "未设置",
                "teacher_contact": row["teacher_contact"] or "",
                "class_type": row["class_type"] or "regular",
                "max_students": row["max_students"] or 50,
                "academic_year": row["academic_year"] or "2024-2025",
                "semester": row["semester"] or 1,
                "is_active": bool(row["is_active"]) if row["is_active"] is not None else True,
                "start_date": row["start_date"],
                "end_date": row["end_date"],
            }

            # 创建配置文件
            config_dir = data_dir / f"Class_{class_id}"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "config.json"

            # 保存配置
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            print(f"  ✓ 已创建配置文件: {config_file}")

            # 更新数据库，移除已迁移的字段
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS classrooms_new (
                    id INTEGER PRIMARY KEY,
                    registry_uuid TEXT NOT NULL,
                    base_score REAL DEFAULT 100.0,
                    score_rules TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    deleted_at TIMESTAMP,
                    display_order INTEGER DEFAULT 0
                )
            """)

            # 迁移保留的字段
            cursor.execute("""
                INSERT INTO classrooms_new (id, registry_uuid, base_score, score_rules,
                                          created_at, updated_at, is_deleted, deleted_at, display_order)
                SELECT id, registry_uuid, base_score, score_rules,
                       created_at, updated_at, is_deleted, deleted_at, display_order
                FROM classrooms
            """)

            # 替换表
            cursor.execute("DROP TABLE classrooms")
            cursor.execute("ALTER TABLE classrooms_new RENAME TO classrooms")

            conn.commit()
            conn.close()

            print("  ✓ 已更新数据库结构")
            migrated_count += 1

        except Exception as e:
            print(f"  ✗ 迁移班级 {class_id} 失败: {e}")
            continue

    print(f"\n迁移完成！成功迁移 {migrated_count} 个班级")


def verify_migration():
    """验证迁移结果"""
    print("\n验证迁移结果...")

    data_dir = Path("data")
    class_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name.startswith("Class_")]

    for class_dir in class_dirs:
        config_file = class_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8") as f:
                    config = json.load(f)
                print(f"✓ {class_dir.name}: {config.get('class_name', '未知')}")
            except Exception as e:
                print(f"✗ {class_dir.name}: 配置文件读取失败 - {e}")
        else:
            print(f"✗ {class_dir.name}: 缺少配置文件")


if __name__ == "__main__":
    migrate_class_data()
    verify_migration()
    print("\n迁移脚本执行完成！")
