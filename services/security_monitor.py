"""
GHOST Defensive Security Monitor Daemon
Runs continuous background perimeters scans: process resource spikes,
unauthorized network socket bindings, and system anomaly alerts.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Set
import psutil

from core.event_bus import event_bus, GhostEvent
from database.models import get_connection
from tools.system_tools import check_security_anomalies


class SecurityMonitorDaemon:
    def __init__(self):
        self.known_listening_ports: Set[int] = set()
        self.monitored_threshold_cpu: float = 80.0
        self.is_initialized: bool = False

    async def execute_periodic_sweep(self):
        """Asynchronous scheduled sweep triggered by APScheduler."""
        anomalies = check_security_anomalies()
        new_ports = self._audit_network_ports()

        # Check for CPU / Process anomalies
        for anom in anomalies:
            alert_payload = {
                "type": anom.get("type", "PROCESS_ANOMALY"),
                "pid": anom.get("pid"),
                "name": anom.get("name"),
                "metric": anom.get("metric"),
                "threat_level": anom.get("threat_level", "WARNING"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await event_bus.publish(GhostEvent(
                event_type="SECURITY_ALERT",
                payload=alert_payload,
                source="SECURITY_MONITOR"
            ))

        # Check for newly opened listening network ports
        if new_ports:
            port_alert = {
                "type": "NEW_LISTENING_PORT_DETECTED",
                "ports": list(new_ports),
                "threat_level": "CAUTION",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await event_bus.publish(GhostEvent(
                event_type="SECURITY_ALERT",
                payload=port_alert,
                source="SECURITY_MONITOR"
            ))

    def _audit_network_ports(self) -> Set[int]:
        """Identifies newly established listening ports since last scan."""
        current_ports = set()
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == psutil.CONN_LISTEN:
                    current_ports.add(conn.laddr.port)
        except Exception:
            return set()

        if not self.is_initialized:
            self.known_listening_ports = current_ports
            self.is_initialized = True
            return set()

        new_ports = current_ports - self.known_listening_ports
        self.known_listening_ports = current_ports
        return new_ports


security_monitor = SecurityMonitorDaemon()

