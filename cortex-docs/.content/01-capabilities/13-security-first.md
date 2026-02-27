# Security-First Development

---
title: Security-First — 5-Layer Defence Architecture
type: capability
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-27
source_of_truth: cortex/infrastructure/, cortex/governance/
order: 13
---

> Security in CORTEX is not a phase — it's embedded at every layer, every SDLC phase, and every orchestrator invocation.

---

## 5-Layer Security Architecture

| Layer | Purpose | Key Components |
|-------|---------|----------------|
| **5. Runtime** | Protection during execution | Circuit breakers, rate limiting, graceful degradation |
| **4. Audit** | Compliance and traceability | SQLite WAL audit DB, hash chain, evidence bundles |
| **3. Governance** | Rule enforcement | 38 CORE rules, pre-commit + CI + runtime validation |
| **2. Analysis** | Code-level security | LENS security analyzer, secret scanning, import audit |
| **1. Input** | Request sanitization | PII redaction, schema validation, input filtering |

---

## Shift-Left Security

Security checks run at every SDLC phase transition, not just before deployment:

- **Requirements:** Threat model review, security acceptance criteria
- **Design:** Attack surface analysis, secure pattern selection
- **Implementation:** SAST via LENS, secret scanning, dependency audit
- **Testing:** Security-focused test generation, fuzz testing templates
- **Review:** Security checklist enforcement, vulnerability re-scan
- **Deployment:** Canary with security monitoring, rollback triggers

---

**Full documentation:** `flat-files/20-security-first.md`
**Diagram:** `07-diagrams/16-security-first.md`
