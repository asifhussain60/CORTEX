"""
RegressionMonitor - Integration wrapper for TDDOrchestrator.

Provides simplified interface for TDDOrchestrator to call:
1. Pre-execution: check_completed_phases() via ArchitectureGuard
2. Post-execution: scan_brittleness() via BrittlenessScanner

Non-blocking by default - returns warnings, doesn't raise exceptions.

Author: Asif Hussain
Date: 2026-02-05
Phase: 24 (AC-PHASE24-005)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Any, List

from cortex.orchestrators.core.architecture_guard import ArchitectureGuard
from cortex.orchestrators.support.brittleness_scanner import BrittlenessScanner

logger = logging.getLogger(__name__)


class RegressionMonitor:
    """
    Integration wrapper for regression checks in TDDOrchestrator.
    
    Provides non-blocking interface to Phase 24 layers:
    - Pre-execution: ArchitectureGuard (completed phase validation)
    - Post-execution: BrittlenessScanner (runtime brittleness detection)
    
    Design principle: Never raise exceptions, return warnings/scores.
    """
    
    def __init__(self, registry_dir: Path):
        """
        Initialize RegressionMonitor.
        
        Args:
            registry_dir: Path to cortex-registry/_cortex-master/
        """
        self.registry_dir = registry_dir
        self.architecture_guard = ArchitectureGuard()
        self.brittleness_scanner = BrittlenessScanner()
    
    def check_completed_phases(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check request against completed phases (pre-execution).
        
        Calls ArchitectureGuard.validate_request() and returns simplified result
        for TDDOrchestrator.
        
        Non-blocking: Catches all exceptions and returns PASS status.
        
        Args:
            context: Request context with:
                - request_description (str): User's request
                - intent_type (str): IMPLEMENT, FIX, REFACTOR, etc.
                - scope (str): Target component/file
        
        Returns:
            Dict with:
                - status (str): PASS, WARNING, CRITICAL
                - verdict (str): PROCEED, CREATE_PHASE, BLOCK
                - regression_risk (float): 0.0-1.0
                - reasoning (str): Why this verdict
                - phase_alignment (Dict): Full phase_alignment data
        """
        try:
            # Extract required fields from context
            request_description = context.get("request_description", "")
            intent_type = context.get("intent_type", "IMPLEMENT")
            scope = context.get("scope", "")
            
            # Call ArchitectureGuard
            guard_result = self.architecture_guard.validate_request(
                request_description=request_description,
                intent_type=intent_type,
                scope=scope,
                registry_path=self.registry_dir
            )
            
            # Map verdict to status
            if guard_result.verdict.value == "BLOCK":
                status = "CRITICAL"
            elif guard_result.verdict.value == "CREATE_PHASE":
                status = "WARNING"
            else:
                status = "PASS"
            
            return {
                "status": status,
                "verdict": guard_result.verdict.value,
                "regression_risk": guard_result.regression_risk,
                "reasoning": guard_result.rationale,
                "phase_alignment": {
                    "aligned_phase_id": guard_result.aligned_phase_id,
                    "aligned_phase_name": guard_result.aligned_phase_name,
                    "confidence": guard_result.confidence,
                    "regression_risk": guard_result.regression_risk
                }
            }
            
        except Exception as e:
            logger.error(f"check_completed_phases failed: {e}", exc_info=True)
            # Non-blocking: Return PASS on error
            return {
                "status": "PASS",
                "verdict": "PROCEED",
                "regression_risk": 0.0,
                "reasoning": f"Validation error (non-blocking): {str(e)}",
                "phase_alignment": {}
            }
    
    def scan_brittleness(self, modified_files: List[str]) -> Dict[str, Any]:
        """
        Scan modified files for brittleness issues.
        
        Calls BrittlenessScanner.scan() and returns simplified result
        for TDDOrchestrator.
        
        Args:
            modified_files: List of file paths that were modified
        
        Returns:
            Dict with:
                - status (str): PASS, WARNING, CRITICAL
                - brittleness_score (float): 0.0-1.0
                - issues (List[str]): Detected issues
                - details (Dict): Full scan results
        """
        try:
            # Handle empty file list
            if not modified_files:
                return {
                    "status": "PASS",
                    "brittleness_score": 0.0,
                    "issues": [],
                    "details": {}
                }
            
            # Aggregate results from multiple file scans
            max_brittleness = 0.0
            all_issues = []
            scanned_count = 0
            
            for file_path in modified_files:
                file_path_obj = Path(file_path)
                if not file_path_obj.exists():
                    continue
                
                # Scan single file/directory (scanner handles both)
                scan_result = self.brittleness_scanner.scan(str(file_path_obj))
                scanned_count += 1
                
                # Track max brittleness score across all files
                max_brittleness = max(max_brittleness, scan_result.brittleness_score)
                
                # Collect circular dependency issues
                if scan_result.circular_dependencies:
                    for dep in scan_result.circular_dependencies:
                        cycle_str = " -> ".join(dep.cycle_path)
                        all_issues.append(f"Circular dependency: {cycle_str}")
                
                # Collect coupling violations (high coupling score)
                if scan_result.coupling_violations:
                    for violation in scan_result.coupling_violations:
                        if violation.coupling_score > 0.7:
                            all_issues.append(
                                f"High coupling in {violation.module_name}: "
                                f"{violation.coupling_score:.2f}"
                            )
                
                # Collect anti-pattern violations
                if scan_result.anti_pattern_violations:
                    for violation in scan_result.anti_pattern_violations:
                        all_issues.append(
                            f"Anti-pattern '{violation.pattern_name}' in {violation.location}"
                        )
            
            # Determine status based on max brittleness score
            if max_brittleness > 0.7:
                status = "CRITICAL"
            elif max_brittleness > 0.4:
                status = "WARNING"
            else:
                status = "PASS"
            
            return {
                "status": status,
                "brittleness_score": max_brittleness,
                "issues": all_issues,
                "details": f"Scanned {scanned_count} files"
            }
            
        except Exception as e:
            logger.error(f"scan_brittleness failed: {e}", exc_info=True)
            # Non-blocking: Return PASS on error
            return {
                "status": "PASS",
                "brittleness_score": 0.0,
                "issues": [f"Scan error (non-blocking): {str(e)}"],
                "details": {}
            }


__all__ = ["RegressionMonitor"]
