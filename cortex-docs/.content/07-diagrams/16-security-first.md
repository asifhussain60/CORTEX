# Security-First Architecture Diagram

---
title: Security-First — 5-Layer Defence Architecture
type: diagram
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-28
source_of_truth: cortex/infrastructure/, cortex/governance/
order: 16
---

> The 5-layer security architecture ensuring security is embedded at every stage.

## 5-Layer Security Model

```
  Layer 5: RUNTIME PROTECTION
  ┌───────────────────────────────────────────────────────────┐
  │  Circuit breakers · Rate limiting · Graceful degradation  │
  │  cortex/infrastructure/circuit_breaker.py                 │
  └───────────────────────────────────────────────────────────┘

  Layer 4: AUDIT & COMPLIANCE
  ┌───────────────────────────────────────────────────────────┐
  │  SQLite WAL audit DB · Hash chain · Evidence bundles      │
  │  cortex/infrastructure/audit_db.py                        │
  └───────────────────────────────────────────────────────────┘

  Layer 3: GOVERNANCE ENFORCEMENT
  ┌───────────────────────────────────────────────────────────┐
  │  CORE rules · Pre-commit · CI · Runtime validation                │
  │  cortex/governance/ + cortex-registry/core/               │
  └───────────────────────────────────────────────────────────┘

  Layer 2: CODE ANALYSIS
  ┌───────────────────────────────────────────────────────────┐
  │  LENS security analyzer · Secret scanning · Import audit  │
  │  cortex/lens/ + cortex/secrets/                           │
  └───────────────────────────────────────────────────────────┘

  Layer 1: INPUT VALIDATION
  ┌───────────────────────────────────────────────────────────┐
  │  Request sanitization · PII redaction · Schema validation │
  │  cortex/infrastructure/security/                          │
  └───────────────────────────────────────────────────────────┘

  Security gates at every SDLC phase transition
```

**Detailed diagram:** `flat-files/diagrams/diagram-21-security-first.md`
**Full documentation:** `flat-files/20-security-first.md`

---

*Source: `cortex/infrastructure/` · `cortex/governance/` · `cortex-registry/knowledge-base/security/`*
