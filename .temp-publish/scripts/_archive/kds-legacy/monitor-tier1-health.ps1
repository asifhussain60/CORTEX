<#
.SYNOPSIS
Monitor Tier 1 health and auto-record statistics

.DESCRIPTION
Tracks Tier 1 utilization, alerts if underutilized,
logs metrics to development-context.yaml

.EXAMPLE
.\monitor-tier1-health.ps1
Runs health check and logs metrics

.EXAMPLE
.\monitor-tier1-health.ps1 -Verbose
Runs with detailed output

.NOTES
Author: KDS v7.0
Created: 2025-11-05
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# Paths
$conversationHistoryPath = Join-Path $PSScriptRoot ".." "cortex-brain" "conversation-history.jsonl"
$developmentContextPath = Join-Path $PSScriptRoot ".." "cortex-brain" "development-context.yaml"

# Check if conversation history exists
if (-not (Test-Path $conversationHistoryPath)) {
    Write-Warning "⚠️  conversation-history.jsonl not found - Tier 1 not initialized"
    exit 1
}

# Count conversations
$conversations = @(Get-Content $conversationHistoryPath | ForEach-Object { 
    try { $_ | ConvertFrom-Json } catch { $null }
} | Where-Object { $_ -ne $null })

$totalConversations = $conversations.Count

# Analyze sources
$sourceGroups = $conversations | Group-Object -Property { 
    if ($_.PSObject.Properties.Name -contains 'source') { $_.source } else { 'unknown' }
}

$autoRecorded = 0
$manualRecorded = 0
$unknownSource = 0

foreach ($group in $sourceGroups) {
    switch ($group.Name) {
        { $_ -in @('copilot_chat', 'session_recording') } {
            $autoRecorded += $group.Count
        }
        'manual_recording' {
            $manualRecorded += $group.Count
        }
        default {
            $unknownSource += $group.Count
        }
    }
}

# Calculate utilization
$utilizationRate = if ($totalConversations -gt 0) { 
    [math]::Round(($autoRecorded / $totalConversations) * 100, 1) 
} else { 
    0.0 
}

# Calculate FIFO capacity (max 20 conversations)
$fifoCapacity = [math]::Round(($totalConversations / 20) * 100, 1)

# Calculate average message count
$avgMessageCount = if ($totalConversations -gt 0) {
    $totalMessages = ($conversations | Where-Object { $_.PSObject.Properties.Name -contains 'message_count' } | 
        Measure-Object -Property message_count -Average).Average
    [math]::Round($totalMessages, 1)
} else {
    0
}

# Display stats
Write-Host ""
Write-Host "📊 Tier 1 Utilization Report" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Total Conversations: $totalConversations / 20 (FIFO capacity: $fifoCapacity%)" -ForegroundColor White
Write-Host "Auto-recorded: $autoRecorded" -ForegroundColor $(if ($autoRecorded -gt 0) { "Green" } else { "Yellow" })
Write-Host "Manual-recorded: $manualRecorded" -ForegroundColor Yellow
Write-Host "Unknown source: $unknownSource" -ForegroundColor Gray
Write-Host "Auto-Recording Rate: $utilizationRate%" -ForegroundColor $(if ($utilizationRate -gt 50) { "Green" } elseif ($utilizationRate -gt 20) { "Yellow" } else { "Red" })
Write-Host "Avg Messages/Conv: $avgMessageCount" -ForegroundColor White

# Alert if underutilized
if ($utilizationRate -lt 50 -and $totalConversations -gt 5) {
    Write-Host ""
    Write-Host "⚠️  WARNING: Tier 1 underutilized!" -ForegroundColor Red
    Write-Host "   - Auto-recording is not working effectively" -ForegroundColor Yellow
    Write-Host "   - Check Copilot Chat export integration (.github/workflows/CopilotChats.txt)" -ForegroundColor Yellow
    Write-Host "   - Check session-based recording (sessions/*.json)" -ForegroundColor Yellow
    Write-Host "   - Consider using manual recording: .\scripts\record-conversation.ps1" -ForegroundColor Yellow
}

# Build metrics object
$tier1Metrics = @{
    total_conversations = $totalConversations
    auto_recorded = $autoRecorded
    manual_recorded = $manualRecorded
    unknown_source = $unknownSource
    utilization_rate = $utilizationRate
    fifo_capacity = $fifoCapacity
    avg_message_count = $avgMessageCount
    last_updated = (Get-Date -Format "o")
    status = if ($utilizationRate -gt 50) { "healthy" } elseif ($utilizationRate -gt 20) { "warning" } else { "critical" }
}

# Log to development-context.yaml
try {
    if (Test-Path $developmentContextPath) {
        # Read existing YAML
        $yamlContent = Get-Content $developmentContextPath -Raw
        
        # Simple YAML update (append or replace tier1_metrics section)
        $metricsYaml = @"

# Tier 1 Health Metrics (Auto-updated by monitor-tier1-health.ps1)
tier1_metrics:
  total_conversations: $($tier1Metrics.total_conversations)
  auto_recorded: $($tier1Metrics.auto_recorded)
  manual_recorded: $($tier1Metrics.manual_recorded)
  unknown_source: $($tier1Metrics.unknown_source)
  utilization_rate: $($tier1Metrics.utilization_rate)
  fifo_capacity: $($tier1Metrics.fifo_capacity)
  avg_message_count: $($tier1Metrics.avg_message_count)
  last_updated: "$($tier1Metrics.last_updated)"
  status: $($tier1Metrics.status)
"@

        # Remove existing tier1_metrics section
        $yamlContent = $yamlContent -replace '(?ms)# Tier 1 Health Metrics.*?(?=\n[a-z_]+:|$)', ''
        
        # Append new metrics
        $yamlContent = $yamlContent.TrimEnd() + "`n" + $metricsYaml
        
        # Write back
        Set-Content -Path $developmentContextPath -Value $yamlContent -NoNewline
        
        Write-Host ""
        Write-Host "✅ Tier 1 health metrics logged to development-context.yaml" -ForegroundColor Green
    } else {
        Write-Warning "⚠️  development-context.yaml not found - metrics not logged"
    }
} catch {
    Write-Warning "⚠️  Failed to update development-context.yaml: $_"
}

# Return metrics for programmatic use
return $tier1Metrics
