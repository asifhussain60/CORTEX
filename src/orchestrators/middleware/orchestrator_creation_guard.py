"""
OrchestratorCreationGuard Middleware - Enforce CORE-021 Governance Rule

CORE-021: New Orchestrators MUST Use Scaffolder
  - All new orchestrators MUST be created through OrchestratorScaffolder
  - Direct orchestrator creation is blocked
  - Ensures consistent structure, naming, and governance integration
  - Prevents ad-hoc orchestrator creation

Author: CORTEX Governance System
Version: 1.0.0
Created: 2026-01-12
"""

import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class OrchestratorType(Enum):
    """Types of orchestrators that can be created."""

    CORE = "core"  # Core workflow orchestrators (MasterOrchestrator, etc.)
    FEATURE = "feature"  # Feature-specific orchestrators
    UTILITY = "utility"  # Utility/helper orchestrators
    INTEGRATION = "integration"  # External integration orchestrators


@dataclass
class OrchestratorTemplate:
    """Template for a new orchestrator."""

    name: str
    type: OrchestratorType
    description: str
    base_class: str = "BaseOrchestrator"
    features: List[str] = None

    def __post_init__(self):
        if self.features is None:
            self.features = []


class OrchestratorCreationGuard:
    """Middleware to enforce CORE-021 orchestrator creation requirements."""

    ORCHESTRATOR_DIR = Path('src/orchestrators')

    # Valid orchestrator locations
    VALID_LOCATIONS = {
        'core': 'src/orchestrators/core',
        'feature': 'src/orchestrators/feature',
        'utility': 'src/orchestrators/utility',
        'integration': 'src/orchestrators/integration',
    }

    # Required files for new orchestrators
    REQUIRED_FILES = [
        'orchestrator.py',  # Main orchestrator implementation
        'config.yaml',  # Configuration file
        '__init__.py',  # Package initialization
    ]

    def __init__(self):
        self.scaffolder_available = self._check_scaffolder_available()

    def _check_scaffolder_available(self) -> bool:
        """
        Check if OrchestratorScaffolder is available.

        Returns:
            True if scaffolder is available
        """
        try:
            from src.orchestrators.scaffolding import orchestrator_scaffolder

            logger.info("✅ OrchestratorScaffolder is available")
            return True
        except ImportError:
            logger.warning("⚠️  OrchestratorScaffolder not yet available")
            return False

    def validate_orchestrator_creation(
        self, orch_name: str, orch_type: OrchestratorType
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that an orchestrator is being created through scaffolder.

        Args:
            orch_name: Name of orchestrator
            orch_type: Type of orchestrator

        Returns:
            Tuple of (is_valid: bool, reason: str or None)
        """
        if not self.scaffolder_available:
            return (
                False,
                "CORE-021 VIOLATION: OrchestratorScaffolder not available. "
                "Use scaffolder to create new orchestrators.",
            )

        # Check naming convention
        if not self._is_valid_orchestrator_name(orch_name):
            return (
                False,
                f"CORE-021 VIOLATION: Invalid orchestrator name '{orch_name}'. "
                f"Use kebab-case (lowercase, hyphens, underscores).",
            )

        return True, None

    def _is_valid_orchestrator_name(self, name: str) -> bool:
        """Check if orchestrator name follows conventions."""
        import re

        # Orchestrator names should be kebab-case
        if not re.match(r'^[a-z0-9]+(?:[_-][a-z0-9]+)*$', name):
            return False

        # Max 30 characters for orchestrator names
        if len(name) > 30:
            return False

        return True

    def get_scaffolder_command(
        self, orch_name: str, orch_type: OrchestratorType, description: str
    ) -> str:
        """
        Generate the scaffolder command for creating a new orchestrator.

        Args:
            orch_name: Orchestrator name
            orch_type: Orchestrator type
            description: Orchestrator description

        Returns:
            Scaffolder command
        """
        return (
            f"python3 -m src.main 'scaffold orchestrator --name {orch_name} "
            f"--type {orch_type.value} --description \"{description}\"'"
        )

    def detect_direct_orchestrator_creation(
        self, file_path: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Detect if someone is trying to create an orchestrator directly.

        Args:
            file_path: Path of file being created

        Returns:
            Tuple of (is_direct_creation: bool, reason: str or None)
        """
        path = Path(file_path)

        # Check if file is in orchestrator directories
        orchestrator_dirs = list(self.VALID_LOCATIONS.values())
        if not any(str(orch_dir) in str(path) for orch_dir in orchestrator_dirs):
            return False, None

        # Check if this looks like an orchestrator file
        if path.name in ['orchestrator.py', 'config.yaml', '__init__.py']:
            return (
                True,
                "CORE-021 VIOLATION: Direct orchestrator file creation detected. "
                "Use OrchestratorScaffolder instead.",
            )

        return False, None

    def list_existing_orchestrators(self) -> List[Dict]:
        """
        List all existing orchestrators.

        Returns:
            List of orchestrator information dicts
        """
        orchestrators = []

        for location_type, location_path in self.VALID_LOCATIONS.items():
            dir_path = Path(location_path)

            if not dir_path.exists():
                continue

            for orch_dir in dir_path.iterdir():
                if not orch_dir.is_dir():
                    continue

                if orch_dir.name.startswith('_'):
                    continue

                orchestrators.append({
                    'name': orch_dir.name,
                    'type': location_type,
                    'path': str(orch_dir),
                    'has_init': (orch_dir / '__init__.py').exists(),
                    'has_config': (orch_dir / 'config.yaml').exists(),
                    'has_orchestrator': (orch_dir / 'orchestrator.py').exists(),
                })

        return orchestrators

    def validate_orchestrator_structure(self, orch_path: str) -> Tuple[bool, List[str]]:
        """
        Validate that an orchestrator has required structure.

        Args:
            orch_path: Path to orchestrator

        Returns:
            Tuple of (is_valid: bool, missing_files: List[str])
        """
        orch_dir = Path(orch_path)
        missing_files = []

        for required_file in self.REQUIRED_FILES:
            file_path = orch_dir / required_file
            if not file_path.exists():
                missing_files.append(required_file)

        return len(missing_files) == 0, missing_files


class OrchestratorCreationBlockedException(Exception):
    """Exception raised when orchestrator creation violates CORE-021."""

    pass


# Public API
def validate_new_orchestrator(
    orch_name: str, orch_type: OrchestratorType
) -> Tuple[bool, str]:
    """
    Validate creating a new orchestrator.

    Args:
        orch_name: Orchestrator name
        orch_type: Orchestrator type

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    guard = OrchestratorCreationGuard()
    is_valid, reason = guard.validate_orchestrator_creation(orch_name, orch_type)

    if is_valid:
        command = guard.get_scaffolder_command(orch_name, orch_type, "")
        return True, f"Use scaffolder: {command}"
    else:
        return False, reason


def list_orchestrators() -> List[Dict]:
    """Get list of all existing orchestrators."""
    guard = OrchestratorCreationGuard()
    return guard.list_existing_orchestrators()
