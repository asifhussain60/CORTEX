# FAQ — Governance & TDD

---
title: FAQ — Governance & TDD
type: reference
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-25
source_of_truth: cortex-registry/core/tier0-skull/skull-rules.yaml + cortex/orchestrators/core/enforcement_orchestrator.py
order: 3
---

> **Purpose:** Answers to the most common questions about CORTEX's governance system, CORE rules, and TDD enforcement. All answers verified against `cortex-registry/core/tier0-skull/skull-rules.yaml` (37 CORE-* rules + 2 AC rules, 39 total entries).

---

## How many governance rules does CORTEX enforce?

**39 total rule entries** in `cortex-registry/core/tier0-skull/skull-rules.yaml`:
- **37 CORE-\*** rules (`CORE-001` through `CORE-064`, non-contiguous)
- **2 AC-PERMANENT-FIX** rules (`AC-PERMANENT-FIX-006`, `AC-PERMANENT-FIX-007`)

The metadata header says `rule_count: 35` — this reflects the originally registered canonical CORE rules. New rules (CORE-055, CORE-058 through CORE-064) were added in later phases. All 37 CORE-* rules are enforced at **pre-commit + CI + runtime**.

---

## What are the most important CORE rules to know?

| Rule | Name | Why It Matters |
|------|------|---------------|
| **CORE-001** | Flywheel Effect | Operations must work in <500-line increments; state persists between turns |
| **CORE-002** | Markdown Suppression | Never create `.md`/`.txt` report files — all output inline |
| **CORE-008** | TDD Mandatory | Write failing test first. No exceptions. BLOCKED if skipped |
| **CORE-011** | Type Hints | All functions must have type annotations |
| **CORE-012** | Docstrings | All public APIs must have docstrings |
| **CORE-028** | File Naming | snake_case only — no PascalCase or camelCase filenames |
| **CORE-035** | Single Canonical | No duplicate implementations anywhere |
| **CORE-048** | Holistic Validation | Full validation gate before IMPLEMENT/FIX/REFACTOR |
| **CORE-049** | Silent Execution | Progress bars only — no verbose chatter |
| **CORE-055** | Golden Test Contract | 486 golden tests in `tests/golden/` must always pass |
| **CORE-064** | Sweep Completeness | No partial sweeps — every FIX/REFACTOR/AUDIT exhausts its catalogue |

---

## Can I disable a CORE rule?

**No.** Tier 0 skull rules (`cortex-registry/core/tier0-skull/skull-rules.yaml`) are **immutable**. They cannot be overridden, disabled, or bypassed — the file header explicitly states:

> *"CRITICAL: These rules are IMMUTABLE and take precedence over all other tiers. Tier 0 = SKULL rules - cannot be overridden."*

If a rule conflicts with your project's needs, the correct path is to open a governance review — not to modify `skull-rules.yaml` directly.

---

## What is EnforcementOrchestrator and what does it check?

**EnforcementOrchestrator** (`cortex/orchestrators/core/enforcement_orchestrator.py`) coordinates **10 enforcement agents** that each check a category of CORE rules:

| Agent | CORE Rules Checked |
|-------|--------------------|
| TestNamingAgent | CORE-026 (test naming conventions) |
| FileNamingAgent | CORE-028 (snake_case filenames) |
| ImportValidationAgent | CORE-013 (canonical imports only) |
| TypeHintAgent | CORE-011 (type hints on all functions) |
| DocstringAgent | CORE-012 (docstrings on public APIs) |
| DuplicateDetectionAgent | CORE-035 (no duplicate implementations) |
| SecurityScanAgent | CORE-017 (no credentials in code) |
| ExtendedGovernanceAgent | CORE-058 through CORE-063 |
| TDDAgent | CORE-008 (tests before implementation) |
| ArchitectureAgent | CORE-048 (holistic validation gate) |

Gate results are **PASS**, **WARNING**, or **BLOCKED**. A BLOCKED result stops the operation immediately — no files are modified.

---

## What is the TestQualityGate?

A scoring system (0–9) that evaluates every test against 5 criteria:

| Criterion | Weight | What It Measures |
|-----------|--------|-----------------|
| Impact | High | Does this test catch real bugs? |
| Likelihood | High | How often would this failure surface? |
| Detection | Medium | Would this failure be hard to find manually? |
| Efficiency | Medium | Does the test run fast? |
| Maintenance | Low | Is the test easy to maintain? |

**Score bands:**
- **≥ 7** — KEEP (golden tier candidate)
- **4–6** — REVIEW (may need improvement)
- **< 4** — DELETE (low-value test consuming CI time)

**Live location:** `cortex/testing/quality_gate.py` + `cortex-registry/core/test-quality-gate.yaml`
**MCP tool:** `cortex_generate_tests` uses TestQualityGate scores when scaffolding new tests.

---

## What is CORE-055 — Golden Test Tier Contract?

**CORE-055** mandates that the **486 golden tests** in `tests/golden/` must **always pass** with zero regressions.

Golden tests are the highest-value tests in the suite — they validate:
- Core orchestrator contracts (MasterOrchestrator, IntentRouter, TDDOrchestrator)
- Governance rule enforcement (CORE rules checked in isolation)
- LENS analysis correctness
- MCP tool registration and routing

They run **serially** (no xdist parallelism) for deterministic results. A golden test failure is a **P0 blocker** — no commit can proceed until all 486 pass.

---

## What is CORE-064 — Sweep Completeness Contract?

**CORE-064** prevents partial sweeps — the most common source of technical debt accumulation in multi-session refactors.

**Before CORE-064:** A developer starts a 50-file FIX sweep. After 30 files, they switch context. The remaining 20 files stay broken with no record.

**After CORE-064:** Every FIX/REFACTOR/AUDIT creates a `SweepCatalogue` entry in SQLite. The catalogue tracks every item. The operation cannot be marked COMPLETE until:
- Every item has `status: CLOSED`, OR
- An explicit `approve_wont_fix` decision is recorded

The `/audit fix` convergence loop (Stages 7–8) enforces this — it loops until `p0_count == 0 AND p1_count == 0`, not just a single pass.

**Sweep status:** `SweepCatalogueOrchestrator.get_open_issues(sweep_id)` — query open sweeps, assert exhaustion, mark items resolved.

---

## Does governance slow development down?

In practice, no — and here's why:

1. **Gate latency is < 150ms** — enforcement agents run in parallel, not sequentially.
2. **Most requests pass all 10 gates** on the first try when following CORTEX patterns.
3. **The cost of governance is paid once** — before any files change. The cost of *not* having governance is paid repeatedly (regressions, partial sweeps, architectural drift).
4. **Pre-commit is the cheapest fix point** — a BLOCKED pre-commit is infinitely cheaper than a production incident.

The governance system is designed to be invisible when you follow the rules — and immediate when you don't.

---

## What is a pre-commit enforcement gate?

Before any `git commit` in the CORTEX workspace, **EnforcementOrchestrator** runs automatically via a Git pre-commit hook (`deployment/hooks/`). It checks all 10 governance agents. If any check returns BLOCKED, the commit is rejected with a specific violation message and the file that triggered it.

This is separate from CI — pre-commit catches violations on the developer's machine before they ever reach the pipeline.

---

## What is the difference between CORE-002 and creating documentation?

**CORE-002** (Markdown Suppression) blocks **execution report files** — status summaries, deployment docs, orchestrator outputs saved as `.md` files.

It does **not** block:
- `cortex-docs/.content/` — the canonical documentation folder (human-readable, version-controlled)
- `README.md` files that serve as genuine user-facing documentation
- Files explicitly requested by the user (`"save this as a report"`)

The rule's intent is: *eliminate noise, amplify signal*. Auto-generated status clutter is noise. Carefully authored documentation is signal.

---

## How does CORTEX enforce architecture integrity?

**Stage 3 of `/audit fix`** runs the **Wiring Contract Validation** using the architecture integrity agent. It checks three layers:

| Layer | What It Validates |
|-------|-------------------|
| **L1** | Every wired orchestrator exists at its declared path |
| **L2** | Every orchestrator satisfies `IOrchestrator` protocol |
| **L3** | All 51 wired orchestrators are reachable from MasterOrchestrator via IntentRouter |

Violations at L1 are P0 (missing files). L2 violations are P1 (protocol gap). L3 violations are P1 (dead orchestrator — wired but unreachable).

---

*Verified against `cortex-registry/core/tier0-skull/skull-rules.yaml` + `cortex/orchestrators/core/enforcement_orchestrator.py` · 25 February 2026*
