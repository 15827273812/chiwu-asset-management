import json, sys

path = '/home/mzh205/.openclaw/workspace/chiwu/progress.json'
with open(path) as f:
    data = json.load(f)

updates = {
    'fe_shell': ('doing', 40),
    'fe_list': ('doing', 30),
    'fe_form': ('todo', 0),
    'fe_detail': ('todo', 0),
    'fe_categories': ('todo', 0),
    'fe_maintenance': ('todo', 0),
    'fe_stats': ('todo', 0),
    'fe_wish': ('todo', 0),
    'fe_settings': ('todo', 0),
    'ui_polish': ('todo', 0),
}

for m in data:
    if m['id'] in updates:
        s, p = updates[m['id']]
        m['status'] = s
        m['pct'] = p

with open(path, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

total = round(sum(m['pct'] for m in data) / len(data))
print(f"进度更新: {total}%")
