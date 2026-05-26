import paramiko, time, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("43.139.35.190", port=22, username="ubuntu", password="DellG77588")

stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:5001/api/health")
print(f"Health: {stdout.read().decode()[:100]}")

stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:5001/api/market/lof-arbitrage")
lof = stdout.read().decode()
try:
    data = json.loads(lof)
    rows = data.get("data", {}).get("rows", [])
    print(f"LOF rows: {len(rows)}")
    for r in rows[:5]:
        print(f"  {r.get('code')} type={r.get('fundType')} iopv={r.get('iopv')} prem={r.get('premiumRate')} calc={r.get('calcMode')}")
except Exception as e:
    print(f"Parse err: {e}")
    print(lof[:300])

ssh.close()
