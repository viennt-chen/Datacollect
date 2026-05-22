"""
迁移脚本：为 products 表添加 material_type 字段
用于区分物料类型：product（成品）、material（原材料/零部件）、semi_finished（半成品）
"""
import sys
import os
# 添加项目根目录到 path（从 app/migrations/ 上溯两级到项目根）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

from sqlalchemy import text
from app.database import engine


def upgrade():
    """添加 material_type 字段到 products 表"""
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = DATABASE()
            AND table_name = 'products'
            AND column_name = 'material_type'
        """))
        if result.scalar() > 0:
            print("material_type 字段已存在，跳过迁移")
            return

        # 添加 material_type 字段
        conn.execute(text("""
            ALTER TABLE products
            ADD COLUMN material_type VARCHAR(20) NOT NULL DEFAULT 'product'
            COMMENT '物料类型: product(产品)/semi_finished(半成品)/material(原材料)/auxiliary(辅料)'
        """))

        # 添加索引
        conn.execute(text("""
            CREATE INDEX ix_products_material_type ON products(material_type)
        """))

        conn.commit()
        print("成功添加 material_type 字段到 products 表")


def downgrade():
    """移除 material_type 字段"""
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE products DROP INDEX ix_products_material_type"))
        conn.execute(text("ALTER TABLE products DROP COLUMN material_type"))
        conn.commit()
        print("成功移除 material_type 字段")


if __name__ == "__main__":
    upgrade()
