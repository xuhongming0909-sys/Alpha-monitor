"""
AI-SUMMARY: 数据字段端到端验证器 - 支持HTTP和直连两种模式
对应 INDEX.md 9.3

用法：
  # HTTP模式（需要服务运行）
  python scripts/verify_data_field.py lof-arbitrage rows[0].iopv 161125
  
  # 直连模式（不需要HTTP服务，直接调Python函数）
  python scripts/verify_data_field.py --direct lof rows[0].iopv 161125
  python scripts/verify_data_field.py --direct lof rows[0].premiumRate 161125
"""
import sys
import json
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

ENDPOINTS = {
    "lof-arbitrage": "/api/market/lof-arbitrage",
    "ah": "/api/market/ah",
    "ab": "/api/market/ab",
    "exchange-rate": "/api/market/exchange-rate",
    "ipo": "/api/market/ipo",
    "convertible-bonds": "/api/market/convertible-bonds",
    "convertible-bond-arbitrage": "/api/market/convertible-bond-arbitrage",
    "cb-rights-issue": "/api/market/cb-rights-issue",
    "merger": "/api/market/merger",
    "event-arbitrage": "/api/market/event-arbitrage",
}

DIRECT_HANDLERS = {
    "lof": "_fetch_lof_direct",
    "ah": "_fetch_ah_direct",
    "exchange-rate": "_fetch_fx_direct",
}


def _fetch_lof_direct():
    from data_fetch.lof_iopv.source import build_lof_snapshot
    from strategy.lof_iopv.service import build_lof_response
    snap = build_lof_snapshot()
    resp = build_lof_response(snap)
    return resp


def _fetch_ah_direct():
    from data_fetch.ah_premium.source import fetch_ah_data
    return fetch_ah_data()


def _fetch_fx_direct():
    from shared.market_service import get_fx_rates
    return {"success": True, "data": get_fx_rates(["USD", "HKD"])}


def resolve_field(data, field_path):
    parts = field_path.split('.')
    current = data
    for part in parts:
        if current is None:
            return None, f"路径中断: 前一级为 null"
        if '[' in part and part.endswith(']'):
            key, idx = part[:-1].split('[')
            idx = int(idx)
            current = current.get(key) if isinstance(current, dict) else None
            if current is None:
                return None, f"字段 '{key}' 不存在或为 null"
            if not isinstance(current, list):
                return None, f"'{key}' 不是数组"
            if idx >= len(current):
                return None, f"'{key}' 只有 {len(current)} 条，无法取 [{idx}]"
            current = current[idx]
        else:
            if not isinstance(current, dict):
                return None, f"无法从非dict取 '{part}'"
            current = current.get(part)
    return current, None


def check_field(data, field_path, code_filter=None):
    if code_filter and isinstance(data, dict):
        rows = data.get("rows", data.get("data", {}).get("rows", []))
        if isinstance(rows, list):
            matched = [r for r in rows if r.get("code") == code_filter]
            if matched:
                data = dict(data)
                data["_matched"] = matched
                field_path = field_path.replace("rows[0]", "_matched[0]", 1)

    value, err = resolve_field(data, field_path)
    return value, err


def main():
    args = sys.argv[1:]
    direct_mode = False
    if args and args[0] == '--direct':
        direct_mode = True
        args = args[1:]

    if len(args) < 2:
        print("用法:")
        print("  HTTP:  python verify_data_field.py <endpoint> <field> [code]")
        print("  直连:  python verify_data_field.py --direct <lof|ah> <field> [code]")
        print()
        print("示例:")
        print("  python verify_data_field.py --direct lof rows[0].iopv 161125")
        print("  python verify_data_field.py --direct lof rows[0].premiumRate 161125")
        print("  python verify_data_field.py --direct lof rows[0].nav")
        sys.exit(1)

    endpoint = args[0]
    field = args[1]
    code = args[2] if len(args) > 2 else None

    print(f"=== 数据字段验证 ===")
    print(f"模式: {'直连' if direct_mode else 'HTTP'}")
    print(f"端点: {endpoint}")
    print(f"字段: {field}")
    if code:
        print(f"基金: {code}")
    print()

    if direct_mode:
        handler_name = DIRECT_HANDLERS.get(endpoint)
        if not handler_name:
            print(f"未知直连端点: {endpoint}")
            print(f"可用: {', '.join(DIRECT_HANDLERS.keys())}")
            sys.exit(1)

        handler = globals().get(handler_name)
        print(f"[1/3] 调用 {handler_name}()...")
        try:
            data = handler()
        except Exception as e:
            print(f"调用失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        import urllib.request
        path = ENDPOINTS.get(endpoint)
        if not path:
            print(f"未知端点: {endpoint}")
            sys.exit(1)
        base = os.environ.get("API_BASE", "http://127.0.0.1:5001")
        url = f"{base}{path}?force=1"
        print(f"[1/3] 请求: {url}")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "verify-script"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            print(f"API请求失败: {e}")
            sys.exit(1)

    if isinstance(data, dict) and not data.get("success", True):
        print(f"返回 success=false: {data.get('error', 'unknown')}")
        sys.exit(1)

    payload = data.get("data", data) if isinstance(data, dict) else data

    print(f"[2/3] 解析字段 {field}...")
    value, err = check_field(payload if isinstance(payload, dict) else data, field, code)

    if err:
        print(f"字段解析失败: {err}")
        sys.exit(1)

    if value is None:
        print(f"[3/3] 字段值: null")
        print()
        print(f"FAIL: {field} = null (空值!)")
        sys.exit(1)

    print(f"[3/3] 字段值: {value}")
    print()
    print(f"PASS: {field} = {value}")
    sys.exit(0)


if __name__ == "__main__":
    main()