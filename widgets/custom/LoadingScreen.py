"""
加载菜单
"""
from types import TracebackType
from typing import Any, Type, Union, Literal, Callable, Optional
from widgets.basic import MyWidget
from widgets.templates import LoadingScreen
from utils.qtconfig import QTimer, QWidget



class LoadingScreenWidget(MyWidget, LoadingScreen.Ui_Form):
    
    def __init__(self, 
                    parent: Optional[QWidget] = None, 
                    mode: Literal["progressed", "indeterminate"] = "progressed",
                    title: str = "正在加载",
                    progress: Union[int, float] = 0,
                    stage_desc: Optional[str] = None,
                    stage_progress_desc: Optional[str] = None,
                    time_remaning_desc: Optional[str] = None,
                    mode_condition: Optional[Callable[[], Literal["progressed", "indeterminate"]]] = None,
                    progress_condition: Optional[Callable[[], Union[int, float]]] = None,
                    stage_desc_condition: Optional[Callable[[], Optional[str]]] = None,
                    stage_progress_desc_condition: Optional[Callable[[], str]] = None,
                    time_remaning_desc_condition: Optional[Callable[[], str]] = None):
        super().__init__(parent)
        self._mode: Literal["progressed", "indeterminate"] = mode
        self._progress = progress
        self._stage_desc = stage_desc
        self._stage_progress_desc = stage_progress_desc
        self._time_remaining_desc = time_remaning_desc
        self.title = title
        self.mode_condition = mode_condition
        self.progress_condition = progress_condition
        self.stage_desc_condition = stage_desc_condition
        self.stage_progress_desc_condition = stage_progress_desc_condition
        self.time_remaning_desc_condition = time_remaning_desc_condition
        self.setupUi(self) # type: ignore
        if self._mode == "indeterminate":
            self.IndeterminateProgressRing.setVisible(True)
            self.ProgressRing.setVisible(False)
            self.label_2.setVisible(False)
        else:
            self.IndeterminateProgressRing.setVisible(False)
            self.ProgressRing.setVisible(True)
        self.ProgressRing.setValue(int(self._progress))
        self.label_2.setText(f"{self._progress: .2f}%")
        self.label_6.setText(self._stage_desc or "")
        self.label_7.setText(self._stage_progress_desc or "")
        self.label_8.setText(self._time_remaining_desc or "")
        self.update_timer = QTimer(self)
        self.setWindowTitle(self.title)
        self.update_timer.timeout.connect(self.update)
        self.destroyed.connect(self.update_timer.stop)

    def show(self):
        if not self.update_timer.isActive():
            self.update_timer.start(100)
        super().show()

    @property
    def progress(self) -> Union[int, float]:
        return self._progress

    @progress.setter
    def progress(self, value: Union[int, float]):
        self._progress = value
        self.ProgressRing.setValue(int(self._progress))
        self.label_2.setText(f"{self._progress: .2f}%")
        self.update(recheck_conditions=False)


    @property
    def stage_desc(self) -> Union[str, None]:
        return self._stage_desc

    @stage_desc.setter
    def stage_desc(self, value: Union[str, None]):
        self._stage_desc = value
        self.label_6.setText(self._stage_desc or "")
        self.update(recheck_conditions=False)

    
    @property
    def stage_progress_desc(self) -> Union[str, None]:
        return self._stage_progress_desc

    @stage_progress_desc.setter
    def stage_progress_desc(self, value: Union[str, None]):
        self._stage_progress_desc = value
        self.label_7.setText(self._stage_progress_desc or "")
        self.update(recheck_conditions=False)


    @property
    def time_remaning_desc(self) -> Union[str, None]:
        return self._time_remaining_desc

    @time_remaning_desc.setter
    def time_remaning_desc(self, value: Union[str, None]):
        self._time_remaining_desc = value
        self.label_8.setText(self._time_remaining_desc or "")
        self.update(recheck_conditions=False)

    
    @property
    def mode(self) -> Literal["progressed", "indeterminate"]:
        return self._mode

    @mode.setter
    def mode(self, value: Literal["progressed", "indeterminate"]):
        self._mode = value
        if self._mode == "indeterminate":
            self.IndeterminateProgressRing.setVisible(True)
            self.ProgressRing.setVisible(False)
        else:
            self.IndeterminateProgressRing.setVisible(False)
            self.ProgressRing.setVisible(True)
        self.update(recheck_conditions=False)

    def update(self, *args: Any, recheck_conditions: bool = True):
        if recheck_conditions:
            if self.mode_condition:
                self.mode = self.mode_condition()
            if self.progress_condition:
                self.progress = self.progress_condition()
            if self.stage_desc_condition:
                self.stage_desc = self.stage_desc_condition()
            if self.stage_progress_desc_condition:
                self.stage_progress_desc = self.stage_progress_desc_condition()
            if self.time_remaning_desc_condition:
                self.time_remaning_desc = self.time_remaning_desc_condition()
        super().update(*args)

    def __enter__(self):
        self.show()
        return self
    
    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]):
        self.close()
        return False

__all__ = ["LoadingScreenWidget"]
