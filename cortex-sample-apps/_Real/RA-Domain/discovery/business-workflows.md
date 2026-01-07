# Business Workflows - Payment Accounts

**Generated**: December 2024  
**Source**: AST Analysis + Spike Documents  
**Target**: Product.Example Repository

---

## Overview

This document maps the 7 major end-to-end business workflows identified in the Payment Accounts system. Each workflow represents a complete business process from initiation to completion, spanning multiple functional areas and plan types.

---

## 1. Registration & Account Setup Workflow

### Purpose
Establish a new payment account for an employee, configure plan parameters, and activate for use.

### Steps
1. **Employee Selection**: HR/benefits administrator selects employee
2. **Plan Type Selection**: Choose FlexAccount, HealthSavings, HealthReimbursement, or DependentCare FlexAccount
3. **Plan Year Configuration**: Set PlanYearStartDate, PlanYearEndDate
4. **Contribution Setup**:
   - Employee pre-tax deductions (FlexAccount, DependentCare)
   - Organization contributions (HealthSavings, HealthReimbursement)
   - Configure contribution schedule (per-paycheck, lump sum)
5. **Rollover Configuration**:
   - Set CarryoverAmount limits (FlexAccount: $640 max, HealthSavings: 100%)
   - Configure grace period (optional 2.5 months)
6. **Card Issuance**: Generate payment card if applicable
7. **Account Activation**: Set `OpenedDate`, enable transactions

### Key Entities
- `PaymentAccount.cs`: Master account record
- `FlexPlan`: Plan type and configuration
- `PlanYear`: Time boundaries and year-end rules
- `RolloverSettings`: Rollover/grace period rules

### Business Rules
- FlexAccount requires election amount upfront (pre-fund rule)
- HealthSavings requires qualified health plan (HDHP)
- HealthReimbursement is organization-funded only (no employee contributions)
- DependentCare FlexAccount: $5,000 annual limit per household

### Code Locations
- **Registration**: `PaymentAccounts.Lib/Domain/`
- **Plan Configuration**: `FlexPlanDto.cs`, `PlanYearDto.cs`
- **Validation**: RegulatoryAgency limits should be validated (COMPLIANCE GAP)

---

## 2. Contribution Processing Workflow

### Purpose
Process employee/organization contributions, update account balances, and maintain ledger records.

### Steps
1. **Contribution Trigger**:
   - Payroll deduction (FlexAccount, DependentCare)
   - Organization deposit (HealthSavings, HealthReimbursement)
   - Manual adjustment
2. **Amount Validation**:
   - Check against annual limits (FlexAccount: $3,200, HealthSavings: $4,150/$8,300)
   - Verify plan year dates
   - Validate organization match rules (HealthSavings)
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
- `GlobalContributionLimits.cs`: RegulatoryAgency annual limits
- `BalanceDto.cs`: Current available balance

### Business Rules
- **FlexAccount Pre-Fund**: Full election available immediately (even if not contributed yet)
- **HealthSavings Post-Fund**: Only contributed amounts available
- **Catch-Up Contributions**: HealthSavings allows $1,000 extra for age 55+
- **Contribution Deadlines**: Must occur within plan year (or grace period)

### Code Locations
- **Contribution Processing**: `PercentPlanLedgerEntry.cs`, `CashInItem.cs`
- **Balance Calculation**: `BalanceDto.cs`, `AvailableBalance` property
- **Limits Validation**: MISSING (compliance gap - no RegulatoryAgency limit validation found)

### Compliance Gaps
- ⚠️ **P0 Issue**: No validation found for RegulatoryAgency contribution limits ($3,200 FlexAccount, $4,150 HealthSavings)
- ⚠️ **P1 Issue**: Catch-up contribution logic not evident in code

---

## 3. Manual Request Processing Workflow

### Purpose
Reimburse employee for out-of-pocket medical expenses after manual request submission and approval.

### Steps
1. **Request Submission**:
   - Employee submits expense receipt
   - Provides expense date, amount, description
   - Attaches supporting documentation
2. **Request Validation**:
   - Verify expense date within plan year
   - Check expense type against eligible list (RegulatoryAgency Publication 502)
   - Validate sufficient `AvailableBalance`
3. **Request Review**:
   - Administrator reviews documentation
   - Approves/denies request
   - Records `PatientResponsibilityAmount` (if partial approval)
4. **Payment Processing**:
   - Create `ClaimTransferLine` (links request to payment)
   - Deduct from `AvailableBalance`
   - Update `AmountRemainingToBeReimbursed`
   - Issue payment (direct deposit, check, or card reload)
5. **Ledger Update**:
   - Record request transaction
   - Update year-to-date payment totals
6. **Notification**: Confirm payment to employee

### Key Entities
- `ClaimTransferLine.cs`: Request-to-payment linkage
- `PatientResponsibilityAmount`: Employee portion (if any)
- `AmountRemainingToBeReimbursed`: Outstanding request balance
- `BalanceDto.cs`: Post-request balance

### Business Rules
- **Incurred Date Rule**: Expense must occur during plan year (or grace period)
- **Eligible Expenses**: Must match RegulatoryAgency Publication 502 list
- **Over-The-Counter (OTC)**: Requires prescription for most OTC drugs (RegulatoryAgency rule)
- **Substantiation**: Receipt must show date, provider, amount, service description

### Code Locations
- **Request Processing**: `ClaimTransferLine.cs`
- **Balance Updates**: `BalanceDto.cs`
- **Eligible Expense Validation**: NOT FOUND (compliance gap)

### Compliance Gaps
- ⚠️ **P0 Issue**: No code found validating eligible expenses against RegulatoryAgency Publication 502
- ⚠️ **P2 Issue**: Substantiation requirements not enforced in code

---

## 4. Auto-Pay Requests Workflow

### Purpose
Automatically approve and reimburse claims from pre-approved providers (e.g., pharmacy, doctor's office).

### Steps
1. **Provider Submission**:
   - Provider submits request via EDI/API
   - Includes expense date, amount, service codes
2. **Auto-Approval Rules**:
   - Verify provider is on approved list
   - Check service codes against eligible list
   - Validate request amount matches Expected Payment Amount (EPA)
3. **Balance Check**:
   - Verify sufficient `AvailableBalance`
   - If insufficient, create `AmountRemainingToBeReimbursed` (partial payment)
4. **Automatic Payment**:
   - Create `ClaimTransferLine`
   - Deduct from `AvailableBalance`
   - Issue payment to provider (ACH)
5. **Employee Notification**: Inform employee of auto-paid request

### Key Entities
- `ClaimTransferLine.cs`: Auto-pay request record
- `AmountRemainingToBeReimbursed`: Pending balance (if insufficient funds)
- `BalanceDto.cs`: Updated balance

### Business Rules
- **Provider Approval**: Only pre-approved providers can use auto-pay
- **Service Code Validation**: Must match eligible expense codes
- **Expected Payment Amount (EPA)**: Request amount must match EPA from clearinghouse
- **Insufficient Funds**: Create pending request if balance too low

### Code Locations
- **Auto-Pay Processing**: Spike document references "AutoPayClaimsBugInvestigation.docx"
- **Balance Validation**: `BalanceDto.cs`
- **Pending Requests**: `AmountRemainingToBeReimbursed`

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

## 6. Year-End Rollover Workflow

### Purpose
Process end-of-plan-year balances, apply rollover/expiration rules, and transfer eligible amounts to new plan year.

### Steps
1. **Plan Year End Trigger**:
   - Background job detects `PlanYearEndDate` reached
   - Initiates carry-over process
2. **Balance Calculation**:
   - Calculate final `AvailableBalance` for plan year
   - Deduct pending claims (`AmountRemainingToBeReimbursed`)
   - Apply grace period extensions (if configured)
3. **Rollover Rule Application**:
   - **FlexAccount**: Maximum $640 rollover (2025 RegulatoryAgency limit)
   - **HealthSavings**: 100% rollover (no limit)
   - **HealthReimbursement**: Organization-defined rollover rules
   - **DependentCare FlexAccount**: No rollover (use-it-or-lose-it)
4. **Expiration Calculation**:
   - Amount exceeding rollover limit
   - Create expiration record (organization recaptures funds)
5. **Transfer Processing**:
   - Create `CarryoverTransferTrackingDto` record
   - Link old plan year to new plan year
   - Update new year's `AvailableBalance` with rollover amount
6. **Batch Processing**:
   - Process 1,000 accounts per batch (per spike document)
   - Allow 10 concurrent batch operations
   - Monitor performance (V1 slow, V2 optimized)

### Key Entities
- `CarryoverTransferTrackingDto.cs`: Tracks carry-over transactions
- `RolloverSettingDto.cs`: Rollover rules per plan type
- `PlanYear`: Year boundaries
- `BalanceDto.cs`: Updated balances

### Business Rules
- **FlexAccount Rollover vs. Grace Period**: Organization chooses one or the other (not both)
- **Grace Period**: 2.5 months post-year-end to spend prior year funds
- **Expiration Rule**: Unused FlexAccount funds go to organization (RegulatoryAgency "use-it-or-lose-it")
- **HealthSavings Rollover**: Unlimited (funds belong to employee forever)

### Code Locations
- **Carry-Over Service**: `ExampleDomainService.cs` (from spike document)
- **Transfer Tracking**: `CarryoverTransferTrackingDto.cs`
- **Rollover Settings**: `RolloverSettingDto.cs`
- **Batch Processing**: Background job (NServiceBus likely)

### Performance Considerations
- **V1 Performance**: Slow (per spike document "rollover logic.docx")
- **V2 Optimization**: 1,000 account batches, 10 concurrent operations
- **Database Impact**: Heavy reads/writes during year-end processing

### Known Issues
- **Spike Document**: "rollover logic.docx" and "rollover logic v2.docx" suggest prior performance issues

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
   - Display RegulatoryAgency contribution limits and usage
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
- **Statement Frequency**: Monthly or quarterly (organization choice)
- **Transaction Detail**: All contributions, claims, adjustments, fees
- **Year-to-Date Totals**: Required for employee tax reporting
- **Retention**: 7-year archive for PrivacyRegulation/RegulatoryAgency compliance

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
- `PaymentAccount.cs`: Master record used by ALL workflows
- `BalanceDto.cs`: Real-time balance used by contributions, claims, cards, carry-over
- `PlanYear`: Time boundaries for registration, claims, carry-over
- `FlexPlan`: Plan type rules used across all workflows

### Data Flow
1. **Registration** → Creates account → Enables contributions
2. **Contributions** → Update balance → Enables claims/cards
3. **Requests/Cards** → Deduct balance → Affects carry-over calculation
4. **Carry-Over** → Transfers balance → Starts new plan year cycle
5. **Statements** → Reports all activity → Compliance audit trail

### Integration Points
- **Payroll System**: Contribution deductions
- **Payment Processor**: Card transactions (MCC validation, IIAS)
- **Requests Clearinghouse**: Auto-pay claims (EDI, EPA)
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

### RegulatoryAgency Requirements
- **Contribution Limits**: FlexAccount $3,200, HealthSavings $4,150/$8,300, DependentCare $5,000 (2025)
- **Rollover Limits**: FlexAccount $640 max (indexed annually)
- **Eligible Expenses**: RegulatoryAgency Publication 502
- **Tax Reporting**: Form W-2 (FlexAccount), Form 1099-SA (HealthSavings)

### PrivacyRegulation Requirements
- **PHI Protection**: Account balances, claims, transactions (all PHI)
- **Data Retention**: 7 years minimum
- **Access Logging**: Audit trail for all PHI access

### PaymentSecurity (Payment Card)
- **Card Data Security**: PAN encryption, tokenization
- **Transaction Logging**: All card activity auditable

---

## Testing Recommendations

### Workflow-Level Tests
1. **End-to-End Scenarios**: Test complete workflow from start to finish
2. **Cross-Plan-Type Testing**: Verify rules for FlexAccount, HealthSavings, HealthReimbursement, DependentCare
3. **Year-End Testing**: Carry-over with various balance scenarios
4. **Edge Cases**: Grace period boundaries, zero balances, overpayments

### Integration Tests
1. **Payroll Integration**: Contribution deduction synchronization
2. **Payment Processor**: Card authorization/settlement cycle
3. **Requests Clearinghouse**: EDI request submission/approval

### Performance Tests
1. **Carry-Over Batch**: 10,000+ accounts end-of-year processing
2. **Card Transaction Load**: 1,000 concurrent authorizations
3. **Statement Generation**: 50,000+ statements in 24 hours

---

## Identified Gaps & Risks

### Code Gaps
1. ⚠️ **RegulatoryAgency Limit Validation**: No code found enforcing contribution limits (P0)
2. ⚠️ **Eligible Expense Validation**: No RegulatoryAgency Publication 502 lookup (P0)
3. ⚠️ **Catch-Up Contributions**: Age 55+ HealthSavings logic not evident (P1)
4. ⚠️ **Substantiation Tracking**: Card transaction substantiation not clear (P1)

### Known Bugs
1. ⚠️ **Statement Date Bug**: Uses `OpenedDate` instead of `RateScheduleStartDate` (P0)
2. ⚠️ **Auto-Pay Requests**: Spike document suggests existing bugs (P1)

### Performance Risks
1. ⚠️ **Carry-Over V1**: Known slow performance (V2 optimized)
2. ⚠️ **Statement Queries**: All transactions query potentially slow

---

## Next Steps

1. **Extract Workflow Code**: Run AST scanners to locate workflow implementation classes
2. **Validate Business Rules**: Cross-reference RegulatoryAgency regulations with code logic
3. **Map Integration Points**: Identify external system APIs (payroll, payment processor)
4. **Performance Testing**: Benchmark carry-over and statement generation batch jobs
5. **Compliance Audit**: Verify RegulatoryAgency/PrivacyRegulation/PaymentSecurity requirements in code

---

**Document Status**: COMPLETE  
**Related Docs**: `complete-business-domain-map.md`, `business-glossary.md`, `plan-types-comprehensive.md`
