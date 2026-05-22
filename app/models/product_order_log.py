"""产品订单查询日志模型"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ProductOrderQueryLog(Base):
    """产品订单查询日志表"""
    __tablename__ = "product_order_query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 查询信息
    part_number = Column(String(100), index=True, comment="零件号")
    specs = Column(String(200), comment="规格型号")
    
    # 查询结果
    planned_output = Column(Integer, default=0, comment="计划产量")
    order_count = Column(Integer, default=0, comment="订单数量")
    saved_count = Column(Integer, default=0, comment="保存订单数")
    
    # 查询状态
    status = Column(String(50), default="success", comment="状态：success/failed")
    error_message = Column(Text, comment="错误信息")
    
    # 查询时间范围
    query_date = Column(String(20), index=True, comment="查询日期")
    
    # 执行信息
    execution_type = Column(String(50), default="manual", comment="执行类型：manual/auto")
    duration_seconds = Column(Float, comment="查询耗时（秒）")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def __repr__(self):
        return f"<ProductOrderQueryLog(id={self.id}, part_number={self.part_number}, status={self.status})>"
