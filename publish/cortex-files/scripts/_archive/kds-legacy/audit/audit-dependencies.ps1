<#
.SYNOPSIS
    KDS Dependency Audit - Scans for hard-coded paths and application-specific content

.DESCRIPTION
    Comprehensive audit tool that scans all KDS files for:
    - Hard-coded absolute paths (D:\PROJECTS\, C:\, etc.)
    - Application-specific references (Noor Canvas, HostControlPanel, etc.)
    - Hard-coded configuration values
    - External dependencies
    
    Generates detailed JSON report for migration planning.

.PARAMETER OutputPath
    Path to save the audit report JSON file

.PARAMETER Verbose
    Show detailed progress during scan

.EXAMPLE
    .\audit-dependencies.ps1
    .\audit-dependencies.ps1 -OutputPath "D:\PROJECTS\KDS\reports\audit-report.json"
    .\audit-dependencies.ps1 -Verbose

.NOTES
    Part of KDS Independence Project - Phase 0.1
    Created: November 4, 2025
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput
)

# ============================================================================
# Configuration
# ============================================================================

$script:KdsRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$script:ScanStartTime = Get-Date

# Patterns to detect
$script:Patterns = @{
    HardCodedPaths = @(
        'D:\\PROJECTS\\',
        'C:\\Users\\',
        'C:\\Program Files',
        '/Users/',
        '/home/',
        'D:\\\\PROJECTS\\\\',  # Escaped in JSON
        'D:/',
        'C:/'
    )
    
    ApplicationSpecific = @(
        'Noor Canvas',
        'NOOR CANVAS',
        'NoorCanvas',
        'HostControlPanel',
        'UserRegistrationLink',
        'session-212',
        'PQ9N5YWW',
        'localhost:9091',
        'SPA/NoorCanvas'
    )
    
    HardCodedConfig = @(
        'localhost:\d{4,5}',
        'http://localhost',
        'https://localhost',
        '127\.0\.0\.1:\d{4,5}'
    )
}

# File extensions to scan
$script:ScanExtensions = @(
    '*.ps1', '*.psm1',      # PowerShell
    '*.md',                 # Documentation
    '*.json',               # Configuration
    '*.yaml', '*.yml',      # YAML configs
    '*.txt',                # Text files
    '*.sh', '*.bash'        # Shell scripts
)

# Directories to exclude
$script:ExcludeDirs = @(
    '.git',
    'node_modules',
    '_archive',
    'bin',
    'obj'
)

# ============================================================================
# Helper Functions
# ============================================================================

function Write-Progress-Custom {
    param([string]$Message)
    if ($VerboseOutput) {
        Write-Host "⏳ $Message" -ForegroundColor Cyan
    }
}

function Get-RelativePath {
    param([string]$FullPath)
    return $FullPath.Replace($script:KdsRoot, 'KDS').Replace('\', '/')
}

function Test-ShouldExclude {
    param([string]$Path)
    
    foreach ($exclude in $script:ExcludeDirs) {
        if ($Path -like "*\$exclude\*" -or $Path -like "*/$exclude/*") {
            return $true
        }
    }
    return $false
}

function Find-PatternInFile {
    param(
        [string]$FilePath,
        [string]$Pattern,
        [string]$Category
    )
    
    $matches = @()
    
    try {
        $content = Get-Content -Path $FilePath -Raw -ErrorAction Stop
        $lines = Get-Content -Path $FilePath -ErrorAction Stop
        
        # Find all matches
        $regex = [regex]::new($Pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
        $allMatches = $regex.Matches($content)
        
        foreach ($match in $allMatches) {
            # Find line number
            $lineNumber = 1
            $position = $match.Index
            $currentPos = 0
            
            foreach ($line in $lines) {
                $currentPos += $line.Length + 1  # +1 for newline
                if ($currentPos -gt $position) {
                    break
                }
                $lineNumber++
            }
            
            # Get context (the line containing the match)
            $contextLine = if ($lineNumber -le $lines.Count) { 
                $lines[$lineNumber - 1].Trim() 
            } else { 
                $match.Value 
            }
            
            $matches += @{
                Pattern = $Pattern
                Match = $match.Value
                Line = $lineNumber
                Context = $contextLine
                Category = $Category
            }
        }
    }
    catch {
        Write-Warning "Error scanning $FilePath : $_"
    }
    
    return $matches
}

# ============================================================================
# Main Scan Functions
# ============================================================================

function Start-FileScan {
    Write-Host "🔍 KDS Dependency Audit" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "Scan Root: $script:KdsRoot" -ForegroundColor Gray
    Write-Host ""
    
    # Get all files to scan
    Write-Progress-Custom "Collecting files to scan..."
    $allFiles = @()
    
    foreach ($ext in $script:ScanExtensions) {
        $files = Get-ChildItem -Path $script:KdsRoot -Filter $ext -Recurse -File -ErrorAction SilentlyContinue
        $allFiles += $files | Where-Object { -not (Test-ShouldExclude $_.FullName) }
    }
    
    Write-Host "📂 Files to scan: $($allFiles.Count)" -ForegroundColor Cyan
    Write-Host ""
    
    # Initialize results
    $results = @{
        ScanDate = $script:ScanStartTime.ToString('yyyy-MM-dd HH:mm:ss')
        KdsRoot = $script:KdsRoot
        FilesScanned = $allFiles.Count
        IssuesFound = @{
            HardCodedPaths = @()
            ApplicationSpecific = @()
            HardCodedConfig = @()
        }
        FilesByCategory = @{
            Scripts = 0
            Documentation = 0
            Configuration = 0
            Other = 0
        }
        Summary = @{
            TotalIssues = 0
            CriticalFiles = 0
            IndependenceScore = 0
        }
    }
    
    # Scan each file
    $currentFile = 0
    foreach ($file in $allFiles) {
        $currentFile++
        $relativePath = Get-RelativePath $file.FullName
        
        if ($VerboseOutput -and ($currentFile % 10 -eq 0)) {
            Write-Host "  [$currentFile/$($allFiles.Count)] Scanning: $relativePath" -ForegroundColor Gray
        }
        
        # Categorize file
        switch ($file.Extension) {
            {$_ -in @('.ps1', '.psm1', '.sh', '.bash')} { $results.FilesByCategory.Scripts++ }
            '.md' { $results.FilesByCategory.Documentation++ }
            {$_ -in @('.json', '.yaml', '.yml', '.txt')} { $results.FilesByCategory.Configuration++ }
            default { $results.FilesByCategory.Other++ }
        }
        
        # Scan for hard-coded paths
        foreach ($pattern in $script:Patterns.HardCodedPaths) {
            $matches = Find-PatternInFile -FilePath $file.FullName -Pattern $pattern -Category "HardCodedPath"
            foreach ($match in $matches) {
                $results.IssuesFound.HardCodedPaths += @{
                    File = $relativePath
                    Line = $match.Line
                    Pattern = $match.Pattern
                    Match = $match.Match
                    Context = $match.Context
                    Severity = "Critical"
                }
            }
        }
        
        # Scan for application-specific content
        foreach ($pattern in $script:Patterns.ApplicationSpecific) {
            $matches = Find-PatternInFile -FilePath $file.FullName -Pattern $pattern -Category "ApplicationSpecific"
            foreach ($match in $matches) {
                $results.IssuesFound.ApplicationSpecific += @{
                    File = $relativePath
                    Line = $match.Line
                    Pattern = $match.Pattern
                    Match = $match.Match
                    Context = $match.Context
                    Severity = "High"
                }
            }
        }
        
        # Scan for hard-coded config
        foreach ($pattern in $script:Patterns.HardCodedConfig) {
            $matches = Find-PatternInFile -FilePath $file.FullName -Pattern $pattern -Category "HardCodedConfig"
            foreach ($match in $matches) {
                $results.IssuesFound.HardCodedConfig += @{
                    File = $relativePath
                    Line = $match.Line
                    Pattern = $match.Pattern
                    Match = $match.Match
                    Context = $match.Context
                    Severity = "Medium"
                }
            }
        }
    }
    
    return $results
}

function Complete-AuditReport {
    param($Results)
    
    # Calculate summary
    $totalIssues = $Results.IssuesFound.HardCodedPaths.Count + 
                   $Results.IssuesFound.ApplicationSpecific.Count + 
                   $Results.IssuesFound.HardCodedConfig.Count
    
    $Results.Summary.TotalIssues = $totalIssues
    
    # Count files with issues
    $criticalFiles = @{}
    foreach ($issue in $Results.IssuesFound.HardCodedPaths) {
        $criticalFiles[$issue.File] = $true
    }
    foreach ($issue in $Results.IssuesFound.ApplicationSpecific) {
        $criticalFiles[$issue.File] = $true
    }
    $Results.Summary.CriticalFiles = $criticalFiles.Count
    
    # Calculate independence score (100 - penalty per issue)
    # Start at 100, subtract points for issues
    $pathPenalty = [Math]::Min($Results.IssuesFound.HardCodedPaths.Count * 0.8, 50)
    $appPenalty = [Math]::Min($Results.IssuesFound.ApplicationSpecific.Count * 0.5, 30)
    $configPenalty = [Math]::Min($Results.IssuesFound.HardCodedConfig.Count * 0.3, 20)
    
    $independenceScore = [Math]::Max(0, 100 - $pathPenalty - $appPenalty - $configPenalty)
    $Results.Summary.IndependenceScore = [Math]::Round($independenceScore, 1)
    
    # Add scan duration
    $Results.ScanDuration = ((Get-Date) - $script:ScanStartTime).TotalSeconds
    
    return $Results
}

function Show-AuditSummary {
    param($Results)
    
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "📊 Audit Summary" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "Files Scanned: $($Results.FilesScanned)" -ForegroundColor Cyan
    Write-Host "  Scripts:       $($Results.FilesByCategory.Scripts)"
    Write-Host "  Documentation: $($Results.FilesByCategory.Documentation)"
    Write-Host "  Configuration: $($Results.FilesByCategory.Configuration)"
    Write-Host "  Other:         $($Results.FilesByCategory.Other)"
    Write-Host ""
    
    Write-Host "Issues Found: $($Results.Summary.TotalIssues)" -ForegroundColor $(if ($Results.Summary.TotalIssues -gt 50) { 'Red' } else { 'Yellow' })
    Write-Host "  Hard-Coded Paths:      $($Results.IssuesFound.HardCodedPaths.Count) " -NoNewline
    Write-Host "Critical" -ForegroundColor Red
    Write-Host "  Application-Specific:  $($Results.IssuesFound.ApplicationSpecific.Count) " -NoNewline
    Write-Host "High" -ForegroundColor Yellow
    Write-Host "  Hard-Coded Config:     $($Results.IssuesFound.HardCodedConfig.Count) " -NoNewline
    Write-Host "Medium" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Files with Issues: $($Results.Summary.CriticalFiles)" -ForegroundColor Yellow
    Write-Host ""
    
    # Independence score with color coding
    $scoreColor = if ($Results.Summary.IndependenceScore -ge 90) { 'Green' }
                  elseif ($Results.Summary.IndependenceScore -ge 70) { 'Yellow' }
                  else { 'Red' }
    
    Write-Host "Independence Score: " -NoNewline
    Write-Host "$($Results.Summary.IndependenceScore)/100" -ForegroundColor $scoreColor
    Write-Host ""
    
    # Show top offending files
    if ($Results.Summary.CriticalFiles -gt 0) {
        Write-Host "🔥 Top Issues by File:" -ForegroundColor Yellow
        
        $fileIssues = @{}
        foreach ($issue in $Results.IssuesFound.HardCodedPaths) {
            if (-not $fileIssues.ContainsKey($issue.File)) {
                $fileIssues[$issue.File] = 0
            }
            $fileIssues[$issue.File] += 1
        }
        foreach ($issue in $Results.IssuesFound.ApplicationSpecific) {
            if (-not $fileIssues.ContainsKey($issue.File)) {
                $fileIssues[$issue.File] = 0
            }
            $fileIssues[$issue.File] += 1
        }
        
        $topFiles = $fileIssues.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 10
        foreach ($file in $topFiles) {
            Write-Host "  $($file.Value) issues - " -NoNewline -ForegroundColor Red
            Write-Host "$($file.Key)" -ForegroundColor Gray
        }
        Write-Host ""
    }
    
    Write-Host "⏱️  Scan Duration: $([Math]::Round($Results.ScanDuration, 2))s" -ForegroundColor Gray
    Write-Host ""
}

function Save-AuditReport {
    param($Results, [string]$Path)
    
    if ([string]::IsNullOrWhiteSpace($Path)) {
        $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        $reportDir = Join-Path $script:KdsRoot 'reports' 'audit'
        if (-not (Test-Path $reportDir)) {
            New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
        }
        $Path = Join-Path $reportDir "audit-report-$timestamp.json"
    }
    
    # Convert to JSON with proper formatting
    $jsonResults = $Results | ConvertTo-Json -Depth 10
    
    # Save to file
    Set-Content -Path $Path -Value $jsonResults -Encoding UTF8
    
    Write-Host "✅ Report saved: $Path" -ForegroundColor Green
    
    # Also save a human-readable summary
    $summaryPath = $Path -replace '\.json$', '.md'
    $markdown = Generate-MarkdownReport -Results $Results
    Set-Content -Path $summaryPath -Value $markdown -Encoding UTF8
    
    Write-Host "✅ Summary saved: $summaryPath" -ForegroundColor Green
    
    return $Path
}

function Generate-MarkdownReport {
    param($Results)
    
    $md = @"
# KDS Dependency Audit Report
**Scan Date:** $($Results.ScanDate)  
**Scan Duration:** $([Math]::Round($Results.ScanDuration, 2))s  
**Independence Score:** $($Results.Summary.IndependenceScore)/100

---

## 📊 Summary

| Metric | Count |
|--------|-------|
| Files Scanned | $($Results.FilesScanned) |
| Total Issues | $($Results.Summary.TotalIssues) |
| Files with Issues | $($Results.Summary.CriticalFiles) |
| Hard-Coded Paths | $($Results.IssuesFound.HardCodedPaths.Count) |
| Application-Specific | $($Results.IssuesFound.ApplicationSpecific.Count) |
| Hard-Coded Config | $($Results.IssuesFound.HardCodedConfig.Count) |

---

## 🚨 Critical: Hard-Coded Paths ($($Results.IssuesFound.HardCodedPaths.Count))

"@
    
    if ($Results.IssuesFound.HardCodedPaths.Count -gt 0) {
        $md += "`n"
        foreach ($issue in ($Results.IssuesFound.HardCodedPaths | Select-Object -First 20)) {
            $md += "- **$($issue.File):$($issue.Line)**`n"
            $md += "  ``````$($issue.Context)```````n"
            $md += "  Pattern: ``$($issue.Pattern)```n`n"
        }
        
        if ($Results.IssuesFound.HardCodedPaths.Count -gt 20) {
            $md += "`n*... and $($Results.IssuesFound.HardCodedPaths.Count - 20) more*`n"
        }
    } else {
        $md += "`n✅ No hard-coded paths found!`n"
    }
    
    $md += "`n---`n`n## ⚠️ Application-Specific References ($($Results.IssuesFound.ApplicationSpecific.Count))`n"
    
    if ($Results.IssuesFound.ApplicationSpecific.Count -gt 0) {
        $md += "`n"
        foreach ($issue in ($Results.IssuesFound.ApplicationSpecific | Select-Object -First 20)) {
            $md += "- **$($issue.File):$($issue.Line)**`n"
            $md += "  ``````$($issue.Context)```````n"
            $md += "  Pattern: ``$($issue.Pattern)```n`n"
        }
        
        if ($Results.IssuesFound.ApplicationSpecific.Count -gt 20) {
            $md += "`n*... and $($Results.IssuesFound.ApplicationSpecific.Count - 20) more*`n"
        }
    } else {
        $md += "`n✅ No application-specific references found!`n"
    }
    
    $md += "`n---`n`n## 📝 Recommendations`n`n"
    
    if ($Results.Summary.IndependenceScore -lt 70) {
        $md += "**Status:** 🔴 Major refactoring needed`n`n"
        $md += "1. Replace all hard-coded paths with dynamic workspace resolution`n"
        $md += "2. Extract application-specific content to integration packages`n"
        $md += "3. Move configuration to templates with variable substitution`n"
    } elseif ($Results.Summary.IndependenceScore -lt 90) {
        $md += "**Status:** 🟡 Moderate cleanup needed`n`n"
        $md += "1. Address remaining hard-coded paths`n"
        $md += "2. Generalize application-specific examples`n"
        $md += "3. Move to template-based configuration`n"
    } else {
        $md += "**Status:** 🟢 Excellent independence!`n`n"
        $md += "KDS appears to be well-abstracted and portable. Minor cleanup may still improve score.`n"
    }
    
    $md += "`n---`n`n*Generated by KDS Dependency Audit Tool*`n"
    
    return $md
}

# ============================================================================
# Main Execution
# ============================================================================

try {
    # Run the scan
    $results = Start-FileScan
    
    # Complete the report
    $results = Complete-AuditReport -Results $results
    
    # Show summary
    Show-AuditSummary -Results $results
    
    # Save report
    $reportPath = Save-AuditReport -Results $results -Path $OutputPath
    
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "✅ Audit Complete!" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Review the detailed report: $reportPath"
    Write-Host "2. Prioritize critical issues (hard-coded paths)"
    Write-Host "3. Plan refactoring with workspace resolver utility"
    Write-Host ""
    
    exit 0
}
catch {
    Write-Host ""
    Write-Host "❌ ERROR: Audit failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
