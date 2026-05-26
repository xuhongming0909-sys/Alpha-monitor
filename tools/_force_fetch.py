import paramiko, time, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("43.139.35.190", port=22, username="ubuntu", password="DellG77588")

# 强制刷新
stdin, stdout, stderr = ssh.exec_command("curl -s 'http://127.0.0.1:5001/api/market/lof-arbitrage?force=1' > /dev/null 2>&1 &")
stdout.read()
print("Force refresh triggered. Waiting 120s for data fetch...")

ssh.close()

# 等待
time.sleep(120)

# 重新连接验证
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect("43.139.35.190", port=22, username="ubuntu", password="DellG77588")

stdin, stdout, stderr = ssh2.exec_command("curl -s http://127.0.0.1:5001/api/market/lof-arbitrage")
lof = stdout.read().decode()
try:
    data = json.loads(lof)
    rows = data.get("data", {}).get("rows", [])
    print(f"LOF rows: {len(rows)}")
    computed = sum(1 for r in rows if r.get("fundType"))
    print(f"New format rows (with fundType): {computed}")
    for r in rows[:5]:
        print(f"  {r.get('code')} type={r.get('fundType')} iopv={r.get('iopv')} prem={r.get('premiumRate')} calc={r.get('calcMode')} group={r.get('groupKey')}")
    # 看一个QDII的
    for r in rows:
        if r.get("groupKey") == "qdii":
            print(f"\nQDII sample: {r.get('code')} {r.get('name')} type={r.get('fundType')} holdings={len(r.get('holdings') or [])}")
            break
except Exception as e:
    print(f"Parse err: {e}")
    print(lof[:300])

ssh2.close()
