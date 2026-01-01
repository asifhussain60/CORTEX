# 📊 Mermaid Diagram Templates

**Purpose:** Pre-built MMD diagrams for Level 2 documentation

---

## 1. Planning System - 4-Phase State Diagram

```mermaid
stateDiagram-v2
    [*] --> Classification
    Classification --> Discovery: Complexity Analyzed
    Discovery --> Generation: No Duplicates Found
    Discovery --> [*]: Duplicate Exists
    Generation --> Validation: Plan Created
    Validation --> [*]: DoR/DoD Passed
    Validation --> Generation: Validation Failed
    
    state Classification {
        [*] --> AnalyzeComplexity
        AnalyzeComplexity --> DetermineTier
        DetermineTier --> [*]
    }
    
    state Discovery {
        [*] --> SearchExisting
        SearchExisting --> CheckRecent
        CheckRecent --> [*]
    }
    
    state Generation {
        [*] --> CreateStructure
        CreateStructure --> GeneratePlan
        GeneratePlan --> AddArtifacts
        AddArtifacts --> [*]
    }
    
    state Validation {
        [*] --> CheckDoR
        CheckDoR --> CheckDoD
        CheckDoD --> [*]
    }
```

---

## 2. TDD Orchestrator - RED-GREEN-REFACTOR Cycle

```mermaid
flowchart LR
    subgraph RED["🔴 RED Phase"]
        R1[Write Failing Test]
        R2[Verify Test Fails]
        R3[Document Expected Behavior]
    end
    
    subgraph GREEN["🟢 GREEN Phase"]
        G1[Write Minimal Code]
        G2[Make Test Pass]
        G3[Verify All Tests Green]
    end
    
    subgraph REFACTOR["🔵 REFACTOR Phase"]
        RF1[Identify Code Smells]
        RF2[Apply Improvements]
        RF3[Verify Tests Still Pass]
    end
    
    R1 --> R2 --> R3
    R3 --> G1
    G1 --> G2 --> G3
    G3 --> RF1
    RF1 --> RF2 --> RF3
    RF3 --> R1
    
    style RED fill:#ff6b6b,stroke:#ff0000,color:#fff
    style GREEN fill:#00ff88,stroke:#00cc66,color:#000
    style REFACTOR fill:#00d4ff,stroke:#0099cc,color:#000
```

---

## 3. Debug Orchestrator - Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Debug as Debug Orchestrator
    participant Analysis as Root Cause Analyzer
    participant Knowledge as Knowledge Graph
    participant Fix as Fix Engine
    participant Tests as Test Runner
    
    User->>Debug: debug "test_auth failing"
    Debug->>Analysis: Parse bug report
    Analysis->>Knowledge: Query similar issues
    Knowledge-->>Analysis: Related patterns
    Analysis->>Debug: Root cause identified
    Debug->>Fix: Apply template fix
    Fix->>Tests: Run verification
    Tests-->>Fix: Test results
    
    alt Tests Pass
        Fix-->>Debug: Fix successful
        Debug->>Knowledge: Store pattern
        Debug-->>User: ✅ Bug resolved
    else Tests Fail
        Fix-->>Debug: Fix failed
        Debug->>Analysis: Re-analyze
    end
```

---

## 4. Holistic Discovery - 3-Step Flowchart

```mermaid
flowchart TD
    subgraph STEP1["🧠 Step 1: Semantic Search"]
        S1[Natural Language Query]
        S2[AI Intent Matching]
        S3[Cross-File Search]
        S1 --> S2 --> S3
    end
    
    subgraph STEP2["📝 Step 2: Pattern Search"]
        P1[AST Analysis]
        P2[Signature Matching]
        P3[Similar Patterns]
        P1 --> P2 --> P3
    end
    
    subgraph STEP3["🔍 Step 3: Dependency Trace"]
        D1[Import Graph]
        D2[Call Hierarchy]
        D3[Usage Patterns]
        D1 --> D2 --> D3
    end
    
    START([New Implementation Request]) --> STEP1
    STEP1 --> STEP2
    STEP2 --> STEP3
    STEP3 --> DECISION{Existing Code Found?}
    
    DECISION -->|Yes| REUSE[Reuse Existing]
    DECISION -->|No| CREATE[Create New]
    
    style DECISION fill:#ffd700,stroke:#cc9900,color:#000
    style REUSE fill:#00ff88,stroke:#00cc66,color:#000
    style CREATE fill:#00d4ff,stroke:#0099cc,color:#000
```

---

## 5. SKULL Protection - 8-Layer Defense Graph

```mermaid
graph LR
    THREAT([⚠️ Threat]) --> L1
    
    subgraph L1["Layer 1: Document Org"]
        L1A[Path Validation]
    end
    
    subgraph L2["Layer 2: Path Traversal"]
        L2A[Directory Check]
    end
    
    subgraph L3["Layer 3: Git Protection"]
        L3A[Branch Isolation]
    end
    
    subgraph L4["Layer 4: Bloat Detection"]
        L4A[File Size Check]
    end
    
    subgraph L5["Layer 5: Duplication"]
        L5A[Hash Comparison]
    end
    
    subgraph L6["Layer 6: Memory"]
        L6A[Tier Validation]
    end
    
    subgraph L7["Layer 7: Compliance"]
        L7A[Rule Check]
    end
    
    subgraph L8["Layer 8: Governance"]
        L8A[Final Approval]
    end
    
    L1 --> L2 --> L3 --> L4 --> L5 --> L6 --> L7 --> L8
    L8 --> SAFE([✅ Safe])
    
    L1 -.->|Blocked| BLOCKED([🚫 Blocked])
    L2 -.->|Blocked| BLOCKED
    L3 -.->|Blocked| BLOCKED
    L4 -.->|Blocked| BLOCKED
    L5 -.->|Blocked| BLOCKED
    L6 -.->|Blocked| BLOCKED
    L7 -.->|Blocked| BLOCKED
    L8 -.->|Blocked| BLOCKED
    
    style THREAT fill:#ff6b6b,stroke:#ff0000,color:#fff
    style SAFE fill:#00ff88,stroke:#00cc66,color:#000
    style BLOCKED fill:#ff0000,stroke:#cc0000,color:#fff
```

---

## 6. Token Optimization - Tier Distribution Pie

```mermaid
pie showData
    title Token Usage by Response Tier
    "Tier 1 (Instant)" : 15
    "Tier 2 (Focused)" : 35
    "Tier 3 (Structured)" : 30
    "Tier 4 (Comprehensive)" : 20
```

---

## 7. Sanitization Pipeline - Flowchart

```mermaid
flowchart LR
    subgraph PHASE1["🔍 Phase 1: Analysis"]
        A1[Scan Codebase]
        A2[Detect Patterns]
        A3[Build Inventory]
    end
    
    subgraph PHASE2["🗺️ Phase 2: Mapping"]
        M1[Create Mappings]
        M2[Generate Keys]
        M3[Store Reversible]
    end
    
    subgraph PHASE3["🔄 Phase 3: Transform"]
        T1[Apply Replacements]
        T2[Update References]
        T3[Preserve Structure]
    end
    
    subgraph PHASE4["✅ Phase 4: Validate"]
        V1[Build Check]
        V2[Test Suite]
        V3[Manual Review]
    end
    
    subgraph PHASE5["📦 Phase 5: Package"]
        P1[Create Archive]
        P2[Generate Report]
        P3[Store Mapping Key]
    end
    
    PHASE1 --> PHASE2 --> PHASE3 --> PHASE4 --> PHASE5
    
    style PHASE1 fill:rgba(0,212,255,0.3),stroke:#00d4ff
    style PHASE2 fill:rgba(123,97,255,0.3),stroke:#7b61ff
    style PHASE3 fill:rgba(0,255,136,0.3),stroke:#00ff88
    style PHASE4 fill:rgba(255,215,0,0.3),stroke:#ffd700
    style PHASE5 fill:rgba(0,212,255,0.3),stroke:#00d4ff
```

---

## 8. ADO Operations - Work Item Flow

```mermaid
flowchart TD
    INPUT([Natural Language Input]) --> PARSE
    
    subgraph PARSE["📝 Parse Request"]
        P1[Extract Feature Name]
        P2[Identify Scope]
        P3[Detect Dependencies]
    end
    
    subgraph GENERATE["⚙️ Generate Items"]
        G1[Create Feature]
        G2[Break into Stories]
        G3[Add Acceptance Criteria]
        G4[Estimate Points]
    end
    
    subgraph FORMAT["📋 Format Output"]
        F1[ADO JSON Format]
        F2[Markdown Preview]
        F3[Copy-Paste Ready]
    end
    
    PARSE --> GENERATE --> FORMAT
    FORMAT --> OUTPUT([📤 ADO-Ready Work Items])
    
    style INPUT fill:#7b61ff,stroke:#5a45cc,color:#fff
    style OUTPUT fill:#00ff88,stroke:#00cc66,color:#000
```

---

## Glassmorphism MMD Styling

Add to page CSS:

```css
/* Mermaid glassmorphism theme */
.mermaid {
    background: transparent !important;
}

.mermaid .node rect,
.mermaid .node circle,
.mermaid .node polygon {
    fill: var(--glass-bg) !important;
    stroke: var(--glass-border) !important;
    stroke-width: 2px;
}

.mermaid .edgePath path {
    stroke: var(--accent-primary) !important;
    stroke-width: 2px;
}

.mermaid .label {
    color: var(--text-primary) !important;
}

.mermaid .cluster rect {
    fill: rgba(26, 31, 58, 0.4) !important;
    stroke: var(--glass-border) !important;
    rx: 16px;
    ry: 16px;
}
```
