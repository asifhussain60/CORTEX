---
agent_id: cortex-sts-refactoring
version: "1.0"
status: active
layer: core
modes_served:
  - REFACTOR
  - AUDIT
  - INVESTIGATE
capabilities:
  - sts_preflight_analysis
  - functional_completeness_gate
  - security_hardening_gate
  - test_coverage_density_gate
  - di_lifetime_consistency_check
  - health_endpoint_realness_check
  - session_traceability
  - refactoring_scorecard
mcp_tools:
  - cortex_refactor
  - cortex_validate_compliance
  - cortex_audit_remediation_plan
priority: P0
token_cost_estimate: 3500
---

# CORTEX STS Refactoring Agent

**Updated:** 2026-02-22 | **Authority:** `.github/agents/core/cortex-sts-refactoring.md`
**Orchestrator:** `RefactoringOrchestrator` (`cortex/orchestrators/domain/refactoring_orchestrator.py`)
**Template:** `cortex-registry/planning/roadmap-templates/sts-refactoring-template.yaml`
**Workflow:** `cortex-registry/workflows/templates/` (csharp-refactor, csharp-security, typescript-refactor, frontend-tdd)

---

## Purpose

Software Transformation Session (STS) agent. Drives the end-to-end REFACTOR pipeline for
multi-language codebases (C# + TypeScript). Closes the 10 identified gaps from the
CortexLabs BadMonolith audit sessions (01-review.md → 03-review.md).

**Activation:** Load when user requests refactoring of an external codebase via `cortex-sts/`.

---

## Lesson Ledger — Gaps from BadMonolith Analysis

These are the systematically identified failure modes from the 3 CortexLabs review sessions.
Every STS session must check all 10 before marking AC_COMPLETE.

| Gap # | ID | Severity | Description | Gate |
|-------|-----|----------|-------------|------|
| 1 | AP-001 | P0 | AC_COMPLETE written with `source/repo` placeholder | ENH-STS-02 |
| 2 | AP-002 | P0 | Source endpoints dropped without ADR (functional regression) | ENH-STS-01 |
| 3 | AP-003 | P0 | SHA256/MD5 used for password hashing (not BCrypt/Argon2) | ENH-STS-03 |
| 4 | AP-004 | P0 | JWT config in appsettings but no `AddAuthentication` wired | ENH-STS-03 |
| 5 | AP-005 | P1 | Health endpoint returns hardcoded `{status:"healthy"}` — no DB probe | ENH-STS-07 |
| 6 | AP-006 | P1 | `AddSingleton` repos + `AddScoped` services — captive dependency | ENH-STS-05 |
| 7 | AP-007 | P1 | No `XxxServiceTests` class for each `XxxService` | ENH-STS-04 |
| 8 | AP-008 | P1 | Frontend has TypeScript service layer but no test runner in `package.json` | ENH-STS-04 |
| 9 | AP-009 | P1 | No rate limiting on login/payment/transfer endpoints | ENH-STS-03 |
| 10 | AP-010 | P2 | CORTEX refactoring session leaves no genuine trace in `orchestrator-traces.db` | ENH-STS-02 |

---

## 7-Gate ENH-STS Pipeline

### ENH-STS-01 — Functional Completeness Gate

**Tool:** `RefactoringOrchestrator.check_functional_completeness(source_items, target_items)`
**Trigger:** After Architecture Decomposition phase (Wave 2, STS-P-003)
**Rule:** Every source endpoint/function must appear in target OR have an ADR filed justifying its removal.

```
source_items: enumerate all public endpoints from BadMonolith (e.g. grep MapPost/MapGet in Program.cs)
target_items: enumerate all endpoints in Refactored (e.g. grep MapPost/MapGet in Endpoints/*.cs)
gap_count == 0 OR adr_count == len(gaps)  →  PASS
```

**Pass criteria:** `report["complete"] == True` OR every gap item in `report["gaps"]` has a corresponding ADR.

**Anti-patterns caught:** Drop of `/api/accounts/transfer`, `/api/admin/stats`, `/api/admin/users/{id}`.

---

### ENH-STS-02 — Session Traceability

**Tool:** `RefactoringOrchestrator.write_refactor_session_trace(action, source_repo, target_repo, session_id, metadata)`
**Trigger:** Start of Wave 1 (AC_START) and end of Wave 3 (AC_COMPLETE)

**Mandatory fields for AC_START:**
```python
write_refactor_session_trace(
    action="AC_START",
    source_repo="cortex-sts/CortexLabs/BadMonolith",   # REAL path, not "source/repo"
    target_repo="cortex-sts/CortexLabs/Refactored",    # REAL path
    session_id=str(uuid.uuid4()),
    metadata={"smells_catalogued": N, "test_count_before": N, "security_p0_before": N},
)
```

**Mandatory fields for AC_COMPLETE:**
```python
write_refactor_session_trace(
    action="AC_COMPLETE",
    source_repo="cortex-sts/CortexLabs/BadMonolith",
    target_repo="cortex-sts/CortexLabs/Refactored",
    session_id=session_id_from_ac_start,
    metadata={
        "smells_addressed": N,
        "files_created": N,
        "test_count_before": N,
        "test_count_after": N,
        "security_p0_before": N,
        "security_p0_after": 0,
    },
)
```

**Verification:** Query `orchestrator-traces.db → trace_refactoringorchestrator` — must contain a row
with the REAL source/target paths and matching `session_id` between AC_START and AC_COMPLETE.

---

### ENH-STS-03 — Security Hardening Gate

**Tool:** `RefactoringOrchestrator.check_security_hardening(source_code, language, context_hints)`
**Trigger:** After Security Hardening phase (Wave 2, STS-P-004)
**Languages:** `csharp`, `typescript`, `json`, `python`

**Mandatory checks:**

| Rule | Pattern | Severity |
|------|---------|---------|
| `weak_password_hash` | SHA256/MD5/SHA1 in password context | P1 |
| `incomplete_jwt` | `has_jwt_config=True` + `has_jwt_middleware=False` | P0 |
| `missing_rate_limiting` | `has_sensitive_endpoints=True` + `has_rate_limiting=False` | P1 |
| `localstorage_token` | `localStorage.setItem('*token*')` in TypeScript | P1 |

**Pass criteria:** `report["clean"] == True` — zero violations across all scanned files.

**How to scan a C# project:**
```python
# Collect all .cs and appsettings.json files
# Run check_security_hardening for each
# Pass context_hints based on file analysis:
context_hints = {
    "has_jwt_config": "JwtSettings" in appsettings_content,
    "has_jwt_middleware": "AddAuthentication" in program_cs,
    "has_sensitive_endpoints": any("/login" or "/transfer" in endpoints),
    "has_rate_limiting": "RateLimit" in program_cs,
}
```

---

### ENH-STS-04 — Test Coverage Density Gate

**Tool:** `RefactoringOrchestrator.check_test_coverage_density(service_dir, test_dir, service_suffix, test_suffix)`
**Trigger:** After Test Coverage phase (Wave 2, STS-P-006)

**Pass criteria:** `report["complete"] == True` — every `XxxService.{ext}` has a `XxxServiceTests.{ext}`.

**Minimum test count per service:** 8 tests (happy path + boundary + error cases).

**Frontend gate (separate check):**
- If `frontend/src/services/` directory exists AND has ≥1 TypeScript file →
  `frontend/package.json` MUST contain a `"test"` script.
- Use workflow: `cortex-registry/workflows/templates/tdd/frontend-tdd-workflow.yaml`

**Caught by this gate:**
- Missing `AccountServiceTests.cs` (Gap #7 in BadMonolith review)
- Missing `ReportServiceTests.cs`
- No Jest/Vitest in `frontend/package.json` (Gap #8)

---

### ENH-STS-05 — DI Lifetime Consistency Gate *(NEW)*

**Trigger:** After Architecture Decomposition (Wave 2, STS-P-003)
**Rule:** Repositories and Services must use consistent DI lifetimes. `AddSingleton` repositories
+ `AddScoped` services create a **captive dependency** (singleton holds reference to scoped object).

**Detection pattern (C#):**
```
grep "AddSingleton.*Repository" Program.cs  →  must return 0 matches
grep "AddScoped.*Repository" Program.cs     →  must return ≥ 1 match per repository
```

**Pass criteria:** All repository registrations use `AddScoped` (or `AddTransient`). Never `AddSingleton`.

**Remediation:** Replace `builder.Services.AddSingleton<IUserRepository, UserRepository>()`
with `builder.Services.AddScoped<IUserRepository, UserRepository>()`.

---

### ENH-STS-06 — Refactoring Scorecard *(AUTO)*

**Tool:** `RefactoringOrchestrator.generate_scorecard(scores)`
**Trigger:** Automatically at Wave 3 close (STS-P-007). Never manually skipped.

**Weights:**
```
architecture   25%    security      25%
testing        20%    documentation 15%
frontend       10%    traceability   5%
```

**Grade thresholds:** A ≥90 · B ≥80 · C ≥70 · D ≥60 · F <60

**Minimum acceptable:** Grade B (≥80/100) for production approval. Grade C requires sign-off.
Grade D or F → BLOCK release, mandatory remediation.

---

### ENH-STS-07 — Health Endpoint Realness Gate *(NEW)*

**Trigger:** After Architecture Decomposition (Wave 2, STS-P-003)
**Rule:** Health endpoints must perform a live dependency probe — not return hardcoded `{status: "healthy"}`.

**Pattern to REJECT (both BadMonolith and naïve refactor):**
```csharp
// BAD — identical in quality to monolith, no real check
app.MapGet("/health", () => Results.Ok(new { status = "healthy" }));
```

**Required pattern:**
```csharp
// GOOD — actual DB reachability check
app.MapGet("/health", async (IDbConnection db) => {
    try {
        await db.ExecuteScalarAsync("SELECT 1");
        return Results.Ok(new { status = "healthy", db = "reachable" });
    } catch (Exception ex) {
        return Results.Json(new { status = "degraded", db = "unreachable", error = ex.Message },
            statusCode: 503);
    }
});
```

**Detection:** Scan `HealthEndpoints.cs` (or equivalent) for hardcoded `"healthy"` strings without
any async database call. If found → P1 violation.

---

## Execution Flow (Full STS Session)

```
Wave 1: Pre-Flight
  STS-P-001: Enumerate source_items (endpoints + public functions)
  STS-P-001: ENH-STS-02: Write AC_START with REAL source/target paths
  STS-P-002: Holistic Validation Gate (CORE-048)

Wave 2: Execute
  STS-P-003: Architecture Decomposition
    → ENH-STS-01: Functional completeness check
    → ENH-STS-05: DI lifetime consistency check
    → ENH-STS-07: Health endpoint realness check
  STS-P-004: Security Hardening
    → ENH-STS-03: check_security_hardening (all source files)
  STS-P-005: Functional Gap Fill (implement missing endpoints with secure re-implementation)
  STS-P-006: Test Coverage Density
    → ENH-STS-04: check_test_coverage_density (backend + frontend)

Wave 3: Close
  STS-P-007: Generate scorecard (ENH-STS-06)
  STS-P-007: Write AC_COMPLETE with real paths and full metadata (ENH-STS-02)
  Validate: python3 scripts/run_tests.py batch → zero regressions
```

---

## Anti-Patterns (Block Execution)

| ID | Description | Severity |
|----|-------------|---------|
| AP-001 | AC_COMPLETE with `source/repo` placeholder path | P0 — BLOCK |
| AP-002 | Endpoint dropped without ADR | P0 — BLOCK |
| AP-003 | SHA256/MD5 for password hashing | P0 — BLOCK |
| AP-004 | JWT config present, no `AddAuthentication` | P0 — BLOCK |
| AP-005 | Health endpoint returns hardcoded `"healthy"` | P1 — WARN |
| AP-006 | `AddSingleton` repo + `AddScoped` service | P1 — WARN |
| AP-007 | No `XxxServiceTests` per `XxxService` | P1 — WARN |
| AP-008 | Frontend service layer without test runner | P1 — WARN |
| AP-009 | No rate limiting on login/transfer endpoints | P1 — WARN |
| AP-010 | LENS `intelligence_audit.db` has zero STS file analysis rows | P2 — INFO |

P0 violations → `cortex_audit_remediation_plan` BLOCK gate.
P1 violations → proceed with mandatory inline remediation plan.

---

## Scorecard — Minimum Thresholds

| Category | Minimum | Rationale |
|----------|---------|-----------|
| Architecture | 8/10 | Clean layer separation required |
| Security | 9/10 | Financial domain — P0 failures are production blockers |
| Testing | 7/10 | Service coverage density gate enforced |
| Documentation | 7/10 | ADRs required for dropped endpoints |
| Frontend | 7/10 | TypeScript strict mode + test runner required |
| Traceability | 7/10 | Real AC_START/AC_COMPLETE in trace DB required |
| **Overall** | **80/100** | Grade B minimum for release |

---

## Canonical References

| Resource | Path |
|----------|------|
| RefactoringOrchestrator | `cortex/orchestrators/domain/refactoring_orchestrator.py` |
| ENH-STS-01 tests | `tests/unit/orchestrators/domain/test_refactoring_orchestrator_enhancements.py` |
| ENH-STS-03/04 tests | `tests/unit/orchestrators/domain/test_refactoring_security_coverage.py` |
| ENH-STS-05/07 tests | `tests/unit/orchestrators/domain/test_refactoring_di_health_gates.py` |
| Gate MCP tests | `tests/mcp/tools/test_cortex_refactor_gate.py` |
| STS Roadmap Template | `cortex-registry/planning/roadmap-templates/sts-refactoring-template.yaml` |
| C# Refactor Workflow | `cortex-registry/workflows/templates/backend/csharp-refactor-workflow.yaml` |
| C# Security Workflow | `cortex-registry/workflows/templates/backend/csharp-security-workflow.yaml` |
| TypeScript Workflow | `cortex-registry/workflows/templates/frontend/typescript-refactor-workflow.yaml` |
| Frontend TDD Workflow | `cortex-registry/workflows/templates/tdd/frontend-tdd-workflow.yaml` |

---

## ⛔ Deleted Constructs — Never Reference

- `cortex/brain/` — dissolved
- `cortex_intelligence/` — merged into `cortex/intelligence/`
- `cortex_lens/` — merged into `cortex/lens/`
- `_archive/` — deleted directory
- Phase 49 / CCL / CrystallizedContext — removed
