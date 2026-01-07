# CORTEX Architecture Quick Reference

**Version:** 5.0.0 | **Date:** 2026-01-03  
**Purpose:** High-level architecture overview (externalized from CORTEX.prompt.md)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CORTEX Brain (4 Tiers)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tier 0: Governance (brain-protection-rules.yaml - 61 rules)│
│          ↓                                                  │
│  Tier 1: Working Memory (conversation-context.jsonl)       │
│          ↓                                                  │
│  Tier 2: Knowledge Graph (knowledge-graph.yaml)            │
│          ↓                                                  │
│  Tier 3: Development Context (lessons-learned.yaml)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Master Orchestrator v7                      │
│                                                             │
│  User Input → Context Middleware → Pattern Router          │
│                         ↓                                   │
│  Orchestrator Registry (10 registered)                     │
│           ↓                              ↓                  │
│   🛡️ AUTONOMOUS (5)             📋 GUIDED (5)            │
│   - Planning v5                 - TDD v4                   │
│   - ADO v2                      - Sanitization v2          │
│   - Vacuum v2                   - Debug                    │
│   - Cleanup v2                  - Refinement v2            │
│   - Investigation v2            - Maintenance v2           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator Layer                         │
│                                                             │
│  🛡️ AUTONOMOUS: Python implementation → Progress tracking │
│  📋 GUIDED: Manifest → Copilot interprets → Execute       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Output Layer                              │
│                                                             │
│  - Planning folders (context/, artifacts/, reports/, tracking/) │
│  - ADO work items (JSON)                                    │
│  - Cleanup/Vacuum reports                                   │
│  - Investigation reports                                    │
│  - Code changes (TDD, Sanitization, Debug, Refinement)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Directory Structure

```
CORTEX/
├── .github/
│   └── prompts/
│       ├── CORTEX.prompt.md              # 🆕 Lean v5 (127 lines, machine-readable)
│       ├── CORTEX.prompt.md.v4.backup    # 🆕 Backup (507 lines)
│       └── maintenance/                   # Maintenance orchestrator
│
├── cortex-brain/
│   ├── tier0/                             # Governance rules
│   ├── tier1/                             # Working memory (session context)
│   ├── tier2/                             # Knowledge graph
│   ├── tier3/                             # Development context
│   ├── config/
│   │   └── master-orchestrator.yaml       # Master Orch routing config
│   ├── manifests/orchestrators/           # Orchestrator manifests (46 files)
│   ├── documents/
│   │   ├── orchestrators-quick-ref.md     # 🆕 Orchestrator documentation
│   │   ├── cortex-architecture-quick-ref.md # 🆕 This file
│   │   ├── cortex-protocol-examples.md    # 🆕 Learning examples (NOT in prompt)
│   │   ├── reports/                       # Generated reports
│   │   ├── analysis/                      # Analysis documents
│   │   ├── planning/active/               # Active plans
│   │   └── ...
│   └── response-templates-v4.yaml         # Response format templates
│
├── src/
│   ├── orchestrators/
│   │   ├── master_orchestrator.py         # Master routing layer
│   │   ├── pattern_router.py              # Pattern matching engine
│   │   ├── state_manager.py               # Cross-orchestrator state
│   │   ├── execution_engine.py            # Orchestrator lifecycle
│   │   ├── planning/                      # Planning v5 implementation
│   │   ├── ado/                           # ADO v2 implementation
│   │   ├── vacuum/                        # Vacuum v2 implementation
│   │   └── cleanup/                       # Cleanup v2 implementation
│   ├── cortex_agents/                     # Agent layer
│   ├── database/                          # PlanningStateDB
│   └── mcp/                               # MCP tool integration
│
└── tests/                                 # Test suite
```

---

## 🔀 Request Flow

### AUTONOMOUS Orchestrator (🛡️)

```
1. User: "plan user authentication"
        ↓
2. Parse Request (remove meta-directives)
        ↓
3. Pattern Router: Match `^(plan|create a plan).*$`
        ↓
4. Master Orchestrator: Load PlanningOrchestratorV5
        ↓
5. GitHub Copilot: Display progress header
        ↓
6. Python: Execute planning workflow autonomously
        ↓
7. GitHub Copilot: Update progress bars (live)
        ↓
8. Output: Plan folder structure created
```

### GUIDED Orchestrator (📋)

```
1. User: "tdd my_module.py"
        ↓
2. Parse Request (remove meta-directives)
        ↓
3. Pattern Router: Match `^(tdd|start tdd).*$`
        ↓
4. Master Orchestrator: Load tdd-orchestrator-v4-manifest.yaml
        ↓
5. GitHub Copilot: Read manifest → Interpret instructions
        ↓
6. GitHub Copilot: Execute TDD workflow (RED→GREEN→REFACTOR)
        ↓
7. Output: Tests + implementation created
```

---

## 🛡️ Brain Protection (SKULL)

**61 Rules across 6 categories:**

| Category | Rules | Purpose |
|----------|-------|---------|
| **TDD_ENFORCEMENT** | 12 | Enforce test-first development |
| **HOLISTIC_DISCOVERY** | 8 | Search before creating (prevent duplication) |
| **REFACTOR_CLEANUP** | 10 | Remove orphaned/duplicate code |
| **GIT_ISOLATION** | 9 | Separate CORTEX code from user repos |
| **PLANNING_ISOLATION** | 14 | Planning commands create plans, never implement |
| **HAND_OFF_PROTOCOL** | 8 | 🛡️ AUTONOMOUS orchestrators execute independently |

**Full rules:** `cortex-brain/brain-protection-rules.yaml`

---

## 📋 Command Quick Reference

| Command | Type | Duration | Outputs |
|---------|------|----------|---------|
| `plan {feature}` | 🛡️ AUTONOMOUS | ~2h | Plan folder (4 subfolders) |
| `ado story {feature}` | 🛡️ AUTONOMOUS | ~2.5h | ADO work items (JSON) |
| `vacuum {path}` | 🛡️ AUTONOMOUS | ~5h | Cleanup reports |
| `cleanup {mode}` | 🛡️ AUTONOMOUS | ~1h | Cleanup logs |
| `investigate {issue}` | 🛡️ AUTONOMOUS | ~4h | Investigation report |
| `tdd {module}` | 📋 GUIDED | Variable | Tests + code |
| `sanitize {target}` | 📋 GUIDED | Variable | Sanitized files |
| `debug {error}` | 📋 GUIDED | Variable | Debug analysis |
| `refine {target}` | 📋 GUIDED | Variable | Refined code |
| `system maintenance` | 📋 GUIDED | ~3h | 12-phase report |

---

## 🚀 Evolution Timeline

| Version | Date | Changes |
|---------|------|---------|
| **v1.0** | 2024-Q1 | Initial CORTEX with 3 orchestrators |
| **v2.0** | 2024-Q2 | Agent layer + state management |
| **v3.0** | 2024-Q3 | Planning System v3 + 7 orchestrators |
| **v4.0** | 2025-Q4 | Planning v4 + response templates v4 |
| **v4.5** | 2026-01-02 | Cross-Session Context Middleware |
| **v5.0** | 2026-01-03 | 🆕 **Hybrid Ownership Model** (lean prompt + Master Orch) |

---

## 🔗 Related Documentation

- **Main Entry Point:** `.github/prompts/CORTEX.prompt.md` (v5.0 - 127 lines)
- **Orchestrators:** `cortex-brain/documents/orchestrators-quick-ref.md`
- **Response Templates:** `cortex-brain/response-templates-v4.yaml`
- **Brain Protection:** `cortex-brain/brain-protection-rules.yaml`
- **Master Orchestrator Config:** `cortex-brain/config/master-orchestrator.yaml`

---

**Last Updated:** 2026-01-03  
**Maintained By:** CORTEX Planning System v5
