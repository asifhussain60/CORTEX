# CORTEX Dashboard - Quick Command Reference

## 🚀 Launch Dashboard

```bash
# ONE COMMAND - USE THIS!
python launch-dashboard.py
```

Wait 10 seconds → Open http://localhost:8080

---

## 🛑 Stop Dashboard

Close the external terminal window **OR** press `Ctrl+C` in that terminal

---

## 🔍 Check if Running

```bash
# macOS/Linux
lsof -i :8000 -i :8080

# Windows (PowerShell)
Get-NetTCPConnection -LocalPort 8000,8080
```

---

## 🧹 Kill Orphaned Processes

```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9
lsof -ti:8080 | xargs kill -9

# Windows (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force
```

---

## 📊 Dashboard URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8080 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| WebSocket | ws://localhost:8000/ws/audit |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port in use | Launcher auto-cleans, or use kill commands above |
| Terminal doesn't open | macOS: Check permissions / Windows: Run as admin / Linux: Install gnome-terminal |
| Backend fails | `pip install fastapi uvicorn psutil` |
| Frontend loads, API fails | Check backend logs in external terminal |

---

## 📁 File Locations

```
CORTEX/
├── launch-dashboard.py              ← START HERE
├── DASHBOARD-QUICKSTART.md          ← This file
└── src/dashboard/
    ├── serve-cortex-dashboard.py    ← Main server
    ├── launch.py                     ← Alternative launcher
    └── README.md                     ← Full documentation
```

---

**Quick Start**: `python launch-dashboard.py` → Wait 10s → Open http://localhost:8080
