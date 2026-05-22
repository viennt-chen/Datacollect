"""
产品订单 Schema 定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductOrderBase(BaseModel):
    """产品订单基础信息"""
    doc_no: str = Field(..., description='订单编号')
    part_number: str = Field(..., description='零件号')
    u9_material_code: str = Field(..., description='U9 物料号')
    specs: Optional[str] = Field(None, description='规格型号')
    item_code: Optional[str] = Field(None, description='物料代码')
    item_name: Optional[str] = Field(None, description='物料名称')
    planned_output: int = Field(0, description='计划总产量')
    query_date: str = Field(..., description='查询日期 YYYY-MM-DD')
    product_qty: float = Field(0, description='订单数量')
    total_complete_qty: float = Field(0, description='累计完工数量')
    total_eligible_qty: float = Field(0, description='合格数量')
    total_scrap_qty: float = Field(0, description='报废数量')
    complete_wh: Optional[str] = Field(None, description='完工仓库')
    complete_wh_code: Optional[str] = Field(None, description='完工仓库代码')
    line_number: Optional[str] = Field(None, description='产线号')
    line_code: Optional[str] = Field(None, description='产线代码')
    line_description: Optional[str] = Field(None, description='产线描述')
    department_code: Optional[str] = Field(None, description='部门代码')
    department_name: Optional[str] = Field(None, description='部门名称')
    doc_type_code: Optional[str] = Field(None, description='单据类型代码')
    doc_type: Optional[str] = Field(None, description='单据类型')
    doc_state: Optional[str] = Field(None, description='单据状态')
    project: Optional[str] = Field(None, description='项目')
    mold_no: Optional[str] = Field(None, description='模具编号')
    cavity_number: Optional[str] = Field(None, description='腔号')
    short_code: Optional[str] = Field(None, description='短代码')
    packet_qty: float = Field(0, description='包装数量')
    cycle_time: Optional[str] = Field(None, description='周期时间')
    machine: Optional[str] = Field(None, description='设备')
    over_rate: float = Field(0, description='超产率')
    start_date: Optional[datetime] = Field(None, description='开始日期')
    description: Optional[str] = Field(None, description='描述')

    class Config:
        from_attributes = True


class ProductOrderCreate(ProductOrderBase):
    """创建产品订单"""
    query_time: Optional[datetime] = None


class ProductOrderDetail(ProductOrderBase):
    """产品订单详情（含 ID 和时间戳）"""
    id: int
    query_time: datetime
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductOrderList(BaseModel):
    """产品订单列表响应"""
    total: int
    items: List[ProductOrderDetail]


class OrderQueryParams(BaseModel):
    """订单查询参数"""
    part_number: Optional[str] = None
    doc_no: Optional[str] = None
    doc_state: Optional[str] = None
    doc_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    page: int = 1
    page_size: int = 20


class OrderStatsResponse(BaseModel):
    """订单统计响应"""
    total_orders: int
    total_planned_output: int
    total_detail_count: int
    today_orders: int
    today_planned_output: int
    date: str


# ERP 查询相关的 Schema
class ProductOrderDetailItem(BaseModel):
    """订单明细项（对应 U9 返回的 details 数组中的每个对象）"""
    docNo: str = Field(..., description='订单编号')
    itemCode: str = Field(..., description='物料代码')
    specs: str = Field(..., description='规格型号')
    itemName: Optional[str] = Field(None, description='物料名称')
    startDate: Optional[str] = Field(None, description='开始日期')
    productQty: float = Field(0, description='订单数量')
    totalCompleteQty: float = Field(0, description='累计完工数量')
    totalEligibleQty: float = Field(0, description='合格数量')
    totalScrapQty: float = Field(0, description='报废数量')
    lineNumber: Optional[str] = Field(None, description='产线号')
    completeWhCode: Optional[str] = Field(None, description='完工仓库代码')
    completeWh: Optional[str] = Field(None, description='完工仓库')
    lineCode: Optional[str] = Field(None, description='产线代码')
    docTypeCode: Optional[str] = Field(None, description='单据类型代码')
    docType: Optional[str] = Field(None, description='单据类型')
    lineDescription: Optional[str] = Field(None, description='产线描述')
    departmentCode: Optional[str] = Field(None, description='部门代码')
    departmentName: Optional[str] = Field(None, description='部门名称')
    project: Optional[str] = Field(None, description='项目')
    docState: Optional[str] = Field(None, description='单据状态')
    shortCode: Optional[str] = Field(None, description='短代码')
    packetQty: float = Field(0, description='包装数量')
    moldNo: Optional[str] = Field(None, description='模具编号')
    cycleTime: Optional[str] = Field(None, description='周期时间')
    machine: Optional[str] = Field(None, description='设备')
    cavityNumber: Optional[str] = Field(None, description='腔号')
    description: Optional[str] = Field(None, description='描述')
    overRate: float = Field(0, description='超产率')

    class Config:
        from_attributes = True


class ProductOrderData(BaseModel):
    """订单数据（包含计划产量和明细）"""
    planned_output: int = Field(0, description='计划总产量')
    specs: str = Field(..., description='规格型号')
    date: str = Field(..., description='查询日期')
    details: List[ProductOrderDetailItem] = Field(default_factory=list, description='订单明细列表')

    class Config:
        from_attributes = True


class ProductOrderQueryResponse(BaseModel):
    """产品订单查询响应"""
    success: bool = Field(..., description='是否成功')
    data: ProductOrderData = Field(..., description='订单数据')
    message: str = Field(..., description='响应消息')

    class Config:
        from_attributes = True


class OrderAnalysisByDate(BaseModel):
    """按日期分析的订单数据"""
    query_date: str = Field(..., description='查询日期')
    order_count: int = Field(0, description='订单数量')
    total_planned_output: int = Field(0, description='计划总产量')
    total_product_qty: float = Field(0, description='订单总数量')


class OrderAnalysisByMaterial(BaseModel):
    """按物料号分析的订单数据"""
    u9_material_code: str = Field(..., description='U9 物料号')
    part_number: str = Field(..., description='零件号')
    specs: str = Field(..., description='规格型号')
    order_count: int = Field(0, description='订单数量')
    total_planned_output: int = Field(0, description='计划总产量')
    total_product_qty: float = Field(0, description='订单总数量')
    avg_product_qty: float = Field(0, description='平均订单数量')


class OrderAnalysisByWarehouse(BaseModel):
    """按仓库分析的订单数据"""
    complete_wh_code: str = Field(..., description='仓库代码')
    complete_wh: str = Field(..., description='仓库名称')
    order_count: int = Field(0, description='订单数量')
    total_product_qty: float = Field(0, description='总数量')
    total_complete_qty: float = Field(0, description='总完工数量')
    total_eligible_qty: float = Field(0, description='总合格数量')


class OrderAnalysisByDocState(BaseModel):
    """按订单状态分析的订单数据"""
    doc_state: str = Field(..., description='订单状态')
    order_count: int = Field(0, description='订单数量')
    total_product_qty: float = Field(0, description='总数量')


class OrderAnalysisByDepartment(BaseModel):
    """按部门分析的订单数据"""
    department_code: str = Field(..., description='部门代码')
    department_name: str = Field(..., description='部门名称')
    order_count: int = Field(0, description='订单数量')
    total_product_qty: float = Field(0, description='总数量')


class OrderAnalysisByProject(BaseModel):
    """按项目分析的订单数据"""
    project: str = Field(..., description='项目名称')
    order_count: int = Field(0, description='订单数量')
    total_product_qty: float = Field(0, description='总数量')


class OrderAnalysisByDocType(BaseModel):
    """按订单类型分析的订单数据"""
    doc_type_code: str = Field(..., description='订单类型代码')
    doc_type: str = Field(..., description='订单类型')
    order_count: int = Field(0, description='订单数量')
    total_product_qty: float = Field(0, description='总数量')


class OrderTrendData(BaseModel):
    """订单趋势数据"""
    date: str = Field(..., description='日期')
    order_count: int = Field(0, description='订单数量')
    total_planned_output: int = Field(0, description='计划总产量')
    total_product_qty: float = Field(0, description='订单总数量')


class OrderComprehensiveAnalysis(BaseModel):
    """订单综合分析响应"""
    date_range: dict = Field(..., description='查询日期范围')
    summary: dict = Field(..., description='汇总统计')
    by_date: List[OrderAnalysisByDate] = Field(default_factory=list, description='按日期分析')
    by_material: List[OrderAnalysisByMaterial] = Field(default_factory=list, description='按物料分析')
    by_warehouse: List[OrderAnalysisByWarehouse] = Field(default_factory=list, description='按仓库分析')
    by_doc_state: List[OrderAnalysisByDocState] = Field(default_factory=list, description='按订单状态分析')
    by_department: List[OrderAnalysisByDepartment] = Field(default_factory=list, description='按部门分析')
    by_project: List[OrderAnalysisByProject] = Field(default_factory=list, description='按项目分析')
    by_doc_type: List[OrderAnalysisByDocType] = Field(default_factory=list, description='按订单类型分析')
    trend: List[OrderTrendData] = Field(default_factory=list, description='订单趋势')
