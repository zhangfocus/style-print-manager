from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/restrictions", tags=["限定规则"])
bans_router = APIRouter(prefix="/api/bans", tags=["全禁款式"])


# ── 限定规则（StylePositionRule）─────────────────────────

@router.get("/", response_model=List[schemas.StylePositionRuleOut])
def list_rules(
    style_id: Optional[int] = Query(None),
    position_id: Optional[int] = Query(None),
    print_code: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 500,
    db: Session = Depends(get_db),
):
    return crud.get_style_position_rules(db, skip=skip, limit=limit,
                                         style_id=style_id, position_id=position_id,
                                         print_code=print_code)


@router.get("/{rule_id}", response_model=schemas.StylePositionRuleOut)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    obj = crud.get_style_position_rule(db, rule_id)
    if not obj:
        raise HTTPException(status_code=404, detail="规则不存在")
    return obj


@router.post("/", response_model=schemas.StylePositionRuleOut, status_code=201)
def create_rule(data: schemas.StylePositionRuleCreate, db: Session = Depends(get_db)):
    if not crud.get_style(db, data.style_id):
        raise HTTPException(400, f"款式 ID {data.style_id} 不存在")
    if not crud.get_position(db, data.position_id):
        raise HTTPException(400, f"位置 ID {data.position_id} 不存在")
    if crud.get_style_position_rule_by_key(db, data.style_id, data.position_id):
        raise HTTPException(400, "该款式+位置组合已存在")
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
