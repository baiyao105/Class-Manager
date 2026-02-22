"""
单元化测试主程序。

目前还没写多少，后续会慢慢补充
"""

import time
import unittest
st = time.time()
from tests import test_suite
import utils # type: ignore

print(f"全包导入用时: {time.time() - st:.3f}秒") # 目测很慢是因为pygame和更新检测

# from utils.logger import Logger
# Logger.set_capture_stdstream(False, False)

if __name__ == "__main__":
    suite = test_suite()
    unittest.TextTestRunner(verbosity=2, tb_locals=True).run(suite)