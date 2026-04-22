from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/styles", tags=["款式"])


@router.get("/by-ids")
def get_styles_by_ids(ids: str = Query(..., description="逗号分隔的ID列表"), db: Session = Depends(get_db)):
    from .. import models
    id_list = [int(id.strip()) for id in ids.split(',') if id.strip()]
    if not id_list:
        return []
    styles = db.query(models.Style).filter(models.Style.id.in_(id_list)).all()
    return [schemas.StyleOut.model_validate(s) for s in styles]


@router.get("/")
def list_styles(keyword: str = Query("", description="搜索关键词"), page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    return crud.get_styles(db, page=page, page_size=page_size, keyword=keyword)


@router.get("/{style_id}", response_model=schemas.StyleOut)
def get_style(style_id: int, db: Session = Depends(get_db)):
    obj = crud.get_style(db, style_id)
    if not obj:
        raise HTTPException(status_code=404, detail="款式不存在")
    return obj


@router.post("/", response_model=schemas.StyleOut, status_code=201)
def create_style(data: schemas.StyleCreate, db: Session = Depends(get_db)):
    if crud.get_style_by_code(db, data.code):
        raise HTTPException(status_code=400, detail=f"款式编号 {data.code} 已存在")
    return crud.create_style(db, data)


@router.put("/{style_id}", response_model=schemas.StyleOut)
def update_style(style_id: int, data: schemas.StyleUpdate, db: Session = Depends(get_db)):
    obj = crud.update_style(db, style_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="款式不存在")
    return obj


@router.delete("/{style_id}")
def delete_style(style_id: int, db: Session = Depends(get_db)):
    obj = crud.delete_style(db, style_id)
    if not obj:
        raise HTTPException(status_code=404, detail="款式不存在")
    return {"message": "删除成功"}
