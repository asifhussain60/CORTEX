<#
.SYNOPSIS
Import GitHub Copilot Chat history into Tier 1

.DESCRIPTION
Parses .github/workflows/CopilotChats.txt (or custom path) and imports
conversations into conversation-history.jsonl. This enables automatic
conversation tracking from Copilot Chat sessions.

.PARAMETER CopilotChatsPath
Path to CopilotChats.txt file (default: .github/workflows/CopilotChats.txt)

.PARAMETER DryRun
Preview import without modifying conversation-history.jsonl

.EXAMPLE
.\import-copilot-chats.ps1
Import from default .github/workflows/CopilotChats.txt

.EXAMPLE
.\import-copilot-chats.ps1 -DryRun
Preview what would be imported

.EXAMPLE
.\import-copilot-chats.ps1 -CopilotChatsPath "custom-path.txt"
Import from custom path

.NOTES
Author: KDS v7.0
Created: 2025-11-05
Part of: Tier 1 Underutilization Fix (Layer 1)
#>

[CmdletBinding()]
param(
    [string]$CopilotChatsPath = ".github/workflows/CopilotChats.txt",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Paths
$conversationHistoryPath = Join-Path $PSScriptRoot ".." "cortex-brain" "conversation-history.jsonl"

# Check if CopilotChats.txt exists
if (-not (Test-Path $CopilotChatsPath)) {
    Write-Verbose "⚠️  No CopilotChats.txt found at $CopilotChatsPath"
    Write-Host "ℹ️  GitHub Copilot Chat export not found - no conversations to import" -ForegroundColor Gray
    exit 0
}

# Read Copilot Chats file
$chatContent = Get-Content $CopilotChatsPath -Raw

# Parse conversations
# NOTE: Actual format depends on GitHub Copilot's export format
# This is a placeholder parser that needs to be adjusted based on real data

Write-Host "📝 Parsing Copilot Chat history..." -ForegroundColor Cyan

# Split into conversation blocks (assuming separator pattern)
# TODO: Adjust pattern based on actual Copilot export format
$conversationBlocks = $chatContent -split '(?m)^---+$' | Where-Object { $_.Trim() }

if ($conversationBlocks.Count -eq 0) {
    Write-Host "ℹ️  No conversations found in CopilotChats.txt" -ForegroundColor Gray
    exit 0
}

Write-Host "Found $($conversationBlocks.Count) potential conversation(s)" -ForegroundColor White

# Load existing conversations to avoid duplicates
$existingConversations = @()
if (Test-Path $conversationHistoryPath) {
    $existingConversations = @(Get-Content $conversationHistoryPath | ForEach-Object {
        try { $_ | ConvertFrom-Json } catch { $null }
    } | Where-Object { $_ -ne $null })
}

$existingIds = $existingConversations | ForEach-Object { $_.conversation_id }

# Process each conversation block
$importedCount = 0
$skippedCount = 0

foreach ($block in $conversationBlocks) {
    try {
        # Extract metadata (adjust based on actual format)
        # Example parsing - needs to match real Copilot export format
        $lines = $block -split "`n" | Where-Object { $_.Trim() }
        
        if ($lines.Count -lt 2) {
            $skippedCount++
            continue
        }
        
        # Generate conversation ID based on content hash
        $contentHash = [System.BitConverter]::ToString(
            [System.Security.Cryptography.MD5]::Create().ComputeHash(
                [System.Text.Encoding]::UTF8.GetBytes($block)
            )
        ).Replace("-", "").Substring(0, 8)
        
        $conversationId = "conv-copilot-$contentHash"
        
        # Skip if already imported
        if ($existingIds -contains $conversationId) {
            Write-Verbose "Skipping duplicate: $conversationId"
            $skippedCount++
            continue
        }
        
        # Parse messages (simplified - adjust based on format)
        $messages = @()
        $currentRole = $null
        $currentContent = ""
        
        foreach ($line in $lines) {
            if ($line -match '^(User|Assistant|Copilot):') {
                # Save previous message
                if ($currentRole -and $currentContent) {
                    $messages += @{
                        role = $currentRole.ToLower()
                        content = $currentContent.Trim()
                    }
                }
                # Start new message
                $currentRole = $matches[1]
                $currentContent = $line -replace '^(User|Assistant|Copilot):\s*', ''
            } else {
                $currentContent += " " + $line
            }
        }
        
        # Save last message
        if ($currentRole -and $currentContent) {
            $messages += @{
                role = $currentRole.ToLower()
                content = $currentContent.Trim()
            }
        }
        
        # Extract entities and files from messages
        $entities = @()
        $files = @()
        
        foreach ($msg in $messages) {
            # Extract file references (simple pattern: *.ext or path/to/file.ext)
            $fileMatches = [regex]::Matches($msg.content, '[\w/\\-]+\.\w{2,5}')
            foreach ($match in $fileMatches) {
                $files += $match.Value
            }
            
            # Extract common entities (capitalized words, technical terms)
            $entityMatches = [regex]::Matches($msg.content, '\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b')
            foreach ($match in $entityMatches) {
                if ($match.Value.Length -gt 2) {
                    $entities += $match.Value
                }
            }
        }
        
        # Deduplicate
        $entities = $entities | Select-Object -Unique
        $files = $files | Select-Object -Unique
        
        # Create conversation entry
        $conversationEntry = @{
            conversation_id = $conversationId
            title = if ($messages.Count -gt 0) { 
                ($messages[0].content -split '\n')[0].Substring(0, [Math]::Min(60, ($messages[0].content -split '\n')[0].Length)) 
            } else { 
                "Copilot Chat $contentHash" 
            }
            started = Get-Date -Format "o"
            ended = Get-Date -Format "o"
            message_count = $messages.Count
            active = $false
            intent = "UNKNOWN"
            messages = $messages
            entities_discussed = $entities
            files_modified = $files
            outcome = "Imported from Copilot Chat"
            source = "copilot_chat"
            import_date = Get-Date -Format "o"
        }
        
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would import: $($conversationEntry.title)" -ForegroundColor Yellow
            Write-Host "            Messages: $($messages.Count), Entities: $($entities.Count), Files: $($files.Count)" -ForegroundColor Gray
        } else {
            # Append to conversation-history.jsonl
            $conversationEntry | ConvertTo-Json -Compress -Depth 10 | 
                Add-Content $conversationHistoryPath
            
            Write-Host "  ✅ Imported: $($conversationEntry.title)" -ForegroundColor Green
        }
        
        $importedCount++
        
    } catch {
        Write-Warning "⚠️  Failed to parse conversation block: $_"
        $skippedCount++
    }
}

# Summary
Write-Host ""
if ($DryRun) {
    Write-Host "📊 Dry Run Summary:" -ForegroundColor Cyan
    Write-Host "   Would import: $importedCount conversation(s)" -ForegroundColor Yellow
} else {
    Write-Host "📊 Import Summary:" -ForegroundColor Cyan
    Write-Host "   Imported: $importedCount conversation(s)" -ForegroundColor Green
}
Write-Host "   Skipped: $skippedCount (duplicates or parse errors)" -ForegroundColor Gray
Write-Host ""

if ($importedCount -gt 0 -and -not $DryRun) {
    Write-Host "✅ Copilot chats imported to Tier 1 successfully" -ForegroundColor Green
    Write-Host "   Run .\scripts\monitor-tier1-health.ps1 to see updated metrics" -ForegroundColor Gray
}
