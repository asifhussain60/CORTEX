"""
Duplicate Detector - Three-phase duplicate file detection.

Implements progressive duplicate detection to minimize hash computation:
1. Phase 1 (Size): Group files by size
2. Phase 2 (Quick Hash): Hash first 8KB for same-size files
3. Phase 3 (Full Hash): Full SHA256 for quick-hash matches

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict


logger = logging.getLogger(__name__)


class DuplicateDetector:
    """
    Detects duplicate files using three-phase progressive hashing.
    
    Algorithm:
    1. Size grouping: Only compare files with identical sizes
    2. Quick hash: Hash first 8KB for size matches
    3. Full hash: SHA256 full file for quick-hash matches
    
    This minimizes expensive hash operations on large files.
    """
    
    QUICK_HASH_BYTES = 8192  # 8 KB for quick hash
    HASH_CHUNK_SIZE = 65536  # 64 KB for full hash
    
    def __init__(self, min_file_size: int = 1024):
        """
        Initialize duplicate detector.
        
        Args:
            min_file_size: Minimum file size to check (bytes, default 1KB)
        """
        self.min_file_size = min_file_size
        self.stats = {
            'files_scanned': 0,
            'size_groups': 0,
            'quick_hash_computed': 0,
            'full_hash_computed': 0,
            'duplicates_found': 0
        }
        logger.info(f"Initialized DuplicateDetector (min_size={min_file_size} bytes)")
    
    def find_duplicates(self, file_paths: List[Path]) -> Dict[str, Any]:
        """
        Find duplicate files in the given list.
        
        Args:
            file_paths: List of file paths to check
        
        Returns:
            {
                'duplicate_groups': List[List[Path]],  # Each group is duplicate files
                'total_duplicates': int,
                'space_wasted': int,  # Bytes wasted on duplicates
                'stats': Dict[str, int]
            }
        """
        self.stats['files_scanned'] = len(file_paths)
        logger.info(f"Starting duplicate detection on {len(file_paths)} files")
        
        # Phase 1: Group by size
        size_groups = self._group_by_size(file_paths)
        self.stats['size_groups'] = len(size_groups)
        logger.debug(f"Phase 1: {len(size_groups)} size groups")
        
        # Phase 2: Quick hash for size matches
        quick_hash_groups = self._quick_hash_groups(size_groups)
        logger.debug(f"Phase 2: {self.stats['quick_hash_computed']} quick hashes computed")
        
        # Phase 3: Full hash for quick-hash matches
        duplicate_groups = self._full_hash_groups(quick_hash_groups)
        self.stats['duplicates_found'] = len(duplicate_groups)
        logger.info(f"Phase 3: {len(duplicate_groups)} duplicate groups found")
        
        # Calculate space wasted
        space_wasted = self._calculate_space_wasted(duplicate_groups)
        
        return {
            'duplicate_groups': duplicate_groups,
            'total_duplicates': sum(len(group) - 1 for group in duplicate_groups),
            'space_wasted': space_wasted,
            'stats': self.stats.copy()
        }
    
    def _group_by_size(self, file_paths: List[Path]) -> Dict[int, List[Path]]:
        """
        Phase 1: Group files by size.
        
        Args:
            file_paths: Files to group
        
        Returns:
            Dictionary mapping size → list of files
        """
        size_groups = defaultdict(list)
        
        for path in file_paths:
            try:
                size = path.stat().st_size
                
                # Skip small files
                if size < self.min_file_size:
                    continue
                
                size_groups[size].append(path)
            
            except OSError as e:
                logger.warning(f"Cannot stat {path}: {e}")
                continue
        
        # Only keep groups with 2+ files (potential duplicates)
        return {size: paths for size, paths in size_groups.items() if len(paths) > 1}
    
    def _quick_hash_groups(self, size_groups: Dict[int, List[Path]]) -> Dict[str, List[Path]]:
        """
        Phase 2: Compute quick hash (first 8KB) for size-matched files.
        
        Args:
            size_groups: Files grouped by size
        
        Returns:
            Dictionary mapping quick_hash → list of files
        """
        quick_hash_groups = defaultdict(list)
        
        for size, paths in size_groups.items():
            for path in paths:
                try:
                    quick_hash = self._compute_quick_hash(path)
                    self.stats['quick_hash_computed'] += 1
                    quick_hash_groups[quick_hash].append(path)
                
                except OSError as e:
                    logger.warning(f"Cannot hash {path}: {e}")
                    continue
        
        # Only keep groups with 2+ files
        return {qhash: paths for qhash, paths in quick_hash_groups.items() if len(paths) > 1}
    
    def _full_hash_groups(self, quick_hash_groups: Dict[str, List[Path]]) -> List[List[Path]]:
        """
        Phase 3: Compute full SHA256 hash for quick-hash matches.
        
        Args:
            quick_hash_groups: Files grouped by quick hash
        
        Returns:
            List of duplicate file groups
        """
        duplicate_groups = []
        
        for quick_hash, paths in quick_hash_groups.items():
            # Compute full hash for each file
            full_hash_map = defaultdict(list)
            
            for path in paths:
                try:
                    full_hash = self._compute_full_hash(path)
                    self.stats['full_hash_computed'] += 1
                    full_hash_map[full_hash].append(path)
                
                except OSError as e:
                    logger.warning(f"Cannot hash {path}: {e}")
                    continue
            
            # Add groups with 2+ files
            for full_hash, dup_paths in full_hash_map.items():
                if len(dup_paths) > 1:
                    duplicate_groups.append(dup_paths)
        
        return duplicate_groups
    
    def _compute_quick_hash(self, path: Path) -> str:
        """
        Compute quick hash (first 8KB of file).
        
        Args:
            path: File to hash
        
        Returns:
            SHA256 hex digest of first 8KB
        """
        hasher = hashlib.sha256()
        
        with path.open('rb') as f:
            chunk = f.read(self.QUICK_HASH_BYTES)
            hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _compute_full_hash(self, path: Path) -> str:
        """
        Compute full SHA256 hash of file.
        
        Args:
            path: File to hash
        
        Returns:
            SHA256 hex digest of entire file
        """
        hasher = hashlib.sha256()
        
        with path.open('rb') as f:
            while True:
                chunk = f.read(self.HASH_CHUNK_SIZE)
                if not chunk:
                    break
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _calculate_space_wasted(self, duplicate_groups: List[List[Path]]) -> int:
        """
        Calculate total space wasted on duplicates.
        
        Args:
            duplicate_groups: List of duplicate file groups
        
        Returns:
            Total bytes wasted (sum of duplicate file sizes)
        """
        total_wasted = 0
        
        for group in duplicate_groups:
            try:
                # Keep one copy, count others as wasted
                file_size = group[0].stat().st_size
                num_duplicates = len(group) - 1
                total_wasted += file_size * num_duplicates
            
            except OSError:
                continue
        
        return total_wasted
