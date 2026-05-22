"""
设备状态监控配置模型
用于配置设备各状态（加工、换模、故障、报警、缺料、停机）的MQTT数据源和匹配规则
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from datetime import datetime
from app.database import Base


class DeviceStatusMonitorConfig(Base):
    """设备状态监控配置表"""
    __tablename__ = "device_status_monitor_configs"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 设备编号（基础规则可为空）
    device_code = Column(String(100), ForeignKey('devices.device_code'), nullable=True, index=True, comment='设备编号')

    # 规则范围：basic=基础规则（所有设备默认继承），device=设备规则（覆盖基础规则）
    rule_scope = Column(String(20), default='device', nullable=False, comment='规则范围：basic/device')
    
    # 状态类型
    # processing: 加工状态
    # mold_change: 换模状态
    # fault: 故障状态
    # alarm: 报警状态
    # material_shortage: 缺料状态
    # stop: 停机状态
    status_type = Column(String(50), nullable=False, comment='状态类型')
    
    # 关联的MQTT Topic名称
    topic_name = Column(String(255), nullable=False, comment='MQTT Topic名称')
    
    # 字段路径（支持嵌套，如：extra_data.fault）
    field_path = Column(String(255), nullable=False, comment='字段路径')
    
    # 匹配规则类型
    # equals: 等于
    # not_equals: 不等于
    # contains: 包含
    # not_contains: 不包含
    # starts_with: 开头是
    # ends_with: 结尾是
    # greater_than: 大于
    # less_than: 小于
    # greater_equal: 大于等于
    # less_equal: 小于等于
    # in_range: 在范围内
    # regex: 正则匹配
    # is_true: 为true
    # is_false: 为false
    # is_empty: 为空
    # is_not_empty: 不为空
    match_rule = Column(String(50), nullable=True, default='curve_only', comment='匹配规则类型')
    
    # 匹配值（JSON格式，支持单个值或数组）
    match_value = Column(Text, comment='匹配值')
    
    # 截取规则（JSON格式，包含type和params）
    # type: substring, regex_extract, slice_array, math_operation
    # params: 截取参数，如 "0,5" 或 "\\d+"
    extraction_rule = Column(JSON, comment='截取规则配置')
    
    # 关联的DB块参数曲线ID（可选）
    # 用于通过曲线匹配来判断状态
    curve_id = Column(Integer, nullable=True, index=True, comment='关联的DB块参数曲线ID')
    
    # 条件间逻辑运算符（AND/OR）
    logic_operator = Column(String(10), default='AND', comment='条件间逻辑运算符：AND/OR')
    
    # 多条件组合配置（JSON格式）
    # 支持多个Topic/字段的组合匹配
    conditions = Column(JSON, comment='多条件组合配置')
    
    # 是否启用
    enabled = Column(Boolean, default=True, nullable=False, comment='是否启用')
    
    # 优先级（数字越小优先级越高）
    priority = Column(Integer, default=0, comment='优先级')

    # 匹配成功时映射的设备状态（active/inactive/maintenance/unknown/null）
    # null 表示不更新设备状态
    device_status = Column(String(20), nullable=True, comment='匹配成功时映射的设备状态：active/inactive/maintenance/unknown')
    
    # 备注说明
    description = Column(Text, comment='备注说明')
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def __repr__(self):
        return f"<DeviceStatusMonitorConfig(id={self.id}, device_code='{self.device_code}', status_type='{self.status_type}')>"
