
import time
from typing import Any

class Event:

    """
    一个携带着数据的事件。
    """

    def __init__(self, key: str, args: tuple[Any, ...] | None = None, kwargs: dict[str, Any] | None = None, 
                    trig_time: float | None = None):
        self.event_key = key
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.time = trig_time or time.time()

    def __repr__(self):
        return f"Event(event_key={self.event_key}, args={self.args}, kwargs={self.kwargs})"
    
__all__ = ["Event"]
