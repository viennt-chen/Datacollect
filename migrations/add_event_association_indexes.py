"""
添加事件关联查询优化索引
用于提升跨模块关联查询的性能
"""
import mysql.connector
import os
import re
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://admin:admin@10.10.180.241:3306/datacollect')
match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
if match:
    DB_CONFIG = {
        'user': match.group(1),
        'password': match.group(2),
        'host': match.group(3),
        'port': int(match.group(4)),
        'database': match.group(5),
    }
else:
    DB_CONFIG = {
        'host': '10.10.180.241',
        'port': 3306,
        'user': 'admin',
        'password': 'admin',
        'database': 'datacollect'
    }

# 需要创建的索引列表
INDEXES = [
    {
        "table": "event_data",
        "index": "idx_event_data_machine_start",
        "columns": "(machine_id, start_code)",
        "description": "优化按设备+启动码关联查询"
    },
    {
        "table": "event_data",
        "index": "idx_event_data_process_no",
        "columns": "(process_no)",
        "description": "优化按工艺编号关联查询"
    },
    {
        "table": "quality_records",
        "index": "idx_quality_records_device_time",
        "columns": "(device_code, inspect_time)",
        "description": "优化质检记录按设备+时间关联查询"
    },
    {
        "table": "alarm_records",
        "index": "idx_alarm_records_device_time",
        "columns": "(device_code, alarm_time)",
        "description": "优化报警记录按设备+时间关联查询"
    },
    {
        "table": "process_parameters",
        "index": "idx_process_params_machine_start",
        "columns": "(machine_id, start_code)",
        "description": "优化工艺参数按设备+启动码关联查询"
    },
    {
        "table": "order_processing_records",
        "index": "idx_opr_device_date_doc",
        "columns": "(device_code, record_date, doc_no)",
        "description": "优化订单加工记录关联查询"
    },
    {
        "table": "production_flow_instances",
        "index": "idx_pfi_device_date",
        "columns": "(device_code, record_date)",
        "description": "优化流程实例按设备+日期关联查询"
    },
]


def add_indexes():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        for idx in INDEXES:
            table = idx["table"]
            index_name = idx["index"]
            columns = idx["columns"]
            desc = idx["description"]

            # 检查索引是否已存在
            cursor.execute(f"SHOW INDEX FROM {table} WHERE Key_name = %s", (index_name,))
            if cursor.fetchone():
                print(f"  [SKIP] {index_name} 已存在")
                continue

            sql = f"CREATE INDEX {index_name} ON {table} {columns}"
            cursor.execute(sql)
            print(f"  [OK] {index_name} 创建成功 - {desc}")

        conn.commit()
        print("\n[OK] 所有索引创建完成")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] 创建索引失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("添加事件关联查询优化索引")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")

    add_indexes()

    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
