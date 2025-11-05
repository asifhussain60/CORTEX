<#
.SYNOPSIS
Associates git commits with active Tier 1 conversations

.DESCRIPTION
V8 Enhancement - Tier 1 Git Commit Tracking
After each git commit, this script:
1. Extracts commit details (SHA, message, author, stats)
2. Finds the currently active conversation in conversation-history.jsonl
3. Adds the commit to the conversation's associated_commits array
4. Logs the association event to events.jsonl

This enables traceability between discussions and code changes.

.PARAMETER Silent
Suppress output (for use in git hooks)

.EXAMPLE
.\associate-commit-to-conversation.ps1

.EXAMPLE
.\associate-commit-to-conversation.ps1 -Silent

.NOTES
Version: 1.0 (V8 - Tier 1 Enhancement)
Part of: KDS v8.0 Real-Time Intelligence Plan
Phase: 3.5 (Git Commit Tracking)
#>

param(
    [switch]$Silent
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message)
    if (-not $Silent) {
        Write-Host $Message
    }
}

# ===================================
# STEP 1: Get Commit Details
# ===================================

try {
    $commitSha = git rev-parse HEAD
    $commitShort = $commitSha.Substring(0, 8)
    $commitMessage = git log -1 --pretty=%B HEAD
    $commitAuthor = git log -1 --pretty=%an HEAD
    $commitTime = git log -1 --pretty=%aI HEAD
    
    # Get file stats
    $statsOutput = git diff --shortstat HEAD~1 HEAD 2>$null
    $additions = 0
    $deletions = 0
    
    if ($statsOutput -match '(\d+) insertion') {
        $additions = [int]$matches[1]
    }
    if ($statsOutput -match '(\d+) deletion') {
        $deletions = [int]$matches[1]
    }
    
    # Get files changed
    $filesChanged = @(git diff-tree --no-commit-id --name-only -r HEAD)
    
    Write-Log "  Commit: $commitShort - $($commitMessage.Trim())"
    Write-Log "  Files: $($filesChanged.Count) changed, +$additions -$deletions"
}
catch {
    Write-Log "  ⚠️  Not a git commit or git command failed"
    exit 0
}

# ===================================
# STEP 2: Find Active Conversation
# ===================================

$historyPath = "kds-brain/conversation-history.jsonl"

if (-not (Test-Path $historyPath)) {
    Write-Log "  ℹ️  No conversation history found"
    exit 0
}

try {
    # Read all conversations
    $conversations = @()
    Get-Content $historyPath | ForEach-Object {
        $line = $_.Trim()
        if ($line) {
            $conversations += ($line | ConvertFrom-Json)
        }
    }
    
    if ($conversations.Count -eq 0) {
        Write-Log "  ℹ️  No conversations in history"
        exit 0
    }
    
    # Find active conversation (no end_timestamp OR most recent)
    $activeConversation = $conversations | 
        Where-Object { 
            $_.PSObject.Properties.Name -contains 'active' -and $_.active -eq $true 
        } | 
        Select-Object -Last 1
    
    # Fallback: If no explicitly active conversation, use the most recent one
    if (-not $activeConversation) {
        $activeConversation = $conversations | 
            Sort-Object { [DateTime]$_.started } -Descending | 
            Select-Object -First 1
    }
    
    if (-not $activeConversation) {
        Write-Log "  ℹ️  No active conversation found"
        exit 0
    }
    
    Write-Log "  → Conversation: $($activeConversation.conversation_id) - $($activeConversation.title)"
}
catch {
    Write-Log "  ⚠️  Error reading conversation history: $($_.Exception.Message)"
    exit 0
}

# ===================================
# STEP 3: Add Commit to Conversation
# ===================================

try {
    # Create commit object
    $commit = [PSCustomObject]@{
        sha = $commitShort
        timestamp = $commitTime
        message = $commitMessage.Trim()
        author = $commitAuthor
        files_changed = $filesChanged
        additions = $additions
        deletions = $deletions
    }
    
    # Add associated_commits property if it doesn't exist
    if (-not ($activeConversation.PSObject.Properties.Name -contains 'associated_commits')) {
        $activeConversation | Add-Member -NotePropertyName 'associated_commits' -NotePropertyValue @()
    }
    
    # Ensure it's an array
    if ($activeConversation.associated_commits -isnot [Array]) {
        $activeConversation.associated_commits = @()
    }
    
    # Add commit
    $activeConversation.associated_commits += $commit
    
    Write-Log "  ✅ Commit associated with conversation"
}
catch {
    Write-Log "  ⚠️  Error adding commit: $($_.Exception.Message)"
    exit 0
}

# ===================================
# STEP 4: Update Conversation History
# ===================================

try {
    # Rewrite entire conversation history file
    # Each conversation on its own line (JSONL format)
    $outputLines = @()
    foreach ($conv in $conversations) {
        # Convert to JSON (single line, compact)
        $json = $conv | ConvertTo-Json -Compress -Depth 10
        $outputLines += $json
    }
    
    # Write back to file
    $outputLines | Set-Content $historyPath -Encoding UTF8
    
    Write-Log "  💾 Conversation history updated"
}
catch {
    Write-Log "  ⚠️  Error updating history: $($_.Exception.Message)"
    exit 0
}

# ===================================
# STEP 5: Log Association Event
# ===================================

try {
    $associationEvent = [PSCustomObject]@{
        timestamp = Get-Date -Format "o"
        event = "git_commit_associated"
        conversation_id = $activeConversation.conversation_id
        commit_sha = $commitShort
        commit_message = $commitMessage.Trim()
        files_count = $filesChanged.Count
        additions = $additions
        deletions = $deletions
    }
    
    $eventJson = $associationEvent | ConvertTo-Json -Compress
    Add-Content "kds-brain/events.jsonl" -Value $eventJson -Encoding UTF8
    
    Write-Log "  📝 Event logged"
}
catch {
    Write-Log "  ⚠️  Error logging event: $($_.Exception.Message)"
    # Don't exit - commit association already done
}

# Success
if (-not $Silent) {
    Write-Host "✅ Git commit tracked in Tier 1 conversation" -ForegroundColor Green
}

exit 0
