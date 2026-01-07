# Onboarding Orchestrator - Visual Flowcharts

**Purpose:** Mermaid diagrams for onboarding orchestrator workflows  
**Version:** 3.8.1  
**Date:** December 7, 2025

---

## 1. Overall System Architecture

```mermaid
graph TB
    subgraph "User Application"
        A[Source Code]
        B[Config Files]
        C[Dependencies]
    end
    
    subgraph "CORTEX Onboarding System"
        D[Onboarding Orchestrator]
        
        subgraph "Analysis Phase"
            E1[Metadata Gatherer]
            E2[Quality Analyzer]
            E3[Security Scanner]
            E4[Performance Monitor]
            E5[Architecture Builder]
            E6[Tech Stack Analyzer]
            E7[Recommendations Engine]
            E8[UML Generator]
        end
        
        subgraph "Collection Phase - Parallel"
            F1[TechStack Collector]
            F2[Security Collector]
            F3[Architecture Collector]
            F4[CodeOrg Collector]
            F5[Vendor Collector]
            F6[Team Metrics Collector]
        end
        
        subgraph "Output Generation"
            G[Dashboard Data Writer]
            H[Validator]
        end
    end
    
    subgraph "Output Artifacts"
        I[7 JSON Files]
        J[HTML Dashboard]
        K[Validation Report]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E1
    E1 --> E2
    E2 --> E3
    E3 --> E4
    E4 --> E5
    E5 --> E6
    E6 --> E7
    E7 --> E8
    
    E8 --> F1
    E8 --> F2
    E8 --> F3
    E8 --> F4
    E8 --> F5
    E8 --> F6
    
    F1 --> G
    F2 --> G
    F3 --> G
    F4 --> G
    F5 --> G
    F6 --> G
    
    G --> I
    I --> H
    H --> J
    H --> K
```

---

## 2. Onboarding Workflow - Detailed Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant M as Metadata
    participant Q as Quality
    participant S as Security
    participant A as Architecture
    participant T as TechStack
    participant P as Parallel Collectors
    participant D as Dashboard
    participant V as Validator
    
    U->>O: onboard_application(project_path)
    
    Note over O: Phase 1: Metadata
    O->>M: gather_project_info()
    M-->>O: {files, lines, languages}
    
    Note over O: Phase 2: Quality
    O->>Q: run_quality_analysis()
    Q-->>O: {issues[], score}
    
    Note over O: Phase 3: Security
    O->>S: run_security_scan()
    S-->>O: {vulnerabilities[]}
    
    Note over O: Phase 4-6: Architecture & Tech
    O->>A: generate_architecture_graph()
    A-->>O: {nodes[], links[]}
    O->>T: analyze_tech_stack()
    T-->>O: {languages[], frameworks[]}
    
    Note over O: Phase 9: Parallel Collection (6 threads)
    O->>P: collect_all_parallel()
    
    par Thread 1
        P->>P: TechStackCollector
    and Thread 2
        P->>P: SecurityCollector
    and Thread 3
        P->>P: ArchitectureCollector
    and Thread 4
        P->>P: CodeOrgCollector
    and Thread 5
        P->>P: VendorCollector
    and Thread 6
        P->>P: TeamMetricsCollector
    end
    
    P-->>O: {6 JSON files}
    
    O->>D: write_dashboard_files()
    D-->>O: files written
    
    Note over O: Phase 10: Validation
    O->>V: validate_dashboard()
    V-->>O: {success, report}
    
    O-->>U: OnboardingResult{success, dashboard_url}
```

---

## 3. File Filtering Decision Tree

```mermaid
graph TD
    A[File Encountered] --> B{Hidden Directory?}
    B -->|Yes .git, .venv, etc| Z[❌ SKIP]
    B -->|No| C{Build Artifact?}
    
    C -->|Yes __pycache__, dist, etc| Z
    C -->|No| D{Binary Extension?}
    
    D -->|Yes .pyc, .dll, etc| Z
    D -->|No| E{Has File Extension?}
    
    E -->|No| Y[✅ INCLUDE]
    E -->|Yes| F{Source Extension?}
    
    F -->|Yes .py, .js, .cs, etc| Y
    F -->|No| Z
    
    style Y fill:#90EE90
    style Z fill:#FFB6C1
```

---

## 4. Mode-Specific Path Resolution

```mermaid
graph LR
    subgraph "Production Mode"
        A1[User Repo Root] --> B1[cortex-brain/]
        B1 --> C1[dashboards/]
        C1 --> D1[project-slug/]
        D1 --> E1[JSON Files]
    end
    
    subgraph "Test Mode"
        A2[CORTEX Root] --> B2[cortex-brain/]
        B2 --> C2[documents/]
        C2 --> D2[onboarded-apps/]
        D2 --> E2[project-slug/]
        E2 --> F2[JSON Files]
    end
    
    style A1 fill:#87CEEB
    style A2 fill:#FFD700
```

---

## 5. Parallel Collector Thread Pool

```mermaid
graph TD
    A[ParallelCollectorOrchestrator] --> B[ThreadPoolExecutor - 6 Workers]
    
    B --> C1[Worker 1]
    B --> C2[Worker 2]
    B --> C3[Worker 3]
    B --> C4[Worker 4]
    B --> C5[Worker 5]
    B --> C6[Worker 6]
    
    C1 --> D1[TechStackCollector.collect]
    C2 --> D2[SecurityCollector.collect]
    C3 --> D3[ArchitectureCollector.collect]
    C4 --> D4[CodeOrgCollector.collect]
    C5 --> D5[VendorCollector.collect]
    C6 --> D6[TeamMetricsCollector.collect]
    
    D1 --> E1[tech-stack.json]
    D2 --> E2[security.json]
    D3 --> E3[architecture.json]
    D4 --> E4[code-organization.json]
    D5 --> E5[vendors.json]
    D6 --> E6[team-metrics.json]
    
    E1 --> F[Aggregator]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F
    E6 --> F
    
    F --> G[health-data.json]
    F --> H[metadata.json]
    
    style B fill:#FFA500
    style F fill:#9370DB
```

---

## 6. Health Score Calculation Flow

```mermaid
graph TD
    A[Collected Data] --> B[security.json]
    A --> C[code-organization.json]
    A --> D[architecture.json]
    A --> E[tech-stack.json]
    
    B --> F[Security Score × 0.35]
    C --> G[Code Score × 0.25]
    D --> H[Architecture Score × 0.25]
    E --> I[Tech Score × 0.15]
    
    F --> J[Sum All Components]
    G --> J
    H --> J
    I --> J
    
    J --> K{Score Range?}
    K -->|80-100| L[✅ Healthy]
    K -->|60-79| M[⚠️ Warning]
    K -->|0-59| N[❌ Critical]
    
    style L fill:#90EE90
    style M fill:#FFD700
    style N fill:#FFB6C1
```

---

## 7. Dashboard Validation State Machine

```mermaid
stateDiagram-v2
    [*] --> CheckFiles
    CheckFiles --> ValidateStructure: Files Exist
    CheckFiles --> Failed: Missing Files
    
    ValidateStructure --> CheckTabs: Valid JSON
    ValidateStructure --> Failed: Invalid Structure
    
    CheckTabs --> CheckJavaScript: All 7 Tabs Load
    CheckTabs --> WarningState: Some Tabs Missing
    
    CheckJavaScript --> CheckInteractive: Functions Present
    CheckJavaScript --> WarningState: Missing Functions
    
    CheckInteractive --> CheckVisualizations: Elements Work
    CheckInteractive --> WarningState: Broken Elements
    
    CheckVisualizations --> Success: Configured
    CheckVisualizations --> WarningState: Issues Found
    
    WarningState --> GenerateReport
    Failed --> GenerateReport
    Success --> GenerateReport
    
    GenerateReport --> [*]
```

---

## 8. Error Handling Flow

```mermaid
graph TD
    A[Phase Execution] --> B{Exception?}
    B -->|No| C[Continue to Next Phase]
    B -->|Yes| D{Critical Error?}
    
    D -->|Yes| E[Log Error]
    E --> F[Add to errors[]]
    F --> G[Return OnboardingResult]
    G --> H[success = False]
    
    D -->|No| I[Log Warning]
    I --> J[Use Fallback/Default]
    J --> C
    
    C --> K{More Phases?}
    K -->|Yes| A
    K -->|No| L{Any Errors?}
    
    L -->|No| M[success = True]
    L -->|Yes| H
    
    M --> N[Return Complete Result]
    H --> N
    
    style E fill:#FFB6C1
    style I fill:#FFD700
    style M fill:#90EE90
```

---

## 9. Integration with Other Orchestrators

```mermaid
graph TB
    subgraph "Entry Point"
        A[UnifiedEntryPointOrchestrator]
    end
    
    subgraph "User Workflows"
        B[New User Flow]
        C[Application Onboarding]
        D[Dashboard Launch]
    end
    
    subgraph "Orchestrators"
        E[OnboardingAcknowledgment<br/>Orchestrator]
        F[OnboardingApplication<br/>Orchestrator]
        G[DashboardLauncher<br/>Orchestrator]
    end
    
    A --> B
    A --> C
    A --> D
    
    B --> E
    C --> F
    D --> G
    
    E --> H[Governance<br/>Acknowledged]
    F --> I[Application<br/>Analyzed]
    G --> J[Dashboard<br/>Displayed]
    
    H -.->|Enables| C
    I -.->|Provides Data| D
    
    style E fill:#87CEEB
    style F fill:#FFD700
    style G fill:#98FB98
```

---

## 10. Phase Dependency Graph

```mermaid
graph TD
    P1[Phase 1: Metadata] --> P2[Phase 2: Quality]
    P1 --> P3[Phase 3: Security]
    P1 --> P5[Phase 5: Architecture]
    P1 --> P6[Phase 6: Tech Stack]
    
    P2 --> P7[Phase 7: Recommendations]
    P3 --> P7
    P5 --> P7
    P6 --> P7
    
    P1 --> P8[Phase 8: UML]
    
    P7 --> P9[Phase 9: Parallel Collection]
    P8 --> P9
    
    P9 --> P10[Phase 10: Validation]
    
    P10 --> DONE[✅ Complete]
    
    style P1 fill:#FFE4B5
    style P9 fill:#FFA500
    style P10 fill:#98FB98
    style DONE fill:#90EE90
```

---

## 11. Collector Class Hierarchy

```mermaid
classDiagram
    class BaseDataCollector {
        <<abstract>>
        +project_path: Path
        +collect()* Dict~str, Any~
        +_should_include_file(file: Path) bool
    }
    
    class TechStackCollector {
        +collect() Dict
        -_detect_languages()
        -_detect_frameworks()
        -_parse_dependencies()
    }
    
    class SecurityCollector {
        +collect() Dict
        -_scan_vulnerabilities()
        -_check_owasp_patterns()
        -_calculate_score()
    }
    
    class ArchitectureCollector {
        +collect() Dict
        -_build_dependency_graph()
        -_identify_components()
        -_detect_patterns()
    }
    
    class CodeOrganizationCollector {
        +collect() Dict
        -_count_files()
        -_count_lines()
        -_identify_hotspots()
    }
    
    class VendorCollector {
        +collect() Dict
        -_detect_external_apis()
        -_parse_imports()
    }
    
    BaseDataCollector <|-- TechStackCollector
    BaseDataCollector <|-- SecurityCollector
    BaseDataCollector <|-- ArchitectureCollector
    BaseDataCollector <|-- CodeOrganizationCollector
    BaseDataCollector <|-- VendorCollector
```

---

## 12. OnboardingResult State Transitions

```mermaid
stateDiagram-v2
    [*] --> Initializing
    Initializing --> Running: Start Onboarding
    
    Running --> Phase1: Metadata
    Phase1 --> Phase2: Quality
    Phase2 --> Phase3: Security
    Phase3 --> Phase4: Performance
    Phase4 --> Phase5: Architecture
    Phase5 --> Phase6: TechStack
    Phase6 --> Phase7: Recommendations
    Phase7 --> Phase8: UML
    Phase8 --> Phase9: Collection
    Phase9 --> Phase10: Validation
    
    Phase10 --> Success: No Errors
    Phase10 --> SuccessWithWarnings: Validation Issues
    
    Phase1 --> Failed: Critical Error
    Phase2 --> Failed: Critical Error
    Phase3 --> Failed: Critical Error
    Phase9 --> Failed: Critical Error
    
    Success --> [*]
    SuccessWithWarnings --> [*]
    Failed --> [*]
```

---

## Diagram Usage Guide

### For Presentations
- Use **Diagram 1** (System Architecture) for high-level overview
- Use **Diagram 2** (Sequence) for explaining execution flow
- Use **Diagram 6** (Health Score) for quality metrics explanation

### For Development
- Use **Diagram 3** (File Filtering) when implementing file scanners
- Use **Diagram 5** (Thread Pool) when debugging parallel execution
- Use **Diagram 10** (Phase Dependencies) for understanding phase order

### For Troubleshooting
- Use **Diagram 8** (Error Handling) for debugging failures
- Use **Diagram 7** (Validation) for dashboard issues
- Use **Diagram 4** (Path Resolution) for file location problems

### For Architecture Reviews
- Use **Diagram 11** (Class Hierarchy) for OOP design discussions
- Use **Diagram 9** (Integration) for system integration understanding
- Use **Diagram 12** (State Transitions) for workflow state management

---

**Rendering Instructions:**

These diagrams use Mermaid syntax. To view them:

1. **GitHub:** Automatically rendered in `.md` files
2. **VS Code:** Install "Markdown Preview Mermaid Support" extension
3. **Online:** Use https://mermaid.live/
4. **Export:** Use Mermaid CLI to generate PNG/SVG

```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate PNG
mmdc -i flowcharts.md -o flowcharts.png

# Generate SVG
mmdc -i flowcharts.md -o flowcharts.svg
```

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025  
**Maintainer:** Asif Hussain
