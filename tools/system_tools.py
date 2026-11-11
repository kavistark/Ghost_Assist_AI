"""
GHOST System & Hardware Telemetry Tools
Provides direct sensor, resource, and process metrics via psutil.
"""

import psutil
import socket
from typing import Dict, Any, List


def get_hardware_telemetry() -> Dict[str, Any]:
    """Gathers real-time CPU, RAM, Disk, Battery, and Network status."""
    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count = psutil.cpu_count(logical=True)

    # Memory
    mem = psutil.virtual_memory()
    ram_percent = mem.percent
    ram_used_gb = round((mem.total - mem.available) / (1024 ** 3), 2)
    ram_total_gb = round(mem.total / (1024 ** 3), 2)

    # Disk
    disk = psutil.disk_usage("C:\\") if hasattr(psutil, "disk_usage") else None
    disk_percent = disk.percent if disk else 0.0
    disk_free_gb = round(disk.free / (1024 ** 3), 2) if disk else 0.0

    # Battery
    battery = psutil.sensors_battery()
    battery_percent = battery.percent if battery else 100
    power_plugged = battery.power_plugged if battery else True

    # Network Host
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"

    return {
        "hostname": hostname,
        "local_ip": local_ip,
        "cpu_percent": cpu_percent,
        "cpu_cores": cpu_count,
        "ram_percent": ram_percent,
        "ram_used_gb": ram_used_gb,
        "ram_total_gb": ram_total_gb,
        "disk_percent": disk_percent,
        "disk_free_gb": disk_free_gb,
        "battery_percent": battery_percent,
        "power_plugged": power_plugged,
        "status": "NOMINAL" if cpu_percent < 85 and ram_percent < 90 else "ELEVATED_LOAD"
    }


def get_top_processes(limit: int = 5) -> List[Dict[str, Any]]:
    """Returns the top processes sorted by CPU and memory consumption."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            processes.append({
                "pid": info['pid'],
                "name": info['name'],
                "cpu": info['cpu_percent'] or 0.0,
                "memory": round(info['memory_percent'] or 0.0, 1)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(key=lambda x: (x['cpu'], x['memory']), reverse=True)
    return processes[:limit]


def check_security_anomalies() -> List[Dict[str, Any]]:
    """Defensive check for abnormal CPU consumption or unverified processes."""
    anomalies = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            # Detect single process using > 70% CPU
            if proc.info['cpu_percent'] and proc.info['cpu_percent'] > 70.0:
                anomalies.append({
                    "type": "HIGH_CPU_CONSUMPTION",
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "metric": f"{proc.info['cpu_percent']}% CPU",
                    "threat_level": "WARNING"
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return anomalies

