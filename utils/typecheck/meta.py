"""
一些用于检查类的元类。
"""

from __future__ import annotations

from typing import Any

from utils.qtconfig import Signal, SignalInstance, QWidget
from utils.basetypes import Base


# AI写的，可能有点用
class NoDuplicateInherianceMeta(type):
    """
    防止重复继承的元类。
    
    继承此元类的类会在创建时自动检测是否会导致重复继承问题。
    
    Attributes:
        None
        
    Methods:
        __new__(mcs, name, bases, namespace, **kwargs): 创建类时检查重复继承
        _get_all_parents(cls, target_class): 获取目标类的所有父类
        _find_duplicate_inheritance(cls, bases, all_parents): 查找重复继承的类
    """
    
    def __new__(
        mcs: type[NoDuplicateInherianceMeta],
        name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
        **kwargs: Any
    ) -> type[Any]:
        """
        创建类时检查重复继承
        
        Args:
            mcs: 元类本身
            name: 类名
            bases: 父类元组
            namespace: 类的命名空间
            **kwargs: 其他关键字参数
            
        Returns:
            创建的类对象
            
        Raises:
            TypeError: 如果检测到重复继承
        """
        # 调用父类的 __new__ 方法
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        
        # 获取所有父类（排除 object 和当前类）
        all_parents = mcs._get_all_parents(cls)
        
        # 检查重复继承
        duplicates = mcs._find_duplicate_inheritance(bases, all_parents)
        
        if duplicates:
            raise TypeError(
                f"类 {name} 存在重复继承问题！\n"
                f"以下类被重复继承：{', '.join(cls.__name__ for cls in duplicates)}\n"
                f"这会导致重复初始化问题。请移除重复的父类。"
            )
        
        return cls
    
    @classmethod
    def _get_all_parents(cls, target_class: type[Any]) -> set[type[Any]]:
        """
        获取目标类的所有父类（不包括 object）
        
        Args:
            target_class: 要检查的类
            
        Returns:
            所有父类的集合
        """
        parent_classes: set[type[Any]] = set()
        queue: list[type[Any]] = list(target_class.__bases__)
        
        while queue:
            parent = queue.pop(0)
            if parent is not object:
                parent_classes.add(parent)
                queue.extend(parent.__bases__)
        
        return parent_classes
    
    @classmethod
    def _find_duplicate_inheritance(
        cls,
        bases: tuple[type[Any], ...],
        all_parents: set[type[Any]]
    ) -> set[type[Any]]:
        """
        查找重复继承的类
        
        Args:
            bases: 直接父类元组
            all_parents: 所有父类集合
            
        Returns:
            重复继承的类集合
        """
        duplicates: set[type[Any]] = set()
        
        # 检查每个直接父类的所有父类
        for base in bases:
            if base is object:
                continue
                
            # 获取该父类的所有父类
            base_parents = cls._get_all_parents(base)
            
            # 检查是否与其他父类有共同的父类
            for other_base in bases:
                if other_base is object or other_base is base:
                    continue
                
                other_parents = cls._get_all_parents(other_base)
                
                # 找出共同的父类
                common_parents = base_parents & other_parents
                duplicates.update(common_parents)
        
        return duplicates



# AI写的，没啥用
class SingleInitMeta(type):
    """
    确保每个类在实例初始化时只被初始化一次的元类
    
    工作原理：
    1. 跟踪每个实例已初始化的类
    2. 在每次初始化时检查是否已经初始化过该类
    3. 如果发现重复初始化，抛出 RuntimeError
    
    Attributes:
        _initialized_instances: 跟踪每个实例已初始化的类的字典
    """
    
    # 类变量，用于跟踪每个实例已初始化的类
    _initialized_instances: dict[int, set[type[Any]]] = {}
    
    def __new__(
        mcs,
        name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
        **kwargs: Any
    ) -> type[Any]:
        """
        创建类时不需要做特殊处理
        
        Args:
            name: 类名
            bases: 父类元组
            namespace: 类的命名空间
            **kwargs: 其他关键字参数
            
        Returns:
            创建的类对象
        """
        return super().__new__(mcs, name, bases, namespace, **kwargs)
    
    @classmethod
    def check_initialization(
        cls,
        instance: Any,
        class_to_init: type[Any]
    ) -> None:
        """
        检查是否已经初始化过指定的类
        
        Args:
            instance: 实例对象
            class_to_init: 要初始化的类
            
        Raises:
            RuntimeError: 如果该类已经被初始化过
        """
        instance_id = id(instance)
        
        # 如果这是第一次初始化该实例，创建记录
        if instance_id not in cls._initialized_instances:
            cls._initialized_instances[instance_id] = set()
        
        # 检查是否已经初始化过该类
        if class_to_init in cls._initialized_instances[instance_id]:
            raise RuntimeError(
                f"检测到重复初始化！类 {class_to_init.__name__} "
                f"已经被初始化过。这可能是由于在多重继承中多次调用了 "
                f"同一个父类的 __init__ 方法。"
            )
        
        # 记录该类已被初始化
        cls._initialized_instances[instance_id].add(class_to_init)
    
    @classmethod
    def cleanup_initialization(cls, instance: Any) -> None:
        """
        清理实例的初始化记录
        
        Args:
            instance: 实例对象
        """
        instance_id = id(instance)
        if instance_id in cls._initialized_instances:
            del cls._initialized_instances[instance_id]




# 这种短小的一般都是我写的()
class AutoSlotMeta(type(QWidget)):
    """
    一个用来自动复制父类中定义的信号到子类的元类。
    """
    def __new__(mcs, name: str, bases: tuple[type[Any]], attrs: dict[str, Any]) -> type[Any]:
        for base in bases:
            for attr_name, base_attr in base.__dict__.items():
                if isinstance(base_attr, (Signal, SignalInstance)):
                    attrs[attr_name] = base_attr
                    Base.log("T", f"复制基类信号{attr_name}到派生类{name}", "AutoSlotMeta.__new__")
        return super().__new__(mcs, name, bases, attrs)