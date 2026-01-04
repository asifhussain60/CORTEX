# 🎭 Epic & Feature Planner Vision - Dual-Mode Planning System

**Plan ID:** epic-feature-planner-vision  
**Created:** January 4, 2026  
**Author:** Asif Hussain  
**Status:** 🎯 DESIGN PHASE  
**Complexity:** TIER 4 (SYSTEM-WIDE ENHANCEMENT)  
**Affects:** Planning Orchestrator, ADO Orchestrator, Plan Viewer  
**Duration:** 2-3 weeks

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░` **0%** ⏳ DESIGN PHASE

| Phase | Description | Progress | Status | Duration |
|-------|-------------|----------|--------|----------|
| 00 | Architecture Design | `░░░░░░░░░░` 0% | ⏳ Pending | 2d |
| 01 | Epic Planner Implementation | `░░░░░░░░░░` 0% | ⏳ Pending | 3d |
| 02 | Feature Planner Enhancement | `░░░░░░░░░░` 0% | ⏳ Pending | 2d |
| 03 | Plan Viewer HTML Generator | `░░░░░░░░░░` 0% | ⏳ Pending | 4d |
| 04 | Real-Time Progress Updates | `░░░░░░░░░░` 0% | ⏳ Pending | 3d |
| 05 | Testing & Validation | `░░░░░░░░░░` 0% | ⏳ Pending | 2d |
| 06 | Documentation & Templates | `░░░░░░░░░░` 0% | ⏳ Pending | 1d |

---

## 🎯 Executive Summary

### Problem Statement

Current planning system only supports **single-level planning** (one master plan with subfolders). Complex initiatives like CORTEX-5.0 require **hierarchical planning** with:

1. **Epic-level plans** - Strategic initiatives spanning multiple features (e.g., CORTEX-5.0)
2. **Feature-level plans** - Individual work items within epics (e.g., Test Coverage Sprint)
3. **Unified visibility** - Single view showing progress across all levels
4. **Static HTML viewers** - No need to run plan viewer application separately

### Current Limitations

| Issue | Impact | Example |
|-------|--------|---------|
| **No Epic Support** | Can't manage multi-phase strategic work | CORTEX-5.0 has 13 child plans but no epic-level orchestration |
| **Manual Coordination** | Must track dependencies manually | Sub-plan 01 depends on 00, but no automated validation |
| **No Unified View** | Can't see overall epic progress | Must open 13+ folders to understand CORTEX-5.0 status |
| **Separate Viewer App** | CORTEX-LENS runs as standalone | Users must run app + navigate UI vs. simple HTML file |

### Proposed Solution

**Dual-Mode Planning System:**
- **Epic Planner** - Multi-child plans with dependency tracking (like CORTEX-5.0)
- **Feature Planner** - Single plan with subfolder structure (existing behavior)
- **Static HTML Viewer** - Glassmorphism-styled `{PLAN-ID}-plan-viewer.html` per plan
- **Auto-Refresh** - Viewer updates as plan executes (reads progress tracker JSON)

---

## 🏗️ Architecture Design

### 1. Planner Mode Detection

```yaml
# Planning mode detection rules
modes:
  epic_planner:
    triggers:
      - folder_structure: "multiple immediate subfolders with 00-*.md files"
      - naming_pattern: "NN-{name}/ subfolders with master plan in each"
      - master_plan: "00-MASTER-*.md in root"
    example: "CORTEX-5.0/00-MASTER-REMEDIATION-PLAN.md + 13 child plans"
  
  feature_planner:
    triggers:
      - folder_structure: "single plan with context/artifacts/reports/tracking"
      - master_plan: "00-{feature-name}.md in root"
      - no_child_plans: "no NN-{name}/ subfolders"
    example: "test-coverage-sprint/00-test-coverage-sprint.md"
```

**Detection Logic:**

```python
def detect_planner_mode(plan_path: Path) -> PlannerMode:
    """
    Determine if plan is Epic or Feature based on structure.
    
    Epic: Root folder with NN-{name}/ subfolders containing plans
    Feature: Root folder with context/, artifacts/, reports/, tracking/
    """
    master_plan = list(plan_path.glob("00-*.md"))
    child_plans = [d for d in plan_path.iterdir() 
                   if d.is_dir() and re.match(r'^\d{2}-', d.name)]
    
    if len(child_plans) >= 2 and master_plan:
        return PlannerMode.EPIC
    elif (plan_path / "context").exists() and \
         (plan_path / "tracking").exists():
        return PlannerMode.FEATURE
    else:
        raise ValueError(f"Cannot detect planner mode for {plan_path}")
```

### 2. Epic Planner Structure

```
CORTEX-5.0/                              # Epic root
├── 00-MASTER-REMEDIATION-PLAN.md        # Epic master plan
├── README.md                            # Epic overview
├── CORTEX-5.0-plan-viewer.html          # Epic viewer (NEW)
├── tracking/                            # Epic-level tracking
│   ├── epic-progress-tracker.json       # Aggregate progress
│   ├── child-plan-registry.json         # Child plan metadata
│   └── dependency-graph.json            # Inter-plan dependencies
├── 00-test-coverage-sprint/             # Child Feature Plan 1
│   ├── 00-test-coverage-sprint.md
│   ├── test-coverage-sprint-plan-viewer.html  # Feature viewer (NEW)
│   ├── context/
│   ├── artifacts/
│   ├── reports/
│   └── tracking/
│       └── progress-tracker.json        # Feature progress
├── 01-refinement-orchestrator/          # Child Feature Plan 2
│   ├── 00-refinement-orchestrator.md
│   ├── refinement-orchestrator-plan-viewer.html
│   └── tracking/
│       └── progress-tracker.json
└── 02-debug-orchestrator/               # Child Feature Plan 3
    └── ... (same structure)
```

**Key Differences:**

| Aspect | Epic Planner | Feature Planner |
|--------|--------------|-----------------|
| **Root Plan** | `00-MASTER-*.md` | `00-{feature-name}.md` |
| **Child Plans** | 2+ subfolder plans | None (subfolder structure only) |
| **Progress Tracking** | `epic-progress-tracker.json` | `progress-tracker.json` |
| **Viewer Scope** | Shows all child plans | Shows single plan phases |
| **Dependencies** | Inter-plan dependencies | Intra-plan phase dependencies |

### 3. Feature Planner Structure (Existing + Viewer)

```
test-coverage-sprint/                    # Feature root
├── 00-test-coverage-sprint.md           # Feature master plan
├── README.md                            # Feature overview
├── test-coverage-sprint-plan-viewer.html  # Feature viewer (NEW)
├── context/                             # Context discovery
│   ├── discovery.md
│   └── architecture-analysis.md
├── artifacts/                           # Generated outputs
│   ├── test_brain_protection.py
│   └── test_orchestrator_common.py
├── reports/                             # Progress reports
│   ├── phase-1-completion.md
│   └── validation-report.md
└── tracking/                            # State tracking
    ├── progress-tracker.json            # Feature progress
    └── CONTINUATION-PROMPT.md
```

---

## 📄 Plan Viewer HTML Generator

### Design Requirements

**Must Follow:** `glassmorphism-design-standard.md`

#### Visual Design Standards

| Requirement | Glassmorphism Standard | Implementation |
|-------------|------------------------|----------------|
| **Glass Panels** | `backdrop-filter: blur(20px)` | `.plan-panel` class |
| **Subtle Animation** | T1 (0.2-0.3s transitions) | Hover + progress updates only |
| **Progress Bars** | Tetris-style animated fills | `.progress-bar-fill` with gradient |
| **Color Scheme** | Blue-purple gradients | `#00d4ff → #a855f7` |
| **Typography** | Inter font, responsive sizing | `clamp()` with `cqi` units |
| **Accessibility** | WCAG AA compliant | ARIA labels, semantic HTML |

#### Core Features

**1. Epic Plan Viewer (`CORTEX-5.0-plan-viewer.html`)**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX v5 Epic Progress</title>
    <style>
        /* Glassmorphism base styles */
        :root {
            --glass-bg: rgba(15, 23, 42, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
            --progress-gradient: linear-gradient(90deg, #00d4ff 0%, #a855f7 100%);
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: var(--text-primary);
            margin: 0;
            padding: 2rem;
            min-height: 100vh;
        }
        
        .epic-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .glass-panel {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .glass-panel:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);
        }
        
        .epic-header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .epic-title {
            font-size: clamp(2rem, 4cqi, 3rem);
            font-weight: 700;
            background: linear-gradient(90deg, #00d4ff, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .epic-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #00d4ff;
        }
        
        .stat-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .progress-bar {
            height: 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            overflow: hidden;
            position: relative;
            margin: 1rem 0;
        }
        
        .progress-bar-fill {
            height: 100%;
            background: var(--progress-gradient);
            border-radius: 20px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            position: relative;
        }
        
        .progress-bar-fill::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.3),
                transparent
            );
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .child-plans-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1rem;
        }
        
        .child-plan-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 1.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .child-plan-card:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(0, 212, 255, 0.3);
        }
        
        .child-plan-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        
        .child-plan-status {
            font-size: 1.5rem;
        }
        
        .dependency-tag {
            display: inline-block;
            background: rgba(168, 85, 247, 0.2);
            color: #c084fc;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            margin-top: 0.5rem;
        }
        
        .auto-refresh-indicator {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: rgba(0, 212, 255, 0.2);
            border: 1px solid rgba(0, 212, 255, 0.4);
            border-radius: 24px;
            padding: 0.75rem 1.5rem;
            font-size: 0.875rem;
            backdrop-filter: blur(10px);
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="epic-container">
        <!-- Epic Header -->
        <div class="epic-header">
            <h1 class="epic-title">🎯 CORTEX v5 Gap Remediation</h1>
            <p class="epic-subtitle">Strategic Multi-Phase Epic Plan</p>
        </div>
        
        <!-- Epic Stats -->
        <div class="glass-panel">
            <div class="epic-stats">
                <div class="stat-card">
                    <div class="stat-value" id="epic-progress">0%</div>
                    <div class="stat-label">Overall Progress</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="child-plans-complete">0/13</div>
                    <div class="stat-label">Plans Complete</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="total-phases">0/60</div>
                    <div class="stat-label">Phases Complete</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="estimated-days">56d</div>
                    <div class="stat-label">Estimated Duration</div>
                </div>
            </div>
            
            <!-- Overall Progress Bar -->
            <div class="progress-bar">
                <div class="progress-bar-fill" id="epic-progress-bar" style="width: 0%">
                    <span id="epic-progress-text">0% Complete</span>
                </div>
            </div>
        </div>
        
        <!-- Child Plans Grid -->
        <div class="glass-panel">
            <h2>📋 Child Feature Plans</h2>
            <div class="child-plans-grid" id="child-plans-container">
                <!-- Child plan cards dynamically populated -->
            </div>
        </div>
    </div>
    
    <!-- Auto-Refresh Indicator -->
    <div class="auto-refresh-indicator pulse">
        🔄 Auto-refreshing every 5s
    </div>
    
    <script>
        // Configuration
        const EPIC_PATH = '.';
        const TRACKING_FILE = 'tracking/epic-progress-tracker.json';
        const REFRESH_INTERVAL = 5000; // 5 seconds
        
        // Load and render epic progress
        async function loadEpicProgress() {
            try {
                const response = await fetch(TRACKING_FILE);
                const data = await response.json();
                
                // Update epic stats
                document.getElementById('epic-progress').textContent = 
                    `${data.overall_progress}%`;
                document.getElementById('child-plans-complete').textContent = 
                    `${data.completed_plans}/${data.total_plans}`;
                document.getElementById('total-phases').textContent = 
                    `${data.completed_phases}/${data.total_phases}`;
                
                // Update progress bar
                const progressBar = document.getElementById('epic-progress-bar');
                progressBar.style.width = `${data.overall_progress}%`;
                document.getElementById('epic-progress-text').textContent = 
                    `${data.overall_progress}% Complete`;
                
                // Render child plans
                renderChildPlans(data.child_plans);
                
            } catch (error) {
                console.error('Failed to load epic progress:', error);
            }
        }
        
        // Render child plan cards
        function renderChildPlans(childPlans) {
            const container = document.getElementById('child-plans-container');
            container.innerHTML = '';
            
            childPlans.forEach(plan => {
                const card = document.createElement('div');
                card.className = 'child-plan-card';
                card.onclick = () => openChildPlanViewer(plan.id);
                
                card.innerHTML = `
                    <div class="child-plan-header">
                        <h3>${plan.order}. ${plan.name}</h3>
                        <span class="child-plan-status">${plan.status_emoji}</span>
                    </div>
                    <div class="progress-bar" style="height: 20px;">
                        <div class="progress-bar-fill" style="width: ${plan.progress}%; font-size: 0.75rem;">
                            ${plan.progress}%
                        </div>
                    </div>
                    <p style="font-size: 0.875rem; color: var(--text-secondary); margin: 0.5rem 0;">
                        ${plan.phases_complete}/${plan.total_phases} phases • ${plan.duration}
                    </p>
                    ${plan.dependencies.length > 0 ? `
                        <div class="dependency-tag">
                            Depends on: ${plan.dependencies.join(', ')}
                        </div>
                    ` : ''}
                `;
                
                container.appendChild(card);
            });
        }
        
        // Open child plan viewer
        function openChildPlanViewer(planId) {
            const viewerPath = `${planId}/${planId}-plan-viewer.html`;
            window.open(viewerPath, '_blank');
        }
        
        // Auto-refresh
        setInterval(loadEpicProgress, REFRESH_INTERVAL);
        
        // Initial load
        loadEpicProgress();
    </script>
</body>
</html>
```

**2. Feature Plan Viewer (`test-coverage-sprint-plan-viewer.html`)**

Similar structure but simpler:
- Single plan progress (no child plans grid)
- Phase-by-phase breakdown with task lists
- Links to artifacts and reports
- Real-time phase completion updates

---

## 🔧 Implementation Details

### Phase 00: Architecture Design

**Duration:** 2 days

**Tasks:**

1. **Define Data Models**

```python
# src/orchestrators/planning/models.py

from enum import Enum
from dataclasses import dataclass
from pathlib import Path

class PlannerMode(Enum):
    """Planner operational mode."""
    EPIC = "epic"      # Multi-child plans
    FEATURE = "feature"  # Single plan

@dataclass
class EpicPlan:
    """Epic plan with multiple child feature plans."""
    plan_id: str
    name: str
    master_plan_path: Path
    child_plans: list['FeaturePlan']
    tracking_path: Path
    viewer_path: Path
    overall_progress: float
    dependencies: dict[str, list[str]]  # child_id -> [dependency_ids]
    
@dataclass
class FeaturePlan:
    """Single feature plan with phases."""
    plan_id: str
    name: str
    order: int  # For epic child plans (00, 01, 02...)
    master_plan_path: Path
    tracking_path: Path
    viewer_path: Path
    phases: list['PlanPhase']
    progress: float
    status: str
    parent_epic: Optional[str] = None
    
@dataclass
class PlanPhase:
    """Individual phase within a feature plan."""
    number: int
    name: str
    description: str
    progress: float
    status: str
    tasks: list['PlanTask']
    estimated_duration_hours: float
```

2. **Update Manifest Schema**

Add to `planning-system-5.0-manifest.yaml`:

```yaml
# Planner mode configuration
planner_modes:
  epic:
    description: "Multi-child plan orchestration with dependency tracking"
    detection:
      - "Root folder with 2+ NN-{name}/ subfolders"
      - "Each subfolder contains 00-*.md master plan"
      - "Root contains 00-MASTER-*.md epic plan"
    folder_structure:
      root: "cortex-brain/documents/planning/active/{epic-name}/"
      tracking_folder: "tracking/"
      required_files:
        - "00-MASTER-{epic-name}.md"
        - "tracking/epic-progress-tracker.json"
        - "tracking/child-plan-registry.json"
        - "tracking/dependency-graph.json"
        - "{epic-name}-plan-viewer.html"
      child_plans: "NN-{feature-name}/"
    
  feature:
    description: "Single plan with subfolder structure (existing behavior)"
    detection:
      - "Root folder with context/, artifacts/, reports/, tracking/"
      - "Root contains 00-{feature-name}.md"
      - "No NN-{name}/ child plan subfolders"
    folder_structure:
      root: "cortex-brain/documents/planning/active/{feature-name}/"
      subfolders: ["context", "artifacts", "reports", "tracking"]
      required_files:
        - "00-{feature-name}.md"
        - "tracking/progress-tracker.json"
        - "{feature-name}-plan-viewer.html"

# HTML viewer generation
html_viewer:
  enabled: true
  generation_timing:
    - "on_plan_creation"
    - "on_plan_update"
  
  templates:
    epic_viewer: "templates/planning/epic-plan-viewer.jinja2"
    feature_viewer: "templates/planning/feature-plan-viewer.jinja2"
  
  glassmorphism_compliance:
    design_standard: "cortex-brain/documents/standards/glassmorphism-design-standard.md"
    tier: "T1"  # Subtle animations only
    required_features:
      - "Glass panels with backdrop-filter"
      - "Responsive tetris-style progress bars"
      - "Auto-refresh every 5s"
      - "WCAG AA accessibility"
      - "Mobile-friendly (A+ grade)"
  
  output_naming:
    epic: "{epic-id}-plan-viewer.html"
    feature: "{feature-id}-plan-viewer.html"
```

3. **Design Tracking JSON Schemas**

**Epic Progress Tracker:**

```json
{
  "schema_version": "1.0",
  "plan_type": "epic",
  "plan_id": "cortex-v5-gap-remediation",
  "plan_name": "CORTEX v5 Gap Remediation & Completion",
  "created_date": "2026-01-03",
  "last_updated": "2026-01-04T10:30:00Z",
  "overall_progress": 0.0,
  "total_plans": 13,
  "completed_plans": 0,
  "total_phases": 60,
  "completed_phases": 0,
  "estimated_days": 56,
  "status": "not_started",
  "child_plans": [
    {
      "order": "00",
      "id": "test-coverage-sprint",
      "name": "Test Coverage Sprint",
      "folder": "00-test-coverage-sprint/",
      "progress": 0.0,
      "phases_complete": 0,
      "total_phases": 5,
      "duration": "2-3w",
      "status": "not_started",
      "status_emoji": "⏳",
      "dependencies": [],
      "viewer_url": "00-test-coverage-sprint/test-coverage-sprint-plan-viewer.html"
    },
    {
      "order": "01",
      "id": "refinement-orchestrator",
      "name": "Refinement Orchestrator",
      "folder": "01-refinement-orchestrator/",
      "progress": 0.0,
      "phases_complete": 0,
      "total_phases": 4,
      "duration": "1w",
      "status": "blocked",
      "status_emoji": "🔒",
      "dependencies": ["test-coverage-sprint"],
      "dependency_rule": "Test Coverage ≥50%",
      "viewer_url": "01-refinement-orchestrator/refinement-orchestrator-plan-viewer.html"
    }
  ],
  "dependency_graph": {
    "test-coverage-sprint": [],
    "refinement-orchestrator": ["test-coverage-sprint"],
    "debug-orchestrator": ["test-coverage-sprint"]
  }
}
```

**Feature Progress Tracker (Enhanced):**

```json
{
  "schema_version": "1.0",
  "plan_type": "feature",
  "plan_id": "test-coverage-sprint",
  "plan_name": "Test Coverage Sprint",
  "parent_epic": "cortex-v5-gap-remediation",
  "order": "00",
  "created_date": "2026-01-03",
  "last_updated": "2026-01-04T10:30:00Z",
  "overall_progress": 0.0,
  "total_phases": 5,
  "completed_phases": 0,
  "estimated_hours": 120,
  "status": "not_started",
  "phases": [
    {
      "number": 0,
      "name": "Test Infrastructure Setup",
      "description": "Create folder structure and fixtures",
      "progress": 0.0,
      "status": "not_started",
      "tasks": [
        {
          "id": "task-00-01",
          "description": "Create tests/brain_protection/ folder",
          "status": "not_started",
          "completed": false
        },
        {
          "id": "task-00-02",
          "description": "Create tests/orchestrators/common/ folder",
          "status": "not_started",
          "completed": false
        }
      ],
      "estimated_hours": 8
    }
  ]
}
```

### Phase 01: Epic Planner Implementation

**Duration:** 3 days

**Tasks:**

1. Create `src/orchestrators/planning/epic_planner.py`
2. Implement epic detection logic
3. Add child plan registration
4. Build dependency validation
5. Create epic progress aggregation
6. Write unit tests for epic planner

**Key Components:**

```python
# src/orchestrators/planning/epic_planner.py

class EpicPlanner:
    """Orchestrates multi-child feature plans with dependency tracking."""
    
    def __init__(self, epic_path: Path):
        self.epic_path = epic_path
        self.epic_plan = self._load_epic_plan()
        self.child_plans = self._discover_child_plans()
        
    def create_epic(
        self,
        epic_id: str,
        epic_name: str,
        child_plan_specs: list[dict]
    ) -> EpicPlan:
        """Create new epic with child feature plans."""
        pass
    
    def register_child_plan(self, feature_plan: FeaturePlan):
        """Register child feature plan in epic tracker."""
        pass
    
    def validate_dependencies(self) -> dict[str, list[str]]:
        """Check if dependency requirements are met."""
        pass
    
    def aggregate_progress(self) -> float:
        """Calculate overall epic progress from child plans."""
        pass
    
    def update_epic_tracker(self):
        """Sync epic progress tracker JSON."""
        pass
    
    def generate_epic_viewer(self):
        """Generate epic HTML viewer."""
        pass
```

### Phase 02: Feature Planner Enhancement

**Duration:** 2 days

**Tasks:**

1. Update `src/orchestrators/planning/planning_orchestrator_v5.py`
2. Add parent epic awareness
3. Implement feature-to-epic progress sync
4. Enhance feature tracker JSON
5. Add feature viewer generation
6. Write integration tests

### Phase 03: Plan Viewer HTML Generator

**Duration:** 4 days

**Tasks:**

1. Create Jinja2 templates
   - `templates/planning/epic-plan-viewer.jinja2`
   - `templates/planning/feature-plan-viewer.jinja2`

2. Implement viewer generator
   ```python
   # src/orchestrators/planning/viewer_generator.py
   
   class PlanViewerGenerator:
       """Generate glassmorphism-styled HTML plan viewers."""
       
       def generate_epic_viewer(self, epic: EpicPlan) -> Path:
           """Generate epic plan viewer HTML."""
           pass
       
       def generate_feature_viewer(self, feature: FeaturePlan) -> Path:
           """Generate feature plan viewer HTML."""
           pass
       
       def validate_glassmorphism_compliance(self, html_path: Path) -> bool:
           """Ensure viewer follows design standard."""
           pass
   ```

3. Add auto-refresh JavaScript
4. Implement responsive CSS
5. Test across browsers
6. Validate WCAG AA compliance

### Phase 04: Real-Time Progress Updates

**Duration:** 3 days

**Tasks:**

1. Add JSON tracker update hooks to plan executors
2. Implement file watching for auto-refresh
3. Create progress calculation utilities
4. Add status emoji mapping
5. Build dependency status tracker
6. Test concurrent plan execution

### Phase 05: Testing & Validation

**Duration:** 2 days

**Tasks:**

1. Write unit tests for Epic/Feature planners
2. Integration tests for viewer generation
3. End-to-end test with CORTEX-5.0 structure
4. Performance testing (large epic with 20+ child plans)
5. Accessibility audit (WCAG AA)
6. Mobile responsiveness validation

### Phase 06: Documentation & Templates

**Duration:** 1 day

**Tasks:**

1. Update planning system documentation
2. Create Epic/Feature planner user guide
3. Add viewer usage examples
4. Update manifest documentation
5. Create migration guide for existing plans
6. Record demo video

---

## 📊 Success Criteria

### Must-Have (MVP)

- ✅ Epic planner detects and manages 2+ child feature plans
- ✅ Feature planner aware of parent epic (if exists)
- ✅ Static HTML viewers generated for both epic and feature plans
- ✅ Viewers follow glassmorphism-design-standard.md (T1 animations)
- ✅ Auto-refresh every 5s reading progress tracker JSON
- ✅ Dependency tracking shows blocked/ready status
- ✅ Overall progress aggregates from child plans
- ✅ WCAG AA accessibility compliant

### Nice-to-Have (Future)

- ⏭️ Dependency graph visualization (interactive SVG)
- ⏭️ Timeline Gantt chart view
- ⏭️ Export to ADO work items (epic → feature → task mapping)
- ⏭️ Slack/Teams notifications on phase completion
- ⏭️ AI-powered bottleneck detection
- ⏭️ Historical epic analytics dashboard

---

## 🔗 Integration Points

### Planning Orchestrator v5

**Changes:**
- Add `planner_mode` parameter (EPIC | FEATURE)
- Implement `detect_planner_mode()` before execution
- Route to EpicPlanner or FeaturePlanner based on detection
- Generate appropriate HTML viewer post-execution

### ADO Orchestrator

**Changes:**
- Map Epic Plan → ADO Epic
- Map Feature Plan → ADO Feature
- Map Plan Phase → ADO User Story
- Map Plan Task → ADO Task
- Link epic-feature-task hierarchy in Azure DevOps

### CORTEX-LENS (Future)

**Changes:**
- Embed static HTML viewers in LENS admin dashboard
- Add "Open Viewer" button next to each plan
- Display epic/feature tree navigation
- Real-time status badges in plan list

---

## 🚨 Brain Protection Rules

### SKULL Compliance

| Rule | Application |
|------|-------------|
| **TDD_ENFORCEMENT** | All new planner code has tests first |
| **HOLISTIC_DISCOVERY** | Search for existing plan viewers before creating |
| **GIT_ISOLATION** | Plan viewers stay in CORTEX repo only |
| **PLANNING_ISOLATION** | This plan creates NO implementations (design only) |
| **HAND_OFF_PROTOCOL** | Implementation deferred to execution phase |

---

## 📚 References

### Key Files

| File | Purpose |
|------|---------|
| `cortex-brain/documents/standards/glassmorphism-design-standard.md` | UI design requirements |
| `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml` | Current planning manifest |
| `cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml` | ADO integration specs |
| `cortex-brain/documents/planning/active/CORTEX-5.0/` | Epic plan example |

### Template Locations

```
templates/planning/
├── epic-plan-viewer.jinja2           # Epic HTML template
├── feature-plan-viewer.jinja2        # Feature HTML template
├── epic-progress-tracker.json.jinja2
└── dependency-graph.json.jinja2
```

---

## 🎯 Next Steps

**When Ready to Implement:**

1. **Create Sub-Plan:** Generate implementation plan in `cortex-brain/documents/planning/active/CORTEX-5.0/16-epic-feature-planner/`
2. **TDD First:** Write tests before implementing Epic/Feature planners
3. **Iterative Development:** Build Epic → Feature → Viewer → Integration
4. **User Feedback:** Test with CORTEX-5.0 epic structure
5. **ADO Integration:** Extend to ADO orchestrator after planning works

**Approval Gates:**

- ✅ Design review (this document)
- ✅ Glassmorphism standard compliance check
- ✅ Manifest schema validation
- ✅ SKULL rules verification

---

## 📝 Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-04 | 1.0.0 | Initial design document created |

---

**🧠 CORTEX Response Template:** `planning_design_document`  
**Author:** Asif Hussain  
**Last Updated:** January 4, 2026
