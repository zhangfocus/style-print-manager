from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Style(Base):
    """款式"""
    __tablename__ = "styles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, nullable=False, index=True, comment="款式编号")
    name = Column(String(128), nullable=False, comment="款式名称")
    category = Column(String(64), nullable=True, comment="品类")
    color = Column(String(64), nullable=True, comment="颜色")
    description = Column(Text, nullable=True, comment="备注")
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
