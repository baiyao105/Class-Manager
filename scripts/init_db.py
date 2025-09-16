#!/usr/bin/env python3
"""数据库初始化脚本

用于初始化混合架构数据库和创建示例数据
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import DatabaseManager


def main():
    """主函数"""
    print("🚀 开始初始化班级管理系统数据库...")

    try:
        # 创建数据库管理器
        db_manager = DatabaseManager()

        # 初始化数据库架构
        print("📋 初始化数据库架构...")
        db_manager.initialize_database()

        # 创建示例数据
        print("🌱 创建示例数据...")
        db_manager.create_sample_data()

        print("\n✅ 数据库初始化完成！")
        print("📁 数据文件位置:", db_manager.data_dir)
        print("📊 总库文件: master.db")
        print("📚 子库文件: class_*.db")

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
