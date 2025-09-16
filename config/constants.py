"""应用常量定义

包含应用程序中使用的各种常量, 如：
- 应用信息常量
- 数据库相关常量
- UI相关常量
- 业务逻辑常量
"""

import math
from enum import Enum

# ============================================================================
# 应用信息常量
# ============================================================================

APP_NAME = "Class Manager"
APP_VERSION = "2.0.0"
APP_VERSION_CODE = 200
APP_AUTHOR = "Prowaxw"
APP_DESCRIPTION = "现代化班级管理系统"

# ============================================================================
# 数据库相关常量
# ============================================================================

DEFAULT_DATABASE_URL = "sqlite:///./data/class_manager.db"
DATABASE_POOL_SIZE = 5
DATABASE_MAX_OVERFLOW = 10

# 数据表名前缀
TABLE_PREFIX = "cm_"

# ============================================================================
# UI相关常量
# ============================================================================

# 默认窗口设置
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
DEFAULT_OPACITY = 0.95


# 颜色常量
class Colors:
    """颜色常量类"""

    # 主题色
    PRIMARY = "#2563eb"  # 蓝色
    SECONDARY = "#64748b"  # 灰色
    SUCCESS = "#10b981"  # 绿色
    WARNING = "#f59e0b"  # 橙色
    ERROR = "#ef4444"  # 红色
    INFO = "#3b82f6"  # 浅蓝色

    # 分数变化颜色
    SCORE_UP_BEGIN = (0xCA, 0xFF, 0xCA)
    SCORE_UP_END = (0x33, 0xCF, 0x6C)
    SCORE_DOWN_BEGIN = (0xFC, 0xB5, 0xB5)
    SCORE_DOWN_END = (0xA9, 0x00, 0x00)

    # 背景色
    BACKGROUND_LIGHT = "#ffffff"
    BACKGROUND_DARK = "#1f2937"

    # 文本色
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#6b7280"
    TEXT_MUTED = "#9ca3af"


# 动画设置
class Animation:
    """动画相关常量"""

    DEFAULT_DURATION = 300  # 默认动画时长(ms)
    FAST_DURATION = 150
    SLOW_DURATION = 500

    # 缓动函数
    EASE_IN = "ease-in"
    EASE_OUT = "ease-out"
    EASE_IN_OUT = "ease-in-out"
    LINEAR = "linear"


# ============================================================================
# 业务逻辑常量
# ============================================================================


# 学生相关常量
class StudentConstants:
    """学生相关常量"""

    MIN_STUDENT_NUMBER = 1
    MAX_STUDENT_NUMBER = 99999
    DEFAULT_SCORE = 0.0
    MIN_SCORE = -999.0
    MAX_SCORE = 999.0

    # 学生状态
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_GRADUATED = "graduated"


# 班级相关常量
class ClassConstants:
    """班级相关常量"""

    MIN_CLASS_SIZE = 1
    MAX_CLASS_SIZE = 100
    DEFAULT_CLASS_NAME = "新班级"

    # 班级类型
    TYPE_REGULAR = "regular"  # 普通班
    TYPE_HONOR = "honor"  # 荣誉班
    TYPE_SPECIAL = "special"  # 特殊班


# 成就相关常量
class AchievementConstants:
    """成就相关常量"""

    # 成就类型
    TYPE_SCORE = "score"  # 分数类成就
    TYPE_ATTENDANCE = "attendance"  # 考勤类成就
    TYPE_BEHAVIOR = "behavior"  # 行为类成就
    TYPE_SPECIAL = "special"  # 特殊成就

    # 成就等级
    LEVEL_BRONZE = "bronze"  # 铜牌
    LEVEL_SILVER = "silver"  # 银牌
    LEVEL_GOLD = "gold"  # 金牌
    LEVEL_DIAMOND = "diamond"  # 钻石

    # 触发条件
    TRIGGER_IMMEDIATE = "immediate"  # 立即触发
    TRIGGER_DAILY = "daily"  # 每日检查
    TRIGGER_WEEKLY = "weekly"  # 每周检查
    TRIGGER_MONTHLY = "monthly"  # 每月检查


# 考勤相关常量
class AttendanceConstants:
    """考勤相关常量"""

    # 考勤状态
    STATUS_PRESENT = "present"  # 出席
    STATUS_ABSENT = "absent"  # 缺席
    STATUS_LATE = "late"  # 迟到
    STATUS_EARLY_LEAVE = "early_leave"  # 早退
    STATUS_SICK_LEAVE = "sick_leave"  # 病假
    STATUS_PERSONAL_LEAVE = "personal_leave"  # 事假

    # 迟到时间阈值(分钟)
    LATE_THRESHOLD_MINUTES = 10
    VERY_LATE_THRESHOLD_MINUTES = 30


# ============================================================================
# 文件和路径常量
# ============================================================================

# 默认路径
DEFAULT_DATA_DIR = "./data"
DEFAULT_CONFIG_DIR = "./config"
DEFAULT_LOG_DIR = "./logs"
DEFAULT_BACKUP_DIR = "./backups"
DEFAULT_EXPORT_DIR = "./exports"

# 文件扩展名
FILE_EXT_JSON = ".json"
FILE_EXT_CSV = ".csv"
FILE_EXT_XLSX = ".xlsx"
FILE_EXT_PDF = ".pdf"
FILE_EXT_LOG = ".log"
FILE_EXT_DB = ".db"

# ============================================================================
# 系统相关常量
# ============================================================================


# 日志级别
class LogLevel(Enum):
    """日志级别枚举"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# 数学常量
INF = float("inf")
NEG_INF = float("-inf")
PI = math.pi
E = math.e

# 时间常量(秒)
SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
MONTH = 30 * DAY  # 近似值
YEAR = 365 * DAY  # 近似值

# ============================================================================
# 默认数据
# ============================================================================

# 默认成就模板
DEFAULT_ACHIEVEMENTS = {
    "first_score": {
        "name": "初来乍到",
        "description": "获得第一个分数",
        "type": AchievementConstants.TYPE_SCORE,
        "level": AchievementConstants.LEVEL_BRONZE,
        "condition": "score > 0",
    },
    "perfect_attendance": {
        "name": "全勤之星",
        "description": "一周内全勤",
        "type": AchievementConstants.TYPE_ATTENDANCE,
        "level": AchievementConstants.LEVEL_SILVER,
        "condition": "weekly_attendance == 100%",
    },
    "top_student": {
        "name": "学霸",
        "description": "班级排名第一",
        "type": AchievementConstants.TYPE_SCORE,
        "level": AchievementConstants.LEVEL_GOLD,
        "condition": "rank == 1",
    },
}

# 默认分数修改模板
DEFAULT_SCORE_TEMPLATES = {
    "homework_complete": {
        "name": "作业完成",
        "description": "按时完成作业",
        "score_change": 2.0,
        "category": "homework",
    },
    "homework_excellent": {
        "name": "作业优秀",
        "description": "作业质量优秀",
        "score_change": 5.0,
        "category": "homework",
    },
    "late_arrival": {
        "name": "迟到",
        "description": "上课迟到",
        "score_change": -1.0,
        "category": "attendance",
    },
    "help_classmate": {
        "name": "助人为乐",
        "description": "帮助同学",
        "score_change": 3.0,
        "category": "behavior",
    },
}

# API相关常量
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# 分页默认值
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# 缓存相关
CACHE_TTL_SHORT = 5 * MINUTE  # 短期缓存
CACHE_TTL_MEDIUM = 30 * MINUTE  # 中期缓存
CACHE_TTL_LONG = 2 * HOUR  # 长期缓存
