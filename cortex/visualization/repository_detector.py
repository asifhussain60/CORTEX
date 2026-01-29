"""
Repository Type Detector for CORTEX Visualization System.

Detects whether a repository is the CORTEX repository or an external
repository by checking for CORTEX-specific markers.

This enables adaptive dashboard configuration:
- CORTEX repository: Show 8 tabs (5 universal + 3 CORTEX-specific)
- External repository: Show 5 tabs (universal only)

Detection Markers:
- cortex_brain/ directory
- cortex/orchestrators/ directory
- .github/prompts/CORTEX.prompt.md file
- cortex/wiring/specifications/wiring.yaml file

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-001
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class CortexFeatures:
    """
    Detected CORTEX-specific features in a repository.
    
    Attributes:
        has_cortex_brain: Whether cortex_brain/ directory exists
        has_orchestrators: Whether cortex/orchestrators/ directory exists
        has_prompt_file: Whether .github/prompts/CORTEX.prompt.md exists
        has_wiring: Whether cortex/wiring/specifications/wiring.yaml exists
    """
    has_cortex_brain: bool
    has_orchestrators: bool
    has_prompt_file: bool
    has_wiring: bool


class RepositoryDetector:
    """
    Detects repository type (CORTEX vs external).
    
    Used by DashboardConfiguration to determine which tabs to show:
    - CORTEX repository → 8 tabs (universal + CORTEX-specific)
    - External repository → 5 tabs (universal only)
    
    Example:
        ```python
        detector = RepositoryDetector(Path("/path/to/repo"))
        if detector.is_cortex_repository():
            print("CORTEX repository detected - showing 8 tabs")
        else:
            print("External repository - showing 5 tabs")
        
        # Get detailed feature detection
        features = detector.detect_cortex_features()
        if features.has_orchestrators:
            print("Orchestrator constellation tab available")
        ```
    
    Attributes:
        repo_path: Path to repository root
    """
    
    def __init__(self, repo_path: Path) -> None:
        """
        Initialize repository detector.
        
        Args:
            repo_path: Path to repository root directory
        """
        self.repo_path = repo_path
    
    def is_cortex_repository(self) -> bool:
        """
        Check if repository is CORTEX repository.
        
        Returns True if ANY of the CORTEX markers exist in the repository.
        
        Returns:
            True if CORTEX repository, False if external repository
        """
        markers = self.get_cortex_markers()
        return any(marker.exists() for marker in markers)
    
    def detect_cortex_features(self) -> CortexFeatures:
        """
        Detect specific CORTEX features present in repository.
        
        Returns detailed breakdown of which CORTEX components are present,
        enabling fine-grained tab availability decisions.
        
        Returns:
            CortexFeatures dataclass with feature flags
        """
        markers = self.get_cortex_markers()
        
        return CortexFeatures(
            has_cortex_brain=markers[0].exists(),      # cortex_brain/
            has_orchestrators=markers[1].exists(),     # cortex/orchestrators/
            has_prompt_file=markers[2].exists(),       # CORTEX.prompt.md
            has_wiring=markers[3].exists(),            # wiring.yaml
        )
    
    def get_cortex_markers(self) -> List[Path]:
        """
        Get list of paths to check for CORTEX markers.
        
        Returns:
            List of Path objects representing CORTEX-specific markers
        """
        return [
            self.repo_path / "cortex_brain",
            self.repo_path / "cortex" / "orchestrators",
            self.repo_path / ".github" / "prompts" / "CORTEX.prompt.md",
            self.repo_path / "cortex" / "wiring" / "specifications" / "wiring.yaml",
        ]


def is_cortex_repository(repo_path: Path) -> bool:
    """
    Convenience function to check if repository is CORTEX.
    
    Args:
        repo_path: Path to repository root
    
    Returns:
        True if CORTEX repository, False if external repository
    
    Example:
        ```python
        if is_cortex_repository(Path("/project")):
            tabs = get_cortex_tabs()  # 8 tabs
        else:
            tabs = get_universal_tabs()  # 5 tabs
        ```
    """
    detector = RepositoryDetector(repo_path)
    return detector.is_cortex_repository()
