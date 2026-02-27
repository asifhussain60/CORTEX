# cortex/core Architecture — 15 Canonical Subdirs

---
title: CORTEX Core Architecture — Phase 68 Flatten (27→15 Canonical Subdirs)
type: reference
audience: [Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/core/ + cortex/core/common/
phase: Phase 68 (COMPLETE — SWEEP-68-CORE-FLATTEN)
order: 12
---

> **What changed:** Phase 68 flattened `cortex/core/` from 27 subdirectories to **15 canonical subdirs** — eliminating redundant nesting, consolidating 8 dirs into `cortex/core/common/`, and deleting all zero-caller compat shims.

---

## Before and After

| Before (27 subdirs) | After (15 canonical subdirs) | Status |
|--------------------|------------------------------|--------|
| `bootstrap/` | *(deleted — zero callers)* | 🗑️ Deleted |
| `config/timeout_profiles/` | `common/timeout_profiles.py` | ✅ Moved |
| `core/intelligence/` | `cortex/intelligence/` | ✅ Moved to canonical |
| `core/intent/` | `cortex/orchestrators/core/intent_router/` | ✅ Moved |
| `core/interaction/` | `cortex/orchestrators/core/` | ✅ Moved |
| `core/orchestrator/` | `cortex/orchestrators/core/` | ✅ Moved |
| Various nested helpers | `common/` (single flat dir) | ✅ Consolidated |

---

## The 15 Canonical Subdirs

```
cortex/core/
├── common/              ← Phase 68: Consolidated 8 dirs into here
│   ├── connection_utils.py
│   ├── core_progress_reporter.py
│   ├── debug_logger.py
│   ├── exceptions.py
│   ├── file_operations/
│   ├── file_utils.py
│   ├── governance_decorator.py
│   ├── optimistic_lock.py
│   ├── orchestrator_decorator.py
│   ├── orphan_cleaner.py
│   ├── output_validator.py
│   ├── phase_state_machine.py
│   ├── platform_output.py
│   ├── saga_coordinator.py
│   ├── standards_resolver.py
│   ├── state_repair.py
│   ├── structured_error.py
│   ├── thread_safety.py
│   ├── timeout_profiles.py
│   └── validators.py
├── discovery/           ← Repository/file discovery models
├── execution/           ← Execution gateway, guards
├── governance/          ← Governance enforcer, database, models
├── hallucination_prevention/  ← HP output validator
├── intelligence/        ← Intelligence mixin, routing engine (thin — most moved to cortex/intelligence/)
├── intent/              ← Intent models (thin — IntentRouter moved to orchestrators/)
├── interaction/         ← Interaction models (thin — moved to orchestrators/)
├── interfaces/          ← IOrchestrator protocol, OperationMode
├── knowledge/           ← Knowledge guidance engine
├── models/              ← Shared data models
├── orchestrator/        ← OrchestratorBase (legacy — 2 orchestrators only)
├── registry/            ← Feature registry
├── security/            ← Security models
└── wiring/              ← Wiring contracts, specifications
```

---

## What Moved to `cortex/core/common/`

Eight directories that contained thin utility modules were consolidated into `common/`:

| Old path | New path |
|---------|---------|
| `cortex/core/config/timeout_profiles/` | `cortex/core/common/timeout_profiles.py` |
| `cortex/core/utils/` | `cortex/core/common/` (various files) |
| `cortex/core/platform/` | `cortex/core/common/platform_output.py` |
| `cortex/core/threading/` | `cortex/core/common/thread_safety.py` |
| `cortex/core/errors/` | `cortex/core/common/structured_error.py` + `exceptions.py` |
| `cortex/core/decorators/` | `cortex/core/common/governance_decorator.py` + `orchestrator_decorator.py` |
| `cortex/core/state/` | `cortex/core/common/state_repair.py` |
| `cortex/core/saga/` | `cortex/core/common/saga_coordinator.py` |

---

## Import Compatibility

All import paths that existed before Phase 68 continue to work via a **compatibility layer** (`cortex/core/compatibility_layer.py`). No external code changes required.

```python
# These still work (compat shims):
from cortex.core.config import timeout_profiles  # → common/timeout_profiles.py
from cortex.core.utils import file_utils         # → common/file_utils.py

# Preferred new-style imports:
from cortex.core.common.timeout_profiles import TimeoutProfiles
from cortex.core.common.file_utils import safe_read_file
```

---

## OrchestratorBase vs OrchestratorProtocolMixin

Phase 68 confirms the canonical base for all 51 wired orchestrators is **`OrchestratorProtocolMixin`** (Phase 58), not `OrchestratorBase`:

| Base | Location | Used By |
|------|----------|---------|
| `OrchestratorProtocolMixin` | `cortex/core/orchestrator_protocol_mixin.py` | All 51 wired orchestrators (canonical) |
| `OrchestratorBase` | `cortex/core/orchestrator_base.py` | 2 legacy orchestrators only |

`OrchestratorBase` is preserved in `cortex/core/orchestrator/` for backward compatibility but should not be used in new orchestrators.

---

## Why This Matters

1. **Import clarity** — `from cortex.core.common.validators import ...` is unambiguous. No more hunting through 27 dirs.
2. **Reduced confusion** — `cortex/core/intelligence/` → `cortex/intelligence/` removes the duplicate path ambiguity that caused Phase 60 import errors.
3. **Smaller surface** — 15 canonical dirs are auditable. 27 dirs were not.
4. **Bootstrap deleted** — The `cortex/core/bootstrap/` compat shim was the last remnant of pre-Phase-55 init sequences. Deleted in Phase 68 final commit.

---

*Phase 68 COMPLETE — SWEEP-68-CORE-FLATTEN exhausted · All callers verified · Bootstrap/ shim deleted · Verified 2026-02-25*
