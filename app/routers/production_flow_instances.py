"""
流程执行实例 API 路由（流程图版）
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.production_flow import ProductionFlow
from app.models.production_flow_instance import ProductionFlowInstance
from app.schemas.production_flow import (
    FlowInstanceCreate, FlowInstanceResponse, FlowInstanceListResponse,
    NodeStatusUpdate, FlowInstanceStats,
)

router = APIRouter(prefix="/production-flow-instances", tags=["流程执行跟踪"])


def _parse_json(text):
    if not text:
        return {}
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}


def _instance_to_response(inst):
    return FlowInstanceResponse(
        id=inst.id,
        flow_id=inst.flow_id,
        doc_no=inst.doc_no,
        part_number=inst.part_number,
        device_code=inst.device_code,
        status=inst.status,
        node_statuses=_parse_json(inst.node_statuses),
        planned_qty=inst.planned_qty,
        completed_qty=inst.completed_qty or 0,
        record_date=inst.record_date,
        start_time=inst.start_time,
        end_time=inst.end_time,
        notes=inst.notes,
        created_at=inst.created_at,
        updated_at=inst.updated_at,
    )


@router.get("/stats", response_model=FlowInstanceStats)
def get_stats(
    record_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """流程执行统计"""
    query = db.query(ProductionFlowInstance)
    if record_date:
        query = query.filter(ProductionFlowInstance.record_date == record_date)

    instances = query.all()
    return FlowInstanceStats(
        total=len(instances),
        in_progress=sum(1 for i in instances if i.status == 'in_progress'),
        completed=sum(1 for i in instances if i.status == 'completed'),
        paused=sum(1 for i in instances if i.status == 'paused'),
        cancelled=sum(1 for i in instances if i.status == 'cancelled'),
        total_planned=sum(i.planned_qty or 0 for i in instances),
        total_completed=sum(i.completed_qty or 0 for i in instances),
    )


@router.get("/", response_model=FlowInstanceListResponse)
def list_instances(
    status: Optional[str] = Query(None),
    doc_no: Optional[str] = Query(None),
    part_number: Optional[str] = Query(None),
    record_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """实例列表"""
    query = db.query(ProductionFlowInstance)

    if status:
        query = query.filter(ProductionFlowInstance.status == status)
    if doc_no:
        query = query.filter(ProductionFlowInstance.doc_no.contains(doc_no))
    if part_number:
        query = query.filter(ProductionFlowInstance.part_number.contains(part_number))
    if record_date:
        query = query.filter(ProductionFlowInstance.record_date == record_date)

    total = query.count()
    items = query.order_by(ProductionFlowInstance.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return FlowInstanceListResponse(
        total=total,
        items=[_instance_to_response(i) for i in items],
    )


@router.post("/", response_model=FlowInstanceResponse)
def create_instance(data: FlowInstanceCreate, db: Session = Depends(get_db)):
    """创建流程执行实例（从模板初始化节点状态）"""
    flow = db.query(ProductionFlow).filter(ProductionFlow.id == data.flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="工艺路线模板不存在")

    nodes = _parse_json(flow.nodes_data)
    if not nodes:
        raise HTTPException(status_code=400, detail="工艺路线模板没有节点")

    record_date = data.record_date or datetime.now().strftime('%Y-%m-%d')

    # 初始化所有节点状态为 pending
    node_statuses = {}
    for node in nodes:
        node_id = node.get('id', '')
        node_statuses[node_id] = 'pending'

    instance = ProductionFlowInstance(
        flow_id=data.flow_id,
        doc_no=data.doc_no,
        part_number=data.part_number,
        device_code=data.device_code,
        planned_qty=data.planned_qty,
        record_date=record_date,
        status='in_progress',
        node_statuses=json.dumps(node_statuses, ensure_ascii=False),
        start_time=datetime.now(),
        notes=data.notes,
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return _instance_to_response(instance)


@router.get("/{instance_id}", response_model=FlowInstanceResponse)
def get_instance(instance_id: int, db: Session = Depends(get_db)):
    """获取实例详情"""
    instance = db.query(ProductionFlowInstance).filter(
        ProductionFlowInstance.id == instance_id
    ).first()
    if not instance:
        raise HTTPException(status_code=404, detail="实例不存在")
    return _instance_to_response(instance)


@router.put("/{instance_id}/nodes/{node_id}", response_model=FlowInstanceResponse)
def update_node_status(
    instance_id: int,
    node_id: str,
    data: NodeStatusUpdate,
    db: Session = Depends(get_db),
):
    """更新单个节点状态"""
    instance = db.query(ProductionFlowInstance).filter(
        ProductionFlowInstance.id == instance_id
    ).first()
    if not instance:
        raise HTTPException(status_code=404, detail="实例不存在")

    node_statuses = _parse_json(instance.node_statuses)
    if node_id not in node_statuses:
        raise HTTPException(status_code=404, detail="节点不存在")

    node_statuses[node_id] = data.status
    instance.node_statuses = json.dumps(node_statuses, ensure_ascii=False)

    # 更新完成数量
    if data.completed_qty is not None:
        instance.completed_qty = (instance.completed_qty or 0) + data.completed_qty

    # 检查是否所有节点都已完成
    all_done = all(s in ('completed', 'skipped') for s in node_statuses.values())
    if all_done and instance.status == 'in_progress':
        instance.status = 'completed'
        instance.end_time = datetime.now()

    db.commit()
    db.refresh(instance)
    return _instance_to_response(instance)


@router.post("/{instance_id}/complete-node/{node_id}", response_model=FlowInstanceResponse)
def complete_node_and_activate_downstream(
    instance_id: int,
    node_id: str,
    db: Session = Depends(get_db),
):
    """完成某节点并自动激活下游节点"""
    instance = db.query(ProductionFlowInstance).filter(
        ProductionFlowInstance.id == instance_id
    ).first()
    if not instance:
        raise HTTPException(status_code=404, detail="实例不存在")

    node_statuses = _parse_json(instance.node_statuses)
    if node_id not in node_statuses:
        raise HTTPException(status_code=404, detail="节点不存在")

    # 标记当前节点完成
    node_statuses[node_id] = 'completed'

    # 获取 edges 找到下游节点
    flow = db.query(ProductionFlow).filter(ProductionFlow.id == instance.flow_id).first()
    edges = _parse_json(flow.edges_data) if flow else []

    # 找到从当前节点出发的所有下游节点
    downstream_ids = set()
    for edge in edges:
        if edge.get('source') == node_id:
            downstream_ids.add(edge.get('target'))

    # 激活下游节点（如果它们还是 pending 状态）
    for did in downstream_ids:
        if did in node_statuses and node_statuses[did] == 'pending':
            # 检查该下游节点的所有上游是否都已完成
            upstream_ids = set()
            for e in edges:
                if e.get('target') == did:
                    upstream_ids.add(e.get('source'))
            all_upstream_done = all(
                node_statuses.get(uid) in ('completed', 'skipped')
                for uid in upstream_ids
            )
            if all_upstream_done:
                node_statuses[did] = 'in_progress'

    instance.node_statuses = json.dumps(node_statuses, ensure_ascii=False)

    # 检查是否所有节点都已完成
    all_done = all(s in ('completed', 'skipped') for s in node_statuses.values())
    if all_done and instance.status == 'in_progress':
        instance.status = 'completed'
        instance.end_time = datetime.now()

    db.commit()
    db.refresh(instance)
    return _instance_to_response(instance)


@router.post("/{instance_id}/complete", response_model=FlowInstanceResponse)
def complete_instance(instance_id: int, db: Session = Depends(get_db)):
    """完成整个流程"""
    instance = db.query(ProductionFlowInstance).filter(
        ProductionFlowInstance.id == instance_id
    ).first()
    if not instance:
        raise HTTPException(status_code=404, detail="实例不存在")

    node_statuses = _parse_json(instance.node_statuses)
    for nid in node_statuses:
        if node_statuses[nid] in ('pending', 'in_progress'):
            node_statuses[nid] = 'completed'

    instance.node_statuses = json.dumps(node_statuses, ensure_ascii=False)
    instance.status = 'completed'
    instance.end_time = datetime.now()

    db.commit()
    db.refresh(instance)
    return _instance_to_response(instance)


@router.delete("/{instance_id}")
def delete_instance(instance_id: int, db: Session = Depends(get_db)):
    """删除实例"""
    instance = db.query(ProductionFlowInstance).filter(
        ProductionFlowInstance.id == instance_id
    ).first()
    if not instance:
        raise HTTPException(status_code=404, detail="实例不存在")

    db.delete(instance)
    db.commit()
    return {"message": "删除成功"}
