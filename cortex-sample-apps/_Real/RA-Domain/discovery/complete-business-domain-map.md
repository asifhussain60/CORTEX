# Complete Business Domain Map: Payment Accounts

**Repository:** C:\PROJECTS\Product.PaymentAccounts  
**Analysis Date:** December 11, 2025  
**Source:** Spike documents + AST analysis + .NET project structure

---

## 🎯 Application Overview

**Purpose:** Healthcare payment account management platform for FlexAccount, HealthSavings, HealthReimbursement, and DependentCare accounts

**Technology Stack:**
- .NET Framework 4.8
- NServiceBus (messaging/endpoints)
- Entity Framework (data access)
- Background Jobs (scheduled processing)
- Domain-Driven Design architecture

**Project Count:** 12 total (5 Apps, 2 Libs, 1 Contracts, 4 Tests)

---

## 📋 Functional Areas

### 1. **Rollover Processing** (PRIMARY FOCUS - extensively documented)

**Business Purpose:** Year-end processing of FlexAccount account balances (rollover vs expiration)

**Key Components:**
- `CarryoverDollarsDomainService.cs` - Core calculation logic
- `App.PaymentAccounts.Rollover.Jobs` - Background job execution
- `RolloverTransferTracking.Endpoint` - NServiceBus message handling

**Business Rules:**
- RegulatoryAgency allows FlexAccount rollover up to $640 (2025 limit)
- Unused funds over $640 are forfeited at plan year end
- Organizations can opt for 2.5 month grace period OR rollover (not both)
- Processing occurs at `PlanYearEndDate` (typically December 31)

**Implementation Versions:**
- **V1 (Legacy):** Sequential processing, individual database updates, N+1 query issues
- **V2 (Current):** Batch processing (1,000 accounts per batch), parallel execution (10 concurrent operations), pre-fetching scheduled items data, transaction-protected updates

**Performance Characteristics (V2):**
- Batch size: 1,000 accounts
- Concurrency: 10 parallel operations (SemaphoreSlim throttling)
- Data pre-fetching: 20 concurrent batch operations
- Database update batches: 250 records per batch
- Event publishing: 50 events per batch, 10 concurrent

**Feature Flags:**
- `SplitJobPerformanceV2` - Toggles V1 vs V2 processing
- Organization-level feature flags for opt-in/opt-out

**Workflows:**
1. Fetch all eligible accounts (plan year ended)
2. Get organization feature flags (parallel batches)
3. Filter accounts by enabled employers
4. Pre-fetch scheduled items data (cached in memory)
5. Split into 1,000-account batches
6. Process each batch:
   - Calculate expiration/rollover per account
   - Batch database updates (250 records)
   - Publish balance change events (50 events, 10 concurrent)
7. Progress logging every 1,000 accounts

---

### 2. **Request Processing**

**Business Purpose:** Process customer payment requests for eligible healthcare expenses

**Key Components:**
- `ClaimDetailHandlers.cs` - Requests API endpoints
- `ClaimTransferLine` entity - Financial transaction tracking
- Auto-pay vs manual payment workflows

**Workflows:**

#### Auto-Pay Requests
- Customer submits request through Customer Portal or Mobile
- Request automatically approved for payment
- `ClaimTransferLine` created with scheduled payment
- `AmountRemainingToBeReimbursed` calculated to control "Reimburse Me" button visibility
- Formula: `OriginalClaimAmount - Sum(ClaimTransferLines.Amount)`
  - `OriginalClaimAmount = HasUnderwriterAuthorityStored ? PatientResponsibilityAmount : RepricedAmount`

#### Manual Payment
- Customer clicks "Reimburse Me" button
- Creates payment request
- Requests adjudication process
- Payment issued

**Edge Cases:**
- Requests with insurance (use `PatientResponsibilityAmount`)
- Self-pay claims (use `RepricedAmount`)
- Coordination of benefits
- Requests denials and appeals

---

### 3. **Statement Generation**

**Business Purpose:** Generate monthly account statements (PDF) for members

**Key Components:**
- `QAccountStatements.cs` - Statement query/generation logic
- `MonthlyStatementStyled.ascx.cs` - Frontend rendering
- Customer Portal + Plum Page integration

**Known Issues:**
- **Bug 613015:** Pre-2025 statements fail to open ("corrupted PDF" error)
  - **Root Cause:** `RateScheduleStartDate >= EndDate` check incorrectly skips pre-2025 statements after rate schedule migration set all accounts to 2025-01-01
  - **Fix:** Replace `RateScheduleStartDate` with `OpenedDate` in filter logic
  - **Impact:** All members, all pre-2025 dates

**Business Rules:**
- Monthly statements for active accounts
- Historical statements accessible via portal
- Statement includes: balance, contributions, claims, transactions

---

### 4. **Balance Management**

**Business Purpose:** Real-time account balance tracking and calculations

**Key Components:**
- `PaymentAccountBalanceService` - Balance inquiry
- `BalanceChangeAudit` entity - Audit trail
- `PercentPlanLedger` - Specialized balance tracking

**Balance Types:**
- **Available Balance:** Current spendable funds
- **Pending Balance:** Scheduled claims reducing available funds
- **Total Balance:** Opening + contributions - claims - fees

**Calculations:**
```
AvailableBalance = SUM(Contributions) - SUM(Requests) - SUM(ScheduledItems) - SUM(Fees)
```

**Workflows:**
- Real-time balance updates on contributions
- Requests reduce available balance immediately (even if scheduled)
- Expiration/rollover adjustments at year-end
- Audit trail for all balance changes

---

### 5. **Plan Year Management**

**Business Purpose:** Manage plan year lifecycle (open, active, close, rollover)

**Key Components:**
- `MemberFlexSpan` entity - Customer registration periods
- `MemberFlexSpanDomainService` - Plan year logic
- `PaymentPlan` entity - Plan configuration

**Plan Year Stages:**
- **Pre-Open:** Before registration begins
- **Open Registration:** Customers select plans
- **Active:** Plan year in effect
- **Year-End Processing:** Carry over/expiration
- **Closed:** Historical data only

**Business Rules:**
- Plan years typically Jan 1 - Dec 31 (calendar year)
- Some employers use fiscal years
- Mid-year changes allowed for life events
- Termination processing for exited employees

---

### 6. **Flex Plan Processing**

**Business Purpose:** Handle flexible spending account administration

**Key Components:**
- `App.PaymentAccounts.FlexPlan.Jobs` - Background processing
- FlexPlan-specific business logic

**Workflows:**
- Plan setup and configuration
- Contribution processing
- Requests adjudication
- Year-end reconciliation

---

### 7. **Percent Plan Ledger**

**Business Purpose:** Specialized ledger for percentage-based payment plans

**Key Components:**
- `App.PaymentAccounts.PercentPlanLedger.Jobs` - Background jobs
- `PercentPlanLedger` entity - Ledger entries

**Business Rules:**
- Some plans reimburse based on percentage (e.g., 80% of request)
- Separate ledger tracking for percentage calculations
- Different from fixed-dollar FlexAccount/HealthSavings accounts

---

### 8. **Rollover Transfer Tracking**

**Business Purpose:** Track rollover amounts transferred between plan years

**Key Components:**
- `RolloverTransferTracking` entity - Transfer records
- `App.RolloverTransferTracking.Endpoint` - NServiceBus endpoint

**Workflows:**
- Year-end rollover calculation triggers transfer
- Transfer record created linking old plan year to new
- Balance audit trail updated
- Events published for downstream systems

---

### 9. **Scheduled Items / Auto-Pay**

**Business Purpose:** Manage scheduled payments and autopay claims

**Key Components:**
- `ScheduledItem` entity - Future payment schedule
- `ScheduledItemService` - Scheduling logic

**Business Rules:**
- Requests can be scheduled for future payment
- Reduces available balance immediately (reserved funds)
- Auto-pay processes claims automatically
- Mobile team uses `AmountRemainingToBeReimbursed` to hide "Reimburse Me" for autopay claims

---

### 10. **Card Transactions**

**Business Purpose:** Process debit card transactions at point-of-sale

**Key Components:**
- `Card` entity - Customer debit cards
- `CardTransaction` entity - POS transactions

**Workflows:**
- Customer uses HealthSavings/FlexAccount debit card at pharmacy/doctor
- Real-time transaction authorization
- Balance check (sufficient funds?)
- Transaction posted to account
- Substantiation requirements (receipts)

---

### 11. **Cash In/Out Processing**

**Business Purpose:** Handle account contributions and withdrawals

**Key Components:**
- `CashInOut` entity - Cash transactions
- Contribution processing
- Distribution processing (HealthSavings withdrawals)

**Workflows:**
- Organization contributions (payroll deduction)
- Customer direct contributions
- HealthSavings withdrawals (reimbursements, distributions)
- Tax reporting (HealthSavings distributions)

---

### 12. **Dependent Management**

**Business Purpose:** Track dependents for DependentCare FlexAccount and coverage

**Key Components:**
- `Dependent` entity - Dependent information
- `DependentSpan` entity - Coverage periods

**Business Rules:**
- DependentCare FlexAccount requires eligible dependents
- Age limits (under 13, or disabled)
- Qualifying expenses (daycare, after-school programs)
- Different limits than medical FlexAccount

---

### 13. **Rollover Settings**

**Business Purpose:** Configure organization-specific rollover rules

**Key Components:**
- `RolloverSettings` entity - Organization rollover configuration
- `RolloverSettingsService` - Rollover logic

**Business Rules:**
- Organization chooses: Grace period OR rollover (not both)
- Rollover limit: $640 (2025 RegulatoryAgency limit)
- Grace period: 2.5 months post plan year
- Per-organization configuration

---

### 14. **Global Contribution Limits**

**Business Purpose:** Enforce RegulatoryAgency contribution limits by year

**Key Components:**
- `GlobalContributionMaxByYear` entity - Annual limits

**Current Limits (2025):**
- FlexAccount: $3,200
- HealthSavings Individual: $4,150
- HealthSavings Family: $8,300
- DependentCare FlexAccount: $5,000

**Note:** Code does NOT currently validate these limits (gap identified)

---

## 🏢 Plan Types

### FlexAccount (Flexible Spending Account)
- **Purpose:** Tax-advantaged account for out-of-pocket medical expenses
- **Contribution Limit (2025):** $3,200
- **Rollover Limit (2025):** $640
- **Tax Treatment:** Pre-tax contributions, tax-free withdrawals for qualified expenses
- **Expiration Rule:** "Use it or lose it" - funds over $640 forfeited
- **Grace Period Option:** Organization may allow 2.5 months
- **Eligible Expenses:** RegulatoryAgency Publication 502 list

### HealthSavings (Health Savings Account)
- **Purpose:** Tax-advantaged savings for medical expenses (high-deductible plans)
- **Contribution Limit (2025):** $4,150 (individual), $8,300 (family)
- **Rollover:** 100% - no expiration
- **Tax Treatment:** Triple tax advantage (pre-tax contribution, tax-free growth, tax-free withdrawals)
- **Portability:** Customer-owned, portable across employers
- **Eligibility:** Requires High-Deductible Health Plan (HDHP)
- **Withdrawals:** Penalty-free for qualified medical expenses; 20% penalty + tax for non-medical before age 65

### HealthReimbursement (Health Payment Arrangement)
- **Purpose:** Organization-funded account for medical expenses
- **Funding:** 100% organization-funded
- **Rollover:** Organization determines rollover rules
- **Portability:** Generally non-portable (lost on termination)
- **Tax Treatment:** Tax-free reimbursements

### DependentCare FlexAccount
- **Purpose:** Tax-advantaged account for dependent care expenses
- **Contribution Limit (2025):** $5,000 (or $2,500 if married filing separately)
- **Eligible Expenses:** Daycare, preschool, after-school programs, summer camps
- **Dependent Requirements:** Under age 13 or disabled dependent
- **Expiration Rule:** "Use it or lose it"

---

## 📊 Business Workflows

### Workflow 1: Customer Registration
1. Organization offers FlexAccount/HealthSavings/HealthReimbursement during open registration
2. Customer elects plan type and contribution amount
3. `MemberFlexSpan` created with plan year dates
4. `PaymentAccount` created
5. Plan year starts (typically Jan 1)
6. Payroll deductions begin

### Workflow 2: Contribution Processing
1. Organization processes payroll
2. Contributions sent to GenericCorp
3. `CashInOut` transaction created
4. `TransferLine` records contribution
5. `AvailableBalance` increased
6. Balance change event published

### Workflow 3: Requests Submission (Manual)
1. Customer incurs medical expense
2. Customer uploads receipt/EOB to Customer Portal
3. Requests team reviews for eligibility
4. Request approved/denied
5. If approved: `ClaimTransferLine` created
6. Payment issued (check/ACH)
7. `AvailableBalance` decreased

### Workflow 4: Requests Submission (Auto-Pay)
1. Customer incurs expense at participating provider
2. Provider submits request directly
3. Request auto-approved (no review needed)
4. `ClaimTransferLine` created with scheduled payment
5. Payment processed automatically
6. Mobile app hides "Reimburse Me" (AmountRemainingToBeReimbursed = 0)

### Workflow 5: Card Transaction
1. Customer swaps HealthSavings/FlexAccount card at pharmacy
2. Real-time authorization request
3. Balance check (sufficient funds?)
4. If approved: transaction authorized
5. `CardTransaction` created
6. `TransferLine` records transaction
7. May require substantiation (receipt upload)

### Workflow 6: Year-End Rollover Processing
1. Plan year ends (Dec 31)
2. `Rollover.Jobs` triggers processing
3. Feature flag check (organization opt-in)
4. For each account:
   - Calculate unused balance
   - If ≤ $640: Carry over to next year
   - If > $640: Forfeit excess, carry $640
5. `RolloverTransferTracking` created
6. `TransferLine` adjusts balances
7. Balance change events published
8. New plan year begins with carried balance

### Workflow 7: Statement Generation
1. Month ends
2. Customer requests statement (or auto-generated)
3. `QAccountStatements.Execute()` runs
4. Filter: Account active during statement period
5. Aggregate: All transactions for month
6. Generate PDF with balance, contributions, claims
7. Store for Customer Portal access

---

## 🔑 Key Business Terms

### Account Management
- **PaymentAccount** - Core entity representing FlexAccount/HealthSavings/HealthReimbursement account
- **PlanType** - Account classification (FlexAccount, HealthSavings, HealthReimbursement, DependentCare)
- **PlanYear** - 12-month period for account (typically calendar year)
- **AvailableBalance** - Current spendable funds
- **MemberFlexSpan** - Customer's registration period in a plan

### Financial Transactions
- **TransferLine** - Generic financial transaction (contribution, request, adjustment)
- **ClaimTransferLine** - Specific to request reimbursements
- **ScheduledItem** - Future scheduled payment
- **CashInOut** - Contribution or distribution transaction
- **CardTransaction** - Debit card purchase

### Requests
- **Request** - Payment request for medical expense
- **PatientResponsibilityAmount** - Customer's portion after insurance
- **RepricedAmount** - Adjusted request amount (for self-pay)
- **UnderwriterAuthority** - Insurance processing indicator
- **Substantiation** - Receipt/EOB documentation

### Year-End Processing
- **Rollover** - Unused balance transferred to next year
- **Expiration** - Unused balance lost at year-end
- **GracePeriod** - 2.5 month extension to use prior year funds
- **RolloverSettings** - Organization configuration for rollover rules

### Plan Configuration
- **Organization** - Organization offering benefits
- **Product** - GenericCorp product offering
- **Subaccount** - Account subdivision (multiple subaccounts per customer)
- **ActualCoverage** - Customer's health plan coverage level
- **CoverageIntent** - Customer's intended coverage election

---

## 🎯 Stakeholders & User Roles

### Customers
- Account holders (employees)
- Submit claims, check balances, view statements
- Use Customer Portal and Mobile app

### Organizations
- Configure plan offerings
- Process contributions via payroll
- Manage employee eligibility

### Requests Administrators
- Review manual claims
- Approve/deny reimbursements
- Handle appeals

### GenericCorp Operations
- System maintenance
- Customer support
- Regulatory compliance

### Developers/Engineers
- Maintain codebase
- Fix bugs (e.g., statement generation)
- Implement performance improvements (e.g., rollover V2)

---

## 📜 Compliance Requirements

### RegulatoryAgency Regulations
- Contribution limits enforced (currently missing in code)
- Qualified expense definitions
- Expiration rules (use-it-or-lose-it)
- Rollover limits ($640 for FlexAccount)
- Tax reporting (Form 5500, 1099-SA for HealthSavings)

### PrivacyRegulation
- Protected Health Information (PHI) handling
- Customer data encryption
- Access controls and audit trails
- Breach notification requirements

### PaymentSecurity
- Card transaction security
- Cardholder data protection
- Secure payment processing

### State Regulations
- State-specific FlexAccount/HealthSavings rules (vary by state)
- Unclaimed property laws

---

## 🔍 Business Insights from Code Analysis

### Strengths
1. **Well-structured DDD architecture** - Clear separation: Entities, Services, DTOs
2. **Performance optimization** - Rollover V2 shows sophisticated batch processing
3. **Feature flag discipline** - Gradual rollout, easy rollback
4. **Audit trails** - BalanceChangeAudit tracks all changes
5. **Event-driven architecture** - NServiceBus for async processing

### Gaps Identified
1. **Missing RegulatoryAgency limit validation** - Contribution limits not enforced in code
2. **Statement generation bug** - Pre-2025 statements broken (Bug 613015)
3. **Grace period logic unclear** - Implementation not fully documented
4. **Test coverage unknown** - Need Batch 11 analysis
5. **External API integration unclear** - CXC JAMS job mentioned but not analyzed

### Technical Debt
1. **V1 rollover code** - Legacy sequential processing still in codebase
2. **Mixed date logic** - `RateScheduleStartDate` vs `OpenedDate` confusion
3. **XML documentation sparse** - Limited business context in code comments
4. **Hard-coded values** - Some limits may be hard-coded vs configuration

---

## 📈 Next Analysis Steps

Based on this domain map, upcoming batches should focus on:

1. **Batch 2.5:** External RegulatoryAgency/PrivacyRegulation research (validate limits, regulations)
2. **Batch 3:** Deep dive into 56 Entities (understand all domain objects)
3. **Batch 4:** DTO analysis (API contracts, data flow)
4. **Batch 5:** Service layer (business logic implementation)
5. **Batch 11:** Test coverage (validate business rules have tests)
6. **Batch 17:** Code quality (find P0 issues like missing limit validation)

---

**Analysis Complete** ✅  
**Domain Complexity:** Medium-High (healthcare + tax regulations + multi-plan types)  
**Business Value:** Clear workflows, well-documented features, some technical debt  
**Regulatory Risk:** Moderate (RegulatoryAgency limit validation missing, statement bug impacts all users)
