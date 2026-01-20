# Governance Rules Reference

**Complete 29 SKULL Rules**  
**Version:** 1.0.0

---

## SKULL Framework Rules (Tier 0 - Immutable)

All 29 CORE rules from `cortex_brain/tier0/governance/core-rules.yaml`:

### Circuit Breaker Rules (CORE-001 to CORE-002)
- **CORE-001:** Automatic failure detection with timeout
- **CORE-002:** Circuit breaker transition logic (closed/open/half-open)

### State & Concurrency (CORE-003 to CORE-010)
- **CORE-003:** Transactional state semantics
- **CORE-004:** Optimistic concurrency control
- **CORE-005:** Lock-free registry semantics
- **CORE-006:** Race condition prevention
- **CORE-007:** Deadlock detection and recovery
- **CORE-008:** Orphan state cleanup
- **CORE-009:** State snapshot interval
- **CORE-010:** Rollback completeness

### Observability (CORE-011 to CORE-015)
- **CORE-011:** JSON structured logging mandatory
- **CORE-012:** Prometheus metrics exposition
- **CORE-013:** Distributed tracing (OpenTelemetry)
- **CORE-014:** Health check endpoints (liveness/readiness)
- **CORE-015:** Audit trail immutability

### Security (CORE-016 to CORE-029)
- **CORE-016:** TLS mandatory for API
- **CORE-017:** API authentication required
- **CORE-018:** Role-based authorization
- **CORE-019:** Secret encryption at rest
- **CORE-020:** Credential rotation policy
- **CORE-021:** Audit logging of all decisions
- **CORE-022:** GDPR deletion capability
- **CORE-023:** HIPAA compliance requirements
- **CORE-024:** SOC 2 logging requirements
- **CORE-025:** Zero-trust architecture
- **CORE-026:** Input validation mandatory
- **CORE-027:** Output sanitization
- **CORE-028:** Rate limiting per API key
- **CORE-029:** DDoS protection enabled

---

## Rule Application

Rules apply at all tiers:
- **Tier 0:** Rules are immutable, enforced globally
- **Tier 1:** Domain rules must respect tier0 rules
- **Tier 2:** Environment rules must respect tier0+tier1

---

## Related Documentation

- [Multi-Tier Architecture](2-multi-tier-architecture.md)
- [Security & Governance](6-security-governance.md)

