"""
名称解析辅助函数
提供统一的名称→ID转换和404错误处理
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from .cache import name_cache


def resolve_style_code(style_code: str) -> int:
    """
    根据款式编码获取ID

    Args:
        style_code: 款式编码

    Returns:
        款式ID

    Raises:
        HTTPException(404): 款式编码不存在
    """
    style_id = name_cache.get_style_id_by_code(style_code)
    if style_id is None:
        raise HTTPException(status_code=404, detail=f"款式编码 '{style_code}' 不存在")
    return style_id


def resolve_position_name(position_name: str) -> int:
    """
    根据位置名称获取ID

    Args:
        position_name: 位置名称

    Returns:
        位置ID

    Raises:
        HTTPException(404): 位置名称不存在
    """
    position_id = name_cache.get_position_id_by_name(position_name)
    if position_id is None:
        raise HTTPException(status_code=404, detail=f"位置名称 '{position_name}' 不存在")
    return position_id


def resolve_print_code(print_code: str) -> int:
    """
    根据印花编码获取ID

    Args:
        print_code: 印花编码

    Returns:
        印花ID

    Raises:
        HTTPException(404): 印花编码不存在
    """
    print_id = name_cache.get_print_id_by_code(print_code)
    if print_id is None:
        raise HTTPException(status_code=404, detail=f"印花编码 '{print_code}' 不存在")
    return print_id


def resolve_names_to_ids(style_code: str, position_name: str, print_code: str) -> tuple[int, int, int]:
    """
    批量转换名称为ID

    Args:
        style_code: 款式编码
        position_name: 位置名称
        print_code: 印花编码

    Returns:
        (style_id, position_id, print_id)

    Raises:
        HTTPException(404): 任何一个名称不存在
    """
    style_id = resolve_style_code(style_code)
    position_id = resolve_position_name(position_name)
    print_id = resolve_print_code(print_code)
    return style_id, position_id, print_id
