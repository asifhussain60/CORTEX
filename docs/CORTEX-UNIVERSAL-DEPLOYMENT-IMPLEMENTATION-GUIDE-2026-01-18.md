# CORTEX Universal Deployment Implementation Guide
## Building Multi-Repo, MCP-Exposed CORTEX System (2026-01-18)

---

## Executive Summary

This guide details the implementation of a revolutionary CORTEX architecture where:

1. **CORTEX operates from its own folder** (`./CORTEX/`) but reads/modifies user's repo
2. **MCP tools are exposed universally** via `CORTEX.prompt.md` from ANY company repo
3. **Single-command installation**: `git clone + cortex init` provides production-ready system
4. **Single-command upgrades**: `cortex upgrade` pulls latest features from main branch
5. **Complete isolation**: Parent repo completely unchanged except for `CORTEX/` folder
6. **Dashboard accessible immediately** with zero post-install configuration

---

## Architecture Overview

### Current CORTEX Model
```
company-repo/
├── .git/
├── src/
├── cortex/              ← CORTEX mixed with user code
├── cortex-brain/
├── dashboard/
└── [complex setup]
```

### New Universal Model
```
company-repo/
├── .git/
├── src/                 ← User repo (UNCHANGED)
├── tests/
├── [user files]
│
└── CORTEX/              ← NEW: Separate installation
    ├── .git/            ← Independent version history
    ├── cortex           ← CLI entry point
    ├── dashboard/
    ├── cortex-brain/
    └── [CORTEX files]
```

**Key Advantage**: CORTEX can operate on ANY repo structure without modification.

---

## Phase Implementation Roadmap

### PHASE-15-DASHBOARD-UNIVERSAL (16 ACs)
**Timeline**: Weeks 1-4  
**Prerequisite**: None (can start immediately)

#### Section A: Foundation (4 ACs)
- **AC-DASH-001-01**: Universal dashboard shell
  - Single HTML file with embedded JavaScript
  - No build process, CDN-only dependencies
  - Responsive design (mobile/tablet/desktop)
  - **Test**: Dashboard loads in <2 seconds on 3G

- **AC-DASH-001-02**: Repo detection & auto-config
  - Auto-detect parent repo structure
  - Auto-discover `.git`, `src/`, `tests/`, etc.
  - Cache config in `CORTEX/.cortex-config.yaml`
  - **Test**: Works in 5+ different repo structures

- **AC-DASH-001-03**: Real-time metrics collection
  - File count, test coverage, commit history
  - CORTEX operation count, MCP tool usage
  - Audit trail statistics
  - **Test**: All metrics update within <500ms

- **AC-DASH-001-04**: Multi-repo context switching
  - List all repos with CORTEX installed
  - Switch context with single click
  - Persist selected repo in browser storage
  - **Test**: Context switch completes in <1 second

#### Section B: Visualization (4 ACs)
- **AC-DASH-002-01**: Repository health overview
  - Visual indicators: file count, test coverage, commit rate
  - Trend charts (commits over 30 days)
  - Health score (0-100) based on metrics
  - **Test**: All visualizations render correctly

- **AC-DASH-002-02**: CORTEX operation dashboard
  - Last 100 AI operations timeline
  - Operation status (success/failure/pending)
  - Filter by operation type
  - **Test**: Loads 100 operations in <1 second

- **AC-DASH-002-03**: MCP tool status dashboard
  - List all MCP tools available to user
  - Tool usage statistics (calls, success rate)
  - Last 5 tool invocations with results
  - **Test**: Updates in real-time via WebSocket

- **AC-DASH-002-04**: Governance compliance heatmap
  - 80+ CORE rules visualized as grid
  - Color: green (100% compliant), yellow (warning), red (violation)
  - Click cell to see rule details & violations
  - **Test**: Heatmap updates when audit trail changes

#### Section C: Real-Time (4 ACs)
- **AC-DASH-003-01**: WebSocket connection to CORTEX backend
  - Establish persistent connection to `CORTEX/cortex-brain/`
  - Handle reconnection with exponential backoff
  - Broadcast events: new operations, audit entries, test results
  - **Test**: Connection maintains <100ms latency

- **AC-DASH-003-02**: Live audit trail streaming
  - Display audit entries in real-time
  - Show hash chain integrity checks
  - Alert on chain breaks (would be rare)
  - **Test**: Entries appear <500ms after creation

- **AC-DASH-003-03**: Real-time test tracking
  - Show running tests with progress bars
  - Display pass/fail as tests complete
  - Link to test logs
  - **Test**: All test state changes reflected immediately

- **AC-DASH-003-04**: Alert & notification system
  - Toast notifications for critical events
  - Persistent notification area for warnings
  - Sound alerts for failures (if enabled)
  - **Test**: All notification types display correctly

#### Section D: UX (4 ACs)
- **AC-DASH-004-01**: Dark/light theme toggle
  - Theme toggle button in top-right
  - Remember user preference in localStorage
  - All charts & tables adapt to theme
  - **Test**: Theme persists across sessions

- **AC-DASH-004-02**: Export reports
  - Export current view as PDF
  - Export metrics as CSV
  - Export complete audit trail as JSON
  - **Test**: All export formats work correctly

- **AC-DASH-004-03**: Custom dashboard layouts
  - Drag-to-reorder dashboard cards
  - Collapse/expand individual sections
  - Save layout preference
  - **Test**: Layout persists across sessions

- **AC-DASH-004-04**: Search & filter
  - Search operations by keyword
  - Filter audit trail by date range
  - Filter MCP tools by status
  - **Test**: Search returns results in <100ms

### PHASE-DEPLOYMENT (10 ACs)
**Timeline**: Weeks 5-8 (starts after PHASE-15 locked)  
**Prerequisite**: PHASE-15-DASHBOARD-UNIVERSAL locked: true

#### Section A: Bootstrap (3 ACs)
- **AC-DEPLOY-001-01**: `cortex init` command
  - Accepts single parameter: repo path (defaults to `..`)
  - Creates `.env` from `.env.example`
  - Initializes SQLite governance.db
  - Generates `.cortex-config.yaml`
  - **Test**: Init completes in <30 seconds, all files created

- **AC-DEPLOY-001-02**: Auto-detection of repo structure
  - Detect parent repo `.git/` location
  - Scan for `src/`, `tests/`, `docs/`, `scripts/`
  - Infer project type (Python/Node/Go/etc.)
  - Store detection in config
  - **Test**: Correctly identifies 5+ different project structures

- **AC-DEPLOY-001-03**: MCP tool registration
  - Detect user's MCP client (Claude.app, VSCode, etc.)
  - Auto-register CORTEX tools in MCP client config
  - Create symlink/reference to `CORTEX.prompt.md`
  - **Test**: Tools appear in MCP client immediately

#### Section B: Multi-Repo (3 ACs)
- **AC-DEPLOY-002-01**: Path isolation (CORTEX folder separation)
  - All CORTEX operations use relative paths from `CORTEX/` folder
  - All file operations on parent repo use `../` relative paths
  - No hardcoded absolute paths anywhere
  - Governance.db stored in `CORTEX/cortex-brain/state/`
  - **Test**: Works when CORTEX folder moved to different location

- **AC-DEPLOY-002-02**: Context switching between repos
  - `cortex switch ../other-repo/CORTEX` command
  - Updates config to point to different parent repo
  - Re-initializes metrics collection for new repo
  - **Test**: Successfully switches between 3+ repos

- **AC-DEPLOY-002-03**: Shared state management
  - Shared cache: `CORTEX/.cortex-cache/`
  - Repo-specific state: `CORTEX/.cortex-state/<repo-hash>/`
  - Audit trail merged across all repos
  - **Test**: State persists and syncs correctly

#### Section C: Upgrade (2 ACs)
- **AC-DEPLOY-003-01**: `cortex upgrade` command
  - Fetch latest from main branch
  - Check for breaking changes
  - Auto-merge non-breaking changes
  - Migrate state if needed
  - **Test**: Upgrade completes without data loss

- **AC-DEPLOY-003-02**: Backward-compatible versioning
  - Track CORTEX version in `CORTEX/.cortex-version`
  - Migration scripts for version transitions
  - Verify hash chain integrity post-upgrade
  - **Test**: Can upgrade from previous version without issues

#### Section D: Production (2 ACs)
- **AC-DEPLOY-004-01**: Security hardening
  - No secrets stored in CORTEX folder
  - All secrets in `.env` (not in git)
  - Audit logging of all file operations
  - **Test**: No secrets appear in git history

- **AC-DEPLOY-004-02**: Performance optimization
  - Startup time: <1 second
  - Dashboard load: <2 seconds
  - MCP tool invoke: <500ms average
  - Memory usage: <50MB baseline
  - **Test**: All performance targets met

---

## Implementation Sequence

### Week 1: Dashboard Foundation (AC-DASH-001-01/02/03/04)

**Day 1-2: AC-DASH-001-01 - Universal Dashboard Shell**
```bash
# Create minimal HTML shell
CORTEX/dashboard/index.html        # 500 lines with embedded JS
CORTEX/dashboard/styles.embedded  # CSS in <style> tag
CORTEX/dashboard/script.embedded  # JS in <script> tag
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Dashboard</title>
    <style>
        /* All styling embedded - no external CSS */
    </style>
</head>
<body>
    <div id="app">
        <!-- React-free, vanilla JS only -->
    </div>
    <script>
        // All JavaScript embedded - no external files
    </script>
</body>
</html>
```

**Day 3: AC-DASH-001-02 - Repo Auto-Detection**
```python
# CORTEX/scripts/detect-repo.py
import os
import yaml
from pathlib import Path

def detect_repo_structure(parent_path="../"):
    """Auto-detect parent repo structure"""
    config = {
        "repo_path": os.path.abspath(parent_path),
        "has_git": os.path.exists(f"{parent_path}/.git"),
        "has_src": os.path.exists(f"{parent_path}/src"),
        "has_tests": os.path.exists(f"{parent_path}/tests"),
        "languages": detect_languages(parent_path),
        "frameworks": detect_frameworks(parent_path),
    }
    
    # Save to CORTEX/.cortex-config.yaml
    with open(".cortex-config.yaml", "w") as f:
        yaml.dump(config, f)
    
    return config
```

**Day 4: AC-DASH-001-03 - Metrics Collection**
```python
# CORTEX/scripts/collect-metrics.py
def get_repo_metrics(parent_path="../"):
    """Collect metrics from parent repo"""
    return {
        "file_count": count_files(parent_path),
        "test_coverage": get_test_coverage(parent_path),
        "commit_count": get_git_commits(parent_path),
        "cortex_operations": query_cortex_operations(),
        "mcp_tool_usage": query_tool_usage(),
        "audit_entries": query_audit_trail(),
    }
```

**Day 5: AC-DASH-001-04 - Multi-Repo Switching**
```javascript
// CORTEX/dashboard/index.html (in <script> tag)
function switchRepo(repoPath) {
    fetch(`/api/context/switch`, {
        method: "POST",
        body: JSON.stringify({ repo_path: repoPath })
    }).then(() => {
        localStorage.setItem("selected_repo", repoPath);
        location.reload();
    });
}
```

**Tests for Week 1** (test-first approach per CORE-008):
```python
# CORTEX/tests/test_dashboard_foundation.py
def test_dashboard_loads():
    response = requests.get("/dashboard")
    assert response.status_code == 200
    assert "CORTEX Dashboard" in response.text

def test_repo_detection():
    config = detect_repo_structure("../")
    assert config["repo_path"] is not None
    assert config["has_git"] == True

def test_metrics_collection():
    metrics = get_repo_metrics("../")
    assert "file_count" in metrics
    assert metrics["file_count"] > 0

def test_context_switching():
    response = requests.post("/api/context/switch", 
        json={"repo_path": "../other-repo"})
    assert response.status_code == 200
```

### Week 2: Dashboard Visualization (AC-DASH-002-01/02/03/04)

Similar structure: write tests first, then implement each AC.

Key patterns:
- Use Tailwind CSS via CDN (no build step)
- Use Chart.js for graphs (from CDN)
- D3.js for complex visualizations (from CDN)
- Vanilla JavaScript only (no React/Vue)

### Week 3: Real-Time Features (AC-DASH-003-01/02/03/04)

WebSocket implementation:
```python
# CORTEX/cortex-brain/api/websocket.py
from fastapi import WebSocket

@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        metrics = get_repo_metrics()
        await websocket.send_json(metrics)
        await asyncio.sleep(1)  # Update every second
```

### Week 4: UX Polish (AC-DASH-004-01/02/03/04)

Focus on user experience:
- Smooth transitions
- Responsive design
- Accessibility (keyboard navigation, screen readers)
- Error handling & recovery

---

## PHASE-DEPLOYMENT Implementation (After PHASE-15 Locked)

### AC-DEPLOY-001-01: `cortex init` Command

```bash
#!/bin/bash
# CORTEX/cortex

if [ "$1" == "init" ]; then
    PARENT_REPO="${2:-.}"
    
    # 1. Copy .env
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo "Created .env - edit with your settings"
    fi
    
    # 2. Initialize SQLite governance.db
    python3 scripts/init_db.py
    
    # 3. Detect repo structure
    python3 scripts/detect-repo.py "$PARENT_REPO"
    
    # 4. Register MCP tools
    python3 scripts/register_mcp.py
    
    # 5. Start dashboard
    echo "✅ CORTEX initialized!"
    echo "🚀 Starting dashboard..."
    python3 cortex-brain/api/main.py
fi
```

### AC-DEPLOY-002-01: Path Isolation

```python
# CORTEX/cortex-brain/config.py
from pathlib import Path
import os

class Config:
    # CORTEX folder location
    CORTEX_ROOT = Path(__file__).parent.parent
    
    # Parent repo location (always relative)
    PARENT_REPO = CORTEX_ROOT.parent
    
    # All paths computed relative to these base paths
    @property
    def src_path(self):
        return self.PARENT_REPO / "src"
    
    @property
    def tests_path(self):
        return self.PARENT_REPO / "tests"
    
    @property
    def governance_db(self):
        return self.CORTEX_ROOT / "cortex-brain" / "state" / "governance.db"
```

### AC-DEPLOY-003-01: `cortex upgrade` Command

```bash
#!/bin/bash
# In cortex CLI
if [ "$1" == "upgrade" ]; then
    echo "⬆️  Upgrading CORTEX..."
    
    # 1. Fetch latest
    git fetch origin main
    
    # 2. Check for breaking changes
    BREAKING=$(git log HEAD..origin/main --grep="BREAKING" --oneline)
    if [ ! -z "$BREAKING" ]; then
        echo "⚠️  Breaking changes detected:"
        echo "$BREAKING"
        read -p "Continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 3. Merge latest
    git merge origin/main --no-edit
    
    # 4. Migrate state if needed
    python3 scripts/migrate.py
    
    # 5. Verify hash chain
    python3 scripts/verify_integrity.py
    
    echo "✅ CORTEX upgraded successfully!"
fi
```

---

## Testing Strategy

### CORE-008: Tests First (RED → GREEN)

For EVERY AC-ID:

1. **RED**: Write test that fails
   ```python
   def test_ac_dash_001_01_dashboard_loads():
       response = requests.get("/dashboard")
       assert response.status_code == 200
       assert response.headers["content-type"] == "text/html"
   ```

2. **GREEN**: Implement to pass test
   ```python
   @app.get("/dashboard")
   def get_dashboard():
       return FileResponse("dashboard/index.html")
   ```

3. **REFACTOR**: Improve code quality
   - Add type hints (CORE-011)
   - Add docstrings (CORE-012)
   - Improve error handling (CORE-013)

### Test Organization

```
CORTEX/tests/
├── test_dashboard_foundation.py       # AC-DASH-001-*
├── test_dashboard_visualization.py    # AC-DASH-002-*
├── test_dashboard_realtime.py         # AC-DASH-003-*
├── test_dashboard_ux.py               # AC-DASH-004-*
├── test_deployment_bootstrap.py       # AC-DEPLOY-001-*
├── test_deployment_multirepo.py       # AC-DEPLOY-002-*
├── test_deployment_upgrade.py         # AC-DEPLOY-003-*
└── test_deployment_production.py      # AC-DEPLOY-004-*
```

### Coverage Requirements

- All ACs must have >85% code coverage
- Critical functions (file I/O, database) must have >95% coverage
- Security-related code must have 100% coverage

---

## Git Checkpoint Protocol (CORE-026)

Before major checkpoints:

```bash
# After each AC completion
git add .
git commit -m "AC-DASH-001-01: Universal dashboard shell complete ✅"

# After each Section (4 ACs)
git add .
git commit -m "Section A (AC-DASH-001-*): Dashboard Foundation complete ✅"

# After each Phase
git add .
git commit -m "PHASE-15-DASHBOARD-UNIVERSAL: All 16 ACs complete ✅"
git tag -a "PHASE-15-DASHBOARD-UNIVERSAL-COMPLETE" -m "Production ready"
```

---

## Deployment Verification Checklist

- [ ] All 16 AC-DASH ACs passing 100% of tests
- [ ] All 10 AC-DEPLOY ACs passing 100% of tests
- [ ] Dashboard loads in <2 seconds
- [ ] MCP tools functional in 5+ repos
- [ ] `cortex upgrade` works without data loss
- [ ] No secrets in CORTEX folder
- [ ] Audit trail verifies integrity
- [ ] All CORE-008 through CORE-028 governance rules followed
- [ ] Documentation complete and tested
- [ ] Performance meets all targets
- [ ] Security hardening complete

---

## Success Metrics

### PHASE-15-DASHBOARD-UNIVERSAL
- ✅ Works in ANY repo with zero config
- ✅ Dashboard loads in <2 seconds
- ✅ All 16 ACs passing tests
- ✅ 100% uptime on WebSocket connections
- ✅ <100ms latency on metrics updates

### PHASE-DEPLOYMENT
- ✅ Installation takes <5 minutes
- ✅ `cortex upgrade` success rate >99%
- ✅ Zero breaking changes to parent repo
- ✅ All 10 ACs passing tests
- ✅ <1 second startup time

---

## Next Steps

1. **Immediate**: Begin PHASE-15 implementation (Week 1 starts today)
2. **Week 2-4**: Complete dashboard with full testing
3. **Week 5+**: Begin PHASE-DEPLOYMENT implementation
4. **Quality Gates**: Maintain 100% test pass rate throughout
5. **Regular Sync**: Update `implement_when_ready` phases as needed

This architecture delivers CORTEX as a universal, multi-repo, MCP-exposed development orchestration system.
