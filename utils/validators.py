"""数据验证工具模块

提供各种常用的数据验证函数。
"""

import re
from datetime import datetime
from typing import Any, Union

from .logger import get_logger

logger = get_logger("validators")


class ValidationError(Exception):
    """验证错误异常"""


class Validator:
    """数据验证器基类"""

    @staticmethod
    def is_empty(value: Any) -> bool:
        """检查值是否为空

        Args:
            value: 要检查的值

        Returns:
            是否为空
        """
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        return bool(isinstance(value, (list, dict, tuple)) and len(value) == 0)

    @staticmethod
    def is_not_empty(value: Any) -> bool:
        """检查值是否不为空

        Args:
            value: 要检查的值

        Returns:
            是否不为空
        """
        return not Validator.is_empty(value)

    @staticmethod
    def is_email(email: str) -> bool:
        """验证邮箱格式

        Args:
            email: 邮箱地址

        Returns:
            是否为有效邮箱
        """
        if not email or not isinstance(email, str):
            return False

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def is_phone(phone: str) -> bool:
        """验证手机号格式(中国大陆)

        Args:
            phone: 手机号

        Returns:
            是否为有效手机号
        """
        if not phone or not isinstance(phone, str):
            return False

        # 中国大陆手机号格式
        pattern = r"^1[3-9]\d{9}$"
        return bool(re.match(pattern, phone.strip()))

    @staticmethod
    def is_id_card(id_card: str) -> bool:
        """验证身份证号格式(中国大陆)

        Args:
            id_card: 身份证号

        Returns:
            是否为有效身份证号
        """
        if not id_card or not isinstance(id_card, str):
            return False

        id_card = id_card.strip().upper()

        # 18位身份证号格式
        if len(id_card) != 18:
            return False

        pattern = r"^\d{17}[\dX]$"
        if not re.match(pattern, id_card):
            return False

        # 简单的校验码验证
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]

        try:
            sum_val = sum(int(id_card[i]) * weights[i] for i in range(17))
            check_code = check_codes[sum_val % 11]
            return id_card[17] == check_code
        except (ValueError, IndexError):
            return False

    @staticmethod
    def is_student_number(student_number: str) -> bool:
        """验证学号格式

        Args:
            student_number: 学号

        Returns:
            是否为有效学号
        """
        if not student_number or not isinstance(student_number, str):
            return False

        student_number = student_number.strip()

        # 学号格式：4位年份 + 2位专业代码 + 4位序号
        pattern = r"^\d{10}$"
        if not re.match(pattern, student_number):
            return False

        # 检查年份是否合理(2000-2030)
        year = int(student_number[:4])
        return 2000 <= year <= 2030

    @staticmethod
    def is_positive_number(value: Union[int, float, str]) -> bool:
        """检查是否为正数

        Args:
            value: 要检查的值

        Returns:
            是否为正数
        """
        try:
            num = float(value)
            return num > 0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_in_range(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> bool:
        """检查数值是否在指定范围内

        Args:
            value: 要检查的值
            min_val: 最小值
            max_val: 最大值

        Returns:
            是否在范围内
        """
        try:
            num = float(value)
            return min_val <= num <= max_val
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_valid_date(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
        """验证日期格式

        Args:
            date_str: 日期字符串
            format_str: 日期格式

        Returns:
            是否为有效日期
        """
        if not date_str or not isinstance(date_str, str):
            return False

        try:
            datetime.strptime(date_str.strip(), format_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_score(score: Union[int, float, str]) -> bool:
        """验证成绩是否有效(0-100)

        Args:
            score: 成绩

        Returns:
            是否为有效成绩
        """
        return Validator.is_in_range(score, 0, 100)

    @staticmethod
    def validate_required_fields(data: dict[str, Any], required_fields: list[str]) -> list[str]:
        """验证必填字段

        Args:
            data: 数据字典
            required_fields: 必填字段列表

        Returns:
            缺失的字段列表
        """
        missing_fields = []

        for field in required_fields:
            if field not in data or Validator.is_empty(data[field]):
                missing_fields.append(field)

        return missing_fields

    @staticmethod
    def validate_data_types(data: dict[str, Any], type_mapping: dict[str, type]) -> list[str]:
        """验证数据类型

        Args:
            data: 数据字典
            type_mapping: 字段类型映射

        Returns:
            类型错误的字段列表
        """
        type_errors = []

        for field, expected_type in type_mapping.items():
            if field in data and data[field] is not None and not isinstance(data[field], expected_type):
                type_errors.append(f"{field} (期望: {expected_type.__name__}, 实际: {type(data[field]).__name__})")

        return type_errors


def validate_student_data(data: dict[str, Any]) -> dict[str, Any]:
    """验证学生数据

    Args:
        data: 学生数据

    Returns:
        验证结果
    """
    result = {"valid": True, "errors": [], "warnings": []}

    # 必填字段验证
    required_fields = ["name", "student_number", "class_id"]
    missing_fields = Validator.validate_required_fields(data, required_fields)
    if missing_fields:
        result["valid"] = False
        result["errors"].append(f"缺少必填字段: {', '.join(missing_fields)}")

    # 学号格式验证
    if "student_number" in data and not Validator.is_student_number(data["student_number"]):
        result["valid"] = False
        result["errors"].append("学号格式不正确")

    # 邮箱验证
    if "email" in data and data["email"] and not Validator.is_email(data["email"]):
        result["warnings"].append("邮箱格式可能不正确")

    # 手机号验证
    if "phone" in data and data["phone"] and not Validator.is_phone(data["phone"]):
        result["warnings"].append("手机号格式可能不正确")

    logger.debug(f"学生数据验证结果: {result}")
    return result


def validate_class_data(data: dict[str, Any]) -> dict[str, Any]:
    """验证班级数据

    Args:
        data: 班级数据

    Returns:
        验证结果
    """
    result = {"valid": True, "errors": [], "warnings": []}

    # 必填字段验证
    required_fields = ["name", "teacher_name"]
    missing_fields = Validator.validate_required_fields(data, required_fields)
    if missing_fields:
        result["valid"] = False
        result["errors"].append(f"缺少必填字段: {', '.join(missing_fields)}")

    # 班级名称长度验证
    if data.get("name") and len(data["name"]) > 50:
        result["warnings"].append("班级名称过长, 建议不超过50个字符")

    logger.debug(f"班级数据验证结果: {result}")
    return result


def validate_achievement_data(data: dict[str, Any]) -> dict[str, Any]:
    """验证成就数据

    Args:
        data: 成就数据

    Returns:
        验证结果
    """
    result = {"valid": True, "errors": [], "warnings": []}

    # 必填字段验证
    required_fields = ["student_id", "title", "type"]
    missing_fields = Validator.validate_required_fields(data, required_fields)
    if missing_fields:
        result["valid"] = False
        result["errors"].append(f"缺少必填字段: {', '.join(missing_fields)}")

    # 成就类型验证
    valid_types = ["ACADEMIC", "SPORTS", "ARTS", "SOCIAL", "OTHER"]
    if "type" in data and data["type"] not in valid_types:
        result["valid"] = False
        result["errors"].append(f"成就类型无效, 有效类型: {', '.join(valid_types)}")

    # 日期验证
    if data.get("date_achieved") and not Validator.is_valid_date(str(data["date_achieved"])):
        result["warnings"].append("成就日期格式可能不正确")

    logger.debug(f"成就数据验证结果: {result}")
    return result


# 导出的函数和类
__all__ = ["ValidationError", "Validator", "validate_achievement_data", "validate_class_data", "validate_student_data"]
