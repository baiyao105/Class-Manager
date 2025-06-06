"""
关于数字的函数
"""

import time
import random
from typing import Union, List



def utc(prec: int = 3):
    """
    获取当前UTC时间戳

    :param prec: 精度，表示小数点后的位数
    :return: 指定精度的UTC时间戳
    """
    return int(time.time() * (10**prec))


def steprange(
    start: Union[int, float], stop: Union[int, float], step: int
) -> List[float]:
    """
    生成step步长的从start到stop的列表

    :param start: 起始值
    :param stop: 结束值
    :param step: 步长
    :return: 从start到stop的列表

    举个例子

    >>> steprange(0, 10, 5)
    [0, 2.5, 5.0, 7.5, 10]
    """
    if (stop - start) % step != 0:
        return [start + i * (int(stop - start) / step) for i in range(step)][:-1] + [
            stop
        ]
    else:
        return [start + i * (int(stop - start) / (step - 1)) for i in range(step)]


def addrof(obj) -> str:
    """
    获取对象的内存地址

    :param obj: 任意Python对象
    :return: 十六进制格式的内存地址字符串
    """
    return "0x" + hex(id(obj))[2:].zfill(16).upper()


def gen_uuid(length: int = 32) -> str:
    "生成一个长32位的uuid"
    return "".join([str(random.choice("0123456789abcdef")) for _ in range(length)])


def get_time():
    "获得当前时间"
    lt = time.localtime()
    return (
        f"{lt.tm_year}-{lt.tm_mon:02}-{lt.tm_mday:02} "
        + f"{lt.tm_hour:02}:{lt.tm_min:02}:{lt.tm_sec:02}"
        + f".{int((time.time()%1)*1000):03}"
    )
