"""
执行命令相关的模型。
"""

import os
import sys
from typing import Any

from utils.basetypes import Base
from utils.system import system_lined, CommandOutput

class CommandModel:

    def __init__(self):
        self.terminal_locals: dict[str, Any] = {}
        "终端的本地变量"

        
    def exec_command(self, command: str) -> Any:
        """
        执行一行字符串形式的Python命令。
        
        :param command: 要执行的命令
        :return: 命令的返回值
        """
        Base.log("I", f"执行命令：{repr(command)}", "MainWindow.exec_command")
        self.terminal_locals.update({"self": self})
        self.terminal_locals.update(globals())
        self.terminal_locals.update(sys.modules["__main__"].__dict__)
        ret = None
        try:
            ret = eval(command, globals(), self.terminal_locals)
        except SyntaxError:
            exec(f"{command}", globals(), self.terminal_locals)
        return ret
    
    def exec_cmdline(self, cmdline: str, encoding: str = "utf-8",
                        show_output: bool = True, cwd: str = os.getcwd()) -> CommandOutput:
        return system_lined(cmdline, encoding=encoding, show_output=show_output, cwd=cwd)

