# Audit & Compliance

**Status:** Production Ready | **Last Updated:** 2026-01-21

Audit trails and compliance management for governance requirements.

## Overview

CORTEX provides comprehensive audit logging and compliance mapping for regulatory requirements.

## Audit Logging

All decisions and actions are logged with:
- Timestamp
- User ID
- Action type
- Domain
- Result
- Tier applied

## Compliance Mappings

- **GDPR** - Data privacy and right to erasure
- **HIPAA** - Healthcare data protection
- **SOC2** - Security and availability controls
- **PCI-DSS** - Payment card security

## Implementation

```python
from cortex.governance.audit import AuditTrail

audit = AuditTrail()

# Log action
audit.log(
    action="ORCHESTRATOR_EXECUTE",
    user_id="user1",
    domain="payments",
    result="approved",
    metadata={"orchestrator": "payment_approval"}
)

# Generate compliance report
report = audit.generate_compliance_report(
    compliance_framework="GDPR",
    date_range=("2026-01-01", "2026-01-31")
)
```

## Related Resources

- [Governance Framework](../../02-architecture/6-security-governance.md)
- [Compliance Mappings](../../05-reference/compliance-mappings.md)
