"""
事件类型
"""

from typing import Optional

class EventType:

    def __init__(self, key: str, argument_type: Optional[type] = None):
        """
        构造一个新的事件类。

        :param key: 事件类型
        :param argument_type: 事件参数类型
        """
        self.key = key
        self.argument_type = argument_type


    def __repr__(self):
        return f"EventTypes({self.key!r})"

    def __eq__(self, other):
        if isinstance(other, EventType):
            return self.key == other.key
        return False
    
