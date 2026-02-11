"""
Registry-Based Phase Data Loader

Loads phase data from cortex-registry/planning/ structure instead of _workspaces/roadmap/.

Features:
- YAML-based phase registration
- Hierarchical domain support (cortex-registry/domains/*/planning/)
- In-memory caching
- Result<T, E> error handling

Authority: AC-PLANNING-CONSOLIDATED-001
Author: GitHub Copilot
Date: 2026-01-25
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.brain.core.path_resolver import resolve_path
from cortex.brain.core.result import Err, Ok, Result

logger = logging.getLogger(__name__)


class RegistryPathNotFoundError(Exception):
    """Raised when registry path does not exist."""
    pass


class RegistryYAMLParseError(Exception):
    """Raised when YAML parsing fails."""
    pass


# ============================================================================
# NAMING FACTORY (AC-PLANNING-NAMING-001)
# ============================================================================


class NamingFactory:
    """
    Naming utilities for plan folder names.

    Features:
    - Kebab-case conversion
    - Domain inference from descriptions
    - Folder name generation
    - Folder name validation

    AC-PLANNING-NAMING-001: Naming Factory Utilities
    """

    # Domain keywords for inference
    DOMAIN_KEYWORDS = {
        "docs": ["documentation", "guide", "readme", "tutorial", "manual", "reference", "architectural", "diagram"],
        "planning": ["plan", "roadmap", "schedule", "timeline", "phase"],
        "core": ["database", "queue", "storage", "infrastructure", "layer", "persistence", "service bus"],
        "api": ["api", "endpoint", "graphql", "rest"],
    }

    def to_kebab_case(self, text: str) -> str:
        """
        Convert text to kebab-case.

        Args:
            text: Input text

        Returns:
            Kebab-case string
        """
        # Replace underscores and spaces with hyphens
        text = re.sub(r"[_\s]+", "-", text)

        # Handle camelCase: insert hyphen before capitals
        text = re.sub(r"([a-z])([A-Z])", r"\1-\2", text)

        # Remove special characters except hyphens and numbers
        text = re.sub(r"[^a-z0-9\-\.]", "-", text.lower())

        # Remove consecutive hyphens
        text = re.sub(r"-+", "-", text)

        # Remove leading/trailing hyphens
        text = text.strip("-")

        return text

    def infer_domain(self, description: str) -> str:
        """
        Infer domain from description.

        Args:
            description: Plan description

        Returns:
            Domain name (docs, planning, api, core, or general)
        """
        if not description:
            return "general"

        description_lower = description.lower()

        # Check each domain's keywords
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return domain

        return "general"

    def generate_folder_name(self, request: Dict[str, Any]) -> str:
        """
        Generate folder name from request.

        Args:
            request: Dictionary with 'name', 'description', optional 'domain'

        Returns:
            Kebab-case folder name
        """
        name = request.get("name", "")
        description = request.get("description", "")
        domain = request.get("domain")

        if not name:
            name = description or "unnamed"

        # Convert to kebab-case
        folder_name = self.to_kebab_case(name)

        # Infer domain if not provided
        if not domain:
            domain = self.infer_domain(description)

        # Append domain if not "general"
        if domain and domain != "general":
            # Domain is typically used for folder structure, not name
            pass

        return folder_name

    def validate_folder_name(self, name: str) -> bool:
        """
        Validate folder name.

        Rules:
        - Not empty
        - Only alphanumeric, hyphens, dots
        - No leading/trailing hyphens
        - No consecutive hyphens
        - Max 255 characters

        Args:
            name: Folder name to validate

        Returns:
            True if valid, False otherwise
        """
        if not name or len(name.strip()) == 0:
            return False

        if len(name) > 255:
            return False

        # Must match pattern: alphanumeric, hyphens, dots
        # No leading/trailing hyphens
        # No consecutive hyphens
        pattern = r"^[a-z0-9][a-z0-9\.\-]*[a-z0-9]$|^[a-z0-9]$"
        if not re.match(pattern, name):
            return False

        # Check for consecutive hyphens
        if "--" in name or ".." in name:
            return False

        return True


class PlanningRegistryLoader:
    """
    Loads phase data from cortex-registry/planning/ structure.

    Hierarchy:
    - cortex-registry/planning/index.yaml (main registry)
    - cortex-registry/planning/*.yaml (individual phase files)
    - cortex-registry/domains/{domain}/planning/*.yaml (domain-specific phases)

    Features:
    - YAML-based phase registration
    - Hierarchical domain support
    - In-memory caching
    - Naming factory for kebab-case folder generation
    """

    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize registry loader.

        Args:
            registry_path: Path to cortex-registry folder. If None, auto-resolves.

        Raises:
            RegistryPathNotFoundError: If registry path does not exist.
        """
        if registry_path is None:
            # Auto-resolve cortex-registry path
            registry_path = resolve_path("cortex-registry")

        self.registry_path = Path(registry_path)
        self.planning_path = self.registry_path / "planning"
        self._phase_cache: Dict[str, Any] = {}
        self._initialized = False
        self.naming_factory = NamingFactory()  # Add naming factory

        # Validate paths exist
        if not self.registry_path.exists():
            raise RegistryPathNotFoundError(
                f"Registry path not found: {self.registry_path}"
            )

        if not self.planning_path.exists():
            logger.warning(f"Planning path not found: {self.planning_path}")

    def load_all_phases(self) -> Result[Dict[str, Any]]:
        """
        Load all phases from registry.

        Returns:
            Result containing dictionary of all phases, or error.
        """
        try:
            phases = {}

            # Load main index
            index_result = self._load_index()
            if index_result.is_err():
                return index_result

            phases.update(index_result.unwrap())

            # Load individual phase files
            files_result = self._load_phase_files()
            if files_result.is_ok():
                phases.update(files_result.unwrap())

            # Load domain-specific phases
            domains_result = self._load_domain_phases()
            if domains_result.is_ok():
                phases.update(domains_result.unwrap())

            self._phase_cache = phases
            self._initialized = True

            return Ok(phases)

        except Exception as e:
            error_msg = f"Failed to load phases: {str(e)}"
            logger.error(error_msg)
            return Err(error_msg)

    def load_phase(self, phase_id: str) -> Result[Dict[str, Any]]:
        """
        Load single phase by ID.

        Args:
            phase_id: Phase identifier (e.g., "PHASE-001").

        Returns:
            Result containing phase data, or error.
        """
        try:
            # Check cache first
            if phase_id in self._phase_cache:
                return Ok(self._phase_cache[phase_id])

            # Try to load from file
            phase_file = self.planning_path / f"{phase_id}.yaml"

            if phase_file.exists():
                phase_data = self._load_yaml(phase_file)
                self._phase_cache[phase_id] = phase_data
                return Ok(phase_data)

            return Err(f"Phase not found: {phase_id}")

        except Exception as e:
            error_msg = f"Failed to load phase {phase_id}: {str(e)}"
            logger.error(error_msg)
            return Err(error_msg)

    def load_domain_phases(self, domain: str) -> Result[Dict[str, Any]]:
        """
        Load all phases for a specific domain.

        Args:
            domain: Domain name (e.g., "orchestrator", "planning").

        Returns:
            Result containing domain phases, or error.
        """
        try:
            domain_planning_path = self.registry_path / "domains" / domain / "planning"

            if not domain_planning_path.exists():
                return Ok({})  # Empty if domain doesn't exist

            phases = {}

            for yaml_file in domain_planning_path.glob("*.yaml"):
                phase_id = yaml_file.stem
                phase_data = self._load_yaml(yaml_file)
                phases[f"{domain}_{phase_id}"] = phase_data

            return Ok(phases)

        except Exception as e:
            error_msg = f"Failed to load domain phases for {domain}: {str(e)}"
            logger.error(error_msg)
            return Err(error_msg)

    def get_cached_phases(self) -> Dict[str, Any]:
        """Get currently cached phases."""
        return self._phase_cache.copy()

    def clear_cache(self) -> None:
        """Clear phase cache."""
        self._phase_cache = {}
        self._initialized = False

    # ========================================================================
    # NAMING FACTORY DELEGATES (AC-PLANNING-NAMING-001)
    # ========================================================================

    def to_kebab_case(self, text: str) -> str:
        """
        Delegate to naming factory: Convert text to kebab-case.

        Args:
            text: Input text

        Returns:
            Kebab-case string
        """
        return self.naming_factory.to_kebab_case(text)

    def infer_domain(self, description: str) -> str:
        """
        Delegate to naming factory: Infer domain from description.

        Args:
            description: Plan description

        Returns:
            Domain name
        """
        return self.naming_factory.infer_domain(description)

    def generate_folder_name(self, request: Dict[str, Any]) -> str:
        """
        Delegate to naming factory: Generate folder name from request.

        Args:
            request: Dictionary with 'name', 'description', optional 'domain'

        Returns:
            Kebab-case folder name
        """
        return self.naming_factory.generate_folder_name(request)

    def validate_folder_name(self, name: str) -> bool:
        """
        Delegate to naming factory: Validate folder name.

        Args:
            name: Folder name to validate

        Returns:
            True if valid, False otherwise
        """
        return self.naming_factory.validate_folder_name(name)

    # ========================================================================
    # REGISTRY BUILDER METHODS (AC-PLANNING-BUILDER-001)
    # ========================================================================

    def initialize_planning_registry(self) -> Result[None]:
        """
        Initialize planning registry structure.

        Creates:
        - cortex-registry/planning/ folder
        - cortex-registry/planning/index.yaml
        - cortex-registry/domains/ folder

        Returns:
            Result indicating success or error
        """
        try:
            # Create planning folder
            self.planning_path.mkdir(parents=True, exist_ok=True)

            # Create domains folder
            domains_path = self.registry_path / "domains"
            domains_path.mkdir(parents=True, exist_ok=True)

            # Create index.yaml if not exists
            index_file = self.planning_path / "index.yaml"
            if not index_file.exists():
                index_data = {
                    "version": "1.0",
                    "description": "Planning Registry Index",
                    "plans": [],
                }
                with open(index_file, "w", encoding="utf-8") as f:
                    yaml.dump(index_data, f, default_flow_style=False)
                logger.info(f"Created index.yaml at {index_file}")

            logger.info("Planning registry initialized")
            return Ok(None)

        except Exception as e:
            error_msg = f"Failed to initialize planning registry: {str(e)}"
            logger.error(error_msg)
            return Err(error_msg)

    def create_plan_folder(
        self,
        domain: str,
        plan_name: str,
    ) -> Result[Path]:
        """
        Create plan folder structure.

        Creates:
        - cortex-registry/planning/{domain}/{plan-name}/
        - cortex-registry/planning/{domain}/{plan-name}/temp/
        - cortex-registry/planning/{domain}/{plan-name}/artifacts/

        Args:
            domain: Domain name (e.g., 'planning', 'docs', 'api')
            plan_name: Plan name (converted to kebab-case)

        Returns:
            Result containing folder path, or error if name invalid
        """
        try:
            # Validate folder name
            if not self.validate_folder_name(plan_name):
                error_msg = f"Invalid plan name: {plan_name}"
                logger.error(error_msg)
                return Err(error_msg)

            # Create folder structure
            plan_folder = self.planning_path / domain / plan_name
            plan_folder.mkdir(parents=True, exist_ok=True)

            # Create subdirectories
            (plan_folder / "temp").mkdir(exist_ok=True)
            (plan_folder / "artifacts").mkdir(exist_ok=True)

            logger.info(f"Created plan folder: {plan_folder}")
            return Ok(plan_folder)

        except Exception as e:
            error_msg = f"Failed to create plan folder: {str(e)}"
            logger.error(error_msg)
            return Err(error_msg)

    def register_plan(
        self,
        domain: str,
        plan_data: Dict[str, Any],
    ) -> Result[str]:
        """
        Register plan in registry.

        Writes:
        - plan.yaml (plan specification)
        - metadata.yaml (plan metadata)

        Updates:
        - index.yaml (domain index)

        Args:
            domain: Domain name
            plan_data: Plan specification (must have 'name')

        Returns:
            Result containing plan ID (folder name), or error
        """
        try:
            # Extract plan name and convert to kebab-case
            plan_name = plan_data.get("name", "unnamed-plan")
            plan_id = self.to_kebab_case(plan_name)

            # Create plan folder
            folder_result = self.create_plan_folder(domain, plan_id)
            if folder_result.is_err():
                return Err(folder_result.unwrap_err())

            plan_folder = folder_result.unwrap()

            # Write plan.yaml
            plan_file = plan_folder / "plan.yaml"
            with open(plan_file, "w", encoding="utf-8") as f:
                yaml.dump(plan_data, f, default_flow_style=False)
            logger.info(f"Wrote plan.yaml: {plan_file}")

            # Create and write metadata.yaml
            metadata = {
                "plan_id": plan_id,
                "domain": domain,
                "created_at": "2026-01-26T00:00:00Z",
                "epics": [],
                "features": [],
                "linked_phases": [],
            }
            metadata_file = plan_folder / "metadata.yaml"
            with open(metadata_file, "w", encoding="utf-8") as f:
                yaml.dump(metadata, f, default_flow_style=False)
            logger.info(f"Wrote metadata.yaml: {metadata_file}")

            # Update domain index
            domain_index_file = self.planning_path / domain / "index.yaml"
            domain_index_file.parent.mkdir(parents=True, exist_ok=True)

            # Load or create domain index
            if domain_index_file.exists():
                with open(domain_index_file, "r", encoding="utf-8") as f:
                    domain_index = yaml.safe_load(f) or {}
            else:
                domain_index = {"plans": []}

            # Add plan to index
            if "plans" not in domain_index:
                domain_index["plans"] = []

            plan_entry = {
                "id": plan_id,
                "name": plan_name,
                "folder": str(plan_folder.relative_to(self.registry_path)),
            }

            if plan_entry not in domain_index["plans"]:
                domain_index["plans"].append(plan_entry)

            # Write domain index
            with open(domain_index_file, "w", encoding="utf-8") as f:
                yaml.dump(domain_index, f, default_flow_style=False)
            logger.info(f"Updated domain index: {domain_index_file}")

            return Ok(plan_id)

        except Exception as e:
            error_msg = f"Failed to register plan: {str(e)}"
            logger.error(error_msg)
            return Err(error_msg)

    def validate_metadata_schema(
        self,
        metadata: Dict[str, Any],
    ) -> Result[None]:
        """
        Validate plan metadata against schema.

        Required fields:
        - plan_id (str)
        - created_at (str, ISO format)

        Optional fields:
        - epics (list of strings)
        - features (list of strings)
        - linked_phases (list of integers)

        Args:
            metadata: Metadata dictionary to validate

        Returns:
            Result indicating valid or error message
        """
        try:
            # Check required fields
            required_fields = ["plan_id", "created_at"]
            for field in required_fields:
                if field not in metadata:
                    error_msg = f"Missing required field: {field}"
                    logger.error(error_msg)
                    return Err(error_msg)

            # Validate types
            if not isinstance(metadata["plan_id"], str):
                error_msg = "plan_id must be string"
                return Err(error_msg)

            if not isinstance(metadata["created_at"], str):
                error_msg = "created_at must be string (ISO format)"
                return Err(error_msg)

            # Validate optional list fields
            optional_lists = ["epics", "features", "linked_phases"]
            for field in optional_lists:
                if field in metadata and not isinstance(metadata[field], list):
                    error_msg = f"{field} must be list or absent"
                    return Err(error_msg)

            logger.info("Metadata schema validation passed")
            return Ok(None)

        except Exception as e:
            error_msg = f"Metadata validation failed: {str(e)}"
            logger.error(error_msg)
            return Err(error_msg)

    def regenerate_index_from_filesystem(self) -> Result[None]:
        """
        Regenerate registry index from filesystem scan.

        Scans cortex-registry/planning/{domain}/ folders and updates index.yaml files.

        Returns:
            Result indicating success or error
        """
        try:
            if not self.planning_path.exists():
                logger.warning(f"Planning path not found: {self.planning_path}")
                return Ok(None)

            # Scan each domain folder
            for domain_folder in self.planning_path.iterdir():
                if not domain_folder.is_dir() or domain_folder.name == "temp":
                    continue

                domain_name = domain_folder.name
                domain_index = {"plans": []}

                # Scan plan folders
                for plan_folder in domain_folder.iterdir():
                    if not plan_folder.is_dir():
                        continue

                    plan_id = plan_folder.name

                    # Read metadata if exists
                    metadata_file = plan_folder / "metadata.yaml"
                    plan_name = plan_id  # Default to folder name

                    if metadata_file.exists():
                        try:
                            with open(metadata_file, "r", encoding="utf-8") as f:
                                metadata = yaml.safe_load(f) or {}
                            plan_name = metadata.get("name", plan_id)
                        except Exception as e:
                            logger.warning(f"Failed to read metadata: {e}")

                    # Add to index
                    plan_entry = {
                        "id": plan_id,
                        "name": plan_name,
                        "folder": str(plan_folder.relative_to(self.registry_path)),
                    }
                    domain_index["plans"].append(plan_entry)

                # Write domain index.yaml
                domain_index_file = domain_folder / "index.yaml"
                with open(domain_index_file, "w", encoding="utf-8") as f:
                    yaml.dump(domain_index, f, default_flow_style=False)
                logger.info(f"Regenerated index: {domain_index_file}")

            logger.info("Index regeneration complete")
            return Ok(None)

        except Exception as e:
            error_msg = f"Failed to regenerate index: {str(e)}"
            logger.error(error_msg)
            return Err(error_msg)

    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================

    def _load_index(self) -> Result[Dict[str, Any]]:
        """Load main index.yaml."""
        try:
            index_file = self.planning_path / "index.yaml"

            if not index_file.exists():
                logger.info(f"Index file not found: {index_file}")
                return Ok({})

            data = self._load_yaml(index_file)
            return Ok(data.get("plan_types", {}))

        except Exception as e:
            error_msg = f"Failed to load index: {str(e)}"
            logger.error(error_msg)
            return Err(error_msg)

    def _load_phase_files(self) -> Result[Dict[str, Any]]:
        """Load all individual phase files from planning/ folder."""
        try:
            phases = {}

            if not self.planning_path.exists():
                return Ok({})

            for yaml_file in self.planning_path.glob("*.yaml"):
                # Skip index.yaml
                if yaml_file.name == "index.yaml":
                    continue

                phase_id = yaml_file.stem
                phase_data = self._load_yaml(yaml_file)
                phases[phase_id] = phase_data

            return Ok(phases)

        except Exception as e:
            error_msg = f"Failed to load phase files: {str(e)}"
            logger.error(error_msg)
            return Err(error_msg)

    def _load_domain_phases(self) -> Result[Dict[str, Any]]:
        """Load all domain-specific phases."""
        try:
            domains_path = self.registry_path / "domains"
            phases = {}

            if not domains_path.exists():
                return Ok({})

            for domain_folder in domains_path.iterdir():
                if not domain_folder.is_dir():
                    continue

                domain_planning = domain_folder / "planning"

                if not domain_planning.exists():
                    continue

                for yaml_file in domain_planning.glob("*.yaml"):
                    phase_id = yaml_file.stem
                    phase_data = self._load_yaml(yaml_file)
                    phases[f"{domain_folder.name}_{phase_id}"] = phase_data

            return Ok(phases)

        except Exception as e:
            error_msg = f"Failed to load domain phases: {str(e)}"
            logger.error(error_msg)
            return Err(error_msg)

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """
        Load YAML file safely.

        Args:
            file_path: Path to YAML file.

        Returns:
            Parsed YAML as dictionary.

        Raises:
            RegistryYAMLParseError: If YAML parsing fails.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else {}

        except yaml.YAMLError as e:
            error_msg = f"YAML parsing error in {file_path}: {str(e)}"
            logger.error(error_msg)
            raise RegistryYAMLParseError(error_msg)

        except Exception as e:
            error_msg = f"Error loading {file_path}: {str(e)}"
            logger.error(error_msg)
            raise RegistryYAMLParseError(error_msg)

    # ========================================================================
    # PLAN MIGRATION METHODS (AC-PLANNING-MIGRATION-001)
    # ========================================================================

    def discover_legacy_plans(self, legacy_path: Path) -> List[Dict[str, Any]]:
        """Discover plans in legacy location.

        Args:
            legacy_path: Path to legacy plans folder

        Returns:
            List of discovered plan dictionaries
        """
        try:
            plans = []

            if not legacy_path.exists():
                logger.warning(f"Legacy path not found: {legacy_path}")
                return plans

            # Scan for YAML and JSON files
            for ext in ["*.yaml", "*.yml", "*.json"]:
                for plan_file in legacy_path.glob(ext):
                    try:
                        with open(plan_file, "r") as f:
                            if plan_file.suffix in [".yaml", ".yml"]:
                                plan_data = yaml.safe_load(f)
                            else:
                                import json
                                plan_data = json.load(f)

                            if plan_data and isinstance(plan_data, dict):
                                plans.append(plan_data)
                    except Exception as e:
                        logger.warning(f"Failed to read {plan_file}: {str(e)}")

            logger.info(f"Discovered {len(plans)} legacy plans")
            return plans

        except Exception as e:
            logger.error(f"Legacy plan discovery failed: {str(e)}")
            return []

    def infer_domain_from_plan(self, plan_data: Dict[str, Any]) -> str:
        """Infer domain from plan data.

        Args:
            plan_data: Plan dictionary

        Returns:
            Inferred domain or 'general' as fallback
        """
        try:
            # Check for explicit domain
            if "domain" in plan_data:
                return plan_data["domain"]

            # Infer from description
            description = plan_data.get("description", "").lower()
            name = plan_data.get("name", "").lower()
            combined = f"{description} {name}"

            # Domain keywords (same as NamingFactory)
            domain_keywords = {
                "docs": ["documentation", "doc", "guide", "tutorial", "reference"],
                "planning": ["plan", "planning", "orchestrat"],
                "api": ["api", "rest", "endpoint", "request", "response"],
                "core": ["core", "central", "main", "infrastructure"],
            }

            for domain, keywords in domain_keywords.items():
                for keyword in keywords:
                    if keyword in combined:
                        return domain

            return "general"

        except Exception as e:
            logger.warning(f"Domain inference failed: {str(e)}")
            return "general"

    def detect_duplicate_plans(self, legacy_path: Path) -> List[Dict[str, Any]]:
        """Detect duplicate plans in legacy location.

        Args:
            legacy_path: Path to legacy plans

        Returns:
            List of duplicate plan groups
        """
        try:
            import hashlib

            plan_checksums: Dict[str, List[Path]] = {}
            duplicates = []

            for plan_file in legacy_path.glob("*.yaml"):
                try:
                    with open(plan_file, "rb") as f:
                        content_hash = hashlib.md5(f.read()).hexdigest()

                    if content_hash not in plan_checksums:
                        plan_checksums[content_hash] = []

                    plan_checksums[content_hash].append(plan_file)
                except Exception as e:
                    logger.warning(f"Failed to hash {plan_file}: {str(e)}")

            # Collect duplicates
            for file_list in plan_checksums.values():
                if len(file_list) > 1:
                    duplicates.append({"files": [str(f) for f in file_list]})

            logger.info(f"Found {len(duplicates)} duplicate plan groups")
            return duplicates

        except Exception as e:
            logger.error(f"Duplicate detection failed: {str(e)}")
            return []

    def resolve_duplicate_plan_ids(self, plans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve plans with duplicate IDs.

        Args:
            plans: List of plans that may have duplicate IDs

        Returns:
            List of plans with resolved IDs
        """
        try:
            seen_ids: Dict[str, int] = {}
            resolved = []

            for plan in plans:
                plan_id = plan.get("plan_id", "unknown")

                if plan_id in seen_ids:
                    # Add suffix to make unique
                    seen_ids[plan_id] += 1
                    plan["plan_id"] = f"{plan_id}_v{seen_ids[plan_id]}"
                    plan["original_id"] = plan_id
                else:
                    seen_ids[plan_id] = 1

                resolved.append(plan)

            logger.info(f"Resolved {len(plans)} plans with duplicate IDs")
            return resolved

        except Exception as e:
            logger.error(f"Duplicate ID resolution failed: {str(e)}")
            return plans
