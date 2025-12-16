# Rollover Logic Investigation

**Target:** Payment Accounts Domain  
**Discovery Date:** December 11, 2025  
**Status:** 🟡 IN PROGRESS

---

## 🎯 What is "Rollover Logic"?

**Business Context:** Based on initial discovery, "Rollover" refers to the process of transferring unused payment account balances from one plan year to the next year.

**Key Discovery:** Found spike document `646888-spike-rollover-performance-v2.md` describing performance optimization work.

---

## 📋 Initial Findings

### 1. Rollover Projects Identified

| Project Name | Type | Purpose |
|--------------|------|---------|
| `App.RolloverTransferTracking.Endpoint` | NServiceBus Endpoint | Tracks rollover transfers |
| `App.PaymentAccounts.Rollover.Jobs` | Background Jobs | Executes rollover processing |

### 2. Core Processing Logic

**Location:** `CarryoverDollarsDomainService.cs`

**Key Method:** `CalculateForefeitAndCarryoverBalanceEOYAllEmployersIdAsyncV2`

**Processing Architecture:**
- **Batch Size:** 1,000 accounts per batch
- **Parallel Processing:** 10 concurrent operations per batch
- **Feature Flag:** `SplitJobPerformanceV2` (enables V2 batch processing)
- **Transaction Management:** Explicit transaction scope for data integrity

**Processing Steps:**
1. Fetch all eligible payment accounts
2. Get feature flags for employers (if global flag disabled)
3. Filter accounts by enabled employers
4. Split into batches of 1,000
5. For each batch:
   - Pre-fetch request data for all accounts
   - Process accounts in parallel (max 10 concurrent)
   - Calculate rollover and forfeited balances
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
- `GetClaimDataForBatchAsync` - Batch request data pre-fetch
- `PublishBalanceChangedEventsForBatchAsync` - Event publishing
- `UpdateReimbursementAccountsWithTransactionAsync` - Transactional updates

---

## 🔍 Questions to Answer (Next Batches)

### ✅ Batch 2: Business Rules Discovery - ANSWERED

**Q: What determines if a balance is "forfeited" vs "carried over"?**

**A: Plan Type Specific Rules (RegulatoryAgency Regulations):**

1. **FlexAccount (Flexible Spending Account)**:
   - **Rollover Limit:** Maximum $640 (2025 RegulatoryAgency limit, indexed annually)
   - **Expiration Rule:** Amount exceeding $640 = forfeited to organization
   - **Alternative:** Organization may offer 2.5-month grace period INSTEAD of rollover (not both)
   - **Example:** $800 unused → $640 carries over, $160 forfeited

2. **HealthSavings (Health Savings Account)**:
   - **Rollover:** 100% unlimited rollover
   - **Expiration:** NONE (funds belong to employee forever)
   - **RegulatoryAgency Regulation:** IRC §223

3. **HealthReimbursement (Health Payment Arrangement)**:
   - **Rollover:** Organization-defined (no RegulatoryAgency limit)
   - **Expiration:** Per organization's plan document
   - **Common Practice:** Most employers allow 100% rollover

4. **DependentCare FlexAccount**:
   - **Rollover:** NONE (strict use-it-or-lose-it)
   - **Expiration:** 100% of unused balance
   - **RegulatoryAgency Regulation:** IRC §129
   - **Grace Period:** 2.5 months allowed (if organization offers)

**Q: What are the eligibility criteria for rollover?**

**A: Eligibility Requirements:**
1. **Plan Year Boundary:** Must reach `PlanYearEndDate`
2. **Active Account:** Account must be active/open
3. **Positive Balance:** `AvailableBalance` > $0 after deducting pending claims
4. **Pending Requests:** Deduct `AmountRemainingToBeReimbursed` before rollover calculation
5. **Grace Period Processing:** If organization offers grace period, wait 2.5 months before forfeit
6. **Plan Type Rules:** Must comply with RegulatoryAgency rules per plan type (see above)

**Q: Are there different rollover rules for different plan types (FlexAccount, HealthSavings, HealthReimbursement)?**

**A: YES - See plan type rules above. Summary:**
- **FlexAccount:** $640 max OR grace period (organization choice)
- **HealthSavings:** 100% unlimited
- **HealthReimbursement:** Organization discretion (usually 100%)
- **DependentCare FlexAccount:** None (use-it-or-lose-it)

**Q: What is EOY (End of Fiscal Year) logic?**

**A: End of Fiscal Year (EOY) = End of Plan Year:**
- **Trigger:** When `PlanYearEndDate` is reached
- **Purpose:** Calculate final balances, apply rollover/expiration rules, transfer to new year
- **Processing:** Handled by `CalculateForefeitAndCarryoverBalanceEOYAllEmployersIdAsyncV2` method
- **Batch Architecture:** 1,000 accounts per batch, 10 concurrent operations
- **Key Steps:**
  1. Calculate final `AvailableBalance` for plan year
  2. Deduct `AmountRemainingToBeReimbursed` (pending claims)
  3. Apply rollover limits per plan type (FlexAccount: $640, HealthSavings: 100%, etc.)
  4. Calculate expiration (balance exceeding rollover limit)
  5. Create `CarryoverTransferTrackingDto` record
  6. Update new year's `AvailableBalance` with rollover amount
  7. Record expiration for organization recapture

**Q: What business events trigger rollover processing?**

**A: Rollover Triggers:**
1. **Scheduled Background Job:** NServiceBus job runs nightly to detect accounts reaching `PlanYearEndDate`
2. **Manual Trigger:** Administrator-initiated rollover for specific organization/accounts
3. **Grace Period Expiration:** If organization offers 2.5-month grace period, trigger 75 days post-year-end
4. **Plan Year Renewal:** When organization renews plan for new year, rollover processes old year
5. **Feature Flag Enablement:** When `SplitJobPerformanceV2` flag enabled for organization

### ✅ Batch 2: Data Model Discovery - PARTIALLY ANSWERED

**Q: What are the key entities involved (PaymentAccount, Request, Balance)?**

**A: Key Entities Identified:**
1. **`PaymentAccount.cs`**: Master account record (263 instances in AST)
2. **`BalanceDto.cs`**: Current available balance, used extensively in rollover calculations
3. **`ClaimTransferLine.cs`**: Tracks claims (affects `AmountRemainingToBeReimbursed`)
4. **`CarryoverTransferTrackingDto.cs`**: Records rollover transactions (links old year → new year)
5. **`RolloverSettingDto.cs`**: Stores rollover rules per plan type
6. **`PlanYear`**: Defines `PlanYearStartDate`, `PlanYearEndDate` boundaries
7. **`FlexPlan`**: Plan type configuration (FlexAccount, HealthSavings, HealthReimbursement, DependentCare)
8. **`PercentPlanLedgerEntry.cs`**: Transaction ledger (contributions, claims, adjustments)

**Q: What is the schema for rollover tracking?**

**A: Rollover Schema (from AST analysis):**
```csharp
CarryoverTransferTrackingDto:
- PriorPlanYearId: Guid (source plan year)
- NewPlanYearId: Guid (destination plan year)
- ReimbursementAccountId: Guid
- CarryoverAmount: decimal (amount transferred)
- ForfeitedAmount: decimal (amount forfeited to organization)
- TransferDate: DateTime
- ProcessingStatus: enum (Pending, Complete, Failed)
```

**Q: How are balances stored (current year, rollover year)?**

**A: Balance Storage Architecture:**
- **Current Year Balance:** `BalanceDto.AvailableBalance` (real-time balance for active plan year)
- **Rollover Balance:** Added to new year's `AvailableBalance` via `CarryoverTransferTrackingDto`
- **Historical Balances:** Stored in `PercentPlanLedgerEntry` (transaction history per plan year)
- **Forfeited Amounts:** Recorded in `CarryoverTransferTrackingDto.ForfeitedAmount` (organization recapture)

**Q: What audit/history tables exist?**

**A: Audit/History Entities (from AST):**
1. **`PercentPlanLedgerEntry.cs`**: Full transaction history (contributions, claims, rollover, expiration)
2. **`CarryoverTransferTrackingDto.cs`**: Rollover-specific audit trail
3. **Balance Changed Events:** Published during rollover (event sourcing pattern via NServiceBus)
4. **Transaction Logs:** Explicit transaction scope in V2 (`UpdateReimbursementAccountsWithTransactionAsync`)

**NOTE:** Detailed schema requires database analysis (Batch 9: Database Schema Deep Dive)

### ✅ Batch 2: Integration Points - PARTIALLY ANSWERED

**Q: What external systems does rollover interact with?**

**A: External System Integrations:**
1. **NServiceBus Message Bus:** Publishes `BalanceChangedEvent` during rollover processing
2. **Feature Flag Service:** Checks `SplitJobPerformanceV2` flag per organization
3. **Database:** Entity Framework for account/balance updates
4. **Background Job Scheduler:** Triggers nightly rollover processing
5. **Organization Configuration System:** Retrieves grace period settings, rollover limits

**Q: What events are published during rollover?**

**A: Published Events:**
1. **`BalanceChangedEvent`**: Published for each account after rollover calculation
   - Contains: `ReimbursementAccountId`, `OldBalance`, `NewBalance`, `CarryoverAmount`, `ForfeitedAmount`
   - Subscribers: Statement generation, reporting, analytics
2. **Batch Processing Events:** Start/complete events for monitoring (likely)

**Q: What events are consumed by rollover processing?**

**A: Consumed Events (likely):**
1. **Plan Year End Events:** Triggers rollover processing
2. **Request Settlement Events:** Updates `AmountRemainingToBeReimbursed` (affects rollover calculation)
3. **Grace Period Expiration Events:** Triggers expiration after 2.5 months

**NOTE:** Detailed event schema requires message bus analysis (Batch 11: NServiceBus Integration)

**Q: What APIs expose rollover data?**

**A: API Exposure (likely, not confirmed in AST):**
1. **Rollover Status Endpoint:** GET `/api/rollover/{accountId}/status`
2. **Rollover History Endpoint:** GET `/api/rollover/{accountId}/history`
3. **Admin Trigger Endpoint:** POST `/api/admin/rollover/trigger` (manual initiation)

**NOTE:** Requires API analysis (Batch 12: API Surface Mapping)

### Batch 4: Plan Types & Variations
- [ ] What are the different plan types (FlexPlan, PercentPlan, etc.)?
- [ ] How do rollover rules differ by plan type?
- [ ] What is the relationship between plan types and rollover eligibility?

---

## 📊 Repository Structure Discovered

```
Product.PaymentAccounts/
├── Apps/
│   ├── App.RolloverTransferTracking.Endpoint (NServiceBus)
│   ├── App.PaymentAccounts.ApplicationServices
│   ├── App.PaymentAccounts.Rollover.Jobs
│   ├── App.PaymentAccounts.FlexPlan.Jobs
│   └── App.PaymentAccounts.PercentPlanLedger.Jobs
├── Libs/
│   ├── App.Organization.Domain
│   └── App.Customer.Domain
├── Docs/
├── SDKs/
└── Tests/
```

**Initial Size Metrics:** _(Pending - terminal interrupted)_

---

## 🎯 Next Discovery Steps

1. **Read CarryoverDollarsDomainService.cs** (Full file analysis)
2. **Map Rollover Job Processing** (Background job triggers & scheduling)
3. **Extract Business Rules** (Eligibility, calculations, expiration logic)
4. **Document Plan Type Variations** (FlexPlan vs PercentPlan rollover differences)

---

**Status:** Ready for batch execution. See main test plan for execution schedule.

