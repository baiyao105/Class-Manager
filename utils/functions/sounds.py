"""
播放声音和音乐的工具
"""


import os
from threading import Thread
from utils.logger import Logger
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "114514" # 可以让pygame闭嘴


import pygame

pygame.mixer.init()

# 初始化pygame的混音器

__all__ = [
    "play_sound",
    "play_music",
    "stop_music",
]


def play_sound(filename: str, volume: float = 1):
    """
    异步播放声音文件

    :param filename: 声音文件路径
    :param volume: 音量大小，范围0.0-1.0
    """
    Thread(
        target=_play_sound,
        args=(filename, volume),
        daemon=True,
        name="SoundPlayerThread",
    ).start()


def _play_sound(filename: str, volume: float = 1, loop: int = 0, fade_ms: int = 0):
    """
    内部函数：实际播放声音的实现

    :param filename: 声音文件路径
    :param volume: 音量大小，范围0.0-1.0
    :param loop: 循环播放次数，0表示播放一次
    :param fade_ms: 淡入效果的毫秒数
    """
    try:
        sound = pygame.mixer.Sound(filename)
        sound.set_volume(volume)
        sound.play(loops=loop, fade_ms=fade_ms)
    except (OSError, pygame.error) as unused:  # pylint: disable=unused-variable
        Logger.log_exc("播放声音失败")


def play_music(filename: str, volume: float = 0.5, loop: int = 0, fade_ms: int = 0):
    """
    播放背景音乐

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
    except (OSError, pygame.error) as unused:  # pylint: disable=unused-variable
        Logger.log_exc("播放音乐失败")


def stop_music():
    """停止当前正在播放的背景音乐"""
    pygame.mixer.music.stop()
