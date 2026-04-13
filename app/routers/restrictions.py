from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/restrictions", tags=["限定"])


@router.get("/", response_model=List[schemas.RestrictionOut])
def list_restrictions(
    style_id: Optional[int] = Query(None),
    position_id: Optional[int] = Query(None),
    print_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 500,
    db: Session = Depends(get_db),
):
    return crud.get_restrictions(db, skip=skip, limit=limit, style_id=style_id, position_id=position_id, print_id=print_id)


@router.get("/{restriction_id}", response_model=schemas.RestrictionOut)
def get_restriction(restriction_id: int, db: Session = Depends(get_db)):
    obj = crud.get_restriction(db, restriction_id)
    if not obj:
        raise HTTPException(status_code=404, detail="限定记录不存在")
    return obj


@router.post("/", response_model=schemas.RestrictionOut, status_code=201)
def create_restriction(data: schemas.RestrictionCreate, db: Session = Depends(get_db)):
    # Check foreign keys exist
    if not crud.get_style(db, data.style_id):
        raise HTTPException(status_code=400, detail=f"款式 ID {data.style_id} 不存在")
    if not crud.get_position(db, data.position_id):
        raise HTTPException(status_code=400, detail=f"位置 ID {data.position_id} 不存在")
    if not crud.get_print(db, data.print_id):
        raise HTTPException(status_code=400, detail=f"印花 ID {data.print_id} 不存在")
    try:
        return crud.create_restriction(db, data)
    except Exception:
        raise HTTPException(status_code=400, detail="该限定组合已存在")


@router.put("/{restriction_id}", response_model=schemas.RestrictionOut)
def update_restriction(restriction_id: int, data: schemas.RestrictionUpdate, db: Session = Depends(get_db)):
    obj = crud.update_restriction(db, restriction_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="限定记录不存在")
    return obj


@router.delete("/{restriction_id}")
def delete_restriction(restriction_id: int, db: Session = Depends(get_db)):
    obj = crud.delete_restriction(db, restriction_id)
    if not obj:
        raise HTTPException(status_code=404, detail="限定记录不存在")
    return {"message": "删除成功"}
