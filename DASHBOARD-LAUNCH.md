# CORTEX Dashboard Quick Launch

## Usage

### Option 1: PowerShell Script (Recommended)

```powershell
# Launch with default settings (port 8080, auto-open browser)
.\launch-dashboard.ps1

# Launch on custom port
.\launch-dashboard.ps1 -Port 9000

# Launch without opening browser
.\launch-dashboard.ps1 -NoBrowser
```

### Option 2: Manual Launch

```powershell
cd cortex-brain\dashboards
python -m http.server 8080
```

Then open: http://localhost:8080/ui/index.html?source=mock

## Features

- ✅ Auto-detects correct directory (`cortex-brain/dashboards/`)
- ✅ Smart port selection (falls back to 8081-8089 if 8080 in use)
- ✅ Auto-opens browser to dashboard URL
- ✅ Validates directory structure before launch
- ✅ Graceful shutdown with Ctrl+C

## Troubleshooting

**Port already in use:**
Script automatically tries ports 8081-8089. Or specify custom port:
```powershell
.\launch-dashboard.ps1 -Port 9000
```

**Dashboard not loading:**
- Ensure you're running from CORTEX root directory
- Check that `cortex-brain/dashboards/ui/index.html` exists
- Verify Python is installed: `python --version`

**Browser doesn't open:**
Use `-NoBrowser` flag and manually open:
```
http://localhost:8080/ui/index.html?source=mock
```

## Data Sources

- `mock` - Test data (default)
- `luum-fresh` - Luum Fresh project
- `tcbulk` - TC Bulk project
- `v5-coldfusion` - V5 ColdFusion
- `v5-prevalidation-ws` - V5 PreValidation

Change source via URL parameter:
```
http://localhost:8080/ui/index.html?source=luum-fresh
```

## Architecture

Dashboard uses Phase 3 BaseTabComponent pattern:
- All 8 tabs extend `BaseTabComponent`
- Data loaded from `data/repositories/{source}/`
- ES6 modules with top-level imports
- Python HTTP server (no Node.js required)
