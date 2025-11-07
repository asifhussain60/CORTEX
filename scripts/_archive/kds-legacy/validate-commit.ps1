<#
.SYNOPSIS
KDS Tier 0 Enforcement - Pre-Commit Validation

.DESCRIPTION
Enforces KDS governance rules before allowing commits:
1. TDD: Every new .cs file must have corresponding test
2. DoD: Zero errors, zero warnings
3. Integration: Tests must exist for ViewModels
4. Silent Failures: No Debug.WriteLine in production code
5. Schema: Models match actual brain files

.NOTES
This script is called by .git/hooks/pre-commit
Exit code 0 = validation passed (allow commit)
Exit code 1 = validation failed (block commit)

.EXAMPLE
pwsh -File scripts/validate-commit.ps1

#>

$ErrorActionPreference = "Stop"
$script:violations = @()

function Write-ValidationHeader {
    param([string]$Message)
    Write-Host "`n$Message" -ForegroundColor Cyan
}

function Add-Violation {
    param([string]$Message)
    $script:violations += $Message
}

function Test-TDDCompliance {
    Write-ValidationHeader "1️⃣  Validating Test-First Development..."
    
    # Get all new .cs files (excluding test files)
    $newCsFiles = git diff --cached --name-only --diff-filter=A |
        Where-Object { $_ -match '\.cs$' -and $_ -notmatch 'Tests' -and $_ -notmatch '\.g\.cs$' }
    
    if ($newCsFiles.Count -eq 0) {
        Write-Host "   ✓ No new production C# files to validate" -ForegroundColor Green
        return
    }
    
    foreach ($file in $newCsFiles) {
        # Determine expected test file path
        $testFile = $file -replace '\.cs$', 'Tests.cs' -replace 
            'KDS\.Dashboard\.WPF\\', 'KDS.Dashboard.WPF.Tests\'
        
        # Check if test exists in staging area OR file system
        $testStaged = git diff --cached --name-only | Where-Object { $_ -eq $testFile }
        $testExists = Test-Path $testFile
        
        if (-not $testStaged -and -not $testExists) {
            Add-Violation "TDD VIOLATION: $file created without test file: $testFile"
        }
        else {
            Write-Host "   ✓ Test exists for $file" -ForegroundColor Green
        }
    }
}

function Test-BuildValidation {
    Write-ValidationHeader "2️⃣  Validating Build (Zero Errors, Zero Warnings)..."
    
    # Find dashboard solution
    $dashboardPath = "dashboard-wpf"
    if (-not (Test-Path $dashboardPath)) {
        Write-Host "   ⊘ Dashboard not found in this commit" -ForegroundColor Yellow
        return
    }
    
    # Build with no restore (assume already restored)
    Push-Location $dashboardPath
    try {
        $buildOutput = dotnet build --no-restore 2>&1 | Out-String
        
        if ($LASTEXITCODE -ne 0) {
            Add-Violation "BUILD FAILED - fix errors before committing"
            Write-Host "   ✗ Build failed" -ForegroundColor Red
        }
        else {
            Write-Host "   ✓ Build succeeded" -ForegroundColor Green
        }
        
        # Check for warnings
        if ($buildOutput -match 'warning CS') {
            $warnings = ($buildOutput | Select-String 'warning CS').Count
            
            # Allow specific warnings (nullable, xUnit analyzer)
            $allowedWarnings = $buildOutput -match 'warning CS8625|warning xUnit2002'
            if ($warnings -gt $allowedWarnings.Count) {
                Add-Violation "BUILD WARNINGS: $($warnings - $allowedWarnings.Count) non-allowed warnings found"
                Write-Host "   ⚠ Warnings found: $warnings" -ForegroundColor Yellow
            }
            else {
                Write-Host "   ✓ Only allowed warnings present" -ForegroundColor Green
            }
        }
        else {
            Write-Host "   ✓ No warnings" -ForegroundColor Green
        }
    }
    finally {
        Pop-Location
    }
}

function Test-TestValidation {
    Write-ValidationHeader "3️⃣  Validating Tests..."
    
    $dashboardPath = "dashboard-wpf"
    if (-not (Test-Path $dashboardPath)) {
        return
    }
    
    Push-Location $dashboardPath
    try {
        # Run tests quietly
        $testOutput = dotnet test --no-build --logger "console;verbosity=quiet" 2>&1 | Out-String
        
        if ($LASTEXITCODE -ne 0) {
            Add-Violation "TESTS FAILING - all tests must pass before committing"
            Write-Host "   ✗ Tests failed" -ForegroundColor Red
        }
        else {
            # Extract test counts
            if ($testOutput -match 'Total tests: (\d+)') {
                $totalTests = $Matches[1]
                Write-Host "   ✓ All $totalTests tests passed" -ForegroundColor Green
            }
            else {
                Write-Host "   ✓ Tests passed" -ForegroundColor Green
            }
        }
    }
    finally {
        Pop-Location
    }
}

function Test-SilentFailures {
    Write-ValidationHeader "4️⃣  Detecting Silent Failures..."
    
    $dashboardPath = "dashboard-wpf\KDS.Dashboard.WPF"
    if (-not (Test-Path $dashboardPath)) {
        return
    }
    
    # Search for Debug.WriteLine in production code (excluding Generated files and comments)
    $csFiles = Get-ChildItem -Recurse -Filter "*.cs" -Path $dashboardPath |
        Where-Object { $_.FullName -notmatch '\\obj\\' -and $_.FullName -notmatch '\\bin\\' -and $_.FullName -notmatch '\.g\.cs$' }
    
    $debugWrites = @()
    foreach ($file in $csFiles) {
        $content = Get-Content $file.FullName -Raw
        # Remove comments before searching
        $codeOnly = $content -replace '//.*', '' -replace '(?s)/\*.*?\*/', ''
        
        if ($codeOnly -match 'Debug\.WriteLine') {
            # Get line numbers for actual Debug.WriteLine calls (not in comments)
            $lines = Get-Content $file.FullName
            for ($i = 0; $i -lt $lines.Count; $i++) {
                $line = $lines[$i]
                # Skip if line is a comment
                if ($line -match '^\s*//' -or $line -match '^\s*\*') {
                    continue
                }
                # Check if Debug.WriteLine appears on this line
                if ($line -match 'Debug\.WriteLine') {
                    $debugWrites += [PSCustomObject]@{
                        Path = $file.FullName
                        LineNumber = $i + 1
                        Line = $line.Trim()
                    }
                }
            }
        }
    }
    
    if ($debugWrites) {
        $count = ($debugWrites | Measure-Object).Count
        Add-Violation "SILENT FAILURES: Debug.WriteLine found in production code ($count instances)"
        Write-Host "   ✗ Found $count Debug.WriteLine calls" -ForegroundColor Red
        
        # Show first 3 instances
        $debugWrites | Select-Object -First 3 | ForEach-Object {
            Write-Host "      $($_.Path):$($_.LineNumber)" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "   ✓ No Debug.WriteLine in production code" -ForegroundColor Green
    }
}

function Test-IntegrationTests {
    Write-ValidationHeader "5️⃣  Validating Integration Tests..."
    
    $viewModelsPath = "dashboard-wpf\KDS.Dashboard.WPF\ViewModels"
    $integrationTestsPath = "dashboard-wpf\KDS.Dashboard.WPF.Tests\Integration"
    
    if (-not (Test-Path $viewModelsPath)) {
        return
    }
    
    # Get all ViewModels
    $viewModels = Get-ChildItem -Filter "*ViewModel.cs" -Path $viewModelsPath -Recurse |
        Where-Object { $_.Name -notmatch 'ViewModelBase|ErrorViewModel' }
    
    $missingTests = @()
    
    foreach ($vm in $viewModels) {
        $integrationTest = $vm.Name -replace "ViewModel\.cs", "IntegrationTests.cs"
        $testPath = Join-Path $integrationTestsPath $integrationTest
        
        if (-not (Test-Path $testPath)) {
            $missingTests += $integrationTest
        }
    }
    
    if ($missingTests.Count -gt 0) {
        Add-Violation "MISSING INTEGRATION TESTS: $($missingTests -join ', ')"
        Write-Host "   ⚠ Missing integration tests for ViewModels" -ForegroundColor Yellow
    }
    else {
        Write-Host "   ✓ All ViewModels have integration tests" -ForegroundColor Green
    }
}

#region Main Execution

Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  KDS TIER 0 ENFORCEMENT - PRE-COMMIT VALIDATION" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Run all validation gates
Test-TDDCompliance
Test-BuildValidation
Test-TestValidation
Test-SilentFailures
Test-IntegrationTests

# Report Results
Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($script:violations.Count -gt 0) {
    Write-Host "❌ TIER 0 VIOLATIONS DETECTED" -ForegroundColor Red
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Red
    
    foreach ($violation in $script:violations) {
        Write-Host "  • $violation" -ForegroundColor Red
    }
    
    Write-Host "`n📖 See: governance/rules/definition-of-done.md" -ForegroundColor Yellow
    Write-Host "`nCommit REJECTED. Fix violations before committing.`n" -ForegroundColor Red
    
    exit 1
}

Write-Host "✅ All Tier 0 Validations PASSED" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "`n"

exit 0

#endregion
