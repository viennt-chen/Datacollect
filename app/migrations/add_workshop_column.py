"""
数据库迁移：为 products 表添加 workshop（车间）字段
运行方式：python -m app.migrations.add_workshop_column
"""
from sqlalchemy import text, inspect
from app.database import engine


def add_workshop_column():
    """添加车间字段"""
    inspector = inspect(engine)
    columns = {col['name'] for col in inspector.get_columns('products')}

    if 'workshop' not in columns:
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE products ADD COLUMN workshop VARCHAR(100) COMMENT '车间'"))
                conn.commit()
            print('[OK] 已为 products 表添加 workshop 字段')
        except Exception as e:
            print(f'[ERROR] 添加字段失败: {e}')
    else:
        print('[SKIP] workshop 字段已存在')


if __name__ == '__main__':
    add_workshop_column()
