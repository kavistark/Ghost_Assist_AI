"""
GHOST Windows Laptop Agent
Provides direct interface to Windows OS operations, application dispatch, and screen surveillance.
"""

import os
import subprocess
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from tools.system_tools import get_hardware_telemetry, get_top_processes, check_security_anomalies

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None


class WindowsAgent:
    def __init__(self):
        self.device_id = "LAPTOP-ALPHA"
        self.os_type = "Windows"
        # Permitted applications whitelist for Level 2 execution
        self.app_whitelist = {
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "calculator": "calc.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "chrome": "chrome.exe",
            "code": "code.cmd"
        }

    def get_telemetry(self) -> Dict[str, Any]:
        """Provides full real-time telemetry snapshot."""
        telemetry = get_hardware_telemetry()
        telemetry["top_processes"] = get_top_processes(limit=3)
        telemetry["anomalies"] = check_security_anomalies()
        return telemetry

    def launch_application(self, app_alias: str) -> Dict[str, Any]:
        """Launches a registered desktop application under Level 2 clearance."""
        app_clean = app_alias.lower().strip()
        binary = self.app_whitelist.get(app_clean)

        if not binary:
            # Check if it's a known executable format
            if app_clean.endswith(".exe"):
                binary = app_clean
            else:
                return {
                    "success": False,
                    "message": f"Target application '{app_alias}' is not present in tactical whitelist."
                }

        try:
            subprocess.Popen([binary], shell=True)
            return {
                "success": True,
                "message": f"Application '{binary}' launched successfully."
            }
        except Exception as exc:
            return {
                "success": False,
                "message": f"Failed to execute '{binary}': {str(exc)}"
            }

    def capture_screenshot(self, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Captures active screen buffer for multimodal analysis."""
        if not ImageGrab:
            return {"success": False, "message": "PIL ImageGrab module unavailable."}

        target_dir = output_dir or (Path(__file__).resolve().parent.parent / "logs")
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = f"surveillance_{int(time.time())}.png"
        file_path = target_dir / filename

        try:
            screen = ImageGrab.grab()
            screen.save(str(file_path), "PNG")
            return {
                "success": True,
                "file_path": str(file_path),
                "resolution": screen.size
            }
        except Exception as exc:
            return {"success": False, "message": f"Screen capture failed: {str(exc)}"}


# Global singleton
windows_agent = WindowsAgent()

