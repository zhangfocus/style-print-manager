from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/restrictions", tags=["限定规则"])
bans_router = APIRouter(prefix="/api/bans", tags=["全禁款式"])


# ── 限定规则（StylePositionRule）─────────────────────────

@router.get("/")
def list_rules(
    style_id: Optional[int] = Query(None),
    position_id: Optional[int] = Query(None),
    print_code: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 500,
    db: Session = Depends(get_db),
):
    rules = crud.get_style_position_rules(db, skip=skip, limit=limit,
                                         style_id=style_id, position_id=position_id,
                                         print_code=print_code)
    # 手动构造响应以包含动态字段
    result = []
    for rule in rules:
        rule_dict = {
            "id": rule.id,
            "rule_type": rule.rule_type,
            "style_id": rule.style_id,
            "position_id": rule.position_id,
            "print_code": rule.print_code,
            "allowed_prints": rule.allowed_prints,
            "allowed_styles": rule.allowed_styles,
            "allowed_style_positions": rule.allowed_style_positions,
            "allowed_style_positions_display": getattr(rule, 'allowed_style_positions_display', None),
            "is_active": rule.is_active,
            "remark": rule.remark,
            "created_at": rule.created_at,
            "updated_at": rule.updated_at,
            "style": schemas.StyleOut.model_validate(rule.style) if rule.style else None,
            "position": schemas.PositionOut.model_validate(rule.position) if rule.position else None,
        }
        result.append(rule_dict)
    return result


@router.get("/query")
def query_allowed_prints(
    style_id: int = Query(...),
    position_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """查询指定款式+位置允许的印花列表（三维度交集）"""
    allowed = crud.query_allowed_prints(db, style_id, position_id)
    return {"style_id": style_id, "position_id": position_id, "allowed_prints": allowed}


@router.get("/{rule_id}", response_model=schemas.StylePositionRuleOut)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    obj = crud.get_style_position_rule(db, rule_id)
    if not obj:
        raise HTTPException(status_code=404, detail="规则不存在")
    return obj


@router.post("/", response_model=schemas.StylePositionRuleOut, status_code=201)
def create_rule(data: schemas.StylePositionRuleCreate, db: Session = Depends(get_db)):
    # 根据规则类型验证必填字段
    if data.rule_type == 'style_position':
        if not data.style_id or not data.position_id:
            raise HTTPException(400, "款式位置规则需要 style_id 和 position_id")
        if not crud.get_style(db, data.style_id):
            raise HTTPException(400, f"款式 ID {data.style_id} 不存在")
        if not crud.get_position(db, data.position_id):
            raise HTTPException(400, f"位置 ID {data.position_id} 不存在")
        # 检查是否已存在
        if crud.get_style_position_rule_by_key(db, data.style_id, data.position_id):
            raise HTTPException(400, "该款式+位置组合已存在")

    elif data.rule_type == 'position_print':
        if not data.position_id or not data.print_code:
            raise HTTPException(400, "位置印花规则需要 position_id 和 print_code")
        if not crud.get_position(db, data.position_id):
            raise HTTPException(400, f"位置 ID {data.position_id} 不存在")
        if not crud.get_print_by_code(db, data.print_code):
            raise HTTPException(400, f"印花 {data.print_code} 不存在")

    elif data.rule_type == 'print_restriction':
        if not data.print_code:
            raise HTTPException(400, "印花限定规则需要 print_code")
        if not crud.get_print_by_code(db, data.print_code):
            raise HTTPException(400, f"印花 {data.print_code} 不存在")

    elif data.rule_type == 'style_ban':
        if not data.style_id:
            raise HTTPException(400, "款式全禁规则需要 style_id")
        if not crud.get_style(db, data.style_id):
            raise HTTPException(400, f"款式 ID {data.style_id} 不存在")
        # 检查是否已存在
        if crud.get_style_ban_by_style_id(db, data.style_id):
            raise HTTPException(400, "该款式已在全禁列表中")

    else:
        raise HTTPException(400, f"未知的规则类型: {data.rule_type}")

    return crud.create_style_position_rule(db, data)


@router.put("/{rule_id}", response_model=schemas.StylePositionRuleOut)
def update_rule(rule_id: int, data: schemas.StylePositionRuleUpdate, db: Session = Depends(get_db)):
    obj = crud.update_style_position_rule(db, rule_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="规则不存在")
    return obj


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    obj = crud.delete_style_position_rule(db, rule_id)
    if not obj:
        raise HTTPException(status_code=404, detail="规则不存在")
    return {"message": "删除成功"}


# ── 全禁款式（StyleBan）───────────────────────────────────

@bans_router.get("/", response_model=List[schemas.StyleBanOut])
def list_bans(
    keyword: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 500,
    db: Session = Depends(get_db),
):
    return crud.get_style_bans(db, skip=skip, limit=limit, keyword=keyword)


@bans_router.get("/{ban_id}", response_model=schemas.StyleBanOut)
def get_ban(ban_id: int, db: Session = Depends(get_db)):
    obj = crud.get_style_ban(db, ban_id)
    if not obj:
        raise HTTPException(status_code=404, detail="全禁记录不存在")
    return obj


@bans_router.post("/", response_model=schemas.StyleBanOut, status_code=201)
def create_ban(data: schemas.StyleBanCreate, db: Session = Depends(get_db)):
    if not crud.get_style(db, data.style_id):
        raise HTTPException(400, f"款式 ID {data.style_id} 不存在")
    if crud.get_style_ban_by_style_id(db, data.style_id):
        raise HTTPException(400, "该款式已在全禁列表中")
    return crud.create_style_ban(db, data)


@bans_router.put("/{ban_id}", response_model=schemas.StyleBanOut)
def update_ban(ban_id: int, data: schemas.StyleBanUpdate, db: Session = Depends(get_db)):
    obj = crud.update_style_ban(db, ban_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="全禁记录不存在")
    return obj


@bans_router.delete("/{ban_id}")
def delete_ban(ban_id: int, db: Session = Depends(get_db)):
    obj = crud.delete_style_ban(db, ban_id)
    if not obj:
        raise HTTPException(status_code=404, detail="全禁记录不存在")
    return {"message": "删除成功"}
