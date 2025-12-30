# CORTEX Orchestrator Visualization Inventory

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Created:** December 26, 2025  
**Purpose:** Master inventory for orchestrator visualization enhancement project

---

## 📊 Orchestrator Categories

### 🎯 Planning Orchestrators (4)
Focus: Feature planning, work breakdown, TDD integration

1. **Planning System Orchestrator**
   - **File:** `src/orchestrators/planning/planning_orchestrator.py`
   - **Manifest:** `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`
   - **Complexity:** HIGH (4-tier routing, 13+ phases, manifest compliance)
   - **Key Features:** Tiered routing, complexity detection, TDD auto-inclusion, Phase 10 modularization
   - **Visualizations Needed:**
     - Mermaid: 4-tier routing decision tree (skeleton → conditional → incremental → granular)
     - D3.js: Interactive phase tree (expandable phases with DoR/DoD gates)
     - Mermaid: Manifest inheritance diagram (Planning System → ADO → child orchestrators)
     - D3.js: Token optimization visualization (95% reduction, hierarchical structure)

2. **TDD Orchestrator**
   - **File:** `src/orchestrators/tdd/tdd_orchestrator.py`
   - **Manifest:** `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`
   - **Complexity:** HIGH (RED→GREEN→REFACTOR, 11+ languages, quality scoring)
   - **Key Features:** Adaptive tech discovery, clean code enforcement (SOLID/DRY/KISS/YAGNI), per-phase rollback
   - **Visualizations Needed:**
     - Mermaid: RED→GREEN→REFACTOR cycle with validation gates
     - D3.js: Test coverage visualization per layer (unit, integration, e2e)
     - Mermaid: Technology detection flowchart (11+ languages)
     - D3.js: Quality scoring dashboard (0-10 scale, violation categories)

3. **ADO Planning Orchestrator**
   - **File:** `src/orchestrators/ado/ado_orchestrator.py`
   - **Manifest:** `cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml`
   - **Complexity:** MEDIUM (inherits Planning System, ADO formatting)
   - **Key Features:** Story/Feature/Task creation, completion summaries, manifest inheritance
   - **Visualizations Needed:**
     - Mermaid: Inheritance diagram (Planning System → ADO manifest)
     - D3.js: Work item hierarchy (Feature → Story → Task)
     - Mermaid: ADO formatting pipeline (planning → ADO format → output)
     - D3.js: Acceptance criteria flow with DoR/DoD gates

4. **Pre-Flight Orchestrator**
   - **File:** `src/orchestrators/planning/pre_flight_orchestrator.py`
   - **Complexity:** LOW (validation and readiness checks)
   - **Key Features:** Pre-planning discovery, holistic code search, complexity estimation
   - **Visualizations Needed:**
     - Mermaid: Pre-flight validation workflow
     - D3.js: Complexity estimation heatmap

---

### ⚙️ Execution Orchestrators (2)

Focus: Code transformation, deployment, migration

5. **Code Sanitization Orchestrator**
   - **File:** `src/orchestrators/sanitization/sanitization_orchestrator.py`
   - **Manifest:** `cortex-brain/manifests/orchestrators/code-sanitization-manifest.yaml`
   - **Complexity:** HIGH (5-phase workflow, domain transformation)
   - **Key Features:** Company data removal, domain terminology transformation, build/test validation
   - **Visualizations Needed:**
     - Mermaid: 5-phase workflow (Analyze → Mapping → Transform → Validate → Report)
     - D3.js: Transformation heatmap (company-specific → generic mappings)
     - Mermaid: Validation flowchart (build success, test pass, references intact)
     - D3.js: Audit trail visualization (backup → transform → validate)

6. **Autonomous Execution Engine**
   - **File:** `src/orchestrators/autonomous_execution_engine.py`
   - **Complexity:** MEDIUM (plan execution automation)
   - **Key Features:** Phase-by-phase execution, error recovery, progress tracking
   - **Visualizations Needed:**
     - Mermaid: Autonomous execution workflow
     - D3.js: Execution progress timeline

---

### 🔧 System Orchestrators (5)

Focus: Maintenance, integrity, optimization

7. **System Maintenance Orchestrator**
   - **File:** `src/operations/modules/orchestration/maintenance_orchestrator.py`
   - **Complexity:** HIGH (7-phase workflow, tiered routing)
   - **Key Features:** Pre-healthcheck → align → cleanup → optimize → vacuum → refresh → post-healthcheck
   - **Visualizations Needed:**
     - Mermaid: 7-phase sequence diagram with decision gates
     - D3.js: Tiered routing tree (quick → standard → comprehensive)
     - Mermaid: Health delta visualization (baseline vs final metrics)
     - D3.js: Checkpoint strategy and rollback paths

8. **System Integrity Orchestrator**
   - **File:** `src/orchestrators/system/system_integrity_orchestrator.py`
   - **Complexity:** HIGH (8-phase auto-fix workflow)
   - **Key Features:** Comprehensive validation, auto-fix capabilities, manifest compliance
   - **Visualizations Needed:**
     - Mermaid: 8-phase validation workflow with auto-fix paths
     - D3.js: Issue severity heatmap (critical/warning/info)
     - Mermaid: Manifest compliance validation tree
     - D3.js: Auto-fix vs manual resolution decision matrix

9. **Refinement Orchestrator**
   - **File:** `src/operations/modules/orchestration/refinement_orchestrator.py`
   - **Manifest:** `cortex-brain/manifests/orchestrators/refinement-orchestrator-manifest.yaml`
   - **Complexity:** HIGH (7-phase holistic improvement)
   - **Key Features:** Discovery → SKULL Review → Documentation → Code Quality → Architecture → Performance → Validation
   - **Visualizations Needed:**
     - Mermaid: 7-phase refinement workflow with rollback safety
     - D3.js: Complexity analyzer (AST-based metrics, >30 threshold)
     - Mermaid: SKULL test optimization flowchart
     - D3.js: Validation gates and success criteria

10. **Cleanup Orchestrator**
    - **File:** `src/operations/modules/orchestration/cleanup_orchestrator.py`
    - **Manifest:** `cortex-brain/manifests/orchestrators/cleanup-rules.yaml`
    - **Complexity:** MEDIUM (file organization, reference updates)
    - **Key Features:** AST-powered cleanup, protected directories, reference tracking
    - **Visualizations Needed:**
      - Mermaid: File organization workflow (detect → categorize → move → validate)
      - D3.js: Protected directories tree visualization
      - Mermaid: Reference update flowchart (AST analysis → update → verify)
      - D3.js: Cleanup impact assessment (files moved, space freed)

11. **Git Checkpoint Orchestrator**
    - **File:** `src/orchestrators/git_checkpoint_orchestrator.py`
    - **Manifest:** `cortex-brain/manifests/orchestrators/git-checkpoint-rules.yaml`
    - **Complexity:** MEDIUM (checkpoint creation, rollback management)
    - **Key Features:** Phase milestone tracking, rollback points, branch protection
    - **Visualizations Needed:**
      - Mermaid: Checkpoint creation workflow
      - D3.js: Commit timeline (phase milestones, rollback points)
      - Mermaid: Branch protection rules visualization
      - D3.js: Rollback decision tree with impact analysis

---

### 📊 Analysis Orchestrators (3)

Focus: Code review, metrics, insights

12. **Architectural Review Orchestrator**
    - **File:** `src/operations/modules/architectural/review_orchestrator.py`
    - **Complexity:** MEDIUM (6-phase analysis)
    - **Key Features:** 0-100 scoring, git protection, compliance analysis
    - **Visualizations Needed:**
      - Mermaid: 6-phase analysis workflow
      - D3.js: Scoring dashboard (0-100 scale, category breakdown)
      - Mermaid: Git protection flowchart
      - D3.js: Critical issues and recommendations visualization

13. **CORTEX Lens v3 Orchestrator**
    - **File:** `src/cortex_lens/orchestrator.py`
    - **Manifest:** `cortex-brain/manifests/orchestrators/cortex-lens-v3-manifest.yaml`
    - **Complexity:** HIGH (narrative generation, pattern detection)
    - **Key Features:** Story weaving, business value extraction, insight visualization
    - **Visualizations Needed:**
      - Mermaid: Narrative generation workflow
      - D3.js: Insight visualization (pattern detection, hotspot analysis)
      - Mermaid: Learning module integration diagram
      - D3.js: Story element relationship graph

14. **Intelligent Dashboard Orchestrator**
    - **Manifest:** `cortex-brain/manifests/orchestrators/intelligent-dashboard-manifest.yaml`
    - **Complexity:** MEDIUM (data collection and aggregation)
    - **Key Features:** Metrics collection, live monitoring, alert triggers
    - **Visualizations Needed:**
      - Mermaid: Data collection workflow (metrics → aggregation → analysis → visualization)
      - D3.js: Live metrics dashboard mockup
      - Mermaid: Collector orchestration diagram
      - D3.js: Alert trigger and threshold visualization

---

### 🔍 Debug & Recovery Orchestrators (2)

Focus: Debugging, rollback, error recovery

15. **Debug Orchestrator**
    - **Manifest:** `cortex-brain/manifests/orchestrators/debug-orchestrator-manifest.yaml`
    - **Complexity:** MEDIUM (symptom analysis → root cause → fix)
    - **Key Features:** Context capture, learning integration, validation
    - **Visualizations Needed:**
      - Mermaid: Debugging workflow (symptom → root cause → fix strategy → validation)
      - D3.js: Error trace visualization with stack analysis
      - Mermaid: Rollback decision tree
      - D3.js: Context capture and learning integration diagram

16. **Rollback Orchestrator**
    - **File:** `src/orchestrators/rollback_orchestrator.py`
    - **Complexity:** MEDIUM (checkpoint restoration)
    - **Key Features:** Safe rollback, state restoration, validation
    - **Visualizations Needed:**
      - Mermaid: Rollback workflow with validation gates
      - D3.js: Checkpoint selection tree
      - D3.js: State comparison (before/after rollback)

---

## 📈 Visualization Requirements Summary

### Mermaid Diagrams (32 total)
- Workflow sequence diagrams: 16
- Decision trees/flowcharts: 8
- Integration/relationship diagrams: 5
- Inheritance hierarchies: 3

### D3.js Interactive Diagrams (32 total)
- Phase/workflow visualizations: 8
- Heatmaps/dashboards: 7
- Tree structures: 6
- Timeline/progress: 5
- Scoring/metrics: 4
- Network graphs: 2

### Common Elements
- Interactive tooltips (all D3.js diagrams)
- Zoom/pan capabilities (complex diagrams)
- Drill-down exploration (hierarchical data)
- Responsive design (mobile-friendly)
- Legend/key (color-coded categories)
- Export capabilities (PNG/SVG)

---

## 🎨 Design Standards

### Color Palette
- **Planning:** Blue tones (#2196F3, #1976D2, #0D47A1)
- **Execution:** Green tones (#4CAF50, #388E3C, #1B5E20)
- **System:** Orange tones (#FF9800, #F57C00, #E65100)
- **Analysis:** Purple tones (#9C27B0, #7B1FA2, #4A148C)
- **Debug:** Red tones (#F44336, #D32F2F, #B71C1C)
- **Success:** Emerald (#10B981)
- **Warning:** Amber (#F59E0B)
- **Error:** Crimson (#DC2626)

### Typography
- **Headers:** Inter, 600 weight
- **Body:** Inter, 400 weight
- **Code:** Fira Code, 400 weight

### Layout
- Container max-width: 1400px
- Diagram min-height: 500px
- Responsive breakpoints: 1200px, 768px, 480px

---

## 🚀 Implementation Priority

**Phase 1: Core Orchestrators (1-2 weeks)**
1. Planning System (flagship)
2. TDD Orchestrator (most complex)
3. Maintenance Orchestrator (7-phase workflow)

**Phase 2: Execution & System (1 week)**
4. Code Sanitization
5. System Integrity
6. Refinement

**Phase 3: Analysis & Debug (1 week)**
7. Architectural Review
8. CORTEX Lens
9. Debug Orchestrator

**Phase 4: Supporting & Index (3-4 days)**
10. Remaining orchestrators
11. Master index page
12. Story viewer integration

---

## 📁 File Structure

```
docs/
├── technical/
│   ├── orchestrators/
│   │   ├── index.html                          # Master index with D3.js map
│   │   ├── planning-system.html                # Phase 1
│   │   ├── tdd-orchestrator.html               # Phase 1
│   │   ├── maintenance-orchestrator.html       # Phase 1
│   │   ├── code-sanitization.html              # Phase 2
│   │   ├── system-integrity.html               # Phase 2
│   │   ├── refinement-orchestrator.html        # Phase 2
│   │   ├── architectural-review.html           # Phase 3
│   │   ├── cortex-lens.html                    # Phase 3
│   │   ├── debug-orchestrator.html             # Phase 3
│   │   ├── ado-planning.html                   # Phase 4
│   │   ├── git-checkpoint.html                 # Phase 4
│   │   ├── cleanup-orchestrator.html           # Phase 4
│   │   ├── intelligent-dashboard.html          # Phase 4
│   │   ├── rollback-orchestrator.html          # Phase 4
│   │   ├── autonomous-execution.html           # Phase 4
│   │   └── pre-flight-orchestrator.html        # Phase 4
│   ├── assets/
│   │   ├── css/
│   │   │   ├── orchestrator-viz.css            # Common styles
│   │   │   └── mermaid-theme.css               # Mermaid customization
│   │   └── js/
│   │       ├── orchestrator-viz.js             # D3.js utilities
│   │       └── diagram-interactions.js         # Common interactions
│   └── index.html                              # Technical docs landing page
└── story/
    └── story-viewer.js                         # Add orchestrator links
```

---

## 🔗 Related Documents

- Planning System Manifest: `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`
- TDD Orchestrator Manifest: `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`
- Maintenance Architecture: `cortex-brain/documents/archive/SYSTEM-MAINTENANCE-ORCHESTRATOR-ARCHITECTURE.md`
- Code Sanitization Guide: `cortex-brain/CODE-SANITIZATION-QUICK-REF.md`
- Orchestrator Base: `src/orchestrators/base/base_orchestrator.py`

---

**Next Step:** Begin Phase 1 with Planning System Orchestrator visualization (highest complexity, flagship feature)
