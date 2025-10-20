"""单元测试"""

import unittest

from .algorithm import AlgorithmMultiTest
from .classobjects import ClassObjectMultiTest


def test_suite():
    """
    返回测试套件。
    """
    suite = unittest.TestSuite()
    suite.addTest(ClassObjectMultiTest())
    suite.addTest(AlgorithmMultiTest())
    return suite


__all__ = ["AlgorithmMultiTest", "ClassObjectMultiTest", "test_suite"]
