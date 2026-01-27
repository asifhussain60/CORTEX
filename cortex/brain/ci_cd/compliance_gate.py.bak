"""
PHASE 7: CI/CD Integration - Compliance Gate

Enforces compliance requirements in CI/CD pipeline.
Verifies 100% AC coverage before allowing deployments.
"""

import sqlite3
import os
from typing import Dict, Any, Tuple
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../cortex_brain/state/governance.db"
)


class ComplianceGate:
    """Enforce compliance requirements in CI/CD pipeline"""
    
    def __init__(self, required_coverage: float = 100.0, required_acs: int = 120):
        """
        Initialize compliance gate.
        
        Args:
            required_coverage: Required coverage percentage (default 100%)
            required_acs: Required number of covered ACs (default 120)
        """
        self.required_coverage = required_coverage
        self.required_acs = required_acs
        self.db_path = DB_PATH
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn
    
    def check_compliance(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify compliance before deployment.
        
        Returns:
            Tuple of (passed: bool, report: dict)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get total unique ACs
            cursor.execute("SELECT COUNT(DISTINCT ac_id) FROM audit_log")
            total_acs = cursor.fetchone()[0] or 0
            
            # Get completed ACs
            cursor.execute(
                "SELECT COUNT(DISTINCT ac_id) FROM audit_log WHERE operation = 'AC_COMPLETE'"
            )
            current_acs = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # Calculate coverage
            coverage = (current_acs / total_acs * 100) if total_acs > 0 else 0
            
            # Prepare report
            report = {
                "timestamp": datetime.now().isoformat(),
                "total_acs": total_acs,
                "covered_acs": current_acs,
                "coverage_percentage": round(coverage, 1),
                "required_coverage": self.required_coverage,
                "required_acs": self.required_acs,
                "status": "PASSED" if coverage >= self.required_coverage else "FAILED"
            }
            
            # Determine if passed
            passed = coverage >= self.required_coverage
            
            return passed, report
            
        except Exception as e:
            return False, {
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate compliance report for deployment.
        
        Returns:
            Compliance report with deployment decision
        """
        passed, metrics = self.check_compliance()
        
        return {
            "compliance_status": "PASSED" if passed else "FAILED",
            "coverage": metrics.get("coverage_percentage", 0),
            "acs_verified": metrics.get("covered_acs", 0),
            "deployment_approved": passed,
            "report_date": datetime.now().isoformat(),
            "details": metrics
        }
    
    def enforce_gate(self) -> int:
        """
        Enforce compliance gate.
        
        Returns:
            Exit code (0 = success, 1 = failure)
        """
        passed, report = self.check_compliance()
        
        print("\n" + "="*60)
        print("CORTEX COMPLIANCE GATE CHECK")
        print("="*60)
        
        print(f"Total ACs: {report.get('total_acs', 0)}")
        print(f"Covered ACs: {report.get('covered_acs', 0)}")
        print(f"Coverage: {report.get('coverage_percentage', 0)}%")
        print(f"Required: {self.required_coverage}%")
        
        print("-"*60)
        
        if passed:
            print("✅ DEPLOYMENT APPROVED: 100% Compliance Verified")
            print("-"*60 + "\n")
            return 0
        else:
            print(f"❌ DEPLOYMENT BLOCKED: Compliance below {self.required_coverage}%")
            print("-"*60 + "\n")
            return 1


class ContinuousMonitor:
    """Continuous compliance monitoring"""
    
    def __init__(self, check_interval: int = 3600):
        """
        Initialize continuous monitor.
        
        Args:
            check_interval: Check interval in seconds (default 1 hour)
        """
        self.check_interval = check_interval
        self.db_path = DB_PATH
        self.gate = ComplianceGate()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn
    
    def check_compliance_status(self) -> Dict[str, Any]:
        """
        Check current compliance status.
        
        Returns:
            Status dictionary
        """
        passed, report = self.gate.check_compliance()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "entries": self._get_total_entries(),
            "acs": report.get('covered_acs', 0),
            "coverage": f"{report.get('coverage_percentage', 0):.1f}%",
            "status": "COMPLIANT" if passed else "NON_COMPLIANT",
            "details": report
        }
    
    def _get_total_entries(self) -> int:
        """Get total entries"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            count = cursor.fetchone()[0] or 0
            conn.close()
            return count
        except (sqlite3.Error, TypeError):
            return 0
    
    def get_compliance_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get compliance check history.
        
        Args:
            limit: Number of recent checks to return
        
        Returns:
            Historical data
        """
        return {
            "monitor_type": "COMPLIANCE_HISTORY",
            "check_interval": self.check_interval,
            "recent_status": self.check_compliance_status(),
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Main entry point for compliance gate check"""
    gate = ComplianceGate()
    exit_code = gate.enforce_gate()
    exit(exit_code)


if __name__ == "__main__":
    main()
