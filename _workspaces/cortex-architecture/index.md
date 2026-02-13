# CORTEX Architecture Documentation

**Platform:** CORTEX — **CO**gnitive **R**eal-**T**ime **EX**ecution System  
**Version:** 3.0.0 | **Updated:** 2026-02-13  
**Maintainer:** CORTEX Architecture Team

---

## Executive Summary

### CORTEX: A Living Brain for Software Development

Imagine a brain — not a human brain, but an artificial one purpose-built to think about code. Every time you ask CORTEX to implement a feature, fix a bug, or analyze your architecture, that request travels through a **cognitive pipeline** remarkably similar to how the human brain processes a thought.

Your request enters through the **sensory cortex** — the LENS engine — which perceives your codebase the way eyes perceive light: scanning git history, parsing abstract syntax trees, reading comments, and detecting patterns. This raw sensory data flows inward to the **prefrontal cortex** — the MasterOrchestrator — which acts as the executive decision-maker, routing your intent to the right specialist region of the brain. A request to "implement login" activates the **motor cortex** (TDDOrchestrator), while a request to "analyze security" fires up the **analytical cortex** (UnifiedQualityAssuranceOrchestrator).

Throughout this entire cognitive process, a **governance nervous system** of 8 enforcement agents acts like the brain's immune system — constantly scanning for violations, blocking unsafe operations, and maintaining the integrity of the codebase.

CORTEX isn't just a tool. It's a **cognitive architecture** — a thinking system that understands, decides, and acts.

### System Vital Signs (as of 2026-02-13)

| Vital Sign | Measurement | Brain Analogy |
|------------|-------------|---------------|
| **Active Orchestrators** | 17 | Neural processing regions |
| **Deprecated (sunset 2026-03-31)** | 7 | Vestigial brain structures being pruned |
| **Infrastructure Components** | 3 | Brain stem (bootstrap, registry, health) |
| **MCP Tools** | 24 consolidated (86 total operations) | Primary synaptic pathways with specialized operations |
| **LENS Analyzers** | 8 | Sensory receptor types |
| **Enforcement Agents** | 8 | Immune system defenders |
| **CORE Governance Rules** | 50+ | DNA-level behavioral encoding |
| **Consolidation (Wave 7)** | 37% reduction | Neural pruning for efficiency |

### The Wave 7 Consolidation: Neural Pruning

Just as a maturing brain prunes unnecessary synaptic connections to become faster and more efficient, CORTEX underwent **Wave 7 Track 4 consolidation** — reducing from 27 orchestrators to 17. Four new **unified orchestrators** emerged, each absorbing the capabilities of 2-5 predecessors:

| Unified Orchestrator | Absorbed | Brain Analogy |
|---------------------|----------|---------------|
| **UnifiedOnboardingOrchestrator** | 3 predecessors | Consolidated memory formation center |
| **UnifiedAnalysisOrchestrator** | 2 predecessors | Unified perception processing |
| **UnifiedQualityAssuranceOrchestrator** | 5 predecessors | Merged quality judgment center |
| **UnifiedDiscoveryOrchestrator** | 2 predecessors | Combined exploration & learning center |

Seven deprecated orchestrators remain active until their **sunset date (2026-03-31)**, after which they'll be fully removed — like vestigial structures the brain no longer needs.

### What Makes CORTEX Different

**Traditional AI Coding Tools** are like reflexes — fast, automatic, but shallow:
- Code completion only (stimulus → response)
- Limited context awareness (no memory)
- No governance enforcement (no judgment)
- Single-file focus (tunnel vision)

**CORTEX is a full cognitive system** — it perceives, reasons, decides, and learns:
- 🧠 **Multi-orchestrator intelligence** — 17 specialized brain regions collaborating on every request
- 👁️ **Deep LENS perception** — 8 analyzers see your code the way a radiologist reads an MRI
- 🛡️ **Governance immune system** — 8 enforcement agents ensure every output is safe, tested, and compliant
- 🔄 **TDD motor cortex** — RED→GREEN→REFACTOR is the mandatory muscle memory for all code changes
- 📊 **Holistic validation gates** — No operation proceeds without full cognitive review
- 🌐 **MCP nervous system** — Pylance-style architecture connecting the brain to any IDE

---

## Architecture Overview

### The Brain's Anatomy

CORTEX's architecture mirrors the layered structure of a biological brain. Information flows from the outside world through sensory interfaces, into processing centers, and back out as validated action — just as a thought moves from perception through reasoning to motor output.

```
┌──────────────────────────────────────────────────────────────────────┐
│                    🧠 CORTEX: THE AI BRAIN                         │
│               Cognitive Real-Time Execution System                  │
│                                                                     │
│  "A brain that reads code instead of sensory input, reasons about  │
│   architecture instead of language, and produces tested             │
│   implementations instead of motor commands."                       │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
  ╔════════════════════════════╧════════════════════════════════════╗
  ║          💬 SENSORY INTERFACE (The Brain's Senses)              ║
  ║            MCP Protocol — JSON-RPC 2.0 / stdio                  ║
  ║                                                                 ║
  ║   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          ║
  ║   │ VS Code │  │ Claude  │  │ Cursor  │  │ Custom  │          ║
  ║   │ Copilot │  │ Desktop │  │  IDE    │  │ Client  │          ║
  ║   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘          ║
  ║        └────────────┴─────┬──────┴────────────┘                ║
  ║                  24 Consolidated MCP Tools │                   ║
  ║              (86 total operations across tools)                ║
  ╚════════════════════════════╤════════════════════════════════════╝
                               │
  ╔════════════════════════════╧════════════════════════════════════╗
  ║       🧠 PREFRONTAL CORTEX (Executive Decision-Making)         ║
  ║                  17 Active Neural Regions                       ║
  ║                                                                 ║
  ║   ┌─────────────────────────────────────────────────────────┐  ║
  ║   │          🎯 MasterOrchestrator (Priority 10)             │  ║
  ║   │     The CEO of the brain — routes every thought          │  ║
  ║   └──────────────────────┬──────────────────────────────────┘  ║
  ║                          ▼                                      ║
  ║   ┌─────────────────────────────────────────────────────────┐  ║
  ║   │          🧭 IntentRouter (Priority 20)                   │  ║
  ║   │  Thalamus — classifies & routes to specialist regions    │  ║
  ║   └────┬──────────┬──────────────┬──────────────┬───────────┘  ║
  ║        ▼          ▼              ▼              ▼              ║
  ║   ┌────────┐ ┌─────────┐  ┌──────────┐  ┌───────────┐         ║
  ║   │🧠 Core │ │🎨 Domain│  │🔧 Unified│  │⚙️ Infra   │         ║
  ║   │  (5)   │ │   (5)   │  │ Support  │  │   (3)     │         ║
  ║   │        │ │         │  │   (4)    │  │           │         ║
  ║   │ TDD    │ │Refactor │  │Onboard   │  │Bootstrap  │         ║
  ║   │Workflow│ │Planning │  │Analysis  │  │Registry   │         ║
  ║   │Interact│ │Domain   │  │Quality   │  │Health     │         ║
  ║   │        │ │Converse │  │Discovery │  │           │         ║
  ║   │        │ │Selenium │  │          │  │           │         ║
  ║   └────────┘ └─────────┘  └──────────┘  └───────────┘         ║
  ╚════════════════════════════╤════════════════════════════════════╝
                               │
      ┌────────────────────────┼────────────────────────┐
      ▼                        ▼                        ▼
 ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
 │ 👁️ VISUAL CORTEX │ │ 🧬 LIMBIC SYSTEM │ │ 💾 HIPPOCAMPUS   │
 │  (LENS Engine)   │ │ (Learning Loop)  │ │ (Memory/Storage) │
 │                  │ │                  │ │                  │
 │ 8 Analyzers that │ │ Adapts behavior  │ │ Stores long-term │
 │ perceive your    │ │ like emotional   │ │ memories the way │
 │ codebase the way │ │ conditioning —   │ │ the hippocampus  │
 │ eyes perceive    │ │ learning from    │ │ consolidates     │
 │ light            │ │ every test run   │ │ experiences      │
 │                  │ │                  │ │                  │
 │ • Git History    │ │ • Test Quality   │ │ • 4-Tier YAML    │
 │ • AST Analysis   │ │ • Code Patterns  │ │ • Business Logic │
 │ • Comments       │ │ • Validation     │ │ • Best Practices │
 │ • Patterns       │ │ • Adaptive       │ │ • CORE Rules     │
 │ • Config         │ │   Refinement     │ │ • Domain Models  │
 │ • Database       │ │                  │ │                  │
 │ • API            │ │                  │ │                  │
 │ • Security       │ │                  │ │                  │
 └──────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## Documentation Structure

### 📖 Core Documentation (The Brain's Major Systems)

| Section | Description | Brain Analogy |
|---------|-------------|---------------|
| [MCP Overview](./mcp/overview.md) | Model Context Protocol — the nervous system | Peripheral nerves connecting brain to body |
| [MCP Tools Catalog](./mcp/tools-catalog.md) | Complete 24-tool catalog (86+ operations) | Map of every neural connection |
| [Orchestration Overview](./orchestration/overview.md) | 17-orchestrator cognitive system | Brain region atlas |
| [LENS Intelligence](./lens/overview.md) | Code analysis & synthesis engine | Visual cortex documentation |

### 🧠 Orchestrator Deep Dives (Neural Region Studies)

| Section | Count | Brain Analogy |
|---------|-------|---------------|
| [Core Orchestrators](./orchestration/master-orchestrator.md) | 5 | Brain stem & cortex — essential for consciousness |
| [Domain Orchestrators](./orchestration/domain-orchestrators.md) | 5 | Specialized lobes — expert processing centers |
| [Unified Support](./orchestration/support-orchestrators.md) | 4 (+7 deprecated) | Consolidated association areas — efficiency through integration |
| [Infrastructure](./orchestration/overview.md) | 3 | Autonomic systems — keeps the brain alive |

### 🔧 Technical References (Brain Imaging)

| Section | Description | Brain Analogy |
|---------|-------------|---------------|
| [Architecture Diagrams](./diagrams/architecture-overview.md) | Visual system representations | Brain MRI scans |
| [Data Flow](./diagrams/data-flow.md) | Request → Response lifecycle | Neural signal trace |
| [Component Relationships](./diagrams/component-relationships.md) | Orchestrator dependency graph | Connectome mapping |

---

## Quick Start for Developers

### Understanding CORTEX as a Developer

**CORTEX operates on three cognitive layers — like a brain that perceives, thinks, then acts:**

1. **👁️ Sensory Layer (LENS)** — *The Visual Cortex* — Observes and perceives code
   - Git history analysis (24-hour memory window)
   - AST parsing and structural pattern recognition
   - Security vulnerability detection (threat perception)
   - Complexity metrics (cognitive load assessment)

2. **🧠 Processing Layer (17 Orchestrators)** — *The Cerebral Cortex* — Reasons and decides
   - **MasterOrchestrator** — prefrontal cortex, coordinates all thought
   - **IntentRouter** — thalamus, classifies signals → routes to specialist regions
   - **TDDOrchestrator** — motor cortex, enforces disciplined test-first execution
   - **UnifiedQualityAssuranceOrchestrator** — anterior cingulate, validates quality & governance

3. **🌐 Action Layer (24 MCP Tools with 86 Operations)** — *The Motor Cortex* — Executes validated operations
   - `cortex_process_request` — primary motor output (5 operations: implement, fix, refactor, analyze, test)
   - `cortex_lens` — deep perception query (5 operations: analyze, deep_analyze, diff, summarize, validate)
   - `cortex_challenge` — generates alternative cognitive approaches
   - `cortex_debug` — comprehensive debugging cycle (7 operations: inject, capture, analyze, fix-plan, full_cycle, cleanup, status)

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

**Last Updated:** 2026-02-13  
**Data Sources:** `__wiring_contract__.yaml` v2.0.0, cortex-registry, MCP Server  
**Architecture Version:** Wave 7 Track 4 Complete (17 active orchestrators)
