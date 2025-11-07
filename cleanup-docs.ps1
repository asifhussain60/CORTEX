# CORTEX Documentation Cleanup Script
# Moves legacy/temporary documentation files to archive

$docsPath = "D:\PROJECTS\CORTEX\docs"
$archivePath = "D:\PROJECTS\CORTEX\docs\_archive-docs-cleanup"

Write-Host "🧹 CORTEX Documentation Cleanup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Files and folders to KEEP (based on mkdocs.yml nav)
$keepFiles = @(
    "index.md",
    "technical-styling-examples.md",
    "portability-guide.md"
)

$keepFolders = @(
    "Mind-Palace",
    "getting-started",
    "architecture",
    "tiers",
    "agents",
    "api",
    "development",
    "reference",
    "deployment",
    "stylesheets",
    "images",
    "_archive-docs-cleanup"
)

# Move unnecessary root-level files
Write-Host "📄 Moving legacy documentation files..." -ForegroundColor Yellow

$filesToMove = Get-ChildItem -Path $docsPath -File | Where-Object {
    $_.Name -notin $keepFiles -and 
    ($_.Name -like "KDS-*" -or
     $_.Name -like "*-COMPLETE.md" -or
     $_.Name -like "*-PLAN.md" -or
     $_.Name -like "*-SUMMARY.md" -or
     $_.Name -like "*-REPORT.md" -or
     $_.Name -like "TASK-*" -or
     $_.Name -like "GROUP-*" -or
     $_.Name -like "SUB-GROUP-*" -or
     $_.Name -like "WAVE-*" -or
     $_.Name -like "PHASE-*" -or
     $_.Name -like "AGENT-*" -or
     $_.Name -like "AUTOMATIC-*" -or
     $_.Name -like "BRAIN-*" -or
     $_.Name -like "COGNITIVE-*" -or
     $_.Name -like "CORTEX-*" -or
     $_.Name -like "DIRECTORY-*" -or
     $_.Name -like "GIT-*" -or
     $_.Name -like "HOLISTIC-*" -or
     $_.Name -like "IMPLEMENTATION-*" -or
     $_.Name -like "INSTALLATION-*" -or
     $_.Name -like "MIGRATION-*" -or
     $_.Name -like "MONITORING-*" -or
     $_.Name -like "TEST-*" -or
     $_.Name -like "TOOLING-*" -or
     $_.Name -like "V*.md" -or
     $_.Name -like "v*.md" -or
     $_.Name -like "baseline-*" -or
     $_.Name -like "dashboard-*" -or
     $_.Name -like "technical-details.md")
}

foreach ($file in $filesToMove) {
    Write-Host "  Moving: $($file.Name)" -ForegroundColor Gray
    Move-Item -Path $file.FullName -Destination $archivePath -Force
}

Write-Host "  ✅ Moved $($filesToMove.Count) files" -ForegroundColor Green
Write-Host ""

# Move unnecessary folders
Write-Host "📁 Moving legacy documentation folders..." -ForegroundColor Yellow

$foldersToMove = Get-ChildItem -Path $docsPath -Directory | Where-Object {
    $_.Name -notin $keepFolders
}

foreach ($folder in $foldersToMove) {
    Write-Host "  Moving: $($folder.Name)/" -ForegroundColor Gray
    Move-Item -Path $folder.FullName -Destination $archivePath -Force
}

Write-Host "  ✅ Moved $($foldersToMove.Count) folders" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "📊 Cleanup Summary" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host "Files moved: $($filesToMove.Count)" -ForegroundColor White
Write-Host "Folders moved: $($foldersToMove.Count)" -ForegroundColor White
Write-Host "Archive location: $archivePath" -ForegroundColor White
Write-Host ""
Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run 'mkdocs build --clean' to rebuild the site" -ForegroundColor Gray
Write-Host "  2. Review the archived files in $archivePath" -ForegroundColor Gray
Write-Host "  3. If everything works, you can safely delete the _archive-docs-cleanup folder" -ForegroundColor Gray
