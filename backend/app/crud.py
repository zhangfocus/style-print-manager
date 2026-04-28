from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from . import models, schemas


def _parse_bool(value: Optional[str]):
    if value is None or value == "":
        return None
    return value.lower() in {"1", "true", "yes", "on"}


def _apply_keyword(q, model, keyword: str, search_field: str, default_fields: tuple[str, ...], allowed_fields: tuple[str, ...]):
    if not keyword:
        return q
    if search_field and search_field != "all" and search_field in allowed_fields:
        return q.filter(getattr(model, search_field).contains(keyword))
    return q.filter(or_(*(getattr(model, field).contains(keyword) for field in default_fields)))


def _apply_exact_filters(q, model, filters: dict, filter_fields: tuple[str, ...]):
    for field in filter_fields:
        value = filters.get(field)
        if value is None or value == "":
            continue
        column = getattr(model, field)
        if field == "is_active":
            q = q.filter(column == _parse_bool(str(value)))
        else:
            q = q.filter(column == value)
    return q


def _get_filter_options(db: Session, model, option_fields: tuple[str, ...], filters: dict):
    options = {}
    for field in option_fields:
        q = db.query(getattr(model, field)).distinct()
        other_filters = {key: value for key, value in filters.items() if key != field}
        q = _apply_exact_filters(q, model, other_filters, option_fields)
        values = [row[0] for row in q.order_by(getattr(model, field)).all() if row[0] not in (None, "")]
        options[field] = values
    return options


# ───── Style CRUD ─────
STYLE_DEFAULT_SEARCH_FIELDS = ("code", "product_code", "product_category")
STYLE_SEARCH_FIELDS = (
    "code", "product_code", "brand_attr", "attr", "gender", "season", "category",
    "product_category", "virtual_category", "colors_active", "sizes", "printable_area", "fabric_name",
)
STYLE_FILTER_FIELDS = ("is_active", "year", "gender", "season", "category", "product_category", "brand_attr", "attr", "virtual_category")


def get_styles(db: Session, page: int = 1, page_size: int = 10, keyword: str = "", search_field: str = "all", filters: Optional[dict] = None):
    q = db.query(models.Style)
    q = _apply_keyword(q, models.Style, keyword, search_field, STYLE_DEFAULT_SEARCH_FIELDS, STYLE_SEARCH_FIELDS)
    q = _apply_exact_filters(q, models.Style, filters or {}, STYLE_FILTER_FIELDS)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_style_filter_options(db: Session, filters: Optional[dict] = None):
    return _get_filter_options(db, models.Style, STYLE_FILTER_FIELDS, filters or {})


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
PRINT_DEFAULT_SEARCH_FIELDS = ("code", "name", "craft_attr")
PRINT_SEARCH_FIELDS = (
    "code", "name", "pattern_size", "pattern_spec", "craft_attr", "zwx_style_code",
    "jwco_style_code", "city_style_code", "tangshi_style_code", "description",
)
PRINT_FILTER_FIELDS = ("is_active", "pattern_size", "pattern_spec", "craft_attr")


def get_prints(db: Session, page: int = 1, page_size: int = 10, keyword: str = "", search_field: str = "all", filters: Optional[dict] = None):
    q = db.query(models.Print)
    q = _apply_keyword(q, models.Print, keyword, search_field, PRINT_DEFAULT_SEARCH_FIELDS, PRINT_SEARCH_FIELDS)
    q = _apply_exact_filters(q, models.Print, filters or {}, PRINT_FILTER_FIELDS)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_print_filter_options(db: Session, filters: Optional[dict] = None):
    return _get_filter_options(db, models.Print, PRINT_FILTER_FIELDS, filters or {})


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
POSITION_DEFAULT_SEARCH_FIELDS = ("name", "code")
POSITION_SEARCH_FIELDS = ("code", "name", "area", "description")
POSITION_FILTER_FIELDS = ("is_active", "area")


def get_positions(db: Session, page: int = 1, page_size: int = 10, keyword: str = "", search_field: str = "all", filters: Optional[dict] = None):
    q = db.query(models.Position)
    q = _apply_keyword(q, models.Position, keyword, search_field, POSITION_DEFAULT_SEARCH_FIELDS, POSITION_SEARCH_FIELDS)
    q = _apply_exact_filters(q, models.Position, filters or {}, POSITION_FILTER_FIELDS)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_position_filter_options(db: Session, filters: Optional[dict] = None):
    return _get_filter_options(db, models.Position, POSITION_FILTER_FIELDS, filters or {})


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
    page: int = 1,
    page_size: int = 10,
    style_code: Optional[str] = None,
    position_id: Optional[int] = None,
    print_code: Optional[str] = None,
    rule_type: Optional[int] = None,
):
    """
    查询限定规则（支持多种规则类型）
    新结构：使用 FIND_IN_SET 查询 Text 字段
    """
    from sqlalchemy.orm import joinedload
    from sqlalchemy import text

    q = db.query(models.StylePositionRule).options(
        joinedload(models.StylePositionRule.position),
    )

    # 按维度过滤
    if style_code:
        # 先查询款式ID
        style = get_style_by_code(db, style_code)
        if style:
            q = q.filter(text(f"FIND_IN_SET({style.id}, style_ids) > 0"))

    if position_id:
        q = q.filter(models.StylePositionRule.position_id == position_id)

    if print_code:
        # 先查询印花ID
        print_obj = get_print_by_code(db, print_code)
        if print_obj:
            q = q.filter(text(f"FIND_IN_SET({print_obj.id}, print_ids) > 0"))

    if rule_type:
        q = q.filter(models.StylePositionRule.rule_type == rule_type)

    q = q.order_by(models.StylePositionRule.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_style_position_rule(db: Session, rule_id: int):
    from sqlalchemy.orm import joinedload
    return db.query(models.StylePositionRule).options(
        joinedload(models.StylePositionRule.position),
    ).filter(models.StylePositionRule.id == rule_id).first()


def _parse_id_csv(value: Optional[str]) -> Optional[set[int]]:
    if not value:
        return None
    ids = {int(item.strip()) for item in value.split(',') if item.strip()}
    return ids or None


def _format_id_csv(ids: Optional[set[int]]) -> Optional[str]:
    if ids is None:
        return None
    return ",".join(str(item) for item in sorted(ids)) or None


def _merge_nullable_id_csv(existing: Optional[str], incoming: Optional[str]) -> Optional[str]:
    # NULL means unrestricted. If either side is unrestricted, keep it unrestricted.
    existing_ids = _parse_id_csv(existing)
    incoming_ids = _parse_id_csv(incoming)
    if existing_ids is None or incoming_ids is None:
        return None
    return _format_id_csv(existing_ids | incoming_ids)


def _append_id_csv(existing: Optional[str], incoming: Optional[str]) -> Optional[str]:
    # For adding to an existing rule, an empty incoming list means "nothing new".
    incoming_ids = _parse_id_csv(incoming)
    if incoming_ids is None:
        return existing
    existing_ids = _parse_id_csv(existing)
    if existing_ids is None:
        return None
    return _format_id_csv(existing_ids | incoming_ids)


def create_style_position_rule(db: Session, data: schemas.StylePositionRuleCreate):
    """
    创建规则：将 code 转换为 id；已存在的同维度规则会合并，避免重复规则生效不确定。
    """
    # 1. 转换 position_code 为 position_id
    position_id = None
    if data.position_code:
        position = get_position_by_code(db, data.position_code)
        if not position:
            raise ValueError(f"位置编码 '{data.position_code}' 不存在")
        position_id = position.id

    # 2. 转换 style_codes 为 style_ids
    style_ids = None
    if data.style_codes:
        style_id_list = []
        for code in data.style_codes:
            style = get_style_by_code(db, code)
            if not style:
                raise ValueError(f"款式编码 '{code}' 不存在")
            style_id_list.append(str(style.id))
        # 去重、排序，确保唯一性约束正常工作
        style_id_list = sorted(set(style_id_list), key=int)
        style_ids = ",".join(style_id_list)

    # 3. 转换 print_codes 为 print_ids
    print_ids = None
    if data.print_codes:
        print_id_list = []
        for code in data.print_codes:
            print_obj = get_print_by_code(db, code)
            if not print_obj:
                raise ValueError(f"印花编码 '{code}' 不存在")
            print_id_list.append(str(print_obj.id))
        # 去重、排序，确保唯一性约束正常工作
        print_id_list = sorted(set(print_id_list), key=int)
        print_ids = ",".join(print_id_list)

    # 4. 已存在同维度规则时合并，避免同一位置/款式生成多条规则。
    if data.rule_type == 2:
        existing_rules = db.query(models.StylePositionRule).filter(
            models.StylePositionRule.rule_type == 2,
            models.StylePositionRule.position_id == position_id,
        ).order_by(models.StylePositionRule.id).all()

        if existing_rules:
            obj = existing_rules[0]
            for duplicate in existing_rules[1:]:
                obj.style_ids = _merge_nullable_id_csv(obj.style_ids, duplicate.style_ids)
                obj.print_ids = _merge_nullable_id_csv(obj.print_ids, duplicate.print_ids)
                db.delete(duplicate)

            obj.style_ids = _append_id_csv(obj.style_ids, style_ids)
            obj.print_ids = _append_id_csv(obj.print_ids, print_ids)
            obj.is_active = data.is_active
            db.commit()
            db.refresh(obj)
            return obj

    if data.rule_type == 3:
        existing_rule = db.query(models.StylePositionRule).filter(
            models.StylePositionRule.rule_type == 3,
            models.StylePositionRule.position_id == position_id,
            models.StylePositionRule.style_ids == style_ids,
        ).first()

        if existing_rule:
            existing_rule.print_ids = _merge_nullable_id_csv(existing_rule.print_ids, print_ids)
            existing_rule.is_active = data.is_active
            db.commit()
            db.refresh(existing_rule)
            return existing_rule

    if data.rule_type == 1:
        existing_rule = db.query(models.StylePositionRule).filter(
            models.StylePositionRule.rule_type == 1,
            models.StylePositionRule.style_ids == style_ids,
        ).first()

        if existing_rule:
            existing_rule.is_active = data.is_active
            db.commit()
            db.refresh(existing_rule)
            return existing_rule

    # 5. 创建规则
    obj = models.StylePositionRule(
        rule_type=data.rule_type,
        position_id=position_id,
        style_ids=style_ids,
        print_ids=print_ids,
        is_active=data.is_active
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_style_position_rule(db: Session, rule_id: int, data: schemas.StylePositionRuleUpdate):
    """
    更新规则：将 code 转换为 id
    """
    obj = db.query(models.StylePositionRule).filter(models.StylePositionRule.id == rule_id).first()
    if not obj:
        return None

    # 1. 转换 position_code
    if data.position_code is not None:
        if data.position_code:
            position = get_position_by_code(db, data.position_code)
            if not position:
                raise ValueError(f"位置编码 '{data.position_code}' 不存在")
            obj.position_id = position.id
        else:
            obj.position_id = None

    # 2. 转换 style_codes
    if data.style_codes is not None:
        if data.style_codes:
            style_id_list = []
            for code in data.style_codes:
                style = get_style_by_code(db, code)
                if not style:
                    raise ValueError(f"款式编码 '{code}' 不存在")
                style_id_list.append(str(style.id))
            # 去重、排序，确保唯一性约束正常工作
            style_id_list = sorted(set(style_id_list), key=int)
            obj.style_ids = ",".join(style_id_list)
        else:
            obj.style_ids = None

    # 3. 转换 print_codes
    if data.print_codes is not None:
        if data.print_codes:
            print_id_list = []
            for code in data.print_codes:
                print_obj = get_print_by_code(db, code)
                if not print_obj:
                    raise ValueError(f"印花编码 '{code}' 不存在")
                print_id_list.append(str(print_obj.id))
            # 去重、排序，确保唯一性约束正常工作
            print_id_list = sorted(set(print_id_list), key=int)
            obj.print_ids = ",".join(print_id_list)
        else:
            obj.print_ids = None

    # 4. 更新 is_active
    if data.is_active is not None:
        obj.is_active = data.is_active

    db.commit()
    db.refresh(obj)
    return obj


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
