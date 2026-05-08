"""Docker 状态 API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

def get_docker_client():
    import docker
    try:
        client = docker.from_env()
        client.ping()
        return client
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Docker 未运行: {str(e)}")

class ContainerStats(BaseModel):
    id: str
    name: str
    image: str
    status: str
    state: str
    created: str
    ports: list[str]

class ContainerDetail(BaseModel):
    id: str
    name: str
    image: str
    status: str
    state: str
    created: str
    ports: dict
    mounts: list[dict]
    networks: list[str]
    cmd: list[str]

@router.get("/status")
async def docker_status():
    try:
        client = get_docker_client()
        return {"connected": True, "version": client.version()["Version"]}
    except Exception as e:
        return {"connected": False, "error": str(e)}

@router.get("/containers", response_model=list[ContainerStats])
async def list_containers(all_containers: bool = True):
    client = get_docker_client()
    containers = client.containers.list(all=all_containers)
    result = []
    for c in containers:
        ports = []
        ports_data = c.ports or {}
        for protocol_ports in ports_data.values():
            if protocol_ports and isinstance(protocol_ports, list):
                for p in protocol_ports:
                    if isinstance(p, dict) and p.get("PublicPort"):
                        ports.append(f"{p['PublicPort']}/{p.get('IP', '0.0.0.0')}/{list(ports_data.keys())[0]}")
        result.append(ContainerStats(
            id=c.id[:12],
            name=c.name.lstrip("/"),
            image=str(c.image),
            status=c.status,
            state=c.attrs["State"]["Status"],
            created=c.attrs["Created"],
            ports=ports
        ))
    return result

@router.get("/containers/{container_id}")
async def container_detail(container_id: str):
    client = get_docker_client()
    try:
        container = client.containers.get(container_id)
        info = container.attrs
        return ContainerDetail(
            id=container.id[:12],
            name=container.name,
            image=container.image.tags[0] if container.image.tags else container.image.short_id,
            status=container.status,
            state=container.attrs["State"]["Status"],
            created=info["Created"],
            ports=info["NetworkSettings"]["Ports"] or {},
            mounts=[{"type": m["Type"], "source": m["Source"], "dest": m["Destination"]}
                    for m in info["Mounts"] or []],
            networks=list(info["NetworkSettings"]["Networks"].keys()),
            cmd=info["Config"]["Cmd"] or []
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/containers/{container_id}/start")
async def start_container(container_id: str):
    client = get_docker_client()
    container = client.containers.get(container_id)
    container.start()
    return {"ok": True, "status": container.status}

@router.post("/containers/{container_id}/stop")
async def stop_container(container_id: str):
    client = get_docker_client()
    container = client.containers.get(container_id)
    container.stop()
    return {"ok": True, "status": container.status}

@router.post("/containers/{container_id}/restart")
async def restart_container(container_id: str):
    client = get_docker_client()
    container = client.containers.get(container_id)
    container.restart()
    return {"ok": True, "status": container.status}

@router.get("/images")
async def list_images():
    client = get_docker_client()
    images = client.images.list()
    result = []
    for i in images:
        tags = i.attrs.get("RepoTags") or []
        size = int(i.attrs.get("Size", 0))
        result.append({
            "id": i.attrs["Id"].replace("sha256:", "")[-12:],
            "tags": tags,
            "size": size
        })
    return result

@router.get("/volumes")
async def list_volumes():
    client = get_docker_client()
    volumes = client.volumes.list()
    return [{"name": v.name, "driver": v.attrs["Driver"]} for v in volumes]
