# Reimbursement Accounts Terminology Guide
**Purpose:** 80+ business terms for RA domain
**Generated:** December 11, 2025

---

## 🏥 Account Types

**FSA (Flexible Spending Account)**
- Pre-tax healthcare or dependent care funds
- "Use it or lose it" with limited carryover ($640 max)
- Annual limit: $3,200 (2025)
- Employer can offer grace period OR carryover (not both)

**HSA (Health Savings Account)**
- Tax-advantaged savings for high-deductible health plans
- Unlimited carryover (funds roll over indefinitely)
- Annual limit: $4,150 individual / $8,300 family (2025)
- Triple tax advantage (deductible, grows tax-free, tax-free withdrawals)

**HRA (Health Reimbursement Arrangement)**
- Employer-funded only (no employee contributions)
- Employer defines carryover rules
- Not portable (employee loses on termination)

**Dependent Care FSA**
- Child/elder care expenses
- Separate from healthcare FSA
- Annual limit: $5,000 per household

---

## 💰 Financial Terms

**Contribution**
- Employee or employer deposit into account
- Subject to IRS annual limits
- Can be per-paycheck or lump-sum

**Balance**
- Current funds available for claims
- Calculation: Contributions - Claims + Carryover

**Carryover**
- Unused FSA funds from prior year
- FSA: $640 max (2025)
- HSA: Unlimited
- HRA: Varies by employer

**Grace Period**
- 2.5 months after plan year end to incur expenses
- Alternative to carryover (mutual exclusion)
- Example: Plan year ends Dec 31 → grace until Mar 15

**Claim**
- Reimbursement request for qualified expense
- Requires receipt/documentation
- Adjudicated (approved/denied) by system or manual review

**Qualified Expense**
- IRS Pub 502 approved medical/dental expenses
- Examples: Doctor visits, prescriptions, vision, dental
- **Not** qualified: Cosmetic, vitamins, insurance premiums

---

## 📅 Plan Year Terms

**Plan Year**
- 12-month period for contributions/claims
- Common: Calendar year (Jan 1 - Dec 31)
- Can be any 12-month period (e.g., Jul 1 - Jun 30)

**Enrollment Period**
- Annual window to elect FSA/HSA participation
- Typically October-November for January start

**Run-Out Period**
- Time after plan year end to submit claims for prior year
- Example: 90 days after plan year end

---

## 🧾 Claims Terms

**Adjudication**
- Process of approving/denying claims
- Auto-adjudication: System approves automatically
- Manual review: Human reviews documentation

**Substantiation**
- Proof of qualified expense (receipt, EOB)
- Required for all FSA/HSA claims

**EOB (Explanation of Benefits)**
- Insurance statement showing services/costs
- Used for claims substantiation

**Debit Card Transaction**
- Real-time purchase at merchant using FSA/HSA card
- Merchant Category Code (MCC) validation
- May require post-transaction substantiation

---

## 📜 Regulatory Terms

**IRS Publication 969**
- IRS guide for HSAs and other tax-advantaged health plans
- Defines contribution limits, qualified expenses

**IRS Publication 502**
- List of qualified medical/dental expenses
- Updated annually

**IRC §223**
- Internal Revenue Code section governing HSAs

**HIPAA (Health Insurance Portability and Accountability Act)**
- Privacy/security regulations for PHI
- Requires audit logging, encryption, access controls

**PHI (Protected Health Information)**
- Individual health data (diagnoses, prescriptions, claims)
- Must be protected per HIPAA

**PCI-DSS (Payment Card Industry Data Security Standard)**
- Security requirements for debit card processing
- Requires encryption, tokenization

---

## 🏢 Business Process Terms

**Onboarding**
- Setting up new participant account
- Enrollment, contribution elections, beneficiary designation

**Plan Management**
- Configuring FSA/HSA plan rules (limits, carryover, grace period)

**Balance Inquiry**
- Participant checking current available balance
- Real-time vs. batch-updated

**Card Authorization**
- Real-time approval/denial of debit card transaction
- Validates balance, merchant code

**Year-End Processing**
- Carryover calculations
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
- **HDHP:** High-Deductible Health Plan (required for HSA)

---

**Author:** Auto-generated from business-value-scan.json  
**Next Update:** Annually (IRS limit changes)
