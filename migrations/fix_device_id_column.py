"""迁移脚本：修复 device_status_monitor_configs 表的 device_id 列"""
import pymysql

def migrate():
    db_config = {
        'host': '10.10.180.241',
        'port': 3306,
        'user': 'admin',
        'password': 'admin',
        'database': 'datacollect',
        'charset': 'utf8mb4'
    }

    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        # 检查 device_id 列是否存在
        cursor.execute("""
            SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'datacollect'
            AND TABLE_NAME = 'device_status_monitor_configs'
            AND COLUMN_NAME = 'device_id'
        """)

        col = cursor.fetchone()
        if col:
            print(f"找到 device_id 列: nullable={col[1]}, default={col[2]}")
            # 将 device_id 改为可空
            cursor.execute("""
                ALTER TABLE device_status_monitor_configs
                MODIFY COLUMN device_id INT NULL
            """)
            connection.commit()
            print("已将 device_id 改为可空")
        else:
            print("device_id 列不存在，跳过")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"迁移失败: {e}")
        raise

if __name__ == '__main__':
    migrate()
    print("迁移完成")
