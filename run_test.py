"""
单元化测试主程序。

目前还没写多少，后续会慢慢补充
"""

import sys
import unittest
from tests import test_suite

if __name__ == "__main__":
    suite = test_suite()
    unittest.TextTestRunner(verbosity=2, tb_locals=True, stream=sys.stdout).run(suite)