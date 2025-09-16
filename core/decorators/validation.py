"""验证装饰器

提供输入输出验证功能装饰器
"""

import inspect
import logging
from functools import wraps
from typing import Any, Callable, Optional, Union, get_type_hints

from pydantic import BaseModel, ValidationError

from ..exceptions.custom_exceptions import ValidationException


def validate_input(
    schema: Optional[Union[type[BaseModel], dict[str, Any]]] = None, strict: bool = True, log_validation: bool = True
):
    """输入验证装饰器

    Args:
        schema: 验证模式（Pydantic模型或字典）
        strict: 是否严格验证
        log_validation: 是否记录验证日志

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(f"Validation.{func.__name__}")

            try:
                # 获取函数签名
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                # 如果提供了schema，使用schema验证
                if schema:
                    if isinstance(schema, type) and issubclass(schema, BaseModel):
                        # Pydantic模型验证
                        try:
                            validated_data = schema(**bound_args.arguments)
                            # 更新参数
                            for key, value in validated_data.dict().items():
                                if key in bound_args.arguments:
                                    bound_args.arguments[key] = value
                        except ValidationError as e:
                            raise ValidationException(f"输入验证失败: {e}", "INPUT_VALIDATION_FAILED")
                    elif isinstance(schema, dict):
                        # 字典模式验证
                        _validate_with_dict_schema(bound_args.arguments, schema, func.__name__)

                # 类型注解验证
                if strict:
                    type_hints = get_type_hints(func)
                    _validate_type_hints(bound_args.arguments, type_hints, func.__name__)

                if log_validation:
                    logger.debug(f"输入验证通过: {func.__name__}")

                return func(*bound_args.args, **bound_args.kwargs)

            except ValidationException:
                if log_validation:
                    logger.warning(f"输入验证失败: {func.__name__}")
                raise
            except Exception as e:
                if log_validation:
                    logger.exception(f"验证过程异常: {func.__name__} - {e!s}")
                raise ValidationException(f"验证过程异常: {e!s}", "VALIDATION_PROCESS_ERROR")

        return wrapper

    return decorator


def validate_output(
    schema: Optional[Union[type[BaseModel], dict[str, Any]]] = None,
    return_type: Optional[type] = None,
    log_validation: bool = True,
):
    """输出验证装饰器

    Args:
        schema: 验证模式（Pydantic模型或字典）
        return_type: 期望的返回类型
        log_validation: 是否记录验证日志

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(f"Validation.{func.__name__}")

            try:
                result = func(*args, **kwargs)

                # 验证返回值
                if schema:
                    if isinstance(schema, type) and issubclass(schema, BaseModel):
                        # Pydantic模型验证
                        try:
                            if isinstance(result, dict):
                                validated_result = schema(**result)
                                result = validated_result.dict()
                            elif not isinstance(result, schema):
                                raise ValidationException(
                                    f"返回值类型不匹配: 期望 {schema.__name__}, 实际 {type(result).__name__}",
                                    "OUTPUT_TYPE_MISMATCH",
                                )
                        except ValidationError as e:
                            raise ValidationException(f"输出验证失败: {e}", "OUTPUT_VALIDATION_FAILED")
                    elif isinstance(schema, dict):
                        # 字典模式验证
                        if isinstance(result, dict):
                            _validate_with_dict_schema(result, schema, func.__name__)

                # 返回类型验证
                if return_type and not isinstance(result, return_type):
                    raise ValidationException(
                        f"返回值类型不匹配: 期望 {return_type.__name__}, 实际 {type(result).__name__}",
                        "RETURN_TYPE_MISMATCH",
                    )

                if log_validation:
                    logger.debug(f"输出验证通过: {func.__name__}")

                return result

            except ValidationException:
                if log_validation:
                    logger.warning(f"输出验证失败: {func.__name__}")
                raise
            except Exception as e:
                if log_validation:
                    logger.exception(f"输出验证过程异常: {func.__name__} - {e!s}")
                raise ValidationException(f"输出验证过程异常: {e!s}", "OUTPUT_VALIDATION_PROCESS_ERROR")

        return wrapper

    return decorator


def validate_permissions(
    required_permissions: Union[str, list],
    user_getter: Optional[Callable] = None,
    permission_checker: Optional[Callable] = None,
):
    """权限验证装饰器

    Args:
        required_permissions: 所需权限（字符串或列表）
        user_getter: 用户获取函数
        permission_checker: 权限检查函数

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(f"Permission.{func.__name__}")

            try:
                # 获取当前用户
                current_user = None
                if user_getter:
                    current_user = user_getter(*args, **kwargs)
                elif args and hasattr(args[0], "current_user"):
                    current_user = args[0].current_user

                if not current_user:
                    raise ValidationException("无法获取当前用户信息", "USER_NOT_FOUND")

                # 检查权限
                permissions_to_check = required_permissions
                if isinstance(permissions_to_check, str):
                    permissions_to_check = [permissions_to_check]

                for permission in permissions_to_check:
                    has_permission = False

                    if permission_checker:
                        has_permission = permission_checker(current_user, permission)
                    elif hasattr(current_user, "has_permission"):
                        has_permission = current_user.has_permission(permission)
                    elif hasattr(current_user, "permissions"):
                        has_permission = permission in current_user.permissions

                    if not has_permission:
                        logger.warning(f"权限不足: {func.__name__} - 用户: {current_user} - 权限: {permission}")
                        raise ValidationException(f"权限不足: 需要 '{permission}' 权限", "INSUFFICIENT_PERMISSIONS")

                logger.debug(f"权限验证通过: {func.__name__}")
                return func(*args, **kwargs)

            except ValidationException:
                raise
            except Exception as e:
                logger.exception(f"权限验证过程异常: {func.__name__} - {e!s}")
                raise ValidationException(f"权限验证过程异常: {e!s}", "PERMISSION_VALIDATION_ERROR")

        return wrapper

    return decorator


def validate_not_none(*param_names: str):
    """非空验证装饰器

    Args:
        *param_names: 需要验证非空的参数名

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数签名
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # 检查指定参数是否为None
            for param_name in param_names:
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if value is None:
                        raise ValidationException(
                            f"参数 '{param_name}' 不能为空", "PARAMETER_CANNOT_BE_NONE", param_name, value
                        )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_range(
    param_name: str,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    inclusive: bool = True,
):
    """范围验证装饰器

    Args:
        param_name: 参数名
        min_value: 最小值
        max_value: 最大值
        inclusive: 是否包含边界值

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数签名
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # 检查参数范围
            if param_name in bound_args.arguments:
                value = bound_args.arguments[param_name]

                if isinstance(value, (int, float)):
                    if min_value is not None:
                        if inclusive and value < min_value:
                            raise ValidationException(
                                f"参数 '{param_name}' 值 {value} 小于最小值 {min_value}",
                                "VALUE_BELOW_MINIMUM",
                                param_name,
                                value,
                            )
                        if not inclusive and value <= min_value:
                            raise ValidationException(
                                f"参数 '{param_name}' 值 {value} 小于等于最小值 {min_value}",
                                "VALUE_BELOW_OR_EQUAL_MINIMUM",
                                param_name,
                                value,
                            )

                    if max_value is not None:
                        if inclusive and value > max_value:
                            raise ValidationException(
                                f"参数 '{param_name}' 值 {value} 大于最大值 {max_value}",
                                "VALUE_ABOVE_MAXIMUM",
                                param_name,
                                value,
                            )
                        if not inclusive and value >= max_value:
                            raise ValidationException(
                                f"参数 '{param_name}' 值 {value} 大于等于最大值 {max_value}",
                                "VALUE_ABOVE_OR_EQUAL_MAXIMUM",
                                param_name,
                                value,
                            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def _validate_with_dict_schema(data: dict[str, Any], schema: dict[str, Any], func_name: str) -> None:
    """使用字典模式验证数据

    Args:
        data: 要验证的数据
        schema: 验证模式
        func_name: 函数名（用于错误信息）
    """
    for key, expected_type in schema.items():
        if key in data:
            value = data[key]
            if not isinstance(value, expected_type):
                raise ValidationException(
                    f"参数 '{key}' 类型不匹配: 期望 {expected_type.__name__}, 实际 {type(value).__name__}",
                    "PARAMETER_TYPE_MISMATCH",
                    key,
                    value,
                )


def _validate_type_hints(arguments: dict[str, Any], type_hints: dict[str, type], func_name: str) -> None:
    """验证类型注解

    Args:
        arguments: 函数参数
        type_hints: 类型注解
        func_name: 函数名（用于错误信息）
    """
    for param_name, expected_type in type_hints.items():
        if param_name in arguments and param_name != "return":
            value = arguments[param_name]
            if value is not None and not isinstance(value, expected_type):
                raise ValidationException(
                    f"参数 '{param_name}' 类型不匹配: 期望 {expected_type.__name__}, 实际 {type(value).__name__}",
                    "TYPE_HINT_MISMATCH",
                    param_name,
                    value,
                )
