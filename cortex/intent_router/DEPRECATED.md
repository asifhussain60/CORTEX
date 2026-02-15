# DEPRECATED: Enhanced IntentRouter (Phase 81)

**Status:** DEPRECATED as of Phase 25 S2  
**Date:** 2026-02-15  
**Reason:** Consolidation to single IntentRouter implementation (CORE-035)

## Background

This directory contained `EnhancedIntentRouter` from Phase 81 S3 - an experimental
capability-based routing system with multi-agent collaboration features.

## Migration Path

Use the production `IntentRouter` from `cortex.orchestrators.core.intent_router`:

```python
# OLD (Phase 81 - DEPRECATED)
from cortex.intent_router.router import EnhancedIntentRouter, IntentRoutingRequest

# NEW (Production)
from cortex.orchestrators.core.intent_router import IntentRouter, RoutingDecision
```

## Affected Code

- `tests/integration/intent_router/test_mode_routing_integration.py`
- `tests/integration/health_checks/test_health_endpoints.py`
- `tests/unit/intent_router/test_routing_integration.py`
- `tests/performance/test_routing_performance.py`
- `tests/performance/test_load_testing.py`
- `cortex/health_check_service.py`

## Phase 81 Features (Archived)

The experimental features from Phase 81 have been noted for future integration:
- Capability-based agent selection
- Multi-agent collaboration orchestration
- Shared context optimization (LENS cache reuse)
- Dynamic collaboration pattern selection

These may be integrated into the production IntentRouter in a future phase
after Phase 25 stabilization is complete.

## Removal Timeline

- Phase 25 S2: Mark as deprecated (this file)
- Phase 26+: Remove files after all imports migrated

## Reference

- Phase 81: `cortex-registry/_cortex-master/phases/consolidated/81-*.yaml`
- Phase 25: `cortex-registry/_cortex-master/phases/active/phase-25-*.yaml`
- CORE-035: Single canonical implementation rule
