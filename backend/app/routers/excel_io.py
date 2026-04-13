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
PRINT_HEADERS = ["印花编号*", "印花名称*", "图案类型", "色系", "备注"]
POSITION_HEADERS = ["位置编号*", "位置名称*", "区域", "备注"]
RESTRICTION_HEADERS = ["白坯款式编码*", "位置编号*", "印花编号*", "是否启用(1/0)", "备注"]


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
    count, errors = 0, []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        if not row[0] and not row[1]:
            continue
        code, name = _str(row[0]), _str(row[1])
        if not code or not name:
            errors.append(f"第{row_idx}行：编号和名称不能为空")
            continue
        payload = schemas.PrintCreate(
            code=code, name=name,
            pattern_type=_str(row[2]),
            color_scheme=_str(row[3]),
            description=_str(row[4]),
        )
        existing = crud.get_print_by_code(db, code)
        if existing:
            crud.update_print(db, existing.id, schemas.PrintUpdate(**{k: v for k, v in payload.model_dump().items() if k != "code"}))
        else:
            crud.create_print(db, payload)
        count += 1
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


def _import_restrictions(ws, db: Session):
    count, errors = 0, []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        if not row[0] and not row[1] and not row[2]:
            continue
        s_code = _str(row[0]) or ""
        p_code = _str(row[1]) or ""
        pt_code = _str(row[2]) or ""
        if not s_code or not p_code or not pt_code:
            errors.append(f"第{row_idx}行：款式、位置、印花编号不能为空")
            continue
        style = crud.get_style_by_code(db, s_code)
        position = crud.get_position_by_code(db, p_code)
        print_item = crud.get_print_by_code(db, pt_code)
        if not style:
            errors.append(f"第{row_idx}行：白坯款式编码 {s_code} 不存在")
            continue
        if not position:
            errors.append(f"第{row_idx}行：位置编号 {p_code} 不存在")
            continue
        if not print_item:
            errors.append(f"第{row_idx}行：印花编号 {pt_code} 不存在")
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
        count += 1
    return count, errors


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


@router.post("/import/positions", summary="导入位置", response_model=schemas.ImportResult)
async def import_positions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "请上传 .xlsx 或 .xls 文件")
    wb = _parse_wb(await file.read(), file.filename)
    ws = wb["位置"] if "位置" in wb.sheetnames else _first_sheet(wb, file.filename)
    count, errors = _import_positions(ws, db)
    return _result("位置", count, errors)


@router.post("/import/restrictions", summary="导入限定", response_model=schemas.ImportResult)
async def import_restrictions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "请上传 .xlsx 或 .xls 文件")
    wb = _parse_wb(await file.read(), file.filename)
    ws = wb["限定"] if "限定" in wb.sheetnames else _first_sheet(wb, file.filename)
    count, errors = _import_restrictions(ws, db)
    return _result("限定", count, errors)


# ── 分模块模版下载 ─────────────────────────────────────

@router.get("/template/styles", summary="下载款式导入模板")
def template_styles():
    wb = Workbook()
    ws = wb.active
    ws.title = "款式"
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
    return _stream_wb(wb, "template_styles.xlsx")


@router.get("/template/prints", summary="下载印花导入模板")
def template_prints():
    wb = Workbook()
    ws = wb.active
    ws.title = "印花"
    ws.append(PRINT_HEADERS)
    _apply_header_style(ws)
    ws.append(["PT001", "玫瑰花印花", "花卉", "粉色系", ""])
    ws.append(["PT002", "几何图案", "几何", "蓝色系", ""])
    return _stream_wb(wb, "template_prints.xlsx")


@router.get("/template/positions", summary="下载位置导入模板")
def template_positions():
    wb = Workbook()
    ws = wb.active
    ws.title = "位置"
    ws.append(POSITION_HEADERS)
    _apply_header_style(ws)
    ws.append(["PS001", "胸前左", "正面", ""])
    ws.append(["PS002", "后背中", "背面", ""])
    return _stream_wb(wb, "template_positions.xlsx")


@router.get("/template/restrictions", summary="下载限定导入模板")
def template_restrictions():
    wb = Workbook()
    ws = wb.active
    ws.title = "限定"
    ws.append(RESTRICTION_HEADERS)
    _apply_header_style(ws)
    ws.append(["通BBH桑蚕丝POLO长T", "PS001", "PT001", 1, "推荐搭配"])
    ws.append(["通BBH桑蚕丝POLO长T", "PS002", "PT001", 1, ""])
    return _stream_wb(wb, "template_restrictions.xlsx")


# ── 导出全量数据 ───────────────────────────────────────

@router.get("/export", summary="导出全部数据为Excel")
def export_excel(db: Session = Depends(get_db)):
    wb = Workbook()
    wb.remove(wb.active)

    ws = wb.create_sheet("款式")
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

    ws = wb.create_sheet("印花")
    ws.append(PRINT_HEADERS)
    _apply_header_style(ws)
    for p in crud.get_prints(db, limit=99999):
        ws.append([p.code, p.name, p.pattern_type, p.color_scheme, p.description])

    ws = wb.create_sheet("位置")
    ws.append(POSITION_HEADERS)
    _apply_header_style(ws)
    for pos in crud.get_positions(db, limit=99999):
        ws.append([pos.code, pos.name, pos.area, pos.description])

    ws = wb.create_sheet("限定")
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

    return _stream_wb(wb, "export.xlsx")
