"""班级管理系统主入口

现代化的班级管理系统, 基于Rinui框架和PySide6构建
"""

import sys
from pathlib import Path

from PySide6.QtCore import Property, QObject, QSize, Signal, Slot
from PySide6.QtQml import qmlRegisterType
from PySide6.QtWidgets import QApplication

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import get_settings
from config.constants import APP_DESCRIPTION, APP_NAME, APP_VERSION
from core.database import db_manager
from core.services import AchievementService, ClassService, StudentService
from RinUI import RinUIWindow


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
        # 获取总库会话
        master_session_gen = db_manager.get_master_session()
        self._master_session = next(master_session_gen)

        # 初始化服务（传入数据库管理器以支持混合架构）
        self._class_service = ClassService(db_manager)
        self._student_service = StudentService(db_manager)
        self._achievement_service = AchievementService(db_manager)

    def _load_data(self):
        """加载数据"""
        try:
            # 加载统计数据
            class_stats = self._class_service.get_class_stats()
            student_stats = self._student_service.get_student_stats()
            achievement_stats = self._achievement_service.get_achievement_stats()

            self._stats = {
                "total_students": student_stats.get("total_students", 0),
                "total_classes": class_stats.get("total_classes", 0),
                "total_achievements": achievement_stats.get("total_achievements", 0),
                "avg_score": achievement_stats.get("avg_points_per_achievement", 0),
            }

            # 加载列表数据
            self._students = [self._student_to_dict(s) for s in self._student_service.get_all_students()]
            self._classes = [self._class_to_dict(c) for c in self._class_service.get_all_classes()]
            self._achievements = []
            # self._achievements = [
            #     self._achievement_to_dict(a) for a in self._achievement_service.get_all_achievements()
            # ]

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
            "created_at": student.created_at.isoformat() if student.created_at else "",
        }

    def _class_to_dict(self, class_obj) -> dict:
        """将班级注册对象转换为字典"""
        return {
            "id": class_obj.id,
            "name": class_obj.class_name,  # 使用class_name字段
            "description": class_obj.description or "",
            "is_active": class_obj.is_active,  # DataRegistry使用is_active字段，不是is_deleted
            "class_type": class_obj.class_type or "REGULAR",
            "grade": class_obj.grade or "",
            "school_year": class_obj.school_year or "",
            "student_count": class_obj.student_count,  # 直接使用student_count字段
            "created_at": class_obj.created_at.isoformat() if class_obj.created_at else "",
            "class_uuid": class_obj.uuid,  # DataRegistry使用uuid字段，不是class_uuid
        }

    def _achievement_to_dict(self, achievement) -> dict:
        """将成就对象转换为字典"""
        return {
            "id": achievement.id,
            "student_id": achievement.student_id,
            "title": achievement.title,
            "description": achievement.description or "",
            "points": achievement.points,
            "created_at": achievement.created_at.isoformat() if achievement.created_at else "",
        }

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

    @Slot(str, str, int)
    def addStudent(self, name, studentNumber, registryId):
        """添加学生"""
        try:
            # 通过registry_id获取班级信息
            registry = self._class_service.get_class_by_id(registryId)
            if not registry:
                print(f"❌ 班级不存在: {registryId}")
                return

            # 创建学生
            student = self._student_service.create_student(
                name=name,
                student_number=studentNumber,
                registry_id=registryId,
                classroom_id=1,  # 默认classroom_id
            )

            if student:
                # 重新加载学生数据
                self._students = [self._student_to_dict(s) for s in self._student_service.get_all_students()]
                self.studentsChanged.emit()
                print(f"✅ 学生添加成功: {name}")
            else:
                print(f"❌ 学生添加失败: {name}")
        except Exception as e:
            print(f"❌ 添加学生时出错: {e}")
        print(f"添加学生: {name} ({studentNumber})")

    @Slot(str, str)
    def addClass(self, name, description=""):
        """添加班级"""
        try:
            registry = self._class_service.create_class(
                name=name, description=description, class_type="REGULAR", grade="", school_year=""
            )

            if registry:
                # 重新加载班级数据
                self._classes = [self._class_to_dict(c) for c in self._class_service.get_all_classes()]
                self.classesChanged.emit()
                print(f"✅ 班级添加成功: {name}")
            else:
                print(f"❌ 班级添加失败: {name}")
        except Exception as e:
            print(f"❌ 添加班级时出错: {e}")

    @Slot(int)
    def deleteStudent(self, studentId):
        """删除学生（需要班级UUID）"""
        try:
            # 注意：这里需要知道学生所在的班级UUID
            # 在实际使用中，可能需要从UI传递更多参数
            print(f"⚠️ 删除学生功能需要班级UUID参数，学生ID: {studentId}")
            # TODO: 实现跨班级学生查找和删除
        except Exception as e:
            print(f"❌ 删除学生时出错: {e}")

    @Slot(int)
    def deleteClass(self, registryId):
        """删除班级"""
        try:
            success = self._class_service.delete_class(registryId)
            if success:
                # 重新加载班级数据
                self._classes = [self._class_to_dict(c) for c in self._class_service.get_all_classes()]
                self.classesChanged.emit()
                print(f"✅ 班级删除成功，ID: {registryId}")
            else:
                print(f"❌ 班级删除失败，ID: {registryId}")
        except Exception as e:
            print(f"❌ 删除班级时出错: {e}")

    @Slot()
    def exportData(self):
        """导出数据"""
        print("导出数据功能")

    @Slot(str, "QVariant")
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
