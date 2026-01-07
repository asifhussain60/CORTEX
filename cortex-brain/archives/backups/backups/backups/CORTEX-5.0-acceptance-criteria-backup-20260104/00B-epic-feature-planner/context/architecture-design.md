# 🏗️ Epic & Feature Planner - Architecture Design

**Design Document**  
**Created:** January 4, 2026  
**Author:** Asif Hussain  
**Phase:** 00 - Architecture Design  
**Status:** 🎯 ACTIVE

---

## 1️⃣ Executive Summary

This document defines the architecture for CORTEX's dual-mode planning system, enabling both **Epic-level** (hierarchical multi-plan coordination) and **Feature-level** (single-plan execution) planning with static HTML visualization.

### Key Design Principles

1. **Mode Auto-Detection** - System automatically detects Epic vs Feature based on folder structure
2. **Backward Compatibility** - Existing Feature plans continue working unchanged
3. **Static HTML Viewers** - No server required, glassmorphism-styled progress dashboards
4. **Real-Time Updates** - Viewers auto-refresh from JSON trackers
5. **Dependency Validation** - Programmatic enforcement of inter-plan dependencies

---

## 2️⃣ System Architecture

### 2.1 Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                 CORTEX Planning System v5.0                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Mode Detector   │────────▶│  Planner Router  │          │
│  └──────────────────┘         └──────────────────┘          │
│           │                            │                     │
│           ▼                            ▼                     │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Epic Planner    │         │ Feature Planner  │          │
│  │  (Multi-Plan)    │         │  (Single-Plan)   │          │
│  └──────────────────┘         └──────────────────┘          │
│           │                            │                     │
│           ▼                            ▼                     │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │ Epic Tracker     │         │ Feature Tracker  │          │
│  │ (Aggregate)      │         │  (Phase-Based)   │          │
│  └──────────────────┘         └──────────────────┘          │
│           │                            │                     │
│           └────────────┬───────────────┘                     │
│                        ▼                                     │
│              ┌──────────────────┐                            │
│              │  HTML Generator  │                            │
│              │ (Glassmorphism)  │                            │
│              └──────────────────┘                            │
│                        │                                     │
│                        ▼                                     │
│              ┌──────────────────┐                            │
│              │  Static Viewers  │                            │
│              │  (Auto-Refresh)  │                            │
│              └──────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
User Request
     │
     ▼
┌────────────────────┐
│  Plan Directory    │──┐
│  Structure Check   │  │
└────────────────────┘  │
     │                  │
     ▼                  │
┌────────────────────┐  │  Mode Detection
│  Detect Plan Mode  │◀─┘
│  (Epic/Feature)    │
└────────────────────┘
     │
     ├─────────────────┬─────────────────┐
     ▼                 ▼                 ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Epic    │    │ Feature  │    │  Error   │
│  Mode    │    │  Mode    │    │ Handler  │
└──────────┘    └──────────┘    └──────────┘
     │                 │
     ▼                 ▼
┌──────────┐    ┌──────────┐
│ Generate │    │ Generate │
│ Epic     │    │ Feature  │
│ Tracker  │    │ Tracker  │
└──────────┘    └──────────┘
     │                 │
     └────────┬────────┘
              ▼
     ┌──────────────────┐
     │  Generate HTML   │
     │  Plan Viewer     │
     └──────────────────┘
              │
              ▼
     ┌──────────────────┐
     │  Write to Disk   │
     │  (Static HTML)   │
     └──────────────────┘
```

---

## 3️⃣ Planner Mode Detection

### 3.1 Detection Algorithm

```python
from enum import Enum
from pathlib import Path
from typing import List, Optional
import re

class PlannerMode(Enum):
    """Planning system modes."""
    EPIC = "epic"      # Multi-plan coordination
    FEATURE = "feature"  # Single-plan execution
    UNKNOWN = "unknown"  # Cannot determine

def detect_planner_mode(plan_path: Path) -> PlannerMode:
    """
    Detect planning mode based on folder structure.
    
    Epic Mode Indicators:
    - Multiple immediate child folders matching pattern: NN-{name}/
    - Master plan file: 00-MASTER-*.md or 00-EPIC-*.md
    - tracking/ folder with epic-progress-tracker.json
    - Child folders contain their own 00-*.md plans
    
    Feature Mode Indicators:
    - Single plan file: 00-{feature-name}.md
    - Standard subfolders: context/, artifacts/, reports/, tracking/
    - tracking/progress-tracker.json (not epic-progress-tracker.json)
    - No NN-{name}/ child plan folders
    
    Args:
        plan_path: Path to plan directory
        
    Returns:
        PlannerMode enum value
    """
    # Validate path exists
    if not plan_path.exists() or not plan_path.is_dir():
        return PlannerMode.UNKNOWN
    
    # Find master plan file
    master_plans = list(plan_path.glob("00-*.md"))
    if not master_plans:
        return PlannerMode.UNKNOWN
    
    # Check for epic-style child plan folders (NN-{name}/)
    child_plan_folders = [
        d for d in plan_path.iterdir()
        if d.is_dir() and re.match(r'^\d{2}[A-Z]?-', d.name)
    ]
    
    # Check if child folders contain plans
    child_plans_with_master = []
    for child_folder in child_plan_folders:
        child_master = list(child_folder.glob("00-*.md"))
        if child_master:
            child_plans_with_master.append(child_folder)
    
    # Check for epic tracker
    epic_tracker = plan_path / "tracking" / "epic-progress-tracker.json"
    feature_tracker = plan_path / "tracking" / "progress-tracker.json"
    
    # Decision logic
    if len(child_plans_with_master) >= 2 and epic_tracker.exists():
        return PlannerMode.EPIC
    elif (plan_path / "context").exists() and feature_tracker.exists():
        return PlannerMode.FEATURE
    elif len(child_plans_with_master) >= 2:
        # Has child plans but no epic tracker - still epic mode
        return PlannerMode.EPIC
    else:
        return PlannerMode.FEATURE  # Default to feature mode
```

### 3.2 Folder Structure Patterns

#### Epic Mode Pattern

```
CORTEX-5.0/                              # Epic root
├── 00-MASTER-REMEDIATION-PLAN.md        # Epic master plan
├── README.md                            # Epic overview
├── CORTEX-5.0-plan-viewer.html          # 📊 Epic HTML viewer
├── tracking/                            # Epic-level tracking
│   ├── epic-progress-tracker.json       # Aggregate metrics
│   ├── child-plan-registry.json         # Child metadata
│   └── dependency-graph.json            # Dependencies
├── 00A-epic-structure-cleanup/          # Child Plan 1
│   ├── 00-epic-structure-cleanup.md
│   ├── epic-structure-cleanup-plan-viewer.html  # 📊 Child viewer
│   ├── context/
│   ├── artifacts/
│   ├── reports/
│   └── tracking/
│       └── progress-tracker.json        # Child progress
└── 00B-epic-feature-planner/            # Child Plan 2
    ├── 00-epic-feature-planner.md
    ├── epic-feature-planner-plan-viewer.html
    └── tracking/
        └── progress-tracker.json
```

#### Feature Mode Pattern

```
test-coverage-sprint/                    # Feature root
├── 00-test-coverage-sprint.md           # Feature plan
├── README.md                            # Feature overview
├── test-coverage-sprint-plan-viewer.html  # 📊 Feature viewer
├── context/                             # Context discovery
│   ├── discovery.md
│   └── architecture-analysis.md
├── artifacts/                           # Generated code
│   ├── test_orchestrator.py
│   └── test_validator.py
├── reports/                             # Progress reports
│   └── phase-1-completion.md
└── tracking/                            # State tracking
    ├── progress-tracker.json            # Phase progress
    └── CONTINUATION-PROMPT.md           # Session state
```

---

## 4️⃣ Data Structures

### 4.1 Epic Progress Tracker Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Epic Progress Tracker",
  "type": "object",
  "required": [
    "schema_version",
    "plan_type",
    "plan_id",
    "plan_name",
    "overall_progress",
    "child_plans"
  ],
  "properties": {
    "schema_version": {
      "type": "string",
      "const": "1.0"
    },
    "plan_type": {
      "type": "string",
      "const": "epic"
    },
    "plan_id": {
      "type": "string",
      "description": "Unique identifier for the epic plan"
    },
    "plan_name": {
      "type": "string",
      "description": "Human-readable epic name"
    },
    "created_date": {
      "type": "string",
      "format": "date"
    },
    "last_updated": {
      "type": "string",
      "format": "date-time"
    },
    "overall_progress": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "description": "Aggregate progress across all child plans (percentage)"
    },
    "total_plans": {
      "type": "integer",
      "minimum": 2
    },
    "completed_plans": {
      "type": "integer",
      "minimum": 0
    },
    "total_phases": {
      "type": "integer",
      "description": "Sum of all phases across child plans"
    },
    "completed_phases": {
      "type": "integer"
    },
    "estimated_days": {
      "type": "integer"
    },
    "status": {
      "type": "string",
      "enum": ["not_started", "blocked", "in_progress", "paused", "complete", "failed"]
    },
    "child_plans": {
      "type": "array",
      "minItems": 2,
      "items": {
        "$ref": "#/definitions/child_plan"
      }
    },
    "milestones": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/milestone"
      }
    },
    "dependencies": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/dependency"
      }
    }
  },
  "definitions": {
    "child_plan": {
      "type": "object",
      "required": ["order", "id", "name", "folder", "progress", "status"],
      "properties": {
        "order": {
          "type": "string",
          "pattern": "^\\d{2}[A-Z]?$",
          "description": "Execution order (e.g., '00A', '01', '02')"
        },
        "id": {
          "type": "string",
          "description": "Kebab-case identifier"
        },
        "name": {
          "type": "string"
        },
        "folder": {
          "type": "string",
          "description": "Relative path to child plan folder"
        },
        "progress": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "phases_complete": {
          "type": "integer"
        },
        "total_phases": {
          "type": "integer"
        },
        "duration": {
          "type": "string",
          "description": "Human-readable duration (e.g., '2w', '3d')"
        },
        "status": {
          "type": "string",
          "enum": ["not_started", "blocked", "in_progress", "paused", "complete", "failed"]
        },
        "status_emoji": {
          "type": "string",
          "description": "Visual status indicator"
        },
        "dependencies": {
          "type": "array",
          "items": {"type": "string"},
          "description": "List of child_plan IDs this depends on"
        },
        "dependency_rule": {
          "type": "string",
          "description": "Human-readable dependency requirement"
        },
        "viewer_url": {
          "type": "string",
          "description": "Relative path to child plan HTML viewer"
        },
        "start_date": {
          "type": "string",
          "format": "date-time"
        },
        "end_date": {
          "type": "string",
          "format": "date-time"
        }
      }
    },
    "milestone": {
      "type": "object",
      "required": ["id", "name", "status"],
      "properties": {
        "id": {
          "type": "string"
        },
        "name": {
          "type": "string"
        },
        "description": {
          "type": "string"
        },
        "status": {
          "type": "string",
          "enum": ["not_started", "in_progress", "complete", "missed"]
        },
        "target_date": {
          "type": "string",
          "format": "date"
        },
        "actual_date": {
          "type": "string",
          "format": "date"
        },
        "criteria": {
          "type": "string"
        }
      }
    },
    "dependency": {
      "type": "object",
      "required": ["from_plan", "to_plan", "type"],
      "properties": {
        "from_plan": {
          "type": "string",
          "description": "Source plan ID"
        },
        "to_plan": {
          "type": "string",
          "description": "Target plan ID"
        },
        "type": {
          "type": "string",
          "enum": ["blocks", "enables", "informs"]
        },
        "description": {
          "type": "string"
        }
      }
    }
  }
}
```

### 4.2 Feature Progress Tracker Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Feature Progress Tracker",
  "type": "object",
  "required": [
    "schema_version",
    "plan_type",
    "plan_id",
    "plan_name",
    "overall_progress",
    "phases"
  ],
  "properties": {
    "schema_version": {
      "type": "string",
      "const": "1.0"
    },
    "plan_type": {
      "type": "string",
      "const": "feature"
    },
    "plan_id": {
      "type": "string"
    },
    "plan_name": {
      "type": "string"
    },
    "created_date": {
      "type": "string",
      "format": "date"
    },
    "last_updated": {
      "type": "string",
      "format": "date-time"
    },
    "overall_progress": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "current_phase": {
      "type": "integer",
      "minimum": -1,
      "description": "Current phase number (-1 for Phase -1, 0+ for others)"
    },
    "total_phases": {
      "type": "integer"
    },
    "completed_phases": {
      "type": "integer"
    },
    "estimated_hours": {
      "type": "number"
    },
    "actual_hours": {
      "type": "number"
    },
    "status": {
      "type": "string",
      "enum": ["not_started", "in_progress", "paused", "complete", "failed"]
    },
    "phases": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/phase"
      }
    }
  },
  "definitions": {
    "phase": {
      "type": "object",
      "required": ["phase_number", "phase_name", "status"],
      "properties": {
        "phase_number": {
          "type": "integer"
        },
        "phase_name": {
          "type": "string"
        },
        "progress": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "status": {
          "type": "string",
          "enum": ["not_started", "in_progress", "paused", "complete", "failed"]
        },
        "status_emoji": {
          "type": "string"
        },
        "estimated_hours": {
          "type": "number"
        },
        "actual_hours": {
          "type": "number"
        },
        "tasks_complete": {
          "type": "integer"
        },
        "total_tasks": {
          "type": "integer"
        },
        "start_date": {
          "type": "string",
          "format": "date-time"
        },
        "end_date": {
          "type": "string",
          "format": "date-time"
        }
      }
    }
  }
}
```

---

## 5️⃣ HTML Viewer Architecture

### 5.1 Generator Components

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

@dataclass
class ViewerConfig:
    """Configuration for HTML viewer generation."""
    plan_name: str
    plan_type: str  # "epic" or "feature"
    tracker_path: str  # Relative path to JSON tracker
    refresh_interval: int = 30  # seconds
    theme: str = "glassmorphism"
    enable_auto_refresh: bool = True
    
@dataclass
class ViewerStyle:
    """Glassmorphism styling configuration."""
    glass_bg: str = "rgba(15, 23, 42, 0.7)"
    glass_border: str = "rgba(255, 255, 255, 0.1)"
    progress_gradient: str = "linear-gradient(90deg, #00d4ff 0%, #a855f7 100%)"
    text_primary: str = "#e2e8f0"
    text_secondary: str = "#94a3b8"
    
class HTMLViewerGenerator:
    """Generates static HTML plan viewers with glassmorphism styling."""
    
    def __init__(self, config: ViewerConfig, style: ViewerStyle):
        self.config = config
        self.style = style
    
    def generate_epic_viewer(self, tracker_data: Dict) -> str:
        """Generate HTML for epic plan viewer."""
        pass
    
    def generate_feature_viewer(self, tracker_data: Dict) -> str:
        """Generate HTML for feature plan viewer."""
        pass
    
    def generate_css(self) -> str:
        """Generate glassmorphism CSS styles."""
        pass
    
    def generate_javascript(self) -> str:
        """Generate auto-refresh and progress update JavaScript."""
        pass
```

### 5.2 Auto-Refresh Mechanism

```javascript
// viewer-auto-refresh.js
class PlanViewerAutoRefresh {
    constructor(trackerPath, refreshInterval = 30000) {
        this.trackerPath = trackerPath;
        this.refreshInterval = refreshInterval;
        this.lastModified = null;
    }
    
    async checkForUpdates() {
        try {
            const response = await fetch(this.trackerPath);
            const data = await response.json();
            
            if (this.lastModified !== data.last_updated) {
                this.lastModified = data.last_updated;
                this.updateViewer(data);
            }
        } catch (error) {
            console.error('Failed to fetch tracker:', error);
        }
    }
    
    updateViewer(data) {
        // Update progress bars, status indicators, metrics
        this.updateOverallProgress(data.overall_progress);
        this.updateChildPlans(data.child_plans);
        this.updateMilestones(data.milestones);
    }
    
    start() {
        // Initial load
        this.checkForUpdates();
        
        // Set up periodic refresh
        setInterval(() => this.checkForUpdates(), this.refreshInterval);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const viewer = new PlanViewerAutoRefresh('tracking/epic-progress-tracker.json');
    viewer.start();
});
```

---

## 6️⃣ Dependency Validation System

### 6.1 Dependency Graph Structure

```json
{
  "dependencies": [
    {
      "from_plan": "epic-structure-cleanup",
      "to_plan": "epic-feature-planner",
      "type": "blocks",
      "description": "Epic structure must be valid before planner implementation"
    },
    {
      "from_plan": "epic-feature-planner",
      "to_plan": "test-coverage-sprint",
      "type": "enables",
      "description": "Epic infrastructure required for coordinated testing"
    }
  ]
}
```

### 6.2 Validation Algorithm

```python
from typing import Dict, List, Set

class DependencyValidator:
    """Validates inter-plan dependencies."""
    
    def __init__(self, epic_tracker: Dict):
        self.epic_tracker = epic_tracker
        self.child_plans = {
            plan["id"]: plan 
            for plan in epic_tracker["child_plans"]
        }
    
    def validate_dependencies(self, plan_id: str) -> bool:
        """Check if all dependencies for a plan are satisfied."""
        plan = self.child_plans.get(plan_id)
        if not plan:
            return False
        
        dependencies = plan.get("dependencies", [])
        for dep_id in dependencies:
            dep_plan = self.child_plans.get(dep_id)
            if not dep_plan:
                return False
            
            # Dependency must be complete
            if dep_plan["status"] != "complete":
                return False
        
        return True
    
    def get_blocked_plans(self) -> List[str]:
        """Get list of plan IDs blocked by dependencies."""
        blocked = []
        for plan_id, plan in self.child_plans.items():
            if plan["status"] == "blocked":
                if not self.validate_dependencies(plan_id):
                    blocked.append(plan_id)
        return blocked
    
    def get_ready_plans(self) -> List[str]:
        """Get list of plan IDs ready to start."""
        ready = []
        for plan_id, plan in self.child_plans.items():
            if plan["status"] in ["not_started", "blocked"]:
                if self.validate_dependencies(plan_id):
                    ready.append(plan_id)
        return ready
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependency chains."""
        def dfs(node: str, visited: Set[str], path: List[str]) -> Optional[List[str]]:
            if node in path:
                # Found cycle
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]
            
            if node in visited:
                return None
            
            visited.add(node)
            path.append(node)
            
            plan = self.child_plans.get(node)
            if plan:
                for dep in plan.get("dependencies", []):
                    cycle = dfs(dep, visited, path[:])
                    if cycle:
                        return cycle
            
            return None
        
        cycles = []
        visited = set()
        
        for plan_id in self.child_plans:
            if plan_id not in visited:
                cycle = dfs(plan_id, visited, [])
                if cycle:
                    cycles.append(cycle)
        
        return cycles
```

---

## 7️⃣ Integration Points

### 7.1 Planning Orchestrator Integration

```python
# src/orchestrators/planning/planning_orchestrator.py

from src.orchestrators.planning.epic_planner import EpicPlanner
from src.orchestrators.planning.feature_planner import FeaturePlanner
from src.orchestrators.planning.planner_mode_detector import detect_planner_mode, PlannerMode

class PlanningOrchestrator(BaseOrchestrator):
    """Main planning orchestrator with dual-mode support."""
    
    def create_plan(self, request: Dict) -> OrchestratorResult:
        """Create a new plan (epic or feature)."""
        plan_path = Path(request.get("plan_path"))
        
        # Detect mode
        mode = detect_planner_mode(plan_path)
        
        # Route to appropriate planner
        if mode == PlannerMode.EPIC:
            planner = EpicPlanner(plan_path)
            result = planner.create_epic_plan(request)
        elif mode == PlannerMode.FEATURE:
            planner = FeaturePlanner(plan_path)
            result = planner.create_feature_plan(request)
        else:
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                message=f"Cannot determine planner mode for {plan_path}"
            )
        
        # Generate HTML viewer
        self._generate_html_viewer(plan_path, mode)
        
        return result
```

### 7.2 Plan Viewer Generation Integration

```python
# Integrate HTML generation into plan creation workflow

def _generate_html_viewer(self, plan_path: Path, mode: PlannerMode):
    """Generate HTML viewer after plan creation/update."""
    from src.orchestrators.planning.html_viewer_generator import HTMLViewerGenerator
    
    if mode == PlannerMode.EPIC:
        tracker_path = plan_path / "tracking" / "epic-progress-tracker.json"
    else:
        tracker_path = plan_path / "tracking" / "progress-tracker.json"
    
    if not tracker_path.exists():
        logger.warning(f"Tracker not found: {tracker_path}")
        return
    
    # Load tracker data
    with open(tracker_path) as f:
        tracker_data = json.load(f)
    
    # Generate viewer
    generator = HTMLViewerGenerator(
        config=ViewerConfig(
            plan_name=tracker_data["plan_name"],
            plan_type=mode.value,
            tracker_path=f"tracking/{tracker_path.name}"
        ),
        style=ViewerStyle()
    )
    
    if mode == PlannerMode.EPIC:
        html = generator.generate_epic_viewer(tracker_data)
    else:
        html = generator.generate_feature_viewer(tracker_data)
    
    # Write viewer file
    viewer_file = plan_path / f"{tracker_data['plan_id']}-plan-viewer.html"
    viewer_file.write_text(html)
    
    logger.info(f"Generated HTML viewer: {viewer_file}")
```

---

## 8️⃣ Success Criteria

### Phase 00 Completion Criteria

- [x] Architecture design document complete
- [x] Mode detection algorithm defined
- [x] Data structure schemas finalized
- [x] HTML viewer architecture designed
- [x] Dependency validation system designed
- [x] Integration points identified

### Next Phase Prerequisites

**Phase 01: Epic Planner Implementation** requires:
- ✅ Architecture approved
- ✅ Data structures validated
- ✅ Mode detection algorithm tested
- ✅ Integration approach confirmed

---

## 9️⃣ Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Backward compatibility break** | High | Maintain feature planner unchanged, add epic as new mode |
| **Performance (large epics)** | Medium | Lazy load child plan data, paginate if >50 plans |
| **HTML viewer reliability** | Medium | Fallback to JSON if HTML generation fails |
| **Circular dependencies** | High | Implement detection algorithm, fail fast on cycle |

---

## 🎯 Implementation Roadmap

### Phase 01: Epic Planner Core (Next)
- Implement `EpicPlanner` class
- Build child plan registry
- Create aggregate progress calculator
- Add dependency validator

### Phase 02: Feature Planner Enhancement
- Integrate mode detection
- Add HTML viewer generation
- Maintain backward compatibility

### Phase 03: HTML Viewer Generator
- Build glassmorphism template
- Implement auto-refresh JavaScript
- Add responsive design

### Phase 04-06: Testing, Validation, Documentation
- Comprehensive test suite
- User documentation
- Migration guide

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
