"""
侧边栏提示有关的模型。
"""

from __future__ import annotations

import queue
import time
from queue import Queue
from typing import TYPE_CHECKING, Any, Callable
from concurrent.futures import ThreadPoolExecutor

from utils import Base
from utils.algorithm.numeric import addrof
from utils.profiler import profile
from utils.qtconfig import (
    QWidget, QThread, Signal, InfoBarIcon, 
    QIcon, QCloseEvent, Slot
)

from widgets.basic import SideNotice

if TYPE_CHECKING:
    _BaseClass = QWidget
else:
    _BaseClass = object


class SideNoticeModel(_BaseClass):
    """
    侧边栏提示模型。
    
    是一个Mixin类。
    """

    signal_show_tip = Signal(tuple)
    """
    提示更新信号，用于传递需要显示的提示信息。

    这个信号传递元组，然后会构造SideNotice放在TipHandler的队列里。
    """

    @Slot(tuple)
    def slot_show_tip(
        self, 
        args: tuple[
            str, str, QWidget | None, 
            int, InfoBarIcon | QIcon | str | None, 
            str | None, bool, 
            Callable[..., Any] | None, str]):
        """
        显示提示的槽函数。
        """
        self.impl_show_tip(*args)

    signal_place_tip = Signal(SideNotice)
    """
    显示新提示信号，由TipHandler传递。
    
    它如果被传递了会直接在主线程展示这个传过来的SideNotice。
    """

    @Slot(SideNotice)
    def slot_place_tip(self, notice: SideNotice):
        "显示新提示，直接展示传过来的SideNotice对象。"
        Base.log("T", f"在主界面上显示提示 <SideNotice object at <{addrof(notice)}>", 
                 "SideNoticeModel.slot_show_new_tip")
        notice.show()

    
    def __init__(self, master: QWidget | None = None):
        self.side_notice_init_finished = False
        "提示栏初始化完成"
        Base.log("D", "初始化SideNoticeModel", "SideNoticeModel.__init__")
        self.master = master
        # 不调用super().__init__()
        if hasattr(self, 'setParent') and master:
            self.setParent(master)
        self.sidenotice_waiting_order: Queue[SideNotice] = Queue()
        "提示栏等待顺序"
        self.sidenotice_avilable_slots = list(range(5))
        "提示栏可用槽位"
        self.tip_history: list[SideNotice] = []
        self.tip_handler = TipHandler(self)
        "提示处理器"
        self.tip_handler.start()
        "提示历史"
        self.signal_show_tip.connect(self.slot_show_tip)
        self.signal_place_tip.connect(self.slot_place_tip)
        self.side_notice_init_finished = True
        self.show_tip(
            "", "双击项目查看消息记录", duration=5000, further_info="孩子真聪明（bushi"
        )
        

    def show_tip(
        self,
        title: str = "提示",
        content: str = "这是一个提示",
        master: QWidget | None = None,
        icon: InfoBarIcon | QIcon | str | None = None,
        sound: str | None = None,
        duration: int = 5000,
        closeable: bool = True,
        click_command: Callable[..., Any] | None = None,
        further_info: str = "该提示没有详细信息。"
    ):
        """
        向用户发送一个提示

        :param text: 通知显示的文本内容
        :param master: 父窗口对象
        :param icon: 通知图标
        :param sound: 通知出现时播放的声音文件
        :param duration: 通知显示持续时间(毫秒)
        :param closeable: 是否允许用户关闭通知
        :param click_command: 点击通知时的回调函数
        """
        if not hasattr(self, "side_notice_init_finished") or not self.side_notice_init_finished:
            Base.log("W", "提示栏初始化未完成，无法显示提示", "SideNoticeModel.show_tip")
            return
        self.signal_show_tip.emit((
            title, content, master, duration,
            icon, sound, closeable, click_command, further_info
        ))


    def impl_show_tip(self,
        title: str,
        content: str,
        master: QWidget | None,
        duration: int,
        icon: InfoBarIcon | QIcon | str | None,
        sound: str | None,
        closeable: bool,
        click_command: Callable[..., Any] | None,
        further_info: str
    ) -> SideNotice:
        """
        显示提示，是一个接口（喜）（？
        """
        Base.log("D", F"接到提示显示信号，内容：title={title!r}, content={content!r}", "SideNoticeModel._show_tip")
        if master is None:
            master = self

        obj = SideNotice(
            title=title,
            content=content,
            icon=icon,
            sound=sound,
            closeable=closeable,
            click_command=click_command,
            duration=duration,
            master=master,
            further_info=further_info,
        )

        self.sidenotice_waiting_order.put(obj)
        return obj

    def closeEvent(self, event: QCloseEvent):
        event.accept()
        self.stop()
        Base.log("D", "销毁SideNoticeModel", "SideNoticeModel.destroy")
        if self.tip_handler.isRunning():
            self.tip_handler.quit()
            self.tip_handler.requestInterruption()
            st = time.time()
            Base.log("D", "等待提示处理器线程结束", "SideNoticeModel.destroy")
            if not self.tip_handler.wait(3000):
                Base.log("W", "提示处理器线程结束超时 (3000ms)，将会强制结束", "SideNoticeModel.destroy")
                self.tip_handler.terminate()
                self.tip_handler.wait()
            Base.log("D", f"提示处理器线程结束，耗时 {time.time() - st} 秒", "SideNoticeModel.destroy")

        self.tip_handler.return_slot_executor.shutdown(wait=False)
        super().closeEvent(event)

    def stop(self):
        self.tip_handler.requestInterruption()



class TipHandler(QThread):
    "侧边提示处理器"

    return_slot_delay: float = 0.2
    "在展示时间结束后多久才会归还槽位，单位: sec"

    return_slot_executor_workers: int = 30

    
    

    def __init__(self, parent: SideNoticeModel):
        super().__init__(parent)
        self.model = parent
        self.setObjectName("TipHandlerThread")
        self.return_slot_executor: ThreadPoolExecutor = \
            ThreadPoolExecutor(
                max_workers=self.return_slot_executor_workers, 
                thread_name_prefix="ReturnSlotExecutor"
            )


    @profile()
    def run(self):
        Base.log("I", "提示处理器线程开始运行", "TipHandler.run")
        while True:

            while True:
                try:
                    current = self.model.sidenotice_waiting_order.get(timeout=0.01)
                    break
                except queue.Empty:
                    if self.isInterruptionRequested():
                        Base.log("I", "提示处理器线程结束", "TipHandler.run")
                        return

            try:
                index = self.model.sidenotice_avilable_slots.pop(0)
            except IndexError:
                Base.log("W", "没有可用的提示槽位，重新等待", "TipHandler.run")
                continue

            def return_slot(slot: int, current: SideNotice):
                if not current.finished:
                    self.model.sidenotice_avilable_slots.append(slot)
                    current.finished = True

            def _return_slot_after_shown(
                index: int = index, 
                current: SideNotice = current, 
                return_slot: Callable[..., Any] = return_slot
            ):
                time.sleep(current.duration / 1000 + TipHandler.return_slot_delay)
                return_slot(index, current)

            def _exec_on_close(
                index: int=index, 
                current: SideNotice=current, 
                return_slot: Callable[..., Any]=return_slot
            ):
                return_slot(index, current)
                if current.click_command:
                    current.click_command() 


            self.return_slot_executor.submit(_return_slot_after_shown)

            current.closebutton_clicked = lambda: _exec_on_close()

            Base.log(
                "D",
                f"正在将提示 {repr(current)} 放入第 {index} 个位置",
                "TipHandler.run",
            )

            self.model.signal_place_tip.emit(current)


    def destroy(self):
        self.return_slot_executor.shutdown()