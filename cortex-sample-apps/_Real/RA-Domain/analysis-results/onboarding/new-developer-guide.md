# New Developer Onboarding Guide
**Target Time:** 4 hours (down from 13 hours)
**Generated:** December 11, 2025

---

## 🎯 Onboarding Goals

By the end of this guide, you will:
- ✅ Understand the RA domain (FlexAccount, HealthSavings, HealthReimbursement, Rollover)
- ✅ Know the top 20 files to read first
- ✅ Be able to make your first code change
- ✅ Understand the test strategy
- ✅ Know who to ask for help

---

## 📋 5-Step Learning Path

### Step 1: Business Domain (45 min)

**What to Read:**
- `terminology-guide.md` - 80+ business terms (FlexAccount, HealthSavings, rollover, etc.)
- RegulatoryAgency Publication 969 (Health Savings Accounts)
- Internal wiki: "Payment Accounts 101"

**Key Concepts:**
- **FlexAccount (Flexible Spending Account):** Pre-tax healthcare funds, $3,200 annual limit
- **HealthSavings (Health Savings Account):** Tax-advantaged savings, $4,150 individual limit
- **HealthReimbursement (Health Payment Arrangement):** Organization-funded only
- **Rollover:** FlexAccount $640 max, HealthSavings unlimited
- **Qualified Expenses:** RegulatoryAgency Pub 502 list

**Quiz Questions:**
1. What's the difference between FlexAccount and HealthSavings?
2. How much can FlexAccount participants rollover?
3. What's a qualified medical expense?

---

### Step 2: Architecture Overview (60 min)

**What to Read:**
- `key-files-reference.md` - Top 20 files
- `ARCHITECTURE.md` (if exists in repo)
- Domain model diagram

**System Layers:**
```
UI Layer (Web/Mobile)
    ↓
API Layer (REST)
    ↓
Domain Services
    ↓
    ├── CarryoverDollarsDomainService (717 LOC) ⭐
    ├── BalanceCalculationService
    ├── ClaimsProcessingService
    └── PlanManagementService
    ↓
Domain Entities
    ↓
Infrastructure (DB, NServiceBus, EF)
```

**Key Patterns:**
- **Domain-Driven Design (DDD):** Entities, Repositories, Services
- **Message-Driven:** NServiceBus for async processing
- **Entity Framework:** ORM for SQL Server
- **CQRS:** Separate read/write models

---

### Step 3: Deep Dive - Rollover Logic (75 min)

**Why Rollover First?**
- Most complex business logic (717 LOC, 20+ methods)
- Highest regulatory risk ($500k RegulatoryAgency penalties)
- Frequently changes (annual RegulatoryAgency limit updates)

**Files to Read (in order):**
1. `CarryoverDollarsDomainService.cs` (main logic)
2. `CarryoverDollars.cs` (entity)
3. `CarryoverDollarsRepository.cs` (persistence)
4. `CarryoverDollarsTests.cs` (⚠️ NEEDS TESTS - currently 0%)

**Key Methods:**
- `CalculateCarryoverAmount()` - Core logic
- `ValidateIrsLimits()` - Compliance checks
- `ApplyGracePeriodExclusion()` - Mutual exclusion rule

**Debugging Exercise:**
Run `CarryoverCalculationTests.cs` (when implemented) and step through with debugger.

---

### Step 4: Make Your First Change (60 min)

**Starter Task:** Add XML documentation to `CarryoverDollarsDomainService`

**Steps:**
1. Clone repo: `git clone [repo-url]`
2. Create branch: `git checkout -b onboarding/add-xml-docs`
3. Add XML comments to 5 public methods in `CarryoverDollarsDomainService.cs`
4. Run tests: `dotnet test` (currently 8.6% coverage)
5. Create PR and request review from [Team Lead]

**Example XML Comment:**
```csharp
/// <summary>
/// Calculates FlexAccount rollover amount based on RegulatoryAgency limits ($640 max for 2025)
/// </summary>
/// <param name="plan">FlexAccount plan with rollover enabled</param>
/// <param name="remainingBalance">Unused balance from prior year</param>
/// <returns>Rollover amount (capped at RegulatoryAgency limit)</returns>
/// <exception cref="InvalidOperationException">Thrown if plan doesn't allow rollover</exception>
public decimal CalculateCarryoverAmount(Plan plan, decimal remainingBalance)
```

---

### Step 5: Testing & Quality (60 min)

**Current State:** 8.6% test coverage ❌

**Test Strategy:**
- **Unit Tests:** Domain logic (CarryoverService, BalanceCalculation)
- **Integration Tests:** Database, NServiceBus, external APIs
- **E2E Tests:** User workflows (claims submission, balance inquiry)

**Your First Test:**
Write a test for `CalculateCarryoverAmount()`:

```csharp
[Fact]
public void CalculateCarryoverAmount_WhenBalanceExceedsLimit_ReturnsIrsMax()
{
    // Arrange
    var plan = CreateFsaPlanWithCarryover();
    var remainingBalance = 1000m; // Exceeds $640 limit
    
    // Act
    var carryoverAmount = service.CalculateCarryoverAmount(plan, remainingBalance);
    
    // Assert
    Assert.Equal(640m, carryoverAmount); // RegulatoryAgency 2025 limit
}
```

**Run Tests:**
```bash
dotnet test --filter "CarryoverDollars*"
```

---

## 🧑‍💼 Who to Ask

| Topic | Contact | Slack Channel |
|-------|---------|---------------|
| Business logic | [Product Owner] | #ra-product |
| Rollover logic | [Senior Dev - Rollover SME] | #ra-engineering |
| Testing | [QA Lead] | #ra-qa |
| Compliance | [Compliance Manager] | #compliance |
| Deployments | [DevOps Lead] | #devops |

---

## ✅ Onboarding Checklist

- [ ] Read terminology guide (30 min)
- [ ] Review architecture overview (45 min)
- [ ] Deep dive CarryoverDollarsDomainService (60 min)
- [ ] Complete XML documentation task (60 min)
- [ ] Write first unit test (45 min)
- [ ] Attend team standup
- [ ] Schedule 1:1 with tech lead
- [ ] Join Slack channels (#ra-engineering, #ra-product, #ra-qa)

**Completion Time:** ~4 hours  
**Next Steps:** Pick up first ticket from Sprint backlog (tag: "good-first-issue")
