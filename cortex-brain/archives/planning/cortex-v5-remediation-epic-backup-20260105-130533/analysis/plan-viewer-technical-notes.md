# Plan Viewer Technical Notes - C50

**Date:** January 4, 2026  
**Author:** Asif Hussain (via CORTEX)  
**Topic:** localhost:8000 Server Requirement  
**Version:** 5.1.1

---

## 🚨 Critical: CORS Restriction

### Problem: Static `file://` Protocol Doesn't Work

**Initial Approach (FAILED):**
```bash
# ❌ This won't work due to browser CORS policy
open plan-viewer.html
```

**Error:**
```
Failed to fetch tracking/epic-progress-tracker.json
Access to fetch at 'file:///...tracking/epic-progress-tracker.json' from origin 'null' has been blocked by CORS policy: Cross origin requests are only supported for protocol schemes: http, https, etc.
```

**Root Cause:**
- Browsers block `file://` protocol from fetching local JSON files
- Security feature prevents malicious websites from reading your filesystem
- `fetch()` API requires HTTP/HTTPS protocol for CORS compliance

---

## ✅ Solution: Python HTTP Server (localhost:8000)

### Server Architecture

```
┌─────────────────────────────────────────────┐
│ Browser: http://localhost:8000/...         │
│ ↓ HTTP GET request                         │
│ ┌─────────────────────────────────────┐   │
│ │ Python HTTP Server (port 8000)      │   │
│ │ - Serves CORTEX root directory      │   │
│ │ - Adds CORS headers (*)             │   │
│ │ - Handles JSON requests             │   │
│ └─────────────────────────────────────┘   │
│ ↓ Returns file with CORS headers           │
│ plan-viewer.html → JavaScript fetch() OK ✅ │
└─────────────────────────────────────────────┘
```

### Implementation Files

**1. Server Script:** `scripts/serve_plan_viewer.py`
```python
class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')  # CRITICAL
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()
```

**2. Launcher Script:** `scripts/launch_plan_viewer.sh`
```bash
# Kills port 8000, starts server, opens browser
python3 scripts/serve_plan_viewer.py 8000 &
open "http://localhost:8000/cortex-brain/.../plan-viewer.html"
```

---

## 🎨 Theme Update

### Old Theme (Removed)
```css
/* ❌ Ugly purple gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: #333; /* Dark text on purple - bad contrast */
```

### New Theme (CORTEX Docs Style)
```css
/* ✅ CORTEX Brand Colors */
background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e3a8a 100%);
--primary: #7C3AED;  /* Purple - CORTEX brand */
--accent: #10B981;   /* Green - progress/success */
--text-primary: #E5E7EB; /* Light gray - readable */
```

**Source:** `docs/technical/assets/styles/glassmorphism.css`  
**Implementation:** Copied locally (no external dependencies)

---

## 🔧 Usage

### Method 1: Launcher Script (Recommended)
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
./scripts/launch_plan_viewer.sh
```

### Method 2: Manual Server Start
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 scripts/serve_plan_viewer.py 8000
# Then open browser to:
# http://localhost:8000/cortex-brain/documents/planning/active/C50-cortex-v5-remediation/plan-viewer.html
```

### Method 3: Via Orchestrator (Future Enhancement)
```bash
python3 plan_orchestrator.py viewer
# Will check if localhost:8000 is serving
# Auto-launch if not running
# Open browser automatically
```

---

## 📊 Auto-Refresh Mechanism

**How It Works:**
1. Browser loads `plan-viewer.html` from localhost:8000
2. JavaScript `fetch()` requests JSON from same origin (localhost:8000)
3. CORS headers allow cross-directory file access
4. Timer refreshes every 10 seconds:
   ```javascript
   setInterval(() => {
       fetch('tracking/epic-progress-tracker.json')
           .then(res => res.json())
           .then(data => renderEpicView(data));
   }, 10000);
   ```
5. Progress bars update smoothly with CSS transitions

**Benefits:**
- No manual refresh needed
- Real-time progress tracking
- Minimal network overhead (JSON only, ~10KB)
- Works offline (all files local)

---

## 🛡️ Security Considerations

### Why `Access-Control-Allow-Origin: *` is Safe Here

**Context:** Development server on localhost  
**Scope:** Only serves local CORTEX directory  
**Risk:** NONE - no external access, no sensitive data exposure

**Production Note:** If ever deployed publicly, restrict to:
```python
self.send_header('Access-Control-Allow-Origin', 'https://cortex.yourdomain.com')
```

---

## 🚀 Future Enhancements

### 1. WebSocket Real-Time Updates
Replace 10s polling with WebSocket push:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    renderEpicView(data);
};
```

### 2. Plan Orchestrator Integration
```python
# In plan_orchestrator.py
def open_viewer(self):
    if not is_server_running(8000):
        subprocess.Popen(['./scripts/launch_plan_viewer.sh'])
    webbrowser.open('http://localhost:8000/...')
```

### 3. Progress Streaming
```python
# Real-time phase updates
with open('tracking/epic-progress-tracker.json', 'w') as f:
    json.dump(progress_data, f)
    # Trigger WebSocket broadcast to viewer
```

---

## 📁 File References

| File | Purpose |
|------|---------|
| `scripts/serve_plan_viewer.py` | HTTP server with CORS headers |
| `scripts/launch_plan_viewer.sh` | One-command launcher |
| `plan-viewer.html` | Self-contained viewer (no CDN deps) |
| `tracking/epic-progress-tracker.json` | Data source |
| `tracking/child-plan-registry.json` | Metadata source |

---

## ✅ Verification

**Test Server is Working:**
```bash
curl http://localhost:8000/cortex-brain/documents/planning/active/C50-cortex-v5-remediation/tracking/epic-progress-tracker.json
# Should return JSON without errors
```

**Test CORS Headers:**
```bash
curl -I http://localhost:8000/cortex-brain/.../plan-viewer.html | grep "Access-Control"
# Should show: Access-Control-Allow-Origin: *
```

---

**Summary:** Plan viewer MUST be served via HTTP server due to browser CORS restrictions. The `file://` protocol cannot fetch local JSON files. Solution: Python HTTP server on localhost:8000 with CORS headers.
