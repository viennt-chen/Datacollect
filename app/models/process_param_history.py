"""
工艺参数变更历史模型
记录 MQTT 值变化和参数定义变更
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from datetime import datetime

from app.database import Base


class ProcessParamHistory(Base):
    """工艺参数变更历史表"""
    __tablename__ = "process_param_history"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 关联工艺定义 ID
    process_id = Column(Integer, nullable=False, index=True, comment='工艺定义ID')

    # 变更类型：mqtt_value_change / definition_change
    change_type = Column(String(20), nullable=False, index=True, comment='变更类型')

    # 参数名
    param_name = Column(String(100), nullable=False, comment='参数名')

    # 旧值 / 新值（JSON 字符串）
    old_value = Column(Text, comment='旧值')
    new_value = Column(Text, comment='新值')

    # 来源：topic 名称 / 'manual'
    source = Column(String(50), comment='变更来源')

    # 操作人
    operator = Column(String(100), comment='操作人')

    # 时间
    created_at = Column(DateTime, default=datetime.now, index=True, comment='创建时间')

    __table_args__ = (
        Index('idx_process_change', 'process_id', 'change_type'),
    )

    def __repr__(self):
        return f"<ProcessParamHistory(id={self.id}, type={self.change_type}, param={self.param_name})>"
