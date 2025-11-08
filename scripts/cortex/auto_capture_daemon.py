"""
CORTEX 2.0 - Ambient Context Capture Daemon

Purpose: Automatically capture workspace context without user intervention.
Target: Achieve 60% → 85% "continue" command success rate.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

Components:
- File System Watcher: Monitor workspace file changes
- VS Code Monitor: Capture open files and editor state
- Terminal Monitor: Track meaningful commands
- Git Monitor: Capture git operations
- Debouncer: Batch events to prevent excessive captures
"""

import os
import sys
import time
import json
import signal
import threading
import subprocess
import logging
import re
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, List, Callable, Optional, Set

# Add src to path for imports
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

try:
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler
except ImportError:
    print("[CORTEX] ERROR: watchdog library not installed")
    print("[CORTEX] Install with: pip install watchdog")
    sys.exit(1)


# ============================================================================
# Configuration
# ============================================================================

IGNORE_PATTERNS = [
    "**/__pycache__/**",
    "**/.venv/**",
    "**/.git/**",
    "**/node_modules/**",
    "**/*.pyc",
    "**/.DS_Store",
    "**/bin/**",
    "**/obj/**"
]

WATCH_PATTERNS = [
    "**/*.py",
    "**/*.md",
    "**/*.json",
    "**/*.yaml",
    "**/*.yml",
    "**/*.tsx",
    "**/*.ts",
    "**/*.cs",
    "**/*.sql",
    "**/*.sh",
    "**/*.ps1"
]

MEANINGFUL_COMMANDS = [
    "pytest", "npm test", "dotnet test",
    "npm run build", "dotnet build",
    "git commit", "git push", "git pull", "git merge",
    "python", "node", "dotnet run"
]

# Security limits
MAX_FILE_SIZE = 1024 * 1024  # 1MB limit for JSON files
MAX_COMMAND_LENGTH = 1000  # Limit command length
MAX_HISTORY_SIZE = 10 * 1024 * 1024  # 10MB limit for history files

# Dangerous command patterns to block
DANGEROUS_PATTERNS = [
    'rm -rf /',
    'rm -rf *',
    'sudo rm',
    'dd if=',
    'mkfs.',
    '>()',  # Fork bomb
    ':|:',  # Fork bomb pattern
    'wget | sh',
    'wget | bash',
    'curl | sh',
    'curl | bash',
    'eval',
    '__import__',
    'os.system',
    'subprocess.call'
]


# ============================================================================
# Secure Logging Setup
# ============================================================================

def setup_secure_logging():
    """Set up secure logging that doesn't expose sensitive info."""
    log_dir = CORTEX_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "ambient_capture.log"
    
    # Rotating file handler (10MB max, 5 backups)
    handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,
        backupCount=5
    )
    
    # Format without exposing sensitive paths
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger('cortex.ambient')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger

# Initialize secure logger
logger = setup_secure_logging()


# ============================================================================
# Debouncer - Batch events to prevent excessive captures
# ============================================================================

class Debouncer:
    """Debounces context capture events to prevent excessive writes."""
    
    def __init__(self, delay_seconds: int = 5):
        self.delay = delay_seconds
        self.buffer = []
        self.lock = threading.Lock()
        self.timer = None
        
    def add_event(self, context: Dict[str, Any]):
        """Add event to buffer."""
        with self.lock:
            self.buffer.append(context)
            
            # Reset timer
            if self.timer:
                self.timer.cancel()
                
            self.timer = threading.Timer(self.delay, self._flush)
            self.timer.start()
            
    def _flush(self):
        """Flush buffered events to Tier 1."""
        with self.lock:
            if not self.buffer:
                return
                
            # Merge similar events
            merged = self._merge_events(self.buffer)
            
            # Write to Tier 1
            self._write_to_tier1(merged)
            
            # Clear buffer
            self.buffer.clear()
            
    def _merge_events(self, events: List[Dict]) -> List[Dict]:
        """Merge similar events to reduce duplicates."""
        merged = {}
        
        for event in events:
            key = f"{event['type']}:{event.get('file', '')}"
            
            if key not in merged:
                merged[key] = event
            else:
                # Update timestamp to latest
                merged[key]["timestamp"] = event["timestamp"]
                
        return list(merged.values())
        
    def _write_to_tier1(self, events: List[Dict]):
        """Write events to Tier 1."""
        try:
            from src.tier1.working_memory import WorkingMemory
            
            brain_path = os.environ.get("CORTEX_BRAIN_PATH", str(CORTEX_ROOT / "cortex-brain"))
            db_path = Path(brain_path) / "tier1" / "conversations.db"
            
            if not db_path.exists():
                print(f"[CORTEX] WARNING: Tier 1 database not found: {db_path}")
                return
            
            wm = WorkingMemory(str(db_path))
            
            # Get or create ambient session
            session_id = self._get_ambient_session(wm)
            
            # Store events as context
            for event in events:
                wm.store_message(
                    conversation_id=session_id,
                    message={
                        "role": "system",
                        "content": f"[Ambient Capture] {event['type']}: {json.dumps(event)}",
                        "timestamp": event["timestamp"]
                    }
                )
                
            print(f"[CORTEX] Captured {len(events)} context events to Tier 1")
            
        except Exception as e:
            print(f"[CORTEX] ERROR writing to Tier 1: {e}")
            
    def _get_ambient_session(self, wm) -> str:
        """Get or create ambient capture session."""
        # Check for today's ambient session
        from datetime import date
        today = date.today().isoformat()
        
        # Create new ambient session for today
        session_id = wm.start_conversation(
            user_id="ambient_daemon",
            metadata={
                "type": "ambient",
                "date": today,
                "description": "Automatic background context capture"
            }
        )
        
        return session_id


# ============================================================================
# File System Watcher - Monitor workspace file changes
# ============================================================================

class FileSystemWatcher:
    """Monitors workspace file changes in real-time with security hardening."""
    
    # Whitelist of allowed extensions
    ALLOWED_EXTENSIONS = {'.py', '.md', '.json', '.yaml', '.yml', '.tsx', '.ts', '.cs', '.sql', '.sh', '.ps1'}
    
    def __init__(self, workspace_path: str, callback: Callable):
        # SECURITY: Resolve to absolute path and validate
        self.workspace_path = Path(workspace_path).resolve(strict=True)
        
        # SECURITY: Validate workspace is a directory
        if not self.workspace_path.is_dir():
            raise ValueError("Workspace path must be a directory")
            
        self.callback = callback
        self.observer = Observer()
        
    def start(self):
        """Start monitoring file system."""
        handler = PatternMatchingEventHandler(
            patterns=WATCH_PATTERNS,
            ignore_patterns=IGNORE_PATTERNS,
            ignore_directories=True,
            case_sensitive=False
        )
        
        handler.on_modified = self._on_file_changed
        handler.on_created = self._on_file_changed
        handler.on_deleted = self._on_file_changed
        
        self.observer.schedule(handler, str(self.workspace_path), recursive=True)
        self.observer.start()
        
        print(f"[CORTEX] File system watcher started: {self.workspace_path}")
        
    def _on_file_changed(self, event):
        """Handle file change event with security validation."""
        if event.is_directory:
            return
            
        try:
            # SECURITY: Get absolute path and resolve symlinks
            file_path = Path(event.src_path).resolve(strict=False)
            
            # SECURITY: Ensure file is within workspace (prevent path traversal)
            if not self._is_safe_path(file_path):
                logger.warning(f"SECURITY: Blocked access to file outside workspace: {file_path}")
                return
            
            # Get relative path safely
            relative_path = file_path.relative_to(self.workspace_path)
            
            # SECURITY: Validate file extension is in whitelist
            if not self._is_allowed_extension(file_path):
                return
                
            # Create sanitized context
            context = {
                "type": "file_change",
                "file": str(relative_path),
                "event": event.event_type,
                "timestamp": datetime.now().isoformat()
            }
            
            self.callback(context)
            
        except Exception as e:
            # Don't expose detailed errors to console
            logger.error(f"Error processing file event: {type(e).__name__}")
            print(f"[CORTEX] Error processing file event (see logs)")
            
    def _is_safe_path(self, file_path: Path) -> bool:
        """Check if path is within workspace (prevent path traversal)."""
        try:
            # Resolve both paths
            file_resolved = file_path.resolve()
            workspace_resolved = self.workspace_path.resolve()
            
            # Check if file is under workspace
            return workspace_resolved in file_resolved.parents or file_resolved == workspace_resolved
            
        except (ValueError, RuntimeError):
            return False
            
    def _is_allowed_extension(self, file_path: Path) -> bool:
        """Check if file extension is in whitelist."""
        ext = file_path.suffix.lower()
        return ext in self.ALLOWED_EXTENSIONS


# ============================================================================
# VS Code Monitor - Capture editor state
# ============================================================================

class VSCodeMonitor:
    """Monitors VS Code editor state with security hardening."""
    
    def __init__(self, workspace_path: str):
        # SECURITY: Resolve to absolute path
        self.workspace_path = Path(workspace_path).resolve(strict=True)
        self.vscode_path = self.workspace_path / ".vscode"
        
    def get_open_files(self) -> List[str]:
        """Get list of currently open files with security validation."""
        workspace_file = self.vscode_path / "workspace.json"
        
        if not workspace_file.exists():
            return []
            
        try:
            # SECURITY: Check file size before reading
            if workspace_file.stat().st_size > MAX_FILE_SIZE:
                logger.warning("SECURITY: Workspace file too large, skipping")
                return []
            
            # Read JSON safely
            with open(workspace_file, 'r', encoding='utf-8') as f:
                workspace_data = json.load(f)
            
            # Extract files safely (limit to 100)
            open_files = []
            for folder in workspace_data.get("folders", [])[:100]:
                if "path" in folder and isinstance(folder["path"], str):
                    sanitized = self._sanitize_path(folder["path"])
                    if sanitized:
                        open_files.append(sanitized)
                        
            return open_files[:100]
            
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Error reading workspace JSON: {type(e).__name__}")
            return []
            
    def _sanitize_path(self, path_str: str) -> Optional[str]:
        """Sanitize and validate file path."""
        try:
            # Convert to Path and resolve
            path = Path(path_str).resolve()
            
            # SECURITY: Ensure within workspace
            if self.workspace_path not in path.parents and path != self.workspace_path:
                return None
                
            return str(path.relative_to(self.workspace_path))
            
        except (ValueError, RuntimeError):
            return None
        
    def get_active_file(self) -> Optional[str]:
        """Get currently active file in editor."""
        # Note: This is a simplified implementation
        # Full implementation would require VS Code extension
        return None


# ============================================================================
# Terminal Monitor - Track meaningful commands
# ============================================================================

class TerminalMonitor:
    """Monitors terminal command execution with security hardening."""
    
    def __init__(self, callback: Callable):
        self.callback = callback
        self.monitoring = False
        self._validated_history_path = None
        
    def start(self):
        """Start monitoring terminal with security validation."""
        # SECURITY: Validate history file path on startup
        if not self._validate_history_path():
            logger.warning("SECURITY: Could not validate terminal history path")
            print("[CORTEX] Terminal monitor: history path not accessible")
            return
            
        self.monitoring = True
        thread = threading.Thread(target=self._monitor_history_safe, daemon=True)
        thread.start()
        print("[CORTEX] Terminal monitor started")
        
    def _validate_history_path(self) -> bool:
        """Validate terminal history file path."""
        try:
            # Get history path (platform-specific)
            if sys.platform == "win32":
                history_file = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "PowerShell" / "PSReadLine" / "ConsoleHost_history.txt"
            else:
                history_file = Path.home() / ".bash_history"
                
            # SECURITY: Resolve and validate path
            history_file = history_file.resolve(strict=True)
            
            # SECURITY: Ensure it's a file and readable
            if not history_file.is_file():
                return False
                
            # SECURITY: Check file size
            if history_file.stat().st_size > MAX_HISTORY_SIZE:
                logger.warning("SECURITY: History file too large")
                return False
                
            self._validated_history_path = history_file
            return True
            
        except (FileNotFoundError, PermissionError, RuntimeError):
            return False
        
    def _monitor_history_safe(self):
        """Monitor history file with security checks."""
        try:
            with open(self._validated_history_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(0, os.SEEK_END)
                
                while self.monitoring:
                    line = f.readline()
                    if line:
                        self._process_command_safe(line.strip())
                    else:
                        time.sleep(1)
                        
        except Exception as e:
            logger.error(f"Terminal monitoring stopped: {type(e).__name__}")
            print(f"[CORTEX] Terminal monitoring stopped (see logs)")
            
    def _process_command_safe(self, command: str):
        """Process terminal command with security validation."""
        # SECURITY: Validate command length
        if len(command) > MAX_COMMAND_LENGTH:
            return
            
        # SECURITY: Check for malicious patterns
        if self._is_malicious_command(command):
            logger.warning(f"SECURITY: Blocked malicious command pattern")
            return
            
        # Check if meaningful
        is_meaningful = any(
            cmd in command.lower()
            for cmd in MEANINGFUL_COMMANDS
        )
        
        if not is_meaningful:
            return
            
        # SECURITY: Sanitize command before logging
        sanitized_command = self._sanitize_command(command)
        command_type = self._identify_command_type(sanitized_command)
        
        context = {
            "type": "terminal_command",
            "command": sanitized_command,
            "command_type": command_type,
            "timestamp": datetime.now().isoformat()
        }
        
        self.callback(context)
        
    def _is_malicious_command(self, command: str) -> bool:
        """Check for obviously malicious commands."""
        command_lower = command.lower()
        return any(pattern in command_lower for pattern in DANGEROUS_PATTERNS)
        
    def _sanitize_command(self, command: str) -> str:
        """Sanitize command for logging."""
        # Redact passwords after -p, --password flags
        command = re.sub(r'(-p|--password)[\s=]+\S+', r'\1 [REDACTED]', command, flags=re.IGNORECASE)
        command = re.sub(r'(password|passwd|pwd)[\s=]+\S+', r'\1=[REDACTED]', command, flags=re.IGNORECASE)
        
        # Redact GitHub tokens (ghp_, ghs_)
        command = re.sub(r'gh[ps]_[a-zA-Z0-9]{36,}', '[REDACTED]', command)
        
        # Redact tokens and API keys
        command = re.sub(r'(token|api_key|secret)[\s=:]+\S+', r'\1=[REDACTED]', command, flags=re.IGNORECASE)
        
        # Redact credentials in URLs
        command = re.sub(r'(https?://)[^:]+:[^@]+@', r'\1[REDACTED]:[REDACTED]@', command)
        
        return command
        
    def _identify_command_type(self, command: str) -> str:
        """Identify command type."""
        command_lower = command.lower()
        
        if "pytest" in command_lower or "test" in command_lower:
            return "test_execution"
        elif "build" in command_lower:
            return "build"
        elif "git commit" in command_lower:
            return "git_commit"
        elif "git push" in command_lower:
            return "git_push"
        elif "git pull" in command_lower:
            return "git_pull"
        elif "python" in command_lower or "node" in command_lower:
            return "code_execution"
        else:
            return "other"


# ============================================================================
# Git Monitor - Capture git operations
# ============================================================================

class GitMonitor:
    """Monitors git operations with security hardening."""
    
    # Whitelist of allowed hook types
    ALLOWED_HOOKS: Set[str] = {"post-commit", "post-merge", "post-checkout"}
    
    def __init__(self, repo_path: str, callback: Callable):
        # SECURITY: Validate repo_path is absolute and exists
        self.repo_path = Path(repo_path).resolve(strict=True)
        
        # SECURITY: Validate it's a git repository
        self.git_dir = self.repo_path / ".git"
        if not self.git_dir.is_dir():
            logger.info("Not a git repository, git monitoring disabled")
            self.git_dir = None
            
        self.callback = callback
        
    def install_hooks(self):
        """Install git hooks with security validation."""
        if self.git_dir is None:
            print("[CORTEX] Not a git repository, skipping git hooks")
            return
            
        hooks_dir = self.git_dir / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        
        for hook_type in self.ALLOWED_HOOKS:
            self._install_hook_securely(hook_type)
            
        print("[CORTEX] Git hooks installed securely")
        
    def _install_hook_securely(self, hook_type: str):
        """Install specific git hook with security checks."""
        # SECURITY: Validate hook type
        if hook_type not in self.ALLOWED_HOOKS:
            logger.error(f"SECURITY: Invalid hook type rejected: {hook_type}")
            return
            
        hook_file = self.git_dir / "hooks" / hook_type
        
        # SECURITY: Backup existing hook if present
        if hook_file.exists():
            backup = hook_file.with_suffix('.cortex-backup')
            try:
                hook_file.rename(backup)
                print(f"[CORTEX] Backed up existing {hook_type} hook")
            except OSError as e:
                logger.error(f"Failed to backup hook: {type(e).__name__}")
                return
        
        # SECURITY: Use absolute paths (prevent path injection)
        capture_script = (self.repo_path / "scripts" / "cortex" / "capture_git_event.py").resolve()
        
        # Validate capture script exists
        if not capture_script.exists():
            logger.error("Capture script not found, skipping hook install")
            return
        
        # SECURITY: Create hook script with no shell injection possible
        # Using sh instead of bash for better compatibility
        script = f'''#!/bin/sh
# CORTEX Ambient Capture Git Hook
# Generated by CORTEX 2.0 - DO NOT EDIT

PYTHON=python3
CAPTURE_SCRIPT="{capture_script}"
HOOK_TYPE="{hook_type}"

"$PYTHON" "$CAPTURE_SCRIPT" "$HOOK_TYPE"
'''
        
        try:
            hook_file.write_text(script, encoding='utf-8')
            
            # SECURITY: Set safe permissions (owner read/write/execute only)
            if sys.platform != "win32":
                hook_file.chmod(0o700)  # rwx------
                
        except OSError as e:
            logger.error(f"Failed to install hook: {type(e).__name__}")


# ============================================================================
# Main Daemon
# ============================================================================

class AmbientCaptureDaemon:
    """Main ambient capture daemon."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.running = False
        
        # Initialize components
        self.debouncer = Debouncer(delay_seconds=5)
        self.file_watcher = FileSystemWatcher(workspace_path, self.debouncer.add_event)
        self.vscode_monitor = VSCodeMonitor(workspace_path)
        self.terminal_monitor = TerminalMonitor(self.debouncer.add_event)
        self.git_monitor = GitMonitor(workspace_path, self.debouncer.add_event)
        
    def start(self):
        """Start ambient capture daemon."""
        print("=" * 60)
        print("[CORTEX] Starting Ambient Capture Daemon...")
        print("=" * 60)
        
        # Install git hooks
        self.git_monitor.install_hooks()
        
        # Start monitoring components
        self.file_watcher.start()
        self.terminal_monitor.start()
        
        self.running = True
        
        # Periodic VS Code state capture
        threading.Thread(target=self._periodic_vscode_capture, daemon=True).start()
        
        print("[CORTEX] Ambient Capture Daemon started successfully")
        print("[CORTEX] Monitoring workspace:", self.workspace_path)
        print("[CORTEX] Press Ctrl+C to stop")
        print("=" * 60)
        
        # Keep alive
        self._keep_alive()
        
    def _periodic_vscode_capture(self):
        """Periodically capture VS Code state."""
        while self.running:
            try:
                open_files = self.vscode_monitor.get_open_files()
                active_file = self.vscode_monitor.get_active_file()
                
                if open_files or active_file:
                    context = {
                        "type": "vscode_state",
                        "open_files": open_files,
                        "active_file": active_file,
                        "timestamp": datetime.now().isoformat()
                    }
                    self.debouncer.add_event(context)
                    
            except Exception as e:
                print(f"[CORTEX] Error capturing VS Code state: {e}")
                
            time.sleep(60)  # Every minute
            
    def _keep_alive(self):
        """Keep daemon running."""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self._handle_shutdown(None, None)
            
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown gracefully."""
        print("\n" + "=" * 60)
        print("[CORTEX] Shutting down Ambient Capture Daemon...")
        print("=" * 60)
        
        self.running = False
        
        # Stop file watcher
        if hasattr(self, 'file_watcher'):
            self.file_watcher.observer.stop()
            self.file_watcher.observer.join(timeout=2)
            
        # Stop terminal monitor
        if hasattr(self, 'terminal_monitor'):
            self.terminal_monitor.monitoring = False
            
        print("[CORTEX] Daemon stopped")
        sys.exit(0)


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Main entry point."""
    print("\n[CORTEX] Ambient Context Capture Daemon v1.0")
    print("[CORTEX] Author: Asif Hussain")
    print("[CORTEX] Copyright © 2024-2025 Asif Hussain. All rights reserved.\n")
    
    # Get workspace path
    workspace_path = os.environ.get("CORTEX_ROOT")
    
    if not workspace_path:
        workspace_path = os.getcwd()
        print(f"[CORTEX] CORTEX_ROOT not set, using current directory: {workspace_path}")
    
    # Validate workspace
    workspace = Path(workspace_path)
    if not workspace.exists():
        print(f"[CORTEX] ERROR: Workspace not found: {workspace_path}")
        sys.exit(1)
        
    # Start daemon
    daemon = AmbientCaptureDaemon(workspace_path)
    daemon.start()


if __name__ == "__main__":
    main()
