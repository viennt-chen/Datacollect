"""
物料分类管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.material_category import MaterialCategory

router = APIRouter()


class CategoryCreate(BaseModel):
    type_key: str
    type_name: str
    category_name: str
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    sort_order: Optional[int] = None


@router.get("/")
async def list_categories(db: Session = Depends(get_db)):
    """获取所有分类，按类型分组返回"""
    categories = db.query(MaterialCategory).order_by(
        MaterialCategory.type_key, MaterialCategory.sort_order, MaterialCategory.id
    ).all()

    result = {}
    for cat in categories:
        if cat.type_key not in result:
            result[cat.type_key] = {
                "type_key": cat.type_key,
                "type_name": cat.type_name,
                "categories": []
            }
        result[cat.type_key]["categories"].append({
            "id": cat.id,
            "category_name": cat.category_name,
            "sort_order": cat.sort_order,
        })

    return {"items": list(result.values())}


@router.post("/")
async def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    """新增分类"""
    existing = db.query(MaterialCategory).filter(
        MaterialCategory.type_key == data.type_key,
        MaterialCategory.category_name == data.category_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该分类已存在")

    category = MaterialCategory(
        type_key=data.type_key,
        type_name=data.type_name,
        category_name=data.category_name,
        sort_order=data.sort_order,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return {"id": category.id, "category_name": category.category_name, "sort_order": category.sort_order}


@router.put("/{category_id}")
async def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    """更新分类"""
    category = db.query(MaterialCategory).filter(MaterialCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    if data.category_name is not None:
        category.category_name = data.category_name
    if data.sort_order is not None:
        category.sort_order = data.sort_order

    db.commit()
    return {"id": category.id, "category_name": category.category_name, "sort_order": category.sort_order}


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """删除分类"""
    category = db.query(MaterialCategory).filter(MaterialCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    db.delete(category)
    db.commit()
    return {"success": True, "message": "分类已删除"}
