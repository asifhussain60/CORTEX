# Deprecated v3.8.1 Components

**Archive Date:** December 14, 2025  
**Reason:** Replaced by Planning System 3.0 components

## Contents

### system_maintenance_orchestrator_v3.8.1.py
- **Original Location:** `src/operations/modules/orchestration/system_maintenance_orchestrator.py`
- **Replaced By:** `src/operations/modules/orchestration/maintenance_orchestrator_v3.py`
- **Deprecation Reason:** Upgraded to Planning System 3.0 with tiered routing
- **Key Differences:**
  - v3.8.1: 6-phase maintenance cycle (no vacuum)
  - v3.0: 7-phase maintenance cycle with vacuum + tiered routing
  - v3.8.1: Fixed execution path
  - v3.0: Intelligent tier classification (1-4 tiers)
  - v3.8.1: No version management
  - v3.0: Centralized version from cortex.config.json

### Migration Guide

**For Code References:**
```python
# OLD (v3.8.1)
from src.operations.modules.orchestration.system_maintenance_orchestrator import SystemMaintenanceOrchestrator

# NEW (v3.0)
from src.operations.modules.orchestration.maintenance_orchestrator_v3 import MaintenanceOrchestratorV3
```

**For cortex-operations.yaml:**
```yaml
# OLD
modules:
  - system_maintenance_orchestrator

# NEW
modules:
  - maintenance_orchestrator_v3
```

**Backward Compatibility:**
- cortex-operations.yaml automatically uses v3.0
- Old CLI commands still work (routed to v3.0)
- No user-facing breaking changes

### Test Results (Pre-Deprecation)
- Last test run: 2024-12-14 08:50 AM
- Status: All passing
- Reason for archival: Not breaking, just superseded

### Restoration Instructions
If needed for rollback:
1. Copy file back to `src/operations/modules/orchestration/`
2. Update `cortex-operations.yaml` to use `system_maintenance_orchestrator`
3. Revert `.github/prompts/CORTEX.prompt.md` version to 3.8.1

**Archival Authority:** Asif Hussain  
**Related Documentation:** `cortex-brain/documents/planning/completed/cortex-evolution-v3.9/phase-06-maintenance.md`
