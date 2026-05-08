"""日志查看 API"""
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
import os
import asyncio

router = APIRouter()

# 常见日志路径（Linux 服务器）
COMMON_LOG_PATHS = [
    "/var/log/syslog",
    "/var/log/auth.log",
    "/var/log/nginx/access.log",
    "/var/log/nginx/error.log",
    "/var/log/docker.log",
    "/home/deploy/devops-practice/app.log",
]

class LogFile(BaseModel):
    path: str
    size: int
    modified: str

@router.get("/list")
async def list_log_files():
    files = []
    for path in COMMON_LOG_PATHS:
        if os.path.exists(path):
            stat = os.stat(path)
            import datetime
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            files.append(LogFile(path=path, size=stat.st_size, modified=mtime))
    return files

@router.get("/read")
async def read_log(
    path: str = Query(..., description="日志文件路径"),
    lines: int = Query(100, ge=1, le=10000),
    keyword: str = Query(None, description="过滤关键词"),
):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"文件不存在: {path}")
    
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
        
        # 从末尾往前读 lines 条
        tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        # 关键词过滤
        if keyword:
            filtered = [l for l in tail_lines if keyword.lower() in l.lower()]
            tail_lines = filtered
        
        return {
            "path": path,
            "total_lines": len(all_lines),
            "returned_lines": len(tail_lines),
            "lines": [l.rstrip() for l in tail_lines]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_log(
    path: str = Query(...),
    keyword: str = Query(...),
    max_results: int = Query(100, ge=1, le=1000),
):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"文件不存在: {path}")
    
    results = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                if keyword.lower() in line.lower():
                    results.append({"line": i, "content": line.rstrip()})
                    if len(results) >= max_results:
                        break
        return {"keyword": keyword, "path": path, "total_found": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
