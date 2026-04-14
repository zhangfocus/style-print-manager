import io
import json
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from openpyxl import load_workbook, Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .. import crud, schemas, models
from ..database import get_db

router = APIRouter(prefix="/api/excel", tags=["Excel导入导出"])

# 款式表 31 列（与原始模版保持一致）
STYLE_HEADERS = [
    "品牌属性", "属性", "面料种类", "年份", "性别", "季节",
    "类目", "商品分类", "虚拟分类",
    "商品款号", "白坯款式编码*",
    "款式备注",
    "在售颜色", "淘汰颜色", "颜色备注",
    "尺码", "号型", "尺码备注",
    "可印花范围",
    "面料成分", "Fabric Ingredients", "热风成分",
    "面料名称", "面料克重", "白坯重量",
    "开发时间", "吊牌价", "高价品牌吊牌价",
    "执行标准", "安全技术类别", "产品分类",
]
PRINT_HEADERS = [
    "图案名称*", "图案大小", "图案规格", "工艺属性", "商品编码*",
    "真维斯款号", "真维斯替换编码", "真维斯替换款号",
    "JWCO款号", "JWCO替换编码", "JWCO替换款号",
    "CITY款号", "CITY替换编码", "CITY替换款号",
    "唐狮款号", "备注",
]
POSITION_HEADERS = ["位置编号*", "位置名称*", "区域", "备注"]
RESTRICTION_HEADERS = ["白坯款式编码*", "位置名称*", "允许印花编码(逗号分隔，留空=不限)", "是否启用(1/0)", "备注"]


# ── 工具函数 ──────────────────────────────────────────

def _excel_date(val):
    """Excel 序列号 / datetime → Python date"""
    if val is None:
        return None
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val if isinstance(val, datetime.date) else val.date()
    try:
        return datetime.date(1899, 12, 30) + datetime.timedelta(days=int(val))
    except Exception:
        return None


def _str(v):
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def _apply_header_style(ws):
    header_fill = PatternFill("solid", fgColor="4472C4")
    header_font = Font(color="FFFFFF", bold=True)
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for col, cell in enumerate(ws[1], 1):
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        cell.border = border
        ws.column_dimensions[get_column_letter(col)].width = 20


def _parse_wb(content: bytes, filename: str) -> object:
    try:
        return load_workbook(io.BytesIO(content), data_only=True)
    except Exception as e:
        raise HTTPException(400, f"文件解析失败: {e}")


def _stream_wb(wb: object, filename: str) -> StreamingResponse:
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ── 核心导入逻辑（各模块独立） ────────────────────────

def _import_styles(ws, db: Session):
    """从 worksheet 导入款式，返回 (count, errors)"""
    headers = [cell.value for cell in ws[1]]

    def col(row_vals, name):
        # 支持带 * 的列名
        for h in [name, name + "*", name.rstrip("*")]:
            try:
                return row_vals[headers.index(h)]
            except ValueError:
                continue
        return None

    count, errors = 0, []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        code_val = col(row, "白坯款式编码")
        if not code_val:
            continue
        code = str(code_val).strip()
        if not code:
            errors.append(f"第{row_idx}行：白坯款式编码不能为空")
            continue
        try:
            payload = schemas.StyleCreate(
                code=code,
                product_code=_str(col(row, "商品款号")),
                brand_attr=_str(col(row, "品牌属性")),
                attr=_str(col(row, "属性")),
                fabric_type=_str(col(row, "面料种类")),
                year=int(col(row, "年份")) if col(row, "年份") is not None else None,
                gender=_str(col(row, "性别")),
                season=_str(col(row, "季节")),
                category=_str(col(row, "类目")),
                product_category=_str(col(row, "商品分类")),
                virtual_category=_str(col(row, "虚拟分类")),
                description=_str(col(row, "款式备注")),
                colors_active=_str(col(row, "在售颜色")),
                colors_discontinued=_str(col(row, "淘汰颜色")),
                color_remark=_str(col(row, "颜色备注")),
                sizes=_str(col(row, "尺码")),
                size_specs=_str(col(row, "号型")),
                size_remark=_str(col(row, "尺码备注")),
                printable_area=_str(col(row, "可印花范围")),
                fabric_composition=_str(col(row, "面料成分")),
                fabric_composition_en=_str(col(row, "Fabric Ingredients")),
                hot_wind_composition=_str(col(row, "热风成分")),
                fabric_name=_str(col(row, "面料名称")),
                fabric_weight=_str(col(row, "面料克重")),
                blank_weight=float(col(row, "白坯重量")) if col(row, "白坯重量") is not None else None,
                dev_date=_excel_date(col(row, "开发时间")),
                tag_price=float(col(row, "吊牌价")) if col(row, "吊牌价") is not None else None,
                premium_tag_price=float(col(row, "高价品牌吊牌价")) if col(row, "高价品牌吊牌价") is not None else None,
                exec_standard=_str(col(row, "执行标准")),
                safety_category=_str(col(row, "安全技术类别")),
                product_type=_str(col(row, "产品分类")),
            )
            existing = crud.get_style_by_code(db, code)
            if existing:
                crud.update_style(db, existing.id, schemas.StyleUpdate(**{k: v for k, v in payload.model_dump().items() if k != "code"}))
            else:
                crud.create_style(db, payload)
            count += 1
        except Exception as e:
            errors.append(f"第{row_idx}行处理失败: {e}")
            if len(errors) >= 20:
                break
    return count, errors


def _import_prints(ws, db: Session):
    """支持原始印花.xlsx格式（按列名匹配）和模板格式"""
    headers = [cell.value for cell in ws[1]]

    def col(row_vals, *names):
        for name in names:
            for h in [name, name + "*", name.rstrip("*")]:
                try:
                    return row_vals[headers.index(h)]
                except ValueError:
                    continue
        return None

    count, errors = 0, []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        code_val = col(row, "商品编码")
        name_val = col(row, "图案名称")
        if not code_val and not name_val:
            continue
        code = _str(code_val)
        name = _str(name_val)
        if not code:
            errors.append(f"第{row_idx}行：商品编码不能为空")
            continue
        if not name:
            errors.append(f"第{row_idx}行：图案名称不能为空")
            continue
        try:
            payload = schemas.PrintCreate(
                code=code,
                name=name,
                pattern_size=_str(col(row, "图案大小")),
                pattern_spec=_str(col(row, "图案规格")),
                craft_attr=_str(col(row, "工艺属性")),
                zwx_style_code=_str(col(row, "真维斯款号")),
                zwx_replace_code=_str(col(row, "真维斯替换编码")),
                zwx_replace_style=_str(col(row, "真维斯替换款号")),
                jwco_style_code=_str(col(row, "JWCO款号")),
                jwco_replace_code=_str(col(row, "JWCO替换编码")),
                jwco_replace_style=_str(col(row, "JWCO替换款号")),
                city_style_code=_str(col(row, "CITY款号")),
                city_replace_code=_str(col(row, "CITY替换编码")),
                city_replace_style=_str(col(row, "CITY替换款号")),
                tangshi_style_code=_str(col(row, "唐狮款号")),
                description=_str(col(row, "备注")),
            )
            existing = crud.get_print_by_code(db, code)
            if existing:
                crud.update_print(db, existing.id, schemas.PrintUpdate(**{k: v for k, v in payload.model_dump().items() if k != "code"}))
            else:
                crud.create_print(db, payload)
            count += 1
        except Exception as e:
            errors.append(f"第{row_idx}行处理失败: {e}")
            if len(errors) >= 20:
                break
    return count, errors


def _import_positions(ws, db: Session):
    count, errors = 0, []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        if not row[0] and not row[1]:
            continue
        code, name = _str(row[0]), _str(row[1])
        if not code or not name:
            errors.append(f"第{row_idx}行：编号和名称不能为空")
            continue
        payload = schemas.PositionCreate(
            code=code, name=name,
            area=_str(row[2]),
            description=_str(row[3]),
        )
        existing = crud.get_position_by_code(db, code)
        if existing:
            crud.update_position(db, existing.id, schemas.PositionUpdate(**{k: v for k, v in payload.model_dump().items() if k != "code"}))
        else:
            crud.create_position(db, payload)
        count += 1
    return count, errors


import re as _re

# 导入时跳过的特殊印花（不算真实印花，无需限定）
_SPECIAL_PRINTS = {"纯色", "福袋", "自搭"}


def _split_multi(s: str):
    """按中英文逗号/顿号/换行拆分，去空白"""
    return [x.strip() for x in _re.split(r'[,，、\n\r]+', s) if x.strip()]


def _parse_print_list(raw: str):
    """
    解析印花列表字符串：
    - 返回 None  → 不限制任何印花
    - 返回 list  → 仅允许列表中的印花（已去重排序，已剔除特殊印花）
    """
    if not raw:
        return None
    codes = [c for c in _split_multi(raw) if c not in _SPECIAL_PRINTS]
    return sorted(set(codes)) if codes else None


def _upsert_rule(db: Session, style_code: str, position_name: str, new_prints):
    """
    向 style_position_rules 写入或合并一条规则（通过 style_code / position_name 查 ID）。
    - new_prints=None  → 该位置不限印花（若已有列表，升级为 NULL）
    - new_prints=list  → 与已有允许列表取并集
    找不到款式或位置时抛 ValueError，由调用方记录为错误行。
    """
    style = crud.get_style_by_code(db, style_code)
    if not style:
        raise ValueError(f"款式 '{style_code}' 不在款式表中")
    position = crud.get_position_by_name(db, position_name)
    if not position:
        raise ValueError(f"位置 '{position_name}' 不在位置表中")

    existing = crud.get_style_position_rule_by_key(db, style.id, position.id)
    if existing:
        if new_prints is None:
            if existing.allowed_prints is not None:
                existing.allowed_prints = None
                db.commit()
        else:
            if existing.allowed_prints is not None:
                old_set = set(existing.allowed_prints.split(","))
                merged = sorted(old_set | set(new_prints))
                existing.allowed_prints = ",".join(merged)
                db.commit()
    else:
        ap = ",".join(new_prints) if new_prints else None
        db.add(models.StylePositionRule(
            style_id=style.id,
            position_id=position.id,
            allowed_prints=ap,
        ))
        db.commit()


def _upsert_ban(db: Session, style_code: str):
    style = crud.get_style_by_code(db, style_code)
    if not style:
        raise ValueError(f"款式 '{style_code}' 不在款式表中")
    if not crud.get_style_ban_by_style_id(db, style.id):
        db.add(models.StyleBan(style_id=style.id))
        db.commit()


def _import_restrictions(ws, db: Session):
    """
    标准限定格式（3列）：
      A=白坯款式编码  B=位置名称（空=全禁该款式）  C=印花编码（逗号分隔，空=不限）
    同一 (款式, 位置) 多次导入时印花列表取并集。
    """
    rows = list(ws.iter_rows(values_only=True))
    rule_count, ban_count, errors = 0, 0, []

    for row_idx, row in enumerate(rows[1:], 2):
        style_code = _str(row[0]) if len(row) > 0 else None
        pos_name   = _str(row[1]) if len(row) > 1 else None
        prints_raw = _str(row[2]) if len(row) > 2 else None

        if not style_code:
            continue

        if pos_name:
            print_list = _parse_print_list(prints_raw)
            try:
                _upsert_rule(db, style_code, pos_name, print_list)
                rule_count += 1
            except Exception as e:
                errors.append(f"第{row_idx}行 ({style_code}, {pos_name}): {e}")
                if len(errors) >= 30:
                    return rule_count + ban_count, errors
        else:
            try:
                _upsert_ban(db, style_code)
                ban_count += 1
            except Exception as e:
                errors.append(f"第{row_idx}行 全禁 ({style_code}): {e}")

    return rule_count + ban_count, errors


def _result(label: str, count: int, errors: list) -> schemas.ImportResult:
    msg = f"导入完成：{label} {count} 条"
    if errors:
        msg += f"；有 {len(errors)} 条错误"
    return schemas.ImportResult(
        success=len(errors) == 0,
        message=msg,
        details={"counts": {label: count}, "errors": errors[:20]},
    )


def _first_sheet(wb, filename: str):
    """取工作簿第一个 sheet，若无则报错"""
    if not wb.sheetnames:
        raise HTTPException(400, "文件中没有找到任何 Sheet")
    return wb.active


# ── 分模块导入接口 ─────────────────────────────────────

@router.post("/import/styles", summary="导入款式", response_model=schemas.ImportResult)
async def import_styles(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "请上传 .xlsx 或 .xls 文件")
    wb = _parse_wb(await file.read(), file.filename)
    ws = wb["款式"] if "款式" in wb.sheetnames else _first_sheet(wb, file.filename)
    count, errors = _import_styles(ws, db)
    return _result("款式", count, errors)


@router.post("/import/prints", summary="导入印花", response_model=schemas.ImportResult)
async def import_prints(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "请上传 .xlsx 或 .xls 文件")
    wb = _parse_wb(await file.read(), file.filename)
    ws = wb["印花"] if "印花" in wb.sheetnames else _first_sheet(wb, file.filename)
    count, errors = _import_prints(ws, db)
    return _result("印花", count, errors)


@router.post("/import/positions", summary="导入位置（JSON/txt）", response_model=schemas.ImportResult)
async def import_positions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    fname = file.filename or ""
    if not fname.endswith((".json", ".txt")):
        raise HTTPException(400, "请上传 JSON/txt 格式的贴图位置字典文件")
    content = await file.read()
    try:
        data = json.loads(content.decode("utf-8"))
    except Exception as e:
        raise HTTPException(400, f"JSON 解析失败: {e}")

    CATEGORY_MAP = {
        "big_position": "大图位置",
        "small_position": "小图位置",
        "combination_position": "组合位置",
    }
    count, errors = 0, []
    for group_key, items in data.items():
        area = CATEGORY_MAP.get(group_key, group_key)
        if not isinstance(items, dict):
            continue
        for pos_name, pos_code in items.items():
            code = _str(str(pos_code))
            name = _str(str(pos_name))
            if not code or not name:
                continue
            try:
                payload = schemas.PositionCreate(code=code, name=name, area=area)
                existing = crud.get_position_by_code(db, code)
                if existing:
                    crud.update_position(db, existing.id, schemas.PositionUpdate(name=name, area=area))
                else:
                    crud.create_position(db, payload)
                count += 1
            except Exception as e:
                errors.append(f"{code} 处理失败: {e}")
    return _result("位置", count, errors)


@router.post("/import/restrictions", summary="导入限定", response_model=schemas.ImportResult)
async def import_restrictions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "请上传 .xlsx 或 .xls 文件")
    wb = _parse_wb(await file.read(), file.filename)
    ws = _first_sheet(wb, file.filename)
    count, errors = _import_restrictions(ws, db)
    return _result("限定", count, errors)


# ── 分模块模版下载 ─────────────────────────────────────

@router.get("/template/styles", summary="下载款式导入模板")
def template_styles(db: Session = Depends(get_db)):
    wb = Workbook()
    ws = wb.active
    ws.title = "款式"
    ws.append(STYLE_HEADERS)
    _apply_header_style(ws)
    samples = crud.get_styles(db, limit=3)
    for s in samples:
        ws.append([
            s.brand_attr, s.attr, s.fabric_type, s.year, s.gender, s.season,
            s.category, s.product_category, s.virtual_category,
            s.product_code, s.code, s.description,
            s.colors_active, s.colors_discontinued, s.color_remark,
            s.sizes, s.size_specs, s.size_remark,
            s.printable_area,
            s.fabric_composition, s.fabric_composition_en, s.hot_wind_composition,
            s.fabric_name, s.fabric_weight, s.blank_weight,
            s.dev_date, s.tag_price, s.premium_tag_price,
            s.exec_standard, s.safety_category, s.product_type,
        ])
    return _stream_wb(wb, "template_styles.xlsx")


@router.get("/template/prints", summary="下载印花导入模板")
def template_prints(db: Session = Depends(get_db)):
    wb = Workbook()
    ws = wb.active
    ws.title = "印花"
    ws.append(PRINT_HEADERS)
    _apply_header_style(ws)
    samples = crud.get_prints(db, limit=3)
    for p in samples:
        ws.append([
            p.name, p.pattern_size, p.pattern_spec, p.craft_attr, p.code,
            p.zwx_style_code, p.zwx_replace_code, p.zwx_replace_style,
            p.jwco_style_code, p.jwco_replace_code, p.jwco_replace_style,
            p.city_style_code, p.city_replace_code, p.city_replace_style,
            p.tangshi_style_code, p.description,
        ])
    return _stream_wb(wb, "template_prints.xlsx")


@router.get("/template/positions", summary="下载位置模板（JSON/txt）")
def template_positions(db: Session = Depends(get_db)):
    """返回与导入格式完全一致的 JSON/txt 文件，取库中实际数据"""
    AREA_KEY = {
        "大图位置": "big_position",
        "小图位置": "small_position",
        "组合位置": "combination_position",
    }
    groups: dict = {}
    for p in crud.get_positions(db, limit=99999):
        key = AREA_KEY.get(p.area or "", p.area or "other")
        groups.setdefault(key, {})[p.name] = p.code
    content = json.dumps(groups, ensure_ascii=False, indent=2).encode("utf-8")
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=template_positions.txt"},
    )


@router.get("/template/restrictions", summary="下载限定导入模板")
def template_restrictions(db: Session = Depends(get_db)):
    wb = Workbook()
    ws = wb.active
    ws.title = "限定"
    ws.append(["白坯款式编码*", "位置名称（空=全禁该款式）", "允许印花编码（逗号分隔，空=不限）"])
    _apply_header_style(ws)
    for r in crud.get_style_position_rules(db, limit=3):
        ws.append([
            r.style.code if r.style else "",
            r.position.name if r.position else "",
            r.allowed_prints or "",
        ])
    for b in crud.get_style_bans(db, limit=1):
        ws.append([b.style.code if b.style else "", "", ""])
    return _stream_wb(wb, "template_restrictions.xlsx")


# ── 导出数据 ──────────────────────────────────────────────
# entities 参数：逗号分隔，支持 styles / prints / positions / rules / bans
# 不传或传 all 时导出全部

_ALL_ENTITIES = ["styles", "prints", "positions", "rules", "bans"]


@router.get("/export", summary="导出数据为Excel（支持选择实体）")
def export_excel(
    entities: Optional[str] = Query(None, description="逗号分隔: styles,prints,positions,rules,bans；不传=全量"),
    db: Session = Depends(get_db),
):
    selected = (
        {e.strip() for e in entities.split(",") if e.strip()}
        if entities and entities.strip() and entities.strip() != "all"
        else set(_ALL_ENTITIES)
    )

    wb = Workbook()
    wb.remove(wb.active)

    if "styles" in selected:
        ws = wb.create_sheet("款式")
        ws.append(STYLE_HEADERS)
        _apply_header_style(ws)
        for s in crud.get_styles(db, limit=99999):
            ws.append([
                s.brand_attr, s.attr, s.fabric_type, s.year, s.gender, s.season,
                s.category, s.product_category, s.virtual_category,
                s.product_code, s.code, s.description,
                s.colors_active, s.colors_discontinued, s.color_remark,
                s.sizes, s.size_specs, s.size_remark,
                s.printable_area,
                s.fabric_composition, s.fabric_composition_en, s.hot_wind_composition,
                s.fabric_name, s.fabric_weight, s.blank_weight,
                s.dev_date, s.tag_price, s.premium_tag_price,
                s.exec_standard, s.safety_category, s.product_type,
            ])

    if "prints" in selected:
        ws = wb.create_sheet("印花")
        ws.append(PRINT_HEADERS)
        _apply_header_style(ws)
        for p in crud.get_prints(db, limit=99999):
            ws.append([
                p.name, p.pattern_size, p.pattern_spec, p.craft_attr, p.code,
                p.zwx_style_code, p.zwx_replace_code, p.zwx_replace_style,
                p.jwco_style_code, p.jwco_replace_code, p.jwco_replace_style,
                p.city_style_code, p.city_replace_code, p.city_replace_style,
                p.tangshi_style_code, p.description,
            ])

    if "positions" in selected:
        ws = wb.create_sheet("位置")
        ws.append(POSITION_HEADERS)
        _apply_header_style(ws)
        for pos in crud.get_positions(db, limit=99999):
            ws.append([pos.code, pos.name, pos.area, pos.description])

    if "rules" in selected:
        ws = wb.create_sheet("限定规则")
        ws.append(["白坯款式编码", "位置名称", "允许印花编码(逗号分隔，空=不限)", "是否启用", "备注"])
        _apply_header_style(ws)
        for r in crud.get_style_position_rules(db, limit=999999):
            ws.append([
                r.style.code if r.style else "",
                r.position.name if r.position else "",
                r.allowed_prints or "",
                1 if r.is_active else 0,
                r.remark,
            ])

    if "bans" in selected:
        ws = wb.create_sheet("全禁款式")
        ws.append(["白坯款式编码", "备注"])
        _apply_header_style(ws)
        for b in crud.get_style_bans(db, limit=999999):
            ws.append([b.style.code if b.style else "", b.remark])

    if not wb.sheetnames:
        raise HTTPException(400, "未选择任何有效的导出实体")

    name = f"export_{selected.pop()}.xlsx" if len(selected) == 1 else "export_all.xlsx"
    return _stream_wb(wb, name)
