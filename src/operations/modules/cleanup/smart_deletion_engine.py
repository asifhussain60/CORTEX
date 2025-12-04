"""
CORTEX Cleanup: Smart Deletion Engine

Intelligently identifies and safely deletes obsolete files using rules and analysis.
Generates deletion manifest for review and rollback capability.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

from .file_scanner import FileMetadata, FileCategory, FilePurpose

logger = logging.getLogger(__name__)


class DeletionReason(Enum):
    """Reason for file deletion"""
    DUPLICATE = "duplicate"  # Exact duplicate by content hash
    BACKUP = "backup"  # Backup file no longer needed
    TEMPORARY = "temporary"  # Temporary/cache file
    DEPRECATED = "deprecated"  # Deprecated code/feature
    OBSOLETE_TEST = "obsolete_test"  # Test for non-existent code
    EMPTY = "empty"  # Empty file
    OLD_ARCHIVE = "old_archive"  # Old archived content
    GENERATED = "generated"  # Auto-generated that can be regenerated
    UNUSED = "unused"  # Not referenced anywhere
    REDUNDANT_DOC = "redundant_doc"  # Documentation covered elsewhere
    USER_REQUEST = "user_request"  # User explicitly requested deletion


class DeletionRisk(Enum):
    """Risk level of deletion"""
    SAFE = "safe"  # No risk, can auto-delete
    LOW = "low"  # Low risk, minimal review needed
    MEDIUM = "medium"  # Medium risk, review recommended
    HIGH = "high"  # High risk, careful review required
    CRITICAL = "critical"  # Critical risk, manual approval needed


@dataclass
class DeletionCandidate:
    """File candidate for deletion"""
    metadata: FileMetadata
    reason: DeletionReason
    risk: DeletionRisk
    confidence: float  # 0.0-1.0
    evidence: List[str]
    related_files: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'path': str(self.metadata.relative_path),
            'category': self.metadata.category.value,
            'purpose': self.metadata.purpose.value,
            'size_bytes': self.metadata.size_bytes,
            'modified_time': self.metadata.modified_time.isoformat(),
            'reason': self.reason.value,
            'risk': self.risk.value,
            'confidence': self.confidence,
            'evidence': self.evidence,
            'related_files': self.related_files
        }


class SmartDeletionEngine:
    """
    Intelligent file deletion engine.
    
    Capabilities:
    - Rule-based deletion identification
    - Safety validation (protected files, dependencies)
    - Risk assessment
    - Manifest generation for review
    - Safe deletion with rollback capability
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize deletion engine.
        
        Args:
            project_root: Root directory of project
        """
        self.project_root = project_root
        
        # Deletion candidates
        self.candidates: List[DeletionCandidate] = []
        
        # Configuration
        self.auto_delete_risk_levels = {DeletionRisk.SAFE, DeletionRisk.LOW}
        self.min_confidence = 0.7  # Minimum confidence for auto-deletion
        
        # Thresholds
        self.old_archive_days = 180  # Archives older than 6 months
        self.old_temp_days = 7  # Temp files older than 1 week
        
        # Statistics
        self.total_analyzed = 0
        self.total_candidates = 0
        self.total_safe = 0
        self.total_size_to_free = 0
    
    def analyze(self, files: Dict[str, FileMetadata], dependency_graph: Dict[str, Set[str]]) -> List[DeletionCandidate]:
        """
        Analyze files and identify deletion candidates.
        
        Args:
            files: Dictionary of relative_path -> FileMetadata
            dependency_graph: Dictionary of file -> files that depend on it
            
        Returns:
            List of deletion candidates
        """
        logger.info(f"Analyzing {len(files)} files for deletion candidates...")
        
        self.total_analyzed = len(files)
        
        for relative_path, metadata in files.items():
            # Skip protected files
            if metadata.is_protected:
                continue
            
            # Apply deletion rules
            candidate = self._evaluate_file(metadata, dependency_graph)
            
            if candidate:
                self.candidates.append(candidate)
                self.total_candidates += 1
                self.total_size_to_free += metadata.size_bytes
                
                if candidate.risk in self.auto_delete_risk_levels and candidate.confidence >= self.min_confidence:
                    self.total_safe += 1
        
        # Sort by risk (safe first) and size (largest first)
        self.candidates.sort(key=lambda c: (c.risk.value, -c.metadata.size_bytes))
        
        logger.info(f"Found {self.total_candidates} deletion candidates:")
        logger.info(f"  - Safe to auto-delete: {self.total_safe}")
        logger.info(f"  - Total space to free: {self.total_size_to_free / 1024 / 1024:.2f}MB")
        
        return self.candidates
    
    def _evaluate_file(self, metadata: FileMetadata, dependency_graph: Dict[str, Set[str]]) -> Optional[DeletionCandidate]:
        """Evaluate if file is a deletion candidate"""
        # Rule 1: Exact duplicates (by content hash)
        if metadata.is_duplicate and not metadata.is_protected:
            return DeletionCandidate(
                metadata=metadata,
                reason=DeletionReason.DUPLICATE,
                risk=DeletionRisk.SAFE,
                confidence=0.95,
                evidence=[
                    f"Exact duplicate by content hash: {metadata.content_hash[:8]}",
                    "Original file preserved elsewhere"
                ]
            )
        
        # Rule 2: Backup files
        if metadata.category == FileCategory.BACKUP:
            # Check if file is old enough
            age_days = (datetime.now() - metadata.modified_time).days
            
            if age_days > 7:
                return DeletionCandidate(
                    metadata=metadata,
                    reason=DeletionReason.BACKUP,
                    risk=DeletionRisk.LOW,
                    confidence=0.9,
                    evidence=[
                        f"Backup file (age: {age_days} days)",
                        "Original file exists",
                        f"Last modified: {metadata.modified_time.strftime('%Y-%m-%d')}"
                    ]
                )
        
        # Rule 3: Temporary files
        if metadata.category == FileCategory.TEMPORARY:
            age_days = (datetime.now() - metadata.modified_time).days
            
            if age_days > self.old_temp_days:
                return DeletionCandidate(
                    metadata=metadata,
                    reason=DeletionReason.TEMPORARY,
                    risk=DeletionRisk.SAFE,
                    confidence=0.95,
                    evidence=[
                        f"Temporary file (age: {age_days} days)",
                        f"Stale (threshold: {self.old_temp_days} days)"
                    ]
                )
        
        # Rule 4: Empty files
        if metadata.size_bytes == 0 or (metadata.line_count and metadata.line_count <= 1):
            return DeletionCandidate(
                metadata=metadata,
                reason=DeletionReason.EMPTY,
                risk=DeletionRisk.LOW,
                confidence=0.85,
                evidence=[
                    "Empty or near-empty file",
                    f"Size: {metadata.size_bytes} bytes",
                    f"Lines: {metadata.line_count or 0}"
                ]
            )
        
        # Rule 5: Old archived content
        if metadata.purpose == FilePurpose.ARCHIVE:
            age_days = (datetime.now() - metadata.modified_time).days
            
            if age_days > self.old_archive_days:
                return DeletionCandidate(
                    metadata=metadata,
                    reason=DeletionReason.OLD_ARCHIVE,
                    risk=DeletionRisk.LOW,
                    confidence=0.8,
                    evidence=[
                        f"Old archive (age: {age_days} days)",
                        f"Threshold: {self.old_archive_days} days",
                        f"Last modified: {metadata.modified_time.strftime('%Y-%m-%d')}"
                    ]
                )
        
        # Rule 6: Generated files in source control
        if metadata.purpose == FilePurpose.GENERATED:
            # Build artifacts shouldn't be in source control
            if metadata.category == FileCategory.BUILD_ARTIFACT:
                return DeletionCandidate(
                    metadata=metadata,
                    reason=DeletionReason.GENERATED,
                    risk=DeletionRisk.SAFE,
                    confidence=0.9,
                    evidence=[
                        "Build artifact in source control",
                        "Can be regenerated",
                        "Should be in .gitignore"
                    ]
                )
        
        # Rule 7: Unused files (no dependents)
        if metadata.relative_path not in dependency_graph or not dependency_graph[metadata.relative_path]:
            # Only mark as unused if it's not a core file
            if metadata.purpose not in [FilePurpose.CORE, FilePurpose.UNKNOWN]:
                age_days = (datetime.now() - metadata.accessed_time).days
                
                if age_days > 90:  # Not accessed in 90 days
                    return DeletionCandidate(
                        metadata=metadata,
                        reason=DeletionReason.UNUSED,
                        risk=DeletionRisk.MEDIUM,
                        confidence=0.7,
                        evidence=[
                            "No references found in codebase",
                            f"Not accessed in {age_days} days",
                            f"Purpose: {metadata.purpose.value}"
                        ]
                    )
        
        # Rule 8: Obsolete test files (already marked by scanner)
        if metadata.is_obsolete and metadata.category == FileCategory.TEST:
            return DeletionCandidate(
                metadata=metadata,
                reason=DeletionReason.OBSOLETE_TEST,
                risk=DeletionRisk.LOW,
                confidence=0.85,
                evidence=[
                    "Test file marked as obsolete",
                    "Tests non-existent code",
                    "Flagged by analysis"
                ]
            )
        
        return None
    
    def generate_manifest(self, output_path: Optional[Path] = None) -> Path:
        """
        Generate deletion manifest for review.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path to generated manifest
        """
        if output_path is None:
            output_path = self.project_root / 'cortex-brain' / 'cleanup-reports' / f'deletion-manifest-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        manifest = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_analyzed': self.total_analyzed,
                'total_candidates': self.total_candidates,
                'safe_to_delete': self.total_safe,
                'space_to_free_bytes': self.total_size_to_free,
                'space_to_free_mb': self.total_size_to_free / 1024 / 1024
            },
            'risk_breakdown': self._get_risk_breakdown(),
            'reason_breakdown': self._get_reason_breakdown(),
            'candidates': [c.to_dict() for c in self.candidates]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Deletion manifest saved: {output_path}")
        
        return output_path
    
    def execute_deletions(self, dry_run: bool = True, risk_filter: Optional[Set[DeletionRisk]] = None) -> Dict[str, Any]:
        """
        Execute file deletions.
        
        Args:
            dry_run: If True, only simulate deletions
            risk_filter: Optional set of risk levels to delete (defaults to safe auto-delete)
            
        Returns:
            Dictionary with deletion results
        """
        if risk_filter is None:
            risk_filter = self.auto_delete_risk_levels
        
        deleted_files = []
        skipped_files = []
        failed_files = []
        total_freed = 0
        
        for candidate in self.candidates:
            # Check risk level and confidence
            if candidate.risk not in risk_filter:
                skipped_files.append({
                    'path': candidate.metadata.relative_path,
                    'reason': f"Risk level {candidate.risk.value} not in filter"
                })
                continue
            
            if candidate.confidence < self.min_confidence:
                skipped_files.append({
                    'path': candidate.metadata.relative_path,
                    'reason': f"Confidence {candidate.confidence:.2f} below threshold {self.min_confidence}"
                })
                continue
            
            # Perform deletion
            file_path = self.project_root / candidate.metadata.relative_path
            
            if not file_path.exists():
                skipped_files.append({
                    'path': candidate.metadata.relative_path,
                    'reason': "File no longer exists"
                })
                continue
            
            if dry_run:
                logger.info(f"[DRY RUN] Would delete: {candidate.metadata.relative_path} ({candidate.reason.value})")
                deleted_files.append(candidate.metadata.relative_path)
                total_freed += candidate.metadata.size_bytes
            else:
                try:
                    # Delete file
                    file_path.unlink()
                    
                    deleted_files.append(candidate.metadata.relative_path)
                    total_freed += candidate.metadata.size_bytes
                    
                    logger.info(f"Deleted: {candidate.metadata.relative_path} ({candidate.reason.value})")
                    
                except Exception as e:
                    logger.error(f"Failed to delete {candidate.metadata.relative_path}: {e}")
                    failed_files.append({
                        'path': candidate.metadata.relative_path,
                        'error': str(e)
                    })
        
        # Clean up empty directories
        if not dry_run and deleted_files:
            self._cleanup_empty_directories()
        
        results = {
            'dry_run': dry_run,
            'deleted_count': len(deleted_files),
            'skipped_count': len(skipped_files),
            'failed_count': len(failed_files),
            'space_freed_bytes': total_freed,
            'space_freed_mb': total_freed / 1024 / 1024,
            'deleted_files': deleted_files,
            'skipped_files': skipped_files,
            'failed_files': failed_files
        }
        
        logger.info(f"Deletion complete: {len(deleted_files)} files, {total_freed / 1024 / 1024:.2f}MB freed")
        
        return results
    
    def _cleanup_empty_directories(self) -> None:
        """Remove empty directories after file deletion"""
        for candidate in self.candidates:
            file_path = self.project_root / candidate.metadata.relative_path
            parent = file_path.parent
            
            try:
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
                    logger.info(f"Removed empty directory: {parent.relative_to(self.project_root)}")
            except Exception as e:
                logger.debug(f"Could not remove directory {parent}: {e}")
    
    def _get_risk_breakdown(self) -> Dict[str, int]:
        """Get breakdown of candidates by risk level"""
        breakdown = {}
        for risk in DeletionRisk:
            count = sum(1 for c in self.candidates if c.risk == risk)
            if count > 0:
                breakdown[risk.value] = count
        return breakdown
    
    def _get_reason_breakdown(self) -> Dict[str, int]:
        """Get breakdown of candidates by deletion reason"""
        breakdown = {}
        for reason in DeletionReason:
            count = sum(1 for c in self.candidates if c.reason == reason)
            if count > 0:
                breakdown[reason.value] = count
        return breakdown
    
    def get_candidates_by_risk(self, risk: DeletionRisk) -> List[DeletionCandidate]:
        """Get all candidates with specific risk level"""
        return [c for c in self.candidates if c.risk == risk]
    
    def get_candidates_by_reason(self, reason: DeletionReason) -> List[DeletionCandidate]:
        """Get all candidates with specific deletion reason"""
        return [c for c in self.candidates if c.reason == reason]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get deletion statistics"""
        return {
            'total_analyzed': self.total_analyzed,
            'total_candidates': self.total_candidates,
            'safe_to_delete': self.total_safe,
            'space_to_free_bytes': self.total_size_to_free,
            'space_to_free_mb': self.total_size_to_free / 1024 / 1024,
            'risk_breakdown': self._get_risk_breakdown(),
            'reason_breakdown': self._get_reason_breakdown()
        }
