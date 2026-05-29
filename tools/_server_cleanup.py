import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("43.139.35.190", port=22, username="ubuntu", password="DellG77588")

# 清理手动上传的残留：reset 到 git commit + 清除 untracked
cmds = [
    "cd '/home/ubuntu/Alpha monitor' && git checkout -- .",
    "cd '/home/ubuntu/Alpha monitor' && git clean -fd -- data_fetch/lof_iopv strategy/lof_iopv presentation/routes presentation/view_models presentation/dashboard presentation/templates tools/_check_server.py tools/_check2.py tools/_deploy_presentation.py tools/_force_refresh.py tools/_verify_api.py tools/_verify2.py tools/deploy_lof_iopv.py",
    "cd '/home/ubuntu/Alpha monitor' && git status --short",
]
for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip():
        print(out.strip()[:500])
    if err.strip() and "warning" not in err.lower():
        print(f"ERR: {err.strip()[:200]}")

print("\n=== After cleanup ===")
stdin, stdout, stderr = ssh.exec_command("cd '/home/ubuntu/Alpha monitor' && git status --short")
print(stdout.read().decode()[:500])

ssh.close()
