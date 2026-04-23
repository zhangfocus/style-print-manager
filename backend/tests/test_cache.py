"""测试名称解析缓存模块"""
import pytest
from sqlalchemy.orm import Session
from app.cache import NameCache
from app.models import Style, Position, Print


@pytest.fixture
def name_cache():
    """创建缓存实例"""
    return NameCache()


@pytest.fixture
def sample_data(db: Session):
    """创建测试数据"""
    # 创建款式
    style1 = Style(style_code="TEST001", style_name="测试款式1")
    style2 = Style(style_code="TEST002", style_name="测试款式2")
    db.add_all([style1, style2])
    db.flush()

    # 创建位置
    pos1 = Position(position_name="测试位置1", position_code="TP1")
    pos2 = Position(position_name="测试位置2", position_code="TP2")
    db.add_all([pos1, pos2])
    db.flush()

    # 创建印花
    print1 = Print(print_code="TPRINT001", print_name="测试印花1")
    print2 = Print(print_code="TPRINT002", print_name="测试印花2")
    db.add_all([print1, print2])
    db.commit()

    return {
        "styles": [style1, style2],
        "positions": [pos1, pos2],
        "prints": [print1, print2]
    }


def test_init_cache(name_cache: NameCache, db: Session, sample_data):
    """测试缓存初始化"""
    name_cache.init_cache(db)

    # 验证款式映射
    assert name_cache.get_style_id("TEST001") == sample_data["styles"][0].id
    assert name_cache.get_style_code(sample_data["styles"][0].id) == "TEST001"

    # 验证位置映射
    assert name_cache.get_position_id("测试位置1") == sample_data["positions"][0].id
    assert name_cache.get_position_name(sample_data["positions"][0].id) == "测试位置1"

    # 验证印花映射
    assert name_cache.get_print_id("TPRINT001") == sample_data["prints"][0].id
    assert name_cache.get_print_code(sample_data["prints"][0].id) == "TPRINT001"


def test_get_nonexistent_names(name_cache: NameCache, db: Session, sample_data):
    """测试获取不存在的名称"""
    name_cache.init_cache(db)

    assert name_cache.get_style_id("NONEXISTENT") is None
    assert name_cache.get_position_id("不存在的位置") is None
    assert name_cache.get_print_id("NONEXISTENT") is None


def test_get_nonexistent_ids(name_cache: NameCache, db: Session, sample_data):
    """测试获取不存在的ID"""
    name_cache.init_cache(db)

    assert name_cache.get_style_code(99999) is None
    assert name_cache.get_position_name(99999) is None
    assert name_cache.get_print_code(99999) is None


def test_refresh_cache(name_cache: NameCache, db: Session, sample_data):
    """测试缓存刷新"""
    # 初始化缓存
    name_cache.init_cache(db)
    old_style_count = len(name_cache._style_code_to_id)

    # 添加新款式
    new_style = Style(style_code="TEST003", style_name="新款式")
    db.add(new_style)
    db.commit()

    # 刷新缓存
    name_cache.refresh_cache(db)

    # 验证新数据已加载
    assert len(name_cache._style_code_to_id) == old_style_count + 1
    assert name_cache.get_style_id("TEST003") == new_style.id


def test_cache_singleton(db: Session):
    """测试缓存单例模式"""
    from app.cache import get_name_cache

    cache1 = get_name_cache()
    cache2 = get_name_cache()

    assert cache1 is cache2
