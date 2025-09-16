#!/usr/bin/env python3
"""数据库迁移脚本

用于将旧版单库架构迁移到新的混合架构
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, create_engine

from core.database import DatabaseManager
from core.models.master import DataRegistry


def migrate_from_old_db(old_db_path: str):
    """从旧版数据库迁移数据"""
    print(f"🔄 开始从 {old_db_path} 迁移数据...")

    # 连接旧数据库
    old_engine = create_engine(f"sqlite:///{old_db_path}")

    # 创建新的数据库管理器
    new_db_manager = DatabaseManager()
    new_db_manager.initialize_database()

    migration_log = []

    try:
        with Session(old_engine) as old_session:
            # 检查旧数据库中的班级表
            try:
                # 假设旧版本有一个classes表
                old_classes = old_session.execute("SELECT * FROM classes").fetchall()

                print(f"📊 发现 {len(old_classes)} 个班级需要迁移")

                for old_class in old_classes:
                    class_uuid = str(uuid4())

                    # 在总库中创建班级索引
                    with next(new_db_manager.get_master_session()) as master_session:
                        registry = DataRegistry(
                            class_name=old_class.name,
                            class_type=getattr(old_class, "class_type", "普通班级"),
                            teacher_name=getattr(old_class, "teacher", "未知老师"),
                            student_count=0,  # 稍后更新
                            db_path=f"class_{class_uuid}.db",
                            status="active",
                        )
                        master_session.add(registry)
                        master_session.commit()

                        migration_log.append(
                            {
                                "type": "class_registry",
                                "old_id": old_class.id,
                                "new_uuid": str(registry.uuid),
                                "class_uuid": class_uuid,
                                "name": old_class.name,
                            }
                        )

                    # 迁移班级详细数据到子库
                    _migrate_class_data(
                        old_session, new_db_manager, class_uuid, registry.uuid, old_class, migration_log
                    )

            except Exception as e:
                print(f"⚠️  旧数据库结构不兼容: {e}")
                print("💡 建议手动导入数据或使用新的初始化脚本")
                return

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return

    # 保存迁移日志
    log_file = Path("migration_log.json")
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(migration_log, f, ensure_ascii=False, indent=2)

    print(f"✅ 迁移完成！迁移日志保存到: {log_file}")


def _migrate_class_data(old_session, new_db_manager, class_uuid, registry_uuid, old_class, migration_log):
    """迁移班级详细数据到子库"""
    from core.models.class_ import Classroom
    from core.models.student import Student

    with next(new_db_manager.get_sub_session(class_uuid)) as sub_session:
        # 创建班级详细信息
        classroom = Classroom(
            registry_uuid=registry_uuid,
            name=old_class.name,
            description=getattr(old_class, "description", ""),
            class_type=getattr(old_class, "class_type", "普通班级"),
            max_students=getattr(old_class, "max_students", 50),
            current_students=0,  # 稍后更新
        )
        sub_session.add(classroom)
        sub_session.commit()

        # 迁移学生数据
        try:
            old_students = old_session.execute(f"SELECT * FROM students WHERE class_id = {old_class.id}").fetchall()

            student_count = 0
            for old_student in old_students:
                student = Student(
                    registry_uuid=registry_uuid,
                    name=old_student.name,
                    student_number=old_student.student_number,
                    classroom_id=classroom.id,
                    current_score=getattr(old_student, "current_score", 0.0),
                    total_score=getattr(old_student, "total_score", 0.0),
                )
                sub_session.add(student)
                student_count += 1

                migration_log.append(
                    {
                        "type": "student",
                        "old_id": old_student.id,
                        "new_id": None,  # 将在commit后更新
                        "name": old_student.name,
                        "class_uuid": class_uuid,
                    }
                )

            sub_session.commit()

            # 更新班级学生数量
            classroom.current_students = student_count
            sub_session.commit()

            print(f"📚 班级 {old_class.name} 迁移完成: {student_count} 名学生")

        except Exception as e:
            print(f"⚠️  班级 {old_class.name} 学生数据迁移失败: {e}")


def backup_current_db():
    """备份当前数据库"""
    data_dir = Path("data")
    if not data_dir.exists():
        print("📁 未发现现有数据库")
        return

    backup_dir = Path("backup") / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)

    # 备份所有数据库文件
    for db_file in data_dir.glob("*.db"):
        backup_file = backup_dir / db_file.name
        backup_file.write_bytes(db_file.read_bytes())
        print(f"💾 备份: {db_file} -> {backup_file}")

    print(f"✅ 数据库备份完成: {backup_dir}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="数据库迁移工具")
    parser.add_argument("--from-db", help="旧数据库文件路径")
    parser.add_argument("--backup", action="store_true", help="备份当前数据库")

    args = parser.parse_args()

    if args.backup:
        backup_current_db()

    if args.from_db:
        migrate_from_old_db(args.from_db)

    if not args.backup and not args.from_db:
        print("🔧 数据库迁移工具")
        print("使用方法:")
        print("  python migrate_db.py --backup          # 备份当前数据库")
        print("  python migrate_db.py --from-db old.db  # 从旧数据库迁移")


if __name__ == "__main__":
    main()
