"""测试名称解析辅助函数"""
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.name_resolver import (
    resolve_names_to_ids,
    resolve_style_code,
    resolve_position_name,
    resolve_print_code
)
from app.models import Style, Position, Print
from app.cache import get_name_cache


@pytest.fixture
def sample_data(db: Session):
    """创建测试数据"""
    style = Style(style_code="TEST001", style_name="测试款式")
    position = Position(position_name="测试位置", position_code="TP1")
    print_item = Print(print_code="TPRINT001", print_name="测试印花")

    db.add_all([style, position, print_item])
    db.commit()

    # 初始化缓存
    cache = get_name_cache()
    cache.init_cache(db)

    return {
        "style": style,
        "position": position,
        "print": print_item
    }


def test_resolve_names_to_ids_success(sample_data):
    """测试成功解析所有名称"""
    style_id, position_id, print_id = resolve_names_to_ids(
        "TEST001", "测试位置", "TPRINT001"
    )

    assert style_id == sample_data["style"].id
    assert position_id == sample_data["position"].id
    assert print_id == sample_data["print"].id


def test_resolve_names_to_ids_style_not_found(sample_data):
    """测试款式编码不存在"""
    with pytest.raises(HTTPException) as exc_info:
        resolve_names_to_ids("NONEXISTENT", "测试位置", "TPRINT001")

    assert exc_info.value.status_code == 404
    assert "款式编码 'NONEXISTENT' 不存在" in exc_info.value.detail


def test_resolve_names_to_ids_position_not_found(sample_data):
    """测试位置名称不存在"""
    with pytest.raises(HTTPException) as exc_info:
        resolve_names_to_ids("TEST001", "不存在的位置", "TPRINT001")

    assert exc_info.value.status_code == 404
    assert "位置名称 '不存在的位置' 不存在" in exc_info.value.detail


def test_resolve_names_to_ids_print_not_found(sample_data):
    """测试印花编码不存在"""
    with pytest.raises(HTTPException) as exc_info:
        resolve_names_to_ids("TEST001", "测试位置", "NONEXISTENT")

    assert exc_info.value.status_code == 404
    assert "印花编码 'NONEXISTENT' 不存在" in exc_info.value.detail


def test_resolve_style_code_success(sample_data):
    """测试成功解析款式编码"""
    style_id = resolve_style_code("TEST001")
    assert style_id == sample_data["style"].id


def test_resolve_style_code_not_found(sample_data):
    """测试款式编码不存在"""
    with pytest.raises(HTTPException) as exc_info:
        resolve_style_code("NONEXISTENT")

    assert exc_info.value.status_code == 404
    assert "款式编码 'NONEXISTENT' 不存在" in exc_info.value.detail


def test_resolve_position_name_success(sample_data):
    """测试成功解析位置名称"""
    position_id = resolve_position_name("测试位置")
    assert position_id == sample_data["position"].id


def test_resolve_position_name_not_found(sample_data):
    """测试位置名称不存在"""
    with pytest.raises(HTTPException) as exc_info:
        resolve_position_name("不存在的位置")

    assert exc_info.value.status_code == 404
    assert "位置名称 '不存在的位置' 不存在" in exc_info.value.detail


def test_resolve_print_code_success(sample_data):
    """测试成功解析印花编码"""
    print_id = resolve_print_code("TPRINT001")
    assert print_id == sample_data["print"].id


def test_resolve_print_code_not_found(sample_data):
    """测试印花编码不存在"""
    with pytest.raises(HTTPException) as exc_info:
        resolve_print_code("NONEXISTENT")

    assert exc_info.value.status_code == 404
    assert "印花编码 'NONEXISTENT' 不存在" in exc_info.value.detail
