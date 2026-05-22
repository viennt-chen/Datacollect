"""
BOM（物料清单）管理路由 - 离散制造
优化版本：增加拖拽排序API、循环引用深度限制、树查询性能优化、事务安全加固
"""
import logging
from typing import Optional, Dict, List, Set, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.bom import BomHeader, BomItem
from app.models.material import Material
from app.schemas.bom import (
    BomHeaderQuery, BomHeaderCreate, BomHeaderUpdate,
    BomHeaderDetail, BomHeaderWithItems, BomHeaderList,
    BomItemCreate, BomItemUpdate, BomItemDetail,
    BomCopyRequest, BomTreeNode, BomItemReorderRequest,
    BomItemMoveRequest
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ 辅助函数 ============

def _get_product_info(db: Session, product_id: int) -> Optional[dict]:
    """获取产品基本信息"""
    product = db.query(Material).filter(Material.id == product_id).first()
    if not product:
        return None
    return {
        "product_name": product.product_name,
        "product_code": product.u9_material_code,
        "product_part_number": product.part_number,
    }


def _enrich_header(db: Session, header: BomHeader) -> dict:
    """为 BOM 主表补充产品信息和子项数量"""
    product_info = _get_product_info(db, header.product_id) or {}
    item_count = db.query(func.count(BomItem.id)).filter(
        BomItem.bom_header_id == header.id
    ).scalar() or 0

    return {
        "id": header.id,
        "bom_code": header.bom_code,
        "bom_name": header.bom_name,
        "product_id": header.product_id,
        "version": header.version,
        "status": header.status,
        "effective_date": header.effective_date,
        "expiry_date": header.expiry_date,
        "description": header.description,
        "created_by": header.created_by,
        "updated_by": header.updated_by,
        "created_at": header.created_at,
        "updated_at": header.updated_at,
        "product_name": product_info.get("product_name"),
        "product_code": product_info.get("product_code"),
        "product_part_number": product_info.get("product_part_number"),
        "item_count": item_count,
    }


def _enrich_item(db: Session, item: BomItem) -> dict:
    """为 BOM 子项补充产品信息"""
    product = db.query(Material).filter(Material.id == item.child_product_id).first()
    return {
        "id": item.id,
        "bom_header_id": item.bom_header_id,
        "child_product_id": item.child_product_id,
        "quantity": item.quantity,
        "unit": item.unit,
        "reference_designator": item.reference_designator,
        "item_no": item.item_no,
        "remark": item.remark,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "child_product_name": product.product_name if product else None,
        "child_product_code": product.u9_material_code if product else None,
        "child_part_number": product.part_number if product else None,
        "child_specification": product.specification if product else None,
        "child_unit": product.unit if product else None,
    }


async def _get_bom_with_items(bom_id: int, db: Session) -> dict:
    """获取 BOM 详情（含子项）"""
    header = db.query(BomHeader).filter(BomHeader.id == bom_id).first()
    if not header:
        raise HTTPException(status_code=404, detail="BOM 不存在")

    result = _enrich_header(db, header)
    items = db.query(BomItem).filter(BomItem.bom_header_id == bom_id).order_by(BomItem.item_no).all()
    result["items"] = [_enrich_item(db, item) for item in items]
    return result


def _check_circular_ref(
    db: Session,
    parent_product_id: int,
    child_product_id: int,
    visited: Set[int] = None,
    max_depth: int = 20,
    current_depth: int = 0
) -> bool:
    """
    检查将 child_product_id 作为子物料添加到 parent_product_id 的 BOM 下是否会形成循环引用。
    返回 True 表示存在循环风险。
    """
    if current_depth >= max_depth:
        logger.warning(f"循环引用检查超过最大深度 {max_depth}，中断检查")
        return False
    if parent_product_id == child_product_id:
        return True
    if visited is None:
        visited = set()
    if child_product_id in visited:
        return False
    visited.add(child_product_id)

    # 查找子物料的活跃 BOM
    child_header = db.query(BomHeader).filter(
        BomHeader.product_id == child_product_id,
        BomHeader.status == 'active'
    ).first()
    if not child_header:
        return False

    # 递归检查子物料 BOM 中的所有子项
    child_items = db.query(BomItem).filter(BomItem.bom_header_id == child_header.id).all()
    for ci in child_items:
        if _check_circular_ref(db, parent_product_id, ci.child_product_id, visited, max_depth, current_depth + 1):
            return True
    return False


def _build_bom_tree_with_cache(
    db: Session,
    product_id: int,
    quantity: float,
    level: int,
    max_level: int,
    header_cache: Dict[int, BomHeader]
) -> List[dict]:
    """
    递归构建多级 BOM 树，使用 header_cache 避免重复查询。
    header_cache: product_id -> active BomHeader (None 表示无活跃 BOM)
    """
    if level >= max_level:
        return []

    header = header_cache.get(product_id)
    if header is None:
        # 检查是否显式缓存为 None（表示无活跃 BOM）
        if product_id in header_cache and header_cache[product_id] is None:
            return []
        # 查询并缓存
        header = db.query(BomHeader).filter(
            BomHeader.product_id == product_id,
            BomHeader.status == 'active'
        ).first()
        header_cache[product_id] = header
        if not header:
            return []

    items = db.query(BomItem, Material).join(
        Material, BomItem.child_product_id == Material.id
    ).filter(BomItem.bom_header_id == header.id).order_by(BomItem.item_no).all()

    children = []
    for item, product in items:
        child_has_bom = (product.id in header_cache and header_cache.get(product.id) is not None) or \
                        db.query(BomHeader).filter(
                            BomHeader.product_id == product.id,
                            BomHeader.status == 'active'
                        ).first() is not None
        # 若未在缓存中，预先放入缓存（避免子递归时重复查询）
        if product.id not in header_cache:
            sub_header = db.query(BomHeader).filter(
                BomHeader.product_id == product.id,
                BomHeader.status == 'active'
            ).first()
            header_cache[product.id] = sub_header

        node = {
            "product_id": product.id,
            "product_name": product.product_name,
            "product_code": product.u9_material_code,
            "part_number": product.part_number,
            "specification": product.specification,
            "quantity": float(item.quantity) * quantity,
            "unit": item.unit or product.unit,
            "reference_designator": item.reference_designator,
            "level": level,
            "has_bom": child_has_bom,
            "bom_item_id": item.id,
            "bom_header_id": item.bom_header_id,
            "children": _build_bom_tree_with_cache(
                db, product.id, float(item.quantity) * quantity,
                level + 1, max_level, header_cache
            )
        }
        children.append(node)
    return children


def _explode_bom_with_cache(
    db: Session,
    product_id: int,
    quantity: float,
    level: int,
    max_level: int,
    result: dict,
    visited: Set[int],
    header_cache: Dict[int, BomHeader]
):
    """
    递归展开 BOM，使用 header_cache 提升性能
    """
    if level >= max_level or product_id in visited:
        return
    visited.add(product_id)

    header = header_cache.get(product_id)
    if header is None:
        if product_id not in header_cache:
            header = db.query(BomHeader).filter(
                BomHeader.product_id == product_id,
                BomHeader.status == 'active'
            ).first()
            header_cache[product_id] = header
        if not header:
            return

    items = db.query(BomItem, Material).join(
        Material, BomItem.child_product_id == Material.id
    ).filter(BomItem.bom_header_id == header.id).all()

    for item, product in items:
        needed_qty = float(item.quantity) * quantity
        pid = item.child_product_id
        if pid in result:
            result[pid]["total_quantity"] += needed_qty
        else:
            result[pid] = {
                "product_id": pid,
                "product_name": product.product_name,
                "product_code": product.u9_material_code,
                "part_number": product.part_number,
                "specification": product.specification,
                "unit": item.unit or product.unit,
                "total_quantity": needed_qty,
                "first_level": level,
            }
        _explode_bom_with_cache(db, pid, needed_qty, level + 1, max_level, result, visited, header_cache)


# ============ 固定路径接口（须放在动态路径之前） ============

@router.get("/", response_model=BomHeaderList)
async def list_bom_headers(
    query: BomHeaderQuery = Depends(),
    db: Session = Depends(get_db)
):
    """查询 BOM 列表（支持分页、筛选）"""
    db_query = db.query(BomHeader)

    if query.bom_code:
        db_query = db_query.filter(BomHeader.bom_code.like(f"%{query.bom_code}%"))
    if query.bom_name:
        db_query = db_query.filter(BomHeader.bom_name.like(f"%{query.bom_name}%"))
    if query.product_id:
        db_query = db_query.filter(BomHeader.product_id == query.product_id)
    if query.status:
        db_query = db_query.filter(BomHeader.status == query.status)

    total = db_query.count()
    items = db_query.order_by(BomHeader.id.desc()).offset(
        (query.page - 1) * query.page_size
    ).limit(query.page_size).all()

    return {
        "total": total,
        "items": [_enrich_header(db, h) for h in items]
    }


@router.get("/all")
async def list_all_active_boms(db: Session = Depends(get_db)):
    """获取所有活跃 BOM（用于下拉选择）"""
    headers = db.query(BomHeader).filter(
        BomHeader.status == 'active'
    ).order_by(BomHeader.bom_code).all()

    result = []
    for h in headers:
        product_info = _get_product_info(db, h.product_id) or {}
        result.append({
            "id": h.id,
            "bom_code": h.bom_code,
            "bom_name": h.bom_name,
            "product_id": h.product_id,
            "product_name": product_info.get("product_name"),
            "version": h.version,
        })
    return {"items": result}


@router.get("/stats/summary")
async def get_bom_stats(db: Session = Depends(get_db)):
    """BOM 统计信息"""
    total = db.query(func.count(BomHeader.id)).scalar() or 0
    active = db.query(func.count(BomHeader.id)).filter(BomHeader.status == 'active').scalar() or 0
    draft = db.query(func.count(BomHeader.id)).filter(BomHeader.status == 'draft').scalar() or 0
    archived = db.query(func.count(BomHeader.id)).filter(BomHeader.status == 'archived').scalar() or 0
    total_items = db.query(func.count(BomItem.id)).scalar() or 0

    return {
        "total_boms": total,
        "active_boms": active,
        "draft_boms": draft,
        "archived_boms": archived,
        "total_items": total_items,
    }


@router.get("/explode/{bom_id}")
async def explode_bom(
    bom_id: int,
    quantity: float = Query(1.0, gt=0, description='成品数量'),
    max_level: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """BOM 展开：汇总指定数量下所有层级的物料需求（性能优化版）"""
    header = db.query(BomHeader).filter(BomHeader.id == bom_id).first()
    if not header:
        raise HTTPException(status_code=404, detail="BOM 不存在")

    result = {}
    header_cache = {}
    _explode_bom_with_cache(db, header.product_id, quantity, 1, max_level, result, set(), header_cache)

    items = sorted(result.values(), key=lambda x: x["first_level"])
    return {
        "bom_id": bom_id,
        "bom_code": header.bom_code,
        "quantity": quantity,
        "total_materials": len(items),
        "items": items,
    }


@router.get("/where-used/{product_id}")
async def get_where_used(product_id: int, db: Session = Depends(get_db)):
    """用量反查：查找哪些 BOM 使用了指定产品作为子物料"""
    bom_ids = db.query(BomItem.bom_header_id).filter(
        BomItem.child_product_id == product_id
    ).distinct().subquery()

    headers = db.query(BomHeader).filter(BomHeader.id.in_(bom_ids)).all()

    result = []
    for h in headers:
        product_info = _get_product_info(db, h.product_id) or {}
        result.append({
            "bom_id": h.id,
            "bom_code": h.bom_code,
            "bom_name": h.bom_name,
            "parent_product_id": h.product_id,
            "parent_product_name": product_info.get("product_name"),
            "version": h.version,
            "status": h.status,
        })

    return {"items": result}


@router.post("/items/move")
async def move_bom_item(
    req: BomItemMoveRequest,
    db: Session = Depends(get_db)
):
    """移动 BOM 子项到另一个 BOM（用于 MBOM 编辑器拖拽）"""
    # 校验 item 存在且属于 source_bom
    db_item = db.query(BomItem).filter(
        BomItem.id == req.item_id,
        BomItem.bom_header_id == req.source_bom_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="源 BOM 中不存在该子项")

    # 校验 target_bom 存在
    target_header = db.query(BomHeader).filter(BomHeader.id == req.target_bom_id).first()
    if not target_header:
        raise HTTPException(status_code=404, detail="目标 BOM 不存在")

    # 不能移动到同一个 BOM
    if req.source_bom_id == req.target_bom_id:
        raise HTTPException(status_code=400, detail="源 BOM 和目标 BOM 不能相同")

    # 校验目标 BOM 无重复 child_product_id
    duplicate = db.query(BomItem).filter(
        BomItem.bom_header_id == req.target_bom_id,
        BomItem.child_product_id == db_item.child_product_id
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="目标 BOM 中已存在相同子物料")

    # 循环引用检查
    if _check_circular_ref(db, target_header.product_id, db_item.child_product_id):
        raise HTTPException(status_code=400, detail="移动会导致循环引用")

    # 计算新的 item_no
    max_no = db.query(func.max(BomItem.item_no)).filter(
        BomItem.bom_header_id == req.target_bom_id
    ).scalar() or 0

    db_item.bom_header_id = req.target_bom_id
    db_item.item_no = max_no + 1
    db.commit()
    logger.info(f"移动子项: ID={req.item_id}, {req.source_bom_id} -> {req.target_bom_id}")
    return {"message": "子项已移动", "item_id": req.item_id, "target_bom_id": req.target_bom_id}


# ============ 动态路径接口 ============

@router.get("/{bom_id}", response_model=BomHeaderWithItems)
async def get_bom(bom_id: int, db: Session = Depends(get_db)):
    """获取 BOM 详情（含子项）"""
    return await _get_bom_with_items(bom_id, db)


@router.post("/", response_model=BomHeaderWithItems)
async def create_bom(bom: BomHeaderCreate, db: Session = Depends(get_db)):
    """创建 BOM（可同时包含子项）"""
    # 检查编号唯一性
    existing = db.query(BomHeader).filter(BomHeader.bom_code == bom.bom_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="BOM 编号已存在")

    # 检查产品是否存在
    product = db.query(Material).filter(Material.id == bom.product_id).first()
    if not product:
        raise HTTPException(status_code=400, detail="产品不存在")

    # 预先验证所有子项的循环引用（避免创建一半失败）
    for item_data in bom.items:
        if _check_circular_ref(db, bom.product_id, item_data.child_product_id):
            raise HTTPException(status_code=400, detail=f"循环引用：子物料(ID={item_data.child_product_id})的 BOM 中已包含当前父产品")

    # 创建 BOM 头
    header_data = bom.model_dump(exclude={'items'})
    db_header = BomHeader(**header_data)
    db.add(db_header)
    db.flush()  # 获取 ID

    # 批量添加子项
    for idx, item_data in enumerate(bom.items):
        db_item = BomItem(
            bom_header_id=db_header.id,
            item_no=idx + 1,  # 按传入顺序自动编号
            **item_data.model_dump()
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_header)
    logger.info(f"创建 BOM: {db_header.bom_code}, ID={db_header.id}, 子项数={len(bom.items)}")
    return await _get_bom_with_items(db_header.id, db)


@router.put("/{bom_id}", response_model=BomHeaderDetail)
async def update_bom(bom_id: int, bom: BomHeaderUpdate, db: Session = Depends(get_db)):
    """更新 BOM 主表信息"""
    db_bom = db.query(BomHeader).filter(BomHeader.id == bom_id).first()
    if not db_bom:
        raise HTTPException(status_code=404, detail="BOM 不存在")

    update_data = bom.model_dump(exclude_unset=True)
    if 'bom_code' in update_data and update_data['bom_code'] != db_bom.bom_code:
        existing = db.query(BomHeader).filter(BomHeader.bom_code == update_data['bom_code']).first()
        if existing:
            raise HTTPException(status_code=400, detail="BOM 编号已存在")

    for field, value in update_data.items():
        setattr(db_bom, field, value)

    db.commit()
    db.refresh(db_bom)
    logger.info(f"更新 BOM: {db_bom.bom_code}, ID={bom_id}")
    return _enrich_header(db, db_bom)


@router.delete("/{bom_id}")
async def delete_bom(bom_id: int, db: Session = Depends(get_db)):
    """删除 BOM（主表和所有子项）"""
    db_bom = db.query(BomHeader).filter(BomHeader.id == bom_id).first()
    if not db_bom:
        raise HTTPException(status_code=404, detail="BOM 不存在")

    # 删除所有子项
    db.query(BomItem).filter(BomItem.bom_header_id == bom_id).delete()
    db.delete(db_bom)
    db.commit()
    logger.warning(f"删除 BOM: {db_bom.bom_code}, ID={bom_id}")
    return {"message": f"BOM {db_bom.bom_code} 已删除"}


@router.post("/{bom_id}/activate")
async def activate_bom(bom_id: int, db: Session = Depends(get_db)):
    """激活 BOM（自动归档同产品的其他活跃 BOM，幂等）"""
    bom = db.query(BomHeader).filter(BomHeader.id == bom_id).first()
    if not bom:
        raise HTTPException(status_code=404, detail="BOM 不存在")

    # 如果已经是 active 状态，直接返回成功（幂等）
    if bom.status == 'active':
        return _enrich_header(db, bom)

    # 归档同产品的其他活跃 BOM
    db.query(BomHeader).filter(
        BomHeader.product_id == bom.product_id,
        BomHeader.status == 'active',
        BomHeader.id != bom_id
    ).update({"status": "archived"})

    bom.status = 'active'
    db.commit()
    db.refresh(bom)
    logger.info(f"激活 BOM: {bom.bom_code}, 产品ID={bom.product_id}")
    return _enrich_header(db, bom)


@router.post("/{bom_id}/archive")
async def archive_bom(bom_id: int, db: Session = Depends(get_db)):
    """归档 BOM（幂等）"""
    bom = db.query(BomHeader).filter(BomHeader.id == bom_id).first()
    if not bom:
        raise HTTPException(status_code=404, detail="BOM 不存在")

    if bom.status == 'archived':
        return _enrich_header(db, bom)

    bom.status = 'archived'
    db.commit()
    db.refresh(bom)
    logger.info(f"归档 BOM: {bom.bom_code}")
    return _enrich_header(db, bom)


@router.post("/{bom_id}/copy", response_model=BomHeaderWithItems)
async def copy_bom(bom_id: int, copy_req: BomCopyRequest, db: Session = Depends(get_db)):
    """复制 BOM 到新版本（深拷贝所有子项）"""
    source = db.query(BomHeader).filter(BomHeader.id == bom_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="源 BOM 不存在")

    # 检查新编号唯一性
    existing = db.query(BomHeader).filter(BomHeader.bom_code == copy_req.new_bom_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="新 BOM 编号已存在")

    # 创建新 BOM 头
    new_header = BomHeader(
        bom_code=copy_req.new_bom_code,
        bom_name=copy_req.new_bom_name or f"{source.bom_name} (副本)",
        product_id=source.product_id,
        version=copy_req.new_version or 'V1.0',
        status='draft',
        effective_date=source.effective_date,
        expiry_date=source.expiry_date,
        description=source.description,
    )
    db.add(new_header)
    db.flush()

    # 复制所有子项，保持 item_no 顺序
    source_items = db.query(BomItem).filter(BomItem.bom_header_id == bom_id).order_by(BomItem.item_no).all()
    for item in source_items:
        new_item = BomItem(
            bom_header_id=new_header.id,
            child_product_id=item.child_product_id,
            quantity=item.quantity,
            unit=item.unit,
            reference_designator=item.reference_designator,
            item_no=item.item_no,
            remark=item.remark,
        )
        db.add(new_item)

    db.commit()
    db.refresh(new_header)
    logger.info(f"复制 BOM: 源={source.bom_code} -> 新={new_header.bom_code}")
    return await _get_bom_with_items(new_header.id, db)


@router.get("/{bom_id}/tree")
async def get_bom_tree(
    bom_id: int,
    max_level: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """获取多级 BOM 树（性能优化版，使用缓存）"""
    header = db.query(BomHeader).filter(BomHeader.id == bom_id).first()
    if not header:
        raise HTTPException(status_code=404, detail="BOM 不存在")

    product = db.query(Material).filter(Material.id == header.product_id).first()

    # 构建缓存字典
    header_cache = {}
    root_children = _build_bom_tree_with_cache(
        db, header.product_id, 1.0, 1, max_level, header_cache
    )

    root = {
        "product_id": header.product_id,
        "product_name": product.product_name if product else "未知产品",
        "product_code": product.u9_material_code if product else None,
        "part_number": product.part_number if product else None,
        "specification": product.specification if product else None,
        "quantity": 1.0,
        "unit": product.unit if product else None,
        "reference_designator": None,
        "level": 0,
        "has_bom": True,
        "bom_item_id": None,
        "bom_header_id": header.id,
        "children": root_children
    }
    return root


# ============ BOM 子项 CRUD ============

@router.post("/{bom_id}/items", response_model=BomItemDetail)
async def add_bom_item(bom_id: int, item: BomItemCreate, db: Session = Depends(get_db)):
    """添加 BOM 子项（自动分配 item_no）"""
    header = db.query(BomHeader).filter(BomHeader.id == bom_id).first()
    if not header:
        raise HTTPException(status_code=404, detail="BOM 不存在")

    product = db.query(Material).filter(Material.id == item.child_product_id).first()
    if not product:
        raise HTTPException(status_code=400, detail="子物料产品不存在")

    # 检查重复子物料
    existing = db.query(BomItem).filter(
        BomItem.bom_header_id == bom_id,
        BomItem.child_product_id == item.child_product_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该子物料已存在于此 BOM 中")

    # 循环引用检查
    if _check_circular_ref(db, header.product_id, item.child_product_id):
        raise HTTPException(status_code=400, detail="循环引用：该子物料的 BOM 中已包含当前父产品，无法添加")

    # 计算新的 item_no（当前最大 +1）
    max_no = db.query(func.max(BomItem.item_no)).filter(BomItem.bom_header_id == bom_id).scalar() or 0
    db_item = BomItem(
        bom_header_id=bom_id,
        item_no=max_no + 1,
        **item.model_dump()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    logger.info(f"添加子项: BOM ID={bom_id}, 物料ID={item.child_product_id}, 数量={item.quantity}")
    return _enrich_item(db, db_item)


@router.put("/{bom_id}/items/{item_id}", response_model=BomItemDetail)
async def update_bom_item(bom_id: int, item_id: int, item: BomItemUpdate, db: Session = Depends(get_db)):
    """更新 BOM 子项"""
    db_item = db.query(BomItem).filter(
        BomItem.id == item_id,
        BomItem.bom_header_id == bom_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="BOM 子项不存在")

    update_data = item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    logger.info(f"更新子项: ID={item_id}, BOM ID={bom_id}")
    return _enrich_item(db, db_item)


@router.delete("/{bom_id}/items/{item_id}")
async def delete_bom_item(bom_id: int, item_id: int, db: Session = Depends(get_db)):
    """删除 BOM 子项（其余项的 item_no 会自动重排？此处不自动重排，留给前端调用 reorder）"""
    db_item = db.query(BomItem).filter(
        BomItem.id == item_id,
        BomItem.bom_header_id == bom_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="BOM 子项不存在")

    db.delete(db_item)
    db.commit()
    logger.info(f"删除子项: ID={item_id}, BOM ID={bom_id}")
    return {"message": "BOM 子项已删除"}


# ============ 拖拽排序 API（适配 Vue 拖拽组件） ============

@router.post("/{bom_id}/items/reorder")
async def reorder_bom_items(
    bom_id: int,
    req: BomItemReorderRequest,
    db: Session = Depends(get_db)
):
    """
    批量重排 BOM 子项的显示顺序（item_no）
    请求体格式: {"item_order": [item_id1, item_id2, ...]}
    根据数组顺序依次设置 item_no = 1, 2, 3, ...
    用于前端拖拽排序后的保存
    """
    header = db.query(BomHeader).filter(BomHeader.id == bom_id).first()
    if not header:
        raise HTTPException(status_code=404, detail="BOM 不存在")

    item_ids = req.item_order
    if not item_ids:
        raise HTTPException(status_code=400, detail="item_order 不能为空")

    # 验证所有 item_id 是否属于该 BOM
    db_items = db.query(BomItem).filter(
        BomItem.bom_header_id == bom_id,
        BomItem.id.in_(item_ids)
    ).all()
    if len(db_items) != len(item_ids):
        raise HTTPException(status_code=400, detail="部分 item_id 不存在或不属于该 BOM")

    # 批量更新 item_no
    for idx, item_id in enumerate(item_ids, start=1):
        db.query(BomItem).filter(BomItem.id == item_id).update({"item_no": idx})

    db.commit()
    logger.info(f"重排 BOM 子项顺序: BOM ID={bom_id}, 共 {len(item_ids)} 项")
    return {"message": "顺序已更新", "count": len(item_ids)}