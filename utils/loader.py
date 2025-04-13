"""
加载文件，用来给多个文件做适配
"""
from typing import Literal


def log(level: Literal["D", "I", "W", "E", "C"], content: str, source: str):
    """
    记录日志。
    
    :param level: 日志级别，D: debug, I: info, W: warning, E: error, C: critical
    :param content: 日志内容
    :param source: 日志来源
    :return: None
    """
    print(f"{level} {content} {source}")