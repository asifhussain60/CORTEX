# CORTEX Architecture Documentation

**Platform:** CORTEX — **CO**gnitive **R**eal-**T**ime **EX**ecution System  
**Version:** 2.0.0 | **Updated:** 2026-02-11  
**Maintainer:** CORTEX Architecture Team

---

## 🚨 NEW: Production Architecture Review

### [📋 System Manifest](CORTEX_SYSTEM_MANIFEST.md)
**Comprehensive orchestrator & MCP tool inventory with production-readiness assessment**

- ✅ **35 Orchestrators** cataloged across 3 tiers (8 core, 9 domain, 18 support)
- ✅ **73 MCP Tools** mapped with implementation status
- ✅ **Cross-Reference Analysis** - Wiring validation, usage patterns, redundancy detection
- ⚠️ **Production Risks** - 15 P0/P1 findings with prioritized remediation plans
- 📊 **Health Metrics** - Test coverage, utilization rates, dependency validation

**Key Findings:**
- 🔴 **8 P0 Critical Issues** requiring immediate fix (auth, command injection, race conditions)
- 🟡 **7 P1 High Priority** items for next sprint (RBAC, session persistence, monitoring)
- 🟢 **60 of 73 tools** production-ready with >80% test coverage
- ⚪ **3 orchestrators** candidates for deprecation (SeleniumPlaywright, Workflow, Migration)

[**→ Read Full Production Assessment**](CORTEX_SYSTEM_MANIFEST.md)

---

## Executive Summary

**CORTEX: The AI Brain for Software Development**

CORTEX serves as an **AI-powered cognitive system** that orchestrates software development through **60 specialized neural orchestrators**. Operating through the **Model Context Protocol (MCP)**, CORTEX exposes **86 intelligent tools** that enable AI assistants like GitHub Copilot, Claude, and Cursor to leverage sophisticated development workflows.

### Key Metrics (as of 2026-02-11)

| Metric | Count | Description |
|--------|-------|-------------|
| **Core Orchestrators** | 11 | Fundamental processing engines |
| **Domain Orchestrators** | 8 | Business logic specialists |
| **Support Orchestrators** | 41 | Infrastructure & utility |
| **MCP Tools** | 86 | Exposed capabilities via MCP |
| **Total Orchestrators** | 60 | Complete system coverage |

### What Makes CORTEX Different

**Traditional AI Coding Tools:**
- Code completion only
- Limited context awareness
- No governance enforcement
- Single-file focus

**CORTEX Cognitive System:**
- 🧠 Multi-orchestrator intelligence
- 🔍 Deep LENS code analysis (security, complexity, architecture)
- 🛡️ Built-in governance & compliance (CORE rules, audit trails)
- 🔄 TDD-first workflows (RED→GREEN→REFACTOR)
- 📊 Holistic validation gates
- 🌐 MCP-first architecture (scalable, extensible)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🧠 CORTEX AI BRAIN ARCHITECTURE                       │
│                    (Cognitive Real-Time Execution System)                    │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼────────────────────────────────────────────────┐
│                    💬 MCP INTERFACE LAYER                                    │
│                  (JSON-RPC 2.0 - Port 8000/stdio)                            │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│    │  VSCode  │    │  Claude  │    │  Cursor  │    │  Custom  │           │
│    │ Copilot  │    │   AI     │    │   IDE    │    │  Tools   │           │
│    └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘           │
│         └───────────────┴───────┬───────┴───────────────┘                   │
│                    86 MCP Tools Available │
└─────────────────────────────────┼────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────┼────────────────────────────────────────────┐
│                    🧠 COGNITIVE PROCESSING CENTER                            │
│                    (60 Neural Orchestrators) │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                   🎯 MasterOrchestrator                                │   │
│  │                  (Executive Control Center)                            │   │
│  └───────────────────────────┬──────────────────────────────────────────┘   │
│                              ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     🧭 IntentRouter                                    │   │
│  │                 (Decision-Making Cortex)                              │   │
│  └───┬─────────────────┬────────────────────┬────────────────────┬──────┘   │
│      │                 │                    │                    │           │
│      ▼                 ▼                    ▼                    ▼           │
│  ┌────────┐       ┌────────┐          ┌────────┐          ┌────────┐        │
│  │🧠 Core │       │🎨 Domain │        │🔧 Support│        │⚙️ Infra │       │
│  │  (11)   │       │   (8)  │        │   (41)  │        │  (3)   │        │
│  └────────┘       └────────┘          └────────┘          └────────┘        │
└──────────────────────────────────────────────────────────────────────────────┘
              │                           │                           │
              ▼                           ▼                           ▼
┌─────────────────────────┐  ┌──────────────────────┐  ┌─────────────────────┐
│  👁️ LENS SENSORY       │  │  🧠 LEARNING CORTEX  │  │  💾 MEMORY CENTER    │
│ (Visual Cortex for Code)│  │  (Adaptive Learning) │  │  (Knowledge Storage) │
│  • Git History Vision   │  │  • Pattern Learning  │  │  • Knowledge Repos   │
│  • Code Analysis        │  │  • Test Quality Metrics│  │  • Business Logic   │
│  • Comment Reading      │  │  • Validation Loops  │  │  • Governance Rules │
│  • Pattern Detection    │  │  • Adaptive Refinement│  │  • Best Practices   │
└─────────────────────────┘  └──────────────────────┘  └─────────────────────┘
```

---

## Documentation Structure

### 📖 Core Documentation

| Section | Description | Status |
|---------|-------------|--------|
| [MCP Overview](./mcp/overview.md) | Model Context Protocol integration | ✅ Updated |
| [MCP Tools Catalog](./mcp/tools-catalog.md) | Complete 86-tool reference | ✅ Updated |
| [Orchestration Overview](./orchestration/overview.md) | 60-orchestrator system | ✅ Updated |
| [LENS Intelligence](./lens/overview.md) | Code analysis & synthesis | ✅ Updated |

### 🧠 Orchestrator Deep Dives

| Section | Count | Description |
|---------|-------|-------------|
| [Core Orchestrators](./orchestration/master-orchestrator.md) | 11 | MasterOrchestrator, IntentRouter, TDD, LENS |
| [Domain Orchestrators](./orchestration/domain-orchestrators.md) | 8 | Refactoring, Planning, Documentation |
| [Support Orchestrators](./orchestration/support-orchestrators.md) | 41 | Debugging, Knowledge, Dashboards |

### 🔧 Technical References

| Section | Description |
|---------|-------------|
| [Architecture Diagrams](./diagrams/architecture-overview.md) | Visual system representations |
| [Data Flow](./diagrams/data-flow.md) | Request → Response lifecycle |
| [Component Relationships](./diagrams/component-relationships.md) | Orchestrator dependencies |

---

## Quick Start for Developers

### Understanding CORTEX as a Developer

**CORTEX operates on three cognitive layers:**

1. **Sensory Layer (LENS)** - Observes and analyzes code
   - Git history analysis (24-hour context window)
   - AST parsing and pattern detection
   - Security vulnerability scanning
   - Complexity metrics

2. **Processing Layer (Orchestrators)** - Makes intelligent decisions
   - **MasterOrchestrator** coordinates all operations
   - **IntentRouter** classifies requests → routes to specialists
   - **TDDOrchestrator** enforces test-first development
   - **EnforcementOrchestrator** validates governance rules

3. **Action Layer (MCP Tools)** - Executes validated operations
   - `cortex_process_request` - Primary entry point
   - `cortex_lens_analyze` - Deep code intelligence
   - `cortex_challenge` - Generates alternative approaches
   - `cortex_validate_holistically` - Pre-implementation validation

### Example: How CORTEX Processes "Implement Login Feature"

```
User: "Implement login feature"
  ↓
[MCP] cortex_process_request(request="Implement login feature")
  ↓
[MasterOrchestrator] Receives request → delegates to IntentRouter
  ↓
[IntentRouter] Classifies: IMPLEMENT intent → TDDOrchestrator
  ↓
[TDDOrchestrator] Loads:
  • Phase 48: HolisticValidationOrchestrator (pre-flight check)
  • Phase 49: ContextCrystallizationLayer (warm context cache)
  • LENS: Security & complexity analysis
  ↓
[Challenge Gate] Generates 3 alternative approaches
  • Option A: OAuth 2.0 with JWT
  • Option B: Session-based with Redis
  • Option C: Passwordless (magic links)
  ↓
User selects → "proceed"
  ↓
[TDD Cycle] RED → GREEN → REFACTOR
  1. Generate failing tests
  2. Implement minimal code to pass
  3. Refactor with best practices
  ↓
[EnforcementOrchestrator] Validates:
  • CORE-008: Tests before code ✅
  • CORE-011: Type hints present ✅
  • CORE-012: Docstrings complete ✅
  • Security: No hardcoded secrets ✅
  ↓
[Audit Trail] AC_START → AC_COMPLETE markers
  ↓
✅ Feature implemented with governance compliance
```

---

## System Requirements

**Production Environment:**
- Python 3.9+
- Git 2.30+
- MCP Server (stdio or HTTP transport)
- VS Code / Claude Desktop / Cursor (MCP client)

**Development Environment:**
- All production requirements
- pytest for testing
- Node.js 18+ (for dashboard generation)

---

## Navigation

### By Role

**👨‍💼 For Executives:**
- Start: [Executive Summary](#executive-summary)
- Business Value: [Capabilities Overview](./capabilities/overview.md)

**👨‍💻 For Developers:**
- Start: [Quick Start](#quick-start-for-developers)
- Deep Dive: [Orchestration Overview](./orchestration/overview.md)

**🏗️ For Architects:**
- Start: [Architecture Overview](#architecture-overview)
- Technical: [MCP Protocol](./mcp/protocol.md)

**🔒 For Security Teams:**
- Start: [LENS Governance](./lens/governance.md)
- Compliance: [Governance & Compliance](./capabilities/governance-compliance.md)

---

**Last Updated:** 2026-02-11 06:34:11  
**Data Sources:** cortex-registry, wiring.yaml, MCP Server  
**Accuracy:** Live system introspection (100% current)
