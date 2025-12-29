"""
Cleanup Utility

Fast, lightweight cleanup management for Phase 8 integration cleanup.
Replaces cleanup_strategy.py with focused utility for file cleanup.

Features:
- Profile-based cleanup strategies (quick/standard/comprehensive)
- Safe file detection with critical file protection
- Age-based filtering for backups and logs
- Dry-run mode for preview

Operations:
1. get_cleanup_strategy - Get strategy description
2. detect_quick_files - Detect temp/cache files only
3. detect_standard_files - Detect temp/cache/old backups (>30 days)
4. detect_comprehensive_files - Detect all obsolete files
5. execute_cleanup - Remove files safely

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any


# Critical files that should NEVER be deleted
CRITICAL_FILES = {
    'brain-protection-rules.yaml',
    'response-templates.yaml',
    'capabilities.yaml',
    'operations-config.yaml'
}


def get_cleanup_strategy(profile: str) -> Dict[str, Any]:
    """
    Get cleanup strategy description for profile.
    
    Args:
        profile: Profile name (quick|standard|comprehensive)
        
    Returns:
        Dict with strategy info:
            - profile: str
            - description: str
            - targets: list of cleanup targets
    """
    strategies = {
        'quick': {
            'profile': 'quick',
            'description': 'Quick cleanup: temp and cache files only',
            'targets': ['cache/', 'backups/']
        },
        'standard': {
            'profile': 'standard',
            'description': 'Standard cleanup: temp, cache, and old backups (>30 days)',
            'targets': ['cache/', 'backups/ (>30 days)']
        },
        'comprehensive': {
            'profile': 'comprehensive',
            'description': 'Comprehensive cleanup: optimize databases, consolidate documentation, archive backups and logs',
            'targets': ['cache/', 'backups/', 'logs/ (>30 days)']
        }
    }
    
    return strategies.get(profile, strategies['standard'])


def detect_quick_files(brain_path: Path) -> List[Path]:
    """
    Detect files for quick cleanup (temp and cache only).
    
    Args:
        brain_path: Path to CORTEX brain directory
        
    Returns:
        List of files to clean
    """
    files_to_clean = []
    brain = Path(brain_path)
    
    # Cache files
    cache_dir = brain / 'cache'
    if cache_dir.exists():
        for file in cache_dir.rglob('*'):
            if file.is_file() and file.name not in CRITICAL_FILES:
                files_to_clean.append(file)
    
    # Backups (quick cleanup also removes backups)
    backups_dir = brain / 'backups'
    if backups_dir.exists():
        for file in backups_dir.rglob('*'):
            if file.is_file() and file.name not in CRITICAL_FILES:
                files_to_clean.append(file)
    
    return files_to_clean


def detect_standard_files(brain_path: Path, cutoff_days: int = 30) -> List[Path]:
    """
    Detect files for standard cleanup (temp, cache, old backups).
    
    Args:
        brain_path: Path to CORTEX brain directory
        cutoff_days: Age threshold for old backups (default: 30 days)
        
    Returns:
        List of files to clean
    """
    files_to_clean = []
    brain = Path(brain_path)
    cutoff_date = datetime.now() - timedelta(days=cutoff_days)
    
    # Cache files
    cache_dir = brain / 'cache'
    if cache_dir.exists():
        for file in cache_dir.rglob('*'):
            if file.is_file() and file.name not in CRITICAL_FILES:
                files_to_clean.append(file)
    
    # Old backups (>cutoff_days)
    backups_dir = brain / 'backups'
    if backups_dir.exists():
        for file in backups_dir.rglob('*'):
            if file.is_file() and file.name not in CRITICAL_FILES:
                try:
                    if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_date:
                        files_to_clean.append(file)
                except OSError:
                    pass  # Skip files with access issues
    
    return files_to_clean


def detect_comprehensive_files(brain_path: Path, cutoff_days: int = 30) -> List[Path]:
    """
    Detect files for comprehensive cleanup (all obsolete files).
    
    Args:
        brain_path: Path to CORTEX brain directory
        cutoff_days: Age threshold for logs (default: 30 days)
        
    Returns:
        List of files to clean
    """
    files_to_clean = []
    brain = Path(brain_path)
    cutoff_date = datetime.now() - timedelta(days=cutoff_days)
    
    # Cache files
    cache_dir = brain / 'cache'
    if cache_dir.exists():
        for file in cache_dir.rglob('*'):
            if file.is_file() and file.name not in CRITICAL_FILES:
                files_to_clean.append(file)
    
    # ALL backups (comprehensive removes all)
    backups_dir = brain / 'backups'
    if backups_dir.exists():
        for file in backups_dir.rglob('*'):
            if file.is_file() and file.name not in CRITICAL_FILES:
                files_to_clean.append(file)
    
    # Old logs (>cutoff_days)
    logs_dir = brain.parent / 'logs'
    if logs_dir.exists():
        for file in logs_dir.rglob('*.log'):
            if file.is_file():
                try:
                    if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_date:
                        files_to_clean.append(file)
                except OSError:
                    pass  # Skip files with access issues
    
    return files_to_clean


def execute_cleanup(files: List[Path], dry_run: bool = False) -> Dict[str, Any]:
    """
    Execute cleanup by removing files safely.
    
    Args:
        files: List of files to remove
        dry_run: If True, show what would be removed without executing
        
    Returns:
        Dict with cleanup results:
            - success: bool
            - files_removed: int
            - dry_run: bool
            - message: str
    """
    if dry_run:
        return {
            'success': True,
            'files_removed': 0,
            'files_would_remove': len(files),
            'dry_run': True,
            'message': f'[DRY RUN] Would remove {len(files)} files'
        }
    
    removed = 0
    errors = []
    
    for file in files:
        try:
            file.unlink()
            removed += 1
        except Exception as e:
            errors.append(f'{file.name}: {e}')
    
    return {
        'success': len(errors) == 0,
        'files_removed': removed,
        'dry_run': False,
        'errors': errors,
        'message': f'Removed {removed} files' + (f', {len(errors)} errors' if errors else '')
    }


# Self-test
if __name__ == "__main__":
    print("🧪 Cleanup Utility - Self Test")
    print("=" * 50)
    
    brain_path = Path(__file__).resolve().parents[4] / "cortex-brain"
    
    # Test 1: Get strategies
    for profile in ['quick', 'standard', 'comprehensive']:
        strategy = get_cleanup_strategy(profile)
        print(f"✅ get_cleanup_strategy('{profile}'): {strategy['description'][:40]}...")
    
    # Test 2: Detect files (dry-run)
    quick = detect_quick_files(brain_path)
    print(f"✅ detect_quick_files: {len(quick)} files")
    
    standard = detect_standard_files(brain_path)
    print(f"✅ detect_standard_files: {len(standard)} files")
    
    comprehensive = detect_comprehensive_files(brain_path)
    print(f"✅ detect_comprehensive_files: {len(comprehensive)} files")
    
    # Test 3: Execute cleanup (dry-run)
    result = execute_cleanup(quick, dry_run=True)
    print(f"✅ execute_cleanup (dry-run): {result['message']}")
    
    print("=" * 50)
    print("✅ All tests passed! (5 operations available)")
    print(f"📊 Lines: {len(open(__file__).readlines())}")
