"""
产品管理数据库迁移脚本 - 添加单件工时字段
为 products 表添加 unit_work_time 字段
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

def add_unit_work_time_column():
    """为 products 表添加单件工时字段"""
    conn = None
    cursor = None
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'products' 
            AND COLUMN_NAME = 'unit_work_time'
        """, (DB_CONFIG['database'],))
        
        column_exists = cursor.fetchone()[0]
        
        if column_exists > 0:
            print("✓ unit_work_time 字段已存在，正在修改字段类型...")
            # 修改字段类型为 DECIMAL(10,5)
            alter_sql = """
            ALTER TABLE products 
            MODIFY COLUMN unit_work_time DECIMAL(10, 5) COMMENT '单件工时（小时）'
            """
            cursor.execute(alter_sql)
            conn.commit()
            print("✓ unit_work_time 字段类型已修改为 DECIMAL(10, 5)")
        else:
            # 添加 unit_work_time 字段
            alter_sql = """
            ALTER TABLE products 
            ADD COLUMN unit_work_time DECIMAL(10, 5) COMMENT '单件工时（小时）'
            AFTER unit
            """
            
            cursor.execute(alter_sql)
            conn.commit()
            print("✓ unit_work_time 字段添加成功")
        
    except Error as e:
        print(f"✗ 数据库操作失败：{e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("产品管理数据库迁移 - 添加单件工时字段")
    print("=" * 50)
    add_unit_work_time_column()
    print("=" * 50)
    print("迁移完成！")
    print("=" * 50)
