<#
.SYNOPSIS
    Clear coordination queue (for testing/maintenance)

.DESCRIPTION
    Removes all messages or only processed messages from coordination queue.

.PARAMETER All
    Clear all messages (including unprocessed)

.PARAMETER ProcessedOnly
    Clear only processed messages (default)

.EXAMPLE
    .\clear-queue.ps1 -ProcessedOnly
    
.EXAMPLE
    .\clear-queue.ps1 -All

.NOTES
    Version: 6.0.0-Week1
#>

param(
    [switch]$All
)

$ErrorActionPreference = "Stop"

# Paths
$workspaceRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$queueFile = Join-Path $workspaceRoot "KDS\cortex-brain\corpus-callosum\coordination-queue.jsonl"

if (-not (Test-Path $queueFile)) {
    Write-Host "ℹ️  Queue file doesn't exist - nothing to clear" -ForegroundColor Cyan
    return
}

if ($All) {
    # Clear everything
    Set-Content $queueFile -Value "" -Encoding UTF8
    Write-Host "✅ All messages cleared from queue" -ForegroundColor Green
} else {
    # Keep only unprocessed messages
    $messages = Get-Content $queueFile -Encoding UTF8 | ForEach-Object {
        if ($_.Trim()) {
            $_ | ConvertFrom-Json
        }
    }
    
    $unprocessed = $messages | Where-Object { $_.processed -eq $false }
    
    if ($unprocessed) {
        $unprocessed | ForEach-Object {
            $_ | ConvertTo-Json -Compress -Depth 10
        } | Set-Content $queueFile -Encoding UTF8
        
        Write-Host "✅ Cleared processed messages ($($messages.Count - $unprocessed.Count) removed, $($unprocessed.Count) kept)" -ForegroundColor Green
    } else {
        Set-Content $queueFile -Value "" -Encoding UTF8
        Write-Host "✅ All messages were processed - queue cleared" -ForegroundColor Green
    }
}
