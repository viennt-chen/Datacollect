"""
数据库迁移脚本：为 current_product_configs 表添加 extraction_rule 字段
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
        
        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'datacollect' 
            AND TABLE_NAME = 'current_product_configs'
            AND COLUMN_NAME = 'extraction_rule'
        """)
        
        column_exists = cursor.fetchone()[0]
        
        if column_exists:
            print("字段 extraction_rule 已存在，无需迁移")
            return
        
        # 添加 extraction_rule 字段
        add_column_sql = """
        ALTER TABLE current_product_configs 
        ADD COLUMN extraction_rule JSON COMMENT '截取规则配置' 
        AFTER field_description
        """
        
        cursor.execute(add_column_sql)
        connection.commit()
        
        print("成功添加 extraction_rule 字段到 current_product_configs 表")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        raise
    finally:
        if 'connection' in locals() and connection:
            connection.close()

if __name__ == '__main__':
    migrate()
    print("迁移完成！")
