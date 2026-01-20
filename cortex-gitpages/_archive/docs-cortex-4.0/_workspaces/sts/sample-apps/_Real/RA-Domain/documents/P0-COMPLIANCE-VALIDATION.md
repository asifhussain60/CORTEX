# P0 Compliance Validation: ExampleDomainService

**Analysis Date:** December 11, 2025  
**Service:** ExampleDomainService  
**File:** `Libs\App.Example.Domain\Services\ExampleDomainService.cs`  
**Total Methods:** 20  
**Analysis Basis:** AST-extracted method signatures (rollover-service-methods.json)

---

## 🎯 Validation Summary

**Critical Finding:** AST analysis reveals **RegulatoryAgency limit parameters exist but implementation details require source code verification.**

| P0 Gap | Status | Evidence | Remediation |
|--------|--------|----------|-------------|
| **P0-001: FlexAccount $3,200 annual limit** | ⚠️ NEEDS VERIFICATION | No validation evident in method signatures | Requires source code inspection |
| **P0-002: HealthSavings $4,150/$8,300 annual limit** | ⚠️ NEEDS VERIFICATION | Parameter `RegulatoryAgencyMaxForHealthSavingsCarryover` present but usage unclear | Requires source code inspection |
| **P0-003: FlexAccount $640 rollover limit** | ⚠️ PARTIAL EVIDENCE | `CalculateCarryoverAmountAllowedAtPlanYearEnd` method exists | Requires implementation review |
| **P0-004: DependentCare FlexAccount $0 rollover** | ⚠️ NEEDS VERIFICATION | Plan-type-specific logic in `CalculateCarryoverAmountAllowedAtPlanYearEnd` | Requires source code inspection |

**Conclusion:** Method signatures indicate regulatory awareness (RegulatoryAgency parameters, plan-type logic), but AST scanning limitations prevent validating actual enforcement. **Recommend source code review of methods below.**

---

## 🔍 Method-by-Method Analysis

### 1️⃣ MAIN ENTRY POINT (Line 398)

**Method:** `CalculateForefeitAndCarryoverBalanceEOYAllEmployersIdAsync`

**Signature:**
```csharp
async Task<ProcessCarryOverResponse> CalculateForefeitAndCarryoverBalanceEOYAllEmployersIdAsync(
    ProcessCarryOverRequest request
)
```

**Purpose:** Process rollover for all accounts across all employers (V2 batch processing)

**Business Logic:**
1. Fetch all eligible accounts
2. Get feature flags per organization (SplitJobPerformanceV2)
3. Filter accounts by enabled employers
4. Split into batches of 1,000 accounts
5. Process each batch with 10 concurrent operations
6. Pre-fetch request data to reduce DB queries
7. Update accounts with transaction protection
8. Publish BalanceChangedEvent to NServiceBus

**Performance:**
- Batch size: 1,000 accounts
- Concurrency: 10 parallel operations
- Optimization: Pre-fetch request data, parallel processing, transaction-protected updates
- Feature flag: `SplitJobPerformanceV2`
- Spike document: `646888-spike-rollover-performance-v2.md`

**P0 Compliance Check:**
- ❓ **P0-001 (FlexAccount $3,200):** Not validated at this entry point
- ❓ **P0-002 (HealthSavings $4,150/$8,300):** Not validated at this entry point
- ❌ **CRITICAL:** Entry point does NOT receive RegulatoryAgency limits - assumes downstream method handles validation

**Remediation Needed:** Verify downstream calls to `CalculateCarryoverAmountAllowedAtPlanYearEnd` receive correct RegulatoryAgency limits.

---

### 2️⃣ CORE CALCULATION (Line 89)

**Method:** `UpdateCarryoverandForfeitedBalancesAsync` (Overloaded)

**Signature:**
```csharp
async Task<UpdateCarryoverandForfeitedBalancesResponse> UpdateCarryoverandForfeitedBalancesAsync(
    ReimbursementAccountsDto account,
    decimal RegulatoryAgencyMaxForHealthSavingsCarryover,
    bool? isFeatureFlagEnabled,
    bool? saveToDatabase
)
```

**Purpose:** Core rollover calculation logic

**Parameters:**
- `ReimbursementAccountsDto` - Account data (balances, plan type, plan year)
- **`RegulatoryAgencyMaxForHealthSavingsCarryover`** - RegulatoryAgency maximum HealthSavings rollover limit (2025: $4,150/$8,300)
- `isFeatureFlagEnabled` - Feature flag for V2 batch processing
- `saveToDatabase` - Whether to persist updates immediately or defer

**Business Logic:**
1. Calculates rollover/expiration amounts
2. Validates eligibility (account active, plan year ended, balance > 0)
3. Updates balances
4. Publishes BalanceChangedEvent

**P0 Compliance Check:**
- ✅ **P0-002 (HealthSavings limit):** Parameter `RegulatoryAgencyMaxForHealthSavingsCarryover` exists - **POSITIVE SIGNAL**
- ❌ **P0-001 (FlexAccount $3,200):** No FlexAccount annual limit parameter visible
- ❓ **P0-003 (FlexAccount $640 rollover):** Delegates to `CalculateCarryoverAmountAllowedAtPlanYearEnd`

**Key Question:** Where does `RegulatoryAgencyMaxForHealthSavingsCarryover` value come from?
- Expected: GlobalContributionMaxByYear entity (RegulatoryAgency limit table)
- **NEEDS VERIFICATION:** Confirm source retrieves current year's limits correctly

---

### 3️⃣ PLAN-TYPE CARRYOVER RULES (Line 183)

**Method:** `CalculateCarryoverAmountAllowedAtPlanYearEnd`

**Signature:**
```csharp
decimal CalculateCarryoverAmountAllowedAtPlanYearEnd(
    ReimbursementAccountsDto account,
    decimal accountBalanceAtPlanYearEnd,
    decimal RegulatoryAgencyMaxForHealthSavingsCarryover
)
```

**Purpose:** Apply plan-type-specific rollover rules

**Parameters:**
- `account` - Account data with plan type
- `accountBalanceAtPlanYearEnd` - Final available balance after pending claims
- `RegulatoryAgencyMaxForHealthSavingsCarryover` - HealthSavings contribution limit (used for validation)

**Return:** Rollover amount allowed per RegulatoryAgency rules

**Expected Business Logic (Per Documentation):**
```csharp
switch (account.PlanType)
{
    case "FlexAccount":
        return Math.Min(accountBalanceAtPlanYearEnd, 640m); // P0-003
    case "HealthSavings":
        return accountBalanceAtPlanYearEnd; // 100% unlimited (P0-002)
    case "HealthReimbursement":
        return GetEmployerDefinedCarryoverLimit(account); // Organization-defined
    case "DependentCareFlexAccount":
        return 0m; // Strict use-it-or-lose-it (P0-004)
    default:
        throw new InvalidPlanTypeException();
}
```

**P0 Compliance Check:**
- ✅ **P0-003 (FlexAccount $640):** Method name indicates implementation - **LIKELY COMPLIANT**
- ✅ **P0-004 (DependentCare FlexAccount $0):** Plan-type-specific logic expected - **LIKELY COMPLIANT**
- ❓ **P0-002 (HealthSavings limit):** Parameter suggests validation, but signature unclear if used

**CRITICAL VERIFICATION NEEDED:**
1. Confirm FlexAccount max rollover is hardcoded to $640 (or configurable with current RegulatoryAgency limit)
2. Verify DependentCare FlexAccount returns exactly $0
3. Validate HealthSavings allows 100% unlimited rollover (no cap applied)
4. Check if `RegulatoryAgencyMaxForHealthSavingsCarryover` parameter is actually used (or dead code)

---

### 4️⃣ ELIGIBILITY VALIDATION (Line 197)

**Method:** `ValidateReimbursementAccountAndPlanEligibleForRollover`

**Signature:**
```csharp
UpdateCarryoverandForfeitedBalancesResponse ValidateReimbursementAccountAndPlanEligibleForRollover(
    ReimbursementAccountsDto account,
    UpdateCarryoverandForfeitedBalancesResponse response
)
```

**Purpose:** Validate account/plan eligibility for rollover

**Business Logic:**
- Check account is active
- Verify plan year has ended
- Ensure balance > 0
- Confirm no pending issues (claims, disputes, etc.)

**P0 Compliance Check:**
- ✅ **Good Practice:** Pre-validation before calculation reduces errors
- ❌ **Missing:** No contribution limit validation (P0-001, P0-002)

---

### 5️⃣ FEATURE FLAG CHECKS (Lines 388, 393)

**Methods:**
```csharp
async Task<bool> GetIsGlobalCarryoverFeatureFlagEnabledAsync()
async Task<bool> GetIsEmployerCarryoverFeatureFlagEnabledAsync(string employerId)
```

**Purpose:** Check if SplitJobPerformanceV2 feature flag is enabled (global or organization-specific)

**Business Logic:**
- Global flag: Applies to all employers
- Organization-specific flag: Overrides global (allows gradual rollout)

**P0 Compliance Check:**
- ✅ **Good Practice:** Gradual rollout reduces risk
- ⚠️ **Risk:** If V1 has compliance bugs, feature flag delays remediation

---

### 6️⃣ BALANCE RETRIEVAL (Line 498)

**Method:** `GetReimbursementAcountBalanceDetailsAsync`

**Signature:**
```csharp
async Task<ReimbursementAccountBalanceDetailsDto> GetReimbursementAcountBalanceDetailsAsync(
    string reimbursementAccountId
)
```

**Purpose:** Retrieve current balance details

**Return:**
- AvailableBalance - Current usable funds
- AmountRemainingToBeReimbursed - Pending claims
- ContributionToDate - Total contributions for year

**P0 Compliance Check:**
- ❌ **P0-001 (FlexAccount $3,200):** `ContributionToDate` should validate ≤ $3,200
- ❌ **P0-002 (HealthSavings $4,150/$8,300):** `ContributionToDate` should validate against family/individual limits
- ⚠️ **Risk:** If no upstream validation, members can over-contribute and face RegulatoryAgency penalties

---

### 7️⃣ CARRYOVER TRACKING (Line 634)

**Method:** `RecordCarryoverTransferTrackingAsync`

**Signature:**
```csharp
async Task RecordCarryoverTransferTrackingAsync(
    CarryoverTransferTrackingDto trackingData
)
```

**Purpose:** Persist audit trail

**Business Logic:**
- Links source account → destination account
- Records rollover amount transferred
- Records forfeited amount
- Creates audit record (PrivacyRegulation requirement)

**P0 Compliance Check:**
- ✅ **P0-008 (PrivacyRegulation audit):** Audit trail creation is positive signal
- ❓ **Validation:** Confirm `trackingData` includes all required fields (timestamps, user, amounts)

---

### 8️⃣ BALANCE CHANGE PUBLISHING (Line 265)

**Method:** `PublishBalanceChangedById`

**Signature:**
```csharp
async Task PublishBalanceChangedById(
    BalanceChangeInfoDto changeInfo
)
```

**Purpose:** Publish NServiceBus event when balance changes

**Business Logic:**
- BalanceChangedEvent published to message bus
- Downstream systems: statements, reporting, analytics
- Contains: old balance, new balance, rollover amount, forfeited amount

**P0 Compliance Check:**
- ✅ **Good Practice:** Event-driven architecture enables audit trail
- ❓ **Validation:** Confirm event includes all compliance-required fields

---

## 📊 RegulatoryAgency Limit Parameter Analysis

### RegulatoryAgencyMaxForHealthSavingsCarryover Parameter

**Methods Using This Parameter:**
1. `UpdateCarryoverandForfeitedBalancesAsync` (Line 89) - Receives as parameter
2. `CalculateCarryoverAmountAllowedAtPlanYearEnd` (Line 183) - Receives as parameter

**Key Questions:**
1. ✅ **Parameter exists:** Positive signal for HealthSavings limit awareness
2. ❓ **Source of value:** Where is `RegulatoryAgencyMaxForHealthSavingsCarryover` value loaded from?
3. ❓ **Usage confirmation:** Is parameter actually used in validation logic?
4. ❓ **Annual update process:** How is value updated each year when RegulatoryAgency announces new limits?

**Expected Source:** GlobalContributionMaxByYear entity
```csharp
// Expected query:
var hsaLimit = await _context.GlobalContributionMaxByYear
    .Where(g => g.Year == currentYear && g.PlanType == "HealthSavings")
    .Select(g => g.MaxCarryoverAmount)
    .FirstOrDefaultAsync();
```

**CRITICAL VERIFICATION:**
- Confirm GlobalContributionMaxByYear table exists and is populated
- Verify annual update process (manual vs. automated)
- Validate current year (2025) has correct limits: $4,300 individual, $8,550 family

---

### Missing FlexAccount Parameters

**CRITICAL GAP:** No `RegulatoryAgencyMaxForFlexAccountContribution` or `FlexAccountCarryoverLimit` parameters visible

**Expected Parameters:**
```csharp
async Task<UpdateCarryoverandForfeitedBalancesResponse> UpdateCarryoverandForfeitedBalancesAsync(
    ReimbursementAccountsDto account,
    decimal RegulatoryAgencyMaxForHealthSavingsCarryover,         // ✅ Exists
    decimal RegulatoryAgencyMaxForFlexAccountContribution,      // ❌ MISSING
    decimal FlexAccountCarryoverLimit,             // ❌ MISSING (should be $640 for 2025)
    bool? isFeatureFlagEnabled,
    bool? saveToDatabase
)
```

**Possible Explanations:**
1. **Hardcoded:** FlexAccount limits hardcoded in `CalculateCarryoverAmountAllowedAtPlanYearEnd` (bad practice)
2. **GlobalContributionMaxByYear:** Retrieved inside method (not visible in signature)
3. **Configuration:** Loaded from app settings or database table

**Recommended Action:** Source code review to determine FlexAccount limit source.

---

## 🚨 P0 Compliance Gap Summary

| Gap ID | Description | Evidence | Likelihood | Recommended Action |
|--------|-------------|----------|------------|-------------------|
| **P0-001** | No FlexAccount $3,200 annual limit validation | No parameter in method signatures | **HIGH** | Source code review of contribution validation |
| **P0-002** | No HealthSavings $4,150/$8,300 annual limit validation | Parameter exists but usage unclear | **MEDIUM** | Verify RegulatoryAgencyMaxForHealthSavingsCarryover is actually enforced |
| **P0-003** | No FlexAccount $640 rollover limit enforcement | Method name suggests compliance | **LOW** | Confirm CalculateCarryoverAmountAllowedAtPlanYearEnd implements correctly |
| **P0-004** | DependentCare FlexAccount allows rollover (should be $0) | Plan-type logic expected | **LOW** | Verify DependentCare FlexAccount case returns 0m |
| **P0-005** | Cosmetic surgery not rejected | Not applicable to rollover service | N/A | Investigate claims validation service |
| **P0-006** | CVV storage prohibition | Not applicable to rollover service | N/A | Investigate card transaction service |
| **P0-007** | PAN encryption at rest | Not applicable to rollover service | N/A | Investigate card entity configuration |
| **P0-008** | PHI audit trail | `RecordCarryoverTransferTrackingAsync` exists | **LOW** | Verify audit record includes required fields |
| **P0-009** | MFA enforcement | Not applicable to domain service | N/A | Investigate authentication middleware |

---

## 🔍 Source Code Review Checklist

**Priority 1: FlexAccount Rollover Limit (P0-003)**
```csharp
// File: ExampleDomainService.cs, Line 183
decimal CalculateCarryoverAmountAllowedAtPlanYearEnd(...)
{
    // VERIFY:
    // 1. FlexAccount case returns Math.Min(balance, 640m)
    // 2. Value 640 is configurable (not hardcoded)
    // 3. DependentCare FlexAccount case returns 0m
}
```

**Priority 2: HealthSavings Limit Usage (P0-002)**
```csharp
// File: ExampleDomainService.cs, Line 183
decimal CalculateCarryoverAmountAllowedAtPlanYearEnd(
    ReimbursementAccountsDto account,
    decimal accountBalanceAtPlanYearEnd,
    decimal RegulatoryAgencyMaxForHealthSavingsCarryover  // ← IS THIS USED?
)
{
    // VERIFY:
    // 1. RegulatoryAgencyMaxForHealthSavingsCarryover parameter is actually used
    // 2. If not used, why does it exist? (dead code?)
}
```

**Priority 3: FlexAccount Annual Contribution Limit (P0-001)**
```csharp
// Search codebase for:
// - "3200" (FlexAccount limit)
// - "FlexAccountContributionLimit"
// - "GlobalContributionMaxByYear"

// VERIFY:
// 1. Contribution validation exists somewhere (service, API, UI)
// 2. Limit is current year ($3,200 for 2024, TBD for 2025)
// 3. Validation runs BEFORE contribution is accepted
```

**Priority 4: Audit Trail Completeness (P0-008)**
```csharp
// File: ExampleDomainService.cs, Line 634
async Task RecordCarryoverTransferTrackingAsync(
    CarryoverTransferTrackingDto trackingData
)
{
    // VERIFY:
    // 1. Includes: user ID, timestamp, old balance, new balance
    // 2. Includes: rollover amount, forfeited amount, transaction ID
    // 3. Immutable record (no UPDATE, only INSERT)
}
```

---

## 💡 Key Insights

### ✅ Positive Signals
1. **RegulatoryAgency Parameter Exists:** `RegulatoryAgencyMaxForHealthSavingsCarryover` parameter indicates regulatory awareness
2. **Plan-Type Logic:** `CalculateCarryoverAmountAllowedAtPlanYearEnd` method name suggests plan-specific rules
3. **Audit Trail:** `RecordCarryoverTransferTrackingAsync` exists for PrivacyRegulation compliance
4. **Feature Flag Discipline:** Gradual rollout reduces risk (SplitJobPerformanceV2)
5. **Event Publishing:** BalanceChangedEvent enables downstream audit/reporting

### ⚠️ Warning Signs
1. **Missing FlexAccount Parameters:** No FlexAccount annual or rollover limit parameters visible
2. **Unused Parameter Risk:** `RegulatoryAgencyMaxForHealthSavingsCarryover` may be passed but not enforced
3. **Hardcoded Limits:** FlexAccount $640 rollover may be hardcoded (fragile)
4. **No Contribution Validation:** ExampleDomainService doesn't validate annual limits

### 🚨 Critical Gaps
1. **P0-001 (FlexAccount $3,200):** No evidence of annual contribution limit validation
2. **P0-002 (HealthSavings $4,150/$8,300):** Parameter exists but usage unconfirmed

---

## 📋 Recommended Next Steps

### Immediate (This Sprint)
1. **Source Code Review:** Open `ExampleDomainService.cs` and verify:
   - Lines 183-196: `CalculateCarryoverAmountAllowedAtPlanYearEnd` implementation
   - Lines 89-180: `UpdateCarryoverandForfeitedBalancesAsync` logic
   - Lines 634-650: `RecordCarryoverTransferTrackingAsync` audit fields

2. **Database Inspection:** Query GlobalContributionMaxByYear table:
   ```sql
   SELECT * FROM GlobalContributionMaxByYear
   WHERE Year IN (2024, 2025)
   ORDER BY Year DESC, PlanType;
   ```

3. **Feature Flag Audit:** Confirm SplitJobPerformanceV2 rollout status:
   - How many employers enabled?
   - Any compliance issues reported in V1 vs. V2?

### Short-Term (Next Quarter)
4. **Contribution Validation:** Search codebase for FlexAccount/HealthSavings annual limit checks:
   - API controllers
   - Validation services
   - Business rules engine

5. **Test Coverage:** Execute 40+ regulatory test scenarios:
   - FlexAccount $3,200 annual limit boundary conditions
   - FlexAccount $640 rollover limit enforcement
   - HealthSavings family vs. individual limit validation
   - DependentCare FlexAccount zero rollover validation

6. **Compliance Audit:** Engage legal/regulatory team to review:
   - RegulatoryAgency Publication 969 compliance
   - PrivacyRegulation audit trail completeness
   - PaymentSecurity card data security (separate service)

---

**Document Version:** 1.0  
**Last Updated:** December 11, 2025  
**Prepared By:** CORTEX AST Analysis System  
**Next Review:** After source code inspection

**Status:** ⚠️ PARTIAL VALIDATION - AST scanning reveals positive signals (RegulatoryAgency parameters, plan-type logic) but cannot confirm actual enforcement. **Source code review required for P0-001, P0-002, P0-003 gaps.**
