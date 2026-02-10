# CORTEX Agent Index
**Version:** 1.3 | **Updated:** 2026-02-10 | **Purpose:** Lazy loading + silent autonomous execution + architecture integrity | **Agents:** 13 | **Default Mode:** Silent + Visual Progress | **Phase 70:** ✅

---

## 🤖 SILENT AUTONOMOUS EXECUTION (DEFAULT)

**All agents inherit this behavior when user says "proceed" or "implement":**

```yaml
silent_mode: true
visual_feedback: "ascii_progress_bars"
narration: disabled
approval_gates: disabled
completion_report: minimal
```

### Progress Bar Format (UNIVERSAL)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 {phase_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[████████░░] 80% {current_stage}
├─ ✅ S1: {stage_1_name} ({tests} tests)
├─ ✅ S2: {stage_2_name} ({tests} tests)  
├─ 🔵 S3: {stage_3_name} (in progress)
└─ ⚪ S4: {stage_4_name} (pending)

Tests: {passed}/{total} | Coverage: {pct}% | {duration}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Status Icons
| Icon | Meaning |
|------|---------|
| ✅ | Complete |
| 🔵 | In Progress |
| ⚪ | Pending |
| 🔴 | Failed/Blocked |

---

## 🏗️ Governance Architecture (Hybrid Pattern)

**Authority:** CORTEX-CORE-035 (Single Canonical Implementation) + ENH-048 (Prompt Unbloating)  
**Strategy:** YAML for structural rules (rarely change) + Agents for behavioral rules (actively evolving)

### Tier 1: YAML Structural Rules (SSOT - Read-Only)

**Location:** `cortex-registry/_cortex-master/index.yaml` (governance section)

| Rule Category | Owner | Change Frequency | Examples |
|---------------|-------|------------------|----------|
| Trigger Words | YAML | Yearly | "proceed", "implement", "continue" |
| Progress Bar Format | YAML | Never | `[██░░]`, width=10, chars |
| Status Icons | YAML | Never | ✅, 🔵, ⚪, 🔴 |
| Token Budgets | YAML | Quarterly | Per-session limit, warning threshold |
| File Naming | YAML | Never | kebab-case, max 35 chars |
| Risk Thresholds | YAML | Quarterly | Block > 0.7, warn > 0.4 |

### Tier 2: Agent Behavioral Rules (Active Development)

**Location:** Agent specification files in `.github/agents/core/`

| Rule Category | Agent Owner | Change Frequency | Examples |
|---------------|-----------  |------------------|----------|
| Challenge Gate Logic | cortex-holistic-validator.md | Monthly | Alternatives generation, ROI analysis |
| Two-Phase Approval | cortex-architect.md | Monthly | When to ask, when to execute silently |
| Behavioral Patterns | AGENT-INDEX.md | Bi-weekly | What to do on test fail, token budget hit |
| Validation Sequences | cortex-holistic-validator.md | Monthly | Registry checks, dependency analysis |
| Response Formats | response-format-standards.md | Bi-weekly | Visual templates, icon usage |
| Mode Detection | cortex-architect.md | Quarterly | Intent classification, agent routing |

### Tier 3: Cross-References (Consistency)

**Enforcement:** Every 6 months, run Governance Coherence Audit (cortex-auditor.md)

- YAML references agents: "Challenge Gate defined in cortex-holistic-validator.md"
- Agents reference YAML: "See index.yaml for trigger word list and risk thresholds"
- All 3 prompts link to agent/YAML definitions, not redefine them

---

## 🎯 Loading + Rule Ownership Protocol

**New agents follow this pattern:**

1. **Declare rule ownership:** "This agent owns X behavioral rule"
2. **Reference YAML:** "Parameters from cortex-registry/_cortex-master/index.yaml"
3. **No duplication:** Check CORTEX-AGENT-INDEX.md before defining new rule
4. **Update audit checklist:** Add new rule to quarterly governance audit

**Existing agents (audit required):**
- ✅ cortex-holistic-validator.md — Owns Challenge Gate, Validation Sequences
- ✅ cortex-architect.md — Owns Two-Phase Workflow, Mode Detection
- ✅ AGENT-INDEX.md — Owns Protocol Definitions, Loading Strategy
- ⚠️ response-format-standards.md — Owns Response Formats (move duplicates)
- ⚠️ cortex-architect.prompt.md — Owns Challenge Gate details (consolidate with agent)

---



**CRITICAL:** This file replaces bulk agent loading. Load specific agents ONLY when needed per intent.

### Loading Protocol

```yaml
Default Context: THIS FILE ONLY (~200 tokens)
Per Intent Load: 1-2 relevant agents (~1,000-2,500 tokens)
Total Savings: ~245,000 tokens per session (98% reduction)
```

---

## 🤖 Agent Registry (13 Core Agents)

### Master Orchestration
- **CORTEX.md** — Main orchestrator, routes all requests
  - **Load when:** Any production request
  - **Size:** ~250 lines
  - **Key capabilities:** Intent routing, MCP gateway, DoR classification

- **cortex-architect.md** — HEXA-mode router (AUDIT/DESIGN/PLAN/DIGEST/QUERY/META-AUDIT) + Production Readiness Gate
  - **Load when:** Architecture requests, planning, audits, production deployment
  - **Size:** ~939 lines
  - **Key capabilities:** Mode detection, challenge generation, ROI prioritization, alignment validation, production readiness checklist

### Validation & Governance Agents
- **cortex-holistic-validator.md** — Pre-implementation holistic validation (Phase 48) + Implementation Alignment Gate ⭐ ENHANCED
  - **Load when:** Before ANY IMPLEMENT/FIX/REFACTOR intent
  - **Size:** ~480 lines
  - **Key capabilities:** Registry cross-validation, dependency analysis, regression risk scoring, mandatory challenge gate, cortex_brain self-analysis, pre-implementation alignment checks, duplicate detection, test plan validation, LENS integration validation
  - **Enforcement:** BLOCKING — No implementation without validation pass + alignment check

- **architecture-integrity-agent.md** — Wiring alignment enforcer + Auto-remediation ⭐ NEW (Phase 70)
  - **Load when:** Pre-commit hooks, CI/CD pipeline, monthly audits, alignment validation requests
  - **Size:** ~850 lines
  - **Key capabilities:** Wiring ↔ implementation alignment validation (100% target), stub test detection + auto-deletion, duplicate orchestrator detection (>85% similarity), usage tracking + retirement analysis, dependency validation, autonomous gap remediation, dashboard monitoring integration
  - **Enforcement:** BLOCKING — Pre-commit validation blocks commits with alignment <100%, CI/CD blocks merges, production deployment requires full alignment
  - **Auto-fix:** Module path correction, unwired implementation wiring (<5 count), stub test deletion (confidence >95%), priority conflict resolution
  - **Integration:** Real-time dashboard widget, monthly comprehensive audit, GitHub Actions workflow
  - **Target Metrics:** 100% wiring alignment, 0 stub tests, 0 duplicates, 95% orchestrator utilization

- **cortex-auditor.md** — Codebase health scanning + Implementation Alignment Audit ⭐ ENHANCED
  - **Load when:** `/audit`, quality analysis, alignment validation
  - **Size:** ~327 lines
  - **Key capabilities:** P0-P3 issue detection, security scanning, P0.5 holistic validation, P1 implementation alignment audit (wiring score, unwired implementations, stub tests, duplicates, usage analysis), autonomous remediation recommendations
  - **Enforcement:** Comprehensive 12-check alignment matrix, auto-fix eligible issues with confidence >90%, monthly audit automation

### Specialist Agents
- **cortex-designer.md** — Design mode specialist
  - **Load when:** Implementation requests with design phase
  - **Size:** ~229 lines
  - **Key capabilities:** TDD orchestration, incremental execution

- **cortex-mcp-gateway.md** — MCP tool orchestration
  - **Load when:** MCP tool invocation needed
  - **Size:** ~229 lines
  - **Key capabilities:** Tool routing, error handling, retry logic

- **cortex-interactive.md** — Conversational mode
  - **Load when:** Questions, exploratory discussions
  - **Size:** ~516 lines
  - **Key capabilities:** No TDD, no DoR gate, educational responses

- **cortex-digest.md** — Learning extraction
  - **Load when:** Processing chat history files
  - **Size:** ~276 lines
  - **Key capabilities:** Pattern extraction, knowledge enhancement

- **cortex-environment-setup.md** — Environment validation
  - **Load when:** Pre-flight checks, setup issues
  - **Size:** ~510 lines
  - **Key capabilities:** Python validation, dependency checks

- **cortex-storyteller.md** — Documentation generation
  - **Load when:** Creating narratives, reports
  - **Size:** ~274 lines
  - **Key capabilities:** Context synthesis, markdown generation

- **cortex-phase-resolver.md** — Plan phase management
  - **Load when:** `/plan` mode, phase execution
  - **Size:** ~346 lines
  - **Key capabilities:** ROI calculation, progress tracking

- **cortex-executor.md** — Code execution specialist
  - **Load when:** Running tests, executing implementations
  - **Size:** ~215 lines
  - **Key capabilities:** Test execution, validation

---

## 🎯 Intent → Agent Mapping

| User Intent | Load These Agents |
|-------------|-------------------|
| **IMPLEMENT** | CORTEX.md + cortex-holistic-validator.md + cortex-designer.md |
| **AUDIT** | CORTEX.md + cortex-architect.md + cortex-auditor.md |
| **QUESTION** | CORTEX.md + cortex-interactive.md |
| **PLAN** | cortex-architect.md + cortex-phase-resolver.md |
| **DIGEST** | cortex-architect.md + cortex-digest.md |
| **FIX** | CORTEX.md + cortex-holistic-validator.md + cortex-designer.md |
| **REFACTOR** | CORTEX.md + cortex-holistic-validator.md + cortex-designer.md |
| **SETUP** | cortex-environment-setup.md |
| **MCP** | cortex-mcp-gateway.md |
| **VALIDATE** | cortex-holistic-validator.md |

---

## 🛡️ Holistic Validation Flow (Phase 48)

**CRITICAL:** For IMPLEMENT/FIX/REFACTOR intents, load cortex-holistic-validator.md BEFORE cortex-designer.md

```
User Request (IMPLEMENT/FIX/REFACTOR)
         ↓
Load: cortex-holistic-validator.md
         ↓
Execute Validation Sequence:
  1. Registry holistic check
  2. Dependency graph analysis
  3. Regression risk scoring
  4. Architecture drift detection
  5. Mandatory challenge gate
  6. cortex_brain self-analysis
         ↓
IF PASS/WARN → Load cortex-designer.md → Proceed
IF BLOCK → Stop, show remediation, require override
```

---

## 📊 Token Budget Management

```yaml
Initial Budget: 1,000,000 tokens
Reserved for User: 800,000 tokens (80%)
Available for Context: 200,000 tokens (20%)

Context Breakdown:
  - copilot-instructions.md: ~10,000 tokens
  - Primary prompt: ~20,000 tokens
  - AGENT-INDEX.md: ~1,000 tokens
  - Lazy-loaded agents: ~2,000 tokens (per intent)
  - User workspace context: ~167,000 tokens

Total Used: ~200,000 tokens
Remaining for Response: 800,000 tokens ✅
```

---

## 🚀 Usage Instructions

**For GitHub Copilot:**
1. Load THIS file at initialization (not individual agents)
2. Parse user request to determine intent
3. Load ONLY the 1-2 agents needed per intent
4. Never pre-load all agents simultaneously

**For Prompts:**
- Reference `AGENT-INDEX.md` instead of linking to individual agents
- Use intent-based lazy loading
- Monitor token usage per turn

---

## ✅ Verification

**Before this index:**
- ❌ All 11 agents loaded (~8,200 lines)
- ❌ ~250,000 tokens consumed at init
- ❌ Forced summarization on every turn
- ❌ Poor user experience

**After this index:**
- ✅ Only relevant agents loaded (~500-1,000 lines)
- ✅ ~30,000 tokens consumed at init (88% reduction)
- ✅ No premature summarization
- ✅ Fast, responsive interactions

---

*v1.2 — Silent autonomous execution + token optimization index*
