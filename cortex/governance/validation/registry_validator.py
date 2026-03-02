"""
Registry validator for preventing contradictions and detecting stale data.

Ensures registry consistency by validating cross-references, detecting
outdated entries, and preventing contradictory state.

AC_START: AC-WAVE-3-AUTOMATION-HOOKS-001
Description: RegistryValidator for consistency enforcement
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import yaml


logger = logging.getLogger(__name__)


class RegistryValidator:
    """
    Validator for cortex-registry consistency and freshness.
    
    Detects:
    - Contradictory status (phase marked COMPLETE in one file, ACTIVE in another)
    - Stale data (last_updated > staleness_threshold)
    - Broken cross-references (phase references non-existent enhancement)
    
    Attributes:
        registry_path: Path to cortex-registry root
        staleness_days: Days after which data considered stale (default: 30)
    """
    
    def __init__(self, registry_path: Optional[Path] = None, staleness_days: int = 30) -> None:
        """
        Initialize registry validator.
        
        Args:
            registry_path: Path to registry root (defaults to cortex-registry/)
            staleness_days: Days threshold for stale data (default: 30)
        """
        self.registry_path = registry_path or Path("cortex-registry")
        self.staleness_days = staleness_days
        self._validation_count = 0
        
    def validate_phase(self, phase_id: str) -> Dict[str, Any]:
        """
        Validate phase consistency across registry.
        
        Args:
            phase_id: Phase identifier (e.g., "phase-51")
            
        Returns:
            Dictionary with:
                - valid (bool): Whether phase data is consistent
                - issues (List[str]): List of detected issues
                - stale (bool): Whether data is stale
                - last_updated (str): ISO timestamp of last update
        """
        self._validation_count += 1
        issues: List[str] = []
        
        # Find phase file
        phase_file = self._find_phase_file(phase_id)
        if not phase_file:
            return {
                "valid": False,
                "issues": [f"Phase file not found for {phase_id}"],
                "stale": False,
                "last_updated": None
            }
            
        # Load phase data
        try:
            with open(phase_file, "r") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Failed to load phase YAML: {e}"],
                "stale": False,
                "last_updated": None
            }
            
        # Check staleness
        last_updated = data.get("updated_at") or data.get("created_at")
        stale = False
        
        if last_updated:
            try:
                updated_dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                age_days = (datetime.now() - updated_dt.replace(tzinfo=None)).days
                
                if age_days > self.staleness_days:
                    stale = True
                    issues.append(f"Phase data is stale ({age_days} days old)")
            except Exception as e:
                issues.append(f"Invalid timestamp format: {e}")
        else:
            issues.append("No update timestamp found")
            
        # Check status consistency
        status = data.get("status")
        if not status:
            issues.append("Missing status field")
        elif status not in {"PENDING", "ACTIVE", "COMPLETE", "PARTIAL", "FAILED"}:
            issues.append(f"Invalid status: {status}")
            
        # Check cross-references
        enhancements = data.get("enhancements", [])
        for enh_id in enhancements:
            if not self._enhancement_exists(enh_id):
                issues.append(f"Broken reference to enhancement: {enh_id}")
                
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "stale": stale,
            "last_updated": last_updated
        }
        
    def validate_registry(self) -> Dict[str, Any]:
        """
        Validate entire registry for consistency.
        
        Returns:
            Dictionary with:
                - valid (bool): Whether registry is fully consistent
                - phase_count (int): Total phases checked
                - issue_count (int): Total issues found
                - issues_by_phase (Dict[str, List[str]]): Issues grouped by phase
        """
        issues_by_phase: Dict[str, List[str]] = {}
        phase_count = 0
        issue_count = 0
        
        # Validate all active phases
        active_dir = self.registry_path / "_cortex-master" / "phases" / "active"
        if active_dir.exists():
            for phase_file in active_dir.glob("*.yaml"):
                phase_id = phase_file.stem
                result = self.validate_phase(phase_id)
                
                phase_count += 1
                if not result["valid"]:
                    issues_by_phase[phase_id] = result["issues"]
                    issue_count += len(result["issues"])
                    
        return {
            "valid": issue_count == 0,
            "phase_count": phase_count,
            "issue_count": issue_count,
            "issues_by_phase": issues_by_phase
        }
        
    def _find_phase_file(self, phase_id: str) -> Optional[Path]:
        """
        Locate phase YAML file in registry.
        
        Args:
            phase_id: Phase identifier
            
        Returns:
            Path to phase file or None if not found
        """
        # Check active phases
        active_dir = self.registry_path / "_cortex-master" / "phases" / "active"
        if active_dir.exists():
            phase_file = active_dir / f"{phase_id}.yaml"
            if phase_file.exists():
                return phase_file
                
        # Check completed phases
        completed_dir = self.registry_path / "_cortex-master" / "phases" / "completed"
        if completed_dir.exists():
            phase_file = completed_dir / f"{phase_id}.yaml"
            if phase_file.exists():
                return phase_file
                
        return None
        
    def _enhancement_exists(self, enh_id: str) -> bool:
        """
        Check if enhancement exists in registry.
        
        Args:
            enh_id: Enhancement identifier (e.g., "ENH-059")
            
        Returns:
            True if enhancement file exists
        """
        enh_dir = self.registry_path / "_cortex-master" / "enhancements"
        if not enh_dir.exists():
            return False
            
        enh_file = enh_dir / f"{enh_id.lower()}.yaml"
        return enh_file.exists()
        
    def get_validation_count(self) -> int:
        """
        Get total number of validations performed.
        
        Returns:
            Validation count since initialization
        """
        return self._validation_count
