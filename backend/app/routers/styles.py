from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/styles", tags=["款式"])


@router.get("/", response_model=List[schemas.StyleOut])
def list_styles(keyword: str = Query("", description="搜索关键词"), skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    return crud.get_styles(db, skip=skip, limit=limit, keyword=keyword)


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
