"""
工艺参数变更历史表迁移脚本
创建 process_param_history 表
"""
import pymysql
from pymysql import Error

DB_CONFIG = {
    'host': '10.10.180.241',
    'port': 3306,
    'user': 'admin',
    'password': 'admin',
    'database': 'datacollect'
}


def create_table():
    conn = None
    cursor = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        create_sql = """
        CREATE TABLE IF NOT EXISTS process_param_history (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
            process_id INT NOT NULL COMMENT '工艺定义ID',
            change_type VARCHAR(20) NOT NULL COMMENT '变更类型: mqtt_value_change/definition_change',
            param_name VARCHAR(100) NOT NULL COMMENT '参数名',
            old_value TEXT COMMENT '旧值',
            new_value TEXT COMMENT '新值',
            source VARCHAR(50) COMMENT '变更来源',
            operator VARCHAR(100) COMMENT '操作人',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            INDEX idx_process_id (process_id),
            INDEX idx_change_type (change_type),
            INDEX idx_created_at (created_at),
            INDEX idx_process_change (process_id, change_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工艺参数变更历史表'
        """
        cursor.execute(create_sql)
        conn.commit()
        print("[OK] process_param_history table created")

    except Error as e:
        print(f"[FAIL] Database error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Process Param History Migration")
    print("=" * 50)
    create_table()
    print("=" * 50)
    print("Migration done!")
    print("=" * 50)
