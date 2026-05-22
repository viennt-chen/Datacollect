"""
创建质量记录表
"""
import mysql.connector
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# 从 DATABASE_URL 解析配置
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://admin:admin@10.10.180.241:3306/datacollect')
# 解析 mysql+pymysql://user:password@host:port/database
import re
match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
if match:
    DB_CONFIG = {
        'user': match.group(1),
        'password': match.group(2),
        'host': match.group(3),
        'port': int(match.group(4)),
        'database': match.group(5),
    }
else:
    DB_CONFIG = {
        'host': '10.10.180.241',
        'port': 3306,
        'user': 'admin',
        'password': 'admin',
        'database': 'datacollect'
    }

def create_table():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        cursor.execute("SHOW TABLES LIKE 'quality_records'")
        if cursor.fetchone():
            print("表 quality_records 已存在")
            return

        create_sql = """
        CREATE TABLE quality_records (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键 ID',
            product_code VARCHAR(100) NOT NULL COMMENT '产品编号',
            product_name VARCHAR(200) NOT NULL COMMENT '产品名称',
            device_code VARCHAR(100) COMMENT '设备编号',
            status VARCHAR(20) NOT NULL DEFAULT 'passed' COMMENT '检验状态: passed/failed/pending',
            defect_type VARCHAR(100) COMMENT '缺陷类型',
            defect_description TEXT COMMENT '缺陷描述',
            inspector VARCHAR(100) COMMENT '检验员',
            inspect_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '检验时间',
            quantity INT DEFAULT 1 COMMENT '检验数量',
            passed_quantity INT DEFAULT 0 COMMENT '合格数量',
            failed_quantity INT DEFAULT 0 COMMENT '不合格数量',
            remark TEXT COMMENT '备注',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            created_by VARCHAR(100) COMMENT '创建人',
            updated_by VARCHAR(100) COMMENT '更新人',
            INDEX idx_product_code (product_code),
            INDEX idx_device_code (device_code),
            INDEX idx_status (status),
            INDEX idx_defect_type (defect_type),
            INDEX idx_inspect_time (inspect_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='质量检验记录表'
        """

        cursor.execute(create_sql)
        conn.commit()

        print("[OK] 表 quality_records 创建成功")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 创建表失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("创建质量记录表")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")

    create_table()

    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
