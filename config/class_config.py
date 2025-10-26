"""班级特殊配置模型

基于Pydantic v2的班级配置系统，支持：
- 快捷栏配置
- 学生排序方法配置
"""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from utils.basic_dirs import DATA


class QuickBarConfig(BaseModel):
    """快捷栏配置"""

    # 快捷栏显示设置
    show_quick_bar: bool = Field(default=True, description="显示快捷栏")
    quick_bar_position: Literal["top", "bottom", "left", "right"] = Field(default="top", description="快捷栏位置")

    # 快捷操作配置
    quick_actions: list[str] = Field(
        default_factory=lambda: [
            "add_score",  # 加分
            "minus_score",  # 减分
            "attendance",  # 考勤
            "homework",  # 作业
            "behavior",  # 行为记录
            "group_score",  # 小组加分
        ],
        description="快捷操作列表",
    )

    # 快捷分数设置
    quick_score_values: list[int] = Field(
        default_factory=lambda: [1, 2, 5, 10, -1, -2, -5, -10], description="快捷分数值"
    )

    # 自定义快捷操作
    custom_actions: dict[str, dict[str, str | int]] = Field(default_factory=dict, description="自定义快捷操作")

    @field_validator("quick_actions")
    @classmethod
    def validate_quick_actions(cls, v):
        """验证快捷操作列表"""
        valid_actions = {
            "add_score",
            "minus_score",
            "attendance",
            "homework",
            "behavior",
            "group_score",
            "achievement",
            "note",
        }
        for action in v:
            if action not in valid_actions and not action.startswith("custom_"):
                raise ValueError(f"无效的快捷操作: {action}")
        return v


class SortingConfig(BaseModel):
    """学生排序配置"""

    # 班级内排序
    class_sort_method: Literal["score", "name", "student_id", "group", "custom"] = Field(
        default="score", description="班级内排序方法"
    )
    class_sort_order: Literal["asc", "desc"] = Field(default="desc", description="班级内排序顺序")

    # 小组内排序
    group_sort_method: Literal["score", "name", "student_id", "custom"] = Field(
        default="score", description="小组内排序方法"
    )
    group_sort_order: Literal["asc", "desc"] = Field(default="desc", description="小组内排序顺序")

    # 自定义排序规则
    custom_sort_rules: list[dict[str, str | int | float]] = Field(default_factory=list, description="自定义排序规则")

    # 排序显示设置
    show_rank_number: bool = Field(default=True, description="显示排名序号")
    highlight_top_students: int = Field(default=3, ge=0, le=10, description="高亮前N名学生")

    # 字母排序设置（当排序方法为name时）
    name_sort_by_pinyin: bool = Field(default=True, description="按拼音排序（中文名）")
    name_sort_ignore_case: bool = Field(default=True, description="忽略大小写")

    @field_validator("custom_sort_rules")
    @classmethod
    def validate_custom_sort_rules(cls, v):
        """验证自定义排序规则"""
        for rule in v:
            if "field" not in rule or "weight" not in rule:
                raise ValueError("自定义排序规则必须包含field和weight字段")
        return v


class ClassConfig(BaseSettings):
    """班级配置模型 - 存储班级基础信息和特殊配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="allow",  # 允许额外字段，便于扩展
    )

    # 班级基本信息 (从数据库迁移到配置文件)
    class_id: str = Field(description="班级ID")
    class_name: str = Field(description="班级名称")
    description: str | None = Field(default=None, description="班级描述")

    # 班主任信息
    teacher_name: str = Field(description="班主任姓名")
    teacher_contact: str | None = Field(default=None, description="班主任联系方式")

    # 班级设置
    max_students: int = Field(default=50, description="最大学生数量")
    class_type: str = Field(default="regular", description="班级类型")

    # 学期信息
    academic_year: str = Field(default="2024-2025", description="学年")
    semester: int = Field(default=1, description="学期(1或2)")

    # 班级状态
    is_active: bool = Field(default=True, description="是否活跃")
    start_date: str | None = Field(default=None, description="开始日期")
    end_date: str | None = Field(default=None, description="结束日期")

    # 配置模块
    quick_bar: QuickBarConfig = Field(default_factory=QuickBarConfig)
    sorting: SortingConfig = Field(default_factory=SortingConfig)

    # 自定义配置字段
    custom_settings: dict[str, str | int | float | bool] = Field(default_factory=dict, description="自定义配置")

    def save_to_file(self, file_path: Path | None = None) -> None:
        """保存配置到文件"""
        if file_path is None:
            file_path = DATA / f"Class_{self.class_id}/config.json"

        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2, exclude={"class_id"}))

    @classmethod
    def load_from_file(cls, class_id: str, file_path: Path | None = None) -> "ClassConfig":
        """从文件加载配置"""
        if file_path is None:
            file_path = DATA / f"Class_{class_id}/config.json"

        if not file_path.exists():
            # 如果文件不存在，创建默认配置
            config = cls(
                class_id=class_id,
                class_name=f"班级_{class_id[:8]}",
                teacher_name="未设置",
                description="",
                max_students=50,
                class_type="regular",
                academic_year="2024-2025",
                semester=1,
                is_active=True,
            )
            config.save_to_file(file_path)
            return config

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # 添加class_id到数据中
        data["class_id"] = class_id
        return cls.model_validate(data)

    def update_setting(self, key_path: str, value: str | int | float | bool) -> None:
        """更新配置项

        Args:
            key_path: 配置路径，如 "quick_bar.show_quick_bar" 或 "custom_settings.my_key"
            value: 新值
        """
        keys = key_path.split(".")
        obj = self

        # 导航到目标对象
        for key in keys[:-1]:
            if hasattr(obj, key):
                obj = getattr(obj, key)
            elif isinstance(obj, dict):
                obj = obj[key]
            else:
                raise ValueError(f"无效的配置路径: {key_path}")

        # 设置值
        final_key = keys[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
        elif isinstance(obj, dict):
            obj[final_key] = value
        else:
            raise ValueError(f"无效的配置路径: {key_path}")

    def get_setting(self, key_path: str, default=None):
        """获取配置项"""
        keys = key_path.split(".")
        obj = self

        try:
            for key in keys:
                if hasattr(obj, key):
                    obj = getattr(obj, key)
                elif isinstance(obj, dict):
                    obj = obj[key]
                else:
                    return default
            return obj
        except (KeyError, AttributeError):
            return default


# 班级配置管理器
class ClassConfigManager:
    """班级配置管理器"""

    _configs: dict[str, ClassConfig] = {}

    @classmethod
    def get_config(cls, class_id: str) -> ClassConfig:
        """获取班级配置"""
        if class_id not in cls._configs:
            cls._configs[class_id] = ClassConfig.load_from_file(class_id)
        return cls._configs[class_id]

    @classmethod
    def reload_config(cls, class_id: str) -> ClassConfig:
        """重新加载班级配置"""
        if class_id in cls._configs:
            del cls._configs[class_id]
        return cls.get_config(class_id)

    @classmethod
    def save_config(cls, class_id: str) -> None:
        """保存班级配置"""
        if class_id in cls._configs:
            cls._configs[class_id].save_to_file()

    @classmethod
    def create_config(cls, class_id: str, class_name: str, teacher_name: str = "未设置", **kwargs) -> ClassConfig:
        """创建新的班级配置"""
        config_data = {
            "class_id": class_id,
            "class_name": class_name,
            "teacher_name": teacher_name,
            "description": kwargs.get("description", ""),
            "max_students": kwargs.get("max_students", 50),
            "class_type": kwargs.get("class_type", "regular"),
            "academic_year": kwargs.get("academic_year", "2024-2025"),
            "semester": kwargs.get("semester", 1),
            "is_active": kwargs.get("is_active", True),
            **kwargs,
        }
        config = ClassConfig(**config_data)
        config.save_to_file()
        cls._configs[class_id] = config
        return config
