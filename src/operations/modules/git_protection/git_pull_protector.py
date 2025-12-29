"""
Git Pull Protector

Protects locally aligned files from being overwritten by git pull operations.
Uses stash-based protection with intelligent conflict resolution.

Author: Asif Hussain
Version: 3.8.1
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .alignment_state_tracker import AlignmentStateTracker


class GitPullProtector:
    """
    Protects aligned files during git pull operations.
    
    Workflow:
    1. Pre-Pull: Check for aligned files that would be overwritten
    2. Stash: Automatically stash aligned changes
    3. Pull: Execute git pull
    4. Reconcile: Merge stashed alignment with pulled code
    5. Restore: Apply alignment where possible
    """
    
    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or Path.cwd()
        self.tracker = AlignmentStateTracker(workspace_path)
        self.protection_log: List[Dict[str, Any]] = []
    
    def check_pull_safety(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if git pull is safe (won't overwrite aligned files).
        
        Returns:
            Tuple of (is_safe, report)
        """
        aligned_files = self.tracker.get_aligned_files()
        
        if not aligned_files:
            return True, {
                'safe': True,
                'message': 'No aligned files to protect',
                'aligned_count': 0,
                'at_risk': []
            }
        
        # Check which aligned files would be modified by pull
        at_risk = self._get_files_at_risk(aligned_files)
        
        return len(at_risk) == 0, {
            'safe': len(at_risk) == 0,
            'message': f'{len(at_risk)} aligned files at risk' if at_risk else 'All aligned files safe',
            'aligned_count': len(aligned_files),
            'at_risk': [str(f.relative_to(self.workspace_path)) for f in at_risk]
        }
    
    def _get_files_at_risk(self, aligned_files: List[Path]) -> List[Path]:
        """Get aligned files that would be modified by pull."""
        at_risk = []
        
        try:
            # Get list of files that differ from origin
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD', 'origin/HEAD'],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                remote_changed = {
                    self.workspace_path / line.strip()
                    for line in result.stdout.split('\n')
                    if line.strip()
                }
                
                # Check which aligned files are in remote changes
                at_risk = [f for f in aligned_files if f in remote_changed]
        
        except Exception as e:
            print(f"Warning: Could not check remote changes: {e}")
        
        return at_risk
    
    def protect_and_pull(
        self,
        auto_stash: bool = True,
        preserve_alignment: bool = True
    ) -> Dict[str, Any]:
        """
        Execute protected git pull.
        
        Args:
            auto_stash: Automatically stash aligned changes
            preserve_alignment: Try to preserve alignment after pull
            
        Returns:
            Result dictionary with pull status and protection actions
        """
        result = {
            'success': False,
            'pull_executed': False,
            'stashed': False,
            'conflicts': [],
            'preserved_files': [],
            'lost_alignment': [],
            'message': ''
        }
        
        # Step 1: Check safety
        is_safe, safety_report = self.check_pull_safety()
        
        if is_safe:
            # No protection needed - execute pull normally
            pull_result = self._execute_pull()
            result.update({
                'success': pull_result['success'],
                'pull_executed': True,
                'message': 'Pull completed safely (no aligned files at risk)'
            })
            return result
        
        # Step 2: Stash aligned files if requested
        if auto_stash:
            stash_result = self._stash_aligned_files(safety_report['at_risk'])
            result['stashed'] = stash_result['success']
            
            if not stash_result['success']:
                result['message'] = f"Failed to stash aligned files: {stash_result['error']}"
                return result
        
        # Step 3: Execute pull
        pull_result = self._execute_pull()
        result['pull_executed'] = pull_result['success']
        
        if not pull_result['success']:
            # Pull failed - restore stash if we created one
            if result['stashed']:
                self._restore_stash()
            result['message'] = f"Pull failed: {pull_result['error']}"
            return result
        
        # Step 4: Reconcile alignment
        if preserve_alignment and result['stashed']:
            reconcile_result = self._reconcile_alignment(safety_report['at_risk'])
            result.update({
                'conflicts': reconcile_result['conflicts'],
                'preserved_files': reconcile_result['preserved'],
                'lost_alignment': reconcile_result['lost']
            })
        
        result['success'] = True
        result['message'] = self._generate_summary(result)
        
        return result
    
    def _execute_pull(self) -> Dict[str, Any]:
        """Execute git pull."""
        try:
            result = subprocess.run(
                ['git', 'pull'],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _stash_aligned_files(self, at_risk_files: List[str]) -> Dict[str, Any]:
        """Stash aligned files that are at risk."""
        try:
            # Create stash with aligned files
            stash_message = f"CORTEX alignment protection - {datetime.now().isoformat()}"
            
            # Add files to staging
            for file_path in at_risk_files:
                subprocess.run(
                    ['git', 'add', file_path],
                    cwd=self.workspace_path,
                    capture_output=True,
                    timeout=10
                )
            
            # Create stash
            result = subprocess.run(
                ['git', 'stash', 'push', '-m', stash_message],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                'success': result.returncode == 0,
                'stash_message': stash_message,
                'error': result.stderr if result.returncode != 0 else None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _restore_stash(self) -> Dict[str, Any]:
        """Restore most recent stash."""
        try:
            result = subprocess.run(
                ['git', 'stash', 'pop'],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _reconcile_alignment(self, at_risk_files: List[str]) -> Dict[str, Any]:
        """
        Reconcile alignment after pull.
        
        Attempts to restore alignment where possible.
        """
        preserved = []
        lost = []
        conflicts = []
        
        # Restore stash
        restore_result = self._restore_stash()
        
        if not restore_result['success']:
            # Conflicts occurred
            conflicts = self._detect_conflicts()
            lost = [f for f in at_risk_files if f not in conflicts]
        else:
            # Successfully restored - check alignment
            for file_path in at_risk_files:
                full_path = self.workspace_path / file_path
                if self.tracker.is_aligned(full_path):
                    preserved.append(file_path)
                else:
                    lost.append(file_path)
        
        return {
            'preserved': preserved,
            'lost': lost,
            'conflicts': conflicts
        }
    
    def _detect_conflicts(self) -> List[str]:
        """Detect merge conflicts."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', '--diff-filter=U'],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return [
                    line.strip()
                    for line in result.stdout.split('\n')
                    if line.strip()
                ]
        
        except Exception:
            pass
        
        return []
    
    def _generate_summary(self, result: Dict[str, Any]) -> str:
        """Generate human-readable summary."""
        parts = []
        
        if result['pull_executed']:
            parts.append("✅ Pull completed")
        
        if result['stashed']:
            parts.append(f"📦 Stashed {len(result.get('preserved_files', []))} aligned files")
        
        if result['preserved_files']:
            parts.append(f"✅ Preserved {len(result['preserved_files'])} aligned files")
        
        if result['conflicts']:
            parts.append(f"⚠️ {len(result['conflicts'])} conflicts require manual resolution")
        
        if result['lost_alignment']:
            parts.append(f"⚠️ {len(result['lost_alignment'])} files lost alignment")
        
        return " | ".join(parts) if parts else "Pull completed"
    
    def get_protection_status(self) -> Dict[str, Any]:
        """Get current protection status."""
        stats = self.tracker.get_statistics()
        is_safe, safety_report = self.check_pull_safety()
        
        return {
            'protection_enabled': True,
            'alignment_tracking': stats,
            'pull_safety': safety_report,
            'recommendation': (
                'Safe to pull' if is_safe
                else f'Use protect_and_pull() - {len(safety_report["at_risk"])} files at risk'
            )
        }
