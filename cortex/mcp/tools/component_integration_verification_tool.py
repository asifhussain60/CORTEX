"""
MCP tool for Component Integration Verification (CIV).

Authority: ENH-027 (Component Integration Verification)
CORE Rules: CORE-008 (TDD-first), CORE-011 (type hints), CORE-012 (docstrings)

Purpose:
    Exposes ComponentIntegrationVerifier as MCP tool for use in AUDIT mode.
"""

from pathlib import Path
from typing import Any, Dict

from cortex.orchestrators.core.component_integration_verification import (
    ComponentIntegrationVerifier,
)


def cortex_verify_integration(workspace_root: str) -> Dict[str, Any]:
    """
    Verify CORTEX component integration across 3 layers.

    Args:
        workspace_root: Path to CORTEX workspace root

    Returns:
        Dictionary with CIV report data

    Example:
        >>> result = cortex_verify_integration("/path/to/cortex")
        >>> print(result["overall_status"])
        >>> print(result["issues_found"])
    """
    verifier = ComponentIntegrationVerifier(workspace_root=Path(workspace_root))
    report = verifier.verify_all()
    return report.to_dict()
