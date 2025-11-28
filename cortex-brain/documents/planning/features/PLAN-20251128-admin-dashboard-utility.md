# Admin Dashboard Utility - Comprehensive Implementation Plan

**Version:** 1.0  
**Created:** 2025-11-28  
**Author:** Asif Hussain  
**Status:** Planning Phase  
**Priority:** HIGH

---

## 🎯 Executive Summary

Create a web-based Admin Dashboard Utility that consolidates CORTEX admin operations (align, optimize, cleanup, sync, healthcheck, deploy) into a unified, interactive interface with **zero user approval interruptions** and real-time progress monitoring.

**Critical UX Requirement:** Eliminate constant VS Code approval prompts that currently block admin operations. Dashboard must execute operations non-interactively with background progress tracking.

---

## 📊 Problem Analysis

### Current State Issues

**Issue #1: Approval Workflow Interruptions**
```
User Experience (Current):
1. User runs: "align"
2. VS Code prompts: "Allow execution? [Allow] [Deny]"
3. User clicks Allow
4. Operation runs 5 seconds
5. VS Code prompts: "Allow file write? [Allow] [Deny]"
6. User clicks Allow (AGAIN)
7. Operation continues
8. VS Code prompts: "Allow git command? [Allow] [Deny]"
9. User clicks Allow (THIRD TIME)
10. Operation completes

Result: User must approve 3-5 times per operation
Defeats purpose: Manual intervention required constantly
```

**Issue #2: 0% Health Dashboard**
- Root cause: Brain validation failure during alignment
- Path resolution issues (case-sensitive config lookup)
- Prevents accurate health metrics display

**Issue #3: No Centralized Admin Control**
- 6+ admin operations scattered across CLI commands
- No unified view of system health
- No progress tracking across operations
- No operation history/audit trail

### Root Cause: Interactive Orchestrators

**Orchestrators with User Input Prompts:**

| Orchestrator | Interactive Prompts | Impact on Dashboard |
|--------------|---------------------|---------------------|
| `GitCheckpointOrchestrator` | Line 497: `input("\nYour choice (A/B/C/X): ")` | BLOCKS execution until user input |
| `GitCheckpointOrchestrator` | Line 755: `input("Type 'yes' to confirm rollback: ")` | BLOCKS rollback operations |
| `PlanningOrchestrator` | Checkpoints 1-4: User approval gates | BLOCKS planning workflow |
| `RollbackOrchestrator` | Confirmation prompts | BLOCKS rollback operations |
| `CleanupOrchestrator` | Dry-run confirmation | BLOCKS cleanup operations |

**VS Code Approval Layer:**
- VS Code extension security requires user approval for:
  * File system operations (read/write/delete)
  * Git commands (commit, checkout, tag)
  * Terminal command execution
  * Network operations (API calls)

---

## ✅ Solution Architecture

### Option C: Hybrid Approach (RECOMMENDED)

**Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│   Browser UI (HTML + HTMX + Alpine.js)                  │
│   ├── Static HTML dashboard (D3.js visualizations)      │
│   ├── Admin operation buttons (align, optimize, etc.)   │
│   ├── Real-time progress (Server-Sent Events)           │
│   └── Operation history/audit log                       │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP/JSON API
┌─────────────────▼───────────────────────────────────────┐
│   FastAPI Backend (Lightweight Local Server)            │
│   ├── Port: 7878 (auto-launch on first use)             │
│   ├── Non-interactive orchestrator wrappers             │
│   ├── Progress monitoring (SSE endpoint)                │
│   ├── Operation queue (async execution)                 │
│   └── Audit logger (SQLite)                             │
└─────────────────┬───────────────────────────────────────┘
                  │ Direct Python imports
┌─────────────────▼───────────────────────────────────────┐
│   Existing Python Orchestrators (NON-INTERACTIVE MODE)  │
│   ├── SystemAlignmentOrchestrator (auto_approve=True)   │
│   ├── OptimizeOrchestrator (skip_confirm=True)          │
│   ├── CleanupOrchestrator (force=True)                  │
│   ├── GitCheckpointOrchestrator (confirm=False)         │
│   ├── HealthCheckOrchestrator (no input needed)         │
│   └── DeploymentOrchestrator (batch_mode=True)          │
└─────────────────────────────────────────────────────────┘
```

**Key Design Decisions:**

✅ **Non-Interactive Mode Flag:**
- Add `non_interactive: bool = False` parameter to all orchestrators
- When `True`, bypass all `input()` calls
- Use sensible defaults (e.g., `confirm=False`, `force=True`)

✅ **Approval Strategy:**
- User approves operation at dashboard UI level (single click)
- Backend executes with `non_interactive=True`
- No mid-operation prompts
- Progress streamed via SSE

✅ **VS Code Bypass:**
- FastAPI runs outside VS Code extension context
- Direct Python subprocess execution
- File operations use native Python (not VS Code API)
- Git operations use GitPython library (not VS Code Git)

---

## 🏗️ Implementation Phases

### Phase 1: Non-Interactive Orchestrator Refactoring (HIGH PRIORITY)

**Goal:** Make all orchestrators support non-interactive mode

**Tasks:**

**1.1 Add NonInteractiveMode Parameter**
```python
# Base pattern for all orchestrators
class BaseOperationModule:
    def __init__(self, non_interactive: bool = False, **kwargs):
        self.non_interactive = non_interactive
        # ... existing init
    
    def _get_user_input(self, prompt: str, default: str = "") -> str:
        """Safe input wrapper that respects non-interactive mode."""
        if self.non_interactive:
            self.logger.info(f"Non-interactive mode: using default '{default}' for prompt: {prompt}")
            return default
        return input(prompt)
    
    def _get_user_confirmation(self, prompt: str, default: bool = False) -> bool:
        """Safe confirmation wrapper."""
        if self.non_interactive:
            self.logger.info(f"Non-interactive mode: auto-{'approving' if default else 'rejecting'}: {prompt}")
            return default
        response = input(f"{prompt} (yes/no): ").strip().lower()
        return response == 'yes'
```

**1.2 Refactor GitCheckpointOrchestrator**
```python
# Line 497 - Replace direct input() call
# OLD:
choice = input("\nYour choice (A/B/C/X): ").strip().upper()

# NEW:
choice = self._get_user_input("\nYour choice (A/B/C/X): ", default="C").strip().upper()
```

```python
# Line 755 - Replace confirmation input()
# OLD:
confirmation = input("Type 'yes' to confirm rollback: ").strip().lower()

# NEW:
confirmation = "yes" if self._get_user_confirmation("Confirm rollback?", default=False) else "no"
```

**1.3 Refactor PlanningOrchestrator**
```python
# Add auto-approve mode for incremental planning
def generate_incremental_plan(
    self,
    feature_requirements: str,
    checkpoint_callback: Optional[Callable[[str, str, str], bool]] = None,
    auto_approve: bool = False,  # NEW parameter
    output_filename: Optional[str] = None
) -> Tuple[bool, Optional[Path], str]:
    """
    If auto_approve=True, skip all checkpoint prompts.
    """
    if auto_approve:
        # Auto-approve all checkpoints
        checkpoint_callback = lambda cp_id, name, preview: True
    # ... existing logic
```

**1.4 Refactor CleanupOrchestrator**
```python
class CleanupOrchestrator:
    def execute(self, context: Dict = None, force: bool = False) -> AgentResponse:
        """
        force=True bypasses dry-run confirmation
        """
        if not force:
            # Show dry-run, ask for confirmation
            if not self._get_user_confirmation("Proceed with cleanup?", default=False):
                return AgentResponse(success=False, message="Cleanup cancelled by user")
        # Execute cleanup
```

**Affected Files:**
- `src/orchestrators/git_checkpoint_orchestrator.py` (2 changes)
- `src/orchestrators/planning_orchestrator.py` (4 checkpoints)
- `src/orchestrators/rollback_orchestrator.py` (confirmation prompts)
- `src/operations/modules/admin/cleanup_orchestrator.py` (dry-run confirm)
- `src/operations/modules/admin/system_alignment_orchestrator.py` (validation prompts)

**Deliverables:**
- ✅ All orchestrators support `non_interactive=True`
- ✅ Test suite validates both interactive/non-interactive modes
- ✅ Documentation updated with non-interactive usage examples

---

### Phase 2: FastAPI Backend (3-4 hours)

**Goal:** Lightweight local HTTP server for orchestrator operations

**2.1 Server Setup**
```python
# src/dashboard/admin_dashboard_server.py
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse, HTMLResponse
from pathlib import Path
import asyncio
import json

app = FastAPI(title="CORTEX Admin Dashboard", version="1.0")

# Static HTML dashboard
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    html_path = Path(__file__).parent / "templates" / "admin_dashboard.html"
    return html_path.read_text()

# Admin operations API
@app.post("/api/admin/align")
async def run_alignment(background_tasks: BackgroundTasks):
    """Execute system alignment in background."""
    operation_id = generate_operation_id()
    background_tasks.add_task(execute_alignment, operation_id)
    return {"operation_id": operation_id, "status": "started"}

@app.post("/api/admin/optimize")
async def run_optimization(background_tasks: BackgroundTasks):
    """Execute system optimization in background."""
    operation_id = generate_operation_id()
    background_tasks.add_task(execute_optimization, operation_id)
    return {"operation_id": operation_id, "status": "started"}

# Real-time progress via SSE
@app.get("/api/admin/progress/{operation_id}")
async def stream_progress(operation_id: str):
    """Server-Sent Events for real-time progress."""
    async def event_generator():
        while True:
            progress = get_operation_progress(operation_id)
            if progress:
                yield f"data: {json.dumps(progress)}\n\n"
            if progress and progress['status'] == 'complete':
                break
            await asyncio.sleep(0.5)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**2.2 Non-Interactive Orchestrator Wrappers**
```python
# src/dashboard/orchestrator_wrappers.py
from src.operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator
from src.operations.modules.admin.optimize_orchestrator import OptimizeOrchestrator
import logging

def execute_alignment(operation_id: str):
    """Non-interactive alignment execution."""
    try:
        update_progress(operation_id, "Starting alignment...", 0)
        
        orchestrator = SystemAlignmentOrchestrator(non_interactive=True)
        
        # Hook progress updates
        def progress_callback(step, total, message):
            percent = int((step / total) * 100)
            update_progress(operation_id, message, percent)
        
        result = orchestrator.execute({}, progress_callback=progress_callback)
        
        update_progress(operation_id, "Alignment complete", 100, status="complete", result=result)
    except Exception as e:
        logging.error(f"Alignment failed: {e}", exc_info=True)
        update_progress(operation_id, f"Error: {str(e)}", 0, status="error")

def execute_optimization(operation_id: str):
    """Non-interactive optimization execution."""
    try:
        update_progress(operation_id, "Starting optimization...", 0)
        
        orchestrator = OptimizeOrchestrator(non_interactive=True, skip_confirm=True)
        result = orchestrator.execute({})
        
        update_progress(operation_id, "Optimization complete", 100, status="complete", result=result)
    except Exception as e:
        logging.error(f"Optimization failed: {e}", exc_info=True)
        update_progress(operation_id, f"Error: {str(e)}", 0, status="error")
```

**2.3 Progress Tracking**
```python
# src/dashboard/progress_tracker.py
import sqlite3
from pathlib import Path
from datetime import datetime

class ProgressTracker:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS operation_progress (
                operation_id TEXT PRIMARY KEY,
                operation_type TEXT,
                status TEXT,
                message TEXT,
                percent INTEGER,
                started_at TEXT,
                updated_at TEXT,
                result_json TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def update(self, operation_id: str, message: str, percent: int, status: str = "running", result: dict = None):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO operation_progress 
            (operation_id, message, percent, status, updated_at, result_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (operation_id, message, percent, status, datetime.now().isoformat(), json.dumps(result) if result else None))
        conn.commit()
        conn.close()
    
    def get(self, operation_id: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT * FROM operation_progress WHERE operation_id = ?", (operation_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "operation_id": row[0],
                "operation_type": row[1],
                "status": row[2],
                "message": row[3],
                "percent": row[4],
                "started_at": row[5],
                "updated_at": row[6],
                "result": json.loads(row[7]) if row[7] else None
            }
        return None
```

**Deliverables:**
- ✅ FastAPI server running on port 7878
- ✅ 6 admin operation endpoints (align, optimize, cleanup, sync, healthcheck, deploy)
- ✅ SSE progress streaming
- ✅ SQLite-based progress tracking
- ✅ Auto-launch on first dashboard access

---

### Phase 3: Frontend Dashboard (3-4 hours)

**Goal:** Interactive HTML dashboard with real-time updates

**3.1 Dashboard HTML Template**
```html
<!-- src/dashboard/templates/admin_dashboard.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Admin Dashboard</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        /* Existing D3.js dashboard styles + admin controls */
        .admin-panel {
            background: #2c3e50;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .admin-button {
            background: #3498db;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
            transition: background 0.3s;
        }
        .admin-button:hover {
            background: #2980b9;
        }
        .admin-button:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #ecf0f1;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        .operation-log {
            background: #34495e;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            height: 200px;
            overflow-y: auto;
            margin: 10px 0;
        }
    </style>
</head>
<body x-data="adminDashboard()">
    <!-- Existing D3.js dashboard visualizations -->
    <div id="system-health-gauge"></div>
    <div id="layer-breakdown-chart"></div>
    
    <!-- Admin Control Panel -->
    <div class="admin-panel">
        <h2>🛠️ CORTEX Admin Operations</h2>
        
        <div class="admin-controls">
            <button class="admin-button" 
                    @click="runOperation('align')" 
                    :disabled="isRunning">
                🔧 Run Alignment
            </button>
            
            <button class="admin-button" 
                    @click="runOperation('optimize')" 
                    :disabled="isRunning">
                ⚡ Optimize System
            </button>
            
            <button class="admin-button" 
                    @click="runOperation('cleanup')" 
                    :disabled="isRunning">
                🧹 Cleanup Files
            </button>
            
            <button class="admin-button" 
                    @click="runOperation('sync')" 
                    :disabled="isRunning">
                🔄 Sync Repository
            </button>
            
            <button class="admin-button" 
                    @click="runOperation('healthcheck')" 
                    :disabled="isRunning">
                ❤️ System Health
            </button>
            
            <button class="admin-button" 
                    @click="runOperation('deploy')" 
                    :disabled="isRunning">
                🚀 Deploy CORTEX
            </button>
        </div>
        
        <!-- Real-time Progress -->
        <div x-show="isRunning" class="progress-section">
            <h3 x-text="'Running: ' + currentOperation"></h3>
            <div class="progress-bar">
                <div class="progress-fill" :style="'width: ' + progress + '%'">
                    <span x-text="progress + '%'"></span>
                </div>
            </div>
            <p x-text="progressMessage"></p>
        </div>
        
        <!-- Operation Log -->
        <div class="operation-log">
            <template x-for="entry in logEntries" :key="entry.id">
                <div>
                    <span x-text="entry.timestamp"></span> - 
                    <span x-text="entry.message"></span>
                </div>
            </template>
        </div>
    </div>
    
    <script>
        function adminDashboard() {
            return {
                isRunning: false,
                currentOperation: '',
                progress: 0,
                progressMessage: '',
                logEntries: [],
                eventSource: null,
                
                async runOperation(operation) {
                    this.isRunning = true;
                    this.currentOperation = operation;
                    this.progress = 0;
                    this.addLog(`Starting ${operation}...`);
                    
                    try {
                        // Start operation
                        const response = await fetch(`/api/admin/${operation}`, {
                            method: 'POST'
                        });
                        const data = await response.json();
                        
                        // Subscribe to progress updates
                        this.subscribeToProgress(data.operation_id);
                    } catch (error) {
                        this.addLog(`Error: ${error.message}`);
                        this.isRunning = false;
                    }
                },
                
                subscribeToProgress(operationId) {
                    this.eventSource = new EventSource(`/api/admin/progress/${operationId}`);
                    
                    this.eventSource.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        this.progress = data.percent;
                        this.progressMessage = data.message;
                        this.addLog(data.message);
                        
                        if (data.status === 'complete' || data.status === 'error') {
                            this.isRunning = false;
                            this.eventSource.close();
                            
                            if (data.status === 'complete') {
                                this.addLog(`✅ ${this.currentOperation} completed successfully`);
                                // Refresh dashboard data
                                this.refreshDashboard();
                            } else {
                                this.addLog(`❌ ${this.currentOperation} failed`);
                            }
                        }
                    };
                },
                
                addLog(message) {
                    const timestamp = new Date().toLocaleTimeString();
                    this.logEntries.push({ id: Date.now(), timestamp, message });
                    // Keep last 50 entries
                    if (this.logEntries.length > 50) {
                        this.logEntries.shift();
                    }
                },
                
                refreshDashboard() {
                    // Reload health metrics and update D3.js visualizations
                    fetch('/api/admin/health')
                        .then(response => response.json())
                        .then(data => {
                            updateHealthGauge(data.overall_health);
                            updateLayerBreakdown(data.layer_scores);
                        });
                }
            }
        }
    </script>
</body>
</html>
```

**Deliverables:**
- ✅ Interactive admin dashboard with 6 operation buttons
- ✅ Real-time progress bars with SSE
- ✅ Operation log with timestamp
- ✅ Auto-refresh after operation completion
- ✅ Disabled buttons during operation execution

---

### Phase 4: Auto-Launch & Integration (1-2 hours)

**Goal:** Seamless dashboard access from CORTEX CLI

**4.1 Dashboard Launch Script**
```python
# src/dashboard/launcher.py
import subprocess
import webbrowser
import time
import socket
from pathlib import Path

def is_server_running(port: int = 7878) -> bool:
    """Check if FastAPI server is already running."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def launch_dashboard():
    """Launch admin dashboard in browser."""
    port = 7878
    
    # Start server if not running
    if not is_server_running(port):
        server_script = Path(__file__).parent / "admin_dashboard_server.py"
        subprocess.Popen([
            "uvicorn",
            "src.dashboard.admin_dashboard_server:app",
            "--host", "localhost",
            "--port", str(port),
            "--reload"
        ], cwd=Path(__file__).parent.parent.parent)
        
        # Wait for server startup
        for _ in range(10):
            if is_server_running(port):
                break
            time.sleep(0.5)
    
    # Open dashboard in browser
    webbrowser.open(f"http://localhost:{port}")
    print(f"✅ Admin dashboard opened at http://localhost:{port}")
    print("   Press Ctrl+C to stop server")

if __name__ == "__main__":
    launch_dashboard()
```

**4.2 CLI Integration**
```python
# Add to src/main.py or CLI entry point
def handle_admin_dashboard():
    """Handle 'admin dashboard' or 'dashboard' command."""
    from src.dashboard.launcher import launch_dashboard
    launch_dashboard()

# Register trigger in intent router
ADMIN_DASHBOARD_TRIGGERS = [
    "admin dashboard",
    "dashboard",
    "show dashboard",
    "open dashboard",
    "admin panel"
]
```

**Deliverables:**
- ✅ `cortex dashboard` command launches browser
- ✅ Auto-starts FastAPI server if not running
- ✅ Server persists across multiple dashboard opens
- ✅ Graceful shutdown with Ctrl+C

---

## 🧪 Testing Strategy

### Test Suite Structure

```
tests/dashboard/
├── test_non_interactive_orchestrators.py    # Phase 1 tests
├── test_fastapi_backend.py                  # Phase 2 tests
├── test_frontend_integration.py             # Phase 3 tests
└── test_end_to_end_dashboard.py             # Full workflow tests
```

### Phase 1 Tests: Non-Interactive Mode

```python
# tests/dashboard/test_non_interactive_orchestrators.py
import pytest
from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
from src.orchestrators.planning_orchestrator import PlanningOrchestrator

def test_git_checkpoint_non_interactive_mode():
    """Test GitCheckpointOrchestrator bypasses input() in non-interactive mode."""
    orchestrator = GitCheckpointOrchestrator(non_interactive=True)
    
    # Simulate dirty state (normally requires user choice A/B/C/X)
    # Should auto-select default without blocking
    can_proceed, checkpoint_id = orchestrator.check_dirty_state_and_consent("test operation")
    
    assert can_proceed is True  # Auto-approved with default
    assert checkpoint_id is not None

def test_planning_auto_approve():
    """Test PlanningOrchestrator auto-approves checkpoints."""
    orchestrator = PlanningOrchestrator()
    
    success, path, msg = orchestrator.generate_incremental_plan(
        "User authentication feature",
        auto_approve=True  # No checkpoint prompts
    )
    
    assert success is True
    assert path.exists()

def test_cleanup_force_mode():
    """Test CleanupOrchestrator bypasses confirmation in force mode."""
    orchestrator = CleanupOrchestrator()
    
    result = orchestrator.execute({}, force=True)
    
    assert result.success is True
    # Should complete without waiting for user input
```

### Phase 2 Tests: FastAPI Backend

```python
# tests/dashboard/test_fastapi_backend.py
import pytest
from fastapi.testclient import TestClient
from src.dashboard.admin_dashboard_server import app

client = TestClient(app)

def test_dashboard_html_loads():
    """Test dashboard HTML endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "CORTEX Admin Dashboard" in response.text

def test_align_operation_starts():
    """Test alignment operation API."""
    response = client.post("/api/admin/align")
    assert response.status_code == 200
    data = response.json()
    assert "operation_id" in data
    assert data["status"] == "started"

def test_progress_streaming():
    """Test SSE progress endpoint."""
    # Start operation
    response = client.post("/api/admin/optimize")
    operation_id = response.json()["operation_id"]
    
    # Subscribe to progress
    with client.stream("GET", f"/api/admin/progress/{operation_id}") as stream:
        events = []
        for line in stream.iter_lines():
            if line.startswith(b"data:"):
                events.append(line)
                if len(events) >= 5:  # Collect first 5 events
                    break
        
        assert len(events) > 0
        # Verify JSON format
        import json
        data = json.loads(events[0].decode().replace("data: ", ""))
        assert "percent" in data
        assert "message" in data
```

### Phase 3 Tests: Frontend Integration

```python
# tests/dashboard/test_frontend_integration.py
from playwright.sync_api import sync_playwright

def test_dashboard_loads_in_browser():
    """Test dashboard renders correctly in browser."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:7878")
        
        # Verify dashboard elements present
        assert page.query_selector(".admin-panel") is not None
        assert page.query_selector("#system-health-gauge") is not None
        
        browser.close()

def test_align_button_triggers_operation():
    """Test clicking align button starts operation."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:7878")
        
        # Click align button
        page.click("button:has-text('Run Alignment')")
        
        # Wait for progress bar to appear
        page.wait_for_selector(".progress-bar", timeout=5000)
        
        # Verify progress updates
        progress_text = page.text_content(".progress-fill")
        assert "%" in progress_text
        
        browser.close()
```

### End-to-End Tests

```python
# tests/dashboard/test_end_to_end_dashboard.py
def test_complete_align_workflow():
    """Test complete alignment workflow from dashboard."""
    # 1. Launch dashboard
    from src.dashboard.launcher import launch_dashboard
    launch_dashboard()
    
    # 2. Trigger alignment via API
    import requests
    response = requests.post("http://localhost:7878/api/admin/align")
    operation_id = response.json()["operation_id"]
    
    # 3. Monitor progress
    import sseclient
    messages = sseclient.SSEClient(f"http://localhost:7878/api/admin/progress/{operation_id}")
    
    progress_updates = []
    for msg in messages:
        data = json.loads(msg.data)
        progress_updates.append(data)
        if data["status"] == "complete":
            break
    
    # 4. Verify completion
    assert len(progress_updates) > 0
    assert progress_updates[-1]["status"] == "complete"
    assert progress_updates[-1]["percent"] == 100
```

---

## 📊 Success Metrics

**Functional Requirements:**
- ✅ All 6 admin operations executable from dashboard
- ✅ Zero user approval interruptions during execution
- ✅ Real-time progress updates (< 500ms latency)
- ✅ Operation completion within expected timeframes (align: 30s, optimize: 15s, cleanup: 10s)

**Performance Requirements:**
- ✅ Dashboard loads in < 2 seconds
- ✅ Operation start latency < 500ms
- ✅ SSE event delivery < 100ms
- ✅ Browser memory usage < 100MB

**UX Requirements:**
- ✅ Single-click operation execution (no multi-step approval)
- ✅ Visual progress indication (progress bar + percentage)
- ✅ Clear operation status (running/complete/error)
- ✅ Operation log for debugging

**Reliability Requirements:**
- ✅ Server auto-restart on crash
- ✅ Operation recovery on failure (can re-run)
- ✅ No data loss on browser refresh
- ✅ Graceful degradation if server unavailable

---

## 🚀 Deployment Strategy

### Local Development

```bash
# Install dependencies
pip install fastapi uvicorn[standard] sse-starlette

# Start dashboard server
uvicorn src.dashboard.admin_dashboard_server:app --reload --port 7878

# Or use launcher
python -m src.dashboard.launcher
```

### Production Deployment

**Option 1: Standalone Executable (Recommended)**
```bash
# Bundle as standalone app using PyInstaller
pyinstaller --onefile --windowed \
    --add-data "src/dashboard/templates:templates" \
    --name "CORTEX-Dashboard" \
    src/dashboard/launcher.py

# Result: CORTEX-Dashboard.exe (Windows) or CORTEX-Dashboard.app (macOS)
```

**Option 2: System Service**
```bash
# Create systemd service (Linux) or LaunchAgent (macOS)
# Auto-start dashboard on login

# macOS LaunchAgent example
cat > ~/Library/LaunchAgents/com.cortex.dashboard.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cortex.dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/CORTEX/src/dashboard/admin_dashboard_server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.cortex.dashboard.plist
```

---

## 🔒 Security Considerations

**Authentication (Optional - Future Enhancement)**
```python
# Add basic auth for remote access
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    # Load credentials from cortex.config.json
    config_user = os.getenv("CORTEX_ADMIN_USER", "admin")
    config_pass = os.getenv("CORTEX_ADMIN_PASS", "changeme")
    
    if credentials.username != config_user or credentials.password != config_pass:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return credentials.username

# Protect admin endpoints
@app.post("/api/admin/align", dependencies=[Depends(authenticate)])
async def run_alignment(...):
    ...
```

**CSRF Protection**
```python
# Add CSRF token validation
from starlette.middleware.csrf import CSRFMiddleware

app.add_middleware(CSRFMiddleware, secret_key="your-secret-key")
```

**HTTPS (Production)**
```python
# Run with SSL certificate
uvicorn src.dashboard.admin_dashboard_server:app \
    --host 0.0.0.0 \
    --port 7878 \
    --ssl-keyfile /path/to/key.pem \
    --ssl-certfile /path/to/cert.pem
```

---

## 📅 Timeline Estimate

| Phase | Duration | Dependencies | Risk Level |
|-------|----------|--------------|------------|
| Phase 1: Non-Interactive Refactoring | 2-3 hours | None | LOW (well-defined) |
| Phase 2: FastAPI Backend | 3-4 hours | Phase 1 complete | MEDIUM (new tech) |
| Phase 3: Frontend Dashboard | 3-4 hours | Phase 2 complete | LOW (HTML/JS) |
| Phase 4: Auto-Launch Integration | 1-2 hours | Phase 2-3 complete | LOW (simple script) |
| Testing & Validation | 2-3 hours | All phases complete | MEDIUM (E2E tests) |
| Documentation | 1 hour | All phases complete | LOW (markdown) |

**Total Estimate:** 12-17 hours (1.5-2 work days)

**Critical Path:** Phase 1 must complete first (blocks all other phases)

---

## 🎯 Next Actions

### Immediate (Today)

1. **Start Phase 1:** Refactor GitCheckpointOrchestrator for non-interactive mode
2. **Create test harness:** Validate non-interactive behavior works correctly
3. **Document changes:** Update orchestrator docstrings with non-interactive usage

### Short-Term (This Week)

4. **Complete Phase 1:** Refactor all 5 orchestrators
5. **Begin Phase 2:** Setup FastAPI server skeleton
6. **Prototype UI:** Create basic HTML dashboard with one operation

### Medium-Term (Next Week)

7. **Complete Phase 2-3:** Full backend + frontend implementation
8. **Integration testing:** End-to-end workflow validation
9. **User acceptance:** Demo dashboard to stakeholders

---

## 📝 Pending Issues & Risks

### High Priority Issues

**Issue #1: System Alignment 0% Health**
- **Status:** Blocking dashboard accuracy
- **Action:** Fix path resolution in Phase 1
- **Timeline:** Resolve before Phase 3 (dashboard needs real health data)

**Issue #2: VS Code Approval Prompts**
- **Status:** Root cause of UX friction
- **Action:** Non-interactive mode solves this
- **Timeline:** Phase 1 completion

### Medium Priority Issues

**Issue #3: Progress Monitoring Consistency**
- **Status:** Some orchestrators lack progress callbacks
- **Action:** Add `progress_callback` parameter to all orchestrators
- **Timeline:** Phase 2 (backend needs consistent progress API)

**Issue #4: Error Recovery**
- **Status:** No clear retry mechanism for failed operations
- **Action:** Add retry button in dashboard UI
- **Timeline:** Phase 3 enhancement

### Low Priority Issues

**Issue #5: Multi-User Access**
- **Status:** Dashboard assumes single-user (localhost only)
- **Action:** Add authentication if remote access needed
- **Timeline:** Future enhancement (not MVP)

---

## 🔗 Related Documentation

- **System Alignment Guide:** `.github/prompts/modules/system-alignment-guide.md`
- **Git Checkpoint Guide:** `cortex-brain/documents/implementation-guides/git-checkpoint-guide.md`
- **Progress Monitoring Guide:** `cortex-brain/documents/implementation-guides/progress-monitoring-quick-start.md`
- **Response Templates:** `cortex-brain/response-templates.yaml`

---

## ✅ Definition of Done

**Feature is complete when:**
- ✅ All 6 admin operations executable from dashboard without approval interruptions
- ✅ Real-time progress updates via SSE with < 500ms latency
- ✅ Dashboard auto-launches from CLI command (`cortex dashboard`)
- ✅ All Phase 1-4 deliverables completed
- ✅ Test suite passes with 85%+ coverage
- ✅ Documentation updated (user guide + API reference)
- ✅ Demo video created showing workflow
- ✅ Stakeholder approval obtained

---

**Plan Version:** 1.0  
**Last Updated:** 2025-11-28  
**Author:** Asif Hussain  
**Status:** ✅ READY FOR IMPLEMENTATION
