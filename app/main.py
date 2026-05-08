"""
AI 运维助手 - FastAPI 主入口
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.api import system, docker, logs, ai
import os

app = FastAPI(title="AI Ops Platform", version="1.0.0")

# 挂载静态文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 注册 API 路由
app.include_router(system.router, prefix="/api/system", tags=["系统状态"])
app.include_router(docker.router, prefix="/api/docker", tags=["Docker"])
app.include_router(logs.router, prefix="/api/logs", tags=["日志"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI 分析"])

@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = os.path.join(BASE_DIR, "static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return {"message": "AI Ops Platform running", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "ok"}
