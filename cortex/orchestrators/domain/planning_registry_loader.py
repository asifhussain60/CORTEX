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


class PlanningRegistryLoader:
    """
    Loads phase data from cortex-registry/planning/ structure.
    
    Hierarchy:
    - cortex-registry/planning/index.yaml (main registry)
    - cortex-registry/planning/*.yaml (individual phase files)
    - cortex-registry/domains/{domain}/planning/*.yaml (domain-specific phases)
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
