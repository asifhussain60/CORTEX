# Batch 7: Application Composition Analysis

**Date:** December 11, 2025  
**Status:** ✅ COMPLETE  
**Projects:** 12 total (5 Apps, 2 Libs, 1 SDK, 4 Tests)

---

## Project Inventory

### Applications (5 projects in `Apps/`)

1. **Hqy.CarryoverTransferTracking.Endpoint** ⭐ **PRIMARY INVESTIGATION TARGET**
   - Type: NServiceBus Endpoint
   - Purpose: Processes carryover transfer tracking messages
   - Key Components: Handles CarryoverTransferTracking entity updates
   - Business Significance: Real-time carryover fund transfer processing

2. **Hqy.ReimbursementAccounts.ApplicationServices**
   - Type: Application Services Layer
   - Purpose: Orchestrates business workflows
   - Key Components: Service layer between UI and domain

3. **Hqy.ReimbursementAccounts.CarryOver.Jobs** 🎯 **CARRYOVER BATCH PROCESSING**
   - Type: Batch Job Application
   - Purpose: Year-end carryover processing (scheduled jobs)
   - Key Components: Batch processes for FSA/HSA/HRA carryover calculations
   - Expected: $640 FSA limit enforcement, grace period logic, forfeiture calculations

4. **Hqy.ReimbursementAccounts.FlexPlan.Jobs**
   - Type: Batch Job Application
   - Purpose: Flex plan processing (enrollment, eligibility spans)
   - Key Components: Member flex span calculations

5. **Hqy.ReimbursementAccounts.PercentPlanLedger.Jobs**
   - Type: Batch Job Application
   - Purpose: Percentage-based plan ledger processing
   - Key Components: Ledger calculations for percent plans

---

### Libraries (2 projects in `Libs/`)

1. **Hqy.Employer.Domain**
   - Type: Domain Layer
   - Purpose: Employer-side bounded context
   - Entities: Employer, Member, ReimbursementAccount, ReimbursementPlan, Lookup (5 entities)
   - Business Significance: Employer-facing operations

2. **Hqy.Member.Domain** ⭐ **CORE DOMAIN**
   - Type: Domain Layer
   - Purpose: Member-side bounded context
   - Entities: 25 entities (including CarryoverTransferTracking, RolloverSettings, GlobalContributionMaxByYear)
   - Services: 11 domain services (CarryoverDollarsDomainService, RolloverSettingsService, etc.)
   - Business Significance: Member-facing operations, all carryover logic

---

### SDKs/Contracts (1 project in `SDKs/`)

1. **Hqy.ReimbursementAccounts.Contracts**
   - Type: Contract Library
   - Purpose: Shared DTOs and interfaces
   - DTOs: 44 DTOs (all in `Hqy.ReimbursementAccounts.Contracts.DTOs` namespace)
   - Business Significance: API contracts, message contracts for NServiceBus

---

### Tests (4 projects in `Tests/`)

1. **Hqy.Employer.Domain.Tests**
   - Type: Unit Tests
   - Purpose: Test Employer.Domain layer

2. **Hqy.Member.Domain.Tests**
   - Type: Unit Tests
   - Purpose: Test Member.Domain layer (carryover logic tests here!)

3. **Hqy.ReimbursementAccounts.Domain.IntegrationTests**
   - Type: Integration Tests
   - Purpose: Cross-domain integration testing

4. **Hqy.ReimbursementAccounts.FlexPlan.IntegrationTests**
   - Type: Integration Tests
   - Purpose: Flex plan integration testing

---

## Architecture Patterns

### Bounded Contexts (DDD)
- **Employer Context:** `Hqy.Employer.Domain` (employer-side operations)
- **Member Context:** `Hqy.Member.Domain` (member-side operations, carryover logic)

**Why 2 Contexts?**
- Employer-side: Plan configuration, enrollment management
- Member-side: Account balances, transactions, carryover transfers, claims

### NServiceBus Architecture
- **Endpoint:** Hqy.CarryoverTransferTracking.Endpoint (message handlers)
- **Jobs:** 3 batch processing applications (CarryOver, FlexPlan, PercentPlanLedger)
- **Message Contracts:** DTOs in Hqy.ReimbursementAccounts.Contracts

### Layered Architecture
```
Apps (NServiceBus Endpoints + Jobs)
  ↓ uses
SDKs (Contracts - DTOs, Interfaces)
  ↓ implements
Libs (Domain - Entities, Services)
  ↓ tested by
Tests (Unit + Integration)
```

---

## Carryover Logic Architecture Map

### Core Components (Carryover)

**Domain Layer (Hqy.Member.Domain):**
- Entities:
  - `CarryoverTransferTracking` (transfer tracking)
  - `RolloverSettings` (carryover configuration)
  - `GlobalContributionMaxByYear` (IRS limits)
  - `TransferLine` (transfer line items)

- Services:
  - `CarryoverDollarsDomainService` (carryover business logic)
  - `RolloverSettingsService` (configuration management)
  - `CarryoverSharedService` (shared utilities)

- Interfaces:
  - `ICarryoverDollarsDomainService`
  - `IRolloverSettingsService`
  - `ICarryoverSharedService`

**Contracts Layer (Hqy.ReimbursementAccounts.Contracts):**
- DTOs:
  - `ProcessCarryOverRequest`
  - `ProcessCarryOverRequestForEmployer`
  - `CarryOverJobResponse`
  - `CarryoverTransferTrackingDto`
  - `ReimbursementAccountCarryoverDto`
  - `RolloverSettingsDto`
  - `UpdateCarryoverandForfeitedBalancesResponse`

**Application Layer:**
- NServiceBus Endpoint: `Hqy.CarryoverTransferTracking.Endpoint` (real-time processing)
- Batch Job: `Hqy.ReimbursementAccounts.CarryOver.Jobs` (year-end batch processing)

**Test Layer:**
- `Hqy.Member.Domain.Tests` (carryover logic unit tests)

---

## Dependency Flow (Carryover Use Case)

**Year-End Carryover Scenario:**
```
1. CarryOver.Jobs (scheduled)
   → Loads GlobalContributionMaxByYear (IRS limits)
   → Loads RolloverSettings (FSA $640 max, grace period config)
   → Calls CarryoverDollarsDomainService.ProcessCarryover()
   → Validates carryover amount ≤ $640 (FSA)
   → Creates CarryoverTransferTracking records
   → Creates TransferLine items
   → Publishes CarryOverJobResponse
   
2. CarryoverTransferTracking.Endpoint (receives message)
   → Processes CarryoverTransferTrackingDto
   → Updates account balances
   → Logs BalanceChangeAudit
```

---

## Technology Stack

### .NET Framework
- **Version:** 4.8 (all 12 projects)
- **Language:** C# (256 files)

### Messaging
- **Framework:** NServiceBus
- **Pattern:** Command/Event-driven architecture
- **Endpoints:** 1 (CarryoverTransferTracking.Endpoint)
- **Jobs:** 3 (CarryOver, FlexPlan, PercentPlanLedger)

### Data Access
- **ORM:** Entity Framework (Fluent API configuration pattern)
- **Pattern:** Repository pattern (IReimbursementAccountRepository, etc.)
- **Context:** IReimbursementAccountsContext

### Testing
- **Framework:** Likely MSTest or NUnit
- **Coverage:** 0% reported (from Batch 1 metrics - needs verification)
- **Types:** Unit tests + Integration tests

---

## Project Relationships

### Dependency Graph
```
Apps (5)
├── Hqy.CarryoverTransferTracking.Endpoint
│   ├── → Hqy.Member.Domain
│   └── → Hqy.ReimbursementAccounts.Contracts
├── Hqy.ReimbursementAccounts.ApplicationServices
│   ├── → Hqy.Member.Domain
│   ├── → Hqy.Employer.Domain
│   └── → Hqy.ReimbursementAccounts.Contracts
├── Hqy.ReimbursementAccounts.CarryOver.Jobs
│   ├── → Hqy.Member.Domain (CarryoverDollarsDomainService)
│   └── → Hqy.ReimbursementAccounts.Contracts
├── Hqy.ReimbursementAccounts.FlexPlan.Jobs
│   ├── → Hqy.Member.Domain
│   └── → Hqy.ReimbursementAccounts.Contracts
└── Hqy.ReimbursementAccounts.PercentPlanLedger.Jobs
    ├── → Hqy.Member.Domain
    └── → Hqy.ReimbursementAccounts.Contracts

Libs (2)
├── Hqy.Member.Domain (25 entities, 11 services)
└── Hqy.Employer.Domain (5 entities)

SDKs (1)
└── Hqy.ReimbursementAccounts.Contracts (44 DTOs, 16 interfaces)

Tests (4)
├── Hqy.Member.Domain.Tests → Hqy.Member.Domain
├── Hqy.Employer.Domain.Tests → Hqy.Employer.Domain
├── Hqy.ReimbursementAccounts.Domain.IntegrationTests → Both domains
└── Hqy.ReimbursementAccounts.FlexPlan.IntegrationTests → Hqy.Member.Domain
```

---

## Critical Validation Points (From Batch 2.5)

### P0: IRS Contribution Limit Enforcement
**Component:** `Hqy.Member.Domain` → `GlobalContributionMaxByYear` entity
**Validation Required:**
- Does `CarryOver.Jobs` load GlobalContributionMaxByYear?
- Does `CarryoverDollarsDomainService` enforce FSA $3,200 / HSA $4,150-$8,300 limits?
- Are limits validated BEFORE carryover calculations?

### P0: FSA $640 Carryover Limit
**Component:** `Hqy.Member.Domain` → `RolloverSettings` entity
**Validation Required:**
- Does `RolloverSettingsService` load $640 FSA limit?
- Does `CarryoverDollarsDomainService.ProcessCarryover()` validate carryover ≤ $640?
- Is forfeiture calculated for amounts > $640?

### P0: Grace Period Mutual Exclusion
**Component:** `RolloverSettings` entity
**Validation Required:**
- Can both carryover AND grace period be enabled? (IRS violation if yes)
- Is mutual exclusion enforced at configuration level or runtime?

---

## Next Steps (Batch 8+)

### Batch 8: Use Case Extraction
- Extract NServiceBus handlers from CarryoverTransferTracking.Endpoint
- Map message flows for carryover processing
- Document end-to-end carryover workflow

### Batch 9-10: Data Flow & Test Coverage
- Analyze data flow through carryover components
- Review existing test coverage for carryover logic
- Identify missing tests (P0 gaps)

### Critical Deep Dive (Post-Batch 10)
- **Analyze CarryoverDollarsDomainService methods**
- **Validate GlobalContributionMaxByYear usage**
- **Validate RolloverSettings $640 enforcement**
- **Generate P0 compliance report**

---

**Status:** ✅ **BATCH 7 COMPLETE** | **Next:** Batch 8 (Use Case Extraction from NServiceBus handlers)
