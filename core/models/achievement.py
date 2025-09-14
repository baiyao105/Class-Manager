"""成就数据模型

定义成就系统相关的数据模型和业务逻辑
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship, Column, Text
from pydantic import field_validator, model_validator

from .base import BaseModel, ArchiveMixin, OrderMixin
from config.constants import AchievementConstants


class AchievementType(str, Enum):
    """成就类型枚举"""
    SCORE = AchievementConstants.TYPE_SCORE
    ATTENDANCE = AchievementConstants.TYPE_ATTENDANCE
    BEHAVIOR = AchievementConstants.TYPE_BEHAVIOR
    SPECIAL = AchievementConstants.TYPE_SPECIAL


class AchievementLevel(str, Enum):
    """成就等级枚举"""
    BRONZE = AchievementConstants.LEVEL_BRONZE
    SILVER = AchievementConstants.LEVEL_SILVER
    GOLD = AchievementConstants.LEVEL_GOLD
    DIAMOND = AchievementConstants.LEVEL_DIAMOND


class TriggerType(str, Enum):
    """触发类型枚举"""
    IMMEDIATE = AchievementConstants.TRIGGER_IMMEDIATE
    DAILY = AchievementConstants.TRIGGER_DAILY
    WEEKLY = AchievementConstants.TRIGGER_WEEKLY
    MONTHLY = AchievementConstants.TRIGGER_MONTHLY


class AchievementTemplate(BaseModel, ArchiveMixin, OrderMixin, table=True):
    """成就模板数据模型
    
    定义成就的规则和条件，用于生成具体的成就实例
    """
    
    __tablename__ = "cm_achievement_templates"
    
    # 基本信息
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(
        description="成就唯一标识",
        max_length=50,
        nullable=False,
        unique=True,
        index=True
    )
    name: str = Field(
        description="成就名称",
        max_length=100,
        nullable=False
    )
    description: str = Field(
        description="成就描述",
        max_length=500,
        nullable=False
    )
    
    # 成就属性
    achievement_type: AchievementType = Field(
        description="成就类型"
    )
    level: AchievementLevel = Field(
        description="成就等级"
    )
    
    # 触发条件
    trigger_type: TriggerType = Field(
        default=TriggerType.IMMEDIATE,
        description="触发类型"
    )
    condition_expression: str = Field(
        description="条件表达式（Python表达式）",
        sa_column=Column(Text)
    )
    
    # 成就设置
    is_active: bool = Field(
        default=True,
        description="是否启用"
    )
    is_repeatable: bool = Field(
        default=False,
        description="是否可重复获得"
    )
    max_count: Optional[int] = Field(
        default=None,
        description="最大获得次数（None表示无限制）"
    )
    
    # 奖励设置
    reward_score: float = Field(
        default=0.0,
        description="奖励分数"
    )
    reward_description: Optional[str] = Field(
        default=None,
        description="奖励描述",
        max_length=200
    )
    
    # 显示设置
    icon_name: Optional[str] = Field(
        default=None,
        description="图标名称",
        max_length=50
    )
    color_hex: Optional[str] = Field(
        default=None,
        description="颜色（十六进制）",
        max_length=7
    )
    
    # 关系字段
    achievements: List["Achievement"] = Relationship(
        back_populates="template",
        sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"}
    )
    
    # 验证器
    @field_validator('key')
    @classmethod
    def validate_key(cls, v):
        """验证成就标识"""
        if not v or not v.strip():
            raise ValueError('成就标识不能为空')
        # 只允许字母、数字和下划线
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('成就标识只能包含字母、数字、下划线和连字符')
        return v.strip().lower()
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证成就名称"""
        if not v or not v.strip():
            raise ValueError('成就名称不能为空')
        if len(v.strip()) > 100:
            raise ValueError('成就名称长度不能超过100个字符')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """验证成就描述"""
        if not v or not v.strip():
            raise ValueError('成就描述不能为空')
        if len(v.strip()) > 500:
            raise ValueError('成就描述长度不能超过500个字符')
        return v.strip()
    
    @field_validator('condition_expression')
    @classmethod
    def validate_condition_expression(cls, v):
        """验证条件表达式"""
        if not v or not v.strip():
            raise ValueError('条件表达式不能为空')
        # 这里可以添加更复杂的表达式验证逻辑
        return v.strip()
    
    @field_validator('max_count')
    @classmethod
    def validate_max_count(cls, v):
        """验证最大获得次数"""
        if v is not None and v <= 0:
            raise ValueError('最大获得次数必须大于0')
        return v
    
    @field_validator('color_hex')
    @classmethod
    def validate_color_hex(cls, v):
        """验证颜色值"""
        if v is not None:
            if not v.startswith('#') or len(v) != 7:
                raise ValueError('颜色值必须是7位十六进制格式（如#FF0000）')
            try:
                int(v[1:], 16)
            except ValueError:
                raise ValueError('无效的十六进制颜色值')
        return v
    
    # 业务方法
    def check_condition(self, student: "Student", context: Dict[str, Any] = None) -> bool:
        """检查成就条件是否满足
        
        Args:
            student: 学生对象
            context: 额外的上下文数据
            
        Returns:
            是否满足条件
        """
        if not self.is_active:
            return False
        
        # 构建评估上下文
        eval_context = {
            'student': student,
            'score': student.current_score,
            'total_score': student.total_score,
            'highest_score': student.highest_score,
            'lowest_score': student.lowest_score,
            'rank': student.get_rank_in_class() or 0,
            'class_': student.class_,
            'group': student.group,
        }
        
        # 添加额外上下文
        if context:
            eval_context.update(context)
        
        try:
            # 安全地评估表达式
            return bool(eval(self.condition_expression, {"__builtins__": {}}, eval_context))
        except Exception:
            # 如果表达式评估失败，返回False
            return False
    
    def can_be_awarded_to(self, student: "Student") -> bool:
        """检查是否可以授予给指定学生
        
        Args:
            student: 学生对象
            
        Returns:
            是否可以授予
        """
        if not self.is_active:
            return False
        
        # 检查是否可重复获得
        if not self.is_repeatable:
            # 检查学生是否已经获得过这个成就
            existing_count = len([
                a for a in student.achievements 
                if a.template_id == self.id and not a.is_deleted
            ])
            if existing_count > 0:
                return False
        
        # 检查最大获得次数
        if self.max_count is not None:
            existing_count = len([
                a for a in student.achievements 
                if a.template_id == self.id and not a.is_deleted
            ])
            if existing_count >= self.max_count:
                return False
        
        return True
    
    def get_achievement_count(self) -> int:
        """获取此模板生成的成就总数"""
        if not self.achievements:
            return 0
        return len([a for a in self.achievements if not a.is_deleted])
    
    @property
    def display_color(self) -> str:
        """显示颜色（带默认值）"""
        if self.color_hex:
            return self.color_hex
        
        # 根据等级返回默认颜色
        level_colors = {
            AchievementLevel.BRONZE: "#CD7F32",
            AchievementLevel.SILVER: "#C0C0C0",
            AchievementLevel.GOLD: "#FFD700",
            AchievementLevel.DIAMOND: "#B9F2FF"
        }
        return level_colors.get(self.level, "#808080")


class Achievement(BaseModel, ArchiveMixin, table=True):
    """成就实例数据模型
    
    学生获得的具体成就记录
    """
    
    __tablename__ = "cm_achievements"
    
    # 基本信息
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 关联信息
    template_id: int = Field(
        foreign_key="cm_achievement_templates.id",
        description="成就模板ID"
    )
    student_id: int = Field(
        foreign_key="cm_students.id",
        description="学生ID"
    )
    
    # 获得信息
    achieved_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="获得时间"
    )
    achieved_score: float = Field(
        description="获得时的分数"
    )
    achieved_rank: Optional[int] = Field(
        default=None,
        description="获得时的排名"
    )
    
    # 额外信息
    notes: Optional[str] = Field(
        default=None,
        description="备注信息",
        max_length=200
    )
    
    # 关系字段
    template: AchievementTemplate = Relationship(
        back_populates="achievements",
        sa_relationship_kwargs={"lazy": "select"}
    )
    student: "Student" = Relationship(
        back_populates="achievements",
        sa_relationship_kwargs={"lazy": "select"}
    )
    
    # 验证器
    @field_validator('achieved_score')
    @classmethod
    def validate_achieved_score(cls, v):
        """验证获得时分数"""
        if v < -999 or v > 999:
            raise ValueError('分数必须在-999到999范围内')
        return v
    
    @field_validator('achieved_rank')
    @classmethod
    def validate_achieved_rank(cls, v):
        """验证获得时排名"""
        if v is not None and v <= 0:
            raise ValueError('排名必须大于0')
        return v
    
    # 业务方法
    def get_achievement_info(self) -> Dict[str, Any]:
        """获取成就详细信息"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'template_key': self.template.key,
            'template_name': self.template.name,
            'template_description': self.template.description,
            'achievement_type': self.template.achievement_type,
            'level': self.template.level,
            'achieved_at': self.achieved_at,
            'achieved_score': self.achieved_score,
            'achieved_rank': self.achieved_rank,
            'reward_score': self.template.reward_score,
            'notes': self.notes,
            'color': self.template.display_color,
            'icon': self.template.icon_name
        }
    
    @property
    def display_name(self) -> str:
        """显示名称"""
        return f"{self.template.name} ({self.achieved_at.strftime('%Y-%m-%d')})"


class ScoreModificationTemplate(BaseModel, ArchiveMixin, OrderMixin, table=True):
    """分数修改模板数据模型
    
    定义常用的分数修改操作模板
    """
    
    __tablename__ = "cm_score_modification_templates"
    
    # 基本信息
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(
        description="模板唯一标识",
        max_length=50,
        nullable=False,
        unique=True,
        index=True
    )
    name: str = Field(
        description="模板名称",
        max_length=100,
        nullable=False
    )
    description: str = Field(
        description="模板描述",
        max_length=500,
        nullable=False
    )
    
    # 分数修改
    score_change: float = Field(
        description="分数变化量"
    )
    
    # 分类和标签
    category: str = Field(
        description="分类",
        max_length=50,
        default="general"
    )
    tags: Optional[str] = Field(
        default=None,
        description="标签（逗号分隔）",
        max_length=200
    )
    
    # 模板设置
    is_active: bool = Field(
        default=True,
        description="是否启用"
    )
    is_visible: bool = Field(
        default=True,
        description="是否在界面中显示"
    )
    can_be_replaced: bool = Field(
        default=True,
        description="是否可以被替换"
    )
    
    # 显示设置
    color_hex: Optional[str] = Field(
        default=None,
        description="颜色（十六进制）",
        max_length=7
    )
    icon_name: Optional[str] = Field(
        default=None,
        description="图标名称",
        max_length=50
    )
    
    # 关系字段
    # score_modifications: List["ScoreModification"] = Relationship(
    #     back_populates="template",
    #     sa_relationship_kwargs={"lazy": "select"}
    # )
    
    # 验证器
    @field_validator('key')
    @classmethod
    def validate_key(cls, v):
        """验证模板标识"""
        if not v or not v.strip():
            raise ValueError('模板标识不能为空')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('模板标识只能包含字母、数字、下划线和连字符')
        return v.strip().lower()
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证模板名称"""
        if not v or not v.strip():
            raise ValueError('模板名称不能为空')
        return v.strip()
    
    @field_validator('score_change')
    @classmethod
    def validate_score_change(cls, v):
        """验证分数变化量"""
        if abs(v) > 100:
            raise ValueError('分数变化量不能超过±100')
        return v
    
    @field_validator('color_hex')
    @classmethod
    def validate_color_hex(cls, v):
        """验证颜色值"""
        if v is not None:
            if not v.startswith('#') or len(v) != 7:
                raise ValueError('颜色值必须是7位十六进制格式（如#FF0000）')
            try:
                int(v[1:], 16)
            except ValueError:
                raise ValueError('无效的十六进制颜色值')
        return v
    
    # 业务方法
    def create_modification(self, student: "Student", custom_score: Optional[float] = None, 
                          notes: Optional[str] = None) -> "ScoreModification":
        """创建分数修改记录
        
        Args:
            student: 目标学生
            custom_score: 自定义分数变化量（覆盖模板默认值）
            notes: 备注信息
            
        Returns:
            分数修改记录
        """
        from .score_modification import ScoreModification  # 避免循环导入
        
        return ScoreModification(
            template_id=self.id,
            student_id=student.id,
            score_change=custom_score if custom_score is not None else self.score_change,
            notes=notes,
            executed_at=datetime.utcnow()
        )
    
    def get_usage_count(self) -> int:
        """获取使用次数"""
        if not self.score_modifications:
            return 0
        return len([m for m in self.score_modifications if not m.is_deleted])
    
    @property
    def display_color(self) -> str:
        """显示颜色（带默认值）"""
        if self.color_hex:
            return self.color_hex
        
        # 根据分数变化返回默认颜色
        if self.score_change > 0:
            return "#10b981"  # 绿色（正分）
        elif self.score_change < 0:
            return "#ef4444"  # 红色（负分）
        else:
            return "#6b7280"  # 灰色（零分）
    
    @property
    def tag_list(self) -> List[str]:
        """标签列表"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


# 数据传输对象
class AchievementTemplateCreate(SQLModel):
    """创建成就模板的数据模型"""
    key: str = Field(description="成就唯一标识", max_length=50)
    name: str = Field(description="成就名称", max_length=100)
    description: str = Field(description="成就描述", max_length=500)
    achievement_type: AchievementType = Field(description="成就类型")
    level: AchievementLevel = Field(description="成就等级")
    trigger_type: TriggerType = Field(default=TriggerType.IMMEDIATE, description="触发类型")
    condition_expression: str = Field(description="条件表达式")
    is_repeatable: bool = Field(default=False, description="是否可重复获得")
    max_count: Optional[int] = Field(default=None, description="最大获得次数")
    reward_score: float = Field(default=0.0, description="奖励分数")
    reward_description: Optional[str] = Field(default=None, description="奖励描述", max_length=200)
    icon_name: Optional[str] = Field(default=None, description="图标名称", max_length=50)
    color_hex: Optional[str] = Field(default=None, description="颜色", max_length=7)


class AchievementTemplateUpdate(SQLModel):
    """更新成就模板的数据模型"""
    name: Optional[str] = Field(default=None, description="成就名称", max_length=100)
    description: Optional[str] = Field(default=None, description="成就描述", max_length=500)
    achievement_type: Optional[AchievementType] = Field(default=None, description="成就类型")
    level: Optional[AchievementLevel] = Field(default=None, description="成就等级")
    trigger_type: Optional[TriggerType] = Field(default=None, description="触发类型")
    condition_expression: Optional[str] = Field(default=None, description="条件表达式")
    is_active: Optional[bool] = Field(default=None, description="是否启用")
    is_repeatable: Optional[bool] = Field(default=None, description="是否可重复获得")
    max_count: Optional[int] = Field(default=None, description="最大获得次数")
    reward_score: Optional[float] = Field(default=None, description="奖励分数")
    reward_description: Optional[str] = Field(default=None, description="奖励描述", max_length=200)
    icon_name: Optional[str] = Field(default=None, description="图标名称", max_length=50)
    color_hex: Optional[str] = Field(default=None, description="颜色", max_length=7)


class AchievementTemplateRead(SQLModel):
    """读取成就模板的数据模型"""
    id: int
    uuid: str
    key: str
    name: str
    description: str
    achievement_type: AchievementType
    level: AchievementLevel
    trigger_type: TriggerType
    condition_expression: str
    is_active: bool
    is_repeatable: bool
    max_count: Optional[int]
    reward_score: float
    reward_description: Optional[str]
    icon_name: Optional[str]
    color_hex: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AchievementRead(SQLModel):
    """读取成就的数据模型"""
    id: int
    uuid: str
    template_id: int
    student_id: int
    achieved_at: datetime
    achieved_score: float
    achieved_rank: Optional[int]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScoreModificationTemplateCreate(SQLModel):
    """创建分数修改模板的数据模型"""
    key: str = Field(description="模板唯一标识", max_length=50)
    name: str = Field(description="模板名称", max_length=100)
    description: str = Field(description="模板描述", max_length=500)
    score_change: float = Field(description="分数变化量")
    category: str = Field(default="general", description="分类", max_length=50)
    tags: Optional[str] = Field(default=None, description="标签", max_length=200)
    is_visible: bool = Field(default=True, description="是否显示")
    can_be_replaced: bool = Field(default=True, description="是否可替换")
    color_hex: Optional[str] = Field(default=None, description="颜色", max_length=7)
    icon_name: Optional[str] = Field(default=None, description="图标名称", max_length=50)


class ScoreModificationTemplateUpdate(SQLModel):
    """更新分数修改模板的数据模型"""
    name: Optional[str] = Field(default=None, description="模板名称", max_length=100)
    description: Optional[str] = Field(default=None, description="模板描述", max_length=500)
    score_change: Optional[float] = Field(default=None, description="分数变化量")
    category: Optional[str] = Field(default=None, description="分类", max_length=50)
    tags: Optional[str] = Field(default=None, description="标签", max_length=200)
    is_active: Optional[bool] = Field(default=None, description="是否启用")
    is_visible: Optional[bool] = Field(default=None, description="是否显示")
    can_be_replaced: Optional[bool] = Field(default=None, description="是否可替换")
    color_hex: Optional[str] = Field(default=None, description="颜色", max_length=7)
    icon_name: Optional[str] = Field(default=None, description="图标名称", max_length=50)


class ScoreModificationTemplateRead(SQLModel):
    """读取分数修改模板的数据模型"""
    id: int
    uuid: str
    key: str
    name: str
    description: str
    score_change: float
    category: str
    tags: Optional[str]
    is_active: bool
    is_visible: bool
    can_be_replaced: bool
    color_hex: Optional[str]
    icon_name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True