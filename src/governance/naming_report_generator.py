"""Naming report generator."""

from pathlib import Path
from src.governance.naming_convention_enforcer import NamingConventionEnforcer


class NamingReportGenerator:
    """Generates naming violation reports."""
    
    def __init__(self):
        self.enforcer = NamingConventionEnforcer()
    
    def scan_directory(self, directory: Path) -> dict:
        """Scan directory for naming violations."""
        directory = Path(directory)
        files = list(directory.glob("*"))
        
        violations = []
        for file in files:
            if file.is_file() and not self.enforcer.check(file.name):
                violations.append(str(file.name))
        
        return {
            "total_files": len(files),
            "violations": violations,
            "violation_count": len(violations)
        }
