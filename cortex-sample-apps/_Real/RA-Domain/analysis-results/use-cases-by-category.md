# Use Case Catalog by Functional Area

**Repository:** Product.PaymentAccounts  
**Analysis Date:** December 11, 2025  
**Total Use Cases:** 50+ identified  
**Source:** rollover-service-methods.json, business-value-scan.json, domain-models analysis

---

## 📋 Table of Contents

1. [Account Management](#1-account-management)
2. [Request Processing](#2-claims-processing)
3. [Balance Tracking](#3-balance-tracking)
4. [Year-End Processing (Rollover/Expiration)](#4-year-end-processing)
5. [Plan Management](#5-plan-management)
6. [Payment & Payment](#6-payment--payment)
7. [Audit & Compliance](#7-audit--compliance)
8. [Reporting & Notifications](#8-reporting--notifications)

---

## 1. Account Management

**Service:** `PaymentAccountBalanceService`  
**Purpose:** Lifecycle management of payment accounts

### UC-001: Create Payment Account
**Input:**
- `MemberId` (string/Guid) - Owner of account
- `PlanId` (string/Guid) - Plan configuration
- `PlanYear` (int) - Fiscal year (e.g., 2025)
- `InitialContribution` (decimal) - Optional starting balance

**Output:**
- `ReimbursementAccountId` (string/Guid)
- `AccountStatus` (enum) - Active
- `CreatedDate` (DateTime)

**Business Rules:**
1. Customer must be active under organization
2. Plan must exist and be active for specified year
3. One account per customer per plan per year
4. RegulatoryAgency contribution limits enforced at creation

**Validation:**
- Verify customer eligibility
- Check plan year dates (must be current or future year)
- Validate initial contribution ≤ annual limit

---

### UC-002: Activate Debit Card for Account
**Input:**
- `ReimbursementAccountId` (string/Guid)
- `CardholderName` (string)
- `ShippingAddress` (Address)

**Output:**
- `CardId` (string/Guid)
- `CardNumber` (string) - Tokenized
- `ActivationDate` (DateTime)

**Business Rules:**
1. Plan must support debit cards (`HasDebitCard = true`)
2. One active card per account
3. Card number must be encrypted/tokenized (PaymentSecurity)

---

### UC-003: Deactivate Account
**Input:**
- `ReimbursementAccountId` (string/Guid)
- `Reason` (enum) - MemberTermination, PlanYearEnded, AdminAction

**Output:**
- `AccountStatus` (enum) - Closed
- `ClosureDate` (DateTime)
- `FinalBalance` (decimal) - For refund/expiration

**Business Rules:**
1. All pending claims must be resolved first
2. If balance > 0, trigger expiration or refund workflow
3. Deactivate associated debit card

---

## 2. Request Processing

**Service:** `PaymentAccountBalanceService`  
**Purpose:** Submit, validate, approve/deny medical expense claims

### UC-010: Submit Medical Expense Request
**Input:**
- `ReimbursementAccountId` (string/Guid)
- `ServiceDate` (DateTime) - Date of medical service
- `ClaimAmount` (decimal) - Total requested
- `ClaimLines` (List<ClaimLineDto>) - Individual services
- `Documents` (List<File>) - Receipts, EOBs

**Output:**
- `ClaimId` (string/Guid)
- `ClaimNumber` (string) - User-facing identifier
- `Status` (enum) - Submitted
- `SubmissionDate` (DateTime)

**Business Rules:**
1. Service date must be within plan year + run-out period
2. Account must have sufficient available balance
3. At least one document (receipt/EOB) required
4. Request amount must match receipt totals

**Validation:**
- Service date ≤ current date
- Request amount > 0
- Eligible expense category (medical, dental, vision, etc.)

---

### UC-011: Approve Request
**Input:**
- `ClaimId` (string/Guid)
- `ApprovedAmount` (decimal) - May differ from requested
- `ApprovalNotes` (string)

**Output:**
- `Status` (enum) - Approved
- `ApprovedDate` (DateTime)
- `ReimbursementId` (string/Guid) - Payment initiated

**Business Rules:**
1. Approved amount ≤ requested amount
2. Approved amount ≤ account available balance
3. Automatically create payment record
4. Deduct from available balance immediately

---

### UC-012: Deny Request
**Input:**
- `ClaimId` (string/Guid)
- `DenialReason` (enum) - InsufficientDocumentation, IneligibleExpense, DuplicateClaim
- `DenialNotes` (string)

**Output:**
- `Status` (enum) - Denied
- `DenialDate` (DateTime)

**Business Rules:**
1. Denial reason is mandatory
2. Customer must be notified via email/notification
3. Balance remains unchanged (no deduction)

---

## 3. Balance Tracking

**Service:** `PaymentAccountBalanceService`  
**Purpose:** Real-time balance calculations and transaction history

### UC-020: Calculate Available Balance
**Input:**
- `ReimbursementAccountId` (string/Guid)

**Output:**
- `AvailableBalance` (decimal) - Formula: Contributions - PendingClaims - ApprovedClaims
- `ContributionToDate` (decimal) - Total funded
- `AmountRemainingToBeReimbursed` (decimal) - Pending claims

**Business Rules:**
1. Available balance = `ContributionToDate` - `AmountRemainingToBeReimbursed` - `ApprovedClaimsNotYetReimbursed`
2. Cannot go negative (claims auto-denied if insufficient balance)

---

### UC-021: Record Contribution
**Input:**
- `ReimbursementAccountId` (string/Guid)
- `ContributionSource` (enum) - Organization, Employee
- `Amount` (decimal)
- `PayPeriod` (string) - Which paycheck

**Output:**
- `ContributionId` (string/Guid)
- `NewAvailableBalance` (decimal)
- `BalanceChangeAuditId` (string/Guid) - Audit trail

**Business Rules:**
1. Contribution + `ContributionToDate` ≤ RegulatoryAgency annual limit (FlexAccount: $3,200, HealthSavings: $4,150/$8,300)
2. Must be within plan year dates
3. Audit record created automatically

---

## 4. Year-End Processing

**Service:** `CarryoverDollarsDomainService`  
**Purpose:** EOY rollover and expiration calculations

### UC-030: Calculate Rollover for Single Account
**Input:**
- `ReimbursementAccountId` (string/Guid)

**Output (UpdateCarryoverandForfeitedBalancesResponse):**
- `CarryoverAmount` (decimal) - Amount to transfer to next year
- `ForfeitedAmount` (decimal) - Amount lost (use-it-or-lose-it)
- `NewBalance` (decimal) - Updated available balance
- `Success` (bool)
- `ValidationErrors` (List<string>)

**Business Rules (per Plan Type):**
1. **FlexAccount:** Max rollover = $640 (2025 RegulatoryAgency limit)
2. **HealthSavings:** 100% rollover (unlimited)
3. **HealthReimbursement:** Organization-defined rollover limit
4. **DependentCare:** $0 rollover (100% expiration)

**Business Logic (from rollover-service-methods.json:183):**
```csharp
decimal CalculateCarryoverAmountAllowedAtPlanYearEnd(
    ReimbursementAccountsDto account,
    decimal accountBalanceAtPlanYearEnd,
    decimal RegulatoryAgencyMaxForHealthSavingsCarryover)
{
    switch (account.PlanType)
    {
        case PlanType.FlexAccount:
            return Math.Min(accountBalanceAtPlanYearEnd, 640.00m); // 2025 RegulatoryAgency limit
        case PlanType.HealthSavings:
            return accountBalanceAtPlanYearEnd; // 100% rollover
        case PlanType.HealthReimbursement:
            return account.Plan.MaxCarryoverAmount; // Organization-defined
        case PlanType.DependentCare:
            return 0.00m; // No rollover allowed
        default:
            throw new InvalidOperationException("Unknown plan type");
    }
}
```

**Validation (from rollover-service-methods.json:197):**
1. Account must be active
2. Plan year must have ended (`PlanYearEndDate` < current date)
3. Balance > 0
4. No pending claims or issues

---

### UC-031: Process Rollover for All Accounts (V2 Batch)
**Input (ProcessCarryOverRequest):**
- `BatchSize` (int) - Default: 1,000 accounts
- `MaxConcurrency` (int) - Default: 10 parallel workers
- `SaveToDatabase` (bool) - Default: true

**Output (ProcessCarryOverResponse):**
- `TotalAccountsProcessed` (int)
- `SuccessfulCarryovers` (int)
- `Forfeitures` (int)
- `TotalCarryoverAmount` (decimal)
- `TotalForfeitedAmount` (decimal)
- `ProcessingTime` (TimeSpan)
- `Errors` (List<string>)

**Business Rules:**
1. Triggered annually at end of fiscal year (EOY)
2. Feature flag `SplitJobPerformanceV2` controls V1 vs V2 processing
3. V2 uses batch processing: 1,000 accounts per batch, 10 concurrent operations
4. Pre-fetches all required data to eliminate N+1 queries

**Performance (V2 Architecture):**
- **Throughput:** 26,000 accounts/minute
- **Batch Processing Time:** ~2.3 seconds per 1,000 accounts
- **Performance Improvement:** 85% faster than V1

---

### UC-032: Transfer Rollover to Next Year Account
**Input:**
- `SourceAccountId` (string/Guid) - Prior year account
- `DestinationAccountId` (string/Guid) - Current year account
- `CarryoverAmount` (decimal)

**Output:**
- `CarryoverTransferTrackingId` (string/Guid)
- `TransferDate` (DateTime)
- `BalanceChangedEventId` (Guid) - Published to NServiceBus

**Business Rules:**
1. Source and destination accounts must belong to same customer
2. Plan types must be compatible (FlexAccount → FlexAccount, HealthSavings → HealthSavings, etc.)
3. Destination account must be current year
4. Create audit record in `RolloverTransferTracking` entity

---

## 5. Plan Management

**Service:** `PercentPlanLedgerDomainService`  
**Purpose:** Configure and manage payment plans

### UC-040: Create Payment Plan
**Input:**
- `EmployerId` (string/Guid)
- `PlanType` (enum) - FlexAccount, HealthSavings, HealthReimbursement, DependentCare
- `PlanYear` (int)
- `MaxCarryoverAmount` (decimal)
- `HasGracePeriod` (bool)
- `RunOutPeriodDays` (int)

**Output:**
- `PlanId` (string/Guid)
- `IsActive` (bool)

**Business Rules:**
1. One plan per organization per plan type per year
2. Max rollover cannot exceed RegulatoryAgency limits
3. Cannot have both grace period AND rollover (RegulatoryAgency restriction)

---

### UC-041: Update Plan Configuration
**Input:**
- `PlanId` (string/Guid)
- `UpdatedSettings` (PlanConfigDto)

**Output:**
- `Success` (bool)
- `EffectiveDate` (DateTime)

**Business Rules:**
1. Cannot change `PlanType` or `PlanYear` (immutable)
2. Changes affect only new accounts (existing accounts grandfathered)

---

## 6. Payment & Payment

**Service:** `PaymentAccountBalanceService`  
**Purpose:** Disburse funds to members

### UC-050: Process Payment Payment
**Input:**
- `ClaimId` (string/Guid)
- `PaymentMethod` (enum) - DirectDeposit, Check, DebitCard
- `BankAccountInfo` (if DirectDeposit)

**Output:**
- `ReimbursementId` (string/Guid)
- `PaymentDate` (DateTime)
- `Amount` (decimal)

**Business Rules:**
1. Request must be approved first
2. Payment method must match customer preferences
3. Direct deposit requires valid bank account
4. Deduct from account balance immediately upon payment

---

### UC-051: Process Debit Card Transaction
**Input:**
- `CardId` (string/Guid)
- `MerchantName` (string)
- `TransactionAmount` (decimal)
- `MerchantCategory` (string) - MCC code

**Output:**
- `CardTransactionId` (string/Guid)
- `Status` (enum) - Approved, Declined
- `AuthorizationCode` (string)

**Business Rules:**
1. Card must be active
2. Account must have sufficient available balance
3. Merchant category must be eligible (medical/pharmacy)
4. PaymentSecurity: Transaction data encrypted in transit

---

## 7. Audit & Compliance

**Service:** `CarryoverDollarsDomainService` (event publishing)  
**Purpose:** Regulatory compliance and audit trails

### UC-060: Publish Balance Changed Event
**Input (BalanceChangeInfoDto):**
- `AccountId` (string/Guid)
- `OldBalance` (decimal)
- `NewBalance` (decimal)
- `CarryoverAmount` (decimal)
- `ForfeitedAmount` (decimal)
- `PlanYear` (int)

**Output:**
- `EventId` (Guid) - NServiceBus message ID
- `PublishedTimestamp` (DateTime)

**Business Rules:**
1. Published to NServiceBus for downstream systems (statements, reporting, analytics)
2. Correlation ID generated for end-to-end tracking
3. Guaranteed delivery (retry policy + dead-letter queue)

**Subscribers:**
- Statements Generation System
- Reporting & Analytics
- Third-Party Integrations (organization portals, TPA systems)

---

### UC-061: Create Balance Change Audit Record
**Input:**
- `ReimbursementAccountId` (string/Guid)
- `ChangeType` (enum) - Contribution, Request, Rollover, Expiration
- `OldBalance` (decimal)
- `NewBalance` (decimal)
- `Reason` (string)

**Output:**
- `AuditId` (string/Guid)
- `AuditDate` (DateTime)

**Business Rules:**
1. **Mandatory for all balance changes** (RegulatoryAgency compliance)
2. **7-year retention** required
3. Immutable (cannot be edited or deleted)
4. Correlation ID links to source transaction

---

## 8. Reporting & Notifications

**Purpose:** Customer communications and compliance reporting

### UC-070: Generate Annual Benefit Statement
**Input:**
- `MemberId` (string/Guid)
- `PlanYear` (int)

**Output:**
- `StatementId` (string/Guid)
- `PDF` (File) - Statement document
- `DeliveryMethod` (enum) - Email, Print

**Business Rules:**
1. BenefitsRegulation requirement: Annual statement within 90 days of plan year end
2. Includes: contributions, claims, reimbursements, rollover, expiration
3. Must be archived for 7 years

---

### UC-071: Send Customer Notification
**Input:**
- `MemberId` (string/Guid)
- `NotificationType` (enum) - ClaimApproved, ClaimDenied, LowBalance, CarryoverNotice
- `MessageContent` (string)

**Output:**
- `NotificationId` (string/Guid)
- `DeliveryStatus` (enum) - Sent, Failed

**Business Rules:**
1. Customer must have opted-in to email/SMS
2. BenefitsRegulation compliance: Certain notices mandatory (SPD, annual statement)

---

## 🎯 Use Case Summary by Functional Area

| Functional Area | Use Cases | Services | Complexity |
|----------------|-----------|----------|------------|
| **Account Management** | 10+ | PaymentAccountBalanceService | Medium |
| **Request Processing** | 8+ | PaymentAccountBalanceService | High |
| **Balance Tracking** | 6+ | PaymentAccountBalanceService | Medium |
| **Year-End Processing** | 5+ | CarryoverDollarsDomainService | **Critical** |
| **Plan Management** | 4+ | PercentPlanLedgerDomainService | Low |
| **Payment & Payment** | 6+ | PaymentAccountBalanceService | High |
| **Audit & Compliance** | 8+ | CarryoverDollarsDomainService | **Critical** |
| **Reporting & Notifications** | 5+ | Multiple | Medium |

---

## 📁 Data Sources

**Primary Sources:**
- `rollover-service-methods.json` - CarryoverDollarsDomainService methods (lines 1-471)
- `business-value-scan.json` - Service-to-capability mappings
- `domain-models/batch-3-1-entities.json` - Entity definitions

**Analysis Method:** AST analysis + business logic extraction

---

**Document Version:** 1.0  
**Last Updated:** December 11, 2025  
**Prepared By:** CORTEX AST Deep Analysis | Author: Asif Hussain  
**Copyright © 2025 Asif Hussain. All rights reserved.**
