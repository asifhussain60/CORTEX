#!/usr/bin/env pwsh
<#
.SYNOPSIS
    CORTEX conversation capture script - bridges Copilot Chat to Python tracking system

.DESCRIPTION
    This script solves the conversation memory gap by:
    1. Accepting conversation details from Copilot Chat sessions
    2. Calling Python CortexEntry.process() for proper tracking
    3. Ensuring all messages are logged to Tier 1 (conversations.db)
    4. Validating that conversation tracking is working

.PARAMETER Message
    The user message to process

.PARAMETER Intent
    Optional intent classification (PLAN, EXECUTE, TEST, etc.)

.PARAMETER AutoDetect
    Auto-detect conversation from clipboard or last terminal output

.EXAMPLE
    .\cortex-capture.ps1 -Message "Create mkdocs documentation"
    
.EXAMPLE
    .\cortex-capture.ps1 -AutoDetect
    
.NOTES
    This is a CRITICAL brain function (Tier 1 - Working Memory)
    Protected by brain-protector tests
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Message,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('PLAN', 'EXECUTE', 'TEST', 'VALIDATE', 'GOVERN', 'ASK')]
    [string]$Intent,
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoDetect,
    
    [Parameter(Mandatory=$false)]
    [switch]$Validate
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# Ensure Python environment is activated
$PythonCmd = if ($env:VIRTUAL_ENV) { 
    "python" 
} else { 
    Write-Warning "Virtual environment not activated. Attempting to activate..."
    & "$ProjectRoot\venv\Scripts\Activate.ps1"
    "python"
}

function Write-CortexLog {
    param($Level, $Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "INFO" { "Cyan" }
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Get-AutoDetectedMessage {
    Write-CortexLog "INFO" "Auto-detecting conversation from clipboard..."
    
    # Try clipboard first
    try {
        $clipboardText = Get-Clipboard -ErrorAction SilentlyContinue
        if ($clipboardText -and $clipboardText.Length -gt 10) {
            Write-CortexLog "SUCCESS" "Found message in clipboard"
            return $clipboardText
        }
    } catch {
        Write-CortexLog "WARNING" "Could not access clipboard"
    }
    
    # Fall back to manual input
    Write-Host "`nNo message detected. Please enter your conversation:"
    Write-Host "(Type your message and press ENTER twice when done)"
    Write-Host "─────────────────────────────────────────────────────"
    
    $lines = @()
    while ($true) {
        $line = Read-Host
        if ([string]::IsNullOrWhiteSpace($line) -and $lines.Count -gt 0) {
            break
        }
        if (-not [string]::IsNullOrWhiteSpace($line)) {
            $lines += $line
        }
    }
    
    return ($lines -join "`n")
}

function Invoke-PythonTracking {
    param(
        [string]$UserMessage,
        [string]$Intent
    )
    
    Write-CortexLog "INFO" "Invoking Python conversation tracking..."
    
    # Create Python script to call CortexEntry.process()
    $pythonScript = @"
import sys
import json
from pathlib import Path

# Add CORTEX to path
cortex_path = Path('$ProjectRoot') / 'CORTEX' / 'src'
sys.path.insert(0, str(cortex_path))

from entry_point.cortex_entry import CortexEntry

def main():
    user_message = '''$UserMessage'''
    intent = '$Intent' if '$Intent' else None
    
    # Initialize CORTEX entry point
    entry = CortexEntry(
        brain_path='$ProjectRoot/cortex-brain',
        enable_logging=True
    )
    
    # Process message (this triggers Tier 1 tracking)
    metadata = {}
    if intent:
        metadata['intent_hint'] = intent
    
    response = entry.process(
        user_message=user_message,
        resume_session=True,
        format_type='text',
        metadata=metadata
    )
    
    # Get conversation info to verify tracking
    session_info = entry.get_session_info()
    
    result = {
        'success': True,
        'response': response,
        'session_info': session_info,
        'conversation_id': session_info.get('conversation_id') if session_info else None
    }
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }), file=sys.stderr)
        sys.exit(1)
"@

    # Write temp Python script
    $tempScript = "$env:TEMP\cortex_track_$(Get-Random).py"
    $pythonScript | Out-File -FilePath $tempScript -Encoding UTF8
    
    try {
        # Execute Python tracking
        $result = & $PythonCmd $tempScript 2>&1 | Out-String
        
        # Parse result
        try {
            $resultObj = $result | ConvertFrom-Json
            
            if ($resultObj.success) {
                Write-CortexLog "SUCCESS" "Conversation tracked successfully"
                Write-CortexLog "INFO" "Conversation ID: $($resultObj.conversation_id)"
                
                if ($resultObj.session_info) {
                    Write-Host "`nSession Info:" -ForegroundColor Cyan
                    Write-Host "  Messages: $($resultObj.session_info.message_count)" -ForegroundColor White
                    Write-Host "  Started: $($resultObj.session_info.start_time)" -ForegroundColor White
                }
                
                return $resultObj
            } else {
                Write-CortexLog "ERROR" "Tracking failed: $($resultObj.error)"
                return $null
            }
        } catch {
            Write-CortexLog "ERROR" "Failed to parse Python response: $_"
            Write-Host "`nRaw output:" -ForegroundColor Yellow
            Write-Host $result
            return $null
        }
    } finally {
        # Cleanup temp script
        if (Test-Path $tempScript) {
            Remove-Item $tempScript -Force
        }
    }
}

function Test-ConversationTracking {
    Write-CortexLog "INFO" "Validating conversation tracking system..."
    
    # Check database exists
    $dbPath = "$ProjectRoot/cortex-brain/tier1/conversations.db"
    if (-not (Test-Path $dbPath)) {
        Write-CortexLog "ERROR" "Conversations database not found: $dbPath"
        return $false
    }
    
    # Run Python validation
    $validationScript = @"
import sys
import sqlite3
from pathlib import Path

db_path = Path('$dbPath')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check conversations table
    cursor.execute('SELECT COUNT(*) FROM conversations')
    conv_count = cursor.fetchone()[0]
    
    # Check messages table
    cursor.execute('SELECT COUNT(*) FROM messages')
    msg_count = cursor.fetchone()[0]
    
    # Check recent activity (last 24 hours)
    cursor.execute('''
        SELECT COUNT(*) FROM messages 
        WHERE timestamp > datetime('now', '-1 day')
    ''')
    recent_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f'✅ Conversations: {conv_count}')
    print(f'✅ Messages: {msg_count}')
    print(f'✅ Recent (24h): {recent_count}')
    
    if msg_count == 0:
        print('⚠️  WARNING: No messages in database!')
        sys.exit(1)
    
except Exception as e:
    print(f'❌ ERROR: {e}')
    sys.exit(1)
"@

    $tempValidation = "$env:TEMP\cortex_validate_$(Get-Random).py"
    $validationScript | Out-File -FilePath $tempValidation -Encoding UTF8
    
    try {
        $output = & $PythonCmd $tempValidation 2>&1
        Write-Host $output
        return $LASTEXITCODE -eq 0
    } finally {
        if (Test-Path $tempValidation) {
            Remove-Item $tempValidation -Force
        }
    }
}

# Main execution
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   CORTEX CONVERSATION CAPTURE" -ForegroundColor Cyan
Write-Host "   Tier 1 Working Memory Bridge" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Validation mode
if ($Validate) {
    $isValid = Test-ConversationTracking
    if ($isValid) {
        Write-CortexLog "SUCCESS" "Conversation tracking is operational ✅"
        exit 0
    } else {
        Write-CortexLog "ERROR" "Conversation tracking validation failed ❌"
        exit 1
    }
}

# Get message
if ($AutoDetect -or -not $Message) {
    $Message = Get-AutoDetectedMessage
}

if ([string]::IsNullOrWhiteSpace($Message)) {
    Write-CortexLog "ERROR" "No message to process"
    exit 1
}

Write-CortexLog "INFO" "Processing message (${Message.Length} chars)"

# Track conversation
$result = Invoke-PythonTracking -UserMessage $Message -Intent $Intent

if ($result -and $result.success) {
    Write-Host "`n" + "═" * 50 -ForegroundColor Green
    Write-Host "✅ CONVERSATION TRACKED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "═" * 50 -ForegroundColor Green
    
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  • Continue conversation in Copilot Chat" -ForegroundColor White
    Write-Host "  • Run: .\scripts\cortex-capture.ps1 -Validate" -ForegroundColor White
    Write-Host "  • View: sqlite3 cortex-brain/tier1/conversations.db" -ForegroundColor White
    
    exit 0
} else {
    Write-Host "`n" + "═" * 50 -ForegroundColor Red
    Write-Host "❌ CONVERSATION TRACKING FAILED" -ForegroundColor Red
    Write-Host "═" * 50 -ForegroundColor Red
    
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "  • Check Python environment is activated" -ForegroundColor White
    Write-Host "  • Verify cortex-brain/tier1/conversations.db exists" -ForegroundColor White
    Write-Host "  • Run: python -m pytest CORTEX/tests/tier1/" -ForegroundColor White
    
    exit 1
}
