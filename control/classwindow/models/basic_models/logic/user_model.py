"""
用户登录相关模型。
"""

from __future__ import annotations

from typing import Optional
from utils import login


class LoginError(RuntimeError):
    "登录出错。"


class UserModel:

    def __init__(self):
        """
        构造函数。
        """
        self.__current_user: Optional[str] = None


    @property
    def current_user(self):
        return self.__current_user

    @current_user.setter
    def current_user(self, value: str):
        raise AttributeError("current_user不可以手动设置，要等用户自行登陆后才会变更")

    def request_login(self) -> str:
        name = login()
        self.__current_user = name
        return name


