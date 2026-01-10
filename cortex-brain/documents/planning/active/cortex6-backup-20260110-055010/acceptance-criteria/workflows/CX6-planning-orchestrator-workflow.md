# 🎯 CORTEX 6.0 Planning Orchestrator Workflow

**Version:** 3.0.0  
**Date:** 2026-01-09  
**Author:** Asif Hussain  
**Status:** ✅ APPROVED - CORTEX Toolkit & Realignment Integrated

---

## 📋 Executive Summary

The Planning Orchestrator v6.0 implements a **4-phase interactive workflow** that collaborates with users to achieve Definition of Ready (DoR), generates zero-ambiguity execution plans, and executes autonomously with config-based approval enforcement.

**Key Innovations:**
1. **Acceptance criteria** gathered interactively during Phase 1 and enforced throughout execution
2. **CORTEX Toolkit** - Unified modular tools following SOLID/DRY principles, MCP-exposed
3. **Realignment orchestrator** - Periodic health checks with auto-remediation
4. **Audit infrastructure** - Centralized logging with AC-ID traceability

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  PLANNING ORCHESTRATOR v6.0                     │
│         Interactive → Zero Ambiguity → Autonomous Execution     │
└─────────────────────────────────────────────────────────────────┘

Master Orchestrator (Pattern Router + Execution Engine)
    ↓
Planning Orchestrator (4-Phase Workflow)
    ├─► Phase 1: Interactive Requirements (uses CORTEX Toolkit)
    ├─► Phase 2: Zero-Ambiguity Plan Generation
    ├─► Phase 3: Plan Approval & Config Creation
    └─► Phase 4: Autonomous Execution
    
CORTEX Toolkit (Modular, SOLID/DRY, MCP-Exposed)
├─ Semantic Search
├─ AST Parser
├─ Git Analyzer
├─ Knowledge Graph
├─ Pattern Detector
├─ Dependency Mapper
├─ Duplicate Detector
└─ Orphan Detector

Infrastructure Layer (Shared Services)
├─ Audit Logger (src/infrastructure/audit_logger.py)
├─ State Manager
├─ Database Services
└─ Response Renderer

Realignment Orchestrator (Periodic Health Checks)
├─ Audit Consistency Validator
├─ AC Coverage Validator
├─ Knowledge Graph Validator
└─ State/Filesystem Validator
```

---

## 🎯 Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                 PLANNING ORCHESTRATOR v6.0                      │
│                    Interactive → Zero Ambiguity → Autonomous    │
└─────────────────────────────────────────────────────────────────┘

Phase 1: Interactive Requirements Gathering (30-50%)
    ↓ (Uses CORTEX Toolkit for analysis)
    [DoR Checkpoint: Includes Acceptance Criteria]
    ↓
Phase 2: Detailed Plan Generation (15-25%)
    ↓ (Generates plan-viewer.html dashboard)
    [Zero Ambiguity Validation]
    ↓
Phase 3: Plan Approval & Config Creation (Variable)
    ↓
    [config.yaml: approval_granted = true]
    ↓
Phase 4: Autonomous Execution (50-70%)
    ↓
    [Master Orchestrator: Validates config.yaml]
    ↓
[Plan Complete]
    ↓
Realignment Check (Periodic or Phase-Based)
    └─► Health checks, gap detection, auto-remediation
```

---

## 🛠️ CORTEX Toolkit - Modular Analysis Infrastructure

The **CORTEX Toolkit** is a unified system of modular, reusable tools that follow SOLID/DRY principles and are exposed via MCP for external agent usage.

### **Architecture:**

```
src/toolkit/                           # Unified CORTEX Toolkit
├─ __init__.py
├─ base_tool.py                       # Abstract base class
├─ semantic_search.py                 # Workspace semantic search
├─ ast_parser.py                      # Python AST parsing  
├─ git_analyzer.py                    # Git history analysis
├─ knowledge_graph.py                 # Knowledge graph operations
├─ pattern_detector.py                # Code pattern detection
├─ dependency_mapper.py               # Dependency analysis
├─ duplicate_detector.py              # Duplicate code detection
└─ orphan_detector.py                 # Orphan file detection

src/mcp/toolkit_server.py             # MCP server exposing all tools
src/infrastructure/audit_logger.py    # Centralized audit infrastructure
```

### **Design Principles:**

**✅ SOLID Compliance:**
- **S**ingle Responsibility: Each tool has ONE clear purpose
- **O**pen/Closed: Extensible without modification
- **L**iskov Substitution: All tools inherit from BaseTool
- **I**nterface Segregation: Minimal, focused interfaces
- **D**ependency Inversion: Tools depend on abstractions (BaseTool)

**✅ DRY Enforcement:**
- Zero duplicate implementations across orchestrators
- Shared infrastructure (audit logging, state management)
- Reusable components ("Lego pieces")

**✅ MCP Exposure:**
- All 8 tools exposed via standardized MCP server
- External agents (Claude, GPT, etc.) can invoke tools
- Uniform request/response format

**✅ Audit-Aware:**
- All tools log to centralized `EnterpriseAuditLogger`
- AC-ID traceability for every operation
- Dual-format audit trails (JSONL + SQLite)

### **Base Tool Interface:**

```python
# src/toolkit/base_tool.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.infrastructure.audit_logger import EnterpriseAuditLogger

class BaseTool(ABC):
    """
    Base class for all CORTEX toolkit tools.
    
    Enforces:
    - SOLID principles (Single Responsibility)
    - Audit logging for all operations
    - Standardized execute() interface
    """
    
    def __init__(self, audit_logger: EnterpriseAuditLogger):
        self.audit_logger = audit_logger
        self.tool_name = self.__class__.__name__
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool with given context.
        
        Args:
            context: Tool-specific execution context
            
        Returns:
            Tool-specific results dictionary
        """
        pass
    
    def log_execution(self, ac_id: str, details: Dict[str, Any]):
        """Log tool execution to centralized audit infrastructure."""
        self.audit_logger.log_event(
            event_type="toolkit_execution",
            ac_id=ac_id,
            details={
                "tool": self.tool_name,
                **details
            }
        )
```

### **Toolkit Components:**

| Tool | Purpose | Output | MCP Exposed | Audit AC-ID |
|------|---------|--------|-------------|-------------|
| **Semantic Search** | Search workspace for relevant code/docs | Context matches with relevance scores | ✅ | AC-PLAN-SEARCH-001 |
| **AST Parser** | Parse Python files to understand structure | Entity-relationship data (classes, functions, methods) | ✅ | AC-PLAN-AST-001 |
| **Git Analyzer** | Review commits, comments for context | Historical patterns, author insights, change frequency | ✅ | AC-PLAN-GIT-001 |
| **Knowledge Graph** | Build/query entity-relationship graph | domain-knowledge-incremental.json | ✅ | AC-PLAN-GRAPH-001 |
| **Pattern Detector** | Identify reusable code patterns | Common patterns, architectural styles | ✅ | AC-PLAN-PATTERN-001 |
| **Dependency Mapper** | Map internal/external dependencies | dependencies-discovered.yaml | ✅ | AC-PLAN-DEP-001 |
| **Duplicate Detector** | Find duplicate/similar code | Duplication report with recommendations | ✅ | AC-PLAN-DUP-001 |
| **Orphan Detector** | Find orphaned/unused files | Orphan files list with suggested actions | ✅ | AC-PLAN-ORPHAN-001 |

### **Example Tool Implementation:**

```python
# src/toolkit/semantic_search.py
from src.toolkit.base_tool import BaseTool
from typing import Dict, Any, List
from pathlib import Path

class SemanticSearch(BaseTool):
    """
    Semantic workspace search tool.
    
    Searches workspace for relevant code, docs, and patterns
    using semantic similarity matching.
    """
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute semantic search.
        
        Args:
            context: {
                "query": str,
                "workspace": Path,
                "file_types": List[str],
                "max_results": int
            }
            
        Returns:
            {
                "query": str,
                "results": List[SearchResult],
                "count": int,
                "execution_time_ms": float
            }
        """
        query = context['query']
        workspace = context.get('workspace', Path.cwd())
        
        # Log execution start
        self.log_execution(
            "AC-PLAN-SEARCH-001",
            {"query": query, "workspace": str(workspace)}
        )
        
        # Perform search (implementation details...)
        results = self._search_workspace(workspace, query)
        
        # Log execution complete
        self.log_execution(
            "AC-PLAN-SEARCH-001",
            {
                "query": query,
                "results_count": len(results),
                "status": "complete"
            }
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
```

### **MCP Server Exposure:**

```python
# src/mcp/toolkit_server.py
from mcp.server import Server
from src.toolkit import (
    SemanticSearch,
    ASTParser,
    GitAnalyzer,
    KnowledgeGraph,
    PatternDetector,
    DependencyMapper,
    DuplicateDetector,
    OrphanDetector
)
from src.infrastructure.audit_logger import EnterpriseAuditLogger

# Initialize server
server = Server("cortex-toolkit")
audit_logger = EnterpriseAuditLogger()

@server.tool()
def semantic_search(query: str, workspace: str = ".", file_types: List[str] = None):
    """Search workspace semantically for relevant code and documentation."""
    tool = SemanticSearch(audit_logger)
    return tool.execute({
        "query": query,
        "workspace": Path(workspace),
        "file_types": file_types or [".py", ".md", ".yaml"]
    })

@server.tool()
def ast_parse(file_path: str):
    """Parse Python file AST to extract structure information."""
    tool = ASTParser(audit_logger)
    return tool.execute({"file_path": file_path})

# ... (6 more tool exposures)
```

---

## 📊 Phase 1: Interactive Requirements Gathering (WITH CORTEX TOOLKIT)

### **Objective:** Achieve Definition of Ready with zero assumptions using modular toolkit

**Duration:** 30-50% of planning time  
**Mode:** INTERACTIVE (User collaboration required)  
**Tools Used:** All 8 CORTEX Toolkit tools

---

### **Visual Flow:**

```
┌──────────────────────────────────────────────────────────────────┐
│  PHASE 1: Interactive Requirements Gathering (DoR Achievement)   │
│            POWERED BY CORTEX TOOLKIT (SOLID/DRY/MCP)             │
└──────────────────────────────────────────────────────────────────┘

User: "plan user authentication with OAuth2"
    ↓
┌─────────────────────────────────────┐
│ Planning Orchestrator: Introduction │
│ - Interactive planning process      │
│ - CORTEX Toolkit will analyze code  │
│ - Tips for providing context        │
└─────────────────────────────────────┘
    ↓
╔═══════════════════════════════════════════════════════════════╗
║           ITERATIVE REQUIREMENTS CYCLE                        ║
║  (Repeat until Definition of Ready achieved)                  ║
╚═══════════════════════════════════════════════════════════════╝
    │
    ├─► 1. User Provides Context
    │       - Describes work
    │       - States requirements
    │       - Mentions constraints
    │
    ├─► 2. Planning Orchestrator Invokes CORTEX Toolkit
    │       ┌───────────────────────────────────────────┐
    │       │ TOOLKIT EXECUTION (Modular Components):   │
    │       │                                           │
    │       │ ✅ SemanticSearch.execute({              │
    │       │      query: "oauth2 authentication jwt"  │
    │       │    })                                     │
    │       │    → Finds: src/auth/oauth2_provider.py  │
    │       │    → Audit: AC-PLAN-SEARCH-001           │
    │       │                                           │
    │       │ ✅ ASTParser.execute({                   │
    │       │      file_path: "src/auth/*.py"          │
    │       │    })                                     │
    │       │    → Extracts: AuthService, JWTProvider  │
    │       │    → Audit: AC-PLAN-AST-001              │
    │       │                                           │
    │       │ ✅ GitAnalyzer.execute({                 │
    │       │      path: "src/auth/"                   │
    │       │    })                                     │
    │       │    → Security patches, test patterns     │
    │       │    → Audit: AC-PLAN-GIT-001              │
    │       │                                           │
    │       │ ✅ KnowledgeGraph.execute({              │
    │       │      entities: ["AuthService", "User"]   │
    │       │    })                                     │
    │       │    → User → AuthService → JWTProvider    │
    │       │    → Audit: AC-PLAN-GRAPH-001            │
    │       │                                           │
    │       │ ✅ PatternDetector.execute({             │
    │       │      scope: "authentication"             │
    │       │    })                                     │
    │       │    → OAuth2, JWT, Refresh Token patterns │
    │       │    → Audit: AC-PLAN-PATTERN-001          │
    │       │                                           │
    │       │ ✅ DependencyMapper.execute({            │
    │       │      feature: "auth"                     │
    │       │    })                                     │
    │       │    → External: pyjwt, oauth2lib          │
    │       │    → Internal: UserService, RoleService  │
    │       │    → Audit: AC-PLAN-DEP-001              │
    │       └───────────────────────────────────────────┘
    │       
    │       All toolkit executions logged to:
    │       • tracking/requirements-audit.jsonl
    │       • cortex-brain/database/audit_logs (SQLite)
    │
    ├─► 3. Planning Orchestrator Explains Understanding
    │       "✅ Found existing OAuth2 implementation in src/auth/
    │        ✅ Detected JWT token generation (24h expiration)
    │        ✅ Identified reusable: UserService, RoleService
    │        ⚠️ Missing: Refresh token rotation, MFA support
    │        ❓ Questions: Add MFA? Token expiration policy?"
    │
    ├─► 4. Planning Orchestrator Asks for Acceptance Criteria
    │       "For user story: OAuth2 authentication"
    │       "What are the acceptance criteria?"
    │       
    │       User provides criteria:
    │       - "User can log in with email/password"
    │       - "JWT token generated on successful login"
    │       - "Token expires after 24 hours"
    │       
    │       CORTEX validates SMART criteria:
    │       ✓ Specific, ✓ Measurable, ✓ Achievable,
    │       ✓ Relevant, ✓ Testable
    │
    ├─► 5. User Responds with Clarifications
    │
    ├─► 6. Update requirements.yaml (Incremental)
    │       - Add user stories
    │       - Add acceptance criteria
    │       - Update dependencies
    │
    └─► 7. Check DoR Achievement
            ┌──────────────────────────────────┐
            │ Definition of Ready Criteria:    │
            │ ✓ All user stories defined       │
            │ ✓ Acceptance criteria specified  │
            │ ✓ Dependencies identified        │
            │ ✓ Constraints documented         │
            │ ✓ Assumptions validated (zero)   │
            │ ✓ Technical approach agreed      │
            │ ✓ Risks identified & mitigated   │
            │ ✓ Toolkit analysis complete      │
            └──────────────────────────────────┘
            
            DoR Achieved? ──No──► Continue Cycle
                │
                Yes
                ↓
        ┌───────────────────────────────┐
        │  Approval Checkpoint          │
        │  Present requirements summary │
        │  Request user approval        │
        └───────────────────────────────┘
                ↓
        User Approves? ──No──► Continue Modifications
                │
                Yes
                ↓
        [Proceed to Phase 2]
```

### **Key Elements:**

**1. CORTEX Toolkit Integration:**
- Planning Orchestrator invokes toolkit tools (not raw implementations)
- All tools follow BaseTool interface (SOLID/DRY)
- Every tool execution logged to audit infrastructure
- MCP-exposed for external agent usage

**2. Acceptance Criteria Integration:**
- For each user story, CORTEX asks for acceptance criteria
- User provides specific, testable criteria
- CORTEX validates criteria are SMART
- Criteria recorded in requirements.yaml

**3. Definition of Ready (Enhanced):**
- All user stories clearly defined ✅
- Acceptance criteria specified for ALL stories ✅
- Dependencies identified (via Dependency Mapper) ✅
- Constraints documented ✅
- Assumptions validated (zero remaining) ✅
- Technical approach agreed upon ✅
- Risks identified and mitigated ✅
- **Toolkit analysis complete** 🆕 ✅

**4. Outputs:**
- `requirements/requirements.yaml` - Comprehensive requirements with AC
- `analysis/domain-knowledge-final.json` - Knowledge graph from toolkit
- `analysis/dependencies-discovered.yaml` - Dependency mapping
- `tracking/requirements-audit.jsonl` - Complete audit trail (ALL toolkit executions)
- `tracking/requirements-conversation.jsonl` - Interactive session log

---

(Phase 2, 3, and 4 sections remain largely the same, with these additions:)

## 🔄 Realignment Orchestrator - Periodic Health Checks

**NEW:** Periodic system health check and corrective action orchestrator.

### **Purpose:**
Detect gaps between audit logs, filesystem state, AC coverage, and implementation reality. Auto-generate remediation tasks.

### **Architecture:**

```
src/orchestrators/realignment_orchestrator.py
    ├─ Phase 1: Audit Consistency Check
    ├─ Phase 2: AC Coverage vs Implementation
    ├─ Phase 3: Knowledge Graph Freshness
    ├─ Phase 4: State/Filesystem Sync
    └─ Phase 5: Remediation Task Generation
```

### **Execution Schedule:**

```yaml
# cortex-brain/config/realignment.yaml
realignment:
  enabled: true
  schedule:
    default: "phase_based"       # every_3_phases
    cortex6: "weekly"            # high velocity
    maintenance: "monthly"       # low velocity
  
  triggers:
    - event: "phase_complete"
      condition: "phase_number % 3 == 0"
    - event: "user_request"
      immediate: true
    - event: "audit_anomaly_detected"
      immediate: true
```

### **Validators:**

**1. Audit Consistency Validator:**
- Compares audit logs with filesystem state
- Detects missing/orphaned audit entries
- Verifies AC-ID traceability chain

**2. AC Coverage Validator:**
- Compares acceptance-criteria.yaml with implemented features
- Detects criteria without implementations
- Detects implementations without criteria

**3. Knowledge Graph Validator:**
- Checks knowledge graph freshness
- Detects stale entity relationships
- Triggers rebuild if >7 days old

**4. State/Filesystem Validator:**
- Compares progress-tracker.json with filesystem
- Detects completed phases not marked in state
- Detects marked-complete phases with missing files

### **Remediation:**

```python
class RealignmentOrchestrator(BaseOrchestratorV4_1):
    """Periodic system health check and corrective action."""
    
    def execute_phase_5_remediation(self):
        """Generate TODO tasks for identified gaps."""
        gaps = self.collect_all_gaps()
        
        for gap in gaps:
            task = Task(
                id=f"REALIGN-{gap.category}-{timestamp}",
                description=gap.description,
                priority="P1_HIGH",
                assigned_to="tier1/cortex6-dag.yaml"
            )
            self.todo_manager.add_task(task)
        
        # Update plan-viewer.html with new tasks
        self.refresh_dashboard()
        
        # Notify user
        return {
            "gaps_detected": len(gaps),
            "tasks_created": len(gaps),
            "dashboard_updated": True
        }
```

---

## ✅ Summary: What Makes This Workflow Effective (v3.0)

**1. Interactive Requirements Gathering with CORTEX Toolkit**
- Collaborative approach with AI-powered workspace analysis
- **8 modular tools** (SOLID/DRY/MCP-exposed)
- Zero duplicate implementations across orchestrators
- Acceptance criteria gathered upfront with SMART validation
- Definition of Ready ensures zero assumptions
- Complete audit trail with AC-ID traceability

**2. Zero-Ambiguity Plan Generation with Live Dashboard**
- Complete step-by-step instructions for autonomous execution
- Acceptance criteria mapped to specific phases
- Refactor phases ensure quality (99-phase-refactor.yaml)
- **plan-viewer.html** auto-generated with live updates
- Dark Blue Glassmorphism + Material Design 3
- file:// protocol compatible (zero dependencies)

**3. Config-Based Approval Enforcement**
- Clear approval state in config.yaml
- Master Orchestrator validates before execution
- Comprehensive approval metadata
- Audit trail for compliance

**4. Autonomous Execution with Live Dashboard Updates**
- Config-validated before execution
- Acceptance criteria validated during each phase
- Continuous execution with concise updates
- **Live dashboard** auto-refreshes every 5s
- Visual feedback indicators

**5. Complete Traceability & Audit (Enhanced)**
- **Centralized audit infrastructure** (`src/infrastructure/audit_logger.py`)
- Every toolkit execution logged with AC-ID
- Dual-format audit trails (JSONL + SQLite)
- Requirements → Plan → Execution → Completion (full lifecycle)
- Knowledge graph preserved

**6. Periodic Realignment (NEW)**
- **Realignment orchestrator** detects gaps
- Auto-generates remediation tasks
- Validates audit/AC/filesystem consistency
- Scheduled or on-demand execution

**7. Governance Integration**
- SKULL rules enforcement (TDD, holistic discovery, git isolation)
- NO MD files policy (YAML/JSON only)
- Structured data enables AI orchestration
- 61 brain protection rules + 64 governance patterns

---

## 🚀 Implementation Roadmap

### **Phase 1: CORTEX Toolkit Foundation (APPROVED)**
**Estimated:** 24-32 hours

**Tasks:**
1. Create `src/toolkit/` structure
2. Implement `BaseTool` abstract class
3. Extract existing components → toolkit
4. Implement new tools (SemanticSearch, GitAnalyzer, etc.)
5. Add audit logging to all tools
6. Unit tests (85%+ coverage)

### **Phase 2: MCP Toolkit Server (APPROVED)**
**Estimated:** 16-20 hours

**Tasks:**
1. Create `src/mcp/toolkit_server.py`
2. Expose all 8 tools as MCP functions
3. Integration tests with MCP clients
4. Documentation and examples

### **Phase 3: Orchestrator Refactoring (APPROVED)**
**Estimated:** 32-40 hours

**Tasks:**
1. Refactor PlanningOrchestratorV5 to use toolkit
2. Update other orchestrators (Investigation, Maintenance, etc.)
3. Remove duplicate implementations
4. Update all tests

### **Phase 4: Realignment Orchestrator (APPROVED)**
**Estimated:** 20-28 hours

**Tasks:**
1. Create `RealignmentOrchestrator`
2. Implement 4 validators
3. Add remediation task generator
4. Integrate with Epic Review
5. Add scheduling (weekly/phase-based)

---

## 📚 Reference Documents

**Planning Structure:**
- `INTELLIGENT-PLANNING-STRUCTURE-V6.yaml` (1,456 lines) - Technical specification
- `ARCHITECTURE-ANALYSIS-AND-RECOMMENDATIONS.md` - Approved architecture analysis

**Dashboard Specifications:**
- `plan-viewer-dashboard-requirements.yaml` (365 lines) - UI/UX requirements

**Acceptance Criteria:**
- `CX6-acceptance-criteria.yaml` (4,319 lines) - 390+ acceptance criteria
- `CX6-requirements.yaml` (338 lines) - Active remediation plan
- `CX6-completion-criteria.yaml` (550 lines) - 20 automated gates

**Governance:**
- `CX6-GOVERNANCE.yaml` (573 lines) - Machine-readable governance
- `brain-protection-rules.yaml` - 61 SKULL rules
- `cortex-operations.yaml` - 64+ governance patterns

---

**Document Version:** 3.0.0 (CORTEX Toolkit & Realignment Integrated)  
**Last Updated:** 2026-01-09  
**Author:** Asif Hussain  
**Status:** ✅ APPROVED

**Changelog:**
- v3.0 (2026-01-09): 
  - ✅ Integrated CORTEX Toolkit architecture (SOLID/DRY/MCP)
  - ✅ Added Realignment Orchestrator specification
  - ✅ Enhanced audit infrastructure details
  - ✅ Added implementation roadmap (4 phases)
  - ✅ Updated Phase 1 with modular toolkit invocation
  - ✅ Added BaseTool interface and example implementations
- v2.0 (2026-01-09): Added plan-viewer.html, toolkit section, live updates
- v1.0 (2026-01-09): Initial comprehensive workflow

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
