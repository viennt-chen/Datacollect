"""
创建事件数据关联表
"""
import mysql.connector
import os
import sys

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '10.10.150.254'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'datacollect'),
    'password': os.getenv('DB_PASSWORD', 'datacollect'),
    'database': os.getenv('DB_NAME', 'datacollect')
}


def create_table(sql: str, table_name: str):
    """创建表"""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute(sql)
        conn.commit()
        
        print(f"✓ 表 {table_name} 创建成功")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"✗ 创建表 {table_name} 失败：{e}")
        raise
    finally:
        if conn:
            cursor.close()
            conn.close()


def create_event_sv_relations():
    """创建事件-SV关联表"""
    sql = """
    CREATE TABLE IF NOT EXISTS event_sv_relations (
        id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键 ID',
        event_id BIGINT NOT NULL COMMENT '关联的事件ID',
        machine_id VARCHAR(100) NOT NULL COMMENT '设备编号',
        sv_topic VARCHAR(200) NOT NULL COMMENT 'SV Topic名称',
        sv_record_id BIGINT NOT NULL COMMENT 'SV记录ID',
        sv_data_snapshot JSON COMMENT 'SV数据快照',
        sv_timestamp DATETIME(6) COMMENT 'SV数据时间戳',
        time_offset_ms INT COMMENT '时间偏移量（毫秒）',
        created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
        INDEX idx_event_sv_event_id (event_id),
        INDEX idx_event_sv_machine_time (machine_id, sv_timestamp)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='事件-SV关联表'
    """
    create_table(sql, 'event_sv_relations')


def create_event_pv_relations():
    """创建事件-PV关联表"""
    sql = """
    CREATE TABLE IF NOT EXISTS event_pv_relations (
        id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键 ID',
        event_id BIGINT NOT NULL COMMENT '关联的事件ID',
        machine_id VARCHAR(100) NOT NULL COMMENT '设备编号',
        pv_topic VARCHAR(200) NOT NULL COMMENT 'PV Topic名称',
        pv_record_id BIGINT NOT NULL COMMENT 'PV记录ID',
        pv_data_snapshot JSON COMMENT 'PV数据快照',
        pv_timestamp DATETIME(6) COMMENT 'PV数据时间戳',
        time_offset_ms INT COMMENT '时间偏移量（毫秒）',
        sv_point_id VARCHAR(100) COMMENT '对应的SV点位ID',
        sv_value_range JSON COMMENT '对应的SV值范围',
        created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
        INDEX idx_event_pv_event_id (event_id),
        INDEX idx_event_pv_machine_time (machine_id, pv_timestamp)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='事件-PV关联表'
    """
    create_table(sql, 'event_pv_relations')


def create_event_alarm_relations():
    """创建事件-报警关联表"""
    sql = """
    CREATE TABLE IF NOT EXISTS event_alarm_relations (
        id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键 ID',
        event_id BIGINT NOT NULL COMMENT '关联的事件ID',
        machine_id VARCHAR(100) NOT NULL COMMENT '设备编号',
        alarm_record_id BIGINT NOT NULL COMMENT '报警记录ID',
        alarm_code VARCHAR(100) COMMENT '报警编号',
        alarm_level VARCHAR(20) COMMENT '报警级别',
        alarm_type VARCHAR(100) COMMENT '报警类型',
        alarm_title VARCHAR(255) COMMENT '报警标题',
        alarm_value VARCHAR(100) COMMENT '报警值',
        alarm_time DATETIME(6) COMMENT '报警时间',
        time_offset_from_start_ms INT COMMENT '相对于事件开始时间的偏移量（毫秒）',
        created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
        INDEX idx_event_alarm_event_id (event_id),
        INDEX idx_event_alarm_machine_time (machine_id, alarm_time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='事件-报警关联表'
    """
    create_table(sql, 'event_alarm_relations')


def create_event_data_relation_summary():
    """创建事件关联汇总表"""
    sql = """
    CREATE TABLE IF NOT EXISTS event_data_relation_summary (
        id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键 ID',
        event_id BIGINT NOT NULL UNIQUE COMMENT '事件ID',
        machine_id VARCHAR(100) NOT NULL COMMENT '设备编号',
        event_start_time BIGINT COMMENT '事件开始时间（毫秒时间戳）',
        event_end_time BIGINT COMMENT '事件结束时间（毫秒时间戳）',
        sv_count INT DEFAULT 0 COMMENT '关联的SV数量',
        pv_count INT DEFAULT 0 COMMENT '关联的PV数量',
        alarm_count INT DEFAULT 0 COMMENT '关联的报警数量',
        sv_matched INT DEFAULT 0 COMMENT 'SV是否已匹配：0-未匹配，1-已匹配',
        pv_matched INT DEFAULT 0 COMMENT 'PV是否已匹配：0-未匹配，1-已匹配',
        alarm_matched INT DEFAULT 0 COMMENT '报警是否已匹配：0-未匹配，1-已匹配',
        last_match_time DATETIME(6) COMMENT '最后匹配时间',
        created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
        updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
        INDEX idx_relation_summary_event_id (event_id),
        INDEX idx_relation_summary_machine_id (machine_id),
        INDEX idx_relation_summary_match_status (sv_matched, pv_matched, alarm_matched)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='事件关联汇总表'
    """
    create_table(sql, 'event_data_relation_summary')


if __name__ == "__main__":
    print("=" * 60)
    print("创建事件数据关联表")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")

    create_event_sv_relations()
    create_event_pv_relations()
    create_event_alarm_relations()
    create_event_data_relation_summary()

    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
