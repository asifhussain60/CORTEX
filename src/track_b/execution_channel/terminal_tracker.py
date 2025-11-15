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
        """Enhanced Intelligence: Classify a command with intelligent pattern recognition."""
        command_lower = command.lower().strip()
        
        # Enhanced command classification with context awareness
        classification = self._basic_command_classification(command_lower)
        
        # Apply intelligent context analysis
        enhanced_classification = self._enhance_classification_with_context(command, classification)
        
        return enhanced_classification
    
    def _basic_command_classification(self, command: str) -> str:
        """Basic pattern matching for command classification."""
        for category, patterns in self.command_patterns.items():
            for pattern in patterns:
                if pattern in command:
                    return category
        return 'other'
    
    def _enhance_classification_with_context(self, command: str, basic_classification: str) -> str:
        """Enhanced Intelligence: Add context-aware classification enhancement."""
        # Workflow context enhancement
        workflow_context = self._analyze_workflow_context(command)
        
        if workflow_context['is_workflow_command']:
            return f"{basic_classification}_workflow"
        
        # Productivity impact analysis
        productivity_impact = self._assess_productivity_impact(command, basic_classification)
        
        if productivity_impact == 'high':
            return f"{basic_classification}_high_impact"
        elif productivity_impact == 'disruptive':
            return f"{basic_classification}_disruptive"
        
        return basic_classification
    
    def _analyze_workflow_context(self, command: str) -> Dict[str, Any]:
        """Enhanced Intelligence: Analyze workflow context for command."""
        context = {
            'is_workflow_command': False,
            'workflow_type': 'unknown',
            'sequence_position': 'standalone',
            'common_followup': None
        }
        
        # Check for common workflow patterns
        workflow_indicators = {
            'ci_cd': ['pip install', 'npm ci', 'yarn install', 'pytest', 'npm test', 'docker build'],
            'deployment': ['docker push', 'kubectl apply', 'terraform apply', 'git push origin'],
            'debugging': ['grep -r', 'tail -f', 'less', 'cat', 'python -c', 'node -e'],
            'development_cycle': ['git add', 'git commit', 'git push', 'npm run dev', 'python manage.py'],
            'setup': ['mkdir', 'cd', 'virtualenv', 'source', 'export', 'pip install -r']
        }
        
        command_lower = command.lower()
        for workflow_type, indicators in workflow_indicators.items():
            if any(indicator in command_lower for indicator in indicators):
                context['is_workflow_command'] = True
                context['workflow_type'] = workflow_type
                break
        
        # Analyze command sequence position
        if len(self.command_history) > 0:
            recent_commands = [event.command.lower() for event in self.command_history[-3:]]
            context['sequence_position'] = self._determine_sequence_position(command_lower, recent_commands)
        
        return context
    
    def _determine_sequence_position(self, command: str, recent_commands: List[str]) -> str:
        """Enhanced Intelligence: Determine position in command sequence."""
        # Common command sequences
        sequences = {
            'git_workflow': ['git add', 'git commit', 'git push'],
            'test_workflow': ['pip install', 'pytest', 'coverage report'],
            'build_workflow': ['make clean', 'make', 'make install'],
            'docker_workflow': ['docker build', 'docker tag', 'docker push']
        }
        
        for sequence_name, sequence in sequences.items():
            for i, seq_command in enumerate(sequence):
                if seq_command in command:
                    # Check if previous commands match the sequence
                    if i > 0 and len(recent_commands) >= i:
                        if all(sequence[j] in recent_commands[-(i-j)] for j in range(i)):
                            if i == len(sequence) - 1:
                                return 'sequence_end'
                            else:
                                return 'sequence_middle'
                    elif i == 0:
                        return 'sequence_start'
        
        return 'standalone'
    
    def _assess_productivity_impact(self, command: str, command_type: str) -> str:
        """Enhanced Intelligence: Assess productivity impact of command."""
        command_lower = command.lower()
        
        # High productivity commands
        high_productivity = [
            'pytest', 'npm test', 'make test',  # Testing
            'git commit', 'git push',  # Version control
            'python -m', 'node', 'npm run',  # Execution
        ]
        
        # Potentially disruptive commands
        disruptive_patterns = [
            'rm -rf', 'sudo', 'chmod 777', 'kill -9',  # Dangerous operations
            'pip uninstall', 'npm uninstall',  # Dependency removal
            'git reset --hard', 'git clean -fd'  # Destructive git operations
        ]
        
        if any(pattern in command_lower for pattern in high_productivity):
            return 'high'
        elif any(pattern in command_lower for pattern in disruptive_patterns):
            return 'disruptive'
        elif command_type in ['test', 'build', 'git']:
            return 'medium'
        else:
            return 'low'
    
    async def analyze_workflow_patterns(self) -> Dict[str, Any]:
        """Enhanced Intelligence: Analyze workflow patterns and productivity metrics."""
        analysis = {
            'workflow_efficiency': 'unknown',
            'common_workflows': {},
            'productivity_metrics': {},
            'time_patterns': {},
            'recommendations': []
        }
        
        try:
            if len(self.command_history) < 5:
                analysis['workflow_efficiency'] = 'insufficient_data'
                return analysis
            
            # Analyze common workflows
            analysis['common_workflows'] = self._identify_common_workflows()
            
            # Calculate productivity metrics
            analysis['productivity_metrics'] = self._calculate_productivity_metrics()
            
            # Analyze time patterns
            analysis['time_patterns'] = self._analyze_time_patterns()
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_workflow_recommendations(analysis)
            
            # Determine overall efficiency
            analysis['workflow_efficiency'] = self._calculate_workflow_efficiency(analysis)
            
            self.logger.debug(f"Workflow analysis complete: {analysis['workflow_efficiency']}")
            
        except Exception as e:
            self.logger.error(f"Error analyzing workflow patterns: {e}")
            analysis['workflow_efficiency'] = 'analysis_error'
        
        return analysis
    
    def _identify_common_workflows(self) -> Dict[str, Any]:
        """Enhanced Intelligence: Identify recurring workflow patterns."""
        workflows = {}
        
        # Group commands by time windows (1-hour windows)
        command_groups = []
        current_group = []
        
        for i, event in enumerate(self.command_history):
            if not current_group:
                current_group = [event]
            else:
                time_diff = event.timestamp - current_group[-1].timestamp
                if time_diff.total_seconds() <= 3600:  # 1 hour
                    current_group.append(event)
                else:
                    if len(current_group) > 2:
                        command_groups.append(current_group)
                    current_group = [event]
        
        # Add final group
        if len(current_group) > 2:
            command_groups.append(current_group)
        
        # Identify patterns
        workflow_patterns = {}
        for group in command_groups:
            command_sequence = [self._classify_command(event.command) for event in group]
            pattern_key = ' -> '.join(command_sequence[:5])  # First 5 commands
            
            if pattern_key not in workflow_patterns:
                workflow_patterns[pattern_key] = {
                    'count': 0,
                    'avg_duration': timedelta(),
                    'success_rate': 0.0
                }
            
            workflow_patterns[pattern_key]['count'] += 1
            
            # Calculate duration and success rate
            total_duration = group[-1].timestamp - group[0].timestamp
            success_count = sum(1 for event in group if event.exit_code == 0)
            
            patterns = workflow_patterns[pattern_key]
            patterns['avg_duration'] = (
                patterns['avg_duration'] * (patterns['count'] - 1) + total_duration
            ) / patterns['count']
            patterns['success_rate'] = success_count / len(group)
        
        # Return top 5 most common workflows
        sorted_workflows = sorted(
            workflow_patterns.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        workflows['top_workflows'] = sorted_workflows[:5]
        workflows['total_unique_workflows'] = len(workflow_patterns)
        
        return workflows
    
    def _calculate_productivity_metrics(self) -> Dict[str, Any]:
        """Enhanced Intelligence: Calculate productivity and efficiency metrics."""
        metrics = {
            'commands_per_hour': 0.0,
            'success_rate': 0.0,
            'avg_command_duration': timedelta(),
            'most_productive_hours': [],
            'workflow_completion_rate': 0.0
        }
        
        if not self.command_history:
            return metrics
        
        # Calculate basic metrics
        total_commands = len(self.command_history)
        successful_commands = sum(1 for event in self.command_history if event.exit_code == 0)
        
        metrics['success_rate'] = successful_commands / total_commands if total_commands > 0 else 0
        
        # Calculate time-based metrics
        if len(self.command_history) > 1:
            time_span = self.command_history[-1].timestamp - self.command_history[0].timestamp
            hours = time_span.total_seconds() / 3600
            metrics['commands_per_hour'] = total_commands / hours if hours > 0 else 0
        
        # Average duration
        durations = [event.duration_ms for event in self.command_history if event.duration_ms > 0]
        if durations:
            avg_duration_ms = sum(durations) / len(durations)
            metrics['avg_command_duration'] = timedelta(milliseconds=avg_duration_ms)
        
        # Most productive hours
        hour_productivity = {}
        for event in self.command_history:
            hour = event.timestamp.hour
            if hour not in hour_productivity:
                hour_productivity[hour] = {'commands': 0, 'success': 0}
            
            hour_productivity[hour]['commands'] += 1
            if event.exit_code == 0:
                hour_productivity[hour]['success'] += 1
        
        # Sort by success rate * command count
        productive_hours = []
        for hour, stats in hour_productivity.items():
            if stats['commands'] > 0:
                success_rate = stats['success'] / stats['commands']
                productivity_score = success_rate * stats['commands']
                productive_hours.append((hour, productivity_score, stats))
        
        metrics['most_productive_hours'] = sorted(
            productive_hours,
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return metrics
    
    def _analyze_time_patterns(self) -> Dict[str, Any]:
        """Enhanced Intelligence: Analyze temporal patterns in command usage."""
        patterns = {
            'peak_hours': [],
            'workflow_timing': {},
            'session_patterns': {},
            'day_of_week_patterns': {}
        }
        
        if not self.command_history:
            return patterns
        
        # Analyze hourly distribution
        hourly_counts = {}
        for event in self.command_history:
            hour = event.timestamp.hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        # Find peak hours (top 3)
        sorted_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)
        patterns['peak_hours'] = sorted_hours[:3]
        
        # Analyze workflow timing preferences
        workflow_times = {}
        for event in self.command_history:
            command_type = self._classify_command(event.command)
            hour = event.timestamp.hour
            
            if command_type not in workflow_times:
                workflow_times[command_type] = {}
            
            workflow_times[command_type][hour] = workflow_times[command_type].get(hour, 0) + 1
        
        patterns['workflow_timing'] = workflow_times
        
        return patterns
    
    def _generate_workflow_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Enhanced Intelligence: Generate workflow improvement recommendations."""
        recommendations = []
        
        try:
            # Productivity recommendations
            productivity = analysis.get('productivity_metrics', {})
            success_rate = productivity.get('success_rate', 0)
            
            if success_rate < 0.8:
                recommendations.append(f"Command success rate is {success_rate:.1%}. Consider reviewing failed commands for patterns.")
            
            # Workflow efficiency recommendations
            workflows = analysis.get('common_workflows', {})
            top_workflows = workflows.get('top_workflows', [])
            
            for workflow_pattern, stats in top_workflows:
                if stats['success_rate'] < 0.7:
                    recommendations.append(f"Workflow '{workflow_pattern}' has low success rate ({stats['success_rate']:.1%}). Consider optimization.")
            
            # Time pattern recommendations
            time_patterns = analysis.get('time_patterns', {})
            peak_hours = time_patterns.get('peak_hours', [])
            
            if peak_hours:
                most_productive_hour = peak_hours[0][0]
                recommendations.append(f"You're most active at {most_productive_hour}:00. Consider scheduling complex tasks during peak hours.")
            
            # Commands per hour recommendation
            commands_per_hour = productivity.get('commands_per_hour', 0)
            if commands_per_hour > 20:
                recommendations.append("High command frequency detected. Consider batching operations or using scripts for repetitive tasks.")
            
        except Exception as e:
            self.logger.error(f"Error generating workflow recommendations: {e}")
        
        return recommendations
    
    def _calculate_workflow_efficiency(self, analysis: Dict[str, Any]) -> str:
        """Enhanced Intelligence: Calculate overall workflow efficiency score."""
        try:
            score = 100  # Start with perfect score
            
            # Deduct for low success rate
            productivity = analysis.get('productivity_metrics', {})
            success_rate = productivity.get('success_rate', 0)
            if success_rate < 0.8:
                score -= (0.8 - success_rate) * 50  # Up to 10 points deduction
            
            # Deduct for inefficient workflows
            workflows = analysis.get('common_workflows', {})
            top_workflows = workflows.get('top_workflows', [])
            
            inefficient_workflows = sum(1 for _, stats in top_workflows if stats['success_rate'] < 0.7)
            score -= inefficient_workflows * 10
            
            # Bonus for consistent patterns
            if len(top_workflows) > 0 and top_workflows[0][1]['count'] > 3:
                score += 10  # Bonus for consistent workflow usage
            
            # Categorize efficiency
            if score >= 85:
                return 'excellent'
            elif score >= 70:
                return 'good'
            elif score >= 50:
                return 'fair'
            else:
                return 'poor'
        
        except Exception as e:
            self.logger.error(f"Error calculating workflow efficiency: {e}")
            return 'unknown'
    
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