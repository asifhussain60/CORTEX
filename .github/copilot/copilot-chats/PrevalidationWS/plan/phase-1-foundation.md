# Phase 1: Foundation & Infrastructure

**Duration:** Week 1-2  
**Priority:** HIGH - Foundation for all subsequent phases  
**Owner:** Technical Lead

---

## 🎯 Objectives

**Primary Goal:** Create .NET 8 solution structure with Clean Architecture foundations.

**Success Criteria:**
- ✅ Solution compiles without errors
- ✅ All projects use .NET 8.0 target framework
- ✅ Folder structure matches Clean Architecture pattern
- ✅ NuGet packages restored successfully
- ✅ Basic health check endpoint returns 200 OK
- ✅ README.md documents getting started steps

**Dependencies:**
- Phase 0 pre-flight check passed
- .NET SDK 8.0+ installed
- Visual Studio 2022 or VS Code with C# extension

---

## 📁 Solution Structure

**Create:** `cortex/modernized/PSFPrevalidation.sln`

```
cortex/modernized/
├── PSFPrevalidation.sln                    # Solution file
├── README.md                                # Getting started guide
├── Directory.Build.props                    # Shared build properties
├── .editorconfig                           # Code style rules
├── .gitignore                              # Git ignore patterns
├── global.json                             # .NET SDK version lock
│
├── src/
│   ├── PSFPrevalidation.Api/               # Layer 1: API Controllers
│   │   ├── Controllers/
│   │   │   ├── PrevalidationController.cs
│   │   │   └── HealthController.cs
│   │   ├── Middleware/
│   │   │   ├── ExceptionHandlingMiddleware.cs
│   │   │   └── RequestLoggingMiddleware.cs
│   │   ├── Program.cs                      # Application entry point
│   │   ├── appsettings.json
│   │   ├── appsettings.Development.json
│   │   └── PSFPrevalidation.Api.csproj
│   │
│   ├── PSFPrevalidation.Core/              # Layer 2: Domain Models
│   │   ├── Models/
│   │   │   ├── ValidationResult.cs
│   │   │   ├── ValidationRequest.cs
│   │   │   └── PrevalidationData.cs
│   │   ├── Enums/
│   │   │   ├── ErrorType.cs
│   │   │   ├── RecordType.cs
│   │   │   └── ValidationSeverity.cs
│   │   ├── Interfaces/
│   │   │   ├── IPrevalidationService.cs
│   │   │   ├── IPrevalidationRepository.cs
│   │   │   └── IFileParser.cs
│   │   ├── Validators/
│   │   │   └── (Phase 3)
│   │   └── PSFPrevalidation.Core.csproj
│   │
│   ├── PSFPrevalidation.Infrastructure/    # Layer 3: Data Access
│   │   ├── Repositories/
│   │   │   ├── PrevalidationRepository.cs  # EF Core implementation
│   │   │   └── MockPrevalidationRepository.cs # Mock for testing
│   │   ├── Data/
│   │   │   ├── AppDbContext.cs
│   │   │   └── Migrations/
│   │   ├── Services/
│   │   │   ├── BlobStorageService.cs
│   │   │   └── ServiceBusPublisher.cs
│   │   └── PSFPrevalidation.Infrastructure.csproj
│   │
│   └── PSFPrevalidation.Shared/            # Layer 4: Shared Utilities
│       ├── Exceptions/
│       │   ├── ValidationException.cs
│       │   └── PrevalidationException.cs
│       ├── Extensions/
│       │   ├── StringExtensions.cs
│       │   └── StreamExtensions.cs
│       ├── Constants/
│       │   └── ValidationConstants.cs
│       └── PSFPrevalidation.Shared.csproj
│
├── tests/
│   ├── PSFPrevalidation.UnitTests/
│   │   └── PSFPrevalidation.UnitTests.csproj
│   ├── PSFPrevalidation.ComponentTests/
│   │   └── PSFPrevalidation.ComponentTests.csproj
│   ├── PSFPrevalidation.IntegrationTests/
│   │   └── PSFPrevalidation.IntegrationTests.csproj
│   └── PSFPrevalidation.E2ETests/
│       └── PSFPrevalidation.E2ETests.csproj
│
└── docs/
    ├── API.md                              # API documentation
    ├── ARCHITECTURE.md                     # Architecture decisions
    └── DEPLOYMENT.md                       # Deployment guide
```

---

## 🔧 Project Creation Steps

### Step 1: Create Solution and Projects
```powershell
# Navigate to modernized directory
cd C:\PROJECTS\V5.WebServices.PrevalidationWS\cortex\modernized

# Create solution
dotnet new sln -n PSFPrevalidation

# Create API project (ASP.NET Core Web API)
dotnet new webapi -n PSFPrevalidation.Api -o src/PSFPrevalidation.Api --framework net8.0

# Create Core project (Class Library)
dotnet new classlib -n PSFPrevalidation.Core -o src/PSFPrevalidation.Core --framework net8.0

# Create Infrastructure project (Class Library)
dotnet new classlib -n PSFPrevalidation.Infrastructure -o src/PSFPrevalidation.Infrastructure --framework net8.0

# Create Shared project (Class Library)
dotnet new classlib -n PSFPrevalidation.Shared -o src/PSFPrevalidation.Shared --framework net8.0

# Create test projects
dotnet new xunit -n PSFPrevalidation.UnitTests -o tests/PSFPrevalidation.UnitTests --framework net8.0
dotnet new xunit -n PSFPrevalidation.ComponentTests -o tests/PSFPrevalidation.ComponentTests --framework net8.0
dotnet new xunit -n PSFPrevalidation.IntegrationTests -o tests/PSFPrevalidation.IntegrationTests --framework net8.0
dotnet new xunit -n PSFPrevalidation.E2ETests -o tests/PSFPrevalidation.E2ETests --framework net8.0

# Add projects to solution
dotnet sln add src/PSFPrevalidation.Api/PSFPrevalidation.Api.csproj
dotnet sln add src/PSFPrevalidation.Core/PSFPrevalidation.Core.csproj
dotnet sln add src/PSFPrevalidation.Infrastructure/PSFPrevalidation.Infrastructure.csproj
dotnet sln add src/PSFPrevalidation.Shared/PSFPrevalidation.Shared.csproj
dotnet sln add tests/PSFPrevalidation.UnitTests/PSFPrevalidation.UnitTests.csproj
dotnet sln add tests/PSFPrevalidation.ComponentTests/PSFPrevalidation.ComponentTests.csproj
dotnet sln add tests/PSFPrevalidation.IntegrationTests/PSFPrevalidation.IntegrationTests.csproj
dotnet sln add tests/PSFPrevalidation.E2ETests/PSFPrevalidation.E2ETests.csproj
```

### Step 2: Add Project References
```powershell
# API depends on Core, Infrastructure, Shared
dotnet add src/PSFPrevalidation.Api/PSFPrevalidation.Api.csproj reference src/PSFPrevalidation.Core/PSFPrevalidation.Core.csproj
dotnet add src/PSFPrevalidation.Api/PSFPrevalidation.Api.csproj reference src/PSFPrevalidation.Infrastructure/PSFPrevalidation.Infrastructure.csproj
dotnet add src/PSFPrevalidation.Api/PSFPrevalidation.Api.csproj reference src/PSFPrevalidation.Shared/PSFPrevalidation.Shared.csproj

# Infrastructure depends on Core, Shared
dotnet add src/PSFPrevalidation.Infrastructure/PSFPrevalidation.Infrastructure.csproj reference src/PSFPrevalidation.Core/PSFPrevalidation.Core.csproj
dotnet add src/PSFPrevalidation.Infrastructure/PSFPrevalidation.Infrastructure.csproj reference src/PSFPrevalidation.Shared/PSFPrevalidation.Shared.csproj

# Core depends on Shared
dotnet add src/PSFPrevalidation.Core/PSFPrevalidation.Core.csproj reference src/PSFPrevalidation.Shared/PSFPrevalidation.Shared.csproj

# Test projects depend on src projects
dotnet add tests/PSFPrevalidation.UnitTests/PSFPrevalidation.UnitTests.csproj reference src/PSFPrevalidation.Core/PSFPrevalidation.Core.csproj
dotnet add tests/PSFPrevalidation.ComponentTests/PSFPrevalidation.ComponentTests.csproj reference src/PSFPrevalidation.Infrastructure/PSFPrevalidation.Infrastructure.csproj
dotnet add tests/PSFPrevalidation.IntegrationTests/PSFPrevalidation.IntegrationTests.csproj reference src/PSFPrevalidation.Api/PSFPrevalidation.Api.csproj
dotnet add tests/PSFPrevalidation.E2ETests/PSFPrevalidation.E2ETests.csproj reference src/PSFPrevalidation.Api/PSFPrevalidation.Api.csproj
```

### Step 3: Add NuGet Packages
```powershell
# API packages
dotnet add src/PSFPrevalidation.Api/PSFPrevalidation.Api.csproj package Microsoft.AspNetCore.OpenApi --version 8.0.0
dotnet add src/PSFPrevalidation.Api/PSFPrevalidation.Api.csproj package Swashbuckle.AspNetCore --version 6.5.0
dotnet add src/PSFPrevalidation.Api/PSFPrevalidation.Api.csproj package Microsoft.ApplicationInsights.AspNetCore --version 2.21.0
dotnet add src/PSFPrevalidation.Api/PSFPrevalidation.Api.csproj package Serilog.AspNetCore --version 8.0.0

# Core packages
dotnet add src/PSFPrevalidation.Core/PSFPrevalidation.Core.csproj package FluentValidation --version 11.9.0

# Infrastructure packages
dotnet add src/PSFPrevalidation.Infrastructure/PSFPrevalidation.Infrastructure.csproj package Microsoft.EntityFrameworkCore --version 8.0.0
dotnet add src/PSFPrevalidation.Infrastructure/PSFPrevalidation.Infrastructure.csproj package Oracle.EntityFrameworkCore --version 8.21.121
dotnet add src/PSFPrevalidation.Infrastructure/PSFPrevalidation.Infrastructure.csproj package Azure.Storage.Blobs --version 12.19.1
dotnet add src/PSFPrevalidation.Infrastructure/PSFPrevalidation.Infrastructure.csproj package Azure.Messaging.ServiceBus --version 7.17.0

# Test packages
dotnet add tests/PSFPrevalidation.UnitTests/PSFPrevalidation.UnitTests.csproj package Moq --version 4.20.70
dotnet add tests/PSFPrevalidation.UnitTests/PSFPrevalidation.UnitTests.csproj package FluentAssertions --version 6.12.0
dotnet add tests/PSFPrevalidation.UnitTests/PSFPrevalidation.UnitTests.csproj package coverlet.collector --version 6.0.0

# Integration test packages
dotnet add tests/PSFPrevalidation.IntegrationTests/PSFPrevalidation.IntegrationTests.csproj package Microsoft.AspNetCore.Mvc.Testing --version 8.0.0
dotnet add tests/PSFPrevalidation.IntegrationTests/PSFPrevalidation.IntegrationTests.csproj package Testcontainers --version 3.6.0
```

---

## 📄 Key Configuration Files

### global.json (SDK version lock)
```json
{
  "sdk": {
    "version": "8.0.0",
    "rollForward": "latestMinor"
  }
}
```

### Directory.Build.props (Shared build properties)
```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <LangVersion>12.0</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <WarningLevel>5</WarningLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
  </PropertyGroup>

  <PropertyGroup>
    <Authors>PSF Prevalidation Team</Authors>
    <Company>Your Organization</Company>
    <Product>PSF Prevalidation Service</Product>
    <Copyright>Copyright © 2025</Copyright>
    <Version>1.0.0</Version>
  </PropertyGroup>

  <!-- Code coverage thresholds -->
  <PropertyGroup>
    <CoverageThreshold_Line>90</CoverageThreshold_Line>
    <CoverageThreshold_Branch>80</CoverageThreshold_Branch>
    <CoverageThreshold_Method>90</CoverageThreshold_Method>
  </PropertyGroup>
</Project>
```

### .editorconfig (Code style)
```ini
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 4
insert_final_newline = true
trim_trailing_whitespace = true

[*.cs]
# Naming conventions
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.severity = warning
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.symbols = interface
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.style = begins_with_i

dotnet_naming_symbols.interface.applicable_kinds = interface
dotnet_naming_style.begins_with_i.required_prefix = I
dotnet_naming_style.begins_with_i.capitalization = pascal_case

# Code style
csharp_prefer_braces = true:warning
csharp_prefer_simple_using_statement = true:suggestion
csharp_style_namespace_declarations = file_scoped:warning
```

### appsettings.json (API configuration)
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*",
  "ConnectionStrings": {
    "OracleConnection": "Data Source=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=ORCL)));User Id=prevalidation_user;Password=PLACEHOLDER;"
  },
  "AzureBlobStorage": {
    "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=PLACEHOLDER;AccountKey=PLACEHOLDER;EndpointSuffix=core.windows.net",
    "ContainerName": "prevalidation-files"
  },
  "AzureServiceBus": {
    "ConnectionString": "Endpoint=sb://PLACEHOLDER.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=PLACEHOLDER",
    "QueueName": "prevalidation-results"
  },
  "ApplicationInsights": {
    "ConnectionString": "InstrumentationKey=PLACEHOLDER"
  },
  "ValidationSettings": {
    "MaxFileSizeMB": 100,
    "AllowedFileExtensions": [ ".psf", ".txt", ".xml" ],
    "MaxConcurrentValidations": 10
  }
}
```

---

## 🏗️ Initial Code Implementation

### HealthController.cs (Verify API works)
```csharp
using Microsoft.AspNetCore.Mvc;

namespace PSFPrevalidation.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class HealthController : ControllerBase
{
    private readonly ILogger<HealthController> _logger;

    public HealthController(ILogger<HealthController> logger)
    {
        _logger = logger;
    }

    [HttpGet]
    public IActionResult Get()
    {
        _logger.LogInformation("Health check requested");
        
        return Ok(new
        {
            Status = "Healthy",
            Service = "PSF Prevalidation API",
            Version = "1.0.0",
            Timestamp = DateTime.UtcNow
        });
    }

    [HttpGet("ready")]
    public IActionResult Ready()
    {
        // TODO: Check database connectivity, blob storage, etc.
        return Ok(new { Status = "Ready" });
    }

    [HttpGet("live")]
    public IActionResult Live()
    {
        return Ok(new { Status = "Live" });
    }
}
```

### Program.cs (Minimal API setup)
```csharp
using Serilog;

var builder = WebApplication.CreateBuilder(args);

// Add Serilog
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .CreateLogger();

builder.Host.UseSerilog();

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new()
    {
        Title = "PSF Prevalidation API",
        Version = "v1",
        Description = "REST API for PSF file validation (migrated from ASMX)"
    });
});

// Add Application Insights
builder.Services.AddApplicationInsightsTelemetry();

// Add health checks
builder.Services.AddHealthChecks();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();
app.MapHealthChecks("/health");

app.Run();
```

### README.md (Getting started)
```markdown
# PSF Prevalidation Service

REST API for PSF file validation (migrated from ASMX web service).

## Prerequisites

- .NET SDK 8.0+
- Oracle client libraries
- Azure Storage Emulator (for local development)

## Getting Started

1. **Restore packages:**
   ```bash
   dotnet restore
   ```

2. **Build solution:**
   ```bash
   dotnet build
   ```

3. **Run API:**
   ```bash
   cd src/PSFPrevalidation.Api
   dotnet run
   ```

4. **Access Swagger UI:**
   Open browser: https://localhost:7001/swagger

5. **Test health endpoint:**
   ```bash
   curl https://localhost:7001/api/health
   ```

## Project Structure

- `src/PSFPrevalidation.Api` - API controllers, middleware
- `src/PSFPrevalidation.Core` - Domain models, business logic
- `src/PSFPrevalidation.Infrastructure` - Data access, external services
- `src/PSFPrevalidation.Shared` - Shared utilities, constants
- `tests/` - Unit, component, integration, E2E tests

## Configuration

Edit `appsettings.Development.json`:
- Oracle connection string
- Azure Blob Storage connection string
- Application Insights key

## Running Tests

```bash
dotnet test
```

## Related Documentation

- [API Documentation](docs/API.md)
- [Architecture Decisions](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
```

---

## ✅ Phase 1 Deliverables

**Completed Artifacts:**
- [x] Solution file (`PSFPrevalidation.sln`)
- [x] All 8 projects created (4 src + 4 tests)
- [x] Project references configured
- [x] NuGet packages restored
- [x] `Directory.Build.props` with shared settings
- [x] `global.json` with SDK version lock
- [x] `.editorconfig` with code style rules
- [x] `appsettings.json` with configuration sections
- [x] `HealthController.cs` with 3 endpoints
- [x] `Program.cs` with minimal API setup
- [x] `README.md` with getting started guide

**Validation:**
```powershell
# Run from cortex/modernized/
dotnet build
# Expected: Build succeeded. 0 Error(s)

dotnet run --project src/PSFPrevalidation.Api/PSFPrevalidation.Api.csproj
# Expected: Now listening on: https://localhost:7001

# In another terminal:
curl https://localhost:7001/api/health
# Expected: {"status":"Healthy","service":"PSF Prevalidation API"...}
```

---

## 📊 Update Master Plan Progress

**BEFORE proceeding to Phase 2:**

1. Update `MODERNIZATION-PLAN.md` progress tracker:
   ```
   PHASE 1: FOUNDATION & INFRASTRUCTURE [██████████] 100% ✅ Complete
   ```

2. Update Phase 1 checklist to all `[x]` completed

3. Update overall progress:
   ```
   OVERALL PROGRESS: █████░░░░░░░░░░░░░░░░░░░░░░░░░ 2/11 Phases (18%)
   ```

4. Commit foundation code:
   ```powershell
   git add cortex/modernized/
   git commit -m "Phase 1 Complete: Foundation & Infrastructure"
   ```

---

## 📋 Related Documents

- [Master Plan](MODERNIZATION-PLAN.md) - Overall project plan
- [Phase 2: WCF Proxy & Domain Models](phase-2-wcf-proxy.md) - Next phase
- [Test Strategy](test-strategy.md) - TDD workflow
- [Risk Register](risk-register.md) - RISK-001 (SDK missing)

---

**Next Phase:** [Phase 2: WCF Proxy & Domain Models](phase-2-wcf-proxy.md)  
**Duration:** Week 2 (after Phase 1 completion)
