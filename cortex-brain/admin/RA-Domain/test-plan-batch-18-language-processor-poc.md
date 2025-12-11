# BATCH 18: Language Processor Proof of Concept (40 mins)

**Objective:** Validate Language Processor concept before full CORTEX integration

**Status:** ⏳ PENDING  
**Prerequisites:** Batches 1-17 complete (especially Batch 2.5 - External Intelligence)  
**Duration:** 40 minutes  
**Success Criteria:** 80%+ accuracy in business description generation

---

## 🎯 POC Scope

**Test Subject:** Single entity - `ReimbursementAccount.cs` (most critical domain entity)

**Goal:** Prove that AST graphs + external intelligence → professional business documentation

**Technology Stack:**
- **NLP:** spaCy for named entity recognition
- **Scraping:** BeautifulSoup for IRS.gov
- **AST:** Existing tree-sitter-c-sharp analysis
- **Semantic Mapping:** Basic keyword matching (POC only)

---

## 📋 Tasks

### Task 1: Extract Entity Structure (10 mins)
- [ ] Parse `ReimbursementAccount.cs` using existing AST script
- [ ] Extract: class name, properties, navigation relationships
- [ ] Identify: data types, validation attributes, XML doc comments

**Expected Output:**
```json
{
  "class": "ReimbursementAccount",
  "properties": [
    {"name": "ReimbursementAccountId", "type": "Guid"},
    {"name": "PlanType", "type": "enum"},
    {"name": "AvailableBalance", "type": "decimal"},
    {"name": "PlanYearStartDate", "type": "DateTime"},
    {"name": "PlanYearEndDate", "type": "DateTime"}
  ],
  "navigation_properties": ["TransferLines", "ScheduledItems", "Member"]
}
```

### Task 2: Fetch External Intelligence (10 mins)
- [ ] Scrape IRS Publication 969 (FSA/HSA section)
- [ ] Extract: contribution limits (2025), carryover rules, eligible expenses
- [ ] Parse: 26 CFR §125 (FSA regulations)
- [ ] Cache results locally (JSON)

**Expected Output:**
```json
{
  "source": "IRS Publication 969 (2025)",
  "fsa_contribution_limit": 3200,
  "fsa_carryover_limit": 640,
  "hsa_contribution_limit_individual": 4150,
  "hsa_contribution_limit_family": 8300,
  "regulations": [
    {"code": "26 CFR §125-5(c)", "topic": "FSA carryover rules"},
    {"code": "IRC §223", "topic": "HSA qualified accounts"}
  ]
}
```

### Task 3: Generate Business Description (15 mins)
- [ ] Map technical terms → business language
  - `ReimbursementAccount` → "Healthcare reimbursement account"
  - `PlanType` → "Account classification (FSA, HSA, HRA)"
  - `AvailableBalance` → "Current spendable funds"
- [ ] Enrich with external data
  - `PlanType.FSA` → "FSA with $3,200 limit (2025) per IRS [EXTERNAL]"
  - Carryover logic → "Supports $640 max carryover per 26 CFR §125-5 [EXTERNAL]"
- [ ] Add source attribution ([CODE] vs [EXTERNAL])

**Expected Output:** (See template below)

### Task 4: Validate & Score (5 mins)
- [ ] Manual review: Business description accuracy
- [ ] Check: Clear [CODE] vs [EXTERNAL] attribution
- [ ] Score: 0-100% accuracy
- [ ] Identify: What worked, what needs improvement

---

## 📊 Expected POC Output Template

```markdown
# ReimbursementAccount Entity - Business Documentation

**Generated:** December 11, 2025 (Language Processor POC)  
**Source Code:** `Libs/Hqy.Member.Domain/Entities/ReimbursementAccount.cs`

---

## Business Purpose

Manages healthcare reimbursement accounts (FSA, HSA, HRA) with IRS-compliant balance tracking and transaction processing. [CODE + EXTERNAL]

---

## Entity Overview

**Domain:** Healthcare Benefits Administration  
**Pattern:** Domain-Driven Design (Aggregate Root) [CODE]  
**Regulatory Context:** IRS-regulated accounts per Publication 969 [EXTERNAL: IRS.gov]

---

## Key Properties

### Account Identification
- **ReimbursementAccountId** (Guid) - Unique account identifier [CODE]
- **PlanType** (enum: FSA, HSA, HRA, DependentCare) - Account classification per IRS §223 (HSA) and §125 (FSA) [EXTERNAL: IRS.gov]

### Plan Year Configuration
- **PlanYearStartDate** (DateTime) - Plan year start, typically January 1 per employer election [CODE]
- **PlanYearEndDate** (DateTime) - Plan year end, typically December 31 [CODE]
- **Regulatory Note:** Plan years must align with IRS calendar or fiscal year rules per 26 CFR §125-4 [EXTERNAL: IRS.gov]

### Balance Management
- **AvailableBalance** (decimal) - Current spendable funds after claims and contributions [CODE]
- **Calculation:** Opening balance + contributions - claims - fees [CODE pattern detected]

### Relationships
- **TransferLines** (ICollection<TransferLine>) - All financial transactions (contributions, claims, adjustments) [CODE]
- **ScheduledItems** (ICollection<ScheduledItem>) - Scheduled payments and autopay claims [CODE]
- **Member** (Member) - Account owner relationship [CODE]

---

## Regulatory Compliance

### FSA (Flexible Spending Account)
- **Contribution Limit (2025):** $3,200 per IRS Rev. Proc. 2024-40 [EXTERNAL: IRS.gov, cached Dec 2024]
- **Carryover Limit (2025):** $640 maximum to next plan year per 26 CFR §125-5(c) [EXTERNAL: IRS.gov]
- **Use-It-Or-Lose-It Rule:** Funds over $640 forfeited at year-end unless employer offers grace period [EXTERNAL: IRS §125]
- **Grace Period Option:** Employers may allow 2.5 month extension per 26 CFR §125-1(e) [EXTERNAL: IRS.gov]

### HSA (Health Savings Account)
- **Contribution Limit (2025):** $4,150 (individual) / $8,300 (family) per IRS Rev. Proc. 2024-40 [EXTERNAL: IRS.gov]
- **Rollover:** 100% of unused funds roll over annually (no use-it-or-lose-it) per IRC §223(d)(1) [EXTERNAL: IRS.gov]
- **Eligibility:** Requires High-Deductible Health Plan (HDHP) per IRC §223(c)(1) [EXTERNAL: IRS.gov]

### HRA (Health Reimbursement Arrangement)
- **Funding:** Employer-funded only per IRS Notice 2002-45 [EXTERNAL: IRS.gov]
- **Portability:** Generally non-portable (tied to employment) [EXTERNAL: Industry standard]

---

## Business Rules Detected in Code

### Balance Calculations
1. **Available Balance Formula:** [CODE]
   ```
   AvailableBalance = SUM(Contributions) - SUM(Claims) - SUM(Fees) - SUM(Adjustments)
   ```
2. **Pending Claims Impact:** Scheduled autopay claims reduce available balance [CODE]

### Year-End Processing
1. **Forfeiture Logic:** Unused FSA funds over $640 forfeited at `PlanYearEndDate` [CODE matches IRS §125-5(c) ✅]
2. **Carryover Processing:** Implemented in `CarryoverDollarsDomainService.CalculateForefeitAndCarryoverBalanceEOFY` [CODE]
3. **Batch Processing:** Processes 1,000 accounts concurrently (10 parallel operations) [CODE]

### Compliance Validation
- ✅ **Contribution Limits:** Code does NOT validate IRS limits (gap identified)
- ✅ **Carryover Maximum:** Code enforces $640 limit [CODE matches IRS regulation]
- ⚠️  **Grace Period:** Code supports grace periods but implementation not verified [CODE partial]

---

## Code Implementation Details

### Entity Framework Configuration
- **File:** `ReimbursementAccount.Configuration.cs` [CODE]
- **Table Mapping:** Database table name, primary key, indexes [CODE]
- **Relationships:** Foreign keys to Member, TransferLine, ScheduledItem [CODE]

### Domain Service Integration
- **CarryoverDollarsDomainService:** Year-end carryover/forfeiture calculations [CODE]
- **ReimbursementAccountBalanceService:** Balance inquiry and validation [CODE]
- **ScheduledItemService:** Autopay claim scheduling [CODE]

---

## Compliance Gap Analysis

| Requirement | IRS Regulation | Code Implementation | Status |
|-------------|----------------|---------------------|--------|
| FSA Contribution Limit ($3,200) | IRS Rev. Proc. 2024-40 | Not validated in entity | ⚠️ GAP |
| FSA Carryover Limit ($640) | 26 CFR §125-5(c) | Enforced in CarryoverDollars service | ✅ COMPLIANT |
| HSA Contribution Limit ($4,150/$8,300) | IRS Rev. Proc. 2024-40 | Not validated in entity | ⚠️ GAP |
| Year-End Forfeiture | 26 CFR §125-5 | Implemented correctly | ✅ COMPLIANT |
| Grace Period (2.5 months) | 26 CFR §125-1(e) | Supported but not verified | 🔍 REVIEW NEEDED |

---

## Source Breakdown

- **60% CODE:** Entity structure, properties, relationships, domain service references
- **40% EXTERNAL:** IRS regulations, contribution limits, compliance requirements

**External Sources:**
- IRS Publication 969 (Tax Benefits for Health Savings Accounts, 2025 edition)
- 26 CFR §125 (Cafeteria Plans - FSA regulations)
- IRS Revenue Procedure 2024-40 (2025 inflation adjustments)
- IRS Notice 2002-45 (HRA guidance)

**Last External Refresh:** December 11, 2025

---

## Recommended Actions

### P0 (Critical)
1. **Add contribution limit validation** - Enforce IRS limits in entity or domain service
2. **Validate carryover calculations** - Ensure all code paths respect $640 limit

### P1 (High)
3. **Document grace period logic** - Clarify which code handles 2.5 month extension
4. **Add compliance tests** - TDD tests validating IRS regulation adherence

### P2 (Medium)
5. **Update XML comments** - Reference specific IRS regulations in code documentation
6. **Annual limit refresh** - Automate IRS limit updates (2026 inflation adjustments)

---

**Generated by:** CORTEX Language Processor POC v0.1  
**Review Status:** ⏳ Pending manual validation  
**Accuracy Target:** 80%+ (to proceed with full implementation)
```

---

## 🎯 Success Metrics

### Quantitative
- [ ] **Accuracy:** 80%+ of business descriptions factually correct
- [ ] **Attribution:** 100% of external data clearly marked [EXTERNAL]
- [ ] **Coverage:** All properties mapped to business language
- [ ] **Compliance:** 3+ regulatory gaps identified
- [ ] **Time:** POC completed in 40 minutes

### Qualitative
- [ ] **Readability:** Business stakeholders can understand without technical background
- [ ] **Actionability:** Compliance gaps clearly stated with recommended actions
- [ ] **Traceability:** Citations allow verification (e.g., 26 CFR §125-5(c) linkable)
- [ ] **Maintainability:** External data cached, versioned, refreshable

---

## 🚦 Decision Criteria

### ✅ PROCEED with Full Implementation if:
- Accuracy ≥ 80%
- Attribution clear and reliable
- External data scraping stable (IRS.gov accessible, parseable)
- Time investment acceptable (40 mins for 1 entity → 56 entities ≈ 37 hours)
- Compliance gaps valuable (actionable, not obvious)

### 🔴 DEFER if:
- Accuracy < 70%
- Attribution unreliable or confusing
- External scraping fragile (frequent failures)
- Business value unclear (manual review faster)
- CORTEX team capacity constrained

---

## 📊 POC Deliverables

1. **ReimbursementAccount Business Documentation** (above template filled out)
2. **POC Evaluation Report:**
   - Accuracy score (0-100%)
   - What worked well
   - What failed or needs improvement
   - Estimated effort for full implementation (56 entities)
   - Recommendation: PROCEED or DEFER
3. **Updated AST Enhancement Tracker** (add Language Processor findings)
4. **Input to Batch 19** (CORTEX Enhancement with POC results)

---

## 🔄 Integration with Other Batches

**Inputs from Previous Batches:**
- Batch 1: AST analysis of 256 C# files (tree-sitter working)
- Batch 2: Business domain map (plan types, workflows)
- Batch 2.5: External intelligence (IRS regulations cached)
- Batch 3: Entity catalog (all 56 entities listed)

**Outputs to Future Work:**
- Batch 19: CORTEX Enhancement recommendations
- Full Implementation: Language Processor orchestrator (if POC succeeds)
- Dashboard: Compliance gap visualization
- TDD: Test intelligence matrix (regulations → test cases)

---

**Status:** Ready for execution after Batch 17 complete  
**Next Batch:** 19 (CORTEX Self-Enhancement with POC results)
