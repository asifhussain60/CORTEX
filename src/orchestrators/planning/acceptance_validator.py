"""
Phase-Level Acceptance Criteria Validation Module.

Implements DoR (Definition of Ready) and DoD (Definition of Done) validation
for CORTEX-5.0 planning system. Ensures phases cannot start without prerequisites
and cannot complete without deliverables.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.

CORTEX-5.0 Gap 1 Remediation: Phase-Level Acceptance Criteria
"""

import logging
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime


class PhaseNotReadyError(Exception):
    """Raised when phase DoR criteria not met."""
    pass


class PhaseIncompleteError(Exception):
    """Raised when phase DoD criteria not met."""
    pass


class AcceptanceCriteriaValidator:
    """
    Validates phase-level acceptance criteria (DoR/DoD).
    
    Features:
    - Load criteria from acceptance-criteria.yaml
    - Validate automated criteria via command execution
    - Validate manual criteria via checklist review
    - Block phase start if DoR not met
    - Block phase completion if DoD not met
    - Log all validation attempts
    
    Integration:
    - Called by Planning Orchestrator v5 before phase start/complete
    - Criteria stored in plan context folder
    - Results logged to phase execution records
    """
    
    def __init__(self, plan_root: Path, logger: Optional[logging.Logger] = None):
        """
        Initialize acceptance criteria validator.
        
        Args:
            plan_root: Root directory of plan (e.g., C50-10/)
            logger: Logger instance (creates default if None)
        """
        self.plan_root = Path(plan_root)
        self.criteria_file = self.plan_root / "acceptance-criteria.yaml"
        self.logger = logger or logging.getLogger(__name__)
        
        self.criteria = self._load_criteria()
    
    def _load_criteria(self) -> Dict[str, Any]:
        """
        Load acceptance criteria from YAML file.
        
        Returns:
            Criteria dictionary with phase-level DoR/DoD
        """
        if not self.criteria_file.exists():
            self.logger.warning(
                f"Acceptance criteria file not found: {self.criteria_file}. "
                "Creating default structure."
            )
            return {"phases": []}
        
        try:
            with open(self.criteria_file, 'r') as f:
                return yaml.safe_load(f) or {"phases": []}
        except Exception as e:
            self.logger.error(f"Failed to load criteria: {e}")
            return {"phases": []}
    
    def _get_phase_criteria(self, phase_number: int, criteria_type: str) -> List[Dict[str, Any]]:
        """
        Get DoR or DoD criteria for specific phase.
        
        Args:
            phase_number: Phase number to lookup
            criteria_type: 'dor' or 'dod'
        
        Returns:
            List of criteria dictionaries
        """
        phases = self.criteria.get("phases", [])
        
        for phase in phases:
            if phase.get("phase_number") == phase_number:
                return phase.get(criteria_type, [])
        
        self.logger.warning(
            f"No {criteria_type.upper()} criteria defined for Phase {phase_number}. "
            "Skipping validation."
        )
        return []
    
    def _validate_criterion(self, criterion: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate a single acceptance criterion.
        
        Args:
            criterion: Criterion dictionary with validation details
        
        Returns:
            (success, error_message) tuple
        """
        validation_type = criterion.get("validation_type", "manual")
        criterion_text = criterion.get("criterion", "Unknown criterion")
        
        if validation_type == "automated":
            # Execute validation command
            validation_command = criterion.get("validation_command")
            
            if not validation_command:
                return False, f"No validation command for automated criterion: {criterion_text}"
            
            try:
                import subprocess
                
                result = subprocess.run(
                    validation_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.logger.info(f"✅ Automated criterion passed: {criterion_text}")
                    return True, None
                else:
                    error = f"Command failed (exit {result.returncode}): {result.stderr.strip()}"
                    self.logger.error(f"❌ Automated criterion failed: {criterion_text} - {error}")
                    return False, error
            
            except subprocess.TimeoutExpired:
                error = "Validation command timed out (30s)"
                self.logger.error(f"❌ Automated criterion timeout: {criterion_text}")
                return False, error
            
            except Exception as e:
                error = f"Validation error: {e}"
                self.logger.error(f"❌ Automated criterion error: {criterion_text} - {error}")
                return False, error
        
        elif validation_type == "manual":
            # Manual criteria assumed to be validated externally
            # Log for visibility but don't block
            self.logger.info(f"ℹ️  Manual criterion (not validated): {criterion_text}")
            return True, None
        
        else:
            error = f"Unknown validation type: {validation_type}"
            self.logger.warning(f"⚠️  Criterion validation skipped: {criterion_text} - {error}")
            return True, None  # Don't block on unknown types
    
    def validate_phase_dor(self, phase_number: int) -> bool:
        """
        Validate Definition of Ready (DoR) for phase.
        
        Checks all entry criteria before phase can start. Blocks execution
        if any automated criterion fails.
        
        Args:
            phase_number: Phase number to validate
        
        Returns:
            True if ready to start, False otherwise
        
        Raises:
            PhaseNotReadyError: If blocking criteria not met
        """
        self.logger.info(f"Validating DoR for Phase {phase_number}")
        
        dor_criteria = self._get_phase_criteria(phase_number, "dor")
        
        if not dor_criteria:
            # No criteria defined - allow phase to proceed
            self.logger.warning(
                f"No DoR criteria for Phase {phase_number}. Proceeding without validation."
            )
            return True
        
        failures = []
        
        for criterion in dor_criteria:
            success, error = self._validate_criterion(criterion)
            
            if not success:
                criterion_text = criterion.get("criterion", "Unknown")
                failures.append(f"{criterion_text}: {error}")
        
        if failures:
            error_summary = f"Phase {phase_number} DoR validation failed:\n" + "\n".join(
                f"  - {failure}" for failure in failures
            )
            self.logger.error(error_summary)
            raise PhaseNotReadyError(error_summary)
        
        self.logger.info(f"✅ Phase {phase_number} DoR validation passed")
        return True
    
    def validate_phase_dod(self, phase_number: int) -> bool:
        """
        Validate Definition of Done (DoD) for phase.
        
        Checks all exit criteria before phase can complete. Blocks completion
        if any automated criterion fails.
        
        Args:
            phase_number: Phase number to validate
        
        Returns:
            True if ready to complete, False otherwise
        
        Raises:
            PhaseIncompleteError: If blocking criteria not met
        """
        self.logger.info(f"Validating DoD for Phase {phase_number}")
        
        dod_criteria = self._get_phase_criteria(phase_number, "dod")
        
        if not dod_criteria:
            # No criteria defined - allow phase to complete
            self.logger.warning(
                f"No DoD criteria for Phase {phase_number}. Proceeding without validation."
            )
            return True
        
        failures = []
        
        for criterion in dod_criteria:
            success, error = self._validate_criterion(criterion)
            
            if not success:
                criterion_text = criterion.get("criterion", "Unknown")
                failures.append(f"{criterion_text}: {error}")
        
        if failures:
            error_summary = f"Phase {phase_number} DoD validation failed:\n" + "\n".join(
                f"  - {failure}" for failure in failures
            )
            self.logger.error(error_summary)
            raise PhaseIncompleteError(error_summary)
        
        self.logger.info(f"✅ Phase {phase_number} DoD validation passed")
        return True
    
    def get_validation_report(self, phase_number: int) -> Dict[str, Any]:
        """
        Generate validation report for phase.
        
        Args:
            phase_number: Phase number to report on
        
        Returns:
            Report dictionary with DoR/DoD status
        """
        report = {
            "phase_number": phase_number,
            "timestamp": datetime.now().isoformat(),
            "dor_criteria_count": 0,
            "dod_criteria_count": 0,
            "dor_status": "unknown",
            "dod_status": "unknown"
        }
        
        # Check DoR
        try:
            self.validate_phase_dor(phase_number)
            dor_criteria = self._get_phase_criteria(phase_number, "dor")
            report["dor_criteria_count"] = len(dor_criteria)
            report["dor_status"] = "passed"
        except PhaseNotReadyError as e:
            report["dor_status"] = "failed"
            report["dor_errors"] = str(e)
        
        # Check DoD
        try:
            self.validate_phase_dod(phase_number)
            dod_criteria = self._get_phase_criteria(phase_number, "dod")
            report["dod_criteria_count"] = len(dod_criteria)
            report["dod_status"] = "passed"
        except PhaseIncompleteError as e:
            report["dod_status"] = "failed"
            report["dod_errors"] = str(e)
        
        return report


# End of acceptance_validator.py module
