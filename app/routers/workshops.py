"""
车间管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

logger = logging.getLogger(__name__)

from app.database import get_db
from app.models.workshop import Workshop
from app.schemas.workshop import (
    WorkshopCreate, WorkshopUpdate, WorkshopDetail, WorkshopList
)

router = APIRouter()


@router.get("/", response_model=WorkshopList)
async def list_workshops(
    name: Optional[str] = Query(default=None, description="车间名称"),
    code: Optional[str] = Query(default=None, description="车间编码"),
    status: Optional[str] = Query(default=None, description="状态"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """查询车间列表"""
    query = db.query(Workshop)

    if name:
        query = query.filter(Workshop.name.contains(name))
    if code:
        query = query.filter(Workshop.code.contains(code))
    if status:
        query = query.filter(Workshop.status == status)

    total = query.count()
    items = query.order_by(Workshop.sort_order, Workshop.id).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return WorkshopList(total=total, items=items)


@router.get("/all")
async def list_all_workshops(db: Session = Depends(get_db)):
    """获取所有启用的车间（用于下拉选择）"""
    workshops = db.query(Workshop).filter(
        Workshop.status == 'active'
    ).order_by(Workshop.sort_order, Workshop.id).all()
    return {"items": workshops}


@router.get("/{workshop_id}", response_model=WorkshopDetail)
async def get_workshop(workshop_id: int, db: Session = Depends(get_db)):
    """获取车间详情"""
    workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if not workshop:
        raise HTTPException(status_code=404, detail="车间不存在")
    return workshop


@router.post("/", response_model=WorkshopDetail)
async def create_workshop(workshop: WorkshopCreate, db: Session = Depends(get_db)):
    """创建车间"""
    existing = db.query(Workshop).filter(
        (Workshop.name == workshop.name) | (Workshop.code == workshop.code)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="车间名称或编码已存在")

    db_workshop = Workshop(**workshop.model_dump())
    db.add(db_workshop)
    db.commit()
    db.refresh(db_workshop)
    return db_workshop


@router.put("/{workshop_id}", response_model=WorkshopDetail)
async def update_workshop(workshop_id: int, workshop: WorkshopUpdate, db: Session = Depends(get_db)):
    """更新车间"""
    db_workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if not db_workshop:
        raise HTTPException(status_code=404, detail="车间不存在")

    if workshop.name:
        existing = db.query(Workshop).filter(
            Workshop.name == workshop.name, Workshop.id != workshop_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="车间名称已存在")

    if workshop.code:
        existing = db.query(Workshop).filter(
            Workshop.code == workshop.code, Workshop.id != workshop_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="车间编码已存在")

    update_data = workshop.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_workshop, field, value)

    db.commit()
    db.refresh(db_workshop)
    return db_workshop


@router.delete("/{workshop_id}")
async def delete_workshop(workshop_id: int, db: Session = Depends(get_db)):
    """删除车间"""
    db_workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if not db_workshop:
        raise HTTPException(status_code=404, detail="车间不存在")

    db.delete(db_workshop)
    db.commit()
    return {"success": True, "message": "车间已删除"}
