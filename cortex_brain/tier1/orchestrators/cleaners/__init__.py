"""Cleaners Package

This package should NOT be imported directly.
Instead, import from tier1.orchestrators.cleaners (the cleaners.py module)

When Python sees "from tier1.orchestrators.cleaners import X",
it will import from the cleaners/ package directory first.
This __init__.py must re-export the classes from the parent cleaners.py module.

Author: CORTEX Framework
"""

# Import and re-export from parent cleaners module
# We use the parent module path by importing from the package above
import sys
from pathlib import Path

# Get the parent directory (tier1/orchestrators)
parent_dir = Path(__file__).parent.parent

# Try to import from the parent cleaners.py module directly
# by using importlib to avoid circular imports
import importlib.util
cleaners_module_path = parent_dir / "cleaners.py"
spec = importlib.util.spec_from_file_location("_cleaners_module", cleaners_module_path)
_cleaners_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_cleaners_module)

# Re-export all classes
CleanerInterface = _cleaners_module.CleanerInterface
CleanerRegistry = _cleaners_module.CleanerRegistry
Analysis = _cleaners_module.Analysis
Report = _cleaners_module.Report
RollbackResult = _cleaners_module.RollbackResult
CleanerRegistrationError = _cleaners_module.CleanerRegistrationError
CleanerNotFoundError = _cleaners_module.CleanerNotFoundError

__all__ = [
    "CleanerInterface",
    "CleanerRegistry",
    "Analysis",
    "Report",
    "RollbackResult",
    "CleanerRegistrationError",
    "CleanerNotFoundError",
]
