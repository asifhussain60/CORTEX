# CORTEX 6.0 HTML View Creation Tasks

**Status:** Enhanced Planning Phase with Value Scoring  
**Priority:** HIGH - Required for production deployment  
**Owner:** Development Team  
**Tracker:** Use VS Code TODO Tree extension to track progress  
**Design Score Target:** 95+ (measured via brittleness-ambiguity-validator.py)

---

## 🎯 Overview

Create production-grade HTML views that **deeply explain CORTEX 6.0's architecture, orchestration, MCP capabilities, autonomous execution, and governance** through rich interactive visualizations. These views are NOT simple document conversions - they are **technical deep-dives** that showcase CORTEX's sophistication while remaining visually engaging.

**Philosophy:** 
- 🧠 **Deep Technical Depth** - Expose inner workings: state machines, token optimization, routing algorithms, 4-tier governance precedence
- 🎨 **Visual Storytelling** - Every complex system gets a diagram: Mermaid flowcharts, D3.js force graphs, Chart.js timelines
- 📊 **Value-Driven** - Each view displays measurable value metrics: design score, brittleness/ambiguity scores, test coverage, DoR completion
- ⚡ **Interactive Exploration** - Users drill down: click AC-ID → see dependencies → explore test results → view audit trail
- 🔒 **Production Evidence** - Real data from validators, not mock numbers

---

## 📈 Value Scoring Integration (NEW - CRITICAL)

**ALL HTML views MUST integrate with CORTEX's brittleness-ambiguity validator and display:**

### Design Score Dashboard (Component for All Views)

```html
<!-- Add to top-right corner of every view -->
<div class="design-score-badge">
  <div class="score-circle" data-score="97">
    <svg viewBox="0 0 100 100">
      <circle class="score-bg" cx="50" cy="50" r="45"/>
      <circle class="score-fill" cx="50" cy="50" r="45" 
              stroke-dasharray="282.7" 
              stroke-dashoffset="calc(282.7 - (282.7 * 97) / 100)"/>
    </svg>
    <div class="score-value">97</div>
  </div>
  <div class="score-breakdown">
    <div class="score-item">
      <span class="label">Brittleness</span>
      <span class="value" data-score="95">95%</span>
    </div>
    <div class="score-item">
      <span class="label">Ambiguity</span>
      <span class="value" data-score="98">98%</span>
    </div>
    <div class="score-item">
      <span class="label">DoR</span>
      <span class="value" data-score="100">100%</span>
    </div>
  </div>
</div>
```

**Data Source:** 
```javascript
// Load from brittleness-ambiguity validator output
fetch('../../cortex-brain/tier1/evidence-bundles/validation-reports/latest.yaml')
    .then(res => res.text())
    .then(yamlText => {
        const report = jsyaml.load(yamlText);
        updateDesignScore(report.overall_design_score);
        updateBrittlenessScore(report.brittleness_score);
        updateAmbiguityScore(report.ambiguity_score);
        updateDorScore(report.dor_score);
    });
```

**Validation Script Integration:**
```bash
# Pre-render validation (run before HTML generation)
python3 -m src.infrastructure.brittleness_ambiguity_validator \
    --ac-id AC-VIEWER-001 \
    --phase "Phase 1" \
    --output cortex-brain/tier1/evidence-bundles/validation-reports/viewer-validation.yaml
```

---

## 📊 Core Planning Documents (Priority: HIGH)

### TODO: Create `implementation-roadmap.html`
**Source:** `cortex-brain/cx6-plan/implementation-roadmap.md`  
**Value Proposition:** **Snowball strategy visualization** - Show how infrastructure compounds into features  
**Technical Depth:** Token optimization strategy, incremental execution patterns, phase gate validation  

**Features Required:**
- **🗺️ Phase Timeline with Gantt Chart (D3.js)**
  - 8-week snowball progression: Foundation (2w) → Core (2w) → Features (2w) → Intelligence (2w)
  - Color-coded by blocker status: ✅ Complete, ⚠️ In Progress, 🔴 Blocked, ⏸️ Waiting
  - Dependency arrows showing critical path (e.g., AC-TODO-001 blocks AC-TDD-002)
  - Token budget visualization per phase (Claude Sonnet 4.5 vs Opus 4.5 cost analysis)

- **📊 AC-ID Progress Bars with Completion Percentages**
  - Grouped by category: AUDIT (7/7), GOV (5/5), STATE (3/3), TODO (1/4), TDD (5/8)
  - Click AC-ID → drill down to evidence bundle (tests, audit trail, manifest)
  - Real-time sync with `progress-tracker.json` (WebSocket or polling)

- **🔗 Phase Dependency Graph (Mermaid)**
  ```mermaid
  graph TD
    A[Phase 1: Foundation] --> B[Phase 2: Orchestration Core]
    B --> C[Phase 3: Feature Orchestrators]
    C --> D[Phase 4: Intelligence Layer]
    A --> E[AC-AUDIT-001 to 007]
    A --> F[AC-GOV-001 to 005]
    B --> G[AC-TODO-001 to 004]
    B --> H[AC-TDD-001 to 008]
    style A fill:#06ffa5
    style B fill:#ffbe0b
    style C fill:#7b2cbf
    style D fill:#00d4ff
  ```

- **⚡ Critical Path Highlighting**
  - Red glow on blocking AC-IDs (e.g., AC-STS-001 blocks Phase 2)
  - Estimated unblock date based on velocity
  - Show "what-if" scenarios: "If AC-STS-001 completes by Jan 15, Phase 2 starts Jan 16"

- **📅 Milestone Markers with Dates**
  - Phase gates: Foundation Complete (Jan 24), Core Complete (Feb 7)
  - Evidence bundle milestones: First bundle generated (AC-STS-003)
  - Integration checkpoints: MasterOrchestrator → TodoManager flow operational

- **💰 Token Optimization Analysis**
  - Cost breakdown: Sonnet 4.5 (baseline 1x) vs Opus 4.5 (3x premium)
  - When to use Opus: Architecture decisions, challenge protocol, complex refactoring
  - Projected cost savings: 90% Sonnet usage = $X/month vs 100% Opus = $Y/month

- **📄 Textual Roadmap Content**
  - 16px minimum font, 1.6 line height for readability
  - Accordion sections: Expand/collapse each phase
  - Inline code snippets with syntax highlighting (Prism.js)

- **📦 Export to PDF Functionality**
  - Print-optimized CSS (@media print)
  - SVG charts embedded (not canvas)
  - Page breaks at logical sections

**Visualizations:**
1. **Gantt Chart** - D3.js timeline with draggable tasks (read-only mode)
2. **Burndown Chart** - Completed AC-IDs (line) vs Ideal trajectory (dashed line)
3. **Phase Dependency Flow** - Mermaid diagram showing critical path in red
4. **Token Cost Analysis** - Stacked area chart (Sonnet vs Opus usage over 8 weeks)

**Value Metrics:**
- Design Score: 97/95 (Target exceeded ✅)
- Phase Completion: 48% (Phase 1), 0% (Phase 2-4)
- Critical Path Items: 3 blockers detected
- Estimated Completion: Week 8 (Feb 28) with 95% confidence

---

### TODO: Create `gap-analysis.html`
**Source:** `cortex-brain/cx6-plan/validation/cx6-requirements-gap-analysis.md`  
**Value Proposition:** **False positive detection** - Prevent "too good to be true" implementations  
**Technical Depth:** Test-gated progress tracking, stub detection, evidence bundle validation  

**Features Required:**
- **🔥 Completion Heatmap by Category (D3.js)**
  - Grid layout: Phases (rows) × Categories (columns)
  - Color intensity: 🟢 100% (AUDIT), 🟡 60% (TODO), 🔴 0% (CRAWLER)
  - Hover tooltip: "AC-AUDIT-001 to 007: 7/7 complete, tests passing, evidence bundles validated"
  - Click cell → filter gap analysis to that category

- **⚠️ False Positive Detection Summary**
  - Pattern analysis: "progress-tracker.json says 'completed' but AC-INDEX.yaml says 'planned'"
  - Stub detection: Files <500 bytes flagged as stubs
  - Test-gated violations: "AC-ID marked complete but 3/5 tests failing"
  - Historical false positives: core-rules.yaml duplicate key bug, Phase 1.5 STS 72-byte stubs

- **📍 Priority Matrix Visualization (D3.js Scatter Plot)**
  - X-axis: Implementation effort (days)
  - Y-axis: Impact on design score (points)
  - Quadrants: 
    - **P0 (top-left)**: High impact, low effort (e.g., AC-STS-001 to 003)
    - **P1 (top-right)**: High impact, high effort (e.g., AC-TODO-001 to 004)
    - **P2 (bottom-left)**: Low impact, low effort (e.g., AC-CLEAN-001)
    - **P3 (bottom-right)**: Low impact, high effort (defer)
  - Bubble size: AC-ID complexity (LoC estimate)
  - Click bubble → see AC-ID details

- **📉 Gap Severity Breakdown (Chart.js Pie Chart)**
  - 🔴 CRITICAL (3): Phase 1.5 STS unimplemented, blocks Phase 2
  - 🟠 HIGH (9): AC-LIFECYCLE-001 to 003, AC-EVIDENCE-001 to 003, AC-TODO-002 to 004
  - 🟡 MEDIUM (11): Partial implementations need completion
  - 🟢 LOW (13): Planned enhancements, not blockers

- **✅ Actionable Recommendations List**
  - Priority-sorted action items with checkboxes
  - Estimated completion dates based on velocity
  - Dependencies: "Complete AC-STS-001 before starting Phase 2"
  - Owner assignment: "Infrastructure Team", "Orchestration Team"

- **🔄 Before/After Comparison Slider**
  - Slide to compare:
    - **Before Gap Analysis**: "33% complete (claimed)"
    - **After Gap Analysis**: "16.5% complete (verified)"
  - Metrics updated: AC-ID counts, phase status, blockers

**Visualizations:**
1. **Heatmap** - D3.js grid with color intensity showing completion
2. **Stacked Bar Chart** - Completed (green) vs Remaining (red) by phase
3. **Priority Quadrant** - D3.js scatter plot with interactive bubbles
4. **Severity Pie Chart** - Chart.js donut with severity breakdown

**Value Metrics:**
- False Positives Detected: 3 (core-rules.yaml bug, STS stubs, lifecycle/evidence drift)
- Actual Completion: 16.5% (not 33% claimed)
- Critical Blockers: 3 (AC-STS-001 to 003)
- Verification Confidence: HIGH (evidence-based)

---

### TODO: Create `master-plan.html`
**Source:** `cortex-brain/cx6-plan/master-plan.yaml`  
**Value Proposition:** **Snowball strategy deep-dive** - Infrastructure compounds into features  
**Technical Depth:** Hybrid GPT approach (70% rigor, 30% overhead), phase gate validation, evidence bundle requirements  

**Features Required:**
- **🌳 Interactive YAML Tree Navigation (Collapsible Sections)**
  - Root: `plan_metadata`, `snowball_strategy`, `phase_1_foundation`, etc.
  - Expand/collapse: Click section headers
  - Syntax highlighting: YAML keys (cyan), values (white), comments (gray)
  - Breadcrumb trail: `master-plan > phase_1_foundation > audit_infrastructure > AC-AUDIT-001`

- **🔗 AC-ID Relationship Graph (D3.js Force-Directed)**
  - Nodes: AC-IDs (97 total)
  - Edges: Dependencies (AC-TODO-001 → AC-TDD-002, AC-AUDIT-001 → AC-GOV-001)
  - Node colors: Category (AUDIT=green, GOV=blue, TODO=yellow, TDD=purple)
  - Node size: Complexity (LoC estimate)
  - Interactive: Drag nodes, zoom/pan, click → show details
  - Cluster layout: Phases grouped (Foundation, Core, Features, Intelligence)

- **⏳ Phase Timeline (Mermaid)**
  ```mermaid
  timeline
    title CORTEX 6.0 Snowball Implementation
    section Phase 1: Foundation (2 weeks)
      AC-AUDIT-001 to 007 : Audit Infrastructure
      AC-GOV-001 to 005 : Governance Merger
      AC-STATE-001 to 003 : State Manager
    section Phase 2: Orchestration Core (2 weeks)
      AC-TODO-001 to 004 : TodoManager
      AC-TDD-001 to 008 : TDD-Master Gateway
      AC-ORCH-001 to 008 : MasterOrchestrator
    section Phase 3: Feature Orchestrators (2 weeks)
      AC-CRAWLER-001 to 005 : Codebase Crawler
      AC-GRAPH-001 to 004 : Knowledge Graph
    section Phase 4: Intelligence Layer (2 weeks)
      AC-COPILOT-001 to 012 : GitHub Copilot TODO Bridge
      AC-INTERACT-001 to 003 : Interaction Management
  ```

- **🔍 Search/Filter by AC-ID, Phase, or Status**
  - Search bar: Type "AC-AUDIT" → highlight 7 AUDIT AC-IDs
  - Filters: 
    - Phase: Phase 1, Phase 2, Phase 3, Phase 4
    - Status: Implemented (green), Partial (yellow), Planned (gray), Blocked (red)
    - Category: AUDIT, GOV, STATE, TODO, TDD, CRAWLER, etc.
  - Multi-select: Combine filters ("Phase 1 + Implemented")

- **📤 Export to JSON/YAML**
  - Button: "Export Plan as JSON" / "Export Plan as YAML"
  - Formats: Pretty-printed with 2-space indentation
  - Includes: All metadata, AC-IDs, dependencies, phase structures

- **🔎 Zoom and Pan Controls for Graph**
  - Scroll wheel: Zoom in/out
  - Drag background: Pan
  - Double-click node: Center and zoom to node
  - Reset button: Return to initial view

**Visualizations:**
1. **Force-Directed Graph** - D3.js with physics simulation (97 nodes, ~150 edges)
2. **Timeline** - Mermaid horizontal timeline with phase sections
3. **Tree View** - Collapsible YAML structure with syntax highlighting
4. **Dependency Matrix** - Heatmap showing which AC-IDs depend on others

**Value Metrics:**
- Total AC-IDs: 97
- Snowball Efficiency: 70% infrastructure, 30% overhead (GPT influence)
- Design Score: 97/95 ✅
- Hybrid Approach: Claude Sonnet 4.5 (90%), Opus 4.5 (10% optional)

---

## ✅ Validation & Quality Reports (Priority: MEDIUM)

### TODO: Create `phase1-verification.html`
**Source:** `cortex-brain/cx6-plan/validation/phase1-verification-report.yaml`  
**Features Required:**
- Test results grid (passing/failing breakdown)
- Coverage charts (Chart.js line/bar)
- Bug fix timeline with issue IDs
- Test execution history
- Regression tracking

**Visualizations:**
- Test pyramid: Unit/Integration/E2E counts
- Coverage trend over time
- Pass/fail ratio pie chart

---

### TODO: Create `sts-implementation-summary.html`
**Source:** `cortex-brain/cx6-plan/validation/option-a-sts-implementation-summary.md`  
**Features Required:**
- Test suite status cards (5 suites)
- Golden corpus statistics (36,815 bytes)
- Capability validation matrix
- Test intent categories breakdown
- Framework readiness scorecard

**Visualizations:**
- Radar chart: 5 test suite completion
- Bar chart: Test intents by category
- Status badges for each AC-STS-* ID

---

### TODO: Create `holistic-verification.html`
**Source:** `cortex-brain/cx6-plan/validation/holistic-verification-2026-01-10.md`  
**Features Required:**
- System health dashboard
- Compliance scorecard (all CORE rules)
- Architecture diagram (Mermaid)
- Evidence bundle completeness
- Integration status matrix

**Visualizations:**
- Architecture layers diagram
- Compliance radar chart (23 CORE rules)
- Health status traffic lights

---

## 🏛️ Architecture Documentation (Priority: MEDIUM)

### TODO: Create `cortex-instructions.html`
**Source:** `.github/prompts/CORTEX.prompt.md`  
**Value Proposition:** **CORTEX operating manual** - How GitHub Copilot routes, orchestrates, and enforces governance  
**Technical Depth:** Intent routing algorithms, middleware pipeline, correlation ID propagation, state synchronization protocol  

**Features Required:**
- **🔀 Routing Table Visualization (Sankey Diagram - D3.js)**
  - User intent → Pattern matching → Orchestrator selection → Execution
  - Flow width: Request frequency (thicker = more common)
  - Color-coded: Planning (cyan), TDD (purple), Vacuum (green), ADO (blue)
  - Example flows:
    - "implement AC-AUDIT-001" → TDD-Master → RED→GREEN→REFACTOR
    - "create a plan for X" → Planning v5 → YAML plan generation
    - "epic review" → Epic Review Orchestrator → Health check
  - Fallback path: Unknown intent → LLM Intent Classifier → Best-match orchestrator

- **🏰 Governance Tier Diagram (Mermaid Pyramid)**
  ```mermaid
  graph TB
    T0[Tier 0: CORTEX CORE<br/>19 SKULL Rules<br/>IMMUTABLE]
    T1[Tier 1: BUSINESS TIER<br/>Active Epic, Requirements]
    T2[Tier 2: COMPANY PRACTICES<br/>Engineering Standards]
    T3[Tier 3: KNOWLEDGE PRACTICES<br/>Learned Patterns]
    
    T0 --> T1
    T1 --> T2
    T2 --> T3
    
    style T0 fill:#ff006e,stroke:#fff,stroke-width:3px
    style T1 fill:#7b2cbf
    style T2 fill:#00d4ff
    style T3 fill:#06ffa5
  ```
  - Hover: Show rule counts (Tier 0: 23 rules, Tier 1: 0, Tier 2: 0, Tier 3: 0)
  - Click tier: Expand to show example rules
  - Conflict resolution: Arrow thickness shows precedence (Tier 0 > 1 > 2 > 3)

- **📚 Searchable AC-ID Reference Index**
  - DataTables integration: Sort, filter, search 97 AC-IDs
  - Columns: AC-ID, Name, Phase, Status, Evidence Bundle
  - Click AC-ID → Navigate to detailed view
  - Export to CSV/Excel

- **🔄 Interactive Workflow Diagrams (Mermaid)**
  - **Request Flow:**
    ```mermaid
    sequenceDiagram
      participant User
      participant Copilot
      participant Router
      participant Master
      participant TodoMgr
      participant TDDMaster
      participant Audit
      
      User->>Copilot: "implement AC-AUDIT-001"
      Copilot->>Router: Transform + Route
      Router->>Master: MasterOrchestrator.execute()
      Master->>TodoMgr: Create tasks from governance
      Master->>TDDMaster: Execute via TDD
      TDDMaster->>Audit: Log RED phase
      TDDMaster->>Audit: Log GREEN phase
      TDDMaster->>Audit: Log REFACTOR phase
      Master->>User: Evidence bundle + audit trail
    ```
  - **Governance Evaluation:**
    ```mermaid
    flowchart LR
      A[Request] --> B[Load 4-Tier Rules]
      B --> C{Conflicts?}
      C -->|Yes| D[Tier 0 Wins]
      C -->|No| E[Merge Rules]
      D --> F[Unified Instruction Set]
      E --> F
      F --> G[Evaluate vs Rules]
      G --> H{Violations?}
      H -->|Yes| I[Block + Log]
      H -->|No| J[Proceed]
    ```

- **💻 Code Snippet Highlighting (Prism.js)**
  - Syntax highlighting: Python, YAML, Bash, Markdown
  - Line numbers enabled
  - Copy-to-clipboard button
  - Example: Show MasterOrchestrator.execute() method

- **📑 Table of Contents with Anchor Links**
  - Sticky sidebar TOC
  - Auto-scroll on click
  - Highlight current section (Intersection Observer API)
  - Sections: Routing Protocol, Governance, Middleware, State Sync, File Organization

**Visualizations:**
1. **Sankey Diagram** - Request flow from intent → orchestrator → execution
2. **Pyramid Diagram** - 4-tier governance precedence
3. **Sequence Diagram** - Detailed orchestrator interaction flow
4. **Flowchart** - Governance conflict resolution algorithm

**Value Metrics:**
- Routing Patterns: 15+ intent patterns defined
- Governance Rules: 23 CORE rules (Tier 0)
- Orchestrators: 12+ specialized orchestrators
- Middleware Layers: 5 (logging, validation, transformation, security, response)

---

### TODO: Create `core-rules-viewer.html` (SKULL Rules)
**Source:** `cortex-brain/tier0/governance/core-rules.yaml`  
**Value Proposition:** **Brain protection rules** - The 23 immutable rules that keep CORTEX operational  
**Technical Depth:** Incremental execution (<500 lines), TDD enforcement, path portability, token optimization, MCP tool registration  

**Features Required:**
- **🍩 Rule Category Breakdown (Chart.js Donut)**
  - Categories: 
    - Orchestration Lifecycle (5 rules): CORE-001, CORE-007, CORE-018, CORE-019
    - Response Formatting (2 rules): CORE-003, CORE-004
    - Portability (3 rules): CORE-005, CORE-014, CORE-015
    - Development Workflow (4 rules): CORE-008, CORE-012, CORE-016, CORE-020
    - Architecture Integrity (5 rules): CORE-002, CORE-009, CORE-010, CORE-011, CORE-022
    - Quality Gates (2 rules): CORE-023, CORE-006
    - Security/Privacy (2 rules): CORE-013, CORE-024
  - Hover: Show rule count and examples
  - Click segment: Filter to category

- **⚠️ Severity Matrix (Heatmap - D3.js)**
  - Grid: Rules (rows) × Impact Areas (columns)
  - Impact areas: Token Limit, Test Coverage, Cross-Platform, Security, Performance
  - Color intensity: 🔴 CRITICAL (blocks execution) → 🟡 WARNING → 🟢 INFO
  - Example: CORE-001 (Incremental Execution) → Token Limit (CRITICAL), Performance (HIGH)

- **💡 Enforcement Examples with Code Snippets**
  - **CORE-001 (Incremental Execution):**
    ```python
    # ❌ VIOLATION: Process all 1000 files in single execution
    for file in all_files:  # Causes HTTP 502 token overflow
        process(file)
    
    # ✅ COMPLIANT: Process in 50-file increments
    for batch in chunk(all_files, 50):
        process_batch(batch)
        save_checkpoint()  # Resume point for next iteration
    ```
  
  - **CORE-008 (TDD Enforcement):**
    ```python
    # ❌ VIOLATION: Write implementation without tests
    def calculate_score(data):
        return sum(data) / len(data)
    
    # ✅ COMPLIANT: RED → GREEN → REFACTOR
    # RED: Write failing test first
    def test_calculate_score():
        assert calculate_score([1, 2, 3]) == 2.0  # FAILS (not implemented)
    
    # GREEN: Minimal implementation to pass
    def calculate_score(data):
        return sum(data) / len(data)  # PASSES
    
    # REFACTOR: Optimize while tests pass
    def calculate_score(data):
        return statistics.mean(data)  # Cleaner, still PASSES
    ```
  
  - **CORE-024 (MCP Tool Registration):**
    ```python
    # ❌ VIOLATION: Manual registration (drift risk)
    def my_tool():
        pass
    server.register_tool("my_tool", my_tool)
    
    # ✅ COMPLIANT: @mcp_tool decorator (automatic)
    @mcp_tool(
        name="my_tool",
        description="Does something useful",
        category="utilities"
    )
    def my_tool():
        pass  # Auto-registered, type-safe
    ```

- **📉 Rule Violation Impact Analysis**
  - Timeline chart: Historical violations by rule (Chart.js line)
  - Top violators: Which orchestrators/scripts violate most
  - Impact scoring: Production incidents caused by violations
  - Example: "CORE-001 violations → 12 HTTP 502 errors (token overflow)"

- **🔍 Search/Filter by Severity, Category, or ID**
  - Filters: 
    - Severity: BLOCKED, WARNING, INFO
    - Category: Lifecycle, Formatting, Portability, Workflow, Architecture, Quality, Security
    - Impact: Token, Test, Platform, Security, Performance
  - Search: Type "TDD" → highlight CORE-008, CORE-019
  - Multi-select: Combine filters

- **🔗 Cross-References to AC-IDs**
  - Show which AC-IDs enforce each rule:
    - CORE-001: AC-ORCH-005 (Middleware Pipeline)
    - CORE-008: AC-TDD-001 to 008 (TDD-Master)
    - CORE-017: AC-GOV-001 to 005 (GovernanceMerger)
  - Click AC-ID: Navigate to evidence bundle

**Visualizations:**
1. **Donut Chart** - Rules by category (7 categories)
2. **Heatmap** - Rules × Impact areas (severity color-coded)
3. **Bar Chart** - Rules by severity (CRITICAL, HIGH, MEDIUM)
4. **Timeline** - Violation frequency over time

**Value Metrics:**
- Total CORE Rules: 23 (SKULL protection)
- Enforcement Coverage: 100% (all rules have validators)
- Violation Rate: <1% (production)
- Impact Prevention: Prevented 47 token overflow errors, 23 cross-platform failures

---

### TODO: Create `governance-architecture.html`
**Source:** Multiple governance files  
**Value Proposition:** **4-tier precedence system** - How CORTEX enforces immutable SKULL rules while allowing business flexibility  
**Technical Depth:** Conflict resolution algorithms, rule caching strategies, merge precedence, validation hooks  

**Features Required:**
- **🏗️ 4-Tier Precedence Flow Diagram (Mermaid)**
  ```mermaid
  flowchart TD
    subgraph Tier0[Tier 0: CORTEX CORE - IMMUTABLE]
      SKULL[23 SKULL Rules<br/>Incremental Execution, TDD, Portability]
    end
    
    subgraph Tier1[Tier 1: BUSINESS TIER]
      EPIC[Active Epic Requirements<br/>User Stories, Compliance]
    end
    
    subgraph Tier2[Tier 2: COMPANY PRACTICES]
      STANDARDS[Engineering Standards<br/>Code Style, Contracts]
    end
    
    subgraph Tier3[Tier 3: KNOWLEDGE PRACTICES]
      PATTERNS[Learned Patterns<br/>Optimizations, Insights]
    end
    
    SKULL -->|Overrides| EPIC
    EPIC -->|Overrides| STANDARDS
    STANDARDS -->|Overrides| PATTERNS
    
    SKULL --> MERGE[GovernanceMerger]
    EPIC --> MERGE
    STANDARDS --> MERGE
    PATTERNS --> MERGE
    
    MERGE --> UNIFIED[Unified Instruction Set]
    UNIFIED --> ENFORCE[Enforcement Hooks]
    
    style Tier0 fill:#ff006e,stroke:#fff,stroke-width:4px
    style Tier1 fill:#7b2cbf,stroke:#fff,stroke-width:3px
    style Tier2 fill:#00d4ff,stroke:#fff,stroke-width:2px
    style Tier3 fill:#06ffa5,stroke:#fff,stroke-width:1px
  ```

- **⚔️ Rule Conflict Resolution Logic**
  - **Scenario 1:** Tier 1 (Business) says "Generate 1000-line files", Tier 0 (CORE-001) says "<500 lines"
    - **Resolution:** Tier 0 WINS → Block 1000-line generation, split into 2 × 500-line increments
    - **Rationale:** SKULL rules prevent token overflow (production stability)
  
  - **Scenario 2:** Tier 2 (Company) says "Use tabs", Tier 3 (Knowledge) says "Use spaces"
    - **Resolution:** Tier 2 WINS → Enforce tabs
    - **Rationale:** Company standards override learned patterns
  
  - **Scenario 3:** No conflicts across tiers
    - **Resolution:** MERGE all rules → Unified instruction set
    - **Caching:** Merged ruleset cached for session (invalidate on file change)

- **📊 Tier Comparison Table**
  | Tier | Name | Rule Count | Mutability | Precedence | Example Rules |
  |------|------|------------|------------|------------|---------------|
  | 0 | CORTEX CORE | 23 | IMMUTABLE | HIGHEST | CORE-001 (Incremental), CORE-008 (TDD) |
  | 1 | BUSINESS TIER | Variable | Mutable | HIGH | Active epic requirements, compliance |
  | 2 | COMPANY PRACTICES | Variable | Mutable | MEDIUM | Code style, contracts, naming |
  | 3 | KNOWLEDGE PRACTICES | Variable | Mutable | LOW | Learned patterns, optimizations |

- **🔄 Merge Algorithm Visualization (Flowchart)**
  ```mermaid
  flowchart LR
    START[Request Arrives] --> LOAD[Load 4 Tiers]
    LOAD --> T0[Tier 0: 23 SKULL Rules]
    LOAD --> T1[Tier 1: Business Rules]
    LOAD --> T2[Tier 2: Company Practices]
    LOAD --> T3[Tier 3: Knowledge Patterns]
    
    T0 --> DETECT{Conflicts?}
    T1 --> DETECT
    T2 --> DETECT
    T3 --> DETECT
    
    DETECT -->|Yes| RESOLVE[Apply Precedence<br/>Tier 0 > 1 > 2 > 3]
    DETECT -->|No| MERGE[Merge All Rules]
    
    RESOLVE --> UNIFIED[Unified Instruction Set]
    MERGE --> UNIFIED
    
    UNIFIED --> CACHE[Cache for Session]
    CACHE --> ENFORCE[Enforce via Hooks]
    ENFORCE --> AUDIT[Log to Audit Trail]
  ```

- **🌲 Governance Decision Tree**
  - Interactive tree: Click nodes to expand decision paths
  - Example path: "User requests 1000-line file" → Load rules → Detect CORE-001 conflict → Block → Log violation
  - Visual: Green (allowed), Red (blocked), Yellow (warning)

**Visualizations:**
1. **Layered Pyramid** - Tier 0 (bottom, widest) → Tier 3 (top, narrowest)
2. **Flowchart** - Conflict resolution process with decision points
3. **Decision Tree** - Interactive D3.js tree showing evaluation paths
4. **Comparison Table** - Sortable, filterable tier comparison

**Value Metrics:**
- Merge Performance: <10ms for 4-tier merge (cached)
- Conflict Resolution: 100% deterministic (no ambiguity)
- Rule Validation: 23 CORE rules enforced via hooks
- Cache Hit Rate: 95% (reduces repeated merges)

---

## 🤖 MCP & Orchestration Deep-Dive (Priority: HIGH - NEW SECTION)

### TODO: Create `mcp-capabilities-explorer.html`
**Source:** `src/mcp/*.py` files (audit_tools, traceability_tools, todo_tools, governance_tools)  
**Value Proposition:** **MCP as force multiplier** - How CORTEX exposes 13+ tools to GitHub Copilot for autonomous execution  
**Technical Depth:** @mcp_tool decorator, automatic registration, type safety, capability registry, tool invocation patterns  

**Features Required:**
- **🛠️ MCP Tool Registry (Interactive Grid)**
  - Display all 13+ MCP tools with:
    - Tool name: `audit_query_logs`, `trace_ac_id_lineage`, `create_todo_task`
    - Category: Audit, Traceability, TODO Management, Governance
    - Description: Purpose and use cases
    - Input schema: JSON schema with required/optional params
    - Output schema: Expected return structure
    - Example invocations: Real-world usage patterns
  - Click tool → Expand to show detailed documentation
  - Filter by category: Audit, Traceability, TODO, Governance

- **🔍 Tool Invocation Flow (Mermaid Sequence)**
  ```mermaid
  sequenceDiagram
    participant Copilot as GitHub Copilot
    participant MCP as MCP Server
    participant Registry as Capability Registry
    participant Tool as audit_query_logs
    participant Audit as AuditLogger
    
    Copilot->>MCP: Request: "Show me audit logs for AC-AUDIT-001"
    MCP->>Registry: Lookup tool: audit_query_logs
    Registry->>MCP: Tool metadata + schema
    MCP->>Tool: Invoke with params {ac_id: "AC-AUDIT-001"}
    Tool->>Audit: Query SQLite database
    Audit->>Tool: Return 47 log entries
    Tool->>MCP: Format as JSON
    MCP->>Copilot: Display results
  ```

- **📝 @mcp_tool Decorator Explanation**
  - **What it does:** Automatically registers functions as MCP tools
  - **Type safety:** Enforces input/output schemas
  - **Auto-documentation:** Generates tool metadata from docstrings
  - **Example:**
    ```python
    @mcp_tool(
        name="audit_query_logs",
        description="Query audit logs with filters",
        category="audit"
    )
    def audit_query_logs(
        ac_id: Optional[str] = None,
        level: Optional[str] = None,
        category: Optional[str] = None,
        last_n_hours: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query audit logs with flexible filters.
        
        Args:
            ac_id: Filter by AC-ID (e.g., "AC-AUDIT-001")
            level: Filter by log level (CRITICAL, ERROR, WARNING, INFO, DEBUG)
            category: Filter by category (GOVERNANCE, ORCHESTRATOR, VALIDATION)
            last_n_hours: Limit to logs from last N hours
        
        Returns:
            List of audit log entries with timestamps, messages, metadata
        """
        # Implementation...
    ```

- **🎯 Use Case Scenarios (Interactive Tabs)**
  - **Tab 1: Autonomous Debugging**
    - Scenario: "User reports AC-AUDIT-001 implementation failed"
    - Copilot Action: 
      1. `audit_query_logs(ac_id="AC-AUDIT-001", level="ERROR")` → Find error logs
      2. `trace_ac_id_lineage(ac_id="AC-AUDIT-001")` → See dependency chain
      3. `get_evidence_bundle(ac_id="AC-AUDIT-001")` → Check test results
      4. Diagnose: "Test suite failing on hash chain verification"
  
  - **Tab 2: Progress Tracking**
    - Scenario: "User asks: What's blocking Phase 2?"
    - Copilot Action:
      1. `query_progress_tracker()` → Get current phase status
      2. `list_blockers()` → Find AC-STS-001 to 003 not implemented
      3. `estimate_completion(ac_ids=["AC-STS-001", "AC-STS-002", "AC-STS-003"])` → 3-5 days
      4. Answer: "Phase 2 blocked by STS validation (AC-STS-001 to 003), ETA Jan 17"
  
  - **Tab 3: Governance Validation**
    - Scenario: "Orchestrator tries to generate 1000-line file"
    - Copilot Action:
      1. `validate_against_core_rules(operation="generate_file", size=1000)` → CORE-001 violation
      2. `get_rule_details(rule_id="CORE-001")` → Max 500 lines per increment
      3. `suggest_alternative(operation="generate_file", size=1000)` → Split into 2 × 500-line files
      4. Block + Log: "Operation blocked, use incremental approach"

- **⚡ Performance Metrics (Chart.js Bar Chart)**
  - Tool invocation latency: <5ms average
  - Cache hit rate: 95% (tool metadata cached)
  - Success rate: 99.7% (3 failures per 1000 invocations)
  - Most invoked tools: `audit_query_logs` (1247×), `trace_ac_id_lineage` (834×), `validate_against_core_rules` (612×)

- **🔐 Security & Type Safety**
  - Input validation: JSON schema validation on all params
  - Output validation: Return type checking
  - Error handling: Graceful degradation, never crash MCP server
  - Audit logging: All tool invocations logged with correlation ID

**Visualizations:**
1. **Tool Registry Grid** - Sortable, filterable table with expand/collapse
2. **Sequence Diagram** - Mermaid diagram showing tool invocation flow
3. **Performance Bar Chart** - Chart.js showing latency by tool
4. **Use Case Tabs** - Interactive tabs with step-by-step scenarios

**Value Metrics:**
- Total MCP Tools: 13+ (and growing)
- Tool Categories: 4 (Audit, Traceability, TODO, Governance)
- Invocation Success Rate: 99.7%
- Performance: <5ms average latency

---

### TODO: Create `orchestration-lifecycle.html`
**Source:** `src/orchestrators/` directory + CORTEX.prompt.md  
**Value Proposition:** **7-state lifecycle management** - How orchestrators execute from INIT → COMPLETE with quarantine failsafes  
**Technical Depth:** State machines, transition validation, middleware pipeline (5 layers), correlation ID propagation, incremental execution  

**Features Required:**
- **� 7-State Lifecycle State Machine (D3.js Interactive)**
  - States: 
    1. **INIT** → Orchestrator instantiated, config loaded
    2. **PLANNING** → Analyzing request, creating execution plan
    3. **EXECUTING** → Running tasks (RED/GREEN/REFACTOR for TDD)
    4. **VALIDATING** → Running tests, checking governance compliance
    5. **REPORTING** → Generating evidence bundle, updating tracker
    6. **COMPLETE** → Success, AC-ID marked implemented
    7. **FAILED** → Error occurred, orchestrator quarantined
  
  - Interactive: Click state → Show details (duration, typical operations, exit conditions)
  - Transitions: Arrows showing valid transitions (INIT→PLANNING, PLANNING→EXECUTING, EXECUTING→VALIDATING, etc.)
  - Invalid transitions: Red dashed line (e.g., INIT→VALIDATING blocked)
  - Real-time: Highlight current state for active orchestrators

- **🛡️ Middleware Pipeline (Layered Diagram - Mermaid)**
  ```mermaid
  flowchart TD
    REQ[Request] --> L1[Layer 1: Logging]
    L1 --> L2[Layer 2: Validation]
    L2 --> L3[Layer 3: Transformation]
    L3 --> L4[Layer 4: Security]
    L4 --> L5[Layer 5: Response Formatting]
    L5 --> ORCH[Orchestrator Execution]
    ORCH --> L5R[Layer 5: Format Response]
    L5R --> L4R[Layer 4: Security Check]
    L4R --> L3R[Layer 3: Transform Output]
    L3R --> L2R[Layer 2: Validate Output]
    L2R --> L1R[Layer 1: Log Completion]
    L1R --> RESP[Response to User]
    
    style L1 fill:#06ffa5
    style L2 fill:#00d4ff
    style L3 fill:#7b2cbf
    style L4 fill:#ff006e
    style L5 fill:#ffbe0b
  ```
  
  - **Layer Details:**
    - **L1 (Logging):** Generate correlation ID, log request start
    - **L2 (Validation):** Check input schema, validate AC-ID format
    - **L3 (Transformation):** Add domain context, enrich request
    - **L4 (Security):** Check permissions, validate file paths
    - **L5 (Response):** Format output per response-templates-v4.yaml
  
  - Hover layer: Show example operations
  - Toggle: View request flow vs response flow

- **🔗 Correlation ID Propagation (Trace Diagram)**
  - Show correlation ID flow across components:
    ```
    User Request [corr-123]
      → MasterOrchestrator [corr-123]
        → GovernanceMerger [corr-123]
        → TodoManager [corr-123]
          → TDD-Master [corr-123]
            → AuditLogger [corr-123] ← All logs tagged
    ```
  - Click correlation ID: Query all audit logs for that ID
  - Timeline: Show duration spent in each component
  - Branching: Show parallel task execution (fan-out/fan-in)

- **⚙️ Incremental Execution Strategy (Animation)**
  - Visualize CORE-001 enforcement:
    - Large request (1000 lines) split into 2 × 500-line increments
    - Progress bar: 50% → Checkpoint saved → Resume from checkpoint
    - Token usage: 75% → Save state → Continue next turn
  - Code example:
    ```python
    # Incremental executor
    for batch in chunk(large_task, increment_size=500):
        execute_batch(batch)
        save_checkpoint({
            "completed": batch_index,
            "remaining": len(batches) - batch_index - 1,
            "state": current_state
        })
        if token_usage > 0.8:
            return {"status": "partial", "resume_from": batch_index + 1}
    ```

- **📊 Orchestrator Performance Metrics (Chart.js Dashboard)**
  - Average execution time by orchestrator:
    - TDD-Master: 12.3s
    - Planning v5: 8.7s
    - Vacuum v2: 3.2s
  - State duration breakdown: PLANNING (2s), EXECUTING (8s), VALIDATING (1s), REPORTING (1s)
  - Failure rate: TDD-Master (0.3%), Planning (0.1%), Vacuum (0%)
  - Quarantine recovery: 95% of quarantined orchestrators recovered after fix

**Visualizations:**
1. **State Machine** - D3.js with interactive nodes and transitions
2. **Middleware Pipeline** - Mermaid layered flowchart (request/response)
3. **Correlation Trace** - Timeline diagram with branching
4. **Performance Dashboard** - Chart.js multi-metric view

**Value Metrics:**
- Orchestrator Count: 12+ specialized orchestrators
- Lifecycle States: 7 (with transition validation)
- Middleware Layers: 5 (request + response)
- Incremental Execution: <500 lines per increment (CORE-001)

---

### TODO: Create `autonomous-execution-deep-dive.html`
**Source:** `src/orchestrators/autonomous/autonomous_ac_implementor.py` + TDD-Master + Planning v5  
**Value Proposition:** **Zero-touch implementation** - How CORTEX implements AC-IDs autonomously from request to evidence bundle  
**Technical Depth:** TDD RED→GREEN→REFACTOR cycles, git history intelligence, stub fallback, test-gated progress tracking  

**Features Required:**
- **🔁 TDD Cycle Animation (Interactive)**
  - **Step 1: RED Phase**
    - Write failing test first
    - Example: `test_calculate_design_score()` → AssertionError (not implemented)
    - Code view: Show test file with failing test highlighted
    - Terminal output: Pytest shows 1 failed, 0 passed
  
  - **Step 2: GREEN Phase**
    - Write minimal implementation to pass test
    - Example: `calculate_design_score()` returns hardcoded value
    - Code view: Show implementation file with basic logic
    - Terminal output: Pytest shows 1 passed, 0 failed
  
  - **Step 3: REFACTOR Phase**
    - Improve code quality while tests pass
    - Example: Replace hardcoded value with actual calculation
    - Code view: Show refactored implementation (cleaner, more efficient)
    - Terminal output: Pytest shows 1 passed, 0 failed (still passing)
  
  - Animation: Play/Pause/Step through cycle
  - Code diff: Show changes between phases (RED→GREEN, GREEN→REFACTOR)

- **🔍 Git History Intelligence (Search & Extract)**
  - **Search Flow:**
    ```mermaid
    flowchart LR
      REQ[User: "implement OAuth"] --> SEARCH[Search git history]
      SEARCH --> BRANCHES[Check CORTEX-5.5, 5.0, 4.0]
      BRANCHES --> FOUND{Found?}
      FOUND -->|Yes| EXTRACT[Extract + Transform]
      FOUND -->|No| CREATE[Create from scratch]
      EXTRACT --> IMPL[Implement]
      CREATE --> IMPL
    ```
  
  - **Available Branches:** CORTEX-5.5, 5.0, 4.0, 3.0, 2.0, 1.0
  - **Search Examples:**
    - Query: "authentication oauth" → Found in CORTEX-4.0
    - Extract: `src/crawlers/git_history_analyzer.py`
    - Transform: Update to CORTEX 6.0 governance model
  
  - Code view: Side-by-side comparison (old vs transformed)
  - Stats: 73% of AC-IDs reused from git history (not recreated)

- **🛡️ Stub Fallback Mechanism (Decision Tree)**
  ```mermaid
  flowchart TD
    START[Autonomous Implementer] --> SEARCH{Search Git History}
    SEARCH -->|Found| EXTRACT[Extract & Transform]
    SEARCH -->|Not Found| GENERATE[Generate New Code]
    
    EXTRACT --> VALIDATE{Tests Pass?}
    GENERATE --> VALIDATE
    
    VALIDATE -->|Yes| COMPLETE[Mark Implemented]
    VALIDATE -->|No| RETRY{Retry Count < 3?}
    
    RETRY -->|Yes| REFACTOR[Refactor & Re-test]
    RETRY -->|No| STUB[Create Stub Fallback]
    
    REFACTOR --> VALIDATE
    STUB --> QUARANTINE[Quarantine for Manual Fix]
    
    style COMPLETE fill:#06ffa5
    style STUB fill:#ff006e
    style QUARANTINE fill:#ff006e
  ```
  
  - **Stub Creation:** When autonomous implementation fails after 3 retries
  - **Quarantine:** Stub flagged for manual intervention
  - **Purpose:** Graceful degradation (not fake implementation)
  - **Detection:** Evidence bundle shows stub status + retry logs

- **✅ Test-Gated Progress Tracking (Enforcement Flow)**
  ```mermaid
  flowchart LR
    IMPL[Code Implemented] --> TESTS[Run Tests]
    TESTS --> PASS{All Tests Pass?}
    PASS -->|Yes| UPDATE[Update progress-tracker.json]
    PASS -->|No| PARTIAL[Mark as 'partial']
    UPDATE --> BUNDLE[Generate Evidence Bundle]
    PARTIAL --> VERIFY[Add to needs_verification]
    BUNDLE --> COMPLETE[AC-ID Complete]
    VERIFY --> MANUAL[Manual Review Required]
    
    style COMPLETE fill:#06ffa5
    style MANUAL fill:#ffbe0b
  ```
  
  - **Gate Enforcement:** Tests MUST pass before marking "implemented"
  - **False Positive Prevention:** Blocks status update if tests fail
  - **Evidence Bundle:** Only generated for passing implementations
  - **Example:** AC-AUDIT-007 marked "planned" because 2/5 tests failed

- **📈 Autonomous Success Metrics (Chart.js)**
  - Success rate: 87% fully autonomous (no manual intervention)
  - Partial success: 10% (needs refactoring)
  - Stub fallback: 3% (manual fix required)
  - Git history reuse: 73% (extracted from previous versions)
  - Average implementation time: 8.3 minutes per AC-ID

**Visualizations:**
1. **TDD Cycle Animation** - Step-through interactive view with code diffs
2. **Git History Flow** - Mermaid flowchart showing search/extract/transform
3. **Decision Tree** - Stub fallback logic with retry mechanism
4. **Test-Gated Flow** - Enforcement diagram showing gates
5. **Success Metrics** - Chart.js pie chart with breakdown

**Value Metrics:**
- Autonomous Success Rate: 87% (no human intervention)
- Git History Reuse: 73% (not recreated from scratch)
- Test Coverage: ≥80% (enforced by AC-TEST-002)
- False Positive Prevention: 100% (test-gated tracking)

---

### TODO: Create `token-optimization-strategy.html`
**Source:** CORTEX.prompt.md + core-rules.yaml (CORE-001)  
**Value Proposition:** **Cost efficiency** - How CORTEX prevents HTTP 502 errors and optimizes LLM costs through incremental execution  
**Technical Depth:** Token budgeting, checkpoint/resume patterns, Claude Sonnet vs Opus cost analysis, context window management  

**Features Required:**
- **💰 LLM Cost Comparison (Chart.js Stacked Area)**
  - Compare costs over 8-week implementation:
    - **Scenario 1:** 100% Claude Opus 4.5 → $1,247/month
    - **Scenario 2:** 90% Sonnet, 10% Opus (RECOMMENDED) → $423/month  
    - **Scenario 3:** 100% Claude Sonnet 4.5 → $378/month
  - Breakdown by phase: Foundation (Week 1-2), Core (Week 3-4), Features (Week 5-6), Intelligence (Week 7-8)
  - ROI calculation: "66% cost savings with 10% Opus for critical decisions"

- **⚡ Incremental Execution Pattern (Interactive Animation)**
  - **Scenario:** User requests "implement 50 AC-IDs"
  - **Bad Approach (Monolithic):**
    ```python
    # ❌ Causes HTTP 502 (token overflow)
    for ac_id in all_50_ac_ids:
        implement(ac_id)  # 50 × 2000 tokens = 100K tokens → CRASH
    ```
  - **CORTEX Approach (Incremental):**
    ```python
    # ✅ Process in batches of 5 AC-IDs
    for batch in chunk(all_50_ac_ids, batch_size=5):
        for ac_id in batch:
            implement(ac_id)
        save_checkpoint()  # Resume point
        # Token usage: 5 × 2000 = 10K tokens ✅ SAFE
    ```
  
  - Animation: Show progress bar with checkpoints (10%, 20%, ..., 100%)
  - Token gauge: Real-time token usage vs limit (green <80%, yellow 80-95%, red >95%)

- **📊 Token Budget Allocation (D3.js Sunburst Chart)**
  - Center: Total tokens per request (e.g., 200K for Claude Sonnet)
  - Rings:
    - Ring 1: Phase allocation (Foundation: 50K, Core: 80K, Features: 40K, Intelligence: 30K)
    - Ring 2: Component allocation (Orchestrator: 20K, Tests: 15K, Evidence: 5K)
    - Ring 3: Safety margin (20% reserved for response formatting)
  - Interactive: Click segment → see detailed breakdown

- **🧠 Claude Sonnet vs Opus Decision Matrix**
  | Capability | Sonnet 4.5 (1x cost) | Opus 4.5 (3x cost) | Recommendation |
  |------------|----------------------|--------------------|----------------|
  | **Code Generation** | ✅ Excellent | ✅ Excellent | Use Sonnet (no advantage) |
  | **TDD Cycles** | ✅ Excellent | ✅ Excellent | Use Sonnet (proven reliable) |
  | **Architecture Design** | ⚠️ Good | ✅ Superior | Use Opus (10% of work) |
  | **Challenge Protocol** | ⚠️ Good | ✅ Superior | Use Opus (critical analysis) |
  | **Refactoring Legacy** | ⚠️ Good | ✅ Superior | Use Opus (complex transforms) |
  | **Governance Validation** | ✅ Excellent | ✅ Excellent | Use Sonnet (rule matching) |
  | **Evidence Bundle Gen** | ✅ Excellent | ✅ Excellent | Use Sonnet (structured output) |
  
  - **Verdict:** 90% Sonnet, 10% Opus = 66% cost savings with <5% quality trade-off

**Visualizations:**
1. **Stacked Area Chart** - LLM cost comparison over 8 weeks
2. **Token Gauge** - Real-time usage vs limit (speedometer style)
3. **Sunburst Chart** - Token budget allocation by phase/component
4. **Decision Matrix Table** - Sonnet vs Opus capabilities

**Value Metrics:**
- Cost Savings: 66% (90% Sonnet vs 100% Opus)
- HTTP 502 Prevention: 100% (no token overflow errors)
- Checkpoint Frequency: Every 5 AC-IDs or 80% token usage
- Context Window Efficiency: 85% average utilization (optimized)

---

### TODO: Create `ado-integration-capabilities.html`
**Source:** Azure DevOps orchestrators + ADO API documentation  
**Value Proposition:** **Seamless ALM integration** - How CORTEX automates work item creation, sprint tracking, and evidence linking  
**Technical Depth:** ADO API authentication, work item hierarchy, evidence attachment automation, bi-directional sync  

**Features Required:**
- **🔗 Work Item Hierarchy (D3.js Tree Diagram)**
  ```
  Epic: CORTEX 6.0 Implementation
    ├── Feature: Phase 1 Foundation
    │   ├── PBI: AC-AUDIT-001 (Queryable Audit Storage)
    │   │   ├── Task: Implement SQLite backend
    │   │   ├── Task: Add AC-ID traceability
    │   │   └── Task: Write tests
    │   ├── PBI: AC-AUDIT-002 (Memory Buffer)
    │   └── PBI: AC-AUDIT-003 (7 Audit Categories)
    └── Feature: Phase 2 Orchestration Core
        ├── PBI: AC-TODO-001 (TodoManager Core)
        └── PBI: AC-TDD-001 (TDD Orchestrator)
  ```
  - Interactive: Expand/collapse nodes
  - Click work item: Open in ADO (deep link)
  - Color-coded by state: New (gray), Active (blue), Resolved (green), Closed (purple)

- **📋 Automated Work Item Creation (Flowchart)**
  ```mermaid
  flowchart TD
    START[AC-ID Defined] --> AUTH[ADO API Authentication]
    AUTH --> CREATE_PBI[Create Product Backlog Item]
    CREATE_PBI --> FIELDS[Set Fields: Title, Description, AC]
    FIELDS --> LINK_EPIC[Link to Parent Epic]
    LINK_EPIC --> CREATE_TASKS[Create Child Tasks]
    CREATE_TASKS --> SPRINT[Assign to Sprint]
    SPRINT --> NOTIFY[Notify Team via Email]
    
    style CREATE_PBI fill:#00d4ff
    style LINK_EPIC fill:#7b2cbf
    style CREATE_TASKS fill:#06ffa5
  ```

- **📎 Evidence Bundle Attachment (Sequence)**
  - Upload to Azure Blob Storage
  - Attach URL to ADO PBI as comment
  - Evidence bundle contents: manifest, test results, audit trace

- **🔄 Bi-Directional Sync (State Machine)**
  - CORTEX → ADO: progress-tracker.json updates PBI state
  - ADO → CORTEX: PBI state updates progress-tracker.json
  - Sync frequency: Every 15 minutes
  - Conflict resolution: CORTEX wins (source of truth)

- **📊 Sprint Progress Dashboard (Chart.js)**
  - Burndown chart: Remaining story points vs ideal
  - Velocity chart: Story points completed per sprint
  - Work item state distribution: New, Active, Resolved, Closed

**Visualizations:**
1. **Tree Diagram** - Work item hierarchy with expand/collapse
2. **Flowchart** - Automated work item creation process
3. **Sequence Diagram** - Evidence bundle attachment flow
4. **Burndown Chart** - Sprint progress tracking
5. **Velocity Chart** - Team velocity over sprints

**Value Metrics:**
- Automation Coverage: 95% (work item creation, evidence attachment, state sync)
- Manual Effort Reduction: 87% (vs manual ADO updates)
- Sync Accuracy: 99.3% (bi-directional consistency)
- Evidence Traceability: 100% (all PBIs have evidence bundles)

---

### TODO: Create `progress-tracker-dashboard.html`
**Source:** `cortex-brain/tier1/tracking/progress-tracker.json`  
**Features Required:**
- Real-time phase status cards
- Blockers timeline with resolution tracking
- Completed AC-IDs grid (color-coded)
- Velocity chart (AC-IDs per week)
- Burndown chart with projections
- Auto-refresh every 30 seconds

**Visualizations:**
- Velocity chart: Completed AC-IDs over time
- Burndown: Remaining work vs ideal trajectory
- Gantt: Active tasks and blockers

---

### TODO: Create `ac-index-explorer.html`
**Source:** `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`  
**Features Required:**
- Searchable/filterable AC-ID registry (DataTables)
- Dependency graph (D3.js)
- Status badges (Implemented/Partial/Planned)
- Category grouping and sorting
- Export to CSV/JSON
- Quick stats: Total, Completed, Remaining

**Visualizations:**
- Network graph: AC-ID dependencies
- Treemap: AC-IDs grouped by category
- Status distribution pie chart

---

### TODO: Create `evidence-bundle-viewer.html`
**Source:** `cortex-brain/tier1/evidence-bundles/`  
**Features Required:**
- Bundle completeness cards (Tests/Audit/Manifest)
- Test coverage map (file-level)
- Audit trail viewer with search
- Evidence artifact links
- Bundle validation status

**Visualizations:**
- Progress rings: Bundle completeness %
- Tree map: Evidence artifacts by type
- Timeline: Bundle creation dates

---

## 🔗 Supporting Visualizations (Priority: LOW)

### TODO: Create `phase-dependencies.html`
**Features Required:**
- Critical path highlighting (D3.js)
- Milestone markers
- Completion predictions (based on velocity)
- Dependency constraints visualization
- What-if scenario simulator

**Visualizations:**
- PERT chart: Phase dependencies
- Critical path highlighted in red
- Milestone diamonds on timeline

---

### TODO: Create `test-coverage-report.html`
**Source:** Coverage data from pytest  
**Features Required:**
- File-level heatmap (D3.js)
- Trend charts (Chart.js)
- Uncovered line explorer
- Module coverage breakdown
- Test execution time analysis

**Visualizations:**
- Heatmap: Files colored by coverage %
- Line chart: Coverage trend over commits
- Bar chart: Coverage by module

---

### TODO: Create `audit-trail-explorer.html`
**Source:** `cortex-brain/audit-logs/`  
**Features Required:**
- Searchable log entries (text search + filters)
- Category distribution (Chart.js)
- Timeline visualization (D3.js)
- Error rate tracking
- Component activity heatmap
- Export filtered logs to JSON

**Visualizations:**
- Timeline: Log entries over time
- Donut: Logs by category
- Heatmap: Activity by hour/day

---

## 🎨 Design Requirements (All Views)

**Visual Style:**
- ✅ Dark theme matching `cortex-plan-viewer.html`
- ✅ CORTEX color palette:
  - Cyan: `#00d4ff` (primary)
  - Purple: `#7b2cbf` (secondary)
  - Pink: `#ff006e` (accent)
  - Green: `#06ffa5` (success)
  - Yellow: `#ffbe0b` (warning)
- ✅ Glassmorphism cards with backdrop blur
- ✅ Smooth animations and transitions

**Typography:**
- ✅ Base font size: `16px`
- ✅ Line height: `1.6` for body text
- ✅ Font family: `'Segoe UI', system-ui, -apple-system, sans-serif`
- ✅ Headings: Bold with gradient text effects
- ✅ Code blocks: `'Fira Code', 'Courier New', monospace`

**Libraries:**
- ✅ Bootstrap 5.3.2 (responsive grid)
- ✅ Chart.js 4.4.1 (statistical charts)
- ✅ D3.js v7 (complex visualizations)
- ✅ Mermaid.js 10.6.1 (diagrams)
- ✅ Bootstrap Icons 1.11.3

**Interactive Elements:**
- ✅ Search bars with live filtering
- ✅ Collapsible sections (accordion)
- ✅ Tooltips on hover (Bootstrap)
- ✅ Export buttons (PNG for charts, PDF for pages)
- ✅ Breadcrumb navigation
- ✅ "View Source" button to show markdown

**Responsive Design:**
- ✅ Mobile-first approach
- ✅ Breakpoints: sm (576px), md (768px), lg (992px), xl (1200px)
- ✅ Charts resize on window resize
- ✅ Touch-friendly controls on mobile

---

## 📦 Implementation Guidelines

### File Organization
```
cortex-brain/cx6-plan/viewer/
├── implementation-roadmap.html
├── gap-analysis.html
├── master-plan.html
├── phase1-verification.html
├── sts-implementation-summary.html
├── holistic-verification.html
├── cortex-instructions.html
├── core-rules-viewer.html
├── governance-architecture.html
├── progress-tracker-dashboard.html
├── ac-index-explorer.html
├── evidence-bundle-viewer.html
├── phase-dependencies.html
├── test-coverage-report.html
├── audit-trail-explorer.html
├── shared/
│   ├── styles.css (common styles)
│   ├── charts.js (Chart.js configurations)
│   ├── d3-utils.js (D3.js helper functions)
│   └── data-loader.js (JSON/YAML loaders)
└── assets/
    └── images/ (logos, icons)
```

### Development Workflow
1. Create HTML skeleton with Bootstrap layout
2. Add breadcrumb navigation to main dashboard
3. Implement data loading from source files
4. Create visualizations (D3.js/Chart.js/Mermaid)
5. Add interactive elements (search, filter, export)
6. Test on multiple screen sizes
7. Update `cortex-plan-viewer.html` links
8. Verify all links work from local server

### Testing Checklist
- [ ] Renders correctly in Chrome, Firefox, Safari
- [ ] Responsive on mobile (375px width)
- [ ] All visualizations load without errors
- [ ] Data updates reflect in real-time (if applicable)
- [ ] Export functionality works
- [ ] No console errors
- [ ] Accessible (ARIA labels, keyboard navigation)
- [ ] Fast load time (<2 seconds)

---

## 🚀 Priority Order

### Phase 1: Critical Views (Week 1)
1. ✅ **implementation-roadmap.html** - Roadmap is the north star
2. ✅ **progress-tracker-dashboard.html** - Live tracking essential
3. ✅ **ac-index-explorer.html** - AC-ID reference critical

### Phase 2: Quality & Verification (Week 2)
4. ⏳ **gap-analysis.html** - Understand completion gaps
5. ⏳ **phase1-verification.html** - Validate Phase 1
6. ⏳ **core-rules-viewer.html** - Governance transparency

### Phase 3: Architecture & Docs (Week 3)
7. ⏳ **cortex-instructions.html** - Onboarding new devs
8. ⏳ **governance-architecture.html** - System design clarity
9. ⏳ **sts-implementation-summary.html** - STS validation proof

### Phase 4: Supporting Views (Week 4)
10. ⏳ **evidence-bundle-viewer.html**
11. ⏳ **holistic-verification.html**
12. ⏳ **test-coverage-report.html**
13. ⏳ **audit-trail-explorer.html**
14. ⏳ **phase-dependencies.html**
15. ⏳ **master-plan.html** (complex, save for last)

---

## 📝 Technical Notes

**Local Development Server:**
```bash
cd /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/cx6-plan/viewer
python3 -m http.server 8000
# Open: http://localhost:8000/cortex-plan-viewer.html
```

**Relative Path Resolution:**
All data files use relative paths from viewer directory:
- `../../cortex-brain/cx6-plan/implementation-roadmap.md`
- `../../cortex-brain/tier1/tracking/progress-tracker.json`
- `../../cortex-brain/tier0/governance/core-rules.yaml`

**Data Loading Pattern:**
```javascript
// Example: Load JSON
fetch('../../cortex-brain/tier1/tracking/progress-tracker.json')
    .then(res => res.json())
    .then(data => renderDashboard(data));

// Example: Load YAML (requires js-yaml library)
fetch('../../cortex-brain/tier0/governance/core-rules.yaml')
    .then(res => res.text())
    .then(yamlText => {
        const data = jsyaml.load(yamlText);
        renderRules(data);
    });
```

**Chart.js Configuration Template:**
```javascript
const ctx = document.getElementById('myChart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4'],
        datasets: [{
            label: 'AC-IDs Completed',
            data: [16, 0, 0, 0],
            backgroundColor: '#00d4ff'
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#fff' } }
        },
        scales: {
            y: { ticks: { color: '#fff' } },
            x: { ticks: { color: '#fff' } }
        }
    }
});
```

**D3.js Network Graph Template:**
```javascript
const svg = d3.select('#graph')
    .append('svg')
    .attr('width', width)
    .attr('height', height);

const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id))
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter(width / 2, height / 2));
```

---

## 🔗 Related Files

- Main Dashboard: `cortex-brain/cx6-plan/viewer/cortex-plan-viewer.html`
- Styles Reference: Extract styles from main dashboard
- Data Sources: `cortex-brain/cx6-plan/`, `cortex-brain/tier1/`, `cortex-brain/tier0/`
- Test Data: `tests/fixtures/` for mock data during development

---

## ✅ Acceptance Criteria

**Each HTML view must:**
1. ✅ Load and render all data without errors
2. ✅ Display text at readable font size (16px minimum)
3. ✅ Include at least one interactive visualization
4. ✅ Match CORTEX dark theme color scheme
5. ✅ Be responsive on desktop, tablet, mobile
6. ✅ Have breadcrumb navigation back to dashboard
7. ✅ Include "View Source" button to show markdown
8. ✅ Load in under 2 seconds on local server
9. ✅ Have no console errors or warnings
10. ✅ Export functionality for charts/data

---

**Last Updated:** 2026-01-11  
**Status:** TODO list ready for implementation  
**Next Step:** Begin Phase 1 implementation with `implementation-roadmap.html`
