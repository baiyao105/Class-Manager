"""自定义异常类型定义

定义应用程序中使用的各种异常类型，提供统一的错误处理机制
"""

import time
from typing import Any, Optional


class ClassManagerException(Exception):
    """应用基础异常类

    所有自定义异常的基类，提供统一的异常处理接口
    """

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[dict[str, Any]] = None):
        """初始化异常

        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详情
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.timestamp = time.time()

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式

        Returns:
            异常信息字典
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "timestamp": self.timestamp,
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message} (Code: {self.error_code})"


class DatabaseException(ClassManagerException):
    """数据库相关异常

    用于数据库连接、查询、事务等操作失败的情况
    """

    def __init__(
        self, message: str, error_code: str = "DB_ERROR", operation: Optional[str] = None, table: Optional[str] = None
    ):
        details = {}
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table

        super().__init__(message, error_code, details)


class ValidationException(ClassManagerException):
    """数据验证异常

    用于输入数据验证失败的情况
    """

    def __init__(
        self,
        message: str,
        error_code: str = "VALIDATION_ERROR",
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)

        super().__init__(message, error_code, details)


class BusinessLogicException(ClassManagerException):
    """业务逻辑异常

    用于业务规则违反或业务逻辑错误的情况
    """

    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR", context: Optional[dict[str, Any]] = None):
        super().__init__(message, error_code, context or {})


class ResourceNotFoundException(ClassManagerException):
    """资源未找到异常

    用于请求的资源不存在的情况
    """

    def __init__(
        self,
        message: str,
        error_code: str = "RESOURCE_NOT_FOUND",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(message, error_code, details)


class AuthenticationException(ClassManagerException):
    """身份认证异常

    用于用户身份验证失败的情况
    """

    def __init__(self, message: str = "身份认证失败", error_code: str = "AUTH_FAILED"):
        super().__init__(message, error_code)


class AuthorizationException(ClassManagerException):
    """权限授权异常

    用于用户权限不足的情况
    """

    def __init__(
        self, message: str = "权限不足", error_code: str = "ACCESS_DENIED", required_permission: Optional[str] = None
    ):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission

        super().__init__(message, error_code, details)


class ConfigurationException(ClassManagerException):
    """配置异常

    用于配置文件错误或配置项缺失的情况
    """

    def __init__(self, message: str, error_code: str = "CONFIG_ERROR", config_key: Optional[str] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(message, error_code, details)


class ServiceException(ClassManagerException):
    """服务层异常

    用于服务层操作失败的情况
    """

    def __init__(
        self,
        message: str,
        error_code: str = "SERVICE_ERROR",
        service_name: Optional[str] = None,
        method_name: Optional[str] = None,
    ):
        details = {}
        if service_name:
            details["service_name"] = service_name
        if method_name:
            details["method_name"] = method_name

        super().__init__(message, error_code, details)


class RepositoryException(ClassManagerException):
    """仓储层异常

    用于数据访问层操作失败的情况
    """

    def __init__(
        self,
        message: str,
        error_code: str = "REPOSITORY_ERROR",
        repository_name: Optional[str] = None,
        operation: Optional[str] = None,
    ):
        details = {}
        if repository_name:
            details["repository_name"] = repository_name
        if operation:
            details["operation"] = operation

        super().__init__(message, error_code, details)


class EventException(ClassManagerException):
    """事件系统异常

    用于事件发布、订阅或处理失败的情况
    """

    def __init__(self, message: str, error_code: str = "EVENT_ERROR", event_type: Optional[str] = None):
        details = {}
        if event_type:
            details["event_type"] = event_type

        super().__init__(message, error_code, details)


class DependencyInjectionException(ClassManagerException):
    """依赖注入异常

    用于依赖注入容器操作失败的情况
    """

    def __init__(self, message: str, error_code: str = "DI_ERROR", service_name: Optional[str] = None):
        details = {}
        if service_name:
            details["service_name"] = service_name

        super().__init__(message, error_code, details)


# 常用异常实例
class CommonExceptions:
    """常用异常实例"""

    @staticmethod
    def student_not_found(student_id: str) -> ResourceNotFoundException:
        return ResourceNotFoundException(f"学生不存在: {student_id}", "STUDENT_NOT_FOUND", "Student", student_id)

    @staticmethod
    def class_not_found(class_id: str) -> ResourceNotFoundException:
        return ResourceNotFoundException(f"班级不存在: {class_id}", "CLASS_NOT_FOUND", "Class", class_id)

    @staticmethod
    def achievement_not_found(achievement_id: str) -> ResourceNotFoundException:
        return ResourceNotFoundException(
            f"成就不存在: {achievement_id}", "ACHIEVEMENT_NOT_FOUND", "Achievement", achievement_id
        )

    @staticmethod
    def invalid_student_number(student_number: str) -> ValidationException:
        return ValidationException(
            f"无效的学号: {student_number}", "INVALID_STUDENT_NUMBER", "student_number", student_number
        )

    @staticmethod
    def duplicate_student_number(student_number: str) -> BusinessLogicException:
        return BusinessLogicException(
            f"学号已存在: {student_number}", "DUPLICATE_STUDENT_NUMBER", {"student_number": student_number}
        )

    @staticmethod
    def database_connection_failed() -> DatabaseException:
        return DatabaseException("数据库连接失败", "DB_CONNECTION_FAILED", "connect")

    @staticmethod
    def transaction_failed(operation: str) -> DatabaseException:
        return DatabaseException(f"事务执行失败: {operation}", "TRANSACTION_FAILED", operation)
