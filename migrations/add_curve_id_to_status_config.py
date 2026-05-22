"""
数据库迁移脚本：为 device_status_monitor_configs 表添加 curve_id 字段
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
            print("表 device_status_monitor_configs 不存在，跳过迁移")
            cursor.close()
            connection.close()
            return
        
        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'datacollect' 
            AND TABLE_NAME = 'device_status_monitor_configs' 
            AND COLUMN_NAME = 'curve_id'
        """)
        
        exists = cursor.fetchone()[0]
        
        if exists:
            print("字段 curve_id 已存在，跳过迁移")
        else:
            # 添加 curve_id 字段
            sql = """
            ALTER TABLE device_status_monitor_configs 
            ADD COLUMN curve_id INT COMMENT '关联的DB块参数曲线ID' 
            AFTER extraction_rule
            """
            cursor.execute(sql)
            connection.commit()
            print("✓ 成功添加 curve_id 字段")
            
            # 创建索引
            try:
                cursor.execute("CREATE INDEX idx_dsmc_curve_id ON device_status_monitor_configs(curve_id)")
                print("✓ 成功创建 curve_id 索引")
            except Exception as e:
                print(f"创建索引时出错（可能已存在）: {e}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"迁移失败: {e}")
        raise

if __name__ == '__main__':
    migrate()
    print("迁移完成")
