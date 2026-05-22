"""迁移脚本：移除 device_status_monitor_configs 表 curve_id 字段的外键约束"""
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

        # 查找 curve_id 相关的外键约束
        cursor.execute("""
            SELECT CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = 'datacollect'
            AND TABLE_NAME = 'device_status_monitor_configs'
            AND COLUMN_NAME = 'curve_id'
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """)

        fk = cursor.fetchone()
        if fk:
            fk_name = fk[0]
            cursor.execute(f"ALTER TABLE device_status_monitor_configs DROP FOREIGN KEY {fk_name}")
            connection.commit()
            print(f"已移除外键约束: {fk_name}")
        else:
            print("curve_id 字段没有外键约束，跳过")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"迁移失败: {e}")
        raise

if __name__ == '__main__':
    migrate()
    print("迁移完成")
