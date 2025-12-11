# Business Workflows - Reimbursement Accounts

**Generated**: December 2024  
**Source**: AST Analysis + Spike Documents  
**Target**: Product.ReimbursementAccounts Repository

---

## Overview

This document maps the 7 major end-to-end business workflows identified in the Reimbursement Accounts system. Each workflow represents a complete business process from initiation to completion, spanning multiple functional areas and plan types.

---

## 1. Enrollment & Account Setup Workflow

### Purpose
Establish a new reimbursement account for an employee, configure plan parameters, and activate for use.

### Steps
1. **Employee Selection**: HR/benefits administrator selects employee
2. **Plan Type Selection**: Choose FSA, HSA, HRA, or Dependent Care FSA
3. **Plan Year Configuration**: Set PlanYearStartDate, PlanYearEndDate
4. **Contribution Setup**:
   - Employee pre-tax deductions (FSA, Dependent Care)
   - Employer contributions (HSA, HRA)
   - Configure contribution schedule (per-paycheck, lump sum)
5. **Carryover Configuration**:
   - Set CarryoverAmount limits (FSA: $640 max, HSA: 100%)
   - Configure grace period (optional 2.5 months)
6. **Card Issuance**: Generate payment card if applicable
7. **Account Activation**: Set `OpenedDate`, enable transactions

### Key Entities
- `ReimbursementAccount.cs`: Master account record
- `FlexPlan`: Plan type and configuration
- `PlanYear`: Time boundaries and year-end rules
- `RolloverSettings`: Carryover/grace period rules

### Business Rules
- FSA requires election amount upfront (pre-fund rule)
- HSA requires qualified health plan (HDHP)
- HRA is employer-funded only (no employee contributions)
- Dependent Care FSA: $5,000 annual limit per household

### Code Locations
- **Enrollment**: `ReimbursementAccounts.Lib/Domain/`
- **Plan Configuration**: `FlexPlanDto.cs`, `PlanYearDto.cs`
- **Validation**: IRS limits should be validated (COMPLIANCE GAP)

---

## 2. Contribution Processing Workflow

### Purpose
Process employee/employer contributions, update account balances, and maintain ledger records.

### Steps
1. **Contribution Trigger**:
   - Payroll deduction (FSA, Dependent Care)
   - Employer deposit (HSA, HRA)
   - Manual adjustment
2. **Amount Validation**:
   - Check against annual limits (FSA: $3,200, HSA: $4,150/$8,300)
   - Verify plan year dates
   - Validate employer match rules (HSA)
3. **Ledger Update**:
   - Create `PercentPlanLedgerEntry` (percentage-based plans)
   - Update `AvailableBalance`
   - Track `ContributionToDate`
4. **Cash-In Processing**:
   - Create `CashInItem` record
   - Update global contribution limits (if applicable)
5. **Notification**: Confirm contribution to employee

### Key Entities
- `PercentPlanLedgerEntry.cs`: Transaction ledger
- `CashInItem.cs`: Contribution records
- `GlobalContributionLimits.cs`: IRS annual limits
- `BalanceDto.cs`: Current available balance

### Business Rules
- **FSA Pre-Fund**: Full election available immediately (even if not contributed yet)
- **HSA Post-Fund**: Only contributed amounts available
- **Catch-Up Contributions**: HSA allows $1,000 extra for age 55+
- **Contribution Deadlines**: Must occur within plan year (or grace period)

### Code Locations
- **Contribution Processing**: `PercentPlanLedgerEntry.cs`, `CashInItem.cs`
- **Balance Calculation**: `BalanceDto.cs`, `AvailableBalance` property
- **Limits Validation**: MISSING (compliance gap - no IRS limit validation found)

### Compliance Gaps
- ⚠️ **P0 Issue**: No validation found for IRS contribution limits ($3,200 FSA, $4,150 HSA)
- ⚠️ **P1 Issue**: Catch-up contribution logic not evident in code

---

## 3. Manual Claims Processing Workflow

### Purpose
Reimburse employee for out-of-pocket medical expenses after manual claim submission and approval.

### Steps
1. **Claim Submission**:
   - Employee submits expense receipt
   - Provides expense date, amount, description
   - Attaches supporting documentation
2. **Claim Validation**:
   - Verify expense date within plan year
   - Check expense type against eligible list (IRS Publication 502)
   - Validate sufficient `AvailableBalance`
3. **Claim Review**:
   - Administrator reviews documentation
   - Approves/denies claim
   - Records `PatientResponsibilityAmount` (if partial approval)
4. **Payment Processing**:
   - Create `ClaimTransferLine` (links claim to payment)
   - Deduct from `AvailableBalance`
   - Update `AmountRemainingToBeReimbursed`
   - Issue payment (direct deposit, check, or card reload)
5. **Ledger Update**:
   - Record claim transaction
   - Update year-to-date reimbursement totals
6. **Notification**: Confirm payment to employee

### Key Entities
- `ClaimTransferLine.cs`: Claim-to-payment linkage
- `PatientResponsibilityAmount`: Employee portion (if any)
- `AmountRemainingToBeReimbursed`: Outstanding claim balance
- `BalanceDto.cs`: Post-claim balance

### Business Rules
- **Incurred Date Rule**: Expense must occur during plan year (or grace period)
- **Eligible Expenses**: Must match IRS Publication 502 list
- **Over-The-Counter (OTC)**: Requires prescription for most OTC drugs (IRS rule)
- **Substantiation**: Receipt must show date, provider, amount, service description

### Code Locations
- **Claims Processing**: `ClaimTransferLine.cs`
- **Balance Updates**: `BalanceDto.cs`
- **Eligible Expense Validation**: NOT FOUND (compliance gap)

### Compliance Gaps
- ⚠️ **P0 Issue**: No code found validating eligible expenses against IRS Publication 502
- ⚠️ **P2 Issue**: Substantiation requirements not enforced in code

---

## 4. Auto-Pay Claims Workflow

### Purpose
Automatically approve and reimburse claims from pre-approved providers (e.g., pharmacy, doctor's office).

### Steps
1. **Provider Submission**:
   - Provider submits claim via EDI/API
   - Includes expense date, amount, service codes
2. **Auto-Approval Rules**:
   - Verify provider is on approved list
   - Check service codes against eligible list
   - Validate claim amount matches Expected Payment Amount (EPA)
3. **Balance Check**:
   - Verify sufficient `AvailableBalance`
   - If insufficient, create `AmountRemainingToBeReimbursed` (partial payment)
4. **Automatic Payment**:
   - Create `ClaimTransferLine`
   - Deduct from `AvailableBalance`
   - Issue payment to provider (ACH)
5. **Employee Notification**: Inform employee of auto-paid claim

### Key Entities
- `ClaimTransferLine.cs`: Auto-pay claim record
- `AmountRemainingToBeReimbursed`: Pending balance (if insufficient funds)
- `BalanceDto.cs`: Updated balance

### Business Rules
- **Provider Approval**: Only pre-approved providers can use auto-pay
- **Service Code Validation**: Must match eligible expense codes
- **Expected Payment Amount (EPA)**: Claim amount must match EPA from clearinghouse
- **Insufficient Funds**: Create pending claim if balance too low

### Code Locations
- **Auto-Pay Processing**: Spike document references "AutoPayClaimsBugInvestigation.docx"
- **Balance Validation**: `BalanceDto.cs`
- **Pending Claims**: `AmountRemainingToBeReimbursed`

### Known Issues
- **Bug**: Spike document "AutoPayClaimsBugInvestigation.docx" suggests existing defects in auto-pay logic

---

## 5. Card Transaction Workflow

### Purpose
Process real-time payment card transactions at point-of-sale (POS) or online merchants.

### Steps
1. **Card Swipe/Entry**:
   - Employee uses payment card at pharmacy, doctor, etc.
   - Merchant submits authorization request
2. **Real-Time Validation**:
   - Verify card is active
   - Check `AvailableBalance` >= transaction amount
   - Validate merchant category code (MCC) for healthcare
3. **Authorization**:
   - Approve transaction (if valid)
   - Create temporary hold on `AvailableBalance`
4. **Settlement**:
   - Merchant submits final transaction (typically 1-3 days later)
   - Deduct from `AvailableBalance`
   - Create card transaction record
5. **Substantiation** (if required):
   - Request receipt from employee for non-auto-substantiated transactions
   - Employee uploads receipt
   - Administrator reviews and approves

### Key Entities
- `CardTransactionDto.cs`: Transaction record
- `BalanceDto.cs`: Real-time balance updates
- MCC validation (Merchant Category Codes)

### Business Rules
- **Merchant Category Codes**: Only healthcare MCCs allowed (e.g., 5912 pharmacies, 8011 doctors)
- **Inventory Information Approval System (IIAS)**: Auto-substantiate eligible items (e.g., prescription drugs)
- **Manual Substantiation**: Non-IIAS transactions require receipt within 30-90 days
- **Card Suspension**: Card disabled if substantiation overdue

### Code Locations
- **Card Processing**: `CardTransactionDto.cs`
- **Balance Updates**: `BalanceDto.cs`
- **MCC Validation**: NOT FOUND (likely in payment processor integration)

### Compliance Gaps
- ⚠️ **P1 Issue**: Substantiation tracking logic not evident in code

---

## 6. Year-End Carry Over Workflow

### Purpose
Process end-of-plan-year balances, apply carryover/forfeiture rules, and transfer eligible amounts to new plan year.

### Steps
1. **Plan Year End Trigger**:
   - Background job detects `PlanYearEndDate` reached
   - Initiates carry-over process
2. **Balance Calculation**:
   - Calculate final `AvailableBalance` for plan year
   - Deduct pending claims (`AmountRemainingToBeReimbursed`)
   - Apply grace period extensions (if configured)
3. **Carryover Rule Application**:
   - **FSA**: Maximum $640 carryover (2025 IRS limit)
   - **HSA**: 100% rollover (no limit)
   - **HRA**: Employer-defined carryover rules
   - **Dependent Care FSA**: No carryover (use-it-or-lose-it)
4. **Forfeiture Calculation**:
   - Amount exceeding carryover limit
   - Create forfeiture record (employer recaptures funds)
5. **Transfer Processing**:
   - Create `CarryoverTransferTrackingDto` record
   - Link old plan year to new plan year
   - Update new year's `AvailableBalance` with carryover amount
6. **Batch Processing**:
   - Process 1,000 accounts per batch (per spike document)
   - Allow 10 concurrent batch operations
   - Monitor performance (V1 slow, V2 optimized)

### Key Entities
- `CarryoverTransferTrackingDto.cs`: Tracks carry-over transactions
- `RolloverSettingDto.cs`: Carryover rules per plan type
- `PlanYear`: Year boundaries
- `BalanceDto.cs`: Updated balances

### Business Rules
- **FSA Carryover vs. Grace Period**: Employer chooses one or the other (not both)
- **Grace Period**: 2.5 months post-year-end to spend prior year funds
- **Forfeiture Rule**: Unused FSA funds go to employer (IRS "use-it-or-lose-it")
- **HSA Rollover**: Unlimited (funds belong to employee forever)

### Code Locations
- **Carry-Over Service**: `CarryoverDollarsDomainService.cs` (from spike document)
- **Transfer Tracking**: `CarryoverTransferTrackingDto.cs`
- **Rollover Settings**: `RolloverSettingDto.cs`
- **Batch Processing**: Background job (NServiceBus likely)

### Performance Considerations
- **V1 Performance**: Slow (per spike document "carryover logic.docx")
- **V2 Optimization**: 1,000 account batches, 10 concurrent operations
- **Database Impact**: Heavy reads/writes during year-end processing

### Known Issues
- **Spike Document**: "carryover logic.docx" and "carryover logic v2.docx" suggest prior performance issues

---

## 7. Statement Generation Workflow

### Purpose
Generate monthly/quarterly account statements showing contributions, claims, balances, and transactions.

### Steps
1. **Statement Schedule Trigger**:
   - Background job runs monthly/quarterly
   - Identifies accounts requiring statements
2. **Data Aggregation**:
   - Retrieve all transactions for statement period
   - Calculate opening balance, closing balance
   - Summarize contributions, claims, fees
3. **Statement Composition**:
   - Generate PDF with account details
   - Include transaction history
   - Show year-to-date totals
   - Display IRS contribution limits and usage
4. **Rate Schedule Application**:
   - Use `RateScheduleStartDate` to determine fee schedule
   - **BUG**: Code incorrectly uses `OpenedDate` instead (per spike document)
5. **Delivery**:
   - Email PDF to employee
   - Post to online portal
   - Archive for compliance (7 years)

### Key Entities
- `RateScheduleStartDate`: Correct date for fee schedule (NOT `OpenedDate`)
- `BalanceDto.cs`: Statement balance snapshot
- Statement generation service (not in AST output)

### Business Rules
- **Statement Frequency**: Monthly or quarterly (employer choice)
- **Transaction Detail**: All contributions, claims, adjustments, fees
- **Year-to-Date Totals**: Required for employee tax reporting
- **Retention**: 7-year archive for HIPAA/IRS compliance

### Code Locations
- **Statement Generation**: Service not identified in AST output
- **Rate Schedule**: `RateScheduleStartDate` field (misused per spike)
- **Balance Queries**: `BalanceDto.cs`

### Known Issues
- ⚠️ **P0 BUG**: Spike document "StatementsNotDisplayingAllTransactions.docx" reports:
  - Code uses `OpenedDate` instead of `RateScheduleStartDate`
  - Causes statements to exclude transactions before 2025-01-01 for pre-2025 accounts

---

## Cross-Workflow Dependencies

### Shared Entities
- `ReimbursementAccount.cs`: Master record used by ALL workflows
- `BalanceDto.cs`: Real-time balance used by contributions, claims, cards, carry-over
- `PlanYear`: Time boundaries for enrollment, claims, carry-over
- `FlexPlan`: Plan type rules used across all workflows

### Data Flow
1. **Enrollment** → Creates account → Enables contributions
2. **Contributions** → Update balance → Enables claims/cards
3. **Claims/Cards** → Deduct balance → Affects carry-over calculation
4. **Carry-Over** → Transfers balance → Starts new plan year cycle
5. **Statements** → Reports all activity → Compliance audit trail

### Integration Points
- **Payroll System**: Contribution deductions
- **Payment Processor**: Card transactions (MCC validation, IIAS)
- **Claims Clearinghouse**: Auto-pay claims (EDI, EPA)
- **Banking System**: ACH payments for claims
- **Email/Portal**: Statement delivery

---

## Workflow Performance Metrics

### High-Volume Operations
1. **Card Transactions**: Real-time (< 2 seconds response required)
2. **Carry-Over Processing**: Batch (1,000 accounts per batch, 10 concurrent)
3. **Statement Generation**: Batch (monthly/quarterly, thousands of accounts)

### Performance Risks
- **Carry-Over**: V1 had performance issues (V2 optimized)
- **Statement Generation**: Database-intensive (all transactions query)
- **Card Authorizations**: Network latency to payment processor

---

## Compliance & Regulatory Touchpoints

### IRS Requirements
- **Contribution Limits**: FSA $3,200, HSA $4,150/$8,300, Dependent Care $5,000 (2025)
- **Carryover Limits**: FSA $640 max (indexed annually)
- **Eligible Expenses**: IRS Publication 502
- **Tax Reporting**: Form W-2 (FSA), Form 1099-SA (HSA)

### HIPAA Requirements
- **PHI Protection**: Account balances, claims, transactions (all PHI)
- **Data Retention**: 7 years minimum
- **Access Logging**: Audit trail for all PHI access

### PCI-DSS (Payment Card)
- **Card Data Security**: PAN encryption, tokenization
- **Transaction Logging**: All card activity auditable

---

## Testing Recommendations

### Workflow-Level Tests
1. **End-to-End Scenarios**: Test complete workflow from start to finish
2. **Cross-Plan-Type Testing**: Verify rules for FSA, HSA, HRA, Dependent Care
3. **Year-End Testing**: Carry-over with various balance scenarios
4. **Edge Cases**: Grace period boundaries, zero balances, overpayments

### Integration Tests
1. **Payroll Integration**: Contribution deduction synchronization
2. **Payment Processor**: Card authorization/settlement cycle
3. **Claims Clearinghouse**: EDI claim submission/approval

### Performance Tests
1. **Carry-Over Batch**: 10,000+ accounts end-of-year processing
2. **Card Transaction Load**: 1,000 concurrent authorizations
3. **Statement Generation**: 50,000+ statements in 24 hours

---

## Identified Gaps & Risks

### Code Gaps
1. ⚠️ **IRS Limit Validation**: No code found enforcing contribution limits (P0)
2. ⚠️ **Eligible Expense Validation**: No IRS Publication 502 lookup (P0)
3. ⚠️ **Catch-Up Contributions**: Age 55+ HSA logic not evident (P1)
4. ⚠️ **Substantiation Tracking**: Card transaction substantiation not clear (P1)

### Known Bugs
1. ⚠️ **Statement Date Bug**: Uses `OpenedDate` instead of `RateScheduleStartDate` (P0)
2. ⚠️ **Auto-Pay Claims**: Spike document suggests existing bugs (P1)

### Performance Risks
1. ⚠️ **Carry-Over V1**: Known slow performance (V2 optimized)
2. ⚠️ **Statement Queries**: All transactions query potentially slow

---

## Next Steps

1. **Extract Workflow Code**: Run AST scanners to locate workflow implementation classes
2. **Validate Business Rules**: Cross-reference IRS regulations with code logic
3. **Map Integration Points**: Identify external system APIs (payroll, payment processor)
4. **Performance Testing**: Benchmark carry-over and statement generation batch jobs
5. **Compliance Audit**: Verify IRS/HIPAA/PCI-DSS requirements in code

---

**Document Status**: COMPLETE  
**Related Docs**: `complete-business-domain-map.md`, `business-glossary.md`, `plan-types-comprehensive.md`
