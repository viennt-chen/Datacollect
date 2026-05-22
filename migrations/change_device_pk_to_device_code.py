"""
迁移：将设备表主键从 id 改为 device_code
同时更新所有关联表的外键
"""
import pymysql
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '10.10.150.254'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'datacollect'),
    'password': os.getenv('DB_PASSWORD', 'datacollect'),
    'database': os.getenv('DB_NAME', 'datacollect')
}


def drop_foreign_key_if_exists(cursor, table_name, column_name):
    """查询并删除指定表中引用指定列的外键"""
    cursor.execute("""
        SELECT CONSTRAINT_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
          AND REFERENCED_TABLE_NAME IS NOT NULL
    """, (DB_CONFIG['database'], table_name, column_name))
    row = cursor.fetchone()
    if row:
        fk_name = row[0]
        cursor.execute(f"ALTER TABLE {table_name} DROP FOREIGN KEY {fk_name}")
        print(f"  - 删除外键 {fk_name} from {table_name}")


def drop_index_if_exists(cursor, table_name, index_name):
    """删除索引（如果存在）"""
    cursor.execute(f"SHOW INDEX FROM {table_name} WHERE Key_name = %s", (index_name,))
    if cursor.fetchone():
        cursor.execute(f"ALTER TABLE {table_name} DROP INDEX {index_name}")


def migrate():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 1. 更新 device_status_monitor_configs 表
        print("1. 更新 device_status_monitor_configs ...")
        cursor.execute("SHOW COLUMNS FROM device_status_monitor_configs LIKE 'device_code'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE device_status_monitor_configs ADD COLUMN device_code VARCHAR(100) COMMENT '设备编号' AFTER id")
            cursor.execute("""
                UPDATE device_status_monitor_configs c
                JOIN devices d ON c.device_id = d.id
                SET c.device_code = d.device_code
            """)
            drop_foreign_key_if_exists(cursor, 'device_status_monitor_configs', 'device_id')
            cursor.execute("ALTER TABLE device_status_monitor_configs DROP COLUMN device_id")
            cursor.execute("ALTER TABLE device_status_monitor_configs ADD INDEX idx_dsmc_device_code (device_code)")
            print("  ✓ device_status_monitor_configs 更新完成")
        else:
            print("  - device_code 列已存在，跳过")

        # 2. 更新 db_param_curves 表
        print("2. 更新 db_param_curves ...")
        cursor.execute("SHOW COLUMNS FROM db_param_curves LIKE 'device_code'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE db_param_curves ADD COLUMN device_code VARCHAR(100) COMMENT '设备编号' AFTER id")
            cursor.execute("""
                UPDATE db_param_curves c
                JOIN devices d ON c.device_id = d.id
                SET c.device_code = d.device_code
            """)
            drop_foreign_key_if_exists(cursor, 'db_param_curves', 'device_id')
            cursor.execute("ALTER TABLE db_param_curves DROP COLUMN device_id")
            cursor.execute("ALTER TABLE db_param_curves ADD INDEX idx_db_param_curves_device_code (device_code)")
            print("  ✓ db_param_curves 更新完成")
        else:
            print("  - device_code 列已存在，跳过")

        # 3. 更新 current_product_configs 表
        print("3. 更新 current_product_configs ...")
        cursor.execute("SHOW COLUMNS FROM current_product_configs LIKE 'device_code'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE current_product_configs ADD COLUMN device_code VARCHAR(100) COMMENT '设备编号' AFTER id")
            cursor.execute("""
                UPDATE current_product_configs c
                JOIN devices d ON c.device_id = d.id
                SET c.device_code = d.device_code
            """)
            drop_foreign_key_if_exists(cursor, 'current_product_configs', 'device_id')
            cursor.execute("ALTER TABLE current_product_configs DROP COLUMN device_id")
            cursor.execute("ALTER TABLE current_product_configs ADD INDEX idx_cpc_device_code (device_code)")
            print("  ✓ current_product_configs 更新完成")
        else:
            print("  - device_code 列已存在，跳过")

        # 4. 更新 order_processing_records 表
        print("4. 更新 order_processing_records ...")
        cursor.execute("SHOW COLUMNS FROM order_processing_records LIKE 'device_id'")
        if cursor.fetchone():
            drop_foreign_key_if_exists(cursor, 'order_processing_records', 'device_id')
            cursor.execute("ALTER TABLE order_processing_records DROP COLUMN device_id")
            drop_index_if_exists(cursor, 'order_processing_records', 'uq_device_date_docno')
            cursor.execute("ALTER TABLE order_processing_records ADD INDEX idx_opr_device_code (device_code)")
            cursor.execute("ALTER TABLE order_processing_records ADD UNIQUE INDEX uq_device_date_docno (device_code, record_date, doc_no)")
            print("  ✓ order_processing_records 更新完成")
        else:
            print("  - device_id 列已不存在，跳过")

        # 5. 更新 mqtt_topic_configs 表
        print("5. 更新 mqtt_topic_configs ...")
        cursor.execute("SHOW COLUMNS FROM mqtt_topic_configs LIKE 'device_code'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE mqtt_topic_configs ADD COLUMN device_code VARCHAR(100) COMMENT '关联设备编号' AFTER parse_rules")
            cursor.execute("""
                UPDATE mqtt_topic_configs c
                JOIN devices d ON c.device_id = d.id
                SET c.device_code = d.device_code
            """)
            cursor.execute("ALTER TABLE mqtt_topic_configs DROP COLUMN device_id")
            print("  ✓ mqtt_topic_configs 更新完成")
        else:
            print("  - device_code 列已存在，跳过")

        # 6. 更新 devices 表：将 device_code 改为主键
        print("6. 更新 devices 表主键 ...")
        cursor.execute("SHOW COLUMNS FROM devices LIKE 'id'")
        if cursor.fetchone():
            # 先去掉 id 列的自增属性，再删除主键
            cursor.execute("ALTER TABLE devices MODIFY COLUMN id INT NOT NULL")
            cursor.execute("ALTER TABLE devices DROP PRIMARY KEY")
            cursor.execute("ALTER TABLE devices ADD PRIMARY KEY (device_code)")
            cursor.execute("ALTER TABLE devices DROP COLUMN id")
            print("  ✓ devices 表主键已改为 device_code")
        else:
            print("  - id 列已不存在，跳过")

        conn.commit()
        print("\n✓ 迁移完成！")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ 迁移失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("迁移：设备表主键从 id 改为 device_code")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")

    migrate()

    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
