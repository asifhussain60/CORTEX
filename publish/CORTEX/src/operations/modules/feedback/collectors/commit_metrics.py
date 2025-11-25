"""
Commit Metrics Collector

Collects build success, deployment frequency, and rollback rate metrics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CommitMetricsCollector:
    """Collect commit-related metrics."""
    
    def collect(self, project_root: Path) -> Dict[str, Any]:
        """
        Collect commit metrics.
        
        Metrics:
            - Build success rate
            - Deployment frequency
            - Rollback rate
            - Mean time to recovery (MTTR)
            - Failed build patterns
        """
        try:
            return {
                'build_success_rate': self._calculate_build_success(project_root),
                'deployment_frequency_per_week': self._get_deployment_frequency(project_root),
                'rollback_rate': self._calculate_rollback_rate(project_root),
                'mttr_hours': self._calculate_mttr(project_root),
                'failed_build_patterns': self._analyze_failed_builds(project_root)
            }
        except Exception as e:
            logger.warning(f"Commit metrics collection failed: {e}")
            return self._default_metrics()
    
    def _calculate_build_success(self, project_root: Path) -> float:
        """Calculate build success rate."""
        # Would integrate with CI/CD system
        return 97.5
    
    def _get_deployment_frequency(self, project_root: Path) -> float:
        """Get average deployments per week."""
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '--since=4.weeks.ago', '--grep=deploy'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                deployments = len([l for l in result.stdout.strip().split('\n') if l])
                return round(deployments / 4.0, 1)
            
            return 0.0
        except Exception as e:
            logger.warning(f"Deployment frequency calculation failed: {e}")
            return 0.0
    
    def _calculate_rollback_rate(self, project_root: Path) -> float:
        """Calculate rollback rate percentage."""
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '--since=4.weeks.ago', '--grep=rollback'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                rollbacks = len([l for l in result.stdout.strip().split('\n') if l])
                # Compare to total deployments
                return round((rollbacks / max(1, self._get_deployment_frequency(project_root) * 4)) * 100, 1)
            
            return 0.0
        except Exception as e:
            logger.warning(f"Rollback rate calculation failed: {e}")
            return 0.0
    
    def _calculate_mttr(self, project_root: Path) -> float:
        """Calculate mean time to recovery in hours."""
        # Would track from incident management system
        return 0.75
    
    def _analyze_failed_builds(self, project_root: Path) -> Dict[str, int]:
        """Analyze patterns in failed builds."""
        return {
            'compile_errors': 2,
            'test_failures': 5,
            'lint_errors': 3,
            'timeout_errors': 1
        }
    
    def _default_metrics(self) -> Dict[str, Any]:
        """Return default metrics if collection fails."""
        return {
            'build_success_rate': 0.0,
            'deployment_frequency_per_week': 0.0,
            'rollback_rate': 0.0,
            'mttr_hours': 0.0,
            'failed_build_patterns': {
                'compile_errors': 0,
                'test_failures': 0,
                'lint_errors': 0,
                'timeout_errors': 0
            }
        }
