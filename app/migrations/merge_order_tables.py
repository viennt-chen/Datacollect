"""
迁移脚本：合并 product_orders（汇总）和 product_order_details（明细）为单表
新表 product_orders 以 doc_no 为唯一键
"""
from sqlalchemy import text
from app.database import engine


def migrate():
    with engine.begin() as conn:
        # 检查旧表是否存在
        tables = conn.execute(text(
            "SELECT TABLE_NAME FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN ('product_orders', 'product_order_details', 'product_orders_old')"
        )).fetchall()
        table_names = {t[0] for t in tables}

        if 'product_order_details' not in table_names:
            print("product_order_details 不存在，跳过迁移")
            return

        # 1. 备份旧表
        if 'product_orders_old' in table_names:
            conn.execute(text("DROP TABLE product_orders_old"))
        conn.execute(text("RENAME TABLE product_orders TO product_orders_old"))
        print("✓ product_orders → product_orders_old")

        # 2. 创建新表
        conn.execute(text("""
            CREATE TABLE product_orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                doc_no VARCHAR(100) NOT NULL,
                part_number VARCHAR(100) NOT NULL,
                u9_material_code VARCHAR(100) NOT NULL,
                specs VARCHAR(255),
                item_code VARCHAR(100),
                item_name TEXT,
                planned_output INT DEFAULT 0,
                query_date VARCHAR(20) NOT NULL,
                product_qty FLOAT DEFAULT 0,
                total_complete_qty FLOAT DEFAULT 0,
                total_eligible_qty FLOAT DEFAULT 0,
                total_scrap_qty FLOAT DEFAULT 0,
                complete_wh VARCHAR(255),
                complete_wh_code VARCHAR(50),
                line_number VARCHAR(100),
                line_code VARCHAR(50),
                line_description TEXT,
                department_code VARCHAR(50),
                department_name VARCHAR(255),
                doc_type_code VARCHAR(50),
                doc_type VARCHAR(100),
                doc_state VARCHAR(50),
                project VARCHAR(255),
                mold_no VARCHAR(100),
                cavity_number VARCHAR(100),
                short_code VARCHAR(50),
                packet_qty FLOAT DEFAULT 0,
                cycle_time VARCHAR(50),
                machine VARCHAR(100),
                over_rate FLOAT DEFAULT 0,
                start_date DATETIME,
                description TEXT,
                query_time DATETIME NOT NULL,
                created_at DATETIME,
                UNIQUE KEY uq_doc_no (doc_no),
                INDEX idx_part_number (part_number),
                INDEX idx_u9_material_code (u9_material_code),
                INDEX idx_query_date (query_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        print("✓ 新 product_orders 表已创建")

        # 3. 迁移数据：从 details JOIN summary 插入新表
        conn.execute(text("""
            INSERT INTO product_orders (
                doc_no, part_number, u9_material_code, specs, item_code, item_name,
                planned_output, query_date, product_qty, total_complete_qty,
                total_eligible_qty, total_scrap_qty, complete_wh, complete_wh_code,
                line_number, line_code, line_description, department_code, department_name,
                doc_type_code, doc_type, doc_state, project, mold_no, cavity_number,
                short_code, packet_qty, cycle_time, machine, over_rate,
                start_date, description, query_time, created_at
            )
            SELECT
                d.doc_no, s.part_number, s.u9_material_code, d.specs, d.item_code, d.item_name,
                s.planned_output, s.query_date, d.product_qty, d.total_complete_qty,
                d.total_eligible_qty, d.total_scrap_qty, d.complete_wh, d.complete_wh_code,
                d.line_number, d.line_code, d.line_description, d.department_code, d.department_name,
                d.doc_type_code, d.doc_type, d.doc_state, d.project, d.mold_no, d.cavity_number,
                d.short_code, d.packet_qty, d.cycle_time, d.machine, d.over_rate,
                d.start_date, d.description, s.query_time, d.created_at
            FROM product_order_details d
            JOIN product_orders_old s ON d.order_id = s.id
        """))

        count = conn.execute(text("SELECT COUNT(*) FROM product_orders")).scalar()
        print(f"✓ 已迁移 {count} 条记录到新表")

        # 4. 删除旧明细表
        conn.execute(text("DROP TABLE product_order_details"))
        print("✓ 已删除 product_order_details")

        # 5. 备份表保留，后续可手动删除
        print("✓ 迁移完成！旧表 product_orders_old 保留，确认无误后可手动删除")


if __name__ == "__main__":
    migrate()
