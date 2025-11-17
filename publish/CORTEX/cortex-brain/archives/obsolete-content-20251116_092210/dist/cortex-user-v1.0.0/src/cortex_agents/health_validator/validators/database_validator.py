"""Database health validator."""

import os
import sqlite3
from typing import Dict, Any, Optional
from .base_validator import BaseHealthValidator


class DatabaseValidator(BaseHealthValidator):
    """Validator for database integrity checks."""
    
    def __init__(self, tier1_api=None, tier2_kg=None, tier3_context=None, max_size_mb: int = 500):
        """
        Initialize database validator.
        
        Args:
            tier1_api: Tier 1 API instance
            tier2_kg: Tier 2 Knowledge Graph instance
            tier3_context: Tier 3 Context Intelligence instance
            max_size_mb: Maximum allowed database size in MB
        """
        self.tier1 = tier1_api
        self.tier2 = tier2_kg
        self.tier3 = tier3_context
        self.max_size_mb = max_size_mb
    
    def get_risk_level(self) -> str:
        """Database failures are critical."""
        return "critical"
    
    def check(self) -> Dict[str, Any]:
        """Check all tier databases for integrity."""
        results = {
            "status": "pass",
            "details": [],
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check Tier 1 database
            if self.tier1:
                tier1_check = self._check_single_database(
                    getattr(self.tier1, 'db_path', None),
                    "Tier 1"
                )
                results["details"].append(tier1_check)
                if tier1_check["status"] == "fail":
                    results["status"] = "fail"
                    results["errors"].append(tier1_check.get("error", "Tier 1 check failed"))
                elif tier1_check["status"] == "warn":
                    results["warnings"].append(tier1_check.get("error", "Tier 1 warning"))
            
            # Check Tier 2 database
            if self.tier2:
                tier2_check = self._check_single_database(
                    getattr(self.tier2, 'db_path', None),
                    "Tier 2"
                )
                results["details"].append(tier2_check)
                if tier2_check["status"] == "fail":
                    results["status"] = "fail"
                    results["errors"].append(tier2_check.get("error", "Tier 2 check failed"))
                elif tier2_check["status"] == "warn":
                    results["warnings"].append(tier2_check.get("error", "Tier 2 warning"))
            
            # Check Tier 3 database
            if self.tier3:
                tier3_check = self._check_single_database(
                    getattr(self.tier3, 'db_path', None),
                    "Tier 3"
                )
                results["details"].append(tier3_check)
                if tier3_check["status"] == "fail":
                    results["status"] = "fail"
                    results["errors"].append(tier3_check.get("error", "Tier 3 check failed"))
                elif tier3_check["status"] == "warn":
                    results["warnings"].append(tier3_check.get("error", "Tier 3 warning"))
            
        except Exception as e:
            results["status"] = "fail"
            results["errors"].append(f"Database check failed: {str(e)}")
        
        return results
    
    def _check_single_database(self, db_path: Optional[str], name: str) -> Dict[str, Any]:
        """Check a single database file."""
        if not db_path:
            return {
                "name": name,
                "status": "skip",
                "message": f"{name} database path not available"
            }
        
        try:
            # Check file exists
            if not os.path.exists(db_path):
                return {
                    "name": name,
                    "status": "fail",
                    "error": f"{name} database file not found: {db_path}"
                }
            
            # Check file size
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            if size_mb > self.max_size_mb:
                return {
                    "name": name,
                    "status": "warn",
                    "size_mb": round(size_mb, 2),
                    "error": f"{name} database size ({size_mb:.1f}MB) exceeds threshold"
                }
            
            # Check database integrity
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            conn.close()
            
            if integrity != "ok":
                return {
                    "name": name,
                    "status": "fail",
                    "error": f"{name} database integrity check failed: {integrity}"
                }
            
            return {
                "name": name,
                "status": "pass",
                "size_mb": round(size_mb, 2),
                "message": f"{name} database healthy"
            }
            
        except Exception as e:
            return {
                "name": name,
                "status": "fail",
                "error": f"{name} database check error: {str(e)}"
            }
