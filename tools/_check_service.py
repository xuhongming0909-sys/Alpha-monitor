import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("43.139.35.190", port=22, username="ubuntu", password="DellG77588")

# 查看 systemd service 配置
stdin, stdout, stderr = ssh.exec_command("cat /etc/systemd/system/alpha-monitor.service")
print("=== Service file ===")
print(stdout.read().decode())

# 查看是否有其他启动脚本
stdin, stdout, stderr = ssh.exec_command("ls -la '/home/ubuntu/Alpha monitor/tools/' 2>&1 | head -20")
print("=== tools dir ===")
print(stdout.read().decode())

ssh.close()
