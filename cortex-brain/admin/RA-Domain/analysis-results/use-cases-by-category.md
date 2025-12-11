# Use Case Catalog by Functional Area

**Repository:** Product.ReimbursementAccounts  
**Analysis Date:** December 11, 2025  
**Total Use Cases:** 50+ identified  
**Source:** carryover-service-methods.json, business-value-scan.json, domain-models analysis

---

## 📋 Table of Contents

1. [Account Management](#1-account-management)
2. [Claims Processing](#2-claims-processing)
3. [Balance Tracking](#3-balance-tracking)
4. [Year-End Processing (Carryover/Forfeiture)](#4-year-end-processing)
5. [Plan Management](#5-plan-management)
6. [Payment & Reimbursement](#6-payment--reimbursement)
7. [Audit & Compliance](#7-audit--compliance)
8. [Reporting & Notifications](#8-reporting--notifications)

---

## 1. Account Management

**Service:** `ReimbursementAccountBalanceService`  
**Purpose:** Lifecycle management of reimbursement accounts

### UC-001: Create Reimbursement Account
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
1. Member must be active under employer
2. Plan must exist and be active for specified year
3. One account per member per plan per year
4. IRS contribution limits enforced at creation

**Validation:**
- Verify member eligibility
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
3. Card number must be encrypted/tokenized (PCI-DSS)

---

### UC-003: Deactivate Account
**Input:**
- `ReimbursementAccountId` (string/Guid)
- `Reason` (enum) - MemberTermination, PlanYearEnded, AdminAction

**Output:**
- `AccountStatus` (enum) - Closed
- `ClosureDate` (DateTime)
- `FinalBalance` (decimal) - For refund/forfeiture

**Business Rules:**
1. All pending claims must be resolved first
2. If balance > 0, trigger forfeiture or refund workflow
3. Deactivate associated debit card

---

## 2. Claims Processing

**Service:** `ReimbursementAccountBalanceService`  
**Purpose:** Submit, validate, approve/deny medical expense claims

### UC-010: Submit Medical Expense Claim
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
4. Claim amount must match receipt totals

**Validation:**
- Service date ≤ current date
- Claim amount > 0
- Eligible expense category (medical, dental, vision, etc.)

---

### UC-011: Approve Claim
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
3. Automatically create reimbursement record
4. Deduct from available balance immediately

---

### UC-012: Deny Claim
**Input:**
- `ClaimId` (string/Guid)
- `DenialReason` (enum) - InsufficientDocumentation, IneligibleExpense, DuplicateClaim
- `DenialNotes` (string)

**Output:**
- `Status` (enum) - Denied
- `DenialDate` (DateTime)

**Business Rules:**
1. Denial reason is mandatory
2. Member must be notified via email/notification
3. Balance remains unchanged (no deduction)

---

## 3. Balance Tracking

**Service:** `ReimbursementAccountBalanceService`  
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
- `ContributionSource` (enum) - Employer, Employee
- `Amount` (decimal)
- `PayPeriod` (string) - Which paycheck

**Output:**
- `ContributionId` (string/Guid)
- `NewAvailableBalance` (decimal)
- `BalanceChangeAuditId` (string/Guid) - Audit trail

**Business Rules:**
1. Contribution + `ContributionToDate` ≤ IRS annual limit (FSA: $3,200, HSA: $4,150/$8,300)
2. Must be within plan year dates
3. Audit record created automatically

---

## 4. Year-End Processing

**Service:** `CarryoverDollarsDomainService`  
**Purpose:** EOFY carryover and forfeiture calculations

### UC-030: Calculate Carryover for Single Account
**Input:**
- `ReimbursementAccountId` (string/Guid)

**Output (UpdateCarryoverandForfeitedBalancesResponse):**
- `CarryoverAmount` (decimal) - Amount to transfer to next year
- `ForfeitedAmount` (decimal) - Amount lost (use-it-or-lose-it)
- `NewBalance` (decimal) - Updated available balance
- `Success` (bool)
- `ValidationErrors` (List<string>)

**Business Rules (per Plan Type):**
1. **FSA:** Max carryover = $640 (2025 IRS limit)
2. **HSA:** 100% carryover (unlimited)
3. **HRA:** Employer-defined carryover limit
4. **Dependent Care:** $0 carryover (100% forfeiture)

**Business Logic (from carryover-service-methods.json:183):**
```csharp
decimal CalculateCarryoverAmountAllowedAtPlanYearEnd(
    ReimbursementAccountsDto account,
    decimal accountBalanceAtPlanYearEnd,
    decimal IRSMaxForHSACarryover)
{
    switch (account.PlanType)
    {
        case PlanType.FSA:
            return Math.Min(accountBalanceAtPlanYearEnd, 640.00m); // 2025 IRS limit
        case PlanType.HSA:
            return accountBalanceAtPlanYearEnd; // 100% rollover
        case PlanType.HRA:
            return account.Plan.MaxCarryoverAmount; // Employer-defined
        case PlanType.DependentCare:
            return 0.00m; // No carryover allowed
        default:
            throw new InvalidOperationException("Unknown plan type");
    }
}
```

**Validation (from carryover-service-methods.json:197):**
1. Account must be active
2. Plan year must have ended (`PlanYearEndDate` < current date)
3. Balance > 0
4. No pending claims or issues

---

### UC-031: Process Carryover for All Accounts (V2 Batch)
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
1. Triggered annually at end of fiscal year (EOFY)
2. Feature flag `SplitJobPerformanceV2` controls V1 vs V2 processing
3. V2 uses batch processing: 1,000 accounts per batch, 10 concurrent operations
4. Pre-fetches all required data to eliminate N+1 queries

**Performance (V2 Architecture):**
- **Throughput:** 26,000 accounts/minute
- **Batch Processing Time:** ~2.3 seconds per 1,000 accounts
- **Performance Improvement:** 85% faster than V1

---

### UC-032: Transfer Carryover to Next Year Account
**Input:**
- `SourceAccountId` (string/Guid) - Prior year account
- `DestinationAccountId` (string/Guid) - Current year account
- `CarryoverAmount` (decimal)

**Output:**
- `CarryoverTransferTrackingId` (string/Guid)
- `TransferDate` (DateTime)
- `BalanceChangedEventId` (Guid) - Published to NServiceBus

**Business Rules:**
1. Source and destination accounts must belong to same member
2. Plan types must be compatible (FSA → FSA, HSA → HSA, etc.)
3. Destination account must be current year
4. Create audit record in `CarryoverTransferTracking` entity

---

## 5. Plan Management

**Service:** `PercentPlanLedgerDomainService`  
**Purpose:** Configure and manage reimbursement plans

### UC-040: Create Reimbursement Plan
**Input:**
- `EmployerId` (string/Guid)
- `PlanType` (enum) - FSA, HSA, HRA, DependentCare
- `PlanYear` (int)
- `MaxCarryoverAmount` (decimal)
- `HasGracePeriod` (bool)
- `RunOutPeriodDays` (int)

**Output:**
- `PlanId` (string/Guid)
- `IsActive` (bool)

**Business Rules:**
1. One plan per employer per plan type per year
2. Max carryover cannot exceed IRS limits
3. Cannot have both grace period AND carryover (IRS restriction)

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

## 6. Payment & Reimbursement

**Service:** `ReimbursementAccountBalanceService`  
**Purpose:** Disburse funds to members

### UC-050: Process Reimbursement Payment
**Input:**
- `ClaimId` (string/Guid)
- `PaymentMethod` (enum) - DirectDeposit, Check, DebitCard
- `BankAccountInfo` (if DirectDeposit)

**Output:**
- `ReimbursementId` (string/Guid)
- `PaymentDate` (DateTime)
- `Amount` (decimal)

**Business Rules:**
1. Claim must be approved first
2. Payment method must match member preferences
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
4. PCI-DSS: Transaction data encrypted in transit

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
- Third-Party Integrations (employer portals, TPA systems)

---

### UC-061: Create Balance Change Audit Record
**Input:**
- `ReimbursementAccountId` (string/Guid)
- `ChangeType` (enum) - Contribution, Claim, Carryover, Forfeiture
- `OldBalance` (decimal)
- `NewBalance` (decimal)
- `Reason` (string)

**Output:**
- `AuditId` (string/Guid)
- `AuditDate` (DateTime)

**Business Rules:**
1. **Mandatory for all balance changes** (IRS compliance)
2. **7-year retention** required
3. Immutable (cannot be edited or deleted)
4. Correlation ID links to source transaction

---

## 8. Reporting & Notifications

**Purpose:** Member communications and compliance reporting

### UC-070: Generate Annual Benefit Statement
**Input:**
- `MemberId` (string/Guid)
- `PlanYear` (int)

**Output:**
- `StatementId` (string/Guid)
- `PDF` (File) - Statement document
- `DeliveryMethod` (enum) - Email, Print

**Business Rules:**
1. ERISA requirement: Annual statement within 90 days of plan year end
2. Includes: contributions, claims, reimbursements, carryover, forfeiture
3. Must be archived for 7 years

---

### UC-071: Send Member Notification
**Input:**
- `MemberId` (string/Guid)
- `NotificationType` (enum) - ClaimApproved, ClaimDenied, LowBalance, CarryoverNotice
- `MessageContent` (string)

**Output:**
- `NotificationId` (string/Guid)
- `DeliveryStatus` (enum) - Sent, Failed

**Business Rules:**
1. Member must have opted-in to email/SMS
2. ERISA compliance: Certain notices mandatory (SPD, annual statement)

---

## 🎯 Use Case Summary by Functional Area

| Functional Area | Use Cases | Services | Complexity |
|----------------|-----------|----------|------------|
| **Account Management** | 10+ | ReimbursementAccountBalanceService | Medium |
| **Claims Processing** | 8+ | ReimbursementAccountBalanceService | High |
| **Balance Tracking** | 6+ | ReimbursementAccountBalanceService | Medium |
| **Year-End Processing** | 5+ | CarryoverDollarsDomainService | **Critical** |
| **Plan Management** | 4+ | PercentPlanLedgerDomainService | Low |
| **Payment & Reimbursement** | 6+ | ReimbursementAccountBalanceService | High |
| **Audit & Compliance** | 8+ | CarryoverDollarsDomainService | **Critical** |
| **Reporting & Notifications** | 5+ | Multiple | Medium |

---

## 📁 Data Sources

**Primary Sources:**
- `carryover-service-methods.json` - CarryoverDollarsDomainService methods (lines 1-471)
- `business-value-scan.json` - Service-to-capability mappings
- `domain-models/batch-3-1-entities.json` - Entity definitions

**Analysis Method:** AST analysis + business logic extraction

---

**Document Version:** 1.0  
**Last Updated:** December 11, 2025  
**Prepared By:** CORTEX AST Deep Analysis | Author: Asif Hussain  
**Copyright © 2025 Asif Hussain. All rights reserved.**
