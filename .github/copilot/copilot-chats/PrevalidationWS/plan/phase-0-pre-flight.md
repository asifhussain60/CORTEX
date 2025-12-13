# Phase 0: Pre-Flight & Planning

**Duration:** Week 0 (Before Implementation)  
**Priority:** CRITICAL - Prevents BLOCKER-001 from RA Migration  
**Owner:** Technical Lead

---

## 🎯 Objectives

**Primary Goal:** Verify all environment prerequisites, tooling, and access before implementation begins.

**Success Criteria:**
- ✅ .NET SDK 8.0+ installed and verified on all dev machines
- ✅ Azure CLI authenticated with correct subscription
- ✅ Database connectivity confirmed
- ✅ All required NuGet packages accessible
- ✅ CI/CD pipeline prerequisites met
- ✅ Risk register initialized
- ✅ All 38 lessons learned reviewed by team

**Blocker Prevention:**
- **BLOCKER-001:** SDK missing caused 2-week delay in RA migration
- **Root Cause:** Assumed SDK already installed, discovered during Phase 2 implementation
- **Prevention:** Mandatory SDK verification script before Day 1

---

## 📋 Pre-Flight Checklist

### 1. Development Environment Setup

**Required Software:**
```powershell
# Verification Script: pre-flight-check.ps1
# Run this before starting Phase 1

# Check .NET SDK 8.0+
dotnet --version
# Expected: 8.0.x or higher

# Check Azure CLI
az --version
# Expected: 2.50.0+

# Check Git
git --version
# Expected: 2.40.0+

# Check PowerShell
$PSVersionTable.PSVersion
# Expected: 5.1+ or PowerShell Core 7+
```

**Required Visual Studio Extensions:**
- Azure Tools for Visual Studio
- Entity Framework Core Power Tools
- NuGet Package Manager
- Code Coverage (Fine Code Coverage or dotCover)

### 2. Azure Access Verification

**Required Permissions:**
```powershell
# Login to Azure
az login

# Verify subscription access
az account show
# Confirm correct subscription

# Test Azure DevOps access
az devops project list --organization https://dev.azure.com/YourOrg
# Should list projects without errors

# Verify Key Vault access (if used)
az keyvault secret list --vault-name your-vault-name
# Should list secrets or return empty (not 403)
```

**Required Azure Resources:**
- Azure DevOps organization access
- Azure Subscription (Dev/Test/Prod environments)
- Key Vault access (if storing secrets)
- Application Insights workspace
- Azure Blob Storage account (for file uploads)

### 3. Database Connectivity

**Oracle Database Access:**
```powershell
# Test connection string from app.config
# PSFPreValidationTests/app.config line 15-20

# Verify Oracle client installed
# Check ORACLE_HOME environment variable
$env:ORACLE_HOME
# Expected: C:\oracle\product\19.0.0\client_1 or similar

# Test connection using SQL*Plus or Oracle SQL Developer
# Connection string format:
# Data Source=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=hostname)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=service_name)));User Id=user;Password=pwd;
```

**Required Database Access:**
- READ access to prevalidation tables
- WRITE access to logging/audit tables
- CREATE TABLE permission for EF Core migrations (if applicable)

### 4. NuGet Package Access

**Required Packages (from RA Migration):**
```xml
<!-- Verify access to these packages -->
<PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="8.0.0" />
<PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />
<PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
<PackageReference Include="Oracle.EntityFrameworkCore" Version="8.21.121" />
<PackageReference Include="FluentValidation.AspNetCore" Version="11.3.0" />
<PackageReference Include="Azure.Storage.Blobs" Version="12.19.1" />
<PackageReference Include="Microsoft.ApplicationInsights.AspNetCore" Version="2.21.0" />
```

**Verification:**
```powershell
# Test package restore
dotnet new webapi -n TestProject
cd TestProject
dotnet add package Microsoft.EntityFrameworkCore --version 8.0.0
dotnet restore
# Should complete without errors
cd ..
Remove-Item -Recurse -Force TestProject
```

### 5. Source Control Setup

**Repository Structure:**
```
V5.WebServices.PrevalidationWS/
├── cortex/
│   ├── plan/                           # Created ✅
│   │   ├── MODERNIZATION-PLAN.md      # Master plan ✅
│   │   ├── current-state-analysis.md  # ✅
│   │   ├── asmx-rest-contract-mapping.md  # ✅
│   │   └── [16 sub-plans]             # To be created
│   └── modernized/                     # Implementation (Phase 1+)
│       ├── src/
│       ├── tests/
│       └── docs/
```

**Branch Strategy:**
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/phase-{N}-{description}` - Phase-specific work
- `hotfix/` - Emergency fixes

**Git Isolation (SKULL Rule):**
- ✅ CORTEX code stays in `c:\PROJECTS\CORTEX`
- ✅ PrevalidationWS code stays in `c:\PROJECTS\V5.WebServices.PrevalidationWS`
- ❌ NEVER commit CORTEX orchestrators/agents to PrevalidationWS repo

### 6. CI/CD Pipeline Prerequisites

**Azure DevOps Pipeline Requirements:**
```yaml
# Minimum pipeline configuration needed
# azure-pipelines-modernization.yml

trigger:
  branches:
    include:
    - develop
    - main
  paths:
    include:
    - cortex/modernized/*

pool:
  vmImage: 'windows-latest'

variables:
  buildConfiguration: 'Release'
  dotnetSdkVersion: '8.0.x'

steps:
- task: UseDotNet@2
  displayName: 'Install .NET SDK 8.0'
  inputs:
    version: $(dotnetSdkVersion)

- task: DotNetCoreCLI@2
  displayName: 'Restore packages'
  inputs:
    command: 'restore'
    projects: 'cortex/modernized/**/*.csproj'

- task: DotNetCoreCLI@2
  displayName: 'Build'
  inputs:
    command: 'build'
    projects: 'cortex/modernized/**/*.csproj'
    arguments: '--configuration $(buildConfiguration)'

- task: DotNetCoreCLI@2
  displayName: 'Run tests'
  inputs:
    command: 'test'
    projects: 'cortex/modernized/**/*Tests.csproj'
    arguments: '--configuration $(buildConfiguration) --collect:"XPlat Code Coverage"'
```

**Required Service Connections:**
- Azure subscription service connection
- NuGet feed service connection (if using private feed)
- Oracle database connection string (secure variable)

### 7. Team Knowledge Transfer

**Required Training Sessions:**
1. **RA Migration Lessons Learned Review** (2 hours)
   - Review all 38 lessons from `prevalidation-ws-migration-lessons-learned-plan.md`
   - Focus on BLOCKER-001, BLOCKER-002, BLOCKER-003 prevention
   - Q&A on .NET 8 migration patterns

2. **Clean Architecture Overview** (1 hour)
   - Layer responsibilities (API → Service → Repository → Data)
   - Dependency inversion with interfaces
   - Mock vs EF Core swappable pattern

3. **TDD Workflow Training** (1.5 hours)
   - RED→GREEN→REFACTOR cycle
   - Phase-by-phase coverage gates (60% → 75% → 90%)
   - Test naming conventions (`{MethodName}_{Scenario}_{ExpectedBehavior}`)

**Documentation Review:**
- Current State Analysis (read before Phase 1)
- API Contract Mapping (read before Phase 4)
- Test Strategy Plan (read before writing first test)

---

## 🛠️ Pre-Flight Verification Script

**Create: `cortex/plan/scripts/pre-flight-check.ps1`**

```powershell
# Pre-Flight Environment Verification Script
# Purpose: Prevent BLOCKER-001 (SDK missing)
# Run before starting Phase 1 implementation

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$results = @()

function Test-Requirement {
    param(
        [string]$Name,
        [scriptblock]$Check,
        [string]$ErrorMessage,
        [string]$SuccessMessage
    )
    
    Write-Host "`n🔍 Checking: $Name" -ForegroundColor Cyan
    
    try {
        $result = & $Check
        if ($result) {
            Write-Host "✅ $SuccessMessage" -ForegroundColor Green
            $script:results += @{Name=$Name; Status="PASS"; Message=$SuccessMessage}
            return $true
        } else {
            Write-Host "❌ $ErrorMessage" -ForegroundColor Red
            $script:results += @{Name=$Name; Status="FAIL"; Message=$ErrorMessage}
            return $false
        }
    } catch {
        Write-Host "❌ $ErrorMessage" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
        $script:results += @{Name=$Name; Status="FAIL"; Message="$ErrorMessage - $($_.Exception.Message)"}
        return $false
    }
}

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  PSF Prevalidation Pre-Flight Check" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

# 1. .NET SDK 8.0+
Test-Requirement -Name ".NET SDK 8.0+" -Check {
    $version = dotnet --version 2>$null
    if ($version -match '^8\.') {
        $script:dotnetVersion = $version
        return $true
    }
    return $false
} -ErrorMessage ".NET SDK 8.0+ not found. Install from https://dotnet.microsoft.com/download/dotnet/8.0" `
  -SuccessMessage ".NET SDK $dotnetVersion installed"

# 2. Azure CLI
Test-Requirement -Name "Azure CLI" -Check {
    $azVersion = az --version 2>$null | Select-Object -First 1
    if ($azVersion -match 'azure-cli\s+(\d+\.\d+\.\d+)') {
        $script:azCliVersion = $matches[1]
        return $true
    }
    return $false
} -ErrorMessage "Azure CLI not found. Install from https://learn.microsoft.com/cli/azure/install-azure-cli" `
  -SuccessMessage "Azure CLI $azCliVersion installed"

# 3. Git
Test-Requirement -Name "Git" -Check {
    $gitVersion = git --version 2>$null
    if ($gitVersion -match 'git version (\d+\.\d+\.\d+)') {
        $script:gitVersion = $matches[1]
        return $true
    }
    return $false
} -ErrorMessage "Git not found. Install from https://git-scm.com/downloads" `
  -SuccessMessage "Git $gitVersion installed"

# 4. PowerShell version
Test-Requirement -Name "PowerShell 5.1+" -Check {
    $psVersion = $PSVersionTable.PSVersion
    $script:psVersion = "$($psVersion.Major).$($psVersion.Minor)"
    return ($psVersion.Major -ge 5 -and $psVersion.Minor -ge 1) -or ($psVersion.Major -ge 7)
} -ErrorMessage "PowerShell 5.1+ required. Current: $psVersion" `
  -SuccessMessage "PowerShell $psVersion"

# 5. Oracle Home
Test-Requirement -Name "Oracle Client" -Check {
    $oracleHome = $env:ORACLE_HOME
    if ($oracleHome -and (Test-Path $oracleHome)) {
        $script:oracleHome = $oracleHome
        return $true
    }
    return $false
} -ErrorMessage "ORACLE_HOME environment variable not set or path doesn't exist" `
  -SuccessMessage "Oracle Client at $oracleHome"

# 6. Azure login status
Test-Requirement -Name "Azure Authentication" -Check {
    $account = az account show 2>$null | ConvertFrom-Json
    if ($account) {
        $script:azAccount = $account.name
        return $true
    }
    return $false
} -ErrorMessage "Not logged into Azure. Run: az login" `
  -SuccessMessage "Logged in as $azAccount"

# 7. Repository structure
Test-Requirement -Name "Repository Structure" -Check {
    $repoPath = "C:\PROJECTS\V5.WebServices.PrevalidationWS"
    $requiredPaths = @(
        "$repoPath\cortex\plan",
        "$repoPath\Business",
        "$repoPath\WebService",
        "$repoPath\PSFPreValidationTests"
    )
    
    $missing = $requiredPaths | Where-Object { -not (Test-Path $_) }
    if ($missing.Count -eq 0) {
        return $true
    } else {
        Write-Host "   Missing paths:" -ForegroundColor Yellow
        $missing | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
        return $false
    }
} -ErrorMessage "Required repository structure incomplete" `
  -SuccessMessage "Repository structure valid"

# 8. Planning documents
Test-Requirement -Name "Planning Documents" -Check {
    $planPath = "C:\PROJECTS\V5.WebServices.PrevalidationWS\cortex\plan"
    $requiredDocs = @(
        "$planPath\MODERNIZATION-PLAN.md",
        "$planPath\current-state-analysis.md",
        "$planPath\asmx-rest-contract-mapping.md"
    )
    
    $missing = $requiredDocs | Where-Object { -not (Test-Path $_) }
    if ($missing.Count -eq 0) {
        return $true
    } else {
        Write-Host "   Missing documents:" -ForegroundColor Yellow
        $missing | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
        return $false
    }
} -ErrorMessage "Required planning documents missing" `
  -SuccessMessage "All planning documents present"

# Summary
Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "  Pre-Flight Check Summary" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

$passed = ($results | Where-Object { $_.Status -eq "PASS" }).Count
$failed = ($results | Where-Object { $_.Status -eq "FAIL" }).Count
$total = $results.Count

Write-Host "`nPassed: $passed/$total" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Yellow" })
Write-Host "Failed: $failed/$total" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })

if ($failed -gt 0) {
    Write-Host "`n❌ Pre-flight check FAILED. Fix issues before starting Phase 1." -ForegroundColor Red
    Write-Host "`nFailed Checks:" -ForegroundColor Yellow
    $results | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
        Write-Host "  - $($_.Name): $($_.Message)" -ForegroundColor Red
    }
    exit 1
} else {
    Write-Host "`n✅ Pre-flight check PASSED. Ready to start Phase 1!" -ForegroundColor Green
    exit 0
}
```

---

## 🎯 Deliverables

**Phase 0 Outputs:**
1. ✅ Pre-flight verification script (above)
2. ✅ Environment setup documentation (this file)
3. ⏳ Risk register initialized (see risk-register.md)
4. ⏳ Team training completed (38 lessons learned reviewed)
5. ⏳ All 16 sub-plans created
6. ⏳ Master plan links updated

**Sign-Off Criteria:**
- [ ] Pre-flight script passes 100% on all dev machines
- [ ] All developers have completed RA lessons learned review
- [ ] Risk register has all 38 lessons logged as preventive controls
- [ ] Azure DevOps pipeline skeleton created and tested
- [ ] Database connectivity confirmed from dev environment

**Estimated Duration:** 2-3 days (not counted in 19-week timeline)

---

## 📊 Update Master Plan Progress

**BEFORE proceeding to Phase 1:**

1. Update `MODERNIZATION-PLAN.md` progress tracker:
   ```
   PHASE 0: PRE-FLIGHT & PLANNING [██████████] 100% ✅ Complete
   ```

2. Update Phase 0 checklist to all `[x]` completed

3. Update BLOCKER-001 status:
   ```markdown
   ### BLOCKER-001: .NET SDK Not Installed ✅
   **Status:** ✅ **RESOLVED** - SDK 8.0.x installed
   ```

4. Update overall progress:
   ```
   OVERALL PROGRESS: ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 1/11 Phases (9%)
   ```

---

## 📋 Related Documents

- [Master Plan](MODERNIZATION-PLAN.md) - Overall project plan
- [Risk Register](risk-register.md) - All 38 lessons as preventive controls
- [Lessons Learned](prevalidation-ws-migration-lessons-learned-plan.md) - RA migration insights
- [Test Strategy](test-strategy.md) - TDD workflow and coverage gates

---

**Next Phase:** [Phase 1: Foundation & Infrastructure](phase-1-foundation.md)
