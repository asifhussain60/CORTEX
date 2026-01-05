# C15-P7: Planning Orchestrator Governance Violations Remediation

**Plan Type:** Remediation Sub-Plan  
**Parent:** C150 Planning System Governance & Standardization  
**Created:** 2025-01-03  
**Updated:** 2026-01-05 (MAJOR REDESIGN)  
**Priority:** HIGH  
**Estimated Effort:** 16 hours (doubled due to architectural enhancement)

---

## 🎯 Objective

Fix Planning Orchestrator v5 governance violations AND implement YAML-based execution architecture:

### ✅ Phase 1 Complete:
1. **Folder naming with A## prefix** - Implemented and tested

### 🔄 Phase 2 Enhanced Requirements:
2. **YAML-based plan execution** - All sub-plans, phases, tasks defined in YAML (not MD)
3. **Live HTML plan viewer** - Served on localhost:port via Python server
4. **Port management** - Check/reuse/kill server, maintain same port across plans
5. **Real-time updates** - HTML viewer updates as YAML execution progresses
6. **MD files for reporting only** - User-facing summaries, not execution

### 🔜 Phase 3 Unchanged:
7. **Epic vs feature distinction** - Different folder structures and trackers

---

## 🏗️ Architectural Changes

### Current Architecture (MD-based):
```
Planning Request
    ↓
Generate MD plan file
    ↓
Create folder structure
    ↓
Validate files
    ↓
Return to user (chat)
```

### New Architecture (YAML-based):
```
Planning Request
    ↓
Generate master-plan.yaml (execution definition)
    ↓
Generate master-plan.md (user documentation)
    ↓
Create folder structure
    ↓
Start plan-server.py (localhost:8150) ← NEW
    ↓
Generate plan-viewer.html ← NEW
    ↓
Execute phases from YAML ← NEW
    ↓
Update HTML in real-time ← NEW
    ↓
Return completion summary (chat)
```

---

## 📋 Enhanced Remediation Plan

### ✅ Phase 1: Folder Naming Convention (2 hours) - COMPLETE

**Status:** ✅ Implemented and tested

**Changes:**
- Added `_abbreviate_feature_name()` helper method
- Updated `_create_folder_structure()` to use A## prefix
- Modified `_validate_plan()` to check folder naming
- Fixed `_generate_master_plan_filename()` database query

**Test Results:**
```
enterprise-python-audit-logger    → A01-ent-py-aud-log.md
glassmorphism-css-standardization → A02-glassm-css-std.md
oauth2-authentication-system      → A03-oauth2-auth-sys.md
```

---

### 🔄 Phase 2: YAML-Based Planning + Live HTML Viewer (8 hours) - IN PROGRESS

**File:** `src/orchestrators/planning/planning_orchestrator_v5.py`  
**New Files:** `src/servers/plan_server.py`, `templates/plan-viewer-template.html`

#### 2.1 YAML Plan Schema (1 hour)

Create structured YAML format for plan execution:

**File:** `cortex-brain/manifests/schemas/plan-schema.yaml`

```yaml
# Plan Execution Schema v1.0
plan:
  id: "A01"  # 3-char ID
  type: "feature"  # feature | epic | phase
  name: "enterprise-audit-logger"
  title: "Enterprise Python Audit Logger"
  description: "Full-featured audit logging system"
  
  metadata:
    created: "2026-01-05T10:00:00Z"
    author: "CORTEX Planning v5"
    complexity_tier: 3
    estimated_hours: 66
    
  phases:
    - id: "phase-1"
      number: 1
      name: "Core Logger Implementation"
      status: "not-started"
      estimated_hours: 12
      
      tasks:
        - id: "task-1-1"
          name: "Create AuditLogger class"
          status: "not-started"
          estimated_minutes: 60
          dependencies: []
          
          implementation:
            type: "code"
            files:
              - path: "src/audit/logger.py"
                template: "audit-logger-template.py"
                
          validation:
            type: "test"
            files:
              - "tests/audit/test_logger.py"
            coverage_threshold: 90
            
        - id: "task-1-2"
          name: "Add LogBuffer for async writes"
          status: "not-started"
          estimated_minutes: 45
          dependencies: ["task-1-1"]
          
    - id: "phase-2"
      number: 2
      name: "Self-Healing Integration"
      status: "not-started"
      estimated_hours: 18
      
  acceptance_criteria:
    - "All tests pass with >90% coverage"
    - "Production toggle works (on/off)"
    - "Self-healing detects and fixes log issues"
    - "Log rotation prevents bloat"
```

#### 2.2 Plan Server Implementation (3 hours)

**File:** `src/servers/plan_server.py`

```python
"""
CORTEX Plan Server - Live HTML Plan Viewer
Serves plan-viewer.html on localhost:8150 with real-time updates
"""

import http.server
import socketserver
import json
import threading
import time
from pathlib import Path
from typing import Optional
import psutil
import signal
import sys

PLAN_SERVER_PORT = 8150

class PlanRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for plan viewer with CORS and live updates."""
    
    plan_folder: Optional[Path] = None
    
    def do_GET(self):
        """Handle GET requests with CORS headers."""
        # Add CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'text/html' if self.path.endswith('.html') else 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        if self.path == '/api/progress':
            # Serve live progress from YAML
            self.serve_progress()
        elif self.path == '/api/plan':
            # Serve plan definition
            self.serve_plan()
        else:
            # Serve static files
            super().do_GET()
    
    def serve_progress(self):
        """Serve current progress from progress-tracker.json."""
        if not self.plan_folder:
            self.wfile.write(json.dumps({"error": "No plan loaded"}).encode())
            return
            
        tracker_path = self.plan_folder / "tracking" / "progress-tracker.json"
        if tracker_path.exists():
            self.wfile.write(tracker_path.read_bytes())
        else:
            self.wfile.write(json.dumps({"progress": 0}).encode())
    
    def serve_plan(self):
        """Serve plan definition from master-plan.yaml."""
        if not self.plan_folder:
            self.wfile.write(json.dumps({"error": "No plan loaded"}).encode())
            return
            
        # Find master plan YAML
        yaml_files = list(self.plan_folder.glob("[A-Z0-9][A-Z0-9][A-Z0-9]-*.yaml"))
        if yaml_files:
            import yaml
            plan_data = yaml.safe_load(yaml_files[0].read_text())
            self.wfile.write(json.dumps(plan_data).encode())
        else:
            self.wfile.write(json.dumps({"error": "No plan YAML found"}).encode())

class PlanServer:
    """Manages plan viewer server lifecycle."""
    
    def __init__(self, plan_folder: Path, port: int = PLAN_SERVER_PORT):
        self.plan_folder = plan_folder
        self.port = port
        self.server: Optional[socketserver.TCPServer] = None
        self.thread: Optional[threading.Thread] = None
    
    @staticmethod
    def check_port_in_use(port: int) -> bool:
        """Check if port is already in use."""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False
    
    @staticmethod
    def kill_server_on_port(port: int) -> bool:
        """Kill any process using the port."""
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port and conn.status == 'LISTEN':
                        proc.send_signal(signal.SIGTERM)
                        time.sleep(0.5)
                        if proc.is_running():
                            proc.kill()
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def start(self) -> str:
        """Start plan server, reusing or killing existing server."""
        # Check if server already running
        if self.check_port_in_use(self.port):
            print(f"⚠️  Port {self.port} in use - killing existing server...")
            if self.kill_server_on_port(self.port):
                print(f"✅ Killed existing server on port {self.port}")
                time.sleep(1)  # Wait for port to be released
            else:
                print(f"❌ Failed to kill server on port {self.port}")
                return f"http://localhost:{self.port}"  # Return URL anyway (may still work)
        
        # Change to plan folder for serving static files
        import os
        os.chdir(self.plan_folder)
        
        # Create server
        PlanRequestHandler.plan_folder = self.plan_folder
        self.server = socketserver.TCPServer(("", self.port), PlanRequestHandler)
        
        # Start in background thread
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        
        url = f"http://localhost:{self.port}/plan-viewer.html"
        print(f"🌐 Plan viewer started: {url}")
        
        return url
    
    def stop(self):
        """Stop the server."""
        if self.server:
            self.server.shutdown()
            self.server = None
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None

# Singleton instance
_plan_server_instance: Optional[PlanServer] = None

def get_plan_server(plan_folder: Path) -> PlanServer:
    """Get or create plan server singleton."""
    global _plan_server_instance
    
    if _plan_server_instance is None:
        _plan_server_instance = PlanServer(plan_folder)
    else:
        # Update plan folder for existing server
        _plan_server_instance.plan_folder = plan_folder
        PlanRequestHandler.plan_folder = plan_folder
    
    return _plan_server_instance
```

#### 2.3 YAML Plan Generator (2 hours)

**Add to:** `src/orchestrators/planning/planning_orchestrator_v5.py`

```python
def _generate_plan_yaml(
    self,
    feature_name: str,
    **kwargs
) -> str:
    """
    Generate master-plan.yaml for execution.
    
    Args:
        feature_name: Feature being planned
        **kwargs: Additional parameters
    
    Returns:
        Path to generated YAML file
    """
    import yaml
    from datetime import datetime
    
    # Generate master plan filename
    master_plan_filename = self._generate_master_plan_filename(feature_name)
    folder_id_prefix = master_plan_filename.split('-')[0].upper()
    
    # Create plan structure
    plan_data = {
        'plan': {
            'id': folder_id_prefix,
            'type': getattr(self, 'plan_type', 'feature'),
            'name': feature_name,
            'title': feature_name.replace('-', ' ').title(),
            'description': f"Implementation plan for {feature_name}",
            
            'metadata': {
                'created': datetime.now().isoformat(),
                'author': 'CORTEX Planning Orchestrator v5',
                'complexity_tier': 3,
                'estimated_hours': 40,
                'plan_id': self.plan_id
            },
            
            'phases': [
                {
                    'id': 'phase-1',
                    'number': 1,
                    'name': 'Core Implementation',
                    'status': 'not-started',
                    'estimated_hours': 12,
                    'tasks': [
                        {
                            'id': 'task-1-1',
                            'name': 'Setup project structure',
                            'status': 'not-started',
                            'estimated_minutes': 30,
                            'dependencies': []
                        }
                    ]
                },
                {
                    'id': 'phase-2',
                    'number': 2,
                    'name': 'Testing',
                    'status': 'not-started',
                    'estimated_hours': 8,
                    'tasks': []
                },
                {
                    'id': 'phase-3',
                    'number': 3,
                    'name': 'Documentation',
                    'status': 'not-started',
                    'estimated_hours': 4,
                    'tasks': []
                }
            ],
            
            'acceptance_criteria': [
                'All phases complete',
                'All tests passing',
                'Documentation updated'
            ]
        }
    }
    
    # Get plan folder with correct naming
    abbreviated_name = self._abbreviate_feature_name(feature_name, max_length=22)
    folder_name = f"{folder_id_prefix.lower()}-{abbreviated_name}"
    plan_dir = Path(f"cortex-brain/documents/planning/active/{folder_name}")
    
    # Write YAML file
    yaml_filename = master_plan_filename.replace('.md', '.yaml')
    yaml_path = plan_dir / yaml_filename
    
    with open(yaml_path, 'w') as f:
        yaml.dump(plan_data, f, default_flow_style=False, sort_keys=False)
    
    self.logger.info(f"✅ Generated plan YAML: {yaml_path}")
    
    # Register as artifact
    self.create_artifact(
        path=str(yaml_path),
        content=yaml_path.read_text(),
        artifact_type="plan"
    )
    
    return str(yaml_path)
```

#### 2.4 Interactive HTML Viewer (2 hours)

**Update:** `_create_folder_structure()` to generate `plan-viewer.html`

```python
def _generate_plan_viewer_html(self, feature_name: str) -> str:
    """Generate interactive HTML plan viewer with live updates."""
    
    master_plan_filename = self._generate_master_plan_filename(feature_name)
    plan_id = master_plan_filename.split('-')[0]
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{plan_id} - {feature_name.replace('-', ' ').title()} - CORTEX Plan Viewer</title>
    <style>
        /* CORTEX 5.0 Glassmorphism Styles */
        :root {{
            --glass-bg: rgba(15, 23, 42, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
            --progress-gradient: linear-gradient(90deg, #00d4ff 0%, #a855f7 100%);
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent-blue: #00d4ff;
            --accent-purple: #a855f7;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: var(--text-primary);
            padding: 2rem;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .glass-panel {{
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        
        .plan-id {{
            display: inline-block;
            background: var(--progress-gradient);
            color: #000;
            font-weight: 700;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        .plan-title {{
            font-size: clamp(2rem, 4vw, 3rem);
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .live-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: #10b981;
            font-size: 0.875rem;
            margin-top: 1rem;
        }}
        
        .live-dot {{
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .overall-progress {{
            margin: 2rem 0;
        }}
        
        .progress-bar {{
            height: 24px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}
        
        .progress-fill {{
            height: 100%;
            background: var(--progress-gradient);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 1rem;
            color: #000;
            font-weight: 600;
            font-size: 0.875rem;
        }}
        
        .phase-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        .phase-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        
        .phase-title {{
            font-size: 1.5rem;
            font-weight: 600;
        }}
        
        .phase-status {{
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 600;
        }}
        
        .status-not-started {{ background: rgba(148, 163, 184, 0.2); color: #94a3b8; }}
        .status-in-progress {{ background: rgba(0, 212, 255, 0.2); color: #00d4ff; }}
        .status-completed {{ background: rgba(16, 185, 129, 0.2); color: #10b981; }}
        
        .task-list {{
            list-style: none;
            margin-top: 1rem;
        }}
        
        .task-item {{
            padding: 0.75rem;
            border-left: 3px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .task-item.completed {{
            border-left-color: #10b981;
            opacity: 0.7;
        }}
        
        .task-item.in-progress {{
            border-left-color: #00d4ff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header glass-panel">
            <div class="plan-id" id="planId">{plan_id}</div>
            <h1 class="plan-title" id="planTitle">{feature_name.replace('-', ' ').title()}</h1>
            <div class="live-indicator">
                <div class="live-dot"></div>
                <span>Live Updates</span>
            </div>
        </div>
        
        <div class="glass-panel overall-progress">
            <h2>Overall Progress</h2>
            <div class="progress-bar">
                <div class="progress-fill" id="overallProgress" style="width: 0%">0%</div>
            </div>
        </div>
        
        <div id="phasesContainer">
            <!-- Phases loaded dynamically -->
        </div>
    </div>
    
    <script>
        // Fetch plan data from server
        async function fetchPlan() {{
            try {{
                const response = await fetch('/api/plan');
                const data = await response.json();
                return data.plan;
            }} catch (error) {{
                console.error('Failed to fetch plan:', error);
                return null;
            }}
        }}
        
        // Fetch progress data
        async function fetchProgress() {{
            try {{
                const response = await fetch('/api/progress');
                const data = await response.json();
                return data;
            }} catch (error) {{
                console.error('Failed to fetch progress:', error);
                return null;
            }}
        }}
        
        // Render phases
        function renderPhases(plan, progress) {{
            const container = document.getElementById('phasesContainer');
            container.innerHTML = '';
            
            plan.phases.forEach(phase => {{
                const statusClass = `status-${{phase.status.replace('_', '-')}}`;
                
                const phaseHtml = `
                    <div class="glass-panel phase-card">
                        <div class="phase-header">
                            <h3 class="phase-title">Phase ${{phase.number}}: ${{phase.name}}</h3>
                            <span class="phase-status ${{statusClass}}">${{phase.status.replace('_', ' ').toUpperCase()}}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%">0%</div>
                        </div>
                        <ul class="task-list">
                            ${{phase.tasks.map(task => `
                                <li class="task-item ${{task.status.replace('_', '-')}}">
                                    <span>${{task.name}}</span>
                                    <span class="phase-status ${{`status-${{task.status.replace('_', '-')}}`}}">${{task.status.replace('_', ' ')}}</span>
                                </li>
                            `).join('')}}
                        </ul>
                    </div>
                `;
                
                container.innerHTML += phaseHtml;
            }});
        }}
        
        // Update progress
        function updateProgress(progress) {{
            if (!progress || !progress.progress) return;
            
            const overallPercent = progress.progress.overall_percent || 0;
            const overallEl = document.getElementById('overallProgress');
            overallEl.style.width = overallPercent + '%';
            overallEl.textContent = Math.round(overallPercent) + '%';
        }}
        
        // Initialize
        async function init() {{
            const plan = await fetchPlan();
            if (plan) {{
                document.getElementById('planId').textContent = plan.id;
                document.getElementById('planTitle').textContent = plan.title;
                renderPhases(plan, {{}});
            }}
            
            // Poll for updates every 2 seconds
            setInterval(async () => {{
                const progress = await fetchProgress();
                updateProgress(progress);
            }}, 2000);
        }}
        
        init();
    </script>
</body>
</html>
"""
    
    return html_content
```

---

### Phase 3: Epic vs Feature Distinction (3 hours)

*(Unchanged from original plan)*

---

## ✅ Acceptance Criteria (Updated)

### Phase 2 - YAML + HTML Viewer:
- [ ] master-plan.yaml generated with structured phases/tasks
- [ ] master-plan.md generated for user documentation
- [ ] plan-server.py starts on port 8150
- [ ] Port management works (check/reuse/kill existing servers)
- [ ] plan-viewer.html displays live plan progress
- [ ] HTML updates every 2 seconds from progress-tracker.json
- [ ] Server runs in background (daemon thread)
- [ ] All plans use same port 8150

### Phase 1 - Folder Naming:
- [x] Folder names follow `[a-z0-9]{3}-{abbreviated-name}/` pattern
- [x] Folder ID matches master plan ID
- [x] Validation checks folder naming

---

## 🧪 Testing Strategy (Updated)

### Unit Tests:

```python
def test_yaml_plan_generation():
    """Test YAML plan structure."""
    orchestrator = PlanningOrchestratorV5(request="Create test plan")
    yaml_path = orchestrator._generate_plan_yaml("test-feature")
    
    import yaml
    with open(yaml_path) as f:
        plan_data = yaml.safe_load(f)
    
    assert plan_data['plan']['id'] == 'A01'
    assert 'phases' in plan_data['plan']
    assert len(plan_data['plan']['phases']) > 0

def test_plan_server_port_management():
    """Test port check/reuse/kill logic."""
    from src.servers.plan_server import PlanServer
    import time
    
    server1 = PlanServer(Path("/tmp/test-plan"))
    url1 = server1.start()
    assert PlanServer.check_port_in_use(8150)
    
    # Try starting second server (should kill first)
    server2 = PlanServer(Path("/tmp/test-plan2"))
    url2 = server2.start()
    assert PlanServer.check_port_in_use(8150)
    
    server2.stop()
    time.sleep(1)
    assert not PlanServer.check_port_in_use(8150)

def test_html_viewer_generation():
    """Test HTML viewer contains required elements."""
    orchestrator = PlanningOrchestratorV5(request="Create test plan")
    html = orchestrator._generate_plan_viewer_html("test-feature")
    
    assert '<title>' in html
    assert 'fetchProgress' in html
    assert 'phasesContainer' in html
    assert '/api/progress' in html
```

---

## 📅 Implementation Timeline (Updated)

| Phase | Effort | Dependencies | Deliverables |
|-------|--------|--------------|--------------|
| **Phase 1: Folder Naming** | 2h | None | ✅ COMPLETE |
| **Phase 2.1: YAML Schema** | 1h | Phase 1 | plan-schema.yaml |
| **Phase 2.2: Plan Server** | 3h | 2.1 | plan_server.py, port management |
| **Phase 2.3: YAML Generator** | 2h | 2.1, 2.2 | _generate_plan_yaml() |
| **Phase 2.4: HTML Viewer** | 2h | 2.2, 2.3 | _generate_plan_viewer_html() |
| **Phase 3: Epic/Feature** | 3h | Phase 2 | plan_type logic |

**Total Effort:** 16 hours  
**Completion Target:** 2026-01-07 EOD

---

## 🚀 Next Steps

1. ✅ Phase 1 complete - folder naming works
2. ▶️  Create `plan-schema.yaml` (30 min)
3. ▶️  Implement `plan_server.py` with port management (3 hours)
4. ▶️  Add `_generate_plan_yaml()` to orchestrator (2 hours)
5. ▶️  Add `_generate_plan_viewer_html()` to orchestrator (2 hours)
6. ▶️  Test end-to-end: create plan → YAML → server → HTML (1 hour)

---

*Remediation sub-plan updated with YAML-based execution architecture.*
    result = '-'.join(abbreviated)
    
    if len(result) <= max_length:
        return result
    
    # Further abbreviation if needed...
    return result[:max_length]
```

3. **Update validation logic in `_validate_plan()`** (lines ~1014-1070):

```python
# CHANGE: Validate folder name matches master plan ID
master_plan_filename = self._generate_master_plan_filename()
expected_folder_prefix = master_plan_filename.split('-')[0].lower()  # "a01"

folder_name = self.plan_folder.name
if not folder_name.startswith(expected_folder_prefix):
    self.logger.warning(
        f"Folder name '{folder_name}' doesn't match master plan prefix '{expected_folder_prefix}'"
    )
    # Add to validation warnings
```

---

### Phase 2: Plan Viewer HTML Generation (3 hours)

**File:** `src/orchestrators/planning/planning_orchestrator_v5.py`

#### Changes Required:

1. **Add `_generate_plan_viewer_html()` method** (after `_generate_master_plan()`):

```python
def _generate_plan_viewer_html(self) -> str:
    """Generate interactive HTML plan viewer with visual progress tracking.
    
    Template Reference: c150-remediation-plan/plan-viewer.html
    """
    
    # Read master plan for content extraction
    master_plan_path = self.plan_folder / self._generate_master_plan_filename()
    master_plan_content = master_plan_path.read_text()
    
    # Parse plan phases and tasks
    phases = self._parse_plan_phases(master_plan_content)
    
    # Load HTML template
    template_path = (
        self.cortex_root / 
        "cortex-brain/documents/planning/active/c150-remediation-plan/plan-viewer.html"
    )
    template_content = template_path.read_text()
    
    # Inject plan-specific data
    html_content = template_content.replace(
        "{{PLAN_TITLE}}", self.feature_name.replace('-', ' ').title()
    ).replace(
        "{{PLAN_ID}}", self._generate_master_plan_filename().split('-')[0]
    ).replace(
        "{{PHASES}}", self._render_phases_html(phases)
    ).replace(
        "{{TOTAL_HOURS}}", str(sum(p.get('hours', 0) for p in phases))
    )
    
    return html_content

def _parse_plan_phases(self, plan_content: str) -> List[Dict[str, Any]]:
    """Extract phases from master plan markdown."""
    phases = []
    current_phase = None
    
    for line in plan_content.split('\n'):
        if line.startswith('### Phase'):
            if current_phase:
                phases.append(current_phase)
            current_phase = {
                'name': line.strip('# ').strip(),
                'tasks': [],
                'hours': 0
            }
        elif current_phase and line.strip().startswith('-'):
            task = line.strip('- ').strip()
            current_phase['tasks'].append(task)
        elif 'hours' in line.lower() and current_phase:
            # Extract hour estimate
            import re
            hours_match = re.search(r'(\d+)\s*hours?', line, re.IGNORECASE)
            if hours_match:
                current_phase['hours'] = int(hours_match.group(1))
    
    if current_phase:
        phases.append(current_phase)
    
    return phases

def _render_phases_html(self, phases: List[Dict[str, Any]]) -> str:
    """Render phases as HTML for plan viewer."""
    html_parts = []
    
    for idx, phase in enumerate(phases, 1):
        tasks_html = '\n'.join([
            f"<li>{task}</li>" 
            for task in phase['tasks']
        ])
        
        html_parts.append(f"""
        <div class="phase-card" id="phase-{idx}">
            <h3>Phase {idx}: {phase['name']}</h3>
            <div class="phase-meta">
                <span>⏱️ {phase['hours']} hours</span>
                <span>📋 {len(phase['tasks'])} tasks</span>
            </div>
            <ul class="task-list">
                {tasks_html}
            </ul>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%"></div>
            </div>
        </div>
        """)
    
    return '\n'.join(html_parts)
```

2. **Invoke in Phase 3 execution** (in `execute()` method):

```python
# Phase 3: Documentation Setup
if self.current_phase == 3:
    self.logger.info("Phase 3: Creating documentation and plan viewer...")
    
    # EXISTING: Create README.md
    self._create_readme()
    
    # NEW: Generate interactive plan viewer HTML
    plan_viewer_html = self._generate_plan_viewer_html()
    plan_viewer_path = self.plan_folder / "plan-viewer.html"
    plan_viewer_path.write_text(plan_viewer_html)
    self.logger.info(f"✅ Generated plan viewer: {plan_viewer_path}")
    
    # Register artifact in database
    self.db.add_artifact(
        plan_id=self.current_plan_id,
        name="plan-viewer.html",
        type="documentation",
        path=str(plan_viewer_path),
        status="generated"
    )
```

---

### Phase 3: Epic vs Feature Plan Distinction (3 hours)

**File:** `src/orchestrators/planning/planning_orchestrator_v5.py`

#### Changes Required:

1. **Add `plan_type` parameter to `__init__()`** (lines ~77-106):

```python
def __init__(
    self,
    request: str,
    feature_name: Optional[str] = None,
    plan_type: str = "feature",  # NEW: "feature" | "epic" | "phase"
    context: Optional[Dict[str, Any]] = None
):
    super().__init__(request, context)
    self.feature_name = feature_name or self._extract_feature_name()
    self.plan_type = plan_type  # NEW: Store plan type
    
    # Validate plan type
    if plan_type not in ["feature", "epic", "phase"]:
        raise ValueError(f"Invalid plan_type: {plan_type}. Must be 'feature', 'epic', or 'phase'")
```

2. **Update folder structure based on plan type** (in `_create_folder_structure()`):

```python
def _create_folder_structure(self, base_path: Path) -> None:
    """Create folder structure based on plan type."""
    
    # Standard folders for all plan types
    standard_folders = [
        "analysis",
        "artifacts", 
        "context",
        "reports",
        "tracking"
    ]
    
    # Epic-specific folders
    if self.plan_type == "epic":
        standard_folders.extend([
            "features",      # Nested feature plans
            "integration"    # Cross-feature integration tests
        ])
    
    # Create all folders
    for folder in standard_folders:
        folder_path = base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
```

3. **Use different progress tracker templates** (in `_initialize_progress_tracker()`):

```python
def _initialize_progress_tracker(self) -> None:
    """Initialize progress tracker based on plan type."""
    
    tracker_filename = (
        "epic-progress-tracker.json" if self.plan_type == "epic"
        else "progress-tracker.json"
    )
    
    tracker_path = self.plan_folder / "tracking" / tracker_filename
    
    if self.plan_type == "epic":
        # Epic tracker includes nested features
        tracker_data = {
            "plan_id": self.current_plan_id,
            "plan_type": "epic",
            "epic_name": self.feature_name,
            "features": [],  # List of child feature plan IDs
            "overall_progress": 0.0,
            "phases": self._get_epic_phases(),
            "created_at": datetime.now().isoformat()
        }
    else:
        # Standard feature tracker
        tracker_data = {
            "plan_id": self.current_plan_id,
            "plan_type": "feature",
            "feature_name": self.feature_name,
            "progress": 0.0,
            "phases": self._get_feature_phases(),
            "created_at": datetime.now().isoformat()
        }
    
    tracker_path.write_text(json.dumps(tracker_data, indent=2))
```

4. **Use different plan templates** (in `_generate_master_plan()`):

```python
def _generate_master_plan(self) -> str:
    """Generate master plan using type-specific template."""
    
    # Select template based on plan type
    template_name = {
        "feature": "feature-plan-template.md",
        "epic": "epic-plan-template.md",
        "phase": "phase-plan-template.md"
    }[self.plan_type]
    
    template_path = (
        self.cortex_root / 
        "cortex-brain/manifests/orchestrators/planning/" /
        template_name
    )
    
    # Load and render template with plan-specific data
    template = template_path.read_text()
    
    # Epic plans include feature breakdown section
    if self.plan_type == "epic":
        template += "\n\n## 🎯 Feature Breakdown\n\n"
        template += self._generate_feature_breakdown()
    
    # Render template with plan data...
```

---

## ✅ Acceptance Criteria

### Folder Naming:
- [ ] All new plans create folders with `[A-Z0-9]{3}-{abbreviated-name}/` pattern
- [ ] Folder ID matches master plan filename ID (e.g., `a01-enterprise-audit-logger/` for `A01-enterprise-audit-logger.md`)
- [ ] Validation checks folder name against master plan ID
- [ ] Existing plans migrated to new naming convention

### Plan Viewer HTML:
- [ ] `plan-viewer.html` generated in Phase 3 for all plans
- [ ] HTML displays all phases with task lists and hour estimates
- [ ] Progress bars update based on `progress-tracker.json`
- [ ] Interactive navigation between phases
- [ ] Registered as artifact in database

### Epic vs Feature Distinction:
- [ ] `plan_type` parameter accepted in orchestrator initialization
- [ ] Epic plans create `features/` and `integration/` folders
- [ ] Epic plans use `epic-progress-tracker.json` with nested feature tracking
- [ ] Epic plans use comprehensive template with feature breakdown section
- [ ] Feature plans remain focused with standard structure
- [ ] Phase plans support sub-phase tracking

---

## 🧪 Testing Strategy

### Unit Tests:

```python
# test_planning_orchestrator_v5_governance.py

def test_folder_naming_convention():
    """Test folder names match master plan IDs."""
    orchestrator = PlanningOrchestratorV5(
        request="Create enterprise audit logger plan",
        feature_name="enterprise-python-audit-logger"
    )
    
    master_plan_filename = orchestrator._generate_master_plan_filename()
    expected_folder = master_plan_filename.split('-')[0].lower() + "-enterprise-aud-log"
    
    orchestrator.execute()
    
    assert orchestrator.plan_folder.name.startswith(expected_folder[:3])

def test_plan_viewer_generation():
    """Test plan-viewer.html created in Phase 3."""
    orchestrator = PlanningOrchestratorV5(
        request="Create test plan"
    )
    
    orchestrator.execute()
    
    plan_viewer_path = orchestrator.plan_folder / "plan-viewer.html"
    assert plan_viewer_path.exists()
    assert "Phase 1" in plan_viewer_path.read_text()

def test_epic_plan_structure():
    """Test epic plans have features/ folder."""
    orchestrator = PlanningOrchestratorV5(
        request="Create epic plan",
        plan_type="epic"
    )
    
    orchestrator.execute()
    
    features_folder = orchestrator.plan_folder / "features"
    assert features_folder.exists()
    
    tracker_path = orchestrator.plan_folder / "tracking/epic-progress-tracker.json"
    assert tracker_path.exists()
```

### Integration Tests:

1. **End-to-End Plan Creation:** Create feature plan, verify folder naming, HTML generation, tracker initialization
2. **Epic Plan with Nested Features:** Create epic, add 2 feature sub-plans, verify parent-child tracking
3. **Migration Test:** Run folder rename utility on existing plans, verify validation passes

---

## 📅 Implementation Timeline

| Phase | Effort | Dependencies | Deliverables |
|-------|--------|--------------|--------------|
| **Phase 1: Folder Naming** | 2h | None | Updated `_create_folder_structure()`, helper method, validation |
| **Phase 2: Plan Viewer HTML** | 3h | Phase 1 (folder exists) | `_generate_plan_viewer_html()`, Phase 3 integration |
| **Phase 3: Epic/Feature Distinction** | 3h | Phase 1, 2 | `plan_type` parameter, templates, tracker logic |

**Total Effort:** 8 hours  
**Completion Target:** 2025-01-03 EOD

---

## 🔄 Migration Plan

### Existing Plans to Migrate:

```bash
# cortex-brain/documents/planning/active/
enterprise-python-audit-logger-with-self-healing/  → a01-enterprise-audit-logger/
html-glassmorphism-alignment/                      → a02-html-glassmorphism/
poc-python-execution/                              → a03-poc-python-exec/
```

**Migration Script:**

```python
# scripts/migrate_plan_folders.py

import shutil
from pathlib import Path

ACTIVE_PATH = Path("cortex-brain/documents/planning/active")

MIGRATIONS = {
    "enterprise-python-audit-logger-with-self-healing": "a01-enterprise-audit-logger",
    "html-glassmorphism-alignment": "a02-html-glassmorphism",
    "poc-python-execution": "a03-poc-python-exec"
}

for old_name, new_name in MIGRATIONS.items():
    old_path = ACTIVE_PATH / old_name
    new_path = ACTIVE_PATH / new_name
    
    if old_path.exists():
        shutil.move(str(old_path), str(new_path))
        print(f"✅ Migrated: {old_name} → {new_name}")
```

---

## 📊 Success Metrics

- **Governance Compliance:** 100% of plans follow `[A-Z0-9]{3}-{name}/` naming
- **Plan Viewer Coverage:** 100% of plans have `plan-viewer.html`
- **Type Distinction:** Epic plans clearly distinguishable from feature plans
- **Validation Pass Rate:** 100% of new plans pass governance validation
- **Migration Success:** All existing plans migrated without data loss

---

## 🔗 Related Documents

- **Naming Convention:** `context/naming-convention.md`
- **Plan Viewer Template:** `c150-remediation-plan/plan-viewer.html`
- **Planning Orchestrator:** `src/orchestrators/planning/planning_orchestrator_v5.py`
- **Governance Rules:** `cortex-brain/brain-protection-rules.yaml`

---

*Remediation sub-plan created as part of C150 Planning System Governance initiative.*
