---
scope: non-production-admin
purpose: "Architecture review detail for cortex-architecture-review skill; reserved for skill loading"
---

# CORTEX Architecture Review Prompt

**Updated:** 2026-03-17 | **Mode:** Evidence-driven architecture review
**Refresh:** `python3 scripts/refresh_prompt_suite.py`

---

## Purpose

Use this prompt for repeatable, system-level reviews of CORTEX architecture, execution quality, tutorial explainability, cross-cutting governance, and Claude-primary backbone fitness.

This prompt is the canonical review brief for deep architecture analysis of CORTEX as a VS Code GitHub Copilot companion with Claude Code as the execution backbone.

---

## Review Objective

Perform a deep architectural and implementation review of CORTEX and determine whether the system is operating at full capacity across:
- architecture cohesion
- Claude-primary execution
- prompt/agent/skill wiring
- Tutorial Mode and explainability
- LENS and onboarding intelligence
- governance and policy enforcement
- `cortex-registry/` workflow and YAML cross-cuts
- knowledge YAML quality and usage
- response rendering consistency
- testing and golden coverage
- SQLite logging and traceability
- historical regression against prior branch state
- consolidation and tooling-footprint reduction

The review MUST identify contradictions, drift, brittle coupling, missing abstractions, duplication, dead pathways, weakened capabilities, and opportunities to simplify without losing power.

---

## Mandatory Evidence Sources

Always inspect live implementation before making claims.

- `cortex/` for runtime architecture, orchestration, LENS, onboarding, observability, learning, memory, and persistence
- `.github/prompts/`, `.github/agents/`, `.github/skills/`, `.github/templates/` for Copilot-side behavior
- `.claude/agents/`, `.claude/skills/`, `.claude/rules/`, `CLAUDE.md`, `.claude/CLAUDE.md` for Claude-primary backbone parity
- `cortex-registry/core/`, `cortex-registry/governance/`, `cortex-registry/workflows/`, `cortex-registry/knowledge/`, `cortex-registry/planning/` for governance, workflow, and knowledge contracts
- `tests/` and `docs/tests/` for regression, golden, and explainability coverage
- `scripts/` for validation, refresh, parity, and governance tooling
- Git branch history and `origin/CORTEX` for retained vs lost capability analysis

Never trust documentation alone. Verify prompt, agent, skill, YAML, and test claims against code and live references.

---

## Review Scope

### 1. Architecture and Product Fit

- Evaluate whether CORTEX is shaped as a high-value companion to VS Code GitHub Copilot with Claude Code as the primary execution surface.
- Check whether the boundaries between orchestration, skills, prompts, tools, memory, and response rendering are coherent.
- Surface over-engineering, parallel abstractions, fragmented routing, and accidental complexity.

### 2. Cross-Cutting Capability Map

Build an evidence-backed capability map that spans:
- intent routing
- agent and subagent delegation
- skill discovery and invocation
- LENS analysis and repo onboarding
- governance and policy enforcement
- workflow template execution
- response template rendering
- knowledge YAML synthesis and reference quality
- memory and learning loops
- observability and SQLite traceability
- tool footprint and runtime dependencies

Call out missing cross-cuts where capability exists in one surface but not another.

### 3. Claude Code Integration Model

- Verify separation of concerns between CORTEX control logic and Claude-primary execution.
- Inspect dual-surface parity across `.github/` and `.claude/`.
- Identify tight coupling, missing fallback paths, or duplicated policy logic.

### 4. Tutorial Mode and Explainability Pipeline

Treat this as a critical review lane.

- Verify trigger conditions for Tutorial Mode.
- Verify whether major decisions can be explained end-to-end: agent choice, subagent choice, skill selection, prompt construction, tool invocation, response rendering.
- Verify whether knowledge YAML references are real, relevant, and specific.
- Verify whether tutorial responses map decision -> reasoning -> evidence -> knowledge source.
- Verify whether dedicated Copilot Chat rendering uses the canonical response templates consistently.
- Verify whether normal mode and tutorial mode diverge in truth, not just verbosity.
- Identify missing, generic, stale, misleading, or non-actionable explanations.

### 5. Onboarding and Capability Discovery

- Review repo analysis, file discovery, heuristics, and inference of required agents, subagents, and skills.
- Check whether onboarding logic scales across company repositories, mono-repos, and mixed-language workspaces.
- Identify blind spots in recommendation quality and developer guidance.

### 6. Governance, Policy, and Registry Cross-Cuts

- Trace how `cortex-registry/core/`, governance YAMLs, workflow templates, and policy artifacts influence runtime behavior.
- Verify whether policy is enforced in code, prompts, agents, and skills without divergent truth sources.
- Identify stale, unused, duplicated, or unreachable registry contracts.

### 7. Knowledge YAML Integrity

- Verify which knowledge YAMLs are actually consumed.
- Identify stale references, low-value references, dead files, and knowledge that never reaches user-facing explanations.
- Check whether knowledge usage is traceable and testable.

### 8. Testing and Golden Coverage

- Inspect unit, integration, workflow, and golden coverage for architecture decisions and explainability outputs.
- Explicitly check for golden coverage of Tutorial Mode, response templates, routing decisions, onboarding recommendations, and knowledge-backed explanations.
- Call out deterministic gaps, flaky surfaces, and missing regression protection.

### 9. SQLite Logging and Observability

- Verify what is logged, where it is logged, and whether decision traces align with user-visible explanations.
- Review schema quality, migrations, retention, integrity, and usefulness for debugging.
- Check whether Tutorial Mode and explanation events are observable.

### 10. Historical Regression Analysis

- Compare current behavior against `origin/CORTEX`.
- Distinguish intentional simplification from accidental capability loss.
- Specifically track losses or weakening in tutorial behavior, explainability, onboarding, skill inference, logging, and review depth.

### 11. Capacity, Efficiency, and Footprint

- Assess context cost, prompt sprawl, tool sprawl, duplicated orchestration, redundant skill layers, and avoidable runtime complexity.
- Recommend simplifications that preserve capability while reducing drift risk and token/tool overhead.

---

## Review Method

1. Establish current architecture baseline from live code.
2. Build a cross-cutting capability matrix across runtime, prompts, agents, skills, YAML, tests, and logging.
3. Trace Tutorial Mode and explainability end-to-end.
4. Verify onboarding, LENS, memory, and learning loops.
5. Compare current system against `origin/CORTEX` and recent branch history.
6. Classify findings by severity and regression risk.
7. Produce a consolidation plan and prioritized action plan.

Always separate:
- intentional simplification
- incomplete migration
- accidental regression
- dead code or dead policy

---

## Finding Contract

For every issue include:
- severity: `critical`, `high`, `medium`, or `low`
- why it matters
- evidence: files, modules, prompts, skills, YAMLs, tests, or git history
- recommended fix, refactor, or consolidation path

Prioritize:
- runtime correctness
- architecture coherence
- explainability truthfulness
- governance integrity
- regression risk
- developer trust and learnability

---

## Required Output

1. Executive Summary
2. Architecture Review
3. Implementation Review
4. Agent / Subagent / Skill Model Review
5. Onboarding and Repo Analysis Review
6. Tutorial Mode & Explainability Review
7. Testing Review
8. SQLite Logging Review
9. Archived Branch Comparison
10. Consolidation Plan
11. Prioritized Action Plan
12. Appendix: files and modules reviewed

Findings MUST appear before broad summary commentary.

---

## Recurring Review Contract

When this prompt is reused after new enhancements:
- diff current HEAD against the last relevant review scope using git history
- identify newly added prompts, agents, skills, workflows, YAMLs, tests, and runtime components
- rescan cross-cutting capability wiring, not just the touched files
- verify whether new enhancements increased duplication, drift, token cost, or governance divergence
- verify whether tutorial and explainability coverage kept pace with the enhancement
- surface both net gains and newly introduced debt

This review MUST remain forward-looking and cumulative, not a one-time static audit.

---

## Non-Negotiable Rules

- Be precise, evidence-driven, and code-backed.
- Never assume docs are correct without verifying implementation.
- Never create standalone report files; keep output inline in chat.
- Prefer simplification and canonicalization over additive layers.
- Call out absent, partial, or low-value Tutorial Mode behavior explicitly.
- Treat response-template drift and knowledge-reference drift as first-class defects.