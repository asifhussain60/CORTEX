# Token Optimization

---
title: Token Optimization — Maximizing GitHub Copilot Chat Sessions
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-28
source_of_truth: .github/copilot-instructions.md + .github/prompts/cortex-architect.prompt.md + .github/agents/AGENT-INDEX.md + cortex/core/prompt_agent_integration.py + cortex/core/intelligence_mixin.py
order: 8
---

> **Brain analogy:** Token optimization is the **energy metabolism** of CORTEX. Just as the brain consumes 20% of the body's energy but must be ruthlessly efficient about which neurons fire and when, CORTEX must be ruthlessly efficient about which context bytes are loaded into each Copilot Chat session. Wasted tokens are wasted intelligence cycles.

---

## Why Token Optimization Matters

Every VS Code GitHub Copilot Chat session has a finite **context window** — the maximum number of tokens the LLM can hold simultaneously. CORTEX is a large framework (259 orchestrator files across 9 domains, 29 registered MCP tools, 32 governance rules, thousands of tests). Loading everything into every session would exhaust the context budget before the user even asks a question.

Token optimization ensures that every turn in a Copilot Chat session carries only the context the LLM needs — nothing more, nothing less. This directly impacts:

- **Session longevity** — fewer tokens per turn means more turns before the session's budget is exhausted
- **Response quality** — relevant context produces better answers than diluted context
- **Latency** — smaller payloads process faster

---

## The 3-Tier Loading Model

CORTEX implements a **3-tier progressive loading model** that mirrors how the brain activates only the neural pathways needed for a given task:

| Tier | File | When Loaded | Token Cost | What It Contains |
|------|------|-------------|------------|-----------------|
| **T0 — Auto** | `copilot-instructions.md` | Every session (auto by GitHub Copilot) | ~2,700 tokens | Architecture summary, key rules, test commands, file organization |
| **T1 — Prompt** | `CORTEX.prompt.md` or `cortex-architect.prompt.md` | Per session type (user selects via `#file:`) | ~1,500–2,700 tokens | Full mode definitions, routing, governance, response format |
| **T2 — Agent** | Individual agent files in `.github/agents/` | Per intent (lazy-loaded on demand) | ~1,000–5,000 tokens each | Specialist logic for specific execution modes |

### How the Tiers Interact

```
Session Start
    │
    ▼
T0: copilot-instructions.md (~2,700 tokens)  ← Always loaded automatically
    │
    ▼
T1: cortex-architect.prompt.md (~2,700 tokens)  ← User attaches via #file:
    │
    ▼
T2: cortex-executor.md (~2,500 tokens)  ← Loaded on-demand per intent
    │
    Total: ~7,900 tokens (not 50,000+)
```

**Rule:** Each tier may repeat key facts (counts, rules) for context independence, but the **values** must be identical across tiers. Conflicting values across tiers is a P0 governance violation, detected by the Total Recall protocol and the Meta-Audit (Stage 6).

---

## Seven Token Optimization Strategies

### Strategy 1: Lazy Agent Loading

CORTEX never bulk-loads all agent files. The `AGENT-INDEX.md` file (~1,900 tokens) serves as a lightweight registry. Only 1–2 agents are loaded per intent.

| User Intent | Agents Loaded | Token Cost |
|-------------|---------------|-----------|
| IMPLEMENT / FIX / REFACTOR | cortex.md + cortex-holistic-validator.md + cortex-executor.md | ~7,000 |
| AUDIT | cortex.md + cortex-architect.md + cortex-auditor.md | ~8,000 |
| QUERY | cortex.md + cortex-interactive.md | ~4,500 |
| REPHRASE | request-rephrase-orchestrator.md only | ~2,000 |
| VACUUM | cortex-vacuum.md only | ~2,000 |

**If all 17 agents were loaded simultaneously:** ~50,000+ tokens consumed before the user asks anything. With lazy loading: ~2,000–12,000 tokens depending on intent.

**Implementation:** `cortex/core/prompt_agent_integration.py` — the `AgentLoader` class maintains a cache of loaded agents and maps intents to the minimum required agent set.

### Strategy 2: LENS Intelligence Tiering

Not every request needs deep code analysis. CORTEX's `UnifiedIntelligenceProvider` selects the analysis depth automatically:

| Tier | Latency | Scope | When Used |
|------|---------|-------|-----------|
| Quick | <200ms | Cached rules only | QUERY, REPHRASE — no code analysis needed |
| Targeted | <2s | LENS + relevant YAMLs | IMPLEMENT, FIX, REFACTOR — focused analysis |
| Full | <10s | LENS + Knowledge Graph + Profiles | INVESTIGATE — deep analysis only when needed |

**Token savings:** Quick tier injects ~100 tokens of cached context. Full tier may inject ~3,000 tokens of LENS results. Using Quick where Full is unnecessary saves ~2,900 tokens per turn.

**LENS Auto-Fetch rules:**
- ✅ Always triggered: IMPLEMENT, FIX, REFACTOR, INVESTIGATE, AUDIT
- 🔵 Conditional: DIGEST (Pipeline 2 repo content only)
- ⚪ Never triggered: PLAN, DESIGN, QUERY, REPHRASE

**Implementation:** `cortex/core/intelligence_mixin.py` — `IntelligenceMixin.get_lens_context()` uses deferred imports and lazy loading. Heavy imports from `cortex.lens` happen inside the method call, not at module load time.

### Strategy 3: Request Rephrase (Token Compression)

The `/rephrase` command converts verbose natural-language requests into CORTEX-efficient single-paragraph prompts. This compresses user intent into the minimum tokens needed for accurate intent routing.

**Before rephrase (87 tokens):**
> "I have this bug where the orchestrator factory is not loading the right orchestrator when I send a request through the MCP gateway. It seems like the intent router is sending it to the wrong place. Can you help me figure out what's going on and fix it?"

**After rephrase (31 tokens):**
> "FIX: IntentRouter misrouting MCP requests — OrchestratorFactory loads incorrect orchestrator. Root cause analysis + TDD fix via TDDOrchestrator. Scope: cortex/orchestrators/core/, cortex/mcp/."

**Implementation:** `cortex/orchestrators/core/request_rephrase_orchestrator.py` — `RequestRephraseOrchestrator.analyze()` parses intent, extracts scope, measures confidence, and generates a compressed prompt with governance context injected inline.

### Strategy 4: Continuation Prompt Compression

When a session approaches its token budget (>90% used), CORTEX generates a minimal continuation prompt instead of replaying the full conversation history.

**Traditional continuation (60,000 tokens):** Full replay of all completed stages, file contents, terminal output, and session context.

**CORTEX continuation (~60 tokens):**
```markdown
**#file:cortex-architect.prompt.md**
**Session:** Current task · Stage 7.2
**Branch:** CORTEX
**Context:** exposure_auditor.py ✅
**Next:** Implement tool_spec_generator.py (22 orchestrators)
**Command:** `/implement tool_spec_generator`
```

This works because:
- `#file:` references load the prompt automatically (0 tokens — the IDE handles it)
- Git branch context is available from the workspace
- Chat history is automatically available in a new session
- Only the checkpoint delta needs to be stated

**Result:** 99.9% reduction (60 tokens vs 60,000 tokens).

**Implementation:** `.github/templates/cortex-response-templates.md` § Continuation Prompts

### Strategy 5: YAML Lazy Loading with Caching

CORTEX governance rules, patterns, and workflow templates are stored in YAML files across `cortex-registry/`. Instead of loading all YAML at session start, CORTEX uses lazy loaders with LRU caching:

- **First access** loads and parses the YAML file
- **Subsequent accesses** return the cached result (zero parse cost)
- **Cache invalidation** occurs when the file's modification time changes

**Implementation:** `cortex/core/yaml_loaders.py` — the `BaseYAMLLoader` class with `lru_cache` decorators, originating from ENH-048 (Prompt Unbloating System).

### Strategy 6: Thin Index Contract (Master Plan)

`cortex-master.yaml` is a **reference index only** — never a detail document. Phase detail lives in dedicated files under `cortex-registry/planning/phases/`. This prevents the master plan from growing to thousands of lines (it once hit 3,007 lines, causing context exhaustion).

**Rules:**
- `cortex-master.yaml` must remain ≤500 lines (alarm at 400)
- Phase detail lives in `cortex-registry/planning/phases/planned/<phase-id>.yaml`
- Only thin reference entries in the master plan: `id`, `title`, `status`, `priority`, `file`, `note`
- Prohibited inline: `phases`, `gap_catalogue`, `tdd_sequence`, `rewrites`, `new_files`, `implementation`

**Token impact:** Loading a 500-line index costs ~800 tokens. Loading a 3,007-line bloated plan costs ~5,000+ tokens — a 6× overhead that delivers diminishing context quality.

### Strategy 7: Silent Autonomous Execution (CORE-049)

During autonomous operations (triggered by "proceed", "implement", "continue"), CORTEX suppresses narration and uses progress bars only:

```
[████████░░] 80% — Stage 7: Auto-fix convergence
```

**What is suppressed:**
- ❌ "I'll now search for…" narration
- ❌ "Let me check…" confirmations
- ❌ Verbose stage descriptions mid-execution
- ❌ Report files (.md/.txt) — CORE-002

**What is shown:**
- ✅ Progress bar (exactly 10 blocks)
- ✅ Stage bullet list with status icons (✅/🔵/⚪/🔴)
- ✅ Final results inline

**Token savings:** A narrated 9-stage `/audit fix` might consume ~8,000 tokens in status updates. Silent execution uses ~500 tokens for the same operation.

---

## Token Budget Architecture

### Budget Allocation per Session Type

| Session Type | T0 (Auto) | T1 (Prompt) | T2 (Agents) | LENS | Working | Total |
|---|---|---|---|---|---|---|
| Simple query | ~2,700 | ~1,500 | ~1,500 | 0 | ~500 | ~6,200 |
| Implement feature | ~2,700 | ~2,700 | ~7,000 | ~2,000 | ~5,000 | ~19,400 |
| Full audit fix | ~2,700 | ~2,700 | ~12,000 | ~3,000 | ~10,000 | ~30,400 |
| Rephrase | ~2,700 | 0 | ~2,000 | 0 | ~200 | ~4,900 |

### What GitHub Copilot Already Provides (Never Duplicate)

These elements are automatically available in every session — duplicating them wastes tokens:

- ❌ **Chat history** — automatically carried across turns
- ❌ **File contents** — use `#file:` references instead of pasting
- ❌ **Implementation details** — in git history, not conversation replay
- ❌ **Terminal output** — available from terminal state
- ❌ **Stage specifications** — in task specs files, not inline

---

## Implementation Map

| Optimization | Implementation File | Governance |
|---|---|---|
| 3-Tier Loading Model | `.github/copilot-instructions.md` (T0), `.github/prompts/` (T1), `.github/agents/` (T2) | AGENT-INDEX.md |
| Lazy Agent Loading | `cortex/core/prompt_agent_integration.py` | AgentLoader class |
| Intelligence Tiering | `cortex/core/intelligence_mixin.py` | IntelligenceMixin |
| Request Rephrase | `cortex/orchestrators/core/request_rephrase_orchestrator.py` | RequestRephraseOrchestrator |
| Continuation Compression | `.github/templates/cortex-response-templates.md` | § Continuation Prompts |
| YAML Lazy Loading | `cortex/core/yaml_loaders.py` | BaseYAMLLoader + lru_cache |
| Thin Index Contract | `cortex-registry/cortex-master.yaml` | CORE-002, ≤500 lines |
| Silent Execution | CORE-049 governance rule | EnforcementOrchestrator |
| LENS Auto-Fetch | `cortex/orchestrators/core/intent_router.py` | Intent-based gating |

---

## Monitoring and Enforcement

### How CORTEX Detects Token Waste

| Check | Detector | Severity |
|---|---|---|
| Agent bulk-loading | Meta-Audit Check #13 (Prompt/Agent coherence) | P1 |
| Bloated master plan | `wc -l cortex-master.yaml` > 500 | P0 |
| Narration during silent mode | CORE-049 enforcement | P1 |
| Report file creation | CORE-002 enforcement | P0 |
| Stale context duplication | Continuation prompt audit | P2 |
| LENS triggered for QUERY/REPHRASE | IntentRouter gating | P2 |

### Total Recall Protocol (Drift Prevention)

The `/totalrecall` command runs a 7-phase holistic audit that detects **numeric drift** across all three tiers. If `copilot-instructions.md` says "51 orchestrators" but an agent file says "44 orchestrators", the redundant/incorrect context wastes tokens and misleads the LLM.

**Verification command:** `python3 scripts/validate-architecture-counts.py`

---

## Practical Impact

| Scenario | Without Optimization | With Optimization | Savings |
|---|---|---|---|
| Session bootstrap | ~50,000 tokens (all agents) | ~5,400 tokens (T0 + T1 only) | 89% |
| Continuation prompt | ~60,000 tokens (full replay) | ~60 tokens (checkpoint only) | 99.9% |
| Simple query | ~20,000 tokens (full LENS) | ~6,200 tokens (Quick tier, no LENS) | 69% |
| 9-stage audit | ~40,000 tokens (narrated) | ~30,400 tokens (silent + lazy) | 24% |

**Net effect:** A typical developer session gets 3–5× more productive turns before context exhaustion.

---

*Verified against live codebase · Source files: `cortex/core/prompt_agent_integration.py`, `cortex/core/intelligence_mixin.py`, `cortex/core/yaml_loaders.py`, `.github/copilot-instructions.md`, `.github/agents/AGENT-INDEX.md`*
