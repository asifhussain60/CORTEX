"""Evidence Collector - Phase 12 CAP-1 Implementation.

Gathers evidence from multiple sources for capacity estimation:
- LENS orchestrator (complexity, history, patterns)
- Git repository (commit history, contributors)
- Tier3 knowledge base (domain patterns, similar tasks)
- Current workload and team state
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class EvidenceSourceType(Enum):
    """Types of evidence sources."""
    LENS_ANALYSIS = "lens_analysis"
    GIT_HISTORY = "git_history"
    DOMAIN_PATTERNS = "domain_patterns"
    TEAM_WORKLOAD = "team_workload"
    SIMILAR_TASKS = "similar_tasks"


@dataclass
class TaskEvidence:
    """Evidence collected for task estimation.

    Attributes:
        task_id: Task identifier
        task_description: Task description
        lens_complexity: LENS complexity score (1-13)
        git_churn: Number of files likely to change
        similar_tasks: List of similar historical tasks
        domain_patterns: Relevant domain patterns
        team_info: Team composition and skills
    """
    task_id: str
    task_description: str
    lens_complexity: int = 0
    git_churn: int = 0
    similar_tasks: List[str] = field(default_factory=list)
    domain_patterns: Dict[str, Any] = field(default_factory=dict)
    team_info: Dict[str, Any] = field(default_factory=dict)
    evidence_sources: Set[str] = field(default_factory=set)


class LENSEvidenceCollector:
    """Collects complexity evidence from LENS orchestrator."""

    def collect_complexity(self, file_path: str) -> int:
        """Collect complexity score from LENS.

        Returns 1-13 complexity score:
        1-3: Trivial (doc changes, simple reconfig)
        4-6: Simple (single file, straightforward)
        7-9: Medium (multi-file, moderate dependencies)
        10-11: Complex (significant refactoring, many impacts)
        12-13: Very Complex (system-wide changes, many unknowns)

        Args:
            file_path: Path to file

        Returns:
            Complexity score (1-13)
        """
        # In production: Call LENS AST analyzer
        return 7  # Default medium complexity


class GitEvidenceCollector:
    """Collects evidence from Git repository."""

    def collect_churn_estimate(self, task_description: str) -> int:
        """Estimate expected file churn.

        Args:
            task_description: Task description

        Returns:
            Expected number of files to change
        """
        # In production: Analyze Git history patterns
        # High-churn tasks: "refactor", "migrate", "restructure" → 20+
        # Medium-churn: "feature", "fix", "update" → 5-10
        # Low-churn: "docs", "config", "patch" → 1-3

        if any(kw in task_description.lower() for kw in ["refactor", "migrate", "restructure"]):
            return 15
        elif any(kw in task_description.lower() for kw in ["feature", "fix", "update"]):
            return 7
        else:
            return 2

    def get_recent_contributors(self, file_path: str) -> List[str]:
        """Get recent contributors to file.

        Args:
            file_path: Path to file

        Returns:
            List of contributor names
        """
        # In production: Query Git blame/log
        return []


class DomainPatternCollector:
    """Collects evidence from domain knowledge."""

    def find_similar_patterns(self, task_description: str) -> List[Dict[str, Any]]:
        """Find similar historical tasks.

        Args:
            task_description: Task description

        Returns:
            List of similar tasks with metadata
        """
        # In production: Query Tier3 knowledge base
        return []

    def get_domain_risks(self, task_type: str) -> List[str]:
        """Get known risks for task type.

        Args:
            task_type: Type of task

        Returns:
            List of known risks
        """
        # In production: Look up domain patterns
        return []


class EvidenceCollector:
    """Phase 12 CAP-1: Multi-Source Evidence Collector.

    Gathers evidence from:
    1. LENS orchestrator - Code complexity, patterns
    2. Git history - File churn, contributors, trends
    3. Domain patterns - Similar tasks, known risks
    4. Team workload - Availability, skills, capacity
    5. Similar tasks - Historical velocity, effort data

    AC-CAP-001-01: Collect evidence from LENS orchestrator
    AC-CAP-001-02: Collect evidence from Git history
    AC-CAP-001-03: Match to similar historical tasks
    AC-CAP-001-04: Produce unified TaskEvidence object
    """

    def __init__(self):
        """Initialize EvidenceCollector."""
        self.lens_collector = LENSEvidenceCollector()
        self.git_collector = GitEvidenceCollector()
        self.domain_collector = DomainPatternCollector()

    def collect_evidence(self, task_id: str, task_description: str) -> TaskEvidence:
        """Collect comprehensive evidence for task.

        Phase 12 AC-CAP-001-04: Produce unified evidence

        Args:
            task_id: Task identifier
            task_description: Task description

        Returns:
            TaskEvidence object with all collected evidence
        """
        evidence = TaskEvidence(
            task_id=task_id,
            task_description=task_description,
        )

        # Collect LENS evidence
        try:
            evidence.lens_complexity = self.lens_collector.collect_complexity(task_id)
            evidence.evidence_sources.add(EvidenceSourceType.LENS_ANALYSIS.value)
        except Exception as e:
            logger.warning(f"LENS collection failed: {e}")

        # Collect Git evidence
        try:
            evidence.git_churn = self.git_collector.collect_churn_estimate(task_description)
            evidence.evidence_sources.add(EvidenceSourceType.GIT_HISTORY.value)
        except Exception as e:
            logger.warning(f"Git collection failed: {e}")

        # Collect domain patterns
        try:
            similar = self.domain_collector.find_similar_patterns(task_description)
            evidence.similar_tasks = [s.get("task_id", "") for s in similar]
            evidence.evidence_sources.add(EvidenceSourceType.DOMAIN_PATTERNS.value)
        except Exception as e:
            logger.warning(f"Domain pattern collection failed: {e}")

        return evidence

    def get_evidence_summary(self, evidence: TaskEvidence) -> Dict[str, Any]:
        """Get summary of collected evidence.

        Args:
            evidence: Task evidence

        Returns:
            Summary dictionary
        """
        return {
            "task_id": evidence.task_id,
            "lens_complexity": evidence.lens_complexity,
            "git_churn": evidence.git_churn,
            "similar_tasks": len(evidence.similar_tasks),
            "evidence_sources": list(evidence.evidence_sources),
        }


if __name__ == "__main__":
    logger.info("EvidenceCollector - Phase 12 CAP-1")
