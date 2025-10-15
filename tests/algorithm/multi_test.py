
import unittest
from utils.algorithm import *


class AlgorithmMultiTest(unittest.TestCase):

    def test_ctypes(self):
        int8_1 = Int8(114)
        self.assertEqual(int8_1, 114, "由原生int构造的重载C数据类型应当符合构造数值")
        int8_2 = Int8(1)

        self.assertEqual(int8_1 + int8_2, 115, "重载C数据类型应当支持原生的数学运算")
        self.assertEqual(int8_1 * int8_2, 114, "重载C数据类型应当支持原生的数学运算")
        self.assertEqual(int8_1 >> int8_2, 57, "重载C数据类型应当支持原生的位运算")

        self.assertEqual(51 - int8_1, -63, "重载C数据类型应当正确实现了与其他数据类型的__rsub__等方法")
        self.assertEqual(int8_1 + 14, -128, "重载C数据类型应当具有C的自然溢出等特征") # 虽然我设计这个的最初目的只是为了玩抽象（


        my_cfloat = cdatatype(c_float, "my_cfloat")
        self.assertEqual(my_cfloat(1.0), 1.0, "自定义C数据类型应当支持构造函数")
        # 浮点数精度问题（那很具有C特征了
        self.assertNotEqual(my_cfloat(0.1) + my_cfloat(0.2), 0.3, "自定义C数据类型应当具有C数据类型的特征")
        self.assertEqual(my_cfloat(0.1) + my_cfloat(0.2), 0.30000001192092896, "自定义C数据类型应当具有C数据类型的特征")

        my_cdouble = cdatatype(c_double, "my_cdouble")
        self.assertEqual(my_cdouble(1.0), 1.0, "自定义C数据类型应当支持构造函数")
        self.assertNotEqual(my_cdouble(0.1) + my_cdouble(0.2), 0.3, "自定义C数据类型应当具有C数据类型的特征")
        self.assertEqual(my_cdouble(0.1) + my_cdouble(0.2), 0.30000000000000004, "自定义C数据类型应当具有C数据类型的特征")


    def test_function(self):
        test_range1 = steprange(0, 10, 5)
        self.assertEqual(list(test_range1), [0, 2.5, 5, 7.5, 10], "steprange应当正确生成指定元素数均匀分布的序列")
        test_range2 = steprange(1.75, -25, 5)
        self.assertEqual(list(test_range2), [1.75, -4.9375, -11.625, -18.3125, -25], 
                            "steprange应当正确生成指定元素数均匀分布的序列")
        

        uuid1 = gen_uuid()
        uuid2 = gen_uuid()
        self.assertNotEqual(uuid1, uuid2, "gen_uuid应当生成不同的UUID")



    def test_datatypes(self):

        stack: Stack[int] = Stack()
        stack.push(1)
        stack.push(2)
        stack.push(3)
        self.assertEqual(stack.pop(), 3, "Stack应当正确实现栈操作")
        self.assertEqual(stack.pop(), 2, "Stack应当正确实现栈操作")
        self.assertEqual(stack.peek(), 1, "Stack应当正确实现栈操作")
        self.assertEqual(stack.size(), 1, "Stack应当正确实现栈操作")
        self.assertEqual(stack.is_empty(), False, "Stack应当正确实现栈操作")
        stack.push(4)
        self.assertEqual(stack.pop(), 4, "Stack应当正确实现栈操作")
        stack.clear()
        self.assertEqual(stack.size(), 0, "Stack应当正确实现栈操作")
        self.assertEqual(stack.is_empty(), True, "Stack应当正确实现栈操作")

        def test_thread() -> str:
            time.sleep(0.01)
            return "我是返回值"
        thread = Thread(target=test_thread)
        thread.start()
        self.assertEqual(thread.join(), "我是返回值", "Thread应当正确实现返回值处理")
        self.assertEqual(thread.is_alive(), False, "Thread应当可以实现一般Thread的功能")
        self.assertEqual(thread.return_value, "我是返回值", "Thread应当正确实现返回值处理")

        mutex = Mutex()

        mutex.acquire()
        def test_thread2():
            nonlocal mutex
            mutex.acquire()
        thread2 = Thread(target=test_thread2)
        thread2.start()
        time.sleep(0.001)
        self.assertEqual(thread2.is_alive(), True, "Mutex应当正确实现互斥功能")
        mutex.release()
        time.sleep(0.001)
        self.assertEqual(thread2.is_alive(), False, "Mutex应当正确实现互斥功能")
        self.assertEqual(mutex.locked(), True, "Mutex应当正确判断是否锁住")
        mutex.release()

        frame_counter = FrameCounter()
        frame_counter.start()
        time.sleep(0.001)
        self.assertGreater(frame_counter.counted_frames, 0, "FrameCounter应当正确计算帧数")
        self.assertGreater(frame_counter.framerate, 0, "FrameCounter应当正确计算帧率")
        frame_counter.stop()
        self.assertEqual(frame_counter.framerate, 0, "FrameCounter应当正确停止计数")

    def runTest(self):
        self.test_ctypes()
        self.test_function()
        self.test_datatypes()



__all__ = ["AlgorithmMultiTest"]