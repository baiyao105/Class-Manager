"""依赖注入装饰器

提供便捷的服务注册和依赖注入装饰器
"""

import inspect
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from .exceptions import ServiceNotFoundException
from .service_container import ServiceLifetime, container

T = TypeVar("T")


def singleton(name: Optional[str] = None, service_type: Optional[type] = None):
    """单例服务装饰器

    Args:
        name: 服务名称（默认使用类名）
        service_type: 服务类型（默认使用被装饰的类）
    """

    def decorator(cls: type[T]) -> type[T]:
        service_name = name or cls.__name__.lower()
        container.register_singleton(service_name, cls, service_type or cls)
        return cls

    return decorator


def transient(name: Optional[str] = None, service_type: Optional[type] = None):
    """瞬态服务装饰器

    Args:
        name: 服务名称（默认使用类名）
        service_type: 服务类型（默认使用被装饰的类）
    """

    def decorator(cls: type[T]) -> type[T]:
        service_name = name or cls.__name__.lower()
        container.register_transient(service_name, cls, service_type or cls)
        return cls

    return decorator


def scoped(name: Optional[str] = None, service_type: Optional[type] = None):
    """作用域服务装饰器

    Args:
        name: 服务名称（默认使用类名）
        service_type: 服务类型（默认使用被装饰的类）
    """

    def decorator(cls: type[T]) -> type[T]:
        service_name = name or cls.__name__.lower()
        container.register_scoped(service_name, cls, service_type or cls)
        return cls

    return decorator


def service(
    name: Optional[str] = None,
    lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
    service_type: Optional[type] = None,
):
    """通用服务装饰器

    Args:
        name: 服务名称（默认使用类名）
        lifetime: 服务生命周期
        service_type: 服务类型（默认使用被装饰的类）
    """

    def decorator(cls: type[T]) -> type[T]:
        service_name = name or cls.__name__.lower()

        if lifetime == ServiceLifetime.SINGLETON:
            container.register_singleton(service_name, cls, service_type or cls)
        elif lifetime == ServiceLifetime.TRANSIENT:
            container.register_transient(service_name, cls, service_type or cls)
        elif lifetime == ServiceLifetime.SCOPED:
            container.register_scoped(service_name, cls, service_type or cls)

        return cls

    return decorator


def factory(name: str, lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT, service_type: Optional[type] = None):
    """工厂方法装饰器

    Args:
        name: 服务名称
        lifetime: 服务生命周期
        service_type: 服务类型
    """

    def decorator(func: Callable) -> Callable:
        container.register_factory(name, func, service_type, lifetime)
        return func

    return decorator


def inject(*service_names: str, **service_mappings: str):
    """依赖注入装饰器

    支持两种注入方式：
    1. 位置参数：按参数顺序注入服务
    2. 关键字参数：按参数名映射注入服务

    Args:
        *service_names: 按顺序注入的服务名称
        **service_mappings: 参数名到服务名的映射

    Example:
        @inject('database', 'logger')
        def some_function(db, log, other_param):
            # db 将注入 'database' 服务
            # log 将注入 'logger' 服务
            # other_param 保持原值
            pass

        @inject(db='database', log='logger')
        def some_function(db, log, other_param):
            # db 将注入 'database' 服务
            # log 将注入 'logger' 服务
            # other_param 保持原值
            pass
    """

    def decorator(func: Callable) -> Callable:
        # 获取函数签名
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 创建新的参数字典
            bound_args = sig.bind_partial(*args, **kwargs)
            bound_args.apply_defaults()

            # 按位置注入服务
            for i, service_name in enumerate(service_names):
                if i < len(param_names):
                    param_name = param_names[i]
                    if param_name not in bound_args.arguments:
                        try:
                            service_instance = container.resolve(service_name)
                            bound_args.arguments[param_name] = service_instance
                        except ServiceNotFoundException:
                            # 如果服务不存在，保持原参数值
                            pass

            # 按名称映射注入服务
            for param_name, service_name in service_mappings.items():
                if param_name in param_names and param_name not in bound_args.arguments:
                    try:
                        service_instance = container.resolve(service_name)
                        bound_args.arguments[param_name] = service_instance
                    except ServiceNotFoundException:
                        # 如果服务不存在，保持原参数值
                        pass

            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper

    return decorator


def auto_inject(func: Callable) -> Callable:
    """自动依赖注入装饰器

    根据参数名自动注入对应的服务

    Args:
        func: 被装饰的函数

    Returns:
        装饰后的函数
    """
    # 获取函数签名
    sig = inspect.signature(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 创建新的参数字典
        bound_args = sig.bind_partial(*args, **kwargs)
        bound_args.apply_defaults()

        # 自动注入缺失的参数
        for param_name, param in sig.parameters.items():
            if param_name not in bound_args.arguments:
                # 尝试按参数名解析服务
                try:
                    service_instance = container.resolve(param_name)
                    bound_args.arguments[param_name] = service_instance
                except ServiceNotFoundException:
                    # 尝试按参数类型解析服务
                    if param.annotation != inspect.Parameter.empty:
                        try:
                            service_instance = container.resolve_type(param.annotation)
                            bound_args.arguments[param_name] = service_instance
                        except ServiceNotFoundException:
                            # 如果都无法解析，保持原参数值
                            pass

        return func(*bound_args.args, **bound_args.kwargs)

    return wrapper


class InjectableClass:
    """可注入基类

    继承此类的子类将自动支持依赖注入
    """

    def __init__(self, **kwargs):
        """初始化时自动注入依赖"""
        # 获取类的构造函数签名
        sig = inspect.signature(self.__class__.__init__)

        # 自动注入缺失的参数
        for param_name, param in sig.parameters.items():
            if param_name not in ["self"] and param_name not in kwargs:
                # 尝试按参数名解析服务
                try:
                    service_instance = container.resolve(param_name)
                    kwargs[param_name] = service_instance
                except ServiceNotFoundException:
                    # 尝试按参数类型解析服务
                    if param.annotation != inspect.Parameter.empty:
                        try:
                            service_instance = container.resolve_type(param.annotation)
                            kwargs[param_name] = service_instance
                        except ServiceNotFoundException:
                            # 如果都无法解析，使用默认值或跳过
                            if param.default != inspect.Parameter.empty:
                                kwargs[param_name] = param.default

        # 设置属性
        for key, value in kwargs.items():
            if key != "self":
                setattr(self, key, value)


def resolve_service(name: str, scope_id: Optional[str] = None) -> Any:
    """便捷的服务解析函数

    Args:
        name: 服务名称
        scope_id: 作用域ID

    Returns:
        服务实例
    """
    return container.resolve(name, scope_id)


def resolve_service_type(service_type: type[T], scope_id: Optional[str] = None) -> T:
    """便捷的类型解析函数

    Args:
        service_type: 服务类型
        scope_id: 作用域ID

    Returns:
        服务实例
    """
    return container.resolve_type(service_type, scope_id)


# 上下文管理器
class ServiceScope:
    """服务作用域上下文管理器

    用于管理作用域服务的生命周期
    """

    def __init__(self, scope_id: str):
        """初始化作用域

        Args:
            scope_id: 作用域ID
        """
        self.scope_id = scope_id

    def __enter__(self) -> str:
        """进入作用域

        Returns:
            作用域ID
        """
        return self.scope_id

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出作用域，清理作用域实例"""
        container.clear_scope(self.scope_id)

    def resolve(self, name: str) -> Any:
        """在当前作用域中解析服务

        Args:
            name: 服务名称

        Returns:
            服务实例
        """
        return container.resolve(name, self.scope_id)

    def resolve_type(self, service_type: type[T]) -> T:
        """在当前作用域中按类型解析服务

        Args:
            service_type: 服务类型

        Returns:
            服务实例
        """
        return container.resolve_type(service_type, self.scope_id)


# 便捷函数
def create_scope(scope_id: Optional[str] = None) -> ServiceScope:
    """创建服务作用域

    Args:
        scope_id: 作用域ID（默认生成UUID）

    Returns:
        服务作用域实例
    """
    if scope_id is None:
        import uuid

        scope_id = str(uuid.uuid4())

    return ServiceScope(scope_id)
