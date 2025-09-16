"""时间工具模块

提供各种时间处理相关的工具函数。
"""

from datetime import date, datetime, timedelta
from typing import Optional, Union

from .logger import get_logger

logger = get_logger("time_ops")


class TimeFormatter:
    """时间格式化器"""

    # 常用时间格式
    FORMAT_DATETIME = "%Y-%m-%d %H:%M:%S"
    FORMAT_DATE = "%Y-%m-%d"
    FORMAT_TIME = "%H:%M:%S"
    FORMAT_DATETIME_MS = "%Y-%m-%d %H:%M:%S.%f"
    FORMAT_ISO = "%Y-%m-%dT%H:%M:%S"
    FORMAT_CHINESE_DATE = "%Y年%m月%d日"
    FORMAT_CHINESE_DATETIME = "%Y年%m月%d日 %H时%M分%S秒"

    @staticmethod
    def now(format_str: Optional[str] = None) -> str:
        """获取当前时间字符串

        Args:
            format_str: 时间格式字符串

        Returns:
            格式化的时间字符串
        """
        if format_str is None:
            format_str = TimeFormatter.FORMAT_DATETIME

        return datetime.now().strftime(format_str)

    @staticmethod
    def today(format_str: Optional[str] = None) -> str:
        """获取今天日期字符串

        Args:
            format_str: 日期格式字符串

        Returns:
            格式化的日期字符串
        """
        if format_str is None:
            format_str = TimeFormatter.FORMAT_DATE

        return date.today().strftime(format_str)

    @staticmethod
    def format_datetime(dt: datetime, format_str: str = FORMAT_DATETIME) -> str:
        """格式化datetime对象

        Args:
            dt: datetime对象
            format_str: 格式字符串

        Returns:
            格式化的时间字符串
        """
        try:
            return dt.strftime(format_str)
        except Exception as e:
            logger.exception(f"格式化时间失败: {e}")
            return ""

    @staticmethod
    def parse_datetime(time_str: str, format_str: str = FORMAT_DATETIME) -> Optional[datetime]:
        """解析时间字符串

        Args:
            time_str: 时间字符串
            format_str: 格式字符串

        Returns:
            datetime对象
        """
        try:
            return datetime.strptime(time_str, format_str)
        except Exception as e:
            logger.exception(f"解析时间字符串失败 '{time_str}': {e}")
            return None

    @staticmethod
    def auto_parse_datetime(time_str: str) -> Optional[datetime]:
        """自动解析时间字符串(尝试多种格式)

        Args:
            time_str: 时间字符串

        Returns:
            datetime对象
        """
        formats = [
            TimeFormatter.FORMAT_DATETIME,
            TimeFormatter.FORMAT_DATE,
            TimeFormatter.FORMAT_DATETIME_MS,
            TimeFormatter.FORMAT_ISO,
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y",
        ]

        for fmt in formats:
            result = TimeFormatter.parse_datetime(time_str, fmt)
            if result:
                return result

        logger.warning(f"无法解析时间字符串: {time_str}")
        return None

    @staticmethod
    def to_timestamp(dt: datetime) -> float:
        """将datetime转换为时间戳

        Args:
            dt: datetime对象

        Returns:
            时间戳
        """
        return dt.timestamp()

    @staticmethod
    def from_timestamp(timestamp: float) -> datetime:
        """从时间戳创建datetime

        Args:
            timestamp: 时间戳

        Returns:
            datetime对象
        """
        return datetime.fromtimestamp(timestamp)

    @staticmethod
    def to_iso_string(dt: datetime) -> str:
        """转换为ISO格式字符串

        Args:
            dt: datetime对象

        Returns:
            ISO格式字符串
        """
        return dt.isoformat()

    @staticmethod
    def from_iso_string(iso_str: str) -> Optional[datetime]:
        """从ISO格式字符串解析datetime

        Args:
            iso_str: ISO格式字符串

        Returns:
            datetime对象
        """
        try:
            return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        except Exception as e:
            logger.exception(f"解析ISO时间字符串失败 '{iso_str}': {e}")
            return None


class TimeCalculator:
    """时间计算器"""

    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """添加天数

        Args:
            dt: datetime对象
            days: 天数

        Returns:
            新的datetime对象
        """
        return dt + timedelta(days=days)

    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """添加小时数

        Args:
            dt: datetime对象
            hours: 小时数

        Returns:
            新的datetime对象
        """
        return dt + timedelta(hours=hours)

    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        """添加分钟数

        Args:
            dt: datetime对象
            minutes: 分钟数

        Returns:
            新的datetime对象
        """
        return dt + timedelta(minutes=minutes)

    @staticmethod
    def subtract_days(dt: datetime, days: int) -> datetime:
        """减去天数

        Args:
            dt: datetime对象
            days: 天数

        Returns:
            新的datetime对象
        """
        return dt - timedelta(days=days)

    @staticmethod
    def days_between(dt1: datetime, dt2: datetime) -> int:
        """计算两个日期之间的天数差

        Args:
            dt1: 第一个日期
            dt2: 第二个日期

        Returns:
            天数差(dt2 - dt1)
        """
        return (dt2.date() - dt1.date()).days

    @staticmethod
    def hours_between(dt1: datetime, dt2: datetime) -> float:
        """计算两个时间之间的小时差

        Args:
            dt1: 第一个时间
            dt2: 第二个时间

        Returns:
            小时差(dt2 - dt1)
        """
        return (dt2 - dt1).total_seconds() / 3600

    @staticmethod
    def minutes_between(dt1: datetime, dt2: datetime) -> float:
        """计算两个时间之间的分钟差

        Args:
            dt1: 第一个时间
            dt2: 第二个时间

        Returns:
            分钟差(dt2 - dt1)
        """
        return (dt2 - dt1).total_seconds() / 60

    @staticmethod
    def is_same_day(dt1: datetime, dt2: datetime) -> bool:
        """检查两个时间是否在同一天

        Args:
            dt1: 第一个时间
            dt2: 第二个时间

        Returns:
            是否在同一天
        """
        return dt1.date() == dt2.date()

    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """检查是否为周末

        Args:
            dt: datetime对象

        Returns:
            是否为周末
        """
        return dt.weekday() >= 5  # 5=Saturday, 6=Sunday

    @staticmethod
    def get_week_start(dt: datetime) -> datetime:
        """获取本周开始时间(周一)

        Args:
            dt: datetime对象

        Returns:
            本周开始时间
        """
        days_since_monday = dt.weekday()
        return dt - timedelta(days=days_since_monday)

    @staticmethod
    def get_week_end(dt: datetime) -> datetime:
        """获取本周结束时间(周日)

        Args:
            dt: datetime对象

        Returns:
            本周结束时间
        """
        days_until_sunday = 6 - dt.weekday()
        return dt + timedelta(days=days_until_sunday)

    @staticmethod
    def get_month_start(dt: datetime) -> datetime:
        """获取本月开始时间

        Args:
            dt: datetime对象

        Returns:
            本月开始时间
        """
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def get_month_end(dt: datetime) -> datetime:
        """获取本月结束时间

        Args:
            dt: datetime对象

        Returns:
            本月结束时间
        """
        # 下个月第一天减去一天
        if dt.month == 12:
            next_month = dt.replace(year=dt.year + 1, month=1, day=1)
        else:
            next_month = dt.replace(month=dt.month + 1, day=1)

        return next_month - timedelta(days=1)

    @staticmethod
    def age_in_years(birth_date: Union[datetime, date], reference_date: Optional[Union[datetime, date]] = None) -> int:
        """计算年龄

        Args:
            birth_date: 出生日期
            reference_date: 参考日期(默认为今天)

        Returns:
            年龄
        """
        if reference_date is None:
            reference_date = date.today()

        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        if isinstance(reference_date, datetime):
            reference_date = reference_date.date()

        age = reference_date.year - birth_date.year

        # 检查是否还没到生日
        if reference_date.month < birth_date.month or (
            reference_date.month == birth_date.month and reference_date.day < birth_date.day
        ):
            age -= 1

        return max(0, age)


class TimeRange:
    """时间范围类"""

    def __init__(self, start: datetime, end: datetime):
        """初始化时间范围

        Args:
            start: 开始时间
            end: 结束时间
        """
        if start > end:
            raise ValueError("开始时间不能晚于结束时间")

        self.start = start
        self.end = end

    def duration_seconds(self) -> float:
        """获取持续时间(秒)

        Returns:
            持续时间
        """
        return (self.end - self.start).total_seconds()

    def duration_minutes(self) -> float:
        """获取持续时间(分钟)

        Returns:
            持续时间
        """
        return self.duration_seconds() / 60

    def duration_hours(self) -> float:
        """获取持续时间(小时)

        Returns:
            持续时间
        """
        return self.duration_seconds() / 3600

    def duration_days(self) -> float:
        """获取持续时间(天)

        Returns:
            持续时间
        """
        return self.duration_seconds() / 86400

    def contains(self, dt: datetime) -> bool:
        """检查时间是否在范围内

        Args:
            dt: 要检查的时间

        Returns:
            是否在范围内
        """
        return self.start <= dt <= self.end

    def overlaps(self, other: "TimeRange") -> bool:
        """检查是否与另一个时间范围重叠

        Args:
            other: 另一个时间范围

        Returns:
            是否重叠
        """
        return self.start <= other.end and self.end >= other.start

    def __str__(self) -> str:
        return f"TimeRange({self.start} - {self.end})"


# 便捷函数
def now(format_str: Optional[str] = None) -> str:
    """获取当前时间字符串"""
    return TimeFormatter.now(format_str)


def today(format_str: Optional[str] = None) -> str:
    """获取今天日期字符串"""
    return TimeFormatter.today(format_str)


def parse_datetime(time_str: str, format_str: Optional[str] = None) -> Optional[datetime]:
    """解析时间字符串"""
    if format_str:
        return TimeFormatter.parse_datetime(time_str, format_str)
    return TimeFormatter.auto_parse_datetime(time_str)


def format_datetime(dt: datetime, format_str: str = TimeFormatter.FORMAT_DATETIME) -> str:
    """格式化datetime对象"""
    return TimeFormatter.format_datetime(dt, format_str)


def days_between(dt1: datetime, dt2: datetime) -> int:
    """计算两个日期之间的天数差"""
    return TimeCalculator.days_between(dt1, dt2)


def hours_between(dt1: datetime, dt2: datetime) -> float:
    """计算两个时间之间的小时差"""
    return TimeCalculator.hours_between(dt1, dt2)


def age_in_years(birth_date: Union[datetime, date]) -> int:
    """计算年龄"""
    return TimeCalculator.age_in_years(birth_date)


# 导出的函数和类
__all__ = [
    "TimeCalculator",
    "TimeFormatter",
    "TimeRange",
    "age_in_years",
    "days_between",
    "format_datetime",
    "hours_between",
    "now",
    "parse_datetime",
    "today",
]
