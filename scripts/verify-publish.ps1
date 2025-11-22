<#
.SYNOPSIS
    Verify publish/CORTEX package integrity

.DESCRIPTION
    Runs comprehensive verification checks on publish/CORTEX to ensure
    the package is complete and production-ready.

.EXAMPLE
    .\scripts\verify-publish.ps1
#>

$ErrorActionPreference = "Stop"

function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }

Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🔍 CORTEX PACKAGE VERIFICATION           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if (-not (Test-Path "publish/CORTEX")) {
    Write-Host "❌ publish/CORTEX folder not found!" -ForegroundColor Red
    Write-Host "   Run: git checkout cce519b -- publish/CORTEX`n" -ForegroundColor Yellow
    exit 1
}

Write-Info "Running verification checks...`n"

$results = @{ Passed = @(); Failed = @(); Warnings = @() }

# Directory structure
$requiredDirs = @(".github/prompts", "cortex-brain", "prompts/shared", "src", "scripts/cortex")
foreach ($dir in $requiredDirs) {
    if (Test-Path "publish/CORTEX/$dir") {
        $results.Passed += "✓ Directory: $dir"
    } else {
        $results.Failed += "✗ Missing directory: $dir"
    }
}

# Critical files
$requiredFiles = @{
    "Entry Point" = ".github/prompts/CORTEX.prompt.md"
    "Setup Guide" = "SETUP-FOR-COPILOT.md"
    "README" = "README.md"
    "Dependencies" = "requirements.txt"
    "Operations" = "cortex-operations.yaml"
    "Config" = "cortex.config.template.json"
    "Setup Script" = "setup.py"
    "Brain Rules" = "cortex-brain/brain-protection-rules.yaml"
    "Knowledge Graph" = "cortex-brain/knowledge-graph.yaml"
}

foreach ($name in $requiredFiles.Keys) {
    $file = $requiredFiles[$name]
    if (Test-Path "publish/CORTEX/$file") {
        $content = Get-Content "publish/CORTEX/$file" -Raw -ErrorAction SilentlyContinue
        if ($content -and $content.Length -gt 0) {
            $results.Passed += "✓ $name`: $file"
        } else {
            $results.Failed += "✗ Empty file: $file"
        }
    } else {
        $results.Failed += "✗ Missing: $file"
    }
}

# Python files
$pyFiles = (Get-ChildItem "publish/CORTEX/src" -Recurse -Filter "*.py" -ErrorAction SilentlyContinue | Measure-Object).Count
if ($pyFiles -gt 50) {
    $results.Passed += "✓ Source code: $pyFiles Python files"
} else {
    $results.Warnings += "⚠ Low Python file count: $pyFiles (expected >50)"
}

# No test files
$testFiles = (Get-ChildItem "publish/CORTEX" -Recurse -File | Where-Object { $_.Name -match "test_|_test\.py|\.pyc$|__pycache__" } | Measure-Object).Count
if ($testFiles -eq 0) {
    $results.Passed += "✓ No test/cache files"
} else {
    $results.Warnings += "⚠ Found $testFiles test/cache files"
}

# No KDS files
$kdsFiles = (Get-ChildItem "publish/CORTEX" -Recurse -File | Where-Object { $_.Name -match "kds|KDS" } | Measure-Object).Count
if ($kdsFiles -eq 0) {
    $results.Passed += "✓ No KDS-named files"
} else {
    $results.Failed += "✗ Found $kdsFiles KDS-named files"
}

# File count
$files = (Get-ChildItem "publish/CORTEX" -Recurse -File | Measure-Object).Count
if ($files -ge 300 -and $files -le 600) {
    $results.Passed += "✓ File count: $files (expected 300-600)"
} elseif ($files -lt 300) {
    $results.Failed += "✗ File count too low: $files"
} else {
    $results.Warnings += "⚠ File count high: $files"
}

# Package size
$size = [math]::Round((Get-ChildItem "publish/CORTEX" -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
if ($size -ge 1 -and $size -le 10) {
    $results.Passed += "✓ Package size: $size MB (expected 1-10 MB)"
} elseif ($size -lt 1) {
    $results.Failed += "✗ Package too small: $size MB"
} else {
    $results.Warnings += "⚠ Package large: $size MB"
}

# Setup guide validation
$setup = Get-Content "publish/CORTEX/SETUP-FOR-COPILOT.md" -Raw -ErrorAction SilentlyContinue
if ($setup -match "onboard this application" -and $setup -match "cortex/.github/prompts/CORTEX.prompt.md") {
    $results.Passed += "✓ Setup guide has correct instructions"
} else {
    $results.Warnings += "⚠ Setup guide may need review"
}

# Display report
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      PACKAGE VERIFICATION REPORT          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($results.Passed.Count -gt 0) {
    Write-Host "✅ Passed Checks ($($results.Passed.Count)):" -ForegroundColor Green
    $results.Passed | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    Write-Host ""
}

if ($results.Warnings.Count -gt 0) {
    Write-Host "⚠️  Warnings ($($results.Warnings.Count)):" -ForegroundColor Yellow
    $results.Warnings | ForEach-Object { Write-Host "   $_" -ForegroundColor Yellow }
    Write-Host ""
}

if ($results.Failed.Count -gt 0) {
    Write-Host "❌ Failed Checks ($($results.Failed.Count)):" -ForegroundColor Red
    $results.Failed | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
    Write-Host ""
}

$total = $results.Passed.Count + $results.Failed.Count + $results.Warnings.Count
$passRate = [math]::Round(($results.Passed.Count / $total) * 100, 1)

if ($results.Failed.Count -eq 0) {
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║    ✅ PACKAGE READY FOR PRODUCTION        ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "📦 Package Details:" -ForegroundColor Cyan
    Write-Host "  Location:    publish/CORTEX/" -ForegroundColor Gray
    Write-Host "  Files:       $files" -ForegroundColor Gray
    Write-Host "  Size:        $size MB" -ForegroundColor Gray
    Write-Host "  Pass Rate:   $passRate%" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "🚀 Ready to Deploy:" -ForegroundColor Cyan
    Write-Host "  xcopy /E /I /H /Y publish\CORTEX C:\target-app\cortex`n" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║    ❌ PACKAGE HAS CRITICAL ISSUES         ║" -ForegroundColor Red
    Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Red
    exit 1
}
