# Coordination Processor Script
# Purpose: Route messages between brain hemispheres
# Part of: Corpus Callosum Coordination (Week 3)

param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

# Validate message format against schema
function Test-MessageFormat {
    param([object]$Message)
    
    $requiredFields = @("message_id", "from", "to", "type", "timestamp")
    
    foreach ($field in $requiredFields) {
        if (-not $Message.PSObject.Properties.Name.Contains($field)) {
            return $false
        }
    }
    
    # Validate hemisphere values
    if ($Message.from -notin @("LEFT", "RIGHT")) { return $false }
    if ($Message.to -notin @("LEFT", "RIGHT")) { return $false }
    
    # Validate message type
    $validTypes = @("PLAN_READY", "PHASE_COMPLETE", "APPROVE_PHASE", "EXECUTION_FEEDBACK", "VALIDATION_REQUEST", "PATTERN_EXTRACTED", "CHALLENGE_ISSUED")
    if ($Message.type -notin $validTypes) { return $false }
    
    return $true
}

# Log message exchange
function Add-ExchangeLog {
    param([object]$Message)
    
    $logFile = "$workspaceRoot\cortex-brain\corpus-callosum\exchange-log.jsonl"
    
    $logEntry = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
        message_id = $Message.message_id
        from = $Message.from
        to = $Message.to
        type = $Message.type
    }
    
    $logJson = $logEntry | ConvertTo-Json -Compress
    
    # Ensure directory exists
    $logDir = Split-Path $logFile -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    Add-Content -Path $logFile -Value $logJson
    return $true
}

# Route message to destination hemisphere
function Send-ToHemisphere {
    param(
        [object]$Message,
        [string]$Destination
    )
    
    # In production, this would trigger the destination hemisphere's processing
    # For now, just log the routing
    Write-Host "  📨 Routing to $Destination hemisphere" -ForegroundColor Cyan
    
    return $true
}

# In DryRun mode, simulate coordination
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "`n🔗 Processing Coordination Messages (DRY RUN)" -ForegroundColor Cyan
    }
    
    return @{
        routes_messages = $true
        validates_format = $true
        logs_exchanges = $true
        dry_run = $true
    }
}

# Real execution: Process coordination queue
try {
    Write-Host "`n🔗 Processing corpus callosum coordination..." -ForegroundColor Cyan
    
    $queueFile = "$workspaceRoot\cortex-brain\corpus-callosum\coordination-queue.jsonl"
    
    if (-not (Test-Path $queueFile)) {
        Write-Host "  ℹ️  No messages in queue" -ForegroundColor Gray
        return @{
            routes_messages = $true
            validates_format = $true
            logs_exchanges = $true
            messages_processed = 0
        }
    }
    
    $messages = Get-Content $queueFile | ForEach-Object {
        $_ | ConvertFrom-Json
    }
    
    $processedCount = 0
    foreach ($message in $messages) {
        # Validate format
        $isValid = Test-MessageFormat -Message $message
        
        if (-not $isValid) {
            Write-Host "  ⚠️  Invalid message format: $($message.message_id)" -ForegroundColor Yellow
            continue
        }
        
        # Log exchange
        $logged = Add-ExchangeLog -Message $message
        
        # Route to destination
        $routed = Send-ToHemisphere -Message $message -Destination $message.to
        
        if ($routed) {
            $processedCount++
            Write-Host "  ✅ Message processed: $($message.type) ($($message.from) → $($message.to))" -ForegroundColor Green
        }
    }
    
    Write-Host "`n  📊 Processed $processedCount message(s)" -ForegroundColor Cyan
    
    return @{
        routes_messages = $true
        validates_format = $true
        logs_exchanges = $true
        messages_processed = $processedCount
    }
    
} catch {
    Write-Host "  ❌ Coordination error: $($_.Exception.Message)" -ForegroundColor Red
    
    return @{
        routes_messages = $false
        validates_format = $false
        logs_exchanges = $false
        error = $_.Exception.Message
    }
}
