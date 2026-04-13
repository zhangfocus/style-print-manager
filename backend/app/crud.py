from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional, List
from . import models, schemas


# ───── Style CRUD ─────
def get_styles(db: Session, skip: int = 0, limit: int = 200, keyword: str = ""):
    q = db.query(models.Style)
    if keyword:
        q = q.filter(or_(models.Style.name.contains(keyword), models.Style.code.contains(keyword)))
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
        q = q.filter(or_(models.Print.name.contains(keyword), models.Print.code.contains(keyword)))
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


# ───── Restriction CRUD ─────
def get_restrictions(
    db: Session,
    skip: int = 0,
    limit: int = 500,
    style_id: Optional[int] = None,
    position_id: Optional[int] = None,
    print_id: Optional[int] = None,
):
    q = db.query(models.Restriction).options(
        joinedload(models.Restriction.style),
        joinedload(models.Restriction.position),
        joinedload(models.Restriction.print_item),
    )
    if style_id:
        q = q.filter(models.Restriction.style_id == style_id)
    if position_id:
        q = q.filter(models.Restriction.position_id == position_id)
    if print_id:
        q = q.filter(models.Restriction.print_id == print_id)
    return q.offset(skip).limit(limit).all()


def get_restriction(db: Session, restriction_id: int):
    return db.query(models.Restriction).options(
        joinedload(models.Restriction.style),
        joinedload(models.Restriction.position),
        joinedload(models.Restriction.print_item),
    ).filter(models.Restriction.id == restriction_id).first()


def create_restriction(db: Session, data: schemas.RestrictionCreate):
    obj = models.Restriction(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return get_restriction(db, obj.id)


def update_restriction(db: Session, restriction_id: int, data: schemas.RestrictionUpdate):
    obj = db.query(models.Restriction).filter(models.Restriction.id == restriction_id).first()
    if not obj:
        return None
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    return get_restriction(db, obj.id)


def delete_restriction(db: Session, restriction_id: int):
    obj = db.query(models.Restriction).filter(models.Restriction.id == restriction_id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj
