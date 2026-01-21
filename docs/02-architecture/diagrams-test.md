# System Architecture Diagram

This page demonstrates Mermaid diagram rendering in the CORTEX documentation.

## Architecture Overview

```mermaid
flowchart TB
    subgraph "USER INTERFACE LAYER"
        REST["REST API<br/>(FastAPI)"]
        MCP["MCP Server<br/>(JSON-RPC)"]
        CLI["CLI<br/>(Cortex-*)"]
        COPILOT["Copilot Chat<br/>(Prompts/Agents)"]
    end
    
    subgraph "LENS PROTOCOL<br/>(Intent Comprehension)"
        L["Language Phase<br/>Intent parsing"]
        E["Examination Phase<br/>AST analysis"]
        N["Navigation Phase<br/>Git history"]
        S["Synthesis Phase<br/>Context aggregation"]
    end
    
    subgraph "GOVERNANCE TIERS"
        T0["Tier 0: Core Rules<br/>CORE-001 thru CORE-029"]
        T1["Tier 1: Domain Rules<br/>Confirmation Gate<br/>Complexity Matrix"]
        T2["Tier 2: Standards<br/>Response Templates<br/>Best Practices"]
    end
    
    subgraph "MASTER ORCHESTRATOR<br/>(ConversationProtocol)"
        STAGE1["Stage 1: Context"]
        STAGE2["Stage 2: Routing"]
        GATE["Stage 2.5: Gate"]
        STAGE3["Stage 3: Execute"]
        STAGE4["Stage 4: Response"]
    end
    
    REST --> L
    MCP --> L
    CLI --> L
    COPILOT --> L
    
    L --> E --> N --> S
    S --> STAGE1
    
    STAGE1 --> T0
    STAGE1 --> T1
    STAGE1 --> T2
    
    STAGE1 --> STAGE2 --> GATE --> STAGE3 --> STAGE4
```

## Governance Tier Hierarchy

```mermaid
flowchart TD
    T0["🔒 Tier 0: Immutable Core Rules"]
    T1["📋 Tier 1: Domain Rules"]
    T2["⚙️ Tier 2: Standards"]
    T3["🔄 Tier 3: Runtime Rules"]
    
    T0 -->|Immutable| T1
    T1 -->|Context-aware| T2
    T2 -->|Runtime-specific| T3
    
    style T0 fill:#ff6b6b,color:#fff
    style T1 fill:#ffa500,color:#fff
    style T2 fill:#4ecdc4,color:#fff
    style T3 fill:#95e1d3,color:#000
```

## Phase Dependencies

```mermaid
flowchart LR
    A["Phase A<br/>Consolidation"] 
    B["Phase B<br/>MCP Registry"]
    C["Phase C<br/>Hardening"]
    E["Phase E<br/>TDD"]
    H["Phase H<br/>E2E"]
    I["Phase I<br/>CI/CD"]
    J["Phase J<br/>Governance"]
    END["100%<br/>Production"]
    
    A -->|Done| B
    B -->|Done| C
    C -->|In Progress| E
    E -->|Pending| H
    H -->|Pending| I
    I -->|Pending| J
    J -->|Final| END
    
    style END fill:#51cf66,color:#fff,stroke:#2f9e44,stroke-width:3px
```

## Orchestration Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as REST/MCP/CLI
    participant Router as Intent Router
    participant Orch as Master Orchestrator
    participant Brain as Domain Brain
    participant DB as State Store
    
    Client->>API: Request (intent)
    API->>Router: Route intent
    Router->>Orch: Execute (LENS protocol)
    Orch->>Brain: Query knowledge
    Brain->>DB: Fetch context
    DB-->>Brain: Context
    Brain-->>Orch: Knowledge
    Orch->>Orch: Decide (stage 1-4)
    Orch->>DB: Update state
    Orch-->>API: Result
    API-->>Client: Response
```

## Error Recovery Pattern

```mermaid
sequenceDiagram
    participant Client
    participant Retry as Retry Handler
    participant CB as Circuit Breaker
    participant Fallback
    participant Service
    
    Client->>Retry: Request
    loop Retry (max 3x)
        Retry->>CB: Check state
        alt Circuit CLOSED
            CB->>Service: Forward
            alt Success
                Service-->>Client: Result ✅
            else Failure
                Service-->>CB: Error
                CB->>CB: Increment failures
                Note over CB: If failures > threshold
                CB->>CB: OPEN circuit
            end
        else Circuit OPEN
            CB-->>Fallback: Get fallback
            Fallback-->>Client: Degraded response
        end
    end
```

---

**Note:** All diagrams on this page render using Mermaid.js. If you see code instead of graphics, verify that MkDocs Mermaid support is enabled in `mkdocs.yml`.

For more architecture details, see:
- [System Overview](../02-architecture/1-system-overview.md)
- [LENS Protocol](../02-architecture/7-intent-router.md)
- [Governance Rules](../02-architecture/governance-rules.md)
