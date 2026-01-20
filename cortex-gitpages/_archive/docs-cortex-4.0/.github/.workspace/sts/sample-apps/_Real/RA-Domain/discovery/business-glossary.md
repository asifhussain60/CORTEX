# Business Glossary: Payment Accounts Domain

**Repository:** C:\PROJECTS\Product.PaymentAccounts  
**Purpose:** Authoritative definitions for domain terminology  
**Audience:** Developers, business analysts, product managers

---

## 🏥 Account Types

### FlexAccount (Flexible Spending Account)
Tax-advantaged account for out-of-pocket medical expenses. Pre-tax contributions reduce taxable income. Subject to "use-it-or-lose-it" rule (unused funds over $640 forfeited at year-end). Organization may offer 2.5-month grace period OR $640 rollover, but not both.

**RegulatoryAgency Regulation:** 26 CFR §125 (Cafeteria Plans)  
**Contribution Limit (2025):** $3,200  
**Rollover Limit (2025):** $640

### HealthSavings (Health Savings Account)
Tax-advantaged savings account for medical expenses, available only with High-Deductible Health Plans (HDHP). Triple tax advantage: pre-tax contributions, tax-free growth, tax-free withdrawals for qualified expenses. Funds roll over 100% year-over-year. Customer-owned and portable.

**RegulatoryAgency Regulation:** IRC §223  
**Contribution Limit (2025):** $4,150 (individual), $8,300 (family)  
**Rollover:** Unlimited

### HealthReimbursement (Health Payment Arrangement)
Organization-funded account for reimbursing medical expenses. 100% organization contributions (employees cannot contribute). Organization determines rollover rules. Generally non-portable (funds lost on termination unless organization allows).

**RegulatoryAgency Regulation:** RegulatoryAgency Notice 2002-45  
**Funding:** Organization-only  
**Portability:** Organization-determined

### DependentCare FlexAccount
Tax-advantaged account for dependent care expenses (daycare, preschool, after-school programs). Eligible dependents: children under 13 or disabled dependents. Subject to "use-it-or-lose-it" rule.

**RegulatoryAgency Regulation:** IRC §129  
**Contribution Limit (2025):** $5,000 ($2,500 if married filing separately)  
**Eligible Dependents:** Under age 13 or disabled

---

## 💰 Financial Terms

### Available Balance
Current spendable funds in account. Calculated as: Opening balance + Contributions - Requests - Scheduled payments - Fees.

**Formula:** `AvailableBalance = SUM(Contributions) - SUM(Requests) - SUM(ScheduledItems) - SUM(Fees)`

### Pending Balance
Funds reserved for scheduled/autopay claims that haven't been paid yet. Reduces available balance even though payment is future-dated.

### Rollover
Unused FlexAccount funds (up to $640) transferred to next plan year. RegulatoryAgency allows employers to offer rollover OR grace period, not both.

**RegulatoryAgency Limit (2025):** $640  
**Regulation:** 26 CFR §125-5(c)

### Expiration
Unused FlexAccount funds exceeding rollover limit ($640) that are lost at plan year end. "Use-it-or-lose-it" rule.

**Example:** Customer has $800 unused. $640 carries over, $160 forfeited.

### Grace Period
Optional 2.5-month extension (through March 15) allowing members to use prior year FlexAccount funds. Alternative to rollover - employers choose one or the other.

**Regulation:** 26 CFR §125-1(e)  
**Duration:** 2.5 months post plan year

---

## 📅 Plan Year Terms

### Plan Year
12-month period for account activity. Typically calendar year (Jan 1 - Dec 31) but employers may use fiscal year.

**Common Patterns:**
- Calendar Year: Jan 1 - Dec 31
- Fiscal Year: Varies by organization (e.g., Jul 1 - Jun 30)

### MemberFlexSpan
Customer's registration period in a specific plan. Links customer to plan for specific date range.

**Properties:** Customer, Plan, Start Date, End Date, Status

### FlexStage
Status of plan year (Pre-Open, Open, Active, Closed).

**Values:**
- Pre-Open: Before registration
- Open: Open registration period
- Active: Current plan year
- Closed: Historical/completed

### Plan Year End Date (EOY - End of Fiscal Year)
Last day of plan year. Triggers year-end processing (rollover/expiration calculations).

**Typical Date:** December 31

---

## 🏥 Requests Terms

### Request
Payment request for medical expense. Includes receipt/EOB, expense amount, service date, provider.

**Types:**
- Manual request (customer-submitted)
- Auto-pay request (provider-submitted)

### PatientResponsibilityAmount
Customer's financial responsibility after insurance processing. Used for claims with insurance coverage.

**Example:** Doctor bill $500, insurance pays $300 → PatientResponsibility = $200

### RepricedAmount
Adjusted request amount for self-pay claims (no insurance). Provider's negotiated rate.

### UnderwriterAuthority / HasUnderwriterAuthorityStored
Indicates whether request was processed by insurance company. Determines which amount to use: PatientResponsibilityAmount (with insurance) or RepricedAmount (self-pay).

### ClaimTransferLine
Financial transaction record for request payment. Links request to account ledger.

**Properties:** Request ID, Amount, Effective Date, Account ID

### ScheduledItem
Future scheduled payment (autopay request). Reduces available balance immediately even though payment is future-dated.

### AmountRemainingToBeReimbursed
Calculation field for Mobile team to control "Reimburse Me" button visibility.

**Formula:** `OriginalClaimAmount - SUM(ClaimTransferLines.Amount)`  
**Business Rule:** If = $0, request fully scheduled/paid → hide "Reimburse Me" button

### Substantiation
Documentation proving medical expense eligibility. Typically receipt, Explanation of Benefits (EOB), or prescription.

**RegulatoryAgency Requirement:** Requests may require substantiation for audit purposes

---

## 🔄 Transaction Terms

### TransferLine
Generic financial transaction in account. Parent concept for all money movement.

**Types:**
- Contribution
- Request payment
- Adjustment
- Fee
- Rollover
- Expiration

### CashInOut
Contribution or distribution transaction.

**Types:**
- Cash In: Organization/customer contributions
- Cash Out: HealthSavings withdrawals, reimbursements

### CardTransaction
Debit card transaction at point-of-sale (pharmacy, doctor, etc.).

**Properties:** Card ID, Merchant, Amount, Date, Authorization Status

### BalanceChangeAudit
Audit trail record for balance changes. Tracks who, what, when, why for compliance.

---

## 👥 People & Entities

### Customer
Account holder (employee). Person enrolled in FlexAccount/HealthSavings/HealthReimbursement plan.

### Organization
Organization offering benefits. Configures plan rules, processes contributions.

### Dependent
Family customer eligible for coverage or DependentCare FlexAccount benefits.

**Types:**
- Medical dependents (covered under customer's plan)
- Daycare dependents (eligible for DependentCare FlexAccount)

### Provider
Healthcare service provider (doctor, hospital, pharmacy).

---

## ⚙️ System Terms

### NServiceBus
Messaging framework for asynchronous processing. Used for background jobs, event publishing.

**Components:**
- Endpoints (message handlers)
- Messages (commands, events)
- Sagas (long-running processes)

### Entity Framework
ORM (Object-Relational Mapper) for database access.

**Components:**
- DbContext
- Entities (domain objects)
- Configuration classes

### Feature Flag
Configuration toggle enabling/disabling features. Used for gradual rollout, A/B testing.

**Examples:**
- `SplitJobPerformanceV2` - Rollover V1 vs V2
- `Modernization_EdmMultiConnectionMappingEnabled_Claims` - Database connection strategy

### Background Job
Scheduled task running outside request/response cycle.

**Examples:**
- Rollover year-end processing
- Statement generation
- Batch data imports

---

## 🔧 Technical Terms

### Batch Processing
Processing records in groups (batches) rather than individually. Improves performance for large datasets.

**Rollover Example:** 1,000 accounts per batch, 10 concurrent operations

### SemaphoreSlim
Concurrency control mechanism. Limits number of parallel operations to prevent resource exhaustion.

**Usage:** `SemaphoreSlim(10, 10)` = max 10 concurrent operations

### ConcurrentBag
Thread-safe collection for parallel processing. Aggregates results from multiple threads.

### TransactionScope
Ensures database operations complete atomically (all-or-nothing). Rollback on error.

**Rollover Example:** Batch updates wrapped in transaction for data integrity

### Pre-fetching
Loading related data upfront (cached in memory) to avoid N+1 query problems.

**Rollover Example:** Pre-fetch all scheduled items before processing accounts

---

## 📊 RegulatoryAgency Terms

### Qualified Medical Expense
RegulatoryAgency-approved healthcare expense eligible for tax-free payment.

**Reference:** RegulatoryAgency Publication 502  
**Examples:** Doctor visits, prescriptions, dental, vision, medical equipment

### Contribution Limit
Maximum annual contribution allowed by RegulatoryAgency.

**2025 Limits:**
- FlexAccount: $3,200
- HealthSavings Individual: $4,150
- HealthSavings Family: $8,300
- DependentCare FlexAccount: $5,000

**Regulation:** RegulatoryAgency Revenue Procedure 2024-40 (inflation adjustments)

### High-Deductible Health Plan (HDHP)
Health insurance plan with high deductible, required for HealthSavings eligibility.

**2025 HDHP Definition:**
- Minimum deductible: $1,650 (individual), $3,300 (family)
- Maximum out-of-pocket: $8,300 (individual), $16,600 (family)

### Use-It-Or-Lose-It Rule
RegulatoryAgency rule requiring FlexAccount forfeitures. Unused funds (over rollover limit) lost at year-end.

**Exceptions:** Grace period OR $640 rollover (organization choice)

---

## 🏢 GenericCorp-Specific Terms

### Plum Page
GenericCorp internal admin tool for customer service.

### Customer Portal
Public-facing website where members manage accounts, submit claims, view statements.

### CXC JAMS Job
External job processing request data (Requests eXchange Connector).

### Segment4
Legacy codebase namespace/folder. Contains statement generation logic.

---

## 🔍 Acronyms

- **ADO:** Azure DevOps
- **API:** Application Programming Interface
- **CFR:** Code of Federal Regulations
- **DDD:** Domain-Driven Design
- **DTO:** Data Transfer Object
- **EF:** Entity Framework
- **EOB:** Explanation of Benefits (insurance document)
- **EOY:** End of Fiscal Year
- **FlexAccount:** Flexible Spending Account
- **HDHP:** High-Deductible Health Plan
- **PrivacyRegulation:** Health Insurance Portability and Accountability Act
- **HealthReimbursement:** Health Payment Arrangement
- **HealthSavings:** Health Savings Account
- **RegulatoryAgency:** Internal Revenue Service
- **N+1:** Database query anti-pattern (1 query + N additional queries per record)
- **ORM:** Object-Relational Mapper
- **PaymentSecurity:** Payment Card Industry Data Security Standard
- **PDF:** Portable Document Format
- **PHI:** Protected Health Information
- **POC:** Proof of Concept
- **POS:** Point of Sale
- **TDD:** Test-Driven Development

---

## 📚 Regulatory References

### RegulatoryAgency Publications
- **Publication 969:** Health Savings Accounts and Other Tax-Favored Health Plans
- **Publication 502:** Medical and Dental Expenses (qualified expense list)
- **Publication 15-B:** Organization's Tax Guide to Fringe Benefits

### RegulatoryAgency Code Sections
- **IRC §125:** Cafeteria Plans (FlexAccount)
- **IRC §129:** DependentCare Assistance Programs
- **IRC §223:** Health Savings Accounts
- **26 CFR §125-1:** Cafeteria Plan regulations
- **26 CFR §125-5:** FlexAccount rollover and grace period rules

### RegulatoryAgency Notices
- **Notice 2002-45:** HealthReimbursement guidance
- **Revenue Procedure 2024-40:** 2025 inflation adjustments

### PrivacyRegulation
- **45 CFR Part 160:** General administrative requirements
- **45 CFR Part 164:** Security and privacy rules

---

**Glossary Complete** ✅  
**Total Terms:** 80+  
**Categories:** 12 (Account Types, Financial, Plan Year, Requests, Transactions, People, System, Technical, RegulatoryAgency, GenericCorp, Acronyms, Regulations)
