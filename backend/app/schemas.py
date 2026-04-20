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
    code: str = Field(..., description="商品编码（唯一）")
    name: str = Field(..., description="图案名称")
    pattern_size: Optional[str] = None
    pattern_spec: Optional[str] = None
    craft_attr: Optional[str] = None
    zwx_style_code: Optional[str] = None
    zwx_replace_code: Optional[str] = None
    zwx_replace_style: Optional[str] = None
    jwco_style_code: Optional[str] = None
    jwco_replace_code: Optional[str] = None
    jwco_replace_style: Optional[str] = None
    city_style_code: Optional[str] = None
    city_replace_code: Optional[str] = None
    city_replace_style: Optional[str] = None
    tangshi_style_code: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class PrintCreate(PrintBase):
    pass


class PrintUpdate(BaseModel):
    name: Optional[str] = None
    pattern_size: Optional[str] = None
    pattern_spec: Optional[str] = None
    craft_attr: Optional[str] = None
    zwx_style_code: Optional[str] = None
    zwx_replace_code: Optional[str] = None
    zwx_replace_style: Optional[str] = None
    jwco_style_code: Optional[str] = None
    jwco_replace_code: Optional[str] = None
    jwco_replace_style: Optional[str] = None
    city_style_code: Optional[str] = None
    city_replace_code: Optional[str] = None
    city_replace_style: Optional[str] = None
    tangshi_style_code: Optional[str] = None
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


# ───── StylePositionRule (统一限定规则) ─────
class StylePositionRuleBase(BaseModel):
    rule_type: str = Field(..., description="规则类型: style_position|position_restriction|style_ban")
    style_id: Optional[int] = None
    position_id: Optional[int] = None
    print_id: Optional[int] = None
    allowed_print_ids: Optional[str] = Field(None, description="允许印花ID(逗号分隔)，null=不限")
    allowed_style_ids: Optional[str] = Field(None, description="允许款式ID(逗号分隔)")
    is_active: bool = True
    remark: Optional[str] = None


class StylePositionRuleCreate(StylePositionRuleBase):
    pass


class StylePositionRuleUpdate(BaseModel):
    allowed_print_ids: Optional[str] = None
    allowed_style_ids: Optional[str] = None
    is_active: Optional[bool] = None
    remark: Optional[str] = None


class StylePositionRuleOut(StylePositionRuleBase):
    id: int
    style: Optional[StyleOut] = None
    position: Optional[PositionOut] = None
    print_obj: Optional[PrintOut] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ───── 兼容旧接口的 Schema (StyleBan 已合并到 StylePositionRule) ─────
class StyleBanBase(BaseModel):
    style_id: int
    remark: Optional[str] = None


class StyleBanCreate(StyleBanBase):
    pass


class StyleBanUpdate(BaseModel):
    remark: Optional[str] = None


class StyleBanOut(StyleBanBase):
    id: int
    style: Optional[StyleOut] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ───── Excel Import Result ─────
class ImportResult(BaseModel):
    success: bool
    message: str
    details: dict = {}
