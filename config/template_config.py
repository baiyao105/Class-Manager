"""
模板配置
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ScoreTemplateConfig(BaseModel):
    """积分模板配置"""

    template_id: str = Field(description="模板ID")
    template_name: str = Field(description="模板名称")
    description: str | None = Field(default="", description="模板描述")
    base_score: int = Field(default=0, description="基础分数")
    max_score: int | None = Field(default=None, description="最大分数限制")
    min_score: int | None = Field(default=None, description="最小分数限制")
    is_active: bool = Field(default=True, description="是否展示")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator("template_id")
    @classmethod
    def validate_template_id(cls, v):
        """验证模板ID格式"""
        if not v:
            return str(uuid.uuid4())
        return v


class AchievementTemplateConfig(BaseModel):
    """成就模板配置"""

    template_id: str = Field(description="模板ID")
    template_name: str = Field(description="模板名称")
    description: str | None = Field(default="", description="模板描述")
    trigger_condition: dict[str, int | float | str] = Field(default_factory=dict, description="触发条件")

    # 模板设置
    is_active: bool = Field(default=True, description="是否展示")
    auto_award: bool = Field(default=True, description="自动触发")

    # 时间设置
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator("template_id")
    @classmethod
    def validate_template_id(cls, v):
        """验证模板ID格式"""
        if not v:
            return str(uuid.uuid4())
        return v


class TemplateManager:
    """模板管理器"""

    def __init__(self, class_id: str):
        self.class_id = class_id
        self.base_path = Path(f"./data/Class_{class_id}/Template")
        self.score_path = self.base_path / "Score"
        self.achievement_path = self.base_path / "Achievement"
        self.score_path.mkdir(parents=True, exist_ok=True)
        self.achievement_path.mkdir(parents=True, exist_ok=True)

    def save_score_template(self, template: ScoreTemplateConfig) -> None:
        """保存积分模板"""
        template.updated_at = datetime.now()
        file_path = self.score_path / f"{template.template_id}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(template.model_dump_json(indent=2))

    def load_score_template(self, template_id: str) -> ScoreTemplateConfig | None:
        """加载积分模板"""
        file_path = self.score_path / f"{template_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        return ScoreTemplateConfig.model_validate(data)

    def list_score_templates(self) -> list[ScoreTemplateConfig]:
        """列出所有积分模板"""
        templates = []

        for file_path in self.score_path.glob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                template = ScoreTemplateConfig.model_validate(data)
                templates.append(template)
            except Exception as e:
                print(f"加载积分模板失败 {file_path}: {e}")

        return sorted(templates, key=lambda x: x.created_at, reverse=True)

    def delete_score_template(self, template_id: str) -> bool:
        """删除积分模板"""
        file_path = self.score_path / f"{template_id}.json"

        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def save_achievement_template(self, template: AchievementTemplateConfig) -> None:
        """保存成就模板"""
        template.updated_at = datetime.now()
        file_path = self.achievement_path / f"{template.template_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(template.model_dump_json(indent=2))

    def load_achievement_template(self, template_id: str) -> AchievementTemplateConfig | None:
        """加载成就模板"""
        file_path = self.achievement_path / f"{template_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        return AchievementTemplateConfig.model_validate(data)

    def list_achievement_templates(self) -> list[AchievementTemplateConfig]:
        """列出所有成就模板"""
        templates = []
        for file_path in self.achievement_path.glob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                template = AchievementTemplateConfig.model_validate(data)
                templates.append(template)
            except Exception as e:
                print(f"加载成就模板失败 {file_path}: {e}")

        return sorted(templates, key=lambda x: x.created_at, reverse=True)

    def delete_achievement_template(self, template_id: str) -> bool:
        """删除成就模板"""
        file_path = self.achievement_path / f"{template_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def export_all_templates(self, export_path: Path | None = None) -> dict[str, Any]:
        """导出所有模板"""
        if export_path is None:
            export_path = self.base_path / "export.json"
        export_data = {
            "class_id": self.class_id,
            "export_time": datetime.now().isoformat(),
            "score_templates": [t.model_dump() for t in self.list_score_templates()],
            "achievement_templates": [t.model_dump() for t in self.list_achievement_templates()],
        }
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        return export_data

    def import_templates(self, import_path: Path) -> dict[str, int]:
        """导入模板"""
        if not import_path.exists():
            raise FileNotFoundError(f"导入文件不存在: {import_path}")
        with open(import_path, encoding="utf-8") as f:
            import_data = json.load(f)
        imported_count = {"score": 0, "achievement": 0}
        for template_data in import_data.get("score_templates", []):
            try:
                template = ScoreTemplateConfig.model_validate(template_data)
                self.save_score_template(template)
                imported_count["score"] += 1
            except Exception as e:
                print(f"导入积分模板失败: {e}")

        for template_data in import_data.get("achievement_templates", []):
            try:
                template = AchievementTemplateConfig.model_validate(template_data)
                self.save_achievement_template(template)
                imported_count["achievement"] += 1
            except Exception as e:
                print(f"导入成就模板失败: {e}")

        return imported_count


# 全局模板管理器缓存
_template_managers: dict[str, TemplateManager] = {}


def get_template_manager(class_id: str) -> TemplateManager:
    """获取模板管理器实例"""
    if class_id not in _template_managers:
        _template_managers[class_id] = TemplateManager(class_id)
    return _template_managers[class_id]


def clear_template_manager_cache():
    """清空模板管理器缓存"""
    global _template_managers
    _template_managers.clear()
