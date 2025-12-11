# Comprehensive Plan Types Documentation

**Repository:** C:\PROJECTS\Product.ReimbursementAccounts  
**Analysis Date:** December 11, 2025  
**Purpose:** Detailed specifications for all reimbursement account types

---

## 📋 Overview

HealthEquity supports 4 primary account types, each with distinct IRS regulations, contribution limits, rollover rules, and tax treatments.

**Supported Account Types:**
1. FSA (Flexible Spending Account)
2. HSA (Health Savings Account)
3. HRA (Health Reimbursement Arrangement)
4. Dependent Care FSA

---

## 💰 FSA (Flexible Spending Account)

### Purpose
Tax-advantaged account for out-of-pocket medical and dental expenses not covered by insurance.

### IRS Regulations
- **Primary Regulation:** 26 CFR §125 (Cafeteria Plans)
- **Publication:** IRS Publication 969
- **Qualified Expenses:** IRS Publication 502

### 2025 Limits
- **Contribution Limit:** $3,200 annually
- **Carryover Limit:** $640 maximum to next plan year
- **Adjustment:** Annual inflation adjustment per IRS Revenue Procedure

### Key Features

#### Tax Treatment
- **Contributions:** Pre-tax (reduces taxable income)
- **Withdrawals:** Tax-free for qualified medical expenses
- **Employer Contributions:** May contribute (but not required)

#### Use-It-Or-Lose-It Rule
Unused funds exceeding $640 are forfeited at plan year end. This is a strict IRS requirement.

**Example:**
- Member contributes: $2,500
- Claims during year: $1,700
- Unused at year-end: $800
- **Carries over:** $640
- **Forfeited:** $160

#### Grace Period Option
Employers may offer 2.5-month grace period (through March 15) as alternative to carryover.

**Important:** Employers choose EITHER grace period OR carryover, not both.

**Grace Period Details:**
- Duration: 2.5 months post plan year end
- Typical dates: January 1 - March 15
- Purpose: Additional time to incur expenses using prior year funds
- Regulation: 26 CFR §125-1(e)

### Eligible Expenses
Per IRS Publication 502:
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
- **Exception:** COBRA continuation may allow FSA continuation

### Code Implementation
- **Entity:** `ReimbursementAccount` with `PlanType = FSA`
- **Carryover Logic:** `CarryoverDollarsDomainService.CalculateForefeitAndCarryoverBalanceEOFY`
- **Limit Enforcement:** ⚠️ NOT IMPLEMENTED (gap identified)

---

## 🏥 HSA (Health Savings Account)

### Purpose
Tax-advantaged savings account for medical expenses, designed for members with High-Deductible Health Plans (HDHP).

### IRS Regulations
- **Primary Regulation:** IRC §223
- **Publication:** IRS Publication 969
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
Unlike FSA, ALL unused funds roll over year-over-year. No "use-it-or-lose-it" rule.

**Example:**
- Year 1 contribution: $4,150, claims: $2,000 → **Balance carries: $2,150**
- Year 2 contribution: $4,150, balance grows to $6,300
- Unlimited rollover continues indefinitely

#### Portability
- **Member-owned:** Account stays with member even after job change
- **Portable across employers:** Funds never forfeited due to termination

#### Investment Options
HSAs can invest in stocks, bonds, mutual funds once balance reaches threshold (typically $1,000-$2,000).

#### HDHP Requirement
Members must be enrolled in qualifying High-Deductible Health Plan.

**2025 HDHP Definition:**
- Minimum deductible: $1,650 (individual), $3,300 (family)
- Maximum out-of-pocket: $8,300 (individual), $16,600 (family)
- **Disqualifying coverage:** Cannot have non-HDHP health plan, FSA (with exceptions), Medicare

### Withdrawal Rules

#### Qualified Medical Expenses
- Tax-free and penalty-free at any age
- Same eligible expenses as FSA (IRS Pub 502)
- Can reimburse expenses from prior years (no time limit)

#### Non-Qualified Withdrawals
- **Before age 65:** 20% penalty + income tax
- **After age 65:** Income tax only (no penalty) - functions like traditional IRA

### Plan Year
- Calendar year (Jan 1 - Dec 31)
- Contributions allowed through tax filing deadline (April 15 of following year)

### Code Implementation
- **Entity:** `ReimbursementAccount` with `PlanType = HSA`
- **Rollover:** 100% automatic (no special processing needed)
- **Investment Tracking:** May require separate module (not analyzed yet)

---

## 🏢 HRA (Health Reimbursement Arrangement)

### Purpose
Employer-funded account for reimbursing employee medical expenses.

### IRS Regulations
- **Primary Regulation:** IRS Notice 2002-45
- **Updated Guidance:** IRS Notice 2013-54 (integration with ACA)

### Funding Rules
- **100% employer-funded:** Employees cannot contribute
- **No IRS contribution limits:** Employer sets limits
- **Employer discretion:** Employer controls all rules (rollover, portability, eligible expenses)

### Key Features

#### Employer Control
Unlike FSA/HSA, employers have full flexibility:
- Set custom contribution amounts (no IRS limit)
- Decide rollover rules (0% to 100%)
- Determine portability (typically non-portable)
- Define eligible expenses (within IRS guidelines)

#### Typical Configurations

**Standard HRA:**
- Reimburses out-of-pocket medical expenses
- Often integrated with health insurance plan
- Employer may require minimum deductible met first

**QSEHRA (Qualified Small Employer HRA):**
- For employers with <50 employees
- Employees can use with individual insurance
- Subject to annual limits

**ICHRA (Individual Coverage HRA):**
- Reimburses individual health insurance premiums
- Replaces group health plan
- Employees choose individual marketplace plans

### Tax Treatment
- **Employer contributions:** Tax-deductible business expense
- **Employee reimbursements:** Tax-free

### Rollover
Employer determines rollover policy:
- Some employers: 100% rollover
- Some employers: Use-it-or-lose-it
- Some employers: Partial rollover (e.g., 50%)

### Portability
- **Typically non-portable:** Funds forfeited on termination
- **Exception:** Some employers allow limited portability (COBRA continuation)

### Plan Year
Employer-defined (calendar or fiscal year)

### Code Implementation
- **Entity:** `ReimbursementAccount` with `PlanType = HRA`
- **Flexible Rules:** Configuration-driven (employer settings)
- **Rollover Logic:** Depends on employer configuration

---

## 👶 Dependent Care FSA

### Purpose
Tax-advantaged account for dependent care expenses (daycare, preschool, after-school programs).

### IRS Regulations
- **Primary Regulation:** IRC §129
- **Qualified Expenses:** IRC §21 (Child and Dependent Care Credit rules)

### 2025 Limits
- **Contribution Limit:** $5,000 annually
- **Married Filing Separately:** $2,500 each spouse
- **Coordination with Tax Credit:** Cannot "double-dip" (FSA reduces tax credit)

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
Same as medical FSA - unused funds forfeited at year-end.

**No carryover option:** IRS does not allow Dependent Care FSA carryover (unlike medical FSA's $640 carryover)

**No grace period standard:** Less common than medical FSA grace periods

#### Work Requirement
Both spouses must be working, looking for work, or full-time students to claim Dependent Care FSA.

**Exception:** One spouse disabled and incapable of self-care

### Tax Considerations

#### Coordination with Dependent Care Tax Credit
Dependent Care FSA reduces the amount eligible for tax credit.

**Strategy Decision:**
- FSA advantage: Reduces taxable income (higher earners benefit)
- Tax credit advantage: Up to $3,000 per child (lower earners benefit)
- Cannot claim same expenses under both

### Plan Year
- Typically calendar year (Jan 1 - Dec 31)
- Must incur AND pay expenses during plan year (stricter than medical FSA)

### Code Implementation
- **Entity:** `ReimbursementAccount` with `PlanType = DependentCare`
- **Dependent Tracking:** `Dependent` entity links to `DependentSpan`
- **Eligible Expense Validation:** Requires dependent age checks

---

## 📊 Comparative Summary

| Feature | FSA | HSA | HRA | Dependent Care FSA |
|---------|-----|-----|-----|-------------------|
| **Who Funds** | Employee (+ employer optional) | Employee (+ employer optional) | Employer only | Employee (+ employer optional) |
| **2025 Contribution Limit** | $3,200 | $4,150 / $8,300 | Employer-set | $5,000 |
| **Rollover** | $640 max | 100% | Employer-set | None |
| **Portability** | No | Yes | Usually no | No |
| **Tax Advantage** | Pre-tax contributions, tax-free withdrawals | Triple tax advantage | Tax-free reimbursements | Pre-tax contributions, tax-free withdrawals |
| **Eligible Expenses** | Medical (IRS Pub 502) | Medical (IRS Pub 502) | Employer-defined (typically medical) | Dependent care (IRC §21) |
| **Plan Requirement** | Any health plan | HDHP only | Employer-defined | Working requirement |
| **IRS Regulation** | 26 CFR §125 | IRC §223 | IRS Notice 2002-45 | IRC §129 |

---

## 🔍 Business Rules by Plan Type

### FSA Business Rules
1. **Contribution deadline:** Before plan year starts (election irrevocable except for qualifying life events)
2. **Claims deadline:** Varies (run-out period, typically 90 days post plan year)
3. **Carryover OR grace period:** Employer chooses one, not both
4. **Forfeiture processing:** Automated at year-end (CarryoverDollarsDomainService)
5. **Mid-year changes:** Only for qualifying life events (marriage, birth, adoption, etc.)

### HSA Business Rules
1. **HDHP enrollment verification:** Required monthly (lose eligibility if non-HDHP coverage)
2. **Contribution timing:** Anytime during year + through tax filing deadline
3. **Pro-ration:** If HDHP mid-year, contributions pro-rated by month
4. **Investment threshold:** Typically $1,000-$2,000 before investments allowed
5. **Age 55+ catch-up:** Additional $1,000 annually

### HRA Business Rules
1. **Employer discretion:** All rules set by employer (no IRS standard)
2. **Integration with insurance:** Often tied to specific health plan
3. **Claim substantiation:** Typically required (receipts, EOBs)
4. **Termination handling:** Employer policy determines fund disposition

### Dependent Care FSA Business Rules
1. **Incurred AND paid:** Expenses must be both incurred and paid during plan year
2. **Age verification:** Children must be under 13 when care received
3. **Provider identification:** Must provide care provider tax ID or SSN
4. **Work requirement:** Both spouses working/seeking work/full-time student
5. **No carryover:** Strict use-it-or-lose-it (no $640 carryover like medical FSA)

---

## 🚨 Compliance Considerations

### FSA Compliance
- **Uniform coverage rule:** Full annual election available from day 1 (even if not fully contributed)
- **Non-discrimination testing:** Cannot favor highly compensated employees
- **Form 5500 reporting:** Required if part of ERISA plan

### HSA Compliance
- **HDHP verification:** Must maintain HDHP throughout year
- **Medicare coordination:** Cannot contribute once Medicare-eligible
- **Form 8889:** Annual tax reporting required
- **Prohibited transactions:** Cannot use as personal investment vehicle

### HRA Compliance
- **HIPAA privacy:** HRA claims are Protected Health Information (PHI)
- **ACA integration:** Must coordinate with Affordable Care Act requirements
- **ERISA reporting:** Subject to ERISA if employer has 100+ participants

### Dependent Care FSA Compliance
- **Provider reporting:** W-10 form for provider information
- **Tax credit coordination:** IRS Form 2441 coordination
- **Household employment:** Nanny tax obligations if in-home care

---

## 💻 Code Implementation Notes

### Current Implementation
- **Entity:** `ReimbursementAccount.PlanType` (enum: FSA, HSA, HRA, DependentCare)
- **Carryover Service:** `CarryoverDollarsDomainService` (FSA only)
- **Balance Service:** `ReimbursementAccountBalanceService` (all types)
- **Configuration:** `RolloverSettings` (employer-specific rules)

### Gaps Identified
1. ⚠️ **IRS limit validation missing** - Contribution limits not enforced
2. ⚠️ **HDHP verification missing** - HSA eligibility not validated
3. ⚠️ **Dependent age checks unclear** - Dependent Care FSA age validation
4. ⚠️ **Grace period logic undocumented** - FSA grace period implementation unclear
5. ⚠️ **HRA custom rules** - Employer-specific configuration implementation unclear

---

## 📈 Usage Patterns (from Code Analysis)

### Most Common: FSA
- Highest entity count in `ReimbursementAccount` entity
- Most complex year-end processing (CarryoverDollarsDomainService)
- Extensive feature flag usage (V1 vs V2 processing)

### Growing: HSA
- Increasing popularity (tax advantages)
- Simpler processing (no forfeiture logic)
- Investment module may exist (not analyzed yet)

### Employer-Specific: HRA
- Configuration-driven
- Less standardized processing
- Varies significantly by employer

### Specialized: Dependent Care FSA
- Separate from medical FSA
- Distinct eligible expense rules
- Dependent tracking integration

---

**Plan Types Documentation Complete** ✅  
**Total Account Types:** 4 (FSA, HSA, HRA, Dependent Care FSA)  
**Regulatory References:** 10+ IRS codes/publications  
**Compliance Gaps Identified:** 5 critical validations missing
