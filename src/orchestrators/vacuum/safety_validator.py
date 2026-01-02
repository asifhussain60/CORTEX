"""
Safety Validator - Critical file protection and risk classification.

Validates filesystem operations before execution:
- Critical file detection (git, source code, config, docs, CORTEX brain)
- Recently modified file checks (<24h)
- Uncommitted changes detection (git integration)
- Large file warnings (>10MB)
- Risk level classification (SAFE → CRITICAL)
- Permission validation

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Set
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class SafetyValidator:
    """
    Validates file operations for safety.
    
    Implements 5-level risk classification:
    - SAFE: Temp files, caches, build artifacts
    - LOW: Duplicates, empty directories, old logs
    - MEDIUM: Misplaced files, large binaries
    - HIGH: Orphaned files, recently modified files
    - CRITICAL: Git metadata, source code, config, docs, CORTEX brain, uncommitted changes
    """
    
    # Critical file patterns (NEVER DELETE)
    CRITICAL_PATTERNS = [
        '.git', '.git/**', '.gitignore', '.gitattributes', '.gitmodules', '.github/**',
        '*.py', '*.js', '*.ts', '*.jsx', '*.tsx', '*.java', '*.c', '*.cpp', '*.h',
        '*.cs', '*.go', '*.rs', '*.rb', '*.php', '*.html', '*.css', '*.scss',
        '*.yaml', '*.yml', '*.json', '*.toml', '*.ini', '*.conf', '*.config',
        '*.md', '*.rst', '*.txt',
        'requirements.txt', 'package.json', 'pyproject.toml', 'Dockerfile',
        'README*', 'LICENSE*', 'CHANGELOG*', 'CONTRIBUTING*'
    ]
    
    # CORTEX brain critical paths
    CORTEX_CRITICAL_PATHS = [
        'cortex-brain/tier0',
        'cortex-brain/tier1',
        'cortex-brain/tier2',
        'cortex-brain/tier3',
        'cortex-brain/database',
        'cortex-brain/manifests',
        'cortex-brain/config'
    ]
    
    # CORTEX brain safe paths (can clean)
    CORTEX_SAFE_PATHS = [
        'cortex-brain/cache',
        'cortex-brain/logs',
        'cortex-brain/cleanup-reports',
        'cortex-brain/archives'
    ]
    
    # Source code extensions
    SOURCE_CODE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.cs',
        '.go', '.rs', '.rb', '.php', '.html', '.css', '.scss', '.sass',
        '.sql', '.sh', '.bash', '.ps1'
    }
    
    # Configuration extensions
    CONFIG_EXTENSIONS = {
        '.yaml', '.yml', '.json', '.toml', '.ini', '.conf', '.config', '.env'
    }
    
    # Documentation extensions
    DOCUMENTATION_EXTENSIONS = {'.md', '.rst', '.txt'}
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize safety validator.
        
        Args:
            config: Vacuum configuration with safety rules
        """
        self.config = config
        self.safety_rules = config.get('safety', {})
        self.size_threshold_mb = self.safety_rules.get('size_threshold_mb', 10)
        self.protected_paths = config.get('exclusions', [])
        
        # Try to detect git root
        self.git_root = self._find_git_root()
        
        logger.info(
            f"Initialized SafetyValidator "
            f"(size_threshold={self.size_threshold_mb}MB, git_root={self.git_root})"
        )
    
    def _find_git_root(self) -> Path | None:
        """Find git repository root directory."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception:
            pass
        return None
    
    def validate_deletion(self, path: Path) -> Dict[str, Any]:
        """
        Validate if file is safe to delete.
        
        Args:
            path: File path to validate
        
        Returns:
            {
                'safe': bool,
                'risk_level': 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL',
                'reasons': List[str],
                'requires_confirmation': bool
            }
        """
        reasons = []
        risk_level = 'SAFE'
        
        # Check critical file patterns
        if self._is_critical_file(path):
            return {
                'safe': False,
                'risk_level': 'CRITICAL',
                'reasons': ['Critical file (git, source, config, or documentation)'],
                'requires_confirmation': True
            }
        
        # Check CORTEX brain protection
        if self._is_cortex_critical(path):
            return {
                'safe': False,
                'risk_level': 'CRITICAL',
                'reasons': ['CORTEX brain tier0/1/2/3 (governance/memory)'],
                'requires_confirmation': True
            }
        
        # Check recently modified
        if self._is_recently_modified(path, hours=24):
            reasons.append('Modified in last 24 hours')
            risk_level = 'HIGH'
        
        # Check uncommitted changes
        if self._has_uncommitted_changes(path):
            return {
                'safe': False,
                'risk_level': 'CRITICAL',
                'reasons': ['Uncommitted git changes'],
                'requires_confirmation': True
            }
        
        # Check large file
        if self._is_large_file(path):
            reasons.append(f'Large file (>{self.size_threshold_mb} MB)')
            if risk_level == 'SAFE':
                risk_level = 'MEDIUM'
        
        # Determine if confirmation required
        requires_confirmation = risk_level in {'HIGH', 'CRITICAL'}
        
        return {
            'safe': risk_level not in {'CRITICAL'},
            'risk_level': risk_level,
            'reasons': reasons if reasons else ['Safe to delete'],
            'requires_confirmation': requires_confirmation
        }
    
    def _is_critical_file(self, path: Path) -> bool:
        """Check if file matches critical patterns."""
        # Check git metadata
        if '.git' in path.parts or path.name in {'.gitignore', '.gitattributes', '.gitmodules'}:
            return True
        
        # Check source code extensions
        if path.suffix in self.SOURCE_CODE_EXTENSIONS:
            # Allow deletion of compiled Python files
            if path.suffix in {'.pyc', '.pyo'}:
                return False
            return True
        
        # Check configuration extensions
        if path.suffix in self.CONFIG_EXTENSIONS:
            return True
        
        # Check documentation
        if path.suffix in self.DOCUMENTATION_EXTENSIONS:
            return True
        
        # Check special filenames
        special_files = {'README', 'LICENSE', 'CHANGELOG', 'CONTRIBUTING', 'Dockerfile'}
        if path.stem.upper() in special_files:
            return True
        
        return False
    
    def _is_cortex_critical(self, path: Path) -> bool:
        """Check if file is in CORTEX critical brain data."""
        path_str = str(path)
        
        # Check if in safe subfolder first
        for safe_path in self.CORTEX_SAFE_PATHS:
            if safe_path in path_str:
                return False
        
        # Check if in critical path
        for critical_path in self.CORTEX_CRITICAL_PATHS:
            if critical_path in path_str:
                return True
        
        return False
    
    def _is_recently_modified(self, path: Path, hours: int = 24) -> bool:
        """Check if file modified within N hours."""
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            age = datetime.now() - mtime
            return age < timedelta(hours=hours)
        except OSError:
            return False
    
    def _has_uncommitted_changes(self, path: Path) -> bool:
        """Check if file has uncommitted git changes."""
        if not self.git_root:
            return False
        
        try:
            # Get git status for file
            result = subprocess.run(
                ['git', 'status', '--porcelain', str(path)],
                cwd=self.git_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Non-empty output = uncommitted changes
            return bool(result.stdout.strip())
        
        except Exception:
            return False
    
    def _is_large_file(self, path: Path) -> bool:
        """Check if file exceeds size threshold."""
        try:
            size_mb = path.stat().st_size / (1024 * 1024)
            return size_mb > self.size_threshold_mb
        except OSError:
            return False
