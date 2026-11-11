"""
GHOST Notification & Alert Dispatch Tools
Dispatches Windows toast notifications, audio alerts, and tactical mission debriefs.
"""

import subprocess
import asyncio
from typing import Dict, Any, Optional
from voice.text_to_speech import voice_engine


def send_windows_toast(title: str, message: str) -> Dict[str, Any]:
    """Displays a native Windows toast notification via PowerShell."""
    clean_title = title.replace('"', '`"').replace("'", "''")
    clean_msg = message.replace('"', '`"').replace("'", "''")

    ps_script = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $textNodes = $template.GetElementsByTagName("text")
    $textNodes.Item(0).AppendChild($template.CreateTextNode("{clean_title}")) > $null
    $textNodes.Item(1).AppendChild($template.CreateTextNode("{clean_msg}")) > $null
    $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("GHOST Tactical")
    $notifier.Show($toast)
    """

    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, timeout=5)
        return {"success": True, "message": "Windows toast displayed."}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


async def send_debrief(mission_title: str, summary: str, speak: bool = False) -> Dict[str, Any]:
    """Sends mission completion toast and optional vocal debrief."""
    toast_res = send_windows_toast(f"GHOST: {mission_title}", summary)

    if speak:
        try:
            await voice_engine.speak_edge(summary)
        except Exception:
            voice_engine.speak_offline(summary)

    return {
        "success": True,
        "toast": toast_res,
        "spoken": speak,
        "summary": summary
    }

