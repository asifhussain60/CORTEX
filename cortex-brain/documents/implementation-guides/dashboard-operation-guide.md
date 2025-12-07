# CORTEX Dashboard Operation Guide

**Version:** 1.0  
**Created:** 2025-12-06  
**Purpose:** Complete reference for launching, operating, and troubleshooting the CORTEX dashboard

---

## 📋 Quick Reference

**Launch Command:**
```bash
python3 -m src.orchestrators.dashboard_launcher --port 8080 --source mock
```

**Dashboard URL Pattern:**
```
http://localhost:{PORT}/ui/index.html?source={SOURCE}&tab={TAB}
```

**Valid Tabs:** `executive`, `overview`, `architecture`, `tech-stack`, `security`, `code-org`, `vendors`

---

## 🏗️ Architecture Overview

### Directory Structure

```
cortex-brain/dashboards/
├── ui/                          # Frontend application
│   ├── index.html              # Main entry point
│   ├── app.js                  # Application controller
│   ├── data-loader.js          # Data loading logic
│   └── components/             # Tab renderers
│       ├── executive-tab.js    # Narrative executive summary
│       ├── overview-tab.js
│       ├── architecture-tab.js
│       └── ...
├── data/                        # Data directories
│   ├── mock/                   # Mock demo data
│   │   ├── executive-summary.json
│   │   ├── health-data.json
│   │   ├── tech-stack.json
│   │   ├── security.json
│   │   ├── architecture.json
│   │   ├── code-organization.json
│   │   └── vendors.json
│   └── repos/                  # Real repository data
│       ├── {repo-id}/          # One folder per repository
│       │   ├── executive-summary.json
│       │   └── ...
└── config/                      # Configuration files
    └── repository-registry.json
```

### HTTP Server Configuration

**CRITICAL:** The HTTP server MUST serve from the `dashboards/` parent directory, NOT from `ui/` subdirectory.

**Why:** This allows both paths to work:
- `/ui/index.html` - Dashboard UI
- `/data/mock/executive-summary.json` - Data files

**Implementation:**
```python
# CORRECT - Serves from parent directory
handler = functools.partial(CORSHTTPRequestHandler, directory=str(dashboard_dir))

# WRONG - Breaks data loading
# handler = functools.partial(CORSHTTPRequestHandler, directory=str(dashboard_dir / "ui"))
```

**URL Construction:**
```python
# Since server serves from parent, UI needs path prefix
url = f"http://localhost:{port}/ui/index.html?source={source}"
```

---

## 🚀 Launching the Dashboard

### ⚠️ CRITICAL: Working Directory Requirement

**ALWAYS run dashboard launcher from CORTEX root directory:**

```bash
cd /path/to/CORTEX  # MUST be CORTEX root, not cortex-brain/dashboards/
python3 -m src.orchestrators.dashboard_launcher --port 8080 --source mock
```

**Why:**
- Server auto-detects CORTEX root from current working directory
- Locates `cortex-brain/dashboards/` relative to root
- Serves from `cortex-brain/dashboards/` parent to access both `/ui/` and `/data/`
- Running from wrong directory causes "CORTEX root not found" error

**Reference:** This is documented in `dashboard_launcher.py` line 7-9

### Method 1: Interactive Mode (Recommended)

```bash
cd /path/to/CORTEX  # MUST be CORTEX root
python3 -m src.orchestrators.dashboard_launcher --port 8080 --source mock
```

**Features:**
- Auto-opens browser
- Interactive server (Ctrl+C to stop)
- Shows logs in terminal

### Method 2: Background Mode

```bash
cd /path/to/CORTEX  # MUST be CORTEX root
nohup python3 -m src.orchestrators.dashboard_launcher --port 8080 --source mock > /tmp/cortex-dashboard.log 2>&1 &
```

**Features:**
- Runs in background
- Logs to `/tmp/cortex-dashboard.log`
- Survives terminal closure

**Stop Background Server:**
```bash
# Find and kill process
lsof -ti:8080 | xargs kill -9
# OR
pkill -9 -f "dashboard_launcher"
```

### Method 3: Python Code

```python
from src.orchestrators.dashboard_launcher import launch_dashboard

result = launch_dashboard(
    port=8080,
    auto_open=True,
    source="mock"
)

if result["success"]:
    print(f"Dashboard running at {result['url']}")
    # Keep server running
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        result["server"].stop()
```

### Command-Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--port` | Server port | 8080 | `--port 8082` |
| `--source` | Data source | mock | `--source luum-fresh` |
| `--no-browser` | Don't auto-open browser | False | `--no-browser` |

---

## 📊 Data Structure

### Executive Summary (executive-summary.json)

**Format:** Dashboard v3 Narrative Format

```json
{
  "project_name": "Application Name",
  "tagline": "Brief project description",
  "what_it_does": {
    "summary": "2-3 paragraph explanation of what the application does",
    "key_points": [
      "Key feature 1",
      "Key feature 2"
    ],
    "source": "hybrid|readme|generated"
  },
  "composition": {
    "architecture_style": "Modern 3-Tier Web Application",
    "components": [
      {
        "name": "Component Name",
        "technology": "React 18 + TypeScript",
        "purpose": "What this component does",
        "files_count": 147
      }
    ],
    "relationships": [
      "How components interact"
    ]
  },
  "capabilities": [
    {
      "name": "Capability Name",
      "description": "What this capability provides",
      "confidence": 0.95
    }
  ],
  "technical_foundation": {
    "languages": {
      "Python": "75%",
      "JavaScript": "15%"
    },
    "frameworks": ["Framework 1", "Framework 2"],
    "architecture_type": "Microservices",
    "dependencies": {
      "production": 23,
      "development": 24,
      "total": 47
    }
  },
  "health_snapshot": {
    "overall_score": 85.5,
    "security_issues": 0,
    "code_quality": 8.5
  }
}
```

### Other Data Files

| File | Purpose | Required |
|------|---------|----------|
| `health-data.json` | Code quality, security, performance metrics | Yes |
| `tech-stack.json` | Languages, frameworks, tools, versions | Yes |
| `security.json` | Vulnerabilities, security issues, recommendations | Yes |
| `architecture.json` | Component graph, relationships, patterns | Yes |
| `code-organization.json` | File structure, complexity, hotspots | Yes |
| `vendors.json` | Third-party dependencies, licenses, risks | Optional |

---

## 🎨 Frontend Data Loading

### Data Loader Logic

**File:** `cortex-brain/dashboards/ui/data-loader.js`

```javascript
// Base paths for data sources
const DATA_SOURCES = {
    mock: '/data/mock/',
    'repo-id': '/data/repos/repo-id/'
};

// Files loaded for each source
const DATA_FILES = [
    'executive-summary.json',
    'health-data.json',
    'tech-stack.json',
    'security.json',
    'architecture.json',
    'code-organization.json',
    'vendors.json'
];
```

### Data Access Pattern

```javascript
// Load all data for a source
const data = await loadDashboardData('mock');

// Access executive summary
const execSummary = data.executiveSummary;

// Check for narrative format
if (execSummary.project_name) {
    // Render v3 narrative format
    renderNarrativeExecutiveSummary(container, execSummary);
} else {
    // Fallback to legacy format
    renderLegacyExecutiveSummary(container, data);
}
```

---

## 🐛 Troubleshooting

### Issue 1: Executive Summary Shows Empty/Generic Data

**Symptoms:**
- "0 lines of code across 0 files"
- "Unknown" project type
- No narrative content

**Root Cause:** Data files not accessible from HTTP server

**Solution:**
```bash
# Test data access
curl http://localhost:8080/data/mock/executive-summary.json

# If 404 error, server is misconfigured
# Fix: Ensure server serves from dashboards/ parent, not ui/ subdirectory
```

**Verify in Code:**
```python
# In dashboard_launcher.py, line ~269
# MUST be:
handler = functools.partial(CORSHTTPRequestHandler, directory=str(self.dashboard_dir))

# NOT:
# handler = functools.partial(CORSHTTPRequestHandler, directory=str(self.dashboard_dir / "ui"))
```

### Issue 2: Port Already in Use

**Symptoms:**
- `❌ Port 8080 is in use and could not be freed`

**Solutions:**

**Option A - Kill Process:**
```bash
lsof -ti:8080 | xargs kill -9
```

**Option B - Use Different Port:**
```bash
python3 -m src.orchestrators.dashboard_launcher --port 8082 --source mock
```

**Option C - Wait and Retry:**
```bash
# Sometimes takes a few seconds for port to be released
sleep 5
python3 -m src.orchestrators.dashboard_launcher --port 8080 --source mock
```

### Issue 3: Browser Shows Cached Old Version

**Symptoms:**
- Dashboard shows old design/data after updates

**Solutions:**

**Hard Refresh:**
- **Mac:** Cmd + Shift + R
- **Windows/Linux:** Ctrl + Shift + R

**Clear Cache:**
1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"

**Disable Cache (Development):**
1. Open DevTools (F12)
2. Go to Network tab
3. Check "Disable cache"

### Issue 4: JavaScript Errors in Console

**Common Errors:**

**1. "Failed to fetch" / "CORS error"**
- **Cause:** Data files not accessible
- **Fix:** Verify server serves from parent directory

**2. "Cannot read property 'project_name' of undefined"**
- **Cause:** executive-summary.json not loaded
- **Fix:** Check Network tab, verify file returns 200 status

**3. "Unexpected token < in JSON"**
- **Cause:** Server returning HTML error page instead of JSON
- **Fix:** Check file path, verify data source exists

### Issue 5: Data Not Updating After Collection

**Symptoms:**
- Ran dashboard collector but UI shows old data

**Solutions:**

**1. Hard Refresh Browser** (see Issue 3)

**2. Check Data Source:**
```bash
# Verify new data was written
ls -la cortex-brain/dashboards/data/repos/{repo-id}/
cat cortex-brain/dashboards/data/repos/{repo-id}/executive-summary.json
```

**3. Verify Source Parameter:**
```
# URL must match data directory name
http://localhost:8080/ui/index.html?source=my-repo-id

# Data must exist at:
cortex-brain/dashboards/data/repos/my-repo-id/
```

---

## � Troubleshooting

### Error: "CORTEX root directory not found"

**Symptom:** Dashboard fails to launch with message "CORTEX root directory not found. Must contain cortex-brain/"

**Cause:** Running from wrong directory (e.g., from `cortex-brain/dashboards/` instead of CORTEX root)

**Solution:**
```bash
# Find CORTEX root (contains cortex-brain/, src/, tests/, etc.)
pwd  # Should show something like /Users/username/PROJECTS/CORTEX

# If in wrong directory:
cd /path/to/CORTEX  # Move to CORTEX root

# Verify you're in correct location:
ls -la  # Should see: cortex-brain/, src/, tests/, VERSION, etc.

# Now launch:
python3 -m src.orchestrators.dashboard_launcher --port 8080 --source mock
```

**Prevention:** Always run from CORTEX root, never from subdirectories

### Error: "Dashboard directory not found"

**Symptom:** "Dashboard directory not found: /path/to/cortex-brain/dashboards"

**Cause:** Missing dashboard directory or corrupted CORTEX installation

**Solution:**
```bash
# Verify directory exists:
ls -la cortex-brain/dashboards/

# Should see:
# - ui/ (frontend)
# - data/ (data directories)
# - config/ (configuration)

# If missing, restore from repository
```

### Error: "Port XXXX is in use"

**Symptom:** "Port 8080 is in use and could not be freed"

**Cause:** Another process using the port, or previous dashboard server still running

**Solution:**
```bash
# Method 1: Let dashboard launcher handle it (auto-kills process)
python3 -m src.orchestrators.dashboard_launcher --port 8080 --source mock

# Method 2: Manual kill
lsof -ti:8080 | xargs kill -9

# Method 3: Use different port
python3 -m src.orchestrators.dashboard_launcher --port 8082 --source mock
```

### Error: "Failed to render overview - pct.toFixed is not a function"

**Symptom:** Dashboard loads but Overview tab shows JavaScript error

**Cause:** Schema mismatch between data files and rendering code

**Solution:**
```bash
# Check data file schema:
cat cortex-brain/dashboards/data/mock/overview.json | grep -A 10 "composition"

# Should show:
# "composition": {
#   "languages": [
#     {"name": "Python", "percentage": 75.2, "loc": 34340}
#   ]
# }

# If schema is correct, clear browser cache and hard refresh (Cmd+Shift+R)
```

### Dashboard Shows Blank Page

**Symptom:** Dashboard URL opens but shows empty white page

**Causes:**
1. Server serving from wrong directory
2. Missing index.html
3. JavaScript errors

**Solution:**
```bash
# 1. Verify server directory:
# Should serve from cortex-brain/dashboards/ (parent), NOT from ui/

# 2. Check index.html exists:
ls -la cortex-brain/dashboards/ui/index.html

# 3. Check browser console (F12 > Console tab) for errors

# 4. Verify URL structure:
# Correct: http://localhost:8080/ui/index.html?source=mock
# Wrong: http://localhost:8080/index.html?source=mock
```

### Data Files Not Loading (404 Errors)

**Symptom:** Console shows "Failed to load /data/mock/executive-summary.json - 404"

**Cause:** Server serving from wrong directory (ui/ instead of parent)

**Solution:**
```bash
# Verify server directory in dashboard_launcher.py line 287:
# dashboard_parent = cortex_root / "cortex-brain" / "dashboards"
# server = DashboardServer(dashboard_parent, port)  # NOT dashboard_ui!

# If code is correct, restart server from CORTEX root:
cd /path/to/CORTEX  # CORTEX root, NOT cortex-brain/dashboards/
python3 -m src.orchestrators.dashboard_launcher --port 8080 --source mock
```

---

## �🔧 Maintenance

### Adding a New Repository

**1. Generate Dashboard Data:**
```bash
python -m src.orchestrators.dashboard_collector --path "/path/to/repo"
```

**2. Verify Data Created:**
```bash
ls -la cortex-brain/dashboards/data/repos/{repo-id}/
```

**3. Register Repository (Optional):**

Edit `cortex-brain/dashboards/data/repository-registry.json`:
```json
{
  "repositories": [
    {
      "id": "repo-id",
      "name": "Display Name",
      "path": "/path/to/repo",
      "last_collected": "2025-12-06T15:00:00Z"
    }
  ]
}
```

**4. Launch Dashboard:**
```bash
python3 -m src.orchestrators.dashboard_launcher --port 8080 --source repo-id
```

### Updating Mock Data

**Location:** `cortex-brain/dashboards/data/mock/`

**Files to Update:**
- `executive-summary.json` - Main narrative content
- `health-data.json` - Quality metrics
- `tech-stack.json` - Technologies used
- `security.json` - Security vulnerabilities
- `architecture.json` - Component relationships
- `code-organization.json` - File structure
- `vendors.json` - Third-party dependencies

**After Updates:**
- Restart dashboard server
- Hard refresh browser
- Verify changes in UI

---

## 📚 Related Documentation

- **Dashboard Launcher Quick Ref:** `cortex-brain/documents/implementation-guides/dashboard-launcher-quick-ref.md`
- **Dashboard v3 Plan:** `cortex-brain/documents/planning/dashboard-v3-narrative-executive-summary-plan.md`
- **Dashboard Collector:** `src/orchestrators/dashboard_collector.py`
- **Data Loader Source:** `cortex-brain/dashboards/ui/data-loader.js`
- **Executive Tab Source:** `cortex-brain/dashboards/ui/components/executive-tab.js`

---

## 🚨 Critical Reminders

1. **Server MUST serve from `dashboards/` parent directory** to make data files accessible
2. **URL format is `/ui/index.html`** not `/index.html` (when serving from parent)
3. **Hard refresh browser** after any data updates
4. **Check browser console** for JavaScript errors when debugging
5. **Verify data files exist** with `curl` or `ls` commands before debugging UI
6. **Port conflicts are common** - use different port or kill existing process

---

**For issues not covered here, check:**
- Browser DevTools Console (F12)
- Server logs (`/tmp/cortex-dashboard.log` if running in background)
- Network tab to verify data loading
- Repository registry for available data sources
