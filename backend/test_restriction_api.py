"""
测试限定规则查询API
运行前确保后端服务已启动

使用方法:
  python test_restriction_api.py                           # 交互式测试
  python test_restriction_api.py --auto                    # 自动测试（使用第一个款式/位置/印花）
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8001"


def list_styles(limit=10):
    """列出款式"""
    response = requests.get(f"{BASE_URL}/api/styles", params={"page": 1, "page_size": limit})
    if response.status_code == 200:
        return response.json().get("items", [])
    return []


def list_positions(limit=20):
    """列出位置"""
    response = requests.get(f"{BASE_URL}/api/positions", params={"page": 1, "page_size": limit})
    if response.status_code == 200:
        return response.json().get("items", [])
    return []


def list_prints(limit=10):
    """列出印花"""
    response = requests.get(f"{BASE_URL}/api/prints", params={"page": 1, "page_size": limit})
    if response.status_code == 200:
        return response.json().get("items", [])
    return []


def test_check_restriction(style_code=None, position_name=None, print_code=None):
    """测试校验接口"""
    print("\n=== 测试 POST /api/restrictions/check ===")

    # 如果没有提供参数，交互式输入
    if not style_code:
        styles = list_styles()
        if not styles:
            print("[ERROR] 没有可用的款式")
            return False
        print("\n可用款式:")
        for i, s in enumerate(styles[:5], 1):
            print(f"  {i}. {s['code']}")
        style_code = input("请输入款式编码（或直接回车使用第一个）: ").strip() or styles[0]['code']

    if not position_name:
        positions = list_positions()
        if not positions:
            print("[ERROR] 没有可用的位置")
            return False
        print("\n可用位置:")
        for i, p in enumerate(positions[:10], 1):
            print(f"  {i}. {p['name']}")
        position_name = input("请输入位置名称（或直接回车使用第一个）: ").strip() or positions[0]['name']

    if not print_code:
        prints = list_prints()
        if not prints:
            print("[ERROR] 没有可用的印花")
            return False
        print("\n可用印花:")
        for i, p in enumerate(prints[:5], 1):
            print(f"  {i}. {p['code']}")
        print_code = input("请输入印花编码（或直接回车使用第一个）: ").strip() or prints[0]['code']

    print(f"\n查询: 款式={style_code}, 位置={position_name}, 印花={print_code}")

    # 直接使用名称调用接口
    payload = {
        "style_code": style_code,
        "position_name": position_name,
        "print_code": print_code
    }

    response = requests.post(f"{BASE_URL}/api/restrictions/check", json=payload)
    print(f"\n状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"结果: {'[OK] 允许' if data['allowed'] else '[REJECT] 拒绝'}")
        print(f"原因: {data['reason']}")
        if data['rule_type']:
            print(f"规则类型: {data['rule_type']}")
            print(f"规则ID: {data['rule_id']}")
    else:
        print(f"错误: {response.text}")

    return response.status_code == 200


def test_available_by_style(style_code=None):
    """测试款式查询接口"""
    print("\n=== 测试 GET /api/restrictions/available-by-style ===")

    # 如果没有提供参数，交互式输入
    if not style_code:
        styles = list_styles()
        if not styles:
            print("[ERROR] 没有可用的款式")
            return False
        print("\n可用款式:")
        for i, s in enumerate(styles[:5], 1):
            print(f"  {i}. {s['code']}")
        style_code = input("请输入款式编码（或直接回车使用第一个）: ").strip() or styles[0]['code']

    print(f"\n查询: 款式={style_code}")

    # 直接使用名称调用接口
    response = requests.get(f"{BASE_URL}/api/restrictions/available-by-style", params={"style_code": style_code})
    print(f"\n状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"款式编码: {data['style_code']}")
        print(f"是否全禁: {data['is_banned']}")
        print(f"可用位置数量: {len(data['available_positions'])}")

        if data['available_positions']:
            print(f"\n显示前5个位置详情:")
            for pos in data['available_positions'][:5]:
                print(f"\n  位置: {pos['position_name']} ({pos['position_code']})")
                print(f"  可用印花数量: {len(pos['print_codes'])}")
                print(f"  是否受限: {pos.get('is_restricted', False)}")
                print(f"  原因: {pos.get('reason', 'N/A')}")
                if pos['print_codes']:
                    print(f"  印花示例: {', '.join(pos['print_codes'][:3])}")
    else:
        print(f"错误: {response.text}")

    return response.status_code == 200


def test_pattern_suffix_rule():
    """测试印花code后缀规则"""
    print("\n=== 测试印花code后缀规则 ===")

    # 获取测试数据
    styles = list_styles()
    positions = list_positions()

    if not styles or not positions:
        print("[ERROR] 缺少测试数据")
        return False

    style_code = styles[0]['code']

    # 找到小图位置和大图位置
    small_position = None
    large_position = None

    for pos in positions:
        # 通过API获取位置详情来确定area
        response = requests.get(f"{BASE_URL}/api/positions", params={"search": pos['name'], "page": 1, "page_size": 1})
        if response.status_code == 200:
            items = response.json().get("items", [])
            if items:
                area = items[0].get('area', '')
                if '小图' in area and not small_position:
                    small_position = pos['name']
                elif '大图' in area and not large_position:
                    large_position = pos['name']

        if small_position and large_position:
            break

    if not small_position or not large_position:
        print("[WARNING] 未找到小图位置或大图位置，跳过后缀规则测试")
        return True

    print(f"使用款式: {style_code}")
    print(f"小图位置: {small_position}")
    print(f"大图位置: {large_position}")

    all_passed = True

    # 测试用例1: X结尾印花 + 小图位置 = 允许
    print("\n[测试1] X结尾印花 + 小图位置 (应该允许)")
    payload = {
        "style_code": style_code,
        "position_name": small_position,
        "print_code": "测试印花X"
    }
    response = requests.post(f"{BASE_URL}/api/restrictions/check", json=payload)
    if response.status_code == 200:
        data = response.json()
        if data['allowed']:
            print("  ✓ 通过: 允许X结尾印花贴小图位置")
        else:
            print(f"  ✗ 失败: 应该允许但被拒绝 - {data['reason']}")
            all_passed = False
    else:
        print(f"  ✗ 失败: API错误 {response.status_code}")
        all_passed = False

    # 测试用例2: X结尾印花 + 大图位置 = 拒绝
    print("\n[测试2] X结尾印花 + 大图位置 (应该拒绝)")
    payload = {
        "style_code": style_code,
        "position_name": large_position,
        "print_code": "测试印花X"
    }
    response = requests.post(f"{BASE_URL}/api/restrictions/check", json=payload)
    if response.status_code == 200:
        data = response.json()
        if not data['allowed'] and data['rule_type'] == 'pattern_suffix':
            print(f"  ✓ 通过: 正确拒绝 - {data['reason']}")
        else:
            print(f"  ✗ 失败: 应该拒绝但允许了")
            all_passed = False
    else:
        print(f"  ✗ 失败: API错误 {response.status_code}")
        all_passed = False

    # 测试用例3: C结尾印花 + 大图位置 = 允许
    print("\n[测试3] C结尾印花 + 大图位置 (应该允许)")
    payload = {
        "style_code": style_code,
        "position_name": large_position,
        "print_code": "测试印花C"
    }
    response = requests.post(f"{BASE_URL}/api/restrictions/check", json=payload)
    if response.status_code == 200:
        data = response.json()
        if data['allowed']:
            print("  ✓ 通过: 允许C结尾印花贴大图位置")
        else:
            print(f"  ✗ 失败: 应该允许但被拒绝 - {data['reason']}")
            all_passed = False
    else:
        print(f"  ✗ 失败: API错误 {response.status_code}")
        all_passed = False

    # 测试用例4: C结尾印花 + 小图位置 = 拒绝
    print("\n[测试4] C结尾印花 + 小图位置 (应该拒绝)")
    payload = {
        "style_code": style_code,
        "position_name": small_position,
        "print_code": "测试印花C"
    }
    response = requests.post(f"{BASE_URL}/api/restrictions/check", json=payload)
    if response.status_code == 200:
        data = response.json()
        if not data['allowed'] and data['rule_type'] == 'pattern_suffix':
            print(f"  ✓ 通过: 正确拒绝 - {data['reason']}")
        else:
            print(f"  ✗ 失败: 应该拒绝但允许了")
            all_passed = False
    else:
        print(f"  ✗ 失败: API错误 {response.status_code}")
        all_passed = False

    # 测试用例5: 特殊印花 + 任意位置 = 允许
    print("\n[测试5] 特殊印花(纯色) + 大图位置 (应该允许)")
    payload = {
        "style_code": style_code,
        "position_name": large_position,
        "print_code": "纯色"
    }
    response = requests.post(f"{BASE_URL}/api/restrictions/check", json=payload)
    if response.status_code == 200:
        data = response.json()
        if data['allowed']:
            print("  ✓ 通过: 允许特殊印花贴任意位置")
        else:
            print(f"  ✗ 失败: 应该允许但被拒绝 - {data['reason']}")
            all_passed = False
    else:
        print(f"  ✗ 失败: API错误 {response.status_code}")
        all_passed = False

    # 测试用例6: available-prints 应该过滤掉不符合后缀规则的印花
    print("\n[测试6] available-prints 应该根据位置过滤印花")
    response = requests.get(f"{BASE_URL}/api/restrictions/available-prints",
                           params={"style_code": style_code, "position_name": small_position})
    if response.status_code == 200:
        data = response.json()
        print_codes = data.get('print_codes', [])
        # 检查是否有C/D结尾的印花（不应该有）
        invalid_prints = [p for p in print_codes if p not in ['纯色', '自搭', '福袋'] and p and p[-1].upper() in ['C', 'D']]
        if not invalid_prints:
            print(f"  ✓ 通过: 小图位置正确过滤了C/D结尾印花 (共{len(print_codes)}个可用印花)")
        else:
            print(f"  ✗ 失败: 小图位置包含了不应该出现的C/D结尾印花: {invalid_prints}")
            all_passed = False
    else:
        print(f"  ✗ 失败: API错误 {response.status_code}")
        all_passed = False

    # 测试用例7: available-positions 应该过滤掉不符合后缀规则的位置
    print("\n[测试7] available-positions 应该根据印花过滤位置")
    response = requests.get(f"{BASE_URL}/api/restrictions/available-positions",
                           params={"style_code": style_code, "print_code": "测试印花X"})
    if response.status_code == 200:
        data = response.json()
        position_names = data.get('position_names', [])
        # X结尾印花不应该包含大图位置
        if large_position not in position_names:
            print(f"  ✓ 通过: X结尾印花正确排除了大图位置 (共{len(position_names)}个可用位置)")
        else:
            print(f"  ✗ 失败: X结尾印花包含了不应该出现的大图位置")
            all_passed = False
    else:
        print(f"  ✗ 失败: API错误 {response.status_code}")
        all_passed = False

    # 测试用例8: available-by-style 应该为每个位置过滤印花
    print("\n[测试8] available-by-style 应该为每个位置过滤印花")
    response = requests.get(f"{BASE_URL}/api/restrictions/available-by-style",
                           params={"style_code": style_code})
    if response.status_code == 200:
        data = response.json()
        positions = data.get('available_positions', [])

        # 找到小图位置和大图位置的结果
        small_pos_result = next((p for p in positions if p['position_name'] == small_position), None)
        large_pos_result = next((p for p in positions if p['position_name'] == large_position), None)

        test_passed = True
        if small_pos_result:
            invalid_prints = [p for p in small_pos_result['print_codes']
                            if p not in ['纯色', '自搭', '福袋'] and p and p[-1].upper() in ['C', 'D']]
            if invalid_prints:
                print(f"  ✗ 失败: 小图位置包含了C/D结尾印花: {invalid_prints}")
                test_passed = False

        if large_pos_result:
            invalid_prints = [p for p in large_pos_result['print_codes']
                            if p not in ['纯色', '自搭', '福袋'] and p and p[-1].upper() == 'X']
            if invalid_prints:
                print(f"  ✗ 失败: 大图位置包含了X结尾印花: {invalid_prints}")
                test_passed = False

        if test_passed:
            print(f"  ✓ 通过: 每个位置的印花列表都正确应用了后缀规则")
        else:
            all_passed = False
    else:
        print(f"  ✗ 失败: API错误 {response.status_code}")
        all_passed = False

    return all_passed


def test_existing_apis(style_code=None, position_name=None, print_code=None):
    """测试现有的两个接口"""
    print("\n=== 测试现有接口 ===")

    if not style_code:
        styles = list_styles()
        style_code = styles[0]['code'] if styles else None

    if not position_name:
        positions = list_positions()
        position_name = positions[0]['name'] if positions else None

    if not print_code:
        prints = list_prints()
        print_code = prints[0]['code'] if prints else None

    if not all([style_code, position_name, print_code]):
        print("[ERROR] 缺少测试数据")
        return False

    # 测试 available-prints (直接使用名称)
    response1 = requests.get(f"{BASE_URL}/api/restrictions/available-prints",
                            params={"style_code": style_code, "position_name": position_name})
    print(f"available-prints (款式+位置→印花) 状态码: {response1.status_code}")
    if response1.status_code == 200:
        data = response1.json()
        print(f"  可用: {data.get('available', False)}")
        print(f"  可用印花数量: {len(data.get('print_codes', []))}")
        print(f"  是否受限: {data.get('is_restricted', False)}")
        print(f"  原因: {data.get('reason', 'N/A')}")

    # 测试 available-positions (直接使用名称)
    response2 = requests.get(f"{BASE_URL}/api/restrictions/available-positions",
                            params={"style_code": style_code, "print_code": print_code})
    print(f"available-positions (款式+印花→位置) 状态码: {response2.status_code}")
    if response2.status_code == 200:
        data = response2.json()
        print(f"  可用: {data.get('available', False)}")
        print(f"  可用位置数量: {len(data.get('position_names', []))}")
        print(f"  是否受限: {data.get('is_restricted', False)}")
        print(f"  原因: {data.get('reason', 'N/A')}")

    return response1.status_code == 200 and response2.status_code == 200


if __name__ == "__main__":
    print("开始测试限定规则查询API...")
    print(f"后端地址: {BASE_URL}")

    # 检查是否自动模式
    auto_mode = "--auto" in sys.argv

    try:
        # 测试服务是否可用
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print("[ERROR] 后端服务未启动或不可访问")
            exit(1)

        print("[OK] 后端服务正常\n")

        if auto_mode:
            print("【自动测试模式】使用第一个可用的款式/位置/印花\n")
            # 获取第一个可用数据
            styles = list_styles()
            positions = list_positions()
            prints = list_prints()

            if not styles or not positions or not prints:
                print("[ERROR] 缺少测试数据")
                exit(1)

            style_code = styles[0]['code']
            position_name = positions[0]['name']
            print_code = prints[0]['code']

            # 运行测试
            result1 = test_check_restriction(style_code, position_name, print_code)
            result2 = test_available_by_style(style_code)
            result3 = test_existing_apis(style_code, position_name, print_code)
            result4 = test_pattern_suffix_rule()

            print("\n=== 测试结果汇总 ===")
            print(f"check 接口: {'[OK] 通过' if result1 else '[FAIL] 失败'}")
            print(f"available-by-style 接口: {'[OK] 通过' if result2 else '[FAIL] 失败'}")
            print(f"现有接口: {'[OK] 通过' if result3 else '[FAIL] 失败'}")
            print(f"后缀规则测试: {'[OK] 通过' if result4 else '[FAIL] 失败'}")

            if result1 and result2 and result3 and result4:
                print("\n[SUCCESS] 所有测试通过！")
            else:
                print("\n[WARNING] 部分测试失败")
        else:
            print("【交互式测试模式】请根据提示输入\n")
            print("提示: 可以使用 --auto 参数进行自动测试\n")

            # 交互式测试
            while True:
                print("\n" + "="*50)
                print("请选择测试接口:")
                print("  1. POST /api/restrictions/check (校验款式+位置+印花)")
                print("  2. GET /api/restrictions/available-by-style (查询款式可用位置和印花)")
                print("  3. 测试现有接口 (available-prints 和 available-positions)")
                print("  4. 测试印花code后缀规则")
                print("  5. 运行所有测试")
                print("  0. 退出")
                print("="*50)

                choice = input("\n请输入选项 (0-5): ").strip()

                if choice == "0":
                    print("退出测试")
                    break
                elif choice == "1":
                    test_check_restriction()
                elif choice == "2":
                    test_available_by_style()
                elif choice == "3":
                    test_existing_apis()
                elif choice == "4":
                    test_pattern_suffix_rule()
                elif choice == "5":
                    result1 = test_check_restriction()
                    result2 = test_available_by_style()
                    result3 = test_existing_apis()
                    result4 = test_pattern_suffix_rule()

                    print("\n=== 测试结果 ===")
                    print(f"check 接口: {'[OK] 通过' if result1 else '[FAIL] 失败'}")
                    print(f"available-by-style 接口: {'[OK] 通过' if result2 else '[FAIL] 失败'}")
                    print(f"现有接口: {'[OK] 通过' if result3 else '[FAIL] 失败'}")
                    print(f"后缀规则测试: {'[OK] 通过' if result4 else '[FAIL] 失败'}")

                    if result1 and result2 and result3 and result4:
                        print("\n[SUCCESS] 所有测试通过！")
                    else:
                        print("\n[WARNING] 部分测试失败")
                    break
                else:
                    print("[ERROR] 无效选项，请重新输入")

    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到后端服务，请确保服务已启动")
    except KeyboardInterrupt:
        print("\n\n测试已中断")
    except Exception as e:
        print(f"[ERROR] 测试过程中出错: {e}")
