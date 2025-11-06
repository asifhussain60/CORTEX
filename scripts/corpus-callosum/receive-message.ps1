<#
.SYNOPSIS
    Receive messages for a hemisphere from coordination queue

.DESCRIPTION
    Retrieves unprocessed messages for a specified hemisphere.
    Optionally marks messages as processed.

.PARAMETER For
    Destination hemisphere: "left" or "right"

.PARAMETER Type
    Filter by message type (optional)

.PARAMETER MarkProcessed
    Mark retrieved messages as processed (default: $true)

.PARAMETER Latest
    Return only the most recent message (default: $false)

.EXAMPLE
    .\receive-message.ps1 -For "left"
    
.EXAMPLE
    .\receive-message.ps1 -For "right" -Type "validation_request" -Latest

.NOTES
    Version: 6.0.0-Week1
    Part of: KDS v6.0 Progressive Intelligence Implementation
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("left", "right")]
    [string]$For,

    [ValidateSet("validation_request", "planning_update", "execution_complete", "pattern_learned", "rollback_needed")]
    [string]$Type,

    [bool]$MarkProcessed = $true,

    [switch]$Latest
)

$ErrorActionPreference = "Stop"

# Paths
$workspaceRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$queueFile = Join-Path $workspaceRoot "KDS\cortex-brain\corpus-callosum\coordination-queue.jsonl"

# Check if queue file exists
if (-not (Test-Path $queueFile)) {
    Write-Host "⚠️  No messages in queue (file doesn't exist yet)" -ForegroundColor Yellow
    return @()
}

# Read all messages
$allMessages = Get-Content $queueFile -Encoding UTF8 | ForEach-Object {
    if ($_.Trim()) {
        $_ | ConvertFrom-Json
    }
}

# Filter unprocessed messages for this hemisphere
$messages = $allMessages | Where-Object {
    $_.to -eq $For -and $_.processed -eq $false
}

# Further filter by type if specified
if ($Type) {
    $messages = $messages | Where-Object { $_.type -eq $Type }
}

# Sort by priority (high > normal > low) and timestamp
$priorityOrder = @{high=0; normal=1; low=2}
$messages = $messages | Sort-Object {$priorityOrder[$_.priority]}, timestamp

# Return latest if requested
if ($Latest -and $messages) {
    $messages = @($messages[0])
}

if (-not $messages) {
    Write-Host "ℹ️  No unprocessed messages for $For hemisphere" -ForegroundColor Cyan
    return @()
}

# Mark as processed if requested
if ($MarkProcessed -and $messages) {
    $messagesToMark = $messages | ForEach-Object { $_.id }
    
    # Update messages in memory
    $allMessages = $allMessages | ForEach-Object {
        if ($messagesToMark -contains $_.id) {
            $_.processed = $true
        }
        $_
    }
    
    # Rewrite queue file
    $allMessages | ForEach-Object {
        $_ | ConvertTo-Json -Compress -Depth 10
    } | Set-Content $queueFile -Encoding UTF8
}

# Output
Write-Host "✅ Retrieved $($messages.Count) message(s) for $For hemisphere" -ForegroundColor Green
foreach ($msg in $messages) {
    Write-Host "   • $($msg.type) from $($msg.from) ($(($msg.timestamp -as [DateTime]).ToLocalTime()))" -ForegroundColor Gray
}

return $messages
