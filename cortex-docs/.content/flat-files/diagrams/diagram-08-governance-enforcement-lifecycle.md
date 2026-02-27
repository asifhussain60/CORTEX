# Governance Rule Enforcement — Lifecycle Detail
# Shows how CORE rules flow through pre-commit, CI, and runtime gates

```
                         DEVELOPER MAKES CHANGE
                                  │
                                  ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │   PRE-COMMIT GATE (Local Machine)                                       │
  │   ─────────────────────────────────                                     │
  │                                                                         │
  │   pre_commit_validator.py                                               │
  │                                                                         │
  │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
  │   │ CORE-011    │ │ CORE-012    │ │ CORE-028    │ │ CORE-035    │      │
  │   │ Type hints  │ │ Docstrings  │ │ snake_case  │ │ No dupes    │      │
  │   │ on funcs    │ │ on public   │ │ file names  │ │ single impl │      │
  │   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘      │
  │          │               │               │               │              │
  │          └───────────────┴───────┬───────┴───────────────┘              │
  │                                  │                                      │
  │                          ┌───────┴───────┐                              │
  │                          │  ALL PASS?    │                              │
  │                          └───┬───────┬───┘                              │
  │                          YES │       │ NO                               │
  │                              │       │                                  │
  │                              │       └──→ ❌ COMMIT BLOCKED             │
  └──────────────────────────────┼──────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │   CI PIPELINE GATE (GitHub Actions / ADO)                               │
  │   ───────────────────────────────────────                               │
  │                                                                         │
  │   EnforcementOrchestrator + 10 Agents                                   │
  │                                                                         │
  │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
  │   │ TestNamingAgent │  │ FileNamingAgent │  │ ImportValidation│        │
  │   │ test_ prefix    │  │ snake_case      │  │ cortex.* only   │        │
  │   └─────────────────┘  └─────────────────┘  └─────────────────┘        │
  │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
  │   │ TypeHintAgent   │  │ DocstringAgent  │  │ DuplicateDetect │        │
  │   │ all signatures  │  │ public APIs     │  │ no duplicates   │        │
  │   └─────────────────┘  └─────────────────┘  └─────────────────┘        │
  │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
  │   │ SecurityScan    │  │ ExtendedGov.    │  │ ArchitectureInt │        │
  │   │ vuln detection  │  │ CORE-058–063    │  │ wiring contract │        │
  │   └─────────────────┘  └─────────────────┘  └─────────────────┘        │
  │   ┌─────────────────┐                                                   │
  │   │ SweepComplete   │                                                   │
  │   │ CORE-064        │                                                   │
  │   └─────────────────┘                                                   │
  │                                                                         │
  │   All 38 CORE rules evaluated across full codebase                      │
  │                                                                         │
  │   Result: PASS │ WARNING │ BLOCKED                                      │
  │   ❌ BLOCKED → Merge rejected                                           │
  └──────────────────────────────┬──────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │   RUNTIME GATE (MasterOrchestrator Stage 4)                             │
  │   ──────────────────────────────────────────                            │
  │                                                                         │
  │   Every orchestrator invocation:                                        │
  │   ┌─────────────────────────────────────────────────────────────┐       │
  │   │ AC_START: AC-{DOMAIN}-{TIMESTAMP}                          │       │
  │   │   │                                                         │       │
  │   │   ├── CORE-002 check: output inline only                   │       │
  │   │   ├── CORE-008 check: TDD enforced                        │       │
  │   │   ├── CORE-048 check: holistic validation gate             │       │
  │   │   ├── CORE-049 check: silent autonomous execution          │       │
  │   │   │                                                         │       │
  │   │ AC_COMPLETE: AC-{DOMAIN}-{TIMESTAMP} ✅ (or ❌)            │       │
  │   └─────────────────────────────────────────────────────────────┘       │
  │                                                                         │
  │   All violations recorded to:                                           │
  │   .cortex-runtime/traces/orchestrator-traces.db                         │
  │   Tables: audit_sessions, audit_stage_log, audit_violations             │
  └─────────────────────────────────────────────────────────────────────────┘
```
