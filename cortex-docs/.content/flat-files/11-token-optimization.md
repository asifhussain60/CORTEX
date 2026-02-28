# Token Optimization — How CORTEX Maximizes GitHub Copilot Chat Sessions

---
title: Token Optimization — How CORTEX Maximizes Every Chat Turn
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-28
source_of_truth: .github/copilot-instructions.md + .github/prompts/cortex-architect.prompt.md + .github/agents/AGENT-INDEX.md + cortex/core/prompt_agent_integration.py + cortex/core/intelligence_mixin.py + cortex/core/yaml_loaders.py
consolidates: [05-infrastructure-token-optimization]
order: 8
---

> **The core problem:** CORTEX is a large framework — dozens of orchestrators, a growing library of MCP tools, comprehensive governance rules, thousands of tests, and multiple top-level directories. Every VS Code GitHub Copilot Chat session has a finite context window. Loading everything into every session would exhaust the token budget before the developer even asks a question. Token optimization ensures every turn carries only the context the LLM needs — nothing more, nothing less.

---

## Why This Matters

Token optimization directly impacts three things. **Session longevity** — fewer tokens per turn means more productive turns before the session budget is exhausted. **Response quality** — relevant context produces better answers than diluted, bloated context. **Latency** — smaller payloads process faster, meaning the developer waits less for each response.

Without optimization, a typical CORTEX session would consume ~50,000 tokens at bootstrap (loading all 17 agent files, all governance rules, full LENS context). With optimization, the same session starts at ~3,000 tokens — a 94% reduction — and loads additional context only when the specific intent demands it.

---

## The 3-Tier Progressive Loading Model

CORTEX implements a three-tier loading model that mirrors how the brain activates only the neural pathways needed for a given task.

**Tier 0 — Auto (always loaded, ~2,700 tokens).** The file `.github/copilot-instructions.md` is automatically loaded by GitHub Copilot in every session. This file contains the architecture summary (orchestrator tiers, MCP tools, CORE rules), the canonical package name (`cortex`), the file organization map, key governance rules, and the test execution commands. It is intentionally kept concise — dense, factual, and free of narrative.

**Tier 1 — Prompt (user-selected, ~1,500–2,700 tokens).** When a developer starts a session, they attach a prompt file via `#file:`. Two prompts serve different workflows. `CORTEX.prompt.md` (~1,500 tokens) covers day-to-day implementation, fix, and refactor work. `cortex-architect.prompt.md` (~2,700 tokens) covers architecture, auditing, design, and planning. The prompt contains full mode definitions, routing tables, governance rules, response format specifications, and the Agent Loading Map that tells the system which agents to load for each intent.

**Tier 2 — Agent (lazy-loaded per intent, ~1,000–5,000 tokens each).** Individual agent files in `.github/agents/` contain specialist logic for specific execution modes. The `AGENT-INDEX.md` file (~1,900 tokens) serves as a lightweight registry. Only 1–2 agents are loaded per intent. For example, a simple QUERY loads only `cortex-interactive.md` (~1,500 tokens). A full AUDIT FIX loads `cortex-auditor.md`, `architecture-integrity-agent.md`, and `cortex-meta-auditor.md` (~12,000 tokens). The system never bulk-loads all 17 agents simultaneously.

Each tier may repeat key architectural facts (orchestrator count, MCP tool count, CORE rule count) for context independence — a T2 agent should function correctly even if the T1 prompt is absent. But the **values** must be identical across all three tiers. Conflicting values is a P0 governance violation, detected by the Total Recall protocol (`/totalrecall`) and the Meta-Audit (Stage 6 of `/audit fix`).

---

## Seven Token Optimization Strategies

### 1. Lazy Agent Loading

The `AgentLoader` class in `cortex/core/prompt_agent_integration.py` implements intent-to-agent mapping with in-memory caching. When TDDOrchestrator needs `cortex-executor.md`, the loader checks its cache first. If the agent is already loaded (cache hit), zero tokens are spent. If not, it loads the agent file and caches it for subsequent calls.

The intent-to-agent mapping is maintained in `AGENT-INDEX.md` — IMPLEMENT, FIX, and REFACTOR all share the same agent set (`cortex.md` + `cortex-holistic-validator.md` + `cortex-executor.md`, ~7,000 tokens). REPHRASE uses only `request-rephrase-orchestrator.md` (~2,000 tokens). If all 17 agents were loaded simultaneously, the cost would exceed 50,000 tokens. Lazy loading reduces this to 2,000–12,000 tokens depending on the actual intent.

### 2. Intelligence Tiering

The `IntelligenceMixin` in `cortex/core/intelligence_mixin.py` provides lazy-loaded LENS access to all orchestrators. The `get_lens_context()` method uses deferred imports — heavy modules from `cortex.lens` are imported inside the method call, not at module load time. This means orchestrators that never touch LENS (such as VacuumOrchestrator or ConversationOrchestrator) pay zero import cost.

The IntentRouter further gates LENS activation by intent. IMPLEMENT, FIX, REFACTOR, INVESTIGATE, and AUDIT trigger full LENS analysis. DIGEST triggers conditional LENS (Pipeline 2 repo content only). PLAN, DESIGN, QUERY, and REPHRASE skip LENS entirely — because code analysis is not needed to answer architectural questions or rephrase a request. This saves ~2,000–3,000 tokens per turn for intents that do not need code intelligence.

Within LENS itself, three speed tiers exist: Quick (under 200ms, cached rules only, ~100 tokens of context), Targeted (under 2 seconds, LENS scan plus relevant YAMLs, ~1,500 tokens), and Full (under 10 seconds, LENS plus Knowledge Graph plus Profiles, ~3,000 tokens). The IntentRouter selects the tier automatically based on request classification.

### 3. Request Rephrase (Token Compression)

The `/rephrase` command runs through the `RequestRephraseOrchestrator`, which compresses verbose natural-language requests into CORTEX-efficient single-paragraph prompts. A typical user request like "I have this bug where the orchestrator factory is not loading the right orchestrator when I send a request through the MCP gateway — it seems like the intent router is sending it to the wrong place — can you help me figure out what's going on and fix it?" contains 87 tokens. The rephrase output — "FIX: IntentRouter misrouting MCP requests — OrchestratorFactory loads incorrect orchestrator. Root cause analysis + TDD fix via TDDOrchestrator. Scope: cortex/orchestrators/core/, cortex/mcp/." — is 31 tokens. The compression also injects governance context (CORE-008 TDD mandate, CORE-064 sweep completeness) inline, so the downstream orchestrator receives both the request and the compliance context in a single compressed payload.

### 4. Continuation Prompt Compression

When a session approaches its token budget (above 90% usage), CORTEX generates a minimal continuation prompt instead of replaying the entire conversation history. Traditional continuation — replaying all completed stages, file contents, terminal output, and session context — consumes roughly 60,000 tokens. CORTEX's continuation format uses approximately 60 tokens: a `#file:` reference to reload the prompt (0 tokens — the IDE handles it), a session identifier, the git branch, the last completed checkpoint, the next immediate action, and a resume command. This is a 99.9% reduction.

The key insight is that GitHub Copilot already provides chat history, file contents (via `#file:`), terminal output, and git context automatically. Duplicating these in a continuation prompt wastes the exact tokens you are trying to preserve. CORTEX's continuation format provides only the delta — what changed since the last checkpoint.

### 5. YAML Lazy Loading with LRU Caching

Governance rules, workflow templates, and knowledge artifacts live in YAML files across `cortex-registry/`. The `BaseYAMLLoader` class in `cortex/core/yaml_loaders.py` (originating from ENH-048: Prompt Unbloating System) implements lazy loading with `lru_cache` decorators. The first access to a YAML file loads and parses it. Subsequent accesses return the cached result at zero parse cost. Cache invalidation occurs when the file's modification time changes.

The global loader registry uses lazy initialization — loaders for specific YAML file types (core rules, audit checklists, modes, response formats, personas) are instantiated only when first requested.

### 6. Thin Index Contract (Master Plan)

The `cortex-master.yaml` file is a reference index only — never a detail document. Phase detail lives in dedicated files under `cortex-registry/planning/phases/planned/` (active) and `cortex-registry/planning/phases/completed/` (archived). The master plan must remain at or below 500 lines (alarm at 400). It once grew to 3,007 lines when inline phase detail was written directly to it, causing 40+ YAML syntax errors, un-reviewable diffs, context exhaustion when loading the file, and no single-file accountability per phase.

The token impact is direct: a 500-line index costs approximately 800 tokens to load. A 3,007-line bloated plan costs over 5,000 tokens — a 6× overhead that delivers diminishing context quality because the LLM's attention is diluted across thousands of lines of phase detail it doesn't need for the current request.

### 7. Silent Autonomous Execution (CORE-049)

During autonomous operations triggered by "proceed", "implement", "continue", or "do it", CORTEX suppresses all narration and uses only progress bars and stage status icons. A narrated 9-stage `/audit fix` pipeline might consume approximately 8,000 tokens in status updates ("I'll now search for…", "Let me check…", "Here's what I found…"). Silent execution achieves the same result with approximately 500 tokens — a 10-block progress bar and a bullet list of stage completion icons.

CORE-002 reinforces this by prohibiting the creation of `.md` or `.txt` report files. All output is inline in the chat session. This prevents the pattern where a tool generates a report file, then the LLM reads the file back into the context — doubling the token cost for the same information.

---

## Token Budget by Session Type

A simple query (QUERY intent) costs approximately 6,200 tokens total: 2,700 for T0 auto-load, 1,500 for the T1 prompt, 1,500 for the T2 interactive agent, zero for LENS (not triggered), and 500 for working context. An implementation session (IMPLEMENT intent) costs approximately 19,400 tokens: 2,700 for T0, 2,700 for T1, 7,000 for three T2 agents, 2,000 for targeted LENS, and 5,000 for working context. A full audit fix costs approximately 30,400 tokens at peak: 2,700 for T0, 2,700 for T1, 12,000 for four T2 agents, 3,000 for full LENS, and 10,000 for working context across 9 stages. A rephrase costs approximately 4,900 tokens total — the lightest possible session type.

The practical effect is that a typical developer session gets 3–5× more productive turns before context exhaustion compared to a naive bulk-load approach.

---

## Enforcement and Monitoring

CORTEX detects token waste through multiple mechanisms. The Meta-Audit (23 checks, Stage 6 of `/audit fix`) validates prompt and agent coherence — detecting bulk-loaded agents, stale numeric counts, and redundant context. The Total Recall protocol (`/totalrecall`) runs a 7-phase holistic audit that flags numeric drift across all three tiers. The EnforcementOrchestrator blocks CORE-002 violations (report file creation) and CORE-049 violations (narration during silent mode) at pre-commit.

The `validate-architecture-counts.py` script verifies that all orchestrator counts, MCP tool counts, CORE rule counts, and test counts are consistent across `copilot-instructions.md`, all prompt files, and all agent files. Any mismatch wastes tokens by injecting contradictory context into the LLM — and is treated as a P0 validation failure.

---

## Implementation Map

The 3-Tier Loading Model is implemented across `.github/copilot-instructions.md` (T0), `.github/prompts/` (T1), and `.github/agents/` (T2), governed by `AGENT-INDEX.md`. Lazy Agent Loading is implemented in `cortex/core/prompt_agent_integration.py` via the `AgentLoader` class. Intelligence Tiering is implemented in `cortex/core/intelligence_mixin.py` via `IntelligenceMixin`. Request Rephrase is implemented in `cortex/orchestrators/core/request_rephrase_orchestrator.py`. Continuation Compression is defined in `.github/templates/cortex-response-templates.md` § Continuation Prompts. YAML Lazy Loading is implemented in `cortex/core/yaml_loaders.py` via `BaseYAMLLoader` with `lru_cache`. The Thin Index Contract governs `cortex-registry/cortex-master.yaml` structure. Silent Execution is enforced by CORE-049 via the `EnforcementOrchestrator`. LENS Auto-Fetch gating is implemented in `cortex/orchestrators/core/intent_router.py`.

---

*Verified against live codebase · Source files: `cortex/core/prompt_agent_integration.py`, `cortex/core/intelligence_mixin.py`, `cortex/core/yaml_loaders.py`, `.github/copilot-instructions.md`, `.github/agents/AGENT-INDEX.md`, `.github/templates/cortex-response-templates.md`*
