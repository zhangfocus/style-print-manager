from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


# ───── Style ─────
class StyleBase(BaseModel):
    code: str = Field(..., description="白坯款式编码（唯一）")
    product_code: Optional[str] = Field(None, description="商品款号")
    brand_attr: Optional[str] = None
    attr: Optional[str] = None
    fabric_type: Optional[str] = None
    year: Optional[int] = None
    gender: Optional[str] = None
    season: Optional[str] = None
    category: Optional[str] = None
    product_category: Optional[str] = None
    virtual_category: Optional[str] = None
    colors_active: Optional[str] = None
    colors_discontinued: Optional[str] = None
    color_remark: Optional[str] = None
    sizes: Optional[str] = None
    size_specs: Optional[str] = None
    size_remark: Optional[str] = None
    printable_area: Optional[str] = None
    fabric_composition: Optional[str] = None
    fabric_composition_en: Optional[str] = None
    hot_wind_composition: Optional[str] = None
    fabric_name: Optional[str] = None
    fabric_weight: Optional[str] = None
    blank_weight: Optional[float] = None
    dev_date: Optional[date] = None
    tag_price: Optional[float] = None
    premium_tag_price: Optional[float] = None
    exec_standard: Optional[str] = None
    safety_category: Optional[str] = None
    product_type: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class StyleCreate(StyleBase):
    pass


class StyleUpdate(BaseModel):
    product_code: Optional[str] = None
    brand_attr: Optional[str] = None
    attr: Optional[str] = None
    fabric_type: Optional[str] = None
    year: Optional[int] = None
    gender: Optional[str] = None
    season: Optional[str] = None
    category: Optional[str] = None
    product_category: Optional[str] = None
    virtual_category: Optional[str] = None
    colors_active: Optional[str] = None
    colors_discontinued: Optional[str] = None
    color_remark: Optional[str] = None
    sizes: Optional[str] = None
    size_specs: Optional[str] = None
    size_remark: Optional[str] = None
    printable_area: Optional[str] = None
    fabric_composition: Optional[str] = None
    fabric_composition_en: Optional[str] = None
    hot_wind_composition: Optional[str] = None
    fabric_name: Optional[str] = None
    fabric_weight: Optional[str] = None
    blank_weight: Optional[float] = None
    dev_date: Optional[date] = None
    tag_price: Optional[float] = None
    premium_tag_price: Optional[float] = None
    exec_standard: Optional[str] = None
    safety_category: Optional[str] = None
    product_type: Optional[str] = None
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
