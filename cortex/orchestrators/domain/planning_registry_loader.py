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

from cortex.brain.core.result import Result, Ok, Err
from cortex.brain.core.path_resolver import resolve_path

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
