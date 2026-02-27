# Security-First Architecture — Shift-Left Security Layers
# Five-layer security architecture with gates at every SDLC phase

```
 ═══════════════════════════════════════════════════════════════════════════════
  CORTEX SECURITY ARCHITECTURE — 5 LAYERS
 ═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  LAYER 5: RELEASE GATE                                                 │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │  sdlc/release-readiness.yaml                                     │  │
  │  │  Security checklist · Secret rotation · Deployment validation    │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  │                                                                         │
  │  LAYER 4: EXECUTION VALIDATION                                         │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │  SecurityVulnerabilityOrchestrator                                │  │
  │  │  SAST scanning · CVE detection · OWASP Top 10 · Threat modeling  │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  │                                                                         │
  │  LAYER 3: LENS ANALYSIS                                                │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │  Security Analyzer (parallel with 14 other analyzers)            │  │
  │  │  Vulnerability patterns · Credential detection · Dependency scan │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  │                                                                         │
  │  LAYER 2: GOVERNANCE RULES                                             │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │  CORE-013 (error handling) · CORE-058 (SQLite WAL)               │  │
  │  │  SecurityCheckpointAgent in 10-agent enforcement chain           │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  │                                                                         │
  │  LAYER 1: PRE-COMMIT GATE                                              │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │  SanitizationOrchestrator                                        │  │
  │  │  Secret scanning · PII removal · Branch hygiene                  │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  SECURITY THROUGHOUT SDLC — Gate at Every Phase
 ═══════════════════════════════════════════════════════════════════════════════

  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │REQUIRE-  │  │  DESIGN  │  │ IMPLEMENT│  │  REVIEW  │  │ RELEASE  │
  │  MENTS   │  │          │  │          │  │          │  │          │
  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │              │              │              │              │
       ▼              ▼              ▼              ▼              ▼
  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
  │ Threat  │   │Security │   │  SAST   │   │   CVE   │   │ Release │
  │ Surface │   │by-Design│   │  Scan   │   │  Scan   │   │Security │
  │  ID     │   │Patterns │   │Cred Scan│   │PII Check│   │Checklist│
  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
       │              │              │              │              │
       ▼              ▼              ▼              ▼              ▼
  security-     security-     Security     Sanitization  release-
  by-design     by-design     Vulnerability Orchestrator readiness
  .yaml         .yaml         Orchestrator               .yaml


 ═══════════════════════════════════════════════════════════════════════════════
  RESILIENCE INFRASTRUCTURE
 ═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
  │ CIRCUIT BREAKER │   │    BULKHEAD     │   │    GRACEFUL     │
  │                 │   │                 │   │  DEGRADATION    │
  │ Closed ──▶ Open │   │ Partition       │   │ Return partial  │
  │   ▲         │   │   │ resources to    │   │ results when    │
  │   │    Half-Open│   │ prevent cascade │   │ non-critical    │
  │   └────────┘    │   │ failures        │   │ services fail   │
  └─────────────────┘   └─────────────────┘   └─────────────────┘

  ┌─────────────────┐   ┌─────────────────┐
  │  AUDIT HASH     │   │   EVIDENCE      │
  │    CHAIN        │   │    BUNDLE       │
  │                 │   │                 │
  │ Tamper-evident  │   │ Compliance      │
  │ cryptographic   │   │ proof packaging │
  │ linking of all  │   │ for audit       │
  │ audit entries   │   │ trail export    │
  └─────────────────┘   └─────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  SECURITY KNOWLEDGE SOURCES
 ═══════════════════════════════════════════════════════════════════════════════

  cortex-registry/
  ├── knowledge-base/security/
  │   ├── owasp-top10.yaml          ← OWASP Top 10 vulnerabilities
  │   ├── secrets-patterns.yaml     ← Credential detection regex
  │   └── cicd-hardening.yaml       ← Pipeline security
  └── knowledge/
      ├── security/
      │   └── secure-coding-practices.yaml
      └── sdlc/
          └── security-by-design.yaml
```

**Source:** `cortex/orchestrators/validation/security_vulnerability_orchestrator.py` · `cortex/orchestrators/git/sanitization_orchestrator.py`
**Governance:** CORE-013 (Error Handling), CORE-058 (SQLite WAL Mode)
