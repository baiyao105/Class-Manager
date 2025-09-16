"""服务容器实现

提供依赖注入容器的核心功能，包括服务注册、解析和生命周期管理
"""

import inspect
import logging
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, TypeVar, Union

from .exceptions import (
    CircularDependencyException,
    ServiceNotFoundException,
    ServiceRegistrationException,
    ServiceResolutionException,
)

T = TypeVar("T")


class ServiceLifetime(Enum):
    """服务生命周期枚举"""

    SINGLETON = "singleton"  # 单例
    TRANSIENT = "transient"  # 瞬态
    SCOPED = "scoped"  # 作用域


@dataclass
class ServiceDescriptor:
    """服务描述符

    描述服务的注册信息
    """

    name: str
    service_type: type
    implementation: Union[type, Callable, Any]
    lifetime: ServiceLifetime
    dependencies: list[str]
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    created_at: Optional[float] = None
    access_count: int = 0


class ServiceContainer:
    """依赖注入服务容器

    提供服务注册、解析和生命周期管理功能
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化容器"""
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self.logger = logging.getLogger(self.__class__.__name__)

        # 服务注册表
        self._services: dict[str, ServiceDescriptor] = {}
        self._singletons: dict[str, Any] = {}
        self._scoped_instances: dict[str, dict[str, Any]] = {}

        # 解析状态跟踪（用于循环依赖检测）
        self._resolving: dict[str, bool] = {}
        self._resolution_stack: list[str] = []

        # 线程安全
        self._resolution_lock = threading.RLock()

        # 统计信息
        self._stats = {"services_registered": 0, "services_resolved": 0, "resolution_errors": 0}

    def register_singleton(
        self, name: str, implementation: Union[type, Callable, Any], service_type: Optional[type] = None
    ) -> "ServiceContainer":
        """注册单例服务

        Args:
            name: 服务名称
            implementation: 服务实现
            service_type: 服务类型

        Returns:
            容器实例（支持链式调用）
        """
        return self._register_service(name, implementation, ServiceLifetime.SINGLETON, service_type)

    def register_transient(
        self, name: str, implementation: Union[type, Callable, Any], service_type: Optional[type] = None
    ) -> "ServiceContainer":
        """注册瞬态服务

        Args:
            name: 服务名称
            implementation: 服务实现
            service_type: 服务类型

        Returns:
            容器实例（支持链式调用）
        """
        return self._register_service(name, implementation, ServiceLifetime.TRANSIENT, service_type)

    def register_scoped(
        self, name: str, implementation: Union[type, Callable, Any], service_type: Optional[type] = None
    ) -> "ServiceContainer":
        """注册作用域服务

        Args:
            name: 服务名称
            implementation: 服务实现
            service_type: 服务类型

        Returns:
            容器实例（支持链式调用）
        """
        return self._register_service(name, implementation, ServiceLifetime.SCOPED, service_type)

    def register_factory(
        self,
        name: str,
        factory: Callable,
        service_type: Optional[type] = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
    ) -> "ServiceContainer":
        """注册工厂方法

        Args:
            name: 服务名称
            factory: 工厂方法
            service_type: 服务类型
            lifetime: 服务生命周期

        Returns:
            容器实例（支持链式调用）
        """
        try:
            # 分析工厂方法的依赖
            dependencies = self._analyze_dependencies(factory)

            descriptor = ServiceDescriptor(
                name=name,
                service_type=service_type or type(None),
                implementation=factory,
                lifetime=lifetime,
                dependencies=dependencies,
                factory=factory,
            )

            self._services[name] = descriptor
            self._stats["services_registered"] += 1

            self.logger.debug(f"注册工厂服务: {name} ({lifetime.value})")
            return self

        except Exception as e:
            raise ServiceRegistrationException(name, str(e))

    def register_instance(self, name: str, instance: Any, service_type: Optional[type] = None) -> "ServiceContainer":
        """注册实例

        Args:
            name: 服务名称
            instance: 服务实例
            service_type: 服务类型

        Returns:
            容器实例（支持链式调用）
        """
        try:
            descriptor = ServiceDescriptor(
                name=name,
                service_type=service_type or type(instance),
                implementation=type(instance),
                lifetime=ServiceLifetime.SINGLETON,
                dependencies=[],
                instance=instance,
            )

            self._services[name] = descriptor
            self._singletons[name] = instance
            self._stats["services_registered"] += 1

            self.logger.debug(f"注册实例服务: {name}")
            return self

        except Exception as e:
            raise ServiceRegistrationException(name, str(e))

    def _register_service(
        self,
        name: str,
        implementation: Union[type, Callable, Any],
        lifetime: ServiceLifetime,
        service_type: Optional[type] = None,
    ) -> "ServiceContainer":
        """内部服务注册方法

        Args:
            name: 服务名称
            implementation: 服务实现
            lifetime: 服务生命周期
            service_type: 服务类型

        Returns:
            容器实例
        """
        try:
            # 确定服务类型
            if service_type is None:
                service_type = implementation if inspect.isclass(implementation) else type(implementation)

            # 分析依赖
            dependencies = self._analyze_dependencies(implementation)

            descriptor = ServiceDescriptor(
                name=name,
                service_type=service_type,
                implementation=implementation,
                lifetime=lifetime,
                dependencies=dependencies,
            )

            self._services[name] = descriptor
            self._stats["services_registered"] += 1

            self.logger.debug(f"注册服务: {name} ({lifetime.value})")
            return self

        except Exception as e:
            raise ServiceRegistrationException(name, str(e))

    def resolve(self, name: str, scope_id: Optional[str] = None) -> Any:
        """解析服务

        Args:
            name: 服务名称
            scope_id: 作用域ID（用于作用域服务）

        Returns:
            服务实例
        """
        with self._resolution_lock:
            return self._resolve_service(name, scope_id)

    def resolve_type(self, service_type: type[T], scope_id: Optional[str] = None) -> T:
        """根据类型解析服务

        Args:
            service_type: 服务类型
            scope_id: 作用域ID

        Returns:
            服务实例
        """
        # 查找匹配的服务
        for name, descriptor in self._services.items():
            if descriptor.service_type == service_type:
                return self.resolve(name, scope_id)

        raise ServiceNotFoundException(service_type.__name__)

    def _resolve_service(self, name: str, scope_id: Optional[str] = None) -> Any:
        """内部服务解析方法

        Args:
            name: 服务名称
            scope_id: 作用域ID

        Returns:
            服务实例
        """
        # 检查服务是否存在
        if name not in self._services:
            raise ServiceNotFoundException(name)

        descriptor = self._services[name]

        # 循环依赖检测
        if name in self._resolving:
            self._resolution_stack.append(name)
            raise CircularDependencyException(self._resolution_stack.copy())

        try:
            self._resolving[name] = True
            self._resolution_stack.append(name)

            # 根据生命周期返回实例
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                return self._resolve_singleton(descriptor)
            if descriptor.lifetime == ServiceLifetime.TRANSIENT:
                return self._resolve_transient(descriptor)
            if descriptor.lifetime == ServiceLifetime.SCOPED:
                return self._resolve_scoped(descriptor, scope_id or "default")

        finally:
            self._resolving.pop(name, None)
            if self._resolution_stack and self._resolution_stack[-1] == name:
                self._resolution_stack.pop()

    def _resolve_singleton(self, descriptor: ServiceDescriptor) -> Any:
        """解析单例服务"""
        if descriptor.name in self._singletons:
            descriptor.access_count += 1
            return self._singletons[descriptor.name]

        # 创建实例
        instance = self._create_instance(descriptor)
        self._singletons[descriptor.name] = instance
        descriptor.instance = instance
        descriptor.access_count += 1

        return instance

    def _resolve_transient(self, descriptor: ServiceDescriptor) -> Any:
        """解析瞬态服务"""
        descriptor.access_count += 1
        return self._create_instance(descriptor)

    def _resolve_scoped(self, descriptor: ServiceDescriptor, scope_id: str) -> Any:
        """解析作用域服务"""
        if scope_id not in self._scoped_instances:
            self._scoped_instances[scope_id] = {}

        scope_instances = self._scoped_instances[scope_id]

        if descriptor.name in scope_instances:
            descriptor.access_count += 1
            return scope_instances[descriptor.name]

        # 创建实例
        instance = self._create_instance(descriptor)
        scope_instances[descriptor.name] = instance
        descriptor.access_count += 1

        return instance

    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """创建服务实例

        Args:
            descriptor: 服务描述符

        Returns:
            服务实例
        """
        try:
            # 如果已有实例，直接返回
            if descriptor.instance is not None:
                return descriptor.instance

            # 使用工厂方法
            if descriptor.factory:
                return self._invoke_factory(descriptor.factory, descriptor.dependencies)

            # 创建类实例
            if inspect.isclass(descriptor.implementation):
                return self._create_class_instance(descriptor.implementation, descriptor.dependencies)

            # 调用函数
            if callable(descriptor.implementation):
                return self._invoke_factory(descriptor.implementation, descriptor.dependencies)

            # 直接返回值
            return descriptor.implementation

        except Exception as e:
            self._stats["resolution_errors"] += 1
            raise ServiceResolutionException(descriptor.name, str(e))

    def _create_class_instance(self, cls: type, dependencies: list[str]) -> Any:
        """创建类实例

        Args:
            cls: 类类型
            dependencies: 依赖列表

        Returns:
            类实例
        """
        # 解析依赖
        resolved_deps = {}
        for dep_name in dependencies:
            resolved_deps[dep_name] = self._resolve_service(dep_name)

        # 创建实例
        return cls(**resolved_deps)

    def _invoke_factory(self, factory: Callable, dependencies: list[str]) -> Any:
        """调用工厂方法

        Args:
            factory: 工厂方法
            dependencies: 依赖列表

        Returns:
            创建的实例
        """
        # 解析依赖
        resolved_deps = {}
        for dep_name in dependencies:
            resolved_deps[dep_name] = self._resolve_service(dep_name)

        # 调用工厂方法
        return factory(**resolved_deps)

    def _analyze_dependencies(self, implementation: Union[type, Callable]) -> list[str]:
        """分析依赖关系

        Args:
            implementation: 实现类或函数

        Returns:
            依赖名称列表
        """
        dependencies = []

        try:
            # 获取构造函数或函数签名
            if inspect.isclass(implementation):
                sig = inspect.signature(implementation.__init__)
                # 跳过self参数
                params = list(sig.parameters.values())[1:]
            else:
                sig = inspect.signature(implementation)
                params = list(sig.parameters.values())

            # 分析参数
            for param in params:
                if param.name != "self":
                    dependencies.append(param.name)

        except Exception as e:
            self.logger.warning(f"分析依赖失败: {e}")

        return dependencies

    def is_registered(self, name: str) -> bool:
        """检查服务是否已注册

        Args:
            name: 服务名称

        Returns:
            是否已注册
        """
        return name in self._services

    def get_service_info(self, name: str) -> Optional[dict[str, Any]]:
        """获取服务信息

        Args:
            name: 服务名称

        Returns:
            服务信息字典
        """
        if name not in self._services:
            return None

        descriptor = self._services[name]
        return {
            "name": descriptor.name,
            "service_type": descriptor.service_type.__name__,
            "implementation": descriptor.implementation.__name__
            if hasattr(descriptor.implementation, "__name__")
            else str(descriptor.implementation),
            "lifetime": descriptor.lifetime.value,
            "dependencies": descriptor.dependencies,
            "access_count": descriptor.access_count,
            "has_instance": descriptor.instance is not None,
        }

    def list_services(self) -> dict[str, dict[str, Any]]:
        """列出所有服务

        Returns:
            服务信息字典
        """
        return {name: self.get_service_info(name) for name in self._services}

    def clear_scope(self, scope_id: str) -> None:
        """清除作用域实例

        Args:
            scope_id: 作用域ID
        """
        if scope_id in self._scoped_instances:
            del self._scoped_instances[scope_id]
            self.logger.debug(f"清除作用域: {scope_id}")

    def reset(self) -> None:
        """重置容器"""
        self._services.clear()
        self._singletons.clear()
        self._scoped_instances.clear()
        self._resolving.clear()
        self._resolution_stack.clear()

        # 重置统计
        self._stats = {"services_registered": 0, "services_resolved": 0, "resolution_errors": 0}

        self.logger.info("容器已重置")

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息

        Returns:
            统计信息字典
        """
        return {
            **self._stats,
            "total_services": len(self._services),
            "singleton_instances": len(self._singletons),
            "scoped_instances": sum(len(instances) for instances in self._scoped_instances.values()),
            "active_scopes": len(self._scoped_instances),
        }


# 全局容器实例
container = ServiceContainer()
