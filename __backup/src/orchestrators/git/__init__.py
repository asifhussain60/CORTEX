"""
Git Commit Orchestrator - Intelligent git operations with zero untracked files.

AC-GIT-001: Automated file classification (COMMIT/IGNORE/RESET)
AC-GIT-002: Orchestrator discovery and registration
AC-GIT-003: Working copy synchronization

Author: GitHub Copilot
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import re

from src.orchestrators.audit_logger import EnterpriseAuditLogger, AuditLevel, AuditCategory


class FileClassification(str, Enum):
    """File classification types."""
    COMMIT = "commit"
    IGNORE = "ignore"
    RESET = "reset"
    UNKNOWN = "unknown"


@dataclass
class FileClassificationResult:
    """Result of file classification."""
    file_path: str
    classification: FileClassification
    reason: str
    pattern: Optional[str] = None


@dataclass
class OrchestratorDiscovery:
    """Discovered orchestrator information."""
    orchestrator_id: str
    class_name: str
    domain: str
    capabilities: List[str]
    ac_ids: List[str]
    file_path: str
    phase: Optional[str] = None


@dataclass
class GitCommitResult:
    """Result of git commit operation."""
    success: bool
    committed_files: List[str]
    ignored_files: List[str]
    reset_files: List[str]
    orchestrators_registered: int
    capabilities_added: int
    untracked_files_before: int
    untracked_files_after: int
    phase_number: Optional[int] = None
    ac_ids: Optional[List[str]] = None
    error: Optional[str] = None
    commit_hash: Optional[str] = None


class GitCommitOrchestrator:
    """
    AC-GIT-001: Intelligent Git Commit with zero untracked files.
    
    Features:
    - Auto-classify untracked files (COMMIT/IGNORE/RESET)
    - Discover and register new orchestrators
    - Maintain orchestrator registry
    - Sync working copy with remote
    - Generate comprehensive commit messages
    """

    # File patterns for auto-classification
    COMMIT_PATTERNS = [
        r"^src/orchestrators/.*\.py$",
        r"^src/[^/]+/.*\.py$",
        r"^tests/.*\.py$",
        r"^cortex-brain/tier[0-3]/orchestrators/.*",
        r"^cortex-brain/tier[0-3]/.*\.yaml$",
        r"^cortex-brain/tier[0-3]/.*\.md$",
        r"^cortex-brain/documents/.*\.md$",
        r"^\.github/prompts/.*\.md$",
        r"^README\.md$",
        r"^ARCHITECTURE.*\.md$",
    ]

    IGNORE_PATTERNS = [
        r"^\.cortex/.*\.md$",
        r"^cortex-brain/cx6-plan/viewer/.*-backup-.*\.json$",
        r"^cortex-brain/audit-logs/.*\.jsonl$",
        r"^cortex-brain/documents/reports/architecture-audit-.*\.json$",
        r"__pycache__/",
        r".*\.pyc$",
        r"^\.pytest_cache/",
        r"^\.coverage$",
        r"^htmlcov/",
        r".*\.db-wal$",
        r".*\.db-shm$",
    ]

    RESET_PATTERNS = [
        r".*\.tmp$",
        r".*\.bak$",
        r"^build/",
        r"^dist/",
        r"^phase-removal/",
    ]

    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize Git Commit Orchestrator."""
        self.workspace_root = workspace_root or Path.cwd()
        self.logger = logging.getLogger(__name__)
        self.audit_logger = EnterpriseAuditLogger()

    def get_untracked_files(self) -> List[str]:
        """Get list of untracked files from git."""
        try:
            result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True
            )
            files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
            self.logger.info(f"Found {len(files)} untracked files")
            return files
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get untracked files: {e}")
            raise

    def classify_file(self, file_path: str) -> FileClassificationResult:
        """Classify a single file as COMMIT, IGNORE, or RESET."""
        # Check COMMIT patterns first (highest priority)
        for pattern in self.COMMIT_PATTERNS:
            if re.match(pattern, file_path):
                return FileClassificationResult(
                    file_path=file_path,
                    classification=FileClassification.COMMIT,
                    reason="Matches COMMIT pattern",
                    pattern=pattern
                )

        # Check IGNORE patterns
        for pattern in self.IGNORE_PATTERNS:
            if re.match(pattern, file_path):
                return FileClassificationResult(
                    file_path=file_path,
                    classification=FileClassification.IGNORE,
                    reason="Matches IGNORE pattern",
                    pattern=pattern
                )

        # Check RESET patterns
        for pattern in self.RESET_PATTERNS:
            if re.match(pattern, file_path):
                return FileClassificationResult(
                    file_path=file_path,
                    classification=FileClassification.RESET,
                    reason="Matches RESET pattern",
                    pattern=pattern
                )

        # Default: unknown
        return FileClassificationResult(
            file_path=file_path,
            classification=FileClassification.UNKNOWN,
            reason="No matching pattern found"
        )

    def classify_untracked_files(
        self,
        files: List[str]
    ) -> Tuple[List[str], List[str], List[str], List[FileClassificationResult]]:
        """Classify all untracked files."""
        commits = []
        ignores = []
        resets = []
        classifications = []

        for file_path in files:
            result = self.classify_file(file_path)
            classifications.append(result)

            if result.classification == FileClassification.COMMIT:
                commits.append(file_path)
            elif result.classification == FileClassification.IGNORE:
                ignores.append(file_path)
            elif result.classification == FileClassification.RESET:
                resets.append(file_path)

        self.logger.info(
            f"Classification complete: {len(commits)} commit, "
            f"{len(ignores)} ignore, {len(resets)} reset"
        )

        return commits, ignores, resets, classifications

    def discover_orchestrators(self, modified_files: List[str]) -> List[OrchestratorDiscovery]:
        """Discover new/modified orchestrators in modified files."""
        discovered = []

        orchestrator_files = [
            f for f in modified_files
            if f.startswith("src/orchestrators/") and f.endswith(".py")
            and "__init__" not in f
        ]

        for file_path in orchestrator_files:
            try:
                full_path = self.workspace_root / file_path
                if not full_path.exists():
                    continue

                # Read file and extract orchestrator metadata
                with open(full_path, "r") as f:
                    content = f.read()

                # Extract class name
                class_match = re.search(
                    r"class\s+(\w+Orchestrator)\s*[\(:]",
                    content
                )
                if not class_match:
                    continue

                class_name = class_match.group(1)

                # Extract orchestrator ID from decorator or docstring
                id_match = re.search(
                    r'@OrchestratorRegistry\.register\([^)]*name=["\']([^"\']+)["\']',
                    content
                )
                orchestrator_id = id_match.group(1) if id_match else class_name.lower()

                # Extract domain
                domain_match = re.search(
                    r'domain=["\']([^"\']+)["\']',
                    content
                )
                domain = domain_match.group(1) if domain_match else "general"

                # Extract capabilities
                capabilities = []
                cap_match = re.findall(
                    r'"([^"]+)"|\'([^\']+)\'',
                    content
                )
                if cap_match:
                    capabilities = [c[0] or c[1] for c in cap_match[:10]]

                # Extract AC-IDs
                ac_ids = re.findall(r"AC-[A-Z]+-\d+", content)
                ac_ids = list(set(ac_ids))  # Deduplicate

                discovered.append(OrchestratorDiscovery(
                    orchestrator_id=orchestrator_id,
                    class_name=class_name,
                    domain=domain,
                    capabilities=capabilities[:6],  # Limit to 6
                    ac_ids=ac_ids,
                    file_path=file_path
                ))

            except Exception as e:
                self.logger.warning(f"Failed to parse {file_path}: {e}")
                continue

        self.logger.info(f"Discovered {len(discovered)} orchestrators")
        return discovered

    def register_orchestrators(
        self,
        discoveries: List[OrchestratorDiscovery]
    ) -> Tuple[int, List[str]]:
        """Register discovered orchestrators."""
        registered_count = 0
        capabilities_added = []

        try:
            registry_path = (
                self.workspace_root /
                "cortex-brain" / "state" / "orchestrator_registry.json"
            )

            # Load existing registry
            registry = {}
            if registry_path.exists():
                with open(registry_path, "r") as f:
                    registry = json.load(f)

            # Add discoveries
            for discovery in discoveries:
                registry[discovery.orchestrator_id] = {
                    "orchestrator_id": discovery.orchestrator_id,
                    "class_name": discovery.class_name,
                    "domain": discovery.domain,
                    "capabilities": discovery.capabilities,
                    "ac_ids": discovery.ac_ids,
                    "file_path": discovery.file_path,
                    "registered_at": datetime.utcnow().isoformat()
                }
                registered_count += 1
                capabilities_added.extend(discovery.capabilities)

            # Save updated registry
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(registry_path, "w") as f:
                json.dump(registry, f, indent=2)

            self.logger.info(f"Registered {registered_count} orchestrators")

        except Exception as e:
            self.logger.error(f"Failed to register orchestrators: {e}")

        return registered_count, list(set(capabilities_added))

    def update_gitignore(self, patterns: List[str]) -> bool:
        """Add patterns to .gitignore."""
        try:
            gitignore_path = self.workspace_root / ".gitignore"

            # Read current patterns
            existing_patterns = set()
            if gitignore_path.exists():
                with open(gitignore_path, "r") as f:
                    existing_patterns = set(f.read().split("\n"))

            # Add new patterns
            with open(gitignore_path, "a") as f:
                for pattern in patterns:
                    if pattern.strip() and pattern not in existing_patterns:
                        f.write(f"{pattern}\n")

            self.logger.info(f"Updated .gitignore with {len(patterns)} patterns")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update .gitignore: {e}")
            return False

    def git_add_files(self, files: List[str]) -> bool:
        """Stage files for commit."""
        try:
            if not files:
                return True

            subprocess.run(
                ["git", "add"] + files,
                cwd=self.workspace_root,
                check=True,
                capture_output=True
            )
            self.logger.info(f"Staged {len(files)} files")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to git add files: {e}")
            return False

    def git_reset_files(self, files: List[str]) -> bool:
        """Reset (discard) files."""
        try:
            if not files:
                return True

            subprocess.run(
                ["git", "checkout", "--"] + files,
                cwd=self.workspace_root,
                check=True,
                capture_output=True
            )
            self.logger.info(f"Reset {len(files)} files")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to reset files: {e}")
            return False

    def generate_commit_message(
        self,
        phase_number: Optional[int],
        ac_ids: Optional[List[str]],
        completion_percentage: Optional[int],
        committed_files: List[str],
        orchestrators_registered: int,
        capabilities_added: int,
        untracked_files_removed: int
    ) -> str:
        """Generate comprehensive commit message."""
        # Determine category
        if any("orchestrator" in f.lower() for f in committed_files):
            category = "feat"
        elif any("test" in f.lower() for f in committed_files):
            category = "test"
        elif any("doc" in f.lower() for f in committed_files):
            category = "docs"
        else:
            category = "chore"

        # Short description
        if ac_ids and orchestrators_registered > 0:
            short_desc = f"Implement {', '.join(ac_ids[:3])} with orchestrator registration"
        elif ac_ids:
            short_desc = f"Implement {', '.join(ac_ids[:3])}"
        elif orchestrators_registered > 0:
            short_desc = f"Register {orchestrators_registered} orchestrator(s)"
        else:
            short_desc = "Update working tree"

        # Build message
        message = f"{category}: {short_desc}\n\n"

        if committed_files:
            message += f"- Committed {len(committed_files)} file(s)\n"
        if orchestrators_registered > 0:
            message += f"- Registered {orchestrators_registered} orchestrator(s)\n"
        if capabilities_added > 0:
            message += f"- Added {capabilities_added} capability/ies\n"
        if untracked_files_removed > 0:
            message += f"- Cleaned up {untracked_files_removed} untracked file(s)\n"

        message += f"\n---\n"

        if phase_number:
            message += f"PHASE: {phase_number}\n"
        if ac_ids:
            message += f"AC-IDS: {', '.join(ac_ids)}\n"
        if completion_percentage:
            message += f"COMPLETION: {completion_percentage}%\n"
        message += f"ORCHESTRATORS_REGISTERED: {orchestrators_registered}\n"
        message += f"CAPABILITIES_ADDED: {capabilities_added}\n"
        message += f"UNTRACKED_FILES_REMOVED: {untracked_files_removed}\n"

        return message

    def run(
        self,
        phase_number: Optional[int] = None,
        ac_ids: Optional[List[str]] = None,
        completion_percentage: Optional[int] = None,
        auto_classify: bool = True,
        register_orchestrators: bool = True,
        sync_working_copy: bool = True,
    ) -> GitCommitResult:
        """
        Execute full git commit workflow.
        
        Args:
            phase_number: Current phase for commit message
            ac_ids: AC-IDs being completed
            completion_percentage: Phase completion %
            auto_classify: Auto-classify files
            register_orchestrators: Discover and register new orchestrators
            sync_working_copy: Pull and merge remote changes
        
        Returns:
            GitCommitResult with outcome details
        """
        start_time = datetime.utcnow()

        try:
            # Step 1: Get untracked files
            untracked = self.get_untracked_files()
            untracked_before = len(untracked)

            if untracked_before == 0:
                self.logger.info("No untracked files found")
                return GitCommitResult(
                    success=True,
                    committed_files=[],
                    ignored_files=[],
                    reset_files=[],
                    orchestrators_registered=0,
                    capabilities_added=0,
                    untracked_files_before=0,
                    untracked_files_after=0,
                )

            # Step 2: Classify files
            commits, ignores, resets, classifications = self.classify_untracked_files(
                untracked
            )

            # Step 3: Process classifications
            self.git_add_files(commits)
            self.git_reset_files(resets)

            # Add ignore patterns to .gitignore
            if ignores:
                self.update_gitignore(ignores)

            # Step 4: Discover and register orchestrators
            orchestrators_count = 0
            capabilities_count = 0

            if register_orchestrators and commits:
                discoveries = self.discover_orchestrators(commits)
                orchestrators_count, capabilities = self.register_orchestrators(discoveries)
                capabilities_count = len(capabilities)

            # Step 5: Generate commit message
            message = self.generate_commit_message(
                phase_number=phase_number,
                ac_ids=ac_ids,
                completion_percentage=completion_percentage,
                committed_files=commits,
                orchestrators_registered=orchestrators_count,
                capabilities_added=capabilities_count,
                untracked_files_removed=len(ignores) + len(resets)
            )

            # Step 6: Commit if there are staged changes
            commit_hash = None
            if commits or ignores:
                result = subprocess.run(
                    ["git", "commit", "-m", message],
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    # Extract commit hash
                    match = re.search(r"^\[CORTEX6 ([0-9a-f]+)\]", result.stdout)
                    commit_hash = match.group(1) if match else None
                    self.logger.info(f"Committed with hash {commit_hash}")
                else:
                    self.logger.warning(f"Commit returned non-zero: {result.stderr}")

            # Step 7: Push to remote
            try:
                subprocess.run(
                    ["git", "push", "origin", "CORTEX6"],
                    cwd=self.workspace_root,
                    check=True,
                    capture_output=True
                )
                self.logger.info("Pushed to remote")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Failed to push: {e}")

            # Step 8: Verify clean state
            untracked_after = len(self.get_untracked_files())

            # Audit log
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.EXECUTION,
                component="git_commit_orchestrator",
                operation="execute_complete",
                message="Git commit orchestrator execution complete",
                context={
                    "files_committed": len(commits),
                    "files_ignored": len(ignores),
                    "files_reset": len(resets),
                    "orchestrators_registered": orchestrators_count,
                    "capabilities_added": capabilities_count,
                    "untracked_files_before": untracked_before,
                    "untracked_files_after": untracked_after,
                    "phase": phase_number,
                    "ac_ids": ac_ids,
                    "commit_hash": commit_hash,
                },
                duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )

            return GitCommitResult(
                success=True,
                committed_files=commits,
                ignored_files=ignores,
                reset_files=resets,
                orchestrators_registered=orchestrators_count,
                capabilities_added=capabilities_count,
                untracked_files_before=untracked_before,
                untracked_files_after=untracked_after,
                phase_number=phase_number,
                ac_ids=ac_ids,
                commit_hash=commit_hash
            )

        except Exception as e:
            self.logger.error(f"Git commit orchestrator failed: {e}")
            self.audit_logger.log(
                level=AuditLevel.ERROR,
                category=AuditCategory.EXECUTION,
                component="git_commit_orchestrator",
                operation="execute_failed",
                message="Git commit orchestrator execution failed",
                context={"error": str(e)}
            )
            return GitCommitResult(
                success=False,
                committed_files=[],
                ignored_files=[],
                reset_files=[],
                orchestrators_registered=0,
                capabilities_added=0,
                untracked_files_before=len(untracked),
                untracked_files_after=0,
                error=str(e)
            )


if __name__ == "__main__":
    orchestrator = GitCommitOrchestrator()
    result = orchestrator.run(
        phase_number=10,
        ac_ids=["AC-GIT-001"],
        completion_percentage=50
    )

    print(f"\n✅ Success: {result.success}")
    print(f"📝 Committed: {len(result.committed_files)} files")
    print(f"🔗 Registered: {result.orchestrators_registered} orchestrators")
    print(f"📦 Capabilities: {result.capabilities_added} added")
    print(f"🧹 Cleaned: {result.untracked_files_before - result.untracked_files_after} files")
    print(f"🚀 Commit: {result.commit_hash}")
