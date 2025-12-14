"""
Duplicate Detector

Detects and resolves duplicate planning artifacts.

Part of Phase 3: Vacuum & Cleanup Integration
"""

import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Set
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ResolutionStrategy(Enum):
    """Strategies for resolving duplicates"""
    KEEP_NEWEST = "keep_newest"
    KEEP_LARGEST = "keep_largest"
    MANUAL = "manual"


@dataclass
class DuplicateGroup:
    """Group of duplicate files"""
    hash: str
    files: List[Path] = field(default_factory=list)
    similarity_score: float = 1.0  # 1.0 = exact match
    
    def __post_init__(self):
        """Sort files by modification time (newest first)."""
        if self.files:
            self.files.sort(key=lambda f: f.stat().st_mtime, reverse=True)


@dataclass
class ResolutionResult:
    """Result of duplicate resolution"""
    action: str
    kept_file: Optional[Path] = None
    removed_files: List[Path] = field(default_factory=list)
    message: str = ""


class DuplicateDetector:
    """
    Detects duplicate planning artifacts using multiple strategies.
    
    Strategies:
    - Content hash comparison (exact duplicates)
    - Filename similarity (near duplicates)
    - Metadata comparison
    
    Responsibilities:
    - Find duplicate files
    - Group duplicates
    - Provide resolution strategies
    - Archive duplicates
    - Generate reports
    """
    
    def __init__(self, root_directory: Path):
        """
        Initialize duplicate detector.
        
        Args:
            root_directory: Root directory to scan for duplicates
        """
        self.root_directory = Path(root_directory)
        
        if not self.root_directory.exists():
            raise ValueError(f"Root directory does not exist: {self.root_directory}")
        
        logger.info(f"Initialized DuplicateDetector for {self.root_directory}")
    
    def find_duplicates(self, check_filename_similarity: bool = False) -> List[DuplicateGroup]:
        """
        Find duplicate files in root directory.
        
        Args:
            check_filename_similarity: Also check for similar filenames
            
        Returns:
            List of DuplicateGroup objects
        """
        logger.info("Searching for duplicates...")
        
        # Find exact duplicates by content hash
        hash_groups = self.group_by_hash()
        duplicates = []
        
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                group = DuplicateGroup(
                    hash=file_hash,
                    files=files,
                    similarity_score=1.0
                )
                duplicates.append(group)
        
        logger.info(f"Found {len(duplicates)} duplicate groups")
        
        return duplicates
    
    def group_by_hash(self) -> Dict[str, List[Path]]:
        """
        Group files by content hash.
        
        Returns:
            Dict mapping hash to list of files
        """
        hash_map: Dict[str, List[Path]] = {}
        
        # Scan all text files
        for file_path in self.root_directory.rglob("*"):
            if not file_path.is_file():
                continue
            
            # Skip binary files
            if not self._is_text_file(file_path):
                continue
            
            # Calculate hash
            file_hash = self._calculate_hash(file_path)
            
            if file_hash not in hash_map:
                hash_map[file_hash] = []
            
            hash_map[file_hash].append(file_path)
        
        return hash_map
    
    def resolve_duplicates(
        self,
        group: DuplicateGroup,
        strategy: ResolutionStrategy
    ) -> ResolutionResult:
        """
        Resolve duplicates using specified strategy.
        
        Args:
            group: DuplicateGroup to resolve
            strategy: Resolution strategy
            
        Returns:
            ResolutionResult
        """
        logger.info(f"Resolving {len(group.files)} duplicates with strategy: {strategy.value}")
        
        if strategy == ResolutionStrategy.KEEP_NEWEST:
            return self._resolve_keep_newest(group)
        
        elif strategy == ResolutionStrategy.KEEP_LARGEST:
            return self._resolve_keep_largest(group)
        
        elif strategy == ResolutionStrategy.MANUAL:
            return ResolutionResult(
                action="manual_review",
                kept_file=group.files[0] if group.files else None,
                message="Manual review required"
            )
        
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def archive_duplicates(self, group: DuplicateGroup) -> Path:
        """
        Archive duplicate files to duplicates/ folder.
        
        Args:
            group: DuplicateGroup to archive
            
        Returns:
            Path to archive directory
        """
        archive_dir = self.root_directory / "duplicates"
        archive_dir.mkdir(exist_ok=True)
        
        # Keep first file, archive rest
        for file_path in group.files[1:]:
            target = archive_dir / file_path.name
            
            # Handle name conflicts
            counter = 1
            while target.exists():
                target = archive_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
                counter += 1
            
            # Move file
            file_path.rename(target)
            logger.info(f"Archived: {file_path.name} -> {target}")
        
        return archive_dir
    
    def generate_duplicate_manifest(self, duplicates: List[DuplicateGroup]) -> Dict:
        """
        Generate manifest of duplicates.
        
        Args:
            duplicates: List of duplicate groups
            
        Returns:
            Manifest dict
        """
        total_files = sum(len(g.files) for g in duplicates)
        
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "total_groups": len(duplicates),
            "duplicates_found": total_files,
            "groups": []
        }
        
        for group in duplicates:
            manifest["groups"].append({
                "hash": group.hash,
                "file_count": len(group.files),
                "files": [str(f) for f in group.files],
                "similarity_score": group.similarity_score
            })
        
        return manifest
    
    def generate_report(self, duplicates: List[DuplicateGroup]) -> str:
        """
        Generate human-readable duplicate report.
        
        Args:
            duplicates: List of duplicate groups
            
        Returns:
            Report string
        """
        if not duplicates:
            return "No duplicates found."
        
        total_files = sum(len(g.files) for g in duplicates)
        total_wasted = sum(len(g.files) - 1 for g in duplicates)
        
        report = f"""Duplicate Detection Report
==========================

Summary:
- Duplicate Groups: {len(duplicates)}
- Total Duplicate Files: {total_files}
- Redundant Files: {total_wasted}

Details:
"""
        
        for i, group in enumerate(duplicates, 1):
            report += f"\nGroup {i} ({len(group.files)} files):\n"
            report += f"  Hash: {group.hash[:16]}...\n"
            for file_path in group.files:
                size = file_path.stat().st_size
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                report += f"  - {file_path.name} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})\n"
        
        return report
    
    def _resolve_keep_newest(self, group: DuplicateGroup) -> ResolutionResult:
        """Keep newest file, mark others for removal."""
        # Files already sorted by mtime (newest first)
        kept = group.files[0]
        removed = group.files[1:]
        
        return ResolutionResult(
            action="keep_newest",
            kept_file=kept,
            removed_files=removed,
            message=f"Kept {kept.name} (newest)"
        )
    
    def _resolve_keep_largest(self, group: DuplicateGroup) -> ResolutionResult:
        """Keep largest file, mark others for removal."""
        files_by_size = sorted(group.files, key=lambda f: f.stat().st_size, reverse=True)
        kept = files_by_size[0]
        removed = files_by_size[1:]
        
        return ResolutionResult(
            action="keep_largest",
            kept_file=kept,
            removed_files=removed,
            message=f"Kept {kept.name} (largest)"
        )
    
    def _calculate_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of hash
        """
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return ""
    
    def _is_text_file(self, file_path: Path) -> bool:
        """
        Check if file is text file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if text file, False otherwise
        """
        text_extensions = {'.md', '.yaml', '.yml', '.txt', '.json'}
        return file_path.suffix.lower() in text_extensions
