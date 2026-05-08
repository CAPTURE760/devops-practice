"""AI 自动分析 API（规则引擎版）"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import psutil
import time

router = APIRouter()

# ─── 告警规则 ───────────────────────────────────────
ALERT_RULES = [
    {"key": "cpu", "threshold": 80, "level": "warning",  "msg": "CPU 使用率较高，注意观察负载"},
    {"key": "cpu", "threshold": 95, "level": "critical", "msg": "CPU 使用率过高，可能影响服务性能"},
    {"key": "memory", "threshold": 80, "level": "warning",  "msg": "内存使用率偏高，建议检查内存泄漏"},
    {"key": "memory", "threshold": 95, "level": "critical", "msg": "内存即将耗尽，紧急处理！"},
    {"key": "disk",  "threshold": 85, "level": "warning",  "msg": "磁盘使用率超 85%，及时清理"},
    {"key": "disk",  "threshold": 95, "level": "critical", "msg": "磁盘空间告急，立即清理！"},
]

def analyze_single_metric(name: str, value: float, thresholds: list[dict]) -> list[dict]:
    alerts = []
    for rule in thresholds:
        if rule["key"] == name:
            if value >= rule["threshold"]:
                alerts.append({"level": rule["level"], "message": rule["msg"], "value": round(value, 1)})
    return alerts

class AnalyzeRequest(BaseModel):
    cpu: Optional[float] = None
    memory: Optional[float] = None
    disks: Optional[list[dict]] = None

class AlertItem(BaseModel):
    level: str
    message: str
    target: str
    value: float

@router.get("/analyze")
async def analyze_now():
    """获取当前系统状态并 AI 分析"""
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disks = psutil.disk_usage("/")

    all_alerts = []
    all_alerts += analyze_single_metric("cpu", cpu, ALERT_RULES)
    all_alerts += analyze_single_metric("memory", mem.percent, ALERT_RULES)
    all_alerts += analyze_single_metric("disk", disks.percent, ALERT_RULES)

    # 正常判断
    status = "ok"
    if any(a["level"] == "critical" for a in all_alerts):
        status = "critical"
    elif any(a["level"] == "warning" for a in all_alerts):
        status = "warning"

    # 生成健康报告
    report = generate_report(status, cpu, mem.percent, disks.percent)

    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "metrics": {
            "cpu": round(cpu, 1),
            "memory": round(mem.percent, 1),
            "disk": round(disks.percent, 1)
        },
        "alerts": [
            AlertItem(level=a["level"], message=a["message"], target=a["key"], value=a["value"])
            for a in all_alerts
        ],
        "report": report
    }

def generate_report(status: str, cpu: float, mem: float, disk: float) -> str:
    """生成自然语言健康报告"""
    if status == "critical":
        return (f"⚠️ 系统状态异常！CPU {cpu}%，内存 {mem}%，磁盘 {disk}%。"
                f"建议立即检查高负载进程，并清理磁盘空间。")
    elif status == "warning":
        return (f"🔎 系统运行基本正常，但有指标偏高。"
                f"CPU {cpu}%，内存 {mem}%，磁盘 {disk}%。持续关注中。")
    else:
        return (f"✅ 系统运行良好。CPU {cpu}%，内存 {mem}%，磁盘 {disk}%。"
                f"所有指标均在正常范围内。")

@router.post("/analyze")
async def analyze_custom(body: AnalyzeRequest):
    """对自定义数据进行分析"""
    alerts = []
    if body.cpu is not None:
        alerts += analyze_single_metric("cpu", body.cpu, ALERT_RULES)
    if body.memory is not None:
        alerts += analyze_single_metric("memory", body.memory, ALERT_RULES)
    if body.disks:
        for d in body.disks:
            if "percent" in d:
                alerts += analyze_single_metric("disk", d["percent"], ALERT_RULES)

    status = "ok"
    if any(a["level"] == "critical" for a in alerts):
        status = "critical"
    elif any(a["level"] == "warning" for a in alerts):
        status = "warning"

    return {"status": status, "alerts": alerts}
