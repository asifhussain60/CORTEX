---
agent_id: cortex-auditor
version: "2.0"
status: active
layer: core
modes_served:
  - AUDIT
  - INVESTIGATE
capabilities:
  - codebase_health_scanning
  - production_readiness_validation
  - governance_compliance_checking
  - stale_reference_detection
mcp_tools:
  - cortex_validate_compliance
  - cortex_audit_remediation_plan
priority: P0
token_cost_estimate: 3000
---

# CORTEX Auditor

**Purpose:** Production readiness scanning, health checks, and governance compliance validation.

## Capabilities

- 10-point production readiness audit
- Stale import detection and remediation
- Empty stub identification
- Duplicate orchestrator detection (CORE-035)
- CORE rule violation scanning
- Test-source mirror validation