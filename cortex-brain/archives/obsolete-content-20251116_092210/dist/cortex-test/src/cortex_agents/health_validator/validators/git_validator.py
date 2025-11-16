"""Git repository health validator."""

import subprocess
from typing import Dict, Any
from .base_validator import BaseHealthValidator


class GitValidator(BaseHealthValidator):
    """Validator for git repository status."""
    
    def __init__(self, max_uncommitted: int = 50):
        """
        Initialize git validator.
        
        Args:
            max_uncommitted: Maximum acceptable uncommitted changes
        """
        self.max_uncommitted = max_uncommitted
    
    def get_risk_level(self) -> str:
        """Git issues are medium risk."""
        return "medium"
    
    def check(self) -> Dict[str, Any]:
        """Check git repository status."""
        try:
            # Check if we're in a git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return {
                    "status": "skip",
                    "message": "Not a git repository",
                    "details": [],
                    "errors": [],
                    "warnings": []
                }
            
            # Get uncommitted changes count
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            uncommitted_lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
            uncommitted_count = len(uncommitted_lines)
            
            # Determine status
            status_result = {
                "uncommitted_count": uncommitted_count,
                "details": [],
                "errors": [],
                "warnings": []
            }
            
            if uncommitted_count == 0:
                status_result["status"] = "pass"
                status_result["message"] = "No uncommitted changes"
            elif uncommitted_count < self.max_uncommitted:
                status_result["status"] = "pass"
                status_result["message"] = f"{uncommitted_count} uncommitted changes (acceptable)"
            else:
                status_result["status"] = "warn"
                status_result["message"] = f"{uncommitted_count} uncommitted changes (high)"
                status_result["warnings"].append(
                    f"High number of uncommitted changes: {uncommitted_count}"
                )
            
            return status_result
            
        except Exception as e:
            return {
                "status": "fail",
                "details": [],
                "errors": [f"Git status check failed: {str(e)}"],
                "warnings": []
            }
