"""
数据库迁移脚本：为 device_status_monitor_configs 表添加 extraction_rule 字段
"""
import pymysql

def migrate():
    """执行迁移"""
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'datacollect',
        'password': 'datacollect',
        'database': 'datacollect',
        'charset': 'utf8mb4'
    }
    
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'datacollect' 
            AND TABLE_NAME = 'device_status_monitor_configs'
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("表 device_status_monitor_configs 不存在，先创建表")
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS device_status_monitor_configs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                device_id INT NOT NULL,
                status_type VARCHAR(50) NOT NULL,
                topic_name VARCHAR(255) NOT NULL,
                field_path VARCHAR(255) NOT NULL,
                match_rule VARCHAR(50) NOT NULL,
                match_value TEXT,
                extraction_rule JSON COMMENT '截取规则配置',
                enabled BOOLEAN NOT NULL DEFAULT TRUE,
                priority INT NOT NULL DEFAULT 0,
                description TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备状态监控配置表'
            """
            cursor.execute(create_table_sql)
            print("✓ 表 device_status_monitor_configs 创建成功")
            
            # 创建索引
            try:
                cursor.execute("CREATE INDEX idx_dsmc_device_id ON device_status_monitor_configs(device_id)")
            except:
                pass
            try:
                cursor.execute("CREATE INDEX idx_dsmc_status_type ON device_status_monitor_configs(status_type)")
            except:
                pass
            try:
                cursor.execute("CREATE INDEX idx_dsmc_enabled ON device_status_monitor_configs(enabled)")
            except:
                pass
            print("✓ 索引创建成功")
        else:
            # 检查字段是否已存在
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'datacollect' 
                AND TABLE_NAME = 'device_status_monitor_configs' 
                AND COLUMN_NAME = 'extraction_rule'
            """)
            
            exists = cursor.fetchone()[0]
            
            if exists:
                print("字段 extraction_rule 已存在，跳过迁移")
            else:
                # 添加 extraction_rule 字段
                sql = """
                ALTER TABLE device_status_monitor_configs 
                ADD COLUMN extraction_rule JSON COMMENT '截取规则配置' 
                AFTER match_value
                """
                cursor.execute(sql)
                connection.commit()
                print("✓ 成功添加 extraction_rule 字段")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"迁移失败: {e}")
        raise

if __name__ == '__main__':
    migrate()
    print("迁移完成！")
