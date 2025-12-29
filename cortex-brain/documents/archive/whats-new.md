# 🆕 What's New in CORTEX 3.7.1

**Released:** December 5, 2025

## Dashboard Launcher
New command to launch CORTEX dashboard with HTTP server and auto-open browser.

**Natural Language Triggers:**
- `load dashboard` - Launch with defaults (port 8080, auto-open)
- `launch dashboard` - Alternative trigger
- `open dashboard` - Alternative trigger
- `show dashboard` - Alternative trigger
- `dashboard` - Quick access

**Features:**
- ✅ HTTP server auto-serves from `cortex-brain/dashboards/ui/`
- ✅ Smart port selection (8080-8089 auto-fallback)
- ✅ Auto-open browser with configurable data source
- ✅ CORS enabled for local development
- ✅ Background server process (non-blocking)
- ✅ Graceful shutdown (Ctrl+C)

**Files:**
- Orchestrator: `src/orchestrators/dashboard_launcher.py` (376 lines)
- Module: `src/operations/modules/dashboard_launcher_module.py` (149 lines)
- Guide: `cortex-brain/documents/implementation-guides/dashboard-launcher-quick-ref.md`
- YAML: `cortex-operations.yaml` (load_dashboard operation)

**Integration:**
- Auto-routed via Intent Router
- Registered in cortex-operations.yaml
- 8 natural language triggers
- 3 profiles: standard, custom_port, no_browser

**Example:**
```
User: load dashboard

CORTEX: ✅ Dashboard server started successfully

🌐 URL: http://localhost:8080/index.html?source=mock
🔌 Port: 8080
📁 Directory: cortex-brain/dashboards/ui

💡 Dashboard will open automatically in your browser
🛑 Press Ctrl+C in the terminal to stop the server
```

---

## What's New in 3.2.1

**Released:** November 2024

### Git Integration Enforcement
- 18-gate deployment system with git checkpoint validation
- Mandatory clean working directory before deployment
- Auto-stashing with recovery on deployment failure

### Version Cleanup
- Removed all legacy 5.3.x references
- Unified versioning scheme across all components
- Single source of truth in VERSION file

### Universal Upgrade System
- One command works for all repositories (standalone/embedded)
- Smart detection of installation type
- Zero data loss with automatic brain backup
- Path validation and post-upgrade verification

### Issue #3 Fixes
- ViewDiscoveryAgent enhancements
- FeedbackAgent improvements
- Enhanced TDD workflow integration
