"""迁移脚本：为 device_status_monitor_configs 表添加 device_status 字段"""
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
            WHERE table_name = 'device_status_monitor_configs' AND column_name = 'device_status'
        """))
        if result.fetchone():
            print("字段 device_status 已存在，跳过迁移")
            return

        conn.execute(text(
            "ALTER TABLE device_status_monitor_configs ADD COLUMN device_status VARCHAR(20) DEFAULT NULL COMMENT '匹配成功时映射的设备状态：active/inactive/maintenance'"
        ))
        conn.commit()
        print("迁移完成：已添加 device_status 字段")

if __name__ == "__main__":
    migrate()
