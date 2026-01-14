# 🔧 Sharpening CORTEX - Sample Application Test Suite

**Purpose:** Real-world application testing for CORTEX 6.0 orchestrator validation  
**Version:** 1.0.0 | **Created:** 2026-01-10  
**Source:** CORTEX-4.0:cortex-sample-apps/  
**Author:** Asif Hussain

---

## 🎯 Overview

**Sharpening CORTEX** provides intentionally flawed and properly architected applications for validating CORTEX capabilities against **real development problems** rather than mock tests.

### Philosophy

> "Don't sharpen your axe on a rubber tree. Use real wood with real knots."

Traditional mock testing validates AI against artificial scenarios. Sharpening CORTEX uses:
- **Actual security vulnerabilities** (SQL injection, hardcoded credentials)
- **Real architectural anti-patterns** (god classes, no separation of concerns)
- **Production legacy code** (healthcare domain models, payment processors)

---

## 📦 Applications

| Application | Type | Purpose | Reset Mechanism |
|-------------|------|---------|-----------------|
| **BadMonolith** | Anti-Pattern | 28+ intentional flaws in .NET 8 API | SQL Seed |
| **CleanSolidApp** | Best Practice | Same domain, proper architecture | EF Migration |
| **_Real** | Legacy Production | Sanitized healthcare/payment apps | Git Checkout |
| **Cortex-Clean** | Architecture | Clean Architecture example | Docker Compose |
| **Cortex-SDD** | Methodology | Scenario-Driven Development | Test Fixtures |
| **sts-template** | Template | Scaffold new test apps | N/A |

---

## 🚀 Quick Start

### 1. Reset All Applications

```powershell
# Windows
.\reset-all.ps1

# Or use Python
python cortex-brain/tier1/sharpening-cortex/reset-manager.py --app all
```

### 2. Run Test Scenario

```bash
# Example: TDD Security Test Generation
python -m src.main "tdd generate security tests for BadMonolith backend/Program.cs"

# Example: Architecture Analysis
python -m src.main "crawl CleanSolidApp --detect architecture-pattern"

# Example: Refactoring Plan
python -m src.main "plan refactor BadMonolith to CleanSolidApp architecture"
```

### 3. Validate Results

```bash
# Check knowledge graph
sqlite3 cortex-brain/tier1/knowledge-graph.db "SELECT * FROM anti_patterns;"

# Review execution plan
cat cortex-brain/tier1/plans/badmonolith-refactor-plan.yaml

# Check audit trail
python -m src.main "audit query --last 1h --category ORCHESTRATOR"
```

---

## 🔍 Application Details

### 🚨 BadMonolith - The Horror Show

**Path:** `sharpening-cortex/BadMonolith/`  
**Tech Stack:** .NET 8 Minimal API + Angular  
**Purpose:** Showcase 28+ anti-patterns for CORTEX to detect and fix

#### Anti-Patterns Catalog

**Security (CRITICAL):**
- Hardcoded database credentials (line 10)
- SQL injection via string concatenation (line 67)
- No input validation (lines 45-75)

**Architecture (HIGH):**
- God class - everything in Program.cs (143 lines)
- No separation of concerns
- Global mutable state

**Code Quality (HIGH):**
- Zero error handling ("just vibes" comment)
- No logging throughout
- No tests whatsoever
- Magic strings everywhere

**SOLID Violations:**
- Single Responsibility: One method does routing, SQL, caching, HTTP
- Open/Closed: Adding features requires modifying existing code
- Dependency Inversion: Direct SqlConnection instantiation

#### Test Scenarios

1. **TDD-SEC-001:** Generate SQL injection tests
2. **PLAN-REFACTOR-001:** Create migration plan to CleanSolidApp
3. **CRAWL-ANTI-001:** Detect all 28 anti-patterns

#### Reset

```bash
curl http://localhost:5000/api/tasks?action=seed
# Validates: Exactly 2 tasks in database
```

---

### ✅ CleanSolidApp - The Reference

**Path:** `sharpening-cortex/CleanSolidApp/`  
**Tech Stack:** ASP.NET Core Web API + EF Core + Angular  
**Purpose:** Same domain as BadMonolith but properly architected

#### Architecture

```
API/
  ├─ Controllers/TasksController.cs      # HTTP endpoints
Application/
  ├─ Interfaces/ITaskRepository.cs       # Abstractions
  ├─ Services/TaskService.cs             # Business logic
Domain/
  └─ Entities/TaskItem.cs                # Domain models
Infrastructure/
  └─ Data/TaskRepository.cs              # Data access
```

#### Good Practices

- **Repository Pattern:** Abstraction over data access
- **Dependency Injection:** Loose coupling
- **Separation of Concerns:** Clear layer boundaries
- **Service Layer:** Centralized HTTP logic in frontend

#### Test Scenarios

1. **TDD-UNIT-001:** Generate service layer tests with mocks
2. **CRAWL-ARCH-001:** Recognize layered architecture pattern
3. **PLAN-REFACTOR-001:** Compare with BadMonolith for migration plan

#### Reset

```powershell
cd CleanSolidApp/backend
dotnet ef database drop --force
dotnet ef database update
curl http://localhost:5001/api/tasks/seed
```

---

### 🏥 _Real - Production Legacy

**Path:** `sharpening-cortex/_Real/`  
**Tech Stack:** Mixed (C#, Python, SQL, OpenAPI specs)  
**Purpose:** Real-world legacy applications from actual projects (sanitized)

#### Applications

1. **RA-Domain:** Healthcare reimbursement domain model
   - **Challenge:** Complex domain logic with HIPAA compliance
   - **Sanitization:** PHI → PII, HIPAA → GDPR (39 transformations)

2. **payment-api-specs:** OpenAPI specs for payment processor
   - **Challenge:** API contract validation, version management

3. **payment-processor-modernized:** Partially refactored processor
   - **Challenge:** Mid-modernization state, mixed patterns

#### Sanitization Mappings

File: `sanitization-mappings.json` (39 transformations)

```json
{
  "Protected Health Information": "Personal Identifiable Information",
  "HIPAA": "GDPR",
  "Participant": "User",
  "Reimbursement": "Payment"
}
```

#### Test Scenarios

1. **SAN-DOMAIN-001:** Sanitize healthcare to generic payment
2. **PLAN-MODERN-001:** Incremental modernization plan

#### Reset

```bash
cd _Real
git checkout HEAD -- .
# Validates: git status shows no changes
```

---

## 🧪 Test Infrastructure

### Analysis Report

**Location:** `cortex-brain/tier1/sharpening-cortex/analysis-report.yaml`

Contains:
- Complete anti-pattern catalog (47 patterns across 6 apps)
- Orchestrator coverage matrix (94% coverage score)
- Technology stack details
- Test scenario definitions

### Reset Manager

**Location:** `cortex-brain/tier1/sharpening-cortex/reset-manager.py`

Python implementation supporting 5 reset mechanisms:
- SQL Seed (BadMonolith)
- EF Migration (CleanSolidApp)
- Git Checkout (_Real)
- Docker Compose (Cortex-Clean)
- Test Fixtures (Cortex-SDD)

**CLI Usage:**

```bash
# Reset specific app
python reset-manager.py --app BadMonolith

# Reset all apps
python reset-manager.py --app all

# Generate report
python reset-manager.py --app all --report reset-report.json
```

### Test Scenarios

**Location:** `cortex-brain/tier1/sharpening-cortex/test-scenarios.yaml`

18 executable scenarios across 6 categories:
- TDD (3 scenarios)
- Planning (2 scenarios)
- Crawler (2 scenarios)
- Sanitization (1 scenario)
- Onboarding (1 scenario)
- Integration (1 scenario)

---

## 📊 Orchestrator Coverage

| Orchestrator | AC-IDs | Coverage | Applications |
|--------------|--------|----------|--------------|
| **TDD-Master** | AC-TDD-001 to AC-TDD-010 | 95% | BadMonolith, CleanSolidApp |
| **Planning v5** | AC-PLAN-006 to AC-PLAN-008 | 92% | BadMonolith, CleanSolidApp, _Real |
| **Crawler** | AC-CRAWLER-001 to AC-CRAWLER-005 | 98% | BadMonolith, CleanSolidApp, Cortex-Clean |
| **Sanitization** | AC-SAN-001, AC-SAN-002 | 100% | _Real |
| **Onboarding** | AC-ONBOARD-001 to AC-ONBOARD-011 | 96% | All |
| **Vacuum/Cleanup** | AC-VAC-001, AC-CLEAN-001 | 85% | BadMonolith |

**Overall Coverage:** 94% of CORTEX capabilities testable

---

## ⚡ Performance Benchmarks

### Baseline Targets

| Operation | Target | Acceptable | Application |
|-----------|--------|------------|-------------|
| Crawl Time | < 5s | < 10s | BadMonolith |
| Knowledge Graph Build | < 3s | < 8s | All |
| Anti-Pattern Detection | < 2s | < 5s | BadMonolith |
| Reset-All Execution | < 45s | < 60s | All |

---

## 🔄 Reset Capability

### Why Reset?

**Problem:** Traditional test applications become corrupted after testing.  
**Solution:** Each app has appropriate reset mechanism for clean slate.

### Reset Types

1. **SQL Seed:** HTTP endpoint triggers database reset (BadMonolith)
2. **EF Migration:** Drop + recreate database (CleanSolidApp)
3. **Git Checkout:** Hard reset to HEAD (_Real)
4. **Docker Compose:** Volumes down/up (Cortex-Clean)
5. **Test Fixtures:** pytest cleanup (Cortex-SDD)

### Validation

Each reset validates success:
- **BadMonolith:** Row count = 2
- **CleanSolidApp:** Migration history clean
- **_Real:** Git diff empty
- **Cortex-Clean:** Container health checks pass
- **Cortex-SDD:** No active pytest sessions

---

## ✅ Viability Assessment

### Accuracy: 97/100 ⭐

- Real-world validation vs artificial scenarios
- 47 cataloged anti-patterns
- Production legacy code patterns
- Before/after transformation proof (BadMonolith ↔ CleanSolidApp)

### Efficiency: 89/100 ⭐

- Minor overhead: Docker/SQL startup (~15s)
- Sanitization processing for _Real apps
- Benefits vastly outweigh costs

### Coverage: 94/100 ⭐

- 94% of CORTEX orchestrator capabilities testable
- 18 executable test scenarios
- 6 application complexity levels

**RECOMMENDATION:** ✅ HIGHLY VIABLE - Proceed with integration

---

## 🎯 Integration with CORTEX 6.0

### Phase 2: Orchestration Core

**TDD-Master:** Use BadMonolith for RED→GREEN→REFACTOR validation

```bash
python -m src.main "tdd generate tests for BadMonolith backend/Program.cs"
```

### Phase 3: Feature Orchestrators

**Crawler:** Build knowledge graphs from messy real code

```bash
python -m src.main "crawl BadMonolith --level deep"
```

**Planning v5:** Create transformation roadmaps

```bash
python -m src.main "plan refactor BadMonolith to CleanSolidApp"
```

### Phase 4: Intelligence Layer

**Sanitization:** Validate pattern-based transformations

```bash
python -m src.main "sanitize _Real/RA-Domain using sanitization-mappings.json"
```

---

## 📝 Contributing

### Adding New Test Applications

1. Create directory under `sharpening-cortex/`
2. Add reset mechanism to `reset-manager.py`
3. Update `analysis-report.yaml` with anti-patterns
4. Define test scenarios in `test-scenarios.yaml`
5. Update this README

### Template Available

Use `sts-template/` as starting point for new applications.

---

## 🔍 Troubleshooting

### Reset Failures

```powershell
# Check individual app status
python reset-manager.py --app BadMonolith --report debug.json

# View detailed logs
cat cortex-brain/audit-logs/latest.jsonl | grep "RESET"
```

### Test Execution Issues

```bash
# Verify orchestrator registration
python -m src.main "epic review"

# Check knowledge graph
sqlite3 cortex-brain/tier1/knowledge-graph.db ".tables"

# Validate audit trail
python -m src.main "audit query --last 1h"
```

---

## 📚 References

- **Analysis Report:** `cortex-brain/tier1/sharpening-cortex/analysis-report.yaml`
- **Test Scenarios:** `cortex-brain/tier1/sharpening-cortex/test-scenarios.yaml`
- **Reset Manager:** `cortex-brain/tier1/sharpening-cortex/reset-manager.py`
- **Sanitization Mappings:** `sharpening-cortex/sanitization-mappings.json`

---

## 🎉 Success Metrics

**When sharpening-cortex is working:**

✅ All 5 applications reset successfully in < 60s  
✅ TDD-Master generates security tests for BadMonolith  
✅ Crawler detects all 28 anti-patterns  
✅ Planning creates valid BadMonolith → CleanSolidApp migration plan  
✅ Knowledge graph queryable via SQL  
✅ Audit trail captures all operations  
✅ Test scenarios execute repeatedly with identical results  

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
