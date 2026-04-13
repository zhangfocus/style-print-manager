from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ───── Style ─────
class StyleBase(BaseModel):
    code: str = Field(..., description="款式编号")
    name: str = Field(..., description="款式名称")
    category: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class StyleCreate(StyleBase):
    pass


class StyleUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class StyleOut(StyleBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ───── Print ─────
class PrintBase(BaseModel):
    code: str = Field(..., description="印花编号")
    name: str = Field(..., description="印花名称")
    pattern_type: Optional[str] = None
    color_scheme: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class PrintCreate(PrintBase):
    pass


class PrintUpdate(BaseModel):
    name: Optional[str] = None
    pattern_type: Optional[str] = None
    color_scheme: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PrintOut(PrintBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ───── Position ─────
class PositionBase(BaseModel):
    code: str = Field(..., description="位置编号")
    name: str = Field(..., description="位置名称")
    area: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    name: Optional[str] = None
    area: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PositionOut(PositionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ───── Restriction ─────
class RestrictionBase(BaseModel):
    style_id: int
    position_id: int
    print_id: int
    is_active: bool = True
    remark: Optional[str] = None


class RestrictionCreate(RestrictionBase):
    pass


class RestrictionUpdate(BaseModel):
    is_active: Optional[bool] = None
    remark: Optional[str] = None


class RestrictionOut(RestrictionBase):
    id: int
    style: Optional[StyleOut] = None
    position: Optional[PositionOut] = None
    print_item: Optional[PrintOut] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ───── Excel Import Result ─────
class ImportResult(BaseModel):
    success: bool
    message: str
    details: dict = {}
