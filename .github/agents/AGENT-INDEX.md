# CORTEX Agent Index
**Version:** 1.0 | **Updated:** 2026-02-06 | **Purpose:** Lazy loading index to prevent token bloat

---

## ⚡ Token Optimization Strategy

**CRITICAL:** This file replaces bulk agent loading. Load specific agents ONLY when needed per intent.

### Loading Protocol

```yaml
Default Context: THIS FILE ONLY (~200 tokens)
Per Intent Load: 1-2 relevant agents (~1,000-2,000 tokens)
Total Savings: ~245,000 tokens per session (98% reduction)
```

---

## 🤖 Agent Registry (11 Core Agents)

### Master Orchestration
- **CORTEX.md** — Main orchestrator, routes all requests
  - **Load when:** Any production request
  - **Size:** ~250 lines
  - **Key capabilities:** Intent routing, MCP gateway, DoR classification

- **cortex-architect.md** — HEXA-mode router (AUDIT/DESIGN/PLAN/DIGEST/INTERACTIVE/META-AUDIT)
  - **Load when:** Architecture requests, planning, audits
  - **Size:** ~436 lines
  - **Key capabilities:** Mode detection, challenge generation, ROI prioritization

### Specialist Agents
- **cortex-auditor.md** — Codebase health scanning
  - **Load when:** `/audit`, quality analysis
  - **Size:** ~351 lines
  - **Key capabilities:** P0-P3 issue detection, security scanning

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
| **IMPLEMENT** | CORTEX.md + cortex-designer.md |
| **AUDIT** | CORTEX.md + cortex-architect.md + cortex-auditor.md |
| **QUESTION** | CORTEX.md + cortex-interactive.md |
| **PLAN** | cortex-architect.md + cortex-phase-resolver.md |
| **DIGEST** | cortex-architect.md + cortex-digest.md |
| **FIX** | CORTEX.md + cortex-designer.md |
| **REFACTOR** | CORTEX.md + cortex-designer.md |
| **SETUP** | cortex-environment-setup.md |
| **MCP** | cortex-mcp-gateway.md |

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

*v1.0 — Token optimization index for lazy agent loading*
