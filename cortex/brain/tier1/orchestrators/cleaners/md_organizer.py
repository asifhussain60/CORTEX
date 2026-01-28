"""MD Organizer Cleaner - Analyzes and reorganizes markdown files

Implements the CleanerInterface to provide comprehensive markdown file
organization across the CORTEX repository. Scans for all MD files,
categorizes them by type, and generates an execution plan for reorganization.

SOLID Principles:
- Single Responsibility: Only handles MD file organization
- Open/Closed: Can be extended with new categorization rules
- Liskov Substitution: Works transparently via CleanerInterface
- Interface Segregation: Implements only required methods
- Dependency Inversion: Depends on CleanerInterface abstraction

Author: CORTEX Builder
Phase: PHASE-VAC-001-02
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
import logging
import re
from enum import Enum

# Import from cleaner interface
from tier1.orchestrators.cleaners import (
    CleanerInterface,
    Analysis,
    Report,
    RollbackResult,
)


# =============================================================================
# MD File Categories & Classification
# =============================================================================


class MDFileCategory(Enum):
    """Enumeration of MD file categories."""

    PHASE = "phases"  # PHASE-*.md files
    AC_FIX = "fixes"  # AC-FIX-*.md files
    AC_MINOR = "minor_fixes"  # AC-MINOR-*.md files
    SESSION = "sessions"  # SESSION-*.md files
    WEEKLY = "weekly"  # WEEK-*.md files
    COMPLETION = "completion"  # *-COMPLETION-*.md files
    DOCUMENTATION = "documentation"  # General docs
    ARCHITECTURE = "architecture"  # Architecture docs
    IMPLEMENTATION = "implementation"  # Implementation guides
    ROOT = "root"  # Root-level README, index files
    OTHER = "other"  # Uncategorized


class MDFileNamingIssue(Enum):
    """Enumeration of naming issues found in MD files."""

    EXCEEDS_LENGTH = "exceeds_25_chars"  # CORE-028: ≤25 chars
    CAMELCASE = "uses_camelcase"  # Should be kebab-case (MD files use hyphens)
    SPACES = "contains_spaces"  # Should use hyphens
    NO_HYPHEN = "missing_hyphens"  # Should use hyphens
    INCONSISTENT = "inconsistent_format"  # Mixed naming patterns


# =============================================================================
# MD Organizer Cleaner Implementation
# =============================================================================


class MDOrganizerCleaner(CleanerInterface):
    """Cleaner for organizing markdown files in repository.

    Scans the CORTEX repository for markdown files, analyzes their current
    organization and naming conventions, categorizes them into logical groups,
    and generates an execution plan for reorganization according to the
    MD file naming and organization standards defined in CORE-028 and
    project conventions.

    Plugin Domain: 'md_organizer'

    Lifecycle:
    1. analyze() - Scan repository, categorize files, generate plan
    2. execute() - Move/rename files according to plan
    3. rollback() - Restore from pre-execution snapshot

    Type Hints: All parameters and return types fully typed (CORE-011)
    Docstrings: All public methods have Google-style docstrings (CORE-012)
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize MD Organizer with configuration.

        Args:
            config: Configuration dictionary with optional keys:
                - 'repo_root': Repository root path (default: detect)
                - 'target_dir': Target directory for organized files
                - 'dry_run': If True, don't actually move files
                - 'categories': Custom category rules

        Raises:
            ValueError: If repo_root cannot be determined
        """
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Configuration
        self.repo_root = self._resolve_repo_root()
        self.target_dir = config.get("target_dir", ".github/docs")
        self.dry_run = config.get("dry_run", False)

        # State
        self._md_files: Dict[str, Path] = {}
        self._categories: Dict[str, List[str]] = {}
        self._issues: List[Tuple[str, MDFileNamingIssue]] = []
        self._snapshot: Optional[Dict[str, Any]] = None
        self._executed_moves: List[Dict[str, str]] = []

    @property
    def name(self) -> str:
        """Human-readable name.

        Returns:
            Name of this cleaner
        """
        return "MD Organizer Cleaner"

    @property
    def version(self) -> str:
        """Version string.

        Returns:
            Semantic version
        """
        return "1.0.0"

    @property
    def domain(self) -> str:
        """Domain identifier.

        Returns:
            Domain for plugin registration
        """
        return "md_organizer"

    def analyze(self) -> Analysis:
        """Perform non-destructive analysis of markdown files.

        Scans the repository for all markdown files, categorizes them,
        identifies naming/organization issues, and generates an execution
        plan for reorganization.

        Returns:
            Analysis: Contains:
                - files_scanned: Number of MD files found
                - issues_found: Number of organization/naming issues
                - plan: Execution plan with file movements
                - logs: Detailed analysis logs

        Raises:
            ValueError: If repository structure is invalid
        """
        self.logger.info("Starting MD file analysis")
        logs: List[str] = []

        try:
            # Step 1: Scan for all MD files
            logs.append("Scanning repository for markdown files...")
            self._md_files = self._scan_md_files()
            logs.append(f"Found {len(self._md_files)} markdown files")

            # Step 2: Categorize files
            logs.append("Categorizing markdown files...")
            self._categories = self._categorize_files()
            logs.append(
                f"Categorized into {len(self._categories)} groups: "
                f"{', '.join(self._categories.keys())}"
            )

            # Step 3: Identify issues
            logs.append("Identifying naming and organization issues...")
            self._issues = self._identify_issues()
            logs.append(f"Found {len(self._issues)} naming/organization issues")

            # Step 4: Generate execution plan
            logs.append("Generating execution plan...")
            plan = self._generate_plan()
            logs.append(f"Plan includes {len(plan.get('moves', []))} file movements")

            # Build analysis result
            analysis = Analysis(
                cleaner_id=self.cleaner_id,
                timestamp=datetime.now().isoformat(),
                files_scanned=len(self._md_files),
                issues_found=len(self._issues),
                plan=plan,
                logs=logs,
            )

            self.logger.info(f"Analysis complete: {len(self._md_files)} files, "
                           f"{len(self._issues)} issues")
            return analysis

        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            logs.append(f"ERROR: {str(e)}")
            raise ValueError(f"MD file analysis failed: {str(e)}") from e

    def execute(self, plan: Dict[str, Any]) -> Report:
        """Execute file organization according to plan.

        Creates pre-execution snapshot, executes plan (moves/renames files),
        and reports results. If dry_run is enabled, reports what would happen.

        Args:
            plan: Execution plan from analyze() phase

        Returns:
            Report: Contains:
                - status: 'SUCCESS', 'FAILED', 'PARTIAL', or 'DRY_RUN'
                - actions_taken: Number of files moved
                - changes: Dictionary of actual changes
                - errors: List of any errors encountered
                - logs: Detailed execution logs

        Raises:
            ValueError: If execution fails critically
        """
        self.logger.info("Starting MD file reorganization execution")
        logs: List[str] = []
        changes: Dict[str, Any] = {}
        errors: List[str] = []
        actions_taken = 0

        try:
            if self.dry_run:
                logs.append("DRY RUN MODE: No files will be modified")
                report = Report(
                    cleaner_id=self.cleaner_id,
                    timestamp=datetime.now().isoformat(),
                    status="DRY_RUN",
                    actions_taken=0,
                    changes=plan,
                    errors=errors,
                    logs=logs,
                )
                self.logger.info("Dry run complete")
                return report

            # Create snapshot before execution
            logs.append("Creating pre-execution snapshot...")
            snapshot_data = self._create_snapshot()
            self._snapshot = snapshot_data
            logs.append(f"Snapshot created with {len(snapshot_data.get('files', {}))} files")

            # Execute moves from plan
            moves_executed = []
            for move in plan.get("moves", []):
                try:
                    source = Path(move["source"])
                    target = Path(move["target"])

                    # Verify source exists
                    if not source.exists():
                        error_msg = f"Source file not found: {move['source']}"
                        errors.append(error_msg)
                        logs.append(f"ERROR: {error_msg}")
                        self.logger.warning(error_msg)
                        continue

                    # Create target directory if needed
                    target.parent.mkdir(parents=True, exist_ok=True)

                    # Move file
                    source.rename(target)
                    actions_taken += 1
                    moves_executed.append(move)
                    logs.append(f"Moved: {move['source']} → {move['target']}")

                except Exception as e:
                    error_msg = f"Failed to move {move['source']}: {str(e)}"
                    errors.append(error_msg)
                    logs.append(f"ERROR: {error_msg}")
                    self.logger.error(error_msg)

            # Store executed moves for rollback
            self._executed_moves = moves_executed

            # Build report
            status = "SUCCESS" if len(errors) == 0 else (
                "PARTIAL" if actions_taken > 0 else "FAILED"
            )

            report = Report(
                cleaner_id=self.cleaner_id,
                timestamp=datetime.now().isoformat(),
                status=status,
                actions_taken=actions_taken,
                changes={"files_moved": actions_taken, "moves": moves_executed},
                errors=errors,
                logs=logs,
            )

            self.logger.info(f"Execution complete: {actions_taken} files moved, "
                           f"{len(errors)} errors")
            return report

        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}")
            errors.append(f"CRITICAL: {str(e)}")
            raise ValueError(f"MD file execution failed: {str(e)}") from e

    def rollback(self) -> RollbackResult:
        """Restore files from pre-execution snapshot.

        Restores files to their original locations before execute() was called.
        Uses snapshot created at execute() start time.

        Returns:
            RollbackResult: Contains:
                - status: 'SUCCESS' or 'FAILED'
                - files_restored: Number of files restored
                - errors: List of any restoration errors

        Raises:
            ValueError: If rollback fails
        """
        self.logger.info("Starting MD file rollback")
        errors: List[str] = []
        files_restored = 0

        try:
            # Check if snapshot exists
            if not hasattr(self, "_snapshot") or self._snapshot is None:
                error_msg = "No snapshot available for rollback"
                self.logger.warning(error_msg)
                errors.append(error_msg)
                return RollbackResult(
                    cleaner_id=self.cleaner_id,
                    timestamp=datetime.now().isoformat(),
                    status="FAILED",
                    files_restored=0,
                    errors=errors,
                )

            # Reverse the executed moves
            if hasattr(self, "_executed_moves"):
                for move in reversed(self._executed_moves):
                    try:
                        source = Path(move["target"])
                        target = Path(move["source"])

                        if source.exists():
                            target.parent.mkdir(parents=True, exist_ok=True)
                            source.rename(target)
                            files_restored += 1
                            self.logger.info(f"Restored: {source} → {target}")
                        else:
                            warning_msg = f"File not found for restoration: {source}"
                            self.logger.warning(warning_msg)
                            errors.append(warning_msg)

                    except Exception as e:
                        error_msg = f"Failed to restore {move['source']}: {str(e)}"
                        errors.append(error_msg)
                        self.logger.error(error_msg)

            status = "SUCCESS" if len(errors) == 0 else "PARTIAL"

            result = RollbackResult(
                cleaner_id=self.cleaner_id,
                timestamp=datetime.now().isoformat(),
                status=status,
                files_restored=files_restored,
                errors=errors,
            )

            self.logger.info(f"Rollback complete: {files_restored} files restored")
            return result

        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")
            errors.append(f"CRITICAL: {str(e)}")
            raise ValueError(f"MD file rollback failed: {str(e)}") from e

    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================

    def _create_snapshot(self) -> Dict[str, Any]:
        """Create pre-execution snapshot of file state.

        Creates a snapshot of current file locations for rollback support.

        Returns:
            Snapshot dictionary with file state information
        """
        snapshot: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "files": {},
        }

        # Store current file locations
        for filename, filepath in self._md_files.items():
            snapshot["files"][filename] = str(filepath)

        self.logger.info(f"Snapshot created with {len(snapshot['files'])} files")
        return snapshot

    def _resolve_repo_root(self) -> Path:
        """Resolve the repository root directory.

        Walks up from current directory until finding .git directory,
        or uses CORTEX_ROOT environment variable if set.

        Returns:
            Path to repository root

        Raises:
            ValueError: If repository root cannot be determined
        """
        import os

        # Check environment variable first
        env_root = os.getenv("CORTEX_ROOT")
        if env_root:
            path = Path(env_root)
            if path.exists() and (path / ".git").exists():
                return path

        # Walk up directory tree
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent

        raise ValueError("Could not determine repository root")

    def _scan_md_files(self) -> Dict[str, Path]:
        """Scan repository for all markdown files.

        Returns:
            Dictionary mapping filename to absolute path
        """
        md_files: Dict[str, Path] = {}

        for md_file in self.repo_root.rglob("*.md"):
            # Skip hidden directories and common exclusions
            if any(part.startswith(".") for part in md_file.parts):
                continue
            if any(part in ["node_modules", "venv", ".venv"] for part in md_file.parts):
                continue

            md_files[md_file.name] = md_file

        return md_files

    def _categorize_files(self) -> Dict[str, List[str]]:
        """Categorize markdown files into logical groups.

        Returns:
            Dictionary mapping category name to list of filenames
        """
        categories: Dict[str, List[str]] = {cat.value: [] for cat in MDFileCategory}

        for filename in self._md_files.keys():
            category = self._classify_file(filename)
            categories[category.value].append(filename)

        return categories

    def _classify_file(self, filename: str) -> MDFileCategory:
        """Classify a single markdown file into a category.

        Args:
            filename: Name of the markdown file

        Returns:
            MDFileCategory for this file
        """
        name_lower = filename.lower()
        name_no_ext = filename[:-3]  # Remove .md
        name_upper = name_no_ext.upper()

        # Check patterns in order of specificity
        if name_no_ext.startswith("PHASE-"):
            return MDFileCategory.PHASE
        if name_no_ext.startswith("AC-FIX-"):
            return MDFileCategory.AC_FIX
        if name_no_ext.startswith("AC-MINOR-"):
            return MDFileCategory.AC_MINOR
        if name_no_ext.startswith("SESSION-"):
            return MDFileCategory.SESSION
        if name_no_ext.startswith("WEEK-"):
            return MDFileCategory.WEEKLY
        if "COMPLETION" in name_upper:
            return MDFileCategory.COMPLETION
        if name_lower in ["readme.md", "index.md"]:
            return MDFileCategory.ROOT
        if any(keyword in name_lower for keyword in ["architecture", "design", "schema"]):
            return MDFileCategory.ARCHITECTURE
        if any(keyword in name_lower for keyword in ["implementation", "guide", "tutorial"]):
            return MDFileCategory.IMPLEMENTATION
        if any(keyword in name_lower for keyword in ["doc", "documentation", "guide"]):
            return MDFileCategory.DOCUMENTATION

        return MDFileCategory.OTHER

    def _identify_issues(self) -> List[Tuple[str, MDFileNamingIssue]]:
        """Identify naming and organization issues.

        Checks files against CORE-028 naming conventions:
        - Kebab-case (hyphens, no spaces or camelCase)
        - ≤25 characters (not including .md extension)

        Returns:
            List of (filename, issue) tuples
        """
        issues: List[Tuple[str, MDFileNamingIssue]] = []

        for filename in self._md_files.keys():
            name_no_ext = filename[:-3]  # Remove .md

            # Check length (CORE-028: ≤25 chars)
            if len(name_no_ext) > 25:
                issues.append((filename, MDFileNamingIssue.EXCEEDS_LENGTH))

            # Check for spaces
            if " " in filename:
                issues.append((filename, MDFileNamingIssue.SPACES))

            # Check for camelCase
            if self._has_camelcase(name_no_ext):
                issues.append((filename, MDFileNamingIssue.CAMELCASE))

            # Check for inconsistent formatting
            if not self._is_kebab_case(name_no_ext) and name_no_ext.isupper():
                # Upper case filenames (like README) are exceptions
                pass
            elif not self._is_kebab_case(name_no_ext):
                issues.append((filename, MDFileNamingIssue.INCONSISTENT))

        return issues

    def _has_camelcase(self, text: str) -> bool:
        """Check if text contains camelCase.

        Args:
            text: Text to check

        Returns:
            True if text has camelCase patterns
        """
        return bool(re.search(r"[a-z][A-Z]", text))

    def _is_kebab_case(self, text: str) -> bool:
        """Check if text is properly kebab-cased.

        Args:
            text: Text to check

        Returns:
            True if text is valid kebab-case or all-caps
        """
        if text.isupper():
            # All caps files (like README) are acceptable
            return True
        # Valid kebab-case: lowercase with hyphens
        return bool(re.match(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", text))

    def _generate_plan(self) -> Dict[str, Any]:
        """Generate execution plan for file reorganization.

        Returns:
            Plan dictionary with structure:
            {
                'moves': [
                    {'source': 'path/file.md', 'target': 'path/file.md', ...}
                ],
                'renames': [
                    {'old': 'name.md', 'new': 'name.md'}
                ],
                'categories': {...}
            }
        """
        plan: Dict[str, Any] = {
            "moves": [],
            "renames": [],
            "categories": self._categories,
            "issues_identified": len(self._issues),
            "issues": [],
        }

        # For now, generate information-only plan
        # Actual moves will be implemented in VAC-001-03
        for filename, issue in self._issues:
            plan["issues"].append({
                "file": filename,
                "issue": issue.value,
            })

        return plan


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "MDOrganizerCleaner",
    "MDFileCategory",
    "MDFileNamingIssue",
]
