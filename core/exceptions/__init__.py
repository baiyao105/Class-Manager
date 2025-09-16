"""异常处理模块

提供自定义异常类型和全局异常处理器
"""

from .custom_exceptions import (
    AuthenticationException,
    AuthorizationException,
    BusinessLogicException,
    ClassManagerException,
    ConfigurationException,
    DatabaseException,
    ResourceNotFoundException,
    ValidationException,
)
from .exception_handler import ExceptionHandler, exception_handler

__all__ = [
    "AuthenticationException",
    "AuthorizationException",
    "BusinessLogicException",
    "ClassManagerException",
    "ConfigurationException",
    "DatabaseException",
    "ExceptionHandler",
    "ResourceNotFoundException",
    "ValidationException",
    "exception_handler",
]
