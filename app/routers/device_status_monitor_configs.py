"""
设备状态规则配置 API 路由
功能：管理设备各状态的MQTT数据源和匹配规则配置
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from app.database import get_db
from app.models.device_status_monitor_config import DeviceStatusMonitorConfig
from app.models.device import Device
from app.models.mqtt_topic_config import MQTTTopicConfig
from app.schemas.device_status_monitor_config import (
    DeviceStatusMonitorConfigCreate,
    DeviceStatusMonitorConfigUpdate,
    DeviceStatusMonitorConfigDetail,
    DeviceStatusMonitorConfigList,
    TopicFieldSuggestion,
    MatchRuleOption,
    StatusTypeOption
)
from app.services.mqtt_collector import get_collector

router = APIRouter(prefix="/devices/status-monitor-configs", tags=["设备状态规则配置"])


MATCH_RULE_OPTIONS = [
    MatchRuleOption(value="equals", label="等于", description="字段值等于匹配值", requires_value=True, placeholder="输入匹配值", example="1 或 \"OK\"", input_type="text"),
    MatchRuleOption(value="not_equals", label="不等于", description="字段值不等于匹配值", requires_value=True, placeholder="输入匹配值", example="0 或 \"NG\"", input_type="text"),
    MatchRuleOption(value="contains", label="包含", description="字段值包含匹配值", requires_value=True, placeholder="输入要匹配的字符串", example="error", input_type="text"),
    MatchRuleOption(value="not_contains", label="不包含", description="字段值不包含匹配值", requires_value=True, placeholder="输入要排除的字符串", example="error", input_type="text"),
    MatchRuleOption(value="starts_with", label="开头是", description="字段值以匹配值开头", requires_value=True, placeholder="输入开头字符串", example="ERR", input_type="text"),
    MatchRuleOption(value="ends_with", label="结尾是", description="字段值以匹配值结尾", requires_value=True, placeholder="输入结尾字符串", example="_OK", input_type="text"),
    MatchRuleOption(value="greater_than", label="大于", description="字段值大于匹配值", requires_value=True, placeholder="输入数值", example="100", input_type="number"),
    MatchRuleOption(value="less_than", label="小于", description="字段值小于匹配值", requires_value=True, placeholder="输入数值", example="50", input_type="number"),
    MatchRuleOption(value="greater_equal", label="大于等于", description="字段值大于等于匹配值", requires_value=True, placeholder="输入数值", example="100", input_type="number"),
    MatchRuleOption(value="less_equal", label="小于等于", description="字段值小于等于匹配值", requires_value=True, placeholder="输入数值", example="50", input_type="number"),
    MatchRuleOption(value="in_range", label="在范围内", description="字段值在指定范围内（含边界）", requires_value=True, placeholder="输入范围，如 350-353 或 [350,353]", example="350-353", input_type="text"),
    MatchRuleOption(value="regex", label="正则匹配", description="字段值匹配正则表达式", requires_value=True, placeholder="输入正则表达式", example="^ERR\\d+$", input_type="text"),
    MatchRuleOption(value="is_true", label="为true", description="字段值为true（或1、\"true\"）", requires_value=False, placeholder="", example="", input_type="text"),
    MatchRuleOption(value="is_false", label="为false", description="字段值为false（或0、\"false\"）", requires_value=False, placeholder="", example="", input_type="text"),
    MatchRuleOption(value="is_empty", label="为空", description="字段值为空（null、空字符串、空数组）", requires_value=False, placeholder="", example="", input_type="text"),
    MatchRuleOption(value="is_not_empty", label="不为空", description="字段值不为空", requires_value=False, placeholder="", example="", input_type="text"),
]

STATUS_TYPE_OPTIONS = [
    StatusTypeOption(value="processing", label="计划加工", icon="bi-play-circle-fill", color="#52c41a"),
    StatusTypeOption(value="stop", label="计划停机", icon="bi-stop-circle-fill", color="#ff4d4f"),
    StatusTypeOption(value="fault_stop", label="故障停机", icon="bi-exclamation-triangle-fill", color="#ff4d4f"),
    StatusTypeOption(value="emergency stop", label="紧急停机", icon="bi-x-octagon-fill", color="#cf1322"),
    StatusTypeOption(value="mold_change", label="换模", icon="bi-arrow-repeat", color="#faad14"),
    StatusTypeOption(value="maintain", label="维护", icon="bi-wrench", color="#1890ff"),
    StatusTypeOption(value="alarm", label="报警", icon="bi-bell-fill", color="#fa8c16"),
    StatusTypeOption(value="material_shortage", label="缺料", icon="bi-box-seam", color="#8c8c8c"),
]


@router.get("/options/match-rules")
async def get_match_rule_options():
    """获取匹配规则选项"""
    return {"rules": MATCH_RULE_OPTIONS}


@router.get("/options/status-types")
async def get_status_type_options():
    """获取状态类型选项"""
    return {"status_types": STATUS_TYPE_OPTIONS}


@router.get("/device/{device_code}/topics")
async def get_device_topics_and_fields(
    device_code: str,
    db: Session = Depends(get_db)
):
    """
    获取设备关联的topic及其最新字段列表

    从MQTT实时消息缓冲区获取每个topic的最新消息，提取所有字段路径
    """
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    mqtt_topics = []
    if device.mqtt_topics:
        try:
            mqtt_topics = json.loads(device.mqtt_topics)
        except:
            mqtt_topics = []
    
    topic_configs = db.query(MQTTTopicConfig).filter(
        MQTTTopicConfig.topic_name.in_(mqtt_topics)
    ).all()
    
    mqtt_collector = get_collector()
    mqtt_buffer = mqtt_collector.data_buffer if mqtt_collector else []
    
    def get_latest_mqtt_message(topic_name: str) -> Optional[Dict[str, Any]]:
        for message in reversed(mqtt_buffer):
            if message.get('topic') == topic_name:
                return message
        return None
    
    def flatten_object(obj: Any, prefix: str = '') -> List[Dict[str, Any]]:
        fields = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    fields.extend(flatten_object(value, full_key))
                else:
                    fields.append({
                        "field_path": full_key,
                        "field_value": value,
                        "field_type": type(value).__name__
                    })
        return fields
    
    result = []
    for topic_config in topic_configs:
        latest_msg = get_latest_mqtt_message(topic_config.topic_name)
        
        fields = []
        if latest_msg:
            payload = latest_msg.get('payload', {})
            fields = flatten_object(payload)
        
        result.append({
            "topic_name": topic_config.topic_name,
            "topic_type": topic_config.topic_type,
            "description": topic_config.description,
            "latest_message_time": latest_msg.get('timestamp') if latest_msg else None,
            "fields": fields,
            "field_count": len(fields)
        })
    
    return {
        "device_code": device.device_code,
        "device_name": device.device_name,
        "topics": result
    }


@router.get("/device/{device_code}", response_model=DeviceStatusMonitorConfigList)
async def list_device_status_configs(
    device_code: str,
    status_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取设备的状态监控配置列表

    Args:
        device_code: 设备编号
        status_type: 状态类型筛选
    """
    query = db.query(DeviceStatusMonitorConfig).filter(
        DeviceStatusMonitorConfig.device_code == device_code,
        DeviceStatusMonitorConfig.rule_scope == 'device'
    )

    if status_type:
        query = query.filter(DeviceStatusMonitorConfig.status_type == status_type)
    
    total = query.count()
    items = query.order_by(
        DeviceStatusMonitorConfig.status_type,
        DeviceStatusMonitorConfig.priority
    ).all()
    
    return DeviceStatusMonitorConfigList(total=total, items=items)


@router.get("/device/{device_code}/all-rules", response_model=DeviceStatusMonitorConfigList)
async def list_all_device_rules(
    device_code: str,
    status_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取设备的全部规则（基础规则 + 设备规则）"""
    query = db.query(DeviceStatusMonitorConfig).filter(
        or_(
            and_(DeviceStatusMonitorConfig.device_code == device_code, DeviceStatusMonitorConfig.rule_scope == 'device'),
            and_(DeviceStatusMonitorConfig.device_code.is_(None), DeviceStatusMonitorConfig.rule_scope == 'basic')
        )
    )

    if status_type:
        query = query.filter(DeviceStatusMonitorConfig.status_type == status_type)

    total = query.count()
    items = query.order_by(
        DeviceStatusMonitorConfig.status_type,
        DeviceStatusMonitorConfig.priority
    ).all()

    return DeviceStatusMonitorConfigList(total=total, items=items)


@router.get("/basic-rules", response_model=DeviceStatusMonitorConfigList)
async def list_basic_rules(
    status_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取基础规则列表（所有设备默认继承）"""
    query = db.query(DeviceStatusMonitorConfig).filter(
        DeviceStatusMonitorConfig.rule_scope == 'basic'
    )

    if status_type:
        query = query.filter(DeviceStatusMonitorConfig.status_type == status_type)

    total = query.count()
    items = query.order_by(
        DeviceStatusMonitorConfig.status_type,
        DeviceStatusMonitorConfig.priority
    ).all()

    return DeviceStatusMonitorConfigList(total=total, items=items)


@router.post("/", response_model=DeviceStatusMonitorConfigDetail)
async def create_status_config(
    config: DeviceStatusMonitorConfigCreate,
    db: Session = Depends(get_db)
):
    """
    创建设备状态规则配置

    Args:
        config: 配置信息
    """
    rule_scope = config.rule_scope or 'device'

    # 基础规则不需要设备编号
    if rule_scope == 'device':
        if not config.device_code:
            raise HTTPException(status_code=400, detail="设备规则必须指定设备编号")
        device = db.query(Device).filter(Device.device_code == config.device_code).first()
        if not device:
            raise HTTPException(status_code=404, detail="设备不存在")

    # 检查重复
    existing_query = db.query(DeviceStatusMonitorConfig).filter(
        DeviceStatusMonitorConfig.rule_scope == rule_scope,
        DeviceStatusMonitorConfig.status_type == config.status_type,
        DeviceStatusMonitorConfig.topic_name == config.topic_name,
        DeviceStatusMonitorConfig.field_path == config.field_path
    )
    if rule_scope == 'device':
        existing_query = existing_query.filter(DeviceStatusMonitorConfig.device_code == config.device_code)
    else:
        existing_query = existing_query.filter(DeviceStatusMonitorConfig.device_code.is_(None))

    existing = existing_query.first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="该状态类型的相同Topic和字段配置已存在"
        )
    
    conditions_data = None
    if config.conditions:
        conditions_data = [c.dict() for c in config.conditions]

    # 仅曲线绑定时，match_rule 默认为 'curve_only'
    match_rule = config.match_rule
    if not match_rule and config.curve_id:
        match_rule = 'curve_only'

    db_config = DeviceStatusMonitorConfig(
        device_code=config.device_code if rule_scope == 'device' else None,
        rule_scope=rule_scope,
        status_type=config.status_type,
        topic_name=config.topic_name,
        field_path=config.field_path,
        match_rule=match_rule,
        match_value=config.match_value,
        extraction_rule=config.extraction_rule,
        curve_id=config.curve_id,
        logic_operator=config.logic_operator,
        conditions=conditions_data,
        enabled=config.enabled,
        priority=config.priority,
        device_status=config.device_status,
        description=config.description
    )
    
    db.add(db_config)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")
    db.refresh(db_config)

    return db_config


@router.get("/{config_id}", response_model=DeviceStatusMonitorConfigDetail)
async def get_status_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """获取状态监控配置详情"""
    config = db.query(DeviceStatusMonitorConfig).filter(
        DeviceStatusMonitorConfig.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return config


@router.put("/{config_id}", response_model=DeviceStatusMonitorConfigDetail)
async def update_status_config(
    config_id: int,
    config_update: DeviceStatusMonitorConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新状态监控配置"""
    config = db.query(DeviceStatusMonitorConfig).filter(
        DeviceStatusMonitorConfig.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    update_data = config_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    config.updated_at = datetime.now()
    
    db.commit()
    db.refresh(config)
    
    return config


@router.delete("/{config_id}")
async def delete_status_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """删除状态监控配置"""
    config = db.query(DeviceStatusMonitorConfig).filter(
        DeviceStatusMonitorConfig.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    db.delete(config)
    db.commit()
    
    return {"message": "配置已删除"}


@router.post("/device/{device_code}/batch")
async def batch_update_status_configs(
    device_code: str,
    configs: List[DeviceStatusMonitorConfigCreate],
    db: Session = Depends(get_db)
):
    """
    批量更新设备状态规则配置

    先删除该设备的所有配置，然后批量创建新配置
    """
    device = db.query(Device).filter(Device.device_code == device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    db.query(DeviceStatusMonitorConfig).filter(
        DeviceStatusMonitorConfig.device_code == device_code
    ).delete()
    
    created_configs = []
    for config_data in configs:
        conditions_data = None
        if config_data.conditions:
            conditions_data = [c.dict() for c in config_data.conditions]
        
        # 仅曲线绑定时，match_rule 默认为 'curve_only'
        match_rule = config_data.match_rule
        if not match_rule and config_data.curve_id:
            match_rule = 'curve_only'

        db_config = DeviceStatusMonitorConfig(
            device_code=config_data.device_code,
            status_type=config_data.status_type,
            topic_name=config_data.topic_name,
            field_path=config_data.field_path,
            match_rule=match_rule,
            match_value=config_data.match_value,
            extraction_rule=config_data.extraction_rule,
            curve_id=config_data.curve_id,
            logic_operator=config_data.logic_operator,
            conditions=conditions_data,
            enabled=config_data.enabled,
            priority=config_data.priority,
            device_status=config_data.device_status,
            description=config_data.description
        )
        db.add(db_config)
        created_configs.append(db_config)
    
    db.commit()
    
    return {
        "message": f"成功创建 {len(created_configs)} 条配置",
        "configs": [
            {
                "id": c.id,
                "status_type": c.status_type,
                "topic_name": c.topic_name,
                "field_path": c.field_path,
                "match_rule": c.match_rule
            }
            for c in created_configs
        ]
    }
