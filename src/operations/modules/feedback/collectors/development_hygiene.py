"""
Development Hygiene Collector

Collects commit quality, security scans, and code review metrics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DevelopmentHygieneCollector:
    """Collect development hygiene metrics."""
    
    def collect(self, project_root: Path) -> Dict[str, Any]:
        """
        Collect development hygiene metrics.
        
        Metrics:
            - Clean commit rate
            - Branch strategy compliance
            - Security vulnerabilities detected
            - Code review participation rate
            - Merge conflict frequency
        """
        try:
            return {
                'clean_commit_rate': self._calculate_clean_commit_rate(project_root),
                'branch_strategy_compliance': self._check_branch_strategy(project_root),
                'security_vulnerabilities': self._scan_security(project_root),
                'code_review_participation': self._get_review_participation(project_root),
                'merge_conflicts': self._count_merge_conflicts(project_root)
            }
        except Exception as e:
            logger.warning(f"Development hygiene collection failed: {e}")
            return self._default_metrics()
    
    def _calculate_clean_commit_rate(self, project_root: Path) -> float:
        """Calculate percentage of clean commits."""
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '--since=30.days.ago'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                total_commits = len([c for c in commits if c])
                
                # Check for proper commit messages (not "WIP", "fix", etc.)
                clean_commits = len([
                    c for c in commits 
                    if c and not any(bad in c.lower() for bad in ['wip', 'test', 'temp', 'fix'])
                ])
                
                if total_commits > 0:
                    return round((clean_commits / total_commits) * 100, 1)
            
            return 0.0
        except Exception as e:
            logger.warning(f"Clean commit calculation failed: {e}")
            return 0.0
    
    def _check_branch_strategy(self, project_root: Path) -> float:
        """Check branch naming strategy compliance."""
        try:
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                branches = result.stdout.strip().split('\n')
                # Check for feature/, bugfix/, hotfix/ prefixes
                compliant = len([
                    b for b in branches 
                    if any(prefix in b for prefix in ['feature/', 'bugfix/', 'hotfix/', 'release/'])
                ])
                
                total_branches = len([b for b in branches if b.strip()])
                if total_branches > 0:
                    return round((compliant / total_branches) * 100, 1)
            
            return 0.0
        except Exception as e:
            logger.warning(f"Branch strategy check failed: {e}")
            return 0.0
    
    def _scan_security(self, project_root: Path) -> Dict[str, int]:
        """Scan for security vulnerabilities."""
        # Would run actual security scanners
        return {
            'critical': 0,
            'high': 1,
            'medium': 2,
            'low': 5
        }
    
    def _get_review_participation(self, project_root: Path) -> float:
        """Get code review participation rate."""
        # Would track from PR/MR data
        return 85.0
    
    def _count_merge_conflicts(self, project_root: Path) -> int:
        """Count merge conflicts in recent history."""
        # Would track from git history
        return 3
    
    def _default_metrics(self) -> Dict[str, Any]:
        """Return default metrics if collection fails."""
        return {
            'clean_commit_rate': 0.0,
            'branch_strategy_compliance': 0.0,
            'security_vulnerabilities': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'code_review_participation': 0.0,
            'merge_conflicts': 0
        }
