# GHOST — Personal AI Intelligence System

> *"Mission received. Executing with precision."*

GHOST is an autonomous personal command and intelligence system built like a military operations center. It coordinates dual-LLM cognition (Claude for deep reasoning/strategic planning, Gemini for real-time multimodal intelligence and natural interaction), exercises 3-tiered permission gating over device operations, and manages tasks as military-grade missions.

---

## Operational Architecture

```
GHOST/
├── main.py                     # FastAPI Command Gateway & Interactive Tactical CLI
├── config.py                   # Pydantic Settings & Environment Configurations
├── requirements.txt            # Project dependencies
├── .env.example                # Operational environment template
│
├── core/
│   ├── orchestrator.py         # Central Command Controller
│   ├── model_router.py         # Cognitive Model Router (Claude vs. Gemini)
│   ├── permission_engine.py    # 3-Tier Security Clearance Gateway (Observe/Execute/Authorize)
│   ├── mission_controller.py   # Mission lifecycle, checklist tracking, SQLite persistence
│   └── event_bus.py            # Asynchronous pub/sub event bus
│
├── llm/
│   ├── prompts.py              # Military persona directives & system instructions
│   ├── claude_client.py        # Intelligence Alpha: Strategic planning & task breakdown
│   └── gemini_client.py        # Intelligence Bravo: Multimodal, briefings, notification AI
│
├── tools/
│   ├── system_tools.py         # Hardware telemetry (psutil, CPU, RAM, Battery, Disk)
│   └── file_tools.py           # Safe directory scanning & duplicate file identification
│
├── devices/
│   ├── windows_agent.py        # Windows Laptop Controller & surveillance
│   └── android_gateway.py      # Android companion WebSocket & notification ingest
│
├── agents/
│   └── security_agent.py       # Defensive security analyst & anomaly detection
│
├── services/
│   └── task_scheduler.py       # APScheduler for reminders and recurring defensive sweeps
│
├── voice/
│   └── text_to_speech.py       # Vocal debriefing engine (edge-tts / pyttsx3)
│
├── database/
│   ├── models.py               # SQLite schema (missions, devices, notifications)
│   └── ghost.db                # Persistent operational database
│
├── android_app/
│   └── README.md               # Android companion spec (NotificationListenerService)
│
├── tests/
│   └── test_ghost_core.py      # Core test suite
└── logs/                       # Audit logs & telemetry records
```

---

## 3-Tier Permission Hierarchy

1. **LEVEL 1 — OBSERVE (Auto-Cleared)**:
   - Reading telemetry (CPU, RAM, Disk, Battery).
   - Summarizing notifications.
   - Searching file metadata.
2. **LEVEL 2 — EXECUTE (Controlled Sandbox)**:
   - Launching approved applications.
   - Organizing staged directory files.
   - Setting reminders & scheduling missions.
3. **LEVEL 3 — AUTHORIZATION (Explicit Clearance Required)**:
   - Destructive file deletion.
   - Running arbitrary shell scripts.
   - Altering network or firewall parameters.
   - Requires explicit challenge token verification (`AUTH-XXXXXX`).

---

## Quick Start

### 1. Environment Configuration
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```
Set `ANTHROPIC_API_KEY` and `GEMINI_API_KEY`. (GHOST includes offline heuristic fallbacks when keys are pending).

### 2. Launch Interactive Tactical Terminal
```powershell
python main.py --cli
```

### 3. Launch Central FastAPI Command Center
```powershell
python main.py
```
- Interactive Swagger UI: `http://127.0.0.1:8080/docs`
- Real-time WebSockets: `ws://127.0.0.1:8080/ws`
- Hardware Telemetry: `GET http://127.0.0.1:8080/api/telemetry`
- Missions Registry: `GET http://127.0.0.1:8080/api/missions`
- Security Defensive Sweep: `GET http://127.0.0.1:8080/api/security/sweep`

### 4. Run Test Suite
```powershell
python -m pytest tests/test_ghost_core.py -v
```

