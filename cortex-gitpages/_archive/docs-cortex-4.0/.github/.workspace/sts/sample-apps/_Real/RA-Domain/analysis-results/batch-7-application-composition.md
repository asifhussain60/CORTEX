# Batch 7: Application Composition Analysis

**Date:** December 11, 2025  
**Status:** ✅ COMPLETE  
**Projects:** 12 total (5 Apps, 2 Libs, 1 SDK, 4 Tests)

---

## Project Inventory

### Applications (5 projects in `Apps/`)

1. **App.RolloverTransferTracking.Endpoint** ⭐ **PRIMARY INVESTIGATION TARGET**
   - Type: NServiceBus Endpoint
   - Purpose: Processes rollover transfer tracking messages
   - Key Components: Handles RolloverTransferTracking entity updates
   - Business Significance: Real-time rollover fund transfer processing

2. **App.PaymentAccounts.ApplicationServices**
   - Type: Application Services Layer
   - Purpose: Orchestrates business workflows
   - Key Components: Service layer between UI and domain

3. **App.PaymentAccounts.Rollover.Jobs** 🎯 **CARRYOVER BATCH PROCESSING**
   - Type: Batch Job Application
   - Purpose: Year-end rollover processing (scheduled jobs)
   - Key Components: Batch processes for FlexAccount/HealthSavings/HealthReimbursement rollover calculations
   - Expected: $640 FlexAccount limit enforcement, grace period logic, expiration calculations

4. **App.PaymentAccounts.FlexPlan.Jobs**
   - Type: Batch Job Application
   - Purpose: Flex plan processing (registration, eligibility spans)
   - Key Components: Customer flex span calculations

5. **App.PaymentAccounts.PercentPlanLedger.Jobs**
   - Type: Batch Job Application
   - Purpose: Percentage-based plan ledger processing
   - Key Components: Ledger calculations for percent plans

---

### Libraries (2 projects in `Libs/`)

1. **App.Organization.Domain**
   - Type: Domain Layer
   - Purpose: Organization-side bounded context
   - Entities: Organization, Customer, PaymentAccount, PaymentPlan, Lookup (5 entities)
   - Business Significance: Organization-facing operations

2. **App.Customer.Domain** ⭐ **CORE DOMAIN**
   - Type: Domain Layer
   - Purpose: Customer-side bounded context
   - Entities: 25 entities (including RolloverTransferTracking, RolloverSettings, GlobalContributionMaxByYear)
   - Services: 11 domain services (CarryoverDollarsDomainService, RolloverSettingsService, etc.)
   - Business Significance: Customer-facing operations, all rollover logic

---

### SDKs/Contracts (1 project in `SDKs/`)

1. **App.PaymentAccounts.Contracts**
   - Type: Contract Library
   - Purpose: Shared DTOs and interfaces
   - DTOs: 44 DTOs (all in `App.PaymentAccounts.Contracts.DTOs` namespace)
   - Business Significance: API contracts, message contracts for NServiceBus

---

### Tests (4 projects in `Tests/`)

1. **App.Organization.Domain.Tests**
   - Type: Unit Tests
   - Purpose: Test Organization.Domain layer

2. **App.Customer.Domain.Tests**
   - Type: Unit Tests
   - Purpose: Test Customer.Domain layer (rollover logic tests here!)

3. **App.PaymentAccounts.Domain.IntegrationTests**
   - Type: Integration Tests
   - Purpose: Cross-domain integration testing

4. **App.PaymentAccounts.FlexPlan.IntegrationTests**
   - Type: Integration Tests
   - Purpose: Flex plan integration testing

---

## Architecture Patterns

### Bounded Contexts (DDD)
- **Organization Context:** `App.Organization.Domain` (organization-side operations)
- **Customer Context:** `App.Customer.Domain` (customer-side operations, rollover logic)

**Why 2 Contexts?**
- Organization-side: Plan configuration, registration management
- Customer-side: Account balances, transactions, rollover transfers, claims

### NServiceBus Architecture
- **Endpoint:** App.RolloverTransferTracking.Endpoint (message handlers)
- **Jobs:** 3 batch processing applications (Rollover, FlexPlan, PercentPlanLedger)
- **Message Contracts:** DTOs in App.PaymentAccounts.Contracts

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

## Rollover Logic Architecture Map

### Core Components (Rollover)

**Domain Layer (App.Customer.Domain):**
- Entities:
  - `RolloverTransferTracking` (transfer tracking)
  - `RolloverSettings` (rollover configuration)
  - `GlobalContributionMaxByYear` (RegulatoryAgency limits)
  - `TransferLine` (transfer line items)

- Services:
  - `CarryoverDollarsDomainService` (rollover business logic)
  - `RolloverSettingsService` (configuration management)
  - `CarryoverSharedService` (shared utilities)

- Interfaces:
  - `ICarryoverDollarsDomainService`
  - `IRolloverSettingsService`
  - `ICarryoverSharedService`

**Contracts Layer (App.PaymentAccounts.Contracts):**
- DTOs:
  - `ProcessCarryOverRequest`
  - `ProcessCarryOverRequestForEmployer`
  - `CarryOverJobResponse`
  - `CarryoverTransferTrackingDto`
  - `ReimbursementAccountCarryoverDto`
  - `RolloverSettingsDto`
  - `UpdateCarryoverandForfeitedBalancesResponse`

**Application Layer:**
- NServiceBus Endpoint: `App.RolloverTransferTracking.Endpoint` (real-time processing)
- Batch Job: `App.PaymentAccounts.Rollover.Jobs` (year-end batch processing)

**Test Layer:**
- `App.Customer.Domain.Tests` (rollover logic unit tests)

---

## Dependency Flow (Rollover Use Case)

**Year-End Rollover Scenario:**
```
1. Rollover.Jobs (scheduled)
   → Loads GlobalContributionMaxByYear (RegulatoryAgency limits)
   → Loads RolloverSettings (FlexAccount $640 max, grace period config)
   → Calls CarryoverDollarsDomainService.ProcessCarryover()
   → Validates rollover amount ≤ $640 (FlexAccount)
   → Creates RolloverTransferTracking records
   → Creates TransferLine items
   → Publishes CarryOverJobResponse
   
2. RolloverTransferTracking.Endpoint (receives message)
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
- **Endpoints:** 1 (RolloverTransferTracking.Endpoint)
- **Jobs:** 3 (Rollover, FlexPlan, PercentPlanLedger)

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
├── App.RolloverTransferTracking.Endpoint
│   ├── → App.Customer.Domain
│   └── → App.PaymentAccounts.Contracts
├── App.PaymentAccounts.ApplicationServices
│   ├── → App.Customer.Domain
│   ├── → App.Organization.Domain
│   └── → App.PaymentAccounts.Contracts
├── App.PaymentAccounts.Rollover.Jobs
│   ├── → App.Customer.Domain (CarryoverDollarsDomainService)
│   └── → App.PaymentAccounts.Contracts
├── App.PaymentAccounts.FlexPlan.Jobs
│   ├── → App.Customer.Domain
│   └── → App.PaymentAccounts.Contracts
└── App.PaymentAccounts.PercentPlanLedger.Jobs
    ├── → App.Customer.Domain
    └── → App.PaymentAccounts.Contracts

Libs (2)
├── App.Customer.Domain (25 entities, 11 services)
└── App.Organization.Domain (5 entities)

SDKs (1)
└── App.PaymentAccounts.Contracts (44 DTOs, 16 interfaces)

Tests (4)
├── App.Customer.Domain.Tests → App.Customer.Domain
├── App.Organization.Domain.Tests → App.Organization.Domain
├── App.PaymentAccounts.Domain.IntegrationTests → Both domains
└── App.PaymentAccounts.FlexPlan.IntegrationTests → App.Customer.Domain
```

---

## Critical Validation Points (From Batch 2.5)

### P0: RegulatoryAgency Contribution Limit Enforcement
**Component:** `App.Customer.Domain` → `GlobalContributionMaxByYear` entity
**Validation Required:**
- Does `Rollover.Jobs` load GlobalContributionMaxByYear?
- Does `CarryoverDollarsDomainService` enforce FlexAccount $3,200 / HealthSavings $4,150-$8,300 limits?
- Are limits validated BEFORE rollover calculations?

### P0: FlexAccount $640 Rollover Limit
**Component:** `App.Customer.Domain` → `RolloverSettings` entity
**Validation Required:**
- Does `RolloverSettingsService` load $640 FlexAccount limit?
- Does `CarryoverDollarsDomainService.ProcessCarryover()` validate rollover ≤ $640?
- Is expiration calculated for amounts > $640?

### P0: Grace Period Mutual Exclusion
**Component:** `RolloverSettings` entity
**Validation Required:**
- Can both rollover AND grace period be enabled? (RegulatoryAgency violation if yes)
- Is mutual exclusion enforced at configuration level or runtime?

---

## Next Steps (Batch 8+)

### Batch 8: Use Case Extraction
- Extract NServiceBus handlers from RolloverTransferTracking.Endpoint
- Map message flows for rollover processing
- Document end-to-end rollover workflow

### Batch 9-10: Data Flow & Test Coverage
- Analyze data flow through rollover components
- Review existing test coverage for rollover logic
- Identify missing tests (P0 gaps)

### Critical Deep Dive (Post-Batch 10)
- **Analyze CarryoverDollarsDomainService methods**
- **Validate GlobalContributionMaxByYear usage**
- **Validate RolloverSettings $640 enforcement**
- **Generate P0 compliance report**

---

**Status:** ✅ **BATCH 7 COMPLETE** | **Next:** Batch 8 (Use Case Extraction from NServiceBus handlers)
