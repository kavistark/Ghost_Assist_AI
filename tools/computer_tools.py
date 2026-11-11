"""
GHOST Computer Use & UI Automation Tools
Enables programmatic desktop interaction: mouse, keyboard, window focus, and screen inspections.
Controlled under Level 2 (Execute) and Level 3 (Authorize) clearance.
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

try:
    import pyautogui
    # Configure safety fail-safe
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
except ImportError:
    pyautogui = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None


def get_screen_resolution() -> Tuple[int, int]:
    """Returns the primary monitor resolution."""
    if pyautogui:
        size = pyautogui.size()
        return size.width, size.height
    return 1920, 1080


def list_open_windows() -> List[str]:
    """Enumerates visible top-level application windows."""
    if not gw:
        return []
    windows = []
    for title in gw.getAllTitles():
        clean = title.strip()
        if clean and clean not in windows:
            windows.append(clean)
    return windows


def focus_window(window_title_keyword: str) -> Dict[str, Any]:
    """Brings a window matching the keyword to the foreground."""
    if not gw:
        return {"success": False, "message": "pygetwindow not available."}

    matched = [w for w in gw.getAllWindows() if window_title_keyword.lower() in w.title.lower()]
    if not matched:
        return {"success": False, "message": f"No active window found matching '{window_title_keyword}'."}

    target = matched[0]
    try:
        if target.isMinimized:
            target.restore()
        target.activate()
        return {"success": True, "title": target.title, "message": f"Focused window: {target.title}"}
    except Exception as exc:
        return {"success": False, "message": f"Window activation failed: {str(exc)}"}


def mouse_click(x: int, y: int, clicks: int = 1, button: str = "left") -> Dict[str, Any]:
    """Dispatches programmatic mouse click at screen coordinates."""
    if not pyautogui:
        return {"success": False, "message": "pyautogui unavailable."}
    try:
        pyautogui.click(x=x, y=y, clicks=clicks, button=button)
        return {"success": True, "action": f"Clicked at ({x}, {y})"}
    except Exception as exc:
        return {"success": False, "message": f"Mouse action failed: {str(exc)}"}


def keyboard_type(text: str, press_enter: bool = False) -> Dict[str, Any]:
    """Types text buffer into the currently focused window."""
    if not pyautogui:
        return {"success": False, "message": "pyautogui unavailable."}
    try:
        pyautogui.write(text, interval=0.03)
        if press_enter:
            pyautogui.press('enter')
        return {"success": True, "typed": text}
    except Exception as exc:
        return {"success": False, "message": f"Keyboard input failed: {str(exc)}"}


def press_hotkey(*keys: str) -> Dict[str, Any]:
    """Executes a shortcut combination (e.g., 'ctrl', 'c')."""
    if not pyautogui:
        return {"success": False, "message": "pyautogui unavailable."}
    try:
        pyautogui.hotkey(*keys)
        return {"success": True, "keys": list(keys)}
    except Exception as exc:
        return {"success": False, "message": f"Hotkey execution failed: {str(exc)}"}

