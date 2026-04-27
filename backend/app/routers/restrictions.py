from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, schemas
from ..database import get_db
from ..pattern_suffix_validator import check_pattern_suffix_rule, filter_patterns_by_suffix, filter_positions_by_suffix

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


@router.post("/check", response_model=schemas.RestrictionCheckResponse)
def check_restriction(
    data: schemas.RestrictionCheckRequest,
    db: Session = Depends(get_db),
):
    """
    校验款式+位置+印花组合是否被允许
    """
    from sqlalchemy import text
    from .. import models
    from ..name_resolver import resolve_names_to_ids

    # 步骤0: 检查特殊印花（纯色/自搭/福袋）直接放行
    SPECIAL_PRINTS = {"纯色", "自搭", "福袋"}
    if data.print_code in SPECIAL_PRINTS:
        return schemas.RestrictionCheckResponse(
            allowed=True,
            reason="特殊印花无需校验",
            rule_type=None,
            rule_id=None
        )

    # 转换名称为ID
    style_id, position_id, print_id = resolve_names_to_ids(
        data.style_code, data.position_name, data.print_code
    )

    # 步骤1: 检查印花后缀规则（硬性全局规则）
    position = db.query(models.Position).filter(models.Position.id == position_id).first()
    if position:
        try:
            allowed, error_msg = check_pattern_suffix_rule(data.print_code, position.area)
            if not allowed:
                return schemas.RestrictionCheckResponse(
                    allowed=False,
                    reason=error_msg,
                    rule_type="pattern_suffix",
                    rule_id=None
                )
        except ValueError as e:
            return schemas.RestrictionCheckResponse(
                allowed=False,
                reason=str(e),
                rule_type="pattern_suffix",
                rule_id=None
            )

    # 步骤1: 检查款式全禁（类型1）
    style_ban = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 1,
        text(f"FIND_IN_SET({style_id}, style_ids) > 0"),
        models.StylePositionRule.is_active == True
    ).first()

    if style_ban:
        return schemas.RestrictionCheckResponse(
            allowed=False,
            reason=f"款式 {data.style_code} 完全禁止印花",
            rule_type="style_ban",
            rule_id=style_ban.id
        )

    # 步骤2: 检查位置限定（类型2，优先级最高）
    position_restriction = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 2,
        models.StylePositionRule.position_id == position_id,
        models.StylePositionRule.is_active == True
    ).first()

    if position_restriction:
        # 检查款式是否在白名单中
        style_ids_list = position_restriction.style_ids.split(',') if position_restriction.style_ids else None

        if style_ids_list is not None:
            if str(style_id) not in [s.strip() for s in style_ids_list]:
                return schemas.RestrictionCheckResponse(
                    allowed=False,
                    reason=f"款式 {data.style_code} 不在位置 {data.position_name} 的允许款式列表中",
                    rule_type="position_restriction",
                    rule_id=position_restriction.id
                )

        # 检查印花是否在白名单中
        print_ids_list = position_restriction.print_ids.split(',') if position_restriction.print_ids else None

        if print_ids_list is not None:
            if str(print_id) not in [p.strip() for p in print_ids_list]:
                return schemas.RestrictionCheckResponse(
                    allowed=False,
                    reason=f"印花 {data.print_code} 不在位置 {data.position_name} 的允许印花列表中",
                    rule_type="position_restriction",
                    rule_id=position_restriction.id
                )

        # 位置限定通过
        return schemas.RestrictionCheckResponse(
            allowed=True,
            reason=f"符合位置 {data.position_name} 的限定规则",
            rule_type="position_restriction",
            rule_id=position_restriction.id
        )

    # 步骤3: 检查款式位置限定（类型3，黑名单策略）
    style_position_rules = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 3,
        text(f"FIND_IN_SET({style_id}, style_ids) > 0"),
        models.StylePositionRule.is_active == True
    ).all()

    if style_position_rules:
        # 款式有类型3规则，检查该位置是否在白名单中
        style_position_for_this_pos = None
        for rule in style_position_rules:
            if rule.position_id == position_id:
                style_position_for_this_pos = rule
                break

        if style_position_for_this_pos is None:
            # 该位置不在款式的白名单中（黑名单策略）
            return schemas.RestrictionCheckResponse(
                allowed=False,
                reason=f"款式 {data.style_code} 在位置 {data.position_name} 不可用（未在白名单中）",
                rule_type="style_position",
                rule_id=None
            )

        # 该位置在白名单中，检查印花
        print_ids_list = style_position_for_this_pos.print_ids.split(',') if style_position_for_this_pos.print_ids else None

        if print_ids_list is None:
            # 不限印花
            return schemas.RestrictionCheckResponse(
                allowed=True,
                reason=f"款式 {data.style_code} 在位置 {data.position_name} 不限印花",
                rule_type="style_position",
                rule_id=style_position_for_this_pos.id
            )

        # 检查印花是否在白名单中
        if str(print_id) not in [p.strip() for p in print_ids_list]:
            return schemas.RestrictionCheckResponse(
                allowed=False,
                reason=f"印花 {data.print_code} 不在款式 {data.style_code} + 位置 {data.position_name} 的允许印花列表中",
                rule_type="style_position",
                rule_id=style_position_for_this_pos.id
            )

        # 款式位置限定通过
        return schemas.RestrictionCheckResponse(
            allowed=True,
            reason=f"符合款式 {data.style_code} 在位置 {data.position_name} 的限定规则",
            rule_type="style_position",
            rule_id=style_position_for_this_pos.id
        )

    # 步骤4: 默认允许
    return schemas.RestrictionCheckResponse(
        allowed=True,
        reason="无限定规则，默认允许",
        rule_type=None,
        rule_id=None
    )


@router.get("/available-by-style", response_model=schemas.AvailableByStyleResponse)
def get_available_by_style(
    style_code: str = Query(..., description="款式编码"),
    db: Session = Depends(get_db),
):
    """
    查询款式在所有位置上可用的印花列表（带位置对应关系）
    """
    from sqlalchemy import text
    from .. import models
    from ..name_resolver import resolve_style_code

    # 转换名称为ID
    style_id = resolve_style_code(style_code)

    # 步骤1: 检查款式全禁
    style_ban = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 1,
        text(f"FIND_IN_SET({style_id}, style_ids) > 0"),
        models.StylePositionRule.is_active == True
    ).first()

    if style_ban:
        return schemas.AvailableByStyleResponse(
            style_code=style_code,
            is_banned=True,
            available_positions=[]
        )

    # 步骤2: 查询所有启用的位置
    all_positions = db.query(models.Position).filter(
        models.Position.is_active == True
    ).order_by(models.Position.id).all()

    # 步骤3: 对每个位置调用 available-prints 逻辑
    available_positions = []

    for position in all_positions:
        position_id = position.id

        # 复用 available-prints 的逻辑
        # 检查位置限定（类型2）
        position_restriction = db.query(models.StylePositionRule).filter(
            models.StylePositionRule.rule_type == 2,
            models.StylePositionRule.position_id == position_id,
            models.StylePositionRule.is_active == True
        ).first()

        if position_restriction:
            # 检查款式是否在白名单中
            style_ids_list = position_restriction.style_ids.split(',') if position_restriction.style_ids else None

            if style_ids_list is not None:
                if str(style_id) not in [s.strip() for s in style_ids_list]:
                    # 款式不在白名单，跳过该位置
                    continue

            # 款式通过，获取允许的印花
            print_ids_list = position_restriction.print_ids.split(',') if position_restriction.print_ids else None

            if print_ids_list is None:
                # 不限印花
                all_prints = db.query(models.Print).filter(models.Print.is_active == True).order_by(models.Print.id).all()
                print_ids = [p.id for p in all_prints]
                print_codes = [p.code for p in all_prints]
            else:
                print_ids = [int(pid.strip()) for pid in print_ids_list]
                prints = db.query(models.Print).filter(
                    models.Print.id.in_(print_ids),
                    models.Print.is_active == True
                ).order_by(models.Print.id).all()
                print_ids = [p.id for p in prints]
                print_codes = [p.code for p in prints]

            # 应用后缀规则过滤
            print_codes = filter_patterns_by_suffix(print_codes, position.area)

            available_positions.append(schemas.AvailablePositionWithPrints(
                position_name=position.name,
                position_code=position.code,
                print_codes=print_codes,
                available=len(print_codes) > 0,
                is_restricted=print_ids_list is not None,
                reason=f"位置 {position.name} 限定了允许的印花列表" if print_ids_list else "位置限定不限印花"
            ))
            continue

        # 检查款式位置限定（类型3，黑名单策略）
        style_position_rules = db.query(models.StylePositionRule).filter(
            models.StylePositionRule.rule_type == 3,
            text(f"FIND_IN_SET({style_id}, style_ids) > 0"),
            models.StylePositionRule.is_active == True
        ).all()

        if style_position_rules:
            # 款式有类型3规则，检查该位置是否在白名单中
            style_position_for_this_pos = None
            for rule in style_position_rules:
                if rule.position_id == position_id:
                    style_position_for_this_pos = rule
                    break

            if style_position_for_this_pos is None:
                # 该位置不在款式的白名单中（黑名单策略），跳过
                continue

            # 该位置在白名单中，获取允许的印花
            print_ids_list = style_position_for_this_pos.print_ids.split(',') if style_position_for_this_pos.print_ids else None

            if print_ids_list is None:
                # 不限印花
                all_prints = db.query(models.Print).filter(models.Print.is_active == True).order_by(models.Print.id).all()
                print_codes = [p.code for p in all_prints]
            else:
                print_ids = [int(pid.strip()) for pid in print_ids_list]
                prints = db.query(models.Print).filter(
                    models.Print.id.in_(print_ids),
                    models.Print.is_active == True
                ).order_by(models.Print.id).all()
                print_codes = [p.code for p in prints]

            # 应用后缀规则过滤
            print_codes = filter_patterns_by_suffix(print_codes, position.area)

            available_positions.append(schemas.AvailablePositionWithPrints(
                position_name=position.name,
                position_code=position.code,
                print_codes=print_codes,
                available=len(print_codes) > 0,
                is_restricted=print_ids_list is not None,
                reason=f"款式 {style_code} 在位置 {position.name} 限定了允许的印花列表" if print_ids_list else "款式位置限定不限印花"
            ))
            continue

        # 款式无类型3规则，默认返回所有印花
        all_prints = db.query(models.Print).filter(models.Print.is_active == True).order_by(models.Print.id).all()
        print_codes = [p.code for p in all_prints]

        # 应用后缀规则过滤
        print_codes = filter_patterns_by_suffix(print_codes, position.area)

        available_positions.append(schemas.AvailablePositionWithPrints(
            position_name=position.name,
            position_code=position.code,
            print_codes=print_codes,
            available=len(print_codes) > 0,
            is_restricted=False,
            reason="无限定规则，所有印花可用"
        ))

    return schemas.AvailableByStyleResponse(
        style_code=style_code,
        is_banned=False,
        available_positions=available_positions
    )


@router.get("/available-prints")
def get_available_prints(
    style_code: str = Query(..., description="款式编码"),
    position_name: str = Query(..., description="位置名称"),
    db: Session = Depends(get_db),
):
    """
    查询款式+位置可用的印花列表（黑名单策略）
    """
    from sqlalchemy import text
    from .. import models
    from ..name_resolver import resolve_style_code, resolve_position_name

    # 转换名称为ID
    style_id = resolve_style_code(style_code)
    position_id = resolve_position_name(position_name)

    # 获取位置信息用于后缀规则检查
    position = db.query(models.Position).filter(models.Position.id == position_id).first()
    if not position:
        return {
            "available": False,
            "print_codes": [],
            "is_restricted": True,
            "reason": f"位置 {position_name} 不存在"
        }

    # 步骤1: 检查款式全禁
    style_ban = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 1,
        text(f"FIND_IN_SET({style_id}, style_ids) > 0"),
        models.StylePositionRule.is_active == True
    ).first()

    if style_ban:
        return {
            "available": False,
            "print_codes": [],
            "is_restricted": True,
            "reason": f"款式 {style_code} 完全禁止印花"
        }

    # 步骤2: 检查位置限定（类型2，优先级最高）
    position_restriction = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 2,
        models.StylePositionRule.position_id == position_id,
        models.StylePositionRule.is_active == True
    ).first()

    if position_restriction:
        # 检查款式是否在白名单中
        style_ids_list = position_restriction.style_ids.split(',') if position_restriction.style_ids else None

        # 如果限定了款式，检查是否在白名单
        if style_ids_list is not None:
            if str(style_id) not in [s.strip() for s in style_ids_list]:
                return {
                    "available": False,
                    "print_codes": [],
                    "is_restricted": True,
                    "reason": f"款式 {style_code} 不在位置 {position_name} 的允许款式列表中"
                }

        # 款式通过，返回允许的印花
        print_ids_list = position_restriction.print_ids.split(',') if position_restriction.print_ids else None

        if print_ids_list is None:
            # 不限印花
            all_prints = db.query(models.Print).filter(models.Print.is_active == True).order_by(models.Print.id).all()
            print_codes = [p.code for p in all_prints]
        else:
            print_ids = [int(pid.strip()) for pid in print_ids_list]
            prints = db.query(models.Print).filter(
                models.Print.id.in_(print_ids),
                models.Print.is_active == True
            ).order_by(models.Print.id).all()
            print_codes = [p.code for p in prints]

        # 应用后缀规则过滤
        print_codes = filter_patterns_by_suffix(print_codes, position.area)

        return {
            "available": len(print_codes) > 0,
            "print_codes": print_codes,
            "is_restricted": print_ids_list is not None,
            "reason": f"位置 {position_name} 限定了允许的印花列表" if print_ids_list else "位置限定不限印花"
        }

    # 步骤3: 检查款式是否有类型3规则（黑名单策略）
    style_position_rules = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 3,
        text(f"FIND_IN_SET({style_id}, style_ids) > 0"),
        models.StylePositionRule.is_active == True
    ).all()

    if style_position_rules:
        # 款式有类型3规则，检查该位置是否在白名单中
        style_position_for_this_pos = None
        for rule in style_position_rules:
            if rule.position_id == position_id:
                style_position_for_this_pos = rule
                break

        if style_position_for_this_pos is None:
            # 该位置不在款式的白名单中
            return {
                "available": False,
                "print_codes": [],
                "is_restricted": True,
                "reason": f"款式 {style_code} 在位置 {position_name} 不可用（未在白名单中）"
            }

        # 该位置在白名单中，返回允许的印花
        print_ids_list = style_position_for_this_pos.print_ids.split(',') if style_position_for_this_pos.print_ids else None

        if print_ids_list is None:
            # 不限印花
            all_prints = db.query(models.Print).filter(models.Print.is_active == True).order_by(models.Print.id).all()
            print_codes = [p.code for p in all_prints]
        else:
            print_ids = [int(pid.strip()) for pid in print_ids_list]
            prints = db.query(models.Print).filter(
                models.Print.id.in_(print_ids),
                models.Print.is_active == True
            ).order_by(models.Print.id).all()
            print_codes = [p.code for p in prints]

        # 应用后缀规则过滤
        print_codes = filter_patterns_by_suffix(print_codes, position.area)

        return {
            "available": len(print_codes) > 0,
            "print_codes": print_codes,
            "is_restricted": print_ids_list is not None,
            "reason": f"款式 {style_code} 在位置 {position_name} 限定了允许的印花列表" if print_ids_list else "款式位置限定不限印花"
        }

    # 步骤4: 款式无类型3规则，默认返回所有印花
    all_prints = db.query(models.Print).filter(models.Print.is_active == True).order_by(models.Print.id).all()
    print_codes = [p.code for p in all_prints]

    # 应用后缀规则过滤
    print_codes = filter_patterns_by_suffix(print_codes, position.area)

    return {
        "available": len(print_codes) > 0,
        "print_codes": print_codes,
        "is_restricted": False,
        "reason": "无限定规则，所有印花可用"
    }


@router.get("/available-positions")
def get_available_positions(
    style_code: str = Query(..., description="款式编码"),
    print_code: str = Query(..., description="印花编码"),
    db: Session = Depends(get_db),
):
    """
    查询款式+印花可用的位置列表（黑名单策略，类型2可扩展白名单）
    """
    from sqlalchemy import text
    from .. import models
    from ..name_resolver import resolve_style_code, resolve_print_code
    from ..cache import name_cache

    # 步骤0: 检查特殊印花（纯色/自搭/福袋）直接报错
    SPECIAL_PRINTS = {"纯色", "自搭", "福袋"}
    if print_code in SPECIAL_PRINTS:
        raise HTTPException(
            status_code=400,
            detail=f"特殊印花（{print_code}）无贴图位置"
        )

    # 转换名称为ID
    style_id = resolve_style_code(style_code)
    print_id = resolve_print_code(print_code)

    # 步骤1: 检查款式全禁
    style_ban = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 1,
        text(f"FIND_IN_SET({style_id}, style_ids) > 0"),
        models.StylePositionRule.is_active == True
    ).first()

    if style_ban:
        return {
            "available": False,
            "position_names": [],
            "is_restricted": True,
            "reason": f"款式 {style_code} 完全禁止印花"
        }

    # 步骤2: 查询款式在类型3中的所有规则
    style_position_rules = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 3,
        text(f"FIND_IN_SET({style_id}, style_ids) > 0"),
        models.StylePositionRule.is_active == True
    ).all()

    # 步骤3: 初始化候选位置集合
    if style_position_rules:
        # 如果款式有类型3规则，初始候选 = 类型3中的位置（黑名单策略）
        candidate_position_ids = {rule.position_id for rule in style_position_rules}
    else:
        # 如果款式无类型3规则，初始候选 = 所有位置（默认允许）
        all_positions = db.query(models.Position.id).filter(models.Position.is_active == True).all()
        candidate_position_ids = {p.id for p in all_positions}

    # 步骤4: 查询所有类型2规则
    position_restrictions = db.query(models.StylePositionRule).filter(
        models.StylePositionRule.rule_type == 2,
        models.StylePositionRule.is_active == True
    ).all()

    # 步骤5: 应用类型2规则（可以扩展白名单）
    for rule in position_restrictions:
        position_id = rule.position_id

        # 解析款式和印花白名单
        style_ids_list = rule.style_ids.split(',') if rule.style_ids else None
        print_ids_list = rule.print_ids.split(',') if rule.print_ids else None

        # 检查款式和印花是否通过
        style_ok = style_ids_list is None or str(style_id) in [s.strip() for s in style_ids_list]
        print_ok = print_ids_list is None or str(print_id) in [p.strip() for p in print_ids_list]

        if style_ok and print_ok:
            # 通过类型2，加入候选（扩展白名单）
            candidate_position_ids.add(position_id)
        else:
            # 不通过类型2，如果位置在候选中则移除
            candidate_position_ids.discard(position_id)

    # 步骤6: 应用类型3规则（仅对非类型2位置）
    type2_positions = {rule.position_id for rule in position_restrictions}

    for rule in style_position_rules:
        position_id = rule.position_id

        # 如果该位置有类型2，跳过（类型2优先）
        if position_id in type2_positions:
            continue

        # 检查印花
        print_ids_list = rule.print_ids.split(',') if rule.print_ids else None
        print_ok = print_ids_list is None or str(print_id) in [p.strip() for p in print_ids_list]

        if not print_ok:
            candidate_position_ids.discard(position_id)

    # 步骤7: 应用后缀规则过滤位置
    # 获取所有候选位置的详细信息
    positions_with_area = []
    for pos_id in candidate_position_ids:
        pos = db.query(models.Position).filter(models.Position.id == pos_id).first()
        if pos:
            positions_with_area.append((pos.name, pos.area))

    # 应用后缀规则过滤
    position_names = filter_positions_by_suffix(positions_with_area, print_code)

    is_restricted = len(style_position_rules) > 0 or len(position_restrictions) > 0

    return {
        "available": len(position_names) > 0,
        "position_names": position_names,
        "is_restricted": is_restricted,
        "reason": "根据限定规则过滤" if is_restricted else "无限定规则，所有位置可用"
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
            if len(data.style_codes) != 1:
                raise HTTPException(400, "款式位置规则只能指定一个款式")
        elif data.rule_type == 2:  # position_restriction
            if not data.position_code:
                raise HTTPException(400, "位置限定规则需要 position_code")
            if not data.style_codes and not data.print_codes:
                raise HTTPException(400, "位置限定规则的 style_codes 和 print_codes 不能同时为空")
        elif data.rule_type == 1:  # style_ban
            if not data.style_codes:
                raise HTTPException(400, "款式全禁规则需要 style_codes")
            if len(data.style_codes) != 1:
                raise HTTPException(400, "款式全禁规则只能指定一个款式")
        else:
            raise HTTPException(400, f"未知的规则类型: {data.rule_type}")

        obj = crud.create_style_position_rule(db, data)
        return {"id": obj.id, "message": "创建成功"}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.put("/{rule_id}")
def update_rule(rule_id: int, data: schemas.StylePositionRuleUpdate, db: Session = Depends(get_db)):
    try:
        # 获取现有规则
        existing_rule = db.query(models.StylePositionRule).filter(
            models.StylePositionRule.id == rule_id
        ).first()
        if not existing_rule:
            raise HTTPException(status_code=404, detail="规则不存在")

        # 确定规则类型（如果更新中没有提供，使用现有的）
        rule_type = existing_rule.rule_type

        # 类型1和类型3：必须且只能有一个款式
        if rule_type in [1, 3]:
            if data.style_codes is not None:
                if not data.style_codes or len(data.style_codes) != 1:
                    type_name = "款式全禁" if rule_type == 1 else "款式位置限定"
                    raise HTTPException(400, f"{type_name}规则必须且只能选择一个款式")

        # 类型2：style_codes和print_codes不能同时为空
        if rule_type == 2:
            # 确定更新后的值
            final_style_codes = data.style_codes if data.style_codes is not None else (
                existing_rule.style_ids.split(',') if existing_rule.style_ids else []
            )
            final_print_codes = data.print_codes if data.print_codes is not None else (
                existing_rule.print_ids.split(',') if existing_rule.print_ids else []
            )

            if not final_style_codes and not final_print_codes:
                raise HTTPException(400, "位置限定规则的允许款式和允许印花不能同时为空")

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
