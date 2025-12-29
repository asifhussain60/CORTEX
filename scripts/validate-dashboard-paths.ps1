#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Validate Dashboard Repository Paths

.DESCRIPTION
    Ensures all repositories in repository-registry.json exist and all data files are accessible.
    Prevents deployment of broken dashboard configurations.

.EXAMPLE
    .\validate-dashboard-paths.ps1
    
.NOTES
    Author: Asif Hussain
    Copyright: © 2025 Asif Hussain. All rights reserved.
    Version: 1.0.0
#>

$ErrorActionPreference = "Stop"
$CortexRoot = Split-Path -Parent $PSScriptRoot
$DashboardData = Join-Path $CortexRoot "cortex-brain\dashboards\data"
$RegistryFile = Join-Path $DashboardData "repository-registry.json"

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "       DASHBOARD PATH VALIDATOR v1.0.0                 " -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

# Check registry file exists
if (-not (Test-Path $RegistryFile)) {
    Write-Host "ERROR: Registry file not found: $RegistryFile" -ForegroundColor Red
    exit 1
}

Write-Host "Loading repository registry..." -ForegroundColor Yellow
$registry = Get-Content $RegistryFile | ConvertFrom-Json

$totalRepos = $registry.repositories.Count
$validRepos = 0
$errors = @()

Write-Host "Found $totalRepos repositories in registry`n" -ForegroundColor Green

foreach ($repo in $registry.repositories) {
    $repoPath = Join-Path $DashboardData "repos\$($repo.id)"
    Write-Host "Validating: $($repo.id) ..." -NoNewline
    
    # Check repository directory exists
    if (-not (Test-Path $repoPath)) {
        Write-Host " FAILED" -ForegroundColor Red
        $errors += "Repository directory not found: $repoPath"
        continue
    }
    
    # Check all declared data files exist
    $missingFiles = @()
    foreach ($file in $repo.data_file_list) {
        $filePath = Join-Path $repoPath $file
        if (-not (Test-Path $filePath)) {
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Host " FAILED" -ForegroundColor Red
        $errors += "Repository '$($repo.id)' missing files: $($missingFiles -join ', ')"
    } else {
        Write-Host " OK" -ForegroundColor Green
        $validRepos++
    }
}

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "Validation Summary:" -ForegroundColor Yellow
Write-Host "  Total Repositories: $totalRepos" -ForegroundColor White
Write-Host "  Valid: $validRepos" -ForegroundColor Green
Write-Host "  Failed: $($totalRepos - $validRepos)" -ForegroundColor $(if ($errors.Count -gt 0) { "Red" } else { "Green" })
Write-Host "========================================================`n" -ForegroundColor Cyan

if ($errors.Count -gt 0) {
    Write-Host "ERRORS FOUND:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
    Write-Host ""
    exit 1
}

Write-Host "All repository paths validated successfully!" -ForegroundColor Green
Write-Host ""
exit 0
