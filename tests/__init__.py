"""单元测试"""

import unittest

from .classobjects import ClassObjectMultiTest, ClassObjectStudentTest
from .algorithm import AlgorithmMultiTest
from .events import TaskTest


def test_suite():
    """
    返回测试套件。
    """
    suite = unittest.TestSuite()
    suite.addTest(ClassObjectStudentTest())
    suite.addTest(ClassObjectMultiTest())
    suite.addTest(AlgorithmMultiTest())
    suite.addTest(TaskTest())
    return suite

__all__ = [
    "ClassObjectMultiTest",
    "AlgorithmMultiTest",
    "TaskTest",
    "ClassObjectStudentTest",
    "test_suite"
]