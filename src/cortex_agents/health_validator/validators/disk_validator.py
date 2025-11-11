"""Disk space health validator."""

import os
import shutil
import platform
from pathlib import Path
from typing import Dict, Any
from .base_validator import BaseHealthValidator


class DiskValidator(BaseHealthValidator):
    """Validator for available disk space (cross-platform)."""
    
    def __init__(self, min_free_gb: float = 1.0):
        """
        Initialize disk validator.
        
        Args:
            min_free_gb: Minimum required free disk space in GB
        """
        self.min_free_gb = min_free_gb
    
    def get_risk_level(self) -> str:
        """Low disk space is high risk."""
        return "high"
    
    def check(self) -> Dict[str, Any]:
        """Check available disk space (cross-platform)."""
        try:
            # Get current working directory disk usage
            cwd = Path.cwd()
            
            # Use platform-appropriate method
            if platform.system() == "Windows":
                # Windows: use shutil.disk_usage
                usage = shutil.disk_usage(cwd)
                free_bytes = usage.free
                total_bytes = usage.total
            else:
                # Unix/Mac: use os.statvfs
                stat = os.statvfs(cwd)
                free_bytes = stat.f_bavail * stat.f_frsize
                total_bytes = stat.f_blocks * stat.f_frsize
            
            # Calculate free space in GB
            free_gb = free_bytes / (1024 ** 3)
            total_gb = total_bytes / (1024 ** 3)
            used_percent = ((total_gb - free_gb) / total_gb) * 100
            
            status = "pass" if free_gb >= self.min_free_gb else "fail"
            
            result = {
                "status": status,
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "used_percent": round(used_percent, 1),
                "threshold_gb": self.min_free_gb,
                "details": [],
                "errors": [],
                "warnings": []
            }
            
            if status == "fail":
                result["errors"].append(
                    f"Low disk space: {free_gb:.2f}GB free (threshold: {self.min_free_gb}GB)"
                )
            
            return result
            
        except Exception as e:
            return {
                "status": "fail",
                "details": [],
                "errors": [f"Disk space check failed: {str(e)}"],
                "warnings": []
            }
