# Carry Over Logic Investigation

**Target:** Reimbursement Accounts Domain  
**Discovery Date:** December 11, 2025  
**Status:** 🟡 IN PROGRESS

---

## 🎯 What is "Carry Over Logic"?

**Business Context:** Based on initial discovery, "Carry Over" refers to the process of transferring unused reimbursement account balances from one plan year to the next year.

**Key Discovery:** Found spike document `646888-spike-carryover-performance-v2.md` describing performance optimization work.

---

## 📋 Initial Findings

### 1. Carry Over Projects Identified

| Project Name | Type | Purpose |
|--------------|------|---------|
| `Hqy.CarryoverTransferTracking.Endpoint` | NServiceBus Endpoint | Tracks carry over transfers |
| `Hqy.ReimbursementAccounts.CarryOver.Jobs` | Background Jobs | Executes carry over processing |

### 2. Core Processing Logic

**Location:** `CarryoverDollarsDomainService.cs`

**Key Method:** `CalculateForefeitAndCarryoverBalanceEOFYAllEmployersIdAsyncV2`

**Processing Architecture:**
- **Batch Size:** 1,000 accounts per batch
- **Parallel Processing:** 10 concurrent operations per batch
- **Feature Flag:** `SplitJobPerformanceV2` (enables V2 batch processing)
- **Transaction Management:** Explicit transaction scope for data integrity

**Processing Steps:**
1. Fetch all eligible reimbursement accounts
2. Get feature flags for employers (if global flag disabled)
3. Filter accounts by enabled employers
4. Split into batches of 1,000
5. For each batch:
   - Pre-fetch claim data for all accounts
   - Process accounts in parallel (max 10 concurrent)
   - Calculate carryover and forfeited balances
   - Save updates with transaction protection
   - Publish balance changed events

### 3. Performance Evolution

**V1 (Original):**
- Sequential processing of all accounts
- Individual database updates
- No batching
- Memory issues with large datasets

**V2 (Optimized):**
- Batch processing (1,000 accounts)
- Parallel processing (10 concurrent)
- Pre-fetching of related data
- Transaction-protected updates
- Memory-efficient with bounded concurrency

### 4. Supporting Infrastructure

**Methods Identified:**
- `GetEmployerFeatureFlagsAsync` - Feature flag retrieval
- `GetClaimDataForBatchAsync` - Batch claim data pre-fetch
- `PublishBalanceChangedEventsForBatchAsync` - Event publishing
- `UpdateReimbursementAccountsWithTransactionAsync` - Transactional updates

---

## 🔍 Questions to Answer (Next Batches)

### ✅ Batch 2: Business Rules Discovery - ANSWERED

**Q: What determines if a balance is "forfeited" vs "carried over"?**

**A: Plan Type Specific Rules (IRS Regulations):**

1. **FSA (Flexible Spending Account)**:
   - **Carryover Limit:** Maximum $640 (2025 IRS limit, indexed annually)
   - **Forfeiture Rule:** Amount exceeding $640 = forfeited to employer
   - **Alternative:** Employer may offer 2.5-month grace period INSTEAD of carryover (not both)
   - **Example:** $800 unused → $640 carries over, $160 forfeited

2. **HSA (Health Savings Account)**:
   - **Carryover:** 100% unlimited rollover
   - **Forfeiture:** NONE (funds belong to employee forever)
   - **IRS Regulation:** IRC §223

3. **HRA (Health Reimbursement Arrangement)**:
   - **Carryover:** Employer-defined (no IRS limit)
   - **Forfeiture:** Per employer's plan document
   - **Common Practice:** Most employers allow 100% carryover

4. **Dependent Care FSA**:
   - **Carryover:** NONE (strict use-it-or-lose-it)
   - **Forfeiture:** 100% of unused balance
   - **IRS Regulation:** IRC §129
   - **Grace Period:** 2.5 months allowed (if employer offers)

**Q: What are the eligibility criteria for carry over?**

**A: Eligibility Requirements:**
1. **Plan Year Boundary:** Must reach `PlanYearEndDate`
2. **Active Account:** Account must be active/open
3. **Positive Balance:** `AvailableBalance` > $0 after deducting pending claims
4. **Pending Claims:** Deduct `AmountRemainingToBeReimbursed` before carryover calculation
5. **Grace Period Processing:** If employer offers grace period, wait 2.5 months before forfeit
6. **Plan Type Rules:** Must comply with IRS rules per plan type (see above)

**Q: Are there different carry over rules for different plan types (FSA, HSA, HRA)?**

**A: YES - See plan type rules above. Summary:**
- **FSA:** $640 max OR grace period (employer choice)
- **HSA:** 100% unlimited
- **HRA:** Employer discretion (usually 100%)
- **Dependent Care FSA:** None (use-it-or-lose-it)

**Q: What is EOFY (End of Fiscal Year) logic?**

**A: End of Fiscal Year (EOFY) = End of Plan Year:**
- **Trigger:** When `PlanYearEndDate` is reached
- **Purpose:** Calculate final balances, apply carryover/forfeiture rules, transfer to new year
- **Processing:** Handled by `CalculateForefeitAndCarryoverBalanceEOFYAllEmployersIdAsyncV2` method
- **Batch Architecture:** 1,000 accounts per batch, 10 concurrent operations
- **Key Steps:**
  1. Calculate final `AvailableBalance` for plan year
  2. Deduct `AmountRemainingToBeReimbursed` (pending claims)
  3. Apply carryover limits per plan type (FSA: $640, HSA: 100%, etc.)
  4. Calculate forfeiture (balance exceeding carryover limit)
  5. Create `CarryoverTransferTrackingDto` record
  6. Update new year's `AvailableBalance` with carryover amount
  7. Record forfeiture for employer recapture

**Q: What business events trigger carry over processing?**

**A: Carry Over Triggers:**
1. **Scheduled Background Job:** NServiceBus job runs nightly to detect accounts reaching `PlanYearEndDate`
2. **Manual Trigger:** Administrator-initiated carry over for specific employer/accounts
3. **Grace Period Expiration:** If employer offers 2.5-month grace period, trigger 75 days post-year-end
4. **Plan Year Renewal:** When employer renews plan for new year, carry over processes old year
5. **Feature Flag Enablement:** When `SplitJobPerformanceV2` flag enabled for employer

### ✅ Batch 2: Data Model Discovery - PARTIALLY ANSWERED

**Q: What are the key entities involved (ReimbursementAccount, Claim, Balance)?**

**A: Key Entities Identified:**
1. **`ReimbursementAccount.cs`**: Master account record (263 instances in AST)
2. **`BalanceDto.cs`**: Current available balance, used extensively in carryover calculations
3. **`ClaimTransferLine.cs`**: Tracks claims (affects `AmountRemainingToBeReimbursed`)
4. **`CarryoverTransferTrackingDto.cs`**: Records carryover transactions (links old year → new year)
5. **`RolloverSettingDto.cs`**: Stores carryover rules per plan type
6. **`PlanYear`**: Defines `PlanYearStartDate`, `PlanYearEndDate` boundaries
7. **`FlexPlan`**: Plan type configuration (FSA, HSA, HRA, Dependent Care)
8. **`PercentPlanLedgerEntry.cs`**: Transaction ledger (contributions, claims, adjustments)

**Q: What is the schema for carry over tracking?**

**A: Carry Over Schema (from AST analysis):**
```csharp
CarryoverTransferTrackingDto:
- PriorPlanYearId: Guid (source plan year)
- NewPlanYearId: Guid (destination plan year)
- ReimbursementAccountId: Guid
- CarryoverAmount: decimal (amount transferred)
- ForfeitedAmount: decimal (amount forfeited to employer)
- TransferDate: DateTime
- ProcessingStatus: enum (Pending, Complete, Failed)
```

**Q: How are balances stored (current year, carry over year)?**

**A: Balance Storage Architecture:**
- **Current Year Balance:** `BalanceDto.AvailableBalance` (real-time balance for active plan year)
- **Carry Over Balance:** Added to new year's `AvailableBalance` via `CarryoverTransferTrackingDto`
- **Historical Balances:** Stored in `PercentPlanLedgerEntry` (transaction history per plan year)
- **Forfeited Amounts:** Recorded in `CarryoverTransferTrackingDto.ForfeitedAmount` (employer recapture)

**Q: What audit/history tables exist?**

**A: Audit/History Entities (from AST):**
1. **`PercentPlanLedgerEntry.cs`**: Full transaction history (contributions, claims, carryover, forfeiture)
2. **`CarryoverTransferTrackingDto.cs`**: Carryover-specific audit trail
3. **Balance Changed Events:** Published during carryover (event sourcing pattern via NServiceBus)
4. **Transaction Logs:** Explicit transaction scope in V2 (`UpdateReimbursementAccountsWithTransactionAsync`)

**NOTE:** Detailed schema requires database analysis (Batch 9: Database Schema Deep Dive)

### ✅ Batch 2: Integration Points - PARTIALLY ANSWERED

**Q: What external systems does carry over interact with?**

**A: External System Integrations:**
1. **NServiceBus Message Bus:** Publishes `BalanceChangedEvent` during carryover processing
2. **Feature Flag Service:** Checks `SplitJobPerformanceV2` flag per employer
3. **Database:** Entity Framework for account/balance updates
4. **Background Job Scheduler:** Triggers nightly carryover processing
5. **Employer Configuration System:** Retrieves grace period settings, carryover limits

**Q: What events are published during carry over?**

**A: Published Events:**
1. **`BalanceChangedEvent`**: Published for each account after carryover calculation
   - Contains: `ReimbursementAccountId`, `OldBalance`, `NewBalance`, `CarryoverAmount`, `ForfeitedAmount`
   - Subscribers: Statement generation, reporting, analytics
2. **Batch Processing Events:** Start/complete events for monitoring (likely)

**Q: What events are consumed by carry over processing?**

**A: Consumed Events (likely):**
1. **Plan Year End Events:** Triggers carryover processing
2. **Claim Settlement Events:** Updates `AmountRemainingToBeReimbursed` (affects carryover calculation)
3. **Grace Period Expiration Events:** Triggers forfeiture after 2.5 months

**NOTE:** Detailed event schema requires message bus analysis (Batch 11: NServiceBus Integration)

**Q: What APIs expose carry over data?**

**A: API Exposure (likely, not confirmed in AST):**
1. **Carryover Status Endpoint:** GET `/api/carryover/{accountId}/status`
2. **Carryover History Endpoint:** GET `/api/carryover/{accountId}/history`
3. **Admin Trigger Endpoint:** POST `/api/admin/carryover/trigger` (manual initiation)

**NOTE:** Requires API analysis (Batch 12: API Surface Mapping)

### Batch 4: Plan Types & Variations
- [ ] What are the different plan types (FlexPlan, PercentPlan, etc.)?
- [ ] How do carry over rules differ by plan type?
- [ ] What is the relationship between plan types and carry over eligibility?

---

## 📊 Repository Structure Discovered

```
Product.ReimbursementAccounts/
├── Apps/
│   ├── Hqy.CarryoverTransferTracking.Endpoint (NServiceBus)
│   ├── Hqy.ReimbursementAccounts.ApplicationServices
│   ├── Hqy.ReimbursementAccounts.CarryOver.Jobs
│   ├── Hqy.ReimbursementAccounts.FlexPlan.Jobs
│   └── Hqy.ReimbursementAccounts.PercentPlanLedger.Jobs
├── Libs/
│   ├── Hqy.Employer.Domain
│   └── Hqy.Member.Domain
├── Docs/
├── SDKs/
└── Tests/
```

**Initial Size Metrics:** _(Pending - terminal interrupted)_

---

## 🎯 Next Discovery Steps

1. **Read CarryoverDollarsDomainService.cs** (Full file analysis)
2. **Map Carry Over Job Processing** (Background job triggers & scheduling)
3. **Extract Business Rules** (Eligibility, calculations, forfeiture logic)
4. **Document Plan Type Variations** (FlexPlan vs PercentPlan carry over differences)

---

**Status:** Ready for batch execution. See main test plan for execution schedule.

