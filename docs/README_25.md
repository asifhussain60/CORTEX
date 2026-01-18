# CORTEX Dashboard Server

Production-grade server for the CORTEX Neural Observatory Dashboard with intelligent process management.

## 🎯 Features

### Dual-Server Architecture
- **FastAPI Backend** (port 8000): REST API + WebSocket endpoints
- **Static Frontend** (port 8080): HTML/CSS/JS dashboard

### Intelligent Process Management
✅ **Detects orphaned HTTP processes** and kills them automatically  
✅ **Cross-platform support**: macOS, Windows, Linux  
✅ **External terminal launch**: Won't be killed by VS Code prompts  
✅ **Health monitoring**: Auto-detects if servers die  
✅ **Graceful shutdown**: Cleanup on Ctrl+C or termination  

### Why External Terminal?
VS Code's integrated terminal can kill long-running processes when Copilot prompts are triggered. Running in an external terminal ensures the dashboard stays alive during AI interactions.

---

## 🚀 Quick Start

### Option 1: One-Click Launch (Recommended)

```bash
# From project root - use the simple launcher
python launch-dashboard.py
```

This will:
1. Open a **new terminal window** (Terminal.app on macOS, PowerShell on Windows)
2. Start both backend and frontend servers
3. Show you the dashboard URL

**Then open your browser:**
```
http://localhost:8080
```

### Option 2: Manual Launch (External Terminal)

```bash
# From project root
python src/dashboard/launch.py
```

Same as Option 1, but uses the internal launcher script.

### Option 3: Direct Execution

```bash
# From project root
python src/dashboard/serve-cortex-dashboard.py
```

Use this if you want to run in your current terminal or debug output.

---

## 📖 Usage Examples

### Check if Dashboard is Running

```bash
# macOS/Linux
lsof -i :8000 -i :8080

# Windows (PowerShell)
Get-NetTCPConnection -LocalPort 8000,8080
```

### Kill Orphaned Processes Manually

```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9
lsof -ti:8080 | xargs kill -9

# Windows (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force
```

### Make Scripts Executable (macOS/Linux)

```bash
# Root launcher
chmod +x launch-dashboard.py

# Internal scripts
chmod +x src/dashboard/launch.py
chmod +x src/dashboard/serve-cortex-dashboard.py
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CORTEX Dashboard                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Browser (http://localhost:8080)                            │
│      │                                                       │
│      ├─→ Static Frontend (HTML/CSS/JS)                      │
│      │   - Glassmorphism UI                                 │
│      │   - D3.js visualizations                             │
│      │   - Chart.js metrics                                 │
│      │                                                       │
│      └─→ FastAPI Backend (http://localhost:8000)            │
│          - REST endpoints (/api/*)                           │
│          - WebSocket (ws://localhost:8000/ws/audit)          │
│          - CORS enabled                                      │
│                                                              │
│  Data Sources (Read-Only):                                  │
│  - cortex-brain/state/governance.db (audit logs)            │
│  - .github/roadmap/cortex-master.yaml (phase tracker)       │
│  - cortex-brain/registry/ (orchestrators)                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Process Management Flow

```
1. Launch Script Execution
   └─→ Check ports 8000 & 8080

2. Orphan Detection
   ├─→ Find processes using psutil
   └─→ Kill via terminate() → kill()

3. Server Startup
   ├─→ Backend: uvicorn (FastAPI)
   └─→ Frontend: http.server (static)

4. Health Monitoring
   ├─→ Poll process status every 5s
   └─→ Auto-restart on failure

5. Graceful Shutdown
   ├─→ Catch SIGINT/SIGTERM
   └─→ Terminate both processes
```

---

## 🛠️ Configuration

Edit `src/dashboard/serve-cortex-dashboard.py` to customize:

```python
BACKEND_PORT = 8000      # FastAPI server port
FRONTEND_PORT = 8080     # Static file server port
BACKEND_HOST = "127.0.0.1"   # Bind address
FRONTEND_HOST = "127.0.0.1"  # Bind address
```

---

## 🔍 Troubleshooting

### "Port already in use" Error

**Cause**: Orphaned process from previous run

**Solution**: The script automatically kills orphans, but if manual intervention needed:

```bash
# macOS/Linux
python src/dashboard/serve-cortex-dashboard.py  # Will auto-cleanup

# Or kill manually
lsof -ti:8000 | xargs kill -9
lsof -ti:8080 | xargs kill -9
```

```powershell
# Windows
python src/dashboard/serve-cortex-dashboard.py  # Will auto-cleanup

# Or kill manually
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

### "Backend/Frontend failed to start"

**Cause**: Python dependencies missing

**Solution**: Install requirements

```bash
pip install fastapi uvicorn psutil
```

### External Terminal Not Opening

**macOS**: Enable Terminal.app permissions in System Preferences  
**Windows**: Run as Administrator if permission denied  
**Linux**: Install a terminal emulator (gnome-terminal, konsole, or xterm)

---

## 📊 Endpoints

### Frontend (Port 8080)
```
GET /                     Main dashboard
GET /css/*                Stylesheets
GET /js/*                 JavaScript modules
```

### Backend (Port 8000)
```
GET  /api/health          Health check
GET  /api/brain/metrics   Brain tier metrics
GET  /api/audit/entries   Audit log entries
GET  /api/orchestrators   Orchestrator registry
WS   /ws/audit            Real-time audit stream
GET  /docs                Swagger UI (API docs)
```

---

## 🧪 Testing

```bash
# Start servers
python src/dashboard/launch.py

# Test backend
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost:8080/

# Test WebSocket (with wscat)
wscat -c ws://localhost:8000/ws/audit
```

---

## 🔒 Security

- **Localhost only**: Servers bind to 127.0.0.1 (not accessible externally)
- **Read-only data access**: Dashboard only reads existing files
- **No authentication**: Designed for local development
- **CORS enabled**: Frontend can access backend API

For production deployment, add:
- API authentication (JWT tokens)
- HTTPS/WSS encryption
- Rate limiting
- Firewall rules

---

## 📝 Governance Compliance

- ✅ **CORE-011**: Type hints on all functions
- ✅ **CORE-012**: Google-style docstrings
- ✅ **CORE-026**: Git checkpoint protocol (manual commit)
- ✅ **CORE-028**: Kebab-case naming (`serve.py`, `launch.py`)

---

## 🎨 Phase 15 Integration

This server is part of **PHASE-15-DASHBOARD-ENHANCEMENT**:

| AC-ID | Component | Status |
|-------|-----------|--------|
| DO-004-01 | Dashboard server script | ✅ Complete |
| DO-004-02 | External launcher | ✅ Complete |
| DO-004-03 | Process management | ✅ Complete |

See `.github/roadmap/phases/phase-15-dashboard-enhancement.yaml` for full specification.

---

## 🤝 Contributing

1. Test on your platform (macOS/Windows/Linux)
2. Verify orphan cleanup works correctly
3. Check external terminal launches properly
4. Submit issues for platform-specific bugs

---

## 📄 License

Part of the CORTEX framework. See project root for license details.
