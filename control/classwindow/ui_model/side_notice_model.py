"""
侧边栏提示有关的模型。
"""

from __future__ import annotations

from queue import Queue

from utils.qtconfig import QWidget
from widgets.basic.widgets import SideNotice


class SideNoticeModel(QWidget):

    def __init__(self, master: QWidget | None = None):
        self.sidenotice_waiting_order: Queue[SideNotice] = Queue()
        "提示栏等待顺序"
        self.sidenotice_avilable_slots = list(range(5))
        "提示栏可用槽位"