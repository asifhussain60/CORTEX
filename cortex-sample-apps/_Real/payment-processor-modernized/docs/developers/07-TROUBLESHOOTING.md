# Troubleshooting Guide

**Audience:** All developers  
**Purpose:** Quick solutions to common issues  
**Format:** Problem → Symptoms → Solution

---

## 🚀 Quick Diagnostics

### First Steps for Any Issue

```bash
# 1. Clean and rebuild
dotnet clean
dotnet restore
dotnet build

# 2. Run tests to verify setup
dotnet test

# 3. Check logs
Get-Content logs/app.log -Tail 50
```

---

## 🏗️ Build Issues

### Issue: "The type or namespace could not be found"

**Symptoms:**
```
error CS0246: The type or namespace name 'FluentValidation' could not be found
```

**Solutions:**

```bash
# Solution 1: Restore NuGet packages
dotnet restore

# Solution 2: Clear NuGet cache
dotnet nuget locals all --clear
dotnet restore

# Solution 3: Verify package references
dotnet list package
```

**Verify packages in .csproj:**
```xml
<ItemGroup>
  <PackageReference Include="FluentValidation" Version="11.8.0" />
  <PackageReference Include="FluentValidation.DependencyInjectionExtensions" Version="11.8.0" />
</ItemGroup>
```

---

### Issue: "Project file is incomplete or corrupted"

**Symptoms:**
```
error MSB4025: The project file could not be loaded
```

**Solutions:**

```bash
# Solution 1: Check for XML syntax errors
notepad src/PaymentProcessor.TransactionInvoices.API/PaymentProcessor.TransactionInvoices.API.csproj

# Solution 2: Validate XML structure
# Ensure all <ItemGroup>, <PropertyGroup> tags are properly closed

# Solution 3: Restore from source control
git checkout src/PaymentProcessor.TransactionInvoices.API/PaymentProcessor.TransactionInvoices.API.csproj
```

---

### Issue: "Multiple versions of the same assembly"

**Symptoms:**
```
warning CS1702: Assuming assembly reference 'System.Text.Json, Version=6.0.0.0' 
matches 'System.Text.Json, Version=7.0.0.0'
```

**Solutions:**

```xml
<!-- Add binding redirect in .csproj -->
<ItemGroup>
  <PackageReference Include="System.Text.Json" Version="8.0.0" />
</ItemGroup>
```

---

## 🧪 Test Failures

### Issue: All tests fail with "No test is available"

**Symptoms:**
```
No test is available in C:\...\PaymentProcessor.TransactionInvoices.UnitTests.dll
```

**Solutions:**

```bash
# Solution 1: Rebuild test project
dotnet clean tests/PaymentProcessor.TransactionInvoices.UnitTests/
dotnet build tests/PaymentProcessor.TransactionInvoices.UnitTests/

# Solution 2: Verify xUnit package
dotnet add tests/PaymentProcessor.TransactionInvoices.UnitTests/ package xunit
dotnet add tests/PaymentProcessor.TransactionInvoices.UnitTests/ package xunit.runner.visualstudio

# Solution 3: Check for [Fact] or [Theory] attributes
# Tests must be marked with these attributes
```

---

### Issue: Tests pass individually but fail in suite

**Symptoms:**
```
Test "CreateAsync_Test1" passed
Test "CreateAsync_Test2" failed with "Unique constraint violation"
```

**Root Cause:** Shared state between tests

**Solutions:**

```csharp
// Solution 1: Use transactions for isolation
public class MyTests : IDisposable
{
    private readonly DbContext _context;
    
    public MyTests()
    {
        _context = CreateContext();
        _context.Database.BeginTransaction();
    }
    
    public void Dispose()
    {
        _context.Database.RollbackTransaction();
        _context.Dispose();
    }
}

// Solution 2: Use unique test data
var invoice = new TransactionInvoice
{
    InvoiceNumber = $"INV-TEST-{Guid.NewGuid()}",  // Unique per test
    // ...
};

// Solution 3: Reset database between tests
[Collection("Database collection")]  // xUnit collection for sequential execution
public class MyTests
{
    // Tests run sequentially, not parallel
}
```

---

### Issue: "Timeout waiting for database"

**Symptoms:**
```
System.TimeoutException: Timeout expired. The timeout period elapsed prior to 
completion of the operation.
```

**Solutions:**

```bash
# Solution 1: Verify SQL Server is running
sqlcmd -S "(localdb)\MSSQLLocalDB" -Q "SELECT @@VERSION"

# Solution 2: Increase timeout in connection string
"Server=(localdb)\\MSSQLLocalDB;Database=Test;Connection Timeout=60"

# Solution 3: Check firewall/network
Test-NetConnection -ComputerName localhost -Port 1433
```

---

## 🗄️ Database Issues

### Issue: "Cannot connect to database"

**Symptoms:**
```
SqlException: A network-related or instance-specific error occurred while 
establishing a connection to SQL Server
```

**Solutions:**

```bash
# Solution 1: Verify SQL Server service is running
Get-Service MSSQL*

# If stopped:
Start-Service MSSQL$SQLEXPRESS

# Solution 2: Test connection string
sqlcmd -S "(localdb)\MSSQLLocalDB" -Q "SELECT 1"

# Solution 3: Check SQL Server configuration
# Open SQL Server Configuration Manager
# Ensure TCP/IP protocol is enabled

# Solution 4: Recreate LocalDB instance
sqllocaldb delete MSSQLLocalDB
sqllocaldb create MSSQLLocalDB
sqllocaldb start MSSQLLocalDB
```

---

### Issue: "Database does not exist"

**Symptoms:**
```
SqlException: Cannot open database "TransactionInvoices_Test" requested by the login
```

**Solutions:**

```bash
# Solution 1: Create database
sqlcmd -S "(localdb)\MSSQLLocalDB" -Q "CREATE DATABASE TransactionInvoices_Test"

# Solution 2: Run EF Core migrations
cd src/PaymentProcessor.TransactionInvoices.Infrastructure
dotnet ef database update --context TransactionInvoicesDbContext

# Solution 3: Ensure migrations exist
dotnet ef migrations list --context TransactionInvoicesDbContext

# If no migrations:
dotnet ef migrations add InitialCreate --context TransactionInvoicesDbContext
dotnet ef database update --context TransactionInvoicesDbContext
```

---

### Issue: "Migration already applied"

**Symptoms:**
```
The migration '20251212120000_InitialCreate' has already been applied to the database
```

**Solutions:**

```bash
# Solution 1: Reset database (DEVELOPMENT ONLY!)
dotnet ef database drop --context TransactionInvoicesDbContext --force
dotnet ef database update --context TransactionInvoicesDbContext

# Solution 2: Check migration history
sqlcmd -S "(localdb)\MSSQLLocalDB" -d TransactionInvoices_Test -Q "SELECT * FROM __EFMigrationsHistory"

# Solution 3: Remove last migration (if not applied to prod)
dotnet ef migrations remove --context TransactionInvoicesDbContext
```

---

### Issue: "Sequence contains no elements"

**Symptoms:**
```
InvalidOperationException: Sequence contains no elements
  at System.Linq.Enumerable.First[TSource](IEnumerable`1 source)
```

**Root Cause:** Query returned no results but code expected at least one

**Solutions:**

```csharp
// ❌ Bad: Crashes if no results
var invoice = await _context.TransactionInvoices.FirstAsync(i => i.InvoiceId == id);

// ✅ Good: Safe with null check
var invoice = await _context.TransactionInvoices.FirstOrDefaultAsync(i => i.InvoiceId == id);
if (invoice == null)
    throw new NotFoundException($"Invoice {id} not found");

// ✅ Good: Use SingleOrDefaultAsync for unique queries
var invoice = await _context.TransactionInvoices.SingleOrDefaultAsync(i => i.InvoiceNumber == number);
```

---

## 🌐 API Issues

### Issue: "Port already in use"

**Symptoms:**
```
IOException: Failed to bind to address https://127.0.0.1:7001: address already in use
```

**Solutions:**

```bash
# Solution 1: Find and kill process using port 7001
netstat -ano | findstr :7001
taskkill /PID <process_id> /F

# Solution 2: Change port in launchSettings.json
# File: src/PaymentProcessor.TransactionInvoices.API/Properties/launchSettings.json
{
  "applicationUrl": "https://localhost:7002;http://localhost:5002"  # Changed ports
}

# Solution 3: Use dynamic port
dotnet run --urls "https://localhost:0"  # 0 = any available port
```

---

### Issue: "401 Unauthorized" on all endpoints

**Symptoms:**
```
Status: 401 Unauthorized
Response: { "error": "Authorization header missing" }
```

**Solutions:**

```csharp
// Solution 1: Add authorization header
var client = new HttpClient();
client.DefaultRequestHeaders.Authorization = 
    new AuthenticationHeaderValue("Bearer", "your-token-here");

// Solution 2: Disable auth for development (NOT FOR PRODUCTION!)
// In Startup.cs
services.AddAuthentication().AddJwtBearer(options =>
{
    options.RequireHttpsMetadata = false;  // Dev only
    options.SaveToken = true;
});

// Solution 3: Use [AllowAnonymous] for testing
[AllowAnonymous]  // Remove before production!
[HttpPost]
public async Task<IActionResult> CreateInvoice(...)
```

---

### Issue: "HTTPS certificate is invalid"

**Symptoms:**
```
HttpRequestException: The SSL connection could not be established
```

**Solutions:**

```bash
# Solution 1: Trust development certificate
dotnet dev-certs https --trust

# Solution 2: Regenerate certificate
dotnet dev-certs https --clean
dotnet dev-certs https --trust

# Solution 3: Disable SSL validation (DEV ONLY!)
# In API test:
var handler = new HttpClientHandler();
handler.ServerCertificateCustomValidationCallback = 
    HttpClientHandler.DangerousAcceptAnyServerCertificateValidator;
var client = new HttpClient(handler);
```

---

## ⚙️ Configuration Issues

### Issue: "Configuration value not found"

**Symptoms:**
```
NullReferenceException at Configuration["DataLayer:Provider"]
```

**Solutions:**

```bash
# Solution 1: Verify appsettings.json exists
Test-Path src/PaymentProcessor.TransactionInvoices.API/appsettings.json
Test-Path src/PaymentProcessor.TransactionInvoices.API/appsettings.Development.json

# Solution 2: Check JSON syntax
# Use VS Code or jsonlint.com to validate JSON

# Solution 3: Verify configuration is loaded
public void ConfigureServices(IServiceCollection services)
{
    Console.WriteLine($"DataLayer Provider: {Configuration["DataLayer:Provider"]}");
    // Should output: "Mock" or "EFCore"
}

# Solution 4: Check environment variable
$env:ASPNETCORE_ENVIRONMENT
# Should be: Development, Staging, or Production
```

---

### Issue: "Wrong data layer provider loaded"

**Symptoms:**
- Expected EF Core, got Mock (or vice versa)
- Data not persisting
- Connection string errors

**Solutions:**

```bash
# Solution 1: Check active configuration
# In logs, look for:
# "DataLayer provider: Mock" or "DataLayer provider: EFCore"

# Solution 2: Verify appsettings.{Environment}.json
# File: appsettings.Development.json
{
  "DataLayer": {
    "Provider": "Mock"  # ← Check this value
  }
}

# Solution 3: Override with environment variable
$env:DataLayer__Provider = "EFCore"
dotnet run

# Solution 4: Debug configuration loading
public void ConfigureServices(IServiceCollection services)
{
    var provider = Configuration["DataLayer:Provider"];
    Console.WriteLine($"Loading data layer: {provider}");
    
    if (string.IsNullOrEmpty(provider))
        throw new InvalidOperationException("DataLayer:Provider not configured!");
        
    services.AddDataLayer(Configuration);
}
```

---

## 🔍 Debugging Issues

### Issue: Breakpoints not hitting

**Symptoms:**
- Set breakpoint in code
- Run debugger
- Breakpoint is hollow (not solid red)
- Code doesn't pause

**Solutions:**

```bash
# Solution 1: Rebuild in Debug mode
dotnet build --configuration Debug

# Solution 2: Verify .pdb files exist
Get-ChildItem -Recurse -Filter "*.pdb" src/

# Solution 3: Clean and rebuild
dotnet clean
dotnet build

# Solution 4: Check launch.json (VS Code)
{
  "type": "coreclr",
  "request": "launch",
  "preLaunchTask": "build",
  "program": "${workspaceFolder}/src/PaymentProcessor.TransactionInvoices.API/bin/Debug/net8.0/PaymentProcessor.TransactionInvoices.API.dll",
  "args": [],
  "cwd": "${workspaceFolder}/src/PaymentProcessor.TransactionInvoices.API",
  "stopAtEntry": false,
  "serverReadyAction": {
    "action": "openExternally",
    "pattern": "\\bNow listening on:\\s+(https?://\\S+)"
  },
  "env": {
    "ASPNETCORE_ENVIRONMENT": "Development"
  }
}
```

---

### Issue: "Source code not available"

**Symptoms:**
```
Source Not Available
The source code is different from the original version
```

**Solutions:**

```bash
# Solution 1: Rebuild
dotnet clean
dotnet build

# Solution 2: Check for outdated .dll files
# Delete bin/ and obj/ folders
Remove-Item -Recurse -Force src/*/bin/
Remove-Item -Recurse -Force src/*/obj/
dotnet build

# Solution 3: Disable "Just My Code" (Visual Studio)
# Tools → Options → Debugging → General
# Uncheck "Enable Just My Code"
```

---

## 📊 Performance Issues

### Issue: API responses are slow (>5 seconds)

**Symptoms:**
- Requests take several seconds
- Timeout errors under load
- High CPU usage

**Solutions:**

```csharp
// Solution 1: Check for N+1 queries
// ❌ Bad: N+1 query problem
var invoices = await _context.TransactionInvoices.ToListAsync();
foreach (var invoice in invoices)
{
    var batch = await _context.TransactionBatches.FindAsync(invoice.BatchId);  // N queries!
}

// ✅ Good: Single query with Include
var invoices = await _context.TransactionInvoices
    .Include(i => i.Batch)  // Eager load
    .ToListAsync();

// Solution 2: Use AsNoTracking for read-only queries
var invoices = await _context.TransactionInvoices
    .AsNoTracking()  // 30% faster for reads
    .ToListAsync();

// Solution 3: Add database indexes
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<TransactionInvoice>(entity =>
    {
        entity.HasIndex(e => e.EmployerId);  // Index frequently queried fields
        entity.HasIndex(e => e.Status);
        entity.HasIndex(e => e.CreatedDate);
    });
}

// Solution 4: Profile slow queries
// Enable SQL logging
services.AddDbContext<TransactionInvoicesDbContext>(options =>
{
    options.UseSqlServer(connectionString)
        .LogTo(Console.WriteLine, LogLevel.Information)  // Log SQL queries
        .EnableSensitiveDataLogging();  // Dev only!
});
```

---

### Issue: Memory leaks

**Symptoms:**
- Memory usage grows over time
- OutOfMemoryException
- Application crashes after hours

**Solutions:**

```csharp
// Solution 1: Dispose DbContext properly
// ❌ Bad: DbContext never disposed
public class MyService
{
    private readonly DbContext _context = new TransactionInvoicesDbContext();
}

// ✅ Good: Scoped lifetime via DI
services.AddDbContext<TransactionInvoicesDbContext>(options => ...);
// DbContext is automatically disposed after each request

// Solution 2: Don't cache DbContext
// ❌ Bad: Singleton DbContext
services.AddSingleton<TransactionInvoicesDbContext>();

// ✅ Good: Scoped DbContext
services.AddScoped<TransactionInvoicesDbContext>();

// Solution 3: Dispose repositories
public class MyRepository : IDisposable
{
    private readonly DbContext _context;
    
    public void Dispose()
    {
        _context?.Dispose();
    }
}
```

---

## 🚨 Runtime Errors

### Issue: "Object reference not set to an instance of an object"

**Symptoms:**
```
NullReferenceException: Object reference not set to an instance of an object
  at TransactionInvoiceService.CreateAsync(...)
```

**Solutions:**

```csharp
// Solution 1: Add null checks
// ❌ Bad: Assumes value is not null
var plan = await _planAdapter.GetPlanAsync(planId);
var amount = plan.MaxAmount;  // Crashes if plan is null

// ✅ Good: Null check
var plan = await _planAdapter.GetPlanAsync(planId);
if (plan == null)
    throw new NotFoundException($"Plan {planId} not found");
var amount = plan.MaxAmount;

// Solution 2: Use null-conditional operator
var amount = plan?.MaxAmount ?? 0;  // Default to 0 if null

// Solution 3: Enable nullable reference types
// In .csproj:
<PropertyGroup>
  <Nullable>enable</Nullable>
</PropertyGroup>

// Then use nullable syntax:
public async Task<PaymentPlan?> GetPlanAsync(string planId)
{
    // Compiler enforces null checks
}
```

---

### Issue: "The JSON value could not be converted"

**Symptoms:**
```
JsonException: The JSON value could not be converted to System.Decimal
```

**Solutions:**

```csharp
// Solution 1: Check JSON format
// ❌ Bad: String instead of number
{
  "amount": "750.00"  // Should be number, not string
}

// ✅ Good:
{
  "amount": 750.00
}

// Solution 2: Custom JSON converter
public class DecimalJsonConverter : JsonConverter<decimal>
{
    public override decimal Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        if (reader.TokenType == JsonTokenType.String)
        {
            return decimal.Parse(reader.GetString()!);  // Parse string as decimal
        }
        return reader.GetDecimal();
    }
    
    public override void Write(Utf8JsonWriter writer, decimal value, JsonSerializerOptions options)
    {
        writer.WriteNumberValue(value);
    }
}

// Register in Startup.cs
services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.Converters.Add(new DecimalJsonConverter());
    });
```

---

## 🔧 Dependency Injection Issues

### Issue: "No service for type 'ITransactionInvoiceRepository'"

**Symptoms:**
```
InvalidOperationException: Unable to resolve service for type 
'PaymentProcessor.TransactionInvoices.Core.Interfaces.ITransactionInvoiceRepository' while attempting 
to activate 'PaymentProcessor.TransactionInvoices.Core.Services.TransactionInvoiceService'
```

**Solutions:**

```csharp
// Solution 1: Register service in Startup.cs
public void ConfigureServices(IServiceCollection services)
{
    // Add this:
    services.AddScoped<ITransactionInvoiceRepository, MockTransactionInvoiceRepository>();
    // Or use DataLayerRouter:
    services.AddDataLayer(Configuration);
}

// Solution 2: Verify interface and implementation match
public interface ITransactionInvoiceRepository  // ← Interface name
{
    // ...
}

public class MockTransactionInvoiceRepository : ITransactionInvoiceRepository  // ← Implements interface
{
    // ...
}

// Solution 3: Check service lifetime
// Ensure all dependencies have compatible lifetimes:
services.AddScoped<ITransactionInvoiceRepository, ...>();  // Scoped
services.AddScoped<ITransactionInvoiceService, ...>();     // Scoped
// Don't inject Scoped into Singleton!
```

---

## 📞 Getting More Help

### Check Logs

```bash
# Application logs
Get-Content logs/app.log -Tail 100

# Filter errors
Get-Content logs/app.log | Select-String "ERROR"

# Watch logs in real-time
Get-Content logs/app.log -Wait -Tail 50
```

### Enable Verbose Logging

```json
// appsettings.Development.json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",  // More verbose
      "Microsoft": "Information",
      "Microsoft.EntityFrameworkCore": "Information"  // See SQL queries
    }
  }
}
```

### Contact Support

| Issue Type | Contact | When to Escalate |
|------------|---------|------------------|
| **Build/Test** | Tech Lead | After 30 min troubleshooting |
| **Database** | DBA Team | Connection/performance issues |
| **Performance** | Performance Team | P95 latency >200ms |
| **Security** | Security Team | Auth/encryption issues |
| **Production** | On-Call Engineer | Production outages |

---

## 🔍 Diagnostic Commands Cheat Sheet

```bash
# Check .NET version
dotnet --version

# List installed SDKs
dotnet --list-sdks

# Verify project builds
dotnet build --no-incremental

# Check for outdated packages
dotnet list package --outdated

# View project dependencies
dotnet list package

# Check for package vulnerabilities
dotnet list package --vulnerable

# Test with verbose output
dotnet test --logger "console;verbosity=detailed"

# Verify SQL Server is running
Get-Service MSSQL*

# Test database connection
sqlcmd -S "(localdb)\MSSQLLocalDB" -Q "SELECT @@VERSION"

# Check listening ports
netstat -ano | findstr LISTENING

# View environment variables
Get-ChildItem Env:

# Check disk space
Get-PSDrive C
```

---

**Last Updated:** December 12, 2025  
**Maintained By:** Development Team
