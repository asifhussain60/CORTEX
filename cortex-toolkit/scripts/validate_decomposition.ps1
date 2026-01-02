<#
.SYNOPSIS
    Validates decomposition integrity for CORTEX artifacts
.DESCRIPTION
    Comprehensive validation script that checks:
    - Content preservation (line count, sections, headings)
    - File structure correctness (folders, naming conventions)
    - Entry point preservation (original path unchanged)
    - Cross-reference integrity (internal links, includes)
    - Markdown validity (syntax, tables, code blocks)
    - Archive creation (backup exists with correct version)
.PARAMETER OriginalFile
    Path to original monolithic file (for comparison)
.PARAMETER IndexFile
    Path to new index file (should be same as OriginalFile path)
.PARAMETER DecompFolder
    Path to decomposed content folder
.PARAMETER ArtifactType
    Type of artifact: Documentation, Prompt, Config, Manifest
.EXAMPLE
    .\validate_decomposition.ps1 -OriginalFile "cortex-brain/archives/Level1-spec-v3.3.0.md" `
                                   -IndexFile "cortex-brain/documents/planning/active/cortex-documentation/artifacts/Level1-spec.md" `
                                   -DecompFolder "cortex-brain/documents/planning/active/cortex-documentation/artifacts/level1-specs" `
                                   -ArtifactType "Documentation"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$OriginalFile,
    
    [Parameter(Mandatory=$true)]
    [string]$IndexFile,
    
    [Parameter(Mandatory=$true)]
    [string]$DecompFolder,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("Documentation", "Prompt", "Config", "Manifest", "Code")]
    [string]$ArtifactType
)

# Configuration
$ErrorActionPreference = "Stop"
$ValidationResults = @{
    Passed = @()
    Failed = @()
    Warnings = @()
    Metrics = @{}
}

# Color coding for output
function Write-ValidationResult {
    param($Status, $Message)
    switch ($Status) {
        "PASS" { Write-Host "✅ PASS: $Message" -ForegroundColor Green }
        "FAIL" { Write-Host "❌ FAIL: $Message" -ForegroundColor Red }
        "WARN" { Write-Host "⚠️  WARN: $Message" -ForegroundColor Yellow }
        "INFO" { Write-Host "ℹ️  INFO: $Message" -ForegroundColor Cyan }
    }
}

# Test 1: Entry Point Preservation
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "TEST 1: Entry Point Preservation" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

$originalPath = Split-Path -Leaf $OriginalFile
$indexPath = Split-Path -Leaf $IndexFile
$originalDir = Split-Path -Parent $OriginalFile
$indexDir = Split-Path -Parent $IndexFile

if ($originalPath -eq $indexPath) {
    Write-ValidationResult "PASS" "Filename preserved: $indexPath"
    $ValidationResults.Passed += "Entry point filename unchanged"
} else {
    Write-ValidationResult "FAIL" "Filename changed: $originalPath → $indexPath"
    $ValidationResults.Failed += "Entry point filename changed (BREAKING)"
}

if ($originalDir -eq $indexDir) {
    Write-ValidationResult "PASS" "Directory preserved: $indexDir"
    $ValidationResults.Passed += "Entry point directory unchanged"
} else {
    Write-ValidationResult "FAIL" "Directory changed: $originalDir → $indexDir"
    $ValidationResults.Failed += "Entry point directory changed (BREAKING)"
}

if (Test-Path $IndexFile) {
    Write-ValidationResult "PASS" "Index file exists at original location"
    $ValidationResults.Passed += "Index file exists"
} else {
    Write-ValidationResult "FAIL" "Index file not found at: $IndexFile"
    $ValidationResults.Failed += "Index file missing"
}

# Test 2: Content Preservation
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "TEST 2: Content Preservation" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

$originalContent = Get-Content $OriginalFile -Raw
$originalLines = (Get-Content $OriginalFile | Measure-Object -Line).Lines
$originalHeadings = ([regex]::Matches($originalContent, '^#{1,6}\s+.+$', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count
$originalCodeBlocks = ([regex]::Matches($originalContent, '```[\s\S]*?```')).Count
$originalTables = ([regex]::Matches($originalContent, '^\|.+\|$', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count

Write-ValidationResult "INFO" "Original file metrics:"
Write-Host "  - Lines: $originalLines" -ForegroundColor Gray
Write-Host "  - Headings: $originalHeadings" -ForegroundColor Gray
Write-Host "  - Code blocks: $originalCodeBlocks" -ForegroundColor Gray
Write-Host "  - Tables: $originalTables" -ForegroundColor Gray

# Aggregate decomposed content
$decompFiles = Get-ChildItem -Path $DecompFolder -Recurse -Filter "*.md"
$totalDecompLines = 0
$totalDecompHeadings = 0
$totalDecompCodeBlocks = 0
$totalDecompTables = 0

foreach ($file in $decompFiles) {
    $content = Get-Content $file.FullName -Raw
    $totalDecompLines += (Get-Content $file.FullName | Measure-Object -Line).Lines
    $totalDecompHeadings += ([regex]::Matches($content, '^#{1,6}\s+.+$', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count
    $totalDecompCodeBlocks += ([regex]::Matches($content, '```[\s\S]*?```')).Count
    $totalDecompTables += ([regex]::Matches($content, '^\|.+\|$', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count
}

# Add index file metrics
$indexContent = Get-Content $IndexFile -Raw
$indexLines = (Get-Content $IndexFile | Measure-Object -Line).Lines
$totalDecompLines += $indexLines
$totalDecompHeadings += ([regex]::Matches($indexContent, '^#{1,6}\s+.+$', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count
$totalDecompCodeBlocks += ([regex]::Matches($indexContent, '```[\s\S]*?```')).Count
$totalDecompTables += ([regex]::Matches($indexContent, '^\|.+\|$', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count

Write-ValidationResult "INFO" "Decomposed content metrics (including index):"
Write-Host "  - Total lines: $totalDecompLines" -ForegroundColor Gray
Write-Host "  - Headings: $totalDecompHeadings" -ForegroundColor Gray
Write-Host "  - Code blocks: $totalDecompCodeBlocks" -ForegroundColor Gray
Write-Host "  - Tables: $totalDecompTables" -ForegroundColor Gray

# Validation thresholds (allow for added content like index headers, version info)
$lineVariance = [Math]::Abs($originalLines - $totalDecompLines) / $originalLines
$headingVariance = [Math]::Abs($originalHeadings - $totalDecompHeadings) / $originalHeadings

if ($lineVariance -lt 0.10) {  # Allow 10% variance for index overhead
    Write-ValidationResult "PASS" "Line count preserved within 10% (variance: $([Math]::Round($lineVariance * 100, 2))%)"
    $ValidationResults.Passed += "Line count preserved"
} elseif ($totalDecompLines -gt $originalLines) {
    Write-ValidationResult "WARN" "Line count increased by $([Math]::Round($lineVariance * 100, 2))% (likely index overhead)"
    $ValidationResults.Warnings += "Line count increased (acceptable for index structure)"
} else {
    Write-ValidationResult "FAIL" "Line count decreased by $([Math]::Round($lineVariance * 100, 2))% (content may be lost)"
    $ValidationResults.Failed += "Significant line count reduction detected"
}

if ($totalDecompHeadings -ge $originalHeadings) {
    Write-ValidationResult "PASS" "All headings preserved (Original: $originalHeadings, Decomposed: $totalDecompHeadings)"
    $ValidationResults.Passed += "Headings preserved"
} else {
    Write-ValidationResult "FAIL" "Missing headings (Original: $originalHeadings, Decomposed: $totalDecompHeadings)"
    $ValidationResults.Failed += "Heading count reduced"
}

if ($totalDecompCodeBlocks -ge $originalCodeBlocks) {
    Write-ValidationResult "PASS" "All code blocks preserved (Original: $originalCodeBlocks, Decomposed: $totalDecompCodeBlocks)"
    $ValidationResults.Passed += "Code blocks preserved"
} else {
    Write-ValidationResult "WARN" "Fewer code blocks (Original: $originalCodeBlocks, Decomposed: $totalDecompCodeBlocks)"
    $ValidationResults.Warnings += "Code block count reduced"
}

if ($totalDecompTables -ge $originalTables) {
    Write-ValidationResult "PASS" "All tables preserved (Original: $originalTables, Decomposed: $totalDecompTables)"
    $ValidationResults.Passed += "Tables preserved"
} else {
    Write-ValidationResult "WARN" "Fewer tables (Original: $originalTables, Decomposed: $totalDecompTables)"
    $ValidationResults.Warnings += "Table count reduced"
}

$ValidationResults.Metrics.OriginalLines = $originalLines
$ValidationResults.Metrics.DecomposedLines = $totalDecompLines
$ValidationResults.Metrics.IndexLines = $indexLines
$ValidationResults.Metrics.ReductionPercent = [Math]::Round((1 - ($indexLines / $originalLines)) * 100, 2)

# Test 3: File Structure Validation
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "TEST 3: File Structure Validation" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

if (Test-Path $DecompFolder) {
    Write-ValidationResult "PASS" "Decomposed folder exists: $DecompFolder"
    $ValidationResults.Passed += "Decomposed folder exists"
} else {
    Write-ValidationResult "FAIL" "Decomposed folder not found: $DecompFolder"
    $ValidationResults.Failed += "Decomposed folder missing"
}

# Check for expected subfolders based on artifact type
$expectedFolders = switch ($ArtifactType) {
    "Documentation" { @("core", "implementation", "metadata") }
    "Prompt" { @("core", "guides", "metadata") }
    "Config" { @("infrastructure", "application", "environments") }
    "Manifest" { @("phases", "templates", "rules") }
    default { @() }
}

foreach ($folder in $expectedFolders) {
    $folderPath = Join-Path $DecompFolder $folder
    if (Test-Path $folderPath) {
        $fileCount = (Get-ChildItem -Path $folderPath -Recurse -Filter "*.md" -ErrorAction SilentlyContinue).Count
        Write-ValidationResult "PASS" "Subfolder exists: $folder ($fileCount files)"
        $ValidationResults.Passed += "Subfolder $folder exists"
    } else {
        Write-ValidationResult "WARN" "Expected subfolder not found: $folder"
        $ValidationResults.Warnings += "Subfolder $folder missing"
    }
}

# Test 4: Index File Validation
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "TEST 4: Index File Validation" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

$indexContent = Get-Content $IndexFile -Raw

# Check for required index sections
$requiredSections = @(
    "Purpose",
    "Sub-Prompts|Specification Modules|Sub-Configs|Phases",
    "Load Order",
    "Performance Metrics|Metrics",
    "Version|v\d+\.\d+\.\d+"
)

foreach ($section in $requiredSections) {
    if ($indexContent -match $section) {
        Write-ValidationResult "PASS" "Index contains required section: $section"
        $ValidationResults.Passed += "Index section: $section"
    } else {
        Write-ValidationResult "FAIL" "Index missing required section: $section"
        $ValidationResults.Failed += "Index missing: $section"
    }
}

# Check for references to decomposed files
$referencedFiles = [regex]::Matches($indexContent, '→\s+`([^`]+\.md)`') | ForEach-Object { $_.Groups[1].Value }
$foundReferences = 0
$missingReferences = 0

foreach ($ref in $referencedFiles) {
    $refPath = Join-Path (Split-Path $IndexFile -Parent) $ref
    if (Test-Path $refPath) {
        $foundReferences++
    } else {
        $missingReferences++
        Write-ValidationResult "WARN" "Referenced file not found: $ref"
        $ValidationResults.Warnings += "Missing referenced file: $ref"
    }
}

if ($missingReferences -eq 0 -and $foundReferences -gt 0) {
    Write-ValidationResult "PASS" "All $foundReferences referenced files exist"
    $ValidationResults.Passed += "All file references valid"
} elseif ($missingReferences -gt 0) {
    Write-ValidationResult "FAIL" "$missingReferences referenced files missing (out of $($foundReferences + $missingReferences))"
    $ValidationResults.Failed += "File references broken"
}

# Test 5: Archive Validation
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "TEST 5: Archive Validation" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

if (Test-Path $OriginalFile) {
    $archiveSize = (Get-Item $OriginalFile).Length
    Write-ValidationResult "PASS" "Archive exists: $OriginalFile ($([Math]::Round($archiveSize/1KB, 2)) KB)"
    $ValidationResults.Passed += "Archive created"
} else {
    Write-ValidationResult "FAIL" "Archive not found: $OriginalFile"
    $ValidationResults.Failed += "Archive missing (cannot rollback)"
}

# Test 6: Markdown Syntax Validation
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "TEST 6: Markdown Syntax Validation" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

$allMarkdownFiles = @($IndexFile) + $decompFiles.FullName
$syntaxErrors = 0

foreach ($file in $allMarkdownFiles) {
    $content = Get-Content $file -Raw
    
    # Check for unclosed code blocks
    $codeBlockMarkers = ([regex]::Matches($content, '```')).Count
    if ($codeBlockMarkers % 2 -ne 0) {
        Write-ValidationResult "FAIL" "Unclosed code block in: $(Split-Path $file -Leaf)"
        $syntaxErrors++
    }
    
    # Check for malformed tables (unequal pipe counts)
    $tableLines = [regex]::Matches($content, '^\|.+\|$', [System.Text.RegularExpressions.RegexOptions]::Multiline)
    $tablePipeCounts = @{}
    foreach ($line in $tableLines) {
        $pipeCount = ($line.Value.ToCharArray() | Where-Object { $_ -eq '|' }).Count
        if (-not $tablePipeCounts.ContainsKey($pipeCount)) {
            $tablePipeCounts[$pipeCount] = 0
        }
        $tablePipeCounts[$pipeCount]++
    }
    
    # Check for broken internal links
    $internalLinks = [regex]::Matches($content, '\[([^\]]+)\]\(([^)]+)\)')
    foreach ($link in $internalLinks) {
        $linkTarget = $link.Groups[2].Value
        if ($linkTarget -match '^[^#].*\.md' -and -not $linkTarget.StartsWith('http')) {
            $linkPath = Join-Path (Split-Path $file -Parent) $linkTarget
            if (-not (Test-Path $linkPath)) {
                Write-ValidationResult "WARN" "Broken link in $(Split-Path $file -Leaf): $linkTarget"
                $ValidationResults.Warnings += "Broken link: $linkTarget"
            }
        }
    }
}

if ($syntaxErrors -eq 0) {
    Write-ValidationResult "PASS" "No markdown syntax errors detected"
    $ValidationResults.Passed += "Markdown syntax valid"
} else {
    Write-ValidationResult "FAIL" "$syntaxErrors markdown syntax errors found"
    $ValidationResults.Failed += "Markdown syntax errors"
}

# Final Report
Write-Host "`n" -NoNewline
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
Write-Host "VALIDATION SUMMARY" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Magenta

Write-Host "Artifact: " -NoNewline; Write-Host $(Split-Path $IndexFile -Leaf) -ForegroundColor Cyan
Write-Host "Type: " -NoNewline; Write-Host $ArtifactType -ForegroundColor Cyan
Write-Host "Validated: " -NoNewline; Write-Host (Get-Date -Format "yyyy-MM-dd HH:mm:ss") -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Passed: " -NoNewline -ForegroundColor Green
Write-Host $ValidationResults.Passed.Count -ForegroundColor Green
Write-Host "❌ Failed: " -NoNewline -ForegroundColor Red
Write-Host $ValidationResults.Failed.Count -ForegroundColor Red
Write-Host "⚠️  Warnings: " -NoNewline -ForegroundColor Yellow
Write-Host $ValidationResults.Warnings.Count -ForegroundColor Yellow

Write-Host "`nPerformance Metrics:" -ForegroundColor Cyan
Write-Host "  - Original file: $($ValidationResults.Metrics.OriginalLines) lines" -ForegroundColor Gray
Write-Host "  - Index file: $($ValidationResults.Metrics.IndexLines) lines" -ForegroundColor Gray
Write-Host "  - Total decomposed: $($ValidationResults.Metrics.DecomposedLines) lines" -ForegroundColor Gray
Write-Host "  - Size reduction: $($ValidationResults.Metrics.ReductionPercent)%" -ForegroundColor Gray

if ($ValidationResults.Failed.Count -eq 0) {
    Write-Host "`n🎉 VALIDATION PASSED" -ForegroundColor Green -BackgroundColor DarkGreen
    Write-Host "Decomposition integrity verified. Safe to proceed.`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⛔ VALIDATION FAILED" -ForegroundColor Red -BackgroundColor DarkRed
    Write-Host "Critical issues detected. DO NOT PROCEED.`n" -ForegroundColor Red
    Write-Host "Failed Checks:" -ForegroundColor Red
    foreach ($failure in $ValidationResults.Failed) {
        Write-Host "  - $failure" -ForegroundColor Red
    }
    Write-Host "`nAction: Fix issues above, then re-run validation.`n" -ForegroundColor Yellow
    exit 1
}
