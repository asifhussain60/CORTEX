# RA-Domain Sanitization Report

**Date:** 2025-12-16 06:10:19  
**Source:** `C:\PROJECTS\CORTEX\cortex-brain\admin\RA-Domain`  
**Backup:** ✅ Deleted (validation passed)

---

## Summary

- **Files Processed:** 105
- **Total Transformations:** 49
- **Backup Deleted:** ✅ Yes

---

## Transformations by Category

### Company Specific

- `Hqy` → `App` (0 occurrences)
- `HealthEquity` → `GenericCorp` (0 occurrences)
- `Product.ReimbursementAccounts` → `Product.PaymentAccounts` (0 occurrences)

### Domain Specific

- `ReimbursementAccountBalanceService` → `PaymentAccountBalanceService` (19 occurrences)
- `ReimbursementAccount` → `PaymentAccount` (0 occurrences)
- `ReimbursementPlan` → `PaymentPlan` (0 occurrences)
- `ReimbursementAccounts` → `PaymentAccounts` (0 occurrences)
- `Reimbursement` → `Payment` (0 occurrences)
- `reimbursement` → `payment` (0 occurrences)
- `Carryover` → `Rollover` (0 occurrences)
- `CarryoverTransferTracking` → `RolloverTransferTracking` (0 occurrences)
- `CarryOver` → `Rollover` (0 occurrences)
- `carryover` → `rollover` (0 occurrences)
- `carry over` → `rollover` (0 occurrences)
- `Carry Over` → `Rollover` (0 occurrences)

### Plan Types

- `FSA` → `FlexAccount` (0 occurrences)
- `HSA` → `HealthSavings` (0 occurrences)
- `HRA` → `HealthReimbursement` (0 occurrences)
- `Dependent Care` → `DependentCare` (0 occurrences)

### Business Terms

- `Member` → `Customer` (0 occurrences)
- `member` → `customer` (0 occurrences)
- `Members` → `Customers` (0 occurrences)
- `Employer` → `Organization` (0 occurrences)
- `employer` → `organization` (0 occurrences)
- `Employers` → `Organizations` (0 occurrences)
- `EOFY` → `EOY` (0 occurrences)
- `End-of-fiscal-year` → `End-of-year` (0 occurrences)
- `end-of-fiscal-year` → `end-of-year` (0 occurrences)

### Compliance Terms

- `IRS` → `RegulatoryAgency` (0 occurrences)
- `HIPAA` → `PrivacyRegulation` (0 occurrences)
- `PCI-DSS` → `PaymentSecurity` (0 occurrences)
- `ERISA` → `BenefitsRegulation` (0 occurrences)

### Workflow Terms

- `Claims Processing` → `Request Processing` (0 occurrences)
- `Claim` → `Request` (0 occurrences)
- `claim` → `request` (0 occurrences)
- `Claims` → `Requests` (0 occurrences)
- `Forfeiture` → `Expiration` (0 occurrences)
- `forfeiture` → `expiration` (0 occurrences)
- `Enrollment` → `Registration` (0 occurrences)
- `enrollment` → `registration` (0 occurrences)

## Top Transformed Files

- `analysis-results\use-cases-by-category.md`: 8 transformations
- `analysis-results\business-value-scan.json`: 5 transformations
- `COMPLETE-ROADMAP.md`: 4 transformations
- `analysis-results\complete-architecture-guide.md`: 4 transformations
- `documents\BUSINESS-USE-CASES.md`: 4 transformations
- `toolkit\ARCHITECTURE.md`: 3 transformations
- `ast-outputs\complete-csharp-analysis.json`: 3 transformations
- `domain-models\batch-5-1-services.json`: 3 transformations
- `toolkit\templates\onedrive\developers\domain-knowledge.html`: 3 transformations
- `documents\executive-narrative-what-this-application-does.md`: 2 transformations
- `toolkit\templates\onedrive\developers\domain-model.html`: 2 transformations
- `test-plan-batch-18-language-processor-poc.md`: 1 transformations
- `discovery\complete-business-domain-map.md`: 1 transformations
- `discovery\plan-types-comprehensive.md`: 1 transformations
- `findings\issue-summary-dashboard.md`: 1 transformations
- `temp\batch-5-1-files.txt`: 1 transformations
- `toolkit\templates\onedrive\developers\complexity-heatmap.html`: 1 transformations
- `toolkit\templates\onedrive\managers\test-coverage-roadmap.html`: 1 transformations
- `toolkit\templates\onedrive\product\capability-catalog.html`: 1 transformations

---

**Sanitization Complete** ✅
**Status:** All company-specific and domain-specific terminology sanitized
**Backup:** Automatically deleted after successful validation
