"""
数据库迁移脚本 - 添加唯一约束防止重复写入
执行：python add_unique_constraints.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.config import settings


def add_unique_constraints():
    """添加唯一约束到数据库"""
    print("=" * 80)
    print("添加唯一约束防止重复写入")
    print("=" * 80)
    
    engine = create_engine(settings.DATABASE_URL, echo=False)
    
    with engine.connect() as conn:
        try:
            # 1. 为 product_orders 表添加唯一约束
            print("\n[1/2] 为 product_orders 表添加唯一约束 (u9_material_code, query_date)...")
            
            # 检查约束是否已存在
            check_sql = """
            SELECT COUNT(*) 
            FROM information_schema.TABLE_CONSTRAINTS 
            WHERE CONSTRAINT_SCHEMA = DATABASE()
            AND TABLE_NAME = 'product_orders'
            AND CONSTRAINT_NAME = 'uq_material_code_query_date'
            AND CONSTRAINT_TYPE = 'UNIQUE'
            """
            result = conn.execute(text(check_sql))
            count = result.scalar()
            
            if count > 0:
                print("  ✓ 约束已存在，跳过")
            else:
                # 先检查是否有重复数据
                check_duplicates = """
                SELECT u9_material_code, query_date, COUNT(*) as cnt
                FROM product_orders
                GROUP BY u9_material_code, query_date
                HAVING COUNT(*) > 1
                """
                duplicates = conn.execute(text(check_duplicates)).fetchall()
                
                if duplicates:
                    print(f"  ⚠ 发现 {len(duplicates)} 组重复数据，正在清理...")
                    # 保留每组中 id 最小的记录，删除其他重复记录
                    cleanup_sql = """
                    DELETE p1 FROM product_orders p1
                    INNER JOIN (
                        SELECT MIN(id) as min_id, u9_material_code, query_date
                        FROM product_orders
                        GROUP BY u9_material_code, query_date
                        HAVING COUNT(*) > 1
                    ) p2 ON p1.u9_material_code = p2.u9_material_code 
                        AND p1.query_date = p2.query_date 
                        AND p1.id > p2.min_id
                    """
                    result = conn.execute(text(cleanup_sql))
                    conn.commit()
                    print(f"  ✓ 已清理 {result.rowcount} 条重复记录")
                
                # 添加唯一约束
                alter_sql = """
                ALTER TABLE product_orders 
                ADD CONSTRAINT uq_material_code_query_date 
                UNIQUE (u9_material_code, query_date)
                """
                conn.execute(text(alter_sql))
                conn.commit()
                print("  ✓ 唯一约束添加成功")
            
            # 2. 为 product_order_details 表添加唯一约束
            print("\n[2/2] 为 product_order_details 表添加唯一约束 (order_id, doc_no)...")
            
            # 检查约束是否已存在
            check_sql = """
            SELECT COUNT(*) 
            FROM information_schema.TABLE_CONSTRAINTS 
            WHERE CONSTRAINT_SCHEMA = DATABASE()
            AND TABLE_NAME = 'product_order_details'
            AND CONSTRAINT_NAME = 'uq_order_id_doc_no'
            AND CONSTRAINT_TYPE = 'UNIQUE'
            """
            result = conn.execute(text(check_sql))
            count = result.scalar()
            
            if count > 0:
                print("  ✓ 约束已存在，跳过")
            else:
                # 先检查是否有重复数据
                check_duplicates = """
                SELECT order_id, doc_no, COUNT(*) as cnt
                FROM product_order_details
                GROUP BY order_id, doc_no
                HAVING COUNT(*) > 1
                """
                duplicates = conn.execute(text(check_duplicates)).fetchall()
                
                if duplicates:
                    print(f"  ⚠ 发现 {len(duplicates)} 组重复数据，正在清理...")
                    # 保留每组中 id 最小的记录，删除其他重复记录
                    cleanup_sql = """
                    DELETE d1 FROM product_order_details d1
                    INNER JOIN (
                        SELECT MIN(id) as min_id, order_id, doc_no
                        FROM product_order_details
                        GROUP BY order_id, doc_no
                        HAVING COUNT(*) > 1
                    ) d2 ON d1.order_id = d2.order_id 
                        AND d1.doc_no = d2.doc_no 
                        AND d1.id > d2.min_id
                    """
                    result = conn.execute(text(cleanup_sql))
                    conn.commit()
                    print(f"  ✓ 已清理 {result.rowcount} 条重复记录")
                
                # 添加唯一约束
                alter_sql = """
                ALTER TABLE product_order_details 
                ADD CONSTRAINT uq_order_id_doc_no 
                UNIQUE (order_id, doc_no)
                """
                conn.execute(text(alter_sql))
                conn.commit()
                print("  ✓ 唯一约束添加成功")
            
            print("\n" + "=" * 80)
            print("迁移完成！")
            print("=" * 80)
            
        except Exception as e:
            conn.rollback()
            print(f"\n✗ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == '__main__':
    add_unique_constraints()
