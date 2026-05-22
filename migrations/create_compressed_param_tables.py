"""
创建 PV、SV、ALARM 压缩参数分表
"""
import mysql.connector
import os
import sys

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '10.10.150.254'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'datacollect'),
    'password': os.getenv('DB_PASSWORD', 'datacollect'),
    'database': os.getenv('DB_NAME', 'datacollect')
}


def create_table(table_name: str, table_comment: str):
    """创建压缩参数表"""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键 ID',
            topic VARCHAR(200) NOT NULL COMMENT 'MQTT Topic 名称',
            event_uid VARCHAR(100) COMMENT '事件唯一标识',
            timestamp_ms BIGINT NOT NULL COMMENT '时间戳（毫秒）',
            original_timestamp BIGINT COMMENT '原始时间戳（毫秒）',
            compressed_payload LONGBLOB NOT NULL COMMENT '压缩的 payload 数据',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            INDEX idx_{table_name.split("_")[0]}_topic_timestamp (topic, timestamp_ms),
            INDEX idx_{table_name.split("_")[0]}_event_uid (event_uid),
            INDEX idx_{table_name.split("_")[0]}_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{table_comment}';
        """
        
        cursor.execute(create_sql)
        conn.commit()
        print(f"✓ 表 {table_name} 创建成功")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"✗ 创建表 {table_name} 失败：{e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("创建 PV、SV、ALARM 压缩参数分表")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
    
    # 创建 PV 压缩参数表
    create_table('pv_compressed_params', 'PV 压缩参数数据表')
    
    # 创建 SV 压缩参数表
    create_table('sv_compressed_params', 'SV 压缩参数数据表')
    
    # 创建 ALARM 压缩参数表
    create_table('alarm_compressed_params', 'ALARM 压缩参数数据表')
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
