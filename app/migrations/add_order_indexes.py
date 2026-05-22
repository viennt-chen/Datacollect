"""
数据库迁移：为 product_orders 表添加查询优化索引
运行方式：python -m app.migrations.add_order_indexes
"""
from sqlalchemy import text, inspect
from app.database import engine


def add_indexes():
    """添加查询优化索引"""
    inspector = inspect(engine)
    existing_indexes = {idx['name'] for idx in inspector.get_indexes('product_orders')}

    indexes_to_add = [
        ('ix_product_orders_query_date', 'query_date'),
        ('ix_product_orders_u9_material_code', 'u9_material_code'),
        ('ix_product_orders_part_number', 'part_number'),
        ('ix_product_orders_doc_state', 'doc_state'),
    ]

    with engine.connect() as conn:
        for idx_name, column in indexes_to_add:
            if idx_name not in existing_indexes:
                try:
                    conn.execute(text(f'CREATE INDEX {idx_name} ON product_orders ({column})'))
                    print(f'[OK] 创建索引 {idx_name} ON product_orders({column})')
                except Exception as e:
                    print(f'[SKIP] 索引 {idx_name} 已存在或创建失败: {e}')
            else:
                print(f'[SKIP] 索引 {idx_name} 已存在')
        conn.commit()

    print('\n索引迁移完成')


if __name__ == '__main__':
    add_indexes()
