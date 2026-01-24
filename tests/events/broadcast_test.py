
import unittest
from typing import Any
from utils.events.broadcast import BroadcastDispatcher, BroadcastReceiver
from utils.events.event import Event

class BroadcastTest(unittest.TestCase):

    def runTest(self):

        RE = BroadcastReceiver.RE_PATTERN_PREFIX

        dispatcher = BroadcastDispatcher(name="Dispatcher(Test1)")
        number = 114514
        string = "孩子们我没招了"
        key = None
        def _some_task():
            nonlocal number
            number += (1919810 - 114514)

        def _some_task_2(**kwargs: dict[str, Any]):
            nonlocal string, key
            key = kwargs.get(BroadcastReceiver.RECEIVED_KEY, None)
            string += "yy"


        self.assertEqual(number, 114514, "这个根本不可能发生吧")

        receiver1 = BroadcastReceiver(r"I_AM_A_BORADCAST_EVENT", _some_task, name="Receiver(Test1)")
        receiver2 = BroadcastReceiver(RE + r"^I_AM_A_.+$", _some_task_2, name="Receiver(Test2)")

        dispatcher.register(receiver1)
        dispatcher.register(receiver2)

        dispatcher.broadcast(r"I_AM_A_BORADCAST_EVENT")
        dispatcher.broadcast(Event(r"I_AM_A_BRILIANT_EVENT"))

        self.assertEqual(receiver1.called_times, 1, "广播接收器应当可以正确接收事件")
        self.assertEqual(receiver2.called_times, 2, "正则表达式广播接收器应当可以正确接收事件")

        self.assertEqual(number, 1919810, "广播接收器应当可以正确执行任务")
        self.assertEqual(string, "孩子们我没招了yyyy", "正则表达式广播接收器应当做到可以正确执行任务")
        self.assertEqual(key, r"I_AM_A_BRILIANT_EVENT", "广播接收器应当可以正确获取接收到的标签名")

        number2 = 0
        def _some_task_with_variant_args(I_am_a_positional_arg: int, *, I_am_a_keyword_arg: int):
            nonlocal number2
            number2 = I_am_a_positional_arg + I_am_a_keyword_arg

        dispatcher.unregister(receiver1)
        dispatcher.unregister(receiver2)


        receiver3 = BroadcastReceiver(r"I_AM_A_BRILIANT_EVENT", _some_task_with_variant_args, name="Receiver(Test3)")
        dispatcher.register(receiver3)
        dispatcher.broadcast(
            Event(
                r"I_AM_A_BRILIANT_EVENT", 
                args=(114514, 1919810), 
                kwargs={"I_am_a_keyword_arg": 1919810, "I_am_a_unused_arg": "你好"}
            )
        )
        self.assertEqual(number2, 114514 + 1919810, "广播接收器应当可以正确执行任务")
        self.assertEqual(receiver3.called_times, 1, "广播接收器应当可以正确接收事件并处理参数列表")

        dispatcher.unregister(receiver3)
        number4 = 0
        number5 = 0
        number6 = 0

        def _task_1(x: int, a: int):
            nonlocal number4, number5, number6
            number4 += x + a
            number5 = a

        def _task_2(x: int, b: int):
            nonlocal number4, number5, number6
            number4 += x - b
            number6 = b

        receiver4 = BroadcastReceiver(r"I_AM_A_BRILIANT_EVENT", _task_1, name="Receiver(Test4)")
        receiver5 = BroadcastReceiver(r"I_AM_A_BRILIANT_EVENT", _task_2, name="Receiver(Test5)")
        dispatcher.register(receiver4)
        dispatcher.register(receiver5)
        dispatcher.broadcast(r"I_AM_A_BRILIANT_EVENT", 114514, a=1919, b=810)
        self.assertEqual(number4, 114514 + 1919 + 114514 - 810, "广播接收器应当可以正确执行任务")
        self.assertEqual(number5, 1919, "广播接收器应当可以正确执行任务")
        self.assertEqual(number6, 810, "广播接收器应当可以正确执行任务")
        self.assertEqual(receiver4.called_times, 1, "广播接收器应当可以正确接收事件并处理参数列表")
        self.assertEqual(receiver5.called_times, 1, "广播接收器应当可以正确接收事件并处理参数列表")

        @BroadcastDispatcher.as_listener_of(dispatcher, r"re:^I_AM_NOT_A_.+$", name="Receiver(Test6)")
        def _I_am_a_receiver(x: int, a: int, b: int):
            nonlocal number4, number5, number6
            number4 = x + a - b + 114
            number5 = a + 114
            number6 = b + 114

        dispatcher.broadcast(r"I_AM_NOT_A_BRILIANT_EVENT", 114514, a=1919, b=810)

        self.assertEqual(number4, 114514 + 1919 - 810 + 114, "广播接收器应当可以正确执行任务")
        self.assertEqual(number5, 1919 + 114, "广播接收器应当可以正确执行任务")
        self.assertEqual(number6, 810 + 114, "广播接收器应当可以正确执行任务")




__all__ = ["BroadcastTest"]