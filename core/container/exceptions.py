"""依赖注入容器异常定义

定义容器相关的异常类型
"""

from ..exceptions.custom_exceptions import ClassManagerException


class ContainerException(ClassManagerException):
    """容器基础异常"""

    def __init__(self, message: str, error_code: str = "CONTAINER_ERROR"):
        super().__init__(message, error_code)


class ServiceNotFoundException(ContainerException):
    """服务未找到异常"""

    def __init__(self, service_name: str):
        message = f"服务未注册: {service_name}"
        super().__init__(message, "SERVICE_NOT_FOUND")
        self.service_name = service_name


class CircularDependencyException(ContainerException):
    """循环依赖异常"""

    def __init__(self, dependency_chain: list[str]):
        chain_str = " -> ".join(dependency_chain)
        message = f"检测到循环依赖: {chain_str}"
        super().__init__(message, "CIRCULAR_DEPENDENCY")
        self.dependency_chain = dependency_chain


class ServiceRegistrationException(ContainerException):
    """服务注册异常"""

    def __init__(self, service_name: str, reason: str):
        message = f"服务注册失败 '{service_name}': {reason}"
        super().__init__(message, "SERVICE_REGISTRATION_FAILED")
        self.service_name = service_name
        self.reason = reason


class ServiceResolutionException(ContainerException):
    """服务解析异常"""

    def __init__(self, service_name: str, reason: str):
        message = f"服务解析失败 '{service_name}': {reason}"
        super().__init__(message, "SERVICE_RESOLUTION_FAILED")
        self.service_name = service_name
        self.reason = reason


class InvalidServiceTypeException(ContainerException):
    """无效服务类型异常"""

    def __init__(self, service_name: str, expected_type: str, actual_type: str):
        message = f"服务 '{service_name}' 类型不匹配: 期望 {expected_type}, 实际 {actual_type}"
        super().__init__(message, "INVALID_SERVICE_TYPE")
        self.service_name = service_name
        self.expected_type = expected_type
        self.actual_type = actual_type
