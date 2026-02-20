"""
MCP Tools for Change Coherence Engine.

AC_START: AC-ENH-101-011
Description: MCP tool cortex_validate_coherence
Authority: ENH-101 Stage S5 - MCP Integration
Compliance: MCP-FIRST architecture

Purpose:
    Exposes coherence validation via MCP:
    - cortex_validate_coherence: Validate file coherence
    
ENFORCEMENT: All tools MUST validate orchestrator_context.
Only MasterOrchestrator can invoke directly (via cortex_process_request entry point).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional
from cortex.mcp.tools._shared import validate_orchestrator_context

from cortex.orchestrators.validation import (
    ChangeCoherenceEngine,
    CoherenceReport,
    CoherenceStatus,
    PreEditContext,
)

logger = logging.getLogger(__name__)



async def cortex_validate_coherence(
    file_path: str,
    content: str,
    pre_edit_content: Optional[str] = None,
    check_duplicates: bool = True,
    check_versions: bool = True,
    check_structure: bool = True,
    orchestrator_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Validate file coherence using Change Coherence Engine.
    
    MCP Tool: cortex_validate_coherence
    
    ENFORCEMENT: Validates orchestrator_context on entry.
    
    This tool validates that file modifications maintain coherence:
    - No duplicate sections introduced
    - Version markers consistent
    - Structure not degraded
    - Best practices maintained
    
    Args:
        file_path: Path to the file being validated
        content: Current/proposed file content
        pre_edit_content: Original content before edits (optional)
        check_duplicates: Whether to check for duplicates
        check_versions: Whether to check version consistency
        check_structure: Whether to check structure preservation
        orchestrator_context: Context from MasterOrchestrator (required)
        
    Returns:
        Dict with validation results:
        {
            "status": "passed" | "warning" | "failed",
            "file_path": str,
            "issues": [
                {
                    "type": str,
                    "severity": str,
                    "message": str,
                    "location": str,
                    "suggestion": str
                }
            ],
            "duplicates_found": int,
            "version_consistent": bool,
            "recommendations": [str],
            "summary": str
        }
    
    Example:
        >>> result = await cortex_validate_coherence(
        ...     file_path="README.md",
        ...     content="# Title\\n\\n## Section\\n\\n## Section",
        ... )
        >>> print(result["status"])
        "failed"
        >>> print(result["issues"][0]["message"])
        "Duplicate section 'Section' found..."
    """
    # ENFORCEMENT: Validate orchestrator routing
    validate_orchestrator_context(orchestrator_context)
    
    try:
        from cortex.orchestrators.validation.structure_analyzer import StructureAnalyzer
        from cortex.orchestrators.validation.duplicate_scanner import DuplicateScanner
        from cortex.orchestrators.validation import (
            CoherenceValidator,
            ValidationConfig,
        )
        
        analyzer = StructureAnalyzer()
        scanner = DuplicateScanner()
        
        # If we have pre-edit content, do before/after comparison
        if pre_edit_content:
            # Analyze pre-edit structure
            pre_structure = analyzer.analyze(pre_edit_content, file_path)
            pre_duplicates = scanner.scan_sections(pre_structure.sections)
            
            # Create pre-context
            pre_context = PreEditContext(
                file_path=Path(file_path),
                original_content=pre_edit_content,
                structure=pre_structure,
                existing_duplicates=pre_duplicates.all_duplicates,
                relevant_practices=[],
            )
            
            # Validate post-edit content
            config = ValidationConfig(
                check_duplicates=check_duplicates,
                check_versions=check_versions,
                check_structure=check_structure,
                similarity_threshold=0.8,
            )
            
            validator = CoherenceValidator(config=config)
            validation_result = validator.validate(pre_context, content)
            
            # Scan post-edit for duplicates
            post_structure = analyzer.analyze(content, file_path)
            post_scan = scanner.scan_sections(post_structure.sections)
            
            # Check version consistency
            version_issues = validation_result.details.get("issues", [])
            has_version_mismatch = any(
                i.get("type") == "version_mismatch" for i in version_issues
            )
            
            report = CoherenceReport(
                file_path=Path(file_path),
                status=validation_result.status,
                validation_results=[validation_result],
                duplicates_found=post_scan.all_duplicates,
                version_consistent=not has_version_mismatch,
                best_practice_violations=[],
                recommendations=validation_result.details.get("recommendations", []),
            )
        else:
            # Just check the content directly (no before/after comparison)
            from cortex.orchestrators.validation import (
                CoherenceValidator,
                FileStructure,
                ValidationConfig,
            )
            from cortex.orchestrators.validation.structure_analyzer import StructureAnalyzer
            
            config = ValidationConfig(
                check_duplicates=check_duplicates,
                check_versions=check_versions,
                check_structure=False,  # Can't check without pre-edit
                similarity_threshold=0.8,
            )
            
            validator = CoherenceValidator(config=config)
            analyzer = StructureAnalyzer()
            
            # Create minimal pre-context for validation
            structure = analyzer.analyze(content, file_path)
            pre_context = PreEditContext(
                file_path=Path(file_path),
                original_content=content,
                structure=structure,
            )
            
            validation_result = validator.validate(pre_context, content)
            
            # Build report manually
            from cortex.orchestrators.validation.duplicate_scanner import DuplicateScanner
            
            scanner = DuplicateScanner()
            scan_result = scanner.scan_sections(structure.sections)
            
            version_issues = validation_result.details.get("issues", [])
            has_version_mismatch = any(
                i.get("type") == "version_mismatch" for i in version_issues
            )
            
            report = CoherenceReport(
                file_path=Path(file_path),
                status=validation_result.status,
                validation_results=[validation_result],
                duplicates_found=scan_result.all_duplicates,
                version_consistent=not has_version_mismatch,
                best_practice_violations=[],
                recommendations=validation_result.details.get("recommendations", []),
            )
        
        # Format response
        issues = []
        if report.validation_results:
            for vr in report.validation_results:
                for issue in vr.details.get("issues", []):
                    issues.append({
                        "type": issue.get("type", "unknown"),
                        "severity": issue.get("severity", "info"),
                        "message": issue.get("message", ""),
                        "location": issue.get("location", ""),
                        "suggestion": issue.get("suggestion", ""),
                    })
        
        return {
            "status": report.status.value,
            "file_path": str(report.file_path),
            "issues": issues,
            "duplicates_found": len(report.duplicates_found),
            "version_consistent": report.version_consistent,
            "recommendations": report.recommendations,
            "summary": report.summary(),
        }
        
    except Exception as e:
        logger.exception("Error in cortex_validate_coherence")
        return {
            "status": "error",
            "file_path": file_path,
            "issues": [{
                "type": "error",
                "severity": "error",
                "message": f"Validation error: {str(e)}",
                "location": "",
                "suggestion": "Check file format and content",
            }],
            "duplicates_found": 0,
            "version_consistent": True,
            "recommendations": [],
            "summary": f"Error: {str(e)}",
        }


# MCP Tool Registration
MCP_TOOLS = [
    {
        "name": "cortex_validate_coherence",
        "description": "Validate file coherence - detect duplicates, version inconsistencies, and structural issues",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file being validated",
                },
                "content": {
                    "type": "string",
                    "description": "Current/proposed file content",
                },
                "pre_edit_content": {
                    "type": "string",
                    "description": "Original content before edits (optional)",
                },
                "check_duplicates": {
                    "type": "boolean",
                    "description": "Whether to check for duplicates (default: true)",
                    "default": True,
                },
                "check_versions": {
                    "type": "boolean",
                    "description": "Whether to check version consistency (default: true)",
                    "default": True,
                },
                "check_structure": {
                    "type": "boolean",
                    "description": "Whether to check structure preservation (default: true)",
                    "default": True,
                },
            },
            "required": ["file_path", "content"],
        },
        "handler": cortex_validate_coherence,
    },
]


# AC_COMPLETE: AC-ENH-101-011 ✅ MCP tool cortex_validate_coherence
