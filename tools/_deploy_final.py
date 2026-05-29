import paramiko, time, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("43.139.35.190", port=22, username="ubuntu", password="DellG77588")

# git pull
stdin, stdout, stderr = ssh.exec_command("cd '/home/ubuntu/Alpha monitor' && git fetch origin && git checkout main && git pull origin main 2>&1")
print("=== Git pull ===")
print(stdout.read().decode()[:800])
err = stderr.read().decode()
if err.strip() and "warning" not in err.lower():
    print(f"ERR: {err[:200]}")

# 重启
stdin, stdout, stderr = ssh.exec_command("sudo systemctl restart alpha-monitor")
stdout.read()
print("\nRestarting...")
time.sleep(15)

# 检查状态
stdin, stdout, stderr = ssh.exec_command("sudo systemctl is-active alpha-monitor")
status = stdout.read().decode().strip()
print(f"Service: {status}")

if status == "active":
    # 验证 health
    stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:5001/api/health")
    health = stdout.read().decode()
    print(f"Health: {health[:100]}")

    # 验证 LOF API
    stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:5001/api/market/lof-arbitrage")
    lof = stdout.read().decode()
    try:
        data = json.loads(lof)
        rows = data.get("data", {}).get("rows", [])
        print(f"\nLOF rows: {len(rows)}")
        if rows:
            for r in rows[:3]:
                print(f"  {r.get('code')} {r.get('name')} type={r.get('fundType')} iopv={r.get('iopv')} premium={r.get('premiumRate')} calc={r.get('calcMode')}")
    except:
        print(f"LOF raw: {lof[:300]}")
else:
    stdin, stdout, stderr = ssh.exec_command("sudo journalctl -u alpha-monitor -n 20 --no-pager")
    print(stdout.read().decode()[-1000:])

ssh.close()
