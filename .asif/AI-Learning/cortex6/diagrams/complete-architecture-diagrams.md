# CORTEX-6 Complete Architecture Diagrams
# Visual Reference for Holistic Master Plan
# Generated: 2026-01-07

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph "User Interface Layer"
        GHC[GitHub Copilot Chat<br/>Natural Language]
        CLI[Terminal CLI<br/>Direct Invocation]
        Vision[Vision API<br/>Image Analysis]
    end
    
    subgraph "Intent Classification & Routing"
        Intent[CORTEX.prompt.md<br/>Intent Router]
        Trie[Trie Pattern Matcher<br/>O 1 routing]
        LLM[LLM Intent Classifier<br/>Confidence ≥0.7]
    end
    
    subgraph "Master Orchestrator v2"
        Master[Master Orchestrator<br/>Single Entry Point]
        TODO[TODO Orchestrator<br/>DAG Work Tracker]
        State[State Manager<br/>SQLite WAL]
        Exec[Execution Engine<br/>Event-Driven]
    end
    
    subgraph "Governance & Intelligence"
        Gov[Governance Validator<br/>SKULL Rules Enforcer]
        Audit[Audit Logger<br/>Mandatory JSONL]
        Know[Knowledge Merger<br/>3-Tier Hierarchy]
        MCP[MCP Server<br/>JSON-RPC 2.0]
    end
    
    subgraph "Specialized Orchestrators Python"
        Plan[Planning v7]
        TDD[TDD v2]
        Review[Review v2]
        Vacuum[Vacuum v2]
        Custom[Custom Orchestrators]
    end
    
    subgraph "Data Persistence"
        DB[SQLite WAL<br/>State + Audit + TODO]
        Registry[Orchestrator Registry<br/>JSON + Validation]
        KnowLib[Knowledge Library<br/>YAML + Markdown]
        Repos[Multi-Repo Config<br/>repos.yaml]
    end
    
    GHC --> Intent
    CLI --> Intent
    Vision --> Intent
    Intent --> Trie
    Trie -.Fallback.-> LLM
    Trie --> Master
    LLM --> Master
    
    Master --> Gov
    Gov --> Know
    Gov --> Audit
    Master --> TODO
    Master --> MCP
    Master --> Exec
    
    TODO --> State
    State --> DB
    Audit --> DB
    
    Exec --> Plan
    Exec --> TDD
    Exec --> Review
    Exec --> Vacuum
    Exec --> Custom
    
    Plan --> Know
    Plan --> Audit
    TDD --> Know
    Review --> Know
    
    MCP --> Registry
    Know --> KnowLib
    Master --> Repos
    
    style Master fill:#ff9900,stroke:#333,stroke-width:4px
    style TODO fill:#ff6600,stroke:#333,stroke-width:3px
    style Gov fill:#f44336,stroke:#333,stroke-width:3px
    style Audit fill:#e91e63,stroke:#333,stroke-width:2px
    style MCP fill:#2196f3,stroke:#333,stroke-width:3px
    style DB fill:#4CAF50,stroke:#333,stroke-width:3px
```

## 2. Master Orchestrator v2 State Machine

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> ROUTING: User Request
    ROUTING --> ORCHESTRATOR_FOUND: Pattern Match
    ROUTING --> LLM_CLASSIFY: No Match
    LLM_CLASSIFY --> ORCHESTRATOR_FOUND: Confidence ≥0.7
    LLM_CLASSIFY --> ERROR: Confidence <0.7
    ORCHESTRATOR_FOUND --> VALIDATING: Validate Manifest
    VALIDATING --> LOADING: Valid
    VALIDATING --> ERROR: Invalid
    LOADING --> EXECUTING: Orchestrator Ready
    LOADING --> ERROR: Load Failed
    EXECUTING --> CHECKPOINTING: Task Complete
    CHECKPOINTING --> EXECUTING: More Work
    CHECKPOINTING --> COMPLETED: All Done
    EXECUTING --> FAILED: Error
    FAILED --> RETRYING: Retry Count < Max
    FAILED --> ROLLBACK: Retry Exhausted
    RETRYING --> EXECUTING
    ROLLBACK --> IDLE
    COMPLETED --> AUDIT_REVIEW: Phase Complete
    AUDIT_REVIEW --> KNOWLEDGE_UPDATE: Extract Lessons
    KNOWLEDGE_UPDATE --> IDLE
    ERROR --> IDLE
    
    note right of EXECUTING
        Silent execution
        No chatty updates
        Progress bars only
    end note
    
    note right of CHECKPOINTING
        Every 5 tasks
        Graph snapshot
        Rollback ready
    end note
    
    note right of AUDIT_REVIEW
        Analyze logs
        Governance compliance
        Performance metrics
    end note
```

## 3. TODO Orchestrator DAG Structure

```mermaid
graph TD
    subgraph "TODO DAG Example: Planning Workflow"
        T1[Task 1: Initialize Plan<br/>STATUS: COMPLETED<br/>Duration: 5min]
        T2[Task 2: Load User Requirements<br/>STATUS: COMPLETED<br/>Duration: 3min]
        T3[Task 3: Validate Requirements<br/>STATUS: COMPLETED<br/>Duration: 10min]
        T4[Task 4: Create Phase Breakdown<br/>STATUS: IN_PROGRESS<br/>Duration: 15min]
        T5[Task 5: Dependency Analysis<br/>STATUS: READY<br/>Duration: 20min]
        T6[Task 6: Generate YAML Plans<br/>STATUS: READY<br/>Duration: 10min]
        T7[Task 7: Create Progress Tracker<br/>STATUS: PENDING<br/>Duration: 5min]
        T8[Task 8: Validate Plan Completeness<br/>STATUS: PENDING<br/>Duration: 10min]
        T9[Task 9: Generate Plan Viewer<br/>STATUS: BLOCKED<br/>Duration: 5min]
        T10[Task 10: Finalize Documentation<br/>STATUS: PENDING<br/>Duration: 10min]
    end
    
    T1 --> T2
    T2 --> T3
    T3 --> T4
    T3 --> T5
    T4 --> T6
    T5 --> T6
    T6 --> T7
    T6 --> T9
    T7 --> T8
    T8 --> T10
    T9 --> T10
    
    style T1 fill:#4CAF50,stroke:#333,stroke-width:2px
    style T2 fill:#4CAF50,stroke:#333,stroke-width:2px
    style T3 fill:#4CAF50,stroke:#333,stroke-width:2px
    style T4 fill:#FFC107,stroke:#333,stroke-width:2px
    style T5 fill:#2196F3,stroke:#333,stroke-width:2px
    style T6 fill:#2196F3,stroke:#333,stroke-width:2px
    style T7 fill:#E0E0E0,stroke:#333,stroke-width:1px
    style T8 fill:#E0E0E0,stroke:#333,stroke-width:1px
    style T9 fill:#9E9E9E,stroke:#333,stroke-width:1px
    style T10 fill:#E0E0E0,stroke:#333,stroke-width:1px
```

**Legend:**
- 🟢 Green (COMPLETED): Task finished successfully
- 🟡 Yellow (IN_PROGRESS): Currently executing
- 🔵 Blue (READY): Dependencies met, ready to execute
- ⚫ Gray (BLOCKED): Dependencies failed or incomplete
- ⚪ Light Gray (PENDING): Waiting for dependencies

## 4. Resume from Breakage Flow

```mermaid
sequenceDiagram
    participant User
    participant Master as Master Orchestrator
    participant TODO as TODO Orchestrator
    participant DB as SQLite Database
    participant Exec as Execution Engine
    
    User->>Master: Resume execution
    Master->>TODO: Load last checkpoint
    TODO->>DB: SELECT * FROM todo_checkpoints<br/>ORDER BY timestamp DESC LIMIT 1
    DB-->>TODO: Checkpoint data (graph snapshot)
    TODO->>TODO: Parse graph snapshot
    TODO->>TODO: Identify IN_PROGRESS tasks
    TODO->>TODO: Mark IN_PROGRESS → PENDING
    TODO->>TODO: Get ready tasks (dependencies met)
    TODO-->>Master: Ready tasks: [T5, T6]
    
    Note over Master,Exec: NO CHATTY NARRATION
    Master->>Exec: Execute T5 (silent mode)
    Exec-->>Master: T5 complete
    Master->>TODO: Mark T5 COMPLETED
    TODO->>TODO: Update dependents (T6 → READY)
    TODO->>DB: Checkpoint (every 5 tasks)
    
    Master->>Exec: Execute T6 (parallel with T7)
    Exec-->>Master: T6 complete
    Master->>User: ✅ Progress: [████░░░░░░] 40% (4/10 tasks)
    
    Note over User,Master: SILENT PROGRESS<br/>No task-by-task narration
```

## 5. Governance Enforcement Layers

```mermaid
graph TB
    subgraph "Layer 1: Pre-Commit Hooks"
        Git[Git Commit Attempt]
        Hook[Pre-Commit Hook Script]
        AuditCheck{Audit Log<br/>Exists?}
        ViolationCheck{BLOCKED<br/>Violations?}
        TypeCheck{Type Hints<br/>100%?}
        DocCheck{Docstrings<br/>100%?}
        FormatCheck{Code Format<br/>Pass?}
        Block[❌ Block Commit]
        Allow[✅ Allow Commit]
    end
    
    subgraph "Layer 2: Runtime Middleware"
        Orchestrator[Orchestrator Execution]
        GovValidator[Governance Validator]
        FileGuard[File Creation Guard]
        IncrementalExec[Incremental Executor]
        PythonValidator[Python Best Practices]
        RuntimeBlock{Violations?}
    end
    
    subgraph "Layer 3: Static Analysis CI/CD"
        CI[CI/CD Pipeline]
        Mypy[mypy --strict]
        Pylint[pylint ≥8.0]
        Pydocstyle[pydocstyle]
        Black[black --check]
        Isort[isort --check]
        CIBlock{All Pass?}
    end
    
    Git --> Hook
    Hook --> AuditCheck
    AuditCheck -->|No| Block
    AuditCheck -->|Yes| ViolationCheck
    ViolationCheck -->|Yes| Block
    ViolationCheck -->|No| TypeCheck
    TypeCheck -->|No| Block
    TypeCheck -->|Yes| DocCheck
    DocCheck -->|No| Block
    DocCheck -->|Yes| FormatCheck
    FormatCheck -->|No| Block
    FormatCheck -->|Yes| Allow
    
    Orchestrator --> GovValidator
    Orchestrator --> FileGuard
    Orchestrator --> IncrementalExec
    Orchestrator --> PythonValidator
    GovValidator --> RuntimeBlock
    FileGuard --> RuntimeBlock
    IncrementalExec --> RuntimeBlock
    PythonValidator --> RuntimeBlock
    RuntimeBlock -->|Yes| Block
    RuntimeBlock -->|No| Allow
    
    CI --> Mypy
    CI --> Pylint
    CI --> Pydocstyle
    CI --> Black
    CI --> Isort
    Mypy --> CIBlock
    Pylint --> CIBlock
    Pydocstyle --> CIBlock
    Black --> CIBlock
    Isort --> CIBlock
    CIBlock -->|No| Block
    CIBlock -->|Yes| Allow
    
    style Block fill:#f44336,stroke:#333,stroke-width:2px,color:#fff
    style Allow fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff
```

## 6. Knowledge Merger 3-Tier Hierarchy

```mermaid
graph TB
    subgraph "Tier 0: CORTEX Knowledge (Universal)"
        CortexStd[standards/<br/>python-style-guide.yaml]
        CortexPat[patterns/<br/>solid-principles.yaml]
        CortexWF[workflows/<br/>tdd-workflow.yaml]
        CortexSec[security/<br/>secret-management.yaml]
    end
    
    subgraph "Tier 2: Company Knowledge (Overrides)"
        CompanyStd[coding-standards/<br/>python-style-overrides.yaml]
        CompanyArch[architecture/<br/>microservices-guidelines.yaml]
        CompanyWF[workflows/<br/>branching-strategy.yaml]
        CompanySec[security/<br/>compliance-requirements.yaml]
    end
    
    subgraph "Tier 3: Project Knowledge (Context)"
        ProjectArch[architecture/<br/>system-architecture.yaml]
        ProjectDomain[domain-models/<br/>user-management.yaml]
        ProjectAPI[api-contracts/<br/>rest-api-v2.yaml]
        ProjectDeploy[deployment/<br/>kubernetes-manifests.yaml]
    end
    
    subgraph "Knowledge Merger (Intelligent Merge)"
        Merger[Knowledge Merger]
        Conflict{Conflict<br/>Detected?}
        Strategy{Resolution<br/>Strategy}
        CompanyWins[Company Wins<br/>Preferences]
        CortexWins[CORTEX Wins<br/>Best Practices]
        MergeCombine[Merge Combine<br/>Lists]
        UserPrompt[User Prompt<br/>Critical Conflicts]
        FinalKnowledge[Final Merged Knowledge]
    end
    
    CortexStd --> Merger
    CortexPat --> Merger
    CortexWF --> Merger
    CortexSec --> Merger
    
    CompanyStd --> Merger
    CompanyArch --> Merger
    CompanyWF --> Merger
    CompanySec --> Merger
    
    ProjectArch --> Merger
    ProjectDomain --> Merger
    ProjectAPI --> Merger
    ProjectDeploy --> Merger
    
    Merger --> Conflict
    Conflict -->|No| FinalKnowledge
    Conflict -->|Yes| Strategy
    
    Strategy -->|Project Preferences| CompanyWins
    Strategy -->|Universal Best Practices| CortexWins
    Strategy -->|Non-Conflicting| MergeCombine
    Strategy -->|Critical| UserPrompt
    
    CompanyWins --> FinalKnowledge
    CortexWins --> FinalKnowledge
    MergeCombine --> FinalKnowledge
    UserPrompt --> FinalKnowledge
    
    style CortexStd fill:#2196F3,stroke:#333,stroke-width:2px
    style CompanyStd fill:#FF9800,stroke:#333,stroke-width:2px
    style ProjectArch fill:#4CAF50,stroke:#333,stroke-width:2px
    style Merger fill:#9C27B0,stroke:#333,stroke-width:3px,color:#fff
    style FinalKnowledge fill:#FFD700,stroke:#333,stroke-width:3px
```

## 7. MCP Server Architecture (Multi-Repo Support)

```mermaid
graph LR
    subgraph "GitHub Copilot"
        GHC[GitHub Copilot Chat]
        MCPClient[MCP Client]
    end
    
    subgraph "CORTEX MCP Server"
        MCPServer[MCP Server<br/>JSON-RPC 2.0]
        ToolsList[tools/list]
        ToolsCall[tools/call]
        PromptsGet[prompts/get]
        ResourcesRead[resources/read]
    end
    
    subgraph "Multi-Repo Manager"
        RepoConfig[repos.yaml]
        ContextDetect[Context Detection]
        Repo1[Repo 1: Backend]
        Repo2[Repo 2: Frontend]
        Repo3[Repo 3: CORTEX Dev]
    end
    
    subgraph "Orchestrator Registry"
        Registry[Orchestrator Registry]
        Plan[Planning v7]
        TDD[TDD v2]
        Review[Review v2]
        Vacuum[Vacuum v2]
    end
    
    subgraph "Knowledge Library"
        T0[Tier 0: CORTEX]
        T2[Tier 2: Company]
        T3Repo1[Tier 3: Repo 1]
        T3Repo2[Tier 3: Repo 2]
        T3Repo3[Tier 3: Repo 3]
    end
    
    GHC --> MCPClient
    MCPClient <-->|stdio<br/>JSONL| MCPServer
    
    MCPServer --> ToolsList
    MCPServer --> ToolsCall
    MCPServer --> PromptsGet
    MCPServer --> ResourcesRead
    
    ToolsList --> Registry
    ToolsCall --> Registry
    
    Registry --> RepoConfig
    RepoConfig --> ContextDetect
    ContextDetect --> Repo1
    ContextDetect --> Repo2
    ContextDetect --> Repo3
    
    Repo1 --> T3Repo1
    Repo2 --> T3Repo2
    Repo3 --> T3Repo3
    
    Registry --> Plan
    Registry --> TDD
    Registry --> Review
    Registry --> Vacuum
    
    Plan --> T0
    Plan --> T2
    Plan --> T3Repo1
    
    style MCPServer fill:#2196F3,stroke:#333,stroke-width:3px,color:#fff
    style RepoConfig fill:#FF9800,stroke:#333,stroke-width:2px
    style Registry fill:#4CAF50,stroke:#333,stroke-width:2px
```

## 8. Continuous Audit & Learning Loop (Snowball Effect)

```mermaid
graph TB
    subgraph "Phase N Execution"
        Execute[Execute Phase N<br/>with Current Knowledge]
        AuditLog[Log to Audit JSONL]
        Operations[Operations:<br/>Code, Review, Refactor]
    end
    
    subgraph "Phase N Review (End of Phase)"
        Aggregate[Aggregate Audit Logs]
        AnalyzeGov[Analyze Governance<br/>Violations, Trends]
        AnalyzeKnow[Analyze Knowledge<br/>Consultation Patterns]
        AnalyzePerf[Analyze Performance<br/>Bottlenecks]
        ExtractLessons[Extract Lessons Learned<br/>LLM-Assisted]
    end
    
    subgraph "Knowledge & Governance Update"
        UpdateKnowledge[Update Knowledge Library<br/>New Patterns, Anti-Patterns]
        RefineRules[Refine Governance Rules<br/>Strengthen Enforcement]
        GenerateReport[Generate Phase<br/>Governance Report]
    end
    
    subgraph "Phase N+1 Execution (IMPROVED)"
        ExecuteNext[Execute Phase N+1<br/>with IMPROVED Knowledge]
        FewerViolations[Fewer Violations<br/>Rules Enforced Earlier]
        FasterExecution[Faster Execution<br/>Optimizations Applied]
        HigherQuality[Higher Quality<br/>Anti-Patterns Blocked]
    end
    
    Execute --> AuditLog
    Operations --> AuditLog
    AuditLog --> Aggregate
    
    Aggregate --> AnalyzeGov
    Aggregate --> AnalyzeKnow
    Aggregate --> AnalyzePerf
    
    AnalyzeGov --> ExtractLessons
    AnalyzeKnow --> ExtractLessons
    AnalyzePerf --> ExtractLessons
    
    ExtractLessons --> UpdateKnowledge
    ExtractLessons --> RefineRules
    ExtractLessons --> GenerateReport
    
    UpdateKnowledge --> ExecuteNext
    RefineRules --> ExecuteNext
    GenerateReport --> ExecuteNext
    
    ExecuteNext --> FewerViolations
    ExecuteNext --> FasterExecution
    ExecuteNext --> HigherQuality
    
    FewerViolations -.Snowball Effect.-> Execute
    FasterExecution -.Snowball Effect.-> Execute
    HigherQuality -.Snowball Effect.-> Execute
    
    style Execute fill:#2196F3,stroke:#333,stroke-width:2px
    style ExtractLessons fill:#9C27B0,stroke:#333,stroke-width:3px,color:#fff
    style UpdateKnowledge fill:#4CAF50,stroke:#333,stroke-width:2px
    style ExecuteNext fill:#FFD700,stroke:#333,stroke-width:3px
```

## 9. Trie Pattern Router (O(1) Routing)

```mermaid
graph TB
    subgraph "User Request Flow"
        Request[User Request:<br/>'create plan for user auth']
        Normalize[Normalize:<br/>lowercase, trim]
    end
    
    subgraph "Routing Stages (Fastest → Slowest)"
        Cache{Exact Match<br/>Cache?}
        Trie{Prefix Trie<br/>Match?}
        Regex{Regex<br/>Match?}
        LLM{LLM<br/>Classify?}
    end
    
    subgraph "Pattern Storage"
        ExactCache[HashMap<br/>'create plan' → planning_v7]
        TrieTree[Trie Structure<br/>'plan *' → planning_v7]
        RegexList[Regex List<br/>'review.*epic' → review_v2]
        LLMClassifier[LLM Intent Classifier<br/>Confidence ≥0.7]
    end
    
    subgraph "Result"
        Found[Orchestrator Found]
        CacheUpdate[Update Cache]
        Execute[Execute Orchestrator]
        NotFound[Not Found<br/>Prompt User]
    end
    
    Request --> Normalize
    Normalize --> Cache
    
    Cache -->|Hit O1| Found
    Cache -->|Miss| Trie
    Trie -->|Match Ok| Found
    Trie -->|No Match| Regex
    Regex -->|Match On| Found
    Regex -->|No Match| LLM
    LLM -->|Conf ≥0.7| Found
    LLM -->|Conf <0.7| NotFound
    
    Cache --> ExactCache
    Trie --> TrieTree
    Regex --> RegexList
    LLM --> LLMClassifier
    
    Found --> CacheUpdate
    CacheUpdate --> Execute
    NotFound --> Request
    
    style Cache fill:#4CAF50,stroke:#333,stroke-width:3px
    style Trie fill:#2196F3,stroke:#333,stroke-width:2px
    style Regex fill:#FF9800,stroke:#333,stroke-width:2px
    style LLM fill:#9C27B0,stroke:#333,stroke-width:2px
    style Found fill:#FFD700,stroke:#333,stroke-width:3px
    style NotFound fill:#f44336,stroke:#333,stroke-width:2px,color:#fff
```

**Performance:**
- ✅ Cache Hit: <1ms (O(1))
- ✅ Trie Match: <5ms (O(k), k = input length)
- ⚠️ Regex Scan: <20ms (O(n), n = orchestrators)
- ⚠️ LLM Classify: <500ms (network latency)

## 10. Dual-Epic Implementation Strategy

```mermaid
gantt
    title CORTEX-6 Dual-Epic Timeline (11 Weeks Total)
    dateFormat YYYY-MM-DD
    
    section Epic 1: Windows
    Phase 0: Foundational (MCP + Multi-Repo)    :e1p0, 2026-01-10, 17d
    Phase 1: Core Orchestration (TODO + Audit)  :e1p1, after e1p0, 14d
    Phase 2: Resilience (Rollback + Trie)       :e1p2, after e1p1, 9d
    Phase 3: Polish (Edge Cases + Hardening)    :e1p3, after e1p2, 25d
    
    section Epic 2: Mac (Parallel)
    Phase 0: Foundational (Parallel)            :e2p0, 2026-01-27, 10d
    Phase 1+2: Core + Resilience (Optimized)    :e2p1, after e2p0, 10d
    Phase 2: Polish (High Priority Only)        :e2p2, after e2p1, 15d
    
    section Integration
    Cross-Platform Testing                       :int1, after e1p3, 5d
    Performance Benchmarking                     :int2, after e1p3, 3d
    Documentation + Release                      :int3, after e1p3, 4d
```

**Key:**
- 📘 **Epic 1 (Windows)**: 8 weeks sequential (stability focus)
- 📗 **Epic 2 (Mac)**: 5 weeks parallel (optimization focus)
- 🔗 **Integration**: 2 weeks (merge + test + docs)
- 🎯 **Total**: 10-11 weeks to delivery

---

## Diagram Usage Guide

**For Planning:** Use diagrams 1-4 to understand system architecture  
**For Development:** Use diagrams 5-7 to implement governance & knowledge  
**For Operations:** Use diagrams 8-9 to monitor execution & performance  
**For Project Management:** Use diagram 10 to track epic progress

**All diagrams render in GitHub, VS Code, and Mermaid Live Editor.**
