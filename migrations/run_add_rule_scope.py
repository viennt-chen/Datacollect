"""迁移脚本：为 device_status_monitor_configs 表添加 rule_scope 字段，device_code 改为可空"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine

def migrate():
    with engine.connect() as conn:
        # 检查 rule_scope 字段是否已存在
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'device_status_monitor_configs' AND column_name = 'rule_scope'
        """))
        if not result.fetchone():
            conn.execute(text(
                "ALTER TABLE device_status_monitor_configs ADD COLUMN rule_scope VARCHAR(20) NOT NULL DEFAULT 'device' COMMENT '规则范围：basic=device基础规则，device=设备规则'"
            ))
            print("已添加 rule_scope 字段")
        else:
            print("rule_scope 字段已存在，跳过")

        # 修改 device_code 为可空
        conn.execute(text(
            "ALTER TABLE device_status_monitor_configs MODIFY COLUMN device_code VARCHAR(100) NULL COMMENT '设备编号（基础规则可为空）'"
        ))
        print("已修改 device_code 为可空")

        conn.commit()
        print("迁移完成")

if __name__ == "__main__":
    migrate()
