"""
数据库初始化脚本
创建所有表结构并插入默认数据
"""
import sys
import os
import logging
from datetime import datetime

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text, inspect
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_engine():
    """创建数据库引擎"""
    return create_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )


def create_tables(engine):
    """创建所有数据库表"""
    # 导入共享 Base（来自 app.database）
    from app.database import Base as SharedBase

    # 导入所有模型模块，确保它们被加载
    # --- 使用共享 Base 的模型 ---
    from app.models.auth import User, LoginLog, RefreshToken
    from app.models.collected_data import CollectedData
    from app.models.collector_log import CollectorLog
    from app.models.current_product_config import CurrentProductConfig
    from app.models.db_param_curve import DBParamCurve
    from app.models.device import Device
    from app.models.device_status_monitor_config import DeviceStatusMonitorConfig
    from app.models.order_processing_record import OrderProcessingRecord
    from app.models.process_params import ProcessParameter
    from app.models.product_order_log import ProductOrderQueryLog
    from app.models.material_category import MaterialCategory
    from app.models.production_flow import ProductionFlow
    from app.models.production_flow_instance import ProductionFlowInstance
    from app.models.process_definition import ProcessDefinition

    # --- 定义了自己 Base 的模型 ---
    from app.models.alarm_compressed_param import AlarmCompressedParam
    from app.models.alarm_record import AlarmRecord
    from app.models.compressed_param import CompressedParam
    from app.models.event_data import EventData
    from app.models.event_relations import EventSVRelation, EventPVRelation, EventAlarmRelation, EventDataRelationSummary
    from app.models.mqtt_topic_config import MQTTTopicConfig
    from app.models.material import Material
    from app.models.product_order import ProductOrder
    from app.models.pv_compressed_param import PVCompressedParam
    from app.models.raw_data_block import RawDataBlock
    from app.models.sv_compressed_param import SVCompressedParam

    # 收集所有唯一的 Base metadata
    metadata_set = set()
    metadata_list = []

    # 遍历所有已导入的模型类，收集它们的 metadata
    all_models = [
        User, LoginLog, RefreshToken,
        CollectedData, CollectorLog,
        CurrentProductConfig, DBParamCurve, Device,
        DeviceStatusMonitorConfig, MaterialCategory, OrderProcessingRecord,
        ProcessParameter, ProductOrderQueryLog,
        ProductionFlow, ProductionFlowInstance,
        AlarmCompressedParam, AlarmRecord, CompressedParam,
        EventData,
        EventSVRelation, EventPVRelation, EventAlarmRelation, EventDataRelationSummary,
        MQTTTopicConfig,
        Material, ProductOrder,
        PVCompressedParam, RawDataBlock, SVCompressedParam,
        ProcessDefinition,
    ]

    for model_cls in all_models:
        md = model_cls.metadata
        md_id = id(md)
        if md_id not in metadata_set:
            metadata_set.add(md_id)
            metadata_list.append(md)

    logger.info(f"发现 {len(metadata_list)} 个独立的 metadata 实例")

    # 按依赖顺序创建表
    # 先创建没有外键依赖的表（共享 Base，包含 devices 等基础表）
    # 共享 Base 的 metadata 通常是第一个
    shared_md = SharedBase.metadata
    logger.info("创建共享 Base 的表...")
    shared_md.create_all(engine)

    # 再创建其他独立 Base 的表
    for md in metadata_list:
        if id(md) != id(shared_md):
            logger.info(f"创建独立 metadata 的表: {[t.name for t in md.tables.values()]}")
            md.create_all(engine)

    logger.info("所有表创建完成")


def insert_default_data(engine):
    """插入默认数据"""
    from sqlalchemy.orm import sessionmaker
    from app.models.auth import User
    from app.models.device import Device
    from app.models.mqtt_topic_config import MQTTTopicConfig

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. 创建默认管理员账户
        admin_user = session.query(User).filter(User.username == 'admin').first()
        if not admin_user:
            import hashlib
            import secrets

            salt = secrets.token_hex(16)
            password = 'admin123'
            password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

            admin_user = User(
                username='admin',
                email='admin@webadmin.local',
                password_hash=password_hash,
                salt=salt,
                full_name='系统管理员',
                is_active=True,
                is_superuser=True,
                role='admin',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(admin_user)
            logger.info("创建默认管理员账户: admin / admin123")
        else:
            logger.info("管理员账户已存在，跳过创建")

        # 2. 创建默认设备
        default_devices = [
            {
                'device_code': 'IMG-001',
                'device_name': '注塑机-01',
                'device_type': '注塑机',
                'model': 'IMG-200T',
                'manufacturer': '海天',
                'line_code': 'LINE-01',
                'factory_code': 'FAC-01',
                'group_code': 'GRP-01',
                'status': 'active',
                'is_enabled': True,
            },
            {
                'device_code': 'IMG-002',
                'device_name': '注塑机-02',
                'device_type': '注塑机',
                'model': 'IMG-300T',
                'manufacturer': '海天',
                'line_code': 'LINE-01',
                'factory_code': 'FAC-01',
                'group_code': 'GRP-01',
                'status': 'active',
                'is_enabled': True,
            },
        ]

        for device_data in default_devices:
            existing = session.query(Device).filter(Device.device_code == device_data['device_code']).first()
            if not existing:
                device = Device(**device_data, created_at=datetime.now(), updated_at=datetime.now())
                session.add(device)
                logger.info(f"创建默认设备: {device_data['device_code']} - {device_data['device_name']}")
            else:
                logger.info(f"设备 {device_data['device_code']} 已存在，跳过创建")

        # 3. 创建默认 MQTT Topic 配置
        default_topics = [
            {
                'topic_name': 'SHXQ/NO1/KP3/IMG/ProcesEvent',
                'description': '加工事件数据',
                'topic_type': 'event',
                'enabled': True,
                'qos': 1,
                'storage_policy': 'save_raw',
            },
            {
                'topic_name': 'SHXQ/NO1/KP3/IMG/Alarm',
                'description': '报警数据',
                'topic_type': 'alarm',
                'enabled': True,
                'qos': 1,
                'storage_policy': 'save_raw',
            },
            {
                'topic_name': 'SHXQ/NO1/KP3/IMG/PV',
                'description': '过程变量数据',
                'topic_type': 'pv',
                'enabled': True,
                'qos': 1,
                'storage_policy': 'compress',
            },
            {
                'topic_name': 'SHXQ/NO1/KP3/IMG/SV',
                'description': '设定值数据',
                'topic_type': 'sv',
                'enabled': True,
                'qos': 1,
                'storage_policy': 'compress',
            },
        ]

        for topic_data in default_topics:
            existing = session.query(MQTTTopicConfig).filter(
                MQTTTopicConfig.topic_name == topic_data['topic_name']
            ).first()
            if not existing:
                topic = MQTTTopicConfig(**topic_data, created_at=datetime.now(), updated_at=datetime.now())
                session.add(topic)
                logger.info(f"创建默认 MQTT Topic: {topic_data['topic_name']}")
            else:
                logger.info(f"MQTT Topic {topic_data['topic_name']} 已存在，跳过创建")

        session.commit()
        logger.info("默认数据插入完成")

    except Exception as e:
        session.rollback()
        logger.error(f"插入默认数据失败: {e}")
        raise
    finally:
        session.close()


def verify_tables(engine):
    """验证表是否创建成功"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"数据库中共有 {len(tables)} 张表:")

    expected_tables = [
        'users', 'login_logs', 'refresh_tokens',
        'devices', 'products', 'product_orders', 'product_order_query_logs',
        'process_parameters', 'processing_events', 'event_data',
        'collected_data', 'collector_logs', 'mqtt_topic_configs',
        'compressed_params', 'alarm_compressed_params', 'pv_compressed_params',
        'sv_compressed_params', 'raw_data_blocks',
        'alarm_records',
        'event_sv_relations', 'event_pv_relations', 'event_alarm_relations',
        'event_data_relation_summary',
        'db_param_curves', 'device_status_monitor_configs',
        'current_product_configs', 'order_processing_records',
        'production_flows', 'production_flow_instances',
        'process_definitions',
    ]

    for table in sorted(tables):
        status = "  OK" if table in expected_tables else "  (额外)"
        logger.info(f"  - {table}{status}")

    missing = [t for t in expected_tables if t not in tables]
    if missing:
        logger.warning(f"缺少以下表: {missing}")
    else:
        logger.info("所有预期的表都已创建成功")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("数据库初始化开始")
    logger.info(f"数据库地址: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    logger.info("=" * 60)

    engine = get_engine()

    # 测试数据库连接
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        logger.error("请检查 .env 文件中的 DATABASE_URL 配置")
        sys.exit(1)

    # 创建表
    try:
        create_tables(engine)
    except Exception as e:
        logger.error(f"创建表失败: {e}")
        sys.exit(1)

    # 插入默认数据
    try:
        insert_default_data(engine)
    except Exception as e:
        logger.error(f"插入默认数据失败: {e}")
        sys.exit(1)

    # 验证
    verify_tables(engine)

    logger.info("=" * 60)
    logger.info("数据库初始化完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
