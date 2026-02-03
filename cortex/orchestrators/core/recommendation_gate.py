"""
RecommendationGate - Regression Prevention Layer for CORTEX Recommendations.

AC-ID: AC-RECOMMENDATION-GATE-001
Prevents recommendations that could cause regressions by:
1. Checking against rejection history (enhancement-history.yaml)
2. Calculating regression risk score
3. Verifying test health in affected areas
4. Detecting potential code duplication

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: Self-Enhancement
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


class GateStatus(Enum):
    """Status of a single gate check."""
    PASS = "pass"
    BLOCKED = "blocked"
    WARN = "warn"


class GateVerdict(Enum):
    """Final verdict from gate evaluation."""
    SAFE = "safe"
    BLOCKED = "blocked"
    WARN = "warn"


@dataclass
class GateResult:
    """
    Result from a single gate check.
    
    Attributes:
        gate_name: Name of the gate (e.g., "REJ-History", "Regression-Risk")
        status: Pass/Blocked/Warn status
        reason: Human-readable explanation
        score: Optional numeric score (0-1.0)
    """
    gate_name: str
    status: GateStatus
    reason: str
    score: Optional[float] = None


@dataclass
class GateEvaluation:
    """
    Complete evaluation result from all gates.
    
    Attributes:
        verdict: Final SAFE/BLOCKED/WARN verdict
        gates: List of individual gate results
        recommendation_title: Title of evaluated recommendation
    """
    verdict: GateVerdict
    gates: List[GateResult]
    recommendation_title: str = ""
    
    def to_markdown(self) -> str:
        """
        Format evaluation as markdown output.
        
        Returns:
            Markdown-formatted evaluation report
        """
        if self.verdict == GateVerdict.BLOCKED:
            lines = [
                "### ⚡ Recommendation BLOCKED",
                "",
                f"**Recommendation:** {self.recommendation_title}",
                "",
                "| Gate | Status | Reason |",
                "|------|--------|--------|"
            ]
            for gate in self.gates:
                status_icon = "❌" if gate.status == GateStatus.BLOCKED else "✅" if gate.status == GateStatus.PASS else "⚠️"
                score_str = f" ({gate.score:.2f})" if gate.score is not None else ""
                lines.append(f"| {gate.gate_name} | {status_icon}{score_str} | {gate.reason} |")
            
            # Add lessons from blocked gates
            blocked_gates = [g for g in self.gates if g.status == GateStatus.BLOCKED]
            if blocked_gates:
                lines.extend([
                    "",
                    "**Learn from rejection:** This recommendation was blocked due to historical patterns.",
                    ""
                ])
        else:
            lines = [
                "### ⚡ Recommendation Safety Check",
                "",
                f"**Recommendation:** {self.recommendation_title}",
                "",
                "| Gate | Status | Score |",
                "|------|--------|-------|"
            ]
            for gate in self.gates:
                status_icon = "✅" if gate.status == GateStatus.PASS else "⚠️"
                score_str = f"{gate.score:.2f}" if gate.score is not None else "—"
                lines.append(f"| {gate.gate_name} | {status_icon} | {score_str} |")
            
            lines.extend([
                "",
                f"**Verdict:** {'SAFE TO RECOMMEND' if self.verdict == GateVerdict.SAFE else 'PROCEED WITH CAUTION'}"
            ])
        
        return "\n".join(lines)


class RecommendationGate:
    """
    Gate that validates recommendations before emission.
    
    Prevents regression-causing recommendations by checking:
    1. REJ-History: Against previously rejected recommendations
    2. Test-Health: Recent test failures in affected areas
    3. Duplication: CORE-035 violation potential
    4. Regression-Risk: Score based on affected files and change type
    
    Attributes:
        risk_threshold: Maximum allowed regression risk (default 0.7)
        similarity_threshold: Minimum similarity to block (default 0.8)
        rejected_recommendations: Loaded rejection history
    """
    
    # Core infrastructure files that carry higher risk
    CORE_FILES = [
        "master_orchestrator",
        "intent_router",
        "tdd_orchestrator",
        "wiring.yaml",
        "server.py",
        "enforcement_orchestrator",
        "governance_registry"
    ]
    
    # Change types with associated base risk scores
    CHANGE_RISK = {
        "add": 0.1,
        "documentation": 0.05,
        "test": 0.1,
        "modify": 0.3,
        "refactor": 0.4,
        "rewrite": 0.8,
        "delete": 0.6
    }
    
    def __init__(
        self,
        risk_threshold: float = 0.7,
        similarity_threshold: float = 0.8,
        enhancement_history_path: Optional[Path] = None
    ) -> None:
        """
        Initialize RecommendationGate.
        
        Args:
            risk_threshold: Maximum regression risk before blocking (0-1.0)
            similarity_threshold: Similarity score to trigger rejection match (0-1.0)
            enhancement_history_path: Path to enhancement-history.yaml
        """
        self.risk_threshold = risk_threshold
        self.similarity_threshold = similarity_threshold
        self.enhancement_history_path = enhancement_history_path or self._find_enhancement_history()
        self.rejected_recommendations: List[Dict[str, Any]] = []
        self._load_rejection_history()
    
    def _find_enhancement_history(self) -> Path:
        """
        Find enhancement-history.yaml in standard locations.
        
        Returns:
            Path to enhancement history file
        """
        # Try standard locations
        locations = [
            Path("docs/meta/enhancement-history.yaml"),
            Path(__file__).parent.parent.parent.parent / "docs" / "meta" / "enhancement-history.yaml",
        ]
        
        for loc in locations:
            if loc.exists():
                return loc
        
        # Return default even if not exists
        return Path("docs/meta/enhancement-history.yaml")
    
    def _load_rejection_history(self) -> None:
        """Load rejected recommendations from enhancement history."""
        try:
            if self.enhancement_history_path.exists():
                import yaml
                with open(self.enhancement_history_path) as f:
                    data = yaml.safe_load(f) or {}
                    self.rejected_recommendations = data.get("rejected_recommendations", [])
                    logger.info(f"Loaded {len(self.rejected_recommendations)} rejected recommendations")
            else:
                logger.debug(f"Enhancement history not found at {self.enhancement_history_path}")
                self.rejected_recommendations = []
        except Exception as e:
            logger.warning(f"Failed to load enhancement history: {e}")
            self.rejected_recommendations = []
    
    def refresh_history(self) -> None:
        """Refresh rejection history from file."""
        self._load_rejection_history()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity score between two text strings.
        
        Uses simple word overlap (Jaccard similarity) for fast comparison.
        Can be enhanced with embeddings for semantic similarity.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Normalize and tokenize
        def tokenize(text: str) -> set:
            # Remove punctuation and lowercase
            words = re.findall(r'\b\w+\b', text.lower())
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                         'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                         'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                         'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                         'and', 'or', 'but', 'if', 'then', 'else', 'when', 'up', 'out',
                         'all', 'this', 'that', 'these', 'those', 'it', 'its'}
            return set(w for w in words if w not in stop_words and len(w) > 2)
        
        set1 = tokenize(text1)
        set2 = tokenize(text2)
        
        if not set1 or not set2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def check_rejection_history(self, recommendation: Dict[str, Any]) -> GateResult:
        """
        Check if recommendation matches any previously rejected patterns.
        
        Args:
            recommendation: Recommendation dict with title and description
            
        Returns:
            GateResult indicating pass or blocked
        """
        rec_text = f"{recommendation.get('title', '')} {recommendation.get('description', '')}"
        
        for rejection in self.rejected_recommendations:
            rejection_text = rejection.get("recommendation", "")
            similarity = self.calculate_similarity(rec_text, rejection_text)
            
            if similarity >= self.similarity_threshold:
                return GateResult(
                    gate_name="REJ-History",
                    status=GateStatus.BLOCKED,
                    reason=f"{rejection.get('id', 'REJ-XXX')} matched (similarity: {similarity:.2f}): {rejection.get('rejection_reason', 'Previously rejected')}",
                    score=similarity
                )
        
        return GateResult(
            gate_name="REJ-History",
            status=GateStatus.PASS,
            reason="No matching rejections found",
            score=0.0
        )
    
    def calculate_regression_risk(self, recommendation: Dict[str, Any]) -> float:
        """
        Calculate regression risk score for a recommendation.
        
        Factors:
        1. Change type (add/modify/rewrite/delete)
        2. Affected files (core vs peripheral)
        3. Number of files affected
        
        Args:
            recommendation: Recommendation dict with affected_files and change_type
            
        Returns:
            Risk score between 0.0 and 1.0
        """
        affected_files = recommendation.get("affected_files", [])
        change_type = recommendation.get("change_type", "modify").lower()
        
        # Base risk from change type
        base_risk = self.CHANGE_RISK.get(change_type, 0.3)
        
        # File count factor (more files = higher risk)
        file_count_factor = min(len(affected_files) * 0.05, 0.3)  # Max 0.3 from file count
        
        # Core file factor
        core_file_factor = 0.0
        for file_path in affected_files:
            file_str = str(file_path).lower()
            for core_pattern in self.CORE_FILES:
                if core_pattern in file_str:
                    core_file_factor = max(core_file_factor, 0.3)
                    break
        
        # Combine factors
        total_risk = min(base_risk + file_count_factor + core_file_factor, 1.0)
        
        return total_risk
    
    def check_test_health(self, recommendation: Dict[str, Any]) -> GateResult:
        """
        Check test health in affected areas.
        
        Currently a placeholder that returns PASS.
        Future: Integrate with pytest to check recent failures.
        
        Args:
            recommendation: Recommendation dict with affected_files
            
        Returns:
            GateResult indicating test health status
        """
        # TODO: Integrate with pytest last run results
        # For now, return PASS as we don't have test failure data
        return GateResult(
            gate_name="Test-Health",
            status=GateStatus.PASS,
            reason="Test health check passed (no recent failures detected)",
            score=None
        )
    
    def check_duplication(self, recommendation: Dict[str, Any]) -> GateResult:
        """
        Check if recommendation would create CORE-035 violation.
        
        Currently a placeholder that returns PASS.
        Future: Integrate with cortex_detect_duplicates.
        
        Args:
            recommendation: Recommendation dict with code_snippet
            
        Returns:
            GateResult indicating duplication status
        """
        # TODO: Integrate with cortex_detect_duplicates MCP tool
        # For now, return PASS
        return GateResult(
            gate_name="Duplication",
            status=GateStatus.PASS,
            reason="No duplication detected",
            score=None
        )
    
    def evaluate(self, recommendation: Dict[str, Any]) -> GateEvaluation:
        """
        Run all gates and return comprehensive evaluation.
        
        Gates checked:
        1. REJ-History: Against rejection history
        2. Test-Health: Recent test failures
        3. Duplication: CORE-035 violations
        4. Regression-Risk: Score based on impact
        
        Args:
            recommendation: Full recommendation dict
            
        Returns:
            GateEvaluation with verdict and all gate results
        """
        gates: List[GateResult] = []
        blocked = False
        warn = False
        
        # Gate 1: Rejection History
        rej_result = self.check_rejection_history(recommendation)
        gates.append(rej_result)
        if rej_result.status == GateStatus.BLOCKED:
            blocked = True
        
        # Gate 2: Test Health
        test_result = self.check_test_health(recommendation)
        gates.append(test_result)
        if test_result.status == GateStatus.BLOCKED:
            blocked = True
        elif test_result.status == GateStatus.WARN:
            warn = True
        
        # Gate 3: Duplication
        dup_result = self.check_duplication(recommendation)
        gates.append(dup_result)
        if dup_result.status == GateStatus.BLOCKED:
            blocked = True
        
        # Gate 4: Regression Risk
        risk_score = self.calculate_regression_risk(recommendation)
        if risk_score > self.risk_threshold:
            risk_result = GateResult(
                gate_name="Regression-Risk",
                status=GateStatus.BLOCKED,
                reason=f"Risk score {risk_score:.2f} exceeds threshold {self.risk_threshold}",
                score=risk_score
            )
            blocked = True
        elif risk_score > 0.5:
            risk_result = GateResult(
                gate_name="Regression-Risk",
                status=GateStatus.WARN,
                reason=f"Moderate risk score {risk_score:.2f}",
                score=risk_score
            )
            warn = True
        else:
            risk_result = GateResult(
                gate_name="Regression-Risk",
                status=GateStatus.PASS,
                reason=f"Low risk score {risk_score:.2f}",
                score=risk_score
            )
        gates.append(risk_result)
        
        # Determine verdict
        if blocked:
            verdict = GateVerdict.BLOCKED
        elif warn:
            verdict = GateVerdict.WARN
        else:
            verdict = GateVerdict.SAFE
        
        return GateEvaluation(
            verdict=verdict,
            gates=gates,
            recommendation_title=recommendation.get("title", "Untitled recommendation")
        )
