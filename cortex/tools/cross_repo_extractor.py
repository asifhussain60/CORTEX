"""Cross-Repo Feedback Extractor — Phase 139.

Components:
  SanitizationEngine  — 8 privacy gates (G1–G8) with CORTEX vocabulary preservation
  CrossRepoExtractor  — 6-stage extraction pipeline: git analysis → filter →
                        classify → extract → sanitize → markdown output
  CommitRecord        — dataclass for git commit metadata
  CapabilityRecord    — dataclass for extracted CORTEX capability
  ChangeClassification — enum of 8 change types

Phase: 139 (GAP-139-01, GAP-139-02)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-028 (snake_case), CORE-035 (single canonical), CORE-049 (silent)
🔒 Scope Lock: feedback

AC_START: AC-139-FEEDBACK-EXTRACTOR-001
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
from pathlib import Path
import re
import subprocess
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# =============================================================================
# CORTEX Vocabulary — terms preserved through all sanitization gates
# =============================================================================

#: Domain-specific CORTEX terms that MUST survive all sanitization gates.
CORTEX_VOCABULARY: Set[str] = {
    # Orchestrators
    "ComplexityTriageEngine", "CAPE", "KAL", "SubPhaseCheckpointInjector",
    "RollbackManager", "WorkflowComposer", "IntelligenceFacade",
    "MasterOrchestrator", "IntentRouter", "TDDOrchestrator",
    "AuditOrchestrator", "EnforcementOrchestrator", "HealthOrchestrator",
    "VacuumOrchestrator", "DebuggerOrchestrator", "DigestSessionOrchestrator",
    "DistillationOrchestrator", "DesignCoordinator", "PlanningOrchestrator",
    "WorkflowComposer", "RCAEngine", "MarkerInjectionEngine",
    "InteractionOrchestrator", "LearningOrchestrator", "GitOrchestrator",
    "FeedbackOrchestrator", "CrossRepoExtractor", "SanitizationEngine",
    # Governance rules
    "CORE-008", "CORE-011", "CORE-012", "CORE-028", "CORE-035", "CORE-048",
    "CORE-049", "CORE-064", "CORE-068",
    # Framework terms
    "CORTEX", "TDD", "MCP", "LENS", "URS", "RCA", "AC_START", "AC_COMPLETE",
    "cortex-master.yaml", "cortex-registry", "IntentType", "CapabilityRecord",
    "CommitRecord", "ChangeClassification", "CheckpointState",
    # Phase identifiers  
    "phase-139", "phase-138", "phase-137", "phase-136", "phase-135",
    # Design patterns
    "OrchestratorProtocolMixin", "OrchestratorBase", "IntelligenceFacade",
}


# =============================================================================
# SanitizationEngine — 8 privacy gates
# =============================================================================

class SanitizationEngine:
    """8-gate privacy sanitization engine for cross-repo feedback content.

    Removes personal identifiers, organisation URLs, credentials, codenames,
    customer references, algorithm details, channel references, and applies
    a final validation sweep. CORTEX vocabulary terms are preserved through
    all gates.

    Gates:
        G1 — personal identifiers (name patterns)
        G2 — organisation URLs (internal/intranet URLs)
        G3 — credentials (API keys, passwords, tokens)
        G4 — codenames (injected via _codenames set)
        G5 — customer references (injected via _customer_names set)
        G6 — algorithm details (PROPRIETARY_* patterns)
        G7 — channel references (#internal-*, @mentions)
        G8 — final validation (any remaining PROPRIETARY_ patterns)
    """

    # Pre-compiled patterns at class level (REFACTOR gate — CORE-011)
    _RE_PERSONAL: re.Pattern[str] = re.compile(
        r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"  # "First Last" name pattern
    )
    _RE_ORG_URL: re.Pattern[str] = re.compile(
        r"https?://(?:[^\s\"'<>]*(?:internal|intranet|corp|acme|vpn|private|local)[^\s\"'<>]*)",
        re.IGNORECASE,
    )
    _RE_CREDENTIAL: re.Pattern[str] = re.compile(
        r"(?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|auth[_-]?token)"
        r"\s*=\s*\S+|"
        r"ghp_[A-Za-z0-9]{36}|"
        r"(?:Bearer|Basic)\s+[A-Za-z0-9+/=]{16,}",
        re.IGNORECASE,
    )
    _RE_ALGORITHM: re.Pattern[str] = re.compile(
        r"\bPROPRIETARY_[A-Z0-9_]+\b"
    )
    _RE_CHANNEL: re.Pattern[str] = re.compile(
        r"#[a-z][a-z0-9\-_]+-(?:alerts?|internal|private|team|eng|dev|ops|prod)[a-z0-9\-_]*|"
        r"#internal-[a-z0-9\-_]+",
        re.IGNORECASE,
    )
    _RE_FINAL_CHECK: re.Pattern[str] = re.compile(
        r"\bPROPRIETARY_[A-Z0-9_]+\b"
    )

    def __init__(
        self,
        codenames: Optional[Set[str]] = None,
        customer_names: Optional[Set[str]] = None,
    ) -> None:
        """Initialise with optional codename and customer-name sets.

        Args:
            codenames: Set of internal project codenames to redact (G4).
            customer_names: Set of customer names to redact (G5).
        """
        self._codenames: Set[str] = codenames or set()
        self._customer_names: Set[str] = customer_names or set()

    # ------------------------------------------------------------------
    # Gate methods
    # ------------------------------------------------------------------

    def apply_gate_g1(self, text: str) -> Tuple[str, int]:
        """G1 — remove personal identifier patterns (First Last names).

        Args:
            text: Input text.

        Returns:
            Tuple of (sanitized_text, actions_taken).
        """
        matches = self._RE_PERSONAL.findall(text)
        # Preserve CORTEX vocabulary terms that match the name pattern
        preserved = {m for m in matches if m in CORTEX_VOCABULARY}
        actions = 0
        for match in matches:
            if match not in preserved:
                text = text.replace(match, "[REDACTED]")
                actions += 1
        return text, actions

    def apply_gate_g2(self, text: str) -> Tuple[str, int]:
        """G2 — remove internal/organisation URL patterns.

        Args:
            text: Input text.

        Returns:
            Tuple of (sanitized_text, actions_taken).
        """
        result, count = self._RE_ORG_URL.subn("[REDACTED-URL]", text)
        return result, count

    def apply_gate_g3(self, text: str) -> Tuple[str, int]:
        """G3 — remove credential patterns (API keys, passwords, tokens).

        Args:
            text: Input text.

        Returns:
            Tuple of (sanitized_text, actions_taken).
        """
        result, count = self._RE_CREDENTIAL.subn("[REDACTED-CREDENTIAL]", text)
        return result, count

    def apply_gate_g4(self, text: str) -> Tuple[str, int]:
        """G4 — remove internal project codenames.

        Args:
            text: Input text.

        Returns:
            Tuple of (sanitized_text, actions_taken).
        """
        actions = 0
        for codename in self._codenames:
            if codename in text:
                text = text.replace(codename, "[REDACTED-CODENAME]")
                actions += 1
        return text, actions

    def apply_gate_g5(self, text: str) -> Tuple[str, int]:
        """G5 — remove customer name references.

        Args:
            text: Input text.

        Returns:
            Tuple of (sanitized_text, actions_taken).
        """
        actions = 0
        for customer in self._customer_names:
            if customer in text:
                text = text.replace(customer, "[REDACTED-CUSTOMER]")
                actions += 1
        return text, actions

    def apply_gate_g6(self, text: str) -> Tuple[str, int]:
        """G6 — remove proprietary algorithm name patterns (PROPRIETARY_*).

        Args:
            text: Input text.

        Returns:
            Tuple of (sanitized_text, actions_taken).
        """
        result, count = self._RE_ALGORITHM.subn("[REDACTED-ALGORITHM]", text)
        return result, count

    def apply_gate_g7(self, text: str) -> Tuple[str, int]:
        """G7 — remove internal channel references (#channel-name).

        Args:
            text: Input text.

        Returns:
            Tuple of (sanitized_text, actions_taken).
        """
        result, count = self._RE_CHANNEL.subn("[REDACTED-CHANNEL]", text)
        return result, count

    def apply_gate_g8(self, text: str) -> Tuple[str, int]:
        """G8 — final validation sweep for any remaining PROPRIETARY_ patterns.

        Args:
            text: Input text.

        Returns:
            Tuple of (sanitized_text, actions_taken).
        """
        result, count = self._RE_FINAL_CHECK.subn("[REDACTED]", text)
        return result, count

    # ------------------------------------------------------------------
    # Orchestrator
    # ------------------------------------------------------------------

    def sanitize(self, text: str) -> Tuple[str, int]:
        """Apply all 8 gates sequentially to *text*, preserving CORTEX vocabulary.

        Args:
            text: Input text to sanitize.

        Returns:
            Tuple of (sanitized_text, total_action_count).
        """
        # Mask CORTEX vocabulary terms before running gates (longest first to avoid substring clashes)
        placeholders: Dict[str, str] = {}
        masked = text
        for i, term in enumerate(sorted(CORTEX_VOCABULARY, key=len, reverse=True)):
            if term in masked:
                placeholder = f"__CVOCAB{i:03d}__"
                masked = masked.replace(term, placeholder)
                placeholders[placeholder] = term

        # Run all 8 gates
        total_actions = 0
        for gate in (
            self.apply_gate_g1,
            self.apply_gate_g2,
            self.apply_gate_g3,
            self.apply_gate_g4,
            self.apply_gate_g5,
            self.apply_gate_g6,
            self.apply_gate_g7,
            self.apply_gate_g8,
        ):
            masked, actions = gate(masked)
            total_actions += actions

        # Restore CORTEX vocabulary terms
        for placeholder, original in placeholders.items():
            masked = masked.replace(placeholder, original)

        return masked, total_actions


# =============================================================================
# CrossRepoExtractor — dataclasses + 6-stage pipeline
# =============================================================================

class ChangeClassification(Enum):
    """8-type classification of CORTEX-relevant change types.

    Used by CrossRepoExtractor.classify_change() to categorise git changes.
    """
    NEW_ORCHESTRATOR = "new_orchestrator"
    NEW_TEST = "new_test"
    MCP_ENHANCEMENT = "mcp_enhancement"
    NEW_CAPABILITY = "new_capability"
    ENHANCED_CAPABILITY = "enhanced_capability"
    BUG_FIX = "bug_fix"
    NEW_GOVERNANCE = "new_governance"
    CONFIG = "config"


@dataclass
class CommitRecord:
    """Metadata for a single git commit.

    Attributes:
        sha: Full commit SHA.
        message: Commit message.
        files_changed: List of file paths changed in this commit.
        date: ISO date string (YYYY-MM-DD).
    """
    sha: str
    message: str
    files_changed: List[str]
    date: str


@dataclass
class CapabilityRecord:
    """Extracted CORTEX capability from a commit.

    Attributes:
        classification: The ChangeClassification type.
        title: Short capability title.
        description: Sanitized description.
        files: Source files associated with this capability.
        commit_sha: The originating commit SHA.
    """
    classification: ChangeClassification
    title: str
    description: str
    files: List[str]
    commit_sha: str


# Relevance filter — file path prefixes considered CORTEX-framework-relevant
_RELEVANT_PREFIXES = (
    "cortex/",
    "tests/",
    "cortex-registry/",
    ".github/",
    "scripts/",
)

# Classification rules: (path fragment, ChangeClassification)
_CLASSIFICATION_RULES: List[Tuple[str, ChangeClassification]] = [
    ("cortex/orchestrators/", ChangeClassification.NEW_ORCHESTRATOR),
    ("cortex/mcp/", ChangeClassification.MCP_ENHANCEMENT),
    ("tests/", ChangeClassification.NEW_TEST),
    ("cortex-registry/governance/", ChangeClassification.NEW_GOVERNANCE),
    ("cortex-registry/", ChangeClassification.CONFIG),
    ("cortex/models/", ChangeClassification.NEW_CAPABILITY),
    ("cortex/core/", ChangeClassification.NEW_CAPABILITY),
    ("cortex/intelligence/", ChangeClassification.ENHANCED_CAPABILITY),
    (".github/", ChangeClassification.CONFIG),
]


class CrossRepoExtractor:
    """6-stage cross-repo capability extraction pipeline.

    Stages:
        1. Git commit analysis  — parse git log for CommitRecord list
        2. Relevance filter     — is_cortex_relevant() removes non-framework paths
        3. Change classification — classify_change() maps paths to ChangeClassification
        4. Capability extraction — extract_capabilities() builds CapabilityRecord list
        5. Sanitization         — sanitize_capabilities() applies SanitizationEngine
        6. Markdown output      — generate_output() produces structured markdown

    Usage::

        extractor = CrossRepoExtractor(repo_path=Path("/path/to/repo"))
        commits = extractor.get_commits(since="2026-01-01")
        capabilities = extractor.extract_capabilities(commits)
        sanitized = extractor.sanitize_capabilities(capabilities)
        markdown = extractor.generate_output(sanitized)
    """

    def __init__(
        self,
        repo_path: Path,
        sanitization_engine: Optional[SanitizationEngine] = None,
    ) -> None:
        """Initialise extractor with target repo path and optional custom engine.

        Args:
            repo_path: Path to the git repository to analyse.
            sanitization_engine: Optional custom SanitizationEngine instance.
        """
        self.repo_path = repo_path
        self.sanitization_engine = sanitization_engine or SanitizationEngine()

    # ------------------------------------------------------------------
    # Stage 1: Git commit analysis
    # ------------------------------------------------------------------

    def get_commits(self, since: Optional[str] = None) -> List[CommitRecord]:
        """Parse git log for CommitRecord list.

        Args:
            since: ISO date string to filter commits from (e.g. "2026-01-01").

        Returns:
            List of CommitRecord objects.
        """
        cmd = [
            "git", "-C", str(self.repo_path),
            "log", "--name-only", "--format=%H|%s|%ci",
        ]
        if since:
            cmd.append(f"--since={since}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return []
            return self._parse_git_log(result.stdout)
        except FileNotFoundError:
            return []

    def _parse_git_log(self, log_output: str) -> List[CommitRecord]:
        """Parse raw git log output into CommitRecord list.

        Args:
            log_output: Raw stdout from git log.

        Returns:
            List of CommitRecord.
        """
        records: List[CommitRecord] = []
        current_sha = current_msg = current_date = ""
        current_files: List[str] = []

        for line in log_output.splitlines():
            line = line.strip()
            if not line:
                if current_sha:
                    records.append(CommitRecord(
                        sha=current_sha,
                        message=current_msg,
                        files_changed=current_files,
                        date=current_date[:10] if current_date else "",
                    ))
                    current_sha = current_msg = current_date = ""
                    current_files = []
            elif "|" in line and not current_sha:
                parts = line.split("|", 2)
                if len(parts) == 3:
                    current_sha, current_msg, current_date = parts
            else:
                if current_sha:
                    current_files.append(line)

        if current_sha:
            records.append(CommitRecord(
                sha=current_sha,
                message=current_msg,
                files_changed=current_files,
                date=current_date[:10] if current_date else "",
            ))
        return records

    # ------------------------------------------------------------------
    # Stage 2: Relevance filter
    # ------------------------------------------------------------------

    def is_cortex_relevant(self, file_path: str) -> bool:
        """Return True if *file_path* is CORTEX-framework-relevant.

        Relevant paths: cortex/, tests/, cortex-registry/, .github/, scripts/
        Non-relevant: docs/, deployment/, _workspaces/, .cortex-runtime/

        Args:
            file_path: Relative path string to evaluate.

        Returns:
            True if the path is CORTEX-framework-relevant.
        """
        return any(file_path.startswith(prefix) for prefix in _RELEVANT_PREFIXES)

    # ------------------------------------------------------------------
    # Stage 3: Change classification
    # ------------------------------------------------------------------

    def classify_change(self, file_path: str) -> ChangeClassification:
        """Classify a file path into a ChangeClassification type.

        Uses the first matching rule from _CLASSIFICATION_RULES.

        Args:
            file_path: Relative file path.

        Returns:
            ChangeClassification matching the path.
        """
        for fragment, classification in _CLASSIFICATION_RULES:
            if file_path.startswith(fragment) or fragment in file_path:
                return classification
        return ChangeClassification.CONFIG

    # ------------------------------------------------------------------
    # Stage 4: Capability extraction
    # ------------------------------------------------------------------

    def extract_capabilities(self, commits: List[CommitRecord]) -> List[CapabilityRecord]:
        """Extract CapabilityRecord list from commit history.

        Filters commits to CORTEX-relevant files and classifies each.

        Args:
            commits: List of CommitRecord from git log.

        Returns:
            List of CapabilityRecord.
        """
        capabilities: List[CapabilityRecord] = []
        for commit in commits:
            relevant_files = [f for f in commit.files_changed if self.is_cortex_relevant(f)]
            if not relevant_files:
                continue
            classification = self.classify_change(relevant_files[0])
            capabilities.append(CapabilityRecord(
                classification=classification,
                title=commit.message[:80] if commit.message else "Unknown",
                description=commit.message,
                files=relevant_files,
                commit_sha=commit.sha,
            ))
        return capabilities

    # ------------------------------------------------------------------
    # Stage 5: Sanitization
    # ------------------------------------------------------------------

    def sanitize_capabilities(self, capabilities: List[CapabilityRecord]) -> List[CapabilityRecord]:
        """Apply SanitizationEngine to all text fields of every CapabilityRecord.

        Args:
            capabilities: List of CapabilityRecord to sanitize.

        Returns:
            New list of CapabilityRecord with sanitized text fields.
        """
        sanitized: List[CapabilityRecord] = []
        for cap in capabilities:
            clean_title, _ = self.sanitization_engine.sanitize(cap.title)
            clean_desc, _ = self.sanitization_engine.sanitize(cap.description)
            sanitized.append(CapabilityRecord(
                classification=cap.classification,
                title=clean_title,
                description=clean_desc,
                files=cap.files,
                commit_sha=cap.commit_sha,
            ))
        return sanitized

    # ------------------------------------------------------------------
    # Stage 6: Markdown output generation
    # ------------------------------------------------------------------

    def generate_output(self, capabilities: List[CapabilityRecord]) -> str:
        """Generate a structured markdown capability report.

        Args:
            capabilities: Sanitized list of CapabilityRecord.

        Returns:
            Markdown string with Executive Summary + Capability Index sections.
        """
        if not capabilities:
            return "## Capability Report\n\nNo capabilities found.\n"

        date_str = datetime.now().strftime("%Y-%m-%d")
        lines: List[str] = [
            f"# CORTEX Capability Report — {date_str}",
            "",
            "## Executive Summary",
            "",
            f"Extracted **{len(capabilities)}** CORTEX-relevant capability records "
            "from cross-repo git analysis.",
            "",
            "## Capability Index",
            "",
        ]

        for cap in capabilities:
            lines.append(f"### {cap.title}")
            lines.append(f"- **Classification:** `{cap.classification.value}`")
            lines.append(f"- **Commit:** `{cap.commit_sha[:8] if cap.commit_sha else 'N/A'}`")
            lines.append(f"- **Files:** {', '.join(f'`{f}`' for f in cap.files[:3])}")
            lines.append(f"- **Description:** {cap.description}")
            lines.append("")

        return "\n".join(lines)


__all__ = [
    "SanitizationEngine",
    "CrossRepoExtractor",
    "CommitRecord",
    "CapabilityRecord",
    "ChangeClassification",
    "CORTEX_VOCABULARY",
]

# AC_COMPLETE: AC-139-FEEDBACK-EXTRACTOR-001 ✅ SanitizationEngine + CrossRepoExtractor implemented
