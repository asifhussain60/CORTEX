# CortexLabs FinTrack — BadMonolith

> ⚠️ **DO NOT copy this code.** This application is **intentionally broken** — it exists solely as a whetstone for CORTEX's Sharpen-the-Saw (STS) analysis engine.

## Purpose

This is a fictitious financial tracking application ("FinTrack") built by the fictional **CortexLabs** company. It deliberately contains **25+ code smells** across security, SOLID principles, testing, performance, and documentation — each mapped to a specific CORTEX capability.

## Tech Stack

| Layer | Technology | Anti-Patterns |
|-------|-----------|---------------|
| Backend API | C# / ASP.NET Core 8.0 | God class, SQL injection, hardcoded secrets, no DI, no pagination |
| Frontend | Angular 17 / TypeScript | God component, `any` types, business logic in UI, no error handling |
| Database | SQLite (in-process) | Raw SQL, no migrations, no audit fields |
| Tests | xUnit | Tests that assert `true`, zero coverage, mock everything |

## Smell Inventory

Every smell is annotated in-code with `// ❌ SMELL-{N}:` (C#) or `// ❌ SMELL-{N}:` (TypeScript).

| ID | Category | Smell | File |
|----|----------|-------|------|
| 1 | Security | SQL injection via string concatenation | `Program.cs` |
| 2 | Security | Hardcoded secrets in appsettings.json | `appsettings.json` |
| 3 | SOLID | God class (Program.cs > 500 LOC) | `Program.cs` |
| 4 | SOLID | Business logic in controller endpoints | `Program.cs` |
| 5 | SOLID | Circular dependency | `Services/` |
| 6 | Performance | No pagination (unbounded queries) | `Program.cs` |
| 7 | Quality | Mixed naming conventions | `Program.cs`, `Models/` |
| 8 | Quality | Dead code (unused methods) | `Program.cs` |
| 9 | Quality | No API versioning | `Program.cs` |
| 10 | Quality | Duplicate validation logic | `Program.cs` |
| 11 | Quality | No structured logging / OpenTelemetry | `Program.cs` |
| 12 | Testing | Tests that assert True | `Tests/` |
| 13 | Security | CORS wildcard (*) | `Program.cs` |
| 14 | Performance | No retry/circuit breaker | `Services/` |
| 15 | Quality | Magic numbers/strings | `Program.cs` |
| 16 | SOLID | Global mutable state | `Program.cs` |
| 17 | SOLID | No dependency injection (direct new) | `Program.cs` |
| 18 | Security | Stack trace exposure | `Program.cs` |
| 19 | Quality | Missing model validation | `Models/` |
| 20 | Quality | No audit fields | `Models/` |
| 21 | SOLID | God component (Angular) | `frontend/` |
| 22 | Quality | `any` types everywhere | `frontend/` |
| 23 | SOLID | Business logic in UI component | `frontend/` |
| 24 | SOLID | No service layer (direct HTTP in component) | `frontend/` |
| 25 | Quality | No error handling on API calls | `frontend/` |

## CORTEX Demo Flow

```
Step 1: cortex_onboard_repository_v3 → BadMonolith/     [LENS scan]
Step 2: cortex_analyze_sts_app → surfaces all 25 smells
Step 3: cortex_audit_remediation_plan → 4 options
Step 4: TDDOrchestrator → RED tests for P0 smells
Step 5: SecurityOrchestrator → SQL injection + secrets fix (GREEN)
Step 6: RefactoringOrchestrator → SOLID violations resolved
Step 7: Output → cortex-sts/CortexLabs/Refactored/
```

## Isolation

- Analysis outputs → `.cortex-runtime/sts/` (never cortex-registry)
- This folder is git-tracked inside the CORTEX mono-repo
- Zero pollution of production CORTEX assets
