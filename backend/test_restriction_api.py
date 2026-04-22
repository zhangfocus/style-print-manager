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


def get_style_id_by_code(code: str) -> int:
    """通过款式编码获取ID"""
    response = requests.get(f"{BASE_URL}/api/styles", params={"keyword": code, "page": 1, "page_size": 10})
    if response.status_code == 200:
        items = response.json().get("items", [])
        for item in items:
            if item["code"] == code:
                return item["id"]
    return None


def get_position_id_by_name(name: str) -> int:
    """通过位置名称获取ID"""
    response = requests.get(f"{BASE_URL}/api/positions", params={"keyword": name, "page": 1, "page_size": 50})
    if response.status_code == 200:
        items = response.json().get("items", [])
        for item in items:
            if item["name"] == name:
                return item["id"]
    return None


def get_print_id_by_code(code: str) -> int:
    """通过印花编码获取ID"""
    response = requests.get(f"{BASE_URL}/api/prints", params={"keyword": code, "page": 1, "page_size": 10})
    if response.status_code == 200:
        items = response.json().get("items", [])
        for item in items:
            if item["code"] == code:
                return item["id"]
    return None


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

    # 转换为ID
    print(f"\n查询: 款式={style_code}, 位置={position_name}, 印花={print_code}")

    style_id = get_style_id_by_code(style_code)
    position_id = get_position_id_by_name(position_name)
    print_id = get_print_id_by_code(print_code)

    if not style_id:
        print(f"[ERROR] 找不到款式: {style_code}")
        return False
    if not position_id:
        print(f"[ERROR] 找不到位置: {position_name}")
        return False
    if not print_id:
        print(f"[ERROR] 找不到印花: {print_code}")
        return False

    print(f"转换后ID: style_id={style_id}, position_id={position_id}, print_id={print_id}")

    # 调用接口
    payload = {
        "style_id": style_id,
        "position_id": position_id,
        "print_id": print_id
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

    style_id = get_style_id_by_code(style_code)
    if not style_id:
        print(f"[ERROR] 找不到款式: {style_code}")
        return False

    print(f"转换后ID: style_id={style_id}")

    response = requests.get(f"{BASE_URL}/api/restrictions/available-by-style", params={"style_id": style_id})
    print(f"\n状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"款式ID: {data['style_id']}")
        print(f"是否全禁: {data['is_banned']}")
        print(f"可用位置数量: {len(data['available_positions'])}")

        if data['available_positions']:
            print(f"\n显示前5个位置详情:")
            for pos in data['available_positions'][:5]:
                print(f"\n  位置: {pos['position_name']} ({pos['position_code']})")
                print(f"  可用印花数量: {len(pos['print_ids'])}")
                print(f"  是否受限: {pos['is_restricted']}")
                print(f"  原因: {pos['reason']}")
                if pos['print_codes']:
                    print(f"  印花示例: {', '.join(pos['print_codes'][:3])}")
    else:
        print(f"错误: {response.text}")

    return response.status_code == 200


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

    style_id = get_style_id_by_code(style_code)
    position_id = get_position_id_by_name(position_name)
    print_id = get_print_id_by_code(print_code)

    # 测试 available-prints
    response1 = requests.get(f"{BASE_URL}/api/restrictions/available-prints",
                            params={"style_id": style_id, "position_id": position_id})
    print(f"available-prints (款式+位置→印花) 状态码: {response1.status_code}")
    if response1.status_code == 200:
        data = response1.json()
        print(f"  可用印花数量: {len(data.get('print_ids', []))}")

    # 测试 available-positions
    response2 = requests.get(f"{BASE_URL}/api/restrictions/available-positions",
                            params={"style_id": style_id, "print_id": print_id})
    print(f"available-positions (款式+印花→位置) 状态码: {response2.status_code}")
    if response2.status_code == 200:
        data = response2.json()
        print(f"  可用位置数量: {len(data.get('position_ids', []))}")

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
                print("  4. 运行所有测试")
                print("  0. 退出")
                print("="*50)

                choice = input("\n请输入选项 (0-4): ").strip()

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
                    result1 = test_check_restriction()
                    result2 = test_available_by_style()
                    result3 = test_existing_apis()

                    print("\n=== 测试结果 ===")
                    print(f"check 接口: {'[OK] 通过' if result1 else '[FAIL] 失败'}")
                    print(f"available-by-style 接口: {'[OK] 通过' if result2 else '[FAIL] 失败'}")
                    print(f"现有接口: {'[OK] 通过' if result3 else '[FAIL] 失败'}")

                    if result1 and result2 and result3:
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
