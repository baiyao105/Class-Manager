"""
和快捷命令有关的模型。
"""
from __future__ import annotations

import os
import pickle
import functools
from typing import Any, Callable, Literal, ParamSpec, TypeVar

from utils.basetypes import Base
from utils.qtconfig import InfoBarIcon, PushButton, QTimer

from widgets.custom.ListView import ListViewItemDataType

from .class_ui_model import MixinSuperType


P = ParamSpec("P")
T = TypeVar("T")

class Command:
    """快捷命令"""

    def __init__(self, key: str, name: str, func: Callable[..., Any], mode: Literal["method", "normal"]):
        self.name = name
        self.key = key
        self.usage = 0
        self.orig_func = func
        self.callable: Callable[..., Any] | None = None
        self.mode = mode
    

    def __repr__(self):
        return (
            f"Command(key={repr(self.key)}, "
            f"name={repr(self.name)}, orig_func={repr(self.orig_func)},"
            f"mode={repr(self.mode)}, usage={repr(self.usage)}"
        )

class FastCommandModel(MixinSuperType):

    lately_used_commands: list[Command] = []
    command_list: list[Command] = []

    def __init__(
        self, 
        current_user: str, 
        class_name: str, 
        class_key: str, 
        save_path: str | None = None
    ):
        Base.log("D", "初始化FastCommandModel", "FastCommandModel.__init__")

        try:
            with open(
                os.getcwd()
                + os.sep
                + f"chunks/{self.current_user}/quick_commands.pkl",
                "rb",
            ) as f:
                self.load_quick_settings_from_list(pickle.load(f))
        except FileNotFoundError:
            Base.log("W", "未找到快速命令文件，重置为默认", "MainWindow.load_settings")

        self.selected_quick_command: list[Command | None] = [
            [c for c in self.command_list if c.key == "new_template"][0],
            [c for c in self.command_list if c.key == "manage_templates"][0],
            [c for c in self.command_list if c.key == "show_all_history"][0],
            [c for c in self.command_list if c.key == "scoring_select"][0],
            [c for c in self.command_list if c.key == "homework_score_sum_up"][0],
            [c for c in self.command_list if c.key == "cleaning_score_sum_up"][0],
            [c for c in self.command_list if c.key == "show_attendance"][0],
            [c for c in self.command_list if c.key == "detect_new_version"][0],
            [c for c in self.command_list if c.key == "show_update_log"][0],
        ]

        self.refresh_quick_command_btns()
        self.HyperlinkLabel.clicked.connect(self.edit_fast_command_btns)
        self.recent_command_update_timer = QTimer(self)
        "最近命令更新定时器"
        self.recent_command_update_timer.timeout.connect(self.update_recent_command_btns)
        self.recent_command_update_timer.start(300)

    @property
    def command_key_list(self) -> list[str | None]:
        "快捷键列表（返回功能的key）"
        return [c.key if c else None for c in self.selected_quick_command]



    @staticmethod
    def as_method_command(key: str, name: str):
        """
        快捷命令装饰器。

        :param key: 键值
        :param name: 命令名称
        """

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            cmd = Command(key, name, func, "method")
            FastCommandModel.command_list.append(cmd)
            cmd.orig_func = func

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                cmd.usage += 1
                if cmd in FastCommandModel.lately_used_commands:
                    FastCommandModel.lately_used_commands.remove(cmd)
                FastCommandModel.lately_used_commands.append(cmd)
                return func(*args, **kwargs)

            cmd.callable = wrapper
            return wrapper

        return decorator
    

    def refresh_quick_command_btns(self, reset_callable: bool = True):
        """
        刷新快捷命令按钮
        
        :param reset_callable: 是否重置按钮的回调函数
        """
        for i in range(1, 9 + 1):
            btn: PushButton = getattr(self, f"PushButton_{i}")
            item = self.selected_quick_command[i - 1]
            if item is not None:
                btn.setText(item.name)
                if reset_callable:
                    try:
                        btn.clicked.disconnect()
                    except RuntimeError as e:
                        Base.log("W", f"尝试断开未连接的信号：(PushButton_{i}) {e}")
                    cmd = item
                    func = cmd.callable

                    if func:
                        if cmd.mode == "method":
                            # 因为不是直接调用的类方法，需要手动传一个self
                            btn.clicked.connect(lambda *, f=func: f(self)) # type: ignore
                        else:
                            btn.clicked.connect(lambda *, f=func: f()) # type: ignore

                btn.setEnabled(True)
            else:
                btn.setText("未指定")
                btn.setEnabled(False)
            btn.update()


    def edit_fast_command_btns(self):
        """
        编辑快捷命令按钮，如果已经处于编辑状态则退出编辑状态
        """
        self.refresh_quick_command_btns(True)
        if not hasattr(self, "fast_command_edit_state"):
            self.fast_command_edit_state = False
        self.fast_command_edit_state = not self.fast_command_edit_state

        if self.fast_command_edit_state:
            Base.log("I", "进入快捷命令编辑模式", "FastCmdModel.edit_fast_command_btns")
            self.CaptionLabel.setText("快速管理 (编辑中)")
            self.HyperlinkLabel.setText("完成")
            for i in range(1, 9 + 1):
                btn: PushButton = getattr(self, f"PushButton_{i}")

                def _select_command(btn: PushButton, i: int = i):
                    def _set_quick_command(cmd: Command | None, i: int = i) -> None:
                        self.selected_quick_command[i - 1] = cmd
                        Base.log(
                            "I",
                            f"第{i}个快捷命令已被更改：{btn.text()} -> {cmd.name if cmd is not None else '未指定'}",
                        )
                        btn.setText(cmd.name if cmd is not None else "未指定")
                        self.refresh_quick_command_btns(False)
                        for i in range(1, 9 + 1):
                            _btn: PushButton = getattr(self, f"PushButton_{i}")
                            _btn.setEnabled(True)

                    list_view_data: list[ListViewItemDataType] = []
                    list_view_data.append(("选择要设置的快捷命令", lambda: None))
                    list_view_data.extend([("", lambda: None)] * 2)
                    for c in self.command_list:
                        text = c.name
                        func = lambda *, c=c: (
                            _set_quick_command(c),
                            self.refresh_quick_command_btns(False)
                        )
                        list_view_data.append((text, func))
                    list_view_data.append(("<不指定>", lambda: _set_quick_command(None)))

                    self.list_view(
                        list_view_data,
                        "选择要设置的快捷命令",
                        self,
                        select_once_then_exit=True
                    )

                try:
                    btn.clicked.disconnect()
                except RuntimeError as e:
                    Base.log(
                        "W",
                        f"尝试断开未连接的信号：(PushButton_{i}) {e}",
                        "FastCmdModel.edit_fast_command_btns",
                    )
                    
                def _on_click(
                    select_command_callable: Callable[[PushButton], None] = _select_command, 
                    btn: PushButton = btn
                ):
                    select_command_callable(btn)
                    self.refresh_quick_command_btns(False)

                btn.clicked.connect(lambda: _on_click())
                btn.setEnabled(True)

        else:
            Base.log("I", "退出快捷命令编辑模式", "FastCmdModel.edit_fast_command_btns")
            self.CaptionLabel.setText("快速管理")
            self.show_tip(
                "提示", "快捷命令保存成功", duration=3275, icon=InfoBarIcon.SUCCESS
            )
            self.HyperlinkLabel.setText("编辑")
            self.refresh_quick_command_btns(True)
            self.save_quick_command_config()


    def save_quick_command_config(self):
        Base.log("I", "保存快捷命令配置", "FastCmdModel.save_fast_command_config")
        pickle.dump(
            self.command_key_list,
            open(
                os.path.abspath(f"chunks/{self.current_user}/quick_commands.pkl"),
                "wb",
            ),
            pickle.HIGHEST_PROTOCOL,
        )
        self.refresh_quick_command_btns()

    def load_quick_settings_from_list(self, cmdlist: list[str]):
        "从名称或者key值列表中加载快捷命令"
        self.selected_quick_command = [None] * 9
        avaliable = [c.name for c in self.command_list]
        avaliable2 = [c.key for c in self.command_list]

        for i in range(9):
            if cmdlist[i] in avaliable:
                self.selected_quick_command[i] = [
                    c for c in self.command_list if c.name == cmdlist[i]
                ][0]
            elif cmdlist[i] in avaliable2:
                self.selected_quick_command[i] = [
                    c for c in self.command_list if c.key == cmdlist[i]
                ][0]
            else:
                Base.log(
                    "W", f"快捷命令{repr(cmdlist[i])}不存在，将会重置为默认(未指定)"
                )
                self.selected_quick_command[i] = None

        self.refresh_quick_command_btns()

    
    def update_recent_command_btns(self):
        """
        更新最近使用命令按钮。
        """

        for btn in [self.PushButton_10, self.PushButton_11, self.PushButton_12]:
            try:
                btn.clicked.disconnect(None)
            except RuntimeError:
                pass

            
        lately_used_commands = FastCommandModel.lately_used_commands
        callable_last_1 = lately_used_commands[-1] if lately_used_commands else None
        callable_last_2 = lately_used_commands[-2] if len(lately_used_commands) >= 2 else None
        callable_last_3 = lately_used_commands[-3] if len(lately_used_commands) >= 3 else None

        self.PushButton_10.setText(callable_last_1.name if callable_last_1 else "暂无")
        self.PushButton_11.setText(callable_last_2.name if callable_last_2 else "暂无")
        self.PushButton_12.setText(callable_last_3.name if callable_last_3 else "暂无")

        def _exec_command(cmd: Command | None):
            if cmd and cmd.callable:
                if cmd.mode == "method":
                    # 因为不是直接调用的类方法，需要手动传一个self
                    cmd.callable(self)
                else:
                    cmd.callable()

        self.PushButton_10.clicked.connect(lambda cmd=callable_last_1: _exec_command(cmd))
        self.PushButton_11.clicked.connect(lambda cmd=callable_last_2: _exec_command(cmd))
        self.PushButton_12.clicked.connect(lambda cmd=callable_last_3: _exec_command(cmd))


    def stop(self):
        super().stop()
        Base.log("I", "停止更新最近使用命令列表", "FastCmdModel.stop")
        self.recent_command_update_timer.stop()