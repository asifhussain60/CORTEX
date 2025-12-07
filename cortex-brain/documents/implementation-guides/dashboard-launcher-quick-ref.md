# Dashboard Launcher Quick Reference

**Purpose:** Launch CORTEX dashboard with HTTP server and auto-open browser

**Trigger Commands:**
- `load dashboard`
- `launch dashboard`
- `open dashboard`
- `show dashboard`
- `start dashboard`
- `dashboard`
- `view dashboard`
- `open cortex dashboard`

---

## ✨ Features

- **Auto-detect dashboard directory** - Finds `cortex-brain/dashboards/ui/` automatically
- **Smart port selection** - Uses port 8080, auto-falls back to 8081-8089 if occupied
- **Auto-open browser** - Opens dashboard automatically (can be disabled)
- **Background server** - Non-blocking HTTP server runs in separate thread
- **CORS support** - Local development-friendly CORS headers
- **Multiple data sources** - Mock data, Noor Canvas, or live data

---

## 🚀 Usage Examples

### Basic Launch
```
User: load dashboard
```

### Launch with Custom Port
```
User: load dashboard on port 9000
```

### Launch Without Opening Browser
```
User: launch dashboard without opening browser
```

### View Specific Data Source
```
User: open dashboard with noor-canvas data
```

---

## 🔧 Technical Details

### Files
- **Orchestrator:** `src/orchestrators/dashboard_launcher.py`
- **Module:** `src/operations/modules/dashboard_launcher_module.py`
- **YAML Config:** `cortex-operations.yaml` (load_dashboard operation)
- **Dashboard UI:** `cortex-brain/dashboards/ui/`

### Architecture
```
User Command → Intent Router → Dashboard Launcher Module → Orchestrator → HTTP Server
```

### Port Selection Logic
1. Try default port (8080)
2. If occupied, try 8081
3. Continue through 8082-8089
4. If all occupied, return error

### Server Details
- **Handler:** `CORSHTTPRequestHandler` (extends `SimpleHTTPRequestHandler`)
- **CORS:** Enabled for local development
- **Cache:** Disabled (`Cache-Control: no-store`)
- **Thread:** Daemon thread (auto-stops with process)

---

## 🌐 Dashboard URLs

### Format
```
http://localhost:{port}/index.html?source={data_source}
```

### Data Sources
- **mock** - Mock data for testing (default)
- **noor-canvas** - Noor Canvas project data
- **v5-prevalidation** - V5 PreValidation Web Service data
- *(Add custom sources as needed)*

### Examples
- `http://localhost:8080/index.html?source=mock`
- `http://localhost:8080/index.html?source=noor-canvas`
- `http://localhost:8080/index.html?source=v5-prevalidation`

---

## 🛑 Stopping the Server

### From Terminal
Press `Ctrl+C` in the terminal where server is running

### Programmatically
```python
from src.orchestrators.dashboard_launcher import launch_dashboard

result = launch_dashboard()
if result['success'] and 'server' in result:
    result['server'].stop()
```

---

## 🎯 Integration with CORTEX

### YAML Configuration
```yaml
load_dashboard:
  name: Load Dashboard
  deployment_tier: user
  natural_language:
    - load dashboard
    - launch dashboard
    # ... more triggers
  modules:
    - dashboard_launcher
  profiles:
    standard:  # Default profile
      options:
        port: 8080
        auto_open: true
        source: mock
    custom_port:  # Custom port profile
      options:
        port: 9000
    no_browser:  # No auto-open profile
      options:
        auto_open: false
```

### Intent Router Integration
The intent router automatically:
1. Loads triggers from `cortex-operations.yaml`
2. Maps user phrases to `load_dashboard` operation
3. Routes to `DashboardLauncherModule`
4. Executes with appropriate profile

---

## 🧪 Testing

### Run Integration Tests
```bash
python test_dashboard_launcher_integration.py
```

### Test Components
1. **Orchestrator Direct Call** - Tests core functionality
2. **Module Wrapper Call** - Tests operations integration
3. **YAML Registration** - Validates configuration

---

## 📝 Example Session

```
User: load dashboard

CORTEX: ✅ Dashboard server started successfully

🌐 URL: http://localhost:8080/index.html?source=mock
🔌 Port: 8080
📁 Directory: D:\PROJECTS\CORTEX\cortex-brain\dashboards\ui

💡 Dashboard will open automatically in your browser
🛑 Press Ctrl+C in the terminal to stop the server
```

---

## 🔍 Troubleshooting

### Port Already in Use
- Server auto-falls back to next available port (8081-8089)
- Check terminal output for actual port used

### Dashboard Files Not Found
- Ensure `cortex-brain/dashboards/ui/index.html` exists
- Run from CORTEX root directory or subdirectory

### Browser Doesn't Open
- Server still runs successfully
- Manually open URL from terminal output
- Use `no_browser` profile to disable auto-open

### CORS Errors
- Server includes CORS headers by default
- Check browser console for specific errors
- Verify files are being served from correct directory

### ⚠️ CRITICAL: Server Directory Must Be Parent of `/ui/`

**Problem:** Dashboard loads blank or shows "Failed to load resource" errors

**Root Cause:** Server running from wrong directory

**WRONG (Breaks data access):**
```bash
cd cortex-brain/dashboards/ui/
python3 -m http.server 8080
# ❌ URL: http://localhost:8080/index.html
# ❌ Cannot access ../data/*.json
```

**CORRECT (Works):**
```bash
cd cortex-brain/dashboards/
python3 -m http.server 8080
# ✅ URL: http://localhost:8080/ui/index.html?source=mock
# ✅ Can access data/*.json at http://localhost:8080/data/
```

**Why:** Dashboard needs access to both `/ui/` (HTML/CSS/JS) and `/data/` (JSON files). Server must run from parent directory to serve both paths.

**Fix:** Always use `dashboard_launcher` orchestrator - it handles correct directory automatically.

---

## 🏗️ Dashboard Architecture (December 2025)

### Critical Rendering Pattern

**Component Contract:**
- All tab components use **direct DOM manipulation**
- Components find containers via `getElementById()` and set `innerHTML`
- Components **return void** (no HTML string returns)

**Working Pattern (ALL TABS):**
```javascript
// app.js - renderCurrentTab()
async function renderCurrentTab() {
    // STEP 1: Make tab VISIBLE first
    const tabElement = document.getElementById(tabId);
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    tabElement.classList.add('active');
    
    // STEP 2: Call render functions (find visible containers)
    switch (appState.currentTab) {
        case 'tech-stack':
            renderTechStack(appState.data);  // Direct call
            break;
    }
}

// tech-stack-tab.js
export function renderTechStack(data) {
    const container = document.getElementById('tech-stack-container');
    container.innerHTML = `...`;  // Direct DOM manipulation
    // NO return statement
}
```

### ❌ BROKEN Pattern (Removed Dec 2025)

**What was wrong:**
```javascript
// ❌ BROKEN: Expected HTML string returns
const containerId = getTabContainerId(appState.currentTab);
progressiveLoader.showSkeleton(containerId, skeletonType);

let contentHtml;  // Expected string
switch (appState.currentTab) {
    case 'tech-stack':
        contentHtml = renderTechStack(data);  // Returns undefined!
        break;
}

await progressiveLoader.hideSkeleton(containerId, contentHtml);  // undefined!
```

**Why it failed:**
- Progressive loader expected `contentHtml` as string
- Components actually return `undefined` (direct DOM manipulation)
- Loader tried to inject `undefined` → failed
- Only Engineering tab worked (special case created container first)

**Fix Applied:**
- ✅ Removed progressive loader completely
- ✅ Show tab first (make visible) via `classList.add('active')`
- ✅ Then call render functions - they find visible containers
- ✅ All tabs now use same pattern

### Tab Visibility Management

**CSS Pattern:**
```css
.tab-content {
    display: none;  /* Hidden by default */
}

.tab-content.active {
    display: block;  /* Visible when active */
}
```

**JavaScript Pattern:**
```javascript
// Hide all tabs
document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.remove('active');
});

// Show current tab
tabElement.classList.add('active');

// Now components can find their containers
renderTechStack(data);  // Finds #tech-stack-container (now visible)
```

### Data Access Pattern

**Defensive extraction:**
```javascript
// Components handle both flat and nested data
export function renderTechStack(data) {
    const techStack = data.techStack || data;  // Defensive
    const container = document.getElementById('tech-stack-container');
    container.innerHTML = `...`;
}
```

**Why needed:** `appState.data` structure varies by source:
- Mock data: Nested (`data.techStack`)
- Some sources: Flat (`data` itself is tech stack)
- Pattern handles both without errors

---

## 📋 Lessons Learned (December 2025)

### 1. Server Directory Matters
- **Lesson:** HTTP server directory determines accessible paths
- **Impact:** Wrong directory = blank dashboard
- **Solution:** Always serve from parent of `/ui/` directory
- **Prevention:** Use orchestrator, never manual `python3 -m http.server`

### 2. Component Patterns Must Match Framework
- **Lesson:** Progressive loader expected string returns, components used DOM manipulation
- **Impact:** Architectural mismatch broke all tabs except special-cased Engineering
- **Solution:** Remove incompatible layer, use direct visibility management
- **Prevention:** Document component contract, verify pattern consistency

### 3. Tab Visibility Timing
- **Lesson:** Components must find visible containers
- **Impact:** Calling render while tab hidden = getElementById fails
- **Solution:** Show tab FIRST, then render
- **Prevention:** Always manage visibility before component calls

### 4. Engineering Tab Special Case
- **Lesson:** Engineering worked because it created container first
- **Impact:** Masked the broader architectural problem
- **Solution:** Made all tabs follow same working pattern
- **Prevention:** Consistent patterns across all components

---

**Author:** Asif Hussain  
**Version:** 2.0  
**Updated:** December 7, 2025
