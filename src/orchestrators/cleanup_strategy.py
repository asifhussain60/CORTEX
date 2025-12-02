"""
Cleanup Strategy Pattern for Phase 8 Integration Cleanup

Provides profile-specific cleanup strategies:
- QuickCleanupStrategy: Fast cleanup (temp/cache)
- StandardCleanupStrategy: Balanced cleanup (temp/cache/old backups)
- ComprehensiveCleanupStrategy: Deep cleanup (all obsolete files)

Author: Asif Hussain
Date: December 2, 2025
"""

from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from datetime import datetime, timedelta


class CleanupStrategy(ABC):
    """Base class for cleanup strategies."""
    
    def __init__(self, brain_path: Path):
        """
        Initialize cleanup strategy.
        
        Args:
            brain_path: Path to CORTEX brain directory
        """
        self.brain_path = Path(brain_path)
        self.critical_files = {
            'brain-protection-rules.yaml',
            'response-templates.yaml',
            'capabilities.yaml',
            'operations-config.yaml'
        }
    
    @abstractmethod
    def detect_files(self) -> List[Path]:
        """
        Detect files to clean based on strategy.
        
        Returns:
            List of files to clean
        """
        pass
    
    @abstractmethod
    def get_profile_name(self) -> str:
        """Get human-readable profile name."""
        pass


class QuickCleanupStrategy(CleanupStrategy):
    """Quick cleanup: temp and cache files only."""
    
    def detect_files(self) -> List[Path]:
        """Detect temp and cache files."""
        files_to_clean = []
        
        # Cache files
        cache_dir = self.brain_path / 'cache'
        if cache_dir.exists():
            for file in cache_dir.rglob('*'):
                if file.is_file() and file.name not in self.critical_files:
                    files_to_clean.append(file)
        
        # Backups (quick cleanup also removes backups)
        backups_dir = self.brain_path / 'backups'
        if backups_dir.exists():
            for file in backups_dir.rglob('*'):
                if file.is_file() and file.name not in self.critical_files:
                    files_to_clean.append(file)
        
        return files_to_clean
    
    def get_profile_name(self) -> str:
        """Get profile name."""
        return 'Quick cleanup: temp and cache files only'


class StandardCleanupStrategy(CleanupStrategy):
    """Standard cleanup: temp, cache, and old backups (>30 days)."""
    
    def detect_files(self) -> List[Path]:
        """Detect temp, cache, and old backup files."""
        files_to_clean = []
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # Cache files
        cache_dir = self.brain_path / 'cache'
        if cache_dir.exists():
            for file in cache_dir.rglob('*'):
                if file.is_file() and file.name not in self.critical_files:
                    files_to_clean.append(file)
        
        # Old backups (>30 days)
        backups_dir = self.brain_path / 'backups'
        if backups_dir.exists():
            for file in backups_dir.rglob('*'):
                if file.is_file() and file.name not in self.critical_files:
                    try:
                        if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_date:
                            files_to_clean.append(file)
                    except OSError:
                        pass
        
        return files_to_clean
    
    def get_profile_name(self) -> str:
        """Get profile name."""
        return 'Standard cleanup: temp, cache, and old backups (>30 days)'


class ComprehensiveCleanupStrategy(CleanupStrategy):
    """Comprehensive cleanup: optimize, consolidate, archive everything."""
    
    def detect_files(self) -> List[Path]:
        """Detect all obsolete files."""
        files_to_clean = []
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # Cache files
        cache_dir = self.brain_path / 'cache'
        if cache_dir.exists():
            for file in cache_dir.rglob('*'):
                if file.is_file() and file.name not in self.critical_files:
                    files_to_clean.append(file)
        
        # ALL backups (comprehensive removes all)
        backups_dir = self.brain_path / 'backups'
        if backups_dir.exists():
            for file in backups_dir.rglob('*'):
                if file.is_file() and file.name not in self.critical_files:
                    files_to_clean.append(file)
        
        # Old logs (>30 days)
        logs_dir = self.brain_path.parent / 'logs'
        if logs_dir.exists():
            for file in logs_dir.rglob('*.log'):
                if file.is_file():
                    try:
                        if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_date:
                            files_to_clean.append(file)
                    except OSError:
                        pass
        
        return files_to_clean
    
    def get_profile_name(self) -> str:
        """Get profile name."""
        return 'Comprehensive cleanup: optimize databases, consolidate documentation, archive backups and logs'


def get_cleanup_strategy(profile: str, brain_path: Path) -> CleanupStrategy:
    """
    Factory function to get appropriate cleanup strategy.
    
    Args:
        profile: Profile name (quick|standard|comprehensive)
        brain_path: Path to CORTEX brain directory
    
    Returns:
        Appropriate CleanupStrategy instance
    """
    strategies = {
        'quick': QuickCleanupStrategy,
        'standard': StandardCleanupStrategy,
        'comprehensive': ComprehensiveCleanupStrategy
    }
    
    strategy_class = strategies.get(profile, StandardCleanupStrategy)
    return strategy_class(brain_path)
