#!/bin/bash
# CORTEX Auto-Resume Prompt - Cross-Platform Version
# Works on: macOS, Linux, WSL, Git Bash on Windows

<< 'USAGE'
.SYNOPSIS
    CORTEX auto-resume prompt for bash/zsh
    
.DESCRIPTION
    This script checks the WorkStateManager and SessionTokenManager for incomplete work
    and displays a helpful resume prompt when starting a new shell session.
    
.INSTALLATION
    Add to your shell profile:
    
    # For bash (~/.bashrc):
    if [ -f "$HOME/PROJECTS/CORTEX/scripts/auto-resume-prompt.sh" ]; then
        source "$HOME/PROJECTS/CORTEX/scripts/auto-resume-prompt.sh"
    fi
    
    # For zsh (~/.zshrc):
    if [ -f "$HOME/PROJECTS/CORTEX/scripts/auto-resume-prompt.sh" ]; then
        source "$HOME/PROJECTS/CORTEX/scripts/auto-resume-prompt.sh"
    fi
    
.EXAMPLE
    # Manual invocation
    bash auto-resume-prompt.sh
    
.EXAMPLE
    # Silent mode (no output if no incomplete work)
    CORTEX_SILENT=1 bash auto-resume-prompt.sh
    
.EXAMPLE
    # Detailed mode
    CORTEX_DETAILED=1 bash auto-resume-prompt.sh
USAGE

# Configuration
CORTEX_SILENT=${CORTEX_SILENT:-0}
CORTEX_DETAILED=${CORTEX_DETAILED:-0}

# Detect CORTEX root
if [ -n "$CORTEX_ROOT" ]; then
    CORTEX_ROOT="$CORTEX_ROOT"
elif [ -f "$(dirname "$BASH_SOURCE")/../../cortex.config.json" ]; then
    # Try to read from config file
    CORTEX_ROOT=$(cd "$(dirname "$BASH_SOURCE")/.." && pwd)
else
    # Fallback to relative path
    CORTEX_ROOT=$(cd "$(dirname "$BASH_SOURCE")/.." && pwd)
fi

# Detect Python command (python3 on macOS/Linux, python on Windows)
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    [ $CORTEX_SILENT -eq 0 ] && echo "⚠️  CORTEX: Python not found" >&2
    return 1 2>/dev/null || exit 1
fi

# Function to get incomplete work
get_incomplete_work() {
    $PYTHON_CMD -c "
import sys
sys.path.insert(0, '$CORTEX_ROOT')

try:
    from src.tier1.work_state_manager import WorkStateManager
    from src.tier1.session_token import SessionTokenManager
    import json
    
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
    # Silent fail - output empty result
    print('{\"has_incomplete_work\": false, \"work_sessions\": [], \"active_token\": null}')
    sys.exit(0)
" 2>/dev/null
}

# Function to show compact prompt
show_compact_prompt() {
    local work_data="$1"
    
    # Check if there's incomplete work
    local has_work=$(echo "$work_data" | $PYTHON_CMD -c "import sys, json; data=json.load(sys.stdin); print('yes' if data.get('has_incomplete_work') else 'no')" 2>/dev/null)
    
    if [ "$has_work" != "yes" ]; then
        return
    fi
    
    # Get task count and first task
    local task_count=$(echo "$work_data" | $PYTHON_CMD -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('work_sessions', [])))" 2>/dev/null)
    local first_task=$(echo "$work_data" | $PYTHON_CMD -c "import sys, json; data=json.load(sys.stdin); sessions=data.get('work_sessions', []); print(sessions[0]['task'][:50] + '...' if len(sessions[0]['task']) > 50 else sessions[0]['task']) if sessions else ''" 2>/dev/null)
    
    echo ""
    echo "🧠 CORTEX: $task_count incomplete task(s) - Type 'continue' in Copilot Chat"
    echo "   ↳ $first_task"
    echo ""
}

# Function to show detailed prompt
show_detailed_prompt() {
    local work_data="$1"
    
    # Check if there's incomplete work
    local has_work=$(echo "$work_data" | $PYTHON_CMD -c "import sys, json; data=json.load(sys.stdin); print('yes' if data.get('has_incomplete_work') else 'no')" 2>/dev/null)
    
    if [ "$has_work" != "yes" ]; then
        return
    fi
    
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║  🧠 CORTEX: You have incomplete work to resume                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Parse and display each work session
    echo "$work_data" | $PYTHON_CMD -c "
import sys
import json
from datetime import datetime

data = json.load(sys.stdin)

for work in data.get('work_sessions', []):
    status_icon = '⚡' if work['status'] == 'in_progress' else '⏸️'
    
    print(f\"  {status_icon} Task: {work['task']}\")
    print(f\"     Status: {work['status'].upper()}\")
    print(f\"     Duration: {work['duration_minutes']} minutes\")
    
    if work.get('files'):
        files_str = ', '.join(work['files'])
        print(f\"     Files: {files_str}\")
    
    print()

# Show active session token if exists
if data.get('active_token'):
    token_data = data['active_token']
    print(f\"  🔐 Active Session Token: {token_data['token']}\")
    
    if token_data.get('conversation_id'):
        print(f\"     Conversation ID: {token_data['conversation_id']}\")
    
    print()
" 2>/dev/null
    
    echo "  💡 Tip: Open GitHub Copilot Chat and say 'continue' to resume your work"
    echo ""
}

# Main execution (only if not already run in this session)
if [ -z "$CORTEX_AUTO_RESUME_LOADED" ]; then
    export CORTEX_AUTO_RESUME_LOADED=1
    
    if [ -d "$CORTEX_ROOT" ]; then
        work_data=$(get_incomplete_work)
        
        if [ $CORTEX_DETAILED -eq 1 ]; then
            show_detailed_prompt "$work_data"
        elif [ $CORTEX_SILENT -eq 0 ]; then
            show_compact_prompt "$work_data"
        fi
    else
        [ $CORTEX_SILENT -eq 0 ] && echo "⚠️  CORTEX: Root path not found: $CORTEX_ROOT" >&2
    fi
fi
