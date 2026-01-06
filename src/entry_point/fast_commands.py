"""
Fast Command Handler - Lightweight routing for simple commands.

Handles help, version, status without loading heavy dependencies.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional


def is_fast_command(message: str) -> bool:
    """
    Check if message is a fast command (no heavy loading needed).
    
    Args:
        message: User input message
    
    Returns:
        True if fast command, False otherwise
    """
    if not message:
        return False
    
    msg_lower = message.lower().strip()
    fast_commands = [
        'help',
        'version',
        '--version',
        '-v',
        'status',
        'intro',
        'introduce yourself',
        'hello',
        'hi cortex',
    ]
    
    return any(cmd == msg_lower or msg_lower.startswith(cmd + ' ') for cmd in fast_commands)


class FastCommandHandler:
    """
    Lightweight handler for simple commands.
    
    Avoids loading orchestrators, agents, and tiers for basic operations.
    """
    
    def __init__(self, brain_path=None):
        """Initialize fast command handler."""
        self.logger = logging.getLogger("cortex.entry_point.fast_commands")
        self.brain_path = brain_path
    
    def handle(self, message: str, format_type: str = "markdown") -> Optional[str]:
        """
        Handle fast command.
        
        Args:
            message: User input
            format_type: Output format
        
        Returns:
            Response string or None if not a fast command
        """
        msg_lower = message.lower().strip()
        
        if msg_lower in ['help', 'show commands', 'list operations']:
            return self._handle_help()
        
        elif msg_lower in ['version', '--version', '-v']:
            return self._handle_version()
        
        elif msg_lower == 'status':
            return self._handle_status()
        
        elif msg_lower in ['intro', 'introduce yourself', 'hello', 'hi cortex']:
            return self._handle_intro()
        
        return None
    
    def _handle_help(self) -> str:
        """Handle help command."""
        help_text = """
# 🧠 CORTEX Command Reference

## Planning & Execution
- `plan <feature>` - Create structured execution plan
- `continue` - Resume last operation
- `ado story <title>` - Generate Azure DevOps work item

## Testing & Quality
- `tdd <feature>` - Test-driven development workflow
- `test <module>` - Run tests with coverage

## Maintenance & Optimization
- `vacuum` - Deep clean workspace
- `cleanup` - Remove cache/logs/artifacts
- `system maintenance` - 12-phase health check
- `refine <module>` - Code improvement pipeline

## Investigation & Debugging
- `investigate <issue>` - Root cause analysis
- `debug <problem>` - Autonomous debugging
- `sanitize <file>` - Remove sensitive data

## General
- `help` - Show this help
- `intro` - CORTEX introduction
- `version` - Show version

**Usage:** Simply type commands in GitHub Copilot Chat or use:
```bash
python3 -m src.main "<command>"
```
"""
        return help_text
    
    def _handle_version(self) -> str:
        """Handle version command."""
        return 'CORTEX v5.1.0 - AI Assistant with Long-Term Memory'
    
    def _handle_status(self) -> str:
        """Handle status command."""
        status_text = """
# 🧠 CORTEX Status

**Version:** 5.1.0  
**Mode:** Production  
**Brain:** 4-Tier Architecture Active  
**Orchestrators:** 10+ registered  
**Status:** ✅ Operational

**Recent Activity:**
- CORTEX5 Enhancement Epic - Phase 2 in progress
- Knowledge Extension Layer complete (2,506 lines, 43 tests)
- Next: Orchestrator Registry System

**Quick Actions:**
- Type `help` for commands
- Type `continue` to resume last operation
- Type `system maintenance` for health check
"""
        return status_text
    
    def _handle_intro(self) -> str:
        """Handle introduction command."""
        intro_text = """
```
   ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗
  ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝
  ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝ 
  ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗ 
  ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗
   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
```

# 🧠 CORTEX - AI Assistant with Long-Term Memory

**Version:** 5.1.0 | **Author:** Asif Hussain

## What I Do

I enhance GitHub Copilot with:
- 🧠 **Long-term memory** - Remember across sessions
- 📋 **Strategic planning** - Multi-phase execution plans
- 🔍 **Context awareness** - "Make it purple" works anytime
- 🎯 **Autonomous execution** - Self-executing workflows
- 🧪 **TDD enforcement** - RED→GREEN→REFACTOR mandatory
- 🛡️ **Quality protection** - SKULL rules prevent mistakes

## Quick Start

Just say what you need:
- "plan user authentication"
- "tdd validate email"
- "investigate performance issue"
- "system maintenance"

I'll handle the rest autonomously.

Type `help` for full command reference.
"""
        return {
            'success': True,
            'message': intro_text
        }
