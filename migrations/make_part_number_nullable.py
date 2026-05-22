"""
数据库迁移脚本 - 修改 part_number 字段为可空
"""
import mysql.connector
from mysql.connector import Error

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'datacollect',
    'password': 'datacollect',
    'database': 'datacollect'
}

def migrate():
    """执行迁移"""
    conn = None
    cursor = None
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 修改 part_number 字段为可空
        alter_sql = """
        ALTER TABLE products 
        MODIFY COLUMN part_number VARCHAR(100) NULL COMMENT '零件号'
        """
        
        cursor.execute(alter_sql)
        conn.commit()
        
        print("✓ part_number 字段已修改为可空")
        
    except Error as e:
        print(f"✗ 数据库操作失败：{e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("修改 part_number 字段为可空")
    print("=" * 50)
    migrate()
    print("=" * 50)
    print("迁移完成！")
