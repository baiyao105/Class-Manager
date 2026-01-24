"""
列表视图
"""
from typing import List, Any, Union
from concurrent.futures import ThreadPoolExecutor
from utils import Thread, Base, ClassObj as ClassWindow, steprange
from utils.settings import SettingsInfo
from widgets.basic import *


__all__ = ["ListView"]


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
        QMetaObject.connectSlotsByName(form)

    def retranslateUi(self, form: MyWidget):
        "设置UI文本"
        form.setWindowTitle("\u5217\u8868")
        self.pushButton_2.setText("\u56de\u5230\u9876\u90e8")
        self.pushButton_3.setText("\u6eda\u52a8\u5230\u5e95\u90e8")

    def __init__(
        self,
        main_window: ClassWindow = None,
        master_widget: Optional[WidgetType] = None,
        title: str = "列表",
        data: List[
            Union[
                Tuple[str, Callable],
                Tuple[str, Callable, Optional[Tuple[QColor, QColor, int, int]]],
            ]
        ] = None,
        args: Any = None,
        commands: List[Tuple[str, Callable]] = None,
        allow_pre_action: bool = False,
        select_once_then_exit: bool = False,
    ):
        """
        初始化窗口

        :param main_window: 主窗口
        :param master_widget: 父窗口
        :param title: 窗口标题
        :param data: 数据，格式为 [(文本, 回调函数, 可选(起始颜色, 结束颜色, 总渐变步数, 每次变化间隔))]
        :param args: 随便传点什么参数用来存东西
        :param commands: 命令，格式为 [(文本, 回调函数)]
        :param allow_pre_action: 是否允许在动画完成前执行回调函数
        :param select_once_then_exit: 是否选中一次后退出
        """
        if data is None:
            data = [("空", lambda: None)]
        if commands is None:
            commands = []
        super().__init__(master=main_window)
        self.setupui(self)
        self.orig_height = self.height()
        self.data = data
        self.args = args
        self.title = title
        self.allow_pre_action = allow_pre_action
        self.setWindowTitle(title)
        self.main_window = main_window
        self.master_widget = master_widget
        self.listWidget.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )  # 双击编辑有点逆天（这里禁了）
        self.listWidget.doubleClicked.connect(self.itemClicked)
        self.command_update.connect(self.setCommands)
        self.pushButton_2.clicked.connect(self.listWidget.scrollToTop)
        self.pushButton_3.clicked.connect(self.listWidget.scrollToBottom)
        self.item_update.connect(self.update_item_color)
        self.commands = commands
        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.verticalLayout.setSpacing(0)
        self.btn_list: List[QPushButton] = []
        self.cmd_list: List[Callable] = []
        self.ready = False
        self.setting_command = False
        self.setCommands(commands, force=True)
        self.commands = commands
        self.select_once_then_exit = select_once_then_exit
        self.widget_items: List[QListWidgetItem] = []

    @Slot()
    def setCommands(self, commands: List[Tuple[str, Callable]] = None, *, force=False):
        while self.setting_command and not force:
            """"""
        self.commands = commands
        self.setting_command = True
        commands = self.commands
        for btn in self.btn_list:
            btn.deleteLater()
        self.btn_list = []
        if commands is None:
            return
        for string, _callable in commands:
            btn = QPushButton(string)
            self.btn_list.append(btn)
            self.verticalLayout.addWidget(btn)
            self.cmd_list.append(_callable)
            btn.clicked.connect(
                lambda *, string=string, _callable=_callable: (
                    (
                        lambda string=string, _callable=_callable: (
                            Base.log(
                                "I",
                                f"执行命令：{string}，{_callable}",
                                "ListView.setCommands",
                            ),
                            _callable(),
                        )
                    )()
                    if self.ready or self.allow_pre_action
                    else (
                        lambda: Base.log(
                            "W",
                            f"正在初始化，忽略操作 ({string})",
                            "ListView.setCommands",
                        )
                    )()
                )
            )
        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.verticalLayout.update()
        self.setting_command = False

    @Slot(QListWidgetItem, QColor)
    def update_item_color(self, item: QListWidgetItem, color: QColor):
        """
        更新某个项目的颜色

        :param item: 指定的项目
        :param color: 指定的颜色
        """
        try:
            if item is None:
                return
            item.setBackground(QBrush(color))

        except BaseException as unused:  # pylint: disable=broad-exception-caught
            pass

    def show(self):
        "展示窗口"
        self.is_running = True
        self.move(
            (
                self.master.geometry().topLeft()
                + QPoint(
                    self.master.geometry().width() / 2,
                    self.master.geometry().height() / 2,
                )
                - QPoint(self.geometry().width() / 2, self.geometry().height() / 2)
                + QPoint(SettingsInfo.current.subwindow_x_offset, SettingsInfo.current.subwindow_y_offset)
            )
        )
        super().orig_show()
        if SettingsInfo.current.animation_speed <= 114514:
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
        default_color_start = QColor(232, 255, 244)
        default_color_end = QColor(255, 255, 255)
        default_step = int(10 / SettingsInfo.current.animation_speed)
        default_interval = 33
        self.listWidget.clear()
        self.widget_items.clear()

        try:
            for item in self.data:
                if len(item) == 2 or (len(item) == 3 and item[2] is None):
                    self.data[index] = (
                        item[0],
                        item[1],
                        (
                            default_color_start,
                            default_color_end,
                            default_step,
                            default_interval,
                        ),
                    )
                elif len(item) == 3:
                    if len(item[2]) == 2:
                        self.data[index] = (
                            item[0],
                            item[1],
                            (item[2][0], item[2][1], default_step, default_interval),
                        )
                    elif len(item[2]) == 3:
                        self.data[index] = (
                            item[0],
                            item[1],
                            (item[2][0], item[2][1], item[2][2], default_interval),
                        )
                index += 1
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            Base.log_exc("初始化项目时发生错误", "ListView.init_items")
        index = 0
        length = len(self.data)

        try:
            for string, _callable, flash_args in self.data:
                widget_item = QListWidgetItem(string)
                self.widget_items.append(widget_item)
                self.listWidget.addItem(widget_item)
                index += 1

                if SettingsInfo.current.animation_speed <= 114514 and length <= 1000:    # 项目数量大于1000就不显示动画了

                    def _animation(widget_item=widget_item, flash=flash_args, index=index):
                            self.insert_flash(
                                widget_item, flash[0], flash[1], flash[2], flash[3]
                            ),
                            self._set_anim_finished(index - 1),
                    self.anim_executor.submit(_animation)
                    time.sleep(0.01 * ((1000 - length) / 1000) / SettingsInfo.current.animation_speed)

                else:
                    widget_item.setBackground(QBrush(flash_args[1]))
                    self._set_anim_finished(index - 1)

        except BaseException as unused:  # pylint: disable=broad-exception-caught
            Base.log_exc("初始化项目时发生错误", "ListView.init_items")

        Base.log("D", "等待动画结束", "ListView.init_items")
        loop = QEventLoop(self)
        timer = QTimer(self)
        def _check_if_finished():
            if all(self.anim_result):
                loop.quit()
                timer.stop()
        timer.timeout.connect(_check_if_finished)
        timer.start(100)
        loop.exec()
        timer.stop()
        Base.log(
            "D",
            f"初始化项目完成，len(anim_result) = {len(self.anim_result)}",
            "ListView.init_items",
        )
        self.ready = True

    def _set_anim_finished(self, index: int):
        try:
            self.anim_result[index] = True
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            pass

    def insert_flash(
        self,
        item: QListWidgetItem,
        from_color: QColor,
        to_color: QColor,
        step: int = 45,
        interval: int = 1,
    ):
        for r, g, b in list(
            zip(
                steprange(from_color.red(), to_color.red(), step),
                steprange(from_color.green(), to_color.green(), step),
                steprange(from_color.blue(), to_color.blue(), step),
            )
        ):
            try:

                self.item_update.emit(item, QColor(r, g, b))
                if interval:
                    time.sleep((interval / 1000))
                if not self.isVisible():
                    return

            except BaseException as unused:  # pylint: disable=broad-exception-caught
                pass

    def create_animation(
        self,
        property_name,
        duration,
        start_value,
        end_value,
        easing_curve=QEasingCurve.Type.OutCubic,
    ):
        """创建通用属性动画

        Args:
            property_name: 目标属性名
            duration: 动画持续时间(毫秒)
            start_value: 起始值
            end_value: 结束值
            easing_curve: 缓动曲线类型

        Returns:
            配置好的QPropertyAnimation对象
        """
        animation = QPropertyAnimation(self, property_name)
        animation.setEasingCurve(easing_curve)
        animation.setDuration(
            duration / SettingsInfo.current.animation_speed
            if SettingsInfo.current.animation_speed > 0
            else duration
        )
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        return animation

    def showStartAnimation(self):
        Base.log("D", "开始启动动画（阶段1）", "ListView.showStartAnimation")

        # 计算动画终点和起点


        endpoint = (
            self.master.geometry().topLeft()
            + QPoint(
                self.master.geometry().width() / 2, self.master.geometry().height() / 2
            )
            - QPoint(self.geometry().width() / 2, self.orig_height / 2)
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

        self.str_list = [item[0] for item in self.data]
        self.widget_items = [QListWidgetItem(string) for string in self.str_list]
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

    def addData(self, item: Tuple[str, Callable]):
        self.data.append(item)
        self.str_list.append(item[0])
        listwidget_item = QListWidgetItem(item[0])
        self.listWidget.addItem(listwidget_item)
        self.widget_items.append(listwidget_item)

    def addItem(self, item: QListWidgetItem):
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.addItem")
            return
        self.listWidget.addItem(item)
        self.str_list.append(item.text())
        self.data.append((item.text(), None))
        self.widget_items.append(item)

    def setData(self, data: List[Tuple[str, Callable]]):
        self.data = data
        self.str_list = [item[0] for item in data]
        self.listWidget.clear()
        for item in self.str_list:
            self.listWidget.addItem(QListWidgetItem(item))

    def setText(self, index: int, text: str):
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.setText")
            return
        self.str_list[index] = text
        item = self.listWidget.item(index)
        item.setText(text)
        self.data[index] = (text, self.data[index][1])

    def getText(self, index: int):
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.getText")
            return
        return self.data[index][0]

    def getItem(self, index: int) -> QListWidgetItem:
        return self.listWidget.item(index)

    def getCallable(self, index: int):
        return self.data[index][1]

    def setCallable(self, index: int, func: Callable):
        self.data[index] = (self.data[index][0], func)

    def delete(self, index: int) -> QListWidgetItem:
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.delete")
            return
        self.str_list.pop(index)
        item = self.listWidget.takeItem(index)
        self.widget_items.pop(index)
        self.data.pop(index)
        return item

    def insert(self, index, data: Tuple[str, Callable]):
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.insert")
            return
        self.str_list.insert(index, data[0])
        self.listWidget.insertItem(index, QListWidgetItem(data[0]))
        self.listWidget.item(index).setText(data[0])
        self.data.insert(index, data)

    def length(self):
        return len(self.str_list)

    @Slot(QModelIndex)
    def itemClicked(self, qModelIndex: QModelIndex):
        # 弹出消息框
        Base.log(
            "I",
            f"点击了{repr(self.str_list[qModelIndex.row()])}, 调用函数{repr(self.data[qModelIndex.row()][1])}",
            "ListView",
        )
        self.data[qModelIndex.row()][1]()
        if self.select_once_then_exit:
            self.close()

    def closeEvent(self, event: QEvent):
        Base.log("I", "ListView窗口关闭（通过关闭事件）", "ListView")
        super().closeEvent(event)
