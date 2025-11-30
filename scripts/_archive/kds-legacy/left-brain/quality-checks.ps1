# Quality Checks Script
# Purpose: Perform code quality checks during REFACTOR phase
# Validates: Formatting, documentation, complexity, etc.

param(
    [Parameter(Mandatory=$true)]
    [string]$File
)

$ErrorActionPreference = "Stop"

if ($env:KDS_VERBOSE) {
    Write-Host "`n📊 Running Quality Checks" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "File: $File" -ForegroundColor Gray
}

$checks = @{
    has_documentation = $false
    has_proper_formatting = $false
    complexity_acceptable = $false
    follows_conventions = $false
}

try {
    if (-not (Test-Path $File)) {
        throw "File not found: $File"
    }
    
    $content = Get-Content $File -Raw
    
    # Check 1: Documentation
    if ($content -match '///\s*<summary>') {
        $checks.has_documentation = $true
        if ($env:KDS_VERBOSE) {
            Write-Host "  ✅ Has XML documentation" -ForegroundColor Green
        }
    } else {
        if ($env:KDS_VERBOSE) {
            Write-Host "  ⚠️  Missing XML documentation" -ForegroundColor Yellow
        }
    }
    
    # Check 2: Formatting
    if ($content -notmatch '\s{4,}') {  # No excessive whitespace
        $checks.has_proper_formatting = $true
        if ($env:KDS_VERBOSE) {
            Write-Host "  ✅ Proper formatting" -ForegroundColor Green
        }
    }
    
    # Check 3: Complexity (simple heuristic)
    $lineCount = ($content -split "`n").Count
    if ($lineCount -lt 200) {  # Simple complexity check
        $checks.complexity_acceptable = $true
        if ($env:KDS_VERBOSE) {
            Write-Host "  ✅ Complexity acceptable ($lineCount lines)" -ForegroundColor Green
        }
    }
    
    # Check 4: Naming conventions
    if ($content -match 'public\s+(class|interface|enum)') {
        $checks.follows_conventions = $true
        if ($env:KDS_VERBOSE) {
            Write-Host "  ✅ Follows naming conventions" -ForegroundColor Green
        }
    }
    
    $allChecksPassed = $checks.Values | Where-Object { $_ -eq $false } | Measure-Object | Select-Object -ExpandProperty Count
    $passedCount = ($checks.Values | Where-Object { $_ -eq $true } | Measure-Object | Select-Object -ExpandProperty Count)
    
    if ($env:KDS_VERBOSE) {
        Write-Host "`n  Quality Score: $passedCount/4 checks passed" -ForegroundColor $(if ($passedCount -ge 3) { "Green" } else { "Yellow" })
    }
    
    return @{
        checks = $checks
        passed_count = $passedCount
        total_checks = 4
        quality_score = [math]::Round(($passedCount / 4) * 100, 0)
    }
    
} catch {
    throw "Quality checks failed: $($_.Exception.Message)"
}
