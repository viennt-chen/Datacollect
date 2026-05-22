"""
数据库迁移脚本 - 为 products 表添加 project 字段
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config import settings

def migrate():
    """执行数据库迁移"""
    print("开始迁移：为 products 表添加 project 字段...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # 检查 project 列是否已存在
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products' AND column_name = 'project'
        """))
        
        if result.fetchone():
            print("project 字段已存在，跳过迁移")
            return
        
        # 添加 project 列
        conn.execute(text("""
            ALTER TABLE products 
            ADD COLUMN project VARCHAR(255) COMMENT '项目'
        """))
        
        conn.commit()
        print("✓ 成功添加 project 字段到 products 表")

if __name__ == '__main__':
    migrate()
