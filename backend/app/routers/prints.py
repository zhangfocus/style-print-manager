from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/prints", tags=["印花"])


@router.get("/by-ids")
def get_prints_by_ids(ids: str = Query(..., description="逗号分隔的ID列表"), db: Session = Depends(get_db)):
    from .. import models
    id_list = [int(id.strip()) for id in ids.split(',') if id.strip()]
    if not id_list:
        return []
    prints = db.query(models.Print).filter(models.Print.id.in_(id_list)).all()
    return [schemas.PrintOut.model_validate(p) for p in prints]


@router.get("/")
def list_prints(
    keyword: str = Query("", description="搜索关键词"),
    search_field: str = Query("all", description="搜索字段"),
    page: int = 1,
    page_size: int = 10,
    is_active: str | None = None,
    pattern_size: str | None = None,
    pattern_spec: str | None = None,
    craft_attr: str | None = None,
    db: Session = Depends(get_db),
):
    filters = {
        "is_active": is_active,
        "pattern_size": pattern_size,
        "pattern_spec": pattern_spec,
        "craft_attr": craft_attr,
    }
    return crud.get_prints(db, page=page, page_size=page_size, keyword=keyword, search_field=search_field, filters=filters)


@router.get("/filter-options")
def print_filter_options(
    is_active: str | None = None,
    pattern_size: str | None = None,
    pattern_spec: str | None = None,
    craft_attr: str | None = None,
    db: Session = Depends(get_db),
):
    filters = {
        "is_active": is_active,
        "pattern_size": pattern_size,
        "pattern_spec": pattern_spec,
        "craft_attr": craft_attr,
    }
    return crud.get_print_filter_options(db, filters=filters)


@router.get("/{print_id}", response_model=schemas.PrintOut)
def get_print(print_id: int, db: Session = Depends(get_db)):
    obj = crud.get_print(db, print_id)
    if not obj:
        raise HTTPException(status_code=404, detail="印花不存在")
    return obj


@router.post("/", response_model=schemas.PrintOut, status_code=201)
def create_print(data: schemas.PrintCreate, db: Session = Depends(get_db)):
    if crud.get_print_by_code(db, data.code):
        raise HTTPException(status_code=400, detail=f"印花编号 {data.code} 已存在")
    return crud.create_print(db, data)


@router.put("/{print_id}", response_model=schemas.PrintOut)
def update_print(print_id: int, data: schemas.PrintUpdate, db: Session = Depends(get_db)):
    obj = crud.update_print(db, print_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="印花不存在")
    return obj


@router.delete("/{print_id}")
def delete_print(print_id: int, db: Session = Depends(get_db)):
    obj = crud.delete_print(db, print_id)
    if not obj:
        raise HTTPException(status_code=404, detail="印花不存在")
    return {"message": "删除成功"}
