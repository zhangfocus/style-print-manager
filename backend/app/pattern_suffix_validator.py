"""
印花code后缀规则校验模块

硬性全局规则：
- X结尾的印花只能贴小图位置
- C/D结尾的印花只能贴大图位置
- 特殊印花（纯色/自搭/福袋）不受限制
- 组合位置跳过检查
"""

# 特殊印花code（不受后缀规则限制）
SPECIAL_PATTERNS = {"纯色", "自搭", "福袋"}

# 位置大小分类
SMALL_POSITION_AREA = "小图位置"
LARGE_POSITION_AREA = "大图位置"
COMBO_POSITION_AREA = "组合位置"

# 印花后缀
SUFFIX_X = "X"
SUFFIX_C = "C"
SUFFIX_D = "D"


def check_pattern_suffix_rule(pattern_code: str, position_area: str) -> tuple[bool, str]:
    """
    检查印花code后缀与位置大小是否匹配

    Args:
        pattern_code: 印花编码
        position_area: 位置区域（小图位置/大图位置/组合位置）

    Returns:
        (是否允许, 错误信息)
        - 如果允许，返回 (True, "")
        - 如果不允许，返回 (False, "明确的错误信息")

    Raises:
        ValueError: 如果印花code格式不合法
    """
    # 组合位置跳过检查
    if position_area == COMBO_POSITION_AREA:
        return True, ""

    # 特殊印花不受限制
    if pattern_code in SPECIAL_PATTERNS:
        return True, ""

    # 检查印花code后缀
    if not pattern_code:
        raise ValueError(f"印花code不能为空")

    last_char = pattern_code[-1]

    # X结尾：只能贴小图位置
    if last_char == SUFFIX_X:
        if position_area == SMALL_POSITION_AREA:
            return True, ""
        elif position_area == LARGE_POSITION_AREA:
            return False, f"印花'{pattern_code}'只能贴小图位置，不能贴大图位置"
        else:
            raise ValueError(f"未知的位置区域: {position_area}")

    # C/D结尾：只能贴大图位置
    elif last_char in (SUFFIX_C, SUFFIX_D):
        if position_area == LARGE_POSITION_AREA:
            return True, ""
        elif position_area == SMALL_POSITION_AREA:
            return False, f"印花'{pattern_code}'只能贴大图位置，不能贴小图位置"
        else:
            raise ValueError(f"未知的位置区域: {position_area}")

    # 其他格式：报错
    else:
        raise ValueError(
            f"印花code '{pattern_code}' 格式不合法，必须以X/C/D结尾或为特殊印花（纯色/自搭/福袋）"
        )


def filter_patterns_by_suffix(pattern_codes: list[str], position_area: str) -> list[str]:
    """
    根据位置大小过滤印花列表

    Args:
        pattern_codes: 印花编码列表
        position_area: 位置区域（小图位置/大图位置/组合位置）

    Returns:
        过滤后的印花编码列表
    """
    # 组合位置不过滤
    if position_area == COMBO_POSITION_AREA:
        return pattern_codes

    result = []
    for code in pattern_codes:
        try:
            allowed, _ = check_pattern_suffix_rule(code, position_area)
            if allowed:
                result.append(code)
        except ValueError:
            # 格式不合法的印花跳过
            continue

    return result


def filter_positions_by_suffix(
    positions: list[tuple[str, str]],
    pattern_code: str
) -> list[str]:
    """
    根据印花后缀过滤位置列表

    Args:
        positions: 位置列表，每个元素为 (position_name, position_area)
        pattern_code: 印花编码

    Returns:
        过滤后的位置名称列表
    """
    result = []
    for position_name, position_area in positions:
        try:
            allowed, _ = check_pattern_suffix_rule(pattern_code, position_area)
            if allowed:
                result.append(position_name)
        except ValueError:
            # 格式不合法的印花或位置跳过
            continue

    return result
