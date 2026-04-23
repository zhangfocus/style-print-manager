"""
单元测试：印花后缀规则校验模块
"""
import pytest
from app.pattern_suffix_validator import (
    check_pattern_suffix_rule,
    filter_patterns_by_suffix,
    filter_positions_by_suffix,
    SPECIAL_PATTERNS,
)


class TestCheckPatternSuffixRule:
    """测试 check_pattern_suffix_rule 函数"""

    def test_special_patterns_allowed_everywhere(self):
        """特殊印花可以贴任何位置"""
        for special in SPECIAL_PATTERNS:
            allowed, msg = check_pattern_suffix_rule(special, "小图位置")
            assert allowed is True
            assert msg == ""

            allowed, msg = check_pattern_suffix_rule(special, "大图位置")
            assert allowed is True
            assert msg == ""

    def test_x_suffix_only_small_position(self):
        """X结尾的印花只能贴小图位置"""
        allowed, msg = check_pattern_suffix_rule("尤斯樱桃X", "小图位置")
        assert allowed is True
        assert msg == ""

        allowed, msg = check_pattern_suffix_rule("尤斯樱桃X", "大图位置")
        assert allowed is False
        assert "只能贴小图位置" in msg

    def test_c_suffix_only_large_position(self):
        """C结尾的印花只能贴大图位置"""
        allowed, msg = check_pattern_suffix_rule("大奥利给C", "大图位置")
        assert allowed is True
        assert msg == ""

        allowed, msg = check_pattern_suffix_rule("大奥利给C", "小图位置")
        assert allowed is False
        assert "只能贴大图位置" in msg

    def test_d_suffix_only_large_position(self):
        """D结尾的印花只能贴大图位置"""
        allowed, msg = check_pattern_suffix_rule("蓝色小熊D", "大图位置")
        assert allowed is True
        assert msg == ""

        allowed, msg = check_pattern_suffix_rule("蓝色小熊D", "小图位置")
        assert allowed is False
        assert "只能贴大图位置" in msg

    def test_invalid_suffix_raises_error(self):
        """不符合格式的印花code抛出异常"""
        with pytest.raises(ValueError, match="格式不合法"):
            check_pattern_suffix_rule("无效印花A", "小图位置")

        with pytest.raises(ValueError, match="格式不合法"):
            check_pattern_suffix_rule("无效印花B", "大图位置")

    def test_empty_pattern_code_raises_error(self):
        """空印花code抛出异常"""
        with pytest.raises(ValueError, match="不能为空"):
            check_pattern_suffix_rule("", "小图位置")

    def test_combined_position_skipped(self):
        """组合位置跳过检查"""
        allowed, msg = check_pattern_suffix_rule("尤斯樱桃X", "组合位置")
        assert allowed is True
        assert msg == ""

        allowed, msg = check_pattern_suffix_rule("大奥利给C", "组合位置")
        assert allowed is True
        assert msg == ""

    def test_case_sensitive_suffix(self):
        """后缀检查区分大小写"""
        # 小写x不是有效后缀
        with pytest.raises(ValueError, match="格式不合法"):
            check_pattern_suffix_rule("尤斯樱桃x", "小图位置")

        with pytest.raises(ValueError, match="格式不合法"):
            check_pattern_suffix_rule("大奥利给c", "大图位置")

        with pytest.raises(ValueError, match="格式不合法"):
            check_pattern_suffix_rule("蓝色小熊d", "大图位置")


class TestFilterPatternsBySuffix:
    """测试 filter_patterns_by_suffix 函数"""

    def test_filter_for_small_position(self):
        """小图位置只保留X结尾和特殊印花"""
        patterns = ["尤斯樱桃X", "大奥利给C", "蓝色小熊D", "纯色", "自搭", "福袋"]
        filtered = filter_patterns_by_suffix(patterns, "小图位置")
        assert set(filtered) == {"尤斯樱桃X", "纯色", "自搭", "福袋"}

    def test_filter_for_large_position(self):
        """大图位置只保留C/D结尾和特殊印花"""
        patterns = ["尤斯樱桃X", "大奥利给C", "蓝色小熊D", "纯色", "自搭", "福袋"]
        filtered = filter_patterns_by_suffix(patterns, "大图位置")
        assert set(filtered) == {"大奥利给C", "蓝色小熊D", "纯色", "自搭", "福袋"}

    def test_filter_for_combined_position(self):
        """组合位置不过滤"""
        patterns = ["尤斯樱桃X", "大奥利给C", "蓝色小熊D", "纯色"]
        filtered = filter_patterns_by_suffix(patterns, "组合位置")
        assert filtered == patterns

    def test_filter_skips_invalid_patterns(self):
        """过滤时跳过不符合格式的印花"""
        patterns = ["尤斯樱桃X", "无效印花A", "大奥利给C", "无效印花B"]
        filtered = filter_patterns_by_suffix(patterns, "小图位置")
        assert filtered == ["尤斯樱桃X"]

    def test_empty_list(self):
        """空列表返回空列表"""
        filtered = filter_patterns_by_suffix([], "小图位置")
        assert filtered == []


class TestFilterPositionsBySuffix:
    """测试 filter_positions_by_suffix 函数"""

    def test_x_suffix_only_small_positions(self):
        """X结尾的印花只保留小图位置"""
        positions = [
            ("胸标", "小图位置"),
            ("大图", "大图位置"),
            ("裤标", "小图位置"),
            ("背标", "大图位置"),
        ]
        filtered = filter_positions_by_suffix(positions, "尤斯樱桃X")
        assert set(filtered) == {"胸标", "裤标"}

    def test_c_suffix_only_large_positions(self):
        """C结尾的印花只保留大图位置"""
        positions = [
            ("胸标", "小图位置"),
            ("大图", "大图位置"),
            ("裤标", "小图位置"),
            ("背标", "大图位置"),
        ]
        filtered = filter_positions_by_suffix(positions, "大奥利给C")
        assert set(filtered) == {"大图", "背标"}

    def test_d_suffix_only_large_positions(self):
        """D结尾的印花只保留大图位置"""
        positions = [
            ("胸标", "小图位置"),
            ("大图", "大图位置"),
            ("裤标", "小图位置"),
            ("背标", "大图位置"),
        ]
        filtered = filter_positions_by_suffix(positions, "蓝色小熊D")
        assert set(filtered) == {"大图", "背标"}

    def test_special_patterns_all_positions(self):
        """特殊印花保留所有位置"""
        positions = [
            ("胸标", "小图位置"),
            ("大图", "大图位置"),
            ("裤标", "小图位置"),
            ("背标", "大图位置"),
        ]
        for special in SPECIAL_PATTERNS:
            filtered = filter_positions_by_suffix(positions, special)
            assert set(filtered) == {"胸标", "大图", "裤标", "背标"}

    def test_invalid_pattern_skipped(self):
        """不符合格式的印花被跳过"""
        positions = [
            ("胸标", "小图位置"),
            ("大图", "大图位置"),
        ]
        filtered = filter_positions_by_suffix(positions, "无效印花A")
        assert filtered == []

    def test_empty_pattern_skipped(self):
        """空印花code被跳过"""
        positions = [
            ("胸标", "小图位置"),
            ("大图", "大图位置"),
        ]
        filtered = filter_positions_by_suffix(positions, "")
        assert filtered == []

    def test_empty_positions_list(self):
        """空位置列表返回空列表"""
        filtered = filter_positions_by_suffix([], "尤斯樱桃X")
        assert filtered == []

    def test_combined_positions_included(self):
        """组合位置会被包含在结果中（因为跳过检查）"""
        positions = [
            ("胸标", "小图位置"),
            ("组合1", "组合位置"),
            ("大图", "大图位置"),
        ]
        # X结尾的印花，组合位置会通过检查
        filtered = filter_positions_by_suffix(positions, "尤斯樱桃X")
        assert "组合1" in filtered
        assert "胸标" in filtered
        assert "大图" not in filtered
