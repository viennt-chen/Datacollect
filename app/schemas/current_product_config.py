"""
当前加工产品配置 Schema
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime


EXTRACTION_TYPES = {"substring", "regex_extract", "split"}


class ExtractionRule(BaseModel):
    """截取规则配置"""
    type: str = Field(..., description="截取类型: substring, regex_extract, split")
    params: str = Field(..., description="截取参数")
    description: Optional[str] = Field(None, description="规则说明")

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        if v not in EXTRACTION_TYPES:
            raise ValueError(f"不支持的截取类型: {v}，支持: {', '.join(EXTRACTION_TYPES)}")
        return v


class CurrentProductConfigBase(BaseModel):
    """当前加工产品配置基础信息"""
    device_code: str = Field(..., description="设备编号")
    topic_name: str = Field(..., min_length=1, description="MQTT Topic名称")
    field_path: str = Field(..., min_length=1, description="字段路径")
    field_description: Optional[str] = Field(None, max_length=200, description="字段说明")
    extraction_rule: Optional[Dict[str, Any]] = Field(None, description="截取规则配置")
    enabled: bool = Field(default=True, description="是否启用")
    priority: int = Field(default=0, ge=0, description="优先级（数字越小优先级越高）")
    description: Optional[str] = Field(None, description="备注说明")

    @field_validator('extraction_rule')
    @classmethod
    def validate_extraction_rule(cls, v):
        if v is None:
            return v
        if not isinstance(v, dict):
            raise ValueError("extraction_rule 必须是字典类型")
        rule_type = v.get('type')
        if rule_type and rule_type not in EXTRACTION_TYPES:
            raise ValueError(f"不支持的截取类型: {rule_type}，支持: {', '.join(EXTRACTION_TYPES)}")
        if not v.get('params') and rule_type:
            raise ValueError("截取规则的 params 不能为空")
        return v


class CurrentProductConfigCreate(CurrentProductConfigBase):
    """创建当前加工产品配置"""
    pass


class CurrentProductConfigUpdate(BaseModel):
    """更新当前加工产品配置"""
    topic_name: Optional[str] = Field(None, min_length=1)
    field_path: Optional[str] = Field(None, min_length=1)
    field_description: Optional[str] = Field(None, max_length=200)
    extraction_rule: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None

    @field_validator('extraction_rule')
    @classmethod
    def validate_extraction_rule(cls, v):
        if v is None:
            return v
        if not isinstance(v, dict):
            raise ValueError("extraction_rule 必须是字典类型")
        rule_type = v.get('type')
        if rule_type and rule_type not in EXTRACTION_TYPES:
            raise ValueError(f"不支持的截取类型: {rule_type}，支持: {', '.join(EXTRACTION_TYPES)}")
        return v


class CurrentProductConfigDetail(CurrentProductConfigBase):
    """当前加工产品配置详情"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CurrentProductConfigList(BaseModel):
    """当前加工产品配置列表"""
    total: int
    items: list[CurrentProductConfigDetail]


class ConfigTestResult(BaseModel):
    """配置测试结果"""
    success: bool
    raw_value: Optional[str] = None
    extracted_value: Optional[str] = None
    matched_product: Optional[Dict[str, Any]] = None
    matched_order: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BatchToggleRequest(BaseModel):
    """批量切换配置状态"""
    config_ids: List[int] = Field(..., min_length=1, description="配置ID列表")
    enabled: bool = Field(..., description="目标启用状态")


class BatchToggleResult(BaseModel):
    """批量切换结果"""
    updated: int
    enabled: bool


class TopicFieldInfo(BaseModel):
    """Topic 字段信息"""
    topic_name: str
    fields: List[Dict[str, Any]] = Field(default_factory=list)
    sample_message: Optional[Dict[str, Any]] = None
