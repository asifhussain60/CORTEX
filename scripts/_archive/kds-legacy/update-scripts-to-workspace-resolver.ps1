# Update all KDS scripts to use workspace resolver
# This script systematically updates all scripts to use dynamic path resolution

param(
    [switch]$DryRun,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Import workspace resolver
. (Join-Path $PSScriptRoot "lib\workspace-resolver.ps1")

Write-Host "🔄 Updating KDS Scripts to use Workspace Resolver" -ForegroundColor Cyan
Write-Host ""

$scriptsToUpdate = @(
    "run-migration.ps1",
    "fix-github-references.ps1",
    "sensors\query-knowledge-graph.ps1",
    "crawlers\orchestrator.ps1",
    "crawlers\ui-crawler.ps1",
    "brain-amnesia.ps1",
    "brain-crawler.ps1",
    "setup-kds-branch-protection.ps1",
    "sensors\scan-ui.ps1",
    "sensors\scan-routes.ps1",
    "sensors\scan-database.ps1",
    "run-health-checks.ps1",
    "open-dashboard.ps1",
    "launch-dashboard.ps1",
    "generate-monitoring-dashboard.ps1",
    "corpus-callosum\send-message.ps1",
    "corpus-callosum\clear-queue.ps1",
    "corpus-callosum\receive-message.ps1",
    "commit-kds-changes.ps1",
    "collect-pr-intelligence.ps1"
)

$updated = 0
$failed = 0
$skipped = 0

foreach ($scriptRelPath in $scriptsToUpdate) {
    $scriptPath = Join-Path (Get-KdsRoot) "scripts\$scriptRelPath"
    
    if (-not (Test-Path $scriptPath)) {
        Write-Host "⚠️  Skipped: $scriptRelPath (not found)" -ForegroundColor Yellow
        $skipped++
        continue
    }
    
    Write-Host "📝 Processing: $scriptRelPath"
    
    try {
        $content = Get-Content $scriptPath -Raw
        $originalContent = $content
        $modified = $false
        
        # Pattern 1: Hard-coded paths like "D:\PROJECTS\NOOR CANVAS"
        if ($content -match 'D:\\PROJECTS\\NOOR CANVAS|d:\\PROJECTS\\NOOR CANVAS') {
            Write-Host "  → Found hard-coded path pattern" -ForegroundColor Yellow
            
            # Check if workspace resolver is already imported
            if ($content -notmatch '\..*workspace-resolver\.ps1') {
                # Add import after param block or at start
                if ($content -match '(?s)(param\s*\([^\)]*\))') {
                    $paramBlock = $Matches[1]
                    $content = $content -replace [regex]::Escape($paramBlock), "$paramBlock`n`n# Import workspace resolver`n. (Join-Path `$PSScriptRoot `"lib\workspace-resolver.ps1`")`n"
                }
                elseif ($content -match '^(\$ErrorActionPreference)') {
                    $content = "# Import workspace resolver`n. (Join-Path `$PSScriptRoot `"lib\workspace-resolver.ps1`")`n`n$content"
                }
                else {
                    $content = "# Import workspace resolver`n. (Join-Path `$PSScriptRoot `"lib\workspace-resolver.ps1`")`n`n$content"
                }
            }
            
            # Replace hard-coded paths
            $content = $content -replace '\$baseDir\s*=\s*"D:\\PROJECTS\\NOOR CANVAS"', '$baseDir = Get-WorkspaceRoot'
            $content = $content -replace '\$WorkspaceRoot\s*=\s*"d:\\PROJECTS\\NOOR CANVAS"', '$WorkspaceRoot = Get-WorkspaceRoot'
            $content = $content -replace '\$WorkspaceRoot\s*=\s*"D:\\PROJECTS\\NOOR CANVAS"', '$WorkspaceRoot = Get-WorkspaceRoot'
            $content = $content -replace '\$kdsPath\s*=\s*"D:\\PROJECTS\\NOOR CANVAS\\KDS"', '$kdsPath = Get-KdsRoot'
            $content = $content -replace '\$workspaceRoot\s*=\s*"d:\\PROJECTS\\DevProjects"', '$workspaceRoot = Get-WorkspaceRoot'
            
            # Replace inline references in strings (more complex)
            $content = $content -replace '"D:\\PROJECTS\\NOOR CANVAS\\KDS', '"$(Get-KdsRoot)'
            $content = $content -replace '"D:\\PROJECTS\\NOOR CANVAS', '"$(Get-WorkspaceRoot)'
            
            $modified = $true
        }
        
        # Pattern 2: Complex Split-Path chains
        if ($content -match 'Split-Path.*Split-Path.*Split-Path.*\$PSScriptRoot') {
            Write-Host "  → Found complex Split-Path chain" -ForegroundColor Yellow
            
            # Add import if not present
            if ($content -notmatch '\..*workspace-resolver\.ps1') {
                if ($content -match '^(\$ErrorActionPreference)') {
                    $content = "# Import workspace resolver`n. (Join-Path `$PSScriptRoot `"lib\workspace-resolver.ps1`")`n`n$content"
                }
                else {
                    $content = "# Import workspace resolver`n. (Join-Path `$PSScriptRoot `"lib\workspace-resolver.ps1`")`n`n$content"
                }
            }
            
            # Replace Split-Path chains
            $content = $content -replace '\$workspaceRoot\s*=\s*Split-Path.*Split-Path.*\$PSScriptRoot.*', '$workspaceRoot = Get-WorkspaceRoot'
            $content = $content -replace '\$WorkspaceRoot\s*=\s*Split-Path.*Split-Path.*\$PSScriptRoot.*', '$WorkspaceRoot = Get-WorkspaceRoot'
            $content = $content -replace '\$scriptDir\s*=.*\$PSScriptRoot.*[\r\n]+\$workspaceRoot\s*=\s*Split-Path.*', '$scriptDir = $PSScriptRoot' + "`n" + '$workspaceRoot = Get-WorkspaceRoot'
            
            $modified = $true
        }
        
        if ($modified) {
            if ($DryRun) {
                Write-Host "  ✅ Would update (dry run)" -ForegroundColor Green
            }
            else {
                Set-Content -Path $scriptPath -Value $content -NoNewline
                Write-Host "  ✅ Updated successfully" -ForegroundColor Green
            }
            $updated++
        }
        else {
            Write-Host "  ℹ️  No changes needed" -ForegroundColor Blue
            $skipped++
        }
    }
    catch {
        Write-Host "  ❌ Failed: $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Updated: $updated" -ForegroundColor Green
Write-Host "  Skipped: $skipped" -ForegroundColor Yellow
Write-Host "  Failed: $failed" -ForegroundColor Red

if ($DryRun) {
    Write-Host ""
    Write-Host "ℹ️  Dry run complete. No files were modified." -ForegroundColor Blue
}

exit $(if ($failed -eq 0) { 0 } else { 1 })
