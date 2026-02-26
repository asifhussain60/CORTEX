# Total Recall — Production Readiness Holistic Refactor Prompt

**Updated:** 2026-02-26 | **Protocol:** Challenge-First + Numeric Drift Detection + Zero-Version Audit  
**Authority:** Derived from Phase 16 Total Recall execution (chat01.md learnings)

---

## IDENTITY

**Total Recall Protocol** — A 7-phase holistic refactor that audits ALL CORTEX documentation, prompts, agents, and configuration for numeric drift, version violations, contradictions, and duplication. Produces a single unified brain with zero conflicts.

**Core Capabilities:**
- **Numeric Drift Detection** — Grep all claimed values, compare against file system source of truth
- **Version Audit** — Detect any `version: "2.0"`, `v2`, forked implementations (CORE-035 violations)
- **Contradiction Resolution** — Surface 3-way conflicts (metadata vs docs vs actual)
- **Duplication Elimination** — Merge overlapping flows into single canonical implementations
- **Automated Truth Establishment** — Terminal commands to derive canonical values from reality

---

## Challenge-First Protocol (execute in this order)

### 1) INVENTORY — Establish Canonical Values

**Purpose:** Collect ALL numeric claims from documentation and ALL actual values from file system, then build truth table.

**Execution:**

```bash
# A. Collect claimed values from all docs
grep -rn '27 wired\|26 MCP\|38 MCP\|35 CORE\|38 CORE\|16 canonical\|20 dirs\|51 orchestrator\|16,259 test' \
  .github/ cortex-registry/ --include="*.md" --include="*.yaml" | grep -v '__pycache__\|completed/'

# B. Establish file system truth
echo "1. Wired Orchestrators:" && \
  { grep '  - name:' cortex-registry/core/specifications/core-orchestrator-wiring.yaml; \
    grep '  - name:' cortex-registry/core/specifications/domain-orchestrator-wiring.yaml; \
    grep '  - name:' cortex-registry/core/specifications/support-orchestrator-wiring.yaml; \
    grep '  - name:' cortex-registry/core/specifications/git-orchestrator-wiring.yaml; } | \
  grep -v 'core_orchestrators\|governance_registry\|audit_logger\|state_manager\|documentation_system\|business_knowledge' | \
  sort -u | wc -l

echo "2. MCP Tools:" && \
  grep -rn 'class Cortex.*Tool\|class Cortex.*ConsolidatedTool' cortex/mcp/tools/ --include="*.py" | \
  grep -v '__pycache__\|Base\|Category\|Parameter' | wc -l

echo "3. CORE Rules:" && \
  grep -c 'rule_id: CORE-' cortex-registry/core/tier0-skull/skull-rules.yaml

echo "4. Top-level Dirs:" && \
  ls -d cortex/*/ | grep -v __pycache__ | wc -l

echo "5. Orchestrator Subdirs:" && \
  ls -d cortex/orchestrators/*/ | grep -v __pycache__ | wc -l
```

**Output:** Truth Table

| Metric | Claimed (docs) | Actual (file system) | Status |
|--------|----------------|----------------------|--------|
| Wired Orchestrators | (from grep A) | (from grep B.1) | ✅ / ❌ |
| MCP Tools | (from grep A) | (from grep B.2) | ✅ / ❌ |
| CORE Rules | (from grep A) | (from grep B.3) | ✅ / ❌ |
| Top-level Dirs | (from grep A) | (from grep B.4) | ✅ / ❌ |
| Orchestrator Subdirs | (from grep A) | (from grep B.5) | ✅ / ❌ |

---

### 2) CONTRADICTION DETECTION — Find All Conflicts

You are operating inside the CORTEX repo. Apply CORTEX Challenge-First Protocol to produce a single holistic refactor + cleanup that reduces duplication, maximizes unified intelligence, and prevents regressions.

Goal (one unified brain, zero drift)

Refactor and align the following as one system:

#file:copilot-instructions.md

#file:prompts/

#file:agents/

Outcomes:

Lean + accurate instructions/prompts/agents with no overlap, no conflicting guidance, and no redundant flows.

A single unified “brain” where all CORTEX intelligence/capabilities are wired together and maximized, with explicit brain tiers (routing by complexity/risk/latency).

Success + failure patterns are standardized, discoverable, and efficiently used at runtime (read/apply loops are explicit).

All golden tests are generated via a factory (consistent scaffolding + naming + fixtures + coverage invariants).

Key concern to resolve

We currently have overlapping flows (e.g., healthcheck, audit-and-fix, and others) doing the same job. Deliver the best unified efficient solution that eliminates duplication without losing coverage.

Constraints (must follow)

Assume the user has no knowledge of CORTEX architecture: explain structure briefly as part of the refactor.

Maintain MCP-first exposure, orchestrator integrity, and zero regression risk.

Produce executive-ready output optimized for VS Code Copilot Chat rendering: clear sections, bullets, and comparison tables.

All feedback should be inline (comments in-file / diffs / annotations).

Do not create any new summary/report markdown files. Only update existing files and create necessary non-report artifacts (e.g., test factory code, configs) if required by the plan.

Prefer minimal surface area changes with maximum leverage.

Challenge-First Protocol (execute in this order)
1) Audit existing capabilities (facts only)

Inspect copilot-instructions.md, prompts/, agents/ for:

Duplicated responsibilities (healthcheck/audit/fix overlap)

Conflicting rules and routing ambiguity

Missing/unclear “brain tier” definitions

Where success/failure patterns live and how they’re invoked

Golden test generation approach and gaps

Output a tight inventory table:

Component → Purpose → Inputs/Outputs → Overlaps → Risks → Keep/Merge/Remove

2) Architectural fit within current patterns (map before changing)

Identify the current orchestration pattern (who calls what, in what order).

Identify where MCP integration is expected and where it’s missing/duplicated.

Identify existing “brain” concepts (if any) and how tiers should align with current files.

3) Single best recommendation (addresses ask vs. tension inline)

Provide one unified solution that resolves duplication without losing functionality. It must include:

A single canonical workflow replacing overlapping “healthcheck” + “audit-and-fix” behaviors:

Example: One pipeline with modes/phases (Detect → Diagnose → Plan → Patch → Verify), rather than separate commands.

A clear routing model (brain tiers) determining:

Which agent/prompt executes, when, and with what guardrails.

A standardized success/failure pattern contract:

Where patterns are defined, how they’re referenced, and how they’re enforced.

A golden test factory approach:

Factory API, templates, invariants, and integration into CI.

4) Implement as edits (tight diffs, no fluff)

Perform the refactor by producing:

Concrete edits to copilot-instructions.md to become the single source of truth (SSOT) for:

Brain tiers

Orchestrator rules

MCP-first integration rules

Error handling + success criteria

Restructured prompts/ and agents/:

Remove duplication, consolidate naming, ensure each artifact has one job.

Ensure cross-references are consistent and minimal.

Add/upgrade golden test factory implementation and update tests to use it.

5) Zero regression proof (explicit)

Add or update:

Safety checks, invariants, and minimal CI gates.

A small set of golden tests that validate orchestration and routing.

Provide a “regression risk” section with mitigations and verification steps.

Required Output Format (≤ 60 seconds read)

Use the following structure exactly:

A) Current-State Audit (table)

Provide a concise inventory + overlap detection.

B) Problem: Duplication & Drift (bullet list)

Explicitly call out healthcheck/audit-and-fix overlap and consequences.

C) Recommendation: One Unified Solution (single choice)

Describe the unified pipeline, brain tiers, and pattern contracts.

D) Comparison Table (Before vs After)

Include: workflows, responsibilities, files touched, risk, maintainability.

E) Implementation Plan (phased, minimal risk)

Phase 0: Safety net (tests/invariants)
Phase 1: SSOT brain spec
Phase 2: Consolidate prompts/agents
Phase 3: Golden test factory rollout
Phase 4: Cleanup + enforce

F) Inline Diffs / Patch Instructions

Show exact edits for the specified files (and any necessary code/test files). Keep changes lean.

G) Verification (commands + expected signals)

Provide concrete steps to validate correctness and no regressions.

Design Pillars (evaluate every decision against these)

Extensibility: new capabilities plug in without new duplication.

Scalability: routing + tiers handle growth in agents/tools/tests.

Accuracy: fewer conflicting instructions; deterministic orchestration.

Team collaboration: predictable file layout, naming, conventions.

Long-term maintainability: SSOT rules, minimal redundancy.

Hard Requirements for the Unified Workflow

MCP-first exposure: tools/capabilities are invoked through MCP integration points by default; direct calls are the exception and must be justified.

Orchestrator integrity: one orchestrator entry point defines routing; no “shadow orchestrators” in prompt files.

Success/Failure patterns:

Patterns are referenced by canonical ID (no version suffixes — single implementation only).

Every agent/prompt declares which patterns it uses.

Failure patterns include: detect → rollback/contain → retry strategy → escalate.

Golden tests via factory:

All new golden tests must be created through the factory API.

Enforce with lint/CI or a test that fails if patterns are bypassed.

Zero versioning / single canonical implementation (CORE-035):

Everything in CORTEX is version 1.0 — there is ONLY ONE implementation of any concept, pattern, workflow, template, or block. No v2, no "enhanced" copies, no parallel editions.

No file, YAML entry, prompt, agent, or template may declare a version other than 1.0. If a capability is improved, the single canonical implementation is updated in-place — not forked into a "v2" alongside the original.

Zero contradictions, zero conflicts: no two files may give conflicting guidance on the same topic. If the same concept is referenced from multiple locations, one file is the SSOT and all others pointer-reference it.

Audit check: `grep -rn 'version.*[2-9]\.' cortex-registry/ .github/ cortex/` must return zero matches (excluding third-party dependency versions and external standard references like OWASP).

Violation is P0: any versioned duplicate (e.g., "template v2", "pipeline 2.0", "schema v2.0") indicates a CORE-035 violation — the old version was not replaced, it was forked. Remediation: merge into the single canonical version, delete the fork, update all references.

Deliverable

Execute the protocol and implement the refactor now, producing the required output format and inline diffs.

Only one recommendation. No alternative architectures unless required to justify risk mitigation.