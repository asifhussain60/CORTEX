"""
Path Utilities - CORE-005 Compliance (Path Portability)

Provides portable path utilities that work across different machines,
CI/CD systems, containers, and operating systems.
"""

from pathlib import Path
import os
import sys
import logging

logger = logging.getLogger(__name__)


def project_root() -> Path:
    """
    Get absolute path to CORTEX project root.
    
    Works regardless of:
    - Current working directory
    - Machine configuration
    - Operating system (Windows/macOS/Linux)
    - Container vs. host
    - CI/CD environment
    
    Returns:
        Path to project root (directory containing .github/prompts/)
        
    Raises:
        RuntimeError: If project root cannot be found
    """
    # Start from this file's location
    current = Path(__file__).resolve().parent.parent.parent
    
    # Verify we found the right location by checking for distinctive marker
    marker_path = current / ".github" / "prompts"
    
    if not marker_path.exists():
        # Try searching upward (in case __file__ resolution is unusual)
        search_path = current
        for _ in range(5):  # Search up to 5 levels
            marker = search_path / ".github" / "prompts"
            if marker.exists():
                current = search_path
                break
            search_path = search_path.parent
        else:
            raise RuntimeError(
                f"Cannot find CORTEX project root. "
                f"Expected {marker_path} to exist. "
                f"Started from: {__file__}"
            )
    
    logger.debug(f"Project root: {current}")
    return current


def cortex_brain_path() -> Path:
    """Get path to cortex-brain directory (portable)."""
    return project_root() / "cortex-brain"


def audit_logs_path() -> Path:
    """Get path to audit logs directory."""
    return cortex_brain_path() / "audit-logs"


def state_db_path() -> Path:
    """Get path to state database."""
    return cortex_brain_path() / "state" / "cortex.db"


def tier0_governance_path() -> Path:
    """Get path to Tier 0 governance directory."""
    return cortex_brain_path() / "tier0" / "governance"


def tier1_tracking_path() -> Path:
    """Get path to Tier 1 tracking directory."""
    return cortex_brain_path() / "tier1" / "tracking"


def tier1_acceptance_criteria_path() -> Path:
    """Get path to acceptance criteria directory."""
    return cortex_brain_path() / "tier1" / "acceptance-criteria"


def tier1_evidence_bundles_path() -> Path:
    """Get path to evidence bundles directory."""
    return cortex_brain_path() / "tier1" / "evidence-bundles"


def progress_tracker_path() -> Path:
    """Get path to progress tracker JSON file."""
    return tier1_tracking_path() / "progress-tracker.json"


def ac_index_path() -> Path:
    """Get path to AC-INDEX YAML file."""
    return tier1_acceptance_criteria_path() / "AC-INDEX.yaml"


def core_rules_path() -> Path:
    """Get path to core governance rules YAML file."""
    return tier0_governance_path() / "core-rules.yaml"


def ensure_dir(path: Path) -> Path:
    """
    Create directory if it doesn't exist.
    
    Args:
        path: Directory path to create
        
    Returns:
        Path object (created or already existing)
        
    Raises:
        OSError: If directory cannot be created
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory: {path}")
        return path
    except OSError as e:
        logger.error(f"Failed to create directory {path}: {e}")
        raise


def ensure_file_dir(file_path: Path) -> Path:
    """
    Ensure directory for a file exists.
    
    Args:
        file_path: Path to file
        
    Returns:
        Parent directory path
    """
    return ensure_dir(file_path.parent)
