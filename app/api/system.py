"""系统状态 API"""
from fastapi import APIRouter
from pydantic import BaseModel
import psutil
import platform

router = APIRouter()

class CpuInfo(BaseModel):
    usage: float
    cores: int

class MemInfo(BaseModel):
    total: int
    available: int
    used: int
    percent: float

class DiskInfo(BaseModel):
    device: str
    total: int
    used: int
    free: int
    percent: float
    mount: str

class SystemStatus(BaseModel):
    hostname: str
    platform: str
    cpu: CpuInfo
    memory: MemInfo
    disks: list[DiskInfo]
    uptime: str

@router.get("/status", response_model=SystemStatus)
async def get_status():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append(DiskInfo(
                device=part.device,
                total=usage.total,
                used=usage.used,
                free=usage.free,
                percent=usage.percent,
                mount=part.mountpoint
            ))
        except PermissionError:
            pass

    boot_time = psutil.boot_time()
    import time
    uptime_seconds = time.time() - boot_time
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    uptime_str = f"{hours}h {minutes}m"

    return SystemStatus(
        hostname=platform.node(),
        platform=platform.platform(),
        cpu=CpuInfo(usage=cpu, cores=psutil.cpu_count()),
        memory=MemInfo(
            total=mem.total,
            available=mem.available,
            used=mem.used,
            percent=mem.percent
        ),
        disks=disks,
        uptime=uptime_str
    )

@router.get("/cpu")
async def cpu_usage():
    return {"usage": psutil.cpu_percent(interval=1), "cores": psutil.cpu_count()}

@router.get("/memory")
async def memory_usage():
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "available": mem.available,
        "used": mem.used,
        "percent": mem.percent
    }
