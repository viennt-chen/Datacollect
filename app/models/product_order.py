"""
产品订单模型 - 单表结构
用于存储 U9 ERP 系统查询的产品订单数据
订单号(doc_no)保持唯一
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Index
from datetime import datetime

from app.database import Base


class ProductOrder(Base):
    """产品订单表 - 单表存储所有订单信息"""
    __tablename__ = "product_orders"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 订单号（唯一）
    doc_no = Column(String(100), nullable=False, unique=True, comment='订单编号')

    # 基本信息
    part_number = Column(String(100), nullable=False, comment='零件号')
    u9_material_code = Column(String(100), nullable=False, comment='U9 物料号')
    specs = Column(String(255), comment='规格型号')
    item_code = Column(String(100), comment='物料代码')
    item_name = Column(Text, comment='物料名称')

    # 计划信息
    planned_output = Column(Integer, default=0, comment='计划总产量')
    query_date = Column(String(20), nullable=False, comment='查询日期 YYYY-MM-DD')

    # 订单数量信息
    product_qty = Column(Float, default=0, comment='订单数量')
    total_complete_qty = Column(Float, default=0, comment='累计完工数量')
    total_eligible_qty = Column(Float, default=0, comment='合格数量')
    total_scrap_qty = Column(Float, default=0, comment='报废数量')

    # 仓库信息
    complete_wh = Column(String(255), comment='完工仓库')
    complete_wh_code = Column(String(50), comment='完工仓库代码')

    # 产线信息
    line_number = Column(String(100), comment='产线号')
    line_code = Column(String(50), comment='产线代码')
    line_description = Column(Text, comment='产线描述')

    # 部门信息
    department_code = Column(String(50), comment='部门代码')
    department_name = Column(String(255), comment='部门名称')

    # 订单类型
    doc_type_code = Column(String(50), comment='单据类型代码')
    doc_type = Column(String(100), comment='单据类型')
    doc_state = Column(String(50), comment='单据状态')

    # 项目信息
    project = Column(String(255), comment='项目')

    # 模具信息
    mold_no = Column(String(100), comment='模具编号')
    cavity_number = Column(String(100), comment='腔号')
    short_code = Column(String(50), comment='短代码')

    # 生产信息
    packet_qty = Column(Float, default=0, comment='包装数量')
    cycle_time = Column(String(50), comment='周期时间')
    machine = Column(String(100), comment='设备')
    over_rate = Column(Float, default=0, comment='超产率')

    # 日期信息
    start_date = Column(DateTime, comment='开始日期')

    # 描述
    description = Column(Text, comment='描述')

    # 查询时间
    query_time = Column(DateTime, default=datetime.now, nullable=False, comment='查询时间')

    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    # 数据库索引 - 优化查询性能
    __table_args__ = (
        Index('ix_product_orders_query_date', 'query_date'),
        Index('ix_product_orders_u9_material_code', 'u9_material_code'),
        Index('ix_product_orders_part_number', 'part_number'),
        Index('ix_product_orders_doc_state', 'doc_state'),
    )

    def __repr__(self):
        return f"<ProductOrder(id={self.id}, doc_no={self.doc_no}, part_number={self.part_number})>"
