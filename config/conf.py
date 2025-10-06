import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .class_config import ClassConfig, ClassConfigManager
from .global_config import GlobalConfig, GlobalConfigManager
from .template_config import TemplateManager, get_template_manager


class ConfigManager:
    """统一配置管理器"""

    def __init__(self):
        self.global_manager = GlobalConfigManager()
        self.class_managers: dict[str, ClassConfigManager] = {}
        self.template_managers: dict[str, TemplateManager] = {}

    def get_class_manager(self, class_id: str) -> ClassConfigManager:
        """获取班级配置管理器"""
        if class_id not in self.class_managers:
            self.class_managers[class_id] = ClassConfigManager(class_id)
        return self.class_managers[class_id]

    def get_template_manager(self, class_id: str) -> TemplateManager:
        """获取模板管理器"""
        if class_id not in self.template_managers:
            self.template_managers[class_id] = get_template_manager(class_id)
        return self.template_managers[class_id]

    def get_setting(self, key_path: str, class_id: str | None = None, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key_path: 配置路径 (如 "ui.opacity" 或 "quick_bar.show_quick_bar")
            class_id: 班级ID, 如果提供则优先从班级配置读取
            default: 默认值

        Returns:
            配置值
        """
        if class_id:
            class_manager = self.get_class_manager(class_id)
            class_config = class_manager.get_config()
            class_value = class_config.get_setting(key_path, None)
            if class_value is not None:
                return class_value
        global_config = self.global_manager.get_config()
        return global_config.get_setting(key_path, default)

    def set_setting(self, key_path: str, value: Any, class_id: str | None = None) -> None:
        """
        统一设置配置项

        Args:
            key_path: 配置路径
            value: 配置值
            class_id: 班级ID, 如果提供则设置到班级配置
        """
        if class_id:
            class_manager = self.get_class_manager(class_id)
            class_config = class_manager.get_config()
            class_config.update_setting(key_path, value)
            class_manager.save_config()
        else:
            global_config = self.global_manager.get_config()
            global_config.update_setting(key_path, value)
            self.global_manager.save_config()

    def get_merged_config(self, class_id: str) -> dict[str, Any]:
        """
        获取合并后的配置

        Args:
            class_id: 班级ID

        Returns:
            合并后的配置字典
        """
        global_config = self.global_manager.get_config()
        global_dict = global_config.model_dump()
        class_manager = self.get_class_manager(class_id)
        class_config = class_manager.get_config()
        class_dict = class_config.model_dump()
        merged_config = deepcopy(global_dict)
        self._deep_merge(merged_config, class_dict)

        return merged_config

    def _deep_merge(self, base_dict: dict[str, Any], override_dict: dict[str, Any]) -> None:
        """深度合并字典"""
        for key, value in override_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value

    def get_all_class_configs(self) -> dict[str, dict[str, Any]]:
        """获取所有班级配置"""
        configs = {}
        data_path = Path("./data")
        if data_path.exists():
            for class_dir in data_path.glob("Class_*"):
                if class_dir.is_dir():
                    class_id = class_dir.name.replace("Class_", "")
                    try:
                        configs[class_id] = self.get_merged_config(class_id)
                    except Exception as e:
                        print(f"加载班级配置失败 {class_id}: {e}")

        return configs

    def export_all_configs(self, export_path: Path | None = None) -> dict[str, Any]:
        """导出所有配置"""
        if export_path is None:
            export_path = Path("./data/config_export.json")
        export_data = {
            "export_time": str(Path().cwd()),
            "global_config": self.global_manager.get_config().model_dump(),
            "class_configs": self.get_all_class_configs(),
        }
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return export_data

    def import_configs(self, import_path: Path) -> dict[str, int]:
        """导入配置"""
        if not import_path.exists():
            raise FileNotFoundError(f"导入文件不存在: {import_path}")

        with open(import_path, encoding="utf-8") as f:
            import_data = json.load(f)

        imported_count = {"global": 0, "class": 0}
        if "global_config" in import_data:
            try:
                global_config = GlobalConfig.model_validate(import_data["global_config"])
                self.global_manager._config = global_config
                self.global_manager.save_config()
                imported_count["global"] = 1
            except Exception as e:
                print(f"导入全局配置失败: {e}")
        if "class_configs" in import_data:
            for class_id, config_data in import_data["class_configs"].items():
                try:
                    class_data = {
                        "class_id": class_id,
                        "class_name": config_data.get("class_name", f"班级_{class_id[:8]}"),
                        "quick_bar": config_data.get("quick_bar", {}),
                        "sorting": config_data.get("sorting", {}),
                        "custom_settings": config_data.get("custom_settings", {}),
                    }
                    class_config = ClassConfig.model_validate(class_data)
                    class_manager = self.get_class_manager(class_id)
                    class_manager._config = class_config
                    class_manager.save_config()
                    imported_count["class"] += 1
                except Exception as e:
                    print(f"导入班级配置失败 {class_id}: {e}")

        return imported_count

    def get_all_class_ids(self) -> list[str]:
        """获取所有班级ID"""
        class_ids = []
        data_path = Path("./data")
        if data_path.exists():
            for class_dir in data_path.glob("Class_*"):
                if class_dir.is_dir():
                    class_id = class_dir.name.replace("Class_", "")
                    class_ids.append(class_id)
        return class_ids

    def reset_config(self, class_id: str | None = None) -> None:
        """重置配置到默认值"""
        if class_id:
            # 重置班级配置
            class_manager = self.get_class_manager(class_id)
            default_config = ClassConfig(class_id=class_id, class_name=f"班级_{class_id[:8]}")
            class_manager._config = default_config
            class_manager.save_config()
        else:
            # 重置全局配置
            default_config = GlobalConfig()
            self.global_manager._config = default_config
            self.global_manager.save_config()

    def reload_all_configs(self) -> None:
        """重新加载所有配置"""
        self.global_manager.reload_config()
        for class_id in self.get_all_class_ids():
            class_manager = self.get_class_manager(class_id)
            class_manager.reload_config()
        self.template_managers.clear()


_unified_manager: ConfigManager | None = None


def get_conf_manager() -> ConfigManager:
    """获取配置管理器实例"""
    global _unified_manager
    if _unified_manager is None:
        _unified_manager = ConfigManager()
    return _unified_manager


def reload_conf_manager() -> ConfigManager:
    """重新加载配置管理器"""
    global _unified_manager
    _unified_manager = ConfigManager()
    return _unified_manager


def get_config(key_path: str, class_id: str | None = None, default: Any = None) -> Any:
    """获取配置项"""
    return get_conf_manager().get_setting(key_path, class_id, default)


def set_config(key_path: str, value: Any, class_id: str | None = None) -> None:
    """设置配置项"""
    get_conf_manager().set_setting(key_path, value, class_id)


def get_merged_config(class_id: str) -> dict[str, Any]:
    """获取合并配置"""
    return get_conf_manager().get_merged_config(class_id)
