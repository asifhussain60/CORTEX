# Clean Architecture Layer Definitions

**Version:** 1.0  
**Author:** Asif Hussain  
**Date:** December 15, 2025  
**Status:** ✅ PRODUCTION STANDARD  
**Source:** Platform.Classic Vision API Documentation

---

## 🏗️ Architecture Overview

Clean Architecture enforces strict dependency rules through physical project separation. The compiler enforces boundaries, preventing violations at build time.

**Dependency Flow:**
```
Presentation Layer → Use Case Layer → Domain Layer
                  ↘               ↗
                   External Infrastructure Layer
                                 ↗
                   Internal Infrastructure Layer → Domain Layer
```

---

## 📦 Layer Definitions

### 1. Domain Layer (*.DomainCore)

**Purpose:** Core business logic and entities - the heart of the application

**Dependency Rule:** ❌ MUST NOT depend on ANY other layer  
**Implementation:** Separate project (e.g., `RA.DomainCore`)

#### Defines:

**Aggregates**
- Root entities that encapsulate related entities and value objects
- Enforce consistency boundaries
- Control all access to child entities

**Commands**
- Represent user intentions/actions
- Immutable data structures
- Used by use cases to perform operations

**Derived Values**
- Calculated properties from entity state
- Business rules for computation
- Read-only values

**Domain Events**
- Represent something that happened in the domain
- Trigger side effects in other parts of the system
- Immutable event data

**Domain Exceptions**
- Business rule violations
- Domain-specific error conditions
- Rich error information for business stakeholders

**Entities**
- Objects with unique identity
- Mutable state with invariants
- Business behavior encapsulation

**Enums**
- Domain-specific enumerations
- Type-safe constants
- Business concept representations

**Port Interfaces for Internal Infrastructure**
- Abstractions for owned dependencies
- Repository contracts
- Data access interfaces

**Repository Interfaces**
- Data access contracts defined by domain needs
- Persistence-agnostic
- Domain-centric query methods

**Specifications**
- Reusable business rules
- Query criteria encapsulation
- Composable logic

**Validators**
- Business rule validation
- Entity invariant checking
- Cross-entity validation rules

**Value Objects**
- Immutable objects without identity
- Defined by their attributes
- Encapsulate business concepts (e.g., Money, Address)

---

### 2. Use Case Layer (*.UseCase)

**Purpose:** Application-specific business logic orchestration

**Dependency Rule:** ✅ MAY depend on Domain Layer ONLY  
**Implementation:** Separate project (e.g., `RA.UseCase`)

#### Defines:

**Port Interfaces for External Infrastructure**
- Abstractions for external dependencies
- Third-party service contracts
- External API client interfaces

**Use Cases (Application Services)**
- Orchestrate domain logic for specific application scenarios
- Coordinate multiple domain operations
- Handle cross-cutting concerns (logging, transactions)
- Map between DTOs and domain entities

**Examples:**
- `CreateFundingInvoiceUseCase`
- `GenerateFundingInvoiceUseCase`
- `CloseFundingBatchUseCase`

---

### 3. Internal Infrastructure Layer (*.Data.*)

**Purpose:** Adapters for dependencies the application OWNS

**Dependency Rule:** ✅ MAY depend on Domain Layer ONLY  
**Implementation:** Separate projects per technology (e.g., `RA.Data.SqlServer`, `RA.Data.MongoDB`)

#### Implements:

**Port Interfaces for Internal Infrastructure**
- Concrete implementations of repository interfaces
- Data access technology adapters (EF Core, Dapper, MongoDB driver)

**Repository Interfaces**
- Actual database queries
- ORM configurations
- Data mapping logic

**Examples:**
- `FundingInvoiceRepository : IFundingInvoiceRepository`
- `FundingBatchRepository : IFundingBatchRepository`
- `SqlServerUnitOfWork : IUnitOfWork`

---

### 4. External Infrastructure Layer (*.Client.*)

**Purpose:** Adapters for dependencies the application DOES NOT OWN

**Dependency Rule:** ✅ MAY depend on Use Case Layer AND optionally Domain Layer  
**Implementation:** Separate projects per external system (e.g., `RA.Client.FinanceDomain`, `RA.Client.Paragon`)

#### Implements:

**Port Interfaces for External Infrastructure**
- HTTP clients for external APIs
- Message queue adapters
- Third-party service wrappers

**Examples:**
- `FinanceClient : IFinanceClient`
- `ParagonApiClient : IParagonApiClient`
- `KafkaMessagePublisher : IMessagePublisher`

---

### 5. Presentation Layer (*.Api.Host)

**Purpose:** Application UI/API hosting

**Dependency Rules:**
- **Implementation perspective:** ✅ MAY depend on Domain and Use Case layers ONLY
- **Hosting perspective:** ✅ MAY depend on ALL layers (for dependency injection setup)

**Implementation:** Separate project (e.g., `RA.Api.Host`)

#### Contains:

**Controllers**
- HTTP request/response handling
- Route definitions
- Model binding and validation

**Models (DTOs)**
- Request/Response models
- API contracts
- Data transfer objects

**Middleware**
- Cross-cutting concerns (auth, logging, error handling)
- Request/response pipeline

**Startup/Program**
- Dependency injection configuration
- Application bootstrapping
- References ALL layers for DI setup

---

## 🚫 Prohibited Patterns

### ❌ Domain Layer Violations

```csharp
// BAD: Domain depending on infrastructure
namespace RA.DomainCore.Entities
{
    using Microsoft.EntityFrameworkCore; // ❌ VIOLATION
    
    public class FundingInvoice 
    {
        // Domain should NOT know about EF Core
    }
}
```

### ❌ Use Case Layer Violations

```csharp
// BAD: Use Case depending on infrastructure
namespace RA.UseCase.Fees
{
    using RA.Data.SqlServer; // ❌ VIOLATION
    
    public class GetFeeUseCase
    {
        // Use Case should only depend on abstractions (interfaces)
    }
}
```

### ❌ External Infrastructure Accessing Internal Infrastructure

```csharp
// BAD: External infrastructure using repositories directly
namespace RA.Client.FinanceDomain
{
    using RA.Data.SqlServer; // ❌ VIOLATION
    
    public class FinanceClient
    {
        // External clients should NOT access repositories
    }
}
```

---

## ✅ Correct Patterns

### ✅ Domain Defining Interface

```csharp
// GOOD: Domain defines what it needs
namespace RA.DomainCore.Repositories
{
    public interface IFundingInvoiceRepository
    {
        Task<FundingInvoice> GetByIdAsync(string id);
        Task CreateAsync(FundingInvoice invoice);
    }
}
```

### ✅ Infrastructure Implementing Interface

```csharp
// GOOD: Infrastructure implements domain contract
namespace RA.Data.SqlServer.Repositories
{
    using RA.DomainCore.Repositories;
    
    public class FundingInvoiceRepository : IFundingInvoiceRepository
    {
        private readonly ApplicationDbContext _context;
        
        public async Task<FundingInvoice> GetByIdAsync(string id)
        {
            return await _context.FundingInvoices.FindAsync(id);
        }
    }
}
```

### ✅ Use Case Orchestrating Domain

```csharp
// GOOD: Use Case coordinates domain logic
namespace RA.UseCase.Fees
{
    using RA.DomainCore.Repositories;
    using RA.UseCase.Fees.Ports;
    
    public class CreateFundingInvoiceUseCase
    {
        private readonly IFundingInvoiceRepository _repo;
        private readonly IParagonApiClient _paragonClient; // External dependency
        
        public async Task ExecuteAsync(CreateFundingInvoiceCommand cmd)
        {
            // Orchestrate domain + external services
        }
    }
}
```

---

## 📐 Project Reference Matrix

| Layer | Can Reference |
|-------|---------------|
| **Domain** | NONE |
| **Use Case** | Domain |
| **Internal Infrastructure** | Domain |
| **External Infrastructure** | Use Case, (optional) Domain |
| **Presentation (Code)** | Domain, Use Case |
| **Presentation (DI Setup)** | ALL (for registration) |

---

## 🔍 Compiler-Enforced Boundaries

Projects are used instead of folders to enforce boundaries:

```xml
<!-- RA.DomainCore.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <!-- NO REFERENCES - Domain is independent -->
  </ItemGroup>
</Project>

<!-- RA.UseCase.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <ProjectReference Include="..\RA.DomainCore\RA.DomainCore.csproj" />
  </ItemGroup>
</Project>

<!-- RA.Data.SqlServer.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <ProjectReference Include="..\RA.DomainCore\RA.DomainCore.csproj" />
    <!-- NOT allowed to reference Use Case -->
  </ItemGroup>
</Project>

<!-- RA.Api.Host.csproj -->
<Project Sdk="Microsoft.NET.Sdk.Web">
  <ItemGroup>
    <ProjectReference Include="..\RA.DomainCore\RA.DomainCore.csproj" />
    <ProjectReference Include="..\RA.UseCase\RA.UseCase.csproj" />
    <!-- For DI setup ONLY: -->
    <ProjectReference Include="..\RA.Data.SqlServer\RA.Data.SqlServer.csproj" />
    <ProjectReference Include="..\RA.Client.FinanceDomain\RA.Client.FinanceDomain.csproj" />
  </ItemGroup>
</Project>
```

---

## 📊 Visual Diagrams Reference

**Detailed diagrams available in attached images:**

1. **Layer Dependency Graph** - Shows allowed dependencies between layers
2. **Project Reference Graph** - Concrete project structure with references
3. **Application Dependency Graph** - Multi-application domain isolation
4. **Fee Calculation Example** - Complex cross-layer flow
5. **Cancel Membership Example** - Cross-domain communication pattern

---

## 🎯 Agent Compliance Requirements

When generating specifications and implementations:

1. **Identify Legacy Layer Violations** - Document where legacy code violates boundaries
2. **Map Legacy to Clean Architecture** - Show which legacy classes belong in which layer
3. **Enforce Separation** - Generate separate projects for each layer
4. **Use Interfaces** - All cross-layer dependencies MUST use abstractions
5. **No Shortcuts** - Cannot skip layers (e.g., Controller → Repository directly)

---

## 📚 Related Documentation

- **Vision API Guidelines:** Platform.Classic architecture standards
- **DomainFramework Documentation:** Base entity and aggregate patterns
- **ClassicModernization Library:** Migration helpers and adapters

---

**End of Guidelines**
