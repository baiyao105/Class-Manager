
import time
import unittest
from utils.events.tasks import Task

class TaskTest(unittest.TestCase):

    def runTest(self):
        
        something = 1
        self.assertEqual(something, 1, "这个根本不可能发生吧")

        def _func_to_do_something(x: int):
            nonlocal something
            time.sleep(0.1)
            something = x

        task = Task(_func_to_do_something, args=(114514, ), name="TaskToDoSomething", delay=0.2)
        st = time.time()
        task(1919810)
        self.assertEqual(task.running_tasks(), 1, "Task.start应当启动任务并且正常计数总任务量")
        self.assertAlmostEqual(time.time() - st, 0.0, None, "Task.start不应当阻塞", delta=0.005)
        self.assertEqual(something, 1, "task应当按设定的延时启动")
        st = time.time()
        task.join()
        self.assertEqual(task.running_tasks(), 0, "Task.join应当等待任务结束并且正常计数总任务量")
        self.assertAlmostEqual(time.time() - st, 0.3, None, "Task.join应当阻塞，Task应当正确执行函数", delta=0.005)
        self.assertEqual(something, 1919810, "Task应当正确执行函数")
        self.assertFalse(task.is_running(), "Task应当正确判断任务状态")

        something_2 = 1

        def _func_to_do_something_2():
            nonlocal something_2
            something_2 += 1
        
        task_2 = Task(_func_to_do_something_2, name="TaskToDoSomething_2")
        task_2.enable_repeat(3, 0.01)
        task_2()
        task_2()
        task_2()
        task_2.disable_multi_threading()
        self.assertTrue(task_2.is_running(), "Task应当正确判断任务状态")
        with self.assertRaises(RuntimeError, msg="在多线程未启动时重复启动任务应当抛出异常"):
            task_2()
        self.assertEqual(task_2.running_tasks(), 3, "Task.enable_repeat应当启动任务并且正常计数总任务量")
        st = time.time()
        task_2.join()
        self.assertAlmostEqual(time.time() - st, 0.03, None, "Task.enable_repeat应当正确设置重复延时", delta=0.005)
        self.assertEqual(task_2.running_tasks(), 0, "Task.enable_repeat应当等待任务结束并且正常计数总任务量")
        self.assertEqual(something_2, 10, "Task.enable_repeat应当正确执行函数")
        task_2.enable_multi_threading()
        task_2()






__all__ = ["TaskTest"]