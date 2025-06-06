"""
事件连接机制
"""
import time
from typing import Callable, List, Optional, Literal, Any, Dict, Tuple, Iterable, Union
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from .event_types import EventType

def addrof(obj) -> str:

    """获取对象的内存地址

    :param obj: 任意Python对象
    :return: 十六进制格式的内存地址字符串
    """
    return "0x" + hex(id(obj))[2:].zfill(16).upper()




class TaskingError(Exception):
    "任务错误"

class TaskRunningError(TaskingError):
    "任务正在运行中"

class CooldownError(TaskingError):
    "冷却时间未到"

class MaxTrigError(TaskingError):
    "触发次数已达到上限"


class EventTask(Callable):
    "一个事件任务"

    task_threadpool = ThreadPoolExecutor(max_workers=256, thread_name_prefix="EventTaskExecutor")

    def __init__(self,
                 func: Callable,
                 args: List = None,
                 kwargs: dict = None,
                 name: str = "Task",
                 max_trig: int = -1,
                 cooldown: float = 0.0,
                 allow_async: bool = False,
                 on_error: Literal["ignore", "strict"] = "strict",
                 use_thread: bool = False,
                 use_threadpool: bool = False
                 ):
        """
        构造一个事件任务，传递给事件/事件类型进行操作

        :param func: 任务函数
        :param args: 任务函数参数
        :param kwargs: 任务函数关键字参数
        :param name: 任务名称
        :param max_trig: 最大触发次数
        :param cooldown: 冷却时间
        :param allow_async: 是否允许异步
        """
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.name = name
        self.max_trig = max_trig
        self.cooldown = cooldown
        self.allow_async = allow_async
        self.on_error = on_error
        self.trig_count = 0
        self.last_trig = 0.0
        self.use_thread = use_thread
        self.use_threadpool = use_threadpool
        if use_threadpool and use_thread:
            raise TaskingError("不能同时使用线程池和线程")
        self.is_running = False

    def __call__(self):

                
        if self.cooldown > 0 and time.time() - self.last_trig < self.cooldown:
            if self.on_error == "strict":
                raise CooldownError(f"任务 {self.name} ({addrof(self)}) 冷却时间未到 ({self.cooldown})")
            else:
                return
    
        if self.max_trig != -1 and self.trig_count >= self.max_trig:
            if self.on_error == "strict":
                raise MaxTrigError(f"任务 {self.name} ({addrof(self)}) 触发次数已达到上限 ({self.max_trig})")
            else:
                return
            
        if self.is_running and not self.allow_async:
                if self.on_error == "strict":
                    raise TaskRunningError(f"任务 {self.name} ({addrof(self)}) 正在运行中")
                else:
                    return


        self.is_running = True
        def _run(self: "EventTask"):
            self.func(*self.args, **self.kwargs)
            self.is_running = False
            self.trig_count += 1
            self.last_trig = time.time()

        if self.use_thread:
            Thread(target=lambda: _run(self), name=self.name).start()

        elif self.use_threadpool:
            self.task_threadpool.submit(_run, self)



        else:
            self.func(*self.args, **self.kwargs)
            self.is_running = False
            self.trig_count += 1
            self.last_trig = time.time()



class EventTaskGroup(EventTask):
    "一个事件组"
    def __init__(self,
                 name: str = "EventType",
                 max_trig: int = -1,
                 cooldown: float = 0.0,
                 tasks: List[EventTask] = None,
                 allow_async: bool = False,
                 use_thread: bool = False,
                 on_error: Literal["ignore", "strict"] = "strict",
                 ):
        """
        构造一个事件类型，传递给事件进行操作

        :param name: 事件类型名称
        :param max_trig: 最大触发次数
        :param cooldown: 冷却时间
        :param tasks: 任务列表
        :param allow_async: 是否允许异步
        :param use_thread: 执行任务时是否使用线程
        :param on_error: 出现错误时的处理方式
        """
        super().__init__(None, None, None, name, max_trig, cooldown, allow_async, on_error, use_thread, None)
        self.tasks = tasks or []

    def __call__(self, use_thread: bool = None):

        use_thread = use_thread or self.use_thread

        if self.cooldown > 0 and time.time() - self.last_trig < self.cooldown:
            if self.on_error == "strict":
                raise CooldownError(f"任务 {self.name} ({addrof(self)}) 冷却时间未到 ({self.cooldown})")
            else:
                return
    
        if self.max_trig != -1 and self.trig_count >= self.max_trig:
            if self.on_error == "strict":
                raise MaxTrigError(f"任务 {self.name} ({addrof(self)}) 触发次数已达到上限 ({self.max_trig})")
            else:
                return
            
        if self.is_running and not self.allow_async:
                if self.on_error == "strict":
                    raise TaskRunningError(f"任务 {self.name} ({addrof(self)}) 正在运行中")
                else:
                    return
                
        self.is_running = True

        def _run(self: "EventTaskGroup"):
            for task in self.tasks:
                task()
            self.is_running = False
            self.trig_count += 1
            self.last_trig = time.time()

        if use_thread:
            Thread(target=lambda: _run(self), name=self.name).start()

        else:
            _run(self)




class EventSignal:
    "事件信号"
    
    signal_mapping: Dict[Any, List[Callable]] = {}


    @staticmethod
    def connect(func: Callable, identifier: Any):
        """
        增加一个绑定事件

        :param func: 绑定事件执行的任务
        :param identifier: 绑定任务的标识
        """
        if identifier not in EventSignal.signal_mapping:
            EventSignal.signal_mapping[identifier] = []
        EventSignal.signal_mapping[identifier].append(func)

    @staticmethod
    def disconnect(
        func: Callable, 
        identifier: Optional[Any] = None,
        on_error: Literal["ignore", "strict"] = "strict",
        if_dumplicated: Literal["remove_once", "remove_all"] = "remove_all") -> List[Tuple[Callable, Any]]:
        """
        断开一个绑定事件

        :param func: 绑定事件执行的任务
        :param identifier: 绑定任务的标识
        :return List[Tuple[Callable, Any]]: 断开的绑定事件，格式为 [(identifier, func)]
        """
        if identifier:
            if identifier not in EventSignal.signal_mapping:
                if on_error == "strict":
                    raise KeyError(f"信号连接类 {identifier!r} ({addrof(identifier)}) 不在连接池中")
                else:
                    return []
            elif func not in EventSignal.signal_mapping[identifier]:
                if on_error == "strict":
                    raise KeyError(f"任务 {func!r} ({addrof(func)}) 不在信号连接类 {identifier!r} ({addrof(identifier)} 的绑定中")
                else:
                    return []
            result = [(identifier, func) for f in EventSignal.signal_mapping[identifier] if f is func]
            if if_dumplicated == "remove_all":
                while func in EventSignal.signal_mapping[identifier]:
                    EventSignal.signal_mapping[identifier].remove(func)
            elif if_dumplicated == "remove_once":
                EventSignal.signal_mapping[identifier].remove(func)
            if not EventSignal.signal_mapping[identifier]:
                del EventSignal.signal_mapping[identifier]
            return result

        else:
            succeed = False
            results = []

            for _id, func_list in EventSignal.signal_mapping.items():
                try:
                    results.extend([(_id, func) for f in func_list if f is func])
                    if if_dumplicated == "remove_all":
                        while func in func_list:
                            func_list.remove(func)
                    elif if_dumplicated == "remove_once":
                        func_list.remove(func)
                    succeed = True
                except (ValueError, KeyError):
                    pass

            if not succeed:
                if on_error == "strict":
                    raise KeyError(f"任务 {func!r} ({addrof(func)}) 不在任何信号连接类中")
                else:
                    return []
            

            empty_ids = []
            for _id, func_list in EventSignal.signal_mapping.items():
                if not func_list:
                    empty_ids.append(_id)
            
            for _id in empty_ids:   # 不然会报错（RuntimeError: dictionary changed size during iteration）
                del EventSignal.signal_mapping[_id]

            return results
        
    @staticmethod
    def emit(identifier: Any, 
             arguments: Optional[List[Tuple[Callable, Iterable, Dict]]] = None, 
             default_arguments: Optional[Tuple[Iterable, Dict]] = None,
             use_thread: bool = False,
             on_error: Literal["ignore", "strict"] = "ignore") -> int:
        """
        触发一个信号

        :param identifier: 信号标识
        :param arguments: 传递给指定的任务的参数, 格式为 [(callable, args, kwargs)]
        :param default_arguments: 默认参数, 格式为 [(args, kwargs)]
        :param use_thread: 是否使用线程
        :return int: 触发的任务数量
        """     
        if identifier not in EventSignal.signal_mapping:
            if on_error == "strict":
                raise KeyError(f"信号连接类 {identifier!r} ({addrof(identifier)}) 不在连接池中")
            else:
                return 0

        finished = 0
        arguments = arguments or []
        default_arguments = default_arguments or ([], {})
        passed_arguments = [item[0] for item in arguments]

        for task in EventSignal.signal_mapping[identifier]:
            if task in passed_arguments:
                if use_thread:
                    Thread( target=task, 
                            args=arguments[passed_arguments.index(task)][1], 
                            kwargs=arguments[passed_arguments.index(task)][2],
                            name=f"EventSignal.emit({identifier!r})").start()
                else:
                    task(*arguments[passed_arguments.index(task)][1], **arguments[passed_arguments.index(task)][2])
            else:
                if use_thread:
                    Thread(target=task, args=default_arguments[0], kwargs=default_arguments[1], name=f"EventSignal.emit({identifier!r})").start()
                else:
                    task(*default_arguments[0], **default_arguments[1])
            finished += 1

        return finished
    
    @staticmethod
    def clear(identifier: Optional[Any] = None) -> List[Tuple[Callable, Any]]:
        """
        清除所有信号

        :param identifier: 信号标识，None表示清除所有信号
        :return List[Tuple[Callable, Any]]: 清除的信号，格式为 [(identifier, func)]
        """
        if identifier:
            if identifier not in EventSignal.signal_mapping:
                raise KeyError(f"信号连接类 {identifier!r} ({addrof(identifier)}) 不在连接池中")
            result = [(identifier, func) for func in EventSignal.signal_mapping[identifier]]
            del EventSignal.signal_mapping[identifier]
            return result

        else:
            result = []
            for _id, func_list in EventSignal.signal_mapping.items():
                result.extend([(identifier, func) for func in func_list])
                del EventSignal.signal_mapping[_id]
            return result
        
        
    @staticmethod
    def get_bindings(identifier: Optional[Union[Any, Iterable[Any]]] = None, 
                        func: Optional[Union[Callable, Iterable[Callable]]] = None,
                        on_error: Literal["strict", "ignore"] = "strict") \
                            -> List[Tuple[Any, Callable]]:
        """
        获取绑定连接

        :param identifier: 信号标识，None表示所有信号
        :param func: 绑定任务，None表示所有任务
        :return List[Tuple[Any, Callable]: 绑定连接，格式为 [(identifier, func)]
        """
        result = []
        if not identifier:

            if not func:
                for _id, tasks in EventSignal.signal_mapping.items():
                    for task in tasks:
                        result.append((_id, task))

            else:
                funcs = func
                for _id, tasks in EventSignal.signal_mapping.items():
                    for task in tasks:
                        if task in funcs:
                            result.append((_id, task))

            if not result and on_error == "strict":
                    raise KeyError(f"任务 {func!r} ({addrof(func)}) 不在任何信号连接类中")

        else:

            ids = identifier if isinstance(identifier, Iterable) else [identifier]
            for _id in ids:

                if _id not in EventSignal.signal_mapping:
                    if on_error == "strict":
                        raise KeyError(f"信号连接类 {_id!r} ({addrof(_id)}) 不在连接池中")
                    else:
                        continue

                if not func:
                    for task in EventSignal.signal_mapping[_id]:
                        result.append((_id, task))

                else:
                    funcs = func if isinstance(func, Iterable) else [func]
                    for task in EventSignal.signal_mapping[_id]:
                        if task in funcs:
                            result.append((_id, task))

        return result


    @staticmethod
    def count_bindings(identifier: Optional[Union[Any, Iterable[Any]]] = None,
                        func: Optional[Union[Callable, Iterable[Callable]]] = None) -> int:
        """
        统计绑定连接数量

        :param identifier: 信号标识，None表示所有信号
        :param func: 绑定任务，None表示所有任务
        :return int: 绑定连接数量
        """
        return len(EventSignal.get_bindings(identifier, func, "ignore"))
    







if __name__ == "__main__":

    def time_wasting_task():
        print("1 + 1 = 3")
        time.sleep(1)
        print("1 + 1 = 2")

    def time_wasting_task_2():
        print("2 + 2 = 3")
        time.sleep(1)
        print("2 + 2 = 4")

    def time_wasting_task_3():
        print("3 + 3 = 6")
        time.sleep(1)
        print("3 + 3 = 5")

    # task1 = EventTask(time_wasting_task, [], {}, "test", max_trig=3, cooldown=0.5, use_thread=True, allow_async=True)
    # task2 = EventTask(time_wasting_task_2, [], {}, "test", max_trig=3, cooldown=0.5, use_thread=True, allow_async=True)
    # task3 = EventTask(time_wasting_task_3, [], {}, "test", max_trig=3, cooldown=0.5, use_thread=True, allow_async=True)

    # task_group = EventTaskGroup("test_group", max_trig=3, cooldown=0.5, tasks=[task1, task2, task3], use_thread=True, allow_async=True)
    # task_group(True)
    # task_group(True)
    f = lambda x: print(x)
    f1 = lambda: f(114514)
    f2 = lambda: f(1919810)
    EventSignal.connect(f1, "test1")
    EventSignal.connect(f2, "test2")
    EventSignal.connect(f2, "test2")
    EventSignal.connect(f2, "test2")
    EventSignal.disconnect(f2, if_dumplicated="remove_once")
    EventSignal.emit("test2")
    EventSignal.emit("test2")
    EventSignal.emit("test2")
    EventSignal.emit("test1")




