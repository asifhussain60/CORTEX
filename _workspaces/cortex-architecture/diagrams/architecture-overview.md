# CORTEX Architecture Overview Diagram

**Updated:** 2026-02-11 | **Version:** 2.0.0

---

## System-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🌐 CLIENT LAYER                                    │
│               (AI Assistants & Development Tools)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  GitHub    │  │   Claude   │  │   Cursor   │  │   Custom   │           │
│  │  Copilot   │  │  Desktop   │  │    IDE     │  │   Clients  │           │
│  │  Chat      │  │            │  │            │  │            │           │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘           │
│         │                │                │                │                 │
│         └────────────────┴────────────────┴────────────────┘                 │
│                              │ MCP Protocol                                  │
│                              │ (JSON-RPC 2.0)                                │
└──────────────────────────────┼──────────────────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────────────────┐
│                         🔗 MCP GATEWAY LAYER                                 │
│                      (Communication Interface)                               │
├──────────────────────────────┼──────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     MCP Server (stdio/HTTP)                            │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐               │  │
│  │  │   Tool      │  │    Request   │  │   Response    │               │  │
│  │  │  Registry   │  │   Validator  │  │   Formatter   │               │  │
│  │  │  (86 tools) │  │              │  │               │               │  │
│  │  └─────────────┘  └──────────────┘  └───────────────┘               │  │
│  │                                                                        │  │
│  │  Capabilities:                                                        │  │
│  │  • Tool discovery & invocation                                       │  │
│  │  • Request authentication & routing                                  │  │
│  │  • Response serialization (JSON-RPC)                                 │  │
│  │  • Health monitoring & metrics                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────────────────┐
│                      🧠 ORCHESTRATION LAYER                                  │
│                    (Cognitive Processing Center)                             │
├──────────────────────────────┼──────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                   🎯 MasterOrchestrator                                │  │
│  │             (Executive Coordinator - Entry Point)                      │  │
│  │  • Environment validation                                             │  │
│  │  • Dependency resolution                                              │  │
│  │  • Lifecycle management                                               │  │
│  └───────────────────────────┬───────────────────────────────────────────┘  │
│                              ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     🧭 IntentRouter                                    │  │
│  │              (Decision Engine - Request Classifier)                   │  │
│  │  Classifies: IMPLEMENT │ FIX │ REFACTOR │ ANALYZE │ PLAN │ DEBUG     │  │
│  └─┬────────────────┬────────────────┬────────────────┬──────────────────┘  │
│    │                │                │                │                     │
│    ▼                ▼                ▼                ▼                     │
│  ┌────────┐    ┌────────┐      ┌────────┐      ┌────────┐                  │
│  │🧠 Core│    │🎨 Domain│      │🔧Support│      │⚙️ Cross│                  │
│  │  (11) │    │   (8)  │      │  (41)  │      │ Cutting│                  │
│  └────────┘    └────────┘      └────────┘      └────────┘                  │
│                                                                              │
│  Core Examples:                Domain Examples:      Support Examples:      │
│  • TDDOrchestrator            • RefactoringOrch.    • DebugOrchestrator     │
│  • LENSSynthesis              • PlanOrchestrator    • DashboardGen.         │
│  • EnforcementOrch.           • DocumentationOrch.  • KnowledgeQuery        │
└──────────────────────────────────────────────────────────────────────────────┘
         │                               │                          │
         ▼                               ▼                          ▼
┌──────────────────────┐  ┌────────────────────────┐  ┌──────────────────────┐
│  👁️ LENS LAYER      │  │  💾 STORAGE LAYER      │  │  🧠 LEARNING LAYER   │
│  (Code Intelligence) │  │  (Persistence)         │  │  (Adaptive Systems)  │
├──────────────────────┤  ├────────────────────────┤  ├──────────────────────┤
│ • SecurityAnalyzer   │  │ • cortex_brain/        │  │ • Pattern Learning   │
│ • ComplexityAnalyzer │  │ • Knowledge Repos      │  │ • Test Quality Metrics│
│ • ArchitectureAnalyz.│  │ • cortex-registry/     │  │ • Validation Loops   │
│ • GitHistoryAnalyzer │  │ • State Management     │  │ • Adaptive Refinement│
│ • ASTParser          │  │ • Audit Trails         │  │ • Feedback Integration│
│ • PatternDetector    │  │ • Dashboard Data       │  │ • Continuous Improvement│
└──────────────────────┘  └────────────────────────┘  └──────────────────────┘
```

---

## Layer Responsibilities

### 1. Client Layer
**Purpose:** AI assistants and development tools that consume CORTEX capabilities

**Components:**
- GitHub Copilot Chat (VS Code)
- Claude Desktop
- Cursor IDE
- Custom MCP clients

**Interaction:** JSON-RPC 2.0 over stdio or HTTP

---

### 2. MCP Gateway Layer
**Purpose:** Protocol translation and tool management

**Key Features:**
- **86 MCP Tools** exposed via protocol
- Tool discovery (`tools/list`)
- Tool invocation (`tools/call`)
- Health checks & metrics
- Request validation

**Transport:**
- stdio (development, VS Code)
- HTTP (production, port 8000)

---

### 3. Orchestration Layer
**Purpose:** Intelligent request processing and coordination

**Architecture:**
```
MasterOrchestrator (entry point)
  ↓
IntentRouter (classifier)
  ↓
Specialist Orchestrators (60 total)
  ├─ Core (11): Fundamental operations
  ├─ Domain (8): Business logic
  ├─ Support (41): Infrastructure
  └─ Cross-Cutting: Governance, Validation
```

**Key Orchestrators:**
- **TDDOrchestrator:** RED→GREEN→REFACTOR workflow
- **LENSSynthesis:** Deep code intelligence
- **EnforcementOrchestrator:** CORE rules validation
- **HolisticValidationOrchestrator:** Phase 48 gate
- **RefactoringOrchestrator:** Code improvement
- **PlanOrchestrator:** Phase management

---

### 4. LENS Layer
**Purpose:** Code sensory and analysis system

**Capabilities:**
- **Security Analysis:** Vulnerability scanning, OWASP checks
- **Complexity Analysis:** Cyclomatic complexity, cognitive load
- **Architecture Analysis:** Pattern detection, drift identification
- **Git History:** 24-hour context window
- **AST Parsing:** Deep code structure understanding

---

### 5. Storage Layer
**Purpose:** Persistence and state management

**Components:**
- `cortex_brain/`: System state, learned patterns
- `cortex-registry/`: Orchestrator wiring, phase definitions
- `company/`: Customer-specific configurations
- Knowledge repositories: Best practices, domain wisdom

---

### 6. Learning Layer
**Purpose:** Adaptive intelligence and continuous improvement

**Capabilities:**
- Pattern learning from successful implementations
- Test quality measurement and feedback
- Validation loop refinement
- Adaptive threshold tuning
- Feedback integration from user corrections

---

## Data Flow: End-to-End Request

```
1. User Types: "Implement user authentication"
   ↓
2. GitHub Copilot → MCP Protocol
   {
     "tool": "cortex_process_request",
     "args": {"request": "Implement user authentication"}
   }
   ↓
3. MCP Server → Tool Registry
   Validates request, routes to tool handler
   ↓
4. cortex_process_request → MasterOrchestrator
   orchestrator.process_user_request(...)
   ↓
5. MasterOrchestrator → IntentRouter
   intent = classify_request()  # Result: IMPLEMENT
   ↓
6. IntentRouter → TDDOrchestrator
   Load dependencies: LENS, Enforcement, Validation
   ↓
7. TDDOrchestrator → LENS Layer
   lens.analyze(security=True, complexity=True)
   ↓
8. TDDOrchestrator → Challenge Gate
   Generate 3 alternative approaches
   Return to user for selection
   ↓
9. User Selects → "proceed"
   ↓
10. TDD Cycle Execution
    RED: Generate failing tests
    GREEN: Implement minimal code
    REFACTOR: Apply best practices
   ↓
11. EnforcementOrchestrator Validation
    Check CORE-008, CORE-011, CORE-012
   ↓
12. Audit Trail Generation
    AC_START → AC_COMPLETE markers
   ↓
13. Response Generation → MCP Protocol
    {
      "success": true,
      "files_modified": [...],
      "tests_passing": 12,
      "coverage": 94.2
    }
   ↓
14. GitHub Copilot Displays Result
```

---

## Scalability Architecture

### Horizontal Scaling

```
                        Load Balancer
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
   MCP Server 1         MCP Server 2         MCP Server 3
   (Port 8001)          (Port 8002)          (Port 8003)
        │                    │                    │
        └────────────────────┴────────────────────┘
                             │
                   Shared Storage Layer
                   (cortex_brain, registry)
```

### Performance Targets

| Component | Target | Status |
|-----------|--------|--------|
| **MCP Request → Response** | <500ms | ✅ ~320ms |
| **Tool Discovery** | <50ms | ✅ ~25ms |
| **Orchestrator Load** | <100ms | ✅ ~80ms |
| **LENS Analysis** | <2s | ✅ ~1.4s |
| **TDD Cycle (small feature)** | <10s | ✅ ~7s |
| **Concurrent Requests** | 50+ | ✅ Tested |

---

**Last Updated:** 2026-02-11 06:37:48  
**Architecture Version:** 2.0.0  
**Production Ready:** ✅ Yes
