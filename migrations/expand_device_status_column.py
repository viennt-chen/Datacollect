"""迁移脚本：扩大 devices 表 status 列长度（支持多状态逗号分隔）"""
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

        cursor.execute("""
            ALTER TABLE devices
            MODIFY COLUMN status VARCHAR(100) DEFAULT 'active' COMMENT '设备状态（多状态逗号分隔如 processing,alarm）'
        """)
        connection.commit()
        print("已将 devices.status 列长度扩大到 100")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"迁移失败: {e}")
        raise

if __name__ == '__main__':
    migrate()
    print("迁移完成")
