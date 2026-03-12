"""IngestFileClassifier — Phase 144-a.

Classifies files into 9 categories before ingestion,
rejecting PII-sensitive filenames and unsupported binary formats.

Source: GitHub Issue #17 — FB-2026-03-09-074435-001
CORE: CORE-008, CORE-011, CORE-012
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class IngestFileCategory(str, Enum):
    """Nine classification categories for ingested files."""

    KNOWLEDGE_YAML = "knowledge_yaml"
    ARCHITECTURE_DOC = "architecture_doc"
    PROCESS_DOC = "process_doc"
    TECHNICAL_DOC = "technical_doc"
    RCA_DOC = "rca_doc"
    RELEASE_DOC = "release_doc"
    REJECTED_PII = "rejected_pii"
    REJECTED_BINARY = "rejected_binary"
    REJECTED_IRRELEVANT = "rejected_irrelevant"


# ─────────────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ClassifiedFile:
    """A single file with its classification result.

    Attributes:
        path: Absolute path to the file.
        category: Assigned IngestFileCategory.
        reason: Human-readable classification rationale.
        domain_hint: Optional domain hint extracted from filename/path.
        confidence: Classification confidence (0.0–1.0).
        size_bytes: File size in bytes.
    """

    path: Path
    category: IngestFileCategory
    reason: str
    domain_hint: Optional[str] = None
    confidence: float = 1.0
    size_bytes: int = 0


@dataclass
class IngestClassificationResult:
    """Aggregate result from classifying a directory.

    Attributes:
        processable: Files that can be ingested.
        rejected: Files rejected (PII, binary, irrelevant).
        total_scanned: Total files examined.
    """

    processable: List[ClassifiedFile] = field(default_factory=list)
    rejected: List[ClassifiedFile] = field(default_factory=list)
    total_scanned: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

_BINARY_EXTENSIONS = frozenset({
    ".zip", ".tar", ".gz", ".7z", ".rar",
    ".mp4", ".mp3", ".wav", ".avi", ".mov",
    ".exe", ".dll", ".so", ".dylib",
    ".db", ".sqlite", ".sqlite3",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
    ".bin", ".dat",
})

_PII_PATTERNS = (
    re.compile(r"passport", re.IGNORECASE),
    re.compile(r"ssn|social[_-]?security", re.IGNORECASE),
    re.compile(r"credit[_-]?card", re.IGNORECASE),
    re.compile(r"salary|payroll|payslip", re.IGNORECASE),
    re.compile(r"medical|health[_-]?record", re.IGNORECASE),
    re.compile(r"private[_-]?key|secret[_-]?key", re.IGNORECASE),
)

_DOMAIN_HINT_PATTERNS = {
    re.compile(r"architect|design|diagram|adr", re.IGNORECASE): "architecture",
    re.compile(r"security|owasp|pentest|vuln", re.IGNORECASE): "security",
    re.compile(r"test|qa|quality|bdd|tdd", re.IGNORECASE): "testing-validation",
    re.compile(r"deploy|infra|devops|k8s|docker", re.IGNORECASE): "devops-infrastructure",
    re.compile(r"frontend|ui|ux|react|angular|vue", re.IGNORECASE): "frontend",
    re.compile(r"backend|api|service|dotnet|csharp", re.IGNORECASE): "backend-dotnet",
    re.compile(r"python|django|flask|fastapi", re.IGNORECASE): "backend-python",
    re.compile(r"java|spring|maven|gradle", re.IGNORECASE): "backend-java",
    re.compile(r"rca|root.?cause|incident|postmortem", re.IGNORECASE): "rca",
    re.compile(r"release|version|changelog|migration", re.IGNORECASE): "migration",
    re.compile(r"sdlc|process|workflow|agile|scrum|safe", re.IGNORECASE): "sdlc",
    re.compile(r"business|product|owner|stakeholder", re.IGNORECASE): "business-rules",
    re.compile(r"ai|ml|model|llm|neural", re.IGNORECASE): "ai",
    re.compile(r"performance|latency|throughput|benchmark", re.IGNORECASE): "performance-optimization",
}


# ─────────────────────────────────────────────────────────────────────────────
# Classifier
# ─────────────────────────────────────────────────────────────────────────────

class IngestFileClassifier:
    """Classifies files for ingestion pipeline routing.

    Rejects PII-sensitive filenames and unsupported binary formats.
    Assigns domain hints from filename/path patterns.

    Usage::

        classifier = IngestFileClassifier()
        result = classifier.classify_directory(Path("/path/to/docs"))
        for cf in result.processable:
            print(cf.path, cf.category, cf.domain_hint)
    """

    def classify_file(self, path: Path) -> ClassifiedFile:
        """Classify a single file.

        Args:
            path: Path to the file to classify.

        Returns:
            ClassifiedFile with assigned category and domain hint.
        """
        size_bytes = path.stat().st_size if path.exists() else 0
        name = path.name
        suffix = path.suffix.lower()

        # 1. Binary rejection
        if suffix in _BINARY_EXTENSIONS:
            return ClassifiedFile(
                path=path,
                category=IngestFileCategory.REJECTED_BINARY,
                reason=f"Binary extension '{suffix}' not supported for knowledge ingestion.",
                size_bytes=size_bytes,
            )

        # 2. PII rejection
        for pattern in _PII_PATTERNS:
            if pattern.search(name):
                return ClassifiedFile(
                    path=path,
                    category=IngestFileCategory.REJECTED_PII,
                    reason=f"Filename matches PII pattern '{pattern.pattern}'.",
                    size_bytes=size_bytes,
                )

        # 3. Classify processable files
        domain_hint = self._extract_domain_hint(name)
        category, reason = self._categorise(suffix, name)
        return ClassifiedFile(
            path=path,
            category=category,
            reason=reason,
            domain_hint=domain_hint,
            confidence=0.85,
            size_bytes=size_bytes,
        )

    def classify_directory(
        self,
        source_path: Path,
        recursive: bool = True,
    ) -> IngestClassificationResult:
        """Classify all files in a directory.

        Args:
            source_path: Root directory to scan.
            recursive: When True, descend into subdirectories.

        Returns:
            IngestClassificationResult with processable and rejected lists.
        """
        result = IngestClassificationResult()
        if not source_path.is_dir():
            return result

        pattern = "**/*" if recursive else "*"
        for file_path in source_path.glob(pattern):
            if not file_path.is_file():
                continue
            result.total_scanned += 1
            classified = self.classify_file(file_path)
            if classified.category in {
                IngestFileCategory.REJECTED_BINARY,
                IngestFileCategory.REJECTED_PII,
                IngestFileCategory.REJECTED_IRRELEVANT,
            }:
                result.rejected.append(classified)
            else:
                result.processable.append(classified)
        return result

    # ── Helpers ───────────────────────────────────────────────────────────

    def _extract_domain_hint(self, name: str) -> Optional[str]:
        """Return domain hint from filename or None."""
        for pattern, domain in _DOMAIN_HINT_PATTERNS.items():
            if pattern.search(name):
                return domain
        return None

    def _categorise(self, suffix: str, name: str) -> tuple[IngestFileCategory, str]:
        """Return (IngestFileCategory, reason) for a processable file."""
        if suffix in {".yaml", ".yml"}:
            return IngestFileCategory.KNOWLEDGE_YAML, "YAML knowledge file."
        if suffix in {".md", ".txt", ".rst"}:
            name_lower = name.lower()
            if "rca" in name_lower or "root-cause" in name_lower or "incident" in name_lower:
                return IngestFileCategory.RCA_DOC, "RCA/incident document."
            if "release" in name_lower or "changelog" in name_lower:
                return IngestFileCategory.RELEASE_DOC, "Release/changelog document."
            if "architecture" in name_lower or "design" in name_lower or "adr" in name_lower:
                return IngestFileCategory.ARCHITECTURE_DOC, "Architecture/design document."
            if "process" in name_lower or "runbook" in name_lower or "playbook" in name_lower:
                return IngestFileCategory.PROCESS_DOC, "Process/runbook document."
            return IngestFileCategory.TECHNICAL_DOC, "Technical document."
        if suffix in {".docx", ".doc"}:
            return IngestFileCategory.TECHNICAL_DOC, "Word document."
        if suffix in {".xlsx", ".xls"}:
            return IngestFileCategory.TECHNICAL_DOC, "Excel spreadsheet."
        if suffix in {".pptx", ".ppt"}:
            return IngestFileCategory.TECHNICAL_DOC, "PowerPoint presentation."
        if suffix == ".pdf":
            return IngestFileCategory.TECHNICAL_DOC, "PDF document."
        return IngestFileCategory.REJECTED_IRRELEVANT, f"Unsupported extension '{suffix}'."
