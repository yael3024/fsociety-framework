"""Cross-platform read-only system inventory."""

from __future__ import annotations

import psutil


def system_snapshot() -> dict:
    vm = psutil.virtual_memory()
    disks = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, OSError):
            continue
        disks.append({"device": part.device, "mountpoint": part.mountpoint, "filesystem": part.fstype, "total": usage.total, "used": usage.used, "free": usage.free})
    return {"cpu_percent": psutil.cpu_percent(interval=0.1), "cpu_count": psutil.cpu_count(), "memory": {"total": vm.total, "available": vm.available, "percent": vm.percent}, "disks": disks}


def processes() -> list[dict]:
    results = []
    for proc in psutil.process_iter(["pid", "name", "username", "status", "cpu_percent", "memory_info"]):
        try:
            item = proc.info
            memory = item.pop("memory_info", None)
            item["memory_rss"] = memory.rss if memory else None
            results.append(item)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return results


def connections() -> list[dict]:
    results = []
    try:
        items = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, OSError):
        return results
    for item in items:
        results.append({"family": str(item.family), "type": str(item.type), "local": f"{item.laddr.ip}:{item.laddr.port}" if item.laddr else None, "remote": f"{item.raddr.ip}:{item.raddr.port}" if item.raddr else None, "status": item.status, "pid": item.pid})
    return results
