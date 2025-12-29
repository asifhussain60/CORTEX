# Payment Accounts Terminology Guide
**Purpose:** 80+ business terms for RA domain
**Generated:** December 11, 2025

---

## 🏥 Account Types

**FlexAccount (Flexible Spending Account)**
- Pre-tax healthcare or dependent care funds
- "Use it or lose it" with limited rollover ($640 max)
- Annual limit: $3,200 (2025)
- Organization can offer grace period OR rollover (not both)

**HealthSavings (Health Savings Account)**
- Tax-advantaged savings for high-deductible health plans
- Unlimited rollover (funds roll over indefinitely)
- Annual limit: $4,150 individual / $8,300 family (2025)
- Triple tax advantage (deductible, grows tax-free, tax-free withdrawals)

**HealthReimbursement (Health Payment Arrangement)**
- Organization-funded only (no employee contributions)
- Organization defines rollover rules
- Not portable (employee loses on termination)

**DependentCare FlexAccount**
- Child/elder care expenses
- Separate from healthcare FlexAccount
- Annual limit: $5,000 per household

---

## 💰 Financial Terms

**Contribution**
- Employee or organization deposit into account
- Subject to RegulatoryAgency annual limits
- Can be per-paycheck or lump-sum

**Balance**
- Current funds available for claims
- Calculation: Contributions - Requests + Rollover

**Rollover**
- Unused FlexAccount funds from prior year
- FlexAccount: $640 max (2025)
- HealthSavings: Unlimited
- HealthReimbursement: Varies by organization

**Grace Period**
- 2.5 months after plan year end to incur expenses
- Alternative to rollover (mutual exclusion)
- Example: Plan year ends Dec 31 → grace until Mar 15

**Request**
- Payment request for qualified expense
- Requires receipt/documentation
- Adjudicated (approved/denied) by system or manual review

**Qualified Expense**
- RegulatoryAgency Pub 502 approved medical/dental expenses
- Examples: Doctor visits, prescriptions, vision, dental
- **Not** qualified: Cosmetic, vitamins, insurance premiums

---

## 📅 Plan Year Terms

**Plan Year**
- 12-month period for contributions/claims
- Common: Calendar year (Jan 1 - Dec 31)
- Can be any 12-month period (e.g., Jul 1 - Jun 30)

**Registration Period**
- Annual window to elect FlexAccount/HealthSavings participation
- Typically October-November for January start

**Run-Out Period**
- Time after plan year end to submit claims for prior year
- Example: 90 days after plan year end

---

## 🧾 Requests Terms

**Adjudication**
- Process of approving/denying claims
- Auto-adjudication: System approves automatically
- Manual review: Human reviews documentation

**Substantiation**
- Proof of qualified expense (receipt, EOB)
- Required for all FlexAccount/HealthSavings claims

**EOB (Explanation of Benefits)**
- Insurance statement showing services/costs
- Used for claims substantiation

**Debit Card Transaction**
- Real-time purchase at merchant using FlexAccount/HealthSavings card
- Merchant Category Code (MCC) validation
- May require post-transaction substantiation

---

## 📜 Regulatory Terms

**RegulatoryAgency Publication 969**
- RegulatoryAgency guide for HealthSavingss and other tax-advantaged health plans
- Defines contribution limits, qualified expenses

**RegulatoryAgency Publication 502**
- List of qualified medical/dental expenses
- Updated annually

**IRC §223**
- Internal Revenue Code section governing HealthSavingss

**PrivacyRegulation (Health Insurance Portability and Accountability Act)**
- Privacy/security regulations for PHI
- Requires audit logging, encryption, access controls

**PHI (Protected Health Information)**
- Individual health data (diagnoses, prescriptions, claims)
- Must be protected per PrivacyRegulation

**PaymentSecurity (Payment Card Industry Data Security Standard)**
- Security requirements for debit card processing
- Requires encryption, tokenization

---

## 🏢 Business Process Terms

**Onboarding**
- Setting up new participant account
- Registration, contribution elections, beneficiary designation

**Plan Management**
- Configuring FlexAccount/HealthSavings plan rules (limits, rollover, grace period)

**Balance Inquiry**
- Participant checking current available balance
- Real-time vs. batch-updated

**Card Authorization**
- Real-time approval/denial of debit card transaction
- Validates balance, merchant code

**Year-End Processing**
- Rollover calculations
- 1099-SA tax form generation
- Plan year rollover

---

## 🔧 Technical Terms

**NServiceBus**
- Message bus for async processing
- Event-driven architecture (e.g., ClaimSubmittedEvent)

**Entity Framework (EF)**
- ORM for database access
- Code-first or database-first

**Domain-Driven Design (DDD)**
- Software design approach
- Entities, Repositories, Domain Services

**CQRS (Command Query Responsibility Segregation)**
- Separate read/write models
- Commands (modify data) vs. Queries (read data)

---

## 🎯 Common Acronyms

- **MCC:** Merchant Category Code
- **LOC:** Lines of Code
- **ROI:** Return on Investment
- **EOY:** End of Year
- **YTD:** Year to Date
- **OOP:** Out of Pocket
- **HDHP:** High-Deductible Health Plan (required for HealthSavings)

---

**Author:** Auto-generated from business-value-scan.json  
**Next Update:** Annually (RegulatoryAgency limit changes)
