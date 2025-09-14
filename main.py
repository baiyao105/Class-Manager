"""班级管理系统主入口

现代化的班级管理系统，基于Rinui框架和PySide6构建
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import qmlRegisterType
from PySide6.QtCore import QObject, Signal, Slot, Property, QSize
from sqlmodel import Session

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import RinUI
from RinUI import RinUIWindow
from config import get_settings
from config.constants import APP_NAME, APP_VERSION, APP_DESCRIPTION
from core.database import db_manager
from core.services import ClassService, StudentService, AchievementService


class ClassManagerController(QObject):
    """班级管理系统控制器"""
    
    # 信号定义
    statsChanged = Signal()
    studentsChanged = Signal()
    classesChanged = Signal()
    achievementsChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        
        # 初始化数据库
        db_manager.initialize_database()
        db_manager.create_sample_data()
        
        # 初始化服务
        self._session = None
        self._class_service = None
        self._student_service = None
        self._achievement_service = None
        
        # 初始化数据
        self._init_services()
        self._load_data()
    
    def _init_services(self):
        """初始化服务层"""
        session_gen = db_manager.get_session()
        self._session = next(session_gen)
        self._class_service = ClassService(self._session)
        self._student_service = StudentService(self._session)
        self._achievement_service = AchievementService(self._session)
    
    def _load_data(self):
        """加载数据"""
        try:
            # 加载统计数据
            class_stats = self._class_service.get_class_stats()
            student_stats = self._student_service.get_student_stats()
            achievement_stats = self._achievement_service.get_achievement_stats()
            
            self._stats = {
                "total_students": student_stats["total_students"],
                "total_classes": class_stats["total_classes"],
                "total_achievements": achievement_stats["total_achievements"],
                "avg_score": achievement_stats["avg_points_per_achievement"]
            }
            
            # 加载列表数据
            self._students = [self._student_to_dict(s) for s in self._student_service.get_all_students()]
            self._classes = [self._class_to_dict(c) for c in self._class_service.get_all_classes()]
            self._achievements = [self._achievement_to_dict(a) for a in self._achievement_service.get_all_achievements()]
            
            # 发出信号
            self.statsChanged.emit()
            self.studentsChanged.emit()
            self.classesChanged.emit()
            self.achievementsChanged.emit()
            
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
    
    def _student_to_dict(self, student) -> dict:
        """将学生对象转换为字典"""
        return {
            "id": student.id,
            "name": student.name,
            "student_id": student.student_number,  # 使用student_number字段
            "class_id": student.class_id,
            "email": student.email or "",
            "is_active": student.status == "ACTIVE",  # 使用status字段
            "created_at": student.created_at.isoformat() if student.created_at else ""
        }
    
    def _class_to_dict(self, class_obj) -> dict:
        """将班级对象转换为字典"""
        return {
            "id": class_obj.id,
            "name": class_obj.name,
            "description": class_obj.description or "",
            "is_active": class_obj.is_active,
            "teacher_name": class_obj.teacher_name or "",  # 添加教师姓名
            "student_count": len(class_obj.students) if class_obj.students else 0,
            "created_at": class_obj.created_at.isoformat() if class_obj.created_at else ""
        }
    
    def _achievement_to_dict(self, achievement) -> dict:
        """将成就对象转换为字典"""
        return {
            "id": achievement.id,
            "student_id": achievement.student_id,
            "title": achievement.title,
            "description": achievement.description or "",
            "points": achievement.points,
            "created_at": achievement.created_at.isoformat() if achievement.created_at else ""
        }
    
    # 属性定义
    @Property('QVariant', notify=statsChanged)
    def stats(self):
        return self._stats
    
    @Property('QVariant', notify=studentsChanged)
    def students(self):
        return self._students
    
    @Property('QVariant', notify=classesChanged)
    def classes(self):
        return self._classes
    
    @Property('QVariant', notify=achievementsChanged)
    def achievements(self):
        return self._achievements
    
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
        print("刷新统计数据")
        self.statsChanged.emit()
    
    @Slot(str, str, str)
    def addStudent(self, name, studentNumber, className):
        """添加学生"""
        new_student = {
            "id": len(self._students) + 1,
            "name": name,
            "studentNumber": studentNumber,
            "className": className,
            "currentScore": 0.0,
            "rank": len(self._students) + 1,
            "status": "活跃"
        }
        self._students.append(new_student)
        self.studentsChanged.emit()
        print(f"添加学生: {name} ({studentNumber})")
    
    @Slot(str, str)
    def addClass(self, name, teacherName):
        """添加班级"""
        new_class = {
            "id": len(self._classes) + 1,
            "name": name,
            "teacherName": teacherName,
            "studentCount": 0,
            "averageScore": 0.0,
            "isActive": True
        }
        self._classes.append(new_class)
        self.classesChanged.emit()
        print(f"添加班级: {name} (班主任: {teacherName})")
    
    @Slot(int)
    def deleteStudent(self, studentId):
        """删除学生"""
        self._students = [s for s in self._students if s["id"] != studentId]
        self.studentsChanged.emit()
        print(f"删除学生ID: {studentId}")
    
    @Slot(int)
    def deleteClass(self, classId):
        """删除班级"""
        self._classes = [c for c in self._classes if c["id"] != classId]
        self.classesChanged.emit()
        print(f"删除班级ID: {classId}")
    
    @Slot()
    def exportData(self):
        """导出数据"""
        print("导出数据功能")
    
    @Slot(str, 'QVariant')
    def saveSettings(self, key, value):
        """保存设置"""
        print(f"保存设置: {key} = {value}")


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
        if hasattr(main_window, 'engine') and main_window.engine:
            main_window.engine.rootContext().setContextProperty("controller", controller)
        elif hasattr(main_window, 'rootContext'):
            main_window.rootContext().setContextProperty("controller", controller)
        else:
            print("⚠️ 无法设置QML上下文属性，controller可能无法在QML中访问")
    except Exception as e:
        print(f"⚠️ 设置QML上下文属性失败: {e}")
    
    # 加载QML文件
    main_window.load("qml/main.qml")
    
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