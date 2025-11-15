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
from datetime import datetime, timedelta
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
    
    async def analyze_repository_health(self) -> Dict[str, Any]:
        """Enhanced Intelligence: Analyze repository health and provide insights."""
        health_analysis = {
            'overall_health': 'unknown',
            'commit_patterns': {},
            'branch_analysis': {},
            'file_hotspots': [],
            'productivity_metrics': {},
            'recommendations': []
        }
        
        try:
            if not self.is_git_repo:
                health_analysis['overall_health'] = 'no_git_repo'
                return health_analysis
            
            # Analyze commit patterns (last 30 days)
            health_analysis['commit_patterns'] = await self._analyze_commit_patterns()
            
            # Analyze branch structure
            health_analysis['branch_analysis'] = await self._analyze_branch_structure()
            
            # Identify file hotspots
            health_analysis['file_hotspots'] = await self._identify_file_hotspots()
            
            # Calculate productivity metrics
            health_analysis['productivity_metrics'] = await self._calculate_productivity_metrics()
            
            # Generate health recommendations
            health_analysis['recommendations'] = self._generate_health_recommendations(health_analysis)
            
            # Determine overall health score
            health_analysis['overall_health'] = self._calculate_overall_health_score(health_analysis)
            
            self.logger.debug(f"Repository health analysis complete: {health_analysis['overall_health']}")
            
        except Exception as e:
            self.logger.error(f"Error analyzing repository health: {e}")
            health_analysis['overall_health'] = 'analysis_error'
        
        return health_analysis
    
    async def _analyze_commit_patterns(self) -> Dict[str, Any]:
        """Analyze commit patterns to understand development rhythm."""
        patterns = {
            'total_commits_30_days': 0,
            'avg_commits_per_day': 0.0,
            'commit_sizes': {'small': 0, 'medium': 0, 'large': 0},
            'commit_times': [],
            'most_active_days': [],
            'commit_message_quality': 'unknown'
        }
        
        try:
            # Get commits from last 30 days
            since_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            commits_output = await self._run_git_command([
                'log', '--since', since_date, '--pretty=format:%H|%ad|%s', '--date=iso'
            ])
            
            if not commits_output:
                return patterns
            
            commits = commits_output.strip().split('\n')
            patterns['total_commits_30_days'] = len(commits)
            patterns['avg_commits_per_day'] = len(commits) / 30.0
            
            # Analyze commit characteristics
            commit_hours = []
            for commit_line in commits:
                if '|' not in commit_line:
                    continue
                    
                parts = commit_line.split('|')
                if len(parts) < 3:
                    continue
                    
                commit_hash, date_str, message = parts[0], parts[1], '|'.join(parts[2:])
                
                # Extract hour from date
                try:
                    commit_date = datetime.fromisoformat(date_str.replace(' +', '+'))
                    commit_hours.append(commit_date.hour)
                except:
                    pass
                
                # Analyze commit message quality
                if len(message) < 10:
                    continue
                elif message.startswith(('feat:', 'fix:', 'refactor:', 'docs:')):
                    # Conventional commits format - good quality
                    pass
            
            # Calculate most active hours
            if commit_hours:
                hour_counts = {}
                for hour in commit_hours:
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                
                patterns['most_active_hours'] = sorted(
                    hour_counts.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:3]
            
        except Exception as e:
            self.logger.error(f"Error analyzing commit patterns: {e}")
        
        return patterns
    
    async def _analyze_branch_structure(self) -> Dict[str, Any]:
        """Analyze branch structure and workflow patterns."""
        branch_analysis = {
            'total_branches': 0,
            'active_branches': [],
            'stale_branches': [],
            'default_branch': 'main',
            'workflow_pattern': 'unknown'
        }
        
        try:
            # Get all branches
            branches_output = await self._run_git_command(['branch', '-a'])
            if branches_output:
                lines = branches_output.strip().split('\n')
                branch_analysis['total_branches'] = len([l for l in lines if l.strip()])
                
                # Identify current/default branch
                for line in lines:
                    if line.strip().startswith('*'):
                        branch_analysis['default_branch'] = line.strip()[2:].strip()
                        break
            
            # Analyze branch activity (last 30 days)
            recent_branches = await self._run_git_command([
                'for-each-ref', '--format=%(refname:short) %(committerdate:relative)', 
                '--sort=-committerdate', 'refs/heads/'
            ])
            
            if recent_branches:
                for line in recent_branches.strip().split('\n'):
                    if not line.strip():
                        continue
                    parts = line.rsplit(' ', 1)
                    if len(parts) == 2:
                        branch_name, last_activity = parts
                        if any(recent in last_activity for recent in ['hours', 'days']) and not any(old in last_activity for old in ['weeks', 'months', 'years']):
                            branch_analysis['active_branches'].append({
                                'name': branch_name,
                                'last_activity': last_activity
                            })
                        else:
                            branch_analysis['stale_branches'].append({
                                'name': branch_name,
                                'last_activity': last_activity
                            })
            
        except Exception as e:
            self.logger.error(f"Error analyzing branch structure: {e}")
        
        return branch_analysis
    
    async def _identify_file_hotspots(self) -> List[Dict[str, Any]]:
        """Identify files that are changed frequently (potential hotspots)."""
        hotspots = []
        
        try:
            # Get file change frequency over last 30 days
            since_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            file_stats = await self._run_git_command([
                'log', '--since', since_date, '--name-only', '--pretty=format:'
            ])
            
            if not file_stats:
                return hotspots
            
            # Count file modifications
            file_counts = {}
            for line in file_stats.strip().split('\n'):
                if line.strip():
                    file_counts[line.strip()] = file_counts.get(line.strip(), 0) + 1
            
            # Sort by frequency and take top hotspots
            sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
            
            for file_path, change_count in sorted_files[:10]:  # Top 10 hotspots
                if change_count > 2:  # Only consider files changed more than twice
                    hotspots.append({
                        'file_path': file_path,
                        'change_count': change_count,
                        'risk_level': self._assess_hotspot_risk(change_count)
                    })
        
        except Exception as e:
            self.logger.error(f"Error identifying file hotspots: {e}")
        
        return hotspots
    
    def _assess_hotspot_risk(self, change_count: int) -> str:
        """Assess risk level based on file change frequency."""
        if change_count > 15:
            return 'high'
        elif change_count > 8:
            return 'medium'
        else:
            return 'low'
    
    async def _calculate_productivity_metrics(self) -> Dict[str, Any]:
        """Calculate productivity and development velocity metrics."""
        metrics = {
            'lines_of_code_trend': 'stable',
            'commit_velocity': 0.0,
            'average_commit_size': 0,
            'code_churn_rate': 0.0,
            'development_efficiency': 'unknown'
        }
        
        try:
            # Analyze code changes over time
            recent_stats = await self._run_git_command([
                'log', '--since=30.days.ago', '--numstat', '--pretty=format:'
            ])
            
            if recent_stats:
                lines_added_total = 0
                lines_deleted_total = 0
                total_commits = 0
                
                for line in recent_stats.strip().split('\n'):
                    if line.strip() and '\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                            lines_added_total += int(parts[0])
                            lines_deleted_total += int(parts[1])
                            total_commits += 1
                
                if total_commits > 0:
                    metrics['commit_velocity'] = total_commits / 30.0  # commits per day
                    metrics['average_commit_size'] = (lines_added_total + lines_deleted_total) / total_commits
                    metrics['code_churn_rate'] = lines_deleted_total / max(lines_added_total, 1)
                    
                    # Determine trend
                    if lines_added_total > lines_deleted_total * 1.5:
                        metrics['lines_of_code_trend'] = 'growing'
                    elif lines_deleted_total > lines_added_total * 1.2:
                        metrics['lines_of_code_trend'] = 'shrinking'
                    else:
                        metrics['lines_of_code_trend'] = 'stable'
        
        except Exception as e:
            self.logger.error(f"Error calculating productivity metrics: {e}")
        
        return metrics
    
    def _generate_health_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on repository health analysis."""
        recommendations = []
        
        try:
            # Commit pattern recommendations
            commit_patterns = analysis.get('commit_patterns', {})
            if commit_patterns.get('avg_commits_per_day', 0) < 0.5:
                recommendations.append("Consider more frequent, smaller commits for better tracking")
            
            # Branch recommendations
            branch_analysis = analysis.get('branch_analysis', {})
            if len(branch_analysis.get('stale_branches', [])) > 5:
                recommendations.append("Clean up stale branches to reduce repository clutter")
            
            # Hotspot recommendations
            file_hotspots = analysis.get('file_hotspots', [])
            high_risk_hotspots = [h for h in file_hotspots if h.get('risk_level') == 'high']
            if high_risk_hotspots:
                recommendations.append(f"Consider refactoring {len(high_risk_hotspots)} high-risk hotspot files")
            
            # Productivity recommendations
            productivity = analysis.get('productivity_metrics', {})
            if productivity.get('average_commit_size', 0) > 500:
                recommendations.append("Consider breaking down large commits into smaller, focused changes")
            
            if productivity.get('code_churn_rate', 0) > 0.3:
                recommendations.append("High code churn detected - review deleted code patterns")
        
        except Exception as e:
            self.logger.error(f"Error generating health recommendations: {e}")
        
        return recommendations
    
    def _calculate_overall_health_score(self, analysis: Dict[str, Any]) -> str:
        """Calculate overall repository health score."""
        try:
            score = 100  # Start with perfect score
            
            # Deduct points for issues
            commit_patterns = analysis.get('commit_patterns', {})
            if commit_patterns.get('avg_commits_per_day', 0) < 0.3:
                score -= 20  # Low commit frequency
            
            branch_analysis = analysis.get('branch_analysis', {})
            stale_branches = len(branch_analysis.get('stale_branches', []))
            if stale_branches > 10:
                score -= 15  # Too many stale branches
            
            file_hotspots = analysis.get('file_hotspots', [])
            high_risk_hotspots = len([h for h in file_hotspots if h.get('risk_level') == 'high'])
            score -= high_risk_hotspots * 5  # High-risk hotspots
            
            productivity = analysis.get('productivity_metrics', {})
            if productivity.get('code_churn_rate', 0) > 0.4:
                score -= 10  # High code churn
            
            # Categorize health
            if score >= 85:
                return 'excellent'
            elif score >= 70:
                return 'good'
            elif score >= 50:
                return 'fair'
            else:
                return 'poor'
        
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return 'unknown'
    
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