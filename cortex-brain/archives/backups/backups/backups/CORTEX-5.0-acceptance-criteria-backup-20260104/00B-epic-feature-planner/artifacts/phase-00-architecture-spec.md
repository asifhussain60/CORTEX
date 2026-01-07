# 🏗️ Phase 00: Architecture Specification - Epic & Feature Planner

**Sub-Plan:** 00B - Epic & Feature Planner Implementation  
**Phase:** 00 - Architecture Design  
**Created:** January 4, 2026  
**Author:** Asif Hussain  
**Status:** ✅ COMPLETE

---

## 📊 Phase Progress

**Progress:** `██████████` **100%** ✅ COMPLETE

**Deliverables:**
- ✅ Data model specifications (Python dataclasses)
- ✅ Manifest schema updates (YAML)
- ✅ JSON tracking schemas (epic + feature)
- ✅ HTML viewer architecture (glassmorphism compliant)
- ✅ Integration point specifications

---

## 🎯 Architecture Overview

### Core Components

```
Epic & Feature Planner System
├── 1. Planner Mode Detector
│   ├── detect_planner_mode(plan_path) → PlannerMode
│   ├── validate_epic_structure(plan_path) → bool
│   └── validate_feature_structure(plan_path) → bool
│
├── 2. Epic Planner
│   ├── EpicPlan (dataclass)
│   ├── load_epic_tracker() → EpicPlan
│   ├── update_epic_progress() → None
│   └── generate_epic_viewer() → Path
│
├── 3. Feature Planner
│   ├── FeaturePlan (dataclass)
│   ├── load_feature_tracker() → FeaturePlan
│   ├── update_feature_progress() → None
│   └── generate_feature_viewer() → Path
│
├── 4. HTML Viewer Generator
│   ├── EpicViewerTemplate (Jinja2)
│   ├── FeatureViewerTemplate (Jinja2)
│   ├── render_epic_viewer() → HTML
│   └── render_feature_viewer() → HTML
│
└── 5. Progress Tracker
    ├── epic-progress-tracker.json
    ├── child-plan-registry.json
    ├── dependency-graph.json
    └── progress-tracker.json (feature)
```

---

## 📐 Data Models

### 1. Planner Mode Enumeration

```python
# src/orchestrators/planning/models.py

from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

class PlannerMode(Enum):
    """Planner operational mode."""
    EPIC = "epic"       # Multi-child plans with dependencies
    FEATURE = "feature"  # Single plan with phases
    
    @classmethod
    def detect(cls, plan_path: Path) -> 'PlannerMode':
        """
        Detect planner mode from folder structure.
        
        Epic indicators:
        - 2+ immediate subfolders matching NN-{name}/ pattern
        - Each subfolder contains 00-*.md master plan
        - Root contains 00-MASTER-*.md or similar
        
        Feature indicators:
        - Root contains context/, artifacts/, reports/, tracking/
        - Root contains 00-{feature-name}.md
        - No NN-{name}/ child plan subfolders
        """
        # Check for epic structure
        master_plans = list(plan_path.glob("00-*.md"))
        child_dirs = [d for d in plan_path.iterdir() 
                      if d.is_dir() and re.match(r'^\d{2}[A-Z]?-', d.name)]
        
        # Epic: Multiple child plan directories
        if len(child_dirs) >= 2 and master_plans:
            return cls.EPIC
        
        # Feature: Standard subfolder structure
        if (plan_path / "context").exists() and \
           (plan_path / "tracking").exists() and \
           master_plans:
            return cls.FEATURE
        
        raise ValueError(
            f"Cannot detect planner mode for {plan_path}. "
            f"Missing required structure for both EPIC and FEATURE modes."
        )


class PlanStatus(Enum):
    """Plan execution status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETE = "complete"
    FAILED = "failed"
    
    @property
    def emoji(self) -> str:
        """Get emoji representation."""
        return {
            self.NOT_STARTED: "⏳",
            self.IN_PROGRESS: "🔄",
            self.BLOCKED: "🔒",
            self.COMPLETE: "✅",
            self.FAILED: "❌"
        }[self]
```

### 2. Epic Plan Model

```python
@dataclass
class EpicPlan:
    """
    Epic plan coordinating multiple feature plans.
    
    Represents the top-level strategic initiative (e.g., CORTEX-5.0)
    that contains multiple child feature plans with dependencies.
    """
    # Identity
    plan_id: str  # e.g., "cortex-v5-gap-remediation"
    name: str     # e.g., "CORTEX v5 Gap Remediation & Completion"
    order: Optional[str] = None  # For nested epics (rare)
    
    # File paths
    root_path: Path
    master_plan_path: Path
    tracking_path: Path
    viewer_path: Path
    
    # Child plans
    child_plans: List['FeaturePlan'] = field(default_factory=list)
    
    # Progress
    overall_progress: float = 0.0  # 0-100%
    total_plans: int = 0
    completed_plans: int = 0
    total_phases: int = 0
    completed_phases: int = 0
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    estimated_days: int = 0
    status: PlanStatus = PlanStatus.NOT_STARTED
    
    # Dependencies
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    
    def update_progress(self) -> None:
        """
        Recalculate overall progress from child plans.
        
        Epic progress = weighted average of child plan progress
        """
        if not self.child_plans:
            return
        
        total_progress = sum(plan.progress for plan in self.child_plans)
        self.overall_progress = total_progress / len(self.child_plans)
        
        self.completed_plans = sum(
            1 for plan in self.child_plans 
            if plan.status == PlanStatus.COMPLETE
        )
        
        self.completed_phases = sum(
            plan.completed_phases for plan in self.child_plans
        )
        
        self.last_updated = datetime.now()
    
    def get_ready_child_plans(self) -> List['FeaturePlan']:
        """
        Get child plans ready to execute (dependencies met).
        """
        ready = []
        for plan in self.child_plans:
            if plan.status in [PlanStatus.NOT_STARTED, PlanStatus.IN_PROGRESS]:
                # Check if dependencies are met
                deps = self.dependency_graph.get(plan.plan_id, [])
                deps_met = all(
                    self.get_child_by_id(dep_id).status == PlanStatus.COMPLETE
                    for dep_id in deps
                )
                if deps_met:
                    ready.append(plan)
        return ready
    
    def get_child_by_id(self, plan_id: str) -> Optional['FeaturePlan']:
        """Get child plan by ID."""
        for plan in self.child_plans:
            if plan.plan_id == plan_id:
                return plan
        return None
```

### 3. Feature Plan Model

```python
@dataclass
class FeaturePlan:
    """
    Single feature plan with phases.
    
    Can be standalone or part of an epic.
    """
    # Identity
    plan_id: str    # e.g., "test-coverage-sprint"
    name: str       # e.g., "Test Coverage Sprint"
    order: str      # e.g., "00", "01", "02" (for epic child plans)
    
    # File paths
    root_path: Path
    master_plan_path: Path
    tracking_path: Path
    viewer_path: Path
    folder: str  # e.g., "00-test-coverage-sprint/"
    
    # Phases
    phases: List['PlanPhase'] = field(default_factory=list)
    total_phases: int = 0
    completed_phases: int = 0
    
    # Progress
    progress: float = 0.0  # 0-100%
    status: PlanStatus = PlanStatus.NOT_STARTED
    
    # Metadata
    duration: str = "TBD"  # e.g., "2-3w", "1w", "3-4d"
    priority: str = "Medium"
    created_date: datetime = field(default_factory=datetime.now)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Epic relationship
    parent_epic: Optional[str] = None  # Epic plan_id
    dependencies: List[str] = field(default_factory=list)  # Other plan IDs
    dependency_rule: Optional[str] = None  # e.g., "Test Coverage ≥50%"
    
    def update_progress(self) -> None:
        """Recalculate progress from phases."""
        if not self.phases:
            return
        
        total_progress = sum(phase.progress for phase in self.phases)
        self.progress = total_progress / len(self.phases)
        
        self.completed_phases = sum(
            1 for phase in self.phases 
            if phase.status == PlanStatus.COMPLETE
        )
        
        # Auto-update status
        if self.completed_phases == self.total_phases:
            self.status = PlanStatus.COMPLETE
            if not self.end_date:
                self.end_date = datetime.now()
        elif self.completed_phases > 0:
            self.status = PlanStatus.IN_PROGRESS
            if not self.start_date:
                self.start_date = datetime.now()


@dataclass
class PlanPhase:
    """Individual phase within a feature plan."""
    number: int
    name: str
    description: str
    progress: float = 0.0
    status: PlanStatus = PlanStatus.NOT_STARTED
    tasks: List['PlanTask'] = field(default_factory=list)
    estimated_duration_hours: float = 0.0
    actual_duration_hours: Optional[float] = None


@dataclass
class PlanTask:
    """Individual task within a phase."""
    id: str
    description: str
    status: PlanStatus = PlanStatus.NOT_STARTED
    assignee: Optional[str] = None
    completed_date: Optional[datetime] = None
```

---

## 📋 JSON Schemas

### 1. Epic Progress Tracker

**File:** `tracking/epic-progress-tracker.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["schema_version", "plan_type", "plan_id", "child_plans"],
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
      "description": "Unique epic identifier (kebab-case)"
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
    "total_plans": {
      "type": "integer",
      "minimum": 0
    },
    "completed_plans": {
      "type": "integer",
      "minimum": 0
    },
    "total_phases": {
      "type": "integer"
    },
    "completed_phases": {
      "type": "integer"
    },
    "estimated_days": {
      "type": "integer"
    },
    "status": {
      "type": "string",
      "enum": ["not_started", "in_progress", "blocked", "complete", "failed"]
    },
    "child_plans": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["order", "id", "name", "folder"],
        "properties": {
          "order": {
            "type": "string",
            "pattern": "^\\d{2}[A-Z]?$"
          },
          "id": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "folder": {
            "type": "string"
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
            "type": "string"
          },
          "status": {
            "type": "string",
            "enum": ["not_started", "in_progress", "blocked", "complete", "failed"]
          },
          "status_emoji": {
            "type": "string"
          },
          "dependencies": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "dependency_rule": {
            "type": "string"
          },
          "viewer_url": {
            "type": "string"
          }
        }
      }
    },
    "dependency_graph": {
      "type": "object",
      "additionalProperties": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    }
  }
}
```

### 2. Feature Progress Tracker

**File:** `tracking/progress-tracker.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["schema_version", "plan_type", "plan_id", "phases"],
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
    "order": {
      "type": "string",
      "pattern": "^\\d{2}[A-Z]?$"
    },
    "progress": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "status": {
      "type": "string",
      "enum": ["not_started", "in_progress", "blocked", "complete", "failed"]
    },
    "parent_epic": {
      "type": ["string", "null"]
    },
    "phases": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["number", "name", "progress", "status"],
        "properties": {
          "number": {
            "type": "integer"
          },
          "name": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "progress": {
            "type": "number",
            "minimum": 0,
            "maximum": 100
          },
          "status": {
            "type": "string"
          },
          "tasks": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "id": {
                  "type": "string"
                },
                "description": {
                  "type": "string"
                },
                "status": {
                  "type": "string"
                },
                "completed_date": {
                  "type": ["string", "null"],
                  "format": "date-time"
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## 🎨 HTML Viewer Architecture

### Glassmorphism Design Compliance

**Standard:** `cortex-brain/documents/standards/glassmorphism-design-standard.md`

**Tier:** T1 (Subtle Animation)  
**Animation Budget:** Transitions only (0.2-0.3s), shimmer effect on progress bars

**Required Elements:**
1. ✅ Glass panels with `backdrop-filter: blur(20px)`
2. ✅ Subtle borders with `rgba(255, 255, 255, 0.1)`
3. ✅ Blue-purple gradient progress bars (`#00d4ff → #a855f7`)
4. ✅ Tetris-style animated progress fills
5. ✅ Responsive typography with `clamp()` and `cqi` units
6. ✅ WCAG AA contrast ratios (4.5:1 minimum)
7. ✅ Mobile-friendly (A+ grade on tools)

### Epic Viewer Component Map

```
Epic Viewer HTML
├── Header Section
│   ├── Epic Title (gradient text)
│   └── Epic Subtitle
│
├── Stats Grid (4 cards)
│   ├── Overall Progress %
│   ├── Plans Complete (N/M)
│   ├── Phases Complete (N/M)
│   └── Estimated Duration
│
├── Overall Progress Bar
│   ├── Animated fill with gradient
│   └── Shimmer effect overlay
│
├── Child Plans Grid
│   ├── Child Plan Cards (responsive grid)
│   │   ├── Order + Name header
│   │   ├── Status emoji
│   │   ├── Progress bar (mini)
│   │   ├── Phase count + duration
│   │   └── Dependency tags
│   └── Click → opens child viewer
│
└── Auto-Refresh Indicator
    └── Pulse animation, 5s interval
```

### Feature Viewer Component Map

```
Feature Viewer HTML
├── Header Section
│   ├── Feature Title
│   └── Order + Duration + Status
│
├── Stats Grid (3 cards)
│   ├── Progress %
│   ├── Phases Complete
│   └── Time Elapsed/Remaining
│
├── Overall Progress Bar
│
├── Phases List
│   ├── Phase Cards
│   │   ├── Phase number + name
│   │   ├── Progress bar
│   │   ├── Task checklist
│   │   └── Expand/collapse
│
└── Artifacts & Reports Links
    ├── Context files
    ├── Generated artifacts
    └── Progress reports
```

---

## 🔧 Implementation Functions

### Planner Mode Detection

```python
# src/orchestrators/planning/detector.py

import re
from pathlib import Path
from .models import PlannerMode

class PlannerModeDetector:
    """Detect planner mode from folder structure."""
    
    @staticmethod
    def detect(plan_path: Path) -> PlannerMode:
        """
        Detect planner mode (EPIC vs FEATURE).
        
        Args:
            plan_path: Root path to plan folder
            
        Returns:
            PlannerMode.EPIC or PlannerMode.FEATURE
            
        Raises:
            ValueError: If structure doesn't match either mode
        """
        # Find master plan files
        master_plans = list(plan_path.glob("00-*.md"))
        
        # Find child plan directories (NN-{name}/ pattern)
        child_dirs = [
            d for d in plan_path.iterdir()
            if d.is_dir() and re.match(r'^\d{2}[A-Z]?-', d.name)
        ]
        
        # Epic detection
        if len(child_dirs) >= 2 and master_plans:
            # Validate each child has a master plan
            valid_children = sum(
                1 for d in child_dirs
                if list(d.glob("00-*.md"))
            )
            
            if valid_children >= 2:
                return PlannerMode.EPIC
        
        # Feature detection
        required_folders = ["context", "artifacts", "reports", "tracking"]
        has_structure = all((plan_path / folder).exists() for folder in required_folders)
        
        if has_structure and master_plans and not child_dirs:
            return PlannerMode.FEATURE
        
        # Neither matched
        raise ValueError(
            f"Cannot detect planner mode for {plan_path}\n"
            f"Epic requirements: 2+ child dirs with plans\n"
            f"Feature requirements: context/, artifacts/, reports/, tracking/ + no child plans"
        )
    
    @staticmethod
    def validate_epic_structure(plan_path: Path) -> bool:
        """Validate epic folder structure."""
        try:
            # Check for tracking infrastructure
            tracking = plan_path / "tracking"
            required_files = [
                tracking / "epic-progress-tracker.json",
                tracking / "child-plan-registry.json",
                tracking / "dependency-graph.json"
            ]
            
            return all(f.exists() for f in required_files)
        except Exception:
            return False
    
    @staticmethod
    def validate_feature_structure(plan_path: Path) -> bool:
        """Validate feature folder structure."""
        try:
            tracking = plan_path / "tracking" / "progress-tracker.json"
            return tracking.exists()
        except Exception:
            return False
```

---

## 📦 Deliverables Checklist

### Phase 00 Completion Criteria

- [x] **Data Models Defined** - Python dataclasses for Epic/Feature/Phase/Task
- [x] **JSON Schemas Created** - Epic and Feature progress tracker schemas
- [x] **HTML Architecture Designed** - Component maps and glassmorphism compliance
- [x] **Detection Logic Specified** - PlannerModeDetector with validation
- [x] **Integration Points Mapped** - Planning Orchestrator, ADO, CORTEX-LENS
- [x] **Documentation Complete** - This architecture spec document

### Phase 00 Sign-Off

**Status:** ✅ COMPLETE  
**Progress:** 100%  
**Duration:** 2 hours  
**Next Phase:** Phase 01 - Epic Planner Implementation

---

## 🎯 Next Phase Preview

**Phase 01: Epic Planner Implementation**

**Tasks:**
1. Implement `EpicPlanner` class with load/save/update methods
2. Create epic tracker JSON loader/parser
3. Build dependency resolution algorithm
4. Implement progress aggregation from child plans
5. Add tests for epic orchestration logic

**Estimated Duration:** 3 days

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
