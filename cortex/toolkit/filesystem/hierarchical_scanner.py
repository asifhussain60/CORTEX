"""HierarchicalScanner — Generic recursive file discovery with organization detection.

Extracted from MediaScanner (cortex/tools/media/media_scanner.py) and made domain-agnostic.

Features:
    - Recursive directory traversal
    - Extension filtering
    - Hierarchy depth tracking (1=root, 2=organization, 3+=nested)
    - Organization detection from folder structure
    - Pluggable OrganizationAdapter for domain-specific rules

Authority: phase-toolkit-consolidation.yaml Sub-phase S2
CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
CORE-028: snake_case naming

AC_START: AC-TOOLKIT-HIERARCHICAL-SCANNER-IMPL-001
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Protocol, Set


@dataclass
class ScannedFile:
    """Represents a discovered file with organizational metadata.
    
    Attributes:
        path:             Absolute Path to the file.
        extension:        Lowercase extension including dot (e.g., `.mp4`).
        organization:     Organization/domain name from parent folder, or empty if root-level.
        hierarchy_depth:  Nesting depth from root: 1 (root), 2 (organization), 3+ (nested).
        folder_name:      Immediate parent directory name.
        filename_stem:    Filename without extension.
    """
    
    path: Path
    extension: str
    organization: str
    hierarchy_depth: int
    folder_name: str
    filename_stem: str
    
    def __eq__(self, other: object) -> bool:
        """Two ScannedFile instances are equal if their paths match."""
        if not isinstance(other, ScannedFile):
            return NotImplemented
        return self.path == other.path


class OrganizationAdapter(Protocol):
    """Protocol for custom organization detection strategies.
    
    Implementations can transform folder names into domain-specific organization
    names (e.g., "Studio_A" → "StudioA", "com.example.myapp" → "myapp").
    """
    
    def detect_organization(self, path: Path, folder_name: str) -> str:
        """Detect organization name from file path and folder context.
        
        Args:
            path:        Full path to the file.
            folder_name: Immediate parent folder name.
        
        Returns:
            Organization name (domain-specific transformation applied).
        """
        ...


class IScannerProtocol(Protocol):
    """Generic scanner protocol — language-agnostic scanning interface.

    Phase 78 GAP-78-B-05: Formal Protocol enabling multi-language scanners
    to be used interchangeably. HierarchicalScanner implements this protocol
    structurally (no explicit inheritance required for Protocol compliance).

    All scanners in cortex/toolkit/filesystem/ should satisfy this interface.
    """

    def scan(self) -> List[ScannedFile]:
        """Execute a full scan and return discovered files.

        Returns:
            List of ScannedFile instances from the scanned root.
        """
        ...


class DefaultOrganizationAdapter:
    """Default adapter returns folder name as-is."""
    
    def detect_organization(self, path: Path, folder_name: str) -> str:
        """Return folder name without transformation."""
        return folder_name


class HierarchicalScanner:
    """Recursively discovers files under a root directory with hierarchy tracking.
    
    Generic scanner for any file-based domain (media, documents, code repositories).
    Tracks organizational structure via folder hierarchy and supports custom
    organization detection via pluggable adapters.
    
    Attributes:
        root:       Root directory to scan.
        extensions: Set of file extensions to include (e.g., {`.mp4`, `.mkv`}).
        adapter:    Optional OrganizationAdapter for custom detection logic.
    
    Examples:
        >>> scanner = HierarchicalScanner(Path("/data"), extensions={".mp4"})
        >>> files = scanner.scan()
        >>> organized = [f for f in files if f.hierarchy_depth >= 2]
    """
    
    DEFAULT_EXTENSIONS: Set[str] = {
        ".txt", ".md", ".pdf", ".docx",
        ".mp4", ".mkv", ".avi", ".mov",
        ".py", ".js", ".ts", ".java", ".cs",
    }
    
    def __init__(
        self,
        root: Path,
        extensions: Optional[Set[str]] = None,
        adapter: Optional[OrganizationAdapter] = None,
    ) -> None:
        """Initialize hierarchical scanner.
        
        Args:
            root:       Root directory to scan.
            extensions: Set of extensions to include. Defaults to common file types.
            adapter:    Custom organization adapter. Defaults to folder-name passthrough.
        """
        self.root = root
        self.extensions = extensions if extensions is not None else self.DEFAULT_EXTENSIONS
        self.adapter = adapter if adapter is not None else DefaultOrganizationAdapter()
    
    def scan(self) -> List[ScannedFile]:
        """Recursively scan root directory and return discovered files.
        
        Returns:
            List of ScannedFile instances with organizational metadata.
        """
        discovered: List[ScannedFile] = []
        
        for file_path in self._walk_directory(self.root):
            if file_path.suffix.lower() not in self.extensions:
                continue
            
            scanned = self._analyze_file(file_path)
            discovered.append(scanned)
        
        return discovered
    
    def _walk_directory(self, directory: Path) -> List[Path]:
        """Recursively walk directory and return all file paths.
        
        Args:
            directory: Directory to walk.
        
        Returns:
            List of file paths (not directories).
        """
        files: List[Path] = []
        
        try:
            for item in directory.iterdir():
                if item.is_file():
                    files.append(item)
                elif item.is_dir():
                    files.extend(self._walk_directory(item))
        except PermissionError:
            # Skip directories without read permission
            pass
        
        return files
    
    def _analyze_file(self, file_path: Path) -> ScannedFile:
        """Analyze file and extract organizational metadata.
        
        Args:
            file_path: Path to file.
        
        Returns:
            ScannedFile with hierarchy and organization information.
        """
        # Calculate hierarchy depth (root=1, organization=2, nested=3+)
        relative_path = file_path.relative_to(self.root)
        depth = len(relative_path.parts)
        
        # Extract folder name and organization
        folder_name = file_path.parent.name if file_path.parent != self.root else ""
        
        if depth == 1:
            # Root-level file
            organization = ""
        else:
            # Use adapter to detect organization from folder hierarchy
            organization = self.adapter.detect_organization(file_path, folder_name)
        
        return ScannedFile(
            path=file_path,
            extension=file_path.suffix.lower(),
            organization=organization,
            hierarchy_depth=depth,
            folder_name=folder_name,
            filename_stem=file_path.stem,
        )


# AC_COMPLETE: AC-TOOLKIT-HIERARCHICAL-SCANNER-IMPL-001 ✅ Implementation complete (GREEN phase)
