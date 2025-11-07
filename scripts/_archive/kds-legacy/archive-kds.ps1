# KDS → CORTEX Archival Helper
# Safely moves legacy KDS artifacts into a dated archive folder inside the repo.
# Non-destructive: nothing is deleted; Git captures all moves.

param(
    [string]$ArchiveRoot = "_archive/20251106-kds-deprecated"
)

$ErrorActionPreference = 'Stop'

function New-DirectoryIfMissing($path) {
    if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path | Out-Null }
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Set-Location $repoRoot

New-DirectoryIfMissing $ArchiveRoot

$items = @(
    'kds-dashboard.html',
    'dashboard',
    'dashboard-wpf',
    'update-kds-story.ps1',
    'prompts/user/kds.md',
    'tests/test-dashboard-visual-loading.ps1',
    'tests/test-dashboard-refresh.ps1',
    'tests/test-dashboard-loading-states.ps1',
    'tests/test-dashboard-api.ps1',
    'scripts/open-dashboard.ps1',
    'scripts/launch-dashboard.ps1',
    'scripts/dashboard-api-server.ps1',
    'scripts/validate-kds-references.ps1'
)

$moveCount = 0
foreach ($item in $items) {
    if (Test-Path $item) {
        $dest = Join-Path $ArchiveRoot $item
        $destDir = Split-Path $dest -Parent
        New-DirectoryIfMissing $destDir
        Write-Host "→ Archiving $item → $dest" -ForegroundColor Yellow
        Move-Item -Force $item $dest
        $moveCount++
    }
}

Write-Host "\n✅ Archived $moveCount item(s) to $ArchiveRoot" -ForegroundColor Green
Write-Host "Next: commit the move and update references to CORTEX/cortex.md" -ForegroundColor Cyan
