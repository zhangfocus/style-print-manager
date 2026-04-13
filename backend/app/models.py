from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Style(Base):
    """款式"""
    __tablename__ = "styles"

    id = Column(Integer, primary_key=True, index=True)
    # 白坯款式编码 — 唯一标识
    code = Column(String(256), unique=True, nullable=False, index=True, comment="白坯款式编码")
    # 商品款号
    product_code = Column(String(64), nullable=True, index=True, comment="商品款号")
    # 基础分类属性
    brand_attr = Column(String(64), nullable=True, comment="品牌属性")
    attr = Column(String(64), nullable=True, comment="属性")
    fabric_type = Column(String(64), nullable=True, comment="面料种类")
    year = Column(Integer, nullable=True, comment="年份")
    gender = Column(String(16), nullable=True, comment="性别")
    season = Column(String(32), nullable=True, comment="季节")
    category = Column(String(64), nullable=True, comment="类目")
    product_category = Column(String(64), nullable=True, comment="商品分类")
    virtual_category = Column(String(64), nullable=True, comment="虚拟分类")
    # 颜色 / 尺码
    colors_active = Column(String(512), nullable=True, comment="在售颜色")
    colors_discontinued = Column(String(512), nullable=True, comment="淘汰颜色")
    color_remark = Column(Text, nullable=True, comment="颜色备注")
    sizes = Column(String(256), nullable=True, comment="尺码")
    size_specs = Column(Text, nullable=True, comment="号型")
    size_remark = Column(Text, nullable=True, comment="尺码备注")
    # 印花相关
    printable_area = Column(String(512), nullable=True, comment="可印花范围")
    # 面料
    fabric_composition = Column(Text, nullable=True, comment="面料成分")
    fabric_composition_en = Column(Text, nullable=True, comment="Fabric Ingredients")
    hot_wind_composition = Column(Text, nullable=True, comment="热风成分")
    fabric_name = Column(String(128), nullable=True, comment="面料名称")
    fabric_weight = Column(String(64), nullable=True, comment="面料克重")
    blank_weight = Column(Float, nullable=True, comment="白坯重量(kg)")
    # 商业信息
    dev_date = Column(Date, nullable=True, comment="开发时间")
    tag_price = Column(Float, nullable=True, comment="吊牌价")
    premium_tag_price = Column(Float, nullable=True, comment="高价品牌吊牌价")
    exec_standard = Column(String(128), nullable=True, comment="执行标准")
    safety_category = Column(String(128), nullable=True, comment="安全技术类别")
    product_type = Column(String(128), nullable=True, comment="产品分类")
    # 备注 / 状态
    description = Column(Text, nullable=True, comment="款式备注")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    restrictions = relationship("Restriction", back_populates="style", cascade="all, delete-orphan")


class Print(Base):
    """印花"""
    __tablename__ = "prints"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, nullable=False, index=True, comment="印花编号")
    name = Column(String(128), nullable=False, comment="印花名称")
    pattern_type = Column(String(64), nullable=True, comment="图案类型")
    color_scheme = Column(String(64), nullable=True, comment="色系")
    description = Column(Text, nullable=True, comment="备注")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    restrictions = relationship("Restriction", back_populates="print_item", cascade="all, delete-orphan")


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

    restrictions = relationship("Restriction", back_populates="position", cascade="all, delete-orphan")


class Restriction(Base):
    """限定：指定款式+位置下允许使用的印花"""
    __tablename__ = "restrictions"

    id = Column(Integer, primary_key=True, index=True)
    style_id = Column(Integer, ForeignKey("styles.id", ondelete="CASCADE"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id", ondelete="CASCADE"), nullable=False)
    print_id = Column(Integer, ForeignKey("prints.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True, comment="是否启用")
    remark = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    style = relationship("Style", back_populates="restrictions")
    position = relationship("Position", back_populates="restrictions")
    print_item = relationship("Print", back_populates="restrictions")

    __table_args__ = (
        UniqueConstraint("style_id", "position_id", "print_id", name="uq_style_position_print"),
    )
