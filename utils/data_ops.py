"""数据处理工具模块

提供各种数据处理相关的工具函数。
"""

import hashlib
import re
from collections import Counter, defaultdict
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Callable, Union

from .logger import get_logger

logger = get_logger("data_ops")


class DataProcessor:
    """数据处理器"""

    @staticmethod
    def clean_string(text: str, remove_extra_spaces: bool = True, strip: bool = True) -> str:
        """清理字符串

        Args:
            text: 输入文本
            remove_extra_spaces: 是否移除多余空格
            strip: 是否去除首尾空格

        Returns:
            清理后的字符串
        """
        if not isinstance(text, str):
            text = str(text)

        if strip:
            text = text.strip()

        if remove_extra_spaces:
            # 将多个连续空格替换为单个空格
            text = re.sub(r"\s+", " ", text)

        return text

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """标准化手机号格式

        Args:
            phone: 手机号

        Returns:
            标准化后的手机号
        """
        if not phone:
            return ""

        # 移除所有非数字字符
        phone = re.sub(r"\D", "", str(phone))

        # 如果是11位且以1开头, 认为是中国大陆手机号
        if len(phone) == 11 and phone.startswith("1"):
            return phone

        # 如果是13位且以86开头, 去掉国家代码
        if len(phone) == 13 and phone.startswith("86"):
            return phone[2:]

        return phone

    @staticmethod
    def normalize_email(email: str) -> str:
        """标准化邮箱格式

        Args:
            email: 邮箱地址

        Returns:
            标准化后的邮箱
        """
        if not email:
            return ""

        return str(email).strip().lower()

    @staticmethod
    def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: float = 0.0) -> float:
        """安全除法

        Args:
            numerator: 分子
            denominator: 分母
            default: 除零时的默认值

        Returns:
            除法结果
        """
        try:
            if denominator == 0:
                return default
            return float(numerator) / float(denominator)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def round_decimal(value: Union[int, float, str], decimal_places: int = 2) -> float:
        """精确四舍五入

        Args:
            value: 数值
            decimal_places: 小数位数

        Returns:
            四舍五入后的数值
        """
        try:
            decimal_value = Decimal(str(value))
            rounded = decimal_value.quantize(Decimal("0." + "0" * decimal_places), rounding=ROUND_HALF_UP)
            return float(rounded)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def calculate_percentage(part: Union[int, float], total: Union[int, float], decimal_places: int = 2) -> float:
        """计算百分比

        Args:
            part: 部分值
            total: 总值
            decimal_places: 小数位数

        Returns:
            百分比
        """
        if total == 0:
            return 0.0

        percentage = (float(part) / float(total)) * 100
        return DataProcessor.round_decimal(percentage, decimal_places)

    @staticmethod
    def generate_hash(data: str, algorithm: str = "md5") -> str:
        """生成数据哈希值

        Args:
            data: 输入数据
            algorithm: 哈希算法 (md5, sha1, sha256)

        Returns:
            哈希值
        """
        try:
            data_bytes = data.encode("utf-8")

            if algorithm.lower() == "md5":
                return hashlib.md5(data_bytes).hexdigest()
            if algorithm.lower() == "sha1":
                return hashlib.sha1(data_bytes).hexdigest()
            if algorithm.lower() == "sha256":
                return hashlib.sha256(data_bytes).hexdigest()
            logger.warning(f"不支持的哈希算法: {algorithm}, 使用MD5")
            return hashlib.md5(data_bytes).hexdigest()
        except Exception as e:
            logger.exception(f"生成哈希值失败: {e}")
            return ""

    @staticmethod
    def flatten_dict(data: dict[str, Any], separator: str = ".", prefix: str = "") -> dict[str, Any]:
        """扁平化字典

        Args:
            data: 输入字典
            separator: 分隔符
            prefix: 前缀

        Returns:
            扁平化后的字典
        """
        result = {}

        for key, value in data.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key

            if isinstance(value, dict):
                result.update(DataProcessor.flatten_dict(value, separator, new_key))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    list_key = f"{new_key}{separator}{i}"
                    if isinstance(item, dict):
                        result.update(DataProcessor.flatten_dict(item, separator, list_key))
                    else:
                        result[list_key] = item
            else:
                result[new_key] = value

        return result

    @staticmethod
    def group_by(data: list[dict[str, Any]], key: str) -> dict[Any, list[dict[str, Any]]]:
        """按指定键分组数据

        Args:
            data: 数据列表
            key: 分组键

        Returns:
            分组后的数据
        """
        grouped = defaultdict(list)

        for item in data:
            if key in item:
                grouped[item[key]].append(item)
            else:
                grouped[None].append(item)

        return dict(grouped)

    @staticmethod
    def aggregate_data(
        data: list[dict[str, Any]], group_key: str, agg_funcs: dict[str, Callable]
    ) -> list[dict[str, Any]]:
        """聚合数据

        Args:
            data: 数据列表
            group_key: 分组键
            agg_funcs: 聚合函数字典 {字段名: 聚合函数}

        Returns:
            聚合后的数据
        """
        grouped = DataProcessor.group_by(data, group_key)
        result = []

        for group_value, group_data in grouped.items():
            agg_result = {group_key: group_value}

            for field, func in agg_funcs.items():
                try:
                    values = [item.get(field) for item in group_data if item.get(field) is not None]
                    if values:
                        agg_result[f"{field}_{func.__name__}"] = func(values)
                    else:
                        agg_result[f"{field}_{func.__name__}"] = None
                except Exception as e:
                    logger.exception(f"聚合字段 {field} 失败: {e}")
                    agg_result[f"{field}_{func.__name__}"] = None

            result.append(agg_result)

        return result

    @staticmethod
    def filter_data(data: list[dict[str, Any]], filters: dict[str, Any]) -> list[dict[str, Any]]:
        """过滤数据

        Args:
            data: 数据列表
            filters: 过滤条件字典

        Returns:
            过滤后的数据
        """
        result = []

        for item in data:
            match = True
            for key, value in filters.items():
                if key not in item:
                    match = False
                    break

                if isinstance(value, (list, tuple)):
                    # 如果过滤值是列表, 检查是否在列表中
                    if item[key] not in value:
                        match = False
                        break
                elif isinstance(value, dict):
                    # 支持范围过滤 {"min": 0, "max": 100}
                    if "min" in value and item[key] < value["min"]:
                        match = False
                        break
                    if "max" in value and item[key] > value["max"]:
                        match = False
                        break
                # 精确匹配
                elif item[key] != value:
                    match = False
                    break

            if match:
                result.append(item)

        return result

    @staticmethod
    def sort_data(data: list[dict[str, Any]], sort_keys: list[tuple[str, bool]]) -> list[dict[str, Any]]:
        """排序数据

        Args:
            data: 数据列表
            sort_keys: 排序键列表 [(字段名, 是否降序), ...]

        Returns:
            排序后的数据
        """
        try:
            # 多字段排序
            for key, reverse in reversed(sort_keys):
                data.sort(key=lambda x: x.get(key, 0), reverse=reverse)
            return data
        except Exception as e:
            logger.exception(f"排序数据失败: {e}")
            return data


class StatisticsCalculator:
    """统计计算器"""

    @staticmethod
    def calculate_mean(values: list[Union[int, float]]) -> float:
        """计算平均值

        Args:
            values: 数值列表

        Returns:
            平均值
        """
        if not values:
            return 0.0

        try:
            numeric_values = [float(v) for v in values if v is not None]
            if not numeric_values:
                return 0.0
            return sum(numeric_values) / len(numeric_values)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def calculate_median(values: list[Union[int, float]]) -> float:
        """计算中位数

        Args:
            values: 数值列表

        Returns:
            中位数
        """
        if not values:
            return 0.0

        try:
            numeric_values = sorted([float(v) for v in values if v is not None])
            if not numeric_values:
                return 0.0

            n = len(numeric_values)
            if n % 2 == 0:
                return (numeric_values[n // 2 - 1] + numeric_values[n // 2]) / 2
            return numeric_values[n // 2]
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def calculate_mode(values: list[Any]) -> Any:
        """计算众数

        Args:
            values: 值列表

        Returns:
            众数
        """
        if not values:
            return None

        counter = Counter(values)
        max_count = max(counter.values())
        modes = [k for k, v in counter.items() if v == max_count]

        return modes[0] if len(modes) == 1 else modes

    @staticmethod
    def calculate_range(values: list[Union[int, float]]) -> float:
        """计算极差

        Args:
            values: 数值列表

        Returns:
            极差
        """
        if not values:
            return 0.0

        try:
            numeric_values = [float(v) for v in values if v is not None]
            if not numeric_values:
                return 0.0
            return max(numeric_values) - min(numeric_values)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def calculate_variance(values: list[Union[int, float]]) -> float:
        """计算方差

        Args:
            values: 数值列表

        Returns:
            方差
        """
        if not values:
            return 0.0

        try:
            numeric_values = [float(v) for v in values if v is not None]
            if len(numeric_values) < 2:
                return 0.0

            mean = StatisticsCalculator.calculate_mean(numeric_values)
            return sum((x - mean) ** 2 for x in numeric_values) / len(numeric_values)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def calculate_std_dev(values: list[Union[int, float]]) -> float:
        """计算标准差

        Args:
            values: 数值列表

        Returns:
            标准差
        """
        variance = StatisticsCalculator.calculate_variance(values)
        return variance**0.5

    @staticmethod
    def calculate_percentile(values: list[Union[int, float]], percentile: float) -> float:
        """计算百分位数

        Args:
            values: 数值列表
            percentile: 百分位 (0-100)

        Returns:
            百分位数值
        """
        if not values or not (0 <= percentile <= 100):
            return 0.0

        try:
            numeric_values = sorted([float(v) for v in values if v is not None])
            if not numeric_values:
                return 0.0

            if percentile == 0:
                return numeric_values[0]
            if percentile == 100:
                return numeric_values[-1]

            index = (percentile / 100) * (len(numeric_values) - 1)
            lower_index = int(index)
            upper_index = min(lower_index + 1, len(numeric_values) - 1)

            if lower_index == upper_index:
                return numeric_values[lower_index]

            # 线性插值
            weight = index - lower_index
            return numeric_values[lower_index] * (1 - weight) + numeric_values[upper_index] * weight
        except (ValueError, TypeError):
            return 0.0


# 便捷函数
def clean_string(text: str) -> str:
    """清理字符串"""
    return DataProcessor.clean_string(text)


def safe_divide(numerator: Union[int, float], denominator: Union[int, float]) -> float:
    """安全除法"""
    return DataProcessor.safe_divide(numerator, denominator)


def calculate_percentage(part: Union[int, float], total: Union[int, float]) -> float:
    """计算百分比"""
    return DataProcessor.calculate_percentage(part, total)


def group_by(data: list[dict[str, Any]], key: str) -> dict[Any, list[dict[str, Any]]]:
    """按指定键分组数据"""
    return DataProcessor.group_by(data, key)


def calculate_mean(values: list[Union[int, float]]) -> float:
    """计算平均值"""
    return StatisticsCalculator.calculate_mean(values)


def calculate_median(values: list[Union[int, float]]) -> float:
    """计算中位数"""
    return StatisticsCalculator.calculate_median(values)


# 导出的函数和类
__all__ = [
    "DataProcessor",
    "StatisticsCalculator",
    "calculate_mean",
    "calculate_median",
    "calculate_percentage",
    "clean_string",
    "group_by",
    "safe_divide",
]
