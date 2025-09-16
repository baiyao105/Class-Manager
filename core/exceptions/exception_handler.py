"""全局异常处理器

提供统一的异常处理、日志记录和用户友好的错误信息
"""

import logging
import traceback
from datetime import datetime
from typing import Any, Callable, Optional

from .custom_exceptions import (
    AuthenticationException,
    AuthorizationException,
    BusinessLogicException,
    ClassManagerException,
    ConfigurationException,
    DatabaseException,
    DependencyInjectionException,
    EventException,
    RepositoryException,
    ResourceNotFoundException,
    ServiceException,
    ValidationException,
)


class ExceptionHandler:
    """全局异常处理器

    提供统一的异常处理、日志记录和错误信息格式化功能
    """

    def __init__(self, logger_name: str = "ClassManager"):
        """初始化异常处理器

        Args:
            logger_name: 日志记录器名称
        """
        self.logger = logging.getLogger(logger_name)
        self._error_handlers: dict[type, Callable] = {
            DatabaseException: self._handle_database_error,
            ValidationException: self._handle_validation_error,
            BusinessLogicException: self._handle_business_error,
            ResourceNotFoundException: self._handle_not_found_error,
            AuthenticationException: self._handle_auth_error,
            AuthorizationException: self._handle_authorization_error,
            ConfigurationException: self._handle_config_error,
            ServiceException: self._handle_service_error,
            RepositoryException: self._handle_repository_error,
            EventException: self._handle_event_error,
            DependencyInjectionException: self._handle_di_error,
        }

        # 错误统计
        self._error_stats: dict[str, int] = {}

    def handle_exception(self, exception: Exception, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """处理异常并返回标准化的错误信息

        Args:
            exception: 异常对象
            context: 异常上下文信息

        Returns:
            标准化的错误信息字典
        """
        # 基础错误信息
        error_info = {
            "success": False,
            "timestamp": datetime.utcnow().isoformat(),
            "error_id": self._generate_error_id(),
            "context": context or {},
        }

        # 处理自定义异常
        if isinstance(exception, ClassManagerException):
            error_info.update(self._handle_custom_exception(exception))
        else:
            error_info.update(self._handle_system_exception(exception))

        # 记录日志
        self._log_exception(exception, error_info)

        # 更新统计
        self._update_error_stats(error_info.get("error_code", "UNKNOWN"))

        return error_info

    def _handle_custom_exception(self, exception: ClassManagerException) -> dict[str, Any]:
        """处理自定义异常

        Args:
            exception: 自定义异常对象

        Returns:
            异常信息字典
        """
        exception_type = type(exception)

        # 基础信息
        error_info = {
            "error_type": exception_type.__name__,
            "message": exception.message,
            "error_code": exception.error_code,
            "details": exception.details,
        }

        # 使用特定处理器
        if exception_type in self._error_handlers:
            handler_info = self._error_handlers[exception_type](exception)
            error_info.update(handler_info)
        else:
            # 默认处理
            error_info.update(
                {
                    "category": "application",
                    "user_message": exception.message,
                    "technical_message": str(exception),
                    "severity": "error",
                }
            )

        return error_info

    def _handle_system_exception(self, exception: Exception) -> dict[str, Any]:
        """处理系统异常

        Args:
            exception: 系统异常对象

        Returns:
            异常信息字典
        """
        return {
            "error_type": type(exception).__name__,
            "message": str(exception),
            "error_code": "SYSTEM_ERROR",
            "category": "system",
            "user_message": "系统内部错误，请联系管理员",
            "technical_message": str(exception),
            "severity": "critical",
            "details": {"exception_type": type(exception).__name__, "traceback": traceback.format_exc()},
        }

    def _handle_database_error(self, exception: DatabaseException) -> dict[str, Any]:
        """处理数据库异常"""
        return {
            "category": "database",
            "user_message": "数据库操作失败，请稍后重试",
            "technical_message": exception.message,
            "severity": "error",
            "suggestions": ["检查数据库连接", "验证SQL语句语法", "检查数据完整性约束"],
        }

    def _handle_validation_error(self, exception: ValidationException) -> dict[str, Any]:
        """处理验证异常"""
        return {
            "category": "validation",
            "user_message": f"数据验证失败: {exception.message}",
            "technical_message": exception.message,
            "severity": "warning",
            "suggestions": ["检查输入数据格式", "确认必填字段已填写", "验证数据类型和长度"],
        }

    def _handle_business_error(self, exception: BusinessLogicException) -> dict[str, Any]:
        """处理业务逻辑异常"""
        return {
            "category": "business",
            "user_message": exception.message,
            "technical_message": exception.message,
            "severity": "warning",
            "suggestions": ["检查业务规则", "确认操作权限", "验证前置条件"],
        }

    def _handle_not_found_error(self, exception: ResourceNotFoundException) -> dict[str, Any]:
        """处理资源未找到异常"""
        return {
            "category": "not_found",
            "user_message": f"资源不存在: {exception.message}",
            "technical_message": exception.message,
            "severity": "warning",
            "suggestions": ["检查资源ID是否正确", "确认资源未被删除", "验证访问权限"],
        }

    def _handle_auth_error(self, exception: AuthenticationException) -> dict[str, Any]:
        """处理身份认证异常"""
        return {
            "category": "authentication",
            "user_message": "身份认证失败，请重新登录",
            "technical_message": exception.message,
            "severity": "warning",
            "suggestions": ["检查用户名和密码", "确认账户未被锁定", "清除浏览器缓存"],
        }

    def _handle_authorization_error(self, exception: AuthorizationException) -> dict[str, Any]:
        """处理权限授权异常"""
        return {
            "category": "authorization",
            "user_message": "权限不足，无法执行此操作",
            "technical_message": exception.message,
            "severity": "warning",
            "suggestions": ["联系管理员申请权限", "确认角色配置正确", "检查资源访问策略"],
        }

    def _handle_config_error(self, exception: ConfigurationException) -> dict[str, Any]:
        """处理配置异常"""
        return {
            "category": "configuration",
            "user_message": "系统配置错误，请联系管理员",
            "technical_message": exception.message,
            "severity": "error",
            "suggestions": ["检查配置文件语法", "验证配置项完整性", "确认环境变量设置"],
        }

    def _handle_service_error(self, exception: ServiceException) -> dict[str, Any]:
        """处理服务层异常"""
        return {
            "category": "service",
            "user_message": "服务处理失败，请稍后重试",
            "technical_message": exception.message,
            "severity": "error",
            "suggestions": ["检查服务依赖", "验证输入参数", "确认服务状态"],
        }

    def _handle_repository_error(self, exception: RepositoryException) -> dict[str, Any]:
        """处理仓储层异常"""
        return {
            "category": "repository",
            "user_message": "数据访问失败，请稍后重试",
            "technical_message": exception.message,
            "severity": "error",
            "suggestions": ["检查数据库连接", "验证查询语句", "确认数据模型"],
        }

    def _handle_event_error(self, exception: EventException) -> dict[str, Any]:
        """处理事件系统异常"""
        return {
            "category": "event",
            "user_message": "事件处理失败",
            "technical_message": exception.message,
            "severity": "warning",
            "suggestions": ["检查事件订阅者", "验证事件数据格式", "确认事件总线状态"],
        }

    def _handle_di_error(self, exception: DependencyInjectionException) -> dict[str, Any]:
        """处理依赖注入异常"""
        return {
            "category": "dependency_injection",
            "user_message": "系统初始化失败，请联系管理员",
            "technical_message": exception.message,
            "severity": "critical",
            "suggestions": ["检查服务注册", "验证依赖关系", "确认容器配置"],
        }

    def _log_exception(self, exception: Exception, error_info: dict[str, Any]) -> None:
        """记录异常日志

        Args:
            exception: 异常对象
            error_info: 错误信息
        """
        severity = error_info.get("severity", "error")
        error_id = error_info.get("error_id")

        log_message = (
            f"[{error_id}] {error_info.get('error_type', 'Unknown')}: {error_info.get('message', str(exception))}"
        )

        if severity == "critical":
            self.logger.critical(log_message, exc_info=True, extra={"error_info": error_info})
        elif severity == "error":
            self.logger.error(log_message, exc_info=True, extra={"error_info": error_info})
        elif severity == "warning":
            self.logger.warning(log_message, extra={"error_info": error_info})
        else:
            self.logger.info(log_message, extra={"error_info": error_info})

    def _generate_error_id(self) -> str:
        """生成错误ID

        Returns:
            唯一的错误ID
        """
        import uuid

        return str(uuid.uuid4())[:8]

    def _update_error_stats(self, error_code: str) -> None:
        """更新错误统计

        Args:
            error_code: 错误代码
        """
        self._error_stats[error_code] = self._error_stats.get(error_code, 0) + 1

    def get_error_stats(self) -> dict[str, int]:
        """获取错误统计信息

        Returns:
            错误统计字典
        """
        return self._error_stats.copy()

    def reset_error_stats(self) -> None:
        """重置错误统计"""
        self._error_stats.clear()

    def register_error_handler(self, exception_type: type, handler: Callable) -> None:
        """注册自定义错误处理器

        Args:
            exception_type: 异常类型
            handler: 处理器函数
        """
        self._error_handlers[exception_type] = handler


# 全局异常处理器实例
exception_handler = ExceptionHandler()


# 装饰器函数
def handle_exceptions(reraise: bool = True, return_error_info: bool = False):
    """异常处理装饰器

    Args:
        reraise: 是否重新抛出异常
        return_error_info: 是否返回错误信息而不是抛出异常
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_info = exception_handler.handle_exception(
                    e,
                    {
                        "function": func.__name__,
                        "args": str(args)[:200],  # 限制长度
                        "kwargs": str(kwargs)[:200],
                    },
                )

                if return_error_info:
                    return error_info
                if reraise:
                    raise
                return None

        return wrapper

    return decorator
