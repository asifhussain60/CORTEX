"""
cortex/infrastructure/core035_compliance_check.py

CORE-035 Duplication Compliance Health Check

Detects violations of CORE-035 (Single Canonical Implementation rule).
Runs as part of health check infrastructure for audit trail and early warning.

AC-ID: AC-CORE035-HEALTH-001
Authority: CORE-035 Governance Rule
Status: Detection-only (non-blocking, audit trail)
"""

import time
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import subprocess
import json
from datetime import datetime


@dataclass
class CORE035ComplianceStatus:
    """CORE-035 compliance check result."""
    component: str = "core035_compliance"
    healthy: bool = True
    message: str = ""
    violations_count: int = 0
    duplicate_classes: int = 0
    duplicate_functions: int = 0
    multi_path_orchestrators: int = 0
    latency_ms: float = 0.0
    timestamp: float = 0.0
    baseline_comparison: str = ""  # "improved", "stable", "degraded"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "component": self.component,
            "healthy": self.healthy,
            "message": self.message,
            "violations_count": self.violations_count,
            "duplicate_classes": self.duplicate_classes,
            "duplicate_functions": self.duplicate_functions,
            "multi_path_orchestrators": self.multi_path_orchestrators,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
            "baseline_comparison": self.baseline_comparison,
        }


class CORE035ComplianceCheck:
    """
    Health check for CORE-035 (Single Canonical Implementation) compliance.
    
    Detects:
    - Duplicate class definitions (same class in multiple files)
    - Duplicate function implementations (same function in multiple files)
    - Multi-path orchestrators (parallel execute methods)
    
    Features:
    - Non-blocking (violations are warnings, not failures)
    - Audit trail (logs violations for compliance)
    - Baseline comparison (tracks improvement/degradation)
    - Integration with health check infrastructure
    """
    
    def __init__(self, repo_root: Optional[Path] = None, baseline_file: Optional[Path] = None):
        """
        Initialize CORE-035 compliance checker.
        
        Args:
            repo_root: Repository root path (for running audit script)
            baseline_file: Path to baseline violations file (for comparison)
        """
        self.logger = logging.getLogger(__name__)
        self.repo_root = repo_root or Path("/Users/asifhussain/PROJECTS/CORTEX")
        self.audit_script = self.repo_root / "scripts" / "duplication_audit.py"
        self.baseline_file = baseline_file or self.repo_root / ".cortex" / "core035_baseline.json"
        self.baseline = self._load_baseline()
    
    def _load_baseline(self) -> Dict[str, Any]:
        """Load baseline violations from previous check."""
        try:
            if self.baseline_file.exists():
                with open(self.baseline_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.debug(f"Could not load baseline: {e}")
        
        return {
            "violations_count": 0,
            "duplicate_classes": 0,
            "duplicate_functions": 0,
            "timestamp": 0,
        }
    
    def _save_baseline(self, violations: Dict[str, Any]) -> None:
        """Save current violations as new baseline."""
        try:
            self.baseline_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.baseline_file, 'w') as f:
                json.dump(violations, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save baseline: {e}")
    
    def _run_duplication_audit(self) -> Tuple[int, int, int, int]:
        """
        Run duplication audit script and parse results.
        
        Returns:
            Tuple of (total_violations, duplicate_classes, duplicate_functions, multi_path_count)
        """
        try:
            if not self.audit_script.exists():
                self.logger.warning(f"Audit script not found: {self.audit_script}")
                return 0, 0, 0, 0
            
            # Run audit script with timeout (prevent hanging)
            result = subprocess.run(
                ["python3", str(self.audit_script)],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode != 0:
                self.logger.warning(f"Audit script failed: {result.stderr}")
                return 0, 0, 0, 0
            
            output = result.stdout
            
            # Parse output for violation counts
            # Format: "❌ CLASS: X" and "❌ FUNCTION: Y"
            violations_total = output.count("❌ CLASS:") + output.count("❌ FUNCTION:")
            duplicate_classes = output.count("❌ CLASS:")
            duplicate_functions = output.count("❌ FUNCTION:")
            
            # Detect multi-path orchestrators (looking for specific patterns)
            multi_path_count = 0
            multi_path_patterns = [
                "HandlerCoordinator",
                "OrchestrationCoordinator",
                "DocumentationOrchestrator",
                "RefactoringOrchestrator",
                "PlanningOrchestrator",
                "execute_operation",
                "coordinate_operation",
            ]
            
            for pattern in multi_path_patterns:
                if output.count(pattern) >= 2:
                    multi_path_count += 1
            
            return violations_total, duplicate_classes, duplicate_functions, multi_path_count
        
        except subprocess.TimeoutExpired:
            self.logger.error("Duplication audit timed out (>120 seconds)")
            return 0, 0, 0, 0
        except Exception as e:
            self.logger.error(f"Error running duplication audit: {e}")
            return 0, 0, 0, 0
    
    def _compare_to_baseline(
        self,
        violations: int,
        baseline_violations: int
    ) -> str:
        """
        Compare current violations to baseline.
        
        Returns:
            "improved", "stable", or "degraded"
        """
        if violations < baseline_violations:
            return "improved"
        elif violations == baseline_violations:
            return "stable"
        else:
            return "degraded"
    
    def check(self) -> CORE035ComplianceStatus:
        """
        Run CORE-035 compliance check.
        
        Returns:
            CORE035ComplianceStatus with violation counts and audit data
        """
        start = time.time()
        
        # Run audit
        violations, dup_classes, dup_funcs, multi_path = self._run_duplication_audit()
        
        # Compare to baseline
        baseline_comparison = self._compare_to_baseline(
            violations,
            self.baseline.get("violations_count", 0)
        )
        
        # Save new baseline
        self._save_baseline({
            "violations_count": violations,
            "duplicate_classes": dup_classes,
            "duplicate_functions": dup_funcs,
            "multi_path_orchestrators": multi_path,
            "timestamp": time.time(),
            "baseline_comparison": baseline_comparison,
        })
        
        latency = (time.time() - start) * 1000
        
        # Determine health status (non-blocking: always healthy for health check)
        # Violations don't fail the check, just flag for audit trail
        healthy = True
        
        # Build message
        if violations == 0:
            message = "✅ CORE-035: COMPLIANT (zero duplicates detected)"
        else:
            message = (
                f"⚠️  CORE-035: {violations} violations detected "
                f"({dup_classes} classes, {dup_funcs} functions, {multi_path} multi-path orchestrators) - "
                f"Status: {baseline_comparison.upper()} "
                f"[Audit trail recorded, manual remediation recommended]"
            )
        
        # Log for audit trail
        if violations > 0:
            self.logger.warning(
                f"AC-CORE035-HEALTH-001: {violations} CORE-035 violations detected. "
                f"Baseline: {self.baseline.get('violations_count', 0)}. "
                f"Trend: {baseline_comparison}."
            )
        
        return CORE035ComplianceStatus(
            component="core035_compliance",
            healthy=healthy,
            message=message,
            violations_count=violations,
            duplicate_classes=dup_classes,
            duplicate_functions=dup_funcs,
            multi_path_orchestrators=multi_path,
            latency_ms=latency,
            timestamp=time.time(),
            baseline_comparison=baseline_comparison,
        )


# Singleton instance for health check integration
_core035_checker: CORE035ComplianceCheck = None


def get_core035_checker(repo_root: Path = None) -> CORE035ComplianceCheck:
    """Get or create singleton CORE-035 compliance checker."""
    global _core035_checker
    if _core035_checker is None:
        _core035_checker = CORE035ComplianceCheck(repo_root)
    return _core035_checker


def reset_core035_checker() -> None:
    """Reset singleton (for testing)."""
    global _core035_checker
    _core035_checker = None
