from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from . import models, schemas


# ───── Style CRUD ─────
def get_styles(db: Session, skip: int = 0, limit: int = 200, keyword: str = ""):
    q = db.query(models.Style)
    if keyword:
        q = q.filter(or_(
            models.Style.code.contains(keyword),
            models.Style.product_code.contains(keyword),
            models.Style.product_category.contains(keyword),
        ))
    return q.offset(skip).limit(limit).all()


def get_style(db: Session, style_id: int):
    return db.query(models.Style).filter(models.Style.id == style_id).first()


def get_style_by_code(db: Session, code: str):
    return db.query(models.Style).filter(models.Style.code == code).first()


def create_style(db: Session, data: schemas.StyleCreate):
    obj = models.Style(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_style(db: Session, style_id: int, data: schemas.StyleUpdate):
    obj = get_style(db, style_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_style(db: Session, style_id: int):
    obj = get_style(db, style_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj


# ───── Print CRUD ─────
def get_prints(db: Session, skip: int = 0, limit: int = 200, keyword: str = ""):
    q = db.query(models.Print)
    if keyword:
        q = q.filter(or_(
            models.Print.code.contains(keyword),
            models.Print.name.contains(keyword),
            models.Print.craft_attr.contains(keyword),
        ))
    return q.offset(skip).limit(limit).all()


def get_print(db: Session, print_id: int):
    return db.query(models.Print).filter(models.Print.id == print_id).first()


def get_print_by_code(db: Session, code: str):
    return db.query(models.Print).filter(models.Print.code == code).first()


def create_print(db: Session, data: schemas.PrintCreate):
    obj = models.Print(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_print(db: Session, print_id: int, data: schemas.PrintUpdate):
    obj = get_print(db, print_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_print(db: Session, print_id: int):
    obj = get_print(db, print_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj


# ───── Position CRUD ─────
def get_positions(db: Session, skip: int = 0, limit: int = 200, keyword: str = ""):
    q = db.query(models.Position)
    if keyword:
        q = q.filter(or_(models.Position.name.contains(keyword), models.Position.code.contains(keyword)))
    return q.offset(skip).limit(limit).all()


def get_position(db: Session, position_id: int):
    return db.query(models.Position).filter(models.Position.id == position_id).first()


def get_position_by_code(db: Session, code: str):
    return db.query(models.Position).filter(models.Position.code == code).first()


def get_position_by_name(db: Session, name: str):
    return db.query(models.Position).filter(models.Position.name == name).first()


def create_position(db: Session, data: schemas.PositionCreate):
    obj = models.Position(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_position(db: Session, position_id: int, data: schemas.PositionUpdate):
    obj = get_position(db, position_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_position(db: Session, position_id: int):
    obj = get_position(db, position_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj


# ───── StylePositionRule CRUD ─────
def get_style_position_rules(
    db: Session,
    skip: int = 0,
    limit: int = 500,
    style_id: Optional[int] = None,
    position_id: Optional[int] = None,
    print_code: Optional[str] = None,
):
    from sqlalchemy.orm import joinedload
    q = db.query(models.StylePositionRule).options(
        joinedload(models.StylePositionRule.style),
        joinedload(models.StylePositionRule.position),
    )
    if style_id:
        q = q.filter(models.StylePositionRule.style_id == style_id)
    if position_id:
        q = q.filter(models.StylePositionRule.position_id == position_id)
    if print_code:
        # 仅当印花编码确实存在于印花库时，才把 allowed_prints IS NULL（不限）的行纳入结果；
        # 若印花不存在，只返回明确列出该编码的行（通常为空）。
        print_exists = db.query(models.Print.id).filter(models.Print.code == print_code).first() is not None
        if print_exists:
            q = q.filter(
                or_(
                    models.StylePositionRule.allowed_prints == None,
                    models.StylePositionRule.allowed_prints.contains(print_code),
                )
            )
        else:
            q = q.filter(models.StylePositionRule.allowed_prints.contains(print_code))
    return q.order_by(models.StylePositionRule.created_at.desc()).offset(skip).limit(limit).all()


def get_style_position_rule(db: Session, rule_id: int):
    from sqlalchemy.orm import joinedload
    return db.query(models.StylePositionRule).options(
        joinedload(models.StylePositionRule.style),
        joinedload(models.StylePositionRule.position),
    ).filter(models.StylePositionRule.id == rule_id).first()


def get_style_position_rule_by_key(db: Session, style_id: int, position_id: int):
    return db.query(models.StylePositionRule).filter(
        models.StylePositionRule.style_id == style_id,
        models.StylePositionRule.position_id == position_id,
    ).first()


def create_style_position_rule(db: Session, data: schemas.StylePositionRuleCreate):
    obj = models.StylePositionRule(**data.model_dump())
    db.add(obj)
    db.commit()
    return get_style_position_rule(db, obj.id)


def update_style_position_rule(db: Session, rule_id: int, data: schemas.StylePositionRuleUpdate):
    obj = db.query(models.StylePositionRule).filter(models.StylePositionRule.id == rule_id).first()
    if not obj:
        return None
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    return get_style_position_rule(db, rule_id)


def delete_style_position_rule(db: Session, rule_id: int):
    obj = db.query(models.StylePositionRule).filter(models.StylePositionRule.id == rule_id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj


# ───── StyleBan CRUD ─────
def get_style_bans(db: Session, skip: int = 0, limit: int = 500, keyword: Optional[str] = None):
    from sqlalchemy.orm import joinedload
    q = db.query(models.StyleBan).options(joinedload(models.StyleBan.style))
    if keyword:
        q = q.join(models.Style).filter(models.Style.code.contains(keyword))
    return q.offset(skip).limit(limit).all()


def get_style_ban(db: Session, ban_id: int):
    from sqlalchemy.orm import joinedload
    return db.query(models.StyleBan).options(
        joinedload(models.StyleBan.style)
    ).filter(models.StyleBan.id == ban_id).first()


def get_style_ban_by_style_id(db: Session, style_id: int):
    return db.query(models.StyleBan).filter(models.StyleBan.style_id == style_id).first()


def create_style_ban(db: Session, data: schemas.StyleBanCreate):
    obj = models.StyleBan(**data.model_dump())
    db.add(obj)
    db.commit()
    return get_style_ban(db, obj.id)


def update_style_ban(db: Session, ban_id: int, data: schemas.StyleBanUpdate):
    obj = db.query(models.StyleBan).filter(models.StyleBan.id == ban_id).first()
    if not obj:
        return None
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    return get_style_ban(db, ban_id)


def delete_style_ban(db: Session, ban_id: int):
    obj = db.query(models.StyleBan).filter(models.StyleBan.id == ban_id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj
