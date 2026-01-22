# LENS Overview & Architecture

## System Design

The LENS Protocol is CORTEX's foundational intent comprehension system. It transforms user requests through four complementary analysis layers (Language, Examination, Navigation, Synthesis) to enable precise intent routing with high confidence scoring.

## Architecture Overview

```mermaid
graph TB
    Request["User Request<br/>Text/JSON/Code/Schema"]
    
    subgraph LENS["LENS Protocol Layers"]
        L["<b>L: Language Layer</b><br/>Intent Classification<br/>Multi-label ML model<br/>Confidence scoring"]
        E["<b>E: Examination Layer</b><br/>AST Analysis<br/>Code semantics<br/>Symbol resolution"]
        N["<b>N: Navigation Layer</b><br/>Git History Analysis<br/>Change patterns<br/>Hotspot detection"]
        S["<b>S: Synthesis Layer</b><br/>Signal aggregation<br/>Governance application<br/>Confidence calculation"]
    end
    
    subgraph ContextSources["Context Sources"]
        Gov["Governance Rules<br/>TIER 0-3"]
        KB["Knowledge Repository<br/>Best Practices"]
        DB["Domain Brain<br/>Business Entities"]
        KG["Knowledge Graph<br/>(Optional)"]
    end
    
    Request --> L
    Request --> E
    Request --> N
    
    L --> ContextAgg["Context Aggregator"]
    E --> ContextAgg
    N --> ContextAgg
    
    ContextAgg --> S
    
    Gov --> S
    KB --> S
    DB --> S
    KG -.-> S
    
    S --> Decision{"Confidence<br/>≥ 0.7?"}
    
    Decision -->|Yes| Route["Route to<br/>Orchestrator"]
    Decision -->|No| Disamb["Disambiguation<br/>& Options"]
    
    Route --> Exec["Orchestration<br/>Execution"]
    Disamb --> User["Present Options<br/>to User"]
    User -->|Select| Exec
    
    style L fill:#4A90E2,stroke:#2E5C8A,color:#fff,stroke-width:2px
    style E fill:#50C878,stroke:#2F7C4F,color:#fff,stroke-width:2px
    style N fill:#F39C12,stroke:#B8860B,color:#fff,stroke-width:2px
    style S fill:#9B59B6,stroke:#6C3D6C,color:#fff,stroke-width:2px
    style Route fill:#27AE60,stroke:#1E8449,color:#fff
    style Disamb fill:#E74C3C,stroke:#A93226,color:#fff
    style LENS fill:#f9f,stroke:#666,stroke-width:2px,stroke-dasharray: 5
    style ContextSources fill:#fff9e6,stroke:#666
```

## Component Architecture

```mermaid
graph TB
    IntentClassifier["IntentClassifier<br/>(Language Layer)"]
    MultiModalProcessor["MultiModalIntentProcessor<br/>TEXT/JSON/COMMAND/CODE/SCHEMA"]
    ConfidenceScorer["ConfidenceScorer<br/>Multi-label scoring"]
    
    ASTAnalyzer["ASTAnalyzer<br/>(Examination Layer)"]
    SymbolResolver["SymbolResolver<br/>Import resolution"]
    SemanticAnalyzer["SemanticAnalyzer<br/>Type inference"]
    
    GitNavigator["GitNavigator<br/>(Navigation Layer)"]
    ChangeAnalyzer["ChangeAnalyzer<br/>Pattern detection"]
    HotspotDetector["HotspotDetector<br/>Churn analysis"]
    
    ContextManager["ContextManager<br/>State aggregation"]
    
    GovernanceRegistry["GovernanceRegistry<br/>Rule enforcement"]
    KnowledgeRepository["KnowledgeRepository<br/>Best practices"]
    BusinessKnowledgeRepo["BusinessKnowledgeRepository<br/>Domain context"]
    
    Synthesizer["Synthesizer<br/>(Synthesis Layer)"]
    ConfidenceCalculator["ConfidenceCalculator<br/>Score aggregation"]
    
    Router["Intent Router<br/>Routing engine"]
    
    IntentClassifier --> MultiModalProcessor
    MultiModalProcessor --> ConfidenceScorer
    
    ASTAnalyzer --> SymbolResolver
    SymbolResolver --> SemanticAnalyzer
    
    GitNavigator --> ChangeAnalyzer
    ChangeAnalyzer --> HotspotDetector
    
    ConfidenceScorer --> ContextManager
    SemanticAnalyzer --> ContextManager
    HotspotDetector --> ContextManager
    
    ContextManager --> Synthesizer
    
    GovernanceRegistry --> Synthesizer
    KnowledgeRepository --> Synthesizer
    BusinessKnowledgeRepo --> Synthesizer
    
    Synthesizer --> ConfidenceCalculator
    ConfidenceCalculator --> Router
    
    style IntentClassifier fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style ASTAnalyzer fill:#50C878,stroke:#2F7C4F,color:#fff
    style GitNavigator fill:#F39C12,stroke:#B8860B,color:#fff
    style Synthesizer fill:#9B59B6,stroke:#6C3D6C,color:#fff
    style Router fill:#27AE60,stroke:#1E8449,color:#fff
```

## Detailed Layer Architecture

### Language Layer (L)

The language layer performs natural language understanding using multi-label classification:

```mermaid
graph LR
    Input["User Input<br/>Natural Language"]
    
    subgraph LanguageLayer["Language Layer"]
        Tokenize["Tokenization &<br/>Preprocessing"]
        MultiModal["MultiModal<br/>Detection"]
        Embed["Intent Embedding"]
        Model["ML Classification<br/>Model"]
        Labels["Multi-Label<br/>Predictions"]
    end
    
    Input --> Tokenize
    Tokenize --> MultiModal
    MultiModal --> Embed
    Embed --> Model
    Model --> Labels
    
    Labels --> Confidence["Confidence Scoring<br/>per Intent"]
    Confidence --> Output["Intent List<br/>[Intent, score]"]
    
    style LanguageLayer fill:#e6f2ff,stroke:#4A90E2,stroke-width:2px
```

**Key Features:**
- **Multi-Label Classification**: Single request can match multiple intents
- **Modality Support**: TEXT, JSON, COMMAND, CODE, SCHEMA inputs
- **Confidence Scoring**: Per-intent confidence [0, 1] range
- **Fallback Strategies**: Fuzzy matching when confidence low

### Examination Layer (E)

The examination layer analyzes code structure through AST parsing and semantic analysis:

```mermaid
graph LR
    File["Source File<br/>Code"]
    
    subgraph ExamLayer["Examination Layer"]
        Parse["AST Parsing"]
        Resolve["Symbol Resolution<br/>Imports/Definitions"]
        Semantic["Semantic Analysis<br/>Types/Relationships"]
        Quality["Quality Metrics<br/>Hallucination Check"]
    end
    
    File --> Parse
    Parse --> Resolve
    Resolve --> Semantic
    Semantic --> Quality
    
    Quality --> Output["Examination Results<br/>AST + Metadata"]
    
    style ExamLayer fill:#e6ffe6,stroke:#50C878,stroke-width:2px
```

**Key Features:**
- **AST Parsing**: Full Python AST with symbol table
- **Import Resolution**: Transitive import tracking
- **Type Inference**: Basic type information extraction
- **Code Quality Metrics**: Hallucination boundary detection

### Navigation Layer (N)

The navigation layer analyzes Git history to extract change patterns:

```mermaid
graph LR
    Repo["Git Repository"]
    
    subgraph NavLayer["Navigation Layer"]
        Log["Git Log Analysis"]
        Pattern["Pattern Detection<br/>Frequency/Trend"]
        Hotspot["Hotspot Analysis<br/>High Churn"]
        Evolution["Code Evolution<br/>Historical Context"]
    end
    
    Repo --> Log
    Log --> Pattern
    Pattern --> Hotspot
    Pattern --> Evolution
    
    Output["Navigation Results<br/>Patterns + Context"]
    Hotspot --> Output
    Evolution --> Output
    
    style NavLayer fill:#fff9e6,stroke:#F39C12,stroke-width:2px
```

**Key Features:**
- **Change Pattern Analysis**: Frequency, recency, authorship
- **Hotspot Detection**: High-churn files and functions
- **Evolution Tracking**: Historical code changes
- **Impact Prediction**: Files likely affected by similar changes

### Synthesis Layer (S)

The synthesis layer aggregates all signals and applies governance rules:

```mermaid
graph LR
    Lang["Language<br/>Signals"]
    Exam["Examination<br/>Signals"]
    Nav["Navigation<br/>Signals"]
    
    subgraph SynthLayer["Synthesis Layer"]
        Agg["Signal<br/>Aggregation"]
        Weight["Weighted<br/>Combination"]
        Gov["Governance<br/>Application"]
        Final["Confidence<br/>Calculation"]
    end
    
    Lang --> Agg
    Exam --> Agg
    Nav --> Agg
    
    Agg --> Weight
    Weight --> Gov
    Gov --> Final
    
    Final --> Score["Final Score<br/>[0, 1]"]
    Score --> Decision{"≥ 0.7?"}
    
    Decision -->|Yes| Route["Route"]
    Decision -->|No| Disamb["Disambiguate"]
    
    style SynthLayer fill:#f9e6ff,stroke:#9B59B6,stroke-width:2px
    style Route fill:#e6ffe6,stroke:#27AE60,stroke-width:2px
    style Disamb fill:#ffe6e6,stroke:#E74C3C,stroke-width:2px
```

**Key Features:**
- **Signal Aggregation**: Combines all layer outputs
- **Weighted Scoring**: Configurable signal weights
- **Governance Integration**: TIER 0-3 rule application
- **Threshold-Based Routing**: 0.7 confidence threshold

## Data Flow: Request to Routing Decision

```mermaid
sequenceDiagram
    participant User
    participant LensProtocol as LENS<br/>Protocol
    participant L as Language<br/>Layer
    participant E as Examination<br/>Layer
    participant N as Navigation<br/>Layer
    participant S as Synthesis<br/>Layer
    participant Router as Intent<br/>Router
    
    User->>LensProtocol: Submit request
    
    par Language Analysis
        LensProtocol->>L: Process text/code
        L-->>LensProtocol: Intents + scores
    and Examination
        LensProtocol->>E: Parse code structure
        E-->>LensProtocol: AST + metadata
    and Navigation
        LensProtocol->>N: Analyze history
        N-->>LensProtocol: Patterns + context
    end
    
    LensProtocol->>S: Aggregate signals
    S->>S: Apply governance rules
    S-->>LensProtocol: Confidence score
    
    alt Score ≥ 0.7
        LensProtocol->>Router: Route with confidence
        Router-->>User: Routing decision
    else Score < 0.7
        LensProtocol->>Router: Request clarification
        Router-->>User: Present options
    end
```

## Integration with Domain Brain

```mermaid
graph TB
    Request["Operation Request"]
    
    subgraph LENS["LENS Analysis"]
        L["Language Layer"]
        E["Examination Layer"]
        N["Navigation Layer"]
        S["Synthesis Layer"]
    end
    
    Request --> L & E & N
    L & E & N --> S
    
    subgraph DomainContext["Domain Brain Context"]
        Domains["Domain<br/>Catalog"]
        Services["Service<br/>Registry"]
        APIs["API<br/>Definitions"]
        Knowledge["Business<br/>Knowledge"]
    end
    
    S -->|Query| DomainContext
    S -->|Enrich| Synthesis["Signal<br/>Enrichment"]
    
    Synthesis -->|Apply| Rules["Governance<br/>Rules<br/>TIER 0-3"]
    
    Rules --> Decision["Routing<br/>Decision"]
    
    Decision -->|High Confidence| Route["Route to<br/>Orchestrator"]
    Decision -->|Low Confidence| Disamb["Disambiguate"]
    
    style L fill:#4A90E2,color:#fff
    style E fill:#50C878,color:#fff
    style N fill:#F39C12,color:#fff
    style S fill:#9B59B6,color:#fff
    style Route fill:#27AE60,color:#fff
    style Disamb fill:#E74C3C,color:#fff
```

## Performance Characteristics

| Component | Latency | Notes |
|-----------|---------|-------|
| **Language Layer** | ~50ms | ML inference (CPU) |
| **Examination Layer** | ~200ms | File size dependent |
| **Navigation Layer** | ~400ms | Git operations |
| **Synthesis Layer** | ~100ms | Governance + scoring |
| **Total E2E** | ~750ms | Typical request |

## Test Coverage

- **Intent Classification**: 128/128 tests (100%)
- **AST Analysis**: Full symbol resolution validation
- **Git Navigation**: Pattern detection and hotspot identification
- **Synthesis Engine**: Confidence calculation and governance application
- **Integration Tests**: End-to-end LENS pipeline

## Next Steps

- [Intent Classification Details](02-intent-classification.md)
- [AST Analysis & Examination](03-ast-analysis.md)
- [Git History & Navigation](04-git-navigation.md)
- [Knowledge Integration & Synthesis](05-knowledge-synthesis.md)
- [LENS Crawler Implementation](06-lens-crawler.md)
- [Domain Brain Integration](07-domain-brain-integration.md)
