from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/positions", tags=["位置"])


@router.get("/")
def list_positions(keyword: str = Query("", description="搜索关键词"), page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    return crud.get_positions(db, page=page, page_size=page_size, keyword=keyword)


@router.get("/{position_id}", response_model=schemas.PositionOut)
def get_position(position_id: int, db: Session = Depends(get_db)):
    obj = crud.get_position(db, position_id)
    if not obj:
        raise HTTPException(status_code=404, detail="位置不存在")
    return obj


@router.post("/", response_model=schemas.PositionOut, status_code=201)
def create_position(data: schemas.PositionCreate, db: Session = Depends(get_db)):
    if crud.get_position_by_code(db, data.code):
        raise HTTPException(status_code=400, detail=f"位置编号 {data.code} 已存在")
    return crud.create_position(db, data)


@router.put("/{position_id}", response_model=schemas.PositionOut)
def update_position(position_id: int, data: schemas.PositionUpdate, db: Session = Depends(get_db)):
    obj = crud.update_position(db, position_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="位置不存在")
    return obj


@router.delete("/{position_id}")
def delete_position(position_id: int, db: Session = Depends(get_db)):
    obj = crud.delete_position(db, position_id)
    if not obj:
        raise HTTPException(status_code=404, detail="位置不存在")
    return {"message": "删除成功"}
