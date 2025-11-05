<#
.SYNOPSIS
Record active KDS session to conversation-history.jsonl

.DESCRIPTION
Converts active session JSON to conversation format.
Part of Layer 2 auto-recording (session-based tracking).

.PARAMETER SessionFile
Path to session JSON file

.PARAMETER Force
Force recording even if session is still active

.EXAMPLE
.\record-session-conversation.ps1 -SessionFile "sessions/current-session.json"
Records completed session to Tier 1

.EXAMPLE
.\record-session-conversation.ps1 -SessionFile "sessions/session-123.json" -Force
Force record even if session active

.NOTES
Author: KDS v7.0
Created: 2025-11-05
Part of: Tier 1 Underutilization Fix (Layer 2)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$SessionFile,
    
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Paths
$conversationHistoryPath = Join-Path $PSScriptRoot ".." "kds-brain" "conversation-history.jsonl"

# Check if session file exists
if (-not (Test-Path $SessionFile)) {
    Write-Error "Session file not found: $SessionFile"
    exit 1
}

# Read session
try {
    $session = Get-Content $SessionFile -Raw | ConvertFrom-Json
} catch {
    Write-Error "Failed to parse session file: $_"
    exit 1
}

# Validate session structure
$requiredFields = @('session_id', 'title', 'start_time')
foreach ($field in $requiredFields) {
    if (-not ($session.PSObject.Properties.Name -contains $field)) {
        Write-Error "Session file missing required field: $field"
        exit 1
    }
}

# Check if session is still active
if (-not $Force) {
    $isActive = $session.PSObject.Properties.Name -contains 'active' -and $session.active
    if ($isActive) {
        Write-Verbose "Session is still active - skipping (use -Force to override)"
        exit 0
    }
}

# Load existing conversations to avoid duplicates
$existingConversations = @()
if (Test-Path $conversationHistoryPath) {
    $existingConversations = @(Get-Content $conversationHistoryPath | ForEach-Object {
        try { $_ | ConvertFrom-Json } catch { $null }
    } | Where-Object { $_ -ne $null })
}

$conversationId = "conv-session-$($session.session_id)"
$existingIds = $existingConversations | ForEach-Object { $_.conversation_id }

# Skip if already recorded
if ($existingIds -contains $conversationId) {
    Write-Verbose "Session already recorded: $conversationId"
    exit 0
}

# Extract conversation details
$messages = @()
$messageCount = 0

# Convert tasks to messages (if available)
if ($session.PSObject.Properties.Name -contains 'tasks') {
    foreach ($task in $session.tasks) {
        $taskContent = if ($task -is [string]) {
            $task
        } elseif ($task.PSObject.Properties.Name -contains 'description') {
            $task.description
        } elseif ($task.PSObject.Properties.Name -contains 'title') {
            $task.title
        } else {
            "Task: $($task | ConvertTo-Json -Compress)"
        }
        
        $messages += @{
            role = "user"
            content = $taskContent
            timestamp = $session.start_time
        }
        $messageCount++
    }
}

# If no tasks, create single message from session
if ($messages.Count -eq 0) {
    $messages = @(@{
        role = "user"
        content = $session.title
        timestamp = $session.start_time
    })
    $messageCount = 1
}

# Extract entities
$entities = @()
if ($session.PSObject.Properties.Name -contains 'entities') {
    $entities = $session.entities
} elseif ($session.PSObject.Properties.Name -contains 'tags') {
    $entities = $session.tags
}

# Extract files
$files = @()
if ($session.PSObject.Properties.Name -contains 'files_modified') {
    $files = $session.files_modified
} elseif ($session.PSObject.Properties.Name -contains 'files') {
    $files = $session.files
}

# Extract outcome
$outcome = "Session completed"
if ($session.PSObject.Properties.Name -contains 'outcome') {
    $outcome = $session.outcome
} elseif ($session.PSObject.Properties.Name -contains 'status') {
    $outcome = "Session status: $($session.status)"
}

# Extract intent
$intent = "EXECUTE"
if ($session.PSObject.Properties.Name -contains 'intent') {
    $intent = $session.intent
} elseif ($session.PSObject.Properties.Name -contains 'type') {
    $intent = $session.type.ToUpper()
}

# Create conversation entry
$conversationEntry = @{
    conversation_id = $conversationId
    title = $session.title
    started = $session.start_time
    ended = if ($session.PSObject.Properties.Name -contains 'end_time') { 
        $session.end_time 
    } else { 
        Get-Date -Format "o" 
    }
    message_count = $messageCount
    active = $false
    intent = $intent
    messages = $messages
    entities_discussed = $entities
    files_modified = $files
    outcome = $outcome
    source = "session_recording"
    session_id = $session.session_id
    import_date = Get-Date -Format "o"
}

# Append to conversation-history.jsonl
try {
    $conversationEntry | ConvertTo-Json -Compress -Depth 10 | 
        Add-Content $conversationHistoryPath
    
    Write-Host "✅ Session recorded to Tier 1: $($session.title)" -ForegroundColor Green
    Write-Host "   Session ID: $($session.session_id)" -ForegroundColor Gray
    Write-Host "   Messages: $messageCount, Entities: $($entities.Count), Files: $($files.Count)" -ForegroundColor Gray
    
} catch {
    Write-Error "Failed to write to conversation-history.jsonl: $_"
    exit 1
}
