# cortex/core Architecture — Canonical Subdirs

---
title: CORTEX Core Architecture — Canonical Subdirectory Layout
type: reference
audience: [Software Developers]
last_verified: 2026-02-28
source_of_truth: cortex/core/ + cortex/core/common/
order: 12
---

> **What changed:** `cortex/core/` was flattened into **canonical subdirs** — eliminating redundant nesting, consolidating dissolved packages into `cortex/core/common/`, and deleting all zero-caller compat shims.

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

## The Canonical Subdirs

```
cortex/core/
├── common/              ← Consolidated from dissolved packages
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

All legacy import paths continue to work via a **compatibility layer** (`cortex/core/compatibility_layer.py`). No external code changes required.

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

The canonical base for all wired orchestrators is **`OrchestratorProtocolMixin`**, not `OrchestratorBase`:

| Base | Location | Used By |
|------|----------|---------|
| `OrchestratorProtocolMixin` | `cortex/core/orchestrator_protocol_mixin.py` | All wired orchestrators (canonical) |
| `OrchestratorBase` | `cortex/core/orchestrator_base.py` | Legacy orchestrators only |

`OrchestratorBase` is preserved in `cortex/core/orchestrator/` for backward compatibility but should not be used in new orchestrators.

---

## Why This Matters

1. **Import clarity** — `from cortex.core.common.validators import ...` is unambiguous. No more hunting through deeply nested dirs.
2. **Reduced confusion** — `cortex/core/intelligence/` → `cortex/intelligence/` removes duplicate path ambiguity.
3. **Smaller surface** — fewer canonical dirs are auditable; a sprawling directory tree is not.
4. **Bootstrap deleted** — The `cortex/core/bootstrap/` compat shim has been removed. All init sequences use the canonical path.

---

*Verified against `cortex/core/` directory structure*
