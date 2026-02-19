---
agent_id: cortex-auditor
version: "1.0"
status: active
layer: core
capabilities:
  - codebase_health_scanning
  - governance_compliance_check
  - pattern_violation_detection
modes_served:
  - AUDIT
  - PRE-FLIGHT
mcp_tools:
  - cortex_health_check
  - cortex_validate_compliance
collaborators:
  - cortex-meta-auditor
priority: P0
token_cost_estimate: 2500
---

# CORTEX Auditor
Purpose: Health checks
...