"""单元测试"""

import unittest
from .classobjects import ClassObjectMultiTest
from .algorithm import AlgorithmMultiTest


def test_suite():
    """
    返回测试套件。
    """
    suite = unittest.TestSuite()
    suite.addTest(ClassObjectMultiTest())
    suite.addTest(AlgorithmMultiTest())
    return suite

__all__ = [
    "ClassObjectMultiTest",
    "AlgorithmMultiTest",
    "test_suite"
]