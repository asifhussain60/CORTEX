"""
CORTEX 3.0 Track B: Git Monitor
==============================

Git monitoring component for capturing repository changes and developer workflow.
Integrates with git hooks and provides intelligent commit analysis.

Key Features:
- Git hook integration for real-time change detection
- Commit analysis and pattern recognition
- Branch workflow tracking
- Integration with CORTEX brain for project evolution tracking
- macOS git optimization

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import asyncio
import subprocess
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class GitEvent:
    """Represents a git operation event."""
    event_type: str  # 'commit', 'branch', 'merge', 'pull', 'push'
    timestamp: datetime
    author: str
    message: str
    files_changed: List[str]
    stats: Dict[str, int]  # lines added/removed
    branch: str
    commit_hash: Optional[str] = None


class GitMonitor:
    """
    Git monitoring component for CORTEX Track B
    
    Monitors git operations and analyzes repository evolution
    for development context capture.
    """
    
    def __init__(self, workspace_path: Path, enable_hooks: bool = True):
        self.workspace_path = workspace_path
        self.enable_hooks = enable_hooks
        self.logger = logging.getLogger("cortex.track_b.git_monitor")
        
        self.is_running = False
        self.event_queue = asyncio.Queue()
        
        # Git repository validation
        self.git_dir = self._find_git_directory()
        self.is_git_repo = self.git_dir is not None
        
        # Last processed commit to avoid duplicates
        self.last_commit_hash = None
        
        self._validate_setup()
    
    def _find_git_directory(self) -> Optional[Path]:
        """Find the .git directory in the workspace or parent directories."""
        current_path = self.workspace_path
        
        while current_path.parent != current_path:  # Not root directory
            git_dir = current_path / '.git'
            if git_dir.exists():
                return git_dir
            current_path = current_path.parent
        
        return None
    
    def _validate_setup(self):
        """Validate git monitoring setup."""
        if not self.is_git_repo:
            self.logger.warning(f"No git repository found in {self.workspace_path}")
            return
        
        # Check if git command is available
        try:
            result = subprocess.run(
                ['git', '--version'], 
                capture_output=True, 
                text=True, 
                cwd=self.workspace_path
            )
            if result.returncode != 0:
                raise subprocess.SubprocessError("Git command failed")
                
            self.logger.debug(f"Git available: {result.stdout.strip()}")
            
        except (subprocess.SubprocessError, FileNotFoundError):
            self.logger.error("Git command not available")
            self.is_git_repo = False
    
    async def start(self):
        """Start git monitoring."""
        if self.is_running:
            self.logger.warning("Git monitor is already running")
            return
        
        if not self.is_git_repo:
            self.logger.warning("Git monitoring disabled: not a git repository")
            return
        
        self.logger.info(f"Starting git monitor for: {self.workspace_path}")
        
        # Get initial state
        await self._initialize_state()
        
        # Setup git hooks if enabled
        if self.enable_hooks:
            await self._setup_git_hooks()
        
        self.is_running = True
        self.logger.info("Git monitor started successfully")
    
    async def stop(self):
        """Stop git monitoring."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping git monitor...")
        self.is_running = False
        self.logger.info("Git monitor stopped")
    
    async def _initialize_state(self):
        """Initialize monitoring state with current git status."""
        try:
            # Get current commit hash
            result = await self._run_git_command(['rev-parse', 'HEAD'])
            if result:
                self.last_commit_hash = result.strip()
                self.logger.debug(f"Initialized with commit: {self.last_commit_hash[:8]}")
            
        except Exception as e:
            self.logger.error(f"Error initializing git state: {e}")
    
    async def _setup_git_hooks(self):
        """Setup git hooks for real-time monitoring."""
        try:
            hooks_dir = self.git_dir / 'hooks'
            hooks_dir.mkdir(exist_ok=True)
            
            # Post-commit hook
            post_commit_hook = hooks_dir / 'post-commit'
            hook_script = f'''#!/bin/sh
# CORTEX Track B Git Hook
echo "$(date -Iseconds) post-commit $(git rev-parse HEAD)" >> "{self.git_dir}/cortex-events.log"
'''
            
            with open(post_commit_hook, 'w') as f:
                f.write(hook_script)
            
            post_commit_hook.chmod(0o755)
            
            # Post-merge hook
            post_merge_hook = hooks_dir / 'post-merge'
            hook_script = f'''#!/bin/sh
# CORTEX Track B Git Hook  
echo "$(date -Iseconds) post-merge $(git rev-parse HEAD)" >> "{self.git_dir}/cortex-events.log"
'''
            
            with open(post_merge_hook, 'w') as f:
                f.write(hook_script)
            
            post_merge_hook.chmod(0o755)
            
            self.logger.info("Git hooks installed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup git hooks: {e}")
    
    async def _run_git_command(self, args: List[str]) -> Optional[str]:
        """Run a git command and return the output."""
        try:
            result = await asyncio.create_subprocess_exec(
                'git', *args,
                cwd=self.workspace_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                return stdout.decode('utf-8')
            else:
                self.logger.error(f"Git command failed: {stderr.decode('utf-8')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error running git command: {e}")
            return None
    
    async def _get_commit_info(self, commit_hash: str) -> Optional[GitEvent]:
        """Get detailed information about a commit."""
        try:
            # Get commit details
            format_str = '%H%n%an%n%s%n%ai'  # hash, author, subject, date
            result = await self._run_git_command([
                'show', '--format=' + format_str, '--name-only', commit_hash
            ])
            
            if not result:
                return None
            
            lines = result.strip().split('\n')
            if len(lines) < 4:
                return None
            
            commit_hash_full = lines[0]
            author = lines[1]
            message = lines[2]
            timestamp_str = lines[3]
            
            # Parse timestamp
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except ValueError:
                timestamp = datetime.now()
            
            # Get changed files
            files_changed = lines[4:] if len(lines) > 4 else []
            
            # Get current branch
            branch_result = await self._run_git_command(['branch', '--show-current'])
            branch = branch_result.strip() if branch_result else 'unknown'
            
            # Get commit stats
            stats_result = await self._run_git_command([
                'show', '--stat', '--format=', commit_hash
            ])
            
            stats = await self._parse_git_stats(stats_result or '')
            
            return GitEvent(
                event_type='commit',
                timestamp=timestamp,
                author=author,
                message=message,
                files_changed=files_changed,
                stats=stats,
                branch=branch,
                commit_hash=commit_hash_full
            )
            
        except Exception as e:
            self.logger.error(f"Error getting commit info: {e}")
            return None
    
    async def _parse_git_stats(self, stats_output: str) -> Dict[str, int]:
        """Parse git stats output to extract line changes."""
        stats = {'files_changed': 0, 'lines_added': 0, 'lines_deleted': 0}
        
        try:
            lines = stats_output.strip().split('\n')
            
            for line in lines:
                if ' files changed' in line or ' file changed' in line:
                    # Parse summary line: "2 files changed, 15 insertions(+), 3 deletions(-)"
                    parts = line.split(',')
                    
                    for part in parts:
                        part = part.strip()
                        if 'file' in part and 'changed' in part:
                            stats['files_changed'] = int(part.split()[0])
                        elif 'insertion' in part:
                            stats['lines_added'] = int(part.split()[0])
                        elif 'deletion' in part:
                            stats['lines_deleted'] = int(part.split()[0])
                    break
        
        except Exception as e:
            self.logger.error(f"Error parsing git stats: {e}")
        
        return stats
    
    async def _check_for_new_commits(self):
        """Check for new commits since last check."""
        try:
            # Get current HEAD
            current_commit = await self._run_git_command(['rev-parse', 'HEAD'])
            if not current_commit:
                return
            
            current_commit = current_commit.strip()
            
            # Check if this is a new commit
            if current_commit != self.last_commit_hash:
                # Get all commits since last check
                if self.last_commit_hash:
                    commit_range = f"{self.last_commit_hash}..{current_commit}"
                    commit_list = await self._run_git_command([
                        'rev-list', '--reverse', commit_range
                    ])
                else:
                    # First run, just get the current commit
                    commit_list = current_commit
                
                if commit_list:
                    commits = commit_list.strip().split('\n')
                    
                    for commit_hash in commits:
                        if commit_hash.strip():
                            commit_info = await self._get_commit_info(commit_hash.strip())
                            if commit_info:
                                await self.event_queue.put(commit_info)
                
                self.last_commit_hash = current_commit
                
        except Exception as e:
            self.logger.error(f"Error checking for new commits: {e}")
    
    async def _check_hook_events(self):
        """Check for events from git hooks."""
        try:
            hook_log = self.git_dir / 'cortex-events.log'
            
            if not hook_log.exists():
                return
            
            # Read and process hook events
            with open(hook_log, 'r') as f:
                lines = f.readlines()
            
            if lines:
                # Process hook events
                for line in lines:
                    await self._process_hook_event(line.strip())
                
                # Clear the log after processing
                with open(hook_log, 'w') as f:
                    f.write('')
                    
        except Exception as e:
            self.logger.error(f"Error checking hook events: {e}")
    
    async def _process_hook_event(self, event_line: str):
        """Process a single hook event line."""
        try:
            # Parse event line: "2024-11-15T10:30:00+00:00 post-commit abc123def"
            parts = event_line.split(' ', 2)
            if len(parts) < 3:
                return
            
            timestamp_str = parts[0]
            event_type = parts[1]
            commit_hash = parts[2]
            
            # Get detailed commit info
            commit_info = await self._get_commit_info(commit_hash)
            if commit_info:
                await self.event_queue.put(commit_info)
                
        except Exception as e:
            self.logger.error(f"Error processing hook event: {e}")
    
    async def get_events(self) -> List[Dict[str, Any]]:
        """Get all pending git events."""
        if not self.is_running or not self.is_git_repo:
            return []
        
        # Check for new commits
        await self._check_for_new_commits()
        
        # Check hook events
        await self._check_hook_events()
        
        events = []
        
        try:
            # Collect all queued events
            while not self.event_queue.empty():
                event = await self.event_queue.get()
                events.append({
                    'type': 'git_operation',
                    'event_type': event.event_type,
                    'timestamp': event.timestamp.isoformat(),
                    'author': event.author,
                    'message': event.message,
                    'commit_hash': event.commit_hash,
                    'branch': event.branch,
                    'files_changed': event.files_changed,
                    'stats': event.stats,
                    'summary': f"{event.event_type.capitalize()}: {event.message[:50]}{'...' if len(event.message) > 50 else ''}"
                })
        except Exception as e:
            self.logger.error(f"Error getting git events: {e}")
        
        return events
    
    def get_status(self) -> Dict[str, Any]:
        """Get git monitor status."""
        return {
            'is_running': self.is_running,
            'is_git_repo': self.is_git_repo,
            'git_dir': str(self.git_dir) if self.git_dir else None,
            'workspace_path': str(self.workspace_path),
            'hooks_enabled': self.enable_hooks,
            'last_commit': self.last_commit_hash,
            'pending_events': self.event_queue.qsize()
        }