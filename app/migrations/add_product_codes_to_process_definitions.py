"""
迁移脚本：为 process_definitions 表添加 product_codes 字段
用于存储关联产品物料编码列表（JSON）
"""
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


def upgrade():
    """添加 product_codes 字段到 process_definitions 表"""
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = DATABASE()
            AND table_name = 'process_definitions'
            AND column_name = 'product_codes'
        """))
        if result.scalar() > 0:
            print("product_codes 字段已存在，跳过迁移")
            return

        # 添加 product_codes 字段
        conn.execute(text("""
            ALTER TABLE process_definitions
            ADD COLUMN product_codes TEXT DEFAULT '[]'
            COMMENT '关联产品物料编码 JSON 列表'
        """))

        conn.commit()
        print("成功添加 product_codes 字段到 process_definitions 表")


def downgrade():
    """移除 product_codes 字段"""
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE process_definitions DROP COLUMN product_codes"))
        conn.commit()
        print("成功移除 product_codes 字段")


if __name__ == "__main__":
    upgrade()
