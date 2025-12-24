# Architecture Diagrams and Patterns

**Version:** 1.0  
**Author:** Asif Hussain  
**Date:** December 15, 2025  
**Status:** ✅ REFERENCE MATERIAL  
**Source:** Platform.Classic Vision API Documentation

---

## 📊 Diagram Catalog

This document catalogs all architecture diagrams extracted from Vision API documentation for agent reference.

---

## 1. Layer Dependency Graph

**Purpose:** Shows allowed dependencies between Clean Architecture layers

**Key Insights:**
- Domain Layer has ZERO dependencies
- Use Case depends on Domain only
- Infrastructure layers implement ports defined in Domain/Use Case
- External Dependencies isolated from Domain

**Diagram Location:** `cortex-brain/documents/guidelines/architecture/diagrams/layer-dependency-graph.png`

**ASCII Representation:**
```
┌─────────────────────┐
│ Presentation Layer  │
└──────────┬──────────┘
           │
           ├───────────────────────┐
           │                       │
           ▼                       ▼
┌─────────────────────┐   ┌──────────────────────────┐
│ External            │   │ Owned Infrastructure     │
│ Infrastructure      │   │ Layer                    │
│ Layer               │   │                          │
└──────────┬──────────┘   └──────────┬───────────────┘
           │                         │
           │                         │
           ▼                         ▼
┌─────────────────────┐   ┌──────────────────────────┐
│ Use Case Layer      │◄──┤ External Dependencies    │
└──────────┬──────────┘   └──────────────────────────┘
           │
           ▼
┌─────────────────────┐   ┌──────────────────────────┐
│ Domain Layer        │◄──┤ Owned Dependencies       │
└─────────────────────┘   └──────────────────────────┘
```

---

## 2. Project Reference Graph

**Purpose:** Concrete project structure showing actual .csproj references

**Key Insights:**
- `*.Api.Host` references ALL projects (for DI setup only)
- Dotted lines indicate "reference but don't use" (hosting concern)
- `*.UseCase` is central orchestration point
- `*.DomainCore` has no outgoing references

**Diagram Location:** `cortex-brain/documents/guidelines/architecture/diagrams/project-reference-graph.png`

**Projects:**
- **Presentation:** `*.Api.Host`
- **External Infrastructure:** `*.Client.OtherDomain`, `*.Messaging.Kafka`
- **External Dependencies:** Kafka, Other Domain API (hexagons)
- **Use Case:** `*.UseCase`
- **Owned Infrastructure:** `*.Data.MongoDB`, `*.Data.SqlServer`
- **Owned Dependencies:** Sql Server, MongoDB (cylinders)
- **Domain:** `*.DomainCore`

---

## 3. Application Dependency Graph

**Purpose:** Shows how multiple applications in same domain must isolate layers

**Key Insights:**
- Domain Job and Domain Endpoint are separate applications
- Each application has own data store (no sharing)
- Both can call shared Domain API (cross-application communication)
- Prevents tight coupling between applications

**Diagram Location:** `cortex-brain/documents/guidelines/architecture/diagrams/application-dependency-graph.png`

**Pattern:**
```
┌────────────────────────────────────────────┐
│              Domain                        │
│                                            │
│  ┌─────────────┐       ┌─────────────┐   │
│  │ Domain Job  │──────►│ Domain API  │   │
│  └──────┬──────┘       └──────┬──────┘   │
│         │                     │           │
│         ▼                     ▼           │
│  ┌─────────────┐       ┌─────────────┐   │
│  │ Sql Server  │       │ MongoDB     │   │
│  └─────────────┘       └─────────────┘   │
│         ▲                     ▲           │
│         │                     │           │
│  ┌──────┴──────┐       ┌──────┴──────┐   │
│  │Domain       │       │Domain       │   │
│  │Endpoint     │──────►│API          │   │
│  └─────────────┘       └─────────────┘   │
└────────────────────────────────────────────┘
```

**Rule:** Each application owns its data store; cross-app communication via API only.

---

## 4. Fee Calculation Example (Complex Logic)

**Purpose:** Demonstrates handling complex data retrieval across repositories

**Scenario:** Reimbursement Account Fees calculated from settings on reimbursement account plan and associated fee schedule (doesn't fit standard repository pattern)

**Components:**
- `FeesController` (Presentation)
- `IGetFeeUseCase` (Use Case interface)
- `GetFeeUseCase` (Use Case implementation)
- `FeeScheduleRepository` (Internal Infrastructure)
- `ReimbursementAccountPlanRepository` (Internal Infrastructure)

**Diagram Location:** `cortex-brain/documents/guidelines/architecture/diagrams/fee-calculation-example.png`

**Dependency Flow:**
```
FeesController (Presentation)
    │
    │ Uses
    ▼
IGetFeeUseCase (Use Case - Interface)
    ▲
    │ Implements
    │
GetFeeUseCase (Use Case - Implementation)
    │
    ├──► ReimbursementAccountPlanRepository (Infrastructure)
    │        │
    │        │ Implements
    │        ▼
    │    IReimbursementAccountPlanRepository (Domain)
    │
    └──► FeeScheduleRepository (Infrastructure)
             │
             │ Implements
             ▼
         IFeeScheduleRepository (Domain)
```

**Sequence:**
1. Consumer calls `GET /reimbursement-account/{id}/fee/{fee_type}`
2. FeesController calls `GetFeeUseCase.GetFee(raId, feeType)`
3. Use Case calls `GetReimbursementAccountPlan(raId)` → returns raPlan
4. Use Case calls `GetFeeSchedule(raId)` → returns feeSchedule
5. Use Case executes `CalculateFee(raPlan, feeSchedule)` → returns Fee
6. Controller returns FeeResponse to consumer

**Key Pattern:** Use Case orchestrates multiple repositories and domain logic.

---

## 5. Cancel Membership Example (Cross-Domain Communication)

**Purpose:** Shows how to call other domains while maintaining boundaries

**Scenario:** Members can cancel membership only if they have no outstanding balances (requires Finance domain validation)

**Components:**
- `MembersController` (Presentation)
- `ICancelMembershipUseCase` (Use Case interface)
- `CancelMembershipUseCase` (Use Case implementation)
- `IFinanceClient` (External Infrastructure interface)
- `FinanceClient` (External Infrastructure implementation)
- `MemberRepository` (Internal Infrastructure)

**Diagram Location:** `cortex-brain/documents/guidelines/architecture/diagrams/cancel-membership-example.png`

**Dependency Flow:**
```
MembersController (Presentation)
    │
    │ Uses
    ▼
ICancelMembershipUseCase (Use Case - Interface)
    ▲
    │ Implements
    │
CancelMembershipUseCase (Use Case - Implementation)
    │
    ├──► IFinanceClient (Use Case - External Port Interface)
    │        ▲
    │        │ Implements
    │        │
    │    FinanceClient (External Infrastructure)
    │
    └──► MemberRepository (Internal Infrastructure)
             │
             │ Implements
             ▼
         IMemberRepository (Domain)
```

**Sequence:**
1. Consumer calls `PUT /members/{id} {State -> Cancelled}`
2. MembersController calls `CancelMembershipUseCase.CancelMembership(id)`
3. Use Case calls `FinanceClient.GetMember(id)` → returns member
4. Use Case calls `FinanceClient.Get /balances?memberId={id}` → returns balances
5. Use Case validates `balances.Any()` → throws if balances exist
6. Use Case calls `MemberRepository.UpdateMember(member)` → persists cancellation
7. Controller returns UpdateMemberResponse

**Key Pattern:** External domain accessed via client adapter (port interface in Use Case layer).

---

## 🎯 Pattern Summary for Agents

### When to Use What

| Scenario | Pattern | Layers Involved |
|----------|---------|-----------------|
| **Simple CRUD** | Repository Pattern | Controller → Use Case → Repository |
| **Complex Business Logic** | Use Case Orchestration | Controller → Use Case → Multiple Repositories + Domain |
| **Cross-Domain Validation** | External Client Adapter | Controller → Use Case → External Client + Repository |
| **Multi-Step Workflow** | Use Case Coordination | Controller → Use Case → Repositories + Clients + Domain Events |

### Prohibited Shortcuts

| ❌ Anti-Pattern | ✅ Correct Pattern |
|----------------|-------------------|
| Controller → Repository | Controller → Use Case → Repository |
| Use Case → Concrete Infrastructure | Use Case → Interface (implemented by Infrastructure) |
| Domain → External Service | Use Case → External Client (implements port interface) |
| External Infrastructure → Internal Infrastructure | External Infrastructure → Use Case → Domain (never cross infrastructure) |

---

## 📁 File Organization for Diagrams

```
cortex-brain/documents/guidelines/architecture/
├── clean-architecture-layer-definitions.md (this file's sibling)
├── architecture-diagrams-and-patterns.md (current file)
└── diagrams/
    ├── layer-dependency-graph.png
    ├── project-reference-graph.png
    ├── application-dependency-graph.png
    ├── fee-calculation-example.png
    ├── fee-calculation-sequence.png
    ├── cancel-membership-example.png
    └── cancel-membership-sequence.png
```

**Note:** Diagram images extracted from Vision API documentation and stored for agent reference.

---

## 🔄 Integration with Legacy API Specification Plan

These patterns MUST be incorporated into:

1. **Phase 1 (Reverse Engineering):** Identify which legacy classes belong in which layer
2. **Phase 2 (Technical Design):** Map legacy to Clean Architecture with proper project separation
3. **Phase 3 (Implementation):** Generate code in correct layers with proper dependencies

**Agent Prompt Enhancement:**
- Reference this document when designing modern architecture
- Validate all project references against Project Reference Matrix
- Use sequence diagram patterns for complex workflows
- Enforce compiler boundaries (reject designs that violate project references)

---

**End of Diagram Catalog**
