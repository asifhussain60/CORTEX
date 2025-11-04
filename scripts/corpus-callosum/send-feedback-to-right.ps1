# Send Feedback to Right Brain
# Week 4 Phase 2: Left→Right Feedback
# Sends execution metrics to right hemisphere for optimization

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [hashtable]$Metrics,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Get-CoordinationQueue {
    $queueFile = "kds-brain\corpus-callosum\coordination-queue.jsonl"
    
    if (-not (Test-Path $queueFile)) {
        # Create empty queue if doesn't exist
        $null = New-Item $queueFile -ItemType File -Force
        return @()
    }
    
    Get-Content $queueFile |
        ForEach-Object { 
            try { $_ | ConvertFrom-Json } 
            catch { $null }
        } |
        Where-Object { $_ -ne $null }
}

function Add-FeedbackMessage {
    param(
        [hashtable]$Metrics,
        [switch]$WhatIf
    )
    
    $queueFile = "kds-brain\corpus-callosum\coordination-queue.jsonl"
    
    # Ensure directory exists
    $queueDir = Split-Path $queueFile -Parent
    if (-not (Test-Path $queueDir)) {
        $null = New-Item $queueDir -ItemType Directory -Force
    }
    
    # Create feedback message
    $message = @{
        id = [guid]::NewGuid().ToString()
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        type = "EXECUTION_FEEDBACK"
        source = "left_hemisphere"
        destination = "right_hemisphere"
        priority = "normal"
        status = "pending"
        
        content = @{
            session_id = $Metrics.session_id
            collected_at = $Metrics.collected_at
            event_count = $Metrics.event_count
            
            phase_duration = $Metrics.phase_duration
            tdd_effectiveness = $Metrics.tdd_effectiveness
            test_results = $Metrics.test_results
            complexity_metrics = $Metrics.complexity_metrics
            error_recovery = $Metrics.error_recovery
            success_indicators = $Metrics.success_indicators
        }
    }
    
    if ($WhatIf) {
        Write-Verbose "WhatIf: Would add feedback message"
        return $message
    }
    
    # Append to coordination queue
    $message | ConvertTo-Json -Depth 10 -Compress | Add-Content $queueFile
    
    Write-Verbose "Added feedback message ID: $($message.id)"
    
    return $message
}

function Test-FeedbackQuality {
    param([hashtable]$Metrics)
    
    $issues = @()
    
    # Check for missing data
    if (-not $Metrics.session_id) {
        $issues += "Missing session_id"
    }
    
    if (-not $Metrics.test_results) {
        $issues += "Missing test_results"
    }
    
    if (-not $Metrics.phase_duration) {
        $issues += "Missing phase_duration"
    }
    
    # Check for completeness
    if ($Metrics.event_count -lt 5) {
        $issues += "Low event count: $($Metrics.event_count)"
    }
    
    # Check for anomalies
    if ($Metrics.test_results.failed -gt 0) {
        Write-Verbose "Session has failing tests"
    }
    
    if ($Metrics.error_recovery.errors_encountered -gt 5) {
        Write-Verbose "High error count: $($Metrics.error_recovery.errors_encountered)"
    }
    
    return @{
        is_valid = ($issues.Count -eq 0)
        issues = $issues
        quality_score = if ($issues.Count -eq 0) { 1.0 } else { [Math]::Max(0, 1.0 - ($issues.Count * 0.2)) }
    }
}

function Get-FeedbackPriority {
    param([hashtable]$Metrics)
    
    # Determine priority based on metrics
    
    # High priority if:
    # - Tests failing
    # - Many errors
    # - TDD not followed
    # - Performance issues
    
    if ($Metrics.test_results.failed -gt 0) {
        return "high"
    }
    
    if ($Metrics.error_recovery.errors_encountered -gt 3) {
        return "high"
    }
    
    if (-not $Metrics.tdd_effectiveness.tdd_followed) {
        return "high"
    }
    
    # Medium priority if:
    # - Slow phase execution
    # - High complexity
    
    $totalDuration = ($Metrics.phase_duration.Values | Measure-Object -Sum).Sum
    if ($totalDuration -gt 1800) { # > 30 minutes
        return "medium"
    }
    
    if ($Metrics.complexity_metrics.files_created -gt 10) {
        return "medium"
    }
    
    # Low priority otherwise
    return "normal"
}

function Log-FeedbackSent {
    param(
        [hashtable]$Message,
        [hashtable]$Quality
    )
    
    $logFile = "kds-brain\corpus-callosum\feedback-log.jsonl"
    
    # Ensure directory exists
    $logDir = Split-Path $logFile -Parent
    if (-not (Test-Path $logDir)) {
        $null = New-Item $logDir -ItemType Directory -Force
    }
    
    $logEntry = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        type = "feedback_sent"
        message_id = $Message.id
        session_id = $Message.content.session_id
        priority = $Message.priority
        quality_score = $Quality.quality_score
        is_valid = $Quality.is_valid
        issues = $Quality.issues
    }
    
    $logEntry | ConvertTo-Json -Depth 10 -Compress | Add-Content $logFile
    
    Write-Verbose "Logged feedback sent"
}

# Main execution
try {
    Write-Verbose "Starting feedback transmission"
    
    if ($WhatIf) {
        Write-Host "⚙️  WhatIf mode: Would send feedback to right brain" -ForegroundColor Yellow
        
        # Validate metrics
        $quality = Test-FeedbackQuality -Metrics $Metrics
        $priority = Get-FeedbackPriority -Metrics $Metrics
        
        Write-Host "  Quality Score: $($quality.quality_score)" -ForegroundColor Cyan
        Write-Host "  Priority: $priority" -ForegroundColor Cyan
        
        if ($quality.issues.Count -gt 0) {
            Write-Host "  Issues: $($quality.issues -join ', ')" -ForegroundColor Yellow
        }
        
        # Create mock message
        $message = Add-FeedbackMessage -Metrics $Metrics -WhatIf
        $message.priority = $priority
        
        return @{
            message_id = $message.id
            priority = $priority
            quality = $quality
            sent = $false
            success = $true
            whatif = $true
        }
    }
    
    # Validate feedback quality
    Write-Verbose "Validating feedback quality"
    $quality = Test-FeedbackQuality -Metrics $Metrics
    
    if (-not $quality.is_valid) {
        Write-Warning "Feedback quality issues detected: $($quality.issues -join ', ')"
    }
    
    Write-Verbose "Quality score: $($quality.quality_score)"
    
    # Determine priority
    $priority = Get-FeedbackPriority -Metrics $Metrics
    Write-Verbose "Feedback priority: $priority"
    
    # Add to coordination queue
    $message = Add-FeedbackMessage -Metrics $Metrics
    $message.priority = $priority
    
    # Log the feedback transmission
    Log-FeedbackSent -Message $message -Quality $quality
    
    Write-Host "✅ Feedback sent to right brain" -ForegroundColor Green
    Write-Host "  Message ID: $($message.id)" -ForegroundColor Cyan
    Write-Host "  Priority: $priority" -ForegroundColor Cyan
    Write-Host "  Quality: $($quality.quality_score)" -ForegroundColor Cyan
    
    return @{
        message_id = $message.id
        timestamp = $message.timestamp
        priority = $priority
        quality = $quality
        sent = $true
        success = $true
    }
    
} catch {
    Write-Error "Feedback transmission failed: $_"
    throw
}
