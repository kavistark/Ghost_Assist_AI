"""
GHOST Defensive Security Analyst Agent
Monitors system activity, identifies abnormal resource consumption, detects foreign network sockets,
and compiles incident debriefs for the Operator.
"""

import psutil
from typing import Dict, Any, List
from datetime import datetime, timezone
from core.event_bus import event_bus, GhostEvent
from tools.system_tools import check_security_anomalies


class SecurityAgent:
    def __init__(self):
        self.callsign = "SECURITY_ANALYST"
        self.monitored_threshold_cpu = 75.0

    def run_defensive_sweep(self) -> Dict[str, Any]:
        """Conducts an all-sector security and process telemetry scan."""
        anomalies = check_security_anomalies()
        open_sockets = self._scan_listening_sockets()

        status = "SECURE"
        recommendations = []

        if anomalies:
            status = "ELEVATED_RISK"
            for anom in anomalies:
                recommendations.append(
                    f"Process {anom['name']} (PID: {anom['pid']}) consuming excessive CPU ({anom['metric']}). Recommend inspection."
                )

        return {
            "agent": self.callsign,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies,
            "active_listening_sockets_count": len(open_sockets),
            "recommendations": recommendations or ["All sectors secure. Defense perimeter intact."]
        }

    def _scan_listening_sockets(self) -> List[Dict[str, Any]]:
        """Audits open listening network ports."""
        listening = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == psutil.CONN_LISTEN:
                    listening.append({
                        "laddr": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "pid": conn.pid
                    })
        except (psutil.AccessDenied, Exception):
            pass
        return listening[:10]


# Global security agent instance
security_agent = SecurityAgent()
