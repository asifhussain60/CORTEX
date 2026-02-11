"""
MCP Tool: cortex_vacuum

Markdown cleanup tool with post-cleanup validation workflow.
Automates detection, archival, verification, and audit offering for
markdown files outside docs/.github (P3 compliance).

Authority: AC-VACUUM-CLEANUP-001, CORE-002
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from cortex.mcp.decorators import mcp_tool

logger = logging.getLogger(__name__)


@mcp_tool(
    name="cortex_vacuum",
    description="Clean up markdown sprawl with automated archival and verification",
    parameters={
        "repo_path": {
            "type": "string",
            "description": "Path to repository to clean (defaults to current directory)",
            "required": False
        },
        "age_threshold_days": {
            "type": "integer",
            "description": "Archive files older than this threshold (default: 30 days)",
            "required": False
        },
        "execute": {
            "type": "boolean",
            "description": "Execute cleanup (true) or dry-run only (false)",
            "required": False
        }
    }
)
def cortex_vacuum(
    repo_path: Optional[str] = None,
    age_threshold_days: int = 30,
    execute: bool = False,
) -> Dict[str, Any]:
    """
    Clean up markdown sprawl with 5-stage workflow.

    Workflow:
        1. SCAN - Detect markdown files outside docs/.github
        2. PLAN - Categorize files for archival
        3. CLEANUP - Move files to docs/archive/ (if execute=True)
        4. VERIFY - Validate no deletions, check links, git status
        5. AUDIT OFFER - Suggest post-cleanup audit if verification passes

    Safety Guarantees:
        - Never deletes files (only moves to archive)
        - Respects age threshold (default 30 days)
        - Resolves naming conflicts automatically
        - Validates git status and broken links

    Args:
        repo_path: Path to repository (defaults to current directory)
        age_threshold_days: Only archive files older than this (default: 30)
        execute: If True, execute cleanup; if False, dry-run only

    Returns:
        Dict with:
        - success: bool
        - mode: "dry-run" or "execute"
        - scan_result: Dict with files_found, total_count
        - cleanup_plan: Dict with files_to_archive, total_files
        - cleanup_result: Dict with files_moved, conflicts_resolved (if execute=True)
        - verification: Dict with validation results (if execute=True)
        - offer_audit: bool (if execute=True and verification passed)
        - audit_message: str (if offer_audit=True)
        - report: Dict with comprehensive metrics
        - error: str (if failed)

    Example:
        >>> # Dry-run (scan only)
        >>> result = cortex_vacuum(repo_path="/path/to/repo", execute=False)
        >>> print(f"Found {result['scan_result']['total_count']} files")

        >>> # Execute cleanup
        >>> result = cortex_vacuum(repo_path="/path/to/repo", execute=True)
        >>> print(f"Moved {result['cleanup_result']['files_moved']} files")
        >>> if result['offer_audit']:
        ...     print(result['audit_message'])
    """
    try:
        from cortex.orchestrators.support.vacuum_orchestrator import (
            VacuumOrchestrator,
        )

        # Initialize orchestrator
        orchestrator = VacuumOrchestrator()

        # Determine repository path
        target_path = str(Path(repo_path).resolve()) if repo_path else str(Path.cwd())

        # Stage 1: SCAN
        logger.info(f"VacuumOrchestrator: Scanning {target_path} for markdown sprawl")
        scan_result = orchestrator.scan_repository(target_path)

        if scan_result["status"] == "error":
            return {
                "success": False,
                "mode": "scan-failed",
                "error": scan_result.get("error", "Unknown scan error"),
                "repo_path": target_path,
            }

        # Stage 2: PLAN
        logger.info(f"VacuumOrchestrator: Generating cleanup plan ({scan_result['total_count']} files)")
        cleanup_plan = orchestrator.generate_cleanup_plan(
            scan_result=scan_result,
            age_threshold_days=age_threshold_days,
        )

        # Dry-run mode: Return scan + plan only
        if not execute:
            return {
                "success": True,
                "mode": "dry-run",
                "repo_path": target_path,
                "scan_result": {
                    "files_found": scan_result["files_found"],
                    "total_count": scan_result["total_count"],
                },
                "cleanup_plan": {
                    "files_to_archive": cleanup_plan.files_to_archive,
                    "archive_base_path": cleanup_plan.archive_base_path,
                    "total_files": cleanup_plan.total_files,
                },
                "message": f"Dry-run complete. Found {cleanup_plan.total_files} files to archive. Set execute=True to proceed.",
            }

        # Execute mode: Stages 3-5

        # Stage 3: CLEANUP
        logger.info(f"VacuumOrchestrator: Executing cleanup (moving {cleanup_plan.total_files} files)")
        cleanup_result = orchestrator.execute_cleanup(
            plan=cleanup_plan,
            root_path=target_path,
        )

        # Stage 4: VERIFY
        logger.info("VacuumOrchestrator: Verifying cleanup results")
        verification = orchestrator.verify_cleanup(
            cleanup_result=cleanup_result,
            plan=cleanup_plan,
        )

        # Stage 5: AUDIT OFFER
        offer_audit = orchestrator.should_offer_audit(verification)
        audit_message = ""
        if offer_audit:
            audit_message = orchestrator.format_audit_offer(verification)
            logger.info("VacuumOrchestrator: Verification passed - offering post-cleanup audit")
        else:
            logger.warning(f"VacuumOrchestrator: Verification issues detected: {verification.issues}")

        # Generate comprehensive report
        report = orchestrator.generate_report(
            scan_result=scan_result,
            plan=cleanup_plan,
            cleanup_result=cleanup_result,
            verification=verification,
        )

        return {
            "success": cleanup_result.success,
            "mode": "execute",
            "repo_path": target_path,
            "scan_result": {
                "files_found": scan_result["files_found"],
                "total_count": scan_result["total_count"],
            },
            "cleanup_plan": {
                "files_to_archive": cleanup_plan.files_to_archive,
                "archive_base_path": cleanup_plan.archive_base_path,
                "total_files": cleanup_plan.total_files,
            },
            "cleanup_result": {
                "success": cleanup_result.success,
                "files_moved": cleanup_result.files_moved,
                "files_deleted": cleanup_result.files_deleted,
                "conflicts_resolved": cleanup_result.conflicts_resolved,
                "errors": cleanup_result.errors,
            },
            "verification": {
                "files_preserved": verification.files_preserved,
                "no_deletions": verification.no_deletions,
                "broken_links_count": verification.broken_links_count,
                "git_status_clean": verification.git_status_clean,
                "issues": verification.issues,
            },
            "offer_audit": offer_audit,
            "audit_message": audit_message if offer_audit else None,
            "report": report,
        }

    except ImportError as e:
        logger.error(f"cortex_vacuum import error: {e}", exc_info=True)
        return {
            "success": False,
            "mode": "import-error",
            "error": f"Failed to import VacuumOrchestrator: {str(e)}",
            "repo_path": repo_path or str(Path.cwd()),
        }
    except Exception as e:
        logger.error(f"cortex_vacuum failed: {e}", exc_info=True)
        return {
            "success": False,
            "mode": "error",
            "error": str(e),
            "repo_path": repo_path or str(Path.cwd()),
        }
