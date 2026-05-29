import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("43.139.35.190", port=22, username="ubuntu", password="DellG77588")

# 从 git 恢复 tools/deploy
stdin, stdout, stderr = ssh.exec_command("cd '/home/ubuntu/Alpha monitor' && git checkout HEAD -- tools/deploy/ 2>&1")
print(stdout.read().decode())
print(stderr.read().decode())

# 验证文件存在
stdin, stdout, stderr = ssh.exec_command("ls -la '/home/ubuntu/Alpha monitor/tools/deploy/' 2>&1")
print(stdout.read().decode())

# 重启
stdin, stdout, stderr = ssh.exec_command("sudo systemctl restart alpha-monitor")
stdout.read()

ssh.close()
print("Restarted")
