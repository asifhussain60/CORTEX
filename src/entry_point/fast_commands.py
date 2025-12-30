"""
CORTEX Fast-Path Command Handler

Zero-overhead handler for simple commands that don't require full system initialization.
Bypasses tier loading, agent routing, and heavy dependencies for instant responses.

Supported Commands:
    - help: Show command reference
    - version: Display CORTEX version
    - status: Quick health check
    - info: System information

Performance:
    - Response time: <10ms (vs ~2.6s full init)
    - Memory: ~5MB (vs ~50MB full init)
    - No database connections
    - No agent initialization

Usage:
    from src.entry_point.fast_commands import FastCommandHandler
    
    handler = FastCommandHandler()
    if handler.can_handle("help"):
        response = handler.handle("help")
        print(response)
        # No need for full CortexEntry

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Fast-path commands (no full initialization needed)
FAST_COMMANDS = {
    'help', 'version', 'status', 'info',
    '--help', '-h', '--version', '-v',
    'commands', 'quickhelp'
}


class FastCommandHandler:
    """
    Handles simple commands without full CORTEX initialization.
    
    Provides instant responses for informational commands by:
    - Using template system directly (no agent routing)
    - Skipping tier database connections
    - Avoiding heavy import overhead
    - Reading static configuration files
    
    Example:
        handler = FastCommandHandler()
        
        if handler.can_handle("help"):
            response = handler.handle("help")
            print(response)
            sys.exit(0)
    """
    
    def __init__(self, brain_path: Optional[Path] = None):
        """
        Initialize fast command handler.
        
        Args:
            brain_path: Path to CORTEX brain (for templates and config)
        """
        if brain_path is None:
            # Minimal config loading (no tier initialization)
            from src.config import config
            brain_path = config.brain_path
        
        self.brain_path = Path(brain_path)
        self.template_path = self.brain_path / "response-templates-v4.yaml"
        self._templates = None
        self._version = None
    
    def can_handle(self, user_message: str) -> bool:
        """
        Check if message is a fast-path command.
        
        Args:
            user_message: User input
        
        Returns:
            True if fast-path handling available
        """
        message_lower = user_message.strip().lower()
        
        # Exact match
        if message_lower in FAST_COMMANDS:
            return True
        
        # Starts with fast command
        for cmd in FAST_COMMANDS:
            if message_lower.startswith(cmd):
                return True
        
        return False
    
    def handle(self, user_message: str, format_type: str = "text") -> str:
        """
        Handle fast-path command.
        
        Args:
            user_message: User input
            format_type: Output format (text/json/markdown)
        
        Returns:
            Formatted response
        """
        start_time = time.perf_counter()
        message_lower = user_message.strip().lower()
        
        # Route to specific handler
        if message_lower in ['help', '--help', '-h', 'commands']:
            response = self._handle_help()
        elif message_lower in ['version', '--version', '-v']:
            response = self._handle_version()
        elif message_lower in ['status', 'health']:
            response = self._handle_status()
        elif message_lower in ['info', 'about']:
            response = self._handle_info()
        elif message_lower == 'quickhelp':
            response = self._handle_quickhelp()
        else:
            # Default help for unrecognized fast command
            response = self._handle_help()
        
        # Format response
        if format_type == "json":
            import json
            return json.dumps({
                "response": response,
                "processing_time_ms": (time.perf_counter() - start_time) * 1000,
                "fast_path": True
            }, indent=2)
        elif format_type == "markdown":
            return f"```markdown\n{response}\n```"
        else:
            return response
    
    def _handle_help(self) -> str:
        """Generate help response."""
        # Try template first
        if self._load_templates():
            template = self._templates.get('help', {})
            if 'response' in template:
                return template['response']
        
        # Fallback to built-in help
        return self._builtin_help()
    
    def _handle_version(self) -> str:
        """Generate version response."""
        version = self._get_version()
        return f"""# 🧠 CORTEX Version Information
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

**CORTEX Version:** {version}
**Python Version:** {sys.version.split()[0]}
**Platform:** {sys.platform}

For changelog and release notes, see: CHANGELOG.md
"""
    
    def _handle_status(self) -> str:
        """Generate quick status check."""
        brain_exists = self.brain_path.exists()
        config_exists = (self.brain_path.parent / "cortex.config.json").exists()
        
        status_icon = "✅" if brain_exists and config_exists else "⚠️"
        
        return f"""# 🧠 CORTEX Status Check
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

{status_icon} **Brain Status:** {"Online" if brain_exists else "Not found"}
{status_icon} **Configuration:** {"Found" if config_exists else "Missing"}

**Brain Path:** {self.brain_path}

For detailed health check, use: `cortex diagnose`
"""
    
    def _handle_info(self) -> str:
        """Generate system information."""
        version = self._get_version()
        
        return f"""# 🧠 CORTEX System Information
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## Version
**CORTEX:** {version}
**Python:** {sys.version.split()[0]}

## Paths
**Brain:** {self.brain_path}
**Config:** {self.brain_path.parent / 'cortex.config.json'}

## Capabilities
- 🧠 4-Tier Brain Architecture
- 🤖 10 Specialist Agents
- 🔬 TDD Mastery with Auto-Debug
- 📋 Planning System with Vision API
- 🔄 Git Checkpoint & History
- 📊 Progress Monitoring

For full documentation: `cortex help`
"""
    
    def _handle_quickhelp(self) -> str:
        """Generate quick reference."""
        return """# 🧠 CORTEX Quick Reference
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## Common Commands

**Planning:**
- `plan [feature]` - Create feature plan
- `approve plan` - Approve and execute plan

**TDD:**
- `start tdd` - Begin TDD workflow
- `run tests` - Execute tests
- `suggest refactorings` - Get optimization ideas

**Git:**
- `checkpoint` - Create git checkpoint
- `status` - Show git status

**Feedback:**
- `feedback` - Report bug/feature/improvement

**System:**
- `help` - Full command reference
- `version` - Show version
- `upgrade cortex` - Upgrade CORTEX

For detailed help: `cortex help`
"""
    
    def _builtin_help(self) -> str:
        """Built-in help text (fallback when templates unavailable)."""
        return """# 🧠 CORTEX AI Assistant
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

CORTEX is an AI-powered development assistant with long-term memory,
context awareness, and strategic planning capabilities.

## Core Features

### 📋 Planning System
- `plan [feature]` - Create detailed feature plan
- `plan ado` - Import from Azure DevOps
- `approve plan` - Approve and execute
- `resume plan [name]` - Continue saved plan

### 🔬 TDD Mastery
- `start tdd` - Begin RED→GREEN→REFACTOR workflow
- `run tests` - Execute test suite
- `suggest refactorings` - Get optimization suggestions
- Auto-debug on test failures

### 🔄 Git Operations
- `checkpoint` - Create git checkpoint
- `status` - Show git status
- `diff` - Show changes

### 📊 Feedback System
- `feedback` - Report issue or suggestion
- Structured bug/feature/improvement reports
- Privacy-protected, auto-uploaded to Gist

### 🛠️ System Operations
- `version` - Show CORTEX version
- `status` - Quick health check
- `upgrade cortex` - Upgrade to latest version
- `diagnose` - Full system diagnostics

### ⚙️ Phase 8: Integration & Cleanup
- `integration-cleanup` - Final cleanup before deployment
  - `--dry-run` - Simulate without changes
  - `--operation-profile quick|standard|comprehensive` - Cleanup thoroughness
- `completion-report` - Generate Phase 8 completion report
  - `--output /path/to/report.md` - Custom output path
- `phase8-status` - Show Phase 8 progress

## Usage

**Interactive Mode:**
```bash
python -m src.main
You: create tests for auth.py
```

**Single Command:**
```bash
python -m src.main "plan user authentication"
```

**With Options:**
```bash
python -m src.main "status" --format json --verbose
```

## Getting Started

1. **Setup:** `python -m src.main --setup`
2. **Tutorial:** `tutorial` (15-30 min interactive learning)
3. **First Plan:** `plan [your feature]`

## Documentation

- **Full Guide:** `.github/prompts/CORTEX.prompt.md`
- **TDD Guide:** `.github/prompts/modules/tdd-mastery-guide.md`
- **Planning Guide:** `.github/prompts/modules/planning-system-guide.md`

## Support

- **GitHub:** github.com/asifhussain60/CORTEX
- **Issues:** Use `feedback` command
- **Questions:** Ask me in natural language!

---

**Note:** All commands support natural language. You can say:
- "Show me the status" instead of `status`
- "I want to create a plan for authentication" instead of `plan auth`
- "Can you help me with tests?" instead of `start tdd`

Type your request naturally, and I'll understand! 🚀
"""
    
    def _load_templates(self) -> bool:
        """
        Load response templates (lazy).
        
        Returns:
            True if templates loaded successfully
        """
        if self._templates is not None:
            return True
        
        if not self.template_path.exists():
            return False
        
        try:
            import yaml
            with open(self.template_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self._templates = data.get('templates', {})
            return True
        except Exception as e:
            logger.warning(f"Failed to load templates: {e}")
            return False
    
    def _get_version(self) -> str:
        """
        Get CORTEX version (lazy).
        
        Returns:
            Version string
        """
        if self._version is not None:
            return self._version
        
        version_file = self.brain_path.parent / "VERSION"
        if version_file.exists():
            try:
                self._version = version_file.read_text().strip().split('\n')[0]
                return self._version
            except Exception:
                pass
        
        self._version = "3.2.0"  # Default
        return self._version


def is_fast_command(user_message: str) -> bool:
    """
    Quick check if message is a fast-path command.
    
    Args:
        user_message: User input
    
    Returns:
        True if fast-path available
    
    Example:
        if is_fast_command("help"):
            # Use FastCommandHandler
        else:
            # Use full CortexEntry
    """
    message_lower = user_message.strip().lower()
    return any(
        message_lower.startswith(cmd) or message_lower == cmd
        for cmd in FAST_COMMANDS
    )
