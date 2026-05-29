#!/bin/bash
sudo python3 -c "import json; f=open('/etc/docker/daemon.json','w'); json.dump({'registry-mirrors':['https://docker.1ms.run','https://docker.xuanyuan.me']},f); f.close()"
cat /etc/docker/daemon.json
sudo systemctl restart docker
echo "Docker status: $(systemctl is-active docker)"