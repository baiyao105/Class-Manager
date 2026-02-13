"""
一些关于特殊类处理的函数
"""

from __future__ import annotations
from types import MappingProxyType
from typing import Dict, TypeVar, Union, Any


def update_mapping(isolated: Union[MappingProxyType[Any, Any], Dict[Any, Any]], 
                        new: Union[MappingProxyType[Any, Any], Dict[Any, Any]]) \
                          -> Union[MappingProxyType[Any, Any], Dict[Any, Any]]:
    if not (hasattr(isolated, "__setitem__")):
        raise RuntimeError("isolated无法被修改，它没有__setitem__方法")
    for key in new:
        isolated[key] = new.get(key)   # pyright: ignore[reportIndexIssue]
    return isolated

_T = TypeVar("_T", bound=object)

def update_object_mapping(isolated: _T, new: Union[MappingProxyType[str, Any], Dict[str, Any]]) -> _T:
    for key in new:
        setattr(isolated, key, new.get(key))
    return isolated