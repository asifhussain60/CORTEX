"""
Design Sync Helpers

Helper functions for design sync orchestrator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
import subprocess
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from src.operations.modules.design_sync.design_sync_models import (
    ImplementationState,
    DesignState,
    GapAnalysis,
    SyncMetrics
)

logger = logging.getLogger(__name__)


class RecentUpdatesGenerator:
    """
    Generates recent updates list from git commit history.
    
    Parses git log for the last N days and extracts meaningful updates
    to auto-generate the "Recent Updates" section in status documents.
    """
    
    def __init__(self, format_commit_callback: callable):
        """
        Initialize RecentUpdatesGenerator.
        
        Args:
            format_commit_callback: Function to format commit messages as updates
        """
        self.format_commit = format_commit_callback
    
    def generate(self, project_root: Path, lookback_days: int = 1) -> List[str]:
        """
        Generate recent updates list from git history.
        
        Args:
            project_root: Project root directory
            lookback_days: Number of days to look back in git history
            
        Returns:
            List of update strings with emoji prefixes
        """
        updates = []
        
        try:
            # Get commits from last N days
            since_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
            
            result = subprocess.run(
                ['git', 'log', f'--since={since_date}', '--oneline', '--no-merges'],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse commit messages
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                # Extract commit message (after hash)
                parts = line.split(' ', 1)
                if len(parts) < 2:
                    continue
                
                commit_msg = parts[1].strip()
                
                # Skip internal/noise commits
                if any(skip in commit_msg.lower() for skip in ['wip', 'temp', 'fixup', 'test commit']):
                    continue
                
                # Categorize and format update
                update = self.format_commit(commit_msg, project_root)
                if update and update not in updates:  # Deduplicate
                    updates.append(update)
            
            # Limit to most recent 10 updates
            return updates[:10]
        
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not parse git history: {e}")
            return []
        except Exception as e:
            logger.warning(f"Error generating recent updates: {e}")
            return []


class CommitReporter:
    """
    Commits design sync changes and generates comprehensive report.
    """
    
    def commit_and_report(
        self,
        impl_state: ImplementationState,
        design_state: DesignState,
        gaps: GapAnalysis,
        optimizations: Dict[str, Any],
        transformations: Dict[str, Any],
        project_root: Path,
        metrics: SyncMetrics,
        profile: str
    ) -> Dict[str, Any]:
        """
        Commit changes and generate comprehensive report.
        
        Returns:
            Dict with final report data
        """
        report = {
            'sync_id': metrics.sync_id,
            'timestamp': metrics.timestamp.isoformat(),
            'profile': profile,
            'implementation_state': {
                'total_modules': impl_state.total_modules,
                'implemented_modules': impl_state.implemented_modules,
                'completion_percentage': impl_state.completion_percentage,
                'total_tests': sum(impl_state.tests.values()),
                'plugins': len(impl_state.plugins),
                'agents': len(impl_state.agents)
            },
            'design_state': {
                'version': design_state.version,
                'design_files': len(design_state.design_files),
                'status_files': len(design_state.status_files),
                'yaml_documents': len(design_state.yaml_documents)
            },
            'gaps_analyzed': metrics.gaps_analyzed,
            'optimizations_integrated': metrics.optimizations_integrated,
            'transformations': {
                'status_files_consolidated': metrics.status_files_consolidated,
                'md_to_yaml_converted': metrics.md_to_yaml_converted
            },
            'git_commits': metrics.git_commits,
            'duration_seconds': metrics.duration_seconds,
            'next_actions': []
        }
        
        # Git commit if changes made
        if profile != 'quick':
            try:
                # Add changed files
                subprocess.run(
                    ['git', 'add', 'cortex-brain/'],
                    cwd=project_root,
                    check=True,
                    capture_output=True
                )
                
                # Commit
                commit_msg = (
                    f"design: synchronize CORTEX {design_state.version} design with implementation\n\n"
                    f"Profile: {profile}\n"
                    f"Gaps analyzed: {metrics.gaps_analyzed}\n"
                    f"Status files consolidated: {metrics.status_files_consolidated}\n"
                    f"MD to YAML converted: {metrics.md_to_yaml_converted}\n"
                    f"Optimizations integrated: {metrics.optimizations_integrated}\n\n"
                    f"[design_sync {metrics.sync_id}]"
                )
                
                result = subprocess.run(
                    ['git', 'commit', '-m', commit_msg],
                    cwd=project_root,
                    check=False,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Get commit hash
                    hash_result = subprocess.run(
                        ['git', 'rev-parse', 'HEAD'],
                        cwd=project_root,
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    commit_hash = hash_result.stdout.strip()[:8]
                    metrics.git_commits.append(commit_hash)
                    logger.info(f"  ✅ Git commit: {commit_hash}")
                else:
                    logger.info("  ℹ️  No changes to commit")
            
            except subprocess.CalledProcessError as e:
                logger.warning(f"Git commit failed: {e}")
        
        # Generate next actions
        if gaps.inconsistent_counts:
            report['next_actions'].append("Review inconsistent module counts in operations")
        
        if gaps.verbose_md_candidates and profile != 'comprehensive':
            report['next_actions'].append(
                f"Run comprehensive profile to convert {len(gaps.verbose_md_candidates)} verbose MD to YAML"
            )
        
        if metrics.optimizations_integrated > 0:
            report['next_actions'].append("Review and implement integrated optimizations")
        
        return report
