# CORTEX Registry Cleanup Script
# Authority: CORE-028 + User request (chat01.md digest)
# Purpose: Fix SCREAMING_CASE files, consolidate sprawl, implement auto-status updates

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔧 CORTEX Registry Holistic Cleanup" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Phase 1: SCREAMING_CASE Remediation
Write-Host "📝 Phase 1: Renaming SCREAMING_CASE files..." -ForegroundColor Yellow

$files = Get-ChildItem "cortex-registry\_cortex-master" -Recurse -File | 
    Where-Object { $_.Name -cmatch '[A-Z]{2,}.*[A-Z]{2,}' -and $_.Extension -in '.md','.yaml','.yml' }

$renamed = 0
$skipped = 0

foreach ($file in $files) {
    $kebab = $file.Name.ToLower() -replace '_','-' -replace '\s+','-'
    $dest = Join-Path $file.DirectoryName $kebab
    
    if (Test-Path $dest) {
        Write-Host "  ⚠️  Skip (exists): $($file.Name)" -ForegroundColor Yellow
        $skipped++
        continue
    }
    
    try {
        Move-Item -Path $file.FullName -Destination $dest -Force -ErrorAction Stop
        $renamed++
    } catch {
        Write-Host "  ❌ Failed: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
        $skipped++
    }
}

Write-Host "  ✅ Renamed: $renamed files" -ForegroundColor Green
Write-Host "  ⚠️  Skipped: $skipped files" -ForegroundColor Yellow
Write-Host ""

# Phase 2: File Count Report
Write-Host "📊 Phase 2: File count analysis..." -ForegroundColor Yellow

$totalFiles = (Get-ChildItem "cortex-registry\_cortex-master" -Recurse -File | 
    Where-Object { $_.Extension -in '.md','.yaml','.yml' }).Count
$screaming = (Get-ChildItem "cortex-registry\_cortex-master" -Recurse -File | 
    Where-Object { $_.Name -cmatch '[A-Z]{2,}.*[A-Z]{2,}' }).Count

Write-Host "  Total files: $totalFiles" -ForegroundColor White
Write-Host "  SCREAMING_CASE remaining: $screaming" -ForegroundColor $(if ($screaming -gt 0) { 'Red' } else { 'Green' })
Write-Host "  Target: ≤20 active files" -ForegroundColor Gray
Write-Host ""

# Phase 3: Summary
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ Cleanup Phase Complete" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Commit renamed files: git add -A && git commit" -ForegroundColor Gray
Write-Host "  2. Move historical files to _archive/ (manual or script)" -ForegroundColor Gray
Write-Host "  3. Create master-status.yaml as single source of truth" -ForegroundColor Gray
Write-Host ""
