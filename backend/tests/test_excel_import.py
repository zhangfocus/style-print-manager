import sys
from pathlib import Path

from openpyxl import Workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import models, schemas
from app.crud import create_style_position_rule
from app.database import Base
from app.routers.excel_io import _import_positions_dict, _import_restrictions


def make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def test_restrictions_with_missing_reference_do_not_replace_existing_rules():
    db = make_db()
    try:
        style = models.Style(code="S001")
        position = models.Position(code="P001", name="胸标", area="小图位置")
        print_obj = models.Print(code="PR001", name="现有印花")
        db.add_all([style, position, print_obj])
        db.commit()

        create_style_position_rule(
            db,
            schemas.StylePositionRuleCreate(
                rule_type=3,
                position_code="P001",
                style_codes=["S001"],
                print_codes=["PR001"],
            ),
        )

        wb = Workbook()
        ws = wb.active
        ws.append(["款式", "位置", "印花", "限定款式"])
        ws.append(["S001", "胸标", "MISSING_PRINT", None])

        count, errors, _, _ = _import_restrictions(ws, db)

        assert count == 0
        assert any("印花编码不存在" in error for error in errors)
        rules = db.query(models.StylePositionRule).all()
        assert len(rules) == 1
        assert rules[0].print_ids == str(print_obj.id)
    finally:
        db.close()


def test_position_import_does_not_update_existing_code_name_binding():
    db = make_db()
    try:
        db.add(models.Position(code="P001", name="胸标", area="小图位置"))
        db.commit()

        count, errors, stats = _import_positions_dict(
            {"big_position": {"大图": "P001", "背标": "P002"}},
            db,
        )

        assert count == 1
        assert stats["created"] == 1
        assert any("位置编号 P001 已绑定名称 '胸标'" in error for error in errors)
        assert db.query(models.Position).filter_by(code="P001").one().name == "胸标"
        assert db.query(models.Position).filter_by(code="P002").one().name == "背标"
    finally:
        db.close()
