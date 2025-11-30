"""Health check result analyzer."""

from typing import Dict, Any, List, Tuple


class ResultAnalyzer:
    """Analyzes health check results to determine overall status and risk."""
    
    # Risk levels for each check type
    RISK_LEVELS = {
        "databases": "critical",
        "tests": "high",
        "git": "medium",
        "disk": "high",
        "performance": "medium"
    }
    
    def analyze_results(
        self,
        check_results: Dict[str, Dict[str, Any]]
    ) -> Tuple[str, List[str], List[str]]:
        """
        Analyze check results to determine overall status.
        
        Args:
            check_results: Results from all checks
        
        Returns:
            Tuple of (status, warnings, errors)
        """
        warnings = []
        errors = []
        
        for check_name, result in check_results.items():
            status = result.get("status", "unknown")
            
            if status == "fail":
                error_msg = result.get("error", f"{check_name} check failed")
                errors.append(f"{check_name}: {error_msg}")
            elif status == "warn":
                warning_msg = result.get("message", result.get("error", f"{check_name} warning"))
                warnings.append(f"{check_name}: {warning_msg}")
            
            # Check for specific error fields in details
            if "errors" in result and result["errors"]:
                for err in result["errors"]:
                    if err:  # Skip None/empty errors
                        errors.append(f"{check_name}: {err}")
            
            # Check for warnings
            if "warnings" in result and result["warnings"]:
                for warn in result["warnings"]:
                    if warn:
                        warnings.append(f"{check_name}: {warn}")
        
        # Determine overall status
        if errors:
            overall_status = "unhealthy"
        elif warnings:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return overall_status, warnings, errors
    
    def calculate_risk(
        self,
        check_results: Dict[str, Dict[str, Any]],
        errors: List[str]
    ) -> str:
        """
        Calculate overall risk level.
        
        Args:
            check_results: Results from all checks
            errors: List of error messages
        
        Returns:
            Risk level: "low", "medium", "high", or "critical"
        """
        if not errors:
            return "low"
        
        # Check for critical failures
        for check_name, result in check_results.items():
            if result.get("status") == "fail":
                risk = self.RISK_LEVELS.get(check_name, "medium")
                if risk == "critical":
                    return "critical"
        
        # Count high-risk failures
        high_risk_count = sum(
            1 for check_name, result in check_results.items()
            if result.get("status") == "fail" and self.RISK_LEVELS.get(check_name) == "high"
        )
        
        if high_risk_count >= 2:
            return "high"
        elif high_risk_count == 1:
            return "medium"
        
        return "medium"
