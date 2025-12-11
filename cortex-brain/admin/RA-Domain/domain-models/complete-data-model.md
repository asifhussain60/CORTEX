# Complete Data Model Documentation

**Repository:** Product.ReimbursementAccounts  
**Analysis Date:** December 11, 2025  
**Entity Count:** 30 domain entities  
**Source:** batch-3-1-entities.json, complete-csharp-analysis.json, business-value-scan.json

---

## 📊 Entity Catalog Overview

This document provides comprehensive documentation of all 30 domain entities in the Reimbursement Accounts repository, organized by category with entity relationship diagrams (ERD), enum catalogs, and DTO specifications.

---

## 🏢 Core Entities (Multi-Tenant Hierarchy)

### 1. Employer
**Namespace:** `Hqy.Employer.Domain.Entities`  
**File:** `Employer.cs`  
**Line:** 19

**Purpose:** Multi-tenant root entity representing an organization that offers benefit plans to employees.

**Key Properties** (inferred):
- `EmployerId` (string/Guid) - Primary key
- `CompanyName` (string) - Legal entity name
- `TaxId` (string) - EIN for IRS reporting
- `IsActive` (bool) - Active/inactive status
- `CreatedDate` (DateTime) - Account creation timestamp

**Navigation Properties:**
- `Members` (ICollection<Member>) - One-to-Many
- `ReimbursementPlans` (ICollection<ReimbursementPlan>) - One-to-Many

**Compliance Scope:** HIPAA (PHI container)

---

### 2. Member
**Namespace:** `Hqy.Employer.Domain.Entities`  
**File:** `Member.cs`  
**Line:** 21

**Purpose:** Employee/participant in a benefits program under an employer.

**Key Properties** (inferred):
- `MemberId` (string/Guid) - Primary key
- `EmployerId` (string/Guid) - Foreign key to Employer
- `FirstName` (string) - Personal identifier
- `LastName` (string) - Personal identifier
- `SSN` (string) - Encrypted PII
- `DateOfBirth` (DateTime) - Age verification
- `Email` (string) - Contact information
- `IsActive` (bool) - Active/inactive status

**Navigation Properties:**
- `Employer` (Employer) - Many-to-One
- `ReimbursementAccounts` (ICollection<ReimbursementAccount>) - One-to-Many
- `BenefitElections` (ICollection<BenefitElection>) - One-to-Many

**Compliance Scope:** HIPAA (PHI - personal identifiers)

---

### 3. ReimbursementAccount
**Namespace:** `Hqy.Employer.Domain.Entities`  
**File:** `ReimbursementAccount.cs`  
**Line:** 21

**Purpose:** Specific account instance (FSA/HSA/HRA) linked to a member and plan.

**Key Properties** (inferred):
- `ReimbursementAccountId` (string/Guid) - Primary key
- `MemberId` (string/Guid) - Foreign key to Member
- `PlanId` (string/Guid) - Foreign key to ReimbursementPlan
- `PlanYear` (int) - Fiscal year (e.g., 2024, 2025)
- `AvailableBalance` (decimal) - Current balance
- `ContributionToDate` (decimal) - Total contributions
- `AmountRemainingToBeReimbursed` (decimal) - Pending claims
- `CarryoverBalance` (decimal) - Amount carried from prior year
- `ForfeitedAmount` (decimal) - Use-it-or-lose-it forfeiture
- `Status` (enum) - Active, Closed, Terminated

**Navigation Properties:**
- `Member` (Member) - Many-to-One
- `Plan` (ReimbursementPlan) - Many-to-One
- `Claims` (ICollection<Claim>) - One-to-Many
- `Transactions` (ICollection<Transaction>) - One-to-Many
- `Contributions` (ICollection<Contribution>) - One-to-Many
- `Card` (Card) - One-to-One (optional)

**Compliance Scope:** IRS (balance tracking, carryover calculations)

---

### 4. ReimbursementPlan
**Namespace:** `Hqy.Employer.Domain.Entities`  
**File:** `ReimbursementPlan.cs`  
**Line:** 24

**Purpose:** Plan definition and configuration (FSA/HSA/HRA rules).

**Key Properties** (inferred):
- `PlanId` (string/Guid) - Primary key
- `EmployerId` (string/Guid) - Foreign key to Employer
- `PlanType` (enum) - FSA, HSA, HRA, DependentCare, LimitedFSA
- `PlanYear` (int) - Applicable year
- `MaxCarryoverAmount` (decimal) - IRS limit (e.g., $640 for FSA)
- `HasGracePeriod` (bool) - 2.5 month extension
- `GracePeriodEndDate` (DateTime?) - If grace period enabled
- `RunOutPeriodDays` (int) - Days to submit claims post plan year
- `HasDebitCard` (bool) - Debit card availability
- `IsActive` (bool)

**Navigation Properties:**
- `Employer` (Employer) - Many-to-One
- `Accounts` (ICollection<ReimbursementAccount>) - One-to-Many

**Compliance Scope:** IRS (plan rules, carryover configuration)

---

## 💳 Transaction Entities

### 5. Claim
**Namespace:** `Hqy.Member.Domain.Entities`  
**File:** `Claim.cs`  
**Line:** (inferred from batch analysis)

**Purpose:** Member-submitted request for reimbursement of medical expenses.

**Key Properties** (inferred):
- `ClaimId` (string/Guid) - Primary key
- `ReimbursementAccountId` (string/Guid) - Foreign key
- `MemberId` (string/Guid) - Foreign key
- `ClaimNumber` (string) - User-facing identifier
- `SubmissionDate` (DateTime) - Date submitted
- `ServiceDate` (DateTime) - Date of medical service
- `TotalClaimAmount` (decimal) - Total requested
- `ApprovedAmount` (decimal) - Amount approved
- `Status` (enum) - Submitted, Approved, Denied, PendingDocumentation
- `DenialReason` (string?) - If denied

**Navigation Properties:**
- `ReimbursementAccount` (ReimbursementAccount) - Many-to-One
- `ClaimLines` (ICollection<ClaimLine>) - One-to-Many
- `Documents` (ICollection<Document>) - One-to-Many

**Compliance Scope:** HIPAA (medical claims data)

---

### 6. ClaimLine
**Namespace:** `Hqy.Member.Domain.Entities`  
**File:** `ClaimLine.cs`  
**Line:** (inferred)

**Purpose:** Individual line item within a claim (multiple services per claim).

**Key Properties** (inferred):
- `ClaimLineId` (string/Guid) - Primary key
- `ClaimId` (string/Guid) - Foreign key
- `ServiceDescription` (string) - What was purchased
- `ServiceDate` (DateTime) - Date of service
- `Amount` (decimal) - Line item cost
- `DiagnosisCode` (string?) - ICD-10 code
- `ProcedureCode` (string?) - CPT code
- `IsEligible` (bool) - Meets plan criteria

**Navigation Properties:**
- `Claim` (Claim) - Many-to-One

**Compliance Scope:** HIPAA (PHI - medical codes)

---

### 7. Transaction
**Namespace:** `Hqy.Member.Domain.Entities`  
**File:** `Transaction.cs`  
**Line:** (inferred)

**Purpose:** Balance change record (contributions, deductions, adjustments).

**Key Properties** (inferred):
- `TransactionId` (string/Guid) - Primary key
- `ReimbursementAccountId` (string/Guid) - Foreign key
- `TransactionType` (enum) - Contribution, Claim, Adjustment, Carryover, Forfeiture
- `Amount` (decimal) - Transaction value
- `TransactionDate` (DateTime) - When occurred
- `Description` (string) - Human-readable detail
- `CorrelationId` (Guid?) - Links to claim/reimbursement

**Navigation Properties:**
- `ReimbursementAccount` (ReimbursementAccount) - Many-to-One

**Compliance Scope:** IRS (audit trail for balance changes)

---

### 8. Contribution
**Namespace:** `Hqy.Member.Domain.Entities`  
**File:** `Contribution.cs`  
**Line:** (inferred)

**Purpose:** Employer or employee contributions to account.

**Key Properties** (inferred):
- `ContributionId` (string/Guid) - Primary key
- `ReimbursementAccountId` (string/Guid) - Foreign key
- `ContributionSource` (enum) - Employer, Employee
- `Amount` (decimal)
- `ContributionDate` (DateTime)
- `PayPeriod` (string) - Which pay period

**Navigation Properties:**
- `ReimbursementAccount` (ReimbursementAccount) - Many-to-One

**Compliance Scope:** IRS (contribution limits tracking)

---

### 9. Reimbursement
**Namespace:** `Hqy.Member.Domain.Entities`  
**File:** `Reimbursement.cs`  
**Line:** (inferred)

**Purpose:** Payout to member for approved claims.

**Key Properties** (inferred):
- `ReimbursementId` (string/Guid) - Primary key
- `ClaimId` (string/Guid) - Foreign key
- `ReimbursementAccountId` (string/Guid) - Foreign key
- `Amount` (decimal) - Amount disbursed
- `PaymentMethod` (enum) - DirectDeposit, Check, DebitCard
- `PaymentDate` (DateTime) - When paid
- `CheckNumber` (string?) - If check payment

**Navigation Properties:**
- `Claim` (Claim) - Many-to-One
- `ReimbursementAccount` (ReimbursementAccount) - Many-to-One

**Compliance Scope:** IRS (distribution rules)

---

## 🔒 Compliance Entities

### 10. BalanceChangeAudit
**Namespace:** `Hqy.Member.Domain.Entities`  
**File:** `BalanceChangeAudit.cs`  
**Line:** 9

**XML Documentation:** "Represents an audit record for balance changes in ReimbursementAccounts."

**Purpose:** Track all balance modifications for IRS compliance (7-year retention).

**Key Properties** (inferred):
- `AuditId` (string/Guid) - Primary key
- `ReimbursementAccountId` (string/Guid) - Foreign key
- `ChangeType` (enum) - Contribution, Claim, Carryover, Forfeiture, Adjustment
- `OldBalance` (decimal) - Balance before change
- `NewBalance` (decimal) - Balance after change
- `ChangeAmount` (decimal) - Delta
- `ChangeDate` (DateTime) - When occurred
- `UserId` (string/Guid) - Who made change
- `Reason` (string) - Business justification
- `CorrelationId` (Guid) - Link to transaction

**Compliance Scope:** IRS (7-year audit retention requirement)

---

### 11. CarryoverTransferTracking
**Namespace:** `Hqy.Member.Domain.Entities`  
**File:** `CarryoverTransferTracking.cs`  
**Line:** 9

**Purpose:** Record year-end carryover transfers from one plan year to next.

**Key Properties** (inferred):
- `TrackingId` (string/Guid) - Primary key
- `SourceAccountId` (string/Guid) - Prior year account
- `DestinationAccountId` (string/Guid) - Current year account
- `PlanYearFrom` (int) - Source year
- `PlanYearTo` (int) - Destination year
- `CarryoverAmount` (decimal) - Amount transferred
- `ForfeitedAmount` (decimal) - Amount lost
- `TransferDate` (DateTime) - EOFY processing date
- `CorrelationId` (Guid) - Link to BalanceChangedEvent

**Compliance Scope:** IRS (carryover documentation)

---

### 12. Card
**Namespace:** `Hqy.Member.Domain.Entities`  
**File:** `Card.cs`  
**Line:** 22

**Purpose:** Debit card linked to reimbursement account for direct payment.

**Key Properties** (inferred):
- `CardId` (string/Guid) - Primary key
- `ReimbursementAccountId` (string/Guid) - Foreign key
- `CardNumber` (string) - **ENCRYPTED/TOKENIZED** (PCI-DSS requirement)
- `CardholderName` (string)
- `ExpirationDate` (DateTime)
- `CVV` (string?) - **NEVER STORED** (PCI-DSS violation)
- `IsActive` (bool)
- `ActivationDate` (DateTime)

**Navigation Properties:**
- `ReimbursementAccount` (ReimbursementAccount) - One-to-One
- `Transactions` (ICollection<CardTransaction>) - One-to-Many

**Compliance Scope:** PCI-DSS Level 1 (quarterly SAQ-D required)

---

### 13. CardTransaction
**Namespace:** `Hqy.Member.Domain.Entities`  
**File:** `CardTransaction.cs`  
**Line:** 22

**Purpose:** Record of debit card usage for medical purchases.

**Key Properties** (inferred):
- `TransactionId` (string/Guid) - Primary key
- `CardId` (string/Guid) - Foreign key
- `ReimbursementAccountId` (string/Guid) - Foreign key
- `MerchantName` (string)
- `TransactionAmount` (decimal)
- `TransactionDate` (DateTime)
- `MerchantCategory` (string) - MCC code
- `AuthorizationCode` (string)
- `Status` (enum) - Approved, Pending, Declined

**Navigation Properties:**
- `Card` (Card) - Many-to-One
- `ReimbursementAccount` (ReimbursementAccount) - Many-to-One

**Compliance Scope:** PCI-DSS (transaction data encryption in transit)

---

## 📄 Additional Entities (14-30)

### 14. ActualCoverage
**Namespace:** `Hqy.Member.Domain.Entities`  
**File:** `ActualCoverage.cs`  
**Line:** 21  
**Purpose:** Track insurance coverage periods

### 15. Lookup
**Namespace:** `Hqy.Employer.Domain.Entities`  
**File:** `Lookup.cs`  
**Line:** 19  
**Purpose:** Reference data (categories, codes, etc.)

### 16. AutoPayrollDeduction
**Purpose:** Automated payroll contribution settings

### 17. BenefitElection
**Purpose:** Member benefit enrollment choices

### 18. Document
**Purpose:** File attachments (receipts, EOBs, etc.)  
**Compliance:** HIPAA (secure storage)

### 19. Notification
**Purpose:** Email/SMS communications  
**Compliance:** ERISA (disclosure requirements)

### 20. ScheduledItem
**Purpose:** Background job scheduling

### 21. Balance
**Purpose:** Balance snapshot history

### 22. PlanYear
**Purpose:** Fiscal year configuration

### 23. PlanType
**Purpose:** FSA/HSA/HRA/DependentCare enumeration

### 24. ForfeitureRule
**Purpose:** Use-it-or-lose-it rule definitions  
**Compliance:** IRS (forfeiture calculations)

### 25. CarryoverRule
**Purpose:** Carryover limit configuration  
**Compliance:** IRS (e.g., $640 for FSA)

### 26. Statement
**Purpose:** Member benefit statements  
**Compliance:** ERISA (annual statement requirement)

### 27. AuditLog
**Purpose:** System-level access logging  
**Compliance:** HIPAA (access audit trail)

### 28. RolloverSettings
**Purpose:** HSA rollover configuration

### 29. PercentPlanLedger
**Purpose:** Ledger for percent-based plans

### 30. FeatureFlag
**Purpose:** A/B testing and gradual rollouts (e.g., `SplitJobPerformanceV2`)

---

## 🔗 Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────────────┐
│ MULTI-TENANT HIERARCHY                                              │
└─────────────────────────────────────────────────────────────────────┘

                         Employer (Tenant Root)
                              │
                              │ 1:N
                              ▼
                           Member
                              │
                              │ 1:N
                              ▼
                    ReimbursementAccount ────────── N:1 ────────▶ ReimbursementPlan
                              │                                         │
                              │ 1:N                                     │ N:1
                              ├──────────────────┐                      │
                              ▼                  ▼                      ▼
                          Claim ◀────1:1──── Card                   Employer
                              │                  │
                              │ 1:N              │ 1:N
                              ▼                  ▼
                         ClaimLine        CardTransaction
                              │
                              │ 1:N
                              ▼
                          Document

┌─────────────────────────────────────────────────────────────────────┐
│ TRANSACTION & AUDIT TRAIL                                           │
└─────────────────────────────────────────────────────────────────────┘

         ReimbursementAccount
                 │
                 │ 1:N
                 ├───────────────┬─────────────────┬──────────────────┬──────────────────┐
                 ▼               ▼                 ▼                  ▼                  ▼
           Transaction    Contribution      Reimbursement    BalanceChangeAudit   CarryoverTransferTracking
           (all types)    (funding)         (payouts)        (7-year retention)   (year-end processing)

```

---

## 📋 Enum Catalog

### PlanType Enumeration
```csharp
public enum PlanType
{
    FSA,                 // Flexible Spending Account
    HSA,                 // Health Savings Account
    HRA,                 // Health Reimbursement Arrangement
    DependentCare,       // Dependent Care FSA
    LimitedFSA,          // Limited Purpose FSA (dental/vision only)
    CommutingFSA         // Transportation benefits (rare)
}
```

### TransactionType Enumeration
```csharp
public enum TransactionType
{
    Contribution,        // Employer or employee funding
    Claim,               // Medical expense deduction
    Adjustment,          // Manual correction
    Carryover,           // Year-end rollover
    Forfeiture,          // Use-it-or-lose-it
    Reimbursement        // Claim payout
}
```

### ClaimStatus Enumeration
```csharp
public enum ClaimStatus
{
    Submitted,           // Initial state
    PendingDocumentation, // Awaiting receipts
    UnderReview,         // Being processed
    Approved,            // Approved for payment
    Denied,              // Rejected
    Paid                 // Reimbursed
}
```

### AccountStatus Enumeration
```csharp
public enum AccountStatus
{
    Active,              // Normal operation
    Suspended,           // Temporarily disabled
    Closed,              // Plan year ended
    Terminated           // Member left employer
}
```

### PaymentMethod Enumeration
```csharp
public enum PaymentMethod
{
    DirectDeposit,       // ACH to bank account
    Check,               // Mailed check
    DebitCard            // Direct payment via card
}
```

---

## 📦 DTO Specifications

### Key DTOs (from carryover-service-methods.json)

#### BalanceChangeInfoDto
```csharp
public class BalanceChangeInfoDto
{
    public string AccountId { get; set; }
    public decimal OldBalance { get; set; }
    public decimal NewBalance { get; set; }
    public decimal CarryoverAmount { get; set; }
    public decimal ForfeitedAmount { get; set; }
    public int PlanYear { get; set; }
    public DateTime Timestamp { get; set; }
}
```

#### ReimbursementAccountsDto
```csharp
public class ReimbursementAccountsDto
{
    public string AccountId { get; set; }
    public string MemberId { get; set; }
    public string PlanId { get; set; }
    public int PlanYear { get; set; }
    public PlanType PlanType { get; set; }
    public decimal AvailableBalance { get; set; }
    public decimal ContributionToDate { get; set; }
    public decimal AmountRemainingToBeReimbursed { get; set; }
}
```

#### ProcessCarryOverRequest
```csharp
public class ProcessCarryOverRequest
{
    public int BatchSize { get; set; } = 1000;         // V2 batch size
    public int MaxConcurrency { get; set; } = 10;      // Parallel workers
    public bool SaveToDatabase { get; set; } = true;
}
```

#### ProcessCarryOverResponse
```csharp
public class ProcessCarryOverResponse
{
    public int TotalAccountsProcessed { get; set; }
    public int SuccessfulCarryovers { get; set; }
    public int Forfeitures { get; set; }
    public decimal TotalCarryoverAmount { get; set; }
    public decimal TotalForfeitedAmount { get; set; }
    public TimeSpan ProcessingTime { get; set; }
    public List<string> Errors { get; set; }
}
```

---

## 🎯 Data Sources

**Primary Sources:**
- `batch-3-1-entities.json` - First 10 entities with metadata
- `complete-csharp-analysis.json` - Full AST analysis
- `business-value-scan.json` - Business capability mappings
- `carryover-service-methods.json` - DTO definitions

**Analysis Method:** Static AST analysis via Python scripts

---

**Document Version:** 1.0  
**Last Updated:** December 11, 2025  
**Prepared By:** CORTEX AST Deep Analysis | Author: Asif Hussain  
**Copyright © 2025 Asif Hussain. All rights reserved.**
