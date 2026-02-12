"""
AC-FILENAME-FACTORY-001: MCP Tool Exposure

Exposes filename factory capabilities via MCP decorator for Claude usage.
Provides suggestion and validation tools without enforcing file creation.

CORE Rules Applied:
- CORE-024: MCP Decorator (Tool Registration)
- CORE-027: Audit trail logging
"""

import logging
from typing import Any, Dict, List, Optional

from cortex.governance.filename_factory import (
    FilenameFactory,
    FilenameValidator,
    FilePathEnforcer,
)
from cortex.mcp.decorators import mcp_tool

logger = logging.getLogger(__name__)


@mcp_tool(
    name="suggest-compliant-filename",
    description="Suggest CORE-028 compliant filename from natural language purpose",
    category="governance",
)
def suggest_compliant_filename(
    purpose: str,
    file_type: str,
    max_chars: int = 25,
    prefix: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Suggest a filename compliant with CORE-028 rules.

    CORE-028 Requirements:
    - Kebab-case (lowercase with hyphens)
    - Maximum 25 characters including extension
    - Uses semantic acronyms

    Args:
        purpose: Natural language description of file purpose
        file_type: File extension (py, yaml, md, db, txt, etc.)
        max_chars: Maximum filename length (default 25)
        prefix: Optional prefix (e.g., "test" for test files)

    Returns:
        Dictionary with suggested filename, reasoning, and alternatives

    Example:
        >>> suggest_compliant_filename(
        ...     purpose="logging analysis utility",
        ...     file_type="py"
        ... )
        {
            "success": True,
            "filename": "log-ana-util.py",
            "reasoning": "Generated from 'logging analysis utility'...",
            "alternatives": ["log-ana.py", "log-util.py"]
        }
    """
    try:
        factory = FilenameFactory()
        result = factory.generate(
            purpose=purpose,
            file_type=file_type,
            max_chars=max_chars,
            prefix=prefix
        )

        logger.info(f"Filename suggestion: {result.filename} for purpose: {purpose}")

        return {
            "success": result.success,
            "filename": result.filename,
            "reasoning": result.reasoning,
            "alternatives": result.alternative_names,
            "rule": "CORE-028 (Kebab-case, 25-char limit)",
        }

    except Exception as e:
        logger.error(f"Filename suggestion failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "rule": "CORE-028",
        }


@mcp_tool(
    name="validate-filename",
    description="Validate filename against CORE-028 rules",
    category="governance",
)
def validate_filename(filename: str) -> Dict[str, Any]:
    """
    Validate filename against CORE-028 rules.

    CORE-028 Requirements:
    - Kebab-case (lowercase with hyphens)
    - Maximum 25 characters including extension
    - Self-documenting purpose

    Args:
        filename: Filename to validate (e.g., "cortex-vacuum-exec.py")

    Returns:
        Dictionary with validation status and any violations

    Example:
        >>> validate_filename("cortex-vacuum-exec.py")
        {
            "is_valid": True,
            "violations": [],
            "message": "Filename is compliant with CORE-028"
        }
    """
    try:
        validator = FilenameValidator()
        result = validator.validate(filename)

        if result.is_valid:
            logger.info(f"Filename valid: {filename}")
            return {
                "is_valid": True,
                "violations": [],
                "message": "Filename is compliant with CORE-028",
                "rule": "CORE-028",
            }
        else:
            violations = [
                {
                    "code": v.code,
                    "message": v.message,
                    "suggestion": v.suggestion,
                    "severity": v.severity,
                }
                for v in result.violations
            ]

            logger.warning(f"Filename invalid: {filename}, violations: {violations}")

            return {
                "is_valid": False,
                "violations": violations,
                "message": f"Filename violates {len(result.violations)} rule(s)",
                "rule": "CORE-028",
            }

    except Exception as e:
        logger.error(f"Filename validation failed: {e}")
        return {
            "is_valid": False,
            "error": str(e),
            "rule": "CORE-028",
        }


@mcp_tool(
    name="validate-filepath",
    description="Validate file path against CORE-038 placement policy",
    category="governance",
)
def validate_filepath(path: str, file_type: str) -> Dict[str, Any]:
    """
    Validate file path against CORE-038 placement policy.

    CORE-038 Requirements:
    - NO files at repository root (except whitelist)
    - .md files only in docs/{subfolder}/ or reports/{subfolder}/
    - .py files only in cortex/{module}/, cortex_brain/{module}/, or tests/
    - cortex_brain files follow tier structure

    Args:
        path: Full file path to validate
        file_type: File extension/type (py, md, yaml, etc.)

    Returns:
        Dictionary with validation status and any violations

    Example:
        >>> validate_filepath(
        ...     path="/Users/asifhussain/PROJECTS/CORTEX/cortex/governance/filename-factory.py",
        ...     file_type="py"
        ... )
        {
            "is_valid": True,
            "violations": [],
            "message": "Path is compliant with CORE-038"
        }
    """
    try:
        from pathlib import Path
        enforcer = FilePathEnforcer()
        result = enforcer.validate_path(Path(path), file_type)

        if result.is_valid:
            logger.info(f"Path valid: {path}")
            return {
                "is_valid": True,
                "violations": [],
                "message": "Path is compliant with CORE-038",
                "rule": "CORE-038",
            }
        else:
            violations = [
                {
                    "code": v.code,
                    "message": v.message,
                    "suggested_path": v.suggested_path,
                    "severity": v.severity,
                }
                for v in result.violations
            ]

            logger.warning(f"Path invalid: {path}, violations: {violations}")

            return {
                "is_valid": False,
                "violations": violations,
                "message": f"Path violates {len(result.violations)} rule(s)",
                "rule": "CORE-038",
            }

    except Exception as e:
        logger.error(f"Path validation failed: {e}")
        return {
            "is_valid": False,
            "error": str(e),
            "rule": "CORE-038",
        }


@mcp_tool(
    name="suggest-compliant-path",
    description="Suggest CORE-038 compliant file path",
    category="governance",
)
def suggest_compliant_path(
    filename: str,
    file_type: str,
    domain: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Suggest a file path compliant with CORE-038 placement policy.

    CORE-038 Domains:
    - "py": Python modules → cortex/{module}/
    - "md-doc": Documentation → docs/{subfolder}/
    - "md-report": Reports → reports/{subfolder}/
    - "test": Tests → tests/{subfolder}/

    Args:
        filename: Desired filename (should already be CORE-028 compliant)
        file_type: File extension (py, md, yaml, etc.)
        domain: Optional domain hint (py, doc, report, test)

    Returns:
        Dictionary with suggested path and reasoning

    Example:
        >>> suggest_compliant_path(
        ...     filename="cortex-vacuum-exec.py",
        ...     file_type="py",
        ...     domain="py"
        ... )
        {
            "success": True,
            "suggested_path": "/Users/.../CORTEX/cortex/governance/cortex-vacuum-exec.py",
            "reasoning": "Python module files belong in cortex/{module}/"
        }
    """
    try:
        # Suggest path based on file type and domain
        base_path = "/Users/asifhussain/PROJECTS/CORTEX"

        if file_type == "py":
            if domain == "test":
                path = f"{base_path}/tests/unit/governance/{filename}"
            else:
                path = f"{base_path}/cortex/governance/{filename}"
        elif file_type in ("md", "markdown"):
            if domain == "report":
                path = f"{base_path}/reports/governance/{filename}"
            else:
                path = f"{base_path}/docs/guides/{filename}"
        elif file_type in ("yaml", "yml"):
            if domain == "cortex-brain":
                path = f"{base_path}/cortex_brain/tier0/governance/{filename}"
            else:
                path = f"{base_path}/cortex/governance/{filename}"
        else:
            path = f"{base_path}/cortex/{filename}"

        logger.info(f"Path suggestion: {path} for filename: {filename}")

        return {
            "success": True,
            "suggested_path": path,
            "reasoning": f"File type '{file_type}' with domain '{domain}' suggests this path",
            "rule": "CORE-038",
        }

    except Exception as e:
        logger.error(f"Path suggestion failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "rule": "CORE-038",
        }


__all__ = [
    "suggest_compliant_filename",
    "validate_filename",
    "validate_filepath",
    "suggest_compliant_path",
]
