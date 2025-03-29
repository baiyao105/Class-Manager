from typing import Literal, Any
import pickle
import os
import dill as pickle
from types import MethodType, FunctionType
from utils.basetypes import Base
from utils.update_check import CLIENT_VERSION, CLIENT_VERSION_CODE

class SettingsInfo:
        """设置信息类，用于管理和存储应用程序的配置参数"""

        current: "SettingsInfo"
        
        def __init__(self, **kwargs):
            """初始化设置信息对象
            
            :param kwargs: 键值对形式的初始设置参数
            """
            self.reset()
            for k, v in kwargs.items():
                setattr(self, k, v)

        def reset(self) -> "SettingsInfo":
            """重置所有设置参数为默认值
            
            :return: 重置后的设置信息对象
            """

            if not hasattr(self, "client_version"):
                self.client_version = CLIENT_VERSION
                self.client_version_code = CLIENT_VERSION_CODE
                
            self.opacity = 0.82
            self.score_up_color_mixin_begin = (0xca, 0xff, 0xca) 
            self.score_up_color_mixin_end = (0x33, 0xcf, 0x6c)
            self.score_up_color_mixin_step = 15
            self.score_up_color_mixin_start = 2
            self.score_up_flash_framelength_base = 300
            self.score_up_flash_framelength_step = 100
            self.score_up_flash_framelength_max = 2000

            self.score_down_color_mixin_begin = (0xfc, 0xb5, 0xb5)
            self.score_down_color_mixin_end = (0xa9, 0x00, 0x00)
            self.score_down_color_mixin_step = 15
            self.score_down_color_mixin_start = 2
            self.score_down_flash_framelength_base = 300
            self.score_down_flash_framelength_step = 100
            self.score_down_flash_framelength_max = 2000

            self.log_file_path = 'class_manager.log'
            self.log_format = '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {module}:{function}:{line} - {message}'
            self.log_keep_linecount = 100
            self.log_update_interval = 0.1

            self.auto_save_enabled = True
            self.auto_save_interval = 300
            self.auto_save_path:Literal["folder", "user"] = "folder"
            self.auto_backup_scheme:Literal["none", "only_data", "all"] = "none"

            self.animation_speed = 1.0
            self.subwindow_x_offset = 0
            self.subwindow_y_offset = 0
            self.use_animate_background = False
            self.max_framerate = 60
            return self

        def save_to(self, file_path:str) -> "SettingsInfo":
            """将当前设置保存到指定文件
            
            :param file_path: 保存设置的文件路径
            :return: 当前设置信息对象
            """
            Base.log("I", f"保存设置到{file_path}", "SettingsInfo.save_to")
            if not os.path.isdir(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            os.remove(file_path) if os.path.exists(file_path) else None
            try:
                pickle.dump(self, open(file_path, "wb"))
            except Exception as e:
                Base.log_exc("保存设置失败", "SettingsInfo.save_to", exc=e)
            return self

        def load_from(self, file_path:str) -> "SettingsInfo":
            """从指定文件加载设置
            
            :param file_path: 设置文件的路径
            :return: 加载后的设置信息对象
            """
            try:
                obj: "SettingsInfo" = pickle.load(open(file_path, "rb"))
                self.__dict__.update(obj.get_dict())
            except Exception as e:
                Base.log_exc("加载设置失败，将会返回默认", "SettingsInfo.load_from", exc=e)
                self.reset()
                self.save_to(file_path)
            return self

        def set(self, **kwargs) -> "SettingsInfo":
            """批量设置多个配置参数
            
            :param kwargs: 键值对形式的设置参数
            :return: 当前设置信息对象
            """
            Base.log("I", "设置设置", "SettingsInfo.set")
            for k, v in kwargs.items():
                setattr(self, k, v)
            return self
        
        def get(self, key:str) -> Any:
            """获取指定键名的设置值
            
            :param key: 设置参数的键名
            :return: 对应的设置值
            """
            return getattr(self, key)

        def get_dict(self):
            """返回所有设置参数的字典表示
            
            :return: 包含所有设置的字典
            """
            return dict((k, v) for k, v in self.__dict__.items() 
                        if (not k.startswith('__')) and 
                        (not isinstance(k, (FunctionType, MethodType))))
        
        def __repr__(self):
            "返回设置信息"
            return f"SettingsInfo({dict((k, v) for k, v in self.__dict__.items() if not k.startswith('__')) !r})"
        

SettingsInfo.current = SettingsInfo()
