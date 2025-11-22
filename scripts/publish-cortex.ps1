<#
.SYNOPSIS
    Publish CORTEX 3.0 to publish/CORTEX folder

.DESCRIPTION
    Creates a clean production package with ONLY CORTEX 3.0 files.
    No KDS, no dev files, no tests. Pure production code.

.EXAMPLE
    .\scripts\publish-cortex.ps1 -Force
#>

[CmdletBinding()]
param([switch]$Force)

$ErrorActionPreference = "Stop"

function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }

Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     📦 PUBLISH CORTEX 3.0                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if (-not (Test-Path "cortex-brain")) {
    Write-Error "Not in CORTEX root"
    exit 1
}

if (-not $Force) {
    $response = Read-Host "Rebuild publish/CORTEX? (yes/NO)"
    if ($response -ne 'yes') { exit 0 }
}

# Clean publish/CORTEX
Write-Info "🗑️  Step 1/6: Cleaning publish/CORTEX"
if (Test-Path "publish/CORTEX") {
    Remove-Item "publish/CORTEX" -Recurse -Force
}
New-Item -ItemType Directory -Path "publish/CORTEX" -Force | Out-Null
Write-Success "✅ Clean slate ready`n"

# Copy files with explicit paths (no wildcards that match everything)
Write-Info "📦 Step 2/6: Copying CORTEX 3.0 files"

$copies = @(
    # Root files
    @{Src="LICENSE"; Dst="publish/CORTEX/LICENSE"},
    @{Src="requirements.txt"; Dst="publish/CORTEX/requirements.txt"},
    @{Src="cortex-operations.yaml"; Dst="publish/CORTEX/cortex-operations.yaml"},
    @{Src="cortex.config.template.json"; Dst="publish/CORTEX/cortex.config.template.json"},
    @{Src="setup.py"; Dst="publish/CORTEX/setup.py"},
    
    # Directories (recursive)
    @{Src=".github"; Dst="publish/CORTEX/.github"; Recurse=$true},
    @{Src="cortex-brain"; Dst="publish/CORTEX/cortex-brain"; Recurse=$true},
    @{Src="prompts/shared"; Dst="publish/CORTEX/prompts/shared"; Recurse=$true},
    @{Src="src"; Dst="publish/CORTEX/src"; Recurse=$true},
    @{Src="scripts/cortex"; Dst="publish/CORTEX/scripts/cortex"; Recurse=$true}
)

$count = 0
foreach ($copy in $copies) {
    if (Test-Path $copy.Src) {
        $targetDir = Split-Path $copy.Dst -Parent
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        
        if ($copy.Recurse) {
            Copy-Item $copy.Src $copy.Dst -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            Copy-Item $copy.Src $copy.Dst -Force
        }
        $count++
    }
}

# Clean up unwanted files
Write-Host "  Copied $count source items" -ForegroundColor Gray

Write-Info "  Step 2b/6: Cleaning up dev files"
$cleanup = @("__pycache__", "*.pyc", ".pytest_cache", "test_*.py", "*_test.py", ".venv", "node_modules", "dist", "build", "*.backup")
$cleanedCount = 0
foreach ($pattern in $cleanup) {
    $items = Get-ChildItem "publish/CORTEX" -Recurse -Force -ErrorAction SilentlyContinue | 
        Where-Object { $_.Name -like $pattern }
    $cleanedCount += $items.Count
    $items | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host "  Removed $cleanedCount dev/test files" -ForegroundColor Gray

Write-Success "✅ Copied $count source items`n"

# Create SETUP guide
Write-Info "📝 Step 3/6: Creating SETUP-FOR-COPILOT.md"

$setup = @"
# CORTEX 3.0 Setup Guide

## ⚡ Quick Start

### Step 1: Copy CORTEX to Your Application

``````bash
# Windows
xcopy /E /I /H /Y D:\path\to\publish\CORTEX C:\your-app\cortex

# Unix/Mac
cp -r /path/to/publish/CORTEX ./cortex
``````

### Step 2: Onboard with Copilot

Open your app in VS Code, then in GitHub Copilot Chat:

``````
onboard this application
``````

**Done!** CORTEX will:
- ✅ Preserve any existing knowledge graphs
- ✅ Copy entry points to your app's .github/ folder  
- ✅ Initialize brain databases (only if missing)
- ✅ Analyze your codebase
- ✅ Suggest improvements

**CORTEX NEVER deletes existing knowledge!**

---

## 🔄 Upgrading Existing Installation

Already have CORTEX? Just copy the new files over:

``````bash
# Your knowledge is safe - CORTEX preserves brain databases
xcopy /E /I /H /Y D:\path\to\publish\CORTEX C:\your-app\cortex
``````

Then in Copilot: ``upgrade cortex``

---

## 📋 Manual Setup

If auto-onboarding fails:

``````bash
cd your-app

# Copy entry points
mkdir .github\prompts
copy cortex\.github\prompts\CORTEX.prompt.md .github\prompts\
copy cortex\.github\copilot-instructions.md .github\

# Install dependencies
cd cortex
pip install -r requirements.txt

# Test in Copilot
# Type: help
``````

---

## 🆘 Troubleshooting

**Copilot doesn't find CORTEX:**
- Ensure ``cortex/.github/prompts/CORTEX.prompt.md`` exists
- Restart VS Code
- Try: ``help`` in Copilot Chat

**Worried about losing data?**
- CORTEX never deletes brain files
- All conversations and patterns preserved
- Backup if you want: ``xcopy /E /I cortex\cortex-brain cortex-brain.backup``

---

**Version:** 3.0  
**Updated:** 2025-11-22  
**🧠 CORTEX - Your Intelligent Development Partner**
"@

$setup | Out-File "publish/CORTEX/SETUP-FOR-COPILOT.md" -Encoding UTF8
Write-Success "✅ Setup guide created`n"

# Create README
Write-Info "📝 Step 4/6: Creating README.md"

$readme = @"
# CORTEX 3.0 - Intelligent Development Assistant

**Status:** 🚀 Production Ready

## What is CORTEX?

CORTEX transforms GitHub Copilot into an intelligent partner with:

- **🧠 Memory:** Persistent across sessions
- **📚 Learning:** Accumulates codebase knowledge
- **🛡️ Governance:** Enforces quality standards
- **📊 Intelligence:** Tracks metrics and patterns

## Quick Start

See **SETUP-FOR-COPILOT.md** for complete instructions.

**TL;DR:**
1. Copy this folder to your app: ``your-app/cortex/``
2. In Copilot Chat: ``onboard this application``
3. Done!

## What's Included

- **BRAIN:** 3-tier memory system
- **Governance:** 22 quality rules
- **Operations:** Setup, analysis, cleanup
- **Agents:** Code execution, testing, validation

## Requirements

- Python 3.10+
- Git
- VS Code with GitHub Copilot

---

**© 2024-2025. All rights reserved.**
"@

$readme | Out-File "publish/CORTEX/README.md" -Encoding UTF8
Write-Success "✅ README created`n"

# Verification Phase
Write-Info "🔍 Step 6/6: Verifying Package Integrity"

$verificationResults = @{
    Passed = @()
    Failed = @()
    Warnings = @()
}

# 1. Check critical directories exist
Write-Host "  Checking directory structure..." -ForegroundColor Gray
$requiredDirs = @(".github/prompts", "cortex-brain", "prompts/shared", "src", "scripts/cortex")
foreach ($dir in $requiredDirs) {
    $fullPath = "publish/CORTEX/$dir"
    if (Test-Path $fullPath) {
        $verificationResults.Passed += "✓ Directory: $dir"
    } else {
        $verificationResults.Failed += "✗ Missing directory: $dir"
    }
}

# 2. Check critical files exist
Write-Host "  Checking critical files..." -ForegroundColor Gray
$requiredFiles = @{
    "Entry Point" = ".github/prompts/CORTEX.prompt.md"
    "Setup Guide" = "SETUP-FOR-COPILOT.md"
    "README" = "README.md"
    "Dependencies" = "requirements.txt"
    "Operations" = "cortex-operations.yaml"
    "Config Template" = "cortex.config.template.json"
    "Setup Script" = "setup.py"
    "Brain Rules" = "cortex-brain/brain-protection-rules.yaml"
    "Knowledge Graph" = "cortex-brain/knowledge-graph.yaml"
}

foreach ($name in $requiredFiles.Keys) {
    $file = $requiredFiles[$name]
    $fullPath = "publish/CORTEX/$file"
    if (Test-Path $fullPath) {
        # Check file is not empty
        $content = Get-Content $fullPath -Raw -ErrorAction SilentlyContinue
        if ($content -and $content.Length -gt 0) {
            $verificationResults.Passed += "✓ $name`: $file"
        } else {
            $verificationResults.Failed += "✗ Empty file: $file"
        }
    } else {
        $verificationResults.Failed += "✗ Missing file: $file"
    }
}

# 3. Check for Python source files in src
Write-Host "  Checking source code..." -ForegroundColor Gray
$pythonFiles = Get-ChildItem "publish/CORTEX/src" -Recurse -Filter "*.py" -ErrorAction SilentlyContinue
if ($pythonFiles.Count -gt 50) {
    $verificationResults.Passed += "✓ Source code: $($pythonFiles.Count) Python files"
} else {
    $verificationResults.Warnings += "⚠ Low Python file count: $($pythonFiles.Count) (expected >50)"
}

# 4. Check for test files (should be excluded)
Write-Host "  Checking for excluded content..." -ForegroundColor Gray
$testFiles = Get-ChildItem "publish/CORTEX" -Recurse -File | Where-Object { $_.Name -match "test_|_test\.py|\.pyc$|__pycache__" }
if ($testFiles.Count -eq 0) {
    $verificationResults.Passed += "✓ No test/cache files included"
} else {
    $verificationResults.Warnings += "⚠ Found $($testFiles.Count) test/cache files (should be cleaned)"
}

# 5. Check for KDS references (should be none)
Write-Host "  Checking for legacy KDS references..." -ForegroundColor Gray
$kdsFiles = Get-ChildItem "publish/CORTEX" -Recurse -File | Where-Object { $_.Name -match "kds|KDS" }
if ($kdsFiles.Count -eq 0) {
    $verificationResults.Passed += "✓ No KDS-named files"
} else {
    $verificationResults.Failed += "✗ Found $($kdsFiles.Count) KDS-named files"
}

# 6. Check file count is reasonable
$files = (Get-ChildItem "publish/CORTEX" -Recurse -File | Measure-Object).Count
if ($files -ge 300 -and $files -le 600) {
    $verificationResults.Passed += "✓ File count: $files (expected range: 300-600)"
} elseif ($files -lt 300) {
    $verificationResults.Failed += "✗ File count too low: $files (expected ≥300)"
} else {
    $verificationResults.Warnings += "⚠ File count high: $files (expected ≤600)"
}

# 7. Check package size is reasonable
$size = [math]::Round((Get-ChildItem "publish/CORTEX" -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
if ($size -ge 1 -and $size -le 10) {
    $verificationResults.Passed += "✓ Package size: $size MB (expected 1-10 MB)"
} elseif ($size -lt 1) {
    $verificationResults.Failed += "✗ Package too small: $size MB"
} else {
    $verificationResults.Warnings += "⚠ Package large: $size MB (expected ≤10 MB)"
}

# 8. Verify SETUP guide has correct instructions
Write-Host "  Validating setup documentation..." -ForegroundColor Gray
$setupContent = Get-Content "publish/CORTEX/SETUP-FOR-COPILOT.md" -Raw -ErrorAction SilentlyContinue
if ($setupContent) {
    if ($setupContent -match "onboard this application" -and $setupContent -match "cortex/.github/prompts/CORTEX.prompt.md") {
        $verificationResults.Passed += "✓ Setup guide has correct instructions"
    } else {
        $verificationResults.Warnings += "⚠ Setup guide may need review"
    }
} else {
    $verificationResults.Failed += "✗ Setup guide not readable"
}

Write-Success "✅ Verification complete`n"

# Display results
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      PACKAGE VERIFICATION REPORT          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Show passed checks
if ($verificationResults.Passed.Count -gt 0) {
    Write-Host "✅ Passed Checks ($($verificationResults.Passed.Count)):" -ForegroundColor Green
    foreach ($item in $verificationResults.Passed) {
        Write-Host "   $item" -ForegroundColor Gray
    }
    Write-Host ""
}

# Show warnings
if ($verificationResults.Warnings.Count -gt 0) {
    Write-Host "⚠️  Warnings ($($verificationResults.Warnings.Count)):" -ForegroundColor Yellow
    foreach ($item in $verificationResults.Warnings) {
        Write-Host "   $item" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Show failures
if ($verificationResults.Failed.Count -gt 0) {
    Write-Host "❌ Failed Checks ($($verificationResults.Failed.Count)):" -ForegroundColor Red
    foreach ($item in $verificationResults.Failed) {
        Write-Host "   $item" -ForegroundColor Red
    }
    Write-Host ""
}

# Final verdict
$totalChecks = $verificationResults.Passed.Count + $verificationResults.Failed.Count + $verificationResults.Warnings.Count
$passRate = [math]::Round(($verificationResults.Passed.Count / $totalChecks) * 100, 1)

if ($verificationResults.Failed.Count -eq 0) {
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║    ✅ PACKAGE READY FOR PRODUCTION        ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "📦 Package Details:" -ForegroundColor Cyan
    Write-Host "  Location:    publish/CORTEX/" -ForegroundColor Gray
    Write-Host "  Files:       $files" -ForegroundColor Gray
    Write-Host "  Size:        $size MB" -ForegroundColor Gray
    Write-Host "  Pass Rate:   $passRate%" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "🚀 Deployment Instructions:" -ForegroundColor Cyan
    Write-Host "  1. Copy to target:" -ForegroundColor Gray
    Write-Host "     xcopy /E /I /H /Y publish\CORTEX C:\target-app\cortex" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  2. In target app, open VS Code Copilot Chat:" -ForegroundColor Gray
    Write-Host "     'onboard this application'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "✨ CORTEX preserves existing knowledge - upgrades are safe!`n" -ForegroundColor Cyan
    
    exit 0
} else {
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║    ❌ PACKAGE HAS CRITICAL ISSUES         ║" -ForegroundColor Red
    Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Red
    
    Write-Host "⚠️  Package cannot be deployed until issues are fixed." -ForegroundColor Yellow
    Write-Host "   Review the failed checks above and re-run publish.`n" -ForegroundColor Gray
    
    exit 1
}
