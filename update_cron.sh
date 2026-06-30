#!/bin/bash
# 每5分钟更新 progress.json 并重启服务
cd /home/mzh205/.openclaw/workspace/chiwu
python3 -c "
import json, os, subprocess, sys
path = 'progress.json'
try:
    with open(path) as f:
        data = json.load(f)
except:
    sys.exit(1)
# 只更新更新时间为实时变化
os.environ['UPDATED'] = 'done'
# 重启服务
pkill -f 'uvicorn.*8808' 2>/dev/null
# 写最后的更新时间
with open('last_update.txt', 'w') as f:
    import datetime
    f.write(datetime.datetime.now().isoformat())
"
nohup python3 main.py &>/tmp/chiwu.log &
