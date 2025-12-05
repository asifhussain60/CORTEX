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

---

**Author:** Asif Hussain  
**Version:** 1.0  
**Updated:** December 5, 2025
