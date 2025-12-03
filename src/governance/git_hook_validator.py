"""Git pre-commit hook validator."""

from src.governance.naming_convention_enforcer import NamingConventionEnforcer


class GitHookValidator:
    """Validates files for git pre-commit hook."""
    
    def __init__(self):
        self.enforcer = NamingConventionEnforcer()
    
    def validate_files(self, filenames: list) -> list:
        """Validate list of files."""
        results = []
        for filename in filenames:
            results.append({
                "filename": filename,
                "valid": self.enforcer.check(filename)
            })
        return results
