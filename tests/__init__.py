"""单元测试"""

import unittest

from .classobjects import ClassObjectMultiTest, ClassObjectStudentTest
from .classobjects.pydantic_test import PydanticConversionTest
from .classobjects.complex_pydantic_test import ComplexPydanticTest
from .algorithm import AlgorithmMultiTest
from .events import TaskTest, BroadcastTest


def test_suite():
    """
    返回测试套件。
    """
    suite = unittest.TestSuite()
    suite.addTest(ClassObjectStudentTest())
    suite.addTest(ClassObjectMultiTest())
    suite.addTest(AlgorithmMultiTest())
    suite.addTest(TaskTest())
    suite.addTest(BroadcastTest())
    suite.addTest(PydanticConversionTest())
    suite.addTest(ComplexPydanticTest())
    return suite

__all__ = [
    "ClassObjectMultiTest",
    "AlgorithmMultiTest",
    "TaskTest",
    "ClassObjectStudentTest",
    "PydanticConversionTest",
    "ComplexPydanticTest",
    "test_suite"
]
