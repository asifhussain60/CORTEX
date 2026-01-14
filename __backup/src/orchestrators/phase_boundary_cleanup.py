"""
Phase-Boundary Cleanup Framework (AC-CLEAN-201)

Integrates cleanup into MasterOrchestrator.complete_phase() workflow.
Provides:
- Intent registry loading and validation
- Phase-boundary artifact cleanup
- Evidence bundle generation
- Approval workflow for semantic cleanup

Author: GitHub Copilot + Asif Hussain
Date: 2026-01-12
Status: Implementation for AC-CLEAN-201
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import yaml
import json
import hashlib
from enum import Enum
import logging


class FileIntent(Enum):
    """Classification of file intent for cleanup decisions."""
    KEEP = "keep"
    OPTIONAL = "optional"
    BUILD_ARTIFACT = "build_artifact"


@dataclass
class IntentEntry:
    """Single entry in intent registry."""
    path: str
    intent: FileIntent
    intent_reason: str
    deletion_requires_approval: bool = False
    notes: Optional[str] = None
    
    @classmethod
    def from_dict(cls, path: str, data: dict) -> "IntentEntry":
        """Create IntentEntry from registry dict."""
        intent_str = data.get('intent', '').lower()
        try:
            intent = FileIntent(intent_str)
        except ValueError:
            intent = FileIntent.KEEP  # Default to safe option
        
        return cls(
            path=path,
            intent=intent,
            intent_reason=data.get('intent_reason', ''),
            deletion_requires_approval=data.get('deletion_requires_approval', False),
            notes=data.get('notes')
        )


@dataclass
class CleanupOperation:
    """Single cleanup operation with evidence."""
    file_path: str
    intent: FileIntent
    intent_reason: str
    approval_required: bool
    approval_by: Optional[str] = None
    approval_timestamp: Optional[str] = None
    deleted_at: Optional[str] = None
    file_hash: Optional[str] = None  # Hash before deletion for recovery
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to audit trail entry."""
        return {
            'file_path': self.file_path,
            'intent': self.intent.value,
            'intent_reason': self.intent_reason,
            'approval_required': self.approval_required,
            'approval_by': self.approval_by,
            'approval_timestamp': self.approval_timestamp,
            'deleted_at': self.deleted_at,
            'file_hash': self.file_hash,
            'error': self.error
        }


@dataclass
class CleanupEvidenceBundle:
    """Evidence bundle for cleanup operations."""
    ac_id: str = "AC-CLEAN-201"
    operation_type: str = "phase_boundary_cleanup"
    phase_number: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    operations: List[CleanupOperation] = field(default_factory=list)
    total_files_deleted: int = 0
    total_bytes_freed: int = 0
    total_approval_required: int = 0
    total_approved: int = 0
    total_errors: int = 0
    
    def add_operation(self, op: CleanupOperation) -> None:
        """Add cleanup operation to bundle."""
        self.operations.append(op)
        self.total_files_deleted += 1 if op.deleted_at else 0
        if op.approval_required:
            self.total_approval_required += 1
            if op.approval_by:
                self.total_approved += 1
        if op.error:
            self.total_errors += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            'ac_id': self.ac_id,
            'operation_type': self.operation_type,
            'phase_number': self.phase_number,
            'timestamp': self.timestamp,
            'summary': {
                'total_files_deleted': self.total_files_deleted,
                'total_bytes_freed': self.total_bytes_freed,
                'total_approval_required': self.total_approval_required,
                'total_approved': self.total_approved,
                'total_errors': self.total_errors
            },
            'operations': [op.to_dict() for op in self.operations]
        }


class IntentRegistry:
    """Load and query file intent registry."""
    
    def __init__(self, registry_path: Path):
        """Initialize from YAML file."""
        self.registry_path = registry_path
        self.entries: Dict[str, IntentEntry] = {}
        self.protected_patterns: List[str] = []
        self.cleanup_workflows: Dict[str, dict] = {}
        self._load()
    
    def _load(self) -> None:
        """Load registry from YAML file."""
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Intent registry not found: {self.registry_path}")
        
        with open(self.registry_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            raise ValueError("Intent registry is empty")
        
        # Load registry entries
        registry = data.get('registry', {})
        for path, entry_data in registry.items():
            self.entries[path] = IntentEntry.from_dict(path, entry_data)
        
        # Load protected patterns
        safety_rules = data.get('safety_rules', {})
        self.protected_patterns = safety_rules.get('protected_patterns', [])
        
        # Load cleanup workflows
        self.cleanup_workflows = data.get('cleanup_workflow', {})
    
    def get_intent(self, file_path: str) -> Optional[IntentEntry]:
        """Get intent for a file path (exact match)."""
        return self.entries.get(file_path)
    
    def get_intent_by_pattern(self, file_path: str) -> Optional[IntentEntry]:
        """Get intent by pattern matching (directory patterns)."""
        file_path_obj = Path(file_path)
        
        for pattern_str, entry in self.entries.items():
            pattern_path = Path(pattern_str)
            try:
                # Check if file is under pattern directory
                if pattern_str.endswith('/'):
                    if str(file_path_obj).startswith(str(pattern_path)):
                        return entry
                # Check exact match
                elif str(file_path_obj) == str(pattern_path):
                    return entry
            except Exception:
                continue
        
        return None
    
    def is_protected(self, file_path: str) -> bool:
        """Check if file matches protected patterns."""
        file_path_obj = Path(file_path)
        
        for pattern in self.protected_patterns:
            if pattern.endswith('*'):
                # Pattern ends with * - check startswith
                pattern_base = pattern[:-1]  # Remove *
                if str(file_path_obj).startswith(pattern_base):
                    return True
            else:
                # Exact match
                if str(file_path_obj) == pattern:
                    return True
        
        return False
    
    def requires_approval(self, file_path: str) -> bool:
        """Check if cleanup of file requires approval."""
        entry = self.get_intent_by_pattern(file_path)
        if entry and entry.intent == FileIntent.OPTIONAL:
            return entry.deletion_requires_approval
        return False


class PhaseBoundaryCleanup:
    """Phase-boundary cleanup framework."""
    
    def __init__(self, workspace_root: Path, intent_registry: IntentRegistry, 
                 audit_logger=None):
        """Initialize cleanup framework."""
        self.workspace_root = workspace_root
        self.intent_registry = intent_registry
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
    
    def cleanup_phase_artifacts(self, phase_number: int) -> CleanupEvidenceBundle:
        """
        Execute phase-boundary cleanup.
        
        Deletes artifacts from previous phase (phase_number - 1).
        Returns evidence bundle with all operations for audit trail.
        """
        evidence = CleanupEvidenceBundle(phase_number=phase_number)
        
        if phase_number <= 1:
            # No previous phase to cleanup
            return evidence
        
        # Define phase artifact patterns (would be extended per phase)
        previous_phase = phase_number - 1
        artifact_patterns = self._get_phase_artifacts(previous_phase)
        
        for pattern in artifact_patterns:
            self._cleanup_pattern(pattern, evidence, phase_number)
        
        # Log to audit trail
        self._log_cleanup(evidence)
        
        return evidence
    
    def _get_phase_artifacts(self, phase_num: int) -> List[str]:
        """Get cleanup patterns for a specific phase."""
        # Phase 1 artifacts: build caches, test artifacts
        phase_artifacts = {
            1: [
                "**/__pycache__",
                "**/.pytest_cache",
                "**/*.pyc",
                "**/htmlcov"
            ],
            2: [
                "**/.coverage",
                "**/test-results"
            ]
        }
        return phase_artifacts.get(phase_num, [])
    
    def _cleanup_pattern(self, pattern: str, evidence: CleanupEvidenceBundle,
                        phase_num: int) -> None:
        """Cleanup files matching a pattern."""
        try:
            import glob
            matches = glob.glob(str(self.workspace_root / pattern), recursive=True)
            
            for file_path in matches:
                file_path_obj = Path(file_path)
                
                # Check protection
                if self.intent_registry.is_protected(str(file_path_obj)):
                    op = CleanupOperation(
                        file_path=str(file_path_obj),
                        intent=FileIntent.KEEP,
                        intent_reason="Protected pattern",
                        approval_required=False,
                        error="Skipped - protected pattern"
                    )
                    evidence.add_operation(op)
                    continue
                
                # Get intent
                entry = self.intent_registry.get_intent_by_pattern(str(file_path_obj))
                intent = entry.intent if entry else FileIntent.BUILD_ARTIFACT
                intent_reason = entry.intent_reason if entry else "Phase artifact"
                requires_approval = entry.deletion_requires_approval if entry else False
                
                # Check approval
                if requires_approval:
                    op = CleanupOperation(
                        file_path=str(file_path_obj),
                        intent=intent,
                        intent_reason=intent_reason,
                        approval_required=True,
                        error="Requires approval - skipped"
                    )
                    evidence.add_operation(op)
                    continue
                
                # Compute hash before deletion
                file_hash = self._compute_file_hash(file_path_obj)
                
                # Delete file
                try:
                    if file_path_obj.is_file():
                        file_size = file_path_obj.stat().st_size
                        file_path_obj.unlink()
                        evidence.total_bytes_freed += file_size
                    elif file_path_obj.is_dir():
                        import shutil
                        dir_size = self._get_dir_size(file_path_obj)
                        shutil.rmtree(file_path_obj, ignore_errors=True)
                        evidence.total_bytes_freed += dir_size
                    
                    op = CleanupOperation(
                        file_path=str(file_path_obj),
                        intent=intent,
                        intent_reason=intent_reason,
                        approval_required=requires_approval,
                        deleted_at=datetime.utcnow().isoformat() + 'Z',
                        file_hash=file_hash
                    )
                    evidence.add_operation(op)
                    
                except Exception as e:
                    op = CleanupOperation(
                        file_path=str(file_path_obj),
                        intent=intent,
                        intent_reason=intent_reason,
                        approval_required=requires_approval,
                        error=str(e)
                    )
                    evidence.add_operation(op)
        
        except Exception as e:
            self.logger.error(f"Error processing pattern {pattern}: {e}")
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute hash of file for recovery purposes."""
        try:
            if file_path.is_file() and file_path.stat().st_size < 1000000:  # <1MB
                with open(file_path, 'rb') as f:
                    return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            pass
        return ""
    
    def _get_dir_size(self, dir_path: Path) -> int:
        """Calculate total size of directory."""
        total = 0
        try:
            for item in dir_path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except Exception:
            pass
        return total
    
    def _log_cleanup(self, evidence: CleanupEvidenceBundle) -> None:
        """Log cleanup evidence to audit trail."""
        if self.audit_logger:
            self.audit_logger.log_event(
                category="INFRASTRUCTURE",
                level="INFO",
                message=f"Phase boundary cleanup completed: {evidence.total_files_deleted} files deleted",
                ac_id="AC-CLEAN-201",
                correlation_id=f"cleanup-phase-{evidence.phase_number}",
                extra={
                    'evidence_bundle': evidence.to_dict()
                }
            )
