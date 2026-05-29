import paramiko, time, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("43.139.35.190", port=22, username="ubuntu", password="DellG77588")

# 清理 untracked 文件（之前手动上传的残留）
cmds = [
    "cd '/home/ubuntu/Alpha monitor' && git clean -fd",
    "cd '/home/ubuntu/Alpha monitor' && git checkout -- .",
    "cd '/home/ubuntu/Alpha monitor' && git pull origin main 2>&1",
]
for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip():
        print(out.strip()[:300])
    if err.strip() and "warning" not in err.lower() and "From" not in err:
        print(f"ERR: {err.strip()[:200]}")

# 验证新文件存在
stdin, stdout, stderr = ssh.exec_command("ls '/home/ubuntu/Alpha monitor/data_fetch/lof_iopv/' 2>&1")
print(f"\nlof_iopv files: {stdout.read().decode().strip()}")

stdin, stdout, stderr = ssh.exec_command("ls '/home/ubuntu/Alpha monitor/strategy/lof_iopv/' 2>&1")
print(f"strategy files: {stdout.read().decode().strip()}")

# 检查 git log
stdin, stdout, stderr = ssh.exec_command("cd '/home/ubuntu/Alpha monitor' && git log --oneline -3")
print(f"\n{stdout.read().decode()}")

ssh.close()
