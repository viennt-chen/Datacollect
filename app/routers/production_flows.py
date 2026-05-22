"""
工艺路线模板 API 路由（流程图版）
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.production_flow import ProductionFlow
from app.schemas.production_flow import (
    FlowCreate, FlowUpdate, FlowResponse, FlowListResponse,
    FlowSimpleResponse,
)

router = APIRouter(prefix="/production-flows", tags=["工艺路线模板"])


def _parse_json(text):
    if not text:
        return []
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return []


def _flow_to_response(flow):
    return FlowResponse(
        id=flow.id,
        flow_code=flow.flow_code,
        flow_name=flow.flow_name,
        description=flow.description,
        status=flow.status or 'active',
        nodes_data=_parse_json(flow.nodes_data),
        edges_data=_parse_json(flow.edges_data),
        created_at=flow.created_at,
        updated_at=flow.updated_at,
    )


@router.get("/templates", response_model=list[FlowSimpleResponse])
def get_templates(db: Session = Depends(get_db)):
    """获取所有活跃模板（下拉选择用）"""
    flows = db.query(ProductionFlow).filter(
        ProductionFlow.status == 'active'
    ).order_by(ProductionFlow.flow_code).all()

    result = []
    for flow in flows:
        nodes = _parse_json(flow.nodes_data)
        result.append(FlowSimpleResponse(
            id=flow.id,
            flow_code=flow.flow_code,
            flow_name=flow.flow_name,
            node_count=len(nodes),
        ))
    return result


@router.get("/", response_model=FlowListResponse)
def list_flows(
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """列表查询工艺路线模板"""
    query = db.query(ProductionFlow)

    if status:
        query = query.filter(ProductionFlow.status == status)
    if keyword:
        query = query.filter(
            ProductionFlow.flow_code.contains(keyword) |
            ProductionFlow.flow_name.contains(keyword)
        )

    total = query.count()
    items = query.order_by(ProductionFlow.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return FlowListResponse(
        total=total,
        items=[_flow_to_response(f) for f in items],
    )


@router.post("/", response_model=FlowResponse)
def create_flow(data: FlowCreate, db: Session = Depends(get_db)):
    """新增工艺路线模板（含流程图数据）"""
    existing = db.query(ProductionFlow).filter(ProductionFlow.flow_code == data.flow_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="流程编码已存在")

    flow = ProductionFlow(
        flow_code=data.flow_code,
        flow_name=data.flow_name,
        description=data.description,
        status=data.status,
        nodes_data=json.dumps(data.nodes_data, ensure_ascii=False) if data.nodes_data else '[]',
        edges_data=json.dumps(data.edges_data, ensure_ascii=False) if data.edges_data else '[]',
    )
    db.add(flow)
    db.commit()
    db.refresh(flow)
    return _flow_to_response(flow)


@router.get("/{flow_id}", response_model=FlowResponse)
def get_flow(flow_id: int, db: Session = Depends(get_db)):
    """获取工艺路线模板详情（含流程图数据）"""
    flow = db.query(ProductionFlow).filter(ProductionFlow.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="工艺路线不存在")
    return _flow_to_response(flow)


@router.put("/{flow_id}", response_model=FlowResponse)
def update_flow(flow_id: int, data: FlowUpdate, db: Session = Depends(get_db)):
    """更新工艺路线模板"""
    flow = db.query(ProductionFlow).filter(ProductionFlow.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="工艺路线不存在")

    update_data = data.model_dump(exclude_unset=True)

    if 'flow_code' in update_data and update_data['flow_code'] != flow.flow_code:
        existing = db.query(ProductionFlow).filter(ProductionFlow.flow_code == update_data['flow_code']).first()
        if existing:
            raise HTTPException(status_code=400, detail="流程编码已存在")

    # 处理 JSON 字段
    if 'nodes_data' in update_data:
        flow.nodes_data = json.dumps(update_data.pop('nodes_data'), ensure_ascii=False)
    if 'edges_data' in update_data:
        flow.edges_data = json.dumps(update_data.pop('edges_data'), ensure_ascii=False)

    for key, value in update_data.items():
        setattr(flow, key, value)

    db.commit()
    db.refresh(flow)
    return _flow_to_response(flow)


@router.delete("/{flow_id}")
def delete_flow(flow_id: int, db: Session = Depends(get_db)):
    """删除工艺路线模板"""
    flow = db.query(ProductionFlow).filter(ProductionFlow.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="工艺路线不存在")

    db.delete(flow)
    db.commit()
    return {"message": "删除成功"}
