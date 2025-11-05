<#
.SYNOPSIS
Analyze efficiency of Markdown agents vs PowerShell scripts

.DESCRIPTION
Measures time spent on tasks and identifies automation opportunities.
Part of KDS v7.0 Phase 3: PowerShell Efficiency Analysis

.PARAMETER AnalysisType
Type of analysis to run: TaskTiming, AutomationOpportunities, or EfficiencyReport

.PARAMETER Days
Number of days to analyze (default: 30)

.EXAMPLE
.\efficiency-analyzer.ps1 -AnalysisType TaskTiming
Analyze recent task execution times

.EXAMPLE
.\efficiency-analyzer.ps1 -AnalysisType EfficiencyReport -Days 90
Generate 90-day efficiency report
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('TaskTiming', 'AutomationOpportunities', 'EfficiencyReport', 'All')]
    [string]$AnalysisType = 'All',
    
    [Parameter(Mandatory=$false)]
    [int]$Days = 30,
    
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Get KDS root
$kdsRoot = Split-Path -Parent $PSScriptRoot
$brainDir = Join-Path $kdsRoot "kds-brain"
$eventsFile = Join-Path $brainDir "events.jsonl"
$efficiencyFile = Join-Path $brainDir "efficiency-history.jsonl"

Write-Host "`n⚡ KDS Efficiency Analyzer v7.0" -ForegroundColor Magenta
Write-Host "================================`n" -ForegroundColor Magenta

# ========================================
# TASK TIMING ANALYSIS
# ========================================
function Analyze-TaskTiming {
    Write-Host "📊 Task Timing Analysis" -ForegroundColor Yellow
    Write-Host "   Analyzing last $Days days...`n" -ForegroundColor Gray
    
    if (-not (Test-Path $eventsFile)) {
        Write-Host "   ⚠️  No events file found: $eventsFile" -ForegroundColor Yellow
        return
    }
    
    # Load events
    $events = Get-Content $eventsFile | ForEach-Object { $_ | ConvertFrom-Json }
    $cutoffDate = (Get-Date).AddDays(-$Days)
    $recentEvents = $events | Where-Object { 
        try { [DateTime]$_.timestamp -gt $cutoffDate } catch { $false }
    }
    
    if ($recentEvents.Count -eq 0) {
        Write-Host "   ℹ️  No events in last $Days days" -ForegroundColor Cyan
        return
    }
    
    # Group by agent type
    $markdownAgents = $recentEvents | Where-Object { $_.agent_type -eq 'markdown' }
    $powershellScripts = $recentEvents | Where-Object { $_.agent_type -eq 'powershell' -or $_.response_type -eq 'execute' }
    
    Write-Host "   Markdown Agents:" -ForegroundColor Cyan
    Write-Host "   - Total invocations: $($markdownAgents.Count)" -ForegroundColor White
    if ($markdownAgents.Count -gt 0) {
        $avgDuration = ($markdownAgents | Measure-Object -Property duration_seconds -Average).Average
        Write-Host "   - Average duration: $([math]::Round($avgDuration, 2))s" -ForegroundColor White
    }
    
    Write-Host "`n   PowerShell Scripts:" -ForegroundColor Cyan
    Write-Host "   - Total invocations: $($powershellScripts.Count)" -ForegroundColor White
    if ($powershellScripts.Count -gt 0) {
        $avgDuration = ($powershellScripts | Measure-Object -Property duration_seconds -Average).Average
        Write-Host "   - Average duration: $([math]::Round($avgDuration, 2))s" -ForegroundColor White
    }
    
    # Calculate speedup
    if ($markdownAgents.Count -gt 0 -and $powershellScripts.Count -gt 0) {
        $mdAvg = ($markdownAgents | Measure-Object -Property duration_seconds -Average).Average
        $psAvg = ($powershellScripts | Measure-Object -Property duration_seconds -Average).Average
        
        if ($psAvg -gt 0) {
            $speedup = [math]::Round((($mdAvg - $psAvg) / $mdAvg) * 100, 1)
            Write-Host "`n   ⚡ PowerShell Speedup: $speedup%" -ForegroundColor Green
        }
    }
    
    Write-Host ""
}

# ========================================
# AUTOMATION OPPORTUNITIES
# ========================================
function Find-AutomationOpportunities {
    Write-Host "🔍 Automation Opportunities" -ForegroundColor Yellow
    Write-Host "   Searching for repetitive tasks...`n" -ForegroundColor Gray
    
    if (-not (Test-Path $eventsFile)) {
        Write-Host "   ⚠️  No events file found: $eventsFile" -ForegroundColor Yellow
        return
    }
    
    # Load events
    $events = Get-Content $eventsFile | ForEach-Object { $_ | ConvertFrom-Json }
    $cutoffDate = (Get-Date).AddDays(-$Days)
    $recentEvents = $events | Where-Object { 
        try { [DateTime]$_.timestamp -gt $cutoffDate } catch { $false }
    }
    
    # Find repetitive patterns
    $taskGroups = $recentEvents | Group-Object -Property request_summary | Sort-Object Count -Descending
    
    $opportunities = @()
    
    foreach ($group in $taskGroups) {
        if ($group.Count -ge 3) {
            # Check if task is still using markdown agent
            $usesMarkdown = $group.Group | Where-Object { $_.agent_type -eq 'markdown' }
            
            if ($usesMarkdown.Count -gt 0) {
                $avgDuration = ($group.Group | Measure-Object -Property duration_seconds -Average).Average
                
                $opportunities += [PSCustomObject]@{
                    Task = $group.Name
                    Frequency = $group.Count
                    AvgDuration = [math]::Round($avgDuration, 2)
                    TotalTimeSpent = [math]::Round($avgDuration * $group.Count, 2)
                    CurrentMethod = 'Markdown Agent'
                    Recommendation = 'Create PowerShell script'
                }
            }
        }
    }
    
    if ($opportunities.Count -eq 0) {
        Write-Host "   ✅ No obvious automation opportunities found" -ForegroundColor Green
        Write-Host "   (All repetitive tasks already automated)`n" -ForegroundColor Gray
        return
    }
    
    Write-Host "   Found $($opportunities.Count) automation opportunities:`n" -ForegroundColor Cyan
    
    $opportunities | Sort-Object TotalTimeSpent -Descending | Select-Object -First 10 | ForEach-Object {
        Write-Host "   📌 Task: $($_.Task)" -ForegroundColor White
        Write-Host "      Frequency: $($_.Frequency) times" -ForegroundColor Gray
        Write-Host "      Avg Duration: $($_.AvgDuration)s" -ForegroundColor Gray
        Write-Host "      Total Time: $($_.TotalTimeSpent)s" -ForegroundColor Gray
        Write-Host "      💡 Recommendation: $($_.Recommendation)" -ForegroundColor Yellow
        Write-Host ""
    }
}

# ========================================
# EFFICIENCY REPORT
# ========================================
function Generate-EfficiencyReport {
    Write-Host "📈 Efficiency Report" -ForegroundColor Yellow
    Write-Host "   Last $Days days summary`n" -ForegroundColor Gray
    
    # Check if efficiency history exists
    if (-not (Test-Path $efficiencyFile)) {
        Write-Host "   ℹ️  No efficiency history file found" -ForegroundColor Cyan
        Write-Host "   Creating new efficiency tracking...`n" -ForegroundColor Gray
        
        # Create initial entry
        $initialEntry = @{
            timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
            period_days = $Days
            total_tasks = 0
            markdown_tasks = 0
            powershell_tasks = 0
            avg_markdown_duration = 0
            avg_powershell_duration = 0
            efficiency_gain_percent = 0
            automation_opportunities = 0
        }
        
        $initialEntry | ConvertTo-Json -Compress | Out-File $efficiencyFile -Encoding utf8
    }
    
    # Load events
    if (-not (Test-Path $eventsFile)) {
        Write-Host "   ⚠️  No events file found: $eventsFile" -ForegroundColor Yellow
        return
    }
    
    $events = Get-Content $eventsFile | ForEach-Object { $_ | ConvertFrom-Json }
    $cutoffDate = (Get-Date).AddDays(-$Days)
    $recentEvents = $events | Where-Object { 
        try { [DateTime]$_.timestamp -gt $cutoffDate } catch { $false }
    }
    
    $markdownTasks = $recentEvents | Where-Object { $_.agent_type -eq 'markdown' }
    $powershellTasks = $recentEvents | Where-Object { $_.agent_type -eq 'powershell' -or $_.response_type -eq 'execute' }
    
    $mdAvg = if ($markdownTasks.Count -gt 0) {
        ($markdownTasks | Measure-Object -Property duration_seconds -Average).Average
    } else { 0 }
    
    $psAvg = if ($powershellTasks.Count -gt 0) {
        ($powershellTasks | Measure-Object -Property duration_seconds -Average).Average
    } else { 0 }
    
    $efficiencyGain = if ($mdAvg -gt 0 -and $psAvg -gt 0) {
        [math]::Round((($mdAvg - $psAvg) / $mdAvg) * 100, 1)
    } else { 0 }
    
    # Find automation opportunities
    $taskGroups = $recentEvents | Group-Object -Property request_summary
    $automationOps = ($taskGroups | Where-Object { $_.Count -ge 3 -and ($_.Group | Where-Object { $_.agent_type -eq 'markdown' }).Count -gt 0 }).Count
    
    Write-Host "   Total Tasks: $($recentEvents.Count)" -ForegroundColor White
    Write-Host "   Markdown Agents: $($markdownTasks.Count) ($([math]::Round(($markdownTasks.Count / $recentEvents.Count) * 100, 1))%)" -ForegroundColor White
    Write-Host "   PowerShell Scripts: $($powershellTasks.Count) ($([math]::Round(($powershellTasks.Count / $recentEvents.Count) * 100, 1))%)" -ForegroundColor White
    Write-Host "`n   Average Duration:" -ForegroundColor Cyan
    Write-Host "   - Markdown: $([math]::Round($mdAvg, 2))s" -ForegroundColor White
    Write-Host "   - PowerShell: $([math]::Round($psAvg, 2))s" -ForegroundColor White
    Write-Host "`n   ⚡ Efficiency Gain: $efficiencyGain%" -ForegroundColor Green
    Write-Host "   🎯 Automation Opportunities: $automationOps" -ForegroundColor Yellow
    
    # Save report
    $reportEntry = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        period_days = $Days
        total_tasks = $recentEvents.Count
        markdown_tasks = $markdownTasks.Count
        powershell_tasks = $powershellTasks.Count
        avg_markdown_duration = [math]::Round($mdAvg, 2)
        avg_powershell_duration = [math]::Round($psAvg, 2)
        efficiency_gain_percent = $efficiencyGain
        automation_opportunities = $automationOps
    }
    
    $reportEntry | ConvertTo-Json -Compress | Out-File $efficiencyFile -Append -Encoding utf8
    
    Write-Host "`n   📄 Report saved to: $efficiencyFile" -ForegroundColor Gray
    Write-Host ""
}

# ========================================
# MAIN EXECUTION
# ========================================

switch ($AnalysisType) {
    'TaskTiming' {
        Analyze-TaskTiming
    }
    'AutomationOpportunities' {
        Find-AutomationOpportunities
    }
    'EfficiencyReport' {
        Generate-EfficiencyReport
    }
    'All' {
        Analyze-TaskTiming
        Find-AutomationOpportunities
        Generate-EfficiencyReport
    }
}

Write-Host "================================" -ForegroundColor Magenta
Write-Host "✅ Efficiency Analysis Complete" -ForegroundColor Green
Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "  - Review automation opportunities" -ForegroundColor White
Write-Host "  - Create PowerShell scripts for repetitive tasks" -ForegroundColor White
Write-Host "  - Monitor efficiency gains over time" -ForegroundColor White
Write-Host ""
