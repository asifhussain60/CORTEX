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

### Hqy.Employer.Domain.Entities (5 entities)
1. **Employer** (line 19)
   - Namespace: `Hqy.Employer.Domain.Entities`
   - File: `Employer.cs`
   - XML Doc: None

2. **Lookup** (line 19)
   - Namespace: `Hqy.Employer.Domain.Entities`
   - File: `Lookup.cs`
   - XML Doc: None

3. **Member** (line 21)
   - Namespace: `Hqy.Employer.Domain.Entities`
   - File: `Member.cs`
   - XML Doc: None

4. **ReimbursementAccount** (line 21) ⭐ **CORE ENTITY**
   - Namespace: `Hqy.Employer.Domain.Entities`
   - File: `ReimbursementAccount.cs`
   - XML Doc: None
   - **Business Significance:** Primary account entity - likely contains FSA/HSA/HRA account data

5. **ReimbursementPlan** (line 24) ⭐ **CORE ENTITY**
   - Namespace: `Hqy.Employer.Domain.Entities`
   - File: `ReimbursementPlan.cs`
   - XML Doc: None
   - **Business Significance:** Plan configuration entity - FSA/HSA/HRA plan types

### Hqy.Member.Domain.Entities (5 entities)
6. **ActualCoverage** (line 21)
   - Namespace: `Hqy.Member.Domain.Entities`
   - File: `ActualCoverage.cs`
   - XML Doc: None

7. **BalanceChangeAudit** (line 9) 🔍 **AUDIT TRAIL**
   - Namespace: `Hqy.Member.Domain.Entities`
   - File: `BalanceChangeAudit.cs`
   - XML Doc: ✅ **"Represents an audit record for balance changes in ReimbursementAccounts."**
   - **Business Significance:** Tracks all balance modifications - critical for regulatory compliance (HIPAA audit requirements)

8. **Card** (line 22) 💳 **PCI-DSS SCOPE**
   - Namespace: `Hqy.Member.Domain.Entities`
   - File: `Card.cs`
   - XML Doc: None
   - **Business Significance:** FSA/HSA debit card data - **PCI-DSS compliance required** (see Batch 2.5 findings)

9. **CardTransaction** (line 22) 💳 **PCI-DSS SCOPE**
   - Namespace: `Hqy.Member.Domain.Entities`
   - File: `CardTransaction.cs`
   - XML Doc: None
   - **Business Significance:** Card transaction data - **must validate PAN encryption, no CVV storage** (PCI-DSS Requirements 3-4)

10. **CarryoverTransferTracking** (line 9) 🎯 **CARRYOVER LOGIC**
    - Namespace: `Hqy.Member.Domain.Entities`
    - File: `CarryoverTransferTracking.cs`
    - XML Doc: None
    - **Business Significance:** ⭐ **PRIMARY DISCOVERY** - Tracks carryover transfers, directly related to our investigation target

---

## Technical Findings

### Entity Framework Pattern: Partial Classes
- **Main File** (e.g., `Employer.cs`): Class declaration only
- **Configuration File** (e.g., `Employer.Configuration.cs`): EF Fluent API property mappings
- **Impact:** Properties NOT extracted from main files - need to analyze `.Configuration.cs` files separately

**Example Pattern:**
```
Employer.cs              → public partial class Employer { }
Employer.Configuration.cs → Property mappings via Fluent API
```

### Modifiers Extraction: Empty
- Tree-sitter not capturing modifiers (`public`, `partial`, etc.)
- **AST Enhancement Required:** Improve modifier detection in C# parser

### Inheritance: Empty
- No base classes/interfaces detected in Batch 3.1 entities
- Likely using EF conventions (no explicit inheritance)

---

## Critical Business Entities Identified

### 🎯 Carryover Logic (PRIMARY INVESTIGATION TARGET)
- **CarryoverTransferTracking**: Tracks carryover fund transfers
- **Expected Related Entities** (from Batches 3.2-3.6):
  - CarryoverPolicy
  - YearEndProcessing
  - ForfeitureTracking

### 💳 PCI-DSS Compliance Scope (P0 SECURITY)
- **Card**: Debit card master data
- **CardTransaction**: Transaction records
- **Validation Required** (from Batch 2.5):
  - ✅ NEVER store CVV/PIN (PCI-DSS Requirement 3)
  - ✅ Encrypt PAN at rest (AES-256)
  - ✅ Mask PAN display (last 4 digits only)
  - ✅ Tokenize for storage

### 🔍 Audit & Compliance
- **BalanceChangeAudit**: All balance modifications
- **HIPAA Requirement:** PHI access must be audited (45 CFR §164.312(b))

### 📊 Core Domain Model
- **ReimbursementAccount**: Primary account entity
- **ReimbursementPlan**: Plan configuration (FSA/HSA/HRA types)
- **Member**: Account holder
- **Employer**: Account sponsor

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
- Transaction entities (Contribution, Distribution, Claim)
- Coverage entities (DependentCoverage, HDHP validation)

### Batch 3.3: Entities 21-30 (Final)
**Expected Entities:**
- Reference data (PlanType, AccountStatus, TransactionType)
- Compliance entities (TaxReporting, IRS forms)
- Carryover-related entities (continuation of CarryoverTransferTracking)

### Post-Batch 3 Analysis
1. **Analyze Configuration Files**: Extract property mappings from `.Configuration.cs` files
2. **Entity Relationship Diagram**: Map relationships between 30 entities
3. **Carryover Entity Deep Dive**: Detailed analysis of CarryoverTransferTracking + related entities
4. **PCI-DSS Validation**: Inspect Card/CardTransaction for CVV storage, PAN encryption
5. **IRS Limit Validation**: Check if ReimbursementAccount enforces $3,200 FSA / $4,150 HSA limits (P0 gap from Batch 2.5)

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
| Namespaces | 2 (Hqy.Employer.Domain.Entities, Hqy.Member.Domain.Entities) |
| Properties Extracted | 0 (partial class pattern) |
| Navigation Properties | 0 (defined in .Configuration.cs) |
| XML Documentation | 1 (BalanceChangeAudit) |
| Critical Entities | 4 (ReimbursementAccount, ReimbursementPlan, CarryoverTransferTracking, Card/CardTransaction) |

---

**Status:** ✅ Batch 3.1 COMPLETE | **Next:** Execute Batch 3.2 (Entities 11-20)
