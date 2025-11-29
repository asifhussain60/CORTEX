# CORTEX 1.0 Cleanup Script
# Removes all files/folders not relevant to CORTEX 1.0
# All items are already in git history

param(
    [switch]$WhatIf = $false
)

$rootPath = "D:\PROJECTS\CORTEX"

Write-Host "=== CORTEX 1.0 Cleanup Script ===" -ForegroundColor Cyan
Write-Host "Root Path: $rootPath" -ForegroundColor Gray
Write-Host ""

if ($WhatIf) {
    Write-Host "RUNNING IN WHATIF MODE - No files will be deleted" -ForegroundColor Yellow
    Write-Host ""
}

# Define items to remove
$itemsToRemove = @(
    # Legacy session documentation
    "BRAIN-FUNCTION-ANALYSIS-2025-11-07.md",
    "COMPREHENSIVE-DOCUMENTATION-PLAN.md",
    "CONFIGURATION-COMPLETE-READY-FOR-SIMULATION.md",
    "CONVERSATION-TRACKING-COMPLETE.md",
    "CONVERSATION-TRACKING-QUICKREF.md",
    "CORTEX-ALIGNMENT-PLAN.md",
    "CORTEX-ALIGNMENT-QUICKSTART.md",
    "CORTEX-ALIGNMENT-SUMMARY.md",
    "CORTEX-COMPLETION-ANALYSIS.md",
    "cortex-gemini-image-prompts.md",
    "CROSS-PLATFORM-CONFIG-COMPLETE.md",
    "DOCUMENTATION-ENHANCEMENT-PLAN-NOV7.md",
    "GROUP-3-SUCCESS.md",
    "IMPLEMENTATION-PROGRESS.md",
    "KNOWLEDGE-BOUNDARIES-GAP-FIX.md",
    "KNOWLEDGE-BOUNDARIES-PROGRESS.md",
    "MIND-PALACE-THEME-UPDATE.md",
    "MKDOCS-ISSUES-AND-FIXES.md",
    "MKDOCS-REBUILD-PLAN.md",
    "MKDOCS-STYLING-UPDATE.md",
    "ORACLE-CRAWLER-SUMMARY.md",
    "PHASES-4-5-COMPLETE.md",
    "SESSION-COMPLETION-CONVERSATION-TRACKING.md",
    "SESSION-SUMMARY-NOV-6-2025.md",
    "SESSION-SUMMARY-PHASES-4-5.md",
    "SYSTEM-INVENTORY.md",
    
    # Utility scripts that were one-time use
    "cleanup-docs.ps1",
    "quick_test.py",
    "test_cortex.py",
    "setup_cortex.py",
    
    # Archive folders (already in git history)
    "_archive",
    "backups",
    
    # Old naming scheme folders
    "kds-brain",
    "cortex-design",
    
    # Old implementations
    "dashboard-wpf",
    "vite-project",
    
    # Old site build (can be regenerated from docs/)
    "site",
    
    # Legacy tooling
    "tooling",
    
    # Old test structure
    "tests",
    
    # Legacy knowledge structure (moved to cortex-brain)
    "knowledge",
    
    # Old session tracking
    "sessions",
    
    # Old reports
    "reports",
    
    # Legacy templates
    "templates",
    
    # Old hooks
    "hooks",
    
    # Legacy governance (consolidated into CORTEX/src/tier0)
    "governance",
    
    # Old database file (replaced by cortex-brain/tier1/conversations.db)
    "cortex-brain.db",
    
    # MkDocs config (will be recreated if needed)
    "mkdocs.yml"
)

$deletedCount = 0
$skippedCount = 0
$notFoundCount = 0

foreach ($item in $itemsToRemove) {
    $fullPath = Join-Path $rootPath $item
    
    if (Test-Path $fullPath) {
        $isDirectory = (Get-Item $fullPath).PSIsContainer
        $itemType = if ($isDirectory) { "Directory" } else { "File" }
        
        if ($WhatIf) {
            Write-Host "[WOULD DELETE] $itemType : $item" -ForegroundColor Yellow
            $deletedCount++
        } else {
            try {
                if ($isDirectory) {
                    Remove-Item -Path $fullPath -Recurse -Force
                    Write-Host "[DELETED] $itemType : $item" -ForegroundColor Green
                } else {
                    Remove-Item -Path $fullPath -Force
                    Write-Host "[DELETED] $itemType : $item" -ForegroundColor Green
                }
                $deletedCount++
            } catch {
                Write-Host "[ERROR] Failed to delete $item : $_" -ForegroundColor Red
                $skippedCount++
            }
        }
    } else {
        Write-Host "[NOT FOUND] $item" -ForegroundColor Gray
        $notFoundCount++
    }
}

Write-Host ""
Write-Host "=== Cleanup Summary ===" -ForegroundColor Cyan
if ($WhatIf) {
    Write-Host "Would delete: $deletedCount items" -ForegroundColor Yellow
} else {
    Write-Host "Deleted: $deletedCount items" -ForegroundColor Green
}
Write-Host "Skipped (errors): $skippedCount items" -ForegroundColor Red
Write-Host "Not found: $notFoundCount items" -ForegroundColor Gray
Write-Host ""

if ($WhatIf) {
    Write-Host "Run without -WhatIf flag to perform actual deletion" -ForegroundColor Yellow
} else {
    Write-Host "Cleanup complete! Run 'git status' to see changes" -ForegroundColor Green
}
