import io
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

STYLE_HEADERS = ["款式编号*", "款式名称*", "品类", "颜色", "备注"]
PRINT_HEADERS = ["印花编号*", "印花名称*", "图案类型", "色系", "备注"]
POSITION_HEADERS = ["位置编号*", "位置名称*", "区域", "备注"]
RESTRICTION_HEADERS = ["款式编号*", "位置编号*", "印花编号*", "是否启用(1/0)", "备注"]


def _style_header(ws):
    header_fill = PatternFill("solid", fgColor="4472C4")
    header_font = Font(color="FFFFFF", bold=True)
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for col, val in enumerate(ws[1], 1):
        val.fill = header_fill
        val.font = header_font
        val.alignment = Alignment(horizontal="center")
        val.border = border
        ws.column_dimensions[get_column_letter(col)].width = 18


@router.get("/template", summary="下载Excel导入模板")
def download_template():
    wb = Workbook()
    wb.remove(wb.active)

    for sheet_name, headers in [
        (SHEET_STYLE, STYLE_HEADERS),
        (SHEET_PRINT, PRINT_HEADERS),
        (SHEET_POSITION, POSITION_HEADERS),
        (SHEET_RESTRICTION, RESTRICTION_HEADERS),
    ]:
        ws = wb.create_sheet(sheet_name)
        ws.append(headers)
        _style_header(ws)
        # Add example rows
        if sheet_name == SHEET_STYLE:
            ws.append(["ST001", "夏季T恤A款", "T恤", "白色", "主推款"])
            ws.append(["ST002", "夏季T恤B款", "T恤", "黑色", ""])
        elif sheet_name == SHEET_PRINT:
            ws.append(["PT001", "玫瑰花印花", "花卉", "粉色系", ""])
            ws.append(["PT002", "几何图案", "几何", "蓝色系", ""])
        elif sheet_name == SHEET_POSITION:
            ws.append(["PS001", "胸前左", "正面", ""])
            ws.append(["PS002", "后背中", "背面", ""])
        elif sheet_name == SHEET_RESTRICTION:
            ws.append(["ST001", "PS001", "PT001", 1, "推荐搭配"])
            ws.append(["ST001", "PS002", "PT002", 1, ""])

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
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
            if not row[0] and not row[1]:
                continue
            code, name = str(row[0]).strip(), str(row[1]).strip()
            if not code or not name:
                errors.append(f"款式第{row_idx}行：编号和名称不能为空")
                continue
            existing = crud.get_style_by_code(db, code)
            payload = schemas.StyleCreate(
                code=code, name=name,
                category=str(row[2]).strip() if row[2] else None,
                color=str(row[3]).strip() if row[3] else None,
                description=str(row[4]).strip() if row[4] else None,
            )
            if existing:
                crud.update_style(db, existing.id, schemas.StyleUpdate(**{k: v for k, v in payload.model_dump().items() if k != "code"}))
            else:
                crud.create_style(db, payload)
            counts["款式"] += 1

    # ── 印花 ──
    if SHEET_PRINT in wb.sheetnames:
        ws = wb[SHEET_PRINT]
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
            if not row[0] and not row[1]:
                continue
            code, name = str(row[0]).strip(), str(row[1]).strip()
            if not code or not name:
                errors.append(f"印花第{row_idx}行：编号和名称不能为空")
                continue
            existing = crud.get_print_by_code(db, code)
            payload = schemas.PrintCreate(
                code=code, name=name,
                pattern_type=str(row[2]).strip() if row[2] else None,
                color_scheme=str(row[3]).strip() if row[3] else None,
                description=str(row[4]).strip() if row[4] else None,
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
            code, name = str(row[0]).strip(), str(row[1]).strip()
            if not code or not name:
                errors.append(f"位置第{row_idx}行：编号和名称不能为空")
                continue
            existing = crud.get_position_by_code(db, code)
            payload = schemas.PositionCreate(
                code=code, name=name,
                area=str(row[2]).strip() if row[2] else None,
                description=str(row[3]).strip() if row[3] else None,
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
            s_code = str(row[0]).strip() if row[0] else ""
            p_code = str(row[1]).strip() if row[1] else ""
            pt_code = str(row[2]).strip() if row[2] else ""
            if not s_code or not p_code or not pt_code:
                errors.append(f"限定第{row_idx}行：款式、位置、印花编号不能为空")
                continue
            style = crud.get_style_by_code(db, s_code)
            position = crud.get_position_by_code(db, p_code)
            print_item = crud.get_print_by_code(db, pt_code)
            if not style:
                errors.append(f"限定第{row_idx}行：款式编号 {s_code} 不存在，请先导入款式")
                continue
            if not position:
                errors.append(f"限定第{row_idx}行：位置编号 {p_code} 不存在，请先导入位置")
                continue
            if not print_item:
                errors.append(f"限定第{row_idx}行：印花编号 {pt_code} 不存在，请先导入印花")
                continue
            is_active = bool(int(row[3])) if row[3] is not None and str(row[3]).strip() != "" else True
            remark = str(row[4]).strip() if row[4] else None
            # Upsert restriction
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
    return schemas.ImportResult(success=True, message=msg, details={"counts": counts, "errors": errors[:20]})


@router.get("/export", summary="导出全部数据为Excel")
def export_excel(db: Session = Depends(get_db)):
    wb = Workbook()
    wb.remove(wb.active)

    # 款式
    ws = wb.create_sheet(SHEET_STYLE)
    ws.append(STYLE_HEADERS)
    _style_header(ws)
    for s in crud.get_styles(db, limit=99999):
        ws.append([s.code, s.name, s.category, s.color, s.description])

    # 印花
    ws = wb.create_sheet(SHEET_PRINT)
    ws.append(PRINT_HEADERS)
    _style_header(ws)
    for p in crud.get_prints(db, limit=99999):
        ws.append([p.code, p.name, p.pattern_type, p.color_scheme, p.description])

    # 位置
    ws = wb.create_sheet(SHEET_POSITION)
    ws.append(POSITION_HEADERS)
    _style_header(ws)
    for pos in crud.get_positions(db, limit=99999):
        ws.append([pos.code, pos.name, pos.area, pos.description])

    # 限定
    ws = wb.create_sheet(SHEET_RESTRICTION)
    ws.append(RESTRICTION_HEADERS)
    _style_header(ws)
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
