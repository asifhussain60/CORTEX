# Phase 14 Enhancement Summary: Root-Level Entry Points Architecture

**Updated:** January 29, 2026  
**Version:** 2.0 (Enhanced with Entry Points)  
**Authority:** CORE-038 (File Placement), CORE-030 (Implementation Truth)

---

## 📋 What Was Updated

The Phase 14 LENS Dashboard Implementation plan has been enhanced with root-level entry point architecture:

### **Key Changes:**

1. **New Task: `task_002d_cortex_lens_entry_points`**
   - **AC-ID:** LENS-DASH-007
   - **Priority:** P0
   - **Effort:** 1 day
   - **Status:** Integrated into Phase 1 (Days 1-4)

2. **Entry Points Architecture:**
   ```
   cortex-lens/
   ├── repo-dashboards.html      ⭐ Main entry - repository browser
   ├── cortex-dashboard.html     ⭐ Direct CORTEX - 8-tab analysis
   └── (supporting folders)
   ```

3. **CLI Command Updates:**
   - Enhanced to support both entry points
   - `cortex lens dashboard serve` → repo-dashboards.html
   - `cortex lens dashboard serve cortex` → cortex-dashboard.html
   - New routing behavior documented

4. **Folder Structure Documentation:**
   - Added `cortex_lens_folder_structure` section
   - Added `app_py_routing` section with FastAPI endpoints
   - Clarified frontend component organization

---

## 🎯 Entry Point Architecture

### **repo-dashboards.html** (Main Entry)

**Purpose:** Repository browser with tiles

**Features:**
- Grid of repository tiles from recent analyses
- Search and filter by name, type, tags
- [+ Add Repository] button for new analysis
- Click tile to open that repository's dashboard
- [Recent] and [Bookmarks] tabs

**Loads:**
```
/static/vendor/alpine-3.13.3.min.js
/frontend/css/dashboard-ui.css (shared)
/frontend/js/repo-tiles.js (grid display)
/frontend/js/dashboard-app.js (shared logic)
```

**Accessed via:**
```bash
cortex lens dashboard serve
# http://localhost:8888/
```

---

### **cortex-dashboard.html** (CORTEX-Specific)

**Purpose:** Direct access to CORTEX 8-tab analysis

**Features:**
- Skips repository selection
- Loads all 8 tabs immediately (5 universal + 3 CORTEX-specific)
- [← Back to Repositories] button at top
- Tab navigation for all 8 tabs
- Overlay system (security, performance, compliance)

**Loads:**
```
/static/vendor/alpine-3.13.3.min.js
/static/vendor/d3-7.8.5.min.js
/frontend/css/dashboard-ui.css (shared)
/frontend/js/dashboard-app.js (shared logic)
```

**Accessed via:**
```bash
cortex lens dashboard serve cortex
# http://localhost:8888/cortex
```

---

## 🔄 FastAPI Routing (cortex-lens/app.py)

```python
@app.get("/")
def home():
    """Serve repo-dashboards.html - Repository browser"""
    return serve_file("repo-dashboards.html")

@app.get("/cortex")
def cortex_dashboard():
    """Serve cortex-dashboard.html - 8-tab CORTEX view"""
    return serve_file("cortex-dashboard.html")

@app.get("/api/dashboard/analyze")
def analyze_repository(repo: str, format: str = "json"):
    """Analyze repository and return data"""
    # Calls cortex-lens/backend/orchestrator.py
    # Which calls cortex/orchestrators/support/LENSVisualizationOrchestrator
    # Which returns data from cortex/visualization/*

@app.get("/api/dashboard/tab/{tab_id}")
def get_tab_data(tab_id: str, repo: str, overlay: str = None):
    """Get data for specific tab"""
    # Routes to appropriate renderer based on tab_id

@app.get("/api/dashboard/overlay/{overlay_type}")
def get_overlay_data(overlay_type: str, repo: str):
    """Get overlay data (security, performance, compliance)"""
    # Routes to overlay renderer
```

---

## 📁 Updated Folder Structure

```
cortex-lens/
├── repo-dashboards.html         # Main entry point
├── cortex-dashboard.html        # CORTEX shortcut
├── app.py                       # FastAPI server (routing)
│
├── backend/
│   ├── __init__.py
│   ├── orchestrator.py          # Routes to cortex/visualization/*
│   ├── cache_manager.py         # Manages dashboard cache
│   ├── repository_loader.py     # Analyzes repositories
│   └── routes.py                # API endpoints
│
├── frontend/
│   ├── css/
│   │   └── dashboard-ui.css     # Shared styles
│   ├── js/
│   │   ├── dashboard-app.js     # Shared Alpine.js logic
│   │   ├── repo-tiles.js        # Repository grid display
│   │   ├── tab-controller.js    # Tab management
│   │   ├── overlay-ui.js        # Overlay system
│   │   └── navigation.js        # Top-level navigation
│   └── views/                   # Tab fragments (from cortex/visualization/templates/)
│
├── static/                      # Symlink to cortex/visualization/static/vendor/
│   └── vendor/
│       ├── alpine-3.13.3.min.js
│       ├── d3-7.8.5.min.js
│       ├── mermaid-10.6.1.min.js
│       └── tailwind-3.4.0.min.css
│
├── tests/
│   ├── test_entry_points.py
│   ├── test_dashboard_api.py
│   └── test_cache_manager.py
│
├── docker/
│   ├── Dockerfile.dashboard
│   └── docker-compose.lens.yml
│
└── docs/
    └── dashboard-guide.md
```

---

## ✅ Test Coverage (task_002d)

**Test file:** `tests/cortex_lens/test_entry_points.py`

**Test cases:**
- ✅ GET / returns repo-dashboards.html
- ✅ GET /cortex returns cortex-dashboard.html
- ✅ Both entry points load Alpine.js correctly
- ✅ repo-dashboards.html shows repository tiles
- ✅ cortex-dashboard.html shows 8 tabs
- ✅ Shared JavaScript works from both entry points
- ✅ Tab fragments load correctly
- ✅ API routes serve JSON data

**Acceptance criteria:**
- ✅ Both HTML files at cortex-lens/ root (not in frontend/)
- ✅ Clear, descriptive filenames
- ✅ app.py routes correctly to both entry points
- ✅ Shared components loaded from frontend/
- ✅ Tab fragments loaded from cortex/visualization/templates/
- ✅ 100% test coverage
- ✅ Both entry points work offline (no external CDN)

---

## 🚀 Usage Examples

### Start Dashboard Server (Repository Browser)
```bash
cortex lens dashboard serve
# Opens http://localhost:8888/
# Landing: repo-dashboards.html (repository tiles)
# User can click on a repository to view its dashboard
```

### Start Dashboard Server (Direct CORTEX)
```bash
cortex lens dashboard serve cortex
# Opens http://localhost:8888/cortex
# Landing: cortex-dashboard.html (full 8 tabs immediately)
# User can click [← Back to Repositories] to return
```

### Generate Standalone Dashboard
```bash
cortex lens dashboard generate
# Generates in reports/lens-dashboard/ (if in CORTEX repo)
# Generates in .cortex/lens-dashboard/ (if in user repo)
```

### CLI Help
```bash
cortex lens dashboard --help
# Shows all available commands and entry point routing
```

---

## 🔄 Data Flow: Request to Visualization

```
User Request (http://localhost:8888/cortex)
    ↓
app.py routing: @app.get("/cortex")
    ↓
serve_file("cortex-dashboard.html")
    ↓
Browser loads HTML + Alpine.js
    ↓
Alpine.js calls backend/orchestrator.py via /api/*
    ↓
backend/orchestrator.py calls:
    cortex/orchestrators/support/LENSVisualizationOrchestrator
    ↓
LENSVisualizationOrchestrator:
    ├─ Calls cortex/brain/analysis/GitHistoryAnalyzer
    ├─ Calls cortex/brain/analysis/ASTAnalyzer
    ├─ Calls cortex/brain/analysis/CommentExtractor
    ├─ Calls cortex/visualization/renderers/d3_renderer.py
    ├─ Calls cortex/visualization/renderers/mermaid_renderer.py
    └─ Calls cortex/visualization/formatters/response_formatter.py
    ↓
Returns JSON (D3 data, Mermaid syntax, etc.)
    ↓
Alpine.js renders visualizations in browser
    ↓
User sees 8-tab CORTEX dashboard
```

---

## 📊 Phase 14 Task Timeline (Updated)

**Phase 1: Core Infrastructure (Days 1-4)**
- Task 001: Visualization package structure (0.5 days)
- Task 002a: Repository detector (0.5 days)
- Task 002b: Dashboard configuration (0.5 days)
- Task 002c: Output manager (1 day)
- **Task 002d: Entry points architecture (1 day)** ← NEW
- Task 003: Business language generator (2 days)
- Task 004: LENS visualization orchestrator (1.5 days)

**Phase 2: D3.js Visualizations (Days 5-8)** (unchanged)

**Phase 3: Mermaid Diagrams (Days 9-12)** (unchanged)

**Phase 4: API Routes & Frontend (Days 13-15)** (unchanged)

---

## 📝 Documentation Updates

Three new documentation files created in `docs/17-wiring/`:

1. **PHASE-14-FOLDER-STRUCTURE.md**
   - Complete three-folder CORTEX system overview
   - Detailed communication flows
   - User repository examples
   - Bundle size optimization

2. **PHASE-14-FOLDER-STRUCTURE-TREE.md**
   - Quick-reference tree format
   - Multiple repository scenarios
   - Tab visibility matrix
   - Performance metrics

3. **PHASE-14-QUICK-REFERENCE.md** (existing, updated)
   - Entry point routing behavior

---

## ✨ Benefits of Root-Level Entry Points

✅ **Clear Intent:** Filename explicitly states purpose  
✅ **Better UX:** Users see navigation immediately  
✅ **Simple Routing:** `cortex lens dashboard serve cortex` → cortex-dashboard.html  
✅ **No Confusion:** No generic index.html hiding purpose  
✅ **Discoverable:** Developers know what each file does  
✅ **Organized:** Frontend components in subfolders, entry points at root  
✅ **Maintainable:** Easy to find, understand, and modify  

---

## 🔐 Accidental Deletion Protection

With root-level entry points clearly named:

```bash
# .git/hooks/pre-commit
if git diff --cached --name-only | grep -q 'cortex-lens/.*\.html'; then
  echo "⚠️  Modifying cortex-lens entry points"
  echo "Review carefully: dashboard functionality depends on these files"
fi
```

Entry points are discoverable and protectable as critical files.

---

**Authority:** CORE-038 (File Placement), CORE-030 (Implementation Truth)  
**Updated:** January 29, 2026  
**Version:** Phase 14 v2.0 with Entry Point Architecture
