# CORTEX Agents

**Version:** 11.0 | **Updated:** 2026-02-20 | **Post-Refactor:** v2.0.0-cohesive-brain

---

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

---

## Architecture Reference

| Metric | Value |
|--------|-------|
| Orchestrators | 52 canonical (`cortex/orchestrators/`) |
| MCP Tools | 23 (`cortex/mcp/tools/`) |
| CORE Rules | 17 (`cortex-registry/core/`) |
| Package | `cortex` (single canonical) |
| Tests | 15,230 (486 golden, 177 phase) |

---

## Related

| Resource | Purpose |
|----------|---------|
| `agent-index.md` | Lazy-loading registry (SSOT) |
| `../prompts/cortex-architect.prompt.md` | Expanded execution modes |
| `../prompts/cortex.prompt.md` | Master orchestrator prompt |
| `../templates/cortex-response-templates.md` | Response formatting |

---

*v11.0 — Post-refactor v2.0.0-cohesive-brain. 52 orchestrators, 23 MCP tools, 1 package.*
