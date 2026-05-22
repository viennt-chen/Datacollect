"""
工艺参数数据模型
用于存储和管理工艺参数历史数据
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from datetime import datetime

from app.database import Base


class ProcessParameter(Base):
    """工艺参数表"""
    __tablename__ = "process_parameters"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 基础信息
    create_time = Column(DateTime, default=datetime.now, nullable=False, index=True, comment="创建时间")
    process_type = Column(String(50), index=True, comment="工艺类型")
    machine_id = Column(String(50), index=True, comment="设备编号")
    product_model = Column(String(100), index=True, comment="产品型号")
    
    # 参数信息
    param_name = Column(String(100), nullable=False, index=True, comment="参数名称")
    param_value = Column(Float, nullable=False, comment="参数值")
    unit = Column(String(20), comment="单位")
    
    # 关联信息
    start_code = Column(String(50), index=True, comment="启动码")
    process_no = Column(String(50), index=True, comment="工艺编号")
    batch_no = Column(String(50), comment="批次号")
    
    # 人员和备注
    operator = Column(String(50), comment="操作员")
    remark = Column(Text, comment="备注")
    
    # 创建索引以优化查询性能
    __table_args__ = (
        Index('idx_time_machine', 'create_time', 'machine_id'),
        Index('idx_process_param', 'process_type', 'param_name'),
        Index('idx_start_code', 'start_code', 'process_no'),
    )
    
    def __repr__(self):
        return f"<ProcessParameter(id={self.id}, param_name={self.param_name}, param_value={self.param_value})>"
