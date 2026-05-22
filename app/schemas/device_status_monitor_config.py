"""
设备状态监控配置 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ConditionItem(BaseModel):
    """单个匹配条件"""
    topic_name: str = Field(..., description="MQTT Topic名称")
    field_path: str = Field(..., description="字段路径")
    match_rule: str = Field(default='curve_only', description="匹配规则类型")
    match_value: Optional[str] = Field(None, description="匹配值（JSON格式）")
    extraction_rule: Optional[Dict[str, Any]] = Field(None, description="截取规则配置")
    curve_id: Optional[int] = Field(None, description="关联的DB块参数曲线ID")

    class Config:
        extra = "ignore"


class DeviceStatusMonitorConfigBase(BaseModel):
    """设备状态监控配置基础信息"""
    device_code: Optional[str] = Field(None, description="设备编号（基础规则可为空）")
    rule_scope: str = Field(default="device", description="规则范围：basic=基础规则，device=设备规则")
    status_type: str = Field(..., description="状态类型：processing/stop/fault_stop/emergency stop/mold_change/maintain/alarm/material_shortage")
    topic_name: str = Field(..., description="MQTT Topic名称")
    field_path: str = Field(..., description="字段路径")
    match_rule: str = Field(default='curve_only', description="匹配规则类型")
    match_value: Optional[str] = Field(None, description="匹配值（JSON格式）")
    extraction_rule: Optional[Dict[str, Any]] = Field(None, description="截取规则配置")
    curve_id: Optional[int] = Field(None, description="关联的DB块参数曲线ID")
    logic_operator: str = Field(default="AND", description="条件间逻辑运算符：AND/OR")
    conditions: Optional[List[ConditionItem]] = Field(None, description="多条件组合配置")
    enabled: bool = Field(default=True, description="是否启用")
    priority: int = Field(default=0, description="优先级")
    device_status: Optional[str] = Field(None, description="匹配成功时映射的设备状态：active/inactive/maintenance")
    description: Optional[str] = Field(None, description="备注说明")


class DeviceStatusMonitorConfigCreate(DeviceStatusMonitorConfigBase):
    """创建设备状态监控配置"""
    pass


class DeviceStatusMonitorConfigUpdate(BaseModel):
    """更新设备状态监控配置"""
    device_code: Optional[str] = None
    rule_scope: Optional[str] = None
    topic_name: Optional[str] = None
    field_path: Optional[str] = None
    match_rule: Optional[str] = None
    match_value: Optional[str] = None
    extraction_rule: Optional[Dict[str, Any]] = None
    curve_id: Optional[int] = None
    logic_operator: Optional[str] = None
    conditions: Optional[List[ConditionItem]] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None
    device_status: Optional[str] = None
    description: Optional[str] = None


class DeviceStatusMonitorConfigDetail(DeviceStatusMonitorConfigBase):
    """设备状态监控配置详情"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DeviceStatusMonitorConfigList(BaseModel):
    """设备状态监控配置列表"""
    total: int
    items: List[DeviceStatusMonitorConfigDetail]


class TopicFieldSuggestion(BaseModel):
    """Topic字段建议"""
    field_path: str = Field(..., description="字段路径")
    field_value: Any = Field(None, description="字段值示例")
    field_type: str = Field(..., description="字段类型")


class MatchRuleOption(BaseModel):
    """匹配规则选项"""
    value: str = Field(..., description="规则值")
    label: str = Field(..., description="规则标签")
    description: str = Field(..., description="规则描述")
    requires_value: bool = Field(default=True, description="是否需要匹配值")
    placeholder: str = Field(default="输入匹配值", description="输入框占位符")
    example: str = Field(default="", description="输入示例")
    input_type: str = Field(default="text", description="输入类型：text/number")


class StatusTypeOption(BaseModel):
    """状态类型选项"""
    value: str = Field(..., description="状态值")
    label: str = Field(..., description="状态标签")
    icon: str = Field(..., description="图标")
    color: str = Field(..., description="颜色")
