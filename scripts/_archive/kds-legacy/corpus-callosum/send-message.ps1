<#
.SYNOPSIS
    Send inter-hemisphere message via corpus callosum

.DESCRIPTION
    Sends a message from one brain hemisphere to another through the coordination queue.
    Messages are stored in corpus-callosum/coordination-queue.jsonl

.PARAMETER From
    Source hemisphere: "left" or "right"

.PARAMETER To
    Destination hemisphere: "left" or "right"

.PARAMETER Type
    Message type: "validation_request", "planning_update", "execution_complete", "pattern_learned", "rollback_needed"

.PARAMETER Data
    Message payload (hashtable or PSObject)

.PARAMETER Priority
    Message priority: "high", "normal", "low" (default: "normal")

.EXAMPLE
    .\send-message.ps1 -From "right" -To "left" -Type "planning_update" -Data @{task="1.1"; file="Test.cs"}

.NOTES
    Version: 6.0.0-Week1
    Part of: KDS v6.0 Progressive Intelligence Implementation
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("left", "right")]
    [string]$From,

    [Parameter(Mandatory=$true)]
    [ValidateSet("left", "right")]
    [string]$To,

    [Parameter(Mandatory=$true)]
    [ValidateSet("validation_request", "planning_update", "execution_complete", "pattern_learned", "rollback_needed")]
    [string]$Type,

    [Parameter(Mandatory=$true)]
    [object]$Data,

    [ValidateSet("high", "normal", "low")]
    [string]$Priority = "normal"
)

$ErrorActionPreference = "Stop"

# Paths
$workspaceRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$queueFile = Join-Path $workspaceRoot "KDS\cortex-brain\corpus-callosum\coordination-queue.jsonl"

# Create message object
$message = @{
    id = [Guid]::NewGuid().ToString()
    timestamp = (Get-Date).ToUniversalTime().ToString("o")
    from = $From
    to = $To
    type = $Type
    data = $Data
    priority = $Priority
    processed = $false
}

# Convert to JSON (compact, single line)
$jsonLine = $message | ConvertTo-Json -Compress -Depth 10

# Append to queue file
Add-Content -Path $queueFile -Value $jsonLine -Encoding UTF8

# Output confirmation
Write-Host "✅ Message sent: $From → $To ($Type)" -ForegroundColor Green
Write-Host "   ID: $($message.id)" -ForegroundColor Gray

# Return message for chaining
return $message
