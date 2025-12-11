# Business Glossary: Reimbursement Accounts Domain

**Repository:** C:\PROJECTS\Product.ReimbursementAccounts  
**Purpose:** Authoritative definitions for domain terminology  
**Audience:** Developers, business analysts, product managers

---

## 🏥 Account Types

### FSA (Flexible Spending Account)
Tax-advantaged account for out-of-pocket medical expenses. Pre-tax contributions reduce taxable income. Subject to "use-it-or-lose-it" rule (unused funds over $640 forfeited at year-end). Employer may offer 2.5-month grace period OR $640 carryover, but not both.

**IRS Regulation:** 26 CFR §125 (Cafeteria Plans)  
**Contribution Limit (2025):** $3,200  
**Carryover Limit (2025):** $640

### HSA (Health Savings Account)
Tax-advantaged savings account for medical expenses, available only with High-Deductible Health Plans (HDHP). Triple tax advantage: pre-tax contributions, tax-free growth, tax-free withdrawals for qualified expenses. Funds roll over 100% year-over-year. Member-owned and portable.

**IRS Regulation:** IRC §223  
**Contribution Limit (2025):** $4,150 (individual), $8,300 (family)  
**Rollover:** Unlimited

### HRA (Health Reimbursement Arrangement)
Employer-funded account for reimbursing medical expenses. 100% employer contributions (employees cannot contribute). Employer determines rollover rules. Generally non-portable (funds lost on termination unless employer allows).

**IRS Regulation:** IRS Notice 2002-45  
**Funding:** Employer-only  
**Portability:** Employer-determined

### Dependent Care FSA
Tax-advantaged account for dependent care expenses (daycare, preschool, after-school programs). Eligible dependents: children under 13 or disabled dependents. Subject to "use-it-or-lose-it" rule.

**IRS Regulation:** IRC §129  
**Contribution Limit (2025):** $5,000 ($2,500 if married filing separately)  
**Eligible Dependents:** Under age 13 or disabled

---

## 💰 Financial Terms

### Available Balance
Current spendable funds in account. Calculated as: Opening balance + Contributions - Claims - Scheduled payments - Fees.

**Formula:** `AvailableBalance = SUM(Contributions) - SUM(Claims) - SUM(ScheduledItems) - SUM(Fees)`

### Pending Balance
Funds reserved for scheduled/autopay claims that haven't been paid yet. Reduces available balance even though payment is future-dated.

### Carryover
Unused FSA funds (up to $640) transferred to next plan year. IRS allows employers to offer carryover OR grace period, not both.

**IRS Limit (2025):** $640  
**Regulation:** 26 CFR §125-5(c)

### Forfeiture
Unused FSA funds exceeding carryover limit ($640) that are lost at plan year end. "Use-it-or-lose-it" rule.

**Example:** Member has $800 unused. $640 carries over, $160 forfeited.

### Grace Period
Optional 2.5-month extension (through March 15) allowing members to use prior year FSA funds. Alternative to carryover - employers choose one or the other.

**Regulation:** 26 CFR §125-1(e)  
**Duration:** 2.5 months post plan year

---

## 📅 Plan Year Terms

### Plan Year
12-month period for account activity. Typically calendar year (Jan 1 - Dec 31) but employers may use fiscal year.

**Common Patterns:**
- Calendar Year: Jan 1 - Dec 31
- Fiscal Year: Varies by employer (e.g., Jul 1 - Jun 30)

### MemberFlexSpan
Member's enrollment period in a specific plan. Links member to plan for specific date range.

**Properties:** Member, Plan, Start Date, End Date, Status

### FlexStage
Status of plan year (Pre-Open, Open, Active, Closed).

**Values:**
- Pre-Open: Before enrollment
- Open: Open enrollment period
- Active: Current plan year
- Closed: Historical/completed

### Plan Year End Date (EOFY - End of Fiscal Year)
Last day of plan year. Triggers year-end processing (carryover/forfeiture calculations).

**Typical Date:** December 31

---

## 🏥 Claims Terms

### Claim
Reimbursement request for medical expense. Includes receipt/EOB, expense amount, service date, provider.

**Types:**
- Manual claim (member-submitted)
- Auto-pay claim (provider-submitted)

### PatientResponsibilityAmount
Member's financial responsibility after insurance processing. Used for claims with insurance coverage.

**Example:** Doctor bill $500, insurance pays $300 → PatientResponsibility = $200

### RepricedAmount
Adjusted claim amount for self-pay claims (no insurance). Provider's negotiated rate.

### UnderwriterAuthority / HasUnderwriterAuthorityStored
Indicates whether claim was processed by insurance company. Determines which amount to use: PatientResponsibilityAmount (with insurance) or RepricedAmount (self-pay).

### ClaimTransferLine
Financial transaction record for claim payment. Links claim to account ledger.

**Properties:** Claim ID, Amount, Effective Date, Account ID

### ScheduledItem
Future scheduled payment (autopay claim). Reduces available balance immediately even though payment is future-dated.

### AmountRemainingToBeReimbursed
Calculation field for Mobile team to control "Reimburse Me" button visibility.

**Formula:** `OriginalClaimAmount - SUM(ClaimTransferLines.Amount)`  
**Business Rule:** If = $0, claim fully scheduled/paid → hide "Reimburse Me" button

### Substantiation
Documentation proving medical expense eligibility. Typically receipt, Explanation of Benefits (EOB), or prescription.

**IRS Requirement:** Claims may require substantiation for audit purposes

---

## 🔄 Transaction Terms

### TransferLine
Generic financial transaction in account. Parent concept for all money movement.

**Types:**
- Contribution
- Claim payment
- Adjustment
- Fee
- Carryover
- Forfeiture

### CashInOut
Contribution or distribution transaction.

**Types:**
- Cash In: Employer/member contributions
- Cash Out: HSA withdrawals, reimbursements

### CardTransaction
Debit card transaction at point-of-sale (pharmacy, doctor, etc.).

**Properties:** Card ID, Merchant, Amount, Date, Authorization Status

### BalanceChangeAudit
Audit trail record for balance changes. Tracks who, what, when, why for compliance.

---

## 👥 People & Entities

### Member
Account holder (employee). Person enrolled in FSA/HSA/HRA plan.

### Employer
Organization offering benefits. Configures plan rules, processes contributions.

### Dependent
Family member eligible for coverage or Dependent Care FSA benefits.

**Types:**
- Medical dependents (covered under member's plan)
- Daycare dependents (eligible for Dependent Care FSA)

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
- `SplitJobPerformanceV2` - Carryover V1 vs V2
- `Modernization_EdmMultiConnectionMappingEnabled_Claims` - Database connection strategy

### Background Job
Scheduled task running outside request/response cycle.

**Examples:**
- Carryover year-end processing
- Statement generation
- Batch data imports

---

## 🔧 Technical Terms

### Batch Processing
Processing records in groups (batches) rather than individually. Improves performance for large datasets.

**Carryover Example:** 1,000 accounts per batch, 10 concurrent operations

### SemaphoreSlim
Concurrency control mechanism. Limits number of parallel operations to prevent resource exhaustion.

**Usage:** `SemaphoreSlim(10, 10)` = max 10 concurrent operations

### ConcurrentBag
Thread-safe collection for parallel processing. Aggregates results from multiple threads.

### TransactionScope
Ensures database operations complete atomically (all-or-nothing). Rollback on error.

**Carryover Example:** Batch updates wrapped in transaction for data integrity

### Pre-fetching
Loading related data upfront (cached in memory) to avoid N+1 query problems.

**Carryover Example:** Pre-fetch all scheduled items before processing accounts

---

## 📊 IRS Terms

### Qualified Medical Expense
IRS-approved healthcare expense eligible for tax-free reimbursement.

**Reference:** IRS Publication 502  
**Examples:** Doctor visits, prescriptions, dental, vision, medical equipment

### Contribution Limit
Maximum annual contribution allowed by IRS.

**2025 Limits:**
- FSA: $3,200
- HSA Individual: $4,150
- HSA Family: $8,300
- Dependent Care FSA: $5,000

**Regulation:** IRS Revenue Procedure 2024-40 (inflation adjustments)

### High-Deductible Health Plan (HDHP)
Health insurance plan with high deductible, required for HSA eligibility.

**2025 HDHP Definition:**
- Minimum deductible: $1,650 (individual), $3,300 (family)
- Maximum out-of-pocket: $8,300 (individual), $16,600 (family)

### Use-It-Or-Lose-It Rule
IRS rule requiring FSA forfeitures. Unused funds (over carryover limit) lost at year-end.

**Exceptions:** Grace period OR $640 carryover (employer choice)

---

## 🏢 HealthEquity-Specific Terms

### Plum Page
HealthEquity internal admin tool for customer service.

### Member Portal
Public-facing website where members manage accounts, submit claims, view statements.

### CXC JAMS Job
External job processing claim data (Claims eXchange Connector).

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
- **EOFY:** End of Fiscal Year
- **FSA:** Flexible Spending Account
- **HDHP:** High-Deductible Health Plan
- **HIPAA:** Health Insurance Portability and Accountability Act
- **HRA:** Health Reimbursement Arrangement
- **HSA:** Health Savings Account
- **IRS:** Internal Revenue Service
- **N+1:** Database query anti-pattern (1 query + N additional queries per record)
- **ORM:** Object-Relational Mapper
- **PCI-DSS:** Payment Card Industry Data Security Standard
- **PDF:** Portable Document Format
- **PHI:** Protected Health Information
- **POC:** Proof of Concept
- **POS:** Point of Sale
- **TDD:** Test-Driven Development

---

## 📚 Regulatory References

### IRS Publications
- **Publication 969:** Health Savings Accounts and Other Tax-Favored Health Plans
- **Publication 502:** Medical and Dental Expenses (qualified expense list)
- **Publication 15-B:** Employer's Tax Guide to Fringe Benefits

### IRS Code Sections
- **IRC §125:** Cafeteria Plans (FSA)
- **IRC §129:** Dependent Care Assistance Programs
- **IRC §223:** Health Savings Accounts
- **26 CFR §125-1:** Cafeteria Plan regulations
- **26 CFR §125-5:** FSA carryover and grace period rules

### IRS Notices
- **Notice 2002-45:** HRA guidance
- **Revenue Procedure 2024-40:** 2025 inflation adjustments

### HIPAA
- **45 CFR Part 160:** General administrative requirements
- **45 CFR Part 164:** Security and privacy rules

---

**Glossary Complete** ✅  
**Total Terms:** 80+  
**Categories:** 12 (Account Types, Financial, Plan Year, Claims, Transactions, People, System, Technical, IRS, HealthEquity, Acronyms, Regulations)
