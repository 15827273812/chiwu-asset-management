#!/bin/bash
cd /home/mzh205/.openclaw/workspace/chiwu || exit 1

# 检查是否有变化
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git add -A
    git commit -m "auto: $(date '+%Y-%m-%d %H:%M') 自动提交更新"
    git push origin main 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pushed changes"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No changes"
fi
