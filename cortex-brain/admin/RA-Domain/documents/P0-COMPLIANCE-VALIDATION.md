# P0 Compliance Validation: CarryoverDollarsDomainService

**Analysis Date:** December 11, 2025  
**Service:** CarryoverDollarsDomainService  
**File:** `Libs\Hqy.Member.Domain\Services\CarryoverDollarsDomainService.cs`  
**Total Methods:** 20  
**Analysis Basis:** AST-extracted method signatures (carryover-service-methods.json)

---

## 🎯 Validation Summary

**Critical Finding:** AST analysis reveals **IRS limit parameters exist but implementation details require source code verification.**

| P0 Gap | Status | Evidence | Remediation |
|--------|--------|----------|-------------|
| **P0-001: FSA $3,200 annual limit** | ⚠️ NEEDS VERIFICATION | No validation evident in method signatures | Requires source code inspection |
| **P0-002: HSA $4,150/$8,300 annual limit** | ⚠️ NEEDS VERIFICATION | Parameter `IRSMaxForHSACarryover` present but usage unclear | Requires source code inspection |
| **P0-003: FSA $640 carryover limit** | ⚠️ PARTIAL EVIDENCE | `CalculateCarryoverAmountAllowedAtPlanYearEnd` method exists | Requires implementation review |
| **P0-004: Dependent Care FSA $0 carryover** | ⚠️ NEEDS VERIFICATION | Plan-type-specific logic in `CalculateCarryoverAmountAllowedAtPlanYearEnd` | Requires source code inspection |

**Conclusion:** Method signatures indicate regulatory awareness (IRS parameters, plan-type logic), but AST scanning limitations prevent validating actual enforcement. **Recommend source code review of methods below.**

---

## 🔍 Method-by-Method Analysis

### 1️⃣ MAIN ENTRY POINT (Line 398)

**Method:** `CalculateForefeitAndCarryoverBalanceEOFYAllEmployersIdAsync`

**Signature:**
```csharp
async Task<ProcessCarryOverResponse> CalculateForefeitAndCarryoverBalanceEOFYAllEmployersIdAsync(
    ProcessCarryOverRequest request
)
```

**Purpose:** Process carryover for all accounts across all employers (V2 batch processing)

**Business Logic:**
1. Fetch all eligible accounts
2. Get feature flags per employer (SplitJobPerformanceV2)
3. Filter accounts by enabled employers
4. Split into batches of 1,000 accounts
5. Process each batch with 10 concurrent operations
6. Pre-fetch claim data to reduce DB queries
7. Update accounts with transaction protection
8. Publish BalanceChangedEvent to NServiceBus

**Performance:**
- Batch size: 1,000 accounts
- Concurrency: 10 parallel operations
- Optimization: Pre-fetch claim data, parallel processing, transaction-protected updates
- Feature flag: `SplitJobPerformanceV2`
- Spike document: `646888-spike-carryover-performance-v2.md`

**P0 Compliance Check:**
- ❓ **P0-001 (FSA $3,200):** Not validated at this entry point
- ❓ **P0-002 (HSA $4,150/$8,300):** Not validated at this entry point
- ❌ **CRITICAL:** Entry point does NOT receive IRS limits - assumes downstream method handles validation

**Remediation Needed:** Verify downstream calls to `CalculateCarryoverAmountAllowedAtPlanYearEnd` receive correct IRS limits.

---

### 2️⃣ CORE CALCULATION (Line 89)

**Method:** `UpdateCarryoverandForfeitedBalancesAsync` (Overloaded)

**Signature:**
```csharp
async Task<UpdateCarryoverandForfeitedBalancesResponse> UpdateCarryoverandForfeitedBalancesAsync(
    ReimbursementAccountsDto account,
    decimal IRSMaxForHSACarryover,
    bool? isFeatureFlagEnabled,
    bool? saveToDatabase
)
```

**Purpose:** Core carryover calculation logic

**Parameters:**
- `ReimbursementAccountsDto` - Account data (balances, plan type, plan year)
- **`IRSMaxForHSACarryover`** - IRS maximum HSA carryover limit (2025: $4,150/$8,300)
- `isFeatureFlagEnabled` - Feature flag for V2 batch processing
- `saveToDatabase` - Whether to persist updates immediately or defer

**Business Logic:**
1. Calculates carryover/forfeiture amounts
2. Validates eligibility (account active, plan year ended, balance > 0)
3. Updates balances
4. Publishes BalanceChangedEvent

**P0 Compliance Check:**
- ✅ **P0-002 (HSA limit):** Parameter `IRSMaxForHSACarryover` exists - **POSITIVE SIGNAL**
- ❌ **P0-001 (FSA $3,200):** No FSA annual limit parameter visible
- ❓ **P0-003 (FSA $640 carryover):** Delegates to `CalculateCarryoverAmountAllowedAtPlanYearEnd`

**Key Question:** Where does `IRSMaxForHSACarryover` value come from?
- Expected: GlobalContributionMaxByYear entity (IRS limit table)
- **NEEDS VERIFICATION:** Confirm source retrieves current year's limits correctly

---

### 3️⃣ PLAN-TYPE CARRYOVER RULES (Line 183)

**Method:** `CalculateCarryoverAmountAllowedAtPlanYearEnd`

**Signature:**
```csharp
decimal CalculateCarryoverAmountAllowedAtPlanYearEnd(
    ReimbursementAccountsDto account,
    decimal accountBalanceAtPlanYearEnd,
    decimal IRSMaxForHSACarryover
)
```

**Purpose:** Apply plan-type-specific carryover rules

**Parameters:**
- `account` - Account data with plan type
- `accountBalanceAtPlanYearEnd` - Final available balance after pending claims
- `IRSMaxForHSACarryover` - HSA contribution limit (used for validation)

**Return:** Carryover amount allowed per IRS rules

**Expected Business Logic (Per Documentation):**
```csharp
switch (account.PlanType)
{
    case "FSA":
        return Math.Min(accountBalanceAtPlanYearEnd, 640m); // P0-003
    case "HSA":
        return accountBalanceAtPlanYearEnd; // 100% unlimited (P0-002)
    case "HRA":
        return GetEmployerDefinedCarryoverLimit(account); // Employer-defined
    case "DependentCareFSA":
        return 0m; // Strict use-it-or-lose-it (P0-004)
    default:
        throw new InvalidPlanTypeException();
}
```

**P0 Compliance Check:**
- ✅ **P0-003 (FSA $640):** Method name indicates implementation - **LIKELY COMPLIANT**
- ✅ **P0-004 (Dependent Care FSA $0):** Plan-type-specific logic expected - **LIKELY COMPLIANT**
- ❓ **P0-002 (HSA limit):** Parameter suggests validation, but signature unclear if used

**CRITICAL VERIFICATION NEEDED:**
1. Confirm FSA max carryover is hardcoded to $640 (or configurable with current IRS limit)
2. Verify Dependent Care FSA returns exactly $0
3. Validate HSA allows 100% unlimited rollover (no cap applied)
4. Check if `IRSMaxForHSACarryover` parameter is actually used (or dead code)

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

**Purpose:** Validate account/plan eligibility for carryover

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

**Purpose:** Check if SplitJobPerformanceV2 feature flag is enabled (global or employer-specific)

**Business Logic:**
- Global flag: Applies to all employers
- Employer-specific flag: Overrides global (allows gradual rollout)

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
- ❌ **P0-001 (FSA $3,200):** `ContributionToDate` should validate ≤ $3,200
- ❌ **P0-002 (HSA $4,150/$8,300):** `ContributionToDate` should validate against family/individual limits
- ⚠️ **Risk:** If no upstream validation, members can over-contribute and face IRS penalties

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
- Records carryover amount transferred
- Records forfeited amount
- Creates audit record (HIPAA requirement)

**P0 Compliance Check:**
- ✅ **P0-008 (HIPAA audit):** Audit trail creation is positive signal
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
- Contains: old balance, new balance, carryover amount, forfeited amount

**P0 Compliance Check:**
- ✅ **Good Practice:** Event-driven architecture enables audit trail
- ❓ **Validation:** Confirm event includes all compliance-required fields

---

## 📊 IRS Limit Parameter Analysis

### IRSMaxForHSACarryover Parameter

**Methods Using This Parameter:**
1. `UpdateCarryoverandForfeitedBalancesAsync` (Line 89) - Receives as parameter
2. `CalculateCarryoverAmountAllowedAtPlanYearEnd` (Line 183) - Receives as parameter

**Key Questions:**
1. ✅ **Parameter exists:** Positive signal for HSA limit awareness
2. ❓ **Source of value:** Where is `IRSMaxForHSACarryover` value loaded from?
3. ❓ **Usage confirmation:** Is parameter actually used in validation logic?
4. ❓ **Annual update process:** How is value updated each year when IRS announces new limits?

**Expected Source:** GlobalContributionMaxByYear entity
```csharp
// Expected query:
var hsaLimit = await _context.GlobalContributionMaxByYear
    .Where(g => g.Year == currentYear && g.PlanType == "HSA")
    .Select(g => g.MaxCarryoverAmount)
    .FirstOrDefaultAsync();
```

**CRITICAL VERIFICATION:**
- Confirm GlobalContributionMaxByYear table exists and is populated
- Verify annual update process (manual vs. automated)
- Validate current year (2025) has correct limits: $4,300 individual, $8,550 family

---

### Missing FSA Parameters

**CRITICAL GAP:** No `IRSMaxForFSAContribution` or `FSACarryoverLimit` parameters visible

**Expected Parameters:**
```csharp
async Task<UpdateCarryoverandForfeitedBalancesResponse> UpdateCarryoverandForfeitedBalancesAsync(
    ReimbursementAccountsDto account,
    decimal IRSMaxForHSACarryover,         // ✅ Exists
    decimal IRSMaxForFSAContribution,      // ❌ MISSING
    decimal FSACarryoverLimit,             // ❌ MISSING (should be $640 for 2025)
    bool? isFeatureFlagEnabled,
    bool? saveToDatabase
)
```

**Possible Explanations:**
1. **Hardcoded:** FSA limits hardcoded in `CalculateCarryoverAmountAllowedAtPlanYearEnd` (bad practice)
2. **GlobalContributionMaxByYear:** Retrieved inside method (not visible in signature)
3. **Configuration:** Loaded from app settings or database table

**Recommended Action:** Source code review to determine FSA limit source.

---

## 🚨 P0 Compliance Gap Summary

| Gap ID | Description | Evidence | Likelihood | Recommended Action |
|--------|-------------|----------|------------|-------------------|
| **P0-001** | No FSA $3,200 annual limit validation | No parameter in method signatures | **HIGH** | Source code review of contribution validation |
| **P0-002** | No HSA $4,150/$8,300 annual limit validation | Parameter exists but usage unclear | **MEDIUM** | Verify IRSMaxForHSACarryover is actually enforced |
| **P0-003** | No FSA $640 carryover limit enforcement | Method name suggests compliance | **LOW** | Confirm CalculateCarryoverAmountAllowedAtPlanYearEnd implements correctly |
| **P0-004** | Dependent Care FSA allows carryover (should be $0) | Plan-type logic expected | **LOW** | Verify Dependent Care FSA case returns 0m |
| **P0-005** | Cosmetic surgery not rejected | Not applicable to carryover service | N/A | Investigate claims validation service |
| **P0-006** | CVV storage prohibition | Not applicable to carryover service | N/A | Investigate card transaction service |
| **P0-007** | PAN encryption at rest | Not applicable to carryover service | N/A | Investigate card entity configuration |
| **P0-008** | PHI audit trail | `RecordCarryoverTransferTrackingAsync` exists | **LOW** | Verify audit record includes required fields |
| **P0-009** | MFA enforcement | Not applicable to domain service | N/A | Investigate authentication middleware |

---

## 🔍 Source Code Review Checklist

**Priority 1: FSA Carryover Limit (P0-003)**
```csharp
// File: CarryoverDollarsDomainService.cs, Line 183
decimal CalculateCarryoverAmountAllowedAtPlanYearEnd(...)
{
    // VERIFY:
    // 1. FSA case returns Math.Min(balance, 640m)
    // 2. Value 640 is configurable (not hardcoded)
    // 3. Dependent Care FSA case returns 0m
}
```

**Priority 2: HSA Limit Usage (P0-002)**
```csharp
// File: CarryoverDollarsDomainService.cs, Line 183
decimal CalculateCarryoverAmountAllowedAtPlanYearEnd(
    ReimbursementAccountsDto account,
    decimal accountBalanceAtPlanYearEnd,
    decimal IRSMaxForHSACarryover  // ← IS THIS USED?
)
{
    // VERIFY:
    // 1. IRSMaxForHSACarryover parameter is actually used
    // 2. If not used, why does it exist? (dead code?)
}
```

**Priority 3: FSA Annual Contribution Limit (P0-001)**
```csharp
// Search codebase for:
// - "3200" (FSA limit)
// - "FSAContributionLimit"
// - "GlobalContributionMaxByYear"

// VERIFY:
// 1. Contribution validation exists somewhere (service, API, UI)
// 2. Limit is current year ($3,200 for 2024, TBD for 2025)
// 3. Validation runs BEFORE contribution is accepted
```

**Priority 4: Audit Trail Completeness (P0-008)**
```csharp
// File: CarryoverDollarsDomainService.cs, Line 634
async Task RecordCarryoverTransferTrackingAsync(
    CarryoverTransferTrackingDto trackingData
)
{
    // VERIFY:
    // 1. Includes: user ID, timestamp, old balance, new balance
    // 2. Includes: carryover amount, forfeited amount, transaction ID
    // 3. Immutable record (no UPDATE, only INSERT)
}
```

---

## 💡 Key Insights

### ✅ Positive Signals
1. **IRS Parameter Exists:** `IRSMaxForHSACarryover` parameter indicates regulatory awareness
2. **Plan-Type Logic:** `CalculateCarryoverAmountAllowedAtPlanYearEnd` method name suggests plan-specific rules
3. **Audit Trail:** `RecordCarryoverTransferTrackingAsync` exists for HIPAA compliance
4. **Feature Flag Discipline:** Gradual rollout reduces risk (SplitJobPerformanceV2)
5. **Event Publishing:** BalanceChangedEvent enables downstream audit/reporting

### ⚠️ Warning Signs
1. **Missing FSA Parameters:** No FSA annual or carryover limit parameters visible
2. **Unused Parameter Risk:** `IRSMaxForHSACarryover` may be passed but not enforced
3. **Hardcoded Limits:** FSA $640 carryover may be hardcoded (fragile)
4. **No Contribution Validation:** CarryoverDollarsDomainService doesn't validate annual limits

### 🚨 Critical Gaps
1. **P0-001 (FSA $3,200):** No evidence of annual contribution limit validation
2. **P0-002 (HSA $4,150/$8,300):** Parameter exists but usage unconfirmed

---

## 📋 Recommended Next Steps

### Immediate (This Sprint)
1. **Source Code Review:** Open `CarryoverDollarsDomainService.cs` and verify:
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
4. **Contribution Validation:** Search codebase for FSA/HSA annual limit checks:
   - API controllers
   - Validation services
   - Business rules engine

5. **Test Coverage:** Execute 40+ regulatory test scenarios:
   - FSA $3,200 annual limit boundary conditions
   - FSA $640 carryover limit enforcement
   - HSA family vs. individual limit validation
   - Dependent Care FSA zero carryover validation

6. **Compliance Audit:** Engage legal/regulatory team to review:
   - IRS Publication 969 compliance
   - HIPAA audit trail completeness
   - PCI-DSS card data security (separate service)

---

**Document Version:** 1.0  
**Last Updated:** December 11, 2025  
**Prepared By:** CORTEX AST Analysis System  
**Next Review:** After source code inspection

**Status:** ⚠️ PARTIAL VALIDATION - AST scanning reveals positive signals (IRS parameters, plan-type logic) but cannot confirm actual enforcement. **Source code review required for P0-001, P0-002, P0-003 gaps.**
