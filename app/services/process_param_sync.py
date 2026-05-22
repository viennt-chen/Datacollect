"""
工艺参数自动同步服务
每秒从 MQTT 数据采集模块检查最新数据，根据筛选规则自动更新工艺参数值
"""
import json
import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database import get_db_session
from app.models.process_definition import ProcessDefinition
from app.models.process_param_history import ProcessParamHistory
from app.models.mqtt_topic_config import MQTTTopicConfig
from app.utils.rule_evaluator import get_nested_value

logger = logging.getLogger(__name__)


class ProcessParamSyncService:
    """工艺参数自动同步服务"""

    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        # 缓存: process_id -> 最新参数值快照
        self._live_params: Dict[int, Dict[str, Any]] = {}

    def start(self):
        """启动同步服务"""
        if self._running:
            logger.warning("工艺参数同步服务已在运行")
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="process-param-sync")
        self._thread.start()
        logger.info("工艺参数同步服务已启动，轮询间隔: %s 秒", self.interval)

    def stop(self):
        """停止同步服务"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        logger.info("工艺参数同步服务已停止")

    def get_live_params(self, process_id: int) -> Optional[Dict[str, Any]]:
        """获取指定工艺的实时参数值"""
        with self._lock:
            return self._live_params.get(process_id)

    def _run_loop(self):
        """主循环"""
        while self._running:
            try:
                self._sync_all()
            except Exception as e:
                logger.error("工艺参数同步异常: %s", e, exc_info=True)
            time.sleep(self.interval)

    def _sync_all(self):
        """同步所有活跃工艺定义的参数"""
        with get_db_session() as db:
            # 查询所有活跃且关联了 MQTT Topic 的工艺定义
            processes = db.query(ProcessDefinition).filter(
                ProcessDefinition.status == 'active',
                ProcessDefinition.mqtt_topic_ids != '[]',
                ProcessDefinition.mqtt_topic_ids.isnot(None),
            ).all()

            if not processes:
                return

            # 获取 MQTT 采集器
            from app.services.mqtt_collector import get_collector
            collector = get_collector()
            if not collector or not collector.stats.is_running:
                return

            # 获取每个 topic 的最新消息
            latest_by_topic = collector.get_latest_by_topic()

            for proc in processes:
                try:
                    self._sync_process(db, proc, latest_by_topic)
                except Exception as e:
                    logger.error("同步工艺 %s 参数失败: %s", proc.process_code, e, exc_info=True)

            db.commit()

    def _sync_process(self, db, proc: ProcessDefinition, latest_by_topic: Dict[str, Dict]):
        """同步单个工艺定义的参数"""
        # 解析关联的 topic IDs
        try:
            topic_ids = json.loads(proc.mqtt_topic_ids) if proc.mqtt_topic_ids else []
        except (json.JSONDecodeError, TypeError):
            return

        if not topic_ids:
            return

        # 获取关联 topic 的名称
        topics = db.query(MQTTTopicConfig).filter(
            MQTTTopicConfig.id.in_(topic_ids)
        ).all()
        topic_names = {t.topic_name for t in topics}

        if not topic_names:
            return

        # 找到关联 topic 的最新消息
        latest_msg = None
        latest_time = None
        for topic_name, msg in latest_by_topic.items():
            if topic_name in topic_names:
                msg_time = msg.get('timestamp', '')
                if latest_time is None or msg_time > latest_time:
                    latest_time = msg_time
                    latest_msg = msg

        if not latest_msg:
            return

        payload = latest_msg.get('payload', {})
        if not isinstance(payload, dict):
            return

        # 解析工艺参数
        try:
            parameters = json.loads(proc.parameters) if proc.parameters else {}
        except (json.JSONDecodeError, TypeError):
            return

        if not parameters:
            return

        # 获取筛选规则
        filter_rules = parameters.get('_filter_rules', [])

        # 评估筛选条件
        if filter_rules and not self._evaluate_filter_rules(filter_rules, payload):
            # 条件不满足，跳过更新
            return

        # 提取并更新参数值
        changed = False
        history_records = []
        source_topic = latest_msg.get('topic', '')

        for param_name, param_conf in parameters.items():
            if param_name == '_filter_rules':
                continue
            if not isinstance(param_conf, dict):
                continue

            # 从 payload 中提取对应字段的值
            new_value = get_nested_value(payload, param_name)
            if new_value is None:
                continue

            new_value_str = str(new_value)
            old_value = param_conf.get('set_value')

            # 仅在值发生变化时更新
            if old_value is not None and str(old_value) == new_value_str:
                continue

            # 更新参数值
            old_value_str = str(old_value) if old_value is not None else None
            param_conf['set_value'] = new_value
            changed = True

            # 记录历史
            history_records.append(ProcessParamHistory(
                process_id=proc.id,
                change_type='mqtt_value_change',
                param_name=param_name,
                old_value=old_value_str,
                new_value=new_value_str,
                source=source_topic,
                created_at=datetime.now(),
            ))

        if changed:
            # 保存更新后的参数
            proc.parameters = json.dumps(parameters, ensure_ascii=False)
            proc.updated_at = datetime.now()

            # 批量写入历史记录
            for record in history_records:
                db.add(record)

            logger.info(
                "工艺 %s 参数已更新: %d 个参数变化 (来源: %s)",
                proc.process_code, len(history_records), source_topic
            )

        # 更新实时参数缓存
        with self._lock:
            self._live_params[proc.id] = {
                'process_id': proc.id,
                'process_code': proc.process_code,
                'parameters': parameters,
                'last_source': source_topic,
                'last_sync_time': datetime.now().isoformat(),
            }

    def _evaluate_filter_rules(self, rules: List[Dict], payload: Dict) -> bool:
        """评估筛选规则（AND 逻辑）"""
        for rule in rules:
            field_path = rule.get('field_path', '')
            operator = rule.get('operator', '==')
            expected_value = rule.get('value', '')

            if not field_path:
                continue

            actual_value = get_nested_value(payload, field_path)
            actual_str = str(actual_value) if actual_value is not None else ''

            if operator == '==':
                if actual_str != str(expected_value):
                    return False
            elif operator == '!=':
                if actual_str == str(expected_value):
                    return False
            else:
                logger.warning("不支持的筛选运算符: %s", operator)
                return False

        return True


# 全局单例
_sync_service: Optional[ProcessParamSyncService] = None
_sync_lock = threading.Lock()


def get_sync_service() -> ProcessParamSyncService:
    """获取同步服务实例（单例模式）"""
    global _sync_service
    with _sync_lock:
        if _sync_service is None:
            _sync_service = ProcessParamSyncService()
        return _sync_service


def init_param_sync_service(interval: float = 1.0):
    """初始化并启动参数同步服务"""
    service = get_sync_service()
    service.interval = interval
    service.start()
    return service
