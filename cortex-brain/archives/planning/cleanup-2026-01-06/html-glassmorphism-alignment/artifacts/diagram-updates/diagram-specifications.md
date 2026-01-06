# 🔷 Mermaid Diagram Specifications for Phase 7d

**Plan:** html-glassmorphism-alignment  
**Phase:** 7d - Diagram & Illustration Updates  
**Created:** 2026-01-04

---

## 📊 Diagram 1: Plan Viewer Architecture & Data Flow

**File:** `plan-viewer-architecture.mmd`  
**Purpose:** Show Plan Viewer component architecture + data flow from plans-index.json

```mermaid
graph TD
    subgraph "CORTEX Brain"
        Plans[("📁 Active Plans<br/>cortex-brain/documents/planning/active/")]
        Metadata["📋 Plan Metadata<br/>(YAML frontmatter)"]
    end
    
    subgraph "Metadata Generator"
        Script["🐍 generate-plans-index.py"]
        Parser["Parse YAML frontmatter"]
        Aggregator["Aggregate all plans"]
    end
    
    subgraph "Data Layer"
        JSON[("📄 plans-index.json<br/>cortex-lens-output/data/")]
    end
    
    subgraph "CORTEX-LENS UI"
        Index["🏠 index.html<br/>(Multi-tab dashboard)"]
        Viewer["🧠 plan-viewer.html<br/>(Plan progress view)"]
        JS["💻 plan-viewer.js<br/>(Rendering engine)"]
    end
    
    subgraph "User Interface"
        Sidebar["📋 Plan List Sidebar<br/>(Search + Filter)"]
        Detail["📊 Plan Detail View<br/>(Phases + ACs)"]
        Progress["📈 Progress Bars"]
        Links["🔗 Cross-Links to Repo Lens"]
    end
    
    Plans --> Metadata
    Metadata --> Parser
    Parser --> Aggregator
    Aggregator --> JSON
    Script --> Parser
    
    JSON --> JS
    Index --> Viewer
    Viewer --> JS
    
    JS --> Sidebar
    JS --> Detail
    Detail --> Progress
    Detail --> Links
    
    Links -.->|"View in Repository Lens"| RepoLens["🔍 Repository Lens<br/>(AST code view)"]
    
    style JSON fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Viewer fill:#2196F3,stroke:#1565C0,color:#fff
    style RepoLens fill:#FF9800,stroke:#E65100,color:#fff
```

**Usage:** `docs/orchestrators/cortex-lens-architecture.html`

---

## 🌳 Diagram 2: Epic vs. Feature Decision Tree

**File:** `epic-vs-feature-decision-tree.mmd`  
**Purpose:** Help users decide when to use Epic planning vs. Feature planning

```mermaid
graph TD
    Start["🚀 User Request:<br/>Planning Orchestrator"]
    
    Complexity{"📊 Complexity Score<br/>(0-100)"}
    
    Points{"🎯 Story Points<br/>(Fibonacci)"}
    
    Epic{"≥21 Story Points?"}
    
    EpicFlow["✅ EPIC PLANNING<br/>Hierarchical breakdown"]
    FeatureFlow["✅ FEATURE PLANNING<br/>Flat breakdown"]
    
    EpicStructure["📦 Structure:<br/>Epic → Features (2-5)<br/>→ Stories (3-7 per feature)<br/>→ Tasks (2-4 per story)"]
    
    FeatureStructure["📦 Structure:<br/>Feature → Stories (2-4)<br/>→ Tasks (2-3 per story)"]
    
    Examples1["📋 Examples:<br/>• E-commerce platform (55 SP)<br/>• Multi-app refactor (34 SP)<br/>• Major system migration (21+ SP)"]
    
    Examples2["📋 Examples:<br/>• User login feature (13 SP)<br/>• API endpoint (8 SP)<br/>• Bug fix initiative (5 SP)"]
    
    Start --> Complexity
    Complexity -->|"0-30"| Points
    Complexity -->|"31-60"| Points
    Complexity -->|"61-100"| Points
    
    Points -->|"1,2,3,5,8,13"| Epic
    Points -->|"21,34,55"| Epic
    
    Epic -->|"YES"| EpicFlow
    Epic -->|"NO"| FeatureFlow
    
    EpicFlow --> EpicStructure
    EpicStructure --> Examples1
    
    FeatureFlow --> FeatureStructure
    FeatureStructure --> Examples2
    
    style Epic fill:#FF5722,stroke:#D84315,color:#fff
    style EpicFlow fill:#4CAF50,stroke:#2E7D32,color:#fff
    style FeatureFlow fill:#2196F3,stroke:#1565C0,color:#fff
```

**Usage:** `docs/orchestrators/planning-v5-epic-vs-feature.html`

---

## 🔄 Diagram 3: Plan Viewer ↔ Repository Lens Cross-Linking

**File:** `plan-repo-lens-cross-linking.mmd`  
**Purpose:** Show bidirectional cross-linking between Plan Viewer and Repository Lens

```mermaid
sequenceDiagram
    participant User
    participant PlanViewer as 🧠 Plan Viewer
    participant TabRouter as 🔀 Tab Router
    participant RepoLens as 🔍 Repository Lens
    participant AST as 📄 repo-ast.json
    participant PlansIndex as 📋 plans-index.json
    
    Note over User,PlansIndex: Scenario 1: Plan → Code Navigation
    
    User->>PlanViewer: View plan "html-glassmorphism-alignment"
    PlanViewer->>PlansIndex: Load plan metadata
    PlansIndex-->>PlanViewer: Return linked_files: ["docs/index.html", ...]
    
    PlanViewer->>User: Show "Linked Files" section
    User->>PlanViewer: Click "View docs/index.html in Repository Lens"
    
    PlanViewer->>TabRouter: switchTab('repository-lens', context={file: 'docs/index.html'})
    TabRouter->>RepoLens: Activate + pass context
    
    RepoLens->>AST: Load file tree
    AST-->>RepoLens: Return AST data
    RepoLens->>RepoLens: Highlight file in tree
    RepoLens->>RepoLens: Scroll to file location
    RepoLens->>User: Display file with AST analysis
    
    Note over User,PlansIndex: Scenario 2: Code → Plan Navigation (Reverse)
    
    User->>RepoLens: Browse file "src/orchestrators/planning/planning_orchestrator.py"
    RepoLens->>PlansIndex: Query plans that reference this file
    PlansIndex-->>RepoLens: Return [{plan: "planning-v5", phase: "Phase 3"}, ...]
    
    RepoLens->>User: Show "Referenced in Plans:" section
    User->>RepoLens: Click "View planning-v5 plan"
    
    RepoLens->>TabRouter: switchTab('plan-viewer', context={planId: 'planning-v5'})
    TabRouter->>PlanViewer: Activate + pass context
    
    PlanViewer->>PlansIndex: Load plan metadata
    PlansIndex-->>PlanViewer: Return plan data
    PlanViewer->>User: Display plan with Phase 3 highlighted
```

**Usage:** `docs/orchestrators/cortex-lens-architecture.html`

---

## 🧠 Diagram 4: Phase -1 Knowledge Library Flow

**File:** `phase-minus-1-knowledge-library-flow.mmd`  
**Purpose:** Show how Phase -1 queries Knowledge Library before plan creation

```mermaid
graph TD
    Start["🚀 Planning Orchestrator<br/>Receives user request"]
    
    Phase0["⏸️ Phase -1: Knowledge Library Query<br/>(PRE-PLANNING)"]
    
    Query["🔍 Query Tier 0 + Tier 2"]
    
    Tier0["📜 Tier 0: Governance<br/>SKULL rules, constraints"]
    Tier2["🧠 Tier 2: Knowledge Graph<br/>Lessons learned, past plans"]
    
    Results{"📊 Relevant<br/>Knowledge Found?"}
    
    Inject["💉 Inject context into plan"]
    Warnings["⚠️ Add governance warnings"]
    Recommendations["💡 Add recommendations"]
    
    Phase0Plan["📋 Phase 0: Context Discovery<br/>(WITH pre-loaded knowledge)"]
    
    Start --> Phase0
    Phase0 --> Query
    Query --> Tier0
    Query --> Tier2
    
    Tier0 --> Results
    Tier2 --> Results
    
    Results -->|"YES"| Inject
    Results -->|"NO"| Phase0Plan
    
    Inject --> Warnings
    Warnings --> Recommendations
    Recommendations --> Phase0Plan
    
    Phase0Plan --> Continue["➡️ Continue with<br/>Phases 1-N"]
    
    style Phase0 fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style Tier0 fill:#FF5722,stroke:#D84315,color:#fff
    style Tier2 fill:#4CAF50,stroke:#2E7D32,color:#fff
```

**Usage:** `docs/orchestrators/planning-v5.html` (Phase -1 section)

---

## 🔍 Diagram 5: AST Scanning Integration in Planning v5

**File:** `ast-scanning-planning-v5.mmd`  
**Purpose:** Show how AST scanning integrates into Planning v5 workflow

```mermaid
graph TD
    Start["🚀 Planning Orchestrator<br/>Phase 0: Context Discovery"]
    
    Discover["🔍 Discover relevant files<br/>(file_search, semantic_search)"]
    
    AST{"🤖 AST Scanning<br/>Available?"}
    
    NoAST["⏭️ Skip AST<br/>(basic context only)"]
    
    ScanFiles["📊 Scan files with AST<br/>(Sub-Plan 04)"]
    
    Extract["🔎 Extract:<br/>• Function signatures<br/>• Class hierarchies<br/>• Dependencies<br/>• Complexity metrics"]
    
    Inject["💉 Inject AST data<br/>into plan phases"]
    
    PhaseExample["📋 Example Phase 3:<br/>'Update calculate_total() function'<br/>+ AST shows current signature:<br/>  def calculate_total(items: List[Item]) -> float"]
    
    Benefit["✅ Benefits:<br/>• Accurate refactoring guidance<br/>• Breaking change detection<br/>• Test coverage mapping"]
    
    Start --> Discover
    Discover --> AST
    
    AST -->|"NO"| NoAST
    AST -->|"YES"| ScanFiles
    
    ScanFiles --> Extract
    Extract --> Inject
    Inject --> PhaseExample
    PhaseExample --> Benefit
    
    NoAST --> Continue["➡️ Continue with<br/>basic context"]
    Benefit --> Continue
    
    style AST fill:#FF9800,stroke:#E65100,color:#fff
    style Extract fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Benefit fill:#2196F3,stroke:#1565C0,color:#fff
```

**Usage:** `docs/orchestrators/planning-v5.html` (AST Scanning section)

---

## 🔧 Diagram 6: Context Middleware Priority Logic

**File:** `context-middleware-priority-logic.mmd`  
**Purpose:** Show how Context Middleware prioritizes context sources

```mermaid
sequenceDiagram
    participant User
    participant Router as Toolkit Manager
    participant Middleware as Context Middleware
    participant Sources as Context Sources
    participant Orch as Orchestrator
    
    User->>Router: User request: "Fix the login bug"
    Router->>Middleware: load_context(request, orchestrator="debug")
    
    Note over Middleware,Sources: Priority 1: Session Context
    Middleware->>Sources: Query active session
    Sources-->>Middleware: Return: Previous context (10 KB)
    
    Note over Middleware,Sources: Priority 2: Git Context
    Middleware->>Sources: Query git status
    Sources-->>Middleware: Return: Modified files (5 KB)
    
    Note over Middleware,Sources: Priority 3: File Discovery
    Middleware->>Sources: semantic_search("login bug")
    Sources-->>Middleware: Return: Relevant files (20 KB)
    
    Note over Middleware,Sources: Priority 4: Knowledge Library
    Middleware->>Sources: Query Tier 2 (similar issues)
    Sources-->>Middleware: Return: Past solutions (15 KB)
    
    Middleware->>Middleware: Calculate total: 50 KB<br/>Budget: 100 KB → ✅ PASS
    
    Middleware->>Orch: Inject context (50 KB)
    Orch->>User: Execute with enriched context
    
    Note over Middleware: Budget Exceeded Scenario
    
    Middleware->>Middleware: Calculate total: 120 KB<br/>Budget: 100 KB → ❌ FAIL
    
    Middleware->>Middleware: Prioritize:<br/>1. Session (10 KB) ✅<br/>2. Git (5 KB) ✅<br/>3. File Discovery (20 KB) ✅<br/>4. Knowledge Library (15 KB) → ❌ TRIM to 5 KB
    
    Middleware->>Orch: Inject context (40 KB trimmed)
```

**Usage:** `docs/features/context-middleware.html`

---

## 📊 Diagram 7: 10 Orchestrator Ecosystem Update

**File:** `10-orchestrator-ecosystem.mmd`  
**Purpose:** Update existing 8-orchestrator diagram to show all 10

```mermaid
graph TB
    TM["🎛️ Toolkit Manager<br/><small>Master Orchestrator</small>"]
    
    subgraph "Planning & Strategy (3)"
        Plan["🧠 Planning v5<br/>🛡️ AUTONOMOUS"]
        Refine["🔄 Refinement<br/>🛡️ AUTONOMOUS"]
        Debug["🐛 Debug<br/>🛡️ AUTONOMOUS"]
    end
    
    subgraph "Execution (3)"
        TDD["🧪 TDD Mastery<br/>📋 GUIDED"]
        ADO["📋 ADO v2<br/>🛡️ AUTONOMOUS"]
        Deploy["🚀 Deployment<br/>📋 GUIDED"]
    end
    
    subgraph "System Operations (4)"
        Vacuum["🧹 Vacuum v2<br/>🛡️ AUTONOMOUS"]
        Cleanup["🗑️ Cleanup v2<br/>🛡️ AUTONOMOUS"]
        Sanitize["🔒 Sanitization<br/>🛡️ AUTONOMOUS"]
        Maint["🔧 Maintenance<br/>📋 GUIDED"]
    end
    
    TM --> Plan
    TM --> Refine
    TM --> Debug
    TM --> TDD
    TM --> ADO
    TM --> Deploy
    TM --> Vacuum
    TM --> Cleanup
    TM --> Sanitize
    TM --> Maint
    
    style TM fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style Plan fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Refine fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Debug fill:#4CAF50,stroke:#2E7D32,color:#fff
```

**Usage:** Replace existing diagram in `docs/architecture/orchestrator-ecosystem.html`

---

## 📝 Implementation Notes

### Rendering Requirements

All Mermaid diagrams must:
1. Use **consistent color scheme** (glassmorphism palette)
2. Include **Font Awesome icons** (fa-* classes)
3. **Responsive sizing** (work on mobile + desktop)
4. **High contrast** for accessibility (WCAG 2.1 AA)

### Glassmorphism Color Palette

```css
/* Use these colors in Mermaid diagrams */
--primary: #2196F3 (Blue)
--success: #4CAF50 (Green)
--warning: #FF9800 (Orange)
--error: #F44336 (Red)
--purple: #9C27B0 (Epic/Master Orchestrator)
```

### Integration Points

| Diagram | Target Page | Section |
|---------|-------------|---------|
| Plan Viewer Architecture | `docs/orchestrators/cortex-lens-architecture.html` | Architecture Overview |
| Epic vs. Feature Decision Tree | `docs/orchestrators/planning-v5-epic-vs-feature.html` | Decision Guide |
| Cross-Linking | `docs/orchestrators/cortex-lens-architecture.html` | Integration |
| Phase -1 Flow | `docs/orchestrators/planning-v5.html` | Phase -1 Section |
| AST Scanning | `docs/orchestrators/planning-v5.html` | AST Integration |
| Context Middleware | `docs/features/context-middleware.html` | Priority Logic |
| 10 Orchestrators | `docs/architecture/orchestrator-ecosystem.html` | Ecosystem |

---

**Status:** ✅ READY FOR PHASE 7D IMPLEMENTATION
