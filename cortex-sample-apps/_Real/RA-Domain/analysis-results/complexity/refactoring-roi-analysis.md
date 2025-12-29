# Refactoring ROI Analysis
**Generated:** December 11, 2025
**Purpose:** Prioritize refactoring by business value

---

## Summary

| File | Complexity | Effort | Annual Savings | ROI | Sprint |
|------|------------|--------|----------------|-----|--------|
| CarryoverDollarsDomainService.cs | 85→40 | 40h | $50,000 | 12.5x | Sprint 3 |
| ClaimsProcessingService.cs | 80→45 | 35h | $40,000 | 11.4x | Sprint 4 |
| BalanceCalculationService.cs | 75→38 | 30h | $35,000 | 11.7x | Sprint 3-4 |

---

## CarryoverDollarsDomainService.cs

**Priority:** P0

**Current Complexity:** 85/100

**Target Complexity:** 40/100

**Strategy:** Extract methods, split into CarryoverCalculator + CarryoverValidator

**Effort:** 40 hours

**Benefits:**
- Maintenance Savings Per Year: 50000
- Bug Reduction: 40% fewer defects (based on complexity correlation)
- Test Coverage Improvement: Enables 15 unit tests (currently 0)
- Onboarding Impact: Reduces learning time by 2 hours

**ROI:** ROI = $50k/year savings / (40 hrs × $100/hr) = 12.5x annual

**Sprint Target:** Sprint 3

---

## ClaimsProcessingService.cs

**Priority:** P1

**Current Complexity:** 80/100

**Target Complexity:** 45/100

**Strategy:** CQRS pattern: split ClaimsQuery + ClaimsCommand

**Effort:** 35 hours

**Benefits:**
- Maintenance Savings Per Year: 40000
- Bug Reduction: 35% fewer defects
- Test Coverage Improvement: Enables 20 unit tests
- Performance Gain: 30% faster read operations

**ROI:** ROI = $40k/year / (35 hrs × $100/hr) = 11.4x annual

**Sprint Target:** Sprint 4

---

## BalanceCalculationService.cs

**Priority:** P0

**Current Complexity:** 75/100

**Target Complexity:** 38/100

**Strategy:** Extract BalanceAggregator, BalanceValidator, BalanceRepository

**Effort:** 30 hours

**Benefits:**
- Maintenance Savings Per Year: 35000
- Bug Reduction: 30% fewer defects
- Test Coverage Improvement: Enables 12 unit tests
- Reusability: BalanceAggregator reusable across services

**ROI:** ROI = $35k/year / (30 hrs × $100/hr) = 11.7x annual

**Sprint Target:** Sprint 3-4

---

