# RA Domain Architectural Standards

**Version:** 1.0  
**Author:** Asif Hussain  
**Date:** December 15, 2025  
**Applies To:** `**/*.ra.*`, `RA/**/*`  
**Purpose:** Domain-specific extensions to Clean Architecture for Reimbursement Account (RA) domain

---

## 🎯 Overview

This document extends the core Clean Architecture guidelines with RA domain-specific patterns, naming conventions, and business rules enforcement.

**Base Guidelines:** See `CORTEX/cortex-brain/documents/guidelines/architecture/clean-architecture-layer-definitions.md`

---

## 📦 RA Project Structure

### Mandatory Project Naming Convention

```
HealthEquity.RA.DomainCore           # Domain layer
HealthEquity.RA.UseCase              # Use Case layer  
HealthEquity.RA.Data.SqlServer       # Internal infrastructure (SQL Server)
HealthEquity.RA.Data.MongoDB         # Internal infrastructure (MongoDB, if needed)
HealthEquity.RA.Client.Finance       # External infrastructure (Finance domain)
HealthEquity.RA.Client.Paragon       # External infrastructure (Paragon API)
HealthEquity.RA.Api.Host             # Presentation layer (REST API)
HealthEquity.RA.Jobs.Host            # Presentation layer (Background jobs)
```

**Rationale:** 
- `HealthEquity` prefix aligns with company namespace
- `RA` identifies domain
- Layer suffix enforces Clean Architecture boundaries
- Technology suffix on infrastructure layers (`.SqlServer`, `.MongoDB`)

---

## 🚫 RA-Specific Boundary Rules

### Prohibited Cross-Domain Entity Exposure

**❌ NEVER expose these entities directly in RA API responses:**

```csharp
// From Employer Domain
- Employer
- EmployerPlan
- EmployerGroup

// From Member Domain  
- Member
- MemberEnrollment
- MemberDemographics

// From Plan Domain
- Plan
- PlanBenefit
- BenefitGroup

// From Payroll Domain
- PayrollSchedule
- PayrollDeduction
```

**✅ ALWAYS use RA-specific wrapper DTOs:**

```csharp
// RA.Api.Host/Models/
public class RAEmployerSummary  
{
    public string EmployerId { get; set; }
    public string EmployerName { get; set; }
    // ONLY fields relevant to RA operations
}

public class RAPlanSummary
{
    public string PlanId { get; set; }
    public string PlanType { get; set; }
    public bool IsLSA { get; set; }
    // ONLY fields relevant to RA funding
}
```

---

## 🏗️ RA Domain Entities

### Core Aggregates

**FundingBatch (Aggregate Root)**
```csharp
namespace HealthEquity.RA.DomainCore.Aggregates
{
    public class FundingBatch : AggregateRoot<string>
    {
        public string BatchId { get; private set; }
        public string Status { get; private set; } // Open, Pending, Closed, Reopened
        public List<FundingInvoice> Invoices { get; private set; }
        
        // Business rules enforced in domain
        public void Close()
        {
            if (Status != "Open" && Status != "Reopened")
                throw new DomainException("Cannot close batch in current state");
                
            Status = "Pending";
            RaiseDomainEvent(new FundingBatchClosedEvent(BatchId));
        }
    }
}
```

**FundingInvoice (Entity within FundingBatch aggregate)**
```csharp
namespace HealthEquity.RA.DomainCore.Entities
{
    public class FundingInvoice : Entity<string>
    {
        public string InvoiceId { get; private set; }
        public string SubaccountId { get; private set; }
        public Money EmployerAmount { get; private set; }
        public Money EmployeeAmount { get; private set; }
        public bool IsExcluded { get; private set; }
        
        public Money TotalAmount => EmployerAmount + EmployeeAmount;
    }
}
```

### Value Objects

**Money (RA uses decimal for financial calculations)**
```csharp
namespace HealthEquity.RA.DomainCore.ValueObjects
{
    public class Money : ValueObject
    {
        public decimal Amount { get; }
        public string Currency { get; }
        
        public Money(decimal amount, string currency = "USD")
        {
            if (amount < 0)
                throw new DomainException("Amount cannot be negative");
            Amount = amount;
            Currency = currency;
        }
        
        public static Money operator +(Money a, Money b)
        {
            if (a.Currency != b.Currency)
                throw new DomainException("Cannot add different currencies");
            return new Money(a.Amount + b.Amount, a.Currency);
        }
    }
}
```

---

## 🔌 Repository Patterns

### RA Repository Interface Conventions

**Location:** `HealthEquity.RA.DomainCore/Repositories/`

```csharp
namespace HealthEquity.RA.DomainCore.Repositories
{
    public interface IFundingInvoiceRepository
    {
        // Query methods return domain entities or value objects
        Task<FundingInvoice?> GetByIdAsync(string invoiceId);
        Task<IEnumerable<FundingInvoice>> GetBySubaccountAsync(string subaccountId);
        Task<IEnumerable<FundingInvoice>> GetPendingInvoicesAsync();
        
        // Command methods
        Task CreateAsync(FundingInvoice invoice);
        Task UpdateAsync(FundingInvoice invoice);
        Task DeleteAsync(string invoiceId); // Soft delete
        
        // Specifications support
        Task<IEnumerable<FundingInvoice>> FindAsync(ISpecification<FundingInvoice> spec);
    }
}
```

**Implementation:** `HealthEquity.RA.Data.SqlServer/Repositories/`

```csharp
namespace HealthEquity.RA.Data.SqlServer.Repositories
{
    public class FundingInvoiceRepository : IFundingInvoiceRepository
    {
        private readonly RADbContext _context;
        
        public async Task<FundingInvoice?> GetByIdAsync(string invoiceId)
        {
            return await _context.FundingInvoices
                .Where(x => !x.IsDeleted)
                .FirstOrDefaultAsync(x => x.InvoiceId == invoiceId);
        }
        
        // EF Core implementation details...
    }
}
```

---

## 🎯 Use Case Patterns

### RA Use Case Conventions

**Location:** `HealthEquity.RA.UseCase/[Feature]/`

**Naming:** `[Verb][Noun]UseCase.cs`

**Examples:**
- `CreateFundingInvoiceUseCase`
- `GenerateFundingInvoiceUseCase`
- `CloseFundingBatchUseCase`

**Structure:**
```csharp
namespace HealthEquity.RA.UseCase.Fees
{
    public class CreateFundingInvoiceUseCase
    {
        private readonly IFundingInvoiceRepository _invoiceRepo;
        private readonly ICashInOutRepository _cashInOutRepo;
        private readonly IParagonApiClient _paragonClient; // External dependency
        private readonly ILogger<CreateFundingInvoiceUseCase> _logger;
        
        public CreateFundingInvoiceUseCase(
            IFundingInvoiceRepository invoiceRepo,
            ICashInOutRepository cashInOutRepo,
            IParagonApiClient paragonClient,
            ILogger<CreateFundingInvoiceUseCase> logger)
        {
            _invoiceRepo = invoiceRepo;
            _cashInOutRepo = cashInOutRepo;
            _paragonClient = paragonClient;
            _logger = logger;
        }
        
        public async Task<CreateFundingInvoiceResult> ExecuteAsync(
            CreateFundingInvoiceCommand command)
        {
            // 1. Validate command (FluentValidation)
            // 2. Load domain entities
            // 3. Execute business logic (delegate to domain)
            // 4. Persist changes
            // 5. Call external services (via adapters)
            // 6. Return result DTO
        }
    }
}
```

---

## 🌐 External Client Patterns

### Cross-Domain Communication

**Port Interface Location:** `HealthEquity.RA.UseCase/Ports/`

```csharp
namespace HealthEquity.RA.UseCase.Ports
{
    public interface IFinanceClient
    {
        Task<FinanceBalanceResponse> GetBalancesAsync(string memberId);
        Task<FinanceMemberResponse> GetMemberAsync(string memberId);
    }
}
```

**Implementation Location:** `HealthEquity.RA.Client.Finance/`

```csharp
namespace HealthEquity.RA.Client.Finance
{
    public class FinanceClient : IFinanceClient
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<FinanceClient> _logger;
        
        public FinanceClient(HttpClient httpClient, ILogger<FinanceClient> logger)
        {
            _httpClient = httpClient;
            _logger = logger;
        }
        
        public async Task<FinanceBalanceResponse> GetBalancesAsync(string memberId)
        {
            var response = await _httpClient.GetAsync($"/api/v1/balances?memberId={memberId}");
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadFromJsonAsync<FinanceBalanceResponse>();
        }
    }
}
```

---

## 🎨 API Design Standards

### REST Endpoint Conventions

**Base Path:** `/api/v1/ra/`

**Resource Naming:**
- `funding-invoices` (kebab-case, plural)
- `funding-batches`
- `contributions`
- `distributions`

**HTTP Methods:**
```
POST   /api/v1/ra/funding-invoices          # Create
GET    /api/v1/ra/funding-invoices/{id}     # Read
PATCH  /api/v1/ra/funding-invoices/{id}     # Partial update
PUT    /api/v1/ra/funding-invoices/{id}     # Full replace
DELETE /api/v1/ra/funding-invoices/{id}     # Soft delete

POST   /api/v1/ra/funding-invoices/generate # Action (RPC-style)
POST   /api/v1/ra/funding-batches/{id}/close # State transition
POST   /api/v1/ra/funding-batches/{id}/reopen
```

**Controller Structure:**
```csharp
namespace HealthEquity.RA.Api.Host.Controllers
{
    [ApiController]
    [Route("api/v1/ra/funding-invoices")]
    public class FundingInvoiceController : ControllerBase
    {
        private readonly ICreateFundingInvoiceUseCase _createUseCase;
        
        [HttpPost]
        public async Task<ActionResult<FundingInvoiceResponse>> Create(
            [FromBody] CreateFundingInvoiceRequest request)
        {
            var command = request.ToCommand(); // Map to domain command
            var result = await _createUseCase.ExecuteAsync(command);
            return CreatedAtAction(nameof(GetById), new { id = result.InvoiceId }, result.ToResponse());
        }
    }
}
```

---

## ✅ Validation Standards

### FluentValidation Rules

**Location:** `HealthEquity.RA.Api.Host/Validators/`

```csharp
namespace HealthEquity.RA.Api.Host.Validators
{
    public class CreateFundingInvoiceRequestValidator : AbstractValidator<CreateFundingInvoiceRequest>
    {
        public CreateFundingInvoiceRequestValidator()
        {
            RuleFor(x => x.SubaccountId)
                .NotEmpty()
                .WithMessage("Subaccount ID is required");
                
            RuleFor(x => x.EmployerAmount)
                .GreaterThanOrEqualTo(0)
                .WithMessage("Employer amount cannot be negative");
                
            RuleFor(x => x.EmployeeAmount)
                .GreaterThanOrEqualTo(0)
                .WithMessage("Employee amount cannot be negative");
                
            RuleFor(x => x)
                .Must(x => x.EmployerAmount + x.EmployeeAmount >= 10)
                .WithMessage("Total funding amount must be at least $10");
        }
    }
}
```

---

## 🔐 Security Standards

### RA-Specific Authorization

**Claims Required:**
- `domain:ra` - Access to RA domain
- `ra:funding:read` - Read funding data
- `ra:funding:write` - Create/update funding data
- `ra:admin` - Administrative operations

**Controller Authorization:**
```csharp
[Authorize(Policy = "RAFundingWrite")]
[HttpPost]
public async Task<ActionResult<FundingInvoiceResponse>> Create(...)
{
    // Implementation
}
```

---

## 📊 Logging Standards

### RA-Specific Log Events

**Event IDs (2000-2999 reserved for RA domain):**
- `2001` - Funding invoice created
- `2002` - Funding invoice generation triggered
- `2003` - Funding batch closed
- `2004` - Cross-domain call to Finance
- `2005` - Paragon API call

**Usage:**
```csharp
_logger.LogInformation(2001, 
    "Funding invoice created: InvoiceId={InvoiceId}, SubaccountId={SubaccountId}, Amount={Amount}",
    invoice.InvoiceId, invoice.SubaccountId, invoice.TotalAmount);
```

---

## 🧪 Testing Standards

### Test Project Structure

```
HealthEquity.RA.DomainCore.Tests/
  Entities/
    FundingInvoiceTests.cs
  ValueObjects/
    MoneyTests.cs
  Validators/
    FundingInvoiceValidatorTests.cs

HealthEquity.RA.UseCase.Tests/
  Fees/
    CreateFundingInvoiceUseCaseTests.cs
  Mocks/
    MockFundingInvoiceRepository.cs

HealthEquity.RA.Api.Host.Tests/
  Controllers/
    FundingInvoiceControllerTests.cs
  Integration/
    FundingInvoiceEndpointTests.cs
```

### Test Naming Convention

```csharp
[Fact]
public async Task ExecuteAsync_WhenAmountBelowMinimum_ShouldThrowValidationException()
{
    // Arrange
    // Act
    // Assert
}
```

---

## 📚 References

**Core Guidelines:**
- Clean Architecture Layer Definitions: `CORTEX/cortex-brain/documents/guidelines/architecture/clean-architecture-layer-definitions.md`
- Architecture Patterns: `CORTEX/cortex-brain/documents/guidelines/architecture/architecture-diagrams-and-patterns.md`

**Platform Standards:**
- SQL Server SQL: `.github/instructions/sql-server-sql.instructions.md`
- Databricks SQL: `.github/instructions/databricks-sql.instructions.md`

**Frameworks:**
- DomainFramework: [Internal documentation]
- ClassicModernization: [Internal documentation]

---

**Enforcement:** These standards are validated by:
- `domain_boundary_checker.py`
- `project_reference_validator.py`
- Code review checklist
- CI/CD pipeline checks

---

**Last Updated:** December 15, 2025  
**Next Review:** Quarterly or as needed
