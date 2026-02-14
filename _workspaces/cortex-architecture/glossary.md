# CORTEX Glossary

**A comprehensive reference for CORTEX-specific terminology**

**Terms:** 50+ | **Updated:** 2026-02-14 | **Audience:** Technical and non-technical users

---

## Quick Navigation

[A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [J](#j) · [K](#k) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [Q](#q) · [R](#r) · [S](#s) · [T](#t) · [U](#u) · [V](#v) · [W](#w)

---

## A

### AC Markers
**Definition:** Audit Compliance markers that track the start and completion of governance-gated work.

**Format:** `AC_START: AC-{PHASE}-{ID}` and `AC_COMPLETE: AC-{PHASE}-{ID}`

**Example:**
```python
# AC_START: AC-PHASE48.0-001
# Description: Implement holistic validation gate
class HolisticValidationGate:
    ...
# AC_COMPLETE: AC-PHASE48.0-001 ✅ 15/15 passing
```

**Related:** [Audit Trail](#audit-trail), [Governance](#governance)

---

### Architect Mode
**Definition:** A CORTEX operational mode for system design and internal development. Uses `cortex-architect.prompt.md` and targets CORTEX repository enhancement.

**When Used:** When developing CORTEX itself (detected by presence of `.cortex/` or `cortex-registry/` directories).

**Related:** [Production Mode](#production-mode), [HEXA-MODE](#hexa-mode)

---

### AST Analysis
**Definition:** Abstract Syntax Tree analysis — parsing source code into a tree structure to understand code structure, complexity, and patterns without executing it.

**CORTEX Tool:** `cortex_ast_analyze`

**Related:** [LENS](#lens), [Static Analysis](#static-analysis)

---

### Audit Trail
**Definition:** A complete record of all governance-gated operations, tracked via AC markers and logged for compliance verification.

**Rule:** CORE-027

**Related:** [AC Markers](#ac-markers), [Governance](#governance)

---

## B

### Brain (CORTEX Brain)
**Definition:** The knowledge storage layer of CORTEX, organized in tiers from most permanent (tier0) to most volatile (tier3).

**Structure:**
- `tier0/` — Immutable principles, CORE rules
- `tier1/` — Stable knowledge, best practices
- `tier2/` — Session context, recent learnings
- `tier3/` — Volatile state, temporary caches

**Location:** `cortex_brain/`

**Related:** [Knowledge Tiers](#knowledge-tiers), [Domain Brain](#domain-brain)

---

### Brain Analogy
**Definition:** CORTEX documentation uses human brain analogies to explain technical concepts. Orchestrators are like brain regions, MCP is the nervous system, LENS is the visual cortex, etc.

**Purpose:** Makes complex architecture accessible to non-technical users.

---

## C

### CCL (Context Crystallization Layer)
**Definition:** Phase 49 enhancement that pre-warms context asynchronously before request processing, reducing Stage 2 latency by ~15%.

**Process:**
1. Async load rules cache (company > tier1 > tier0)
2. Warm LENS (AST, git, comments)
3. Detect infrastructure
4. Merge into request processing

**SLA:** 300ms target, 500ms fallback max

**Related:** [Phase 49](#phases), [LENS](#lens)

---

### Challenge Gate
**Definition:** A mandatory design review checkpoint where CORTEX presents counter-proposals and alternative approaches before implementation.

**Part of:** CORE-048 (Holistic Validation Gate)

**Output:** Agreement/disagreement, confidence score, counter-proposal if applicable.

**Related:** [DoR](#dor), [Holistic Validation](#holistic-validation)

---

### CORE Rules
**Definition:** The 30+ immutable governance rules that enforce quality, security, and consistency across CORTEX operations.

**Format:** CORE-{NNN}

**Key Rules:**
- CORE-002: No markdown file generation (inline only)
- CORE-008: TDD mandatory (tests before code)
- CORE-011: Type hints mandatory
- CORE-035: Single canonical implementation (no duplicates)

**Location:** `cortex-registry/_cortex-master/governance/core-rules.yaml`

**Related:** [Governance](#governance), [Tier 0 Rules](#tier-0-rules)

---

### Consolidated Tools
**Definition:** The Wave 100 reorganization that grouped 86 flat MCP tools into 24 parent tools with multiple operations each.

**Example:** Instead of `cortex_lens_analyze`, `cortex_lens_diff`, `cortex_lens_validate` (3 tools), there's `cortex_lens` (1 tool with 3 operations).

**Benefits:** Cognitive clarity, easier discovery, consistent patterns.

**Related:** [MCP](#mcp), [Wave 100](#wave-100)

---

## D

### DoR (Definition of Ready)
**Definition:** The classification table shown before any implementation, confirming intent, handler, confidence, scope, and impact.

**Format:**
| Field | Value |
|-------|-------|
| Intent | IMPLEMENT |
| Handler | TDDOrchestrator |
| Confidence | 🟢 95% |
| Scope | cortex/mcp/ |
| Impact | 🟡 Medium |

**Rule:** CORE-029

**Related:** [Intent Router](#intent-router), [Challenge Gate](#challenge-gate)

---

### Domain Brain
**Definition:** Company-specific knowledge loaded from `company/domains/` that takes precedence over CORTEX's built-in best practices.

**Priority:** Company knowledge > CORTEX knowledge

**Related:** [Brain](#brain-cortex-brain), [Knowledge Layering](#knowledge-layering)

---

## E

### Enforcement Orchestrator
**Definition:** The 7-agent pre-execution gate that validates all IMPLEMENT/FIX/REFACTOR requests against governance rules.

**Agents:**
1. GovernanceEnforcementAgent (CORE-008, 011, 012, 013, 029, 030)
2. SecurityCheckpointAgent (CORE-025, 026, 027)
3. ComplianceValidationAgent (Tier 1 rules)
4. FileNamingEnforcementAgent (CORE-028)
5. IncrementalExecutionAgent (CORE-001, 004)
6. MarkdownSuppressionAgent (CORE-002)
7. ArchitectureIntegrityAgent (CORE-017-020, 032, 034, 035, 038-041)

**Coverage:** 87% of CORE rules automated

**Related:** [Governance](#governance), [Pre-Execution Gate](#pre-execution-gate)

---

## G

### Governance
**Definition:** The 4-layer defense system that ensures quality, security, and compliance across all CORTEX operations.

**Layers:**
1. Pre-Execution Gate (blocks violations)
2. Runtime Monitor (stops at 3+ violations)
3. Post-Execution Audit (detects bypasses)
4. Production Gate (prevents broken deployment)

**Related:** [CORE Rules](#core-rules), [Enforcement Orchestrator](#enforcement-orchestrator)

---

## H

### HEXA-MODE
**Definition:** The 6 operational modes of CORTEX Architect: PRE-FLIGHT, AUDIT, META-AUDIT, DIGEST, PLAN, and DESIGN.

**Trigger:** Auto-detected based on request keywords and file types.

**Related:** [Architect Mode](#architect-mode), [DIGEST](#digest)

---

### Holistic Validation
**Definition:** Phase 48 enhancement that runs comprehensive pre-implementation checks including registry validation, dependency analysis, risk scoring, and mandatory Challenge Gate.

**Rule:** CORE-048

**Related:** [Challenge Gate](#challenge-gate), [Pre-Execution Gate](#pre-execution-gate)

---

## I

### Incremental Execution
**Definition:** The requirement that all tasks stay ≤500 lines of code per commit with automatic subtask decomposition.

**Rule:** CORE-001

**Process:** Large tasks → IncrementalTaskDecomposer → Subtasks (10K tokens each) → Sequential execution

**Related:** [Token Budget](#token-budget), [TDD](#tdd)

---

### Intent Router
**Definition:** The orchestrator that classifies user requests into intents (IMPLEMENT, FIX, REFACTOR, ANALYZE, etc.) and routes to appropriate handlers.

**Output:** Intent type, target orchestrator, confidence score.

**Related:** [DoR](#dor), [Master Orchestrator](#master-orchestrator)

---

## K

### Knowledge Layering
**Definition:** The priority system for loading knowledge: Company standards (highest) → CORTEX best practices → Language defaults.

**Priority:** `company/domains/` > `cortex/knowledge/best-practices/`

**Related:** [Domain Brain](#domain-brain), [Brain](#brain-cortex-brain)

---

### Knowledge Tiers
**Definition:** The 4-tier organization of CORTEX Brain knowledge by volatility.

| Tier | Content | Volatility |
|------|---------|------------|
| tier0 | CORE rules, principles | Immutable |
| tier1 | Best practices, patterns | Stable |
| tier2 | Session context | Session-scoped |
| tier3 | Caches, temporary state | Volatile |

**Related:** [Brain](#brain-cortex-brain)

---

## L

### LENS
**Definition:** **L**anguage **E**xamination **N**avigation **S**ynthesis — CORTEX's unified code intelligence protocol.

**Process:**
1. **L**anguage: Detect language and framework
2. **E**xamination: AST parsing, complexity analysis
3. **N**avigation: Cross-file relationships, call graphs
4. **S**ynthesis: Merge findings into actionable insights

**Tools:** `cortex_lens_analyze`, `cortex_lens_deep_analyze`

**Related:** [AST Analysis](#ast-analysis), [Static Analysis](#static-analysis)

---

## M

### Master Orchestrator
**Definition:** The primary entry point orchestrator that receives all requests and coordinates with specialized orchestrators.

**Role:** Like the prefrontal cortex — executive function, decision-making, coordination.

**Related:** [Orchestrator](#orchestrator), [Intent Router](#intent-router)

---

### MCP (Model Context Protocol)
**Definition:** The standardized communication layer (JSON-RPC 2.0) that connects AI assistants (Copilot, Claude, Cursor) to CORTEX orchestrators.

**Analogy:** CORTEX's nervous system.

**Tools:** 24 consolidated tools with 86+ operations.

**Related:** [Consolidated Tools](#consolidated-tools), [Pylance-Style MCP](#pylance-style-mcp)

---

### MCP-FIRST
**Definition:** The architectural principle that ALL CORTEX functionality must be exposed via MCP tools. Direct Python imports are forbidden in production.

**Why:** Ensures consistent governance, audit trails, and client compatibility.

**Related:** [MCP](#mcp-model-context-protocol)

---

## O

### Orchestrator
**Definition:** A specialized component that handles a specific domain of CORTEX functionality.

**Count:** 17 active + 7 deprecated (as of 2026-02-14)

**Examples:**
- `TDDOrchestrator` — Test-driven development workflow
- `LENSSynthesis` — Code intelligence analysis
- `EnforcementOrchestrator` — Governance validation

**Related:** [Master Orchestrator](#master-orchestrator), [Unified Orchestrators](#unified-orchestrators)

---

## P

### Phases
**Definition:** Numbered development milestones in CORTEX evolution (e.g., Phase 48, Phase 49, Phase 53).

**Format:** Phase {NN}

**Examples:**
- Phase 48: Holistic Validation Gate
- Phase 49: Context Crystallization Layer
- Phase 53: Pylance-Style MCP Architecture

**Related:** [Waves](#waves)

---

### Pre-Execution Gate
**Definition:** The first layer of governance that validates requests before any code is generated or modified.

**Enforcement:** BLOCKS violations (no partial execution)

**Related:** [Enforcement Orchestrator](#enforcement-orchestrator), [Governance](#governance)

---

### Production Mode
**Definition:** The standard operational mode for user repositories. Uses `CORTEX.prompt.md` and targets user domain implementation.

**When Used:** When working on non-CORTEX repositories.

**Related:** [Architect Mode](#architect-mode)

---

### Pylance-Style MCP
**Definition:** Phase 53 architecture where MCP server auto-starts when tools are invoked (no manual server startup required), similar to how Pylance language server works in VS Code.

**Benefits:** Zero setup friction, on-demand lifecycle, automatic error recovery.

**Related:** [MCP](#mcp-model-context-protocol)

---

## R

### Response Header
**Definition:** The mandatory header that begins every CORTEX response.

**Format:**
```markdown
## 🧠 CORTEX {operation}
**Author:** Asif Hussain | **Orchestrator:** {orchestrator} ✅

---
```

**Rule:** CORE-029

**Related:** [DoR](#dor)

---

## S

### Silent Autonomous Execution
**Definition:** The default execution mode where CORTEX proceeds without narration, showing only progress bars and completion reports.

**Trigger Words:** "proceed", "implement", "continue", "yes"

**Rule:** CORE-049

**Format:** ASCII progress bars only (no text descriptions)

**Related:** [Progress Bars](#progress-bars)

---

### Static Analysis
**Definition:** Code analysis without execution — examining source code for patterns, complexity, potential bugs, and style issues.

**Related:** [AST Analysis](#ast-analysis), [LENS](#lens)

---

### Sunset Date
**Definition:** The deadline after which deprecated components will be removed.

**Current:** 2026-03-31 (for Wave 7 deprecated orchestrators)

**Related:** [Deprecated Orchestrators](#deprecated-orchestrators), [Unified Orchestrators](#unified-orchestrators)

---

## T

### TDD (Test-Driven Development)
**Definition:** The mandatory development workflow: write tests first (RED), implement to pass (GREEN), then refactor.

**Rule:** CORE-008

**Process:** RED → GREEN → REFACTOR

**Related:** [TDD Orchestrator](#tdd-orchestrator)

---

### TDD Orchestrator
**Definition:** The orchestrator that enforces test-first development workflow for all IMPLEMENT/FIX intents.

**Related:** [TDD](#tdd-test-driven-development)

---

### Tier 0 Rules
**Definition:** The immutable subset of CORE rules that cannot be overridden under any circumstances.

**Examples:** CORE-002 (no markdown), CORE-008 (TDD), CORE-035 (no duplicates)

**Related:** [CORE Rules](#core-rules)

---

### Token Budget
**Definition:** The constraint on context size (≤200K tokens) and per-turn context (≤20K) to prevent runaway costs and context overflow.

**Related:** [Incremental Execution](#incremental-execution)

---

## U

### Unified Orchestrators
**Definition:** The 4 consolidated orchestrators created in Wave 7 Track 4 that replace multiple deprecated orchestrators.

**List:**
1. `UnifiedOnboardingOrchestrator`
2. `UnifiedAnalysisOrchestrator`
3. `UnifiedQualityAssuranceOrchestrator`
4. `UnifiedDiscoveryOrchestrator`

**Impact:** 37% reduction (27 → 17 active orchestrators)

**Related:** [Orchestrator](#orchestrator), [Wave 7](#wave-7)

---

## W

### Wave 7
**Definition:** The orchestrator consolidation initiative that reduced CORTEX from 27 to 17 active orchestrators.

**Tracks:** 4 tracks completed 2026-02-13

**Related:** [Unified Orchestrators](#unified-orchestrators)

---

### Wave 100
**Definition:** The MCP tool consolidation that reorganized 86 flat tools into 24 parent tools with operations.

**Impact:** 72% reduction in top-level tools, 0% reduction in functionality.

**Related:** [Consolidated Tools](#consolidated-tools), [MCP](#mcp-model-context-protocol)

---

### Waves
**Definition:** Major CORTEX initiatives that span multiple phases.

**Examples:**
- Wave 7: Orchestrator consolidation
- Wave 100: MCP tool consolidation

**Related:** [Phases](#phases)

---

## See Also

- [CORTEX Architecture Index](./index.md)
- [MCP Tools Catalog](./mcp/tools-catalog.md)
- [Governance Compliance](./capabilities/governance-compliance.md)
- [Orchestration Overview](./orchestration/overview.md)

---

**Last Updated:** 2026-02-14
