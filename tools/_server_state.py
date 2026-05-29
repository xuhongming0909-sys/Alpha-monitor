import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("43.139.35.190", port=22, username="ubuntu", password="DellG77588")

# git log
stdin, stdout, stderr = ssh.exec_command("cd '/home/ubuntu/Alpha monitor' && git log --oneline --format='%h %ai %s' -10")
print("=== Server git log ===")
print(stdout.read().decode())

# git status
stdin, stdout, stderr = ssh.exec_command("cd '/home/ubuntu/Alpha monitor' && git status --short | head -30")
print("=== Server git status ===")
print(stdout.read().decode())

# check if presentation dir exists (we manually uploaded it)
stdin, stdout, stderr = ssh.exec_command("ls -la '/home/ubuntu/Alpha monitor/presentation/routes/' 2>&1")
print("=== Server presentation/routes ===")
print(stdout.read().decode())

# check data_fetch/lof_iopv (we manually uploaded)
stdin, stdout, stderr = ssh.exec_command("ls -la '/home/ubuntu/Alpha monitor/data_fetch/lof_iopv/' 2>&1")
print("=== Server data_fetch/lof_iopv ===")
print(stdout.read().decode())

ssh.close()
