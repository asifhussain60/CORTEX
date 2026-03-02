# CORTEX Agents

**Updated:** 2026-02-27 | ---

## Structure

```
agents/
├── agent-index.md                  # Lazy-loading registry (load FIRST)
├── README.md                       # This file
├── core/                           # Production agents
│   ├── cortex.md                  # Master orchestrator
│   ├── cortex-architect.md        # Mode router + challenge enforcer
│   ├── cortex-holistic-validator.md # Pre-implementation gate
│   ├── cortex-auditor.md          # Codebase health scanning
│   ├── cortex-executor.md         # Code execution + TDD
│   ├── cortex-interactive.md      # Conversational mode
│   ├── cortex-digest.md           # Learning extraction
│   ├── cortex-environment-setup.md # Environment validation
│   ├── cortex-meta-auditor.md     # Meta governance auditing
│   ├── cortex-master-plan-auditor.md # Plan integrity
│   ├── cortex-documentation-architect.md # Doc architecture
│   ├── cortex-storyteller.md      # Narrative generation
│   ├── cortex-phase-resolver.md   # Phase management
│   ├── cortex-gitpages-builder.md # GitHub Pages deployment
│   ├── request-rephrase-orchestrator.md # Request optimization
│   └── architecture-integrity-agent.md # Wiring enforcement
├── certification/                  # Total Recall — Production Certification
│   ├── cortex-certification-coordinator.md # Pipeline orchestrator
│   ├── cortex-audit-agent.md      # Delta analysis + drift detection (P1-2)
│   ├── cortex-regression-agent.md # Regression + dead code scan (P3)
│   ├── cortex-refactor-agent.md   # Prompt optimization + intel wiring (P4-5)
│   ├── cortex-memory-agent.md     # Adaptive learning + lifecycle (P6)
│   ├── cortex-db-agent.md         # SQLite integrity + migrations (P7)
│   └── cortex-certification-agent.md # Hardening + scoring + sign-off (P8-9)
├── orchestration/                  # Cross-agent orchestration
│   └── cortex-universal-orchestration.md
├── education/                      # Educational agents
│   ├── cortex-ask-coordinator.md
│   └── truth-verifier.md
└── support/                        # Support utilities
```

---

## Active Agents

| Agent | Purpose | Load When |
|-------|---------|-----------|
| **cortex.md** | Master orchestrator — routes all requests | Any production request |
| **cortex-architect.md** | Mode router + production readiness | Architecture, audit, design |
| **cortex-holistic-validator.md** | Pre-implementation validation | IMPLEMENT/FIX/REFACTOR |
| **cortex-auditor.md** | P0-P3 health scanning | `/audit` |
| **cortex-executor.md** | TDD execution | Tests, implementation |
| **cortex-interactive.md** | Conversational Q&A | Questions, exploration |
| **cortex-digest.md** | Chat session learning | Processing chat files |
| **cortex-environment-setup.md** | Python/MCP validation | Pre-flight, setup |
| **cortex-meta-auditor.md** | Governance coherence | Meta-level audits |

---

## Intent → Mode → Agent

| Intent | Agent(s) |
|--------|----------|
| IMPLEMENT | cortex.md + cortex-holistic-validator.md + cortex-executor.md |
| FIX | cortex.md + cortex-holistic-validator.md + cortex-executor.md |
| REFACTOR | cortex.md + cortex-holistic-validator.md |
| AUDIT | cortex.md + cortex-architect.md + cortex-auditor.md |
| INVESTIGATE | cortex.md + cortex-architect.md |
| QUERY | cortex.md + cortex-interactive.md |
| DESIGN | cortex.md + cortex-architect.md |
| PLAN | cortex-architect.md + cortex-phase-resolver.md |
| DIGEST | cortex-architect.md + cortex-digest.md |
| REPHRASE | request-rephrase-orchestrator.md |
| SETUP | cortex-environment-setup.md |
| SYNC | cortex-sync-agent.md |
| VACUUM | cortex-vacuum.md |
| DEBUG | cortex-debugger.md |
| TOTAL RECALL | cortex-total-recall.prompt.md → certification/ agents |

---

## Architecture Reference

| Metric | Value |
|--------|-------|
| Orchestrators | 51 wired (`cortex/orchestrators/`) |
| MCP Tools | 29 registered (39 target) (`cortex/mcp/tools/`) |
| CORE Rules | 38 (`cortex-registry/core/tier0-skull/`) |
| Package | `cortex` (single canonical) |
| Tests | 16,942 (486 golden, 177 phase) |

---

## Related

| Resource | Purpose |
|----------|---------|
| `agent-index.md` | Lazy-loading registry (SSOT) |
| `../prompts/cortex-architect.prompt.md` | Expanded execution modes |
| `../prompts/cortex.prompt.md` | Master orchestrator prompt |
| `../templates/cortex-response-templates.md` | Response formatting |

---

