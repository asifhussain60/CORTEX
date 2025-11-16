# CORTEX 4-Tier Architecture Preview

**Diagram:** 01-tier-architecture.mmd  
**Description:** Hierarchical cognitive architecture showing Tier 0-3 memory system

---

## Diagram

```mermaid
%% CORTEX 4-Tier Memory Architecture
%% Shows the hierarchical cognitive architecture

graph TB
    subgraph tier0["🛡️ TIER 0: INSTINCT<br/>(Immutable Core Rules)"]
        T0_TDD["Test-Driven Development<br/>RED → GREEN → REFACTOR"]
        T0_DOR["Definition of READY<br/>Clear Requirements First"]
        T0_DOD["Definition of DONE<br/>Zero Errors, Zero Warnings"]
        T0_BP["Brain Protection (Rule #22)<br/>Challenge Risky Changes"]
        T0_IC["Incremental Creation<br/>Large Files in Chunks"]
    end

    subgraph tier1["💾 TIER 1: WORKING MEMORY<br/>(Last 20 Conversations)"]
        T1_CONV["Conversation History<br/>FIFO Queue"]
        T1_MSG["Message Context<br/>Last 10 Messages"]
        T1_ENT["Entity Tracking<br/>Files, Classes, Methods"]
        T1_PERF["Performance: 18ms avg<br/>Target: <50ms"]
    end

    subgraph tier2["🧩 TIER 2: KNOWLEDGE GRAPH<br/>(Long-Term Memory)"]
        T2_PAT["Intent Patterns<br/>Learning from Conversations"]
        T2_REL["File Relationships<br/>Co-modification Tracking"]
        T2_WORK["Workflow Templates<br/>Proven Patterns"]
        T2_VAL["Validation Insights<br/>Correction History"]
        T2_PERF["Performance: 92ms avg<br/>Target: <150ms"]
    end

    subgraph tier3["📊 TIER 3: CONTEXT INTELLIGENCE<br/>(Development Metrics)"]
        T3_GIT["Git Analysis<br/>Commit Velocity, Hotspots"]
        T3_CODE["Code Health<br/>Test Coverage, Build Success"]
        T3_SESS["Session Analytics<br/>Productivity Patterns"]
        T3_FILE["File Stability<br/>Churn Rate Classification"]
        T3_PERF["Performance: 156ms avg<br/>Target: <200ms"]
    end

    tier0 -.->|"Enforces Rules"| tier1
    tier0 -.->|"Protects Integrity"| tier2
    tier0 -.->|"Validates Quality"| tier3
    
    tier1 -->|"Recent Patterns"| tier2
    tier2 -->|"Historical Context"| tier3
    tier1 -.->|"Active Context"| tier3

    style tier0 fill:#6B46C1,stroke:#4C1D95,color:#fff
    style tier1 fill:#3B82F6,stroke:#1E3A8A,color:#fff
    style tier2 fill:#10B981,stroke:#065F46,color:#fff
    style tier3 fill:#F59E0B,stroke:#92400E,color:#fff
```

---

## How to View

1. **Open this markdown file** (PREVIEW-01-tier-architecture.md)
2. **Press:** `Ctrl+Shift+V` (Windows) or `Cmd+Shift+V` (Mac)
3. **Or:** Right-click → "Open Preview"

The Markdown Preview Mermaid Support extension will render the diagram automatically.
