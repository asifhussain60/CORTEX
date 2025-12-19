# Planning System 4.0 - Architecture Diagram

**Version:** 1.0  
**Created:** December 19, 2025  
**Author:** Asif Hussain  

---

## Component Architecture

```mermaid
graph TB
    subgraph "Planning System 4.0 Orchestrator"
        PO[PlanningOrchestrator<br/>extends BaseOrchestrator]
        
        subgraph "Routing Module"
            TR[TieredRouter<br/>4-tier classification]
            CA[ComplexityAnalyzer<br/>4D scoring]
            PIC[PlanningIntelligenceCoordinator<br/>Orchestrates routing]
        end
        
        subgraph "Discovery Module"
            PPD[PrePlanningDiscovery<br/>Search existing plans]
            PM[PlanMatcher<br/>Semantic matching]
        end
        
        subgraph "Tracking Module"
            PT[ProgressTracker<br/>PlanningSession]
            MC[MetricsCollector<br/>Phase metrics]
        end
        
        subgraph "Management Module"
            TPM[TemporaryPlanManager<br/>Implicit planning]
            PL[PlanLifecycle<br/>Active→Completed→Archived]
        end
        
        PO --> TR
        PO --> PPD
        PO --> PT
        PO --> TPM
        
        TR --> CA
        TR --> PIC
        
        PPD --> PM
        
        PT --> MC
        
        TPM --> PL
    end
    
    subgraph "External Dependencies"
        PFM[PlanFolderManager<br/>Hierarchical folders]
        PLearner[PlanningLearner<br/>Learn from history]
        PU[PlanningUtility<br/>Shared functions]
        Brain[BrainInterface<br/>Tier 2 knowledge]
    end
    
    PO --> PFM
    PO --> PLearner
    PO --> PU
    PO --> Brain
    
    subgraph "DI Container"
        DIC[CortexContainer]
    end
    
    DIC -.registers.-> PO
    DIC -.injects.-> TR
    DIC -.injects.-> PPD
    DIC -.injects.-> PT
    DIC -.injects.-> TPM
```

---

## Tiered Routing Decision Flow

```mermaid
flowchart TD
    Start[User Request] --> Analyze[ComplexityAnalyzer<br/>4D Scoring]
    
    Analyze --> Score{Complexity<br/>Score}
    
    Score -->|0-25| Tier1[Tier 1: INSTANT<br/>&lt;2 seconds<br/>Direct execution]
    Score -->|26-50| Tier2[Tier 2: LIGHTWEIGHT<br/>&lt;10 seconds<br/>Inline validation]
    Score -->|51-75| Tier3[Tier 3: DOCUMENTED<br/>10-60 min<br/>Single MD plan]
    Score -->|76-100| Tier4[Tier 4: COMPLEX<br/>&gt;1 hour<br/>Nested plans]
    
    Tier1 --> Execute1[Execute immediately]
    Tier2 --> Execute2[Generate inline plan<br/>+ Execute]
    Tier3 --> Discover3{Pre-Planning<br/>Discovery}
    Tier4 --> Discover4{Pre-Planning<br/>Discovery}
    
    Discover3 -->|Found| Recommend3[Recommend existing plan]
    Discover3 -->|Not Found| Create3[Create new plan MD]
    
    Discover4 -->|Found| Recommend4[Recommend existing plan]
    Discover4 -->|Not Found| Create4[Create master + sub-plans]
    
    Execute1 --> Track[Progress Tracker]
    Execute2 --> Track
    Create3 --> Track
    Create4 --> Track
    
    Track --> Metrics[Metrics Collector]
    Metrics --> Complete[Completion]
    
    style Tier1 fill:#90EE90
    style Tier2 fill:#87CEEB
    style Tier3 fill:#FFD700
    style Tier4 fill:#FF6B6B
```

---

## Pre-Planning Discovery Workflow

```mermaid
sequenceDiagram
    participant User
    participant PO as PlanningOrchestrator
    participant PPD as PrePlanningDiscovery
    participant PM as PlanMatcher
    participant FS as FileSystem
    
    User->>PO: Request "Plan auth system"
    PO->>PPD: pre_planning_discovery(request)
    
    PPD->>PM: extract_feature_slug(request)
    PM-->>PPD: "auth-system"
    
    PPD->>FS: Search active/ folder
    FS-->>PPD: Found: auth-system-v1
    
    PPD->>PM: semantic_match(request, found_plans)
    PM-->>PPD: Confidence: 95%
    
    PPD-->>PO: Recommendation: Reuse "auth-system-v1"
    
    PO->>User: "Found existing plan: auth-system-v1<br/>Continue or create new?"
    
    alt User continues
        User->>PO: Continue existing
        PO->>PO: Load existing plan
    else User creates new
        User->>PO: Create new v2
        PO->>PO: Create auth-system-v2
    end
```

---

## Module Interactions

```mermaid
graph LR
    subgraph "Request Flow"
        R[Request] --> TR[TieredRouter]
        TR --> CA[ComplexityAnalyzer]
        CA --> TR
        TR --> PO[PlanningOrchestrator]
    end
    
    subgraph "Discovery Flow"
        PO --> PPD[PrePlanningDiscovery]
        PPD --> PM[PlanMatcher]
        PM --> FS[FileSystem]
        FS --> PM
        PM --> PPD
        PPD --> PO
    end
    
    subgraph "Execution Flow"
        PO --> EX[Execute Plan]
        EX --> PT[ProgressTracker]
        PT --> MC[MetricsCollector]
        MC --> Brain[BrainInterface]
    end
    
    subgraph "Lifecycle Flow"
        PO --> TPM[TemporaryPlanManager]
        TPM --> PL[PlanLifecycle]
        PL --> PFM[PlanFolderManager]
    end
```

---

## Complexity Scoring (4 Dimensions)

```mermaid
graph TD
    subgraph "Complexity Dimensions"
        CI[Code Impact<br/>LOC, Files, Modules]
        RL[Risk Level<br/>Breaking changes, Dependencies]
        DC[Domain Complexity<br/>Business logic, Algorithms]
        IS[Integration Scope<br/>External systems, APIs]
    end
    
    CI --> Score[Weighted Score<br/>0-100]
    RL --> Score
    DC --> Score
    IS --> Score
    
    Score --> T1{Score < 25}
    Score --> T2{Score 26-50}
    Score --> T3{Score 51-75}
    Score --> T4{Score > 75}
    
    T1 -->|Yes| Tier1[Tier 1: INSTANT]
    T2 -->|Yes| Tier2[Tier 2: LIGHTWEIGHT]
    T3 -->|Yes| Tier3[Tier 3: DOCUMENTED]
    T4 -->|Yes| Tier4[Tier 4: COMPLEX]
```

---

## Progress Tracking Integration

```mermaid
sequenceDiagram
    participant PO as PlanningOrchestrator
    participant PS as PlanningSession
    participant MC as MetricsCollector
    participant PT as ProgressTracker
    participant RP as Response
    
    PO->>PS: create_session(plan_id)
    PS-->>PO: session_id
    
    loop For each phase
        PO->>PS: record_phase_start(phase_name)
        PO->>PO: Execute phase work
        PO->>MC: collect_metrics(phase_name)
        MC-->>PO: metrics
        PO->>PS: record_phase_end(phase_name, metrics)
    end
    
    PO->>PT: render_progress_table(session)
    PT-->>PO: markdown_table
    
    PO->>RP: Include progress table in response
    RP-->>User: Response with visual tracker
```

---

## Directory Structure

```
src/orchestrators/planning_system/
├── __init__.py
├── planning_orchestrator.py        # Main orchestrator
├── routing/
│   ├── __init__.py
│   ├── tiered_router.py           # 4-tier classification
│   └── complexity_analyzer.py     # 4D scoring
├── discovery/
│   ├── __init__.py
│   ├── pre_planning_discovery.py  # Search existing plans
│   └── plan_matcher.py            # Semantic matching
├── tracking/
│   ├── __init__.py
│   ├── progress_tracker.py        # PlanningSession
│   └── metrics_collector.py       # Phase metrics
├── management/
│   ├── __init__.py
│   ├── temporary_plan_manager.py  # Implicit planning
│   └── plan_lifecycle.py          # Lifecycle management
├── tests/
│   ├── __init__.py
│   ├── test_planning_orchestrator.py
│   ├── test_tiered_routing.py
│   ├── test_pre_planning_discovery.py
│   ├── test_progress_tracking.py
│   └── test_temporary_plans.py
└── README.md
```

---

## Key Design Decisions

**1. Reuse Over Rewrite**
- TieredRouter, ComplexityAnalyzer already exist → COPY to v4.0 structure
- TemporaryPlanManager, PlanFolderManager → USE as dependencies
- PlanningLearner → Tier 2 integration, no migration needed

**2. Extract Discovery Logic**
- Pre-planning discovery was embedded in archived PlanningOrchestrator
- Extract to standalone `pre_planning_discovery.py` module
- Add `plan_matcher.py` for semantic matching

**3. Co-Located Tests**
- All tests in `src/orchestrators/planning_system/tests/`
- No CORTEX tests in user repos
- Target: 85%+ coverage (50+ tests)

**4. Module Boundaries**
- **routing/** - Complexity analysis + tier classification
- **discovery/** - Find existing plans before creating new
- **tracking/** - Real-time progress + metrics
- **management/** - Temporary plans + lifecycle

**5. BaseOrchestrator Integration**
- Extends `BaseOrchestrator` from Phase 1
- Uses DI container for wiring
- Integrates response templates v4.0
- Standard logging + error handling

---

## Integration Points

**With Other Orchestrators:**
- **TDD Orchestrator** - Planning includes TDD phases automatically
- **Execution Orchestrator** - Executes Tier 3-4 plans
- **Documentation Orchestrator** - Documents planning workflows

**With Brain Tiers:**
- **Tier 1** - Conversation history for context
- **Tier 2** - PlanningLearner for historical insights
- **Tier 3** - Project metrics, codebase context

**With External Systems:**
- **FileSystem** - Plan folder structure (hierarchical)
- **Git** - Version control for plans
- **LLM** - Tiered routing classification (fallback)

---

**Version Control:**
- This diagram will be auto-updated by DocumentationOrchestrator
- Manual updates should preserve Mermaid syntax
- Regenerate diagrams after architecture changes
