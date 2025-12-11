# Complete Business Domain Map: Reimbursement Accounts

**Repository:** C:\PROJECTS\Product.ReimbursementAccounts  
**Analysis Date:** December 11, 2025  
**Source:** Spike documents + AST analysis + .NET project structure

---

## 🎯 Application Overview

**Purpose:** Healthcare reimbursement account management platform for FSA, HSA, HRA, and Dependent Care accounts

**Technology Stack:**
- .NET Framework 4.8
- NServiceBus (messaging/endpoints)
- Entity Framework (data access)
- Background Jobs (scheduled processing)
- Domain-Driven Design architecture

**Project Count:** 12 total (5 Apps, 2 Libs, 1 Contracts, 4 Tests)

---

## 📋 Functional Areas

### 1. **Carry Over Processing** (PRIMARY FOCUS - extensively documented)

**Business Purpose:** Year-end processing of FSA account balances (carryover vs forfeiture)

**Key Components:**
- `CarryoverDollarsDomainService.cs` - Core calculation logic
- `Hqy.ReimbursementAccounts.CarryOver.Jobs` - Background job execution
- `CarryoverTransferTracking.Endpoint` - NServiceBus message handling

**Business Rules:**
- IRS allows FSA carryover up to $640 (2025 limit)
- Unused funds over $640 are forfeited at plan year end
- Employers can opt for 2.5 month grace period OR carryover (not both)
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
- Employer-level feature flags for opt-in/opt-out

**Workflows:**
1. Fetch all eligible accounts (plan year ended)
2. Get employer feature flags (parallel batches)
3. Filter accounts by enabled employers
4. Pre-fetch scheduled items data (cached in memory)
5. Split into 1,000-account batches
6. Process each batch:
   - Calculate forfeiture/carryover per account
   - Batch database updates (250 records)
   - Publish balance change events (50 events, 10 concurrent)
7. Progress logging every 1,000 accounts

---

### 2. **Claims Processing**

**Business Purpose:** Process member reimbursement requests for eligible healthcare expenses

**Key Components:**
- `ClaimDetailHandlers.cs` - Claims API endpoints
- `ClaimTransferLine` entity - Financial transaction tracking
- Auto-pay vs manual reimbursement workflows

**Workflows:**

#### Auto-Pay Claims
- Member submits claim through Member Portal or Mobile
- Claim automatically approved for payment
- `ClaimTransferLine` created with scheduled payment
- `AmountRemainingToBeReimbursed` calculated to control "Reimburse Me" button visibility
- Formula: `OriginalClaimAmount - Sum(ClaimTransferLines.Amount)`
  - `OriginalClaimAmount = HasUnderwriterAuthorityStored ? PatientResponsibilityAmount : RepricedAmount`

#### Manual Reimbursement
- Member clicks "Reimburse Me" button
- Creates reimbursement request
- Claims adjudication process
- Payment issued

**Edge Cases:**
- Claims with insurance (use `PatientResponsibilityAmount`)
- Self-pay claims (use `RepricedAmount`)
- Coordination of benefits
- Claims denials and appeals

---

### 3. **Statement Generation**

**Business Purpose:** Generate monthly account statements (PDF) for members

**Key Components:**
- `QAccountStatements.cs` - Statement query/generation logic
- `MonthlyStatementStyled.ascx.cs` - Frontend rendering
- Member Portal + Plum Page integration

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
- `ReimbursementAccountBalanceService` - Balance inquiry
- `BalanceChangeAudit` entity - Audit trail
- `PercentPlanLedger` - Specialized balance tracking

**Balance Types:**
- **Available Balance:** Current spendable funds
- **Pending Balance:** Scheduled claims reducing available funds
- **Total Balance:** Opening + contributions - claims - fees

**Calculations:**
```
AvailableBalance = SUM(Contributions) - SUM(Claims) - SUM(ScheduledItems) - SUM(Fees)
```

**Workflows:**
- Real-time balance updates on contributions
- Claims reduce available balance immediately (even if scheduled)
- Forfeiture/carryover adjustments at year-end
- Audit trail for all balance changes

---

### 5. **Plan Year Management**

**Business Purpose:** Manage plan year lifecycle (open, active, close, carry over)

**Key Components:**
- `MemberFlexSpan` entity - Member enrollment periods
- `MemberFlexSpanDomainService` - Plan year logic
- `ReimbursementPlan` entity - Plan configuration

**Plan Year Stages:**
- **Pre-Open:** Before enrollment begins
- **Open Enrollment:** Members select plans
- **Active:** Plan year in effect
- **Year-End Processing:** Carry over/forfeiture
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
- `Hqy.ReimbursementAccounts.FlexPlan.Jobs` - Background processing
- FlexPlan-specific business logic

**Workflows:**
- Plan setup and configuration
- Contribution processing
- Claims adjudication
- Year-end reconciliation

---

### 7. **Percent Plan Ledger**

**Business Purpose:** Specialized ledger for percentage-based reimbursement plans

**Key Components:**
- `Hqy.ReimbursementAccounts.PercentPlanLedger.Jobs` - Background jobs
- `PercentPlanLedger` entity - Ledger entries

**Business Rules:**
- Some plans reimburse based on percentage (e.g., 80% of claim)
- Separate ledger tracking for percentage calculations
- Different from fixed-dollar FSA/HSA accounts

---

### 8. **Carryover Transfer Tracking**

**Business Purpose:** Track carryover amounts transferred between plan years

**Key Components:**
- `CarryoverTransferTracking` entity - Transfer records
- `Hqy.CarryoverTransferTracking.Endpoint` - NServiceBus endpoint

**Workflows:**
- Year-end carryover calculation triggers transfer
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
- Claims can be scheduled for future payment
- Reduces available balance immediately (reserved funds)
- Auto-pay processes claims automatically
- Mobile team uses `AmountRemainingToBeReimbursed` to hide "Reimburse Me" for autopay claims

---

### 10. **Card Transactions**

**Business Purpose:** Process debit card transactions at point-of-sale

**Key Components:**
- `Card` entity - Member debit cards
- `CardTransaction` entity - POS transactions

**Workflows:**
- Member uses HSA/FSA debit card at pharmacy/doctor
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
- Distribution processing (HSA withdrawals)

**Workflows:**
- Employer contributions (payroll deduction)
- Member direct contributions
- HSA withdrawals (reimbursements, distributions)
- Tax reporting (HSA distributions)

---

### 12. **Dependent Management**

**Business Purpose:** Track dependents for Dependent Care FSA and coverage

**Key Components:**
- `Dependent` entity - Dependent information
- `DependentSpan` entity - Coverage periods

**Business Rules:**
- Dependent Care FSA requires eligible dependents
- Age limits (under 13, or disabled)
- Qualifying expenses (daycare, after-school programs)
- Different limits than medical FSA

---

### 13. **Rollover Settings**

**Business Purpose:** Configure employer-specific rollover rules

**Key Components:**
- `RolloverSettings` entity - Employer rollover configuration
- `RolloverSettingsService` - Rollover logic

**Business Rules:**
- Employer chooses: Grace period OR carryover (not both)
- Carryover limit: $640 (2025 IRS limit)
- Grace period: 2.5 months post plan year
- Per-employer configuration

---

### 14. **Global Contribution Limits**

**Business Purpose:** Enforce IRS contribution limits by year

**Key Components:**
- `GlobalContributionMaxByYear` entity - Annual limits

**Current Limits (2025):**
- FSA: $3,200
- HSA Individual: $4,150
- HSA Family: $8,300
- Dependent Care FSA: $5,000

**Note:** Code does NOT currently validate these limits (gap identified)

---

## 🏢 Plan Types

### FSA (Flexible Spending Account)
- **Purpose:** Tax-advantaged account for out-of-pocket medical expenses
- **Contribution Limit (2025):** $3,200
- **Carryover Limit (2025):** $640
- **Tax Treatment:** Pre-tax contributions, tax-free withdrawals for qualified expenses
- **Forfeiture Rule:** "Use it or lose it" - funds over $640 forfeited
- **Grace Period Option:** Employer may allow 2.5 months
- **Eligible Expenses:** IRS Publication 502 list

### HSA (Health Savings Account)
- **Purpose:** Tax-advantaged savings for medical expenses (high-deductible plans)
- **Contribution Limit (2025):** $4,150 (individual), $8,300 (family)
- **Rollover:** 100% - no forfeiture
- **Tax Treatment:** Triple tax advantage (pre-tax contribution, tax-free growth, tax-free withdrawals)
- **Portability:** Member-owned, portable across employers
- **Eligibility:** Requires High-Deductible Health Plan (HDHP)
- **Withdrawals:** Penalty-free for qualified medical expenses; 20% penalty + tax for non-medical before age 65

### HRA (Health Reimbursement Arrangement)
- **Purpose:** Employer-funded account for medical expenses
- **Funding:** 100% employer-funded
- **Rollover:** Employer determines rollover rules
- **Portability:** Generally non-portable (lost on termination)
- **Tax Treatment:** Tax-free reimbursements

### Dependent Care FSA
- **Purpose:** Tax-advantaged account for dependent care expenses
- **Contribution Limit (2025):** $5,000 (or $2,500 if married filing separately)
- **Eligible Expenses:** Daycare, preschool, after-school programs, summer camps
- **Dependent Requirements:** Under age 13 or disabled dependent
- **Forfeiture Rule:** "Use it or lose it"

---

## 📊 Business Workflows

### Workflow 1: Member Enrollment
1. Employer offers FSA/HSA/HRA during open enrollment
2. Member elects plan type and contribution amount
3. `MemberFlexSpan` created with plan year dates
4. `ReimbursementAccount` created
5. Plan year starts (typically Jan 1)
6. Payroll deductions begin

### Workflow 2: Contribution Processing
1. Employer processes payroll
2. Contributions sent to HealthEquity
3. `CashInOut` transaction created
4. `TransferLine` records contribution
5. `AvailableBalance` increased
6. Balance change event published

### Workflow 3: Claims Submission (Manual)
1. Member incurs medical expense
2. Member uploads receipt/EOB to Member Portal
3. Claims team reviews for eligibility
4. Claim approved/denied
5. If approved: `ClaimTransferLine` created
6. Reimbursement issued (check/ACH)
7. `AvailableBalance` decreased

### Workflow 4: Claims Submission (Auto-Pay)
1. Member incurs expense at participating provider
2. Provider submits claim directly
3. Claim auto-approved (no review needed)
4. `ClaimTransferLine` created with scheduled payment
5. Payment processed automatically
6. Mobile app hides "Reimburse Me" (AmountRemainingToBeReimbursed = 0)

### Workflow 5: Card Transaction
1. Member swaps HSA/FSA card at pharmacy
2. Real-time authorization request
3. Balance check (sufficient funds?)
4. If approved: transaction authorized
5. `CardTransaction` created
6. `TransferLine` records transaction
7. May require substantiation (receipt upload)

### Workflow 6: Year-End Carry Over Processing
1. Plan year ends (Dec 31)
2. `CarryOver.Jobs` triggers processing
3. Feature flag check (employer opt-in)
4. For each account:
   - Calculate unused balance
   - If ≤ $640: Carry over to next year
   - If > $640: Forfeit excess, carry $640
5. `CarryoverTransferTracking` created
6. `TransferLine` adjusts balances
7. Balance change events published
8. New plan year begins with carried balance

### Workflow 7: Statement Generation
1. Month ends
2. Member requests statement (or auto-generated)
3. `QAccountStatements.Execute()` runs
4. Filter: Account active during statement period
5. Aggregate: All transactions for month
6. Generate PDF with balance, contributions, claims
7. Store for Member Portal access

---

## 🔑 Key Business Terms

### Account Management
- **ReimbursementAccount** - Core entity representing FSA/HSA/HRA account
- **PlanType** - Account classification (FSA, HSA, HRA, DependentCare)
- **PlanYear** - 12-month period for account (typically calendar year)
- **AvailableBalance** - Current spendable funds
- **MemberFlexSpan** - Member's enrollment period in a plan

### Financial Transactions
- **TransferLine** - Generic financial transaction (contribution, claim, adjustment)
- **ClaimTransferLine** - Specific to claim reimbursements
- **ScheduledItem** - Future scheduled payment
- **CashInOut** - Contribution or distribution transaction
- **CardTransaction** - Debit card purchase

### Claims
- **Claim** - Reimbursement request for medical expense
- **PatientResponsibilityAmount** - Member's portion after insurance
- **RepricedAmount** - Adjusted claim amount (for self-pay)
- **UnderwriterAuthority** - Insurance processing indicator
- **Substantiation** - Receipt/EOB documentation

### Year-End Processing
- **Carryover** - Unused balance transferred to next year
- **Forfeiture** - Unused balance lost at year-end
- **GracePeriod** - 2.5 month extension to use prior year funds
- **RolloverSettings** - Employer configuration for carryover rules

### Plan Configuration
- **Employer** - Organization offering benefits
- **Product** - HealthEquity product offering
- **Subaccount** - Account subdivision (multiple subaccounts per member)
- **ActualCoverage** - Member's health plan coverage level
- **CoverageIntent** - Member's intended coverage election

---

## 🎯 Stakeholders & User Roles

### Members
- Account holders (employees)
- Submit claims, check balances, view statements
- Use Member Portal and Mobile app

### Employers
- Configure plan offerings
- Process contributions via payroll
- Manage employee eligibility

### Claims Administrators
- Review manual claims
- Approve/deny reimbursements
- Handle appeals

### HealthEquity Operations
- System maintenance
- Customer support
- Regulatory compliance

### Developers/Engineers
- Maintain codebase
- Fix bugs (e.g., statement generation)
- Implement performance improvements (e.g., carryover V2)

---

## 📜 Compliance Requirements

### IRS Regulations
- Contribution limits enforced (currently missing in code)
- Qualified expense definitions
- Forfeiture rules (use-it-or-lose-it)
- Carryover limits ($640 for FSA)
- Tax reporting (Form 5500, 1099-SA for HSA)

### HIPAA
- Protected Health Information (PHI) handling
- Member data encryption
- Access controls and audit trails
- Breach notification requirements

### PCI-DSS
- Card transaction security
- Cardholder data protection
- Secure payment processing

### State Regulations
- State-specific FSA/HSA rules (vary by state)
- Unclaimed property laws

---

## 🔍 Business Insights from Code Analysis

### Strengths
1. **Well-structured DDD architecture** - Clear separation: Entities, Services, DTOs
2. **Performance optimization** - Carryover V2 shows sophisticated batch processing
3. **Feature flag discipline** - Gradual rollout, easy rollback
4. **Audit trails** - BalanceChangeAudit tracks all changes
5. **Event-driven architecture** - NServiceBus for async processing

### Gaps Identified
1. **Missing IRS limit validation** - Contribution limits not enforced in code
2. **Statement generation bug** - Pre-2025 statements broken (Bug 613015)
3. **Grace period logic unclear** - Implementation not fully documented
4. **Test coverage unknown** - Need Batch 11 analysis
5. **External API integration unclear** - CXC JAMS job mentioned but not analyzed

### Technical Debt
1. **V1 carry over code** - Legacy sequential processing still in codebase
2. **Mixed date logic** - `RateScheduleStartDate` vs `OpenedDate` confusion
3. **XML documentation sparse** - Limited business context in code comments
4. **Hard-coded values** - Some limits may be hard-coded vs configuration

---

## 📈 Next Analysis Steps

Based on this domain map, upcoming batches should focus on:

1. **Batch 2.5:** External IRS/HIPAA research (validate limits, regulations)
2. **Batch 3:** Deep dive into 56 Entities (understand all domain objects)
3. **Batch 4:** DTO analysis (API contracts, data flow)
4. **Batch 5:** Service layer (business logic implementation)
5. **Batch 11:** Test coverage (validate business rules have tests)
6. **Batch 17:** Code quality (find P0 issues like missing limit validation)

---

**Analysis Complete** ✅  
**Domain Complexity:** Medium-High (healthcare + tax regulations + multi-plan types)  
**Business Value:** Clear workflows, well-documented features, some technical debt  
**Regulatory Risk:** Moderate (IRS limit validation missing, statement bug impacts all users)
