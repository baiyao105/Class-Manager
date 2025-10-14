from __future__ import annotations

import sys
import time
from queue import Queue
from typing import (TYPE_CHECKING, Callable, Any, Optional, Tuple)
from utils.algorithm import Thread
from utils.basetypes import Base
from ..objects.achievement import Achievement


if TYPE_CHECKING:
    from ..objects.student import Student
    from ..classobj import ClassObj


class AchievementStatusObserver:
    "成就侦测器"

    def __init__(
        self,
        base: ClassObj,
        class_key: str,
        achievement_display: Optional[Callable[[str, Student], Any]] = None,
        tps: int = 20,
    ):
        """
        构造新的成就侦测器

        :param base_classes: 班级信息
        :param base_templates: 成就模板
        :param class_name: 班级名称
        :param class_obs: 班级信息侦测器（因为不想去各种奇怪的地方获取所以直接传参吧）

        """
        self.on_active: bool = False
        "侦测器是否在运行"
        self.class_id = class_key
        "班级id"
        self.classes = base.classes
        "班级信息（Dict[班级id, Class]）"
        self.achievement_templates = base.achievement_templates
        "成就模板（Dict[成就模板key, 成就模板]）"
        self.class_obs = base.class_obs
        "班级信息侦测器"
        self.display_achievement_queue: Queue[Tuple[str, Student]] = Queue()
        "成就显示队列"
        self.achievement_displayer: Optional[Callable[[str, Student], Any]] = (
            achievement_display
        )
        "成就显示器，传参是一个成就模板的key和一个学生"
        self.class_obs = base.class_obs
        "班级信息侦测器"
        self.last_update = time.time()
        "上次更新时间"
        self.base = base
        "算法基层"
        self.limited_tps = tps
        "侦测器帧率"
        self.mspt = 0
        "侦测器每帧耗时"
        self.overload_ratio = 0.15
        """侦测器过载比例

        当一帧实际耗时大于 (1s/帧率)*过载比例 就视为过载，会减小侦测器tps
        
        设置这个的目的是防止在处理过大数据的时候系统把时间花在计算成就上导致界面卡顿"""
        self.overloaded = False
        "侦测器是否过载"
        self.tps: float = 0
        "侦测器帧率"
        self.total_frame_count = 0
        "运行总帧数"
        self.overload_warning_frame_limit = 2
        "超载警告帧数阈值，连续超载的帧数大于这个数就会有提示"
        self.achievement_displayer = achievement_display or (lambda a, s: None)
        "成就显示器，传参是一个成就模板的key和一个学生"
        self.start_time = 0.0
        "启动时间"
        self.last_frame_time = 0.0
        "上一帧时间"
        self.overload_count = 0
        "过载帧数"

    def next_frame(self, 
                    recheck_achievement: bool = True,
                    recheck_interval: float = 0.1,
                    handle_overloading: bool = True
                    ):

        """
        下一帧
        
        :param recheck_achievement: 是否需要重新检查成就
        :param recheck_interval: 重新检查成就的间隔
        :param handle_overloading: 是否需要处理过载
        """
        self.total_frame_count += 1
        last_opreate_time = time.time()

        if time.time() - self.last_update > 1:
            self.last_update = time.time()
        if self.limited_tps:
            time.sleep(
                max((1 / self.limited_tps) - (time.time() - self.last_frame_time), 0)
            )
        self.last_frame_time = time.time()
        opreated = False
        # 性能优化点：O(n²)复杂度(?)
        for s in list(self.classes[self.class_id].students.values()):

            for a in list(self.achievement_templates.keys()):

                if self.achievement_templates[a].achieved_by(
                    s, self.class_obs
                ) and (
                    self.achievement_templates[a].key
                    not in [  # 判断成就是否已经达成过
                        a.temp.key
                        for a in self.classes[self.class_id]
                        .students[s.num]
                        .achievements.values()
                    ]
                ):
                    opreated = True
                    if recheck_achievement and recheck_interval > 0:
                        time.sleep(recheck_interval)  # 等待操作完成，避免竞态条件
                    if self.achievement_templates[a].achieved_by(
                        s, self.class_obs
                    ) or not recheck_achievement:
                        Base.log(
                            "I",
                            f"[{s.name}] 达成了成就 [{self.achievement_templates[a].name}]",
                        )
                        a2 = Achievement(
                            self.achievement_templates[a], s
                        )
                        a2.give()
                        self.display_achievement_queue.put(
                            (a, s)
                        )

        cur_time = time.time()
        self.mspt = (cur_time - self.last_frame_time) * 1000
        overload_before = self.overloaded
        if not opreated:  # 只在空扫描的时候才检测是否过载
            if self.mspt > 1000 / self.limited_tps * self.overload_ratio:
                self.overloaded = True
                self.overload_count += 1
            else:
                self.overloaded = False
                self.overload_count = 0
            if (
                self.overloaded
                and self.overload_count > self.overload_warning_frame_limit
                and (cur_time - self.start_time) > 1
                and not overload_before
            ):
                # 刚才才开始过载并且已经开了有一段时间了
                if handle_overloading:
                    self.on_observer_overloaded(
                        self.last_frame_time, last_opreate_time, self.mspt
                    )
            time.sleep((self.mspt * (1 / self.overload_ratio)) / 1000)
        self.tps = 1 / max((time.time() - last_opreate_time), 0.001)

    

    def on_observer_overloaded(
        self,
        last_fr_time: float,  # pylint: disable=unused-argument
        last_op_time: float,  # pylint: disable=unused-argument
        cur_mspt: float,
    ) -> None:
        "侦测器过载时调用"
        Base.log(
            "W",
            "侦测器过载，当前帧耗时：" f"{round(cur_mspt, 3)}" "ms, 将会适当减小tps",
            "AchievementStatusObserver._start",
        )

    def run(self):
        "内部启动用函数"
        self.total_frame_count = 0
        self.on_active = True
        t = Thread(
            target=self._display_thread, name="DisplayAchievement", daemon=True
        )
        t.start()
        self.start_time = time.time()
        while self.on_active:
            self.next_frame()
        t.join()
        


    def _display_thread(self):
        "显示成就的线程"
        while self.on_active:
            try:
                if not self.display_achievement_queue.empty():
                    item = self.display_achievement_queue.get()
                    if self.achievement_displayer:
                        self.achievement_displayer(item[0], item[1])
                time.sleep(0.1)  # 每一行代码都有它存在的意义，不信删了试试
            except Exception as e:  # pylint: disable=broad-exception-caught
                Base.log(
                    "E",
                    f"成就显示线程出错: [{sys.exc_info()[1].__class__.__name__}]{e}",
                )
                break

    def start(self):
        "启动侦测器"
        self.on_active = True
        Thread(target=self.run, name="AchievementStatusObserver", daemon=True).start()


    def stop(self):
        "停止侦测器"
        self.on_active = False
