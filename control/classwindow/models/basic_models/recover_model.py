"""
数据恢复有关的模型。
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import time
import pickle
import traceback
from typing import Literal

from utils.functions.prompts import question_yes_no
from utils.functions.qtutils import wait_until
from utils.qtconfig import QMessageBox
from utils.basetypes import Base


from .dataset_model import DataSetModel

class RecoverModel(DataSetModel):
    """
    和数据恢复有关的模型。
    """

    def __init__(
        self,
        current_user: str,
        class_name: str,
        class_key: str,
        save_path: str | None = None
    ):
        Base.log("D", "初始化RecoverModel", "RecoverModel.__init__")
        DataSetModel.__init__(self, 
            current_user=current_user, 
            class_name=class_name, 
            class_key=class_key, 
            save_path=save_path
        )


    def script_backup(self, mode: Literal["none", "all", "only_data"] = "only_data"):
        """
        执行应用程序备份

        :param mode: 备份模式
            "none": 不执行备份
            "all": 备份所有程序文件
            "only_data": 仅备份数据文件
        """
        if not os.path.exists(self.backup_path):
            os.mkdir(self.backup_path)

        infof: dict[float, RecoveryPoint] = {}

        try:
            with open(os.path.join(self.backup_path, "backup_info.json"), "r") as f:
                data: list[str] = json.load(f)
                for i in data:
                    item = RecoveryPoint.from_json(i, self)
                    infof[item.time] = item
        except FileNotFoundError:
            pass

        except pickle.PickleError:
            Base.log_exc("备份信息文件损坏", "RecoverModel.script_backup")
            QMessageBox.critical(self, "错误", "备份信息文件损坏，已经重置备份信息文件")
            infof = {}

        except Exception:
            Base.log_exc("备份信息文件损坏", "RecoverModel.script_backup")
            QMessageBox.critical(
                self,
                "错误",
                "加载备份信息文件出错：\n"
                + traceback.format_exc()
                + "\n可以尝试过一会再试试？",
            )
            return

        today_and_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())

        if mode == "none":
            Base.log("I", "脚本备份已关闭，跳过此步", "RecoverModel.script_backup")
            return

        if mode == "only_data":
            Base.log("I", "正在对数据文件进行备份...", "RecoverModel.script_backup")
            try:
                p = self.backup_path + f"dataonly/b_{today_and_time}"
                for i in range(6):
                    try:
                        shutil.copytree("chunks", p + "/chunks")
                    except OSError as e:
                        if i > 4:
                            raise e
                    else:
                        break

                t = time.time()
                infof[t] = RecoveryPoint(p, mode, time.time(), "active", self)
                Base.log("I", "备份成功！", "RecoverModel.script_backup")

            except OSError:
                Base.log_exc("保存失败！", "RecoverModel.script_backup")

        if mode == "all":
            Base.log("I", "正在对完整程序进行备份...", "RecoverModel.script_backup")
            try:
                p = self.backup_path + f"dataonly/b_{today_and_time}"

                shutil.copytree(os.getcwd(), "backup_tmp")
                for i in range(6):
                    try:
                        shutil.copytree(
                            "backup_tmp", self.backup_path + f"full/b_{today_and_time}"
                        )
                        shutil.rmtree("backup_tmp")
                    except OSError as e:
                        if i > 4:
                            raise e
                    else:
                        break

                t = time.time()
                infof[t] = RecoveryPoint(p, mode, time.time(), "active", self)
                Base.log("I", "备份成功！", "RecoverModel.script_backup")

            except Exception:
                Base.log_exc("保存失败！", "RecoverModel.script_backup")

        with open(os.path.join(self.backup_path, "backup_info.json"), "w") as f:
            json.dump([i.to_json() for i in infof.values()], f, indent=4)
    
    def read_recovery_point_list(self) -> dict[float, RecoveryPoint]:
        """
        读取还原点列表。
        """
        infof: dict[float, RecoveryPoint] = {}

        try:
            with open(os.path.join(self.backup_path, "backup_info.json"), "r") as f:
                data: list[str] = json.load(f)
                for i in data:
                    item = RecoveryPoint.from_json(i, self)
                    infof[item.time] = item

        except FileNotFoundError:
            pass


        except Exception:
            Base.log_exc("备份信息文件损坏", "RecoverModel.load_recovery_points")
            QMessageBox.critical(
                self,
                "错误",
                "加载备份信息文件出错：\n"
                + traceback.format_exc()
                + "\n可以尝试过一会再试试？",
            )

        return infof

    def load_recovery_point(self, point: "RecoveryPoint"):
        """加载还原点"""
        Base.log("I", "询问是否加载还原点", "RecoverModel.load_recovery_point")
        if question_yes_no(
            self,
            "提示",
            "是否加载还原点？\n恢复后，需要手动重启程序。\n还原点将会覆盖当前存档且无法恢复。",
            False,
            "warning",
        ):
            try:
                point.load_onlydata_and_set(self.current_user)
            except Exception:
                Base.log("E", "加载还原点失败", "RecoverModel.load_recovery_point")
                QMessageBox.critical(
                    self,
                    "错误",
                    "加载还原点失败:\n\n"
                    + traceback.format_exc()
                    + "\n\n请尝试重新创建还原点",
                )
            else:
                Base.log("I", "加载还原点成功", "RecoverModel.load_recovery_point")

    

    def stop(self):
        "停止运行并保存最后的备份"
        Base.log("I", "正在保存最后的备份", "RecoverModel.stop")
        self.script_backup(self.auto_backup_scheme)
        super().stop()


class RecoveryPoint:
    """
    还原点。
    """

    def __init__(
        self,
        path: str,
        mode: Literal["all", "only_data"],
        _time: float,
        stat: Literal["active", "unknown", "damaged", "missed"],
        binding: RecoverModel
    ):
        """
        初始化

        :param path: 路径
        :param mode: 模式
        :param stat: 状态
        """
        self.path = path
        self.mode = mode
        self.time = _time
        self.stat = stat
        self.binding = binding

    def to_json(self):
        """
        把还原点数据转换为json。
        """
        return json.dumps(
            {
                "path": self.path,
                "mode": self.mode,
                "stat": self.stat,
                "time": self.time
            }
        )
    
    @staticmethod
    def from_json(json_str: str, binding: RecoverModel):
        """
        从json字符串中加载还原点。

        :param json_str: json字符串
        """
        data = json.loads(json_str)
        return RecoveryPoint(data["path"], data["mode"], data["time"], data["stat"], binding)

    def get_data_path(self, current_user: str):
        """
        获取数据路径。

        :param current_user: 当前用户
        """
        return os.path.join(self.path, "chunks", current_user)

    def exists(self):
        """
        检查还原点是否存在。
        """
        return os.path.exists(self.path)

    def load_onlydata_and_set(self, current_user: str):
        """
        加载数据并设置。

        :param current_user: 当前用户
        """
        Base.log("I", "正在从还原点恢复数据", "RecoveryPoint.load_onlydata")
        Base.log("I", "还原点路径：" + self.path, "RecoveryPoint.load_onlydata")
        Base.log("I", "还原点模式：" + self.mode, "RecoveryPoint.load_onlydata")
        Base.log("I", "还原点时间：" + str(self.time), "RecoveryPoint.load_onlydata")
        Base.log("I", "当前用户：" + current_user, "RecoveryPoint.load_onlydata")
        wait_until(lambda: self.binding.auto_saving)
        self.load_onlydata(self.binding.current_user)
        self.binding.stop()
        shutil.rmtree(self.binding.save_path)

        def _copy():
            for root, _, files in os.walk(self.get_data_path(self.binding.current_user)):
                for file in files:
                    os.makedirs(
                        os.path.join(
                            self.binding.save_path,
                            os.path.relpath(
                                root, self.get_data_path(self.binding.current_user)
                            ),
                        ),
                        exist_ok=True,
                    )
                    shutil.copy(
                        os.path.join(root, file),
                        os.path.join(
                            self.binding.save_path,
                            os.path.relpath(
                                root, self.get_data_path(self.binding.current_user)
                            ),
                            file,
                        ),
                    )

        _copy()
        Base.log(
            "I",
            f"将文件从{self.get_data_path(self.binding.current_user)}"
            f"复制到{self.binding.save_path}...",
            "RecoveryPoint.load_onlydata_and_set",
        )
        QMessageBox.information(self.binding, "恢复成功", "恢复成功，请重新启动程序")

        wait_until(lambda: not self.binding.auto_saving)
        _copy()  # 我就不信保存两次还能失败
        pid = os.getpid()  # 获取当前进程的PID
        os.kill(pid, signal.SIGTERM)  # 发送终止信号给当前进程（什么抽象关闭方法）

    def load_onlydata(self, current_user: str):
        """
        只加载数据。
        """
        Base.log("I", "正在从还原点加载数据", "RecoveryPoint.load_onlydata")
        Base.log("I", "还原点路径：" + self.path, "RecoveryPoint.load_onlydata")
        Base.log("I", "还原点模式：" + self.mode, "RecoveryPoint.load_onlydata")
        Base.log("I", "还原点时间：" + str(self.time), "RecoveryPoint.load_onlydata")
        Base.log("I", "当前用户：" + current_user, "RecoveryPoint.load_onlydata")
        return self.binding.load_data(self.get_data_path(current_user), strict=True)