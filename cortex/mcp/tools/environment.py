"""Environment verification MCP tool.

Exposes environment validation checks via MCP protocol, wrapping the
existing verify_environment.py script with MCP-compatible interface.
"""

import sys
import subprocess
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

# Import existing environment verifier
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from cortex.scripts.verify_environment import EnvironmentVerifier
from cortex.mcp.decorators import mcp_tool


class EnvironmentStatus(str, Enum):
    """Environment validation status."""

    READY = "READY"
    MISSING_PYTHON = "MISSING_PYTHON"
    MISSING_DEPS = "MISSING_DEPS"
    PARTIAL = "PARTIAL"


@dataclass
class EnvironmentCheckResult:
    """Result of environment verification.

    Attributes:
        status: Overall environment status
        python_version: Detected Python version string
        missing_packages: List of missing package names
        recommendations: List of actionable recommendations
        details: Optional detailed check results (if verbose=True)
    """

    status: EnvironmentStatus
    python_version: str
    missing_packages: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    details: Optional[List[Dict[str, Any]]] = None


@mcp_tool(
    name="cortex_verify_environment",
    description=(
        "Verify CORTEX development environment setup. "
        "Checks Python version (3.9+), dependencies, development tools, "
        "and MCP server connectivity. Optionally attempts auto-fix for missing packages."
    ),
)
def cortex_verify_environment(
    auto_fix: bool = False,
    verbose: bool = True,
) -> EnvironmentCheckResult:
    """Verify CORTEX environment setup.

    Args:
        auto_fix: If True, attempt to install missing packages via pip
        verbose: If True, include detailed diagnostic information

    Returns:
        EnvironmentCheckResult with status, version, missing packages, and recommendations

    Example:
        >>> result = cortex_verify_environment(auto_fix=False, verbose=True)
        >>> if result.status == EnvironmentStatus.READY:
        >>>     print("Environment ready!")
        >>> else:
        >>>     print(f"Issues: {result.recommendations}")
    """
    # Initialize result containers
    missing_packages: List[str] = []
    recommendations: List[str] = []
    details: Optional[List[Dict[str, Any]]] = None

    # Get current Python version - handle both sys.version_info and mocked tuples
    version_info = sys.version_info
    if isinstance(version_info, tuple):
        python_version = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"
        version_check = version_info
    else:
        python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
        version_check = (version_info.major, version_info.minor, version_info.micro)

    # Early check for Python version before running verifier
    if version_check < (3, 9, 0):
        recommendations.append(
            f"Upgrade Python to 3.9+ (current: {python_version}). "
            "Visit https://www.python.org/downloads/"
        )
        return EnvironmentCheckResult(
            status=EnvironmentStatus.MISSING_PYTHON,
            python_version=python_version,
            missing_packages=[],
            recommendations=recommendations,
            details=None,
        )

    # Run environment checks
    verifier = EnvironmentVerifier()
    exit_code = verifier.run_all_checks()

    # Parse verifier results (remove duplicate declarations)
    for check in verifier.results:
        if not check.passed:
            # Extract package names from error messages
            if "Missing:" in check.message:
                packages_str = check.message.split("Missing:")[1].strip()
                # Remove "Run: pip install -r requirements.txt" suffix if present
                packages_str = packages_str.split(".")[0].strip()
                packages = [
                    pkg.strip() for pkg in packages_str.split(",")
                ]
                missing_packages.extend(packages)

            # Generate recommendations
            if check.severity == "error":
                if "Python" in check.name:
                    recommendations.append(
                        f"Upgrade Python to 3.9+ (current: {python_version}). "
                        "Visit https://www.python.org/downloads/"
                    )
                elif "Dependencies" in check.name:
                    recommendations.append(
                        "Install missing core dependencies: "
                        "pip install -r requirements.txt"
                    )
            elif check.severity == "warning":
                if "Quality Tools" in check.name:
                    recommendations.append(
                        "Install optional quality tools for better development experience: "
                        "pip install black mypy pylint isort"
                    )
                else:
                    # Generic warning recommendation
                    recommendations.append(f"Warning: {check.message}")

    # Build detailed results if verbose
    if verbose:
        details = [
            {
                "name": check.name,
                "passed": check.passed,
                "message": check.message,
                "severity": check.severity,
            }
            for check in verifier.results
        ]

    # Determine overall status
    if version_check < (3, 9, 0):
        status = EnvironmentStatus.MISSING_PYTHON
    elif verifier.critical_failures > 0:
        # Check if it's specifically dependency issues
        has_dep_failure = any(
            "Dependencies" in check.name and not check.passed
            for check in verifier.results
        )
        status = EnvironmentStatus.MISSING_DEPS if has_dep_failure else EnvironmentStatus.MISSING_PYTHON
    elif verifier.warnings > 0:
        status = EnvironmentStatus.PARTIAL
        # Add generic recommendation if none generated from specific checks
        if not recommendations:
            recommendations.append(
                "Environment has warnings. Review details for optional improvements."
            )
    else:
        status = EnvironmentStatus.READY

    # Attempt auto-fix if requested
    if auto_fix and missing_packages:
        recommendations.append("Attempting automatic package installation...")
        try:
            # Use pip to install missing packages
            subprocess.run(
                [sys.executable, "-m", "pip", "install"] + missing_packages,
                check=True,
                capture_output=True,
                text=True,
            )
            recommendations.append(
                f"✅ Successfully installed: {', '.join(missing_packages)}"
            )
            # Re-run checks after installation
            verifier_recheck = EnvironmentVerifier()
            recheck_exit_code = verifier_recheck.run_all_checks()
            if recheck_exit_code == 0:
                status = EnvironmentStatus.READY
                missing_packages = []
        except subprocess.CalledProcessError as e:
            recommendations.append(
                f"❌ Auto-fix failed: {e.stderr}. Please install manually."
            )

    return EnvironmentCheckResult(
        status=status,
        python_version=python_version,
        missing_packages=missing_packages,
        recommendations=recommendations,
        details=details,
    )
