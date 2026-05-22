"""
规则评估工具模块 - 优化版

提供设备状态监控规则的评估函数，包括增强的曲线匹配算法。
支持起始点随机、分段匹配、斜率验证等功能。
"""
import re
import json
import bisect
from typing import Any, Dict, List, Optional, Callable, Tuple
from datetime import datetime


# ==================== 基础工具函数 ====================

def get_nested_value(data: Dict[str, Any], path: str) -> Any:
    """从嵌套字典中按点分路径获取值"""
    if isinstance(data, dict) and path in data:
        return data[path]
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def match_value(actual_value: Any, match_rule: str, match_value_str: Optional[str]) -> bool:
    """评估单个匹配规则"""
    if match_rule == 'curve_only':
        return False
    if match_rule == 'is_true':
        return actual_value is True or actual_value == 'true' or actual_value == 'True' or actual_value == 1
    elif match_rule == 'is_false':
        return actual_value is False or actual_value == 'false' or actual_value == 'False' or actual_value == 0
    elif match_rule == 'is_empty':
        return actual_value is None or actual_value == '' or actual_value == []
    elif match_rule == 'is_not_empty':
        return actual_value is not None and actual_value != '' and actual_value != []

    if match_value_str is None:
        return False

    try:
        match_value_parsed = json.loads(match_value_str)
    except:
        match_value_parsed = match_value_str

    if match_rule == 'equals':
        return actual_value == match_value_parsed
    elif match_rule == 'not_equals':
        return actual_value != match_value_parsed
    elif match_rule == 'contains':
        return isinstance(actual_value, str) and str(match_value_parsed) in actual_value
    elif match_rule == 'not_contains':
        return isinstance(actual_value, str) and str(match_value_parsed) not in actual_value
    elif match_rule == 'starts_with':
        return isinstance(actual_value, str) and actual_value.startswith(str(match_value_parsed))
    elif match_rule == 'ends_with':
        return isinstance(actual_value, str) and actual_value.endswith(str(match_value_parsed))
    elif match_rule == 'greater_than':
        try:
            return float(actual_value) > float(match_value_parsed)
        except:
            return False
    elif match_rule == 'less_than':
        try:
            return float(actual_value) < float(match_value_parsed)
        except:
            return False
    elif match_rule == 'greater_equal':
        try:
            return float(actual_value) >= float(match_value_parsed)
        except:
            return False
    elif match_rule == 'less_equal':
        try:
            return float(actual_value) <= float(match_value_parsed)
        except:
            return False
    elif match_rule == 'in_range':
        try:
            if isinstance(match_value_parsed, list) and len(match_value_parsed) == 2:
                min_val, max_val = float(match_value_parsed[0]), float(match_value_parsed[1])
            else:
                range_match = re.match(r'[\[\(]?\s*([\d.]+)\s*[-,]\s*([\d.]+)\s*[\]\)]?', str(match_value_str))
                if range_match:
                    min_val, max_val = float(range_match.group(1)), float(range_match.group(2))
                else:
                    return False
            return min_val <= float(actual_value) <= max_val
        except:
            return False
    elif match_rule == 'regex':
        try:
            return bool(re.match(str(match_value_parsed), str(actual_value)))
        except:
            return False

    return False


def apply_extraction(value: Any, extraction_rule: Dict[str, Any]) -> Any:
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
                start, length = params.split(',')
                start = int(start)
                length = int(length)
                return str_value[start:start + length]
            else:
                start = int(params)
                return str_value[start:]
    except Exception as e:
        print(f"截取规则应用失败: {e}")

    return value


def evaluate_single_condition(
    condition: Dict[str, Any],
    get_mqtt_message_fn: Callable[[str], Optional[Dict[str, Any]]]
) -> bool:
    """评估单个条件是否匹配"""
    topic_name = condition.get('topic_name')
    field_path = condition.get('field_path')
    match_rule = condition.get('match_rule')
    match_value_str = condition.get('match_value')
    extraction_rule = condition.get('extraction_rule')

    msg = get_mqtt_message_fn(topic_name)
    if not msg:
        return False

    payload = msg.get('payload', {})
    actual_value = get_nested_value(payload, field_path)

    if actual_value is None:
        return False

    if extraction_rule and extraction_rule.get('type'):
        actual_value = apply_extraction(actual_value, extraction_rule)
        if actual_value is None:
            return False

    return match_value(actual_value, match_rule, match_value_str)


def evaluate_config(
    config,
    get_mqtt_message_fn: Callable[[str], Optional[Dict[str, Any]]]
) -> bool:
    """评估一个配置规则是否匹配，支持多条件组合"""
    conditions = config.conditions
    logic_operator = config.logic_operator or 'AND'

    if not conditions:
        msg = get_mqtt_message_fn(config.topic_name)
        if not msg:
            return False
        payload = msg.get('payload', {})
        actual_value = get_nested_value(payload, config.field_path)

        if actual_value is None:
            return False
        if config.extraction_rule and config.extraction_rule.get('type'):
            actual_value = apply_extraction(actual_value, config.extraction_rule)
            if actual_value is None:
                return False

        return match_value(actual_value, config.match_rule, config.match_value)

    condition_results = []
    for condition in conditions:
        result = evaluate_single_condition(condition, get_mqtt_message_fn)
        condition_results.append(result)

    if logic_operator.upper() == 'OR':
        return any(condition_results)
    else:
        return all(condition_results)


def load_device_rules(db, device_code: str, DeviceStatusMonitorConfig) -> Dict[str, list]:
    """加载设备的规则配置：基础规则 + 设备规则，设备规则覆盖同类型基础规则"""
    from sqlalchemy import and_

    basic_configs = db.query(DeviceStatusMonitorConfig).filter(
        and_(
            DeviceStatusMonitorConfig.rule_scope == 'basic',
            DeviceStatusMonitorConfig.enabled == True
        )
    ).order_by(DeviceStatusMonitorConfig.priority).all()

    device_configs = db.query(DeviceStatusMonitorConfig).filter(
        and_(
            DeviceStatusMonitorConfig.device_code == device_code,
            DeviceStatusMonitorConfig.rule_scope == 'device',
            DeviceStatusMonitorConfig.enabled == True
        )
    ).order_by(DeviceStatusMonitorConfig.priority).all()

    config_by_status_type: Dict[str, list] = {}

    for config in basic_configs:
        config_by_status_type.setdefault(config.status_type, []).append(config)

    device_types = {config.status_type for config in device_configs}
    for status_type in device_types:
        config_by_status_type[status_type] = []

    for config in device_configs:
        config_by_status_type.setdefault(config.status_type, []).append(config)

    return config_by_status_type


# ==================== 曲线匹配增强算法 ====================

def _binary_search_nearest(curve_times: List[float], target_time: float) -> int:
    """二分搜索曲线时间数组，返回最近点的索引"""
    idx = bisect.bisect_left(curve_times, target_time)
    if idx == 0:
        return 0
    if idx >= len(curve_times):
        return len(curve_times) - 1
    left_diff = abs(curve_times[idx - 1] - target_time)
    right_diff = abs(curve_times[idx] - target_time)
    return idx - 1 if left_diff <= right_diff else idx


def _interpolate_value(
    curve_data: List[Dict[str, Any]], 
    curve_times: List[float],
    time_ms: float
) -> Optional[float]:
    """在标准曲线上按时间线性插值，获取期望值"""
    idx = bisect.bisect_left(curve_times, time_ms)
    if idx == 0:
        return curve_data[0]['value']
    if idx >= len(curve_times):
        return curve_data[-1]['value']
    t0, t1 = curve_times[idx - 1], curve_times[idx]
    if t1 == t0:
        return curve_data[idx]['value']
    ratio = (time_ms - t0) / (t1 - t0)
    v0, v1 = curve_data[idx - 1]['value'], curve_data[idx]['value']
    return v0 + ratio * (v1 - v0)


def _find_best_start_index(
    curve_times: List[float],
    curve_values: List[float],
    target_time: float,
    target_value: float,
    time_weight: float = 0.3,
    value_weight: float = 0.7,
    search_window: int = 50
) -> int:
    """
    在标准曲线上搜索综合代价最小的起点索引。
    综合代价 = time_weight * 归一化时间差 + value_weight * 归一化值差
    """
    if not curve_times:
        return 0

    # 先按时间找到大致位置
    approx_idx = bisect.bisect_left(curve_times, target_time)

    # 计算归一化因子
    max_time = max(curve_times) - min(curve_times)
    max_value = max(curve_values) - min(curve_values)
    if max_time <= 0:
        max_time = 1
    if max_value <= 0:
        max_value = 1

    # 在附近窗口内搜索最佳匹配
    start_idx = max(0, approx_idx - search_window)
    end_idx = min(len(curve_times), approx_idx + search_window + 1)

    best_idx = approx_idx
    best_cost = float('inf')

    for idx in range(start_idx, end_idx):
        time_cost = abs(curve_times[idx] - target_time) / max_time
        value_cost = abs(curve_values[idx] - target_value) / max_value
        cost = time_weight * time_cost + value_weight * value_cost

        if cost < best_cost:
            best_cost = cost
            best_idx = idx

    return best_idx


def match_curve(
    realtime_data: List[Dict[str, Any]],
    curve_data: List[Dict[str, Any]],
    time_tolerance_ms: float,
    value_tolerance: float,
    min_points: int = 5,
    time_weight: float = 0.3,
    value_weight: float = 0.7,
    enable_slope_check: bool = True,
    slope_window: int = 3
) -> Dict[str, Any]:
    """
    曲线匹配核心算法 — 增强版，支持随机起点、分段匹配、斜率验证。

    Args:
        realtime_data: 实时数据 [{'time': float, 'value': float}, ...]
        curve_data: 标准曲线数据 [{'time': float, 'value': float}, ...]
        time_tolerance_ms: 时间容差（毫秒），用于时间范围检查
        value_tolerance: 值容差
        min_points: 最少数据点数
        time_weight: 起点搜索时间权重 (0-1)
        value_weight: 起点搜索数值权重 (0-1)
        enable_slope_check: 是否启用斜率方向验证
        slope_window: 斜率验证窗口大小

    Returns:
        {
            'matched': bool,
            'score': float,
            'max_deviation': float,
            'avg_deviation': float,
            'matched_points': int,
            'total_points': int,
            'segments': int,
            'reason': str
        }
    """
    if not realtime_data or not curve_data:
        return {
            'matched': False, 'score': 0, 'max_deviation': 0,
            'avg_deviation': 0, 'matched_points': 0, 'total_points': 0,
            'segments': 0, 'reason': '数据为空'
        }

    # 排序
    sorted_realtime = sorted(realtime_data, key=lambda x: x['time'])
    sorted_curve = sorted(curve_data, key=lambda x: x['time'])
    curve_times = [p['time'] for p in sorted_curve]
    curve_values = [p['value'] for p in sorted_curve]
    total_points = len(sorted_realtime)

    if total_points < min_points:
        return {
            'matched': False, 'score': 0, 'max_deviation': 0,
            'avg_deviation': 0, 'matched_points': 0, 'total_points': total_points,
            'segments': 0, 'reason': f'数据点不足({total_points}<{min_points})'
        }

    curve_start_time = curve_times[0]
    curve_end_time = curve_times[-1]

    matched_count = 0
    total_deviation = 0.0
    max_deviation = 0.0
    segment_count = 0
    i = 0  # 实时数据索引

    # 斜率验证滑动窗口
    real_window: List[float] = []
    expected_window: List[float] = []

    while i < total_points:
        segment_count += 1

        # === 步骤1: 搜索最佳起点（时间+数值） ===
        current_point = sorted_realtime[i]
        start_idx = _find_best_start_index(
            curve_times, curve_values,
            current_point['time'], current_point['value'],
            time_weight, value_weight
        )
        # 重置曲线位置到起点附近
        curve_pos = start_idx

        # === 步骤2: 分段跟踪 ===
        consecutive_miss = 0
        max_consecutive_miss = max(3, min_points // 3)
        points_in_segment = 0

        while i < total_points:
            real_point = sorted_realtime[i]
            real_time = real_point['time']
            real_value = real_point['value']

            # 时间范围检查（超出曲线范围且超出容差的点直接跳过）
            if real_time < curve_start_time - time_tolerance_ms or \
               real_time > curve_end_time + time_tolerance_ms:
                i += 1
                continue

            # 获取期望值（线性插值）
            expected_value = _interpolate_value(sorted_curve, curve_times, real_time)
            if expected_value is None:
                i += 1
                continue

            # 计算偏差
            value_diff = abs(expected_value - real_value)
            total_deviation += value_diff
            max_deviation = max(max_deviation, value_diff)

            # 斜率/方向验证
            slope_ok = True
            if enable_slope_check:
                real_window.append(real_value)
                expected_window.append(expected_value)
                if len(real_window) > slope_window:
                    real_window.pop(0)
                    expected_window.pop(0)
                if len(real_window) >= slope_window:
                    real_slope = real_window[-1] - real_window[0]
                    expected_slope = expected_window[-1] - expected_window[0]
                    # 方向不一致（一个增加一个减少）视为不匹配
                    if real_slope * expected_slope < 0:
                        slope_ok = False

            # 判断是否匹配
            if value_diff <= value_tolerance and slope_ok:
                matched_count += 1
                consecutive_miss = 0
            else:
                consecutive_miss += 1

            # 更新曲线位置（用于后续可能的扩展）
            curve_pos = _binary_search_nearest(curve_times, real_time)
            points_in_segment += 1

            # === 步骤3: 截断与重规划 ===
            if consecutive_miss >= max_consecutive_miss:
                # 连续未匹配过多，结束当前段，下一个循环会重新搜索起点
                i += 1  # 跳过当前点，从下一个点开始新段
                break

            i += 1

        # 防止段内没有任何进展导致死循环
        if points_in_segment == 0:
            i += 1

    # 计算评分
    match_score = (matched_count / total_points * 100) if total_points > 0 else 0
    avg_deviation = (total_deviation / total_points) if total_points > 0 else 0

    is_matched = match_score >= 80 and max_deviation <= value_tolerance * 2

    return {
        'matched': is_matched,
        'score': round(match_score, 2),
        'max_deviation': round(max_deviation, 2),
        'avg_deviation': round(avg_deviation, 2),
        'matched_points': matched_count,
        'total_points': total_points,
        'segments': segment_count,
        'reason': '' if is_matched else f'匹配度{match_score:.1f}%<80%或最大偏差{max_deviation:.1f}超限'
    }


# ==================== 统一曲线评估接口 ====================

def _extract_realtime_data_from_buffer(
    mqtt_buffer: list,
    topic_filter: str,
    field_path: str,
    time_base: Optional[datetime] = None,
    max_duration_ms: Optional[float] = None
) -> Tuple[List[Dict[str, Any]], Optional[datetime]]:
    """
    从MQTT缓冲区提取实时数据，统一时间基准。

    Args:
        mqtt_buffer: MQTT消息列表
        topic_filter: 主题过滤字符串（servo_axis）
        field_path: 数值字段路径
        time_base: 基准时间，若为None则使用最早消息时间
        max_duration_ms: 最大时长过滤（毫秒），超出该范围的消息会被忽略

    Returns:
        (realtime_data, actual_base_time)
        realtime_data: [{'time': int(ms), 'value': any}, ...]
    """
    messages = []
    for msg in mqtt_buffer:
        topic = msg.get('topic', '')
        if topic_filter not in topic:
            continue
        msg_time_str = msg.get('timestamp', '')
        if not msg_time_str:
            continue
        try:
            msg_time = datetime.fromisoformat(msg_time_str)
            payload = msg.get('payload', {})
            value = get_nested_value(payload, field_path)
            if value is not None:
                messages.append({'time': msg_time, 'value': value})
        except (ValueError, TypeError):
            continue

    if not messages:
        return [], None

    # 按时间排序
    messages.sort(key=lambda x: x['time'])

    # 确定时间基准
    if time_base is None:
        actual_base = messages[0]['time']
    else:
        actual_base = time_base

    # 转换为相对时间（毫秒）
    realtime_data = []
    for msg in messages:
        offset_ms = int((msg['time'] - actual_base).total_seconds() * 1000)
        if max_duration_ms is not None and offset_ms > max_duration_ms:
            continue
        realtime_data.append({'time': offset_ms, 'value': msg['value']})

    return realtime_data, actual_base


def evaluate_curve_config(
    config,
    curve,
    mqtt_buffer: list,
    curve_start_time: Optional[datetime] = None,
    field_path: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    评估单个曲线配置（统一接口，兼容原有两个函数）。

    如果 curve_start_time 不为 None，则使用绝对时间基准；
    否则自动以缓冲区最早消息时间为基准。

    Args:
        config: DeviceStatusMonitorConfig 对象
        curve: DBParamCurve 对象
        mqtt_buffer: MQTT消息缓冲区列表
        curve_start_time: 曲线起始时间（可选，用于事件触发的匹配）
        field_path: 字段路径（若不提供则从 config.field_path 读取）

    Returns:
        match_curve 结果，额外包含 'status_type'
    """
    # 确定字段路径
    if field_path is None:
        field_path = getattr(config, 'field_path', None)
        if not field_path:
            return {'matched': False, 'status_type': config.status_type, 'reason': '未指定字段路径'}

    total_duration = getattr(curve, 'total_duration_ms', None)
    if not total_duration:
        return {'matched': False, 'status_type': config.status_type, 'reason': '曲线时长未设置'}

    # 提取实时数据
    realtime_data, _ = _extract_realtime_data_from_buffer(
        mqtt_buffer=mqtt_buffer,
        topic_filter=curve.servo_axis,
        field_path=field_path,
        time_base=curve_start_time,
        max_duration_ms=total_duration
    )

    if not realtime_data:
        return {
            'matched': False, 'score': 0, 'max_deviation': 0,
            'avg_deviation': 0, 'matched_points': 0, 'total_points': 0,
            'segments': 0, 'reason': '缓冲区无有效数据',
            'status_type': config.status_type
        }

    # 调用匹配算法
    result = match_curve(
        realtime_data=realtime_data,
        curve_data=curve.curve_data,
        time_tolerance_ms=curve.time_tolerance_ms,
        value_tolerance=curve.value_tolerance
    )
    result['status_type'] = config.status_type
    return result


# 保留原函数名以兼容旧代码，但内部调用统一接口
def evaluate_curve_config_from_buffer(config, curve, mqtt_buffer: list, field_path: str) -> Dict[str, Any]:
    """
    无event消息时的曲线评估（兼容旧接口）
    内部直接调用 evaluate_curve_config，curve_start_time=None 自动使用缓冲区最早时间。
    """
    return evaluate_curve_config(config, curve, mqtt_buffer, curve_start_time=None, field_path=field_path)