# HTML View Orchestrator Integration Guide

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION | **Type:** GUIDED Orchestrator  
**Author:** Asif Hussain | **Created:** 2026-01-04  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Overview

The **HTML View Orchestrator** is an intelligent HTML/CSS development system integrated into CORTEX's master orchestrator toolset. It enforces the glassmorphism design system, provides Vision API integration for visual analysis, and maintains persistent learning through the Tier 2 knowledge graph.

### Key Features

- **Glassmorphism Design System**: Automatic enforcement of CORTEX v4.0 glassmorphism standards
- **Vision API Integration**: Automatic screenshot analysis when images are attached
- **Tier 2 Learning System**: Persistent pattern storage in `cortex-brain/tier2/html-view-requirements.yaml`
- **WCAG AA Compliance**: Automated accessibility validation (contrast, font size, touch targets)
- **Mermaid Diagram Generation**: Intelligent diagram type selection (mindmap, flowchart, sequence)
- **Preview-First Workflow**: Safe development in `cortex-lens-output/preview-approval/`
- **Component Pattern Library**: Reusable components (tier-card, stat-badge, example-tile, etc.)

---

## 🏗️ Architecture

### Integration Points

```
Master Orchestrator
  ├── Pattern Router (routing_rules)
  │   └── ^(build html view|fix visual issues|standardize .+ to glassmorphism).*$
  │       → html_view_orchestrator (priority: 58)
  │
  ├── Orchestrator Registry (mcp-server.yaml)
  │   └── HTMLViewOrchestrator
  │       ├── Module: src.orchestrators.html_view.html_view_orchestrator
  │       ├── Config: cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml
  │       └── Type: GUIDED
  │
  └── Brain Integration
      ├── Tier 0: SKULL rules (HOLISTIC_DISCOVERY, REFACTOR_CLEANUP)
      ├── Tier 1: PlanningStateDB (state tracking)
      ├── Tier 2: html-view-requirements.yaml (learning system)
      └── Tier 3: Workspace HTML context
```

### File Structure

```
src/orchestrators/html_view/
  ├── __init__.py                     # Module exports
  └── html_view_orchestrator.py       # Main orchestrator implementation

cortex-brain/
  ├── config/
  │   ├── master-orchestrator.yaml    # Routing rules (priority: 58)
  │   └── mcp-server.yaml             # Registry entry
  ├── manifests/orchestrators/
  │   └── html-view-orchestrator-manifest.yaml  # Config (513 lines)
  └── tier2/
      └── html-view-requirements.yaml # Learning system storage

tests/orchestrators/html_view/
  ├── __init__.py
  └── test_html_view_orchestrator.py  # Comprehensive test suite
```

---

## 🚀 Usage

### Command Patterns

The orchestrator responds to these natural language patterns:

| Pattern | Mode | Example |
|---------|------|---------|
| `build html view for X` | `full_workflow` | `build html view for four-tier brain` |
| `fix visual issues in X` | `fix_visual_issues` | `fix visual issues in tier details tab` |
| `standardize X to glassmorphism` | `standardize_glassmorphism` | `standardize dashboard to glassmorphism` |
| `add diagram to X showing Y` | `add_diagram` | `add diagram to Tier 0 showing SKULL rules` |
| `make X responsive` | `make_responsive` | `make tier cards responsive` |

### Example: Full Workflow

```python
from src.orchestrators.html_view import HTMLViewOrchestrator

# Initialize
orchestrator = HTMLViewOrchestrator(
    config_path="cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml",
    state_db=planning_state_db
)

# Execute
result = orchestrator.execute(
    target_file="docs/orchestrators/planning-v5.html",
    mode="full_workflow",
    screenshot_paths=["path/to/before.png"]
)

# Check result
if result.status == OrchestratorStatus.COMPLETED:
    print(f"Enhanced: {result.metadata['enhanced_html_path']}")
    print(f"Issues fixed: {result.metadata['issues_fixed']}")
    print(f"Patterns captured: {result.metadata['patterns_captured']}")
```

### Example: Master Orchestrator Integration

```python
from src.orchestrators.master_orchestrator import MasterOrchestrator

master = MasterOrchestrator(
    config_path='cortex-brain/config/master-orchestrator.yaml',
    registry=orchestrator_registry,
    state_db=planning_state_db
)

# Route automatically via pattern matching
result = master.handle_request(
    user_input="build html view for four-tier brain",
    context={'screenshot_paths': ['before.png']}
)
```

---

## 📋 Workflow Phases

### Mode: `full_workflow` (6 phases)

1. **DISCOVERY** - Analyze existing HTML structure
   - Read HTML file
   - Vision API analysis (if screenshots provided)
   - Load learning system (past requirements)
   - Identify component types used
   - Extract design system gaps

2. **PLANNING** - Prioritize changes
   - Prioritize issues (visual impact × effort)
   - Identify reusable components
   - Plan diagram insertions
   - Check WCAG compliance needs

3. **CSS_ENHANCEMENT** - Update stylesheets
   - Increase margins/padding
   - Add gradient backgrounds
   - Create stat badge styles
   - Add diagram container styles
   - Enhance hover effects

4. **HTML_RESTRUCTURING** - Transform content structure
   - Add stat badges to headers
   - Insert Mermaid diagrams
   - Convert feature lists to grids
   - Elevate storage paths (code blocks)
   - Add tooltips to technical terms

5. **VALIDATION** - WCAG AA and responsive testing
   - Contrast ratio checks (≥4.5:1)
   - Font size validation (≥16px)
   - Touch target checks (≥44px)
   - Responsive breakpoints (320px, 768px, 1920px)

6. **LEARNING_CAPTURE** - Save patterns to Tier 2
   - Extract successful patterns
   - Document spacing decisions
   - Save component recipes
   - Record WCAG fixes
   - Update anti-patterns

### Mode: `fix_visual_issues` (4 phases)

Executes: DISCOVERY → CSS_ENHANCEMENT → HTML_RESTRUCTURING → LEARNING_CAPTURE

### Mode: `standardize_glassmorphism` (2 phases)

Executes: CSS_ENHANCEMENT → LEARNING_CAPTURE

---

## 🧠 Brain Integration

### Tier 0: SKULL Rules Enforcement

The orchestrator enforces these brain protection rules:

- **HOLISTIC_DISCOVERY**: Search for existing views before creating new ones
- **REFACTOR_CLEANUP**: Remove inline styles when extracting to CSS
- **TDD_ENFORCEMENT**: Write visual regression tests (optional)
- **GIT_ISOLATION**: Never commit to user repos

### Tier 1: State Tracking

Uses `PlanningStateDB` for persistent execution state:

```python
# Plan creation
plan_id = state_db.create_plan(
    feature_name=f"HTML View: {target_file.name}",
    metadata={
        'orchestrator': 'html_view_orchestrator',
        'target_file': str(target_file),
        'mode': mode,
        'brain_tier': 'tier2_learning_enabled'
    }
)

# State updates
state_db.save_phase_result(plan_id, phase_result)
state_db.complete_plan(plan_id, status='completed')
```

### Tier 2: Learning System

Persistent pattern storage in `cortex-brain/tier2/html-view-requirements.yaml`:

```yaml
visual_patterns:
  patterns:
    - id: "VP001"
      name: "Examples Tab Transformation"
      context: "four-tier-brain-preview.html"
      problem: "Plain <ol> lists were boring"
      solution: "Interactive tile grid with tier-flow visualization"
      visual_impact: "high"
      reusability: "high"

spacing_rules:
  rules:
    - id: "SR001"
      name: "Card Bottom Margin Standard"
      value: "3rem"
      context: "Tier card spacing"

component_recipes:
  recipes:
    - id: "CR001"
      name: "Interactive Tile"
      structure: "hover + lift + glow"
```

**Loading and Saving:**

```python
# Load on initialization
orchestrator._load_learning_system()

# Save after pattern capture
orchestrator._save_learning_system()
```

### Tier 3: Workspace Context

Reads HTML files from workspace:

```python
with open(self.target_file, 'r', encoding='utf-8') as f:
    html_content = f.read()
```

---

## 🎨 Design System Integration

### Glassmorphism v4.0 Standards

```yaml
design_system:
  name: "CORTEX Glassmorphism v4.0"
  
  core_principles:
    - "Glassmorphism: rgba backgrounds + backdrop-filter blur"
    - "Tier-coded colors: T0=#ff6b6b, T1=#ffd700, T2=#00d4ff, T3=#00ff88"
    - "WCAG AA: 4.5:1 contrast, 16-18px fonts, 44px touch targets"
    - "Responsive: clamp() typography, 320px-2560px breakpoints"
  
  typography:
    font_family: "Inter, system-ui, sans-serif"
    base_size: "clamp(16px, 2vw, 18px)"
    line_height: 1.7
  
  effects:
    blur: "blur(20px)"
    border_radius: "12px"
    transition: "all 0.3s ease"
```

### Component Library

| Component | Class | Use Case |
|-----------|-------|----------|
| **Tier Card** | `.tier-card` | Individual tier description panels |
| **Stat Badge** | `.stat-badge` | Inline metrics highlighting |
| **Example Tile** | `.example-tile` | Interactive example showcase cards |
| **Diagram Container** | `.diagram-container` | Mermaid.js diagram embedding |
| **Feature List** | `.feature-list` | 2-column responsive grid |

---

## 🧪 Testing

### Running Tests

```powershell
# Run all HTML view orchestrator tests
pytest tests/orchestrators/html_view/ -v

# Run with coverage
pytest tests/orchestrators/html_view/ --cov=src.orchestrators.html_view --cov-report=html

# Run specific test class
pytest tests/orchestrators/html_view/test_html_view_orchestrator.py::TestHTMLViewOrchestrator -v
```

### Test Coverage

The test suite covers:

- ✅ Orchestrator initialization
- ✅ Learning system loading/saving
- ✅ HTML issue analysis
- ✅ Component inventory
- ✅ Design gap identification
- ✅ All execution modes (full_workflow, fix_visual_issues, etc.)
- ✅ Error handling
- ✅ Command pattern detection
- ✅ Brain tier integrations (Tier 0-3)

---

## 📊 Metrics and Monitoring

### Execution Metadata

```python
result.metadata = {
    'enhanced_html_path': str(target_file),
    'issues_fixed': len(issues_identified),
    'patterns_captured': len(patterns_captured),
    'wcag_compliant': wcag_results.get('compliant', False),
    'responsive_validated': responsive_results.get('validated', False)
}
```

### Logging

```python
self.logger.info(
    f"Discovery complete: {len(self.issues_identified)} issues, "
    f"{len(self.component_inventory)} components, "
    f"{len(self.design_gaps)} design gaps"
)
```

---

## 🔄 Vision API Integration

### Auto-Detection

When images are attached to requests, Vision API automatically analyzes them:

```python
screenshot_paths = context.get('screenshot_paths', [])

result = orchestrator.execute(
    target_file="docs/page.html",
    mode="fix_visual_issues",
    screenshot_paths=screenshot_paths  # Auto-analyzed
)
```

### Analysis Prompts

The orchestrator uses these Vision API prompts (from manifest):

1. **Visual Issues Analysis**: Text density, missing visual elements, spacing, hierarchy
2. **Component Detection**: Card types, layouts, interactive elements
3. **Before/After Comparison**: Improvements made, remaining issues, consistency

---

## ⚠️ Important Notes

### GUIDED Orchestrator

The HTML View Orchestrator is **GUIDED** (not autonomous):

- ❌ Does NOT self-execute via Python scripts
- ✅ Requires GitHub Copilot to interpret manifest and execute
- ✅ Uses GitHub Copilot's file editing tools (replace_string_in_file, multi_replace)

### Preview-First Workflow

All changes are made in preview environment first:

```yaml
workflow:
  mode: "preview_first"
  preview_location: "cortex-lens-output/preview-approval/"
  production_location: "docs/"
```

### Accessibility Enforcement

WCAG AA compliance is mandatory:

- Minimum contrast ratio: 4.5:1
- Minimum font size: 16px
- Minimum touch target: 44px
- Line height: ≥1.5
- Line length: ≤80ch

---

## 📝 Example: Command Detection

```python
from src.orchestrators.html_view import detect_html_view_command

# Detect command pattern
command = detect_html_view_command("build html view for four-tier brain")

if command:
    print(f"Mode: {command['mode']}")           # 'full_workflow'
    print(f"Target: {command['target_file']}")  # 'four-tier brain'
```

---

## 🎉 Benefits

1. **Consistency**: All HTML views follow glassmorphism v4.0 standards
2. **Quality**: Automatic WCAG AA compliance validation
3. **Learning**: Patterns are reused across views (Tier 2)
4. **Efficiency**: Preview-first workflow prevents production breakage
5. **Visibility**: Vision API catches visual issues before deployment
6. **Integration**: Seamless master orchestrator routing

---

## 📚 References

- **Manifest**: `cortex-brain/manifests/orchestrators/html-view-orchestrator-manifest.yaml`
- **Routing**: `cortex-brain/config/master-orchestrator.yaml` (lines 120-143)
- **Registry**: `cortex-brain/config/mcp-server.yaml` (lines 63-72)
- **Learning System**: `cortex-brain/tier2/html-view-requirements.yaml`
- **Design Standard**: `cortex-brain/documents/glassmorphism-design-standard.md`

---

**Status:** ✅ Ready for production use  
**Next Steps:** 
1. Run tests to verify integration: `pytest tests/orchestrators/html_view/ -v`
2. Test routing: `build html view for test page`
3. Verify learning system updates in Tier 2
