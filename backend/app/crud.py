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
    """
    查询限定规则（支持多种规则类型）
    注意：此函数返回原始规则记录，不做交集计算
    """
    from sqlalchemy.orm import joinedload
    q = db.query(models.StylePositionRule).options(
        joinedload(models.StylePositionRule.style),
        joinedload(models.StylePositionRule.position),
    )

    # 按维度过滤
    if style_id:
        q = q.filter(models.StylePositionRule.style_id == style_id)
    if position_id:
        q = q.filter(models.StylePositionRule.position_id == position_id)
    if print_code:
        # 印花过滤：匹配 print_code 字段或 allowed_prints 中包含该编码
        q = q.filter(
            or_(
                models.StylePositionRule.print_code == print_code,
                models.StylePositionRule.allowed_prints.contains(print_code),
            )
        )

    rules = q.order_by(models.StylePositionRule.created_at.desc()).offset(skip).limit(limit).all()

    # 为每条规则计算 allowed_style_positions_display
    for rule in rules:
        if rule.allowed_style_positions:
            display_parts = []
            for pair in rule.allowed_style_positions.split(','):
                if ':' in pair:
                    sid, pid = pair.split(':')
                    style = db.query(models.Style).filter_by(id=int(sid)).first()
                    position = db.query(models.Position).filter_by(id=int(pid)).first()
                    if style and position:
                        display_parts.append(f"{style.code}:{position.name}")
            rule.allowed_style_positions_display = ', '.join(display_parts) if display_parts else rule.allowed_style_positions
        else:
            rule.allowed_style_positions_display = None

    return rules


def query_allowed_prints(
    db: Session,
    style_id: int,
    position_id: int
) -> list[str]:
    """
    查询某款式在某位置可以贴哪些印花
    逻辑：三个维度的约束取交集
    """
    # 0. 获取所有印花编码
    all_prints = {p.code for p in db.query(models.Print).all()}

    # 1. 检查款式是否全禁
    style_ban = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 'style_ban',
        models.StylePositionRule.style_id == style_id,
        models.StylePositionRule.is_active == True
    ).first()

    if style_ban:
        return []

    # 2. 款式+位置维度（款式视角）
    style_pos_rule = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 'style_position',
        models.StylePositionRule.style_id == style_id,
        models.StylePositionRule.position_id == position_id,
        models.StylePositionRule.is_active == True
    ).first()

    if style_pos_rule:
        if style_pos_rule.allowed_prints is None:
            set_a = all_prints  # 不限
        else:
            set_a = set(style_pos_rule.allowed_prints.split(','))
    else:
        set_a = all_prints  # 无规则 = 不限

    # 3. 位置+印花维度（位置视角）
    position_print_rules = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 'position_print',
        models.StylePositionRule.position_id == position_id,
        models.StylePositionRule.is_active == True
    ).all()

    if position_print_rules:
        set_b = set()
        for rule in position_print_rules:
            # 检查当前款式是否在该印花的款式白名单中
            if rule.allowed_styles:
                allowed_style_ids = [int(x) for x in rule.allowed_styles.split(',')]
                if style_id in allowed_style_ids:
                    set_b.add(rule.print_code)
        # 如果 set_b 为空，说明该位置的所有印花规则都不包含当前款式，视为该维度不限
        if not set_b:
            set_b = all_prints
    else:
        set_b = all_prints  # 无规则 = 不限

    # 4. 印花维度（印花视角）
    print_restriction_rules = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 'print_restriction',
        models.StylePositionRule.is_active == True
    ).all()

    set_c = all_prints.copy()
    for rule in print_restriction_rules:
        # 解析允许的款式位置组合
        if rule.allowed_style_positions:
            allowed_combos = []
            for combo_str in rule.allowed_style_positions.split(','):
                parts = combo_str.split(':')
                if len(parts) == 2:
                    allowed_combos.append((int(parts[0]), int(parts[1])))

            # 如果当前组合不在白名单中，该印花被禁止
            if (style_id, position_id) not in allowed_combos:
                set_c.discard(rule.print_code)

    # 5. 取三个维度的交集
    result = set_a & set_b & set_c

    return sorted(list(result))


def get_style_position_rule(db: Session, rule_id: int):
    from sqlalchemy.orm import joinedload
    return db.query(models.StylePositionRule).options(
        joinedload(models.StylePositionRule.style),
        joinedload(models.StylePositionRule.position),
    ).filter(models.StylePositionRule.id == rule_id).first()


def get_style_position_rule_by_key(db: Session, style_id: int, position_id: int):
    """查询 style_position 类型的规则"""
    return db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 'style_position',
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


# ───── StyleBan CRUD (兼容旧接口，实际使用 StylePositionRule) ─────
def get_style_bans(db: Session, skip: int = 0, limit: int = 500, keyword: Optional[str] = None):
    from sqlalchemy.orm import joinedload
    q = db.query(models.StylePositionRule).options(
        joinedload(models.StylePositionRule.style)
    ).filter(models.StylePositionRule.rule_type == 'style_ban')
    if keyword:
        q = q.join(models.Style).filter(models.Style.code.contains(keyword))
    return q.offset(skip).limit(limit).all()


def get_style_ban(db: Session, ban_id: int):
    from sqlalchemy.orm import joinedload
    return db.query(models.StylePositionRule).options(
        joinedload(models.StylePositionRule.style)
    ).filter(
        models.StylePositionRule.rule_type == 'style_ban',
        models.StylePositionRule.id == ban_id
    ).first()


def get_style_ban_by_style_id(db: Session, style_id: int):
    return db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 'style_ban',
        models.StylePositionRule.style_id == style_id
    ).first()


def create_style_ban(db: Session, data: schemas.StyleBanCreate):
    obj = models.StylePositionRule(
        rule_type='style_ban',
        style_id=data.style_id,
        remark=data.remark
    )
    db.add(obj)
    db.commit()
    return get_style_ban(db, obj.id)


def update_style_ban(db: Session, ban_id: int, data: schemas.StyleBanUpdate):
    obj = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 'style_ban',
        models.StylePositionRule.id == ban_id
    ).first()
    if not obj:
        return None
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    return get_style_ban(db, ban_id)


def delete_style_ban(db: Session, ban_id: int):
    obj = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 'style_ban',
        models.StylePositionRule.id == ban_id
    ).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj
