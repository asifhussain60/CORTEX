# Compliance Mappings

Map CORTEX capabilities to regulatory requirements.

## GDPR (General Data Protection Regulation)

| GDPR Article | CORTEX Feature | Implementation |
|---|---|---|
| Right to Access | Audit Trail API | All user actions logged and retrievable |
| Right to Erasure | Data Deletion API | Remove PII with automated cleanup |
| Data Minimization | Context Scoping | Only retrieve necessary knowledge |
| Consent Management | Request Validation | Enforce consent rules in Tier 0 governance |
| Privacy by Design | Encryption | All data encrypted at rest and in transit |

## HIPAA (Health Insurance Portability and Accountability Act)

| HIPAA Rule | CORTEX Feature | Implementation |
|---|---|---|
| Access Control | Tier-based Governance | Role-based access enforcement |
| Audit Controls | Audit Trail | 100% of access logged immutably |
| Integrity Controls | Transaction ACID | Atomic, consistent healthcare data |
| Transmission Security | Encryption | TLS for REST, encrypted knowledge storage |
| Minimum Necessary | Knowledge Scoping | Query constraints limit data exposure |

## SOC 2 (Service Organization Control)

| Control | CORTEX Feature | Implementation |
|---|---|---|
| CC6.1 Data Confidentiality | Encryption | All sensitive data encrypted |
| A1.1 COSO Framework | Governance Model | CORTEX Tier 0-3 enforces controls |
| C1 Availability | Resilience Patterns | Circuit breakers, retry, partial failure |
| C2 Processing Integrity | Transaction Model | ACID guarantees data consistency |
| CC7 Monitoring | Audit Trail | Continuous logging and analysis |

---

See [Architecture](../02-architecture/1-system-overview.md) for detailed security implementation.
