# CORTEX Git Exclude Setup Script (PowerShell)
# Configures .git/info/exclude to hide CORTEX files from git status
#
# Author: Asif Hussain
# Copyright: © 2024-2025 Asif Hussain. All rights reserved.
# License: Proprietary

$ErrorActionPreference = "Stop"

Write-Host "🔧 Configuring Git local exclude for CORTEX..." -ForegroundColor Cyan

# Find repository root
try {
    $repoRoot = git rev-parse --show-toplevel 2>$null
    if (-not $repoRoot) { $repoRoot = Get-Location }
} catch {
    $repoRoot = Get-Location
}

$excludeFile = Join-Path $repoRoot ".git\info\exclude"

# Check if .git exists
if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
    Write-Host "❌ Not a Git repository. Run this from within a Git repository." -ForegroundColor Red
    exit 1
}

# Ensure .git/info directory exists
$infoDir = Join-Path $repoRoot ".git\info"
if (-not (Test-Path $infoDir)) {
    New-Item -ItemType Directory -Path $infoDir -Force | Out-Null
}

# Check if CORTEX exclusions already exist
if (Test-Path $excludeFile) {
    $content = Get-Content $excludeFile -Raw -ErrorAction SilentlyContinue
    if ($content -match "CORTEX AI Assistant") {
        Write-Host "✅ CORTEX exclusions already configured" -ForegroundColor Green
        exit 0
    }
}

# Add CORTEX exclusions
$exclusions = @"

# CORTEX AI Assistant - Local exclusion (not visible in git status)
# These files are already in .gitignore but this removes them from untracked status entirely
CORTEX/
.github/prompts/CORTEX.prompt.md
.github/prompts/cortex-story-builder.md
.github/prompts/modules/
.github/copilot-instructions.md
"@

Add-Content -Path $excludeFile -Value $exclusions

Write-Host "✅ Git local exclude configured successfully" -ForegroundColor Green
Write-Host "📊 Untracked file count should now be zero or near-zero" -ForegroundColor Cyan
Write-Host ""
Write-Host "Verify with: git status --porcelain" -ForegroundColor Yellow
