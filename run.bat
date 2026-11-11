@echo off
title GHOST Tactical Command Center
cls
echo ========================================================================
echo    GHOST PERSONAL AI INTELLIGENCE SYSTEM — CENTRAL COMMAND
echo    Clearance: DEFCON 3
echo ========================================================================
echo.
echo [1/2] Opening Tactical HUD in default browser...
start http://127.0.0.1:8080
echo.
echo [2/2] Initializing GHOST FastAPI server and WebSocket Gateway...
python main.py
pause

