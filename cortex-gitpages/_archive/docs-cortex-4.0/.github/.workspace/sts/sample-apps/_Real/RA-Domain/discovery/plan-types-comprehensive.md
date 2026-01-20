# Comprehensive Plan Types Documentation

**Repository:** C:\PROJECTS\Product.PaymentAccounts  
**Analysis Date:** December 11, 2025  
**Purpose:** Detailed specifications for all payment account types

---

## 📋 Overview

GenericCorp supports 4 primary account types, each with distinct RegulatoryAgency regulations, contribution limits, rollover rules, and tax treatments.

**Supported Account Types:**
1. FlexAccount (Flexible Spending Account)
2. HealthSavings (Health Savings Account)
3. HealthReimbursement (Health Payment Arrangement)
4. DependentCare FlexAccount

---

## 💰 FlexAccount (Flexible Spending Account)

### Purpose
Tax-advantaged account for out-of-pocket medical and dental expenses not covered by insurance.

### RegulatoryAgency Regulations
- **Primary Regulation:** 26 CFR §125 (Cafeteria Plans)
- **Publication:** RegulatoryAgency Publication 969
- **Qualified Expenses:** RegulatoryAgency Publication 502

### 2025 Limits
- **Contribution Limit:** $3,200 annually
- **Rollover Limit:** $640 maximum to next plan year
- **Adjustment:** Annual inflation adjustment per RegulatoryAgency Revenue Procedure

### Key Features

#### Tax Treatment
- **Contributions:** Pre-tax (reduces taxable income)
- **Withdrawals:** Tax-free for qualified medical expenses
- **Organization Contributions:** May contribute (but not required)

#### Use-It-Or-Lose-It Rule
Unused funds exceeding $640 are forfeited at plan year end. This is a strict RegulatoryAgency requirement.

**Example:**
- Customer contributes: $2,500
- Requests during year: $1,700
- Unused at year-end: $800
- **Carries over:** $640
- **Forfeited:** $160

#### Grace Period Option
Organizations may offer 2.5-month grace period (through March 15) as alternative to rollover.

**Important:** Organizations choose EITHER grace period OR rollover, not both.

**Grace Period Details:**
- Duration: 2.5 months post plan year end
- Typical dates: January 1 - March 15
- Purpose: Additional time to incur expenses using prior year funds
- Regulation: 26 CFR §125-1(e)

### Eligible Expenses
Per RegulatoryAgency Publication 502:
- Doctor/specialist visits
- Prescription medications
- Dental care (cleanings, fillings, braces)
- Vision care (exams, glasses, contacts)
- Medical equipment (crutches, wheelchairs)
- Chiropractic services
- Mental health counseling
- Physical therapy

**Exclusions:**
- Cosmetic procedures (unless medically necessary)
- Over-the-counter medications (without prescription)
- Health insurance premiums
- Long-term care

### Plan Year
- Typically calendar year (Jan 1 - Dec 31)
- Some employers use fiscal year

### Portability
- **Non-portable:** Funds forfeited on employment termination
- **Exception:** COBRA continuation may allow FlexAccount continuation

### Code Implementation
- **Entity:** `PaymentAccount` with `PlanType = FlexAccount`
- **Rollover Logic:** `CarryoverDollarsDomainService.CalculateForefeitAndCarryoverBalanceEOY`
- **Limit Enforcement:** ⚠️ NOT IMPLEMENTED (gap identified)

---

## 🏥 HealthSavings (Health Savings Account)

### Purpose
Tax-advantaged savings account for medical expenses, designed for members with High-Deductible Health Plans (HDHP).

### RegulatoryAgency Regulations
- **Primary Regulation:** IRC §223
- **Publication:** RegulatoryAgency Publication 969
- **HDHP Requirements:** IRC §223(c)(2)

### 2025 Limits
- **Individual Contribution:** $4,150
- **Family Contribution:** $8,300
- **Catch-up (55+):** Additional $1,000
- **HDHP Minimum Deductible:** $1,650 (individual), $3,300 (family)
- **HDHP Maximum Out-of-Pocket:** $8,300 (individual), $16,600 (family)

### Key Features

#### Triple Tax Advantage
1. **Contributions:** Pre-tax or tax-deductible
2. **Growth:** Tax-free interest/investment earnings
3. **Withdrawals:** Tax-free for qualified medical expenses

**Unique Benefit:** Only account type with tax-free growth potential

#### 100% Rollover
Unlike FlexAccount, ALL unused funds roll over year-over-year. No "use-it-or-lose-it" rule.

**Example:**
- Year 1 contribution: $4,150, claims: $2,000 → **Balance carries: $2,150**
- Year 2 contribution: $4,150, balance grows to $6,300
- Unlimited rollover continues indefinitely

#### Portability
- **Customer-owned:** Account stays with customer even after job change
- **Portable across employers:** Funds never forfeited due to termination

#### Investment Options
HealthSavingss can invest in stocks, bonds, mutual funds once balance reaches threshold (typically $1,000-$2,000).

#### HDHP Requirement
Customers must be enrolled in qualifying High-Deductible Health Plan.

**2025 HDHP Definition:**
- Minimum deductible: $1,650 (individual), $3,300 (family)
- Maximum out-of-pocket: $8,300 (individual), $16,600 (family)
- **Disqualifying coverage:** Cannot have non-HDHP health plan, FlexAccount (with exceptions), Medicare

### Withdrawal Rules

#### Qualified Medical Expenses
- Tax-free and penalty-free at any age
- Same eligible expenses as FlexAccount (RegulatoryAgency Pub 502)
- Can reimburse expenses from prior years (no time limit)

#### Non-Qualified Withdrawals
- **Before age 65:** 20% penalty + income tax
- **After age 65:** Income tax only (no penalty) - functions like traditional IRA

### Plan Year
- Calendar year (Jan 1 - Dec 31)
- Contributions allowed through tax filing deadline (April 15 of following year)

### Code Implementation
- **Entity:** `PaymentAccount` with `PlanType = HealthSavings`
- **Rollover:** 100% automatic (no special processing needed)
- **Investment Tracking:** May require separate module (not analyzed yet)

---

## 🏢 HealthReimbursement (Health Payment Arrangement)

### Purpose
Organization-funded account for reimbursing employee medical expenses.

### RegulatoryAgency Regulations
- **Primary Regulation:** RegulatoryAgency Notice 2002-45
- **Updated Guidance:** RegulatoryAgency Notice 2013-54 (integration with ACA)

### Funding Rules
- **100% organization-funded:** Employees cannot contribute
- **No RegulatoryAgency contribution limits:** Organization sets limits
- **Organization discretion:** Organization controls all rules (rollover, portability, eligible expenses)

### Key Features

#### Organization Control
Unlike FlexAccount/HealthSavings, employers have full flexibility:
- Set custom contribution amounts (no RegulatoryAgency limit)
- Decide rollover rules (0% to 100%)
- Determine portability (typically non-portable)
- Define eligible expenses (within RegulatoryAgency guidelines)

#### Typical Configurations

**Standard HealthReimbursement:**
- Reimburses out-of-pocket medical expenses
- Often integrated with health insurance plan
- Organization may require minimum deductible met first

**QSEHealthReimbursement (Qualified Small Organization HealthReimbursement):**
- For employers with <50 employees
- Employees can use with individual insurance
- Subject to annual limits

**ICHealthReimbursement (Individual Coverage HealthReimbursement):**
- Reimburses individual health insurance premiums
- Replaces group health plan
- Employees choose individual marketplace plans

### Tax Treatment
- **Organization contributions:** Tax-deductible business expense
- **Employee reimbursements:** Tax-free

### Rollover
Organization determines rollover policy:
- Some employers: 100% rollover
- Some employers: Use-it-or-lose-it
- Some employers: Partial rollover (e.g., 50%)

### Portability
- **Typically non-portable:** Funds forfeited on termination
- **Exception:** Some employers allow limited portability (COBRA continuation)

### Plan Year
Organization-defined (calendar or fiscal year)

### Code Implementation
- **Entity:** `PaymentAccount` with `PlanType = HealthReimbursement`
- **Flexible Rules:** Configuration-driven (organization settings)
- **Rollover Logic:** Depends on organization configuration

---

## 👶 DependentCare FlexAccount

### Purpose
Tax-advantaged account for dependent care expenses (daycare, preschool, after-school programs).

### RegulatoryAgency Regulations
- **Primary Regulation:** IRC §129
- **Qualified Expenses:** IRC §21 (Child and DependentCare Credit rules)

### 2025 Limits
- **Contribution Limit:** $5,000 annually
- **Married Filing Separately:** $2,500 each spouse
- **Coordination with Tax Credit:** Cannot "double-dip" (FlexAccount reduces tax credit)

### Key Features

#### Eligible Dependents
- **Children under age 13**
- **Disabled dependents** (spouse or other dependent incapable of self-care)

#### Eligible Expenses
- Daycare center costs
- Preschool or nursery school
- Before/after school programs
- Summer day camps (not overnight)
- In-home care providers (nanny, au pair)

**Exclusions:**
- Overnight camps
- Kindergarten (educational expenses)
- Care provided by spouse or dependent under 19
- Tuition for grades K-12

#### Use-It-Or-Lose-It Rule
Same as medical FlexAccount - unused funds forfeited at year-end.

**No rollover option:** RegulatoryAgency does not allow DependentCare FlexAccount rollover (unlike medical FlexAccount's $640 rollover)

**No grace period standard:** Less common than medical FlexAccount grace periods

#### Work Requirement
Both spouses must be working, looking for work, or full-time students to request DependentCare FlexAccount.

**Exception:** One spouse disabled and incapable of self-care

### Tax Considerations

#### Coordination with DependentCare Tax Credit
DependentCare FlexAccount reduces the amount eligible for tax credit.

**Strategy Decision:**
- FlexAccount advantage: Reduces taxable income (higher earners benefit)
- Tax credit advantage: Up to $3,000 per child (lower earners benefit)
- Cannot request same expenses under both

### Plan Year
- Typically calendar year (Jan 1 - Dec 31)
- Must incur AND pay expenses during plan year (stricter than medical FlexAccount)

### Code Implementation
- **Entity:** `PaymentAccount` with `PlanType = DependentCare`
- **Dependent Tracking:** `Dependent` entity links to `DependentSpan`
- **Eligible Expense Validation:** Requires dependent age checks

---

## 📊 Comparative Summary

| Feature | FlexAccount | HealthSavings | HealthReimbursement | DependentCare FlexAccount |
|---------|-----|-----|-----|-------------------|
| **Who Funds** | Employee (+ organization optional) | Employee (+ organization optional) | Organization only | Employee (+ organization optional) |
| **2025 Contribution Limit** | $3,200 | $4,150 / $8,300 | Organization-set | $5,000 |
| **Rollover** | $640 max | 100% | Organization-set | None |
| **Portability** | No | Yes | Usually no | No |
| **Tax Advantage** | Pre-tax contributions, tax-free withdrawals | Triple tax advantage | Tax-free reimbursements | Pre-tax contributions, tax-free withdrawals |
| **Eligible Expenses** | Medical (RegulatoryAgency Pub 502) | Medical (RegulatoryAgency Pub 502) | Organization-defined (typically medical) | Dependent care (IRC §21) |
| **Plan Requirement** | Any health plan | HDHP only | Organization-defined | Working requirement |
| **RegulatoryAgency Regulation** | 26 CFR §125 | IRC §223 | RegulatoryAgency Notice 2002-45 | IRC §129 |

---

## 🔍 Business Rules by Plan Type

### FlexAccount Business Rules
1. **Contribution deadline:** Before plan year starts (election irrevocable except for qualifying life events)
2. **Requests deadline:** Varies (run-out period, typically 90 days post plan year)
3. **Rollover OR grace period:** Organization chooses one, not both
4. **Expiration processing:** Automated at year-end (CarryoverDollarsDomainService)
5. **Mid-year changes:** Only for qualifying life events (marriage, birth, adoption, etc.)

### HealthSavings Business Rules
1. **HDHP registration verification:** Required monthly (lose eligibility if non-HDHP coverage)
2. **Contribution timing:** Anytime during year + through tax filing deadline
3. **Pro-ration:** If HDHP mid-year, contributions pro-rated by month
4. **Investment threshold:** Typically $1,000-$2,000 before investments allowed
5. **Age 55+ catch-up:** Additional $1,000 annually

### HealthReimbursement Business Rules
1. **Organization discretion:** All rules set by organization (no RegulatoryAgency standard)
2. **Integration with insurance:** Often tied to specific health plan
3. **Request substantiation:** Typically required (receipts, EOBs)
4. **Termination handling:** Organization policy determines fund disposition

### DependentCare FlexAccount Business Rules
1. **Incurred AND paid:** Expenses must be both incurred and paid during plan year
2. **Age verification:** Children must be under 13 when care received
3. **Provider identification:** Must provide care provider tax ID or SSN
4. **Work requirement:** Both spouses working/seeking work/full-time student
5. **No rollover:** Strict use-it-or-lose-it (no $640 rollover like medical FlexAccount)

---

## 🚨 Compliance Considerations

### FlexAccount Compliance
- **Uniform coverage rule:** Full annual election available from day 1 (even if not fully contributed)
- **Non-discrimination testing:** Cannot favor highly compensated employees
- **Form 5500 reporting:** Required if part of BenefitsRegulation plan

### HealthSavings Compliance
- **HDHP verification:** Must maintain HDHP throughout year
- **Medicare coordination:** Cannot contribute once Medicare-eligible
- **Form 8889:** Annual tax reporting required
- **Prohibited transactions:** Cannot use as personal investment vehicle

### HealthReimbursement Compliance
- **PrivacyRegulation privacy:** HealthReimbursement claims are Protected Health Information (PHI)
- **ACA integration:** Must coordinate with Affordable Care Act requirements
- **BenefitsRegulation reporting:** Subject to BenefitsRegulation if organization has 100+ participants

### DependentCare FlexAccount Compliance
- **Provider reporting:** W-10 form for provider information
- **Tax credit coordination:** RegulatoryAgency Form 2441 coordination
- **Household employment:** Nanny tax obligations if in-home care

---

## 💻 Code Implementation Notes

### Current Implementation
- **Entity:** `PaymentAccount.PlanType` (enum: FlexAccount, HealthSavings, HealthReimbursement, DependentCare)
- **Rollover Service:** `CarryoverDollarsDomainService` (FlexAccount only)
- **Balance Service:** `PaymentAccountBalanceService` (all types)
- **Configuration:** `RolloverSettings` (organization-specific rules)

### Gaps Identified
1. ⚠️ **RegulatoryAgency limit validation missing** - Contribution limits not enforced
2. ⚠️ **HDHP verification missing** - HealthSavings eligibility not validated
3. ⚠️ **Dependent age checks unclear** - DependentCare FlexAccount age validation
4. ⚠️ **Grace period logic undocumented** - FlexAccount grace period implementation unclear
5. ⚠️ **HealthReimbursement custom rules** - Organization-specific configuration implementation unclear

---

## 📈 Usage Patterns (from Code Analysis)

### Most Common: FlexAccount
- Highest entity count in `PaymentAccount` entity
- Most complex year-end processing (CarryoverDollarsDomainService)
- Extensive feature flag usage (V1 vs V2 processing)

### Growing: HealthSavings
- Increasing popularity (tax advantages)
- Simpler processing (no expiration logic)
- Investment module may exist (not analyzed yet)

### Organization-Specific: HealthReimbursement
- Configuration-driven
- Less standardized processing
- Varies significantly by organization

### Specialized: DependentCare FlexAccount
- Separate from medical FlexAccount
- Distinct eligible expense rules
- Dependent tracking integration

---

**Plan Types Documentation Complete** ✅  
**Total Account Types:** 4 (FlexAccount, HealthSavings, HealthReimbursement, DependentCare FlexAccount)  
**Regulatory References:** 10+ RegulatoryAgency codes/publications  
**Compliance Gaps Identified:** 5 critical validations missing
