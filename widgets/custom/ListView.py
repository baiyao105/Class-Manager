"""
列表视图
"""
from __future__ import annotations


import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, Sequence, Tuple, TypeAlias, Union, overload

from utils import Thread, Base, ClassDataSet as steprange, wait_until, steprange
from utils.qtconfig import (
    Signal, QWidget, QListWidgetItem, QListWidget, QPropertyAnimation,
    QColor, QRect, QVBoxLayout, QPushButton, QAbstractItemView, QEventLoop,
    QMetaObject, QModelIndex, Qt, Slot, QBrush, QPoint, QGuiApplication,
    QSize, QCloseEvent
)
from utils.settings import SettingsInfo

from widgets.basic import MyWidget




CallableWithNoArgsNeeded: TypeAlias = Callable[..., Any]
"不需要主动提供参数的函数，用...是因为有的可能带着默认参数"

AnimationConfigDataType: TypeAlias = Union[
    Tuple[QColor, QColor], 
    Tuple[QColor, QColor, int], 
    Tuple[QColor, QColor, int, int]
]

ListViewItemDataType: TypeAlias = Union[
    Tuple[str],
    Tuple[str, CallableWithNoArgsNeeded],
    Tuple[str, CallableWithNoArgsNeeded, AnimationConfigDataType]
]

ListViewCommandDataType: TypeAlias = Tuple[str, CallableWithNoArgsNeeded]


default_color_start = QColor(232, 255, 244)
default_color_end = QColor(255, 255, 255)
default_step = int(10 / SettingsInfo.get_global_settings().animation_speed)
default_interval = 33

class AnimationConfig:
    def __init__(self, 
                begin: QColor | None = None, 
                end: QColor | None = None,
                step: int | None = None,
                step_interval: int | None = None):
        self.begin = begin or default_color_start
        self.end = end or default_color_end
        self.step = step or default_step
        self.step_interval = step_interval or default_interval

    @staticmethod
    def from_tuple(data: AnimationConfigDataType) -> AnimationConfig:
        try:
            length = len(data)
        except Exception:
            raise TypeError("应当提供一个类似于元组的数据")

        if length == 2:
            begin, end = data  # type: ignore[misc]
            return AnimationConfig(begin=begin, end=end)
        if length == 3:
            begin, end, step = data  # type: ignore[misc]
            return AnimationConfig(begin=begin, end=end, step=step)
        if length == 4:
            begin, end, step, step_interval = data  # type: ignore[misc]
            return AnimationConfig(begin=begin, end=end, step=step, step_interval=step_interval)

        raise TypeError("Invalid AnimationConfigDataType length")

class ListViewItem:
    def __init__(self,
                text: str,
                command: CallableWithNoArgsNeeded | None = None,
                anim_config: AnimationConfig | None = None):
        self.text = text
        self.command = command or (lambda: None)
        self.anim_config = anim_config or AnimationConfig()

    @staticmethod
    def from_tuple(data: ListViewItemDataType):
        text = data[0]
        command = data[1] if len(data) > 1 else None
        raw_anim = data[2] if len(data) > 2 else None
        if isinstance(raw_anim, AnimationConfig):
            anim_config = raw_anim
        elif isinstance(raw_anim, tuple):
            anim_config = AnimationConfig.from_tuple(raw_anim)
        else:
            anim_config = AnimationConfig()
        return ListViewItem(text, command, anim_config)

class ListViewCommand:
    def __init__(self,
                name: str,
                command: CallableWithNoArgsNeeded | None = None):
        self.name = name
        self.command = command or (lambda: None)
    
    @staticmethod
    def from_tuple(data: ListViewCommandDataType):
        name = data[0]
        command = data[1]
        return ListViewCommand(name, command)


class ListView(MyWidget):  # pylint: disable=function-redefined
    "列表视图，全程序用的最多的窗口"

    item_update = Signal(QListWidgetItem, QColor)

    command_update = Signal(list)

    anim_executor = ThreadPoolExecutor(max_workers=64)

    def setupui(self, form: MyWidget):
        "设置UI"
        if not form.objectName():
            form.setObjectName("Form")
        form.resize(437, 551)
        self.listWidget = QListWidget(form)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setGeometry(QRect(0, 0, 341, 551))
        self.verticalLayoutWidget = QWidget(form)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(340, -1, 101, 551))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_2 = QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QPushButton(self.verticalLayoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout.addWidget(self.pushButton_3)
        self.retranslateUi(form)
        self.startanimation_1: QPropertyAnimation | None = None
        QMetaObject.connectSlotsByName(form)

    def retranslateUi(self, form: MyWidget):
        "设置UI文本"
        form.setWindowTitle("\u5217\u8868")
        self.pushButton_2.setText("\u56de\u5230\u9876\u90e8")
        self.pushButton_3.setText("\u6eda\u52a8\u5230\u5e95\u90e8")

    def __init__(
        self,
        title: str = "列表",
        master: QWidget | None = None,
        data: Sequence[ListViewItemDataType] | None = None,
        args: Any = None,
        commands: Sequence[ListViewCommandDataType] | None = None,
        allow_pre_action: bool = False,
        select_once_then_exit: bool = False,
    ):
        """
        初始化窗口

        :param title: 窗口标题
        :param master: 父窗口
        :param data: 数据，格式为 [(文本, 回调函数, 可选(起始颜色, 结束颜色, 总渐变步数, 每次变化间隔))]
        :param args: 随便传点什么参数用来存东西
        :param commands: 用来当作侧边栏按钮的命令，格式为 [(文本, 回调函数)]
        :param allow_pre_action: 是否允许在动画完成前执行回调函数
        :param select_once_then_exit: 是否选中一次后退出
        """
        super().__init__(master=master)
        self.setupui(self)
        self.orig_height = self.height()
        self.data: list[ListViewItem] = self.parse_data(data)
        self.args = args
        self.title = title
        self.allow_pre_action = allow_pre_action
        self.setWindowTitle(title)
        self.master_widget = master
        self.listWidget.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )  # 双击编辑有点逆天（这里禁了）
        self.listWidget.doubleClicked.connect(self.itemClicked)
        self.command_update.connect(self.setCommands)
        self.pushButton_2.clicked.connect(self.listWidget.scrollToTop)
        self.pushButton_3.clicked.connect(self.listWidget.scrollToBottom)
        self.item_update.connect(self.update_item_color)
        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.verticalLayout.setSpacing(0)
        self.btn_list: list[QPushButton] = []
        self.cmd_list: list[CallableWithNoArgsNeeded] = []
        self.ready = False
        self.setting_command = False
        self.setCommands(list(commands or []), force=True)
        self.select_once_then_exit = select_once_then_exit
        self.widget_items: list[QListWidgetItem] = []


    def parse_data(self, data: Sequence[ListViewItemDataType] | None = None) -> list[ListViewItem]:
        "解析数据。"
        result: list[ListViewItem] = []
        if data is None:
            return result
        for item in data:
            result.append(ListViewItem.from_tuple(item))
        return result


    @overload
    def setCommands(self, commands: list[tuple[str, CallableWithNoArgsNeeded]] | None = None, *, force: bool = True) -> None:
        ...

    @overload
    def setCommands(self, commands: list[ListViewCommand] | None = None, *, force: bool = True) -> None:
        ...


    @Slot()
    def setCommands(self, commands_param: 
                    list[tuple[str, CallableWithNoArgsNeeded]] | list[ListViewCommand] | None = None, 
                    *, force: bool = False):
        commands: list[tuple[str, CallableWithNoArgsNeeded]] = []
        if commands_param is not None:
            for item in commands_param:
                if isinstance(item, ListViewCommand):
                    commands.append((item.name, item.command))
                else:
                    commands.append(item)
        if not len(commands): 
            return
        
        while self.setting_command and not force:
            time.sleep(0.001)
        
        self.commands = commands
        self.setting_command = True
        for btn in self.btn_list:
            btn.deleteLater()
        self.btn_list = []
        for string, _callable in commands:
            btn = QPushButton(string)
            self.btn_list.append(btn)
            self.verticalLayout.addWidget(btn)
            self.cmd_list.append(_callable)
            Base.log("D", F"设置命令: {string} ({_callable}) -> {btn}", "ListView.setCommands")
            def wrapper(*, string: str = string, func: CallableWithNoArgsNeeded = _callable):
                if self.ready or self.allow_pre_action:
                    Base.log("I", f"执行命令：{string}，{func}", "ListView.setCommands")
                    func()
                else:
                    Base.log("W", f"正在初始化，忽略操作 ({string})", "ListView.setCommands")
            btn.clicked.connect(wrapper)
        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.verticalLayout.update()
        self.setting_command = False


    @Slot(QListWidgetItem, QColor)
    def update_item_color(self, item: QListWidgetItem | None, color: QColor):
        """
        更新某个项目的颜色

        :param item: 指定的项目
        :param color: 指定的颜色
        """
        try:
            if item is None:
                return
            item.setBackground(QBrush(color))

        except Exception:
            pass


    def show(self):
        "展示窗口"
        self.is_running = True
        startpoint: QPoint
        if self._master:
            startpoint = (
                self._master.geometry().topLeft()
                + QPoint(
                    self._master.geometry().width() // 2,
                    self._master.geometry().height() // 2,
                )
                - QPoint(self.geometry().width() // 2, self.geometry().height() // 2)
                + QPoint(SettingsInfo.get_global_settings().subwindow_x_offset, SettingsInfo.get_global_settings().subwindow_y_offset)
            )
        else:
            startpoint = QPoint(
                QGuiApplication.primaryScreen().geometry().width() // 2 - self.geometry().width() // 2,
                QGuiApplication.primaryScreen().geometry().height() // 2 - self.geometry().height() // 2
            )
        self.move(startpoint)
        super().orig_show()
        if SettingsInfo.get_global_settings().animation_speed <= 114514:
            self.showStartAnimation()
        else:
            self.init_items()



    def init_items(self):
        """
        初始化列表项目
        """
        Base.log("D", f"开始初始化项目，数量：{len(self.data)}", "ListView.init_items")
        self.anim_result = [False] * len(self.data)
        index = 0
        
        self.listWidget.clear()
        self.widget_items.clear()


        index = 0
        length = len(self.data)

        try:
            for item in self.data:
                string = item.text
                widget_item = QListWidgetItem(string)
                self.widget_items.append(widget_item)
                self.listWidget.addItem(widget_item)
                index += 1

                if SettingsInfo.get_global_settings().animation_speed <= 114514 and length <= 1000:    # 项目数量大于1000就不显示动画了
                   
                    def _animation(
                            widget_item: QListWidgetItem = widget_item, 
                            anim_conf: AnimationConfig = item.anim_config, 
                            index: int = index
                        ):
                            self.insert_flash(
                                widget_item,
                                anim_conf.begin,
                                anim_conf.end,
                                anim_conf.step,
                                anim_conf.step_interval
                            )
                            self._set_anim_finished(index - 1)

                    self.anim_executor.submit(_animation)

                    time.sleep(0.01 * ((1000 - length) / 1000) / SettingsInfo.get_global_settings().animation_speed)

                else:
                    widget_item.setBackground(QBrush(item.anim_config.end))
                    self._set_anim_finished(index - 1)

        except Exception as exc:
            Base.log_exc("初始化项目时发生错误", "ListView.init_items", "E", exc)

        Base.log("D", "等待动画结束", "ListView.init_items")
        wait_until(lambda: all(self.anim_result))
        Base.log(
            "D",
            f"初始化项目完成，len(anim_result) = {len(self.anim_result)}",
            "ListView.init_items",
        )
        self.ready = True

    def _set_anim_finished(self, index: int):
        try:
            self.anim_result[index] = True
        except (IndexError, KeyError):
            pass

    def insert_flash(
        self,
        item: QListWidgetItem,
        from_color: QColor,
        to_color: QColor,
        step: int = 45,
        interval: int = 1
    ):
        for r, g, b in zip(
            steprange(from_color.red(), to_color.red(), step),
            steprange(from_color.green(), to_color.green(), step),
            steprange(from_color.blue(), to_color.blue(), step),
        ):
            try:

                self.item_update.emit(item, QColor(int(r), int(g), int(b)))
                if interval:
                    time.sleep((interval / 1000))
                if not self.isVisible():
                    return

            except Exception as exc:
                Base.log_exc_short("更新动画背景色时出现错误", exc=exc)

    def showStartAnimation(self):
        Base.log("D", "开始启动动画（阶段1）", "ListView.showStartAnimation")

        # 计算动画终点和起点

        endpoint = (
            self._master.geometry().topLeft()
            + QPoint(
                self._master.geometry().width() // 2, self._master.geometry().height() // 2
            )
            - QPoint(self.geometry().width() // 2, self.orig_height // 2)
        ) if  self._master else QPoint(
            QGuiApplication.primaryScreen().availableGeometry().width() // 2 - self.geometry().width() // 2,
            QGuiApplication.primaryScreen().availableGeometry().height() // 2 - self.orig_height // 2
        )

        startpoint = QPoint(
            endpoint.x(),
            QGuiApplication.primaryScreen().availableGeometry().height()
            + QGuiApplication.primaryScreen().availableGeometry().top(),
        )


        # 使用通用动画创建方法
        self.startanimation_1 = self.create_animation(b"pos", 400, startpoint, endpoint)

        self.setGeometry(self.x(), self.y(), self.width(), 1)
        wait_loop_1 = QEventLoop(self)
        self.startanimation_1.finished.connect(wait_loop_1.quit)
        self.startanimation_1.start()
        wait_loop_1.exec()

        Base.log("D", "开始启动动画（阶段2）", "ListView.showStartAnimation")

        self.widget_items = [QListWidgetItem(item.text) for item in self.data]
        self.listWidget.clear()
        Thread(target=self.init_items, name="ListView.init_items").start()

        # 获取当前尺寸信息
        width, height = self.width(), self.orig_height

        # 使用通用动画创建方法
        self.startanimation_2 = self.create_animation(
            b"size", 400, QSize(width, 1), QSize(width, height)
        )
        wait_loop_2 = QEventLoop(self)
        self.startanimation_2.finished.connect(wait_loop_2.quit)
        self.startanimation_2.start()
        wait_loop_2.exec()

    def addData(self, item: ListViewItemDataType):
        self.data.append(ListViewItem.from_tuple(item))
        listwidget_item = QListWidgetItem(item[0])
        self.listWidget.addItem(listwidget_item)
        self.widget_items.append(listwidget_item)

    def addItem(self, item: QListWidgetItem):
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.addItem")
            return
        self.listWidget.addItem(item)
        self.data.append(ListViewItem(item.text()))
        self.widget_items.append(item)

    @overload
    def setData(self, data: list[ListViewItemDataType]) -> None: ...

    @overload
    def setData(self, data: list[ListViewItem]) -> None: ...

    def setData(self, data: list[ListViewItemDataType] | list[ListViewItem]):
        if len(data):
            if isinstance(data[0], ListViewItem):
                self.data = data # type: ignore
            else:
                self.data = [ListViewItem.from_tuple(item) for item in data] # type: ignore

        self.listWidget.clear()
        for item in self.data:
            self.listWidget.addItem(QListWidgetItem(item.text))

    def setText(self, index: int, text: str):
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.setText")
            return
        item = self.listWidget.item(index)
        item.setText(text)
        self.data[index].text = text

    def getText(self, index: int):
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.getText")
            return
        return self.data[index].text

    def getItem(self, index: int) -> QListWidgetItem:
        return self.listWidget.item(index)

    def getCallable(self, index: int):
        return self.data[index].command

    def setCallable(self, index: int, func: CallableWithNoArgsNeeded):
        self.data[index].command = func

    def delete(self, index: int) -> QListWidgetItem | None:
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.delete")
            return
        item = self.listWidget.takeItem(index)
        self.widget_items.pop(index)
        self.data.pop(index)
        return item
    
    @overload
    def insert(self, index: int, data: ListViewItemDataType) -> None: ...

    @overload
    def insert(self, index: int, data: ListViewItem) -> None: ...

    def insert(self, index: int, data: ListViewItemDataType | ListViewItem):
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.insert")
            return
        if not isinstance(data, ListViewItem):
            data = ListViewItem.from_tuple(data)
        self.listWidget.insertItem(index, QListWidgetItem(data.text))
        self.listWidget.item(index).setText(data.text)
        self.data.insert(index, data)

    def length(self):
        return len(self.data)

    @Slot(QModelIndex)
    def itemClicked(self, model_index: QModelIndex):
        # 弹出消息框
        Base.log(
            "I",
            f"点击了{repr(self.data[model_index.row()].text)}, 调用函数{repr(self.data[model_index.row()].command)}",
            "ListView",
        )
        self.data[model_index.row()].command()
        if self.select_once_then_exit:
            self.close()

    def closeEvent(self, event: QCloseEvent):
        Base.log("I", "ListView窗口关闭（通过关闭事件）", "ListView")
        super().closeEvent(event)

__all__ = ["ListView"]
