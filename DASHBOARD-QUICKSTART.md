# 🚀 CORTEX Dashboard Quick Start

## One-Click Launch

```bash
python launch-dashboard.py
```

Wait ~10 seconds, then open: **http://localhost:8080**

---

## What Gets Launched

- **Frontend**: http://localhost:8080 (HTML/CSS/JS dashboard)
- **Backend**: http://localhost:8000 (FastAPI + WebSocket)
- **API Docs**: http://localhost:8000/docs (Swagger UI)

---

## Features

✅ **Automatic orphan cleanup** - Kills old processes on ports 8000/8080  
✅ **External terminal** - Won't be killed by VS Code prompts  
✅ **Cross-platform** - Works on macOS, Windows, Linux  
✅ **Health monitoring** - Auto-detects server failures  

---

## Stop the Dashboard

Close the external terminal window **OR** press `Ctrl+C` in that terminal.

---

## Troubleshooting

### Port Already in Use
The launcher automatically kills orphaned processes. If it fails:

**macOS/Linux:**
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:8080 | xargs kill -9
```

**Windows (PowerShell):**
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force
```

### Dependencies Missing
```bash
pip install fastapi uvicorn psutil
```

---

## File Organization

```
CORTEX/
├── launch-dashboard.py              ← ONE-CLICK LAUNCHER (START HERE)
│
└── src/dashboard/
    ├── serve-cortex-dashboard.py    ← Main server script
    ├── launch.py                     ← Internal launcher (alternative)
    ├── README.md                     ← Full documentation
    │
    ├── api/
    │   └── main.py                   ← FastAPI backend
    │
    └── frontend/
        ├── index.html                ← Dashboard UI
        ├── css/                      ← Stylesheets
        └── js/                       ← JavaScript modules
```

---

## More Info

See full documentation: `src/dashboard/README.md`
