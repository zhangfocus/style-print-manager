import io
import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from openpyxl import load_workbook, Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .. import crud, schemas, models
from ..database import get_db

router = APIRouter(prefix="/api/excel", tags=["Excel导入导出"])

SHEET_STYLE = "款式"
SHEET_PRINT = "印花"
SHEET_POSITION = "位置"
SHEET_RESTRICTION = "限定"

# 款式表与 Excel 模版一致的 31 列
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

PRINT_HEADERS = ["印花编号*", "印花名称*", "图案类型", "色系", "备注"]
POSITION_HEADERS = ["位置编号*", "位置名称*", "区域", "备注"]
RESTRICTION_HEADERS = ["白坯款式编码*", "位置编号*", "印花编号*", "是否启用(1/0)", "备注"]

# Excel serial date → Python date（1900-01-01 = 1, off-by-2 bug corrected）
def _excel_date(val):
    if val is None:
        return None
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val if isinstance(val, datetime.date) else val.date()
    try:
        n = int(val)
        return (datetime.date(1899, 12, 30) + datetime.timedelta(days=n))
    except Exception:
        return None


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


def _str(v):
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


@router.get("/template", summary="下载Excel导入模板")
def download_template():
    wb = Workbook()
    wb.remove(wb.active)

    # 款式 sheet
    ws = wb.create_sheet(SHEET_STYLE)
    ws.append(STYLE_HEADERS)
    _apply_header_style(ws)
    ws.append([
        "基本盘", "外采", "针织", 2024, "男", "春秋",
        "上装", "T恤", "T恤类",
        "FX24M003", "通BBH桑蚕丝POLO长T",
        "",
        "黑/白/海蓝/杏", "", "",
        "M/L/XL/2XL/3XL", "M=170/88A,L=175/92A", "",
        "可印花",
        "67.3%聚酯纤维+29.9%棉+2.8%桑蚕丝",
        "67.3% polyester+29.9% cotton+2.8% mulberry silk",
        "67.3%聚酯纤维+29.9%棉+2.8%桑蚕丝",
        "", "", 0.305,
        45498, 199, 599,
        "GB/T 22849-2024", "GB18401-2010 B类", "直接接触皮肤的纺织产品",
    ])

    # 印花 sheet
    ws = wb.create_sheet(SHEET_PRINT)
    ws.append(PRINT_HEADERS)
    _apply_header_style(ws)
    ws.append(["PT001", "玫瑰花印花", "花卉", "粉色系", ""])

    # 位置 sheet
    ws = wb.create_sheet(SHEET_POSITION)
    ws.append(POSITION_HEADERS)
    _apply_header_style(ws)
    ws.append(["PS001", "胸前左", "正面", ""])

    # 限定 sheet
    ws = wb.create_sheet(SHEET_RESTRICTION)
    ws.append(RESTRICTION_HEADERS)
    _apply_header_style(ws)
    ws.append(["通BBH桑蚕丝POLO长T", "PS001", "PT001", 1, "推荐搭配"])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=import_template.xlsx"},
    )


@router.post("/import", summary="从Excel导入数据", response_model=schemas.ImportResult)
async def import_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "请上传 .xlsx 或 .xls 格式的文件")

    content = await file.read()
    try:
        wb = load_workbook(io.BytesIO(content), data_only=True)
    except Exception as e:
        raise HTTPException(400, f"文件解析失败: {e}")

    counts = {"款式": 0, "印花": 0, "位置": 0, "限定": 0}
    errors = []

    # ── 款式 ──
    if SHEET_STYLE in wb.sheetnames:
        ws = wb[SHEET_STYLE]
        headers = [cell.value for cell in ws[1]]

        def col(row_vals, name):
            try:
                return row_vals[headers.index(name)]
            except (ValueError, IndexError):
                return None

        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
            # 白坯款式编码 是唯一键（必填）
            code_val = col(row, "白坯款式编码*") or col(row, "白坯款式编码")
            if not code_val:
                continue
            code = str(code_val).strip()
            if not code:
                errors.append(f"款式第{row_idx}行：白坯款式编码不能为空")
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
                    update_data = {k: v for k, v in payload.model_dump().items() if k != "code"}
                    crud.update_style(db, existing.id, schemas.StyleUpdate(**update_data))
                else:
                    crud.create_style(db, payload)
                counts["款式"] += 1
            except Exception as e:
                errors.append(f"款式第{row_idx}行处理失败: {e}")
                if len(errors) >= 20:
                    break

    # ── 印花 ──
    if SHEET_PRINT in wb.sheetnames:
        ws = wb[SHEET_PRINT]
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
            if not row[0] and not row[1]:
                continue
            code, name = _str(row[0]), _str(row[1])
            if not code or not name:
                errors.append(f"印花第{row_idx}行：编号和名称不能为空")
                continue
            existing = crud.get_print_by_code(db, code)
            payload = schemas.PrintCreate(
                code=code, name=name,
                pattern_type=_str(row[2]),
                color_scheme=_str(row[3]),
                description=_str(row[4]),
            )
            if existing:
                crud.update_print(db, existing.id, schemas.PrintUpdate(**{k: v for k, v in payload.model_dump().items() if k != "code"}))
            else:
                crud.create_print(db, payload)
            counts["印花"] += 1

    # ── 位置 ──
    if SHEET_POSITION in wb.sheetnames:
        ws = wb[SHEET_POSITION]
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
            if not row[0] and not row[1]:
                continue
            code, name = _str(row[0]), _str(row[1])
            if not code or not name:
                errors.append(f"位置第{row_idx}行：编号和名称不能为空")
                continue
            existing = crud.get_position_by_code(db, code)
            payload = schemas.PositionCreate(
                code=code, name=name,
                area=_str(row[2]),
                description=_str(row[3]),
            )
            if existing:
                crud.update_position(db, existing.id, schemas.PositionUpdate(**{k: v for k, v in payload.model_dump().items() if k != "code"}))
            else:
                crud.create_position(db, payload)
            counts["位置"] += 1

    # ── 限定 ──
    if SHEET_RESTRICTION in wb.sheetnames:
        ws = wb[SHEET_RESTRICTION]
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
            if not row[0] and not row[1] and not row[2]:
                continue
            s_code = _str(row[0]) or ""
            p_code = _str(row[1]) or ""
            pt_code = _str(row[2]) or ""
            if not s_code or not p_code or not pt_code:
                errors.append(f"限定第{row_idx}行：款式、位置、印花编号不能为空")
                continue
            style = crud.get_style_by_code(db, s_code)
            position = crud.get_position_by_code(db, p_code)
            print_item = crud.get_print_by_code(db, pt_code)
            if not style:
                errors.append(f"限定第{row_idx}行：白坯款式编码 {s_code} 不存在")
                continue
            if not position:
                errors.append(f"限定第{row_idx}行：位置编号 {p_code} 不存在")
                continue
            if not print_item:
                errors.append(f"限定第{row_idx}行：印花编号 {pt_code} 不存在")
                continue
            is_active = bool(int(row[3])) if row[3] is not None and str(row[3]).strip() != "" else True
            remark = _str(row[4])
            existing = db.query(models.Restriction).filter(
                models.Restriction.style_id == style.id,
                models.Restriction.position_id == position.id,
                models.Restriction.print_id == print_item.id,
            ).first()
            if existing:
                crud.update_restriction(db, existing.id, schemas.RestrictionUpdate(is_active=is_active, remark=remark))
            else:
                crud.create_restriction(db, schemas.RestrictionCreate(
                    style_id=style.id, position_id=position.id, print_id=print_item.id,
                    is_active=is_active, remark=remark,
                ))
            counts["限定"] += 1

    msg = f"导入完成：款式 {counts['款式']} 条，印花 {counts['印花']} 条，位置 {counts['位置']} 条，限定 {counts['限定']} 条"
    if errors:
        msg += f"；有 {len(errors)} 条错误"
    return schemas.ImportResult(success=not errors, message=msg, details={"counts": counts, "errors": errors[:20]})


@router.get("/export", summary="导出全部数据为Excel")
def export_excel(db: Session = Depends(get_db)):
    wb = Workbook()
    wb.remove(wb.active)

    # 款式
    ws = wb.create_sheet(SHEET_STYLE)
    ws.append(STYLE_HEADERS)
    _apply_header_style(ws)
    for s in crud.get_styles(db, limit=99999):
        ws.append([
            s.brand_attr, s.attr, s.fabric_type, s.year, s.gender, s.season,
            s.category, s.product_category, s.virtual_category,
            s.product_code, s.code,
            s.description,
            s.colors_active, s.colors_discontinued, s.color_remark,
            s.sizes, s.size_specs, s.size_remark,
            s.printable_area,
            s.fabric_composition, s.fabric_composition_en, s.hot_wind_composition,
            s.fabric_name, s.fabric_weight, s.blank_weight,
            s.dev_date, s.tag_price, s.premium_tag_price,
            s.exec_standard, s.safety_category, s.product_type,
        ])

    # 印花
    ws = wb.create_sheet(SHEET_PRINT)
    ws.append(PRINT_HEADERS)
    _apply_header_style(ws)
    for p in crud.get_prints(db, limit=99999):
        ws.append([p.code, p.name, p.pattern_type, p.color_scheme, p.description])

    # 位置
    ws = wb.create_sheet(SHEET_POSITION)
    ws.append(POSITION_HEADERS)
    _apply_header_style(ws)
    for pos in crud.get_positions(db, limit=99999):
        ws.append([pos.code, pos.name, pos.area, pos.description])

    # 限定
    ws = wb.create_sheet(SHEET_RESTRICTION)
    ws.append(RESTRICTION_HEADERS)
    _apply_header_style(ws)
    for r in crud.get_restrictions(db, limit=999999):
        ws.append([
            r.style.code if r.style else "",
            r.position.code if r.position else "",
            r.print_item.code if r.print_item else "",
            1 if r.is_active else 0,
            r.remark,
        ])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=export.xlsx"},
    )
