# RA Funding Invoices Migration Plan (Enhanced v2.0)
**Migration Target:** Product.RA.Api (.NET 8)  
**Author:** Asif Hussain  
**Date:** December 12, 2025  
**Version:** 2.0 (Enhanced with Mock Layer, UI Test Client, Contract Verification, HIPAA/SOC2)  

---

## Executive Summary

This plan outlines the migration of two critical RA (Reimbursement Arrangement) funding invoice services from legacy .NET Framework to modern .NET 8 REST APIs. The migration focuses on **cost-effectiveness, security, extensibility, and scalability** while maintaining **100% backward compatibility** with existing WCF contracts.

**Services in Scope:**
1. `Updater_CreateRAFundingInvoices.cs` - Scheduled service for bulk RA invoice creation
2. `XGenerateFundingInvoice.cs` - Transaction-based individual invoice generation

**Enhanced Features (v2.0):**
- ✅ **Mock Data Layer:** In-memory repositories for fast testing without database dependencies
- ✅ **Repository Abstraction:** Seamless swapping between Mock → EF Core → Dapper implementations
- ✅ **Schema Validation Phase:** Ensures mock data contracts match production database schema (prevents UI breaks)
- ✅ **UI Test Client:** Blazor-based web interface for manual API testing and contract validation
- ✅ **Contract Verification Framework:** Automated 100% WCF contract compatibility testing (MANDATORY phase)
- ✅ **90% Test Coverage:** Comprehensive automated test suite (unit + integration + contract + schema)
- ✅ **HIPAA/SOC2 Compliance:** Enhanced security with audit logging, field-level encryption, PHI protection
- ✅ **13-Week Timeline:** Includes mandatory contract verification gate (Phase 4a) and schema validation (Phase 5a)

---

## 1. Current State Analysis

### 1.1 Service Architecture Overview

#### **Updater_CreateRAFundingInvoices** 
- **Type:** Scheduled background service (SimpleServiceBase)
- **Location:** `Platform.Classic/HealthEquity/Libs/HEInteraction/Services/Updaters/`
- **Primary Function:** Batch processing to create RA funding invoices for employers
- **Execution Model:** Parameter-driven (employer list or all employers)
- **Key Methods:**
  - `Run()` - Main orchestration
  - `QueryDatabaseForSubaccounts()` - EDM query for eligible accounts
  - `CreateRAFundingInvoices()` - Batch invoice creation
  - `ProcessFundingInvoice()` - Individual invoice processing
  - `FindOpenFundingBatch()` - Locate open funding batches
  - `HasInvoiceBeenCreatedToday()` - Duplicate prevention

#### **XGenerateFundingInvoice**
- **Type:** Transaction (HETransaction)
- **Location:** `Platform.Classic/Segment4/HETransactions/`
- **Primary Function:** On-demand funding invoice generation with auto-debit support
- **Input Contract:**
  - `SubaccountId` (string)
  - `InvoiceAmount` (decimal)
  - `InvoiceDate` (DateTime)
- **Output:** 
  - `Result` (string) - "invoice created", "invoice not needed", or error
  - `NewCashInOutId` (CashInOut object)

### 1.2 Technology Stack (Current)

| Component | Technology | Notes |
|-----------|-----------|-------|
| Framework | .NET Framework 4.x | Legacy |
| Data Access | EDM (EBTDataMapping) | Custom ORM |
| Service Layer | HETransaction pattern | Custom request/response |
| Database | SQL Server | Direct ADO.NET + EDM queries |
| Dependency Injection | Unity Container | Legacy IoC |
| Logging | Hqy.Logging.Abstractions | Custom logging |
| Async | Task.Run().Wait() | Blocking async (anti-pattern) |

### 1.3 Dependencies Map

#### **Data Dependencies**
```
Database Tables (Identified):
├── Subaccount (PreFunding type, RA bank account)
├── FundingBatch (Open/Pending/Reopened status)
├── FundingBatchInvoice
├── FundingFrequency (matching logic, peg amounts)
├── CashInOut (RA funding invoices)
├── TransferLine (prefunding transfers)
├── Payment (auto-debit payments)
├── PaymentAuthorization (ACH payment methods)
├── Employer (invoice associations)
├── ReimbursementPlan (benefit group associations)
└── BenefitGroupReimbursementPlan (funding subaccount mappings)
```

#### **Service Dependencies**
```
Internal Services:
├── QFindRAPlansBySubaccount (query)
├── XCloseFundingBatch (transaction)
├── XUpdateFundingBatch (transaction)
├── XAddCashInOut (transaction)
├── XAddPayment (transaction)
├── XAddRABenefitGroupCashInOutsBySubaccountIds (transaction)
└── DataAccessFactory (data access creation)

External Services:
└── IReimbursementPlanService (Paragon microservice)
    ├── GetFundingOptionsAndPaymentAuthorizationsAsync()
    └── AddBenefitGroupCashInOutsBySubaccountAsync()
```

#### **Business Logic Dependencies**
```
Business Rules:
├── Funding Frequency Matching (date-based)
├── Peg Amount Threshold (balance + pending < peg)
├── Duplicate Invoice Prevention (one per employer per day)
├── Third-Party Funding (health plan invoices)
├── Auto-Debit Processing (2 business days + effective date logic)
├── Open Funding Batch Discovery
├── Error Recovery (batch reopening)
└── Benefit Group Cash-In/Out Tracking
```

---

## 2. Target Architecture Design

### 2.1 REST API Structure (Product.RA.Api)

```
Product.RA.Api/
├── Controllers/
│   ├── FundingInvoiceController.cs
│   │   ├── POST /api/v1/funding-invoices          # Single invoice generation
│   │   ├── POST /api/v1/funding-invoices/batch    # Batch invoice creation
│   │   ├── GET  /api/v1/funding-invoices/{id}     # Invoice status
│   │   └── GET  /api/v1/funding-invoices/subaccount/{subaccountId}
│   │
│   ├── FundingBatchController.cs
│   │   ├── GET  /api/v1/funding-batches/{id}
│   │   ├── POST /api/v1/funding-batches/{id}/close
│   │   └── POST /api/v1/funding-batches/{id}/reopen
│   │
│   └── HealthController.cs                        # Health checks
│       ├── GET  /health
│       └── GET  /health/ready
│
├── Services/
│   ├── IFundingInvoiceService.cs
│   │   ├── CreateFundingInvoiceAsync()
│   │   ├── CreateBatchFundingInvoicesAsync()
│   │   ├── ValidateFundingEligibilityAsync()
│   │   └── ProcessAutoDebitAsync()
│   │
│   ├── IFundingBatchService.cs
│   │   ├── FindOpenFundingBatchAsync()
│   │   ├── CloseFundingBatchAsync()
│   │   └── ReopenFundingBatchAsync()
│   │
│   ├── IReimbursementPlanAdapter.cs               # Adapter for Paragon service
│   │   ├── GetPaymentAuthorizationsAsync()
│   │   └── AddBenefitGroupCashInOutsAsync()
│   │
│   └── ISubaccountQueryService.cs
│       ├── GetEligibleSubaccountsAsync()
│       └── HasInvoiceBeenCreatedTodayAsync()
│
├── Repositories/                                  # Abstraction for data access
│   ├── Abstractions/
│   │   ├── IFundingInvoiceRepository.cs
│   │   ├── IFundingBatchRepository.cs
│   │   ├── ISubaccountRepository.cs
│   │   ├── ICashInOutRepository.cs
│   │   └── IUnitOfWork.cs                        # Transaction management
│   │
│   ├── EntityFramework/                          # EF Core implementation
│   │   ├── EfFundingInvoiceRepository.cs
│   │   ├── EfFundingBatchRepository.cs
│   │   ├── EfSubaccountRepository.cs
│   │   ├── EfCashInOutRepository.cs
│   │   └── EfUnitOfWork.cs
│   │
│   ├── Mock/                                     # In-memory mock data
│   │   ├── MockFundingInvoiceRepository.cs
│   │   ├── MockFundingBatchRepository.cs
│   │   ├── MockSubaccountRepository.cs
│   │   ├── MockCashInOutRepository.cs
│   │   ├── MockUnitOfWork.cs
│   │   └── MockDataSeeder.cs                    # Test data generation
│   │
│   └── Dapper/                                   # Optional: High-performance queries
│       ├── DapperQueryRepository.cs              # Read-heavy operations
│       └── DapperBulkOperations.cs               # Batch inserts
│
├── Models/
│   ├── Requests/
│   │   ├── CreateFundingInvoiceRequest.cs
│   │   ├── CreateBatchFundingInvoicesRequest.cs
│   │   └── CloseFundingBatchRequest.cs
│   │
│   ├── Responses/
│   │   ├── FundingInvoiceResponse.cs
│   │   ├── BatchFundingInvoiceResponse.cs
│   │   └── FundingBatchResponse.cs
│   │
│   └── Domain/
│       ├── FundingInvoice.cs
│       ├── FundingBatch.cs
│       ├── SubaccountEligibility.cs
│       └── AutoDebitPayment.cs
│
├── Infrastructure/
│   ├── Data/
│   │   ├── RADbContext.cs (EF Core 8)
│   │   ├── Configurations/
│   │   └── Migrations/
│   │
│   ├── ExternalServices/
│   │   └── ReimbursementPlanServiceClient.cs
│   │
│   └── Messaging/
│       ├── IEventPublisher.cs
│       └── FundingInvoiceCreatedEvent.cs
│
├── Validation/
│   ├── CreateFundingInvoiceValidator.cs
│   └── CreateBatchInvoicesValidator.cs
│
├── Middleware/
│   ├── ErrorHandlingMiddleware.cs
│   ├── RequestLoggingMiddleware.cs
│   ├── AuthenticationMiddleware.cs
│   ├── AuditLoggingMiddleware.cs                # HIPAA compliance
│   └── DataEncryptionMiddleware.cs              # PHI protection
│
├── Testing/
│   ├── ContractVerification/
│   │   ├── WcfContractComparison.cs             # Legacy vs. new contract validation
│   │   ├── ContractCompatibilityTests.cs        # 100% compatibility tests
│   │   └── SchemaValidator.cs                   # JSON schema validation
│   │
│   └── IntegrationTests/
│       ├── FundingInvoiceApiTests.cs
│       ├── FundingBatchApiTests.cs
│       └── ContractComplianceTests.cs           # Backward compatibility suite
│
├── UITestClient/                                # Simple web UI for manual testing
│   ├── wwwroot/
│   │   ├── index.html                           # Main test interface
│   │   ├── css/
│   │   │   └── app.css
│   │   └── js/
│   │       ├── api-client.js                    # REST API wrapper
│   │       ├── test-scenarios.js                # Pre-built test cases
│   │       └── response-viewer.js               # JSON response formatting
│   │
│   ├── Pages/
│   │   ├── SingleInvoice.cshtml                 # Test single invoice creation
│   │   ├── BatchInvoice.cshtml                  # Test batch operations
│   │   └── ContractComparison.cshtml            # Side-by-side WCF vs. REST
│   │
│   └── Program.cs                               # Minimal API host
│
└── Configuration/
    ├── ServiceCollectionExtensions.cs
    ├── RepositoryConfiguration.cs               # Repository DI setup
    ├── MockDataConfiguration.cs                 # Mock layer toggle
    ├── appsettings.json
    ├── appsettings.Mock.json                    # Mock environment
    ├── appsettings.Development.json
    └── appsettings.Production.json
```

### 2.2 Technology Stack (Target)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Framework | .NET 8 | LTS, performance, modern features |
| API Pattern | REST (ASP.NET Core Controllers) | Industry standard, scalable, contract-first design |
| Data Access | Repository Pattern with Multiple Implementations | Abstraction allows mock → EF Core → Dapper swap |
| ORM | Entity Framework Core 8 | Primary implementation, async-first, LINQ support |
| Micro-ORM | Dapper (optional) | High-performance queries for read-heavy operations |
| Mock Layer | In-Memory Repository Pattern | Unit testing without database, fast CI/CD |
| Validation | FluentValidation | Declarative, testable, maintainable |
| Dependency Injection | Built-in (.NET DI) | Native, performant, zero cost |
| Logging | Serilog + Application Insights | Structured logging, cloud-native observability |
| Audit Logging | Custom Middleware + Azure Table Storage | HIPAA compliance, immutable audit trail |
| Async | async/await (true async) | Non-blocking, scalable |
| Authentication | JWT Bearer Tokens | Stateless, secure, standard |
| Authorization | Policy-based (ASP.NET Core) | Fine-grained, role-based |
| Health Checks | ASP.NET Core Health Checks | Built-in, Kubernetes-ready |
| API Documentation | Swagger/OpenAPI | Self-documenting, developer-friendly |
| Contract Testing | Custom WCF Comparison Framework | 100% backward compatibility verification |
| Circuit Breaker | Polly | Resilience, fault tolerance |
| Rate Limiting | ASP.NET Core Rate Limiting | DDoS protection, cost control |
| Caching | IDistributedCache (Redis) | Performance optimization |
| Encryption | AES-256 for data at rest, TLS 1.3 for transit | HIPAA/SOC2 compliance |
| Secret Management | Azure Key Vault | Centralized, audited secret storage |
| UI Test Client | Blazor Server (minimal) | Rapid prototyping, same stack as API |

### 2.3 Security Architecture

#### **Authentication & Authorization**
```csharp
// JWT Bearer Token with role-based claims
[Authorize(Policy = "RAFundingInvoiceWrite")]
[HttpPost("api/v1/funding-invoices")]
public async Task<ActionResult<FundingInvoiceResponse>> CreateInvoice(
    [FromBody] CreateFundingInvoiceRequest request)
{
    // Role: "RA.FundingInvoice.Create"
    // Scope: "api://product-ra/funding.write"
}
```

#### **Security Features (Enhanced for HIPAA/SOC2)**
- **Transport Security:** TLS 1.3 minimum, HSTS enabled
- **Authentication:** OAuth 2.0 / JWT Bearer Tokens (RS256 signing)
- **Authorization:** Role-based + Claim-based policies + attribute-based access control (ABAC)
- **Input Validation:** FluentValidation + model binding + request size limits
- **SQL Injection Prevention:** EF Core parameterized queries only (no raw SQL)
- **Rate Limiting:** Per-endpoint throttling (100 req/min per user, 1000 req/min per API key)
- **Audit Logging:** All create/update/delete operations logged with user identity, timestamp, IP address
- **Secret Management:** Azure Key Vault integration (no secrets in config files)
- **CORS:** Restricted origins (whitelist only, no wildcard)
- **Data Encryption at Rest:** Transparent Data Encryption (TDE) on SQL Server
- **Data Encryption in Transit:** TLS 1.3 for all API calls, certificate pinning for external services
- **PHI Protection:** Encrypted columns for sensitive data (SSN, DOB), field-level encryption
- **Session Management:** Short-lived tokens (15 min access, 7 day refresh), token revocation list
- **Security Headers:** Content-Security-Policy, X-Frame-Options, X-Content-Type-Options
- **Dependency Scanning:** Automated NuGet package vulnerability scanning (Dependabot, Snyk)
- **Penetration Testing:** Annual third-party pen tests, quarterly internal scans
- **Data Retention:** 7-year retention for audit logs (HIPAA requirement), automated archival to cold storage
- **Breach Notification:** Automated alerting for suspicious activity (failed auth attempts, data exfiltration patterns)
- **Least Privilege:** Service accounts with minimal permissions, no shared credentials

#### **HIPAA/SOC2 Compliance Enhancements**
```csharp
// Audit logging middleware
public class AuditLoggingMiddleware
{
    public async Task InvokeAsync(HttpContext context)
    {
        var auditEntry = new AuditLogEntry
        {
            Timestamp = DateTimeOffset.UtcNow,
            UserId = context.User.FindFirst(ClaimTypes.NameIdentifier)?.Value,
            Username = context.User.Identity?.Name,
            IPAddress = context.Connection.RemoteIpAddress?.ToString(),
            Method = context.Request.Method,
            Path = context.Request.Path,
            QueryString = context.Request.QueryString.ToString(),
            UserAgent = context.Request.Headers["User-Agent"]
        };
        
        // Capture request body for POST/PUT (excluding PHI fields)
        if (context.Request.Method == "POST" || context.Request.Method == "PUT")
        {
            context.Request.EnableBuffering();
            var body = await new StreamReader(context.Request.Body).ReadToEndAsync();
            auditEntry.RequestBody = RedactPHI(body); // Remove SSN, DOB, etc.
            context.Request.Body.Position = 0;
        }
        
        await _next(context);
        
        auditEntry.StatusCode = context.Response.StatusCode;
        auditEntry.ResponseTimeMs = stopwatch.ElapsedMilliseconds;
        
        await _auditLogger.LogAsync(auditEntry); // Write to Azure Table Storage (immutable)
    }
}

// Data encryption for PHI fields
public class EncryptedStringConverter : ValueConverter<string, string>
{
    public EncryptedStringConverter() : base(
        v => Encrypt(v),
        v => Decrypt(v))
    { }
    
    private static string Encrypt(string plainText)
    {
        // Use Azure Key Vault managed keys for encryption
        var keyVaultKey = _keyVaultClient.GetKeyAsync("data-encryption-key").Result;
        return _cryptoService.Encrypt(plainText, keyVaultKey);
    }
}

// Entity configuration with encrypted fields
public class SubaccountConfiguration : IEntityTypeConfiguration<Subaccount>
{
    public void Configure(EntityTypeBuilder<Subaccount> builder)
    {
        builder.Property(s => s.TaxId)
               .HasConversion(new EncryptedStringConverter())
               .HasColumnType("varbinary(max)");
    }
}
```

#### **Security Recommendations**
1. **API Gateway:** Use Azure API Management for centralized authentication, rate limiting, IP filtering
2. **WAF:** Web Application Firewall to prevent OWASP Top 10 attacks
3. **DDoS Protection:** Azure DDoS Protection Standard
4. **Network Isolation:** API hosted in private VNet, accessible only via Private Endpoints
5. **Zero Trust:** Assume breach mentality, verify every request, least privilege access
6. **MFA Enforcement:** Require multi-factor authentication for all admin operations
7. **Security Monitoring:** Real-time threat detection with Azure Sentinel
8. **Incident Response Plan:** Documented procedures for security incidents, 24-hour response SLA

---

### 2.4 Data Layer Abstraction (Mock → EF Core → Dapper)

#### **Repository Pattern Design**

The data layer uses the Repository Pattern with interface abstractions, allowing seamless swapping between implementations:

```csharp
// Core abstraction - technology agnostic
public interface IFundingInvoiceRepository
{
    Task<FundingInvoice?> GetByIdAsync(string invoiceId, CancellationToken cancellationToken = default);
    Task<List<FundingInvoice>> GetBySubaccountIdAsync(string subaccountId, CancellationToken cancellationToken = default);
    Task<FundingInvoice> CreateAsync(FundingInvoice invoice, CancellationToken cancellationToken = default);
    Task UpdateAsync(FundingInvoice invoice, CancellationToken cancellationToken = default);
    Task<bool> HasInvoiceForTodayAsync(string employerId, DateTime date, CancellationToken cancellationToken = default);
}

// Unit of Work for transaction management
public interface IUnitOfWork : IDisposable
{
    IFundingInvoiceRepository FundingInvoices { get; }
    IFundingBatchRepository FundingBatches { get; }
    ISubaccountRepository Subaccounts { get; }
    ICashInOutRepository CashInOuts { get; }
    
    Task<int> SaveChangesAsync(CancellationToken cancellationToken = default);
    Task BeginTransactionAsync(CancellationToken cancellationToken = default);
    Task CommitTransactionAsync(CancellationToken cancellationToken = default);
    Task RollbackTransactionAsync(CancellationToken cancellationToken = default);
}
```

#### **Implementation 1: Mock (In-Memory)**
Fast, deterministic testing without external dependencies.

```csharp
public class MockFundingInvoiceRepository : IFundingInvoiceRepository
{
    private readonly List<FundingInvoice> _invoices = new();
    private readonly object _lock = new();
    
    public Task<FundingInvoice?> GetByIdAsync(string invoiceId, CancellationToken ct = default)
    {
        lock (_lock)
        {
            var invoice = _invoices.FirstOrDefault(i => i.InvoiceId == invoiceId);
            return Task.FromResult(invoice);
        }
    }
    
    public Task<FundingInvoice> CreateAsync(FundingInvoice invoice, CancellationToken ct = default)
    {
        lock (_lock)
        {
            invoice.InvoiceId = $"MOCK-INV-{Guid.NewGuid():N}";
            invoice.CreatedAt = DateTimeOffset.UtcNow;
            _invoices.Add(invoice);
            return Task.FromResult(invoice);
        }
    }
    
    // ... other methods
}

// Mock data seeder for realistic test scenarios
public class MockDataSeeder
{
    public static void SeedTestData(IUnitOfWork unitOfWork)
    {
        // Seed 100 subaccounts with varied scenarios
        var subaccounts = GenerateSubaccounts(100);
        foreach (var sa in subaccounts)
        {
            unitOfWork.Subaccounts.CreateAsync(sa).Wait();
        }
        
        // Seed open funding batches
        var batches = GenerateOpenFundingBatches(subaccounts.Take(50));
        foreach (var batch in batches)
        {
            unitOfWork.FundingBatches.CreateAsync(batch).Wait();
        }
        
        // Seed historical invoices (for duplicate detection tests)
        var historicalInvoices = GenerateHistoricalInvoices(subaccounts.Take(20));
        foreach (var invoice in historicalInvoices)
        {
            unitOfWork.FundingInvoices.CreateAsync(invoice).Wait();
        }
        
        unitOfWork.SaveChangesAsync().Wait();
    }
}
```

#### **Implementation 2: Entity Framework Core**
Primary production implementation with full ORM features.

```csharp
public class EfFundingInvoiceRepository : IFundingInvoiceRepository
{
    private readonly RADbContext _context;
    
    public EfFundingInvoiceRepository(RADbContext context)
    {
        _context = context;
    }
    
    public async Task<FundingInvoice?> GetByIdAsync(string invoiceId, CancellationToken ct = default)
    {
        return await _context.FundingInvoices
            .AsNoTracking()
            .Include(i => i.TransferLines)
            .Include(i => i.AutoDebitPayment)
            .FirstOrDefaultAsync(i => i.InvoiceId == invoiceId, ct);
    }
    
    public async Task<FundingInvoice> CreateAsync(FundingInvoice invoice, CancellationToken ct = default)
    {
        _context.FundingInvoices.Add(invoice);
        // SaveChanges handled by UnitOfWork
        return invoice;
    }
    
    public async Task<bool> HasInvoiceForTodayAsync(string employerId, DateTime date, CancellationToken ct = default)
    {
        return await _context.FundingInvoices
            .AnyAsync(i => i.EmployerId == employerId 
                        && i.InvoiceDate.Date == date.Date, ct);
    }
}

// EF Core DbContext
public class RADbContext : DbContext
{
    public DbSet<FundingInvoice> FundingInvoices { get; set; }
    public DbSet<FundingBatch> FundingBatches { get; set; }
    public DbSet<Subaccount> Subaccounts { get; set; }
    public DbSet<CashInOut> CashInOuts { get; set; }
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(RADbContext).Assembly);
    }
}
```

#### **Implementation 3: Dapper (Optional - High Performance)**
For read-heavy operations or complex queries where EF Core is suboptimal.

```csharp
public class DapperQueryRepository : ISubaccountQueryRepository
{
    private readonly IDbConnection _connection;
    
    public async Task<List<Subaccount>> GetEligibleSubaccountsAsync(
        List<string> employerIds, 
        CancellationToken ct = default)
    {
        var sql = @"
            SELECT s.*, 
                   ff.*, 
                   frp.*
            FROM Subaccount s
            INNER JOIN FundingFrequency ff ON s.SubaccountId = ff.SubaccountId
            INNER JOIN FundingReimbursementPlan frp ON s.SubaccountId = frp.FundingSubaccount
            WHERE s.SubaccountType = 'PreFunding'
              AND s.BankAccount = @BankAccountRA
              AND (@EmployerCount = 0 OR s.HeldFor_ObjectId IN @EmployerIds)
            ORDER BY s.SubaccountId";
        
        var lookup = new Dictionary<string, Subaccount>();
        
        await _connection.QueryAsync<Subaccount, FundingFrequency, FundingReimbursementPlan, Subaccount>(
            sql,
            (subaccount, frequency, plan) =>
            {
                if (!lookup.TryGetValue(subaccount.SubaccountId, out var sa))
                {
                    sa = subaccount;
                    sa.FundingFrequencies = new List<FundingFrequency>();
                    sa.FundingReimbursementPlans = new List<FundingReimbursementPlan>();
                    lookup.Add(sa.SubaccountId, sa);
                }
                
                sa.FundingFrequencies.Add(frequency);
                sa.FundingReimbursementPlans.Add(plan);
                return sa;
            },
            new { BankAccountRA = BankAccountIds.WellsFargo.RA, EmployerIds = employerIds, EmployerCount = employerIds.Count },
            splitOn: "FundingFrequencyId,ReimbursementPlanId"
        );
        
        return lookup.Values.ToList();
    }
}
```

#### **Dependency Injection Configuration**

```csharp
// Startup.cs or Program.cs
public static IServiceCollection AddDataLayer(
    this IServiceCollection services, 
    IConfiguration configuration)
{
    var dataLayerMode = configuration.GetValue<string>("DataLayer:Mode"); // "Mock", "EFCore", "Dapper"
    
    switch (dataLayerMode)
    {
        case "Mock":
            services.AddSingleton<IUnitOfWork, MockUnitOfWork>();
            services.AddSingleton<IFundingInvoiceRepository, MockFundingInvoiceRepository>();
            services.AddSingleton<IFundingBatchRepository, MockFundingBatchRepository>();
            services.AddSingleton<ISubaccountRepository, MockSubaccountRepository>();
            services.AddSingleton<ICashInOutRepository, MockCashInOutRepository>();
            
            // Seed mock data on startup
            var serviceProvider = services.BuildServiceProvider();
            var unitOfWork = serviceProvider.GetRequiredService<IUnitOfWork>();
            MockDataSeeder.SeedTestData(unitOfWork);
            break;
        
        case "EFCore":
            services.AddDbContext<RADbContext>(options =>
                options.UseSqlServer(configuration.GetConnectionString("RADatabase")));
            services.AddScoped<IUnitOfWork, EfUnitOfWork>();
            services.AddScoped<IFundingInvoiceRepository, EfFundingInvoiceRepository>();
            services.AddScoped<IFundingBatchRepository, EfFundingBatchRepository>();
            services.AddScoped<ISubaccountRepository, EfSubaccountRepository>();
            services.AddScoped<ICashInOutRepository, EfCashInOutRepository>();
            break;
        
        case "Dapper":
            services.AddScoped<IDbConnection>(sp => 
                new SqlConnection(configuration.GetConnectionString("RADatabase")));
            services.AddScoped<IUnitOfWork, DapperUnitOfWork>();
            services.AddScoped<IFundingInvoiceRepository, DapperFundingInvoiceRepository>();
            // ... other Dapper repositories
            break;
        
        default:
            throw new InvalidOperationException($"Unknown DataLayer:Mode '{dataLayerMode}'");
    }
    
    return services;
}
```

#### **Configuration (appsettings.json)**

```json
{
  "DataLayer": {
    "Mode": "Mock"  // "Mock", "EFCore", "Dapper"
  },
  "ConnectionStrings": {
    "RADatabase": "Server=localhost;Database=HealthEquity;Trusted_Connection=true;"
  }
}
```

**Benefits:**
- ✅ **Fast Unit Tests:** Mock layer runs in-memory, no database required
- ✅ **Flexible:** Swap implementations without changing business logic
- ✅ **Testable:** Each repository implementation independently testable
- ✅ **Performance:** Use Dapper for read-heavy queries, EF Core for writes
- ✅ **Migration Path:** Start with mock, migrate to EF Core, optimize with Dapper selectively

---

### 2.5 Scalability & Performance

#### **Horizontal Scaling**
- Stateless API design (no session affinity required)
- Containerized deployment (Docker + Kubernetes)
- Auto-scaling based on CPU/memory/request metrics
- Load balancing (Azure Application Gateway or APIM)

#### **Performance Optimizations**
```csharp
// Caching strategy
[ResponseCache(Duration = 60, VaryByQueryKeys = new[] { "subaccountId" })]
public async Task<ActionResult<SubaccountEligibility>> GetEligibility(string subaccountId)
{
    var cacheKey = $"eligibility:{subaccountId}";
    var cached = await _cache.GetAsync<SubaccountEligibility>(cacheKey);
    if (cached != null) return Ok(cached);
    
    var result = await _service.ValidateEligibilityAsync(subaccountId);
    await _cache.SetAsync(cacheKey, result, TimeSpan.FromMinutes(5));
    return Ok(result);
}

// Database query optimization
public async Task<List<Subaccount>> GetEligibleSubaccountsAsync(List<string> employerIds)
{
    return await _context.Subaccounts
        .AsNoTracking() // Read-only query
        .Include(s => s.FundingFrequencies)
        .Include(s => s.FundingReimbursementPlans)
        .Where(s => s.SubaccountType == "PreFunding" 
                 && s.BankAccountId == BankAccountIds.WellsFargo.RA
                 && (employerIds.Count == 0 || employerIds.Contains(s.HeldFor_ObjectId)))
        .AsSplitQuery() // Prevent cartesian explosion
        .ToListAsync();
}

// Batch processing (chunked)
public async Task<BatchFundingInvoiceResponse> CreateBatchInvoicesAsync(
    CreateBatchFundingInvoicesRequest request)
{
    const int BATCH_SIZE = 100;
    var subaccounts = await GetEligibleSubaccountsAsync(request.EmployerIds);
    var results = new List<FundingInvoiceResult>();
    
    foreach (var batch in subaccounts.Chunk(BATCH_SIZE))
    {
        var tasks = batch.Select(async s => 
            await ProcessSubaccountAsync(s, cancellationToken));
        var batchResults = await Task.WhenAll(tasks);
        results.AddRange(batchResults);
    }
    
    return new BatchFundingInvoiceResponse { Results = results };
}
```

#### **Database Performance**
- Read replicas for query-heavy operations
- Connection pooling (configured in DbContext)
- Index optimization on key columns (SubaccountId, FundingBatchId, Date)
- Query plan analysis and optimization
- Database-level caching (query store)

---

### 2.6 UI Test Client Architecture

A simple Blazor Server web application for manual API testing and contract validation.

#### **Features**
- **Single Invoice Creation:** Form-based interface to test individual invoice generation
- **Batch Operations:** Upload CSV or manually enter employer lists for batch testing
- **Contract Comparison:** Side-by-side view of WCF request/response vs. REST API
- **Response Viewer:** Formatted JSON with syntax highlighting
- **Test Scenarios:** Pre-built test cases (success, validation errors, edge cases)
- **Authentication:** JWT token input or Azure AD integration
- **Performance Metrics:** Response time, payload size, status codes

#### **Implementation**

```csharp
// UITestClient/Pages/SingleInvoice.razor
@page "/single-invoice"
@inject HttpClient ApiClient
@inject ILogger<SingleInvoice> Logger

<h3>Test Single Funding Invoice Creation</h3>

<EditForm Model="@request" OnValidSubmit="@CreateInvoiceAsync">
    <DataAnnotationsValidator />
    <ValidationSummary />
    
    <div class="form-group">
        <label>Subaccount ID:</label>
        <InputText @bind-Value="request.SubaccountId" class="form-control" />
    </div>
    
    <div class="form-group">
        <label>Invoice Amount:</label>
        <InputNumber @bind-Value="request.InvoiceAmount" class="form-control" />
    </div>
    
    <div class="form-group">
        <label>Invoice Date:</label>
        <InputDate @bind-Value="request.InvoiceDate" class="form-control" />
    </div>
    
    <button type="submit" class="btn btn-primary">Create Invoice</button>
    <button type="button" class="btn btn-secondary" @onclick="LoadTestScenario">Load Test Scenario</button>
</EditForm>

@if (response != null)
{
    <div class="mt-4">
        <h4>Response (@responseTime ms)</h4>
        <pre><code>@JsonSerializer.Serialize(response, new JsonSerializerOptions { WriteIndented = true })</code></pre>
    </div>
}

@code {
    private CreateFundingInvoiceRequest request = new();
    private FundingInvoiceResponse? response;
    private long responseTime;
    
    private async Task CreateInvoiceAsync()
    {
        var sw = Stopwatch.StartNew();
        try
        {
            var httpResponse = await ApiClient.PostAsJsonAsync("/api/v1/funding-invoices", request);
            httpResponse.EnsureSuccessStatusCode();
            response = await httpResponse.Content.ReadFromJsonAsync<FundingInvoiceResponse>();
        }
        catch (Exception ex)
        {
            Logger.LogError(ex, "Failed to create invoice");
        }
        finally
        {
            responseTime = sw.ElapsedMilliseconds;
        }
    }
    
    private void LoadTestScenario()
    {
        // Load pre-defined test data
        request = new CreateFundingInvoiceRequest
        {
            SubaccountId = "SUB123456",
            InvoiceAmount = 500.00m,
            InvoiceDate = DateTime.Today
        };
    }
}
```

```csharp
// UITestClient/Pages/ContractComparison.razor
@page "/contract-comparison"
@inject IContractComparisonService ComparisonService

<h3>WCF vs. REST Contract Comparison</h3>

<div class="row">
    <div class="col-md-6">
        <h4>Legacy WCF (XGenerateFundingInvoice)</h4>
        <pre><code>@wcfRequest</code></pre>
        <button @onclick="InvokeLegacyService">Invoke Legacy</button>
        <pre><code>@wcfResponse</code></pre>
    </div>
    
    <div class="col-md-6">
        <h4>New REST API</h4>
        <pre><code>@restRequest</code></pre>
        <button @onclick="InvokeRestApi">Invoke REST</button>
        <pre><code>@restResponse</code></pre>
    </div>
</div>

<div class="mt-4">
    <h4>Comparison Results</h4>
    @if (comparisonResult != null)
    {
        <div class="alert @(comparisonResult.IsMatch ? "alert-success" : "alert-danger")">
            @(comparisonResult.IsMatch ? "✅ Contracts Match" : "❌ Contracts Differ")
        </div>
        
        @if (!comparisonResult.IsMatch)
        {
            <ul>
                @foreach (var diff in comparisonResult.Differences)
                {
                    <li>@diff</li>
                }
            </ul>
        }
    }
</div>

@code {
    private string wcfRequest, wcfResponse, restRequest, restResponse;
    private ContractComparisonResult? comparisonResult;
    
    private async Task InvokeLegacyService()
    {
        // Call legacy WCF service
        var legacyResult = await ComparisonService.InvokeLegacyAsync(wcfRequest);
        wcfResponse = JsonSerializer.Serialize(legacyResult, new JsonSerializerOptions { WriteIndented = true });
    }
    
    private async Task InvokeRestApi()
    {
        // Call new REST API
        var restResult = await ComparisonService.InvokeRestAsync(restRequest);
        restResponse = JsonSerializer.Serialize(restResult, new JsonSerializerOptions { WriteIndented = true });
        
        // Compare results
        comparisonResult = ComparisonService.CompareContracts(wcfResponse, restResponse);
    }
}
```

#### **JavaScript API Client (wwwroot/js/api-client.js)**

```javascript
class RAApiClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.token = token;
    }
    
    async createInvoice(request) {
        const response = await fetch(`${this.baseUrl}/api/v1/funding-invoices`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify(request)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message);
        }
        
        return await response.json();
    }
    
    async createBatchInvoices(request) {
        const response = await fetch(`${this.baseUrl}/api/v1/funding-invoices/batch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify(request)
        });
        
        return await response.json();
    }
}

// Pre-built test scenarios
const testScenarios = {
    success: {
        subaccountId: 'SUB123456',
        invoiceAmount: 500.00,
        invoiceDate: new Date().toISOString().split('T')[0]
    },
    
    validationError: {
        subaccountId: '',  // Missing required field
        invoiceAmount: -100,  // Invalid amount
        invoiceDate: '2020-01-01'  // Past date
    },
    
    largeAmount: {
        subaccountId: 'SUB789012',
        invoiceAmount: 50000.00,
        invoiceDate: new Date().toISOString().split('T')[0]
    }
};
```

**Deployment:** 
- Host alongside API or as separate Azure Web App
- Accessible only in dev/staging environments (not production)
- Requires same authentication as API

---

### 2.7 Contract Verification Framework

**MANDATORY PHASE:** Dedicated testing to ensure 100% WCF contract compatibility.

#### **Verification Strategy**

```csharp
// Product.RA.Api.Tests/ContractVerification/WcfContractComparison.cs
public class WcfContractComparisonTests
{
    private readonly IWcfServiceClient _legacyClient;
    private readonly HttpClient _restClient;
    private readonly IContractValidator _validator;
    
    [Fact]
    public async Task CreateInvoice_RequestContract_MatchesLegacy()
    {
        // Arrange
        var testData = new
        {
            SubaccountId = "SUB123456",
            InvoiceAmount = 500.00m,
            InvoiceDate = DateTime.Today
        };
        
        // Legacy WCF request
        var wcfRequest = new XGenerateFundingInvoice
        {
            SubaccountId = testData.SubaccountId,
            InvoiceAmount = testData.InvoiceAmount,
            InvoiceDate = testData.InvoiceDate
        };
        
        // New REST request
        var restRequest = new CreateFundingInvoiceRequest
        {
            SubaccountId = testData.SubaccountId,
            InvoiceAmount = testData.InvoiceAmount,
            InvoiceDate = testData.InvoiceDate
        };
        
        // Act - Serialize both to JSON
        var wcfJson = JsonSerializer.Serialize(wcfRequest);
        var restJson = JsonSerializer.Serialize(restRequest);
        
        // Assert - Property names and types must match
        var wcfSchema = JSchema.Parse(wcfJson);
        var restSchema = JSchema.Parse(restJson);
        
        _validator.ValidateSchemaCompatibility(wcfSchema, restSchema).Should().BeTrue();
    }
    
    [Theory]
    [MemberData(nameof(GetTestScenarios))]
    public async Task CreateInvoice_ResponseContract_MatchesLegacy(TestScenario scenario)
    {
        // Arrange - Same input to both services
        var wcfRequest = scenario.ToWcfRequest();
        var restRequest = scenario.ToRestRequest();
        
        // Act - Invoke both services
        var wcfResponse = await _legacyClient.GenerateFundingInvoiceAsync(wcfRequest);
        var restResponse = await _restClient.PostAsJsonAsync("/api/v1/funding-invoices", restRequest);
        var restResult = await restResponse.Content.ReadFromJsonAsync<FundingInvoiceResponse>();
        
        // Assert - Compare results
        var comparison = _validator.CompareResponses(wcfResponse, restResult);
        
        comparison.IsMatch.Should().BeTrue($"Scenario: {scenario.Name}");
        comparison.Differences.Should().BeEmpty();
        
        // Validate specific fields
        restResult.SubaccountId.Should().Be(wcfResponse.SubaccountId);
        restResult.Amount.Should().Be(wcfResponse.NewCashInOutId?.Amount ?? 0);
        restResult.Status.Should().Be(MapLegacyResult(wcfResponse.Result));
    }
    
    public static IEnumerable<object[]> GetTestScenarios()
    {
        yield return new object[] { new TestScenario("SuccessfulInvoice", "SUB123", 500m, DateTime.Today) };
        yield return new object[] { new TestScenario("InvoiceNotNeeded", "SUB456", 100m, DateTime.Today) };
        yield return new object[] { new TestScenario("ThirdPartyFunding", "SUB789", 1000m, DateTime.Today) };
        yield return new object[] { new TestScenario("AutoDebitProcessing", "SUB012", 750m, DateTime.Today.AddDays(3)) };
        // ... 50+ test scenarios covering all edge cases
    }
}

// Contract validator implementation
public class ContractValidator : IContractValidator
{
    public ValidationResult ValidateSchemaCompatibility(JSchema legacy, JSchema modern)
    {
        var result = new ValidationResult { IsValid = true };
        
        // Compare required properties
        var legacyRequired = legacy.Required ?? new HashSet<string>();
        var modernRequired = modern.Required ?? new HashSet<string>();
        
        var missingProperties = legacyRequired.Except(modernRequired).ToList();
        if (missingProperties.Any())
        {
            result.IsValid = false;
            result.Errors.Add($"Missing required properties: {string.Join(", ", missingProperties)}");
        }
        
        // Compare property types
        foreach (var prop in legacy.Properties)
        {
            if (modern.Properties.TryGetValue(prop.Key, out var modernProp))
            {
                if (prop.Value.Type != modernProp.Type)
                {
                    result.IsValid = false;
                    result.Errors.Add($"Property '{prop.Key}' type mismatch: {prop.Value.Type} vs {modernProp.Type}");
                }
            }
        }
        
        return result;
    }
    
    public ContractComparisonResult CompareResponses(object legacy, object modern)
    {
        var result = new ContractComparisonResult { IsMatch = true };
        
        var legacyJson = JsonSerializer.Serialize(legacy);
        var modernJson = JsonSerializer.Serialize(modern);
        
        var legacyObj = JObject.Parse(legacyJson);
        var modernObj = JObject.Parse(modernJson);
        
        // Deep comparison of all properties
        CompareJTokens(legacyObj, modernObj, "", result);
        
        return result;
    }
    
    private void CompareJTokens(JToken legacy, JToken modern, string path, ContractComparisonResult result)
    {
        if (legacy.Type != modern.Type)
        {
            result.IsMatch = false;
            result.Differences.Add($"{path}: Type mismatch ({legacy.Type} vs {modern.Type})");
            return;
        }
        
        if (legacy is JObject legacyObj && modern is JObject modernObj)
        {
            foreach (var prop in legacyObj.Properties())
            {
                var modernProp = modernObj.Property(prop.Name);
                if (modernProp == null)
                {
                    result.IsMatch = false;
                    result.Differences.Add($"{path}.{prop.Name}: Missing in modern contract");
                }
                else
                {
                    CompareJTokens(prop.Value, modernProp.Value, $"{path}.{prop.Name}", result);
                }
            }
        }
        else if (legacy is JArray legacyArr && modern is JArray modernArr)
        {
            if (legacyArr.Count != modernArr.Count)
            {
                result.IsMatch = false;
                result.Differences.Add($"{path}: Array length mismatch ({legacyArr.Count} vs {modernArr.Count})");
            }
        }
        else if (!JToken.DeepEquals(legacy, modern))
        {
            result.IsMatch = false;
            result.Differences.Add($"{path}: Value mismatch ({legacy} vs {modern})");
        }
    }
}
```

#### **Automated Contract Testing Suite**

```csharp
// Product.RA.Api.Tests/ContractVerification/ContractCompatibilityTests.cs
[Collection("ContractVerification")]
public class ContractCompatibilityTests
{
    [Fact]
    public void AllRequestModels_MustMatchLegacyContracts()
    {
        // Get all request models from new API
        var requestModels = typeof(CreateFundingInvoiceRequest).Assembly
            .GetTypes()
            .Where(t => t.Name.EndsWith("Request"))
            .ToList();
        
        // Get corresponding legacy contracts
        var legacyContracts = typeof(XGenerateFundingInvoice).Assembly
            .GetTypes()
            .Where(t => t.IsSubclassOf(typeof(HETransaction)))
            .ToList();
        
        // Validate 1:1 mapping
        var mapping = new Dictionary<Type, Type>
        {
            { typeof(CreateFundingInvoiceRequest), typeof(XGenerateFundingInvoice) },
            { typeof(CreateBatchFundingInvoicesRequest), typeof(Updater_CreateRAFundingInvoices) },
            // ... all mappings
        };
        
        foreach (var pair in mapping)
        {
            ValidateContractCompatibility(pair.Key, pair.Value);
        }
    }
    
    [Fact]
    public void AllResponseModels_MustMatchLegacyContracts()
    {
        var responseModels = typeof(FundingInvoiceResponse).Assembly
            .GetTypes()
            .Where(t => t.Name.EndsWith("Response"))
            .ToList();
        
        // Validate response structure matches legacy output properties
        foreach (var responseType in responseModels)
        {
            ValidateResponseStructure(responseType);
        }
    }
    
    [Fact]
    public async Task EndToEndContractValidation_100PercentMatch()
    {
        // Run 1000 test scenarios comparing legacy vs. new
        var scenarios = ContractTestDataGenerator.Generate(1000);
        var mismatches = new List<string>();
        
        foreach (var scenario in scenarios)
        {
            var legacyResult = await InvokeLegacyService(scenario);
            var modernResult = await InvokeModernService(scenario);
            
            if (!AreResultsEquivalent(legacyResult, modernResult))
            {
                mismatches.Add($"Scenario {scenario.Id}: {scenario.Description}");
            }
        }
        
        mismatches.Should().BeEmpty("All scenarios must produce identical results");
    }
}
```

#### **Contract Verification Metrics**
- **Target:** 100% contract compatibility
- **Coverage:** 50+ test scenarios per endpoint
- **Validation:** Request schemas, response schemas, error codes, business logic outcomes
- **CI/CD Gate:** Contract verification tests must pass before deployment

---

### 2.8 Cost Optimization

#### **Compute Costs**
- **Serverless Option:** Azure Container Apps with scale-to-zero
- **Reserved Instances:** For predictable batch workloads
- **Right-sizing:** CPU/memory allocation based on load testing
- **Auto-scaling Policies:** Scale down during off-peak hours

#### **Data Transfer Costs**
- **Response Compression:** Gzip/Brotli for payloads > 1KB
- **Pagination:** Limit result sets (default 100, max 1000)
- **Field Selection:** Allow clients to request specific fields (GraphQL-style or OData)

#### **Storage Costs**
- **Redis Cache:** Only for hot data (TTL-based eviction)
- **Database:** Archive old invoices to cheaper cold storage
- **Logging:** Retain in Application Insights for 30 days, archive to blob storage

---

## 3. Migration Phases

### Phase 1: Foundation & Infrastructure (Week 1-2)

#### **Definition of Ready (DoR)**
- [ ] .NET 8 SDK installed on dev environments
- [ ] Azure DevOps pipeline templates available
- [ ] Database connection strings configured
- [ ] Access to Platform.Classic codebase for reference
- [ ] Paragon ReimbursementPlan service API documentation
- [ ] Contract verification requirements documented

#### **Tasks**
1. **Project Setup**
   - Create `Product.RA.Api` solution (.NET 8 Web API)
   - Configure project structure (Controllers, Services, Repositories, Models, Testing, UITestClient)
   - Set up dependency injection container with repository abstraction
   - Configure Serilog + Application Insights with HIPAA-compliant audit logging

2. **Database Layer (Multi-Implementation)**
   - Create repository interfaces (IFundingInvoiceRepository, IFundingBatchRepository, etc.)
   - Implement mock repositories with in-memory collections
   - Seed mock data (MockDataSeeder with 100+ test scenarios)
   - Create EF Core DbContext for RA domain
   - Define entity configurations (Fluent API) with encrypted fields
   - Generate initial migration
   - Test database connectivity

3. **Infrastructure Code**
   - Implement base repository pattern with UnitOfWork
   - Create unit of work pattern for transaction management
   - Configure FluentValidation
   - Set up health check endpoints
   - Implement audit logging middleware (HIPAA compliance)
   - Configure data encryption middleware for PHI

4. **CI/CD Pipeline**
   - Azure DevOps YAML pipeline for build
   - Unit test execution stage
   - Code coverage requirements (90% minimum)
   - SonarQube integration
   - Contract verification test stage (must pass)

5. **UI Test Client Setup**
   - Create Blazor Server project
   - Basic authentication scaffolding
   - API client wrapper classes

#### **Definition of Done (DoD)**
- [ ] API project builds successfully in CI/CD
- [ ] Health check endpoints return 200 OK
- [ ] Database migrations run without errors (both mock and EF Core)
- [ ] Mock repositories functional with seeded data
- [ ] All unit tests passing (100% pass rate)
- [ ] Code coverage ≥ 90%
- [ ] SonarQube quality gate passed
- [ ] Audit logging middleware functional
- [ ] Documentation updated (README, architecture diagrams, data layer abstraction guide)

#### **TDD Approach**
- RED: Write failing test for DbContext configuration and mock repository
- GREEN: Implement DbContext with entity mappings + mock repository
- REFACTOR: Extract common configurations to base classes, optimize repository abstraction

---

### Phase 2: Core Domain Models & Repositories (Week 3-4)

#### **Definition of Ready (DoR)**
- [ ] Phase 1 complete and deployed to dev environment
- [ ] Legacy code analysis complete (current state documentation)
- [ ] Database schema review completed
- [ ] Domain model design approved
- [ ] Mock data scenarios defined (100+ test cases)

#### **Tasks**
1. **Domain Models**
   - `FundingInvoice` entity (maps to CashInOut)
   - `FundingBatch` entity
   - `SubaccountEligibility` value object
   - `AutoDebitPayment` entity
   - DTOs for requests/responses (ensuring WCF contract compatibility)

2. **Mock Repository Implementation (Complete)**
   - `MockFundingInvoiceRepository` with thread-safe in-memory storage
   - `MockFundingBatchRepository` with batch state management
   - `MockSubaccountRepository` with complex filtering
   - `MockCashInOutRepository`
   - `MockUnitOfWork` with transaction simulation
   - `MockDataSeeder` with 100+ realistic scenarios

3. **EF Core Repository Implementation**
   - `EfFundingInvoiceRepository` + implementation
   - `EfFundingBatchRepository` + implementation
   - `EfSubaccountRepository` + implementation
   - `EfCashInOutRepository` + implementation
   - `EfUnitOfWork` with real transaction management

4. **Database Queries**
   - Port EDM queries to EF Core LINQ
   - Optimize query performance (includes, split queries)
   - Implement query filters (soft delete, tenant isolation)

5. **Optional: Dapper Repository Scaffolding**
   - `DapperQueryRepository` for complex read queries
   - Performance benchmarking (Dapper vs. EF Core)

#### **Definition of Done (DoD)**
- [ ] All domain models have corresponding unit tests
- [ ] Mock repository tests validate in-memory behavior
- [ ] EF Core repository tests use in-memory database
- [ ] Integration tests verify database CRUD operations
- [ ] Query performance benchmarked (< 500ms for complex queries)
- [ ] All tests passing (100% pass rate)
- [ ] Code coverage ≥ 90% for repositories
- [ ] API documentation generated (XML comments)
- [ ] Repository abstraction allows seamless swapping (mock ↔ EF Core ↔ Dapper)

#### **TDD Approach**
- RED: Write test for `GetEligibleSubaccountsAsync()` with specific filters (mock + EF Core)
- GREEN: Implement repository method with EF Core LINQ + mock in-memory logic
- REFACTOR: Extract reusable query specifications, optimize performance

---

### Phase 3: Business Logic Services (Week 5-6)

#### **Definition of Ready (DoR)**
- [ ] Phase 2 complete with all repositories tested
- [ ] External service (Paragon) API contract reviewed
- [ ] Business rule validation scenarios documented
- [ ] Error handling strategy defined

#### **Tasks**
1. **Service Interfaces & Implementation**
   - `IFundingInvoiceService` (core business logic)
   - `IFundingBatchService` (batch operations)
   - `ISubaccountQueryService` (eligibility checks)
   - `IReimbursementPlanAdapter` (external service wrapper)

2. **Business Rule Implementation**
   - Funding frequency matching logic (port from legacy)
   - Peg amount threshold validation
   - Duplicate invoice prevention
   - Third-party funding handling
   - Auto-debit processing with business day calculation
   - Error recovery (batch reopening on failure)

3. **External Service Integration**
   - Implement Polly retry policies (3 retries with exponential backoff)
   - Circuit breaker for Paragon service (open after 5 consecutive failures)
   - Timeout configuration (30 seconds max)
   - Fallback strategies (degrade gracefully)

#### **Definition of Done (DoD)**
- [ ] All service methods have comprehensive unit tests
- [ ] Integration tests cover happy path + error scenarios
- [ ] Polly resilience policies tested (failure injection)
- [ ] Business rules validated against legacy behavior
- [ ] All tests passing (100% pass rate)
- [ ] Code coverage ≥ 90% for services
- [ ] Performance benchmarks documented (throughput, latency)

#### **TDD Approach**
- RED: Write test for `CreateFundingInvoiceAsync()` with all validations
- GREEN: Implement service with business rules
- REFACTOR: Extract validation rules to separate validator classes

---

### Phase 4: REST API Controllers (Week 7-8)

#### **Definition of Ready (DoR)**
- [ ] Phase 3 complete with all services tested
- [ ] API contract design reviewed (OpenAPI spec)
- [ ] Authentication/authorization policies defined
- [ ] Rate limiting thresholds established

#### **Tasks**
1. **Controller Implementation**
   - `FundingInvoiceController` (CRUD + batch operations)
   - `FundingBatchController` (close, reopen)
   - `HealthController` (liveness, readiness probes)

2. **Request/Response Models**
   - `CreateFundingInvoiceRequest` with validation attributes
   - `CreateBatchFundingInvoicesRequest`
   - `FundingInvoiceResponse` with HATEOAS links
   - `BatchFundingInvoiceResponse` with summary metrics

3. **Validation**
   - FluentValidation validators for all request models
   - Model state validation in controllers
   - Custom validation rules (business-specific)

4. **Middleware**
   - Global error handling middleware
   - Request/response logging middleware
   - Authentication middleware (JWT validation)
   - Rate limiting middleware

5. **Swagger Configuration**
   - XML documentation comments
   - Example request/response payloads
   - Authentication scheme configuration

#### **Definition of Done (DoD)**
- [ ] All endpoints have integration tests (WebApplicationFactory)
- [ ] Swagger UI accessible at `/swagger`
- [ ] All HTTP status codes tested (200, 201, 400, 401, 404, 500)
- [ ] Rate limiting functional (429 Too Many Requests)
- [ ] Authentication enforced on protected endpoints
- [ ] All tests passing (100% pass rate)
- [ ] API documentation complete (Swagger + README)
- [ ] Postman collection created for manual testing
- [ ] UI Test Client functional (single invoice + batch + contract comparison pages)
- [ ] Contract verification tests passing (100% compatibility)

#### **TDD Approach**
- RED: Write integration test for `POST /api/v1/funding-invoices` endpoint + contract verification test
- GREEN: Implement controller action with service call + contract mapping
- REFACTOR: Extract common response mapping to helper methods, optimize contract validation

---

### Phase 4a: **MANDATORY Contract Verification** (Week 8.5-9)

**⚠️ CRITICAL PHASE:** This phase is mandatory and must achieve 100% contract compatibility before proceeding.

#### **Definition of Ready (DoR)**
- [ ] Phase 4 complete with all endpoints functional
- [ ] Legacy WCF services accessible for comparison testing
- [ ] Contract verification framework implemented
- [ ] Test data generator with 100+ scenarios ready
- [ ] Automated comparison infrastructure in place

#### **Tasks**
1. **Contract Schema Validation**
   - Extract JSON schemas from legacy WCF contracts
   - Generate JSON schemas from new REST API models
   - Implement automated schema comparison
   - Validate all properties (name, type, required, format)

2. **End-to-End Contract Testing**
   - Create 100+ test scenarios covering all edge cases
   - Invoke legacy WCF service for each scenario
   - Invoke new REST API for same scenario
   - Compare results automatically (deep JSON comparison)
   - Log any discrepancies with detailed diff output

3. **Business Logic Parity Validation**
   - Validate identical behavior for:
     - Funding frequency matching
     - Peg amount threshold checks
     - Duplicate invoice prevention
     - Third-party funding handling
     - Auto-debit processing logic
     - Error recovery (batch reopening)

4. **Error Response Compatibility**
   - Validate error codes match legacy behavior
   - Ensure error messages provide equivalent information
   - Test all validation failure scenarios

5. **Performance Baseline**
   - Compare response times (legacy vs. new)
   - Ensure new API meets or exceeds legacy performance
   - Target: < 500ms for P95, < 1s for P99

#### **Definition of Done (DoD)**
- [ ] **100% contract compatibility achieved** (zero mismatches)
- [ ] All 100+ test scenarios passing
- [ ] Schema validation passing for all request/response models
- [ ] Business logic parity confirmed by SME review
- [ ] Error response compatibility verified
- [ ] Performance meets or exceeds legacy baseline
- [ ] Contract verification report generated and approved
- [ ] Stakeholder sign-off obtained

#### **Test Coverage Requirements**
- **Request Models:** 100% schema match
- **Response Models:** 100% schema match
- **Business Logic:** 100% behavior match
- **Error Handling:** 100% error code/message match
- **Overall Test Scenarios:** 90% automated coverage

#### **Acceptance Criteria**
```csharp
[Fact]
public async Task ContractVerification_MustAchieve100PercentMatch()
{
    // Run all test scenarios
    var results = await _contractVerifier.RunAllScenariosAsync();
    
    // MANDATORY: 100% match rate
    var matchRate = results.MatchCount / (double)results.TotalCount;
    matchRate.Should().Be(1.0, "100% contract compatibility is mandatory");
    
    // No discrepancies allowed
    results.Discrepancies.Should().BeEmpty("All scenarios must produce identical results");
}
```

#### **Failure Protocol**
If contract verification fails (< 100% match):
1. **HALT deployment** - Do not proceed to Phase 5
2. **Root cause analysis** - Identify all discrepancies
3. **Fix implementation** - Adjust new API to match legacy behavior exactly
4. **Re-test** - Run contract verification again
5. **Iterate** - Repeat until 100% match achieved

**NO EXCEPTIONS:** This phase gates all subsequent deployment activities.

---

### Phase 5: Migration of Legacy Services (Week 10-11)

#### **Definition of Ready (DoR)**
- [ ] **Phase 4a complete with 100% contract compatibility achieved**
- [ ] Legacy service behavior fully documented
- [ ] Automated test suite achieving 90% code coverage
- [ ] Rollback strategy defined

#### **Tasks**
1. **Updater_CreateRAFundingInvoices Migration**
   - Create scheduled background job (IHostedService or Azure Function)
   - Port parameter handling (employer list or all)
   - Implement batch processing with error recovery
   - Add status reporting (same logging as legacy)
   - **Automated testing:** 90% coverage including batch edge cases

2. **XGenerateFundingInvoice Migration**
   - Map to `POST /api/v1/funding-invoices` endpoint
   - Ensure contract compatibility (verified in Phase 4a)
   - Validate business rule parity
   - **Automated testing:** 90% coverage including all validation scenarios

3. **Automated Test Suite (90% Coverage Target)**
   - Unit tests: 95% coverage for services and repositories
   - Integration tests: 90% coverage for controllers and end-to-end flows
   - Contract tests: 100% compatibility verification (from Phase 4a)
   - Performance tests: Load testing with realistic workloads
   - **Coverage validation:** Use code coverage tools (Coverlet, ReportGenerator)

4. **Shadow Testing (Automated)**
   - Deploy both legacy and new services in parallel
   - Route 10% of production traffic to new service (read-only initially)
   - Automated comparison of outputs (no manual comparison needed)
   - Log discrepancies automatically to monitoring system
   - **Target:** < 0.1% discrepancy rate over 1 week

5. **Data Integrity Validation**
   - No data migration needed (same database)
   - Verify data integrity post-migration with automated tests
   - Validate referential integrity constraints

#### **Definition of Done (DoD)**
- [ ] Legacy service behavior replicated 100% (verified by automated tests)
- [ ] **Automated test suite achieving 90% code coverage**
- [ ] **Contract tests achieving 100% compatibility (from Phase 4a)**
- [ ] Shadow testing shows < 0.1% discrepancy rate (automated validation)
- [ ] All discrepancies investigated and resolved
- [ ] Performance meets or exceeds legacy (throughput, latency)
- [ ] All tests passing (100% pass rate)
- [ ] User acceptance testing (UAT) completed
- [ ] Deployment runbook created

#### **Code Coverage Breakdown**
| Layer | Target Coverage | Validation Method |
|-------|----------------|-------------------|
| Controllers | 90% | Integration tests |
| Services | 95% | Unit tests + integration tests |
| Repositories | 95% | Unit tests with mock + in-memory DB |
| Domain Models | 90% | Unit tests |
| Validation | 100% | Unit tests for all rules |
| Contract Mapping | 100% | Contract verification tests |
| **Overall** | **90%** | Coverlet + Azure DevOps reporting |

#### **TDD Approach**
- RED: Write comparison test (legacy vs. new output) + achieve 90% coverage
- GREEN: Implement new service to match legacy behavior
- REFACTOR: Optimize for performance and maintainability, maintain coverage

---

### Phase 5a: **Data Layer Transition & Schema Validation** (Week 11.5)

**⚠️ CRITICAL PHASE:** Validates that mock data contracts match production database schema to prevent UI runtime failures.

#### **Definition of Ready (DoR)**
- [ ] Phase 5 complete with 90% test coverage
- [ ] Mock repositories fully functional in integration tests
- [ ] EF Core repositories implemented and unit tested
- [ ] Production database schema documented
- [ ] UI components rely on mock data contracts

#### **Objective**
Ensure seamless transition from mock data layer to live database by validating that:
1. Mock data structure matches database entity schema (property names, types, nullability)
2. Mock data relationships match database foreign key constraints
3. Mock data validation rules match database constraints
4. All UI components continue functioning without code changes

#### **Tasks**

**1. Schema Contract Validation**
```csharp
// Product.RA.Api.Tests/DataLayer/SchemaContractTests.cs
[Fact]
public void MockFundingInvoice_MustMatchDatabaseSchema()
{
    // Arrange - Get mock data shape
    var mockInvoice = _mockRepository.GetByIdAsync("MOCK-123").Result;
    
    // Arrange - Get EF Core entity configuration
    var dbEntityType = _dbContext.Model.FindEntityType(typeof(FundingInvoice));
    
    // Act - Compare schemas
    var validator = new SchemaContractValidator();
    var result = validator.ValidateContract(mockInvoice, dbEntityType);
    
    // Assert - 100% match required
    result.IsValid.Should().BeTrue("Mock data must match database schema exactly");
    result.MissingProperties.Should().BeEmpty("All DB properties must exist in mock");
    result.TypeMismatches.Should().BeEmpty("Property types must match exactly");
    result.NullabilityMismatches.Should().BeEmpty("Nullability must match constraints");
}

[Theory]
[InlineData(typeof(FundingInvoice))]
[InlineData(typeof(FundingBatch))]
[InlineData(typeof(Subaccount))]
[InlineData(typeof(CashInOut))]
[InlineData(typeof(TransferLine))]
public void AllEntities_MockDataMustMatchDatabaseSchema(Type entityType)
{
    // Validate every entity in the domain model
    var mockData = _mockDataSeeder.GetSampleData(entityType);
    var dbSchema = _dbContext.Model.FindEntityType(entityType);
    
    var result = _validator.ValidateContract(mockData, dbSchema);
    result.IsValid.Should().BeTrue($"{entityType.Name} mock data must match DB schema");
}
```

**2. Relationship Integrity Validation**
```csharp
[Fact]
public void MockData_MustRespectForeignKeyConstraints()
{
    // Arrange - Load mock data with relationships
    var invoice = _mockRepository.GetByIdAsync("MOCK-123").Result;
    
    // Act - Validate foreign key references exist
    var validator = new RelationshipValidator(_dbContext);
    var result = validator.ValidateForeignKeys(invoice);
    
    // Assert
    result.IsValid.Should().BeTrue("All FK references must be valid");
    result.OrphanedReferences.Should().BeEmpty("No orphaned FKs allowed");
}

[Fact]
public void MockSubaccount_MustHaveValidEmployerReference()
{
    // Validate that mock subaccount's HeldFor_ObjectId exists in Employer table
    var subaccount = _mockSubaccountRepo.GetByIdAsync("SUB123").Result;
    var employerExists = _dbContext.Employers.Any(e => e.EmployerId == subaccount.HeldFor_ObjectId);
    
    employerExists.Should().BeTrue("Subaccount must reference valid employer in DB");
}
```

**3. Type Safety Validation**
```csharp
[Fact]
public void MockData_PropertyTypes_MustMatchDatabaseTypes()
{
    // Validate that decimal in mock matches decimal(18,2) in DB
    // Validate that string in mock matches nvarchar(50) in DB
    // Validate that DateTime in mock matches datetime2 in DB
    
    var typeValidator = new TypeSafetyValidator();
    var entities = new[] 
    { 
        typeof(FundingInvoice), 
        typeof(FundingBatch), 
        typeof(Subaccount) 
    };
    
    foreach (var entityType in entities)
    {
        var mockInstance = _mockDataSeeder.GetSampleData(entityType);
        var dbSchema = _dbContext.Model.FindEntityType(entityType);
        
        var result = typeValidator.ValidateTypes(mockInstance, dbSchema);
        
        result.TypeMismatches.Should().BeEmpty(
            $"{entityType.Name}: Property types must match DB exactly");
        result.PrecisionMismatches.Should().BeEmpty(
            $"{entityType.Name}: Decimal precision must match DB constraints");
        result.LengthMismatches.Should().BeEmpty(
            $"{entityType.Name}: String lengths must not exceed DB max length");
    }
}
```

**4. Nullability Contract Validation**
```csharp
[Fact]
public void MockData_Nullability_MustMatchDatabaseConstraints()
{
    // Validate that required fields in DB are never null in mock
    // Validate that nullable fields in DB can be null in mock
    
    var entities = _dbContext.Model.GetEntityTypes();
    
    foreach (var entityType in entities)
    {
        var mockInstance = _mockDataSeeder.GetSampleData(entityType.ClrType);
        
        foreach (var property in entityType.GetProperties())
        {
            var mockValue = property.PropertyInfo.GetValue(mockInstance);
            var isRequired = !property.IsNullable;
            
            if (isRequired)
            {
                mockValue.Should().NotBeNull(
                    $"{entityType.Name}.{property.Name} is required in DB, cannot be null in mock");
            }
        }
    }
}
```

**5. Integration Test Migration (Mock → EF Core)**
```csharp
// Run all integration tests twice: once with Mock, once with EF Core
[Collection("DataLayerIntegration")]
public class FundingInvoiceIntegrationTests
{
    [Theory]
    [InlineData("Mock")]
    [InlineData("EFCore")]
    public async Task CreateInvoice_WithValidData_SucceedsInBothDataLayers(string dataLayerMode)
    {
        // Arrange
        var factory = new WebApplicationFactory<Program>()
            .WithWebHostBuilder(builder =>
            {
                builder.ConfigureAppConfiguration((context, config) =>
                {
                    config.AddInMemoryCollection(new Dictionary<string, string>
                    {
                        { "DataLayer:Mode", dataLayerMode }
                    });
                });
            });
        
        var client = factory.CreateClient();
        var request = new CreateFundingInvoiceRequest
        {
            SubaccountId = "SUB123",
            InvoiceAmount = 500m,
            InvoiceDate = DateTime.Today
        };
        
        // Act
        var response = await client.PostAsJsonAsync("/api/v1/funding-invoices", request);
        
        // Assert - Same result regardless of data layer
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var invoice = await response.Content.ReadFromJsonAsync<FundingInvoiceResponse>();
        invoice.Should().NotBeNull();
        invoice.Amount.Should().Be(500m);
    }
}
```

**6. UI Component Contract Testing**
```csharp
// Ensure UI components get expected data shape from both layers
[Fact]
public async Task GetInvoice_ResponseShape_IdenticalInMockAndEFCore()
{
    // Arrange
    var mockClient = CreateClientWithDataLayer("Mock");
    var efCoreClient = CreateClientWithDataLayer("EFCore");
    var invoiceId = await CreateTestInvoiceAsync();
    
    // Act
    var mockResponse = await mockClient.GetAsync($"/api/v1/funding-invoices/{invoiceId}");
    var efCoreResponse = await efCoreClient.GetAsync($"/api/v1/funding-invoices/{invoiceId}");
    
    var mockJson = await mockResponse.Content.ReadAsStringAsync();
    var efCoreJson = await efCoreResponse.Content.ReadAsStringAsync();
    
    // Assert - JSON shape must be identical
    var mockObj = JObject.Parse(mockJson);
    var efCoreObj = JObject.Parse(efCoreJson);
    
    JToken.DeepEquals(mockObj, efCoreObj).Should().BeTrue(
        "UI components expect identical JSON structure from both data layers");
    
    // Validate property existence
    var mockProperties = mockObj.Properties().Select(p => p.Name).ToHashSet();
    var efCoreProperties = efCoreObj.Properties().Select(p => p.Name).ToHashSet();
    
    mockProperties.Should().BeEquivalentTo(efCoreProperties,
        "Both data layers must return same property names");
}
```

**7. Data Layer Swap Deployment**
```csharp
// Gradual rollout strategy
public class DataLayerToggleService
{
    private readonly IConfiguration _configuration;
    
    public async Task<IUnitOfWork> GetUnitOfWorkAsync(string userId)
    {
        // Feature flag based rollout
        var rolloutPercentage = _configuration.GetValue<int>("DataLayer:EFCoreRolloutPercentage");
        var userHash = GetUserHash(userId);
        
        if (userHash % 100 < rolloutPercentage)
        {
            return _efCoreUnitOfWork; // Gradual rollout to EF Core
        }
        
        return _mockUnitOfWork; // Fallback to mock
    }
}
```

#### **Validation Tools**

**Schema Contract Validator Implementation:**
```csharp
public class SchemaContractValidator
{
    public ValidationResult ValidateContract(object mockInstance, IEntityType dbEntityType)
    {
        var result = new ValidationResult { IsValid = true };
        var mockType = mockInstance.GetType();
        
        // Check all DB properties exist in mock
        foreach (var dbProperty in dbEntityType.GetProperties())
        {
            var mockProperty = mockType.GetProperty(dbProperty.Name);
            
            if (mockProperty == null)
            {
                result.IsValid = false;
                result.MissingProperties.Add(dbProperty.Name);
                continue;
            }
            
            // Validate type compatibility
            if (!AreTypesCompatible(mockProperty.PropertyType, dbProperty.ClrType))
            {
                result.IsValid = false;
                result.TypeMismatches.Add(new TypeMismatch
                {
                    PropertyName = dbProperty.Name,
                    MockType = mockProperty.PropertyType,
                    DatabaseType = dbProperty.ClrType
                });
            }
            
            // Validate nullability
            var dbNullable = dbProperty.IsNullable;
            var mockNullable = Nullable.GetUnderlyingType(mockProperty.PropertyType) != null;
            
            if (dbNullable != mockNullable)
            {
                result.IsValid = false;
                result.NullabilityMismatches.Add(new NullabilityMismatch
                {
                    PropertyName = dbProperty.Name,
                    DatabaseNullable = dbNullable,
                    MockNullable = mockNullable
                });
            }
        }
        
        return result;
    }
}

public class ValidationResult
{
    public bool IsValid { get; set; }
    public List<string> MissingProperties { get; set; } = new();
    public List<TypeMismatch> TypeMismatches { get; set; } = new();
    public List<NullabilityMismatch> NullabilityMismatches { get; set; } = new();
}
```

#### **Definition of Done (DoD)**
- [ ] **100% schema contract validation passing** (all entities)
- [ ] All mock entity properties match database schema (name, type, nullability)
- [ ] All mock entity relationships respect foreign key constraints
- [ ] All integration tests pass with both Mock and EF Core data layers
- [ ] UI component contract tests confirm identical JSON shapes
- [ ] Type safety validation passing (decimals, strings, dates match DB constraints)
- [ ] Nullability validation passing (required vs. optional fields)
- [ ] Feature flag rollout strategy implemented (0% → 10% → 50% → 100%)
- [ ] Rollback plan tested (EF Core → Mock fallback)
- [ ] Performance baseline established (EF Core meets mock performance)

#### **Acceptance Criteria**
```csharp
[Fact]
public void DataLayerTransition_MustPassAllValidations()
{
    var results = new[]
    {
        _schemaValidator.ValidateAllEntities(),
        _relationshipValidator.ValidateAllRelationships(),
        _typeValidator.ValidateAllTypes(),
        _nullabilityValidator.ValidateAllNullability(),
        _integrationTester.RunAllTestsWithBothLayers()
    };
    
    results.All(r => r.IsValid).Should().BeTrue(
        "All validations must pass before swapping data layer in production");
}
```

#### **Rollout Strategy**

**Week 11.5 - Day 1-2:** Schema Validation
- Run all schema contract tests
- Fix any mock data mismatches
- Validate 100% compatibility

**Week 11.5 - Day 3:** Integration Test Dual Run
- Run all integration tests with Mock layer → 100% pass
- Run all integration tests with EF Core layer → 100% pass
- Compare results → 100% identical behavior

**Week 11.5 - Day 4:** Staging Deployment
- Deploy to staging with feature flag (EF Core 0%)
- Smoke test with Mock layer
- Enable EF Core for 10% of test users
- Monitor for errors, performance degradation

**Week 11.5 - Day 5:** Production Rollout
- Deploy to production with feature flag (EF Core 0%)
- Gradual rollout: 0% → 10% → 25% → 50% → 100% (over 24 hours)
- Monitor: error rates, latency, database load
- Rollback trigger: error rate > 0.1% or P95 latency > 500ms

#### **Risk Mitigation**

| Risk | Mitigation |
|------|------------|
| Schema drift during development | Automated nightly schema validation tests |
| UI breaks due to missing properties | 100% contract validation before deployment |
| Performance degradation | Baseline performance tests, canary deployment |
| Database connection failures | Circuit breaker, fallback to mock (read-only) |
| Data integrity issues | Foreign key validation, constraint checking |

#### **Failure Protocol**
If schema validation fails (< 100% match):
1. **HALT deployment** - Do not proceed to production rollout
2. **Root cause analysis** - Identify schema mismatches
3. **Fix mock data** - Update mock repositories to match DB schema
4. **Re-validate** - Run all schema tests again
5. **Iterate** - Repeat until 100% validation success

**NO EXCEPTIONS:** This phase gates production data layer swap.

---

### Phase 6: Deployment & Monitoring (Week 12-13)

#### **Definition of Ready (DoR)**
- [ ] Phase 5 complete with UAT sign-off
- [ ] Production environment provisioned (Azure resources)
- [ ] Monitoring dashboards configured (Application Insights)
- [ ] Runbook reviewed by operations team

#### **Tasks**
1. **Deployment**
   - Deploy to staging environment (smoke tests)
   - Blue-green deployment to production
   - Traffic split (10% → 50% → 100% over 3 days)

2. **Monitoring**
   - Application Insights dashboards (latency, errors, throughput)
   - Alerts for critical metrics (error rate > 1%, latency > 2s)
   - Log analytics queries (top errors, slow queries)

3. **Performance Tuning**
   - Load testing (simulated production traffic)
   - Identify bottlenecks (database queries, external calls)
   - Optimize hot paths (caching, query optimization)

4. **Documentation**
   - API user guide (getting started, authentication, examples)
   - Operations manual (deployment, troubleshooting, runbook)
   - Architecture decision records (ADRs)

#### **Definition of Done (DoD)**
- [ ] API deployed to production with zero downtime
- [ ] Monitoring alerts configured and tested
- [ ] Load testing shows acceptable performance (1000 req/s sustained)
- [ ] No critical bugs reported in first 48 hours
- [ ] Legacy services decommissioned successfully
- [ ] All documentation complete and published
- [ ] Retrospective completed with lessons learned

#### **Success Metrics**
- **Availability:** 99.9% uptime
- **Performance:** P95 latency < 500ms, P99 < 1s
- **Error Rate:** < 0.1%
- **Cost:** 20% reduction vs. legacy (VM → containerized)

---

## 4. Contract Mapping (WCF → REST)

### 4.1 XGenerateFundingInvoice Migration

#### **Legacy WCF Contract**
```csharp
public partial class XGenerateFundingInvoice : HETransaction
{
    public string SubaccountId { get; set; }
    public decimal InvoiceAmount { get; set; }
    public DateTime InvoiceDate { get; set; }
    public string Result { get; set; } // "invoice created", "invoice not needed"
    public CashInOut NewCashInOutId { get; set; }
}
```

#### **New REST API Contract**
```csharp
// POST /api/v1/funding-invoices
public class CreateFundingInvoiceRequest
{
    [Required]
    public string SubaccountId { get; set; }
    
    [Range(0.01, double.MaxValue)]
    public decimal InvoiceAmount { get; set; }
    
    [Required]
    [FutureOrTodayDate]
    public DateTime InvoiceDate { get; set; }
}

public class FundingInvoiceResponse
{
    public string InvoiceId { get; set; }
    public string SubaccountId { get; set; }
    public decimal Amount { get; set; }
    public DateTime InvoiceDate { get; set; }
    public string Status { get; set; } // "Created", "NotNeeded", "Error"
    public string Message { get; set; }
    public CashInOutDetails CashInOut { get; set; }
    public AutoDebitDetails AutoDebit { get; set; }
}
```

### 4.2 Updater_CreateRAFundingInvoices Migration

#### **Legacy Service Contract**
```csharp
[ServiceParameter("Employers", typeof(string), "List of Employers...")]
public class Updater_CreateRAFundingInvoices : SimpleServiceBase
{
    public override void Run()
    {
        // Query eligible subaccounts
        // Create invoices in batch
        // Error recovery
    }
}
```

#### **New REST API Contract (Batch)**
```csharp
// POST /api/v1/funding-invoices/batch
public class CreateBatchFundingInvoicesRequest
{
    public List<string> EmployerIds { get; set; } // Empty = all employers
    public DateTime? InvoiceDate { get; set; } // Default = today
    public bool DryRun { get; set; } // Preview without creating
}

public class BatchFundingInvoiceResponse
{
    public int TotalProcessed { get; set; }
    public int SuccessCount { get; set; }
    public int FailureCount { get; set; }
    public int SkippedCount { get; set; }
    public List<FundingInvoiceResult> Results { get; set; }
    public BatchSummary Summary { get; set; }
}

public class FundingInvoiceResult
{
    public string SubaccountId { get; set; }
    public string EmployerId { get; set; }
    public bool Success { get; set; }
    public string Status { get; set; } // "Created", "Skipped", "Error"
    public string Message { get; set; }
    public string InvoiceId { get; set; }
    public decimal? InvoiceAmount { get; set; }
}
```

---

## 5. Testing Strategy

### 5.1 Unit Testing (95%+ Coverage for Core Logic)

#### **Test Framework**
- xUnit (test framework)
- FluentAssertions (assertions)
- Moq (mocking)
- AutoFixture (test data generation)
- Coverlet (code coverage)
- ReportGenerator (coverage reports)

#### **Test Categories**
```csharp
// Domain logic tests (using mock repositories)
[Fact]
public async Task CreateFundingInvoice_WhenPegAmountExceeded_CreatesInvoice()
{
    // Arrange - Use mock repository for fast, isolated testing
    var mockRepo = new MockFundingInvoiceRepository();
    var service = new FundingInvoiceService(mockRepo, ...);
    
    var subaccount = _fixture.Build<Subaccount>()
        .With(s => s.CachedBalance, 100m)
        .With(s => s.FundingFrequencies, new List<FundingFrequency> 
        { 
            new() { PegAmount = 500m, Matches = () => true } 
        })
        .Create();
    
    // Act
    var result = await service.CreateFundingInvoiceAsync(subaccount, 400m, DateTime.Today);
    
    // Assert
    result.Should().NotBeNull();
    result.Status.Should().Be("Created");
    result.Amount.Should().Be(400m);
}

// Validation tests
[Theory]
[InlineData(-100)] // Negative amount
[InlineData(0)]    // Zero amount
public async Task CreateFundingInvoice_WithInvalidAmount_ThrowsValidationException(decimal amount)
{
    // Arrange
    var request = new CreateFundingInvoiceRequest 
    { 
        SubaccountId = "SUB123", 
        InvoiceAmount = amount 
    };
    
    var validator = new CreateFundingInvoiceValidator();
    
    // Act
    var result = await validator.ValidateAsync(request);
    
    // Assert
    result.IsValid.Should().BeFalse();
    result.Errors.Should().ContainSingle(e => e.PropertyName == nameof(request.InvoiceAmount));
}

// Repository tests (in-memory database for EF Core, mock for unit tests)
[Fact]
public async Task GetEligibleSubaccounts_WithEmployerFilter_ReturnsFilteredResults()
{
    // Arrange - Use mock repository
    var mockRepo = new MockSubaccountRepository();
    await SeedMockDataAsync(mockRepo);
    
    // Act
    var result = await mockRepo.GetEligibleSubaccountsAsync(new[] { "EMP001" });
    
    // Assert
    result.Should().HaveCount(2);
    result.Should().OnlyContain(s => s.HeldFor_ObjectId == "EMP001");
}

// Contract mapping tests
[Fact]
public void WcfRequest_ToRestRequest_MapsAllProperties()
{
    // Arrange
    var wcfRequest = new XGenerateFundingInvoice
    {
        SubaccountId = "SUB123",
        InvoiceAmount = 500m,
        InvoiceDate = DateTime.Today
    };
    
    // Act
    var restRequest = wcfRequest.ToRestRequest();
    
    // Assert
    restRequest.SubaccountId.Should().Be(wcfRequest.SubaccountId);
    restRequest.InvoiceAmount.Should().Be(wcfRequest.InvoiceAmount);
    restRequest.InvoiceDate.Should().Be(wcfRequest.InvoiceDate);
}
```

**Coverage Targets:**
- Services: 95%
- Repositories: 95%
- Domain Models: 90%
- Validators: 100%
- Contract Mappers: 100%
- Controllers: 85% (integration tests cover remainder)

### 5.2 Integration Testing (90%+ End-to-End Coverage)

#### **Test Approach**
- WebApplicationFactory for API tests
- TestContainers for database (SQL Server container)
- WireMock for external service mocking (Paragon)

```csharp
public class FundingInvoiceControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    
    [Fact]
    public async Task CreateFundingInvoice_WithValidRequest_Returns201Created()
    {
        // Arrange
        var request = new CreateFundingInvoiceRequest
        {
            SubaccountId = "SUB123",
            InvoiceAmount = 500m,
            InvoiceDate = DateTime.Today
        };
        
        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/funding-invoices", request);
        
        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var invoice = await response.Content.ReadFromJsonAsync<FundingInvoiceResponse>();
        invoice.Should().NotBeNull();
        invoice.InvoiceId.Should().NotBeNullOrEmpty();
    }
}
```

### 5.3 Shadow Testing (Side-by-Side)

#### **Comparison Framework**
```csharp
public class ShadowTestingService : IHostedService
{
    public async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            var testCase = await GetNextTestCaseAsync();
            
            // Call legacy service
            var legacyResult = await _legacyService.CreateInvoiceAsync(testCase);
            
            // Call new service
            var newResult = await _newService.CreateInvoiceAsync(testCase);
            
            // Compare results
            var discrepancies = CompareResults(legacyResult, newResult);
            if (discrepancies.Any())
            {
                await LogDiscrepanciesAsync(testCase, discrepancies);
            }
            
            await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
        }
    }
}
```

### 5.4 Load Testing

#### **Tool:** Azure Load Testing or k6

```javascript
// k6 load test script
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '5m', target: 100 },  // Ramp up to 100 users
        { duration: '10m', target: 100 }, // Stay at 100 users
        { duration: '5m', target: 0 },    // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
        http_req_failed: ['rate<0.01'], // Error rate < 1%
    },
};

export default function () {
    let payload = JSON.stringify({
        subaccountId: 'SUB' + Math.floor(Math.random() * 1000),
        invoiceAmount: 500,
        invoiceDate: new Date().toISOString(),
    });
    
    let res = http.post('https://api.healthequity.com/api/v1/funding-invoices', payload, {
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + __ENV.JWT_TOKEN
        },
    });
    
    check(res, {
        'status is 201': (r) => r.status === 201,
        'response time < 500ms': (r) => r.timings.duration < 500,
    });
    
    sleep(1);
}
```

---

## 6. Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Business Logic Discrepancies** | Medium | High | Shadow testing for 2 weeks; 100% output comparison |
| **Performance Degradation** | Low | High | Load testing in staging; performance benchmarks |
| **External Service Failures** (Paragon) | Medium | Medium | Polly circuit breaker; retry policies; fallback logic |
| **Database Migration Issues** | Low | High | Use same database; no schema changes initially |
| **Authentication/Authorization Gaps** | Medium | High | Security audit; penetration testing |
| **Deployment Downtime** | Low | Medium | Blue-green deployment; canary releases |
| **Cost Overruns** | Low | Medium | Budget alerts; cost optimization reviews |
| **Missing Business Rules** | Medium | High | Comprehensive code review; SME validation |

---

## 7. Rollback Plan

### 7.1 Triggers
- Error rate > 5% for 10 consecutive minutes
- P95 latency > 2 seconds
- Critical business process failures

### 7.2 Procedure
1. **Immediate:** Redirect traffic to legacy services (100%)
2. **Investigation:** Review Application Insights logs and traces
3. **Fix:** Apply hotfix if possible (within 2 hours)
4. **Re-deploy:** After testing fix in staging
5. **Post-Mortem:** Document root cause and preventive measures

---

## 8. Success Criteria

### 8.1 Functional
- [ ] All legacy service functionality replicated (100%)
- [ ] **100% contract compatibility achieved (MANDATORY - Phase 4a)**
- [ ] All business rules validated by SMEs
- [ ] UAT sign-off from stakeholders
- [ ] Mock layer functional and swappable with EF Core/Dapper
- [ ] UI Test Client operational for manual testing

### 8.2 Testing & Quality
- [ ] **90% automated test coverage (unit + integration + contract)**
- [ ] **100% WCF contract verification (request + response schemas)**
- [ ] All unit tests passing (100% pass rate)
- [ ] All integration tests passing (100% pass rate)
- [ ] All contract verification tests passing (100% match rate)
- [ ] Shadow testing discrepancy rate < 0.1%
- [ ] Code coverage breakdown:
  - Services: ≥ 95%
  - Repositories: ≥ 95%
  - Controllers: ≥ 85%
  - Domain Models: ≥ 90%
  - Validators: 100%
  - Contract Mappers: 100%

### 8.3 Non-Functional
- [ ] API availability > 99.9%
- [ ] P95 latency < 500ms
- [ ] P99 latency < 1000ms
- [ ] Error rate < 0.1%
- [ ] Security scan: Zero critical vulnerabilities
- [ ] HIPAA/SOC2 compliance verified (audit logging, encryption, access controls)

### 8.4 Operational
- [ ] Monitoring dashboards operational
- [ ] Alerts configured and tested
- [ ] Runbook complete and validated
- [ ] Team trained on new system
- [ ] UI Test Client accessible in dev/staging

### 8.5 Cost
- [ ] 20% reduction in infrastructure costs (VM → containers)
- [ ] No increase in database costs
- [ ] Monitoring costs within budget

### 8.6 Contract Compatibility (MANDATORY)
- [ ] **Request schemas: 100% match with legacy WCF**
- [ ] **Response schemas: 100% match with legacy WCF**
- [ ] **Business logic: 100% behavioral equivalence**
- [ ] **Error handling: 100% error code/message compatibility**
- [ ] **100+ test scenarios all passing**
- [ ] **Zero discrepancies in contract verification report**

### 8.7 Data Layer Schema Validation (MANDATORY)
- [ ] **Mock entity schemas: 100% match with database schema**
- [ ] **Property names: Exact match between mock and DB**
- [ ] **Property types: Exact match (string, int, decimal, DateTime, etc.)**
- [ ] **Nullability: Exact match (required vs. optional fields)**
- [ ] **Foreign key relationships: All mock references valid in DB**
- [ ] **Type safety: Decimal precision, string lengths match DB constraints**
- [ ] **Integration tests: 100% pass rate with both Mock and EF Core**
- [ ] **UI component tests: Identical JSON shapes from both data layers**
- [ ] **Feature flag rollout: Tested and functional (0% → 100%)**

---

## 9. Timeline & Milestones

| Milestone | Target Date | Dependencies | Deliverable |
|-----------|-------------|--------------|-------------|
| **Phase 1 Complete** | Week 2 | None | Infrastructure + CI/CD + Mock Layer |
| **Phase 2 Complete** | Week 4 | Phase 1 | Repositories (Mock + EF Core) + Domain Models |
| **Phase 3 Complete** | Week 6 | Phase 2 | Business Logic Services |
| **Phase 4 Complete** | Week 8 | Phase 3 | REST API Endpoints + UI Test Client |
| **Phase 4a Complete** | Week 9 | Phase 4 | **MANDATORY: 100% Contract Verification (WCF)** |
| **Phase 5 Complete** | Week 11 | Phase 4a | Legacy Services Migrated + 90% Test Coverage |
| **Phase 5a Complete** | Week 11.5 | Phase 5 | **Data Layer Transition + Schema Validation** |
| **Production Deployment** | Week 13 | Phase 5a + UAT | Live in Production with EF Core |

**Total Duration:** 13 weeks (~3 months)

**Key Milestones:**
- Week 2: Mock layer functional, fast unit tests running
- Week 4: Can swap between mock/EF Core repositories seamlessly
- Week 6: Business logic complete with 95% unit test coverage
- Week 8: API endpoints functional, UI test client deployed
- Week 9: **100% WCF contract compatibility achieved (MANDATORY GATE)**
- Week 11: 90% automated test coverage, shadow testing complete
- Week 11.5: **100% schema validation complete, mock data matches DB schema**
- Week 13: Production deployment with EF Core data layer (0% → 100% rollout)

**Critical Path:**
Phase 1 → Phase 2 → Phase 3 → Phase 4 → **Phase 4a** (BLOCKER) → Phase 5 → **Phase 5a** (BLOCKER) → Phase 6

**Risk Buffer:** 
- 1 week for contract compatibility issues (Phase 4a)
- 0.5 week for schema validation fixes (Phase 5a)

**Deployment Gates:**
1. **Phase 4a:** 100% WCF contract compatibility - MUST PASS
2. **Phase 5a:** 100% schema validation - MUST PASS

---

## 10. Post-Migration Activities

### 10.1 Decommissioning Legacy Services (Week 13-14)
- [ ] Archive legacy code to source control (tag: `legacy-final`)
- [ ] Remove legacy services from deployment pipelines
- [ ] Update documentation to reference new APIs only
- [ ] Notify consumers of deprecation timeline

### 10.2 Continuous Improvement (Ongoing)
- [ ] Monitor performance metrics (weekly review)
- [ ] Collect user feedback (monthly survey)
- [ ] Optimize based on production data (quarterly review)
- [ ] Update documentation (as needed)

### 10.3 Knowledge Transfer (Week 15)
- [ ] Conduct training sessions for support team
- [ ] Create video tutorials for API usage
- [ ] Publish internal blog post (lessons learned)
- [ ] Update team onboarding materials

---

## Appendix A: Key Dependencies

### External Services
- **Paragon ReimbursementPlan Service:** `IReimbursementPlanService`
  - `GetFundingOptionsAndPaymentAuthorizationsAsync()`
  - `AddBenefitGroupCashInOutsBySubaccountAsync()`

### Database Tables
- Subaccount, FundingBatch, FundingBatchInvoice, FundingFrequency
- CashInOut, TransferLine, Payment, PaymentAuthorization
- Employer, ReimbursementPlan, BenefitGroupReimbursementPlan

### Legacy Transactions (Internal)
- `QFindRAPlansBySubaccount`
- `XCloseFundingBatch`
- `XUpdateFundingBatch`
- `XAddCashInOut`
- `XAddPayment`
- `XAddRABenefitGroupCashInOutsBySubaccountIds`

---

## Appendix B: Sample API Requests

### Create Single Invoice
```http
POST /api/v1/funding-invoices HTTP/1.1
Host: api.healthequity.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "subaccountId": "SUB123456",
  "invoiceAmount": 500.00,
  "invoiceDate": "2025-12-15"
}
```

**Response:**
```json
{
  "invoiceId": "INV789012",
  "subaccountId": "SUB123456",
  "amount": 500.00,
  "invoiceDate": "2025-12-15",
  "status": "Created",
  "message": "Invoice created successfully",
  "cashInOut": {
    "cashInOutId": "CIO345678",
    "description": "RA Prefunding for Benefits Group A - Plan XYZ",
    "amount": 500.00,
    "date": "2025-12-15"
  },
  "autoDebit": {
    "paymentId": "PAY901234",
    "amount": 500.00,
    "effectiveDate": "2025-12-17",
    "status": "Requested"
  }
}
```

### Create Batch Invoices
```http
POST /api/v1/funding-invoices/batch HTTP/1.1
Host: api.healthequity.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "employerIds": ["EMP001", "EMP002"],
  "invoiceDate": "2025-12-15",
  "dryRun": false
}
```

**Response:**
```json
{
  "totalProcessed": 150,
  "successCount": 145,
  "failureCount": 3,
  "skippedCount": 2,
  "results": [
    {
      "subaccountId": "SUB123",
      "employerId": "EMP001",
      "success": true,
      "status": "Created",
      "message": "Invoice created",
      "invoiceId": "INV789",
      "invoiceAmount": 500.00
    },
    {
      "subaccountId": "SUB456",
      "employerId": "EMP001",
      "success": false,
      "status": "Error",
      "message": "No open funding batch found"
    }
  ],
  "summary": {
    "totalInvoiceAmount": 72500.00,
    "averageInvoiceAmount": 500.00,
    "processingTimeMs": 12345
  }
}
```

---

## Appendix C: Database Schema (Key Tables)

### Subaccount (Simplified)
```sql
CREATE TABLE Subaccount (
    SubaccountId NVARCHAR(50) PRIMARY KEY,
    SubaccountType NVARCHAR(50), -- 'PreFunding'
    BankAccount NVARCHAR(50),    -- BankAccountIds.WellsFargo.RA
    HeldFor_ObjectId NVARCHAR(50), -- EmployerId
    HeldFor_Type NVARCHAR(50),
    CachedBalance DECIMAL(18,2),
    AccountId NVARCHAR(50)
);

CREATE INDEX IX_Subaccount_Type_Bank ON Subaccount(SubaccountType, BankAccount);
CREATE INDEX IX_Subaccount_HeldFor ON Subaccount(HeldFor_ObjectId);
```

### FundingBatch (Simplified)
```sql
CREATE TABLE FundingBatch (
    FundingBatchId NVARCHAR(50) PRIMARY KEY,
    FundingSubaccount NVARCHAR(50) FOREIGN KEY REFERENCES Subaccount(SubaccountId),
    Status NVARCHAR(20), -- 'Open', 'Pending', 'Reopened', 'Closed'
    CreatedAt DATETIME2,
    UpdatedAt DATETIME2
);

CREATE INDEX IX_FundingBatch_Status ON FundingBatch(Status);
CREATE INDEX IX_FundingBatch_Subaccount ON FundingBatch(FundingSubaccount);
```

### CashInOut (Invoice)
```sql
CREATE TABLE CashInOut (
    CashInOutId NVARCHAR(50) PRIMARY KEY,
    Category NVARCHAR(50), -- 'RAFunding'
    Amount DECIMAL(18,2),
    Date DATE,
    Description NVARCHAR(500),
    Entity_ObjectId NVARCHAR(50), -- EmployerId or PartnerId
    Entity_Type NVARCHAR(50),
    PrefundAmount DECIMAL(18,2),
    TotalLiabilityAmount DECIMAL(18,2),
    CreatedAt DATETIME2
);

CREATE INDEX IX_CashInOut_Date_Category ON CashInOut(Date, Category);
CREATE INDEX IX_CashInOut_Entity ON CashInOut(Entity_ObjectId, Entity_Type);
```

---

## Appendix D: Architecture Decision Records (ADRs)

### ADR-001: Use EF Core instead of Dapper
**Decision:** Use Entity Framework Core 8 for data access  
**Context:** Need ORM for rapid development with LINQ support  
**Alternatives:** Dapper (micro-ORM), ADO.NET (raw SQL)  
**Rationale:** EF Core provides LINQ support, change tracking, migrations, and is well-supported in .NET 8  
**Consequences:** Slightly slower than Dapper for some queries, but acceptable for our use case  

### ADR-002: Use FluentValidation for input validation
**Decision:** Use FluentValidation library for request validation  
**Context:** Need declarative, testable validation logic  
**Alternatives:** Data annotations, manual validation  
**Rationale:** FluentValidation separates validation from models, highly testable, reusable  
**Consequences:** Additional dependency, but industry standard  

### ADR-003: Use Polly for resilience
**Decision:** Use Polly for retry policies and circuit breakers  
**Context:** Need fault tolerance for external service calls (Paragon)  
**Alternatives:** Manual retry logic, custom resilience library  
**Rationale:** Polly is battle-tested, feature-rich, and integrates well with ASP.NET Core  
**Consequences:** Minimal - widely adopted pattern  

### ADR-004: Use JWT Bearer Tokens for authentication
**Decision:** Use JWT tokens with role-based authorization  
**Context:** Need stateless, scalable authentication for REST API  
**Alternatives:** Session-based auth, API keys  
**Rationale:** JWT is stateless, scalable, and supports fine-grained claims  
**Consequences:** Token management complexity (refresh tokens, expiration)  

---

**End of Plan**

*This migration plan will be reviewed and approved by the following stakeholders:*
- Engineering Lead: _________________
- Product Owner: _________________
- Security Team: _________________
- Operations Team: _________________

**Approval Date:** _________________
