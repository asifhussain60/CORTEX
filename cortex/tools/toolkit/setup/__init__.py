"""
CORTEX Toolkit - Setup Module

Consolidates setup verification scripts.

**Consolidated Scripts:**
- .cortex-runtime/verify-setup.py
- .cortex-runtime/verify-autonomous-setup.py
- .cortex-runtime/setup-mcp.py (verification functions)

**Authority:** Phase 90 S-90-04
"""

from cortex.tools.toolkit.setup.verifier import SetupVerifier

# Import consolidated setup from Phase 90
try:
    from pathlib import Path

    # Import from sibling setup.py file
    setup_file = Path(__file__).parent.parent / "setup.py"
    if setup_file.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("toolkit_setup", setup_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            SetupResult = module.SetupResult
            SetupCheck = module.SetupCheck
            # Use new verifier as primary
            if hasattr(module, 'SetupVerifier'):
                SetupVerifier = module.SetupVerifier
    else:
        SetupResult = None
        SetupCheck = None
except Exception:
    SetupResult = None
    SetupCheck = None

__all__ = [
    "SetupVerifier",
    "SetupResult",
    "SetupCheck",
]
