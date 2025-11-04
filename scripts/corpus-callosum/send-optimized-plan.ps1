# Send Optimized Plan
# Week 4 Phase 3: Right→Left Optimization
# Sends optimized plan from right brain back to left hemisphere

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [hashtable]$OptimizedPlan,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$Plan,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Add-OptimizationMessage {
    param(
        [hashtable]$Plan,
        [switch]$WhatIf
    )
    
    $queueFile = "kds-brain\corpus-callosum\coordination-queue.jsonl"
    
    # Ensure directory exists
    $queueDir = Split-Path $queueFile -Parent
    if (-not (Test-Path $queueDir)) {
        $null = New-Item $queueDir -ItemType Directory -Force
    }
    
    # Create optimization message
    $message = @{
        id = [guid]::NewGuid().ToString()
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        type = "plan_optimization"
        source = "right_hemisphere"
        destination = "left_hemisphere"
        priority = Get-MessagePriority -Plan $Plan
        status = "pending"
        
        content = @{
            session_id = $Plan.based_on_session
            generated_at = $Plan.generated_at
            total_optimizations = $Plan.total_optimizations
            estimated_time_saved = $Plan.impact_summary.estimated_time_saved
            
            optimizations = $Plan.optimizations
            recommendations = $Plan.recommendations
        }
    }
    
    if ($WhatIf) {
        Write-Verbose "WhatIf: Would add optimization message"
        return $message
    }
    
    # Append to coordination queue
    $message | ConvertTo-Json -Depth 10 -Compress | Add-Content $queueFile
    
    Write-Verbose "Added optimization message ID: $($message.id)"
    
    return $message
}

function Get-MessagePriority {
    param([hashtable]$Plan)
    
    $immediateCount = ($Plan.recommendations.immediate ?? @()).Count
    $totalSavings = $Plan.impact_summary.estimated_time_saved
    
    # Critical if there are critical recommendations
    $hasCritical = $Plan.optimizations | Where-Object { ($_.priority ?? "medium") -eq "critical" }
    if ($hasCritical) {
        return "critical"
    }
    
    # High if many immediate actions or large time savings
    if ($immediateCount -gt 3 -or $totalSavings -gt 600) {
        return "high"
    }
    
    # Medium if some immediate actions
    if ($immediateCount -gt 0) {
        return "medium"
    }
    
    # Low otherwise
    return "normal"
}

function Log-OptimizationSent {
    param([hashtable]$Message)
    
    $logFile = "kds-brain\corpus-callosum\optimization-log.jsonl"
    
    # Ensure directory exists
    $logDir = Split-Path $logFile -Parent
    if (-not (Test-Path $logDir)) {
        $null = New-Item $logDir -ItemType Directory -Force
    }
    
    $logEntry = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        type = "optimization_sent"
        message_id = $Message.id
        session_id = $Message.content.session_id
        priority = $Message.priority
        optimization_count = $Message.content.total_optimizations
        estimated_savings = $Message.content.estimated_time_saved
    }
    
    $logEntry | ConvertTo-Json -Depth 10 -Compress | Add-Content $logFile
    
    Write-Verbose "Logged optimization sent"
}

function Save-OptimizedPlanToRightBrain {
    param([hashtable]$Plan)
    
    $planFile = "kds-brain\right-hemisphere\optimized-plans.jsonl"
    
    # Ensure directory exists
    $planDir = Split-Path $planFile -Parent
    if (-not (Test-Path $planDir)) {
        $null = New-Item $planDir -ItemType Directory -Force
    }
    
    # Save plan to right brain storage
    $Plan | ConvertTo-Json -Depth 10 -Compress | Add-Content $planFile
    
    Write-Verbose "Saved optimized plan to right brain"
}

# Main execution
try {
    Write-Verbose "Starting optimized plan transmission"
    
    # Handle both -Plan and -OptimizedPlan parameters (for backward compatibility)
    if ($Plan -and -not $OptimizedPlan) {
        $OptimizedPlan = $Plan
    }
    
    if ($WhatIf) {
        Write-Host "⚙️  WhatIf mode: Would send optimized plan to left brain" -ForegroundColor Yellow
        
        # Mock plan if none provided
        if (-not $OptimizedPlan) {
            $OptimizedPlan = @{
                total_optimizations = 2
                impact_summary = @{ estimated_time_saved = 540 }
                optimizations = @()
            }
        }
        
        # Show what would be sent
        $priority = Get-MessagePriority -Plan $OptimizedPlan
        
        Write-Host "  Priority: $priority" -ForegroundColor Cyan
        Write-Host "  Optimizations: $($OptimizedPlan.total_optimizations)" -ForegroundColor Cyan
        
        # Create mock message
        $message = Add-OptimizationMessage -Plan $OptimizedPlan -WhatIf
        
        return @{
            message_id = $message.id
            priority = $priority
            sent = $false
            success = $true
            whatif = $true
        }
    }
    
    # Validate plan has required fields
    if (-not $OptimizedPlan -or -not $OptimizedPlan.optimizations) {
        Write-Warning "No optimizations in plan"
        return @{
            error = "No optimizations to send"
            sent = $false
        }
    }
    
    # Save plan to right brain storage
    Write-Verbose "Saving plan to right brain"
    Save-OptimizedPlanToRightBrain -Plan $OptimizedPlan
    
    # Add to coordination queue
    Write-Verbose "Adding to coordination queue"
    $message = Add-OptimizationMessage -Plan $OptimizedPlan
    
    # Log the transmission
    Log-OptimizationSent -Message $message
    
    Write-Host "✅ Optimized plan sent to left brain" -ForegroundColor Green
    Write-Host "  Message ID: $($message.id)" -ForegroundColor Cyan
    Write-Host "  Priority: $($message.priority)" -ForegroundColor Cyan
    Write-Host "  Optimizations: $($OptimizedPlan.total_optimizations)" -ForegroundColor Cyan
    Write-Host "  Estimated savings: $($OptimizedPlan.impact_summary.estimated_time_saved)s" -ForegroundColor Cyan
    
    return @{
        message_id = $message.id
        timestamp = $message.timestamp
        priority = $message.priority
        optimization_count = $OptimizedPlan.total_optimizations
        sent = $true
        success = $true
    }
    
} catch {
    Write-Error "Optimized plan transmission failed: $_"
    throw
}
