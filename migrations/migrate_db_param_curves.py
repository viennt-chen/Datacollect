"""
数据库迁移脚本：创建DB参数曲线表
"""
import pymysql
import sys
import os

def run_migration():
    """执行数据库迁移"""
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
        
        print("开始执行DB参数曲线表迁移...")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS db_param_curves (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id INT NOT NULL,
            curve_name VARCHAR(200) NOT NULL,
            part_number VARCHAR(100),
            servo_axis VARCHAR(100) NOT NULL,
            curve_data JSON NOT NULL,
            total_duration_ms INT,
            max_value FLOAT,
            min_value FLOAT,
            data_points_count INT,
            value_tolerance FLOAT NOT NULL DEFAULT 5.0,
            time_tolerance_ms INT NOT NULL DEFAULT 100,
            enabled INT NOT NULL DEFAULT 1,
            description TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='DB参数曲线表'
        """
        
        cursor.execute(create_table_sql)
        print("✓ 表 db_param_curves 创建成功")
        
        create_indexes = [
            "CREATE INDEX idx_db_param_curves_device_id ON db_param_curves(device_id)",
            "CREATE INDEX idx_db_param_curves_part_number ON db_param_curves(part_number)",
            "CREATE INDEX idx_db_param_curves_enabled ON db_param_curves(enabled)"
        ]
        
        for index_sql in create_indexes:
            try:
                cursor.execute(index_sql)
                print(f"✓ 索引创建成功: {index_sql.split('ON')[1].split('(')[0].strip()}")
            except Exception as e:
                if 'Duplicate key name' in str(e):
                    print(f"ℹ 索引已存在，跳过")
                else:
                    print(f"✗ 索引创建失败: {e}")
        
        connection.commit()
        print("\n✓ 迁移完成！")
        
    except Exception as e:
        print(f"\n✗ 迁移失败: {e}")
        connection.rollback()
        sys.exit(1)
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    run_migration()
