import os, json, datetime
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from seed import init_db
from api import router as api_router

app = FastAPI(title="持物 - ChiWu")
app.include_router(api_router)

init_db()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "frontend.html")

@app.get("/", response_class=HTMLResponse)
def index():
    if os.path.exists(FRONTEND_PATH):
        with open(FRONTEND_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>持物 ChiWu</h1><p>前端页面加载中...</p>"

# ---- 进度面板 ----
PROGRESS_MODULES = [
    {"id":"framework","name":"框架/数据库","status":"done","pct":100},
    {"id":"api_asset","name":"资产CRUD API","status":"done","pct":100},
    {"id":"api_category","name":"分类API","status":"done","pct":100},
    {"id":"api_channel","name":"渠道API","status":"done","pct":100},
    {"id":"api_maintenance","name":"维护记录API","status":"done","pct":100},
    {"id":"api_wish","name":"心愿单API","status":"done","pct":100},
    {"id":"api_stats","name":"统计API","status":"done","pct":100},
    {"id":"fe_shell","name":"前端框架","status":"todo","pct":0},
    {"id":"fe_list","name":"前端-资产列表","status":"todo","pct":0},
    {"id":"fe_form","name":"前端-新建/编辑","status":"todo","pct":0},
    {"id":"fe_detail","name":"前端-资产详情","status":"todo","pct":0},
    {"id":"fe_categories","name":"前端-分类管理","status":"todo","pct":0},
    {"id":"fe_maintenance","name":"前端-维护记录","status":"todo","pct":0},
    {"id":"fe_stats","name":"前端-统计图表","status":"todo","pct":0},
    {"id":"fe_wish","name":"前端-心愿单","status":"todo","pct":0},
    {"id":"fe_settings","name":"前端-设置/导出","status":"todo","pct":0},
    {"id":"ui_polish","name":"iPhone适配&美化","status":"todo","pct":0},
]

def get_progress():
    progress_path = os.path.join(os.path.dirname(__file__), "progress.json")
    try:
        with open(progress_path) as f:
            modules = json.load(f)
    except:
        modules = PROGRESS_MODULES
    overall = round(sum(m["pct"] for m in modules) / len(modules))
    return {"modules": modules, "overall": overall, "updated_at": datetime.datetime.now().isoformat()}

@app.get("/progress.json")
def progress_json():
    return get_progress()

@app.get("/progress", response_class=HTMLResponse)
def progress_page():
    data = get_progress()
    blocks = ""
    for m in data["modules"]:
        bar = "█" * (m["pct"] // 10) + "░" * (10 - m["pct"] // 10)
        se = {"done":"✅","doing":"🔄","todo":"⏳"}.get(m["status"], "⏳")
        blocks += f'<div class="m"><span class="e">{se}</span><span class="n">{m["name"]}</span><span class="b">{bar}</span><span class="p">{m["pct"]}%</span></div>'
    ob = "█" * (data["overall"] // 10) + "░" * (10 - data["overall"] // 10)
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>持物进度</title><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,sans-serif;background:#1a1a2e;color:#eee;padding:20px;max-width:600px;margin:auto}}
h1{{font-size:22px;margin-bottom:4px}}; .s{{color:#888;font-size:13px;margin-bottom:20px}}
.o{{font-size:32px;font-weight:700;text-align:center;padding:20px;background:#16213e;border-radius:12px;margin-bottom:20px}}
.ob{{font-size:24px;letter-spacing:2px}}
.m{{display:flex;align-items:center;padding:8px 0;border-bottom:1px solid #2a2a4a;font-size:14px;gap:8px}}
.e{{width:24px;text-align:center}}; .n{{flex:1;color:#ccc}}; .b{{font-size:12px;letter-spacing:1px;color:#0f0}}; .p{{width:40px;text-align:right;color:#888}}
</style></head><body>
<h1>🏗️ 持物 ChiWu</h1>
<div class="s">更新于 {data["updated_at"]}</div>
<div class="o"><div class="ob">{ob}</div>{data["overall"]}%</div>
{blocks}
</body></html>"""

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8809, reload=False)
