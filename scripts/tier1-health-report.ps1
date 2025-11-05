<#
.SYNOPSIS
Generate comprehensive Tier 1 health report

.DESCRIPTION
Creates detailed weekly/monthly report of Tier 1 usage patterns,
trends, and recommendations for improvement.

.PARAMETER OutputPath
Path to save report (default: reports/monitoring/tier1-health-report.md)

.PARAMETER Days
Number of days to analyze (default: 7)

.EXAMPLE
.\tier1-health-report.ps1
Generate weekly report

.EXAMPLE
.\tier1-health-report.ps1 -Days 30
Generate monthly report

.EXAMPLE
.\tier1-health-report.ps1 -OutputPath "custom-report.md"
Save to custom location

.NOTES
Author: KDS v7.0
Created: 2025-11-05
Part of: Tier 1 Automatic Tracking System
#>

[CmdletBinding()]
param(
    [string]$OutputPath = "reports/monitoring/tier1-health-report.md",
    [int]$Days = 7
)

$ErrorActionPreference = "Stop"

# Paths
$conversationHistoryPath = Join-Path $PSScriptRoot ".." "kds-brain" "conversation-history.jsonl"
$reportDir = Split-Path $OutputPath -Parent

# Create report directory if needed
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

# Load conversations
if (-not (Test-Path $conversationHistoryPath)) {
    Write-Error "conversation-history.jsonl not found"
    exit 1
}

$allConversations = @(Get-Content $conversationHistoryPath | ForEach-Object {
    try { $_ | ConvertFrom-Json } catch { $null }
} | Where-Object { $_ -ne $null })

# Filter by date range
$cutoffDate = (Get-Date).AddDays(-$Days)
$conversations = $allConversations | Where-Object {
    $started = if ($_.PSObject.Properties.Name -contains 'started') {
        try { [DateTime]::Parse($_.started) } catch { $null }
    } else { $null }
    
    $started -and $started -gt $cutoffDate
}

# Calculate metrics
$totalConversations = $conversations.Count
$sourceGroups = $conversations | Group-Object -Property { 
    if ($_.PSObject.Properties.Name -contains 'source') { $_.source } else { 'unknown' }
}

$autoRecorded = ($sourceGroups | Where-Object { $_.Name -in @('copilot_chat', 'session_recording') } | 
    Measure-Object -Property Count -Sum).Sum ?? 0
$manualRecorded = ($sourceGroups | Where-Object { $_.Name -eq 'manual_recording' } | 
    Measure-Object -Property Count -Sum).Sum ?? 0

$utilizationRate = if ($totalConversations -gt 0) {
    [math]::Round(($autoRecorded / $totalConversations) * 100, 1)
} else { 0.0 }

# Message count stats
$messageStats = $conversations | Where-Object { $_.PSObject.Properties.Name -contains 'message_count' } |
    Measure-Object -Property message_count -Average -Sum -Maximum -Minimum

# Intent distribution
$intentGroups = $conversations | Where-Object { $_.PSObject.Properties.Name -contains 'intent' } |
    Group-Object -Property intent | Sort-Object -Property Count -Descending

# Entity analysis
$allEntities = $conversations | Where-Object { $_.PSObject.Properties.Name -contains 'entities_discussed' } |
    ForEach-Object { $_.entities_discussed } | Where-Object { $_ }
$topEntities = $allEntities | Group-Object | Sort-Object -Property Count -Descending | Select-Object -First 10

# File analysis
$allFiles = $conversations | Where-Object { $_.PSObject.Properties.Name -contains 'files_modified' } |
    ForEach-Object { $_.files_modified } | Where-Object { $_ }
$topFiles = $allFiles | Group-Object | Sort-Object -Property Count -Descending | Select-Object -First 10

# Daily trend
$dailyTrend = $conversations | Group-Object -Property { 
    $started = if ($_.PSObject.Properties.Name -contains 'started') {
        try { ([DateTime]::Parse($_.started)).ToString("yyyy-MM-dd") } catch { "unknown" }
    } else { "unknown" }
    $started
} | Sort-Object -Property Name

# Generate report
$reportDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$periodLabel = if ($Days -eq 7) { "Weekly" } elseif ($Days -eq 30) { "Monthly" } else { "$Days-Day" }

$report = @"
# Tier 1 Health Report - $periodLabel
**Generated:** $reportDate  
**Period:** Last $Days days  
**Total Conversations:** $totalConversations

---

## 📊 Executive Summary

### Overall Health
- **Auto-Recording Rate:** $utilizationRate% ($autoRecorded / $totalConversations)
- **Manual-Recording Rate:** $([math]::Round(($manualRecorded / $totalConversations) * 100, 1))% ($manualRecorded / $totalConversations)
- **Health Status:** $(if ($utilizationRate -gt 50) { "✅ HEALTHY" } elseif ($utilizationRate -gt 20) { "⚠️ WARNING" } else { "❌ CRITICAL" })

### Key Metrics
| Metric | Value |
|--------|-------|
| Total Conversations | $totalConversations |
| Auto-Recorded | $autoRecorded |
| Manual-Recorded | $manualRecorded |
| Avg Messages/Conv | $([math]::Round($messageStats.Average, 1)) |
| Total Messages | $($messageStats.Sum) |
| Max Messages | $($messageStats.Maximum) |
| Min Messages | $($messageStats.Minimum) |

---

## 📈 Recording Sources

| Source | Count | Percentage |
|--------|-------|------------|
$(foreach ($group in $sourceGroups) {
    $pct = [math]::Round(($group.Count / $totalConversations) * 100, 1)
    "| $($group.Name) | $($group.Count) | $pct% |"
})

### Analysis
$(if ($autoRecorded -eq 0) {
    "❌ **CRITICAL:** No automatic recording detected. Layer 1 (Copilot Chat) and Layer 2 (Session) not functioning."
} elseif ($utilizationRate -lt 50) {
    "⚠️ **WARNING:** Auto-recording below target (50%). Check import-copilot-chats.ps1 and session recording."
} else {
    "✅ **GOOD:** Auto-recording above target. Tier 1 functioning as designed."
})

---

## 🎯 Intent Distribution

| Intent | Count | Percentage |
|--------|-------|------------|
$(foreach ($group in $intentGroups) {
    $pct = [math]::Round(($group.Count / $totalConversations) * 100, 1)
    "| $($group.Name) | $($group.Count) | $pct% |"
})

---

## 🏷️ Top Entities Discussed

| Entity | Mentions |
|--------|----------|
$(foreach ($entity in $topEntities) {
    "| $($entity.Name) | $($entity.Count) |"
})

---

## 📁 Top Files Modified

| File | Modifications |
|------|---------------|
$(foreach ($file in $topFiles) {
    "| $($file.Name) | $($file.Count) |"
})

---

## 📅 Daily Trend

| Date | Conversations |
|------|---------------|
$(foreach ($day in $dailyTrend) {
    "| $($day.Name) | $($day.Count) |"
})

---

## 💡 Recommendations

$(if ($utilizationRate -lt 20) {
    @"
### CRITICAL: Fix Auto-Recording
1. **Check Copilot Chat Export**
   - Verify `.github/workflows/CopilotChats.txt` exists
   - Run ``.\scripts\import-copilot-chats.ps1 -DryRun`` to test parser
   
2. **Check Session Recording**
   - Verify sessions are being created in `sessions/`
   - Check `auto-brain-updater.ps1` calls `record-session-conversation.ps1`
   
3. **Fallback to Manual**
   - Use ``.\scripts\record-conversation.ps1`` for important conversations
   - Add reminder to post-commit hook
"@
} elseif ($utilizationRate -lt 50) {
    @"
### WARNING: Improve Auto-Recording
1. **Review Copilot Chat Parser**
   - Check if CopilotChats.txt format changed
   - Validate import-copilot-chats.ps1 patterns
   
2. **Enhance Session Detection**
   - Ensure all work-planner invocations create sessions
   - Check session completion triggers
"@
} else {
    @"
### GOOD: Maintain Current State
1. **Monitor Weekly**
   - Run this report weekly to track trends
   - Set up scheduled task for automation
   
2. **Continuous Improvement**
   - Review conversation quality (entities, outcomes)
   - Ensure FIFO rotation is working (20 conversation limit)
"@
})

---

## 🔧 Action Items

- [ ] $(if ($utilizationRate -lt 50) { "Fix auto-recording (see recommendations)" } else { "Continue monitoring weekly" })
- [ ] Review top entities for pattern insights
- [ ] Check if high-traffic files need better documentation
- [ ] $(if ($messageStats.Average -lt 3) { "Investigate short conversations (avg < 3 messages)" } else { "Conversation depth is healthy" })

---

**Next Report:** $(Get-Date).AddDays($Days).ToString("yyyy-MM-dd")  
**Generated by:** tier1-health-report.ps1 v7.0
"@

# Write report
Set-Content -Path $OutputPath -Value $report

Write-Host ""
Write-Host "✅ Tier 1 Health Report generated" -ForegroundColor Green
Write-Host "   Path: $OutputPath" -ForegroundColor Gray
Write-Host "   Period: Last $Days days" -ForegroundColor Gray
Write-Host "   Conversations analyzed: $totalConversations" -ForegroundColor Gray
Write-Host ""
