# CORTEX Dashboard SPA - Restructured Architecture

**Version:** 2.0  
**Date:** 2026-02-04  
**Status:** ✅ Production Ready

## Overview

This document describes the restructured Single Page Application (SPA) architecture for the CORTEX Dashboard. The restructuring improves code organization, maintainability, and scalability by separating concerns into frontend and backend layers.

## Directory Structure

```
_workspaces/dashboard/
├── frontend/                           # All SPA frontend files
│   ├── public/                         # Static HTML files
│   │   ├── index.html                  # Main dashboard
│   │   ├── lens-dashboard.html         # LENS analysis dashboard
│   │   └── compliance.html             # Governance compliance view
│   │
│   ├── src/                            # Source files
│   │   ├── js/                         # JavaScript files
│   │   │   ├── cortex-unified.js       # Main framework (initialization, tabs, theme)
│   │   │   └── components/             # Reusable components
│   │   │       ├── cortex-components.js      # Core UI components
│   │   │       ├── chart-builder.js          # Chart.js integration
│   │   │       ├── d3-force-graph.js         # D3 force-directed graph
│   │   │       └── data-renderer.js          # Data rendering engine
│   │   │
│   │   └── css/                        # Stylesheets
│   │       ├── cortex-unified.css      # Main styles
│   │       ├── animations.css          # Animation definitions
│   │       ├── colors.css              # Color palette
│   │       ├── glassmorphism.css       # Glass morphism effects
│   │       ├── header.css              # Header styling
│   │       ├── responsive.css          # Responsive breakpoints
│   │       ├── search.css              # Search bar styling
│   │       ├── sidebar.css             # Sidebar styling
│   │       ├── tabs.css                # Tab component styling
│   │       └── tailwind-custom.css     # Tailwind customizations
│   │
│   ├── assets/                         # Static assets
│   │   ├── cortex-logo.svg
│   │   └── cortex-logo-white.svg
│   │
│   └── components/                     # Reusable Vue/JS components (future)
│       ├── common/                     # Common UI elements
│       ├── brain/                      # Brain visualization
│       ├── neural/                     # Neural network viz
│       ├── orchestrator/               # Orchestrator grid
│       ├── temporal/                   # Timeline components
│       └── utils/                      # Utility functions
│
├── backend/                            # Python backend API server
│   ├── dashboard_renderer.py           # Dashboard data rendering
│   ├── launch.py                       # Server launcher
│   ├── serve_cortex_dashboard.py       # HTTP server
│   ├── intent_router.py                # Intent routing logic
│   ├── lens_orchestrator.py            # LENS analysis orchestrator
│   ├── governance_heatmap.py           # Governance heatmap
│   ├── mermaid_diagram_generator.py    # Diagram generation
│   ├── multi_mode_formatter.py         # Multi-mode response formatting
│   ├── remote_git_adapter.py           # Git integration
│   └── api/                            # API routes & handlers
│
├── tests/                              # Test suite
│   └── test_spa_structure.py           # SPA structure & path validation
│
├── ARCHIVE/                            # Legacy files (preserved for history)
│   ├── enhancements_*.* (23 files)     # Old enhancement files
│   └── legacy Python files
│
└── README.md (this file)
```

## File Path References

### HTML Files Location
- `frontend/public/*.html` - All HTML files served from this directory

### JavaScript Loading (from HTML)
```html
<!-- Main framework -->
<script src="../src/js/cortex-unified.js"></script>

<!-- Components -->
<script src="../src/js/components/cortex-components.js"></script>
<script src="../src/js/components/chart-builder.js"></script>
<script src="../src/js/components/d3-force-graph.js"></script>
<script src="../src/js/components/data-renderer.js"></script>
```

### CSS Loading (from HTML)
```html
<link rel="stylesheet" href="../src/css/cortex-unified.css">
```

### Relative Path Reference
- From: `frontend/public/index.html`
- To: `frontend/src/js/cortex-unified.js`
- Path: `../src/js/cortex-unified.js` (one level up, then into src/js/)

## Key Features

### Frontend (SPA)
- **Tab Navigation** - Switch between Overview, Architecture, Code Quality, Dependencies, Testing
- **Dark/Light Theme Toggle** - System-level theme switching
- **Chart.js Integration** - Dynamic chart rendering
- **D3 Visualizations** - Force-directed graph layouts
- **Responsive Design** - Works on desktop, tablet, mobile
- **Real-time Data Injection** - JSON data embedded in HTML

### Backend (Python)
- **Dashboard Renderer** - Generates dashboard data from codebase analysis
- **LENS Orchestrator** - Code analysis and intelligence
- **Governance Heatmap** - Compliance tracking
- **Mermaid Diagrams** - Architecture visualization
- **Git Integration** - Commit history analysis
- **HTTP Server** - Serves SPA and API

## Development Workflow

### Adding New Components

1. Create JavaScript file in `frontend/src/js/components/`
2. Reference in `frontend/public/*.html`
3. Use relative path: `../src/js/components/my-component.js`

### Adding New Styles

1. Create CSS file in `frontend/src/css/`
2. Reference in `frontend/public/*.html`
3. Use relative path: `../src/css/my-styles.css`

### Modifying Backend

1. Update Python files in `backend/`
2. Test with: `python3 backend/serve_cortex_dashboard.py`
3. Access at: `http://localhost:8000`

## Testing

Run the SPA structure validation test suite:

```bash
cd _workspaces/dashboard
python3 tests/test_spa_structure.py
```

**Tests Include:**
- ✅ Directory structure validation
- ✅ HTML file existence
- ✅ JavaScript file existence
- ✅ CSS file existence
- ✅ File path references (resolves relative paths)
- ✅ No orphaned enhancement files
- ✅ Backend files properly organized
- ✅ Archive directory integrity
- ✅ No duplicate assets
- ✅ File permissions
- ✅ HTML validity

## Migration Notes

### Files Moved (2026-02-04)

**Frontend Files:**
- `index.html` → `frontend/public/`
- `lens-dashboard.html` → `frontend/public/`
- `compliance.html` → `frontend/public/`
- `cortex-unified.js` → `frontend/src/js/`
- `cortex-components.js` → `frontend/src/js/components/`
- `chart-builder.js` → `frontend/src/js/components/`
- `d3-force-graph.js` → `frontend/src/js/components/`
- `data-renderer.js` → `frontend/src/js/components/`
- `cortex-unified.css` → `frontend/src/css/`
- All enhancement CSS files → `frontend/src/css/`

**Backend Files:**
- `dashboard_renderer.py` → `backend/`
- `launch.py` → `backend/`
- `serve_cortex_dashboard.py` → `backend/`
- `intent_router.py` → `backend/`
- `lens_orchestrator.py` → `backend/`
- `api/` directory → `backend/api/`

**Archived (for history):**
- 20+ `enhancements_*.*` files → `ARCHIVE/`
- Orphaned Python files → `ARCHIVE/`

## Performance Considerations

### Caching
- Add `?v=1.0.2` query string to assets for cache busting
- CDN: Chart.js and D3 loaded from CDN (external)

### Load Order
1. CSS: cortex-unified.css
2. Vendor JS: Chart.js, D3 (external CDN)
3. Framework: cortex-unified.js
4. Components: cortex-components.js, chart-builder.js, d3-force-graph.js, data-renderer.js

### Optimization Opportunities
- Minify CSS and JS for production
- Lazy load non-critical components
- Implement code splitting
- Use service workers for offline support

## API Integration

Backend serves static HTML + dynamic JSON API:

```
GET  /api/analysis         - Dashboard analysis data
GET  /api/orchestrators    - Orchestrator metrics
GET  /api/compliance       - Governance compliance
POST /api/diagnose         - Run diagnostics
```

## Troubleshooting

### 404 Errors
- Verify file exists in correct directory
- Check relative path references
- Run: `python3 tests/test_spa_structure.py`

### CSS Not Loading
- Check `<link>` path: should be `../src/css/filename.css`
- Verify CSS file exists in `frontend/src/css/`

### JavaScript Not Executing
- Check `<script>` path: should be `../src/js/filename.js`
- Verify JS file exists in `frontend/src/js/` or `frontend/src/js/components/`
- Check browser console for errors

### Backend Server Issues
- Verify Python in `backend/serve_cortex_dashboard.py`
- Check port availability (default: 8000)
- Run: `python3 backend/launch.py`

## Next Steps

1. **Implement Build Tool** - Webpack/Vite for module bundling
2. **Add Unit Tests** - Jest for JavaScript testing
3. **E2E Testing** - Playwright for browser automation
4. **CI/CD Pipeline** - GitHub Actions for automated testing
5. **Performance Monitoring** - Web Vitals tracking
6. **Accessibility** - WCAG 2.1 AA compliance
7. **Documentation** - API docs generation

## Support

For issues or questions:
1. Check test output: `python3 tests/test_spa_structure.py`
2. Review file structure against this README
3. Verify relative paths are correct
4. Check browser console for JavaScript errors
5. Open issue in CORTEX repository

---

**Architecture Review:** ✅ Passed  
**File Path Validation:** ✅ All 11 tests passing  
**Production Ready:** ✅ Yes
