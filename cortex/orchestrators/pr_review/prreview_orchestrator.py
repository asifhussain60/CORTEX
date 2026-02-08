# AC_START: AC-PHASE52-S1-prreview_orchestrator
# Description: Phase 52 S1 - PRReviewOrchestrator Base Component
# Author: Asif Hussain
# Date: 2026-02-08
# Phase: 52, Stage 1

"""
PRReviewOrchestrator: Enterprise PR review automation system.

S1 Foundation: Core diff parsing, security analysis, and review components.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from enum import Enum
import time
import logging

logger = logging.getLogger(__name__)


class FileType(Enum):
    """File type classification."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GOLANG = "go"
    RUST = "rust"
    SQL = "sql"
    YAML = "yaml"
    DOCKERFILE = "dockerfile"
    UNKNOWN = "unknown"


class SecurityLevel(Enum):
    """Security risk levels."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5


@dataclass
class DiffLine:
    """Single line change in diff."""

    line_number: int
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    change_type: str = "context"  # added, removed, context


@dataclass
class FileDiff:
    """Diff for a single file."""

    file_path: str
    file_type: FileType
    additions: int = 0
    deletions: int = 0
    lines: List[DiffLine] = field(default_factory=list)
    is_new: bool = False
    is_deleted: bool = False


@dataclass
class SecurityFinding:
    """Security vulnerability or issue found."""

    title: str
    description: str
    level: SecurityLevel
    line_number: int
    file_path: str
    suggested_fix: Optional[str] = None


@dataclass
class PRReviewAnalysis:
    """Complete PR analysis results."""

    pr_number: int
    title: str
    author: str
    files: List[FileDiff] = field(default_factory=list)
    security_findings: List[SecurityFinding] = field(default_factory=list)
    total_additions: int = 0
    total_deletions: int = 0
    complexity_score: float = 0.0
    test_coverage_impact: float = 0.0
    analysis_timestamp: float = field(default_factory=time.time)


class DiffParser:
    """Parse GitHub diff format into structured data."""

    @staticmethod
    def parse_unified_diff(diff_content: str) -> List[FileDiff]:
        """Parse unified diff format.

        Args:
            diff_content: Unified diff text

        Returns:
            List of FileDiff objects
        """
        # AC_START: AC-PHASE52-S1-diff_parsing
        files = []
        current_file = None
        current_lines = []

        for line in diff_content.split("\n"):
            if line.startswith("+++") or line.startswith("---"):
                if current_file and current_lines:
                    current_file.lines = current_lines
                    files.append(current_file)

                # Extract file path
                file_path = line[6:] if len(line) > 6 else "unknown"

                current_file = FileDiff(
                    file_path=file_path,
                    file_type=DiffParser._detect_file_type(file_path),
                    is_new=line.startswith("+++") and "a/" not in line,
                    is_deleted=line.startswith("---") and "b/" not in line,
                )
                current_lines = []

            elif line.startswith("+") and not line.startswith("+++"):
                if current_file:
                    current_file.additions += 1
                    current_lines.append(
                        DiffLine(
                            line_number=len(current_lines),
                            new_content=line[1:],
                            change_type="added",
                        )
                    )

            elif line.startswith("-") and not line.startswith("---"):
                if current_file:
                    current_file.deletions += 1
                    current_lines.append(
                        DiffLine(
                            line_number=len(current_lines),
                            old_content=line[1:],
                            change_type="removed",
                        )
                    )

            elif line.startswith(" "):
                if current_file:
                    current_lines.append(
                        DiffLine(
                            line_number=len(current_lines),
                            old_content=line[1:],
                            new_content=line[1:],
                            change_type="context",
                        )
                    )

        if current_file and current_lines:
            current_file.lines = current_lines
            files.append(current_file)

        # AC_COMPLETE: AC-PHASE52-S1-diff_parsing
        return files

    @staticmethod
    def _detect_file_type(file_path: str) -> FileType:
        """Detect file type from path."""
        file_path_lower = file_path.lower()

        if file_path_lower.endswith(".py"):
            return FileType.PYTHON
        elif file_path_lower.endswith((".js", ".jsx")):
            return FileType.JAVASCRIPT
        elif file_path_lower.endswith((".ts", ".tsx")):
            return FileType.TYPESCRIPT
        elif file_path_lower.endswith(".java"):
            return FileType.JAVA
        elif file_path_lower.endswith(".go"):
            return FileType.GOLANG
        elif file_path_lower.endswith(".rs"):
            return FileType.RUST
        elif file_path_lower.endswith((".sql", ".sql.py")):
            return FileType.SQL
        elif file_path_lower.endswith((".yaml", ".yml")):
            return FileType.YAML
        elif file_path_lower == "dockerfile" or "dockerfile" in file_path_lower:
            return FileType.DOCKERFILE
        else:
            return FileType.UNKNOWN


class SecurityAnalyzer:
    """Analyze PRs for security vulnerabilities."""

    def __init__(self):
        """Initialize analyzer."""
        self.findings: List[SecurityFinding] = []

    def analyze(
        self,
        files: List[FileDiff],
        pr_title: Optional[str] = None,
        pr_description: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """Analyze files for security issues.

        Args:
            files: List of file diffs
            pr_title: PR title (optional)
            pr_description: PR description (optional)

        Returns:
            List of security findings
        """
        # AC_START: AC-PHASE52-S1-security_analysis
        self.findings = []

        for file in files:
            self._analyze_file_security(file)

        # AC_COMPLETE: AC-PHASE52-S1-security_analysis
        return self.findings

    def _analyze_file_security(self, file: FileDiff) -> None:
        """Analyze single file for security issues."""
        if file.file_type == FileType.PYTHON:
            self._check_python_security(file)
        elif file.file_type in [FileType.JAVASCRIPT, FileType.TYPESCRIPT]:
            self._check_javascript_security(file)
        elif file.file_type == FileType.DOCKERFILE:
            self._check_dockerfile_security(file)
        elif file.file_type == FileType.YAML:
            self._check_yaml_security(file)

    def _check_python_security(self, file: FileDiff) -> None:
        """Check Python file for security issues."""
        patterns = {
            "eval(": SecurityLevel.CRITICAL,
            "exec(": SecurityLevel.CRITICAL,
            "__import__": SecurityLevel.HIGH,
            "pickle.loads": SecurityLevel.HIGH,
            "subprocess.call": SecurityLevel.MEDIUM,
            "os.system": SecurityLevel.HIGH,
        }

        for line in file.lines:
            if line.new_content:
                for pattern, level in patterns.items():
                    if pattern in line.new_content:
                        self.findings.append(
                            SecurityFinding(
                                title=f"Potentially unsafe function: {pattern}",
                                description=f"Found {pattern} which may be unsafe",
                                level=level,
                                line_number=line.line_number,
                                file_path=file.file_path,
                            )
                        )

    def _check_javascript_security(self, file: FileDiff) -> None:
        """Check JavaScript/TypeScript for security issues."""
        patterns = {
            "eval(": SecurityLevel.CRITICAL,
            "dangerouslySetInnerHTML": SecurityLevel.HIGH,
            "innerHTML =": SecurityLevel.HIGH,
        }

        for line in file.lines:
            if line.new_content:
                for pattern, level in patterns.items():
                    if pattern in line.new_content:
                        self.findings.append(
                            SecurityFinding(
                                title=f"Security risk: {pattern}",
                                description=f"Found {pattern} which may be unsafe",
                                level=level,
                                line_number=line.line_number,
                                file_path=file.file_path,
                            )
                        )

    def _check_dockerfile_security(self, file: FileDiff) -> None:
        """Check Dockerfile for security best practices."""
        for line in file.lines:
            if line.new_content:
                if "FROM" in line.new_content and "latest" in line.new_content:
                    self.findings.append(
                        SecurityFinding(
                            title="Using base image 'latest' tag",
                            description="Using 'latest' tag is not reproducible",
                            level=SecurityLevel.MEDIUM,
                            line_number=line.line_number,
                            file_path=file.file_path,
                            suggested_fix="Pin to specific version tag",
                        )
                    )

    def _check_yaml_security(self, file: FileDiff) -> None:
        """Check YAML for security issues."""
        for line in file.lines:
            if line.new_content:
                if "password:" in line.new_content.lower():
                    if not any(
                        x in line.new_content
                        for x in ["${", "{{", "env.", "secret"]
                    ):
                        self.findings.append(
                            SecurityFinding(
                                title="Hardcoded password in YAML",
                                description="Password should be in environment variable",
                                level=SecurityLevel.CRITICAL,
                                line_number=line.line_number,
                                file_path=file.file_path,
                            )
                        )


class ComplexityAnalyzer:
    """Analyze PR complexity score."""

    @staticmethod
    def calculate_complexity(files: List[FileDiff]) -> float:
        """Calculate overall complexity score (0-10).

        Args:
            files: List of file diffs

        Returns:
            Complexity score
        """
        # AC_START: AC-PHASE52-S1-complexity
        if not files:
            return 0.0

        total_changes = sum(f.additions + f.deletions for f in files)
        file_count = len(files)

        # Score based on:
        # - Number of files changed
        # - Total lines changed
        # - File type diversity

        file_type_diversity = len(set(f.file_type for f in files)) / 10
        change_density = min(total_changes / 1000, 5)

        score = (file_count / 10) * 2 + change_density + file_type_diversity
        score = min(score, 10.0)

        # AC_COMPLETE: AC-PHASE52-S1-complexity
        return score


class PRReviewOrchestrator:
    """Main orchestrator for PR review automation."""

    def __init__(self):
        """Initialize orchestrator."""
        self.diff_parser = DiffParser()
        self.security_analyzer = SecurityAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()

    def review_pr(
        self,
        pr_number: int,
        title: str,
        author: str,
        diff_content: str,
        pr_description: Optional[str] = None,
    ) -> PRReviewAnalysis:
        """Perform complete PR review.

        Args:
            pr_number: PR number
            title: PR title
            author: PR author
            diff_content: Unified diff content
            pr_description: PR description (optional)

        Returns:
            PRReviewAnalysis with all findings
        """
        # AC_START: AC-PHASE52-S1-pr_review
        files = self.diff_parser.parse_unified_diff(diff_content)
        security_findings = self.security_analyzer.analyze(
            files, title, pr_description
        )
        complexity = self.complexity_analyzer.calculate_complexity(files)

        total_additions = sum(f.additions for f in files)
        total_deletions = sum(f.deletions for f in files)

        analysis = PRReviewAnalysis(
            pr_number=pr_number,
            title=title,
            author=author,
            files=files,
            security_findings=security_findings,
            total_additions=total_additions,
            total_deletions=total_deletions,
            complexity_score=complexity,
        )

        # AC_COMPLETE: AC-PHASE52-S1-pr_review
        return analysis

    def get_review_summary(self, analysis: PRReviewAnalysis) -> Dict[str, Any]:
        """Get summary of review.

        Args:
            analysis: PRReviewAnalysis

        Returns:
            Summary dictionary
        """
        critical_findings = [
            f for f in analysis.security_findings if f.level == SecurityLevel.CRITICAL
        ]

        return {
            "pr_number": analysis.pr_number,
            "files_changed": len(analysis.files),
            "total_additions": analysis.total_additions,
            "total_deletions": analysis.total_deletions,
            "complexity_score": analysis.complexity_score,
            "security_findings": len(analysis.security_findings),
            "critical_issues": len(critical_findings),
            "recommended_action": "request_changes"
            if critical_findings
            else "approve",
        }
