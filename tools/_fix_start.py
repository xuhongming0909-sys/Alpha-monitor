import paramiko, time, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("43.139.35.190", port=22, username="ubuntu", password="DellG77588")

# 创建目录
stdin, stdout, stderr = ssh.exec_command("mkdir -p '/home/ubuntu/Alpha monitor/tools/deploy'")
stdout.read()

# 上传 start_linux.sh
sftp = ssh.open_sftp()
sftp.put(
    r"C:\Users\93724\Desktop\Alpha monitor\tools\deploy\start_linux.sh",
    "/home/ubuntu/Alpha monitor/tools/deploy/start_linux.sh"
)
# 设置可执行权限
sftp.chmod("/home/ubuntu/Alpha monitor/tools/deploy/start_linux.sh", 0o755)
sftp.close()
print("Uploaded start_linux.sh")

# 重启
stdin, stdout, stderr = ssh.exec_command("sudo systemctl restart alpha-monitor")
stdout.read()
time.sleep(15)

stdin, stdout, stderr = ssh.exec_command("sudo systemctl is-active alpha-monitor")
status = stdout.read().decode().strip()
print(f"Service: {status}")

if status == "active":
    stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:5001/api/health")
    print(f"Health: {stdout.read().decode()[:80]}")
else:
    stdin, stdout, stderr = ssh.exec_command("sudo journalctl -u alpha-monitor -n 15 --no-pager")
    print(stdout.read().decode()[-800:])

ssh.close()
