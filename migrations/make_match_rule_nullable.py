"""迁移脚本：将 match_rule 列改为可为空（支持仅曲线绑定规则）"""
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
            ALTER TABLE device_status_monitor_configs
            MODIFY COLUMN match_rule VARCHAR(50) NULL DEFAULT 'curve_only' COMMENT '匹配规则类型'
        """)
        connection.commit()
        print("已将 match_rule 列改为可为空，默认值 'curve_only'")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"迁移失败: {e}")
        raise

if __name__ == '__main__':
    migrate()
    print("迁移完成")
