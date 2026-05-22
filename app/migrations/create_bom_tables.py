"""
BOM（物料清单）管理数据库迁移脚本
创建 bom_headers 和 bom_items 表
"""
import pymysql
from pymysql import Error

# 数据库配置
DB_CONFIG = {
    'host': '10.10.180.241',
    'port': 3306,
    'user': 'admin',
    'password': 'admin',
    'database': 'datacollect'
}

def create_bom_tables():
    """创建 BOM 主表和子项表"""
    conn = None
    cursor = None
    try:
        # 连接数据库
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 创建 bom_headers 表
        create_header_sql = """
        CREATE TABLE IF NOT EXISTS bom_headers (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'BOM 主键',
            bom_code VARCHAR(50) NOT NULL COMMENT 'BOM 编号',
            bom_name VARCHAR(255) NOT NULL COMMENT 'BOM 名称',
            product_id INT NOT NULL COMMENT '父产品 ID',
            version VARCHAR(20) NOT NULL DEFAULT 'V1.0' COMMENT '版本号',
            status VARCHAR(20) NOT NULL DEFAULT 'draft' COMMENT '状态：draft/active/archived',
            effective_date DATE COMMENT '生效日期',
            expiry_date DATE COMMENT '失效日期',
            description TEXT COMMENT 'BOM 描述',
            created_by VARCHAR(100) COMMENT '创建人',
            updated_by VARCHAR(100) COMMENT '更新人',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            UNIQUE KEY uk_bom_code (bom_code),
            INDEX idx_product_id (product_id),
            INDEX idx_status (status),
            INDEX idx_version (version)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='BOM 主表'
        """
        cursor.execute(create_header_sql)
        print("[OK] bom_headers created")

        # 创建 bom_items 表
        create_item_sql = """
        CREATE TABLE IF NOT EXISTS bom_items (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'BOM 行项 ID',
            bom_header_id INT NOT NULL COMMENT '所属 BOM 主表 ID',
            child_product_id INT NOT NULL COMMENT '子物料 ID',
            quantity DECIMAL(12, 5) NOT NULL DEFAULT 1.00000 COMMENT '用量',
            unit VARCHAR(50) COMMENT '单位',
            reference_designator VARCHAR(100) COMMENT '参考位号',
            item_no INT DEFAULT 0 COMMENT '行号',
            remark TEXT COMMENT '备注',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_bom_header_id (bom_header_id),
            INDEX idx_child_product_id (child_product_id),
            UNIQUE KEY uk_bom_child (bom_header_id, child_product_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='BOM 子项表'
        """
        cursor.execute(create_item_sql)
        print("[OK] bom_items created")

        conn.commit()

        # 插入示例数据
        sample_headers = [
            ('BOM-2026-001', '智能控制器A型-BOM', 1, 'V1.0', 'active', '2026-01-01', None, '智能控制器A型产品BOM'),
            ('BOM-2026-002', '传感器模块X1-BOM', 3, 'V1.0', 'active', '2026-01-01', None, '传感器模块X1产品BOM'),
            ('BOM-2026-003', '执行器总成-BOM', 5, 'V1.0', 'draft', '2026-01-01', None, '执行器总成产品BOM'),
        ]
        insert_header_sql = """
        INSERT INTO bom_headers (bom_code, bom_name, product_id, version, status, effective_date, expiry_date, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE bom_name = VALUES(bom_name)
        """
        cursor.executemany(insert_header_sql, sample_headers)

        sample_items = [
            (1, 3, 2.00000, '个', 'U1', 10, '传感器组件'),
            (1, 5, 1.00000, '台', 'A1', 20, '执行器组件'),
            (1, 4, 3.00000, '个', 'R1-R3', 30, '压力传感器'),
            (2, 4, 1.00000, '个', 'S1', 10, '压力传感器'),
            (2, 6, 2.00000, '米', 'W1-W2', 20, '线缆'),
            (3, 4, 2.00000, '个', 'P1-P2', 10, '压力传感器'),
        ]
        insert_item_sql = """
        INSERT INTO bom_items (bom_header_id, child_product_id, quantity, unit, reference_designator, item_no, remark)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE quantity = VALUES(quantity)
        """
        cursor.executemany(insert_item_sql, sample_items)

        conn.commit()
        print(f"[OK] Inserted {len(sample_headers)} sample BOM headers")
        print(f"[OK] Inserted {len(sample_items)} sample BOM items")

    except Error as e:
        print(f"[FAIL] Database error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("BOM Database Migration")
    print("=" * 50)
    create_bom_tables()
    print("=" * 50)
    print("Migration done!")
    print("=" * 50)
