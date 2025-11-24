"""Health check report formatter."""

from typing import Dict, Any, List


class ReportFormatter:
    """Formats health check results into user-friendly messages."""
    
    def format_message(
        self,
        status: str,
        warnings: List[str],
        errors: List[str],
        check_results: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Format health check results into a message.
        
        Args:
            status: Overall health status
            warnings: List of warning messages
            errors: List of error messages
            check_results: Detailed results from all checks
        
        Returns:
            Formatted message string
        """
        msg_parts = [f"System Status: {status.upper()}"]
        
        if errors:
            msg_parts.append(f"\n❌ ERRORS ({len(errors)}):")
            for error in errors:
                msg_parts.append(f"  - {error}")
        
        if warnings:
            msg_parts.append(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for warning in warnings:
                msg_parts.append(f"  - {warning}")
        
        # Add summary of each check
        msg_parts.append("\n📊 CHECK SUMMARY:")
        for check_name, result in check_results.items():
            status_icon = self._get_status_icon(result.get("status", "unknown"))
            msg_parts.append(f"  {status_icon} {check_name}: {result.get('status', 'unknown')}")
        
        return "\n".join(msg_parts)
    
    def suggest_actions(
        self,
        check_results: Dict[str, Dict[str, Any]],
        risk_level: str
    ) -> List[str]:
        """
        Suggest remediation actions based on check results.
        
        Args:
            check_results: Results from all checks
            risk_level: Overall risk level
        
        Returns:
            List of suggested actions
        """
        suggestions = []
        
        # Database-specific suggestions
        if "databases" in check_results:
            db_result = check_results["databases"]
            if db_result.get("status") == "fail":
                suggestions.append("🔧 Fix database issues before proceeding")
                if "errors" in db_result:
                    for error in db_result["errors"]:
                        if "not found" in error.lower():
                            suggestions.append("  - Initialize missing databases")
                        elif "integrity" in error.lower():
                            suggestions.append("  - Run database repair/backup")
        
        # Test-specific suggestions
        if "tests" in check_results:
            test_result = check_results["tests"]
            if test_result.get("status") == "fail":
                suggestions.append("🧪 Address test failures:")
                pass_rate = test_result.get("pass_rate", 0)
                if pass_rate < 0.5:
                    suggestions.append("  - Critical: <50% tests passing, investigate immediately")
                else:
                    suggestions.append(f"  - {test_result.get('failed', 0)} test(s) failing")
        
        # Git-specific suggestions
        if "git" in check_results:
            git_result = check_results["git"]
            if git_result.get("status") == "warn":
                uncommitted = git_result.get("uncommitted_count", 0)
                if uncommitted > 100:
                    suggestions.append("📝 Consider committing changes (>100 uncommitted files)")
        
        # Disk-specific suggestions
        disk_result = check_results.get("disk") or check_results.get("disk_space")
        if disk_result and disk_result.get("status") == "fail":
            free_gb = disk_result.get("free_gb", 0)
            suggestions.append(f"💾 Free up disk space (only {free_gb}GB available)")
        
        # Performance-specific suggestions
        if "performance" in check_results:
            perf_result = check_results["performance"]
            if perf_result.get("status") == "warn":
                suggestions.append("⚡ Performance degraded - consider optimization")
        
        # General recommendations based on risk
        if risk_level == "critical":
            suggestions.append("\n⛔ CRITICAL: Do not proceed with risky operations")
        elif risk_level == "high":
            suggestions.append("\n⚠️  HIGH RISK: Proceed with caution, fix critical issues first")
        elif risk_level == "medium":
            suggestions.append("\n⚠️  MEDIUM RISK: Review warnings before proceeding")
        
        return suggestions
    
    def _get_status_icon(self, status: str) -> str:
        """Get icon for status."""
        icons = {
            "pass": "✅",
            "warn": "⚠️",
            "fail": "❌",
            "skip": "⏭️",
            "unknown": "❓"
        }
        return icons.get(status, "❓")
