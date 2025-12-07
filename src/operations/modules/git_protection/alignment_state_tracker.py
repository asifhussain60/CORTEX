"""
Alignment State Tracker

Tracks which files have been aligned, optimized, or reviewed on the current machine.
State is machine-local (not shared via git) to prevent conflicts across machines.

Author: Asif Hussain
Version: 3.8.1
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class FileAlignmentState:
    """State of a single file's alignment."""
    path: str
    last_aligned: str  # ISO timestamp
    alignment_hash: str  # Hash of aligned content
    operations: List[str]  # Operations performed: ['align', 'optimize', 'review']
    score: Optional[int] = None  # Review score if available
    issues_fixed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileAlignmentState':
        """Create from dictionary."""
        return cls(**data)


class AlignmentStateTracker:
    """
    Tracks alignment state for files on the current machine.
    
    State file is in .gitignore to prevent cross-machine conflicts.
    Each machine maintains its own alignment state independently.
    """
    
    STATE_FILE = "cortex-brain/admin/alignment-state.json"
    
    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or Path.cwd()
        self.state_file = self.workspace_path / self.STATE_FILE
        self.state: Dict[str, FileAlignmentState] = {}
        self._load_state()
    
    def _load_state(self) -> None:
        """Load alignment state from disk."""
        if not self.state_file.exists():
            self.state = {}
            return
        
        try:
            data = json.loads(self.state_file.read_text(encoding='utf-8'))
            self.state = {
                path: FileAlignmentState.from_dict(file_data)
                for path, file_data in data.get('files', {}).items()
            }
        except Exception as e:
            print(f"Warning: Could not load alignment state: {e}")
            self.state = {}
    
    def _save_state(self) -> None:
        """Save alignment state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'version': '1.0',
            'machine': self._get_machine_id(),
            'last_updated': datetime.now().isoformat(),
            'files': {
                path: state.to_dict()
                for path, state in self.state.items()
            }
        }
        
        self.state_file.write_text(
            json.dumps(data, indent=2),
            encoding='utf-8'
        )
    
    def _get_machine_id(self) -> str:
        """Get unique machine identifier."""
        import socket
        return socket.gethostname()
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate hash of file content."""
        if not file_path.exists():
            return ""
        
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()[:16]
    
    def mark_aligned(
        self,
        file_path: Path,
        operation: str,
        issues_fixed: int = 0,
        score: Optional[int] = None
    ) -> None:
        """
        Mark a file as aligned/optimized/reviewed.
        
        Args:
            file_path: Path to file
            operation: Operation performed ('align', 'optimize', 'review')
            issues_fixed: Number of issues fixed
            score: Review score if available
        """
        relative_path = str(file_path.relative_to(self.workspace_path))
        file_hash = self._calculate_file_hash(file_path)
        
        if relative_path in self.state:
            # Update existing state
            state = self.state[relative_path]
            state.last_aligned = datetime.now().isoformat()
            state.alignment_hash = file_hash
            if operation not in state.operations:
                state.operations.append(operation)
            state.issues_fixed += issues_fixed
            if score is not None:
                state.score = score
        else:
            # Create new state
            self.state[relative_path] = FileAlignmentState(
                path=relative_path,
                last_aligned=datetime.now().isoformat(),
                alignment_hash=file_hash,
                operations=[operation],
                issues_fixed=issues_fixed,
                score=score
            )
        
        self._save_state()
    
    def is_aligned(self, file_path: Path) -> bool:
        """Check if file is currently aligned."""
        relative_path = str(file_path.relative_to(self.workspace_path))
        
        if relative_path not in self.state:
            return False
        
        state = self.state[relative_path]
        current_hash = self._calculate_file_hash(file_path)
        
        # File is aligned if hash matches recorded state
        return state.alignment_hash == current_hash
    
    def get_aligned_files(self) -> List[Path]:
        """Get list of all aligned files."""
        aligned = []
        
        for relative_path, state in self.state.items():
            file_path = self.workspace_path / relative_path
            if file_path.exists():
                current_hash = self._calculate_file_hash(file_path)
                if current_hash == state.alignment_hash:
                    aligned.append(file_path)
        
        return aligned
    
    def get_modified_aligned_files(self) -> List[Path]:
        """Get aligned files that have been modified since alignment."""
        modified = []
        
        for relative_path, state in self.state.items():
            file_path = self.workspace_path / relative_path
            if file_path.exists():
                current_hash = self._calculate_file_hash(file_path)
                if current_hash != state.alignment_hash:
                    modified.append(file_path)
        
        return modified
    
    def get_alignment_info(self, file_path: Path) -> Optional[FileAlignmentState]:
        """Get alignment information for a file."""
        relative_path = str(file_path.relative_to(self.workspace_path))
        return self.state.get(relative_path)
    
    def clear_state(self, file_path: Optional[Path] = None) -> None:
        """
        Clear alignment state.
        
        Args:
            file_path: Specific file to clear, or None to clear all
        """
        if file_path:
            relative_path = str(file_path.relative_to(self.workspace_path))
            self.state.pop(relative_path, None)
        else:
            self.state = {}
        
        self._save_state()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get alignment statistics."""
        aligned_count = len(self.get_aligned_files())
        modified_count = len(self.get_modified_aligned_files())
        
        operations_count = {}
        total_issues_fixed = 0
        
        for state in self.state.values():
            for op in state.operations:
                operations_count[op] = operations_count.get(op, 0) + 1
            total_issues_fixed += state.issues_fixed
        
        return {
            'total_tracked': len(self.state),
            'currently_aligned': aligned_count,
            'modified_since_alignment': modified_count,
            'operations': operations_count,
            'total_issues_fixed': total_issues_fixed,
            'machine': self._get_machine_id()
        }
