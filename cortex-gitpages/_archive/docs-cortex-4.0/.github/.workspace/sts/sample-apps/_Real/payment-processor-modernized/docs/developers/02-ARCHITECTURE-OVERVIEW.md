# Architecture Overview

**Audience:** Developers, architects, technical leads  
**Purpose:** Understand system design, patterns, and architectural decisions  
**Reading Time:** 15 minutes

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│          (Web UI, Mobile Apps, External Systems)             │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS / REST
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (ASP.NET Core 8)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Controllers  │  │  Middleware  │  │   Filters    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────┬────────────────────────────────────────────┘
                 │ DTOs / Requests
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Layer (Business Logic)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Services   │  │  Validators  │  │    DTOs      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────┬────────────────────────────────────────────┘
                 │ Repository Interfaces
                 ▼
┌─────────────────────────────────────────────────────────────┐
│               Infrastructure Layer (Data Access)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ EF Core Repos│  │  Mock Repos  │  │   Adapters   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────┬────────────────────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
┌──────────────┐    ┌──────────────────┐
│  SQL Server  │    │ External APIs    │
│   Database   │    │ (Paragon, etc.)  │
└──────────────┘    └──────────────────┘
```

### Design Pattern: Clean Architecture

**Dependency Rule:** Dependencies flow inward (outer layers depend on inner layers, never the reverse)

```
API Layer → Core Layer ← Infrastructure Layer
  (UI)      (Business)        (Data/External)
```

**Benefits:**
- ✅ Testable: Core logic independent of database/UI
- ✅ Flexible: Swap data providers (Mock ↔ EF Core) without code changes
- ✅ Maintainable: Clear separation of concerns

---

## 📦 Layer Breakdown

### API Layer (`PaymentProcessor.TransactionInvoices.API`)

**Responsibilities:**
- HTTP request/response handling
- Authentication & authorization
- Input validation (model binding)
- API documentation (Swagger/OpenAPI)
- Cross-cutting concerns (logging, error handling)

**Key Components:**

| Component | Purpose | Example |
|-----------|---------|---------|
| **Controllers** | REST endpoints | `TransactionInvoiceController.cs` (248 LOC) |
| **Middleware** | Request pipeline | `ErrorHandlingMiddleware.cs` (87 LOC) |
| **Filters** | Cross-cutting logic | `ValidationFilter.cs` (43 LOC) |
| **DTOs** | API contracts | `CreateTransactionInvoiceRequest.cs` |

**Example Controller:**

```csharp
[ApiController]
[Route("api/v1/transaction-invoices")]
public class TransactionInvoiceController : ControllerBase
{
    private readonly ITransactionInvoiceService _service;
    
    [HttpPost]
    [ProducesResponseType(typeof(TransactionInvoiceResponse), StatusCodes.Status201Created)]
    public async Task<IActionResult> CreateInvoice([FromBody] CreateTransactionInvoiceRequest request)
    {
        // Controller only orchestrates - business logic in service
        var invoice = await _service.CreateAsync(request);
        return CreatedAtAction(nameof(GetInvoice), new { id = invoice.InvoiceId }, invoice);
    }
}
```

---

### Core Layer (`PaymentProcessor.TransactionInvoices.Core`)

**Responsibilities:**
- Business logic and domain rules
- Data validation (FluentValidation)
- Domain models and DTOs
- Service interfaces

**Key Components:**

| Component | Purpose | Example |
|-----------|---------|---------|
| **Services** | Business operations | `TransactionInvoiceService.cs` (538 LOC) |
| **Validators** | Input validation | `CreateTransactionInvoiceValidator.cs` (173 LOC) |
| **DTOs** | Data transfer objects | `TransactionInvoiceDTO.cs` |
| **Interfaces** | Abstraction contracts | `ITransactionInvoiceRepository.cs` |

**Example Service (Business Logic):**

```csharp
public class TransactionInvoiceService : ITransactionInvoiceService
{
    private readonly ITransactionInvoiceRepository _repository;
    private readonly IValidator<CreateTransactionInvoiceRequest> _validator;
    private readonly IPaymentPlanAdapter _planAdapter;
    
    public async Task<TransactionInvoiceDTO> CreateAsync(CreateTransactionInvoiceRequest request)
    {
        // 1. Validate input
        var validationResult = await _validator.ValidateAsync(request);
        if (!validationResult.IsValid)
            throw new ValidationException(validationResult.Errors);
        
        // 2. Get payment plan (external API)
        var plan = await _planAdapter.GetPlanAsync(request.PaymentPlanId);
        
        // 3. Calculate amounts (business rule)
        var totalAmount = request.EmployerTransactionDefault + request.EmployeeTransactionDefault;
        
        // 4. Create invoice entity
        var invoice = new TransactionInvoice
        {
            InvoiceId = Guid.NewGuid(),
            EmployerId = request.EmployerId,
            Amount = totalAmount,
            Status = "Pending",
            // ... other properties
        };
        
        // 5. Persist to repository (abstraction - could be Mock or EF Core)
        await _repository.CreateAsync(invoice);
        
        return MapToDTO(invoice);
    }
}
```

**Example Validator:**

```csharp
public class CreateTransactionInvoiceValidator : AbstractValidator<CreateTransactionInvoiceRequest>
{
    public CreateTransactionInvoiceValidator()
    {
        RuleFor(x => x.EmployerId).NotEmpty().MaximumLength(50);
        RuleFor(x => x.AccountCategoryId).NotEmpty().MaximumLength(50);
        RuleFor(x => x.EmployerTransactionDefault).GreaterThanOrEqualTo(0);
        RuleFor(x => x.EmployeeTransactionDefault).GreaterThanOrEqualTo(0);
        RuleFor(x => x).Must(HavePositiveTotalAmount)
            .WithMessage("Total transaction amount must be greater than zero.");
    }
    
    private bool HavePositiveTotalAmount(CreateTransactionInvoiceRequest request)
    {
        return (request.EmployerTransactionDefault + request.EmployeeTransactionDefault) > 0;
    }
}
```

---

### Infrastructure Layer (`PaymentProcessor.TransactionInvoices.Infrastructure`)

**Responsibilities:**
- Data persistence (EF Core, Mock)
- External API integration (Adapters)
- Feature management (data layer routing)
- Monitoring and logging

**Key Components:**

| Component | Purpose | Example |
|-----------|---------|---------|
| **EF Core Repos** | Database access | `EFCoreTransactionInvoiceRepository.cs` (410 LOC) |
| **Mock Repos** | In-memory storage | `MockTransactionInvoiceRepository.cs` (358 LOC) |
| **Adapters** | External systems | `PaymentPlanAdapter.cs` (102 LOC) |
| **DbContext** | EF Core configuration | `TransactionInvoicesDbContext.cs` (156 LOC) |

**Example Repository (EF Core):**

```csharp
public class EFCoreTransactionInvoiceRepository : ITransactionInvoiceRepository
{
    private readonly TransactionInvoicesDbContext _context;
    
    public async Task<TransactionInvoice> CreateAsync(TransactionInvoice invoice)
    {
        _context.TransactionInvoices.Add(invoice);
        await _context.SaveChangesAsync();
        return invoice;
    }
    
    public async Task<TransactionInvoice?> GetByIdAsync(Guid invoiceId)
    {
        return await _context.TransactionInvoices
            .AsNoTracking()  // Performance optimization
            .FirstOrDefaultAsync(i => i.InvoiceId == invoiceId);
    }
    
    public async Task<IEnumerable<TransactionInvoice>> GetByEmployerIdAsync(string employerId)
    {
        return await _context.TransactionInvoices
            .AsNoTracking()
            .Where(i => i.EmployerId == employerId && !i.IsVoided)
            .OrderByDescending(i => i.CreatedDate)
            .ToListAsync();
    }
}
```

**Example Adapter (External API):**

```csharp
public class PaymentPlanAdapter : IPaymentPlanAdapter
{
    private readonly HttpClient _httpClient;
    
    public async Task<PaymentPlan> GetPlanAsync(string planId)
    {
        var response = await _httpClient.GetAsync($"/api/plans/{planId}");
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsAsync<PaymentPlan>();
    }
}
```

---

## 🔄 Data Flow Example

### Create Transaction Invoice Flow

```
1. HTTP Request
   POST /api/v1/transaction-invoices
   Body: { "employerId": "EMP-001", ... }
   
   ↓
   
2. Controller (API Layer)
   - Binds request to CreateTransactionInvoiceRequest DTO
   - Calls service
   
   ↓
   
3. Service (Core Layer)
   - Validates input (FluentValidation)
   - Fetches payment plan (Adapter)
   - Calculates amounts (business logic)
   - Creates TransactionInvoice entity
   - Calls repository
   
   ↓
   
4. Repository (Infrastructure Layer)
   - EF Core: INSERT INTO TransactionInvoices...
   - OR Mock: Add to in-memory list
   
   ↓
   
5. Response
   - Service maps entity to DTO
   - Controller returns 201 Created
   
   ↓
   
6. HTTP Response
   {
     "invoiceId": "guid-here",
     "invoiceNumber": "INV-0001",
     "amount": 750.00,
     "status": "Pending"
   }
```

---

## 🎨 Design Patterns

### Repository Pattern

**Purpose:** Abstract data access logic

**Implementation:**

```csharp
// Interface (in Core layer)
public interface ITransactionInvoiceRepository
{
    Task<TransactionInvoice> CreateAsync(TransactionInvoice invoice);
    Task<TransactionInvoice?> GetByIdAsync(Guid invoiceId);
    Task UpdateAsync(TransactionInvoice invoice);
    Task DeleteAsync(Guid invoiceId);
}

// Implementation (in Infrastructure layer)
public class EFCoreTransactionInvoiceRepository : ITransactionInvoiceRepository
{
    // EF Core implementation
}

public class MockTransactionInvoiceRepository : ITransactionInvoiceRepository
{
    // In-memory implementation
}
```

**Benefits:**
- ✅ Swap implementations without changing business logic
- ✅ Easy to test (mock repositories)
- ✅ Consistent API for data access

---

### Unit of Work Pattern

**Purpose:** Group multiple repository operations into a single transaction

**Implementation:**

```csharp
public interface IUnitOfWork
{
    ITransactionInvoiceRepository TransactionInvoices { get; }
    ITransactionBatchRepository TransactionBatches { get; }
    IInvoiceLineItemRepository LineItems { get; }
    
    Task<int> SaveChangesAsync();
    Task BeginTransactionAsync();
    Task CommitAsync();
    Task RollbackAsync();
}

// Usage in service
public async Task CloseBatchAsync(Guid batchId)
{
    await _unitOfWork.BeginTransactionAsync();
    
    try
    {
        // 1. Update batch status
        var batch = await _unitOfWork.TransactionBatches.GetByIdAsync(batchId);
        batch.Status = "Closed";
        await _unitOfWork.TransactionBatches.UpdateAsync(batch);
        
        // 2. Update all invoices in batch
        var invoices = await _unitOfWork.TransactionInvoices.GetByBatchIdAsync(batchId);
        foreach (var invoice in invoices)
        {
            invoice.Status = "Processed";
            await _unitOfWork.TransactionInvoices.UpdateAsync(invoice);
        }
        
        // 3. Commit transaction
        await _unitOfWork.CommitAsync();
    }
    catch
    {
        await _unitOfWork.RollbackAsync();
        throw;
    }
}
```

---

### Adapter Pattern

**Purpose:** Integrate with external systems without coupling business logic

**Implementation:**

```csharp
// Interface (in Core layer)
public interface IPaymentPlanAdapter
{
    Task<PaymentPlan> GetPlanAsync(string planId);
    Task<bool> IsPlanActiveAsync(string planId);
}

// Implementation (in Infrastructure layer)
public class ParagonPaymentPlanAdapter : IPaymentPlanAdapter
{
    // Calls Paragon API
}

public class MockPaymentPlanAdapter : IPaymentPlanAdapter
{
    // Returns fake data for testing
}
```

**Benefits:**
- ✅ Isolate external dependencies
- ✅ Easy to test (mock adapters)
- ✅ Swap external systems without changing business logic

---

### Dependency Injection

**Purpose:** Inversion of Control for loose coupling

**Implementation:**

```csharp
// Startup.cs (API project)
public void ConfigureServices(IServiceCollection services)
{
    // Core services
    services.AddScoped<ITransactionInvoiceService, TransactionInvoiceService>();
    services.AddScoped<ITransactionBatchService, TransactionBatchService>();
    
    // Validators
    services.AddValidatorsFromAssemblyContaining<CreateTransactionInvoiceValidator>();
    
    // Data layer (swappable via configuration)
    services.AddDataLayer(Configuration);  // Mock or EF Core
    
    // External adapters
    services.AddScoped<IPaymentPlanAdapter, ParagonPaymentPlanAdapter>();
}
```

**DataLayerRouter:**

```csharp
public static IServiceCollection AddDataLayer(
    this IServiceCollection services,
    IConfiguration configuration)
{
    var provider = configuration["DataLayer:Provider"];
    
    if (provider == "Mock")
    {
        services.AddScoped<ITransactionInvoiceRepository, MockTransactionInvoiceRepository>();
        // ... other mock repos
    }
    else if (provider == "EFCore")
    {
        services.AddDbContext<TransactionInvoicesDbContext>(/* ... */);
        services.AddScoped<ITransactionInvoiceRepository, EFCoreTransactionInvoiceRepository>();
        // ... other EF Core repos
    }
    
    return services;
}
```

---

## 🔐 Security Architecture

### Authentication & Authorization

```csharp
[Authorize(Roles = "TransactionAdmin,SystemAdmin")]
[ApiController]
public class TransactionInvoiceController : ControllerBase
{
    // Only authorized users can access
}
```

### Data Encryption (GDPR Compliance)

```csharp
public class EncryptionService : IEncryptionService
{
    public string Encrypt(string plainText)
    {
        // AES-256 encryption for PII/PII data
    }
    
    public string Decrypt(string cipherText)
    {
        // Decryption with secure key management
    }
}
```

### Secure Logging

```csharp
_logger.LogInformation(
    "Transaction invoice created: {InvoiceId} for Employer: {EmployerId}",
    invoice.InvoiceId,
    MaskEmployerId(invoice.EmployerId)  // Mask PII in logs
);
```

---

## 📊 Monitoring & Observability

### Structured Logging (Serilog)

```csharp
Log.Information(
    "Invoice {InvoiceId} created for employer {EmployerId} with amount {Amount}",
    invoice.InvoiceId,
    invoice.EmployerId,
    invoice.Amount
);
```

**Log Output (JSON):**
```json
{
  "timestamp": "2025-12-12T10:30:00Z",
  "level": "Information",
  "messageTemplate": "Invoice {InvoiceId} created...",
  "properties": {
    "InvoiceId": "guid-here",
    "EmployerId": "EMP-001",
    "Amount": 750.00
  }
}
```

### Correlation IDs

```csharp
public class CorrelationIdMiddleware
{
    public async Task InvokeAsync(HttpContext context)
    {
        var correlationId = context.Request.Headers["X-Correlation-ID"].FirstOrDefault()
            ?? Guid.NewGuid().ToString();
        
        context.Response.Headers.Add("X-Correlation-ID", correlationId);
        
        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            await _next(context);
        }
    }
}
```

**Benefit:** Trace requests across microservices

---

## 🧪 Testability

### Test Pyramid

```
      /\      Unit Tests (87 tests, <1s)
     /  \     - Fast, isolated
    /────\    - Mock all dependencies
   /      \   
  /────────\  Integration Tests (42 tests, ~45s)
 /          \ - Test with real database
/────────────\ Contract Tests (15 tests, ~10s)
               - Schema validation
```

### Example Unit Test

```csharp
public class TransactionInvoiceServiceTests
{
    private readonly Mock<ITransactionInvoiceRepository> _mockRepo;
    private readonly TransactionInvoiceService _service;
    
    [Fact]
    public async Task CreateAsync_ValidRequest_ShouldCreateInvoice()
    {
        // Arrange
        var request = new CreateTransactionInvoiceRequest { /* ... */ };
        _mockRepo.Setup(r => r.CreateAsync(It.IsAny<TransactionInvoice>()))
            .ReturnsAsync((TransactionInvoice i) => i);
        
        // Act
        var result = await _service.CreateAsync(request);
        
        // Assert
        Assert.NotNull(result);
        Assert.Equal(request.EmployerId, result.EmployerId);
        _mockRepo.Verify(r => r.CreateAsync(It.IsAny<TransactionInvoice>()), Times.Once);
    }
}
```

---

## 🚀 Performance Considerations

### Database Optimization

**Indexes:**
```csharp
modelBuilder.Entity<TransactionInvoice>(entity =>
{
    entity.HasIndex(e => e.EmployerId);  // Frequent queries by employer
    entity.HasIndex(e => e.Status);      // Filter by status
    entity.HasIndex(e => e.BatchId);     // Batch operations
});
```

**AsNoTracking:**
```csharp
// Read-only queries don't need change tracking
return await _context.TransactionInvoices
    .AsNoTracking()  // 30% faster
    .Where(i => i.EmployerId == employerId)
    .ToListAsync();
```

### Async/Await

```csharp
// ❌ Bad: Blocking
var invoice = _repository.GetByIdAsync(invoiceId).Result;

// ✅ Good: Non-blocking
var invoice = await _repository.GetByIdAsync(invoiceId);
```

---

## 📚 Key Architectural Decisions

### Why Clean Architecture?

| Decision | Rationale |
|----------|-----------|
| **3-Layer Design** | Clear separation: UI, Business, Data |
| **Dependency Inversion** | Core doesn't depend on Infrastructure |
| **Repository Pattern** | Abstract data access for flexibility |
| **Feature Flags** | Swap Mock ↔ EF Core without code changes |

### Why Mock + EF Core?

| Mode | Purpose | When to Use |
|------|---------|-------------|
| **Mock** | Fast development, no database setup | Local dev, unit tests |
| **EF Core** | Production persistence | Integration tests, production |

### Why FluentValidation?

- ✅ Declarative validation rules
- ✅ Testable validators
- ✅ Separation from business logic
- ✅ Rich error messages

---

## 🔍 Further Reading

- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Repository Pattern](https://docs.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design)
- [EF Core Best Practices](https://docs.microsoft.com/en-us/ef/core/performance/)
- [ASP.NET Core Architecture](https://docs.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/)

---

**Next Step:** [EF Core Migration Guide →](./03-EFCORE-MIGPaymentProcessorTION.md)

**Last Updated:** December 12, 2025
