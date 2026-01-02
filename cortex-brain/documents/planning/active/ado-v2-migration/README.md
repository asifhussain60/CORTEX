# ADO Orchestrator v2 Migration

**Plan ID:** ado-v2-migration  
**Status:** ⏸️ PENDING  
**Created:** January 2, 2026  
**Parent Plan:** cortex-v5-holistic-refactor (Phase 6.1)

---

## Overview

Migration of ADO Orchestrator from hybrid execution (v1) to pure autonomous architecture (v2) with integrated conversational wizard.

### Key Objectives

1. **Pure Autonomous Execution** - All logic in Python, zero natural language in manifest
2. **Dual-Mode Operation** - Auto-generation + conversational wizard
3. **Master Orchestrator Integration** - Pattern-based routing
4. **State Persistence** - Database-backed state tracking
5. **Template-Driven Outputs** - Jinja2 templates for all user-facing content

---

## Structure

```
ado-v2-migration/
├── 00-master-plan.md          # Complete migration plan (6 phases)
├── README.md                   # This file
├── context/                    # Analysis artifacts
│   ├── ado-v1-architecture.md
│   ├── conversational-wizard-design.md
│   └── hybrid-execution-analysis.md
├── artifacts/                  # Migration deliverables
│   └── migration-strategy.md
├── reports/                    # Phase completion reports
└── tracking/
    └── progress-tracker.json   # Progress metadata
```

---

## Quick Reference

**Duration:** 6 days  
**Phases:** 6 (Foundation → Core → Wizard → Config → Testing → Activation)  
**Progress:** 0% (Not started)

**Master Plan:** `00-master-plan.md`  
**Progress Tracker:** `tracking/progress-tracker.json`

---

## Key Deliverables

1. **ADOOrchestratorV2** - Pure Python implementation inheriting BaseOrchestrator v4.1
2. **Conversational Wizard Integration** - 7-stage interactive mode from Phase 5.1a
3. **Config-Only Manifest** - YAML with zero natural language
4. **Jinja2 Templates** - Work item preview, approval gates, wizard prompts
5. **100% Test Coverage** - Unit + integration tests
6. **Master Orchestrator Routing** - Pattern-based routing activated

---

## User Commands (Post-Migration)

**Auto Mode (Quick Generation):**
```
ado story user authentication
ado feature payment system
```

**Wizard Mode (Interactive):**
```
ado wizard user authentication
ado interactive payment system
```

---

## Related Documents

- Parent Plan: `cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/00-MASTER-PLAN-V5.md`
- Phase 5.1a Report: `cortex-v5-holistic-refactor/reports/phase-5-1a-completion.md`
- ADO v1 Implementation: `src/orchestrators/ado/ado_orchestrator.py`
- Conversational Wizard: `src/orchestrators/ado/ado_conversational_wizard.py`

---

**Next:** Execute Phase 0 (Foundation & Analysis) when parent plan Phase 5 completes
