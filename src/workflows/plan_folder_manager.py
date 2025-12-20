"""
Plan Folder Manager - Hierarchical Folder Structure for Planning Artifacts

Manages folder-based organization of planning artifacts with feature flag control.

Author: GitHub Copilot
Created: 2025-12-14
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Union

logger = logging.getLogger(__name__)


class PlanFolderManager:
    """
    Manages hierarchical folder structure for planning artifacts.
    
    Folder Structure:
    ```
    PLAN-{date}-{name}/
    ├── master-plan.md
    ├── README.md
    ├── sub-plans/
    ├── artifacts/
    ├── reports/
    ├── tests/
    └── checkpoints/
    ```
    
    Feature Flag: cortex.config.json::planning.use_folder_structure (default: true)
    """
    
    def __init__(self, cortex_root: Union[Path, str]):
        """
        Initialize PlanFolderManager.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root)
        self.plans_base = self.cortex_root / "cortex-brain" / "documents" / "planning" / "features"
        self.config_path = self.cortex_root / "cortex.config.json"
        
        # Create base directory structure
        self._ensure_base_directories()
        
        # Load feature flag
        self._feature_flag_enabled = self._load_feature_flag()
        
        logger.info(f"PlanFolderManager initialized (folder_structure={'enabled' if self._feature_flag_enabled else 'disabled'})")
    
    def _ensure_base_directories(self):
        """Create base directory structure if it doesn't exist."""
        for status in ["active", "completed", "archived"]:
            status_dir = self.plans_base / status
            status_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_feature_flag(self) -> bool:
        """
        Load feature flag from cortex.config.json.
        
        Returns:
            bool: True if folder structure is enabled, False otherwise (default: True)
        """
        if not self.config_path.exists():
            return True  # Default: enabled
        
        try:
            config = json.loads(self.config_path.read_text())
            return config.get("planning", {}).get("use_folder_structure", True)
        except Exception as e:
            logger.warning(f"Failed to load feature flag: {e}, defaulting to enabled")
            return True
    
    def _save_feature_flag(self, enabled: bool):
        """
        Save feature flag to cortex.config.json.
        
        Args:
            enabled: True to enable folder structure, False to disable
        """
        if not self.config_path.exists():
            config = {}
        else:
            try:
                config = json.loads(self.config_path.read_text())
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                config = {}
        
        if "planning" not in config:
            config["planning"] = {}
        
        config["planning"]["use_folder_structure"] = enabled
        
        self.config_path.write_text(json.dumps(config, indent=2))
        self._feature_flag_enabled = enabled
        
        logger.info(f"Feature flag updated: folder_structure={'enabled' if enabled else 'disabled'}")
    
    def is_folder_structure_enabled(self) -> bool:
        """
        Check if folder structure is enabled.
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self._feature_flag_enabled
    
    def set_folder_structure_enabled(self, enabled: bool):
        """
        Enable or disable folder structure.
        
        Args:
            enabled: True to enable, False to disable
        """
        self._save_feature_flag(enabled)
    
    def create_plan_structure(self, plan_id: str, status: str = "active") -> Optional[Path]:
        """
        Create hierarchical folder structure for a plan.
        
        Args:
            plan_id: Plan identifier (e.g., "PLAN-2025-12-14-feature-name")
            status: Plan status ("active", "completed", or "archived")
        
        Returns:
            Path to plan root folder, or None if feature flag is disabled
        """
        if not self.is_folder_structure_enabled():
            logger.info(f"Folder structure disabled, skipping creation for {plan_id}")
            return None
        
        # Determine plan root path
        plan_root = self.plans_base / status / plan_id
        
        try:
            # Create root folder
            plan_root.mkdir(parents=True, exist_ok=False)
            
            # Create subfolders (atomic - all or nothing)
            subfolders = ["sub-plans", "artifacts", "reports", "tests", "checkpoints"]
            for subfolder in subfolders:
                (plan_root / subfolder).mkdir(exist_ok=True)
            
            # Generate README.md placeholder
            self._generate_readme_placeholder(plan_root, plan_id)
            
            logger.info(f"Created plan structure: {plan_root}")
            return plan_root
            
        except FileExistsError:
            logger.warning(f"Plan folder already exists: {plan_root}")
            return plan_root
        except Exception as e:
            # Rollback on error (atomic)
            if plan_root.exists():
                shutil.rmtree(plan_root)
            logger.error(f"Failed to create plan structure: {e}")
            raise
    
    def _generate_readme_placeholder(self, plan_root: Path, plan_id: str):
        """
        Generate placeholder README.md.
        
        Args:
            plan_root: Path to plan root folder
            plan_id: Plan identifier
        """
        readme_content = f"""# {plan_id}

**Status:** In Progress  
**Created:** {datetime.now().strftime("%Y-%m-%d")}

---

## Folder Structure

- **master-plan.md** - Main plan document
- **sub-plans/** - Phase-specific sub-plans
- **artifacts/** - Generated artifacts (trackers, graphs)
- **reports/** - Status reports and completion summaries
- **tests/** - Test plans and results
- **checkpoints/** - Git checkpoint metadata

---

## Files

_Files will be listed here after generation_

---

**Auto-generated by PlanFolderManager**
"""
        readme_path = plan_root / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")
    
    def get_plan_path(self, plan_id: str) -> Optional[Path]:
        """
        Find path to master plan file.
        
        Searches in order: active → completed → archived
        
        Args:
            plan_id: Plan identifier
        
        Returns:
            Path to master-plan.md, or None if not found
        """
        for status in ["active", "completed", "archived"]:
            plan_folder = self.plans_base / status / plan_id
            
            if plan_folder.exists() and plan_folder.is_dir():
                master_plan = plan_folder / "master-plan.md"
                if master_plan.exists():
                    return master_plan
                else:
                    # Folder exists but no master plan yet
                    return master_plan  # Return path even if file doesn't exist
        
        return None
    
    def get_artifact_path(
        self, 
        plan_id: str, 
        artifact_type: str, 
        filename: Optional[str] = None
    ) -> Optional[Path]:
        """
        Get path for specific artifact within plan folder.
        
        Args:
            plan_id: Plan identifier
            artifact_type: Type of artifact ("master", "sub-plan", "tracker", "report", "test", "checkpoint")
            filename: Specific filename (required for "sub-plan", "report", "test", "checkpoint")
        
        Returns:
            Path to artifact, or None if plan not found
        """
        # Find plan folder
        plan_folder = None
        for status in ["active", "completed", "archived"]:
            candidate = self.plans_base / status / plan_id
            if candidate.exists():
                plan_folder = candidate
                break
        
        if not plan_folder:
            return None
        
        # Map artifact type to path
        if artifact_type == "master":
            return plan_folder / "master-plan.md"
        
        elif artifact_type == "sub-plan":
            if not filename:
                raise ValueError("filename required for sub-plan artifact")
            return plan_folder / "sub-plans" / filename
        
        elif artifact_type == "tracker":
            return plan_folder / "artifacts" / "feature-tracker.md"
        
        elif artifact_type == "report":
            if not filename:
                raise ValueError("filename required for report artifact")
            return plan_folder / "reports" / filename
        
        elif artifact_type == "test":
            if not filename:
                raise ValueError("filename required for test artifact")
            return plan_folder / "tests" / filename
        
        elif artifact_type == "checkpoint":
            if not filename:
                raise ValueError("filename required for checkpoint artifact")
            return plan_folder / "checkpoints" / filename
        
        else:
            raise ValueError(f"Unknown artifact type: {artifact_type}")
    
    def move_plan(self, plan_id: str, from_status: str, to_status: str) -> Path:
        """
        Move plan folder from one status to another.
        
        Args:
            plan_id: Plan identifier
            from_status: Current status ("active", "completed", "archived")
            to_status: Target status ("active", "completed", "archived")
        
        Returns:
            Path to new plan location
        
        Raises:
            FileNotFoundError: If plan doesn't exist in from_status
        """
        from_path = self.plans_base / from_status / plan_id
        to_path = self.plans_base / to_status / plan_id
        
        if not from_path.exists():
            raise FileNotFoundError(f"Plan not found: {from_path}")
        
        # Move entire folder (preserves structure)
        shutil.move(str(from_path), str(to_path))
        
        logger.info(f"Moved plan: {from_path} → {to_path}")
        return to_path
    
    def generate_plan_readme(self, plan_id: str, metadata: Dict):
        """
        Generate comprehensive README.md with metadata and file index.
        
        Args:
            plan_id: Plan identifier
            metadata: Plan metadata (title, date, author, etc.)
        """
        # Find plan folder
        plan_folder = None
        for status in ["active", "completed", "archived"]:
            candidate = self.plans_base / status / plan_id
            if candidate.exists():
                plan_folder = candidate
                break
        
        if not plan_folder:
            logger.warning(f"Plan not found for README generation: {plan_id}")
            return
        
        # Extract metadata
        title = metadata.get("title", plan_id)
        created_date = metadata.get("created_date", "Unknown")
        author = metadata.get("author", "Unknown")
        priority = metadata.get("priority", "MEDIUM")
        
        # Scan for existing files
        file_index = self._generate_file_index(plan_folder)
        
        # Generate README content
        readme_content = f"""# {title}

**Plan ID:** {plan_id}  
**Created:** {created_date}  
**Author:** {author}  
**Priority:** {priority}

---

## Folder Structure

This plan follows the hierarchical folder structure:

- **master-plan.md** - Main plan document with phases and tasks
- **sub-plans/** - Detailed phase-specific sub-plans
- **artifacts/** - Generated artifacts (trackers, dependency graphs)
- **reports/** - Status reports and completion summaries
- **tests/** - Test plans and test results
- **checkpoints/** - Git checkpoint metadata

---

## Files

{file_index}

---

## Navigation

- [Master Plan](./master-plan.md)
- [Sub-Plans](./sub-plans/)
- [Artifacts](./artifacts/)
- [Reports](./reports/)
- [Tests](./tests/)
- [Checkpoints](./checkpoints/)

---

**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Generated by:** PlanFolderManager
"""
        
        readme_path = plan_folder / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")
        
        logger.info(f"Generated README for {plan_id}")
    
    def _generate_file_index(self, plan_folder: Path) -> str:
        """
        Generate file index section for README.
        
        Args:
            plan_folder: Path to plan folder
        
        Returns:
            Markdown formatted file index
        """
        sections = []
        
        # Master plan
        if (plan_folder / "master-plan.md").exists():
            sections.append("### Master Plan\n- [master-plan.md](./master-plan.md)")
        
        # Sub-plans
        sub_plans_dir = plan_folder / "sub-plans"
        if sub_plans_dir.exists():
            sub_plans = sorted(sub_plans_dir.glob("*.md"))
            if sub_plans:
                sub_plans_list = "\n".join([f"- [{sp.name}](./sub-plans/{sp.name})" for sp in sub_plans])
                sections.append(f"### Sub-Plans\n{sub_plans_list}")
        
        # Artifacts
        artifacts_dir = plan_folder / "artifacts"
        if artifacts_dir.exists():
            artifacts = sorted(artifacts_dir.glob("*"))
            if artifacts:
                artifacts_list = "\n".join([f"- [{a.name}](./artifacts/{a.name})" for a in artifacts])
                sections.append(f"### Artifacts\n{artifacts_list}")
        
        # Reports
        reports_dir = plan_folder / "reports"
        if reports_dir.exists():
            reports = sorted(reports_dir.glob("*.md"))
            if reports:
                reports_list = "\n".join([f"- [{r.name}](./reports/{r.name})" for r in reports])
                sections.append(f"### Reports\n{reports_list}")
        
        # Tests
        tests_dir = plan_folder / "tests"
        if tests_dir.exists():
            tests = sorted(tests_dir.glob("*.md"))
            if tests:
                tests_list = "\n".join([f"- [{t.name}](./tests/{t.name})" for t in tests])
                sections.append(f"### Tests\n{tests_list}")
        
        # Checkpoints
        checkpoints_dir = plan_folder / "checkpoints"
        if checkpoints_dir.exists():
            checkpoints = sorted(checkpoints_dir.glob("*.yaml"))
            if checkpoints:
                checkpoints_list = "\n".join([f"- [{c.name}](./checkpoints/{c.name})" for c in checkpoints])
                sections.append(f"### Checkpoints\n{checkpoints_list}")
        
        if not sections:
            return "_No files generated yet_"
        
        return "\n\n".join(sections)
    
    def list_plans(self, status: str = "active") -> List[str]:
        """
        List all plans in a given status.
        
        Args:
            status: Plan status ("active", "completed", "archived")
        
        Returns:
            List of plan IDs
        """
        status_dir = self.plans_base / status
        if not status_dir.exists():
            return []
        
        # Find all plan folders (directories starting with PLAN-)
        plan_folders = [
            d.name for d in status_dir.iterdir() 
            if d.is_dir() and d.name.startswith("PLAN-")
        ]
        
        return sorted(plan_folders)
