# CORTEX Lens Mock Dashboard - Master Implementation Plan

**Author:** Asif Hussain  
**Date:** December 14, 2025  
**Version:** 1.2  
**Status:** 🚧 IN PROGRESS  

**Planning Hub:** `cortex-brain/documents/planning/cortex-lens-dashboard/`

---

## 📁 Related Documents

- **README:** `README.md` - Planning hub overview
- **Workflow Guide:** `iterative-refinement-workflow.md` - Process guide
- **Requirements Log:** `requirements-log.md` - Chronological decisions
- **Tab Sub-Plans:** `tab-refinements/*.md` - Individual tab refinement plans
- **Server Script:** `serve-dashboard.ps1` - PowerShell HTTP server  

---

## 🎯 Objective

Build a production-quality mock dashboard for CORTEX Lens by adapting the Admin Dashboard's superior styling and D3.js visualizations, with a clean architecture that allows seamless transition to live AST data.

## 🏗️ Architectural Decision

**STRATEGY: Redesign CORTEX Lens Dashboard from Scratch (Option A)**

**Rationale:**
- ✅ **Clean Architecture** - Purpose-built for single-repo AST analysis
- ✅ **Module Independence** - Self-contained in `src/cortex_lens/`
- ✅ **Simplified Scope** - 8-10 essential tabs, no admin features
- ✅ **Long-term Maintainability** - Two distinct dashboards for distinct purposes
- ✅ **AST-Optimized Design** - Tailored specifically for AST data visualization
- ✅ **Quality Extraction** - Cherry-pick best UX patterns from Admin Dashboard

**Rejected Alternative: Rename Admin Dashboard (Option B)**
- ❌ Violates module boundaries (couples Lens to admin infrastructure)
- ❌ Brings unnecessary complexity (repo selector, admin-only features)
- ❌ Bloated for single-repo use case
- ❌ Harder to maintain two use cases in one codebase

**Implementation Approach:**
Extract and adapt the best elements from Admin Dashboard (D3 visualizations, glassmorphism styling, adaptive visibility patterns) while building a fresh, purpose-built dashboard for CORTEX Lens's AST-focused workflow.

---

## 🔄 CORTEX Lens Workflow Architecture

### **Q1: Does CORTEX scan repos, build dataset, then combine with template to generate static dashboard?**

**Answer: ✅ YES - This is the correct and implemented architecture**

**Current Implementation (CORTEX Lens v1.0):**
```
Phase 1: CLASSIFY
  └─> Detect project type (Python, C#, JS, mixed)
  
Phase 2: COLLECT (AST Scan)
  └─> Execute 10 collectors to build dataset:
      • HealthCollector → System health metrics
      • ArchitectureCollector → Code structure, layers, patterns
      • APIEndpointCollector → REST/GraphQL endpoints
      • SecurityCollector → Vulnerabilities, secrets
      • ComplexityCollector → Cyclomatic complexity, maintainability
      • TechStackCollector → Dependencies, frameworks
      • DependencyCollector → Package dependencies
      • TestCoverageCollector → Test metrics
      • CommentCollector → Documentation coverage
      • (Future: 10th collector TBD)
  
Phase 3: NARRATE
  └─> Generate human-readable insights from dataset
  
Phase 4: DASHBOARD (Template + Data → Static HTML)
  └─> Combine dataset with HTML/CSS/JS template
  └─> Generate self-contained static dashboard
  └─> Output: Single HTML file or folder with assets
  
Phase 5: VALIDATE
  └─> Verify dashboard integrity, data completeness
  
Phase 6: PACKAGE
  └─> Bundle dashboard with assets for distribution
```

**Mock Dashboard Enhancement (This Plan):**
- Upgrade Phase 4 (DASHBOARD) with D3.js visualizations
- Replace current template with glassmorphism design
- Maintain same workflow: Scan → Dataset → Template → Static Output

---

### **Q2: Does CORTEX delete target folder before republishing?**

**Answer: ⚠️ SHOULD BUT CURRENTLY DOESN'T - Need to add**

**Required Implementation:**
```python
# In dashboard_builder.py or orchestrator.py
def publish_dashboard(output_path: Path):
    # Step 1: Clean target folder
    if output_path.exists():
        logger.info(f"Cleaning existing output: {output_path}")
        shutil.rmtree(output_path)
    
    # Step 2: Create fresh directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Step 3: Generate dashboard
    # ... (existing generation logic)
```

**Why Clean First:**
- ✅ Prevents stale artifacts (old CSS, JS, images)
- ✅ Ensures fresh build every time
- ✅ Avoids version confusion
- ✅ Consistent output state

**Safety:**
- Only delete if folder already exists
- Create parents if needed
- Log operation for transparency

---

### **Q3: Trigger Mechanism & Required Parameters**

**Command-Line Interface (CLI):**

```bash
# Minimum required parameters
cortex-lens analyze <REPO_PATH> --output <TARGET_FOLDER>

# Example: Basic usage
cortex-lens analyze /path/to/my-repo

# Example: Custom output location
cortex-lens analyze /path/to/my-repo --output /custom/publish/folder

# Example: With mock data (testing)
cortex-lens analyze /path/to/my-repo --mock-data

# Example: Specify template
cortex-lens analyze /path/to/my-repo --template glassmorphism
```

**Required Parameters:**
1. **`<REPO_PATH>`** - Path to repository to analyze (REQUIRED)

**Optional Parameters:**
2. **`--output <PATH>`** - Target folder for dashboard (default: `./cortex-lens-output/`)
3. **`--mock-data`** - Use mock data instead of live AST scan (testing)
4. **`--template <NAME>`** - Template to use (default: `glassmorphism`)
5. **`--clean/--no-clean`** - Clean output folder before generation (default: `--clean`)
6. **`--open`** - Auto-open dashboard in browser after generation

**Programmatic API:**
```python
from cortex_lens import LensOrchestrator

# Initialize
orchestrator = LensOrchestrator(
    repo_path="/path/to/repo",
    output_path="/publish/folder",
    clean_before_publish=True  # Delete existing output first
)

# Execute
result = orchestrator.execute()

# Result
print(f"Dashboard: {result.dashboard_path}")
print(f"Metrics: {result.metrics}")
```

---

### **Q4: User Experience (UX)**

**Simple Workflow:**
```bash
# Step 1: User runs command
$ cortex-lens analyze /projects/my-app

# Step 2: CORTEX Lens provides feedback
[CLASSIFY] Detecting project type... Python FastAPI
[COLLECT] Scanning repository... 10 collectors active
  ✓ Health: 45 files analyzed
  ✓ Architecture: 3 layers detected
  ✓ API: 23 endpoints found
  ✓ Security: 0 vulnerabilities
  ✓ Complexity: Average 4.2
  ✓ Tech Stack: 15 dependencies
  ✓ Dependencies: All up-to-date
  ✓ Test Coverage: 87%
  ✓ Comments: 65% documented
[NARRATE] Generating insights...
[DASHBOARD] Building dashboard...
  • Cleaning output folder: ./cortex-lens-output/
  • Rendering glassmorphism template
  • Integrating D3.js visualizations
  • Copying assets (CSS, JS, images)
[VALIDATE] Verifying dashboard integrity... ✓
[PACKAGE] Dashboard ready!

[OK] Dashboard published to: ./cortex-lens-output/index.html
[DASHBOARD] Open in browser: file:///path/to/cortex-lens-output/index.html
```

**Advanced Workflow:**
```bash
# With all options
$ cortex-lens analyze /projects/my-app \
    --output /publish/website/dashboard \
    --template glassmorphism \
    --clean \
    --open

[OK] Cleaning /publish/website/dashboard...
[OK] Analyzing /projects/my-app...
[OK] Dashboard published!
[OK] Opening in browser...
```

**Error Handling:**
```bash
# Invalid repo path
$ cortex-lens analyze /invalid/path
[ERROR] Repository not found: /invalid/path

# Permission denied
$ cortex-lens analyze /protected/repo --output /protected/output
[ERROR] Cannot write to output folder: Permission denied

# No code found
$ cortex-lens analyze /empty/folder
[WARNING] No source code detected. Generating empty dashboard.
```

**Output:**
```
cortex-lens-output/
├── index.html              # Main dashboard (self-contained or with assets)
├── assets/                 # Optional: If not self-contained
│   ├── css/
│   │   ├── base/
│   │   ├── layouts/
│   │   ├── components/
│   │   └── visualizations/
│   ├── js/
│   │   ├── visualizations/
│   │   │   ├── force_graph.js
│   │   │   ├── tree_map.js
│   │   │   ├── sankey.js
│   │   │   ├── heatmap.js
│   │   │   └── timeline.js
│   │   └── app.js
│   └── data/
│       └── dashboard_data.json  # Optional: Separate data file
└── README.md               # How to view the dashboard
```

**Key Principles:**
- ✅ **Self-Contained** - All assets within `src/cortex_lens/`
- ✅ **Mock→Live Ready** - Clean separation for easy data source swap
- ✅ **Visual Excellence** - Preserve Admin Dashboard's glassmorphism styling
- ✅ **Performance Optimized** - Efficient file structure for fast loading

---

## 📐 Proposed CORTEX Lens Structure

```
src/cortex_lens/
├── dashboard/                    # NEW: Dashboard system
│   ├── __init__.py
│   ├── builder.py                # Dashboard orchestrator
│   ├── templates/                # HTML templates
│   │   ├── index.html            # Main dashboard HTML
│   │   └── partials/             # Reusable components
│   ├── visualizations/           # D3.js components
│   │   ├── __init__.py
│   │   ├── force_graph.js        # D3 force-directed graph
│   │   ├── tree_map.js           # D3 tree visualization
│   │   ├── sankey.js             # D3 Sankey diagrams
│   │   ├── heatmap.js            # D3 heatmaps
│   │   └── timeline.js           # D3 timeline charts
│   ├── styles/                   # CSS (layered architecture)
│   │   ├── base/                 # Reset, variables, typography
│   │   ├── layouts/              # Grid, sidebar, containers
│   │   ├── components/           # Buttons, cards, tabs
│   │   ├── visualizations/       # D3-specific styles
│   │   └── main.css              # Entry point
│   ├── mock_data/                # Mock data layer (REMOVABLE)
│   │   ├── __init__.py
│   │   ├── loader.py             # Mock data loader
│   │   ├── schema_mapping.py    # Mock→Lens schema mapper
│   │   └── samples/              # JSON mock data
│   │       ├── health.json
│   │       ├── architecture.json
│   │       ├── tech_stack.json
│   │       ├── security.json
│   │       ├── api_endpoints.json
│   │       └── complexity.json
│   └── data_binding/             # Data source abstraction
│       ├── __init__.py
│       ├── data_source.py        # Abstract data source interface
│       ├── mock_source.py        # Mock data implementation
│       └── live_source.py        # Live AST data implementation
│
├── orchestrator.py               # EXISTING: Main Lens orchestrator
├── cli.py                        # EXISTING: CLI interface
├── collectors/                   # EXISTING: AST data collectors
├── analyzers/                    # EXISTING: Language analyzers
├── generators/                   # EXISTING: Output generators
└── ...                           # Other existing modules
```

---

## 🚀 Implementation Phases

### **Phase 0: D3 Extraction & Data Migration** (NEW - PRIORITY)

**Duration:** 3-4 hours  
**Status:** ☐ NOT STARTED

#### Objectives
1. Extract D3.js visualizations from Admin Dashboard
2. Migrate mock data from Admin Dashboard
3. Create optimal CORTEX Lens folder structure
4. Establish mock data schema mapping

#### Tasks

**Task 0.1: Inventory Admin Dashboard Assets** ✅ DISCOVERED
- Location: `cortex-brain/dashboards/ui/`
- Key files identified:
  - `index.html` (328 lines - main structure)
  - `app.js` (controller)
  - `adaptive-visibility.js` (intelligent UI adaptation)
  - `components/` (10+ tab renderers)
  - `styles/` (40+ CSS files, layered architecture)
  - Mock data: `cortex-brain/dashboards/data/repos/mock/`

**Task 0.2: Extract D3 Visualizations** ☐ TODO
- **Source:** `cortex-brain/dashboards/ui/components/`
- **Strategy:** Extract as standalone modules, not copy entire components
- **Extract:**
  - Architecture tab D3 force graphs → `force_graph.js`
  - Tech stack tree maps → `tree_map.js`
  - Security heatmaps → `heatmap.js`
  - Dependency Sankey diagrams → `sankey.js`
  - Timeline visualizations → `timeline.js`
- **Destination:** `src/cortex_lens/dashboard/visualizations/`
- **Refactor:** Remove Admin Dashboard dependencies, make standalone
- **Simplify:** Adapt to CORTEX Lens data structure, remove multi-repo logic
- **Document:** Each visualization's data requirements and API

**Task 0.3: Migrate Mock Data** ☐ TODO
- **Source:** `cortex-brain/dashboards/data/repos/mock/`
- **Inventory:** List all JSON files and their schemas
- **Transform:** Map to CORTEX Lens schema format (see `src/cortex_lens/core/schema.py`)
- **Destination:** `src/cortex_lens/dashboard/mock_data/samples/`
- **Create:** `schema_mapping.py` to document transformations

**Task 0.4: Create Folder Structure** ☐ TODO
- Create all directories listed in proposed structure
- Add `__init__.py` files for Python modules
- Create placeholder files with docstrings

**Task 0.5: Extract Glassmorphism Styles** ☐ TODO
- **Source:** `cortex-brain/dashboards/ui/styles/`
- **Extract:**
  - `base/variables.css` (CSS custom properties)
  - `components/cards.css` (glassmorphism effects)
  - `utils/animations.css` (transitions)
- **Destination:** `src/cortex_lens/dashboard/styles/`
- **Refactor:** Remove unused styles, optimize for Lens

**Task 0.5b: Extract All Inline CSS** ☐ TODO
- **Source:** `cortex-brain/dashboards/ui/index.html` and component HTML
- **Scan for:** All `<style>` tags and `style=""` attributes
- **Categorize:**
  - Component-specific → `styles/components/`
  - Layout-specific → `styles/layouts/`
  - Visualization-specific → `styles/visualizations/`
  - Utility classes → `styles/utils/`
- **Destination:** Appropriate CSS file in layered structure
- **Safety:** ✅ Static dashboards - external CSS references are safe and cacheable

**Task 0.6: Create Mock Data Loader** ☐ TODO
- File: `src/cortex_lens/dashboard/mock_data/loader.py`
- Functions:
  - `load_mock_data(data_type: str) -> Dict`
  - `validate_mock_schema(data: Dict) -> bool`
  - `list_available_mocks() -> List[str]`
- Schema validation against CORTEX Lens schema

**Task 0.7: Design Data Source Abstraction** ☐ TODO
- File: `src/cortex_lens/dashboard/data_binding/data_source.py`
- Create abstract base class:
  ```python
  class DataSource(ABC):
      @abstractmethod
      def get_health_data(self) -> Dict: pass
      
      @abstractmethod
      def get_architecture_data(self) -> Dict: pass
      
      # ... other collector methods
  ```
- Implementations:
  - `MockDataSource` - reads from mock_data/samples/
  - `LiveDataSource` - calls CORTEX Lens collectors

**Checkpoint 0:** ✅ Complete when:
- [ ] All D3 visualizations extracted and standalone
- [ ] Mock data migrated and schema-mapped
- [ ] Folder structure created with all files
- [ ] Data source abstraction working with mock data
- [ ] All inline CSS extracted to external files
- [ ] CSS layered architecture maintained
- [ ] Zero dependencies on `cortex-brain/dashboards/`

---

### **Phase 1: Admin Dashboard Analysis**

**Duration:** 2 hours  
**Status:** ☐ NOT STARTED  
**Dependencies:** Phase 0 complete

#### Objectives
1. Deep analysis of Admin Dashboard architecture
2. Component dependency mapping
3. Identify reusable patterns

#### Tasks

**Task 1.1: Component Analysis** ☐ TODO
- Analyze each tab component in `components/`
- Document data requirements per component
- Identify shared utilities

**Task 1.2: Style System Analysis** ☐ TODO
- Document CSS variable system
- Map glassmorphism implementation
- Identify animation patterns

**Task 1.3: Adaptive Visibility Study** ☐ TODO
- Analyze `adaptive-visibility.js` logic
- **Evaluate necessity:** Does CORTEX Lens need adaptive visibility?
- **Simplify if adopting:** Single-repo context vs multi-repo
- **Alternative:** Fixed tabs optimized for AST data (may be simpler)
- Plan adaptation strategy (adopt, simplify, or skip)

**Checkpoint 1:** ✅ Complete when:
- [ ] Component architecture documented
- [ ] Style system understood
- [ ] Adaptation strategy defined

---

### **Phase 2: Schema Mapping & Architecture**

**Duration:** 3 hours  
**Status:** ☐ NOT STARTED  
**Dependencies:** Phase 0, 1 complete

#### Objectives
1. Map Admin Dashboard mock data to CORTEX Lens schema
2. Design clean mock→live transition architecture
3. Create data binding layer

#### Tasks

**Task 2.1: Schema Comparison** ☐ TODO
- Admin Dashboard schema: `cortex-brain/dashboards/data/schema/`
- CORTEX Lens schema: `src/cortex_lens/core/schema.py`
- Create mapping document: `schema_mapping.md`

**Task 2.2: Data Transformer** ☐ TODO
- File: `src/cortex_lens/dashboard/mock_data/transformer.py`
- Functions to convert Admin format → Lens format
- Bidirectional transformation for testing

**Task 2.3: Data Binding Implementation** ☐ TODO
- Implement `MockDataSource` class
- Implement `LiveDataSource` class
- Create factory pattern for source selection
- Environment variable: `CORTEX_LENS_DATA_SOURCE=mock|live`

**Task 2.4: Integration Points Documentation** ☐ TODO
- Document where mock data is injected
- Document where live data will be injected
- Create "TODO: Replace with live data" markers

**Checkpoint 2:** ✅ Complete when:
- [ ] Schema mapping complete and documented
- [ ] Data source abstraction fully implemented
- [ ] Mock→live transition path clear
- [ ] All integration points documented

---

### **Phase 3: Dashboard Construction**

**Duration:** 6-8 hours  
**Status:** ☐ NOT STARTED  
**Dependencies:** Phase 0, 1, 2 complete

#### Objectives
1. Build static HTML dashboard using Admin Dashboard design
2. Integrate D3 visualizations
3. Implement tab navigation
4. Apply glassmorphism styling

**Task 3.1: HTML Template** ☐ TODO
- File: `src/cortex_lens/dashboard/templates/index.html`
- **Build from scratch** - Do NOT copy Admin Dashboard HTML
- **Inspiration:** Use Admin Dashboard structure as reference only
- **Essential tabs only** (8-10 tabs):
  1. Executive Summary
  2. Architecture Overview
  3. Code Quality
  4. Security Analysis
  5. API Endpoints
  6. Tech Stack
  7. Dependencies
  8. Test Coverage
  9. Documentation Health
  10. Recommendations
- **Remove:** Repo selector, admin controls, multi-repo features
- **CSS References:** Use relative paths to external CSS files
- **No Inline Styles:** All styling via external CSS (completed in Phase 0)
- **Static Safety:** ✅ Confirmed - external CSS works perfectly in generated HTML
**Task 3.3: Tab Components** ☐ TODO
- **Build fresh components** - Use Admin Dashboard as UX reference only
- File: `src/cortex_lens/dashboard/builder.py`
- Class: `LensDashboardBuilder`
- Methods:
  - `build(data_source: DataSource, output_path: Path) -> Path`
  - `_clean_output_folder(output_path: Path)` - **Delete existing output first**
  - `_render_html(data: Dict) -> str`
  - `_copy_assets(output_path: Path)` - **Must copy all CSS files**
  - `_validate_css_references(html: str) -> bool` - Ensure no broken CSS links
- **Clean First:** Always delete target folder before generation (prevents stale artifacts)
- **Safety:** Only delete if exists, create parents if needed

**Task 3.3: Tab Components** ☐ TODO
- **Build fresh components** - Use Admin Dashboard as UX reference only
- **Purpose-built** for CORTEX Lens AST data structure
- Create modular tab system (8-10 tabs)
- **Data binding:** Each tab designed for specific collector output
- **Remove inline styles** from all component HTML
- **Use CSS classes** for all styling (defined in external files)
- **Simplify logic:** Single-repo focus (no repo switching)
- **Document:** Each component's data contract and rendering logic

**Task 3.4: D3 Integration** ☐ TODO
- Test each D3 visualization standalone
- Integrate into appropriate tabs
- Ensure data binding works with mock data

**Task 3.5: Styling Integration** ☐ TODO
- Verify all external CSS files present
- Adapt color scheme to CORTEX Lens branding
- Optimize for single-repo view (no selector needed)
- **Validate:** Zero inline styles in final HTML
- **Test:** CSS caching works correctly
- **Performance:** Measure load time improvement from cached CSS
- Adapt color scheme to CORTEX Lens branding
**Checkpoint 3:** ✅ Complete when:
- [ ] Dashboard renders with mock data
- [ ] All D3 visualizations working
- [ ] Navigation functional
- [ ] Styling matches Admin Dashboard quality
- [ ] **Zero inline CSS** in final HTML
- [ ] All CSS loaded from external files
- [ ] CSS caching verified working
- [ ] Zero console errors or 404s for CSS filesal
- [ ] Styling matches Admin Dashboard quality
- [ ] Zero console errors

---

### **Phase 4: CORTEX Lens Integration**

**Duration:** 4-5 hours  
**Status:** ☐ NOT STARTED  
**Dependencies:** Phase 3 complete

#### Objectives
1. Integrate dashboard with CORTEX Lens orchestrator
2. Connect all 10 collectors to dashboard
3. Validate data flow

#### Tasks

**Task 4.1: Orchestrator Integration** ☐ TODO
- Modify `src/cortex_lens/orchestrator.py`
- Add dashboard generation phase
- Call `LensDashboardBuilder` after data collection

**Task 4.2: Collector Mapping** ☐ TODO
- Map each collector to dashboard tab:
  - HealthCollector → Overview tab
  - ArchitectureCollector → Architecture tab
  - APIEndpointCollector → API tab
  - SecurityCollector → Security tab
  - ComplexityCollector → Quality tab
  - TechStackCollector → Tech Stack tab
  - DependencyCollector → Dependencies tab
  - TestCoverageCollector → Testing tab
  - CommentCollector → Documentation tab

**Task 4.3: LiveDataSource Implementation** ☐ TODO
- File: `src/cortex_lens/dashboard/data_binding/live_source.py`
- Implement all DataSource interface methods
- Call appropriate collectors
- Transform collector output to dashboard format

**Task 4.4: CLI Integration** ☐ TODO
- Update `src/cortex_lens/cli.py`
- Add `--mock-data` flag to `analyze` command
- Default to live data, allow mock for testing
- **Required parameter:** `<repo_path>` (repository to analyze)
- **Optional parameters:**
  - `--output <path>` - Target folder (default: `./cortex-lens-output/`)
  - `--mock-data` - Use mock data instead of live AST
  - `--template <name>` - Template to use (default: `glassmorphism`)
  - `--clean/--no-clean` - Clean output before generation (default: `--clean`)
  - `--open` - Open dashboard in browser after generation
- **User feedback:** Progress indicators for each phase
- **Error handling:** Clear messages for invalid paths, permissions

**Checkpoint 4:** ✅ Complete when:
- [ ] Dashboard integrated with Lens orchestrator
- [ ] All collectors connected
- [ ] Live data flows through dashboard
- [ ] Mock mode works for testing
- [ ] CLI supports both modes

---

### **Phase 5: Documentation & Validation**

**Duration:** 2 hours  
**Status:** ☐ NOT STARTED  
**Dependencies:** Phase 4 complete

#### Objectives
1. Document mock dashboard system
2. Create developer guide
3. Validate all requirements met

#### Tasks

**Task 5.1: Architecture Documentation** ☐ TODO
- Create: `src/cortex_lens/dashboard/README.md`
- Document folder structure
- Explain mock→live transition
- Include code examples

**Task 5.2: Mock Data Guide** ☐ TODO
- Create: `src/cortex_lens/dashboard/mock_data/README.md`
- Explain schema format
- Document how to add new mock data
- Show transformation examples

**Task 5.3: Developer Guide** ☐ TODO
- Update: `src/cortex_lens/README.md`
- Add dashboard section
**Task 5.4: Validation Checklist** ☐ TODO
- [ ] All 10 collectors represented in dashboard
- [ ] Mock data covers all collector outputs
- [ ] Live data works with real repository
- [ ] D3 visualizations display correctly
- [ ] Styling matches Admin Dashboard quality
- [ ] **Zero inline CSS** in any HTML file
- [ ] All CSS references resolve correctly
- [ ] CSS caching improves load time (2nd load <500ms)
- [ ] **Target folder cleaned before generation** (no stale artifacts)
- [ ] **CLI accepts required parameters** (repo_path, output)
- [ ] **User feedback clear and helpful** (progress indicators)
- [ ] **Error handling graceful** (invalid paths, permissions)
- [ ] Zero dependencies on cortex-brain/dashboards/
- [ ] Performance acceptable (<2s initial load)
- [ ] Documentation completeDashboard quality
- [ ] Zero dependencies on cortex-brain/dashboards/
- [ ] Performance acceptable (<2s load time)
- [ ] Documentation complete

**Checkpoint 5:** ✅ Complete when:
- [ ] All documentation created
- [ ] Validation checklist passes
- [ ] Ready for production use

---
**Technical Metrics:**
- ✅ 100% self-contained (no cortex-brain dependencies)
- ✅ <2 second initial dashboard load time
- ✅ <500ms cached dashboard load time (CSS caching)
- ✅ All 10 collectors represented
- ✅ Mock→live swap in <10 lines of code
- ✅ Zero inline CSS (100% external stylesheets)
- ✅ Zero console errors or 404s
**Quality Metrics:**
- ✅ Visual quality matches Admin Dashboard
- ✅ Code follows CORTEX Lens conventions
- ✅ Clean separation: HTML (structure) + CSS (presentation) + JS (behavior)
- ✅ All styles maintainable in centralized CSS files
- ✅ Documentation complete and clear
- ✅ Mock data comprehensive and realistic
**Quality Metrics:**
- ✅ Visual quality matches Admin Dashboard
- ✅ Code follows CORTEX Lens conventions
- ✅ Documentation complete and clear
- ✅ Mock data comprehensive and realistic

---

## 🔄 Mock→Live Transition Strategy

**Current State (Mock):**
```python
# In orchestrator.py
data_source = MockDataSource()
dashboard_builder = LensDashboardBuilder(data_source)
```

**Future State (Live):**
```python
# In orchestrator.py
data_source = LiveDataSource(collectors=self.collectors)
dashboard_builder = LensDashboardBuilder(data_source)
```

**Environment Control:**
```python
# Configuration-based
import os
source_type = os.getenv('CORTEX_LENS_DATA_SOURCE', 'live')
data_source = (MockDataSource() if source_type == 'mock' 
               else LiveDataSource(collectors=self.collectors))
```

**Phase 0 (Priority):**
- `src/cortex_lens/dashboard/visualizations/*.js` (5 files)
- `src/cortex_lens/dashboard/mock_data/samples/*.json` (6+ files)
- `src/cortex_lens/dashboard/mock_data/loader.py`
- `src/cortex_lens/dashboard/mock_data/schema_mapping.py`
- `src/cortex_lens/dashboard/data_binding/data_source.py`
- `src/cortex_lens/dashboard/data_binding/mock_source.py`
- `src/cortex_lens/dashboard/styles/` (extract from Admin Dashboard + inline CSS)
- `src/cortex_lens/dashboard/mock_data/schema_mapping.py`
- `src/cortex_lens/dashboard/data_binding/data_source.py`
- `src/cortex_lens/dashboard/data_binding/mock_source.py`
- `src/cortex_lens/dashboard/styles/` (copy from Admin Dashboard)

**Phase 1-2:**
- `schema_mapping.md` (documentation)
- `src/cortex_lens/dashboard/mock_data/transformer.py`

**Phase 3:**
- `src/cortex_lens/dashboard/templates/index.html`
- `src/cortex_lens/dashboard/builder.py`
- `src/cortex_lens/dashboard/templates/partials/*.html` (8-10 files)

**Phase 4:**
- `src/cortex_lens/dashboard/data_binding/live_source.py`
- Modifications to `orchestrator.py` and `cli.py`

**Phase 5:**
- `src/cortex_lens/dashboard/README.md`
## 🎯 Workflow Summary

**Iterative Refinement Process:**
1. **Phase 0:** Ground Work - Setup template with mock data
2. **Phase 1:** Serve Dashboard - PowerShell HTTP server for live preview
3. **Phase 2:** Iterative Refinement - Work tab-by-tab with user feedback
4. **Phase 3:** Final Integration - Replace mock data with live AST collectors

**Per-Tab Refinement Cycle:**
1. Review current tab implementation
2. User provides feedback and requirements
3. Document requirements in tab sub-plan
4. Implement changes
5. Regenerate dashboard
6. Refresh browser (http://localhost:8080)
7. User validates changes
8. Repeat until tab approved
9. Move to next tab

**Documentation:**
- Master plan tracks overall progress
- Workflow guide defines process
- Tab sub-plans capture detailed requirements
- Requirements log records all decisions

## 🎯 Next Actions

1. **Immediate:** Execute Phase 0 - D3 extraction and mock data migration
2. **After Ground Work:** Generate initial dashboard and start server
3. **Begin Refinement:** Start with Tab 1 (Executive Summary)
4. **Document Everything:** Record requirements in sub-plans and requirements log
5. **Iterate:** Refine each tab until user approves
6. **Final Phase:** Replace mock data with live AST collectors
## 🎯 Next Actions

1. **Immediate:** Execute Phase 0 - D3 extraction and mock data migration
2. **Review:** Validate proposed structure with stakeholder
3. **Begin:** Start Phase 0 Task 0.2 (Extract D3 visualizations)

---

**Plan Author:** Asif Hussain  
**Plan Status:** Ready for execution  
**Estimated Total Duration:** 20-24 hours  
**Priority:** HIGH - Foundation for CORTEX Lens UI evolution
