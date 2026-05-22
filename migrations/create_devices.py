"""
创建设备管理表
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

def create_table():
    """创建设备管理表"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 检查表是否已存在
        cursor.execute("SHOW TABLES LIKE 'devices'")
        if cursor.fetchone():
            print("表 devices 已存在")
            return
        
        # 创建表
        create_sql = """
        CREATE TABLE devices (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键 ID',
            device_code VARCHAR(100) UNIQUE NOT NULL COMMENT '设备编号',
            device_name VARCHAR(255) NOT NULL COMMENT '设备名称',
            device_type VARCHAR(100) COMMENT '设备类型',
            model VARCHAR(255) COMMENT '设备型号',
            manufacturer VARCHAR(255) COMMENT '制造商',
            line_code VARCHAR(100) COMMENT '所属产线',
            factory_code VARCHAR(100) COMMENT '所属工厂',
            group_code VARCHAR(100) COMMENT '所属集团',
            description TEXT COMMENT '设备描述',
            location VARCHAR(255) COMMENT '安装位置',
            status VARCHAR(20) DEFAULT 'active' COMMENT '设备状态',
            is_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
            ip_address VARCHAR(50) COMMENT 'IP 地址',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            created_by VARCHAR(100) COMMENT '创建人',
            updated_by VARCHAR(100) COMMENT '更新人',
            INDEX idx_device_code (device_code),
            INDEX idx_status (status),
            INDEX idx_device_type (device_type),
            INDEX idx_line_code (line_code),
            INDEX idx_factory_code (factory_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备管理表'
        """
        
        cursor.execute(create_sql)
        conn.commit()
        
        print("✓ 表 devices 创建成功")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 创建表失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("创建设备管理表")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
    
    create_table()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
