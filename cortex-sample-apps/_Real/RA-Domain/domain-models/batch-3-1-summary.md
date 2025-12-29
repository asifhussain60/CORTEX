# Batch 3.1 Entity Extraction Results

**Date:** December 11, 2025  
**Batch:** 3.1 - First 10 of 30 Entities  
**Status:** ✅ COMPLETE

---

## Executive Summary

Successfully extracted metadata from first 10 entity files using Python tree-sitter AST scanner. Discovered **partial class pattern** where entity classes are split between main files (class declaration) and `.Configuration.cs` files (EF Fluent API property mappings).

**Key Finding:** Only **30 total entities** found (not 56 as initially estimated) - test plan batch sizing needs adjustment.

---

## Entities Discovered (Batch 3.1)

### App.Organization.Domain.Entities (5 entities)
1. **Organization** (line 19)
   - Namespace: `App.Organization.Domain.Entities`
   - File: `Organization.cs`
   - XML Doc: None

2. **Lookup** (line 19)
   - Namespace: `App.Organization.Domain.Entities`
   - File: `Lookup.cs`
   - XML Doc: None

3. **Customer** (line 21)
   - Namespace: `App.Organization.Domain.Entities`
   - File: `Customer.cs`
   - XML Doc: None

4. **PaymentAccount** (line 21) ⭐ **CORE ENTITY**
   - Namespace: `App.Organization.Domain.Entities`
   - File: `PaymentAccount.cs`
   - XML Doc: None
   - **Business Significance:** Primary account entity - likely contains FlexAccount/HealthSavings/HealthReimbursement account data

5. **PaymentPlan** (line 24) ⭐ **CORE ENTITY**
   - Namespace: `App.Organization.Domain.Entities`
   - File: `PaymentPlan.cs`
   - XML Doc: None
   - **Business Significance:** Plan configuration entity - FlexAccount/HealthSavings/HealthReimbursement plan types

### App.Customer.Domain.Entities (5 entities)
6. **ActualCoverage** (line 21)
   - Namespace: `App.Customer.Domain.Entities`
   - File: `ActualCoverage.cs`
   - XML Doc: None

7. **BalanceChangeAudit** (line 9) 🔍 **AUDIT TRAIL**
   - Namespace: `App.Customer.Domain.Entities`
   - File: `BalanceChangeAudit.cs`
   - XML Doc: ✅ **"Represents an audit record for balance changes in PaymentAccounts."**
   - **Business Significance:** Tracks all balance modifications - critical for regulatory compliance (PrivacyRegulation audit requirements)

8. **Card** (line 22) 💳 **PaymentSecurity SCOPE**
   - Namespace: `App.Customer.Domain.Entities`
   - File: `Card.cs`
   - XML Doc: None
   - **Business Significance:** FlexAccount/HealthSavings debit card data - **PaymentSecurity compliance required** (see Batch 2.5 findings)

9. **CardTransaction** (line 22) 💳 **PaymentSecurity SCOPE**
   - Namespace: `App.Customer.Domain.Entities`
   - File: `CardTransaction.cs`
   - XML Doc: None
   - **Business Significance:** Card transaction data - **must validate PAN encryption, no CVV storage** (PaymentSecurity Requirements 3-4)

10. **RolloverTransferTracking** (line 9) 🎯 **CARRYOVER LOGIC**
    - Namespace: `App.Customer.Domain.Entities`
    - File: `RolloverTransferTracking.cs`
    - XML Doc: None
    - **Business Significance:** ⭐ **PRIMARY DISCOVERY** - Tracks rollover transfers, directly related to our investigation target

---

## Technical Findings

### Entity Framework Pattern: Partial Classes
- **Main File** (e.g., `Organization.cs`): Class declaration only
- **Configuration File** (e.g., `Organization.Configuration.cs`): EF Fluent API property mappings
- **Impact:** Properties NOT extracted from main files - need to analyze `.Configuration.cs` files separately

**Example Pattern:**
```
Organization.cs              → public partial class Organization { }
Organization.Configuration.cs → Property mappings via Fluent API
```

### Modifiers Extraction: Empty
- Tree-sitter not capturing modifiers (`public`, `partial`, etc.)
- **AST Enhancement Required:** Improve modifier detection in C# parser

### Inheritance: Empty
- No base classes/interfaces detected in Batch 3.1 entities
- Likely using EF conventions (no explicit inheritance)

---

## Critical Business Entities Identified

### 🎯 Rollover Logic (PRIMARY INVESTIGATION TARGET)
- **RolloverTransferTracking**: Tracks rollover fund transfers
- **Expected Related Entities** (from Batches 3.2-3.6):
  - CarryoverPolicy
  - YearEndProcessing
  - ForfeitureTracking

### 💳 PaymentSecurity Compliance Scope (P0 SECURITY)
- **Card**: Debit card master data
- **CardTransaction**: Transaction records
- **Validation Required** (from Batch 2.5):
  - ✅ NEVER store CVV/PIN (PaymentSecurity Requirement 3)
  - ✅ Encrypt PAN at rest (AES-256)
  - ✅ Mask PAN display (last 4 digits only)
  - ✅ Tokenize for storage

### 🔍 Audit & Compliance
- **BalanceChangeAudit**: All balance modifications
- **PrivacyRegulation Requirement:** PHI access must be audited (45 CFR §164.312(b))

### 📊 Core Domain Model
- **PaymentAccount**: Primary account entity
- **PaymentPlan**: Plan configuration (FlexAccount/HealthSavings/HealthReimbursement types)
- **Customer**: Account holder
- **Organization**: Account sponsor

---

## Test Plan Adjustment Required

**Original Estimate:** 56 Entity files  
**Actual Count:** 30 Entity files  

**Impact on Batch 3 Sub-Batches:**
- ~~Sub-Batch 3.1: Entities 1-10~~ ✅ COMPLETE
- Sub-Batch 3.2: Entities 11-20 (10 files)
- Sub-Batch 3.3: Entities 21-30 (10 files)
- ~~Sub-Batch 3.4: Entities 31-40~~ ❌ NOT NEEDED
- ~~Sub-Batch 3.5: Entities 41-50~~ ❌ NOT NEEDED
- ~~Sub-Batch 3.6: Entities 51-56~~ ❌ NOT NEEDED

**Revised Timeline:** Batch 3 reduced from 90 min → 45 min (3 sub-batches × 15 min)

---

## Next Steps (Batch 3.2-3.3)

### Batch 3.2: Entities 11-20
**Expected Entities:**
- Plan-related entities (PlanYear, PlanConfiguration)
- Transaction entities (Contribution, Distribution, Request)
- Coverage entities (DependentCoverage, HDHP validation)

### Batch 3.3: Entities 21-30 (Final)
**Expected Entities:**
- Reference data (PlanType, AccountStatus, TransactionType)
- Compliance entities (TaxReporting, RegulatoryAgency forms)
- Rollover-related entities (continuation of RolloverTransferTracking)

### Post-Batch 3 Analysis
1. **Analyze Configuration Files**: Extract property mappings from `.Configuration.cs` files
2. **Entity Relationship Diagram**: Map relationships between 30 entities
3. **Rollover Entity Deep Dive**: Detailed analysis of RolloverTransferTracking + related entities
4. **PaymentSecurity Validation**: Inspect Card/CardTransaction for CVV storage, PAN encryption
5. **RegulatoryAgency Limit Validation**: Check if PaymentAccount enforces $3,200 FlexAccount / $4,150 HealthSavings limits (P0 gap from Batch 2.5)

---

## AST Enhancements Identified

1. **Modifier Detection**: `public`, `partial`, `sealed` keywords not captured
2. **Property Extraction from Fluent API**: Need EF Configuration file parser
3. **XML Doc Extraction**: Working ✅ (BalanceChangeAudit example)
4. **Navigation Property Detection**: Logic implemented but no data in partial classes
5. **Attribute Extraction**: Working but no class-level attributes found

---

## Batch 3.1 Completion Metrics

| Metric | Value |
|--------|-------|
| Files Analyzed | 10 |
| Classes Found | 10 |
| Namespaces | 2 (App.Organization.Domain.Entities, App.Customer.Domain.Entities) |
| Properties Extracted | 0 (partial class pattern) |
| Navigation Properties | 0 (defined in .Configuration.cs) |
| XML Documentation | 1 (BalanceChangeAudit) |
| Critical Entities | 4 (PaymentAccount, PaymentPlan, RolloverTransferTracking, Card/CardTransaction) |

---

**Status:** ✅ Batch 3.1 COMPLETE | **Next:** Execute Batch 3.2 (Entities 11-20)
