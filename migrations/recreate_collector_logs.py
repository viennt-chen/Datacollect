"""
删除重建采集日志表并简化日志内容
- 删除占用空间的JSON字段（raw_data、transformed_data、extra_info）
- 删除error_stack字段
- 设置500M大小上限
- 添加自动清理机制
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

def recreate_table():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("\n1. 删除旧表...")
        cursor.execute("DROP TABLE IF EXISTS collector_logs")
        print("✓ 旧表已删除")
        
        print("\n2. 创建新表（简化版）...")
        create_sql = """
        CREATE TABLE collector_logs (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
            log_level VARCHAR(20) NOT NULL COMMENT '日志级别(INFO/WARNING/ERROR/DEBUG)',
            log_type VARCHAR(50) NOT NULL COMMENT '日志类型',
            topic_name VARCHAR(200) COMMENT 'MQTT Topic',
            message_id VARCHAR(100) COMMENT '消息ID',
            db_operation VARCHAR(50) COMMENT '数据库操作(INSERT/UPDATE/DELETE)',
            table_name VARCHAR(100) COMMENT '目标表名',
            affected_rows INT COMMENT '影响行数',
            error_message TEXT COMMENT '错误信息',
            execution_time_ms INT COMMENT '执行时间(毫秒)',
            summary VARCHAR(500) COMMENT '日志摘要',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            INDEX idx_log_level (log_level),
            INDEX idx_log_type (log_type),
            INDEX idx_topic_name (topic_name),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='MQTT采集日志表(简化版)'
        """
        cursor.execute(create_sql)
        print("✓ 新表创建成功")
        
        print("\n3. 创建自动清理存储过程...")
        cursor.execute("DROP PROCEDURE IF EXISTS cleanup_collector_logs")
        
        create_procedure = """
        CREATE PROCEDURE cleanup_collector_logs()
        BEGIN
            DECLARE table_size_mb FLOAT;
            DECLARE cutoff_date DATETIME;
            
            SELECT ROUND((data_length + index_length) / 1024 / 1024, 2)
            INTO table_size_mb
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'collector_logs';
            
            IF table_size_mb > 500 THEN
                SELECT DATE_SUB(NOW(), INTERVAL 7 DAY) INTO cutoff_date;
                
                DELETE FROM collector_logs 
                WHERE created_at < cutoff_date;
                
                OPTIMIZE TABLE collector_logs;
            END IF;
        END
        """
        cursor.execute(create_procedure)
        print("✓ 存储过程创建成功")
        
        print("\n4. 创建定时事件（每小时执行）...")
        cursor.execute("DROP EVENT IF EXISTS auto_cleanup_collector_logs")
        
        try:
            cursor.execute("SET GLOBAL event_scheduler = ON")
            print("✓ 事件调度器已启用")
        except Exception as e:
            print(f"⚠ 无法启用事件调度器（需要SUPER权限）: {e}")
            print("  将使用应用层定时任务代替")
        
        create_event = """
        CREATE EVENT IF NOT EXISTS auto_cleanup_collector_logs
        ON SCHEDULE EVERY 1 HOUR
        DO CALL cleanup_collector_logs()
        """
        cursor.execute(create_event)
        print("✓ 定时事件创建成功")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def check_table():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb,
                table_rows
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'collector_logs'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"\n表状态:")
            print(f"  大小: {result[0]} MB")
            print(f"  记录数: {result[1]} 条")
        else:
            print("✗ 表不存在")
            
    except Exception as e:
        print(f"✗ 查询失败: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("重建采集日志表（简化版）")
    print("=" * 60)
    print(f"\n数据库: {DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
    
    check_table()
    
    recreate_table()
    
    check_table()
    
    print("\n" + "=" * 60)
    print("完成！新表已创建，自动清理机制已启用")
    print("=" * 60)
