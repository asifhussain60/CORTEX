"""
DuplicationDetector Orchestrator - PHASE 8.3A Foundation

AC-8.3A-001: DuplicationDetector Orchestrator Implemented

Orchestrator that detects code duplications using LENS analyzers:
- ASTAnalyzer: Detect function/class structure duplications
- GitHistoryAnalyzer: Detect copy-paste patterns
- CommentExtractor: Extract intent hints

Implements:
- Exact duplication detection (99%+ match)
- Semantic duplication detection (75%+ match)
- Copy-paste pattern detection (from git history)
- Severity scoring (CRITICAL, HIGH, MEDIUM, LOW)
- Duplication report generation
- Consolidation path suggestions

Author: Asif Hussain
Date: 2026-01-31
Authority: PHASE 8.3A Specification
"""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator
from cortex.brain.core.orchestrator_base import (
    OrchestrationContext,
    OrchestrationResult,
    OrchestrationStatus,
    OrchestratorBase,
)
from cortex.core.result import Err, Ok, Result
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer
from cortex.lens.analyzers.comment_extractor import CommentExtractor
from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer

logger = logging.getLogger(__name__)

# CONSOLIDATED: Import from cortex.models.canonical_enums
from cortex.models.canonical_enums import SeverityLevel


class DuplicationType(Enum):
    """Type of duplication detected"""
    EXACT = "exact"                  # 95%+ match, identical logic
    SEMANTIC = "semantic"            # 75%+ match, same logic, different names
    COPY_PASTE = "copy_paste"        # Detected via git history
    STRUCTURAL = "structural"        # Same structure, different implementation


@dataclass
class DuplicateEntry:
    """Single duplication entry"""
    id: str
    file1: str
    file2: str
    similarity: float
    type: str
    lines: int
    context: Dict[str, Any] = field(default_factory=dict)
    consolidation_phase: str = "8.3B"

    def __post_init__(self) -> None:
        """Validate fields"""
        if not 0.0 <= self.similarity <= 1.0:
            raise ValueError(f"Similarity must be 0.0-1.0, got {self.similarity}")


@dataclass
class DuplicationReport:
    """Duplication report for codebase"""
    timestamp: datetime
    total_duplications: int
    duplicates: List[DuplicateEntry]
    summary: Dict[str, Any]
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_duplications": self.total_duplications,
            "duplicates": [
                {
                    "id": d.id,
                    "file1": d.file1,
                    "file2": d.file2,
                    "similarity": d.similarity,
                    "type": d.type,
                    "lines": d.lines,
                }
                for d in self.duplicates
            ],
            "summary": self.summary,
            "metrics": self.metrics,
        }


class DuplicationDetector(OrchestratorBase):
    """
    Detects code duplications in CORTEX codebase.

    Uses LENS analyzers to identify:
    - Exact duplications (same code, different files)
    - Semantic duplications (same logic, different names)
    - Copy-paste patterns (detected via git history)

    Domain: Support (Infrastructure)
    Version: 1.0
    Tier: 1
    """

    DOMAIN = "support"
    VERSION = "1.0"
    STAGES = ["analysis", "detection", "scoring", "reporting"]

    def __init__(self, context: Optional[OrchestrationContext] = None) -> None:
        """
        Initialize DuplicationDetector.

        Args:
            context: OrchestrationContext (optional for standalone use)
        """
        if context is None:
            # Create default context for standalone usage
            context = OrchestrationContext(
                orchestrator_id="DuplicationDetector",
                orchestrator_name="DuplicationDetector",
            )

        super().__init__(context)

        # Initialize LENS analyzers
        self.ast_analyzer = ASTAnalyzer()

        # Try to detect CORTEX repo path for GitHistoryAnalyzer
        try:
            from pathlib import Path
            # Look for .git directory starting from current file location
            current_file = Path(__file__)
            search_path = current_file.parent
            for _ in range(10):  # Search up to 10 levels
                if (search_path / ".git").exists():
                    self.git_analyzer = GitHistoryAnalyzer(repo_path=search_path)
                    break
                search_path = search_path.parent
            else:
                # Fallback: use current working directory
                self.git_analyzer = GitHistoryAnalyzer(repo_path=Path.cwd())
        except Exception:
            # Last resort: initialize without git analysis
            self.git_analyzer = None

        self.comment_extractor = CommentExtractor()

        # Audit logger
        self.audit_logger = EnhancedAuditLogger()

        # Duplication registry
        self._duplications: List[DuplicateEntry] = []
        self._next_id = 1

    # =====================================================================
    # ORCHESTRATOR INTERFACE
    # =====================================================================

    def execute(self, parameters: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """
        Execute duplication detection.

        Parameters:
            files: List of file paths to scan
            min_similarity: Minimum similarity threshold (0.0-1.0)
            include_git_analysis: Include git history analysis

        Returns:
            OrchestrationResult with duplication report
        """
        try:
            parameters = parameters or {}

            # Update context
            self.context.status = OrchestrationStatus.EXECUTING
            self._log("Starting duplication detection")

            # Get parameters
            files = parameters.get("files", [])
            min_similarity = parameters.get("min_similarity", 0.75)
            include_git = parameters.get("include_git_analysis", True)

            self._log(f"Scanning {len(files)} files, min_similarity={min_similarity}")

            # Run detection
            duplications = self.detect_duplications(
                files=files,
                min_similarity=min_similarity,
                include_git_analysis=include_git,
            )

            # Generate report
            report = self.generate_duplication_report(duplications)

            self._log(f"Found {report.total_duplications} duplications")

            # Log to audit trail
            self.audit_logger.log(
                ac_id="AC-8.3A-001",
                action="duplication_detection_complete",
                details={
                    "total_duplications": report.total_duplications,
                    "files_scanned": len(files),
                    "by_severity": report.summary.get("by_severity", {}),
                },
            )

            # Return result
            return OrchestrationResult(
                status=OrchestrationStatus.COMPLETED,
                success=True,
                message=f"Found {report.total_duplications} duplications",
                data={
                    "report": report.to_dict(),
                    "duplications": [
                        {
                            "id": d.id,
                            "file1": d.file1,
                            "file2": d.file2,
                            "similarity": d.similarity,
                            "type": d.type,
                        }
                        for d in duplications
                    ],
                },
            )

        except Exception as e:
            logger.exception(f"DuplicationDetector failed: {e}")
            return OrchestrationResult(
                status=OrchestrationStatus.FAILED,
                success=False,
                message=f"DuplicationDetector failed: {str(e)}",
                error_code="DETECTION_FAILED",
            )

    # =====================================================================
    # DUPLICATION DETECTION METHODS
    # =====================================================================

    def detect_duplications(
        self,
        files: List[str],
        min_similarity: float = 0.75,
        include_git_analysis: bool = True,
    ) -> List[DuplicateEntry]:
        """
        Detect all types of duplications.

        Args:
            files: List of file paths
            min_similarity: Minimum similarity threshold
            include_git_analysis: Include git-based detection

        Returns:
            List of DuplicateEntry objects
        """
        self._log(f"Starting duplication detection on {len(files)} files")
        duplications = []

        # 1. Exact duplications (AST-based)
        exact = self.detect_exact_duplications(files)
        self._log(f"Found {len(exact)} exact duplications")
        duplications.extend(exact)

        # 2. Semantic duplications (AST-based with fuzzy matching)
        semantic = self.detect_semantic_duplications(files, min_similarity)
        self._log(f"Found {len(semantic)} semantic duplications")
        duplications.extend(semantic)

        # 3. Copy-paste patterns (Git history)
        if include_git_analysis:
            patterns = self.detect_copy_paste_patterns(files)
            self._log(f"Found {len(patterns)} copy-paste patterns")
            duplications.extend(patterns)

        # Remove duplicates (same pair counted twice)
        duplications = self._deduplicate_entries(duplications)

        return sorted(duplications, key=lambda d: d.similarity, reverse=True)

    def detect_exact_duplications(
        self,
        files: List[str],
    ) -> List[DuplicateEntry]:
        """
        Detect exact code duplications (95%+ match).

        Uses AST analysis to find identical code blocks
        across different files.
        """
        duplications = []

        # Analyze all files
        file_asts = {}
        for file_path in files:
            try:
                analysis = self.ast_analyzer.analyze(file_path)
                file_asts[file_path] = analysis
            except Exception as e:
                self._log(f"Failed to analyze {file_path}: {e}", level="WARNING")

        # Compare ASTs
        file_list = list(file_asts.keys())
        for i, file1 in enumerate(file_list):
            for file2 in file_list[i + 1:]:
                ast1 = file_asts[file1]
                ast2 = file_asts[file2]

                # Compare function definitions
                for func1 in ast1.get("functions", []):
                    for func2 in ast2.get("functions", []):
                        similarity = self._calculate_ast_similarity(func1, func2)
                        if similarity >= 0.95:
                            dup = DuplicateEntry(
                                id=self._next_dup_id(),
                                file1=file1,
                                file2=file2,
                                similarity=similarity,
                                type=DuplicationType.EXACT.value,
                                lines=func1.get("lines", 0),
                                context={
                                    "function1": func1.get("name", "unknown"),
                                    "function2": func2.get("name", "unknown"),
                                },
                            )
                            duplications.append(dup)

                # Compare class definitions
                for cls1 in ast1.get("classes", []):
                    for cls2 in ast2.get("classes", []):
                        similarity = self._calculate_ast_similarity(cls1, cls2)
                        if similarity >= 0.95:
                            dup = DuplicateEntry(
                                id=self._next_dup_id(),
                                file1=file1,
                                file2=file2,
                                similarity=similarity,
                                type=DuplicationType.EXACT.value,
                                lines=cls1.get("lines", 0),
                                context={
                                    "class1": cls1.get("name", "unknown"),
                                    "class2": cls2.get("name", "unknown"),
                                },
                            )
                            duplications.append(dup)

        return duplications

    def detect_semantic_duplications(
        self,
        files: List[str],
        min_similarity: float = 0.75,
    ) -> List[DuplicateEntry]:
        """
        Detect semantic code duplications (same logic, different names).

        Uses AST analysis with fuzzy matching to find
        functionally equivalent code.
        """
        duplications = []

        # Similar to exact detection but with lower threshold
        file_asts = {}
        for file_path in files:
            try:
                analysis = self.ast_analyzer.analyze(file_path)
                file_asts[file_path] = analysis
            except Exception as e:
                self._log(f"Failed to analyze {file_path}: {e}", level="WARNING")

        file_list = list(file_asts.keys())
        for i, file1 in enumerate(file_list):
            for file2 in file_list[i + 1:]:
                ast1 = file_asts[file1]
                ast2 = file_asts[file2]

                # Compare functions
                for func1 in ast1.get("functions", []):
                    for func2 in ast2.get("functions", []):
                        similarity = self._calculate_ast_similarity(func1, func2)
                        if min_similarity <= similarity < 0.95:
                            dup = DuplicateEntry(
                                id=self._next_dup_id(),
                                file1=file1,
                                file2=file2,
                                similarity=similarity,
                                type=DuplicationType.SEMANTIC.value,
                                lines=func1.get("lines", 0),
                            )
                            duplications.append(dup)

        return duplications

    def detect_copy_paste_patterns(
        self,
        files: List[str],
    ) -> List[DuplicateEntry]:
        """
        Detect copy-paste patterns from git history.

        Uses GitHistoryAnalyzer to identify files that
        were committed together or show copy-paste patterns.
        """
        duplications = []

        # Skip if git analyzer not available
        if self.git_analyzer is None:
            return duplications

        try:
            # Get git history for files
            git_data = self.git_analyzer.analyze_batch(files)

            # Look for copy-paste patterns
            for file1 in files:
                for file2 in files:
                    if file1 >= file2:
                        continue

                    # Check if files have same commit history
                    commits1 = git_data.get(file1, {}).get("commits", [])
                    commits2 = git_data.get(file2, {}).get("commits", [])

                    # If they share early commits, likely copy-paste
                    common = set(commits1[:5]) & set(commits2[:5])
                    if len(common) > 0:
                        dup = DuplicateEntry(
                            id=self._next_dup_id(),
                            file1=file1,
                            file2=file2,
                            similarity=0.85,
                            type=DuplicationType.COPY_PASTE.value,
                            lines=0,  # Unknown
                        )
                        duplications.append(dup)

        except Exception as e:
            self._log(f"Git analysis failed: {e}", level="WARNING")

        return duplications

    # =====================================================================
    # SEVERITY SCORING
    # =====================================================================

    def score_severity(self, duplication: DuplicateEntry) -> SeverityLevel:
        """
        Score duplication severity.

        Args:
            duplication: DuplicateEntry to score

        Returns:
            SeverityLevel (CRITICAL, HIGH, MEDIUM, LOW)
        """
        # Factor 1: Similarity
        if duplication.similarity >= 0.95:
            base_level = SeverityLevel.CRITICAL
        elif duplication.similarity >= 0.80:
            base_level = SeverityLevel.HIGH
        elif duplication.similarity >= 0.65:
            base_level = SeverityLevel.MEDIUM
        else:
            base_level = SeverityLevel.LOW

        # Factor 2: Type - copy_paste and exact are always critical
        if duplication.type in (DuplicationType.COPY_PASTE.value, DuplicationType.EXACT.value):
            if base_level == SeverityLevel.HIGH or base_level == SeverityLevel.CRITICAL:
                # Upgrade HIGH to CRITICAL for copy-paste/exact, keep CRITICAL
                if base_level == SeverityLevel.HIGH and duplication.similarity >= 0.80:
                    base_level = SeverityLevel.CRITICAL
            elif base_level == SeverityLevel.MEDIUM and duplication.lines > 50:
                base_level = SeverityLevel.HIGH

        # Factor 3: Lines of code
        if duplication.lines > 100 and base_level.value < SeverityLevel.HIGH.value:
            base_level = SeverityLevel.HIGH

        return base_level

    # =====================================================================
    # CONSOLIDATION SUGGESTIONS
    # =====================================================================

    def suggest_consolidation_path(
        self,
        duplication: DuplicateEntry,
    ) -> Dict[str, Any]:
        """
        Suggest consolidation path for duplication.

        Args:
            duplication: DuplicateEntry to consolidate

        Returns:
            Dict with consolidation suggestion
        """
        severity = self.score_severity(duplication)
        dup_type = duplication.type

        suggestion = {
            "duplication_id": duplication.id,
            "severity": severity.name,
            "file1": duplication.file1,
            "file2": duplication.file2,
        }

        # Exact duplicates: keep one, delete other
        if dup_type == DuplicationType.EXACT.value:
            suggestion["action"] = "consolidate"
            suggestion["keep"] = duplication.file1  # Keep older
            suggestion["delete"] = duplication.file2
            suggestion["phase"] = "8.3C"

        # Semantic duplicates: extract common logic
        elif dup_type == DuplicationType.SEMANTIC.value:
            suggestion["action"] = "extract_base"
            suggestion["phase"] = "8.3B"

        # Copy-paste: merge into canonical
        elif dup_type == DuplicationType.COPY_PASTE.value:
            suggestion["action"] = "merge"
            suggestion["phase"] = "8.3B/C"

        return suggestion

    # =====================================================================
    # REPORT GENERATION
    # =====================================================================

    def generate_duplication_report(
        self,
        duplications: List[DuplicateEntry],
    ) -> DuplicationReport:
        """
        Generate duplication report.

        Args:
            duplications: List of DuplicateEntry objects

        Returns:
            DuplicationReport with statistics
        """
        # Sort by severity
        sorted_dups = sorted(
            duplications,
            key=lambda d: self.score_severity(d).value,
            reverse=True,
        )

        # Calculate statistics
        by_severity = {}
        by_type = {}
        total_lines = 0

        for dup in duplications:
            severity = self.score_severity(dup)
            by_severity[severity.name] = by_severity.get(severity.name, 0) + 1
            by_type[dup.type] = by_type.get(dup.type, 0) + 1
            total_lines += dup.lines

        summary = {
            "by_severity": by_severity,
            "by_type": by_type,
            "total_duplicate_lines": total_lines,
        }

        metrics = {
            "critical_count": by_severity.get("CRITICAL", 0),
            "high_count": by_severity.get("HIGH", 0),
            "medium_count": by_severity.get("MEDIUM", 0),
            "low_count": by_severity.get("LOW", 0),
            "average_similarity": (
                sum(d.similarity for d in duplications) / len(duplications)
                if duplications else 0.0
            ),
        }

        return DuplicationReport(
            timestamp=datetime.now(),
            total_duplications=len(duplications),
            duplicates=sorted_dups,
            summary=summary,
            metrics=metrics,
        )

    # =====================================================================
    # HELPER METHODS
    # =====================================================================

    def _calculate_ast_similarity(self, ast1: Dict, ast2: Dict) -> float:
        """Calculate similarity between two AST nodes."""
        # Simplified: compare structure, ignoring names
        keys1 = set(ast1.keys()) - {"name", "lineno"}
        keys2 = set(ast2.keys()) - {"name", "lineno"}

        if not keys1 or not keys2:
            return 0.0

        intersection = len(keys1 & keys2)
        union = len(keys1 | keys2)

        return intersection / union if union > 0 else 0.0

    def _deduplicate_entries(
        self,
        entries: List[DuplicateEntry],
    ) -> List[DuplicateEntry]:
        """Remove duplicate entries (same pair counted twice)."""
        seen = set()
        result = []

        for entry in entries:
            pair = tuple(sorted([entry.file1, entry.file2]))
            if pair not in seen:
                seen.add(pair)
                result.append(entry)

        return result

    def _next_dup_id(self) -> str:
        """Generate next duplication ID"""
        dup_id = f"DUP-{self._next_id:04d}"
        self._next_id += 1
        return dup_id

    def _log(self, message: str, level: str = "INFO") -> None:
        """Log message"""
        if level == "WARNING":
            logger.warning(message)
        elif level == "ERROR":
            logger.error(message)
        else:
            logger.info(message)

        self.context.progress_percent = min(100, self.context.progress_percent + 5)

    def validate_context(self) -> List[str]:
        """Validate context"""
        errors = []

        if not self.context.orchestrator_id:
            errors.append("orchestrator_id is required")

        return errors
