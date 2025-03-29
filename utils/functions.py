import cv2
import pygame
import sys
import time
import functools
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QMessageBox
from typing import Callable, Literal
from threading import Thread
from utils.basetypes import Base
def addrof(obj) -> str:
    """获取对象的内存地址
    
    :param obj: 任意Python对象
    :return: 十六进制格式的内存地址字符串
    """
    return "0x" + hex(id(obj))[2:].zfill(16).upper()

def mat_to_pixmap(mat: cv2.Mat) -> QPixmap:
    """将OpenCV图像矩阵转换为Qt像素图
    
    :param mat: OpenCV图像矩阵
    :return: 转换后的QPixmap对象
    """
    height, width, channels = mat.shape
    bytes_per_line = channels * width
    qimage = QImage(mat.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
    pixmap = QPixmap.fromImage(qimage)
    return pixmap




def repeat(count):
    """装饰器，用于重复执行函数指定次数

    :param count: 重复执行的次数
    :return: 装饰后的函数

    Demo:
    >>> @repeat(3)
    ... def func():
    ...     print("hello")
    >>> func()
    hello
    hello
    hello
    """
    def executor(func):
        def wrapper(*args, **kwargs):
            for _ in range(count):
                func(*args, **kwargs)
        return wrapper
    return executor


nl = "\n"
"""换行符常量，用于在格式化字符串中插入换行"""




pygame.mixer.init()
# 初始化pygame的混音器

def play_sound(filename, volume=1):
    """异步播放声音文件
    
    :param filename: 声音文件路径
    :param volume: 音量大小，范围0.0-1.0
    """
    Thread(target=_play_sound, args=(filename, volume), daemon=True, name="SoundPlayerThread").start()

def _play_sound(filename, volume=1, loop:int=0, fade_ms:int=0):
    """内部函数：实际播放声音的实现
    
    :param filename: 声音文件路径
    :param volume: 音量大小，范围0.0-1.0
    :param loop: 循环播放次数，0表示播放一次
    :param fade_ms: 淡入效果的毫秒数
    """
    try:
        sound = pygame.mixer.Sound(filename)
        sound.set_volume(volume)
        sound.play(loops=loop, fade_ms=fade_ms)
    except BaseException as unused:
        Base.log_exc("播放声音失败")


def play_music(filename:str, volume:float=0.5, loop:int=0, fade_ms:int=0):
    """播放背景音乐
    
    :param filename: 音乐文件路径
    :param volume: 音量大小，范围0.0-1.0
    :param loop: 循环播放次数，0表示播放一次
    :param fade_ms: 淡入效果的毫秒数
    """
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops=loop, fade_ms=fade_ms)
    except BaseException as unused:
        Base.log_exc("播放音乐失败")

def stop_music():
    """停止当前正在播放的背景音乐"""
    pygame.mixer.music.stop()


def canbe(value, _class:type):
    """检查一个值是否可以转换为指定类型
    
    :param value: 要检查的值
    :param _class: 目标类型
    :return: 如果可以转换则返回True，否则返回False
    
    示例: canbe("11.4514", float) == True
    """
    try:
        _class(value)
        return True
    except BaseException as unused:
        return False



def pass_exceptions(func):
    """装饰器，用于捕获函数执行过程中抛出的异常
    
    :param func: 要装饰的函数
    :return: 装饰后的函数
    
    示例:
    >>> @pass_exceptions
    ... def func():
    ...     raise Exception("错误示例")

    >>> func()
    ---------------------------ExceptionCaught-----------------------------
    执行函数'func'时捕获到异常
    -----------------------------------------------------------------------
    Traceback (most recent call last):
     __错误信息__
       return func(*args, **kwargs)
     __错误信息__
       raise Exception("错误示例")
    Exception: 错误示例
    -----------------------------------------------------------------------
    builtins.Exception: 错误示例
    Stacktrace:
     at __main__.pass_exceptions.<locals>.wrapper(main.py:114514)
    -----------------------------------------------------------------------
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseException as unused:
            Base.log_exc(f"执行函数{repr(func.__name__)}时捕获到异常", f"pass_exceptions -> {func.__name__}")

    return wrapper

def exc_info_short(desc:str="出现了错误：", level:Literal["I", "W", "E"]="E"):
    "简单报一句错"
    Base.log(level, f"{desc}  [{sys.exc_info()[1].__class__.__name__}] {sys.exc_info()[1].args[0] if sys.exc_info()[1].args else ''}")

