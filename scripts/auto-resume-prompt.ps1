# CORTEX Auto-Resume Prompt
# Checks for incomplete work on PowerShell startup and prompts user to continue

<#
.SYNOPSIS
    CORTEX auto-resume prompt for PowerShell
    
.DESCRIPTION
    This script checks the WorkStateManager and SessionTokenManager for incomplete work
    and displays a helpful resume prompt when starting a new shell session.
    
.NOTES
    Add to your PowerShell profile ($PROFILE):
    
    # CORTEX Auto-Resume
    $cortexAutoResume = "D:\PROJECTS\CORTEX\scripts\auto-resume-prompt.ps1"
    if (Test-Path $cortexAutoResume) {
        . $cortexAutoResume
    }
    
.EXAMPLE
    # Manual invocation
    .\auto-resume-prompt.ps1
    
.EXAMPLE
    # Silent mode (no output if no incomplete work)
    .\auto-resume-prompt.ps1 -Silent
#>

param(
    [switch]$Silent,
    [switch]$Detailed,
    [string]$CortexRoot = $null
)

# Auto-detect CORTEX root if not provided
if (-not $CortexRoot) {
    # Priority 1: Environment variable
    if ($env:CORTEX_ROOT) {
        $CortexRoot = $env:CORTEX_ROOT
    }
    # Priority 2: Config file (machine-specific)
    elseif (Test-Path "$PSScriptRoot\..\cortex.config.json") {
        try {
            $config = Get-Content "$PSScriptRoot\..\cortex.config.json" -Raw | ConvertFrom-Json
            $hostname = $env:COMPUTERNAME
            
            # Try machine-specific path first
            if ($config.machines.$hostname.rootPath) {
                $CortexRoot = $config.machines.$hostname.rootPath
            }
            # Fall back to default rootPath
            elseif ($config.application.rootPath) {
                $CortexRoot = $config.application.rootPath
            }
        }
        catch {
            # Silently fall through to next option
        }
    }
    
    # Priority 3: Relative path from script location
    if (-not $CortexRoot) {
        $CortexRoot = Split-Path -Parent $PSScriptRoot
    }
}

function Get-IncompleteWork {
    param([string]$CortexRoot)
    
    try {
        # Create temporary Python script
        $tempScript = [System.IO.Path]::GetTempFileName() + ".py"
        
        $pythonCode = @"
import sys
sys.path.insert(0, r'$CortexRoot')
from src.tier1.work_state_manager import WorkStateManager
from src.tier1.session_token import SessionTokenManager
import json

try:
    wsm = WorkStateManager()
    stm = SessionTokenManager()

    # Get incomplete work
    incomplete_sessions = wsm.get_incomplete_sessions(include_stale=False)
    active_session_token = stm.get_active_session()

    # Build result
    result = {
        'has_incomplete_work': len(incomplete_sessions) > 0,
        'work_sessions': [],
        'active_token': None
    }

    for state in incomplete_sessions:
        result['work_sessions'].append({
            'session_id': state.session_id,
            'task': state.task_description,
            'status': state.status.value,
            'files': state.files_touched[:5],  # First 5 files
            'duration_minutes': round(state.duration_minutes(), 1),
            'last_activity': state.last_activity.isoformat()
        })

    if active_session_token:
        result['active_token'] = {
            'token': active_session_token.token,
            'description': active_session_token.description,
            'conversation_id': active_session_token.conversation_id,
            'work_session_id': active_session_token.work_session_id
        }

    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'error': str(e), 'has_incomplete_work': False, 'work_sessions': []}))
"@
        
        Set-Content -Path $tempScript -Value $pythonCode
        
        $output = python $tempScript 2>$null
        Remove-Item $tempScript -ErrorAction SilentlyContinue
        
        if ($output) {
            $data = $output | ConvertFrom-Json
            if ($data.error) {
                if (-not $Silent) {
                    Write-Warning "CORTEX: Python error: $($data.error)"
                }
                return $null
            }
            return $data
        } else {
            if (-not $Silent) {
                Write-Warning "CORTEX: Could not check for incomplete work"
            }
            return $null
        }
    }
    catch {
        if (-not $Silent) {
            Write-Warning "CORTEX: Error checking work state: $_"
        }
        return $null
    }
}

function Show-ResumePrompt {
    param(
        [object]$WorkData,
        [switch]$Detailed
    )
    
    if ($null -eq $WorkData -or -not $WorkData.has_incomplete_work) {
        return
    }
    
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║" -ForegroundColor Cyan -NoNewline
    Write-Host "  🧠 CORTEX: You have incomplete work to resume                   " -ForegroundColor Yellow -NoNewline
    Write-Host "║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($work in $WorkData.work_sessions) {
        $statusIcon = if ($work.status -eq "in_progress") { "⚡" } else { "⏸️" }
        $statusColor = if ($work.status -eq "in_progress") { "Green" } else { "Yellow" }
        
        Write-Host "  $statusIcon Task: " -NoNewline
        Write-Host $work.task -ForegroundColor White
        Write-Host "     Status: " -NoNewline
        Write-Host $work.status.ToUpper() -ForegroundColor $statusColor
        Write-Host "     Duration: " -NoNewline
        Write-Host "$($work.duration_minutes) minutes" -ForegroundColor Gray
        
        if ($work.files.Count -gt 0) {
            Write-Host "     Files: " -NoNewline
            Write-Host ($work.files -join ", ") -ForegroundColor DarkGray
        }
        
        if ($Detailed) {
            Write-Host "     Session ID: " -NoNewline
            Write-Host $work.session_id -ForegroundColor DarkGray
            Write-Host "     Last Activity: " -NoNewline
            Write-Host ([DateTime]::Parse($work.last_activity).ToString("yyyy-MM-dd HH:mm:ss")) -ForegroundColor DarkGray
        }
        
        Write-Host ""
    }
    
    # Show active session token if exists
    if ($null -ne $WorkData.active_token) {
        Write-Host "  🔐 Active Session Token: " -NoNewline
        Write-Host $WorkData.active_token.token -ForegroundColor Magenta
        
        if ($null -ne $WorkData.active_token.conversation_id) {
            Write-Host "     Conversation ID: " -NoNewline
            Write-Host $WorkData.active_token.conversation_id -ForegroundColor DarkGray
        }
        
        Write-Host ""
    }
    
    Write-Host "  💡 Tip: Open GitHub Copilot Chat and say " -NoNewline -ForegroundColor Cyan
    Write-Host "'continue'" -NoNewline -ForegroundColor White -BackgroundColor DarkBlue
    Write-Host " to resume your work" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  📋 Or use: " -NoNewline -ForegroundColor Cyan
    Write-Host "python -c `"from src.tier1.work_state_manager import WorkStateManager; wsm = WorkStateManager(); print(wsm.get_current_state().task_description)`"" -ForegroundColor DarkGray
    Write-Host ""
}

function Show-CompactPrompt {
    param([object]$WorkData)
    
    if ($null -eq $WorkData -or -not $WorkData.has_incomplete_work) {
        return
    }
    
    $taskCount = $WorkData.work_sessions.Count
    $firstTask = $WorkData.work_sessions[0].task
    
    if ($firstTask.Length -gt 50) {
        $firstTask = $firstTask.Substring(0, 47) + "..."
    }
    
    Write-Host ""
    Write-Host "🧠 CORTEX: " -NoNewline -ForegroundColor Yellow
    Write-Host "$taskCount incomplete task(s) - " -NoNewline -ForegroundColor White
    Write-Host "Type 'continue' in Copilot Chat" -ForegroundColor Cyan
    Write-Host "   ↳ " -NoNewline -ForegroundColor DarkGray
    Write-Host $firstTask -ForegroundColor Gray
    Write-Host ""
}

# Main execution
if (Test-Path $CortexRoot) {
    $workData = Get-IncompleteWork -CortexRoot $CortexRoot
    
    if ($Detailed) {
        Show-ResumePrompt -WorkData $workData -Detailed
    } elseif (-not $Silent) {
        Show-CompactPrompt -WorkData $workData
    }
} else {
    if (-not $Silent) {
        Write-Warning "CORTEX: Root path not found: $CortexRoot"
    }
}
