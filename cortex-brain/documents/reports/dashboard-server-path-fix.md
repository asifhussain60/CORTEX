# Dashboard Server Path Fix

**Date:** December 7, 2025  
**Issue:** Dashboard loading blank, all tabs failing with ERR_CONNECTION_REFUSED

---

## Root Cause

Server was running from **wrong directory**: `cortex-brain/dashboards/ui/`

**Problem:** When server runs from `/ui/`, it cannot access parent `/data/` directory, causing all data file requests to fail:
- `/data/repository-registry.json` → 404
- `/data/mock/*.json` → 404
- Result: Blank dashboard, no tab content

---

## Solution

Server MUST run from **parent directory**: `cortex-brain/dashboards/`

**Correct path structure:**
```
cortex-brain/dashboards/     ← Server starts HERE
├── data/                     ← Data files accessible at /data/
│   ├── repository-registry.json
│   ├── mock/
│   │   ├── overview.json
│   │   ├── tech-stack.json
│   │   └── ...
│   └── repos/
└── ui/                       ← UI files accessible at /ui/
    ├── index.html            ← Access at /ui/index.html
    ├── app.js
    └── components/
```

---

## Correct Launch Commands

### Option 1: Manual HTTP Server
```bash
cd /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/dashboards
python3 -m http.server 8080 &
open 'http://localhost:8080/ui/index.html?source=mock'
```

### Option 2: CORTEX Orchestrator (Recommended)
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -m src.orchestrators.dashboard_launcher
```

**Note:** The orchestrator automatically uses the correct directory.

---

## URL Structure

**Dashboard:** `http://localhost:8080/ui/index.html?source=mock`
- `/ui/` prefix required (server at parent level)
- `?source=mock` specifies data source

**Data files:** `http://localhost:8080/data/mock/overview.json`
- `/data/` accessible at server root

---

## Validation

Test data accessibility:
```bash
curl http://localhost:8080/data/repository-registry.json
curl http://localhost:8080/data/mock/overview.json
```

Expected: 200 OK with JSON data

---

## Documentation References

- **Dashboard Launcher Guide:** `cortex-brain/documents/implementation-guides/dashboard-launcher-quick-ref.md`
- **Orchestrator Source:** `src/orchestrators/dashboard_launcher.py` (lines 14-16)

**Critical comment from orchestrator:**
```python
# CRITICAL CONFIGURATION:
# - Server MUST serve from cortex-brain/dashboards/ (parent directory)
# - NOT from cortex-brain/dashboards/ui/ (breaks data file access)
```

---

**Author:** Asif Hussain  
**Resolution Time:** 5 minutes  
**Status:** ✅ Fixed
