"""
名称解析缓存模块
提供 name↔id 双向映射缓存，用于快速转换款式编码、位置名称、印花编码与ID
"""
import threading
from typing import Optional
from sqlalchemy.orm import Session
from . import models


class NameCache:
    """名称解析缓存（线程安全）"""

    def __init__(self):
        self._lock = threading.RLock()

        # 款式缓存
        self._style_code_to_id: dict[str, int] = {}
        self._style_id_to_code: dict[int, str] = {}

        # 位置缓存
        self._position_name_to_id: dict[str, int] = {}
        self._position_id_to_name: dict[int, str] = {}

        # 印花缓存
        self._print_code_to_id: dict[str, int] = {}
        self._print_id_to_code: dict[int, str] = {}

    def init_cache(self, db: Session) -> None:
        """初始化缓存（应用启动时调用）"""
        with self._lock:
            try:
                # 加载款式
                styles = db.query(models.Style).filter(models.Style.is_active == True).all()
                self._style_code_to_id = {s.code: s.id for s in styles}
                self._style_id_to_code = {s.id: s.code for s in styles}

                # 加载位置
                positions = db.query(models.Position).filter(models.Position.is_active == True).all()
                self._position_name_to_id = {p.name: p.id for p in positions}
                self._position_id_to_name = {p.id: p.name for p in positions}

                # 加载印花
                prints = db.query(models.Print).filter(models.Print.is_active == True).all()
                self._print_code_to_id = {p.code: p.id for p in prints}
                self._print_id_to_code = {p.id: p.code for p in prints}

                print(f"[NameCache] 缓存初始化完成: {len(styles)} 款式, {len(positions)} 位置, {len(prints)} 印花")
            except Exception as e:
                print(f"[NameCache] 缓存初始化失败: {e}")
                raise

    def refresh_cache(self, db: Session) -> None:
        """刷新缓存（定时任务调用）"""
        with self._lock:
            try:
                # 重新加载所有数据
                styles = db.query(models.Style).filter(models.Style.is_active == True).all()
                self._style_code_to_id = {s.code: s.id for s in styles}
                self._style_id_to_code = {s.id: s.code for s in styles}

                positions = db.query(models.Position).filter(models.Position.is_active == True).all()
                self._position_name_to_id = {p.name: p.id for p in positions}
                self._position_id_to_name = {p.id: p.name for p in positions}

                prints = db.query(models.Print).filter(models.Print.is_active == True).all()
                self._print_code_to_id = {p.code: p.id for p in prints}
                self._print_id_to_code = {p.id: p.code for p in prints}

                print(f"[NameCache] 缓存刷新完成: {len(styles)} 款式, {len(positions)} 位置, {len(prints)} 印花")
            except Exception as e:
                print(f"[NameCache] 缓存刷新失败（保持旧缓存）: {e}")

    # ── 款式查询 ──

    def get_style_id_by_code(self, code: str) -> Optional[int]:
        """根据款式编码获取ID"""
        with self._lock:
            return self._style_code_to_id.get(code)

    def get_style_code_by_id(self, style_id: int) -> Optional[str]:
        """根据款式ID获取编码"""
        with self._lock:
            return self._style_id_to_code.get(style_id)

    # ── 位置查询 ──

    def get_position_id_by_name(self, name: str) -> Optional[int]:
        """根据位置名称获取ID"""
        with self._lock:
            return self._position_name_to_id.get(name)

    def get_position_name_by_id(self, position_id: int) -> Optional[str]:
        """根据位置ID获取名称"""
        with self._lock:
            return self._position_id_to_name.get(position_id)

    # ── 印花查询 ──

    def get_print_id_by_code(self, code: str) -> Optional[int]:
        """根据印花编码获取ID"""
        with self._lock:
            return self._print_code_to_id.get(code)

    def get_print_code_by_id(self, print_id: int) -> Optional[str]:
        """根据印花ID获取编码"""
        with self._lock:
            return self._print_id_to_code.get(print_id)


# 全局缓存实例
name_cache = NameCache()
