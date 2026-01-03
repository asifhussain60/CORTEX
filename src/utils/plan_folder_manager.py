"""
Plan Folder Manager - Hierarchical Plan Structure Management

Purpose: Creates and manages structured folder hierarchies for planning artifacts,
         following the Planning System 4.0 manifest specification.

Folder Structure:
    active/plan-name-v1/
    ├── 00-master-plan.md           # Human-readable master plan
    ├── execution/
    │   └── 00-master-plan.yaml     # Machine-executable YAML
    ├── tracking/
    │   └── progress-tracker.json   # Progress tracking
    ├── reports/
    │   └── phase-completion/       # Phase reports
    ├── artifacts/
    │   └── generated-files/        # Supporting artifacts
    └── context/
        └── requirements.md          # Context documents

Author: CORTEX Development Team
Created: December 27, 2025
Version: 1.0.0
Manifest: cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PlanFolderManager:
    """
    Manages hierarchical folder structure for planning artifacts.
    
    Features:
    - Creates standardized folder hierarchies
    - Enforces naming conventions (00-master-plan.md, 01-subplan-*.md)
    - Initializes tracking/progress-tracker.json
    - Generates README.md with plan overview
    - Supports version detection (v1, v2, v3)
    - Atomic folder creation (all-or-nothing)
    
    Usage:
        manager = PlanFolderManager(project_root)
        plan_folder = manager.create_plan_folder(
            plan_id="user-auth-v1",
            title="User Authentication System",
            complexity_tier=3,
            status="active"
        )
        
        # Save master plan
        master_plan_path = plan_folder / "00-master-plan.md"
        master_plan_path.write_text(plan_content)
        
        # Save YAML execution plan
        yaml_path = plan_folder / "execution" / "00-master-plan.yaml"
        yaml_path.write_text(yaml_content)
    """
    
    # Required subfolders for all plans
    REQUIRED_SUBFOLDERS = ["context", "reports", "artifacts", "tracking", "execution"]
    
    # File naming conventions
    TEMP_PLAN_NAME = "11-temp-planning-session.md"
    TRACKER_NAME = "tracking/progress-tracker.json"
    README_NAME = "README.md"
    
    def __init__(self, project_root: Path):
        """
        Initialize PlanFolderManager.
        
        Args:
            project_root: Path to CORTEX project root
        """
        self.project_root = Path(project_root)
        self.planning_root = self.project_root / "cortex-brain" / "documents" / "planning"
        
        logger.info(f"📁 PlanFolderManager initialized: {self.planning_root}")
    
    def _generate_master_plan_filename(self, plan_id: str) -> str:
        """
        Generate meaningful master plan filename from plan ID.
        
        Args:
            plan_id: Plan identifier (e.g., "glassmorphism-css-standardization")
        
        Returns:
            Master plan filename (e.g., "00-glassmorphism.md")
        
        Example:
            >>> manager._generate_master_plan_filename("vacuum-v2-migration")
            "00-vacuum-v2.md"
        """
        # Max 22 chars total - 3 for "00-" - 3 for ".md" = 16 chars for name
        max_name_length = 16
        
        # Split on hyphens
        parts = plan_id.split('-')
        
        # Take first part + version/type suffix if exists
        short_name = parts[0]
        
        for part in parts[1:]:
            if part in ['v1', 'v2', 'v3', 'v4', 'v5', 'migration', 'refactor', 'system']:
                if len(short_name + '-' + part) <= max_name_length:
                    short_name = f"{short_name}-{part}"
                break
        
        # Truncate if needed
        if len(short_name) > max_name_length:
            short_name = short_name[:max_name_length].rstrip('-')
        
        return f"00-{short_name}.md"
    
    def create_plan_folder(
        self,
        plan_id: str,
        title: str,
        complexity_tier: int,
        status: str = "active",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Create hierarchical folder structure for a plan.
        
        Args:
            plan_id: Unique plan identifier (e.g., "user-auth-v1")
            title: Human-readable plan title
            complexity_tier: Plan complexity (1=INSTANT, 2=LIGHTWEIGHT, 3=DOCUMENTED, 4=COMPLEX)
            status: Plan status ("active", "temp-plans", "completed")
            metadata: Optional additional metadata for tracking
        
        Returns:
            Path to created plan folder
        
        Raises:
            ValueError: If status is invalid or plan_id already exists
            OSError: If folder creation fails
        
        Example:
            >>> manager = PlanFolderManager(Path("/cortex"))
            >>> folder = manager.create_plan_folder(
            ...     plan_id="auth-v1",
            ...     title="User Authentication",
            ...     complexity_tier=3,
            ...     status="active"
            ... )
            >>> print(folder)
            /cortex/cortex-brain/documents/planning/active/auth-v1
        """
        # Validate status
        valid_statuses = ["active", "temp-plans", "completed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        
        # Construct folder path
        status_folder = self.planning_root / status
        plan_folder = status_folder / plan_id
        
        # Check for existing plan
        if plan_folder.exists():
            raise ValueError(f"Plan folder already exists: {plan_folder}")
        
        try:
            # Create parent status folder if needed
            status_folder.mkdir(parents=True, exist_ok=True)
            
            # Create plan folder
            plan_folder.mkdir(parents=False, exist_ok=False)
            logger.info(f"✅ Created plan folder: {plan_folder}")
            
            # Create required subfolders
            self._create_subfolders(plan_folder)
            
            # Initialize progress tracker
            self._initialize_tracker(plan_folder, plan_id, title, complexity_tier, metadata)
            
            # Generate README
            self._generate_readme(plan_folder, plan_id, title, complexity_tier, status)
            
            logger.info(f"🎉 Plan folder structure complete: {plan_id}")
            return plan_folder
            
        except Exception as e:
            # Rollback on failure (atomic operation)
            if plan_folder.exists():
                logger.warning(f"⚠️ Rolling back failed folder creation: {plan_folder}")
                self._cleanup_folder(plan_folder)
            raise OSError(f"Failed to create plan folder: {e}") from e
    
    def _create_subfolders(self, plan_folder: Path) -> None:
        """Create required subfolders."""
        for subfolder in self.REQUIRED_SUBFOLDERS:
            subfolder_path = plan_folder / subfolder
            subfolder_path.mkdir(parents=False, exist_ok=False)
            logger.debug(f"  📂 Created: {subfolder}/")
    
    def _initialize_tracker(
        tier_names = {1: "INSTANT", 2: "LIGHTWEIGHT", 3: "DOCUMENTED", 4: "COMPLEX"}
        tier_name = tier_names.get(complexity_tier, "UNKNOWN")
        
        master_plan_filename = self._generate_master_plan_filename(plan_id)
        
        readme_content = f"""# {title}

**Plan ID:** {plan_id}  
**Status:** {status}  
**Complexity:** Tier {complexity_tier} ({tier_name})  
**Created:** {datetime.now().strftime("%B %d, %Y")}

---

## 📁 Folder Structure

```
{plan_id}/
├── {master_plan_filename}           # Human-readable master plan
            "metadata": metadata or {}
        }
        
        tracker_path.parent.mkdir(parents=True, exist_ok=True)
        tracker_path.write_text(json.dumps(tracker_data, indent=2))
        logger.debug(f"  📊 Initialized: {self.TRACKER_NAME}")
    
    def _generate_readme(
        self,
        plan_folder: Path,
        plan_id: str,
        title: str,
        complexity_tier: int,
        status: str
    ) -> None:
        """Generate README.md with plan overview."""
        readme_path = plan_folder / self.README_NAME
        
        tier_names = {1: "INSTANT", 2: "LIGHTWEIGHT", 3: "DOCUMENTED", 4: "COMPLEX"}
        tier_name = tier_names.get(complexity_tier, "UNKNOWN")
        
        readme_content = f"""# {title}

**Plan ID:** {plan_id}  
**Status:** {status}  
**Complexity:** Tier {complexity_tier} ({tier_name})  
**Created:** {datetime.now().strftime("%B %d, %Y")}

---

## 📁 Folder Structure

```
{plan_id}/
├── 00-master-plan.md           # Human-readable master plan
├── execution/
│   └── 00-master-plan.yaml     # Machine-executable YAML
├── tracking/
│   └── progress-tracker.json   # Progress tracking
├── reports/
│   └── phase-completion/       # Phase reports
├── artifacts/
│   └── generated-files/        # Supporting artifacts
└── context/
    └── requirements.md          # Context documents
---

## 🎯 Quick Reference

- **Master Plan:** [`{master_plan_filename}`](./{master_plan_filename})
- **Progress Tracker:** [`tracking/progress-tracker.json`](./tracking/progress-tracker.json)
- **Execution YAML:** [`execution/00-master-plan.yaml`](./execution/00-master-plan.yaml)
- **Progress Tracker:** [`tracking/progress-tracker.json`](./tracking/progress-tracker.json)
- **Execution YAML:** [`execution/00-master-plan.yaml`](./execution/00-master-plan.yaml)

---

**Generated by:** CORTEX Planning System 4.0  
**Manifest:** `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`
"""
        
        readme_path.write_text(readme_content, encoding='utf-8')
        logger.debug(f"  📄 Generated: {self.README_NAME}")
    
    def _cleanup_folder(self, plan_folder: Path) -> None:
        """Recursively delete folder (rollback on failure)."""
        import shutil
        if plan_folder.exists() and plan_folder.is_dir():
            shutil.rmtree(plan_folder)
            logger.debug(f"🗑️ Cleaned up: {plan_folder}")
    
    def get_plan_folder(self, plan_id: str, status: str = "active") -> Optional[Path]:
        """
        Get existing plan folder path.
        
        Args:
            plan_id: Plan identifier
            status: Plan status folder
        
        Returns:
            Path to plan folder if exists, None otherwise
        """
        plan_folder = self.planning_root / status / plan_id
        return plan_folder if plan_folder.exists() else None
    
    def move_plan(self, plan_id: str, from_status: str, to_status: str) -> Path:
        """
        Move plan between status folders (e.g., temp-plans → active).
        
        Args:
            plan_id: Plan identifier
            from_status: Source status folder
            to_status: Target status folder
        
        Returns:
            New plan folder path
        
        Raises:
            ValueError: If source doesn't exist or target already exists
        """
        from_folder = self.planning_root / from_status / plan_id
        to_folder = self.planning_root / to_status / plan_id
        
        if not from_folder.exists():
            raise ValueError(f"Source plan folder not found: {from_folder}")
        
        if to_folder.exists():
            raise ValueError(f"Target plan folder already exists: {to_folder}")
        
        # Ensure target status folder exists
        to_folder.parent.mkdir(parents=True, exist_ok=True)
        
        # Move folder
        from_folder.rename(to_folder)
        logger.info(f"📦 Moved plan: {from_status}/{plan_id} → {to_status}/{plan_id}")
        
        return to_folder
    
    def detect_next_version(self, base_plan_name: str, status: str = "active") -> int:
        """
        Detect next version number for a plan.
        
        Args:
            base_plan_name: Base plan name (e.g., "user-auth")
            status: Status folder to search
        
        Returns:
            Next version number (1 if no existing versions)
        
        Example:
            >>> # Existing: user-auth-v1, user-auth-v2
            >>> manager.detect_next_version("user-auth")
            3
        """
        status_folder = self.planning_root / status
        
        if not status_folder.exists():
            return 1
        
        # Find all matching versions
        versions = []
        for folder in status_folder.iterdir():
            if folder.is_dir() and folder.name.startswith(f"{base_plan_name}-v"):
                try:
                    version_str = folder.name.split("-v")[-1]
                    versions.append(int(version_str))
                except (ValueError, IndexError):
                    continue
        
        return max(versions) + 1 if versions else 1
    
    def validate_folder_structure(self, plan_folder: Path) -> Tuple[bool, List[str]]:
        """
        Validate plan folder has required structure.
        
        Args:
            plan_folder: Path to plan folder
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check folder exists
        if not plan_folder.exists():
            return False, [f"Plan folder does not exist: {plan_folder}"]
        
        # Check required subfolders
        for subfolder in self.REQUIRED_SUBFOLDERS:
            subfolder_path = plan_folder / subfolder
            if not subfolder_path.exists():
                issues.append(f"Missing required subfolder: {subfolder}/")
        
        # Check master plan or temp plan exists
        master_plan = plan_folder / self.MASTER_PLAN_NAME
        temp_plan = plan_folder / self.TEMP_PLAN_NAME
        
        if not master_plan.exists() and not temp_plan.exists():
            issues.append(f"Missing {self.MASTER_PLAN_NAME} or {self.TEMP_PLAN_NAME}")
        
        # Check progress tracker
        tracker_path = plan_folder / self.TRACKER_NAME
        if not tracker_path.exists():
            issues.append(f"Missing {self.TRACKER_NAME}")
        
        is_valid = len(issues) == 0
        return is_valid, issues
