# Backend Setup Instructions

## Prerequisites Verification

Before proceeding, ensure .NET 9.0 SDK is installed:

```powershell
dotnet --version
# Expected output: 9.0.x
```

If not installed, download from: https://dotnet.microsoft.com/download/dotnet/9.0

---

## Step-by-Step Setup

### 1. Create Solution and Projects

```powershell
# Navigate to backend directory
cd backend

# Create solution file
dotnet new sln -n Cortex.SDD

# Create API project (Presentation Layer)
dotnet new webapi -n Cortex.SDD.Api -o src/Cortex.SDD.Api

# Create Application project (Application Layer)
dotnet new classlib -n Cortex.SDD.Application -o src/Cortex.SDD.Application

# Create Domain project (Domain Layer)
dotnet new classlib -n Cortex.SDD.Domain -o src/Cortex.SDD.Domain

# Create Infrastructure project (Infrastructure Layer)
dotnet new classlib -n Cortex.SDD.Infrastructure -o src/Cortex.SDD.Infrastructure

# Create test projects
dotnet new xunit -n Cortex.SDD.Api.Tests -o tests/Cortex.SDD.Api.Tests
dotnet new xunit -n Cortex.SDD.Application.Tests -o tests/Cortex.SDD.Application.Tests
dotnet new xunit -n Cortex.SDD.Integration.Tests -o tests/Cortex.SDD.Integration.Tests

# Add projects to solution
dotnet sln add src/Cortex.SDD.Api/Cortex.SDD.Api.csproj
dotnet sln add src/Cortex.SDD.Application/Cortex.SDD.Application.csproj
dotnet sln add src/Cortex.SDD.Domain/Cortex.SDD.Domain.csproj
dotnet sln add src/Cortex.SDD.Infrastructure/Cortex.SDD.Infrastructure.csproj
dotnet sln add tests/Cortex.SDD.Api.Tests/Cortex.SDD.Api.Tests.csproj
dotnet sln add tests/Cortex.SDD.Application.Tests/Cortex.SDD.Application.Tests.csproj
dotnet sln add tests/Cortex.SDD.Integration.Tests/Cortex.SDD.Integration.Tests.csproj
```

### 2. Add Project References

```powershell
# Api references Application and Infrastructure
dotnet add src/Cortex.SDD.Api/Cortex.SDD.Api.csproj reference src/Cortex.SDD.Application/Cortex.SDD.Application.csproj
dotnet add src/Cortex.SDD.Api/Cortex.SDD.Api.csproj reference src/Cortex.SDD.Infrastructure/Cortex.SDD.Infrastructure.csproj

# Application references Domain
dotnet add src/Cortex.SDD.Application/Cortex.SDD.Application.csproj reference src/Cortex.SDD.Domain/Cortex.SDD.Domain.csproj

# Infrastructure references Domain
dotnet add src/Cortex.SDD.Infrastructure/Cortex.SDD.Infrastructure.csproj reference src/Cortex.SDD.Domain/Cortex.SDD.Domain.csproj

# Test projects reference their respective layers
dotnet add tests/Cortex.SDD.Api.Tests/Cortex.SDD.Api.Tests.csproj reference src/Cortex.SDD.Api/Cortex.SDD.Api.csproj
dotnet add tests/Cortex.SDD.Application.Tests/Cortex.SDD.Application.Tests.csproj reference src/Cortex.SDD.Application/Cortex.SDD.Application.csproj
dotnet add tests/Cortex.SDD.Integration.Tests/Cortex.SDD.Integration.Tests.csproj reference src/Cortex.SDD.Api/Cortex.SDD.Api.csproj
```

### 3. Install NuGet Packages

**Domain Layer (minimal dependencies):**
```powershell
cd src/Cortex.SDD.Domain
# No external dependencies for pure domain layer
```

**Application Layer:**
```powershell
cd src/Cortex.SDD.Application
dotnet add package AutoMapper
dotnet add package AutoMapper.Extensions.Microsoft.DependencyInjection
dotnet add package FluentValidation
dotnet add package FluentValidation.DependencyInjectionExtensions
dotnet add package BCrypt.Net-Next
```

**Infrastructure Layer:**
```powershell
cd src/Cortex.SDD.Infrastructure
dotnet add package Microsoft.EntityFrameworkCore
dotnet add package Microsoft.EntityFrameworkCore.SqlServer
dotnet add package Microsoft.EntityFrameworkCore.Design
dotnet add package Microsoft.EntityFrameworkCore.Tools
```

**Api Layer:**
```powershell
cd src/Cortex.SDD.Api
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer
dotnet add package Serilog.AspNetCore
dotnet add package Serilog.Sinks.Console
dotnet add package Serilog.Sinks.File
dotnet add package Swashbuckle.AspNetCore
dotnet add package Microsoft.AspNetCore.Mvc.Versioning
```

**Test Projects:**
```powershell
cd tests/Cortex.SDD.Api.Tests
dotnet add package Microsoft.AspNetCore.Mvc.Testing
dotnet add package Moq
dotnet add package FluentAssertions
dotnet add package Microsoft.EntityFrameworkCore.InMemory

cd ../Cortex.SDD.Application.Tests
dotnet add package Moq
dotnet add package FluentAssertions
dotnet add package Microsoft.EntityFrameworkCore.InMemory

cd ../Cortex.SDD.Integration.Tests
dotnet add package Microsoft.AspNetCore.Mvc.Testing
dotnet add package FluentAssertions
dotnet add package Microsoft.EntityFrameworkCore.InMemory
```

### 4. Build Solution

```powershell
cd ../..  # Back to backend root
dotnet build
```

Expected output: Build succeeded. 0 Warning(s). 0 Error(s).

### 5. Configure User Secrets

```powershell
cd src/Cortex.SDD.Api
dotnet user-secrets init
dotnet user-secrets set "JwtSettings:Secret" "YourSuperSecretKeyThatIsAtLeast32CharactersLongForHS256"
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "Server=localhost;Database=CortexSDD;Integrated Security=true;TrustServerCertificate=True;"
```

---

## Verification

Run these commands to verify setup:

```powershell
# Verify solution builds
dotnet build

# Verify tests run (will have 0 tests initially)
dotnet test

# Verify API project can start
dotnet run --project src/Cortex.SDD.Api
```

---

## Next Steps

After setup is complete:
1. Proceed to **Phase 1: Domain & Data Layer** implementation
2. Follow TDD approach (RED-GREEN-REFACTOR)
3. Create git checkpoints after each phase

---

**Setup Time Estimate:** 30-45 minutes  
**Prerequisite:** .NET 9.0 SDK installed
