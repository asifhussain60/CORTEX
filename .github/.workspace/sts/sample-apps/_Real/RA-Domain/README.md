# RA-Domain: Payment Accounts Analysis

**Target Repository:** `C:\PROJECTS\Product.Example`  
**Purpose:** Validate CORTEX AST scanning capabilities against production .NET domain  
**Created:** December 11, 2025

---

## 📁 Folder Structure

```
RA-Domain/
├── analysis-results/     # Generated analysis reports
├── ast-outputs/          # Raw AST scan outputs
├── domain-models/        # Extracted domain models & relationships
├── test-plans/           # Test scenarios for AST scanners
└── findings/             # Discovered patterns & insights
```

---

## 🎯 Objectives

1. **Validate AST Scanning:** Test CORTEX's ability to parse .NET/C# codebases
2. **Reverse Engineer Domain:** Extract entities, services, repositories, DTOs
3. **Map Dependencies:** Identify internal and external dependencies
4. **Architecture Analysis:** Document layers, patterns, and boundaries
5. **Test Coverage:** Analyze existing test coverage and gaps

---

## 📋 Analysis Scope

### Target Areas
- Domain entities and value objects
- Service layer architecture
- Data access patterns
- API contracts and DTOs
- Dependency injection configuration
- Test coverage (unit, integration, e2e)

### Technical Stack Detection
- Framework versions (.NET Core/Framework)
- NuGet packages and versions
- Database technologies
- Testing frameworks
- Architecture patterns (DDD, Clean Architecture, etc.)

---

## 🚀 Quick Start

**Primary Execution Plan:** See `test-plan-v2-batched.md` for batch-optimized execution (17 batches, 30-90 min each)

**Python Tools Setup:** See `tools-and-setup.md` for tree-sitter-c-sharp and analysis script usage

**Automated Analysis Script:** Run `python scripts/analyze_ra_domain.py` for comprehensive C# AST extraction

**Original Plan:** See `test-plan.md` for full 4-phase plan (reference only)

**Rollover Discovery:** See `discovery/rollover-logic-investigation.md` for business domain insights

**AST Enhancement Tracking:** See `findings/ast-enhancement-tracker.md` for capability gaps (52+ enhancements identified)

**Code Quality Framework:** See `findings/code-quality-framework.md` for P0-P3 issue detection methodology

**Issue Priority Guide:** See `findings/issue-priority-quick-ref.md` for rapid issue classification

---

**Author:** Asif Hussain | **CORTEX Admin Operations**
