import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("43.139.35.190", port=22, username="ubuntu", password="DellG77588")
stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:5001/api/market/lof-arbitrage")
lof = stdout.read().decode()
data = json.loads(lof)
rows = data.get("data", {}).get("rows", [])
# 统计
types = {}
for r in rows:
    t = r.get("fundType", "?")
    types[t] = types.get(t, 0) + 1
print(f"Type distribution: {types}")
# 找一个有 holdings 的 B 类
for r in rows:
    if r.get("fundType") == "B" and r.get("holdings") and len(r["holdings"]) > 0:
        print(f"\nB-type with holdings: {r.get('code')} {r.get('name')}")
        print(f"  iopv={r.get('iopv')} premium={r.get('premiumRate')} calc={r.get('calcStatus')}")
        print(f"  holdings count: {len(r['holdings'])}")
        for h in r["holdings"][:3]:
            print(f"    {h}")
        break
# 找一个 iopv 为 None 的
none_count = sum(1 for r in rows if r.get("iopv") is None)
print(f"\nRows without iopv: {none_count}")
# 找 160644
for r in rows:
    if r.get("code") == "160644":
        print(f"\n160644 港美互联: {json.dumps(r, ensure_ascii=False)[:500]}")
        break
ssh.close()
