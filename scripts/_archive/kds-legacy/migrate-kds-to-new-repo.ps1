<#
.SYNOPSIS
    Migrate KDS folder to dedicated repository with full git history

.DESCRIPTION
    Uses git filter-branch to extract KDS subfolder history and push to new repo.
    Preserves commits, authors, timestamps, and all KDS-related history.
    
.PARAMETER NewRepoUrl
    GitHub repository URL for new KDS repository (default: https://github.com/asifhussain60/KDS.git)

.PARAMETER TempDir
    Temporary directory for migration work (auto-generated if not specified)

.PARAMETER SkipPush
    If specified, prepares migration but doesn't push to GitHub (for testing)

.EXAMPLE
    .\migrate-kds-to-new-repo.ps1
    
.EXAMPLE
    .\migrate-kds-to-new-repo.ps1 -SkipPush
    
.NOTES
    Version: 1.0.0
    Requires: Git installed and GitHub authentication configured
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$NewRepoUrl = "https://github.com/asifhussain60/KDS.git",
    
    [Parameter(Mandatory=$false)]
    [string]$TempDir = "$env:TEMP\KDS-migration-$(Get-Date -Format 'yyyyMMdd-HHmmss')",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipPush
)

$ErrorActionPreference = "Stop"

Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🔄 KDS Migration to Dedicated Repository" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Source: D:\PROJECTS\DevProjects\KDS" -ForegroundColor Gray
Write-Host "Destination: $NewRepoUrl" -ForegroundColor Gray
Write-Host "Temp Directory: $TempDir" -ForegroundColor Gray
Write-Host ""

# Validation
if (-not (Test-Path "D:\PROJECTS\DevProjects\.git")) {
    Write-Error "DevProjects is not a git repository"
    exit 1
}

if (-not (Test-Path "D:\PROJECTS\DevProjects\KDS")) {
    Write-Error "KDS folder not found in DevProjects"
    exit 1
}

# Confirm before proceeding
Write-Host "⚠️  This will:" -ForegroundColor Yellow
Write-Host "   1. Create temporary clone of DevProjects" -ForegroundColor Yellow
Write-Host "   2. Extract KDS folder history (rewrite git history in temp)" -ForegroundColor Yellow
Write-Host "   3. Push to new repository at $NewRepoUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "Original DevProjects repository will NOT be modified." -ForegroundColor Green
Write-Host ""

$response = Read-Host "Continue? (Y/n)"
if ($response -eq 'n' -or $response -eq 'N') {
    Write-Host "Migration cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# Step 1: Create temporary clone
Write-Host "[1/8] Creating temporary clone..." -ForegroundColor Yellow
try {
    git clone "D:\PROJECTS\DevProjects" $TempDir 2>&1 | Out-Null
    Write-Host "  ✅ Cloned to: $TempDir" -ForegroundColor Green
} catch {
    Write-Error "Failed to clone repository: $_"
    exit 1
}

Push-Location $TempDir

try {
    # Step 2: Verify KDS folder exists in clone
    Write-Host "`n[2/8] Verifying KDS folder in clone..." -ForegroundColor Yellow
    if (-not (Test-Path "KDS")) {
        throw "KDS folder not found in clone"
    }
    
    $kdsFileCount = (Get-ChildItem -Path "KDS" -Recurse -File).Count
    Write-Host "  ✅ KDS folder found ($kdsFileCount files)" -ForegroundColor Green

    # Step 3: Filter to keep only KDS folder history
    Write-Host "`n[3/8] Extracting KDS folder history..." -ForegroundColor Yellow
    Write-Host "  ⚠️  This will rewrite git history (temp clone only)" -ForegroundColor Yellow
    Write-Host "  ⏱️  May take 2-5 minutes depending on history size..." -ForegroundColor Gray
    
    # Use git filter-branch to extract subdirectory
    git filter-branch --subdirectory-filter KDS --prune-empty -- --all 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        throw "Git filter-branch failed"
    }
    
    Write-Host "  ✅ History extracted successfully" -ForegroundColor Green

    # Step 4: Clean up refs
    Write-Host "`n[4/8] Cleaning up git refs..." -ForegroundColor Yellow
    
    git for-each-ref --format="%(refname)" refs/original/ | ForEach-Object {
        git update-ref -d $_ 2>&1 | Out-Null
    }
    
    git reflog expire --expire=now --all 2>&1 | Out-Null
    git gc --prune=now --aggressive 2>&1 | Out-Null
    
    Write-Host "  ✅ Refs cleaned" -ForegroundColor Green

    # Step 5: Verify extraction
    Write-Host "`n[5/8] Verifying extraction..." -ForegroundColor Yellow
    
    $commitCount = (git rev-list --count HEAD)
    $rootFiles = (Get-ChildItem -Path "." -File).Count
    $rootDirs = (Get-ChildItem -Path "." -Directory | Where-Object { $_.Name -ne '.git' }).Count
    
    Write-Host "  Total commits: $commitCount" -ForegroundColor Green
    Write-Host "  Root files: $rootFiles" -ForegroundColor Green
    Write-Host "  Root directories: $rootDirs" -ForegroundColor Green
    
    # Verify expected KDS structure
    $expectedDirs = @('brain', 'docs', 'prompts', 'scripts', 'cortex-brain')
    $missingDirs = @()
    foreach ($dir in $expectedDirs) {
        if (-not (Test-Path $dir)) {
            $missingDirs += $dir
        }
    }
    
    if ($missingDirs.Count -gt 0) {
        Write-Warning "Missing expected directories: $($missingDirs -join ', ')"
    } else {
        Write-Host "  ✅ All expected KDS directories present" -ForegroundColor Green
    }

    # Step 6: Update remote
    Write-Host "`n[6/8] Updating git remote..." -ForegroundColor Yellow
    
    git remote remove origin 2>&1 | Out-Null
    git remote add origin $NewRepoUrl 2>&1 | Out-Null
    
    $remoteUrl = git config --get remote.origin.url
    Write-Host "  New remote: $remoteUrl" -ForegroundColor Green

    # Step 7: Rename branch to main
    Write-Host "`n[7/8] Setting up main branch..." -ForegroundColor Yellow
    
    $currentBranch = git branch --show-current
    if ($currentBranch -ne "main") {
        git branch -M main 2>&1 | Out-Null
    }
    
    Write-Host "  ✅ Branch: main" -ForegroundColor Green

    # Step 8: Push to new repository
    if (-not $SkipPush) {
        Write-Host "`n[8/8] Pushing to new repository..." -ForegroundColor Yellow
        Write-Host "  URL: $NewRepoUrl" -ForegroundColor Gray
        Write-Host "  ⚠️  Ensure repository exists and you have push permissions" -ForegroundColor Yellow
        Write-Host ""
        
        $pushResponse = Read-Host "  Ready to push? (Y/n)"
        if ($pushResponse -eq 'n' -or $pushResponse -eq 'N') {
            Write-Host ""
            Write-Host "Push cancelled. Temp directory preserved for manual push:" -ForegroundColor Yellow
            Write-Host "  $TempDir" -ForegroundColor Gray
            Write-Host ""
            Write-Host "To push manually:" -ForegroundColor Cyan
            Write-Host "  cd $TempDir" -ForegroundColor White
            Write-Host "  git push -u origin main --force" -ForegroundColor White
            Pop-Location
            exit 0
        }
        
        Write-Host ""
        
        # Push main branch
        git push -u origin main --force
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to push to new repository. Please check: `n  1. Repository exists at $NewRepoUrl`n  2. You have push permissions`n  3. GitHub authentication is configured"
        }
        
        Write-Host "  ✅ Main branch pushed successfully" -ForegroundColor Green
        
        # Push other branches if any
        $branches = git branch -r | Where-Object { $_ -notmatch 'origin/HEAD' -and $_ -notmatch 'origin/main' }
        if ($branches) {
            Write-Host "  Pushing additional branches..." -ForegroundColor Gray
            git push origin --all --force 2>&1 | Out-Null
        }
        
        # Push tags if any
        $tags = git tag
        if ($tags) {
            Write-Host "  Pushing tags..." -ForegroundColor Gray
            git push origin --tags --force 2>&1 | Out-Null
        }
        
    } else {
        Write-Host "`n[8/8] Skipping push (test mode)" -ForegroundColor Yellow
        Write-Host "  Migration prepared in: $TempDir" -ForegroundColor Gray
        Write-Host "  To push manually:" -ForegroundColor Cyan
        Write-Host "    cd $TempDir" -ForegroundColor White
        Write-Host "    git push -u origin main --force" -ForegroundColor White
    }

} catch {
    Write-Error "Migration failed: $_"
    Pop-Location
    Write-Host ""
    Write-Host "Temp directory preserved for debugging: $TempDir" -ForegroundColor Yellow
    exit 1
}

Pop-Location

# Success summary
Write-Host ""
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ Migration Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Migration Summary:" -ForegroundColor Cyan
Write-Host "  Source: D:\PROJECTS\DevProjects\KDS" -ForegroundColor White
Write-Host "  Destination: $NewRepoUrl" -ForegroundColor White
Write-Host "  Commits migrated: $commitCount" -ForegroundColor White
Write-Host "  Files migrated: $kdsFileCount" -ForegroundColor White
Write-Host ""

if (-not $SkipPush) {
    Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Verify new repository:" -ForegroundColor White
    Write-Host "     https://github.com/asifhussain60/KDS" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Clone to new location:" -ForegroundColor White
    Write-Host "     cd D:\PROJECTS" -ForegroundColor Gray
    Write-Host "     git clone $NewRepoUrl" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Configure git hooks:" -ForegroundColor White
    Write-Host "     cd D:\PROJECTS\KDS" -ForegroundColor Gray
    Write-Host "     Copy-Item hooks\pre-commit .git\hooks\ -Force" -ForegroundColor Gray
    Write-Host "     Copy-Item hooks\post-merge .git\hooks\ -Force" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  4. Delete KDS from DevProjects:" -ForegroundColor White
    Write-Host "     cd D:\PROJECTS\DevProjects" -ForegroundColor Gray
    Write-Host "     Remove-Item KDS -Recurse -Force" -ForegroundColor Gray
    Write-Host "     git add ." -ForegroundColor Gray
    Write-Host "     git commit -m 'chore: Remove KDS (moved to dedicated repo)'" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "📁 Temp directory: $TempDir" -ForegroundColor Gray
Write-Host "   (Can be deleted after verification)" -ForegroundColor Gray
Write-Host ""

# Offer to clean up temp directory
if (-not $SkipPush) {
    $cleanup = Read-Host "Delete temp directory now? (y/N)"
    if ($cleanup -eq 'y' -or $cleanup -eq 'Y') {
        Remove-Item -Path $TempDir -Recurse -Force
        Write-Host "  ✅ Temp directory deleted" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
