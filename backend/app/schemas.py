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
    rule_type: int = Field(..., description="规则类型: 3=style_position, 2=position_restriction, 1=style_ban")
    position_id: Optional[int] = None
    style_ids: Optional[str] = Field(None, description="款式ID(逗号分隔)")
    print_ids: Optional[str] = Field(None, description="印花ID(逗号分隔)")
    is_active: bool = True


class StylePositionRuleCreate(BaseModel):
    """创建规则时使用 code 而不是 id"""
    rule_type: int = Field(..., description="规则类型: 3=style_position, 2=position_restriction, 1=style_ban")
    position_code: Optional[str] = Field(None, description="位置编码")
    style_codes: Optional[list[str]] = Field(None, description="款式编码列表")
    print_codes: Optional[list[str]] = Field(None, description="印花编码列表")
    is_active: bool = True


class StylePositionRuleUpdate(BaseModel):
    """更新规则时使用 code 而不是 id"""
    position_code: Optional[str] = None
    style_codes: Optional[list[str]] = None
    print_codes: Optional[list[str]] = None
    is_active: Optional[bool] = None


class StylePositionRuleOut(StylePositionRuleBase):
    id: int
    position: Optional[PositionOut] = None
    # 用于前端显示的字段
    style_codes_display: Optional[str] = Field(None, description="款式编码(用于显示)")
    print_codes_display: Optional[str] = Field(None, description="印花编码(用于显示)")
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


# ───── Restriction Query Schemas ─────
class RestrictionCheckRequest(BaseModel):
    """校验款式+位置+印花组合"""
    style_id: int = Field(..., description="款式ID")
    position_id: int = Field(..., description="位置ID")
    print_id: int = Field(..., description="印花ID")


class RestrictionCheckResponse(BaseModel):
    """校验结果"""
    allowed: bool = Field(..., description="是否允许")
    reason: str = Field(..., description="拒绝原因或允许原因")
    rule_type: Optional[str] = Field(None, description="触发的规则类型: style_ban, position_restriction, style_position")
    rule_id: Optional[int] = Field(None, description="触发的规则ID")


class AvailablePositionWithPrints(BaseModel):
    """位置及其可用印花"""
    position_id: int
    position_name: str
    position_code: str
    print_ids: list[int] = Field(default_factory=list, description="可用印花ID列表")
    print_codes: list[str] = Field(default_factory=list, description="可用印花编码列表")
    is_restricted: bool = Field(..., description="是否受限定规则约束")
    reason: str = Field(..., description="限定原因说明")


class AvailableByStyleResponse(BaseModel):
    """款式查询结果"""
    style_id: int
    is_banned: bool = Field(..., description="款式是否被全禁")
    available_positions: list[AvailablePositionWithPrints] = Field(default_factory=list)


# ───── Excel Import Result ─────
class ImportResult(BaseModel):
    success: bool
    message: str
    details: dict = {}
