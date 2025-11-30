"""
CORTEX 3.0 - Workspace Health Collector
======================================

Collects metrics on workspace health and development environment status.
Monitors code quality, build status, test coverage, and development flow.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #3 (Week 1)
Effort: 1 hour (workspace health collector)
Target: Development environment monitoring
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import subprocess
import os
import json
from pathlib import Path

from .base_collector import BaseCollector, CollectorMetric, CollectorPriority


class WorkspaceHealthCollector(BaseCollector):
    """
    Collects metrics on workspace health and development status.
    
    Metrics collected:
    - Git repository health (commit frequency, branch status)
    - Build status and success rates
    - Test coverage and pass rates
    - Code quality metrics
    - Development environment health
    """
    
    def __init__(self, workspace_path: Optional[str] = None, brain_path: Optional[str] = None):
        super().__init__(
            collector_id="workspace_health",
            name="Workspace Health Monitor",
            priority=CollectorPriority.MEDIUM,
            collection_interval_seconds=300.0,  # Every 5 minutes
            brain_path=brain_path
        )
        
        # Workspace configuration
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        
        # Health tracking
        self.git_status = {}
        self.build_history = []
        self.test_results = {}
        self.code_quality_scores = {}
        
        # Environment checks
        self.python_version = None
        self.node_version = None
        self.git_available = False
    
    def _initialize(self) -> bool:
        """Initialize workspace health collector"""
        try:
            # Verify workspace exists
            if not self.workspace_path.exists():
                self.logger.warning(f"Workspace path does not exist: {self.workspace_path}")
                return False
            
            # Check for development tools
            self._check_development_environment()
            
            # Initial git status
            self._update_git_status()
            
            self.logger.info("Workspace health collector initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize workspace health collector: {e}")
            return False
    
    def _check_development_environment(self) -> None:
        """Check availability of development tools"""
        # Check Python
        try:
            result = subprocess.run(['python', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.python_version = result.stdout.strip()
        except:
            try:
                result = subprocess.run(['python3', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.python_version = result.stdout.strip()
            except:
                pass
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.node_version = result.stdout.strip()
        except:
            pass
        
        # Check Git
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.git_available = True
        except:
            pass
    
    def _collect_metrics(self) -> List[CollectorMetric]:
        """Collect workspace health metrics"""
        metrics = []
        timestamp = datetime.now(timezone.utc)
        
        # Git repository health
        metrics.extend(self._collect_git_metrics(timestamp))
        
        # Development environment health
        metrics.extend(self._collect_environment_metrics(timestamp))
        
        # File system health
        metrics.extend(self._collect_filesystem_metrics(timestamp))
        
        # Build and test status
        metrics.extend(self._collect_build_metrics(timestamp))
        
        # Overall workspace health score
        metrics.append(self._calculate_workspace_health_score(timestamp))
        
        return metrics
    
    def _collect_git_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect Git repository metrics"""
        metrics = []
        
        if not self.git_available:
            return metrics
        
        try:
            # Update git status
            self._update_git_status()
            
            # Current branch
            if 'current_branch' in self.git_status:
                metrics.append(CollectorMetric(
                    name="git_current_branch",
                    value=self.git_status['current_branch'],
                    timestamp=timestamp,
                    tags={"type": "git", "category": "branch"}
                ))
            
            # Repository status
            if 'clean' in self.git_status:
                metrics.append(CollectorMetric(
                    name="git_repository_clean",
                    value=self.git_status['clean'],
                    timestamp=timestamp,
                    tags={"type": "git", "category": "status"}
                ))
            
            # Uncommitted changes
            if 'modified_files' in self.git_status:
                metrics.append(CollectorMetric(
                    name="git_modified_files_count",
                    value=len(self.git_status['modified_files']),
                    timestamp=timestamp,
                    tags={"type": "git", "category": "changes"}
                ))
            
            # Recent commit activity
            commit_count = self._get_recent_commit_count()
            metrics.append(CollectorMetric(
                name="git_recent_commits_24h",
                value=commit_count,
                timestamp=timestamp,
                tags={"type": "git", "category": "activity", "timeframe": "24h"}
            ))
            
        except Exception as e:
            self.logger.warning(f"Failed to collect git metrics: {e}")
        
        return metrics
    
    def _collect_environment_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect development environment metrics"""
        metrics = []
        
        # Python availability
        metrics.append(CollectorMetric(
            name="python_available",
            value=self.python_version is not None,
            timestamp=timestamp,
            tags={"type": "environment", "tool": "python"},
            metadata={"version": self.python_version}
        ))
        
        # Node.js availability  
        metrics.append(CollectorMetric(
            name="nodejs_available",
            value=self.node_version is not None,
            timestamp=timestamp,
            tags={"type": "environment", "tool": "nodejs"},
            metadata={"version": self.node_version}
        ))
        
        # Git availability
        metrics.append(CollectorMetric(
            name="git_available",
            value=self.git_available,
            timestamp=timestamp,
            tags={"type": "environment", "tool": "git"}
        ))
        
        # Workspace configuration files
        config_files = [
            "package.json", "requirements.txt", "pyproject.toml", 
            "tsconfig.json", ".gitignore", "README.md"
        ]
        
        existing_configs = [f for f in config_files if (self.workspace_path / f).exists()]
        metrics.append(CollectorMetric(
            name="configuration_files_present",
            value=len(existing_configs),
            timestamp=timestamp,
            tags={"type": "environment", "category": "config"},
            metadata={"files": existing_configs, "total_checked": len(config_files)}
        ))
        
        return metrics
    
    def _collect_filesystem_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect file system health metrics"""
        metrics = []
        
        try:
            # Workspace size
            total_size = self._calculate_directory_size(self.workspace_path)
            metrics.append(CollectorMetric(
                name="workspace_total_size",
                value=total_size,
                timestamp=timestamp,
                tags={"type": "filesystem", "unit": "bytes"}
            ))
            
            # File counts by type
            file_counts = self._count_files_by_type()
            metrics.append(CollectorMetric(
                name="workspace_file_counts",
                value=file_counts,
                timestamp=timestamp,
                tags={"type": "filesystem", "category": "inventory"}
            ))
            
            # Source code health
            source_files = file_counts.get('.py', 0) + file_counts.get('.js', 0) + file_counts.get('.ts', 0)
            test_files = file_counts.get('test_', 0)  # Files starting with 'test_'
            
            if source_files > 0:
                test_coverage_ratio = test_files / source_files
                metrics.append(CollectorMetric(
                    name="test_file_coverage_ratio",
                    value=test_coverage_ratio,
                    timestamp=timestamp,
                    tags={"type": "quality", "category": "testing"},
                    metadata={"source_files": source_files, "test_files": test_files}
                ))
            
        except Exception as e:
            self.logger.warning(f"Failed to collect filesystem metrics: {e}")
        
        return metrics
    
    def _collect_build_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect build and test status metrics"""
        metrics = []
        
        try:
            # Check for common build/test files
            build_files = {
                "package.json": ["npm test", "npm run build"],
                "requirements.txt": ["python -m pytest", "python setup.py build"],
                "pyproject.toml": ["python -m pytest", "python -m build"]
            }
            
            available_commands = []
            for file_name, commands in build_files.items():
                if (self.workspace_path / file_name).exists():
                    available_commands.extend(commands)
            
            metrics.append(CollectorMetric(
                name="build_commands_available",
                value=len(available_commands),
                timestamp=timestamp,
                tags={"type": "build", "category": "availability"},
                metadata={"commands": available_commands}
            ))
            
            # Quick build health check (if package.json exists)
            if (self.workspace_path / "package.json").exists():
                build_health = self._check_npm_health()
                metrics.append(CollectorMetric(
                    name="npm_build_health",
                    value=build_health,
                    timestamp=timestamp,
                    tags={"type": "build", "category": "npm"}
                ))
            
            # Quick Python health check (if requirements.txt exists)
            if (self.workspace_path / "requirements.txt").exists():
                python_health = self._check_python_health()
                metrics.append(CollectorMetric(
                    name="python_environment_health", 
                    value=python_health,
                    timestamp=timestamp,
                    tags={"type": "build", "category": "python"}
                ))
            
        except Exception as e:
            self.logger.warning(f"Failed to collect build metrics: {e}")
        
        return metrics
    
    def _calculate_workspace_health_score(self, timestamp: datetime) -> CollectorMetric:
        """Calculate overall workspace health score (0-100)"""
        score = 100.0
        factors = []
        
        try:
            # Git health (25 points)
            if self.git_available and self.git_status.get('clean', False):
                git_score = 25.0
            elif self.git_available:
                git_score = 15.0  # Git available but has changes
            else:
                git_score = 0.0
            score = min(score, 75 + git_score)
            factors.append(f"git: {git_score}/25")
            
            # Development tools (25 points)
            tools_score = 0
            if self.python_version:
                tools_score += 10
            if self.node_version:
                tools_score += 10
            if self.git_available:
                tools_score += 5
            score = min(score, 75 + tools_score)
            factors.append(f"tools: {tools_score}/25")
            
            # Configuration files (25 points)
            config_files = ["package.json", "requirements.txt", ".gitignore", "README.md"]
            existing_configs = sum(1 for f in config_files if (self.workspace_path / f).exists())
            config_score = (existing_configs / len(config_files)) * 25
            score = min(score, 75 + config_score)
            factors.append(f"config: {config_score:.1f}/25")
            
            # File organization (25 points)
            has_src = (self.workspace_path / "src").exists()
            has_tests = any((self.workspace_path / d).exists() for d in ["tests", "test"])
            has_docs = (self.workspace_path / "docs").exists()
            
            org_score = 0
            if has_src:
                org_score += 10
            if has_tests:
                org_score += 10
            if has_docs:
                org_score += 5
            score = min(score, 75 + org_score)
            factors.append(f"organization: {org_score}/25")
            
        except Exception as e:
            self.logger.warning(f"Error calculating workspace health score: {e}")
            score = 50.0
            factors.append("error in calculation")
        
        return CollectorMetric(
            name="workspace_health_score",
            value=score,
            timestamp=timestamp,
            tags={"type": "health", "unit": "score"},
            metadata={"factors": factors, "max_score": 100.0}
        )
    
    def _update_git_status(self) -> None:
        """Update Git repository status"""
        if not self.git_available:
            return
        
        try:
            os.chdir(self.workspace_path)
            
            # Current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.git_status['current_branch'] = result.stdout.strip()
            
            # Repository status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                modified_files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                self.git_status['modified_files'] = modified_files
                self.git_status['clean'] = len(modified_files) == 0
            
        except Exception as e:
            self.logger.debug(f"Git status update failed: {e}")
    
    def _get_recent_commit_count(self) -> int:
        """Get number of commits in the last 24 hours"""
        try:
            os.chdir(self.workspace_path)
            result = subprocess.run([
                'git', 'rev-list', '--count', '--since=24 hours ago', 'HEAD'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return int(result.stdout.strip())
        except:
            pass
        return 0
    
    def _calculate_directory_size(self, directory: Path) -> int:
        """Calculate total size of directory in bytes"""
        total_size = 0
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            self.logger.warning(f"Error calculating directory size: {e}")
        return total_size
    
    def _count_files_by_type(self) -> Dict[str, int]:
        """Count files by extension"""
        file_counts = {}
        try:
            for file_path in self.workspace_path.rglob("*"):
                if file_path.is_file():
                    # Count by extension
                    ext = file_path.suffix.lower()
                    if ext:
                        file_counts[ext] = file_counts.get(ext, 0) + 1
                    
                    # Count test files
                    if file_path.name.startswith('test_'):
                        file_counts['test_'] = file_counts.get('test_', 0) + 1
        except Exception as e:
            self.logger.warning(f"Error counting files: {e}")
        return file_counts
    
    def _check_npm_health(self) -> bool:
        """Quick check of npm/Node.js health"""
        try:
            os.chdir(self.workspace_path)
            result = subprocess.run(['npm', 'list', '--depth=0'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def _check_python_health(self) -> bool:
        """Quick check of Python environment health"""
        try:
            result = subprocess.run(['python', '-c', 'import sys; print(sys.version)'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            try:
                result = subprocess.run(['python3', '-c', 'import sys; print(sys.version)'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            except:
                return False
    
    def get_workspace_summary(self) -> Dict[str, Any]:
        """Get summary of workspace health"""
        return {
            "workspace_path": str(self.workspace_path),
            "git_available": self.git_available,
            "git_clean": self.git_status.get('clean', False),
            "current_branch": self.git_status.get('current_branch', 'unknown'),
            "python_version": self.python_version,
            "node_version": self.node_version,
            "modified_files_count": len(self.git_status.get('modified_files', []))
        }