from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Style(Base):
    """款式"""
    __tablename__ = "styles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(256), unique=True, nullable=False, index=True, comment="白坯款式编码")
    product_code = Column(String(64), nullable=True, index=True, comment="商品款号")
    brand_attr = Column(String(64), nullable=True, comment="品牌属性")
    attr = Column(String(64), nullable=True, comment="属性")
    fabric_type = Column(String(64), nullable=True, comment="面料种类")
    year = Column(Integer, nullable=True, comment="年份")
    gender = Column(String(16), nullable=True, comment="性别")
    season = Column(String(32), nullable=True, comment="季节")
    category = Column(String(64), nullable=True, comment="类目")
    product_category = Column(String(64), nullable=True, comment="商品分类")
    virtual_category = Column(String(64), nullable=True, comment="虚拟分类")
    colors_active = Column(String(512), nullable=True, comment="在售颜色")
    colors_discontinued = Column(String(512), nullable=True, comment="淘汰颜色")
    color_remark = Column(Text, nullable=True, comment="颜色备注")
    sizes = Column(String(256), nullable=True, comment="尺码")
    size_specs = Column(Text, nullable=True, comment="号型")
    size_remark = Column(Text, nullable=True, comment="尺码备注")
    printable_area = Column(String(512), nullable=True, comment="可印花范围")
    fabric_composition = Column(Text, nullable=True, comment="面料成分")
    fabric_composition_en = Column(Text, nullable=True, comment="Fabric Ingredients")
    hot_wind_composition = Column(Text, nullable=True, comment="热风成分")
    fabric_name = Column(String(128), nullable=True, comment="面料名称")
    fabric_weight = Column(String(64), nullable=True, comment="面料克重")
    blank_weight = Column(Float, nullable=True, comment="白坯重量(kg)")
    dev_date = Column(Date, nullable=True, comment="开发时间")
    tag_price = Column(Float, nullable=True, comment="吊牌价")
    premium_tag_price = Column(Float, nullable=True, comment="高价品牌吊牌价")
    exec_standard = Column(String(128), nullable=True, comment="执行标准")
    safety_category = Column(String(128), nullable=True, comment="安全技术类别")
    product_type = Column(String(128), nullable=True, comment="产品分类")
    description = Column(Text, nullable=True, comment="款式备注")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Print(Base):
    """印花"""
    __tablename__ = "prints"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, nullable=False, index=True, comment="商品编码")
    name = Column(String(128), nullable=False, comment="图案名称")
    pattern_size = Column(String(32), nullable=True, comment="图案大小")
    pattern_spec = Column(String(16), nullable=True, comment="图案规格")
    craft_attr = Column(String(64), nullable=True, comment="工艺属性")
    zwx_style_code = Column(String(64), nullable=True, comment="真维斯款号")
    zwx_replace_code = Column(String(64), nullable=True, comment="真维斯替换编码")
    zwx_replace_style = Column(String(64), nullable=True, comment="真维斯替换款号")
    jwco_style_code = Column(String(64), nullable=True, comment="JWCO款号")
    jwco_replace_code = Column(String(64), nullable=True, comment="JWCO替换编码")
    jwco_replace_style = Column(String(64), nullable=True, comment="JWCO替换款号")
    city_style_code = Column(String(64), nullable=True, comment="CITY款号")
    city_replace_code = Column(String(64), nullable=True, comment="CITY替换编码")
    city_replace_style = Column(String(64), nullable=True, comment="CITY替换款号")
    tangshi_style_code = Column(String(64), nullable=True, comment="唐狮款号")
    description = Column(Text, nullable=True, comment="备注")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Position(Base):
    """位置"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, nullable=False, index=True, comment="位置编号")
    name = Column(String(128), nullable=False, comment="位置名称")
    area = Column(String(64), nullable=True, comment="区域")
    description = Column(Text, nullable=True, comment="备注")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class StylePositionRule(Base):
    """
    统一限定规则表
    支持三种规则类型：
    1. style_ban (1): 款式全禁 - style_ids有值，position_id和print_ids为NULL
    2. position_restriction (2): 位置限定 - position_id有值，style_ids和print_ids有值
    3. style_position (3): 款式位置限定 - position_id有值，style_ids有值，print_ids有值或NULL
    """
    __tablename__ = "style_position_rules"

    id = Column(Integer, primary_key=True, index=True)

    # 规则类型：3=style_position, 2=position_restriction, 1=style_ban
    rule_type = Column(Integer, nullable=False, index=True, comment="规则类型: 3=style_position, 2=position_restriction, 1=style_ban")

    # 位置ID（外键，级联删除）
    position_id = Column(Integer, ForeignKey("positions.id", ondelete="CASCADE"), nullable=True, index=True, comment="位置ID")

    # 款式ID列表（逗号分隔的ID字符串）
    style_ids = Column(Text, nullable=True, comment="款式ID(逗号分隔)，如'1,2,3'")

    # 印花ID列表（逗号分隔的ID字符串）
    print_ids = Column(Text, nullable=True, comment="印花ID(逗号分隔)，如'10,20,30'")

    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # 关系
    position = relationship("Position")

    # 索引
    __table_args__ = (
        Index('idx_rule_type_position', 'rule_type', 'position_id'),
    )
