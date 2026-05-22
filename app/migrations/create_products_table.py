"""
产品管理数据库迁移脚本
创建 products 表
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

def create_products_table():
    """创建产品表"""
    conn = None
    cursor = None
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建 products 表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键 ID',
            u9_material_code VARCHAR(100) NOT NULL UNIQUE COMMENT 'U9 物料号',
            part_number VARCHAR(100) NOT NULL COMMENT '零件号',
            product_name VARCHAR(255) NOT NULL COMMENT '产品名称',
            description TEXT COMMENT '产品描述',
            specification VARCHAR(255) COMMENT '规格型号',
            category VARCHAR(100) COMMENT '产品分类',
            unit VARCHAR(50) COMMENT '单位',
            status VARCHAR(20) DEFAULT 'active' COMMENT '状态（active:启用，inactive:禁用）',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            created_by VARCHAR(100) COMMENT '创建人',
            updated_by VARCHAR(100) COMMENT '更新人',
            INDEX idx_part_number (part_number),
            INDEX idx_u9_material_code (u9_material_code),
            INDEX idx_category (category),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产品表';
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        
        print("✓ products 表创建成功")
        
        # 插入示例数据
        sample_data = [
            ('U9-2024-001', 'PN-001', '智能控制器 A 型', '高性能智能控制器，适用于 KP3 系列设备', 'KT-A-2024', '控制器', '台'),
            ('U9-2024-002', 'PN-002', '智能控制器 B 型', '标准型智能控制器', 'KT-B-2024', '控制器', '台'),
            ('U9-2024-003', 'PN-003', '传感器模块 X1', '温度传感器模块', 'SM-X1-2024', '传感器', '个'),
            ('U9-2024-004', 'PN-004', '传感器模块 X2', '压力传感器模块', 'SM-X2-2024', '传感器', '个'),
            ('U9-2024-005', 'PN-005', '执行器 Y1', '电动执行器', 'AC-Y1-2024', '执行器', '台'),
        ]
        
        insert_sql = """
        INSERT INTO products (u9_material_code, part_number, product_name, description, specification, category, unit, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
        ON DUPLICATE KEY UPDATE 
            part_number = VALUES(part_number),
            product_name = VALUES(product_name),
            description = VALUES(description),
            specification = VALUES(specification),
            category = VALUES(category),
            unit = VALUES(unit)
        """
        
        cursor.executemany(insert_sql, sample_data)
        conn.commit()
        
        print(f"✓ 已插入 {len(sample_data)} 条示例产品数据")
        
    except Error as e:
        print(f"✗ 数据库操作失败：{e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("产品管理数据库迁移")
    print("=" * 50)
    create_products_table()
    print("=" * 50)
    print("迁移完成！")
    print("=" * 50)
