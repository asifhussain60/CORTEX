# Governance Flow

---
title: Governance Enforcement Flow Diagram
type: diagram
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-28
source_of_truth: cortex/governance/ + cortex-registry/core/
order: 6
---

## Rule Enforcement Lifecycle

```
                    CODE CHANGE
                         │
                         ▼
┌────────────────────────────────────────────────┐
│  LAYER 1: PRE-COMMIT                           │
│                                                │
│  pre_commit_validator.py                       │
│  ┌──────────────────────────────────────────┐  │
│  │ CORE-011: Type hints present?            │  │
│  │ CORE-012: Docstrings on public APIs?     │  │
│  │ CORE-028: File names snake_case?         │  │
│  │ CORE-035: No duplicate implementations?  │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ❌ Fail → Block commit                        │
│  ✅ Pass → Continue                            │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────┐
│  LAYER 2: CI PIPELINE                          │
│                                                │
│  EnforcementOrchestrator                       │
│  ┌──────────────────────────────────────────┐  │
│  │ All active CORE rules evaluated            │  │
│  │ Enforcement agents execute                 │  │
│  │                                          │  │
│  │ Agents:                                  │  │
│  │ ├── TestNamingAgent                      │  │
│  │ ├── FileNamingAgent                      │  │
│  │ ├── ImportValidationAgent                │  │
│  │ ├── TypeHintAgent                        │  │
│  │ ├── DocstringAgent                       │  │
│  │ ├── DuplicateDetectionAgent              │  │
│  │ ├── SecurityScanAgent                    │  │
│  │ └── ExtendedGovernanceAgent              │  │
│  │      (CORE-058 through CORE-063)         │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ❌ Fail → Block merge                         │
│  ✅ Pass → Continue                            │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────┐
│  LAYER 3: RUNTIME                              │
│                                                │
│  MasterOrchestrator Stage 4                    │
│  ┌──────────────────────────────────────────┐  │
│  │ CORE-002: Output inline (no .md files)   │  │
│  │ CORE-008: TDD enforced (test first)      │  │
│  │ CORE-048: Holistic validation gate       │  │
│  │ CORE-049: Silent autonomous execution    │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  All violations → CortexAuditDB                │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────┐
│  AUDIT TRAIL                                   │
│                                                │
│  CortexAuditDB (SQLite WAL)                    │
│  ┌──────────────────────────────────────────┐  │
│  │ • Timestamp                              │  │
│  │ • Rule ID (CORE-nnn)                     │  │
│  │ • Violation type                         │  │
│  │ • File path                              │  │
│  │ • Remediation applied                    │  │
│  │ • Hash chain (tamper-evident)            │  │
│  └──────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

## 17 Active CORE Rules

```
┌─────────┬──────────────────────────────────────────────┐
│ Rule    │ Enforcement                                  │
├─────────┼──────────────────────────────────────────────┤
│ CORE-001│ Standard project structure                   │
│ CORE-002│ All output inline — no report files          │
│ CORE-005│ Conventional commit messages                 │
│ CORE-008│ TDD mandatory — test first                   │
│ CORE-011│ Type hints on all functions                  │
│ CORE-012│ Docstrings on all public APIs                │
│ CORE-013│ Error handling standards                     │
│ CORE-028│ File naming: snake_case only                 │
│ CORE-035│ Single canonical — no duplicates             │
│ CORE-048│ Holistic validation gate                     │
│ CORE-049│ Silent autonomous execution                  │
│ CORE-058│ Extended governance (ExtendedGovernanceAgent) │
│ CORE-059│ Extended governance                          │
│ CORE-060│ Extended governance                          │
│ CORE-061│ Extended governance                          │
│ CORE-062│ Extended governance                          │
│ CORE-063│ Extended governance                          │
│         │ + additional rules in skull-rules.yaml       │
└─────────┴──────────────────────────────────────────────┘
```

---

*Verified against `cortex-registry/core/tier0-skull/skull-rules.yaml`*
