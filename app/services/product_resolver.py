"""
当前加工物料解析服务
从 MQTT 消息中根据配置规则提取当前加工物料的零件号，并匹配物料和订单信息
"""
import re
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.current_product_config import CurrentProductConfig
from app.models.material import Material
from app.models.product_order import ProductOrder

logger = logging.getLogger(__name__)


def get_nested_value(data: Dict[str, Any], path: str) -> Any:
    """根据点分隔路径提取嵌套字典中的值"""
    if not data or not path:
        return None
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def apply_extraction(value: Any, extraction_rule: Optional[Dict[str, Any]]) -> Any:
    """应用截取规则提取值"""
    if not extraction_rule or not extraction_rule.get('type'):
        return value

    try:
        rule_type = extraction_rule.get('type', '')
        params = extraction_rule.get('params', '')
        str_value = str(value)

        if rule_type == 'regex_extract':
            match = re.search(params, str_value)
            if match:
                return match.group(0)
        elif rule_type == 'split':
            parts = str_value.split(params)
            if parts:
                return parts[0]
        elif rule_type == 'substring':
            if ',' in params:
                start_str, length_str = params.split(',', 1)
                start = int(start_str.strip())
                length = int(length_str.strip())
                return str_value[start:start + length]
            else:
                start = int(params.strip())
                return str_value[start:]
    except Exception as e:
        logger.warning(f"截取规则应用失败: {e}, rule={extraction_rule}")

    return value


def get_latest_mqtt_message(mqtt_buffer: list, topic_name: str) -> Optional[Dict[str, Any]]:
    """从 MQTT 缓冲区获取指定 topic 的最新消息"""
    for message in reversed(mqtt_buffer):
        if message.get('topic') == topic_name:
            return message
    return None


def resolve_product_from_value(
    db: Session,
    extracted_value: str
) -> Optional[Material]:
    """根据提取的值匹配物料（支持 part_number、u9_material_code、specification）"""
    if not extracted_value:
        return None

    return db.query(Material).filter(
        or_(
            Material.part_number == extracted_value,
            Material.u9_material_code == extracted_value,
            Material.specification == extracted_value
        ),
        Material.status == 'active'
    ).first()


def resolve_order_for_product(
    db: Session,
    product: Material,
    query_date: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """查找物料的今日订单信息"""
    if not product or not product.u9_material_code:
        return None

    from datetime import datetime
    if not query_date:
        query_date = datetime.now().strftime('%Y-%m-%d')

    orders = db.query(ProductOrder).filter(
        ProductOrder.u9_material_code == product.u9_material_code,
        ProductOrder.query_date == query_date
    ).all()

    if not orders:
        return None

    total_qty = sum(o.product_qty or 0 for o in orders)
    total_complete = sum(o.total_complete_qty or 0 for o in orders)
    total_eligible = sum(o.total_eligible_qty or 0 for o in orders)

    return {
        "doc_no": orders[0].doc_no,
        "planned_output": orders[0].planned_output,
        "product_qty": total_qty,
        "total_complete_qty": total_complete,
        "total_eligible_qty": total_eligible,
        "doc_state": orders[0].doc_state,
        "line_code": orders[0].line_code,
        "mold_no": orders[0].mold_no,
        "detail_count": len(orders),
    }


def resolve_current_product(
    db: Session,
    device_code: str,
    mqtt_buffer: list,
    latest_event_start_code: Optional[str] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    解析设备当前加工物料和订单信息

    优先使用 CurrentProductConfig 配置从 MQTT 消息中提取，
    如果配置未匹配到，则回退使用最新事件的 start_code。

    Returns:
        (current_product, current_order) 元组
    """
    configs = db.query(CurrentProductConfig).filter(
        CurrentProductConfig.device_code == device_code,
        CurrentProductConfig.enabled == True
    ).order_by(CurrentProductConfig.priority).all()

    extracted_value = None
    matched_product = None

    # 优先使用配置规则
    for config in configs:
        try:
            msg = get_latest_mqtt_message(mqtt_buffer, config.topic_name)
            if not msg:
                continue

            payload = msg.get('payload', {})
            field_value = get_nested_value(payload, config.field_path)

            if field_value is None:
                continue

            extracted_value = str(field_value)

            if config.extraction_rule:
                extracted_value = apply_extraction(extracted_value, config.extraction_rule)
                if extracted_value is None:
                    continue
                extracted_value = str(extracted_value)

            matched_product = resolve_product_from_value(db, extracted_value)
            if matched_product:
                break
        except Exception as e:
            logger.warning(f"配置规则解析失败 (config_id={config.id}): {e}")

    # 回退：使用最新事件的 start_code
    if not matched_product and latest_event_start_code:
        extracted_value = latest_event_start_code
        matched_product = resolve_product_from_value(db, extracted_value)

    # 构建返回数据
    current_product = None
    current_order = None

    if matched_product:
        current_product = {
            "part_number": matched_product.part_number,
            "product_name": matched_product.product_name,
            "u9_material_code": matched_product.u9_material_code,
            "specification": matched_product.specification,
            "category": matched_product.category,
            "project": matched_product.project,
        }
        current_order = resolve_order_for_product(db, matched_product)
    elif extracted_value:
        current_product = {
            "part_number": extracted_value,
            "product_name": None,
            "u9_material_code": None,
            "specification": None,
        }

    return current_product, current_order


def test_config(
    db: Session,
    config: CurrentProductConfig,
    mqtt_buffer: list
) -> Dict[str, Any]:
    """
    测试单个配置规则，返回解析结果

    Returns:
        {
            "success": bool,
            "raw_value": 原始字段值,
            "extracted_value": 截取后的值,
            "matched_product": 匹配到的物料信息 or None,
            "matched_order": 匹配到的订单信息 or None,
            "error": 错误信息 or None
        }
    """
    result = {
        "success": False,
        "raw_value": None,
        "extracted_value": None,
        "matched_product": None,
        "matched_order": None,
        "error": None,
    }

    try:
        msg = get_latest_mqtt_message(mqtt_buffer, config.topic_name)
        if not msg:
            result["error"] = f"未找到 topic '{config.topic_name}' 的最新消息"
            return result

        payload = msg.get('payload', {})
        field_value = get_nested_value(payload, config.field_path)

        if field_value is None:
            result["error"] = f"字段路径 '{config.field_path}' 在消息中不存在"
            return result

        result["raw_value"] = str(field_value)
        extracted = str(field_value)

        if config.extraction_rule:
            extracted = apply_extraction(extracted, config.extraction_rule)
            if extracted is not None:
                extracted = str(extracted)

        result["extracted_value"] = extracted

        if extracted:
            product = resolve_product_from_value(db, extracted)
            if product:
                result["matched_product"] = {
                    "part_number": product.part_number,
                    "product_name": product.product_name,
                    "u9_material_code": product.u9_material_code,
                }
                order = resolve_order_for_product(db, product)
                if order:
                    result["matched_order"] = order

        result["success"] = True
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"测试配置失败: {e}")

    return result
