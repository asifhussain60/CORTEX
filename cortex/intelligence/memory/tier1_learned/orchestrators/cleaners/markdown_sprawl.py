"""
Markdown Sprawl Cleaner

Purpose:
    Cleans up temporary markdown files (summaries, reports, checkpoints)
    while preserving valid documentation.

Authority:
    - AC-VACUUM-REFACTOR-001: Golden test-driven refactoring
    - CORE-008: TDD
    - CORE-011: Type hints 100%
    - CORE-012: Google-style docstrings

Author: CORTEX Architect
Date: 2026-02-15
"""

from typing import Dict, Any
from .base import (
    CleanerInterface,
    Analysis,
    Report,
    RollbackResult,
)
from .github_folder_guard import GithubFolderGuard, GithubFileClassification


class MarkdownSprawlCleaner(CleanerInterface):
    """
    Cleaner for temporary markdown files.

    Deletes:
        - *-summary.md
        - *-report.md
        - *-checkpoint.md
        - *-debug.md
        - TEMP-*.md
        - _*.md

    Preserves:
        - README.md (everywhere outside .github/ informational roots)
        - docs/**/*.md
        - cortex-registry/**/*.md
        - .github/**/*.md — governed by GithubFolderGuard:
            PROTECTED (never deleted):
                *.prompt.md, active agent specs, non-deprecated templates,
                workflows/, hooks/, scripts/, prompts/reference/
            VACUUM_ELIGIBLE (may delete):
                DEPRECATED-*.md, agents/README.md, agents/AGENT-INDEX.md,
                prompts/README.md
    """

    _github_guard = GithubFolderGuard()

    @property
    def name(self) -> str:
        """Return cleaner name."""
        return "Markdown Sprawl Cleaner"

    @property
    def version(self) -> str:
        """Return cleaner version."""
        return "1.0.0"

    @property
    def domain(self) -> str:
        """Return cleaner domain.

        Note:
            Uses 'markdown_cleanup' for consistency with test expectations.
        """
        return "markdown_cleanup"

    def analyze(self) -> Analysis:
        """
        Scan for markdown sprawl files.

        Returns:
            Analysis with files to delete
        """
        self._log("Scanning for markdown sprawl...")

        # Patterns to delete
        delete_patterns = [
            "*-summary.md",
            "*-report.md",
            "*-checkpoint.md",
            "*-debug.md",
            "TEMP-*.md",
            "_*.md",
            "*-v[0-9].md",  # Version sprawl (e.g., orchestrator-v3.md)
            "*-v[0-9][0-9].md",  # Two-digit versions
            "chat-session-*.md",  # Session documentation
            "session-*.md",  # Session notes
            "conversation-*.md",  # Conversation logs
        ]

        # Directories to exclude unconditionally (no nuance needed)
        excluded_dirs = {
            ".cortex-runtime",
            "cortex-registry",
            "deployment",
            "docs",
        }
        # Note: .github/ is handled by GithubFolderGuard below (nuanced, not blanket)

        files_to_delete = []
        files_scanned = 0

        for pattern in delete_patterns:
            for md_file in self.repo_root.glob(f"**/{pattern}"):
                files_scanned += 1

                # Skip unconditionally excluded directories
                if any(excluded in md_file.parts for excluded in excluded_dirs):
                    continue

                # Skip if it's README.md outside .github/ (special case)
                if md_file.name == "README.md" and ".github" not in md_file.parts:
                    continue

                # .github/ files: delegate to GithubFolderGuard
                if ".github" in md_file.parts:
                    rel = md_file.relative_to(self.repo_root)
                    classification = self._github_guard.classify(rel)
                    if classification != GithubFileClassification.VACUUM_ELIGIBLE:
                        # PROTECTED or UNRELATED → skip
                        continue

                files_to_delete.append(str(md_file.relative_to(self.repo_root)))

        plan = {
            "files_to_delete": files_to_delete,
            "patterns": delete_patterns,
            "excluded_dirs": list(excluded_dirs),
            "github_guard": "GithubFolderGuard (VACUUM-GITHUB-GUARD-001)",
        }

        self._log(f"Found {len(files_to_delete)} markdown sprawl files")

        return Analysis(
            cleaner_id=self.domain,
            timestamp=self._timestamp(),
            files_scanned=files_scanned,
            issues_found=len(files_to_delete),
            plan=plan,
            logs=[f"Scanned {files_scanned} files, found {len(files_to_delete)} to delete"],
        )

    def execute(self, plan: Dict[str, Any]) -> Report:
        """
        Execute markdown sprawl cleanup.

        Args:
            plan: Execution plan from analyze()

        Returns:
            Report with deletion results
        """
        self._log("Executing markdown sprawl cleanup...")

        files_to_delete = plan.get("files_to_delete", [])
        deleted_count = 0
        errors = []
        logs = []

        for file_path_str in files_to_delete:
            file_path = self.repo_root / file_path_str

            if self.dry_run:
                logs.append(f"[DRY RUN] Would delete: {file_path_str}")
                deleted_count += 1
                continue

            try:
                if file_path.exists():
                    file_path.unlink()
                    deleted_count += 1
                    logs.append(f"Deleted: {file_path_str}")
                    self._log(f"Deleted: {file_path_str}")
                else:
                    logs.append(f"Already deleted: {file_path_str}")
            except Exception as e:
                error_msg = f"Failed to delete {file_path_str}: {e}"
                errors.append(error_msg)
                logs.append(error_msg)
                self._log(error_msg)

        status = "SUCCESS" if len(errors) == 0 else "PARTIAL"
        if deleted_count == 0 and len(errors) > 0:
            status = "FAILED"

        return Report(
            cleaner_id=self.domain,
            timestamp=self._timestamp(),
            status=status,
            actions_taken=deleted_count,
            changes={"deleted": deleted_count},
            errors=errors,
            logs=logs,
        )

    def rollback(self) -> RollbackResult:
        """
        Rollback markdown sprawl cleanup.

        Note: Rollback not supported for deletions (no backup made).

        Returns:
            RollbackResult indicating no rollback possible
        """
        return RollbackResult(
            cleaner_id=self.domain,
            timestamp=self._timestamp(),
            status="FAILED",
            files_restored=0,
            errors=["Rollback not supported for markdown sprawl cleanup (no backups)"],
        )
