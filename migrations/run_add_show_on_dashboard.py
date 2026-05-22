"""迁移脚本：为 devices 表添加 show_on_dashboard 字段"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine

def migrate():
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'devices' AND column_name = 'show_on_dashboard'
        """))
        if result.fetchone():
            # 字段已存在，确保默认值为 FALSE
            conn.execute(text("ALTER TABLE devices MODIFY COLUMN show_on_dashboard BOOLEAN DEFAULT FALSE COMMENT '是否在看板显示'"))
            conn.execute(text("UPDATE devices SET show_on_dashboard = FALSE WHERE show_on_dashboard IS NULL"))
            conn.commit()
            print("字段 show_on_dashboard 已存在，已修正默认值为 FALSE")
            return

        conn.execute(text("ALTER TABLE devices ADD COLUMN show_on_dashboard BOOLEAN DEFAULT FALSE COMMENT '是否在看板显示'"))
        conn.commit()
        print("迁移完成：已添加 show_on_dashboard 字段")

if __name__ == "__main__":
    migrate()
