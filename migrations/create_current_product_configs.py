"""
数据库迁移脚本：创建 current_product_configs 表
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
        
        # 检查表是否已存在
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'datacollect' 
            AND TABLE_NAME = 'current_product_configs'
        """)
        
        exists = cursor.fetchone()[0]
        
        if exists:
            print("表 current_product_configs 已存在，跳过迁移")
        else:
            # 创建表
            sql = """
            CREATE TABLE current_product_configs (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键 ID',
                device_id INT NOT NULL COMMENT '设备ID',
                topic_name VARCHAR(255) NOT NULL COMMENT 'MQTT Topic名称',
                field_path VARCHAR(500) NOT NULL COMMENT '字段路径',
                field_description VARCHAR(200) COMMENT '字段说明',
                enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
                priority INT DEFAULT 0 COMMENT '优先级',
                description TEXT COMMENT '备注说明',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_cpc_device_id (device_id),
                INDEX idx_cpc_enabled (enabled),
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='当前加工产品配置表'
            """
            cursor.execute(sql)
            connection.commit()
            print("✓ 成功创建 current_product_configs 表")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"迁移失败: {e}")
        raise

if __name__ == '__main__':
    migrate()
    print("迁移完成")
