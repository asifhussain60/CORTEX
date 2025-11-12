# CORTEX 2.0 - Phase 2.1: Ambient Context Daemon Design

**Version:** 1.0  
**Created:** 2025-11-08  
**Status:** DESIGN PHASE  
**Priority:** HIGH (Critical for 85% "continue" success rate)

---

## 🎯 Objective

**Goal:** Implement ambient background capture to achieve 60% → 85% "continue" command success rate through automatic conversation tracking with zero user intervention.

**Current Problem:**
- Phase 0 achieved 60% success with manual capture helpers
- Users still need to remember to capture conversations
- Context is lost when switching between terminals/editors
- Git operations happen without context capture

**Solution:**
Ambient Context Daemon - a background service that monitors workspace activity and automatically captures context to Tier 1.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Ambient Context Daemon                      │
│                 (auto_capture_daemon.py)                     │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  File System │    │   Terminal   │    │  Git Hooks   │
│   Watcher    │    │   Monitor    │    │  Integration │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │   Debouncer    │
                    │  (5 seconds)   │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │ Context Store  │
                    │   (Tier 1)     │
                    └────────────────┘
```

---

## 📦 Component Design

### 1. File System Watcher

**Purpose:** Monitor workspace file changes in real-time

**Technology:** `watchdog` library (cross-platform)

**Monitored Events:**
- File modifications (`.py`, `.md`, `.json`, `.yaml`, `.tsx`, `.ts`, `.cs`)
- File creation/deletion
- Directory changes

**Filtering Rules:**
```python
IGNORE_PATTERNS = [
    "**/__pycache__/**",
    "**/.venv/**",
    "**/.git/**",
    "**/node_modules/**",
    "**/*.pyc",
    "**/.DS_Store"
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
    "**/*.sql"
]
```

**Implementation:**
```python
class FileSystemWatcher:
    """Monitors workspace file changes."""
    
    def __init__(self, workspace_path: str, callback: Callable):
        self.workspace_path = Path(workspace_path)
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
        
        self.observer.schedule(handler, str(self.workspace_path), recursive=True)
        self.observer.start()
        
    def _on_file_changed(self, event):
        """Handle file change event."""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        relative_path = file_path.relative_to(self.workspace_path)
        
        context = {
            "type": "file_change",
            "file": str(relative_path),
            "event": event.event_type,
            "timestamp": datetime.now().isoformat()
        }
        
        self.callback(context)
```

---

### 2. VS Code Integration

**Purpose:** Capture currently open files and editor state

**Data Sources:**
1. `.vscode/workspace.json` - Workspace state
2. Active window title (via OS-level detection)
3. Recently opened files list

**Implementation:**
```python
class VSCodeMonitor:
    """Monitors VS Code editor state."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.vscode_path = self.workspace_path / ".vscode"
        
    def get_open_files(self) -> List[str]:
        """Get list of currently open files in VS Code."""
        # Check workspace state
        workspace_file = self.vscode_path / "workspace.json"
        if not workspace_file.exists():
            return []
            
        with open(workspace_file, 'r') as f:
            workspace_data = json.load(f)
            
        # Extract open editors
        open_files = []
        if "folders" in workspace_data:
            # Extract from editor groups
            for folder in workspace_data.get("folders", []):
                if "editors" in folder:
                    open_files.extend([
                        editor["resource"]
                        for editor in folder["editors"]
                        if "resource" in editor
                    ])
                    
        return open_files
        
    def get_active_file(self) -> Optional[str]:
        """Get currently active file in editor."""
        # Read from VS Code's recent files
        recent_files = self.vscode_path / "recent.json"
        if not recent_files.exists():
            return None
            
        with open(recent_files, 'r') as f:
            recent_data = json.load(f)
            
        # Return most recent file
        if recent_data.get("files"):
            return recent_data["files"][0]
            
        return None
```

---

### 3. Terminal Monitor

**Purpose:** Capture meaningful terminal commands and their outputs

**Monitored Commands:**
- Test execution: `pytest`, `npm test`, `dotnet test`
- Build commands: `npm run build`, `dotnet build`, `python setup.py`
- Git operations: `git commit`, `git push`, `git pull`
- Code execution: `python script.py`, `node app.js`

**Implementation:**
```python
class TerminalMonitor:
    """Monitors terminal command execution."""
    
    MEANINGFUL_COMMANDS = [
        "pytest", "npm test", "dotnet test",
        "npm run build", "dotnet build",
        "git commit", "git push", "git pull", "git merge",
        "python", "node", "dotnet run"
    ]
    
    def __init__(self, callback: Callable):
        self.callback = callback
        self.last_command = None
        self.monitoring = False
        
    def start(self):
        """Start monitoring terminal."""
        self.monitoring = True
        # Monitor PowerShell history
        self._monitor_powershell_history()
        
    def _monitor_powershell_history(self):
        """Monitor PowerShell command history."""
        history_file = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "PowerShell" / "PSReadLine" / "ConsoleHost_history.txt"
        
        if not history_file.exists():
            return
            
        # Monitor file for new commands
        with open(history_file, 'r', encoding='utf-8') as f:
            f.seek(0, os.SEEK_END)  # Go to end of file
            
            while self.monitoring:
                line = f.readline()
                if line:
                    self._process_command(line.strip())
                else:
                    time.sleep(1)  # Wait for new commands
                    
    def _process_command(self, command: str):
        """Process terminal command."""
        # Check if meaningful
        is_meaningful = any(
            cmd in command.lower()
            for cmd in self.MEANINGFUL_COMMANDS
        )
        
        if not is_meaningful:
            return
            
        # Extract command type
        command_type = self._identify_command_type(command)
        
        context = {
            "type": "terminal_command",
            "command": command,
            "command_type": command_type,
            "timestamp": datetime.now().isoformat()
        }
        
        self.callback(context)
        
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
```

---

### 4. Git Hooks Integration

**Purpose:** Automatically capture git operations with context

**Hook Points:**
1. `post-commit` - After successful commit
2. `post-merge` - After successful merge
3. `post-checkout` - After branch switch

**Implementation:**
```python
class GitMonitor:
    """Monitors git operations."""
    
    def __init__(self, repo_path: str, callback: Callable):
        self.repo_path = Path(repo_path)
        self.git_dir = self.repo_path / ".git"
        self.callback = callback
        
    def install_hooks(self):
        """Install git hooks for automatic capture."""
        hooks_dir = self.git_dir / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        
        # Post-commit hook
        post_commit = hooks_dir / "post-commit"
        post_commit.write_text(self._get_hook_script("post-commit"))
        post_commit.chmod(0o755)
        
        # Post-merge hook
        post_merge = hooks_dir / "post-merge"
        post_merge.write_text(self._get_hook_script("post-merge"))
        post_merge.chmod(0o755)
        
        # Post-checkout hook
        post_checkout = hooks_dir / "post-checkout"
        post_checkout.write_text(self._get_hook_script("post-checkout"))
        post_checkout.chmod(0o755)
        
    def _get_hook_script(self, hook_type: str) -> str:
        """Generate git hook script."""
        return f'''#!/bin/bash
# CORTEX Ambient Capture Git Hook
python "{self.repo_path}/scripts/cortex/capture_git_event.py" {hook_type}
'''
        
    def capture_commit(self, commit_hash: str):
        """Capture commit context."""
        # Get commit details
        result = subprocess.run(
            ["git", "show", "--stat", commit_hash],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            context = {
                "type": "git_commit",
                "commit_hash": commit_hash,
                "commit_details": result.stdout,
                "timestamp": datetime.now().isoformat()
            }
            
            self.callback(context)
```

---

### 5. Debouncer

**Purpose:** Prevent excessive context captures by batching events

**Strategy:**
- Buffer events for 5 seconds
- Merge similar events (same file modified multiple times)
- Batch write to Tier 1 once per debounce window

**Implementation:**
```python
class Debouncer:
    """Debounces context capture events."""
    
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
        """Merge similar events."""
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
        from src.tier1.working_memory import WorkingMemory
        
        wm = WorkingMemory(os.environ["CORTEX_BRAIN_PATH"] + "/tier1/conversations.db")
        
        # Get or create ambient session
        session_id = self._get_ambient_session()
        
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
```

---

### 6. Context Store Integration

**Purpose:** Store captured context in Tier 1 for retrieval

**Storage Strategy:**
1. Create "ambient" conversation type
2. Store events as system messages
3. Tag with event types for filtering
4. Enable retrieval by time range or type

**Schema Addition:**
```sql
-- Add to conversations table
ALTER TABLE conversations ADD COLUMN conversation_type TEXT DEFAULT 'user';
-- Types: 'user' (normal), 'ambient' (background capture), 'external' (Copilot)

-- Add to messages table
ALTER TABLE messages ADD COLUMN event_type TEXT;
-- Types: 'file_change', 'terminal_command', 'git_commit', etc.
```

---

## 🚀 Main Daemon Implementation

```python
# scripts/cortex/auto_capture_daemon.py
import os
import sys
import time
import signal
import threading
from pathlib import Path
from typing import Dict, Any

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
        print("[CORTEX] Starting Ambient Capture Daemon...")
        
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
        
        while self.running:
            time.sleep(1)
            
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown gracefully."""
        print("\n[CORTEX] Shutting down Ambient Capture Daemon...")
        self.running = False
        self.file_watcher.observer.stop()
        self.terminal_monitor.monitoring = False
        print("[CORTEX] Daemon stopped")
        sys.exit(0)

def main():
    """Main entry point."""
    workspace_path = os.environ.get("CORTEX_ROOT", os.getcwd())
    
    daemon = AmbientCaptureDaemon(workspace_path)
    daemon.start()

if __name__ == "__main__":
    main()
```

---

## 🔌 VS Code Integration

**Auto-start on workspace open:**

`.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start CORTEX Ambient Capture",
      "type": "shell",
      "command": "python",
      "args": [
        "${workspaceFolder}/scripts/cortex/auto_capture_daemon.py"
      ],
      "isBackground": true,
      "problemMatcher": [],
      "presentation": {
        "reveal": "never",
        "panel": "dedicated"
      },
      "runOptions": {
        "runOn": "folderOpen"
      }
    }
  ]
}
```

---

## ✅ Success Criteria

1. **Zero Manual Capture Required:** 80% of sessions need no manual intervention
2. **Context Loss:** <20% (down from 40% with Phase 0)
3. **Capture Latency:** <100ms per event
4. **False Positives:** <5% irrelevant captures
5. **"Continue" Success Rate:** 60% → 85%

---

## 🧪 Testing Strategy

### Unit Tests (20 tests)
1. File system watcher pattern matching (5 tests)
2. VS Code state extraction (3 tests)
3. Terminal command parsing (4 tests)
4. Git hook installation and execution (3 tests)
5. Debouncer event merging (5 tests)

### Integration Tests (10 tests)
1. End-to-end file change capture (2 tests)
2. Terminal command capture workflow (2 tests)
3. Git commit capture workflow (2 tests)
4. VS Code state capture workflow (2 tests)
5. Debouncing under high load (2 tests)

---

## 📊 Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Event Processing** | <100ms | Real-time capture |
| **Debounce Window** | 5 seconds | Balance frequency vs efficiency |
| **Memory Usage** | <50MB | Lightweight daemon |
| **CPU Usage** | <5% | Background process |
| **Storage Growth** | <1MB/day | Efficient capture |

---

## 🚀 Implementation Timeline

**Week 7 (Days 1-3):**
- Day 1: File system watcher + debouncer
- Day 2: VS Code integration + terminal monitor
- Day 3: Git hooks + integration

**Week 8 (Days 1-2):**
- Day 1: Write 20 unit tests
- Day 2: Write 10 integration tests + validation

**Total Estimated Time:** 40 hours (5 days)

---

## 📝 Next Steps

1. ✅ Design complete (this document)
2. Create ambient capture daemon file structure
3. Implement file system watcher
4. Implement VS Code integration
5. Implement terminal monitor
6. Implement git hooks
7. Write comprehensive tests
8. Validate against success criteria

---

**Status:** DESIGN COMPLETE - Ready for implementation  
**Next Action:** Create `scripts/cortex/auto_capture_daemon.py` scaffold

