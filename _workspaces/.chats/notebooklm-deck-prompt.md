# NotebookLM Deck Prompt — CORTEX Technical Presentation
**Audience:** Tech Leads & Software Engineers  
**Slides:** ≤ 10 | **Format:** High-value visuals, minimal prose  
**Created:** 2026-02-26

---

## 🎯 PROMPT FOR NotebookLM

---

> **Paste the following into NotebookLM as your Studio prompt:**

---

### PROMPT START

You are creating a **high-impact technical slide deck** for an audience of **tech leads and software engineers**.

**Subject:** CORTEX — a production-grade AI Engineering Framework built on a unified Python package (`cortex.*`), 51 wired orchestrators, 39 MCP tools, and 38 CORE governance rules.

**Constraints:**
- Maximum **10 slides**
- Every slide must contain **one dominant visual element** (architecture diagram, flow chart, table, code snippet, or metric callout) — no bullet-heavy walls of text
- Lead with **what the system does**, not how it was built
- Each slide must answer one engineer's question in ≤ 30 words of prose

**Slide plan — produce exactly these 10 slides:**

---

**SLIDE 1 — The Problem (1 visual: tension diagram)**
Title: *"Why does AI-assisted development break at scale?"*
Visual: A split diagram showing LEFT side (fragmented tools: Copilot, shell scripts, ad-hoc pytest, manual governance) vs RIGHT side (unified CORTEX pipeline). Label each pain point on the left: no audit trail, drift between tools, no TDD gate, no cross-team consistency.
Prose (≤ 20 words): "Scattered AI tools create invisible debt. CORTEX is the engineering framework that enforces discipline."

---

**SLIDE 2 — What CORTEX Is (1 visual: layered architecture box)**
Title: *"One Package. Four Tiers. Zero Ambiguity."*
Visual: Vertical stack diagram with 4 labeled tiers:
  - Tier 1 — CORE Orchestrators (Master, IntentRouter, TDD, Enforcement)
  - Tier 2 — DOMAIN Orchestrators (Refactoring, Planning, Investigation)
  - Tier 3 — SUPPORT Orchestrators (Digest, Sweep, Bulk, Vacuum)
  - Tier 4 — GIT Orchestrators
Below the stack: "51 orchestrators | 39 MCP tools | 38 governance rules | 1 package: cortex.*"
Prose (≤ 20 words): "Every operation routes through MasterOrchestrator → IntentRouter → domain specialist. No side doors."

---

**SLIDE 3 — The MCP Architecture (1 visual: flow diagram)**
Title: *"Pylance-style MCP — Zero Setup, Always On"*
Visual: Sequence flow diagram:
  VS Code opens workspace → MCP stdio server auto-starts (python3 -m cortex.mcp) → GitHub Copilot Chat detects 39 tools → Engineer types natural language → IntentRouter classifies → Orchestrator executes
Callout box: "Transport: stdio | Config: .vscode/settings.json | Detection: cortex_verify(op='mcp')"
Prose (≤ 20 words): "No ports, no manual startup. MCP activates like Pylance — the moment VS Code opens."

---

**SLIDE 4 — The 4-Stage Pipeline (1 visual: pipeline rail diagram)**
Title: *"Every Request Follows One Path"*
Visual: Horizontal pipeline rail with 4 stations:
  [1. INTERACTION] → [2. INTENT] → [3. INTELLIGENCE (LENS)] → [4. EXECUTION]
Below each station, one sub-label:
  Comprehend + DoR | IntentRouter.route() | Language→Examine→Navigate→Synthesize | Delegate to Orchestrator
Colour-code: Stage 0 governance audit fires before Stage 1 (shown as a red guard gate).
Prose (≤ 20 words): "LENS analysis ensures every execution is workspace-aware, not just prompt-aware."

---

**SLIDE 5 — CORE Governance Rules (1 visual: rule card grid)**
Title: *"38 Rules. Zero Exceptions."*
Visual: 3×3 card grid showing the 9 most engineer-critical rules:
  | CORE-002 | No .md/.txt report files — all output inline |
  | CORE-008 | TDD mandatory — RED → GREEN → REFACTOR, always |
  | CORE-011 | Type hints on every function |
  | CORE-012 | Docstrings on all public APIs |
  | CORE-028 | snake_case file naming only |
  | CORE-035 | One canonical implementation — no duplicates |
  | CORE-048 | Holistic validation gate before any IMPLEMENT/FIX |
  | CORE-049 | Silent autonomous execution — no narration |
  | CORE-064 | Sweep completeness — fix the entire class, not one instance |
Footer: "Enforced at: pre-commit hook → CI → runtime (EnforcementOrchestrator)"
Prose (≤ 20 words): "Rules are not suggestions. EnforcementOrchestrator blocks commits that violate any P0 rule."

---

**SLIDE 6 — TDD-First Development Loop (1 visual: TDD cycle diagram)**
Title: *"No Code Ships Without a Failing Test First"*
Visual: Classic RED → GREEN → REFACTOR circle, but annotated with CORTEX specifics:
  - RED: TDDOrchestrator writes the failing test (CORE-008)
  - GREEN: Implement minimum code to pass
  - REFACTOR: RefactoringOrchestrator cleans; scorecard auto-generated
  - GATE: python3 scripts/run_tests.py smoke → AC_COMPLETE emitted
Outside ring callout: "16,259 tests | pytest-xdist -n auto | <60s smoke gate"
Prose (≤ 20 words): "CORTEX enforces TDD structurally — the framework won't proceed without a RED phase."

---

**SLIDE 7 — /audit fix Pipeline (1 visual: numbered stage ladder)**
Title: *"One Command. Production-Ready in 9 Stages."*
Visual: Vertical numbered ladder (Stage -1 → Stage 9) with short labels:
  -1: Environment preflight
   0: Inflight upgrade check
   1: Stage 0 governance pre-flight
   2: 19-point production scan
   3: Wiring contract validation
   4: Orchestrator health (51 checked)
   5: Vacuum / markdown cleanup
   6: Prompt/agent meta-audit (23 checks)
   7–8: Auto-fix convergence loop (loops until 0 P0/P1)
   9: Tests + AC_COMPLETE → SQLite cleanup
Callout: "Convergence guarantee: Stages 7–8 loop until p0_count == 0 AND p1_count == 0 (CORE-064)"
Prose (≤ 20 words): "Not a single pass. CORTEX loops until the codebase is genuinely clean."

---

**SLIDE 8 — Observability & Audit Trail (1 visual: data flow into SQLite)**
Title: *"Every Action Is Traced. Nothing Is Silent."*
Visual: Fan-in diagram: multiple orchestrators (boxes labelled with names) each emitting AC_START / AC_COMPLETE markers → single arrow into .cortex-runtime/traces/orchestrator-traces.db → four output query paths: audit_sessions | audit_violations | workflow_cycles | workflow_runs
Code snippet (small, monospaced):
  # AC_START: AC-TDD-20260226T143200
  # ... execution ...
  # AC_COMPLETE: AC-TDD-20260226T143200 ✅ 142ms
Prose (≤ 20 words): "Orphaned AC_START without AC_COMPLETE = P0 violation. The DB is your governance ledger."

---

**SLIDE 9 — Test Execution Strategy (1 visual: 3-layer pyramid)**
Title: *"Smart Testing — Run Only What Matters"*
Visual: Inverted 3-layer pyramid (fastest at top, slowest at bottom):
  Top (fastest, TDD inner loop): `make test-changed` — pytest-testmon, changed files only, <5s
  Middle (smoke gate, pre-commit): `make test-smoke` — preflight + core, <60s
  Bottom (full suite, CI): `make test-parallel` — pytest-xdist -n auto, 16,259 tests
Callout boxes on the side:
  "CORTEX_WORKERS=4 caps parallelism for CI"
  "CORTEX_DISABLE_TESTMON=true for clean runs after large refactors"
Prose (≤ 20 words): "Testmon means you only wait for tests that touch your change. Local TDD stays fast."

---

**SLIDE 10 — How to Adopt CORTEX (1 visual: 3-step onboarding ladder)**
Title: *"From Zero to Governed in 3 Steps"*
Visual: Rising staircase with 3 steps:
  Step 1 — Install & Connect
    python3 scripts/setup-mcp.py
    VS Code auto-detects MCP (Pylance-style)
  Step 2 — Run First Audit
    /audit fix  →  9-stage pipeline executes
    Inline violations table surfaced in Chat
  Step 3 — Develop with CORTEX Discipline
    Write test → implement → /audit fix → commit
    EnforcementOrchestrator guards every commit
Footer callout: "Docs: cortex-docs/ | Rules: cortex-registry/core/ | MCP: cortex/mcp/tools/"
Prose (≤ 20 words): "CORTEX is not a plugin. It is the engineering discipline layer your team was missing."

---

### PROMPT END

---

## 📎 Source Material to Upload to NotebookLM

Upload the following files as sources before generating the deck:

| Priority | File | Why |
|---|---|---|
| P0 | `.github/copilot-instructions.md` | Architecture numbers (51/39/38), canonical structure |
| P0 | `.github/prompts/cortex-architect.prompt.md` | Full pipeline, CORE rules, orchestrator domains |
| P1 | `cortex-registry/cortex-master.yaml` | Phase history, roadmap, current state |
| P1 | `cortex-docs/ARCHITECTURE-RECOMMENDATION.md` | Design rationale |
| P2 | `cortex-registry/core/tier0-skull/*.yaml` | CORE rule definitions |
| P2 | `scripts/run_tests.py` (first 80 lines) | Test tier evidence |

---

## 🎨 Design Guidance for NotebookLM

- **Colour palette:** Dark background (#0D1117), accent blue (#58A6FF), accent green (#3FB950), alert red (#F85149) — matches GitHub Dark + CORTEX terminal aesthetic
- **Font:** Monospaced (JetBrains Mono or Fira Code) for all code snippets and metric callouts; sans-serif (Inter or SF Pro) for prose
- **Icon system:** Use filled circles for pipeline stages (●), shields for governance rules (🛡️), and lightning bolts for performance claims (⚡)
- **No stock photos** — all visuals are diagrams, code, or metrics
- **Every slide has a single dominant element** that communicates without the prose label
