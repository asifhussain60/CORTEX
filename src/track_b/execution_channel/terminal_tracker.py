"""
CORTEX 3.0 Track B: Terminal Tracker
====================================

Terminal monitoring component for capturing command execution and developer workflow.
Optimized for macOS with intelligent command analysis and context extraction.

Key Features:
- Terminal session monitoring
- Command execution tracking  
- Output analysis and error detection
- Developer workflow pattern recognition
- Integration with CORTEX brain for process context

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import asyncio
import os
import logging
import psutil
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import subprocess


@dataclass
class TerminalEvent:
    """Represents a terminal command event."""
    command: str
    timestamp: datetime
    exit_code: Optional[int]
    output_preview: str
    error_preview: str
    working_directory: str
    duration_ms: int
    process_id: int
    command_type: str  # 'build', 'test', 'git', 'file', 'package', 'other'


class TerminalTracker:
    """
    Terminal tracking component for CORTEX Track B
    
    Monitors terminal activity and command execution to capture
    development workflow and process context.
    """
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.logger = logging.getLogger("cortex.track_b.terminal_tracker")
        
        self.is_running = False
        self.event_queue = asyncio.Queue()
        
        # Tracking state
        self.tracked_processes: Set[int] = set()
        self.command_history: List[TerminalEvent] = []
        self.max_history_size = 100
        
        # Command classification patterns
        self.command_patterns = {
            'build': ['make', 'cmake', 'ninja', 'bazel', 'npm run build', 'yarn build', 'python setup.py'],
            'test': ['pytest', 'jest', 'mocha', 'npm test', 'yarn test', 'python -m pytest', 'cargo test'],
            'git': ['git add', 'git commit', 'git push', 'git pull', 'git merge', 'git checkout'],
            'file': ['ls', 'cat', 'grep', 'find', 'cp', 'mv', 'rm', 'mkdir', 'touch'],
            'package': ['pip install', 'npm install', 'yarn add', 'brew install', 'cargo install'],
        }
        
        # macOS specific terminal detection
        self.macos_terminals = ['Terminal', 'iTerm2', 'Hyper', 'Alacritty']
    
    async def start(self):
        """Start terminal monitoring."""
        if self.is_running:
            self.logger.warning("Terminal tracker is already running")
            return
        
        self.logger.info("Starting terminal tracker")
        
        # Check if we can access process information
        if not self._can_monitor_processes():
            self.logger.warning("Limited process monitoring capabilities")
        
        self.is_running = True
        self.logger.info("Terminal tracker started successfully")
    
    async def stop(self):
        """Stop terminal monitoring."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping terminal tracker...")
        self.is_running = False
        self.logger.info("Terminal tracker stopped")
    
    def _can_monitor_processes(self) -> bool:
        """Check if we have permissions to monitor processes."""
        try:
            # Try to access current process info
            psutil.Process().cmdline()
            return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            return False
    
    def _classify_command(self, command: str) -> str:
        """Classify a command based on patterns."""
        command_lower = command.lower().strip()
        
        for category, patterns in self.command_patterns.items():
            for pattern in patterns:
                if pattern in command_lower:
                    return category
        
        return 'other'
    
    def _is_development_command(self, command: str) -> bool:
        """Check if a command is related to development work."""
        dev_indicators = [
            'python', 'node', 'npm', 'yarn', 'pip', 'git', 'make', 'cmake',
            'cargo', 'go', 'java', 'javac', 'gcc', 'clang', 'rustc',
            'pytest', 'jest', 'mocha', 'test', 'build', 'compile',
            'docker', 'kubectl', 'terraform', 'ansible'
        ]
        
        command_lower = command.lower()
        return any(indicator in command_lower for indicator in dev_indicators)
    
    def _get_terminal_processes(self) -> List[psutil.Process]:
        """Get currently running terminal processes."""
        terminal_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_name = proc.info['name']
                    if proc_name in self.macos_terminals:
                        terminal_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.error(f"Error getting terminal processes: {e}")
        
        return terminal_processes
    
    def _get_child_processes(self, parent_pid: int) -> List[psutil.Process]:
        """Get child processes of a terminal."""
        children = []
        
        try:
            parent = psutil.Process(parent_pid)
            children = parent.children(recursive=True)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return children
    
    async def _monitor_process_execution(self, process: psutil.Process) -> Optional[TerminalEvent]:
        """Monitor a specific process execution."""
        try:
            start_time = datetime.now()
            
            # Get process info
            cmdline = process.cmdline()
            if not cmdline:
                return None
            
            command = ' '.join(cmdline)
            
            # Skip if not a development-related command
            if not self._is_development_command(command):
                return None
            
            working_dir = process.cwd()
            
            # Wait for process to complete (with timeout)
            timeout_seconds = 300  # 5 minutes max
            end_time = start_time + timedelta(seconds=timeout_seconds)
            
            while process.is_running() and datetime.now() < end_time:
                await asyncio.sleep(0.5)
            
            # Get final process info
            duration = datetime.now() - start_time
            duration_ms = int(duration.total_seconds() * 1000)
            
            # Try to get exit code
            try:
                exit_code = process.returncode
            except (psutil.NoSuchProcess, AttributeError):
                exit_code = None
            
            # Create terminal event
            event = TerminalEvent(
                command=command,
                timestamp=start_time,
                exit_code=exit_code,
                output_preview="",  # Would need more complex implementation to capture
                error_preview="",   # Would need more complex implementation to capture
                working_directory=working_dir,
                duration_ms=duration_ms,
                process_id=process.pid,
                command_type=self._classify_command(command)
            )
            
            return event
            
        except Exception as e:
            self.logger.error(f"Error monitoring process: {e}")
            return None
    
    async def _scan_for_new_processes(self):
        """Scan for new terminal processes and commands."""
        try:
            current_processes = set()
            
            # Get all terminal processes
            terminal_processes = self._get_terminal_processes()
            
            for terminal_proc in terminal_processes:
                try:
                    # Get child processes (actual commands)
                    child_processes = self._get_child_processes(terminal_proc.pid)
                    
                    for child in child_processes:
                        current_processes.add(child.pid)
                        
                        # Check if this is a new process
                        if child.pid not in self.tracked_processes:
                            self.tracked_processes.add(child.pid)
                            
                            # Monitor this process
                            asyncio.create_task(self._track_process(child))
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Clean up finished processes from tracking
            finished_pids = self.tracked_processes - current_processes
            for pid in finished_pids:
                self.tracked_processes.discard(pid)
                
        except Exception as e:
            self.logger.error(f"Error scanning for processes: {e}")
    
    async def _track_process(self, process: psutil.Process):
        """Track a single process execution."""
        try:
            event = await self._monitor_process_execution(process)
            
            if event:
                # Add to history
                self.command_history.append(event)
                if len(self.command_history) > self.max_history_size:
                    self.command_history.pop(0)
                
                # Queue for processing
                await self.event_queue.put(event)
                
                self.logger.debug(f"Tracked command: {event.command_type} - {event.command[:50]}")
                
        except Exception as e:
            self.logger.error(f"Error tracking process: {e}")
        finally:
            # Remove from tracking
            self.tracked_processes.discard(process.pid)
    
    async def _analyze_command_patterns(self) -> Dict[str, Any]:
        """Analyze recent command patterns for insights."""
        if not self.command_history:
            return {}
        
        try:
            recent_commands = self.command_history[-20:]  # Last 20 commands
            
            # Command type distribution
            type_counts = {}
            for cmd in recent_commands:
                type_counts[cmd.command_type] = type_counts.get(cmd.command_type, 0) + 1
            
            # Average duration by type
            type_durations = {}
            for cmd_type in type_counts:
                durations = [cmd.duration_ms for cmd in recent_commands if cmd.command_type == cmd_type]
                if durations:
                    type_durations[cmd_type] = sum(durations) / len(durations)
            
            # Failed commands (exit code != 0)
            failed_commands = [cmd for cmd in recent_commands if cmd.exit_code and cmd.exit_code != 0]
            
            return {
                'total_commands': len(recent_commands),
                'command_types': type_counts,
                'average_durations_ms': type_durations,
                'failed_commands': len(failed_commands),
                'success_rate': (len(recent_commands) - len(failed_commands)) / len(recent_commands) if recent_commands else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing command patterns: {e}")
            return {}
    
    async def get_events(self) -> List[Dict[str, Any]]:
        """Get all pending terminal events."""
        if not self.is_running:
            return []
        
        # Scan for new processes
        await self._scan_for_new_processes()
        
        events = []
        
        try:
            # Collect all queued events
            while not self.event_queue.empty():
                event = await self.event_queue.get()
                
                # Skip commands not in workspace
                if not event.working_directory.startswith(str(self.workspace_path)):
                    continue
                
                events.append({
                    'type': 'terminal_command',
                    'command': event.command,
                    'command_type': event.command_type,
                    'timestamp': event.timestamp.isoformat(),
                    'exit_code': event.exit_code,
                    'duration_ms': event.duration_ms,
                    'working_directory': event.working_directory,
                    'process_id': event.process_id,
                    'success': event.exit_code == 0 if event.exit_code is not None else None,
                    'summary': f"{event.command_type.capitalize()} command: {event.command[:50]}{'...' if len(event.command) > 50 else ''}"
                })
        except Exception as e:
            self.logger.error(f"Error getting terminal events: {e}")
        
        return events
    
    async def get_command_analysis(self) -> Dict[str, Any]:
        """Get analysis of recent command patterns."""
        return await self._analyze_command_patterns()
    
    def get_status(self) -> Dict[str, Any]:
        """Get terminal tracker status."""
        return {
            'is_running': self.is_running,
            'workspace_path': str(self.workspace_path),
            'tracked_processes': len(self.tracked_processes),
            'command_history_size': len(self.command_history),
            'pending_events': self.event_queue.qsize(),
            'can_monitor_processes': self._can_monitor_processes(),
            'supported_terminals': self.macos_terminals
        }