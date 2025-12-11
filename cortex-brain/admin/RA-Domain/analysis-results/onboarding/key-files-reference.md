# Key Files Reference
**Purpose:** Top 20 files every developer should know
**Generated:** December 11, 2025

---

## 🔥 Priority 1: Core Business Logic (Read First)

### 1. CarryoverDollarsDomainService.cs
- **Location:** `Domain/Services/`
- **Size:** 717 LOC
- **Complexity:** HIGH (20+ methods)
- **Why Critical:** IRS compliance, $500k penalty risk
- **Read Time:** 45 min

### 2. BalanceCalculationService.cs
- **Location:** `Domain/Services/`
- **Size:** ~500 LOC
- **Complexity:** MEDIUM
- **Why Critical:** Financial accuracy, customer-facing
- **Read Time:** 30 min

### 3. ClaimsProcessingService.cs
- **Location:** `Domain/Services/`
- **Size:** ~600 LOC
- **Complexity:** HIGH
- **Why Critical:** High volume, customer support impact
- **Read Time:** 40 min

---

## 📦 Priority 2: Domain Entities

### 4. Plan.cs
- **Purpose:** Core domain model (FSA/HSA/HRA)
- **Key Properties:** PlanType, CarryoverEnabled, ContributionLimits
- **Read Time:** 20 min

### 5. Participant.cs
- **Purpose:** User account model
- **Key Relations:** Plans, Balances, Claims
- **Read Time:** 15 min

### 6. CarryoverDollars.cs
- **Purpose:** Carryover entity
- **Key Logic:** IRS limit validation
- **Read Time:** 15 min

### 7. Balance.cs
- **Purpose:** Account balance tracking
- **Key Methods:** Debit, Credit, GetAvailableBalance
- **Read Time:** 10 min

---

## 🔌 Priority 3: Integration Points

### 8. NServiceBusConfiguration.cs
- **Purpose:** Message bus setup
- **Why Critical:** Async processing, event-driven architecture
- **Read Time:** 20 min

### 9. ApiController.cs (example)
- **Purpose:** REST API endpoints
- **Why Critical:** External integrations
- **Read Time:** 15 min

### 10. DatabaseContext.cs
- **Purpose:** Entity Framework configuration
- **Why Critical:** Database schema understanding
- **Read Time:** 15 min

---

## 🧪 Priority 4: Testing (Currently Minimal)

### 11. CarryoverDollarsTests.cs
- **Status:** ⚠️ NEEDS IMPLEMENTATION (0% coverage)
- **Why Critical:** P0 regulatory testing
- **Read Time:** 10 min (currently empty/minimal)

### 12. BalanceCalculationTests.cs
- **Status:** ⚠️ PARTIAL (low coverage)
- **Read Time:** 15 min

---

## 🛡️ Priority 5: Compliance & Validation

### 13. IrsLimitsValidator.cs
- **Purpose:** IRS contribution/carryover limits
- **Annual Updates:** YES (update every January)
- **Read Time:** 10 min

### 14. QualifiedExpenseValidator.cs
- **Purpose:** IRS Pub 502 expense validation
- **Read Time:** 15 min

### 15. HipaaAuditLogger.cs
- **Purpose:** PHI access logging
- **Compliance:** HIPAA §164.312
- **Read Time:** 10 min

---

## 📊 Priority 6: Reporting & Analytics

### 16. ReportingService.cs
- **Purpose:** Generate compliance/utilization reports
- **Read Time:** 20 min

### 17. TaxFormGenerator.cs
- **Purpose:** Year-end 1099-SA generation
- **Read Time:** 15 min

---

## 🔧 Priority 7: Infrastructure

### 18. Startup.cs / Program.cs
- **Purpose:** App initialization
- **Read Time:** 10 min

### 19. appsettings.json
- **Purpose:** Configuration (DB, NServiceBus, IRS limits)
- **Read Time:** 5 min

### 20. README.md
- **Status:** ⚠️ MISSING - needs creation
- **Read Time:** N/A

---

## 📖 Reading Order Recommendation

**Day 1 (4 hours):**
1. Terminology guide (30 min)
2. Plan.cs, Participant.cs, Balance.cs (45 min)
3. CarryoverDollarsDomainService.cs (45 min)
4. BalanceCalculationService.cs (30 min)
5. IrsLimitsValidator.cs (10 min)
6. CarryoverDollars.cs (15 min)
7. First coding task: Add XML docs (60 min)

**Day 2-3 (6 hours):**
- ClaimsProcessingService.cs
- NServiceBusConfiguration.cs
- ApiController.cs examples
- Testing strategy review
- Write first unit test

**Week 2:**
- Remaining files as needed for assigned tickets
