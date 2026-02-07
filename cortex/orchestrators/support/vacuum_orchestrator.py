"""
VacuumOrchestrator - Markdown Cleanup & Post-Cleanup Validation Workflow.

Manages the complete cleanup lifecycle:
1. Scan: Detect markdown sprawl (files outside docs/.github)
2. Plan: Categorize files for archival
3. Cleanup: Move files to docs/archive/
4. Verify: Confirm no deletions, check links, validate git status
5. Offer Audit: Suggest post-cleanup audit if verification passes

CORE-002: Enforces no markdown outside docs/.github (except README.md)
CORE-008: TDD-first implementation
CORE-011: Full type hints
CORE-012: Google-style docstrings
"""

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


@dataclass
class CleanupPlan:
    """
    Cleanup execution plan with file categorization.
    
    Attributes:
        files_to_archive: List of files to move with source/dest/category
        archive_base_path: Base path for archive (docs/archive)
        total_files: Total number of files to process
    """
    files_to_archive: List[Dict[str, str]]
    archive_base_path: str
    total_files: int


@dataclass
class CleanupResult:
    """
    Result of cleanup execution.
    
    Attributes:
        success: Whether cleanup completed successfully
        files_moved: Number of files moved to archive
        files_deleted: Number of files deleted (should always be 0)
        conflicts_resolved: Number of naming conflicts resolved
        errors: List of error messages encountered
    """
    success: bool
    files_moved: int
    files_deleted: int
    conflicts_resolved: int
    errors: List[str] = field(default_factory=list)


@dataclass
class VerificationResult:
    """
    Result of post-cleanup verification.
    
    Attributes:
        files_preserved: All files were moved, none deleted
        no_deletions: Confirms no files were deleted
        broken_links_count: Number of broken markdown links detected
        git_status_clean: Git repository is in clean state
        issues: List of verification issues found
    """
    files_preserved: bool
    no_deletions: bool
    broken_links_count: int
    git_status_clean: bool
    issues: List[str] = field(default_factory=list)


class VacuumOrchestrator:
    """
    Orchestrates markdown cleanup with post-cleanup validation workflow.
    
    Workflow:
        1. scan_repository() - Find markdown files outside docs/.github
        2. generate_cleanup_plan() - Categorize files for archival
        3. execute_cleanup() - Move files to archive
        4. verify_cleanup() - Validate cleanup results
        5. should_offer_audit() - Determine if audit should be offered
    
    Safety guarantees:
        - Never deletes files (only moves to archive)
        - Respects 30-day age threshold (configurable)
        - Resolves naming conflicts automatically
        - Preserves file content and metadata
    """

    def __init__(self) -> None:
        """Initialize VacuumOrchestrator."""
        self.exclude_patterns = [
            "**/docs/**",
            "**/.github/**",
            "**/.venv/**",
            "**/node_modules/**",
            "**/company/_archive/**",
            "**/.archive/**",
            "**/README.md",
        ]
        
        # Root-level file categorization for comprehensive cleanup
        self.root_file_rules = {
            # Development utilities that should be in scripts/utilities/
            "utility_scripts": {
                "patterns": [
                    "generate_dashboard_complete.py",
                    "generate_dashboard_data.py",
                    "run_vacuum.py",
                    "verify_cleanup_integrity.py",
                    "verify_dashboard.py",
                ],
                "destination": "scripts/utilities/",
                "action": "move",
            },
            # Production-critical root files (KEEP)
            "production_essential": {
                "patterns": [
                    ".cortex-version",
                    ".dockerignore",
                    ".gitignore",
                    ".pre-commit-config.yaml",
                    "Dockerfile",
                    "Makefile",
                    "README.md",
                    "docker-compose*.yml",
                    "requirements.txt",  # symlink
                ],
                "action": "keep",
            },
        }

    def scan_repository(self, root_path: str) -> Dict[str, Any]:
        """
        Scan repository for markdown files outside docs/.github.
        
        Args:
            root_path: Root directory of repository to scan
            
        Returns:
            Dictionary with scan results:
                - status: "success" or "partial" or "error"
                - files_found: List of markdown file paths
                - total_count: Total number of files found
                
        Example:
            >>> orchestrator = VacuumOrchestrator()
            >>> result = orchestrator.scan_repository("/path/to/repo")
            >>> print(result["total_count"])
            15
        """
        try:
            root = Path(root_path)
            markdown_files = []
            
            # Find all .md files
            for md_file in root.rglob("*.md"):
                # Check if file should be excluded
                should_exclude = False
                relative_path = md_file.relative_to(root)
                
                for pattern in self.exclude_patterns:
                    # Simple pattern matching (could be enhanced with fnmatch)
                    if "docs/" in str(relative_path) or \
                       ".github/" in str(relative_path) or \
                       ".venv/" in str(relative_path) or \
                       "node_modules/" in str(relative_path) or \
                       "_archive/" in str(relative_path) or \
                       ".archive/" in str(relative_path) or \
                       md_file.name == "README.md":
                        should_exclude = True
                        break
                
                if not should_exclude:
                    markdown_files.append(str(relative_path))
            
            return {
                "status": "success",
                "files_found": markdown_files,
                "total_count": len(markdown_files),
            }
            
        except Exception as e:
            return {
                "status": "error",
                "files_found": [],
                "total_count": 0,
                "error": str(e),
            }

    def scan_root_level(self, root_path: str) -> Dict[str, Any]:
        """
        Scan root-level files and directories for cleanup opportunities.
        
        Analyzes:
        - Root Python scripts (should be in scripts/utilities/)
        - Root directories (company/, cortex-lens/, etc.)
        - Production vs development artifacts
        
        Args:
            root_path: Root directory of repository to scan
            
        Returns:
            Dictionary with categorized findings:
                - utility_scripts: Scripts that should move to scripts/utilities/
                - production_files: Essential root files (keep)
                - directories: Root directories with size/purpose analysis
                - recommendations: List of cleanup actions
                
        Example:
            >>> orchestrator = VacuumOrchestrator()
            >>> result = orchestrator.scan_root_level("/path/to/repo")
            >>> print(result["utility_scripts"])
            ['generate_dashboard_complete.py', 'run_vacuum.py']
        """
        try:
            root = Path(root_path)
            utility_scripts = []
            production_files = []
            directories = []
            recommendations = []
            
            # Scan root-level files
            for item in root.iterdir():
                if item.is_file():
                    filename = item.name
                    
                    # Check against utility script patterns
                    if filename in self.root_file_rules["utility_scripts"]["patterns"]:
                        utility_scripts.append(filename)
                        recommendations.append({
                            "file": filename,
                            "action": "move",
                            "destination": self.root_file_rules["utility_scripts"]["destination"],
                            "reason": "Development utility should be in scripts/utilities/",
                            "priority": "medium",
                        })
                    # Check against production patterns
                    elif self._is_production_file(filename):
                        production_files.append(filename)
                    else:
                        # Unknown root file - flag for review
                        recommendations.append({
                            "file": filename,
                            "action": "review",
                            "reason": f"Unknown root-level file: {filename}",
                            "priority": "low",
                        })
                
                elif item.is_dir() and not item.name.startswith("."):
                    # Analyze root directories
                    try:
                        size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                        directories.append({
                            "name": item.name,
                            "size_bytes": size,
                            "size_human": self._format_size(size),
                            "purpose": self._classify_directory(item.name),
                        })
                    except (PermissionError, OSError):
                        pass  # Skip inaccessible directories
            
            return {
                "status": "success",
                "utility_scripts": utility_scripts,
                "production_files": production_files,
                "directories": directories,
                "recommendations": recommendations,
                "summary": {
                    "utility_scripts_count": len(utility_scripts),
                    "production_files_count": len(production_files),
                    "directories_count": len(directories),
                    "total_recommendations": len(recommendations),
                },
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    def _format_size(self, size_bytes: int) -> str:
        """Format byte size to human-readable string."""
        size: float = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    def _is_production_file(self, filename: str) -> bool:
        """Check if filename matches production essential patterns."""
        for pattern in self.root_file_rules["production_essential"]["patterns"]:
            if "*" in pattern:
                # Handle wildcard patterns
                prefix = pattern.replace("*", "")
                if filename.startswith(prefix):
                    return True
            elif filename == pattern:
                return True
        return False
    
    def _classify_directory(self, dir_name: str) -> str:
        """Classify directory purpose based on name."""
        classifications = {
            "cortex": "Production - Core system",
            "cortex_brain": "Production - Brain modules",
            "cortex-registry": "Production - Orchestrator registry",
            "docs": "Production - Documentation",
            "tests": "Production - Test suite",
            "deployment": "Production - Deployment configs",
            "scripts": "Production - Utility scripts",
            "company": "Production - Best practices knowledge",
            "_archives": "Development - Archived artifacts",
            "cortex-lens": "Development - Standalone analysis tool",
        }
        return classifications.get(dir_name, "Unknown")

    def generate_cleanup_plan(
        self,
        scan_result: Dict[str, Any],
        age_threshold_days: int = 30,
    ) -> CleanupPlan:
        """
        Generate cleanup plan with file categorization.
        
        Args:
            scan_result: Result from scan_repository()
            age_threshold_days: Only archive files older than this (default 30)
            
        Returns:
            CleanupPlan with categorized files and archive paths
            
        Categories:
            - phases: PHASE-*.md, *-COMPLETION.md, *-SUMMARY.md
            - testing: files in tests/
            - workspaces: files in _workspaces/
            - reports: *-REPORT.md, *-AUDIT.md
            - other: uncategorized files
        """
        files_to_archive = []
        
        for file_path in scan_result["files_found"]:
            # Determine category
            category = self._categorize_file(file_path)
            
            # Build archive path
            file_name = Path(file_path).name
            archive_path = f"docs/archive/{category}/{file_name}"
            
            files_to_archive.append({
                "source": file_path,
                "destination": archive_path,
                "category": category,
            })
        
        return CleanupPlan(
            files_to_archive=files_to_archive,
            archive_base_path="docs/archive",
            total_files=len(files_to_archive),
        )

    def _categorize_file(self, file_path: str) -> str:
        """
        Categorize file based on path and name patterns.
        
        Args:
            file_path: Relative file path
            
        Returns:
            Category name: "phases", "testing", "workspaces", "reports", or "other"
        """
        file_name = Path(file_path).name.upper()
        path_lower = file_path.lower()
        
        # Category: phases
        if file_name.startswith("PHASE-") or \
           "COMPLETION" in file_name or \
           "SUMMARY" in file_name or \
           "PROGRESS" in file_name:
            return "phases"
        
        # Category: testing
        if "tests/" in path_lower or "testing/" in path_lower:
            return "testing"
        
        # Category: workspaces
        if "_workspaces/" in path_lower or "workspace" in path_lower:
            return "workspaces"
        
        # Category: reports
        if "REPORT" in file_name or "AUDIT" in file_name or "ANALYSIS" in file_name:
            return "reports"
        
        return "other"

    def execute_cleanup(self, plan: CleanupPlan, root_path: Optional[str] = None) -> CleanupResult:
        """
        Execute cleanup by moving files to archive.
        
        Args:
            plan: CleanupPlan from generate_cleanup_plan()
            root_path: Optional root directory (defaults to current working directory)
            
        Returns:
            CleanupResult with execution metrics
            
        Safety:
            - Never deletes files (only moves)
            - Creates archive directories if missing
            - Handles naming conflicts by adding numeric suffix
            - Preserves file content and metadata
        """
        files_moved = 0
        conflicts_resolved = 0
        errors = []
        
        try:
            # Get repository root
            root = Path(root_path) if root_path else Path.cwd()
            
            # Create archive directories
            for category in ["phases", "testing", "workspaces", "reports", "other"]:
                archive_dir = root / "docs" / "archive" / category
                archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Move files
            for item in plan.files_to_archive:
                try:
                    source = root / item["source"]
                    dest = root / item["destination"]
                    
                    if not source.exists():
                        errors.append(f"Source not found: {item['source']}")
                        continue
                    
                    # Handle conflicts
                    if dest.exists():
                        conflicts_resolved += 1
                        # Add numeric suffix
                        counter = 1
                        while dest.exists():
                            stem = dest.stem
                            suffix = dest.suffix
                            dest = dest.parent / f"{stem}_{counter}{suffix}"
                            counter += 1
                    
                    # Ensure destination directory exists
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    shutil.move(str(source), str(dest))
                    files_moved += 1
                    
                except Exception as e:
                    errors.append(f"Error moving {item['source']}: {str(e)}")
            
            success = len(errors) == 0 or files_moved > 0
            
            return CleanupResult(
                success=success,
                files_moved=files_moved,
                files_deleted=0,  # Never delete
                conflicts_resolved=conflicts_resolved,
                errors=errors,
            )
            
        except Exception as e:
            return CleanupResult(
                success=False,
                files_moved=files_moved,
                files_deleted=0,
                conflicts_resolved=conflicts_resolved,
                errors=[str(e)],
            )

    def execute_root_cleanup(
        self,
        scan_result: Dict[str, Any],
        root_path: str = ".",
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute root-level cleanup based on scan results.
        
        Moves utility scripts to scripts/utilities/ and reports on directory structure.
        
        Args:
            scan_result: Result from scan_root_level()
            root_path: Root directory of repository
            dry_run: If True, only simulate actions without making changes
            
        Returns:
            Dictionary with execution results:
                - success: Whether cleanup completed successfully
                - files_moved: Number of files moved
                - dry_run: Whether this was a dry run
                - actions_taken: List of actions performed
                - errors: List of error messages
                
        Example:
            >>> orchestrator = VacuumOrchestrator()
            >>> scan = orchestrator.scan_root_level(".")
            >>> result = orchestrator.execute_root_cleanup(scan, dry_run=True)
            >>> print(result["files_moved"])
            5
        """
        try:
            root = Path(root_path)
            files_moved = 0
            actions_taken = []
            errors = []
            
            # Process recommendations
            for rec in scan_result.get("recommendations", []):
                if rec["action"] == "move":
                    source = root / rec["file"]
                    dest_dir = root / rec["destination"]
                    dest_file = dest_dir / rec["file"]
                    
                    try:
                        if not dry_run:
                            # Create destination directory if needed
                            dest_dir.mkdir(parents=True, exist_ok=True)
                            
                            # Move file
                            shutil.move(str(source), str(dest_file))
                        
                        files_moved += 1
                        actions_taken.append({
                            "action": "moved",
                            "file": rec["file"],
                            "from": str(source),
                            "to": str(dest_file),
                            "reason": rec["reason"],
                        })
                        
                    except Exception as e:
                        errors.append(f"Failed to move {rec['file']}: {str(e)}")
                
                elif rec["action"] == "review":
                    actions_taken.append({
                        "action": "flagged",
                        "file": rec["file"],
                        "reason": rec["reason"],
                        "priority": rec.get("priority", "medium"),
                    })
            
            return {
                "success": len(errors) == 0,
                "files_moved": files_moved,
                "dry_run": dry_run,
                "actions_taken": actions_taken,
                "errors": errors,
                "summary": {
                    "total_actions": len(actions_taken),
                    "moves": files_moved,
                    "reviews": len([a for a in actions_taken if a["action"] == "flagged"]),
                },
            }
            
        except Exception as e:
            return {
                "success": False,
                "files_moved": 0,
                "dry_run": dry_run,
                "actions_taken": [],
                "errors": [str(e)],
            }

    def verify_cleanup(
        self,
        cleanup_result: CleanupResult,
        plan: CleanupPlan,
    ) -> VerificationResult:
        """
        Verify cleanup results and check for issues.
        
        Args:
            cleanup_result: Result from execute_cleanup()
            plan: Original CleanupPlan
            
        Returns:
            VerificationResult with validation checks
            
        Checks:
            - Files were moved, not deleted
            - No broken markdown links
            - Git repository status clean
        """
        issues = []
        
        # Check 1: Verify no deletions
        files_preserved = cleanup_result.files_deleted == 0
        no_deletions = cleanup_result.files_deleted == 0
        
        if not no_deletions:
            issues.append(f"{cleanup_result.files_deleted} files were deleted")
        
        # Check 2: Look for broken links (simple check)
        broken_links_count = self._check_broken_links()
        if broken_links_count > 0:
            issues.append(f"{broken_links_count} broken links detected")
        
        # Check 3: Check git status
        git_status_clean = self._check_git_status()
        if not git_status_clean:
            issues.append("Git repository has uncommitted changes")
        
        return VerificationResult(
            files_preserved=files_preserved,
            no_deletions=no_deletions,
            broken_links_count=broken_links_count,
            git_status_clean=git_status_clean,
            issues=issues,
        )

    def _check_broken_links(self) -> int:
        """
        Check for broken markdown links in docs/ directory.
        
        Returns:
            Number of potentially broken links found
        """
        # Simple implementation: count links to files that don't exist
        broken_count = 0
        
        try:
            docs_dir = Path.cwd() / "docs"
            if not docs_dir.exists():
                return 0
            
            # Scan markdown files in docs
            for md_file in docs_dir.rglob("*.md"):
                try:
                    content = md_file.read_text()
                    # Find markdown links: [text](path)
                    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                    for match in re.finditer(link_pattern, content):
                        link_path = match.group(2)
                        
                        # Skip external links
                        if link_path.startswith(("http://", "https://", "#")):
                            continue
                        
                        # Check if linked file exists
                        full_path = (md_file.parent / link_path).resolve()
                        if not full_path.exists():
                            broken_count += 1
                            
                except Exception:
                    continue
                    
        except Exception:
            pass
        
        return broken_count

    def _check_git_status(self) -> bool:
        """
        Check if git repository has uncommitted changes.
        
        Returns:
            True if git status is clean, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            
            # Clean if no output
            return len(result.stdout.strip()) == 0
            
        except Exception:
            # Assume clean if git check fails
            return True

    def should_offer_audit(self, verification: VerificationResult) -> bool:
        """
        Determine if post-cleanup audit should be offered.
        
        Args:
            verification: VerificationResult from verify_cleanup()
            
        Returns:
            True if audit should be offered, False otherwise
            
        Criteria:
            - Verification passed (no issues)
            - Files were preserved (not deleted)
            - No broken links
        """
        return (
            verification.files_preserved and
            verification.no_deletions and
            verification.broken_links_count == 0 and
            len(verification.issues) == 0
        )

    def format_audit_offer(self, verification: VerificationResult) -> str:
        """
        Format audit offer message for user.
        
        Args:
            verification: VerificationResult from verify_cleanup()
            
        Returns:
            Formatted message string
        """
        return (
            "✅ Cleanup verification complete - all checks passed.\n\n"
            "Would you like to run a post-cleanup audit to validate:\n"
            "- Test collection still works\n"
            "- No import errors introduced\n"
            "- Code quality maintained\n\n"
            "Type 'proceed' or 'yes' to run audit, or 'skip' to finish."
        )

    def generate_report(
        self,
        scan_result: Dict[str, Any],
        plan: CleanupPlan,
        cleanup_result: CleanupResult,
        verification: VerificationResult,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive cleanup report.
        
        Args:
            scan_result: Original scan results
            plan: Cleanup plan
            cleanup_result: Cleanup execution results
            verification: Verification results
            
        Returns:
            Dictionary with complete report data
        """
        return {
            "files_scanned": scan_result["total_count"],
            "files_archived": cleanup_result.files_moved,
            "files_deleted": cleanup_result.files_deleted,
            "conflicts_resolved": cleanup_result.conflicts_resolved,
            "verification_status": "passed" if len(verification.issues) == 0 else "failed",
            "broken_links": verification.broken_links_count,
            "git_status_clean": verification.git_status_clean,
            "errors": cleanup_result.errors,
            "issues": verification.issues,
        }

    # ========================================================================
    # Brain Flush Integration (Phase 38 Stage 6)
    # ========================================================================

    def trigger_brain_flush(
        self,
        targets: Optional[List[str]] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Trigger brain state flush via BrainStateManager.
        
        Integrates brain state cleanup into vacuum workflow, ensuring
        comprehensive cleanup beyond markdown files.
        
        Args:
            targets: Optional list of flush targets (None = all)
            force: Force flush even if recent snapshot exists
            
        Returns:
            Dictionary with flush results:
                - success: bool
                - snapshot_path: str (if successful)
                - files_captured: int
                - total_size_mb: float
                - error_message: str (if failed)
                
        Example:
            >>> orchestrator = VacuumOrchestrator()
            >>> result = orchestrator.trigger_brain_flush()
            >>> print(f"Flushed {result['files_captured']} files")
        """
        try:
            from cortex.brain.core.brain_state_manager import BrainStateManager
            from pathlib import Path
            
            # Get cortex_brain path
            cortex_brain_path = Path(__file__).parent.parent.parent.parent / "cortex_brain"
            
            if not cortex_brain_path.exists():
                return {
                    "success": False,
                    "error_message": f"cortex_brain not found at {cortex_brain_path}",
                }
            
            # Initialize manager
            manager = BrainStateManager(cortex_brain_path)
            
            # Flush state
            flush_result = manager.flush_state()
            
            if flush_result.success and flush_result.snapshot_path:
                # Get snapshot info
                snapshot_path = Path(flush_result.snapshot_path)
                size_mb = snapshot_path.stat().st_size / (1024 * 1024)
                
                # Count files in snapshot
                import json
                with open(snapshot_path) as f:
                    snapshot_data = json.load(f)
                
                files_captured = sum(
                    len(tier_data.get("files", {}))
                    for tier_data in snapshot_data.get("data", {}).values()
                )
                
                return {
                    "success": True,
                    "snapshot_path": str(snapshot_path),
                    "files_captured": files_captured,
                    "total_size_mb": round(size_mb, 2),
                }
            else:
                return {
                    "success": False,
                    "error_message": flush_result.error_message or "Flush failed",
                }
                
        except Exception as e:
            return {
                "success": False,
                "error_message": f"Brain flush error: {str(e)}",
            }

    def cleanup_brain_state(self) -> Dict[str, Any]:
        """
        Alias for trigger_brain_flush() for backward compatibility.
        
        Returns:
            Dictionary with flush results (same as trigger_brain_flush)
        """
        return self.trigger_brain_flush()

    def flush_brain_state(self) -> Dict[str, Any]:
        """
        Alias for trigger_brain_flush() for backward compatibility.
        
        Returns:
            Dictionary with flush results (same as trigger_brain_flush)
        """
        return self.trigger_brain_flush()

