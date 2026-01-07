"""
Planner Mode Detection for Epic & Feature Planning System.

Detects whether a plan folder represents an EPIC (multi-child) or FEATURE (single) plan
based on folder structure and file patterns.

Author: Asif Hussain
Created: January 4, 2026
Part of: CORTEX-5.0 Sub-Plan 00B Phase 00
"""

import re
from enum import Enum
from pathlib import Path
from typing import Optional


class PlannerMode(Enum):
    """Planner operational mode."""
    
    EPIC = "epic"       # Multi-child plans with dependencies (e.g., CORTEX-5.0)
    FEATURE = "feature"  # Single plan with phases (e.g., test-coverage-sprint)
    
    def __str__(self) -> str:
        return self.value


class PlannerModeDetector:
    """
    Detect planner mode from folder structure.
    
    Epic Mode Indicators:
    - 2+ immediate subfolders matching pattern: NN-{name}/ or NNA-{name}/
    - Each subfolder contains a 00-*.md master plan file
    - Root contains 00-MASTER-*.md or similar epic master plan
    
    Feature Mode Indicators:
    - Root contains standard subfolders: context/, artifacts/, reports/, tracking/
    - Root contains 00-{feature-name}.md master plan
    - No NN-{name}/ child plan subfolders present
    
    Examples:
        >>> detector = PlannerModeDetector()
        >>> mode = detector.detect(Path("cortex-brain/documents/planning/active/CORTEX-5.0"))
        >>> print(mode)  # PlannerMode.EPIC
        
        >>> mode = detector.detect(Path("CORTEX-5.0/00-test-coverage-sprint"))
        >>> print(mode)  # PlannerMode.FEATURE
    """
    
    # Folder patterns
    CHILD_PLAN_PATTERN = r'^\d{2}[A-Z]?-'  # Matches: 00-, 01-, 00A-, 10B-, etc.
    MASTER_PLAN_PATTERN = "00-*.md"         # Master plan file pattern
    
    # Feature mode standard folders
    FEATURE_FOLDERS = ["context", "artifacts", "reports", "tracking"]
    
    def detect(self, plan_path: Path) -> PlannerMode:
        """
        Detect planner mode (EPIC vs FEATURE) from folder structure.
        
        Args:
            plan_path: Root path to plan folder
            
        Returns:
            PlannerMode.EPIC or PlannerMode.FEATURE
            
        Raises:
            ValueError: If structure doesn't match either mode
            FileNotFoundError: If plan_path doesn't exist
        """
        if not plan_path.exists():
            raise FileNotFoundError(f"Plan path does not exist: {plan_path}")
        
        if not plan_path.is_dir():
            raise ValueError(f"Plan path must be a directory: {plan_path}")
        
        # Find master plan files in root
        master_plans = list(plan_path.glob(self.MASTER_PLAN_PATTERN))
        
        # Find child plan directories (NN-{name}/ pattern)
        child_dirs = self._find_child_plan_dirs(plan_path)
        
        # Epic detection: 2+ child dirs with master plans
        if len(child_dirs) >= 2 and master_plans:
            # Validate children have master plans
            valid_children = self._validate_child_plans(child_dirs)
            
            if valid_children >= 2:
                # Double-check epic structure integrity
                if self.validate_epic_structure(plan_path):
                    return PlannerMode.EPIC
                # Epic detected but missing tracking files
                return PlannerMode.EPIC
        
        # Feature detection: standard folders + no child plans
        if self._has_feature_structure(plan_path) and master_plans and not child_dirs:
            return PlannerMode.FEATURE
        
        # Neither pattern matched
        raise ValueError(
            f"Cannot detect planner mode for: {plan_path}\n\n"
            f"Epic requirements:\n"
            f"  - 2+ child directories matching {self.CHILD_PLAN_PATTERN}\n"
            f"  - Each child must contain {self.MASTER_PLAN_PATTERN}\n"
            f"  - Root must contain {self.MASTER_PLAN_PATTERN}\n\n"
            f"Feature requirements:\n"
            f"  - Standard folders: {', '.join(self.FEATURE_FOLDERS)}\n"
            f"  - Root must contain {self.MASTER_PLAN_PATTERN}\n"
            f"  - No child plan directories\n\n"
            f"Found:\n"
            f"  - Master plans: {len(master_plans)}\n"
            f"  - Child dirs: {len(child_dirs)}\n"
            f"  - Feature folders: {sum(1 for f in self.FEATURE_FOLDERS if (plan_path / f).exists())}"
        )
    
    def _find_child_plan_dirs(self, plan_path: Path) -> list[Path]:
        """Find directories matching child plan pattern."""
        child_dirs = []
        for item in plan_path.iterdir():
            if item.is_dir() and re.match(self.CHILD_PLAN_PATTERN, item.name):
                child_dirs.append(item)
        return child_dirs
    
    def _validate_child_plans(self, child_dirs: list[Path]) -> int:
        """Count how many child directories contain valid master plans."""
        valid_count = 0
        for child_dir in child_dirs:
            master_plans = list(child_dir.glob(self.MASTER_PLAN_PATTERN))
            if master_plans:
                valid_count += 1
        return valid_count
    
    def _has_feature_structure(self, plan_path: Path) -> bool:
        """Check if plan has standard feature folder structure."""
        return all((plan_path / folder).exists() for folder in self.FEATURE_FOLDERS)
    
    def validate_epic_structure(self, plan_path: Path) -> bool:
        """
        Validate epic folder structure has required tracking infrastructure.
        
        Required files for epic:
        - tracking/epic-progress-tracker.json
        - tracking/child-plan-registry.json
        - tracking/dependency-graph.json
        
        Args:
            plan_path: Root path to epic plan folder
            
        Returns:
            True if all required tracking files exist, False otherwise
        """
        try:
            tracking = plan_path / "tracking"
            if not tracking.exists():
                return False
            
            required_files = [
                tracking / "epic-progress-tracker.json",
                tracking / "child-plan-registry.json",
                tracking / "dependency-graph.json"
            ]
            
            return all(f.exists() for f in required_files)
        except Exception:
            return False
    
    def validate_feature_structure(self, plan_path: Path) -> bool:
        """
        Validate feature folder structure has required tracking file.
        
        Required file for feature:
        - tracking/progress-tracker.json
        
        Args:
            plan_path: Root path to feature plan folder
            
        Returns:
            True if progress tracker exists, False otherwise
        """
        try:
            tracking_file = plan_path / "tracking" / "progress-tracker.json"
            return tracking_file.exists()
        except Exception:
            return False
    
    def get_master_plan_path(self, plan_path: Path) -> Optional[Path]:
        """
        Get the master plan file path for a plan.
        
        Args:
            plan_path: Root path to plan folder
            
        Returns:
            Path to master plan file, or None if not found
        """
        master_plans = list(plan_path.glob(self.MASTER_PLAN_PATTERN))
        return master_plans[0] if master_plans else None
    
    def get_plan_id(self, plan_path: Path) -> str:
        """
        Extract plan ID from folder structure.
        
        For epic: Uses folder name
        For feature: Extracts from folder name (removes NN- prefix)
        
        Args:
            plan_path: Root path to plan folder
            
        Returns:
            Plan ID (kebab-case)
        """
        folder_name = plan_path.name
        
        # Remove numeric prefix if present (for feature plans)
        match = re.match(r'^\d{2}[A-Z]?-(.+)$', folder_name)
        if match:
            return match.group(1)
        
        return folder_name


# Convenience function for quick detection
def detect_planner_mode(plan_path: Path) -> PlannerMode:
    """
    Detect planner mode for a given plan path.
    
    Convenience function wrapper around PlannerModeDetector.detect().
    
    Args:
        plan_path: Root path to plan folder
        
    Returns:
        PlannerMode.EPIC or PlannerMode.FEATURE
        
    Raises:
        ValueError: If structure doesn't match either mode
        FileNotFoundError: If plan_path doesn't exist
        
    Example:
        >>> from pathlib import Path
        >>> mode = detect_planner_mode(Path("cortex-brain/documents/planning/active/CORTEX-5.0"))
        >>> if mode == PlannerMode.EPIC:
        ...     print("This is an epic plan")
    """
    detector = PlannerModeDetector()
    return detector.detect(plan_path)


if __name__ == "__main__":
    # Demo usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python planner_mode_detector.py <plan_path>")
        sys.exit(1)
    
    plan_path = Path(sys.argv[1])
    
    try:
        detector = PlannerModeDetector()
        mode = detector.detect(plan_path)
        
        print(f"✅ Detected mode: {mode}")
        print(f"   Plan ID: {detector.get_plan_id(plan_path)}")
        print(f"   Master plan: {detector.get_master_plan_path(plan_path)}")
        
        if mode == PlannerMode.EPIC:
            valid = detector.validate_epic_structure(plan_path)
            print(f"   Epic structure valid: {'✅' if valid else '❌'}")
        else:
            valid = detector.validate_feature_structure(plan_path)
            print(f"   Feature structure valid: {'✅' if valid else '❌'}")
            
    except (ValueError, FileNotFoundError) as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
