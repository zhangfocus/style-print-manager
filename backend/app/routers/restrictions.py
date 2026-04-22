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
    style_code: Optional[str] = Query(None),
    position_id: Optional[int] = Query(None),
    print_code: Optional[str] = Query(None),
    rule_type: Optional[int] = Query(None),
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    from .. import models

    result_data = crud.get_style_position_rules(
        db, page=page, page_size=page_size,
        style_code=style_code, position_id=position_id,
        print_code=print_code, rule_type=rule_type
    )
    rules = result_data["items"]

    # 批量收集所有需要查询的 ID
    all_print_ids = set()
    all_style_ids = set()
    for rule in rules:
        if rule.print_ids:
            all_print_ids.update(int(pid.strip()) for pid in rule.print_ids.split(',') if pid.strip())
        if rule.style_ids:
            all_style_ids.update(int(sid.strip()) for sid in rule.style_ids.split(',') if sid.strip())

    # 批量查询
    prints_map = {}
    if all_print_ids:
        prints = db.query(models.Print).filter(models.Print.id.in_(all_print_ids)).all()
        prints_map = {p.id: p.code for p in prints}

    styles_map = {}
    if all_style_ids:
        styles = db.query(models.Style).filter(models.Style.id.in_(all_style_ids)).all()
        styles_map = {s.id: s.code for s in styles}

    # 构造响应
    result = []
    for rule in rules:
        prints_display = None
        if rule.print_ids:
            print_ids = [int(pid.strip()) for pid in rule.print_ids.split(',') if pid.strip()]
            print_names = [prints_map[pid] for pid in print_ids if pid in prints_map]
            if print_names:
                prints_display = ', '.join(print_names)

        styles_display = None
        if rule.style_ids:
            style_ids = [int(sid.strip()) for sid in rule.style_ids.split(',') if sid.strip()]
            style_names = [styles_map[sid] for sid in style_ids if sid in styles_map]
            if style_names:
                styles_display = ', '.join(style_names)

        rule_dict = {
            "id": rule.id,
            "rule_type": rule.rule_type,
            "position_id": rule.position_id,
            "style_ids": rule.style_ids,
            "print_ids": rule.print_ids,
            "print_ids_display": prints_display,
            "style_ids_display": styles_display,
            "is_active": rule.is_active,
            "created_at": rule.created_at,
            "updated_at": rule.updated_at,
            "position": schemas.PositionOut.model_validate(rule.position) if rule.position else None,
        }
        result.append(rule_dict)

    return {
        "items": result,
        "total": result_data["total"],
        "page": result_data["page"],
        "page_size": result_data["page_size"]
    }


@router.get("/{rule_id}")
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    from .. import models

    obj = crud.get_style_position_rule(db, rule_id)
    if not obj:
        raise HTTPException(status_code=404, detail="规则不存在")

    # 转换 ID 为 code 用于显示
    prints_display = None
    if obj.print_ids:
        print_ids = [int(pid.strip()) for pid in obj.print_ids.split(',') if pid.strip()]
        prints = db.query(models.Print).filter(models.Print.id.in_(print_ids)).all()
        prints_display = ', '.join([p.code for p in prints])

    styles_display = None
    if obj.style_ids:
        style_ids = [int(sid.strip()) for sid in obj.style_ids.split(',') if sid.strip()]
        styles = db.query(models.Style).filter(models.Style.id.in_(style_ids)).all()
        styles_display = ', '.join([s.code for s in styles])

    return {
        "id": obj.id,
        "rule_type": obj.rule_type,
        "position_id": obj.position_id,
        "style_ids": obj.style_ids,
        "print_ids": obj.print_ids,
        "print_ids_display": prints_display,
        "style_ids_display": styles_display,
        "is_active": obj.is_active,
        "created_at": obj.created_at,
        "updated_at": obj.updated_at,
        "position": schemas.PositionOut.model_validate(obj.position) if obj.position else None,
    }


@router.post("/", status_code=201)
def create_rule(data: schemas.StylePositionRuleCreate, db: Session = Depends(get_db)):
    try:
        # 根据规则类型验证必填字段
        if data.rule_type == 3:  # style_position
            if not data.style_codes or not data.position_code:
                raise HTTPException(400, "款式位置规则需要 style_codes 和 position_code")
        elif data.rule_type == 2:  # position_restriction
            if not data.position_code or not data.style_codes or not data.print_codes:
                raise HTTPException(400, "位置限定规则需要 position_code、style_codes 和 print_codes")
        elif data.rule_type == 1:  # style_ban
            if not data.style_codes:
                raise HTTPException(400, "款式全禁规则需要 style_codes")
        else:
            raise HTTPException(400, f"未知的规则类型: {data.rule_type}")

        obj = crud.create_style_position_rule(db, data)
        return {"id": obj.id, "message": "创建成功"}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.put("/{rule_id}")
def update_rule(rule_id: int, data: schemas.StylePositionRuleUpdate, db: Session = Depends(get_db)):
    try:
        obj = crud.update_style_position_rule(db, rule_id, data)
        if not obj:
            raise HTTPException(status_code=404, detail="规则不存在")
        return {"id": obj.id, "message": "更新成功"}
    except ValueError as e:
        raise HTTPException(400, str(e))


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
