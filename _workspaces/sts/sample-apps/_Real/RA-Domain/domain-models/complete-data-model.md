# Complete Data Model Documentation

**Repository:** Product.Example  
**Analysis Date:** December 11, 2025  
**Entity Count:** 30 domain entities  
**Source:** batch-3-1-entities.json, complete-csharp-analysis.json, business-value-scan.json

---

## 📊 Entity Catalog Overview

This document provides comprehensive documentation of all 30 domain entities in the Payment Accounts repository, organized by category with entity relationship diagrams (ERD), enum catalogs, and DTO specifications.

---

## 🏢 Core Entities (Multi-Tenant Hierarchy)

### 1. Organization
**Namespace:** `App.Organization.Domain.Entities`  
**File:** `Organization.cs`  
**Line:** 19

**Purpose:** Multi-tenant root entity representing an organization that offers benefit plans to employees.

**Key Properties** (inferred):
- `EmployerId` (string/Guid) - Primary key
- `CompanyName` (string) - Legal entity name
- `TaxId` (string) - EIN for RegulatoryAgency reporting
- `IsActive` (bool) - Active/inactive status
- `CreatedDate` (DateTime) - Account creation timestamp

**Navigation Properties:**
- `Customers` (ICollection<Customer>) - One-to-Many
- `ReimbursementPlans` (ICollection<PaymentPlan>) - One-to-Many

**Compliance Scope:** PrivacyRegulation (PHI container)

---

### 2. Customer
**Namespace:** `App.Organization.Domain.Entities`  
**File:** `Customer.cs`  
**Line:** 21

**Purpose:** Employee/participant in a benefits program under an organization.

**Key Properties** (inferred):
- `MemberId` (string/Guid) - Primary key
- `EmployerId` (string/Guid) - Foreign key to Organization
- `FirstName` (string) - Personal identifier
- `LastName` (string) - Personal identifier
- `SSN` (string) - Encrypted PII
- `DateOfBirth` (DateTime) - Age verification
- `Email` (string) - Contact information
- `IsActive` (bool) - Active/inactive status

**Navigation Properties:**
- `Organization` (Organization) - Many-to-One
- `PaymentAccounts` (ICollection<PaymentAccount>) - One-to-Many
- `BenefitElections` (ICollection<BenefitElection>) - One-to-Many

**Compliance Scope:** PrivacyRegulation (PHI - personal identifiers)

---

### 3. PaymentAccount
**Namespace:** `App.Organization.Domain.Entities`  
**File:** `PaymentAccount.cs`  
**Line:** 21

**Purpose:** Specific account instance (FlexAccount/HealthSavings/HealthReimbursement) linked to a customer and plan.

**Key Properties** (inferred):
- `ReimbursementAccountId` (string/Guid) - Primary key
- `MemberId` (string/Guid) - Foreign key to Customer
- `PlanId` (string/Guid) - Foreign key to PaymentPlan
- `PlanYear` (int) - Fiscal year (e.g., 2024, 2025)
- `AvailableBalance` (decimal) - Current balance
- `ContributionToDate` (decimal) - Total contributions
- `AmountRemainingToBeReimbursed` (decimal) - Pending claims
- `CarryoverBalance` (decimal) - Amount carried from prior year
- `ForfeitedAmount` (decimal) - Use-it-or-lose-it expiration
- `Status` (enum) - Active, Closed, Terminated

**Navigation Properties:**
- `Customer` (Customer) - Many-to-One
- `Plan` (PaymentPlan) - Many-to-One
- `Requests` (ICollection<Request>) - One-to-Many
- `Transactions` (ICollection<Transaction>) - One-to-Many
- `Contributions` (ICollection<Contribution>) - One-to-Many
- `Card` (Card) - One-to-One (optional)

**Compliance Scope:** RegulatoryAgency (balance tracking, rollover calculations)

---

### 4. PaymentPlan
**Namespace:** `App.Organization.Domain.Entities`  
**File:** `PaymentPlan.cs`  
**Line:** 24

**Purpose:** Plan definition and configuration (FlexAccount/HealthSavings/HealthReimbursement rules).

**Key Properties** (inferred):
- `PlanId` (string/Guid) - Primary key
- `EmployerId` (string/Guid) - Foreign key to Organization
- `PlanType` (enum) - FlexAccount, HealthSavings, HealthReimbursement, DependentCare, LimitedFlexAccount
- `PlanYear` (int) - Applicable year
- `MaxCarryoverAmount` (decimal) - RegulatoryAgency limit (e.g., $640 for FlexAccount)
- `HasGracePeriod` (bool) - 2.5 month extension
- `GracePeriodEndDate` (DateTime?) - If grace period enabled
- `RunOutPeriodDays` (int) - Days to submit claims post plan year
- `HasDebitCard` (bool) - Debit card availability
- `IsActive` (bool)

**Navigation Properties:**
- `Organization` (Organization) - Many-to-One
- `Accounts` (ICollection<PaymentAccount>) - One-to-Many

**Compliance Scope:** RegulatoryAgency (plan rules, rollover configuration)

---

## 💳 Transaction Entities

### 5. Request
**Namespace:** `App.Example.Domain.Entities`  
**File:** `Request.cs`  
**Line:** (inferred from batch analysis)

**Purpose:** Customer-submitted request for payment of medical expenses.

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
- `PaymentAccount` (PaymentAccount) - Many-to-One
- `ClaimLines` (ICollection<ClaimLine>) - One-to-Many
- `Documents` (ICollection<Document>) - One-to-Many

**Compliance Scope:** PrivacyRegulation (medical claims data)

---

### 6. ClaimLine
**Namespace:** `App.Example.Domain.Entities`  
**File:** `ClaimLine.cs`  
**Line:** (inferred)

**Purpose:** Individual line item within a request (multiple services per request).

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
- `Request` (Request) - Many-to-One

**Compliance Scope:** PrivacyRegulation (PHI - medical codes)

---

### 7. Transaction
**Namespace:** `App.Example.Domain.Entities`  
**File:** `Transaction.cs`  
**Line:** (inferred)

**Purpose:** Balance change record (contributions, deductions, adjustments).

**Key Properties** (inferred):
- `TransactionId` (string/Guid) - Primary key
- `ReimbursementAccountId` (string/Guid) - Foreign key
- `TransactionType` (enum) - Contribution, Request, Adjustment, Rollover, Expiration
- `Amount` (decimal) - Transaction value
- `TransactionDate` (DateTime) - When occurred
- `Description` (string) - Human-readable detail
- `CorrelationId` (Guid?) - Links to request/payment

**Navigation Properties:**
- `PaymentAccount` (PaymentAccount) - Many-to-One

**Compliance Scope:** RegulatoryAgency (audit trail for balance changes)

---

### 8. Contribution
**Namespace:** `App.Example.Domain.Entities`  
**File:** `Contribution.cs`  
**Line:** (inferred)

**Purpose:** Organization or employee contributions to account.

**Key Properties** (inferred):
- `ContributionId` (string/Guid) - Primary key
- `ReimbursementAccountId` (string/Guid) - Foreign key
- `ContributionSource` (enum) - Organization, Employee
- `Amount` (decimal)
- `ContributionDate` (DateTime)
- `PayPeriod` (string) - Which pay period

**Navigation Properties:**
- `PaymentAccount` (PaymentAccount) - Many-to-One

**Compliance Scope:** RegulatoryAgency (contribution limits tracking)

---

### 9. Payment
**Namespace:** `App.Example.Domain.Entities`  
**File:** `Payment.cs`  
**Line:** (inferred)

**Purpose:** Payout to customer for approved claims.

**Key Properties** (inferred):
- `ReimbursementId` (string/Guid) - Primary key
- `ClaimId` (string/Guid) - Foreign key
- `ReimbursementAccountId` (string/Guid) - Foreign key
- `Amount` (decimal) - Amount disbursed
- `PaymentMethod` (enum) - DirectDeposit, Check, DebitCard
- `PaymentDate` (DateTime) - When paid
- `CheckNumber` (string?) - If check payment

**Navigation Properties:**
- `Request` (Request) - Many-to-One
- `PaymentAccount` (PaymentAccount) - Many-to-One

**Compliance Scope:** RegulatoryAgency (distribution rules)

---

## 🔒 Compliance Entities

### 10. BalanceChangeAudit
**Namespace:** `App.Example.Domain.Entities`  
**File:** `BalanceChangeAudit.cs`  
**Line:** 9

**XML Documentation:** "Represents an audit record for balance changes in PaymentAccounts."

**Purpose:** Track all balance modifications for RegulatoryAgency compliance (7-year retention).

**Key Properties** (inferred):
- `AuditId` (string/Guid) - Primary key
- `ReimbursementAccountId` (string/Guid) - Foreign key
- `ChangeType` (enum) - Contribution, Request, Rollover, Expiration, Adjustment
- `OldBalance` (decimal) - Balance before change
- `NewBalance` (decimal) - Balance after change
- `ChangeAmount` (decimal) - Delta
- `ChangeDate` (DateTime) - When occurred
- `UserId` (string/Guid) - Who made change
- `Reason` (string) - Business justification
- `CorrelationId` (Guid) - Link to transaction

**Compliance Scope:** RegulatoryAgency (7-year audit retention requirement)

---

### 11. RolloverTransferTracking
**Namespace:** `App.Example.Domain.Entities`  
**File:** `RolloverTransferTracking.cs`  
**Line:** 9

**Purpose:** Record year-end rollover transfers from one plan year to next.

**Key Properties** (inferred):
- `TrackingId` (string/Guid) - Primary key
- `SourceAccountId` (string/Guid) - Prior year account
- `DestinationAccountId` (string/Guid) - Current year account
- `PlanYearFrom` (int) - Source year
- `PlanYearTo` (int) - Destination year
- `CarryoverAmount` (decimal) - Amount transferred
- `ForfeitedAmount` (decimal) - Amount lost
- `TransferDate` (DateTime) - EOY processing date
- `CorrelationId` (Guid) - Link to BalanceChangedEvent

**Compliance Scope:** RegulatoryAgency (rollover documentation)

---

### 12. Card
**Namespace:** `App.Example.Domain.Entities`  
**File:** `Card.cs`  
**Line:** 22

**Purpose:** Debit card linked to payment account for direct payment.

**Key Properties** (inferred):
- `CardId` (string/Guid) - Primary key
- `ReimbursementAccountId` (string/Guid) - Foreign key
- `CardNumber` (string) - **ENCRYPTED/TOKENIZED** (PaymentSecurity requirement)
- `CardholderName` (string)
- `ExpirationDate` (DateTime)
- `CVV` (string?) - **NEVER STORED** (PaymentSecurity violation)
- `IsActive` (bool)
- `ActivationDate` (DateTime)

**Navigation Properties:**
- `PaymentAccount` (PaymentAccount) - One-to-One
- `Transactions` (ICollection<CardTransaction>) - One-to-Many

**Compliance Scope:** PaymentSecurity Level 1 (quarterly SAQ-D required)

---

### 13. CardTransaction
**Namespace:** `App.Example.Domain.Entities`  
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
- `PaymentAccount` (PaymentAccount) - Many-to-One

**Compliance Scope:** PaymentSecurity (transaction data encryption in transit)

---

## 📄 Additional Entities (14-30)

### 14. ActualCoverage
**Namespace:** `App.Example.Domain.Entities`  
**File:** `ActualCoverage.cs`  
**Line:** 21  
**Purpose:** Track insurance coverage periods

### 15. Lookup
**Namespace:** `App.Organization.Domain.Entities`  
**File:** `Lookup.cs`  
**Line:** 19  
**Purpose:** Reference data (categories, codes, etc.)

### 16. AutoPayrollDeduction
**Purpose:** Automated payroll contribution settings

### 17. BenefitElection
**Purpose:** Customer benefit registration choices

### 18. Document
**Purpose:** File attachments (receipts, EOBs, etc.)  
**Compliance:** PrivacyRegulation (secure storage)

### 19. Notification
**Purpose:** Email/SMS communications  
**Compliance:** BenefitsRegulation (disclosure requirements)

### 20. ScheduledItem
**Purpose:** Background job scheduling

### 21. Balance
**Purpose:** Balance snapshot history

### 22. PlanYear
**Purpose:** Fiscal year configuration

### 23. PlanType
**Purpose:** FlexAccount/HealthSavings/HealthReimbursement/DependentCare enumeration

### 24. ForfeitureRule
**Purpose:** Use-it-or-lose-it rule definitions  
**Compliance:** RegulatoryAgency (expiration calculations)

### 25. CarryoverRule
**Purpose:** Rollover limit configuration  
**Compliance:** RegulatoryAgency (e.g., $640 for FlexAccount)

### 26. Statement
**Purpose:** Customer benefit statements  
**Compliance:** BenefitsRegulation (annual statement requirement)

### 27. AuditLog
**Purpose:** System-level access logging  
**Compliance:** PrivacyRegulation (access audit trail)

### 28. RolloverSettings
**Purpose:** HealthSavings rollover configuration

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

                         Organization (Tenant Root)
                              │
                              │ 1:N
                              ▼
                           Customer
                              │
                              │ 1:N
                              ▼
                    PaymentAccount ────────── N:1 ────────▶ PaymentPlan
                              │                                         │
                              │ 1:N                                     │ N:1
                              ├──────────────────┐                      │
                              ▼                  ▼                      ▼
                          Request ◀────1:1──── Card                   Organization
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

         PaymentAccount
                 │
                 │ 1:N
                 ├───────────────┬─────────────────┬──────────────────┬──────────────────┐
                 ▼               ▼                 ▼                  ▼                  ▼
           Transaction    Contribution      Payment    BalanceChangeAudit   RolloverTransferTracking
           (all types)    (funding)         (payouts)        (7-year retention)   (year-end processing)

```

---

## 📋 Enum Catalog

### PlanType Enumeration
```csharp
public enum PlanType
{
    FlexAccount,                 // Flexible Spending Account
    HealthSavings,                 // Health Savings Account
    HealthReimbursement,                 // Health Payment Arrangement
    DependentCare,       // DependentCare FlexAccount
    LimitedFlexAccount,          // Limited Purpose FlexAccount (dental/vision only)
    CommutingFlexAccount         // Transportation benefits (rare)
}
```

### TransactionType Enumeration
```csharp
public enum TransactionType
{
    Contribution,        // Organization or employee funding
    Request,               // Medical expense deduction
    Adjustment,          // Manual correction
    Rollover,           // Year-end rollover
    Expiration,          // Use-it-or-lose-it
    Payment        // Request payout
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
    Terminated           // Customer left organization
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

### Key DTOs (from rollover-service-methods.json)

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
- `rollover-service-methods.json` - DTO definitions

**Analysis Method:** Static AST analysis via Python scripts

---

**Document Version:** 1.0  
**Last Updated:** December 11, 2025  
**Prepared By:** CORTEX AST Deep Analysis | Author: Asif Hussain  
**Copyright © 2025 Asif Hussain. All rights reserved.**
