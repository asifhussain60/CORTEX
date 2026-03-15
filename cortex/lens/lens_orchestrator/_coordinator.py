"""
LENSOrchestrator — slim coordinator (Phase 103-d, GAP-103-04).

Delegates to 5 extracted mixins:
  - LensAnalysisMixin   : per-file analysis helpers
  - LensRemoteMixin     : remote/branch analysis
  - LensHolisticMixin   : repository holistic analysis
  - LensCompanyMixin    : company knowledge + compliance
  - LensVisionMixin     : image/vision analysis

Original: cortex/lens/lens_orchestrator.py (2,045L)
Coordinator: _coordinator.py (≤ 750L)

Authority: CORE-008, CORE-011, CORE-012, LENS-003, SWEEP-103-GOD-OBJECT-DECOMPOSITION
"""
# CORE-035 — domain-scoped; class name is contextually appropriate here
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from cortex.lens.analyzers.polyglot_analyzer import PolyglotAnalyzer

# Mixins
from cortex.lens.lens_orchestrator.lens_analysis_mixin import LensFileAnalysisMixin
from cortex.lens.lens_orchestrator.lens_remote_mixin import LensRemoteMixin
from cortex.lens.lens_orchestrator.lens_holistic_mixin import LensHolisticMixin
from cortex.lens.lens_orchestrator.lens_company_mixin import LensCompanyMixin
from cortex.lens.lens_orchestrator.lens_vision_mixin import LensVisionMixin

# Models
from cortex.lens.lens_orchestrator.lens_models import LENSContext

# Infrastructure
from cortex.lens.analyzers.api_analyzer import get_api_analyzer
from cortex.lens.analyzers.python_structure_analyzer import ASTAnalyzer
from cortex.lens.analyzers.comment_extractor import CommentExtractor
from cortex.lens.analyzers.config_analyzer import get_config_analyzer
from cortex.lens.analyzers.database_analyzer import get_database_analyzer
from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
from cortex.lens.analyzers.tech_stack_analyzer import TechStackAnalyzer
from cortex.lens.cache import get_lens_cache

# Phase 84-a: Business rules extraction
try:
    from cortex.intelligence.lens.domain_inference.rule_extractor import (
        RuleExtractor as _RuleExtractor,
    )
    _RULE_EXTRACTOR_AVAILABLE = True
except ImportError:
    _RULE_EXTRACTOR_AVAILABLE = False
    _RuleExtractor = None  # type: ignore[assignment,misc]

__all__ = [
    "LENSOrchestrator",
    "LENSContext",
    "LensFileAnalysisMixin",
    "LensRemoteMixin",
    "LensHolisticMixin",
    "LensCompanyMixin",
    "LensVisionMixin",
    "get_lens_orchestrator",
]


class LENSOrchestrator(
    LensFileAnalysisMixin,
    LensRemoteMixin,
    LensHolisticMixin,
    LensCompanyMixin,
    LensVisionMixin,
):
    """
    Unified LENS intelligence orchestrator.

    Coordinates GitHistoryAnalyzer, ASTAnalyzer, and CommentExtractor
    to provide comprehensive code intelligence for CORTEX operations.

    Features:
    - Unified analyze_file() API combining all three analyzers
    - Result caching for performance (avoids repeated analysis)
    - Batch analysis for multiple files
    - IntentRouter-compatible output (LENS-002 integration)
    - Graceful error handling (partial results on analyzer failures)
    - Remote repository and branch comparison
    - Holistic repository analysis (9 analyzers)
    - Company domain knowledge integration
    - Vision API image analysis
    """

    def __init__(
        self,
        repo_path: Path,
        git_analyzer: Optional[GitHistoryAnalyzer] = None,
        ast_analyzer: Optional[ASTAnalyzer] = None,
        comment_extractor: Optional[CommentExtractor] = None,
        polyglot_analyzer: Optional["PolyglotAnalyzer"] = None,
    ) -> None:
        """
        Initialize LENSOrchestrator.

        Args:
            repo_path: Path to git repository root
            git_analyzer: Optional custom GitHistoryAnalyzer (for testing)
            ast_analyzer: Optional custom ASTAnalyzer (for testing)
            comment_extractor: Optional custom CommentExtractor (for testing)
            polyglot_analyzer: Optional custom PolyglotAnalyzer (multi-language support)
        """
        self.repo_path = repo_path
        self.git_analyzer = git_analyzer or GitHistoryAnalyzer(repo_path=repo_path)

        from cortex.lens.analyzers.polyglot_analyzer import PolyglotAnalyzer
        self.polyglot_analyzer = polyglot_analyzer or PolyglotAnalyzer()
        self.ast_analyzer = ast_analyzer or ASTAnalyzer()
        self.comment_extractor = comment_extractor or CommentExtractor()

        self.config_analyzer = get_config_analyzer()
        self.database_analyzer = get_database_analyzer()
        self.api_analyzer = get_api_analyzer()

        from cortex.intelligence.call_graph import CallGraphBuilder
        self.call_graph_builder = CallGraphBuilder()

        from cortex.intelligence.dependency_mapper import DependencyMapper
        self.dependency_mapper = DependencyMapper()

        from cortex.intelligence.pattern_detector import PatternDetector
        self.pattern_detector = PatternDetector()

        self.tech_stack_analyzer = TechStackAnalyzer()

        # ENH-042: TTL-based cache
        self.lens_cache = get_lens_cache()
        self.cache: Dict[Path, Dict[str, Any]] = {}  # legacy

        # Phase 83-e: URS engine (lazy-init)
        self._urs_engine = None

    # ------------------------------------------------------------------
    # Core public API
    # ------------------------------------------------------------------

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a single file using all three LENS analyzers.

        Results are cached. Output format compatible with IntentRouter (LENS-002).

        Args:
            file_path: Path to file to analyze

        Returns:
            Dict with git_analysis, ast_analysis, comment_analysis, and _metadata.
        """
        cache_key = self.lens_cache.generate_key(file_path, self.repo_path)
        cached_result = self.lens_cache.get(cache_key)
        if cached_result is not None:
            cached_result.setdefault("_metadata", {})["cache_hit"] = True
            cached_result["_metadata"]["cache_key"] = cache_key
            return cached_result

        if file_path in self.cache:
            return self.cache[file_path]

        start_time = time.time()

        git_result = self._analyze_git(file_path)
        ast_result = self._analyze_ast(file_path)
        comment_result = self._analyze_comments(file_path)
        relationship_findings = self._build_relationship_findings(file_path, ast_result)
        dependency_findings = self._build_dependency_findings(file_path, ast_result)
        pattern_findings = self._build_pattern_findings(file_path, ast_result)
        tech_stack_result = self._detect_tech_stack(file_path, ast_result)
        analysis_time_ms = int((time.time() - start_time) * 1000)
        business_rules = self._extract_business_rules(file_path, ast_result)

        context = {
            "git_analysis": git_result,
            "ast_analysis": ast_result,
            "comment_analysis": comment_result,
            "relationship_findings": relationship_findings,
            "dependency_findings": dependency_findings,
            "pattern_findings": pattern_findings,
            "tech_stack": tech_stack_result,
            "business_rules": business_rules,
            "_metadata": {
                "analysis_time_ms": analysis_time_ms,
                "file_path": str(file_path),
                "analyzers_run": [
                    "git", "ast", "comment", "relationship",
                    "dependency", "pattern", "tech_stack",
                ],
                "cache_hit": False,
                "cache_key": cache_key,
            },
        }

        self.lens_cache.set(cache_key, context)
        self.cache[file_path] = context
        return context

    def analyze_batch(self, file_paths: List[Path]) -> Dict[Path, Dict[str, Any]]:
        """
        Analyze multiple files in batch.

        Args:
            file_paths: List of file paths to analyze

        Returns:
            Dict mapping file paths to LENS contexts
        """
        return {fp: self.analyze_file(fp) for fp in file_paths}

    # ------------------------------------------------------------------
    # Cache management
    # ------------------------------------------------------------------

    def clear_cache(self) -> None:
        """Clear the result cache (ENH-042: clears both TTL and legacy)."""
        self.lens_cache.clear()
        self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics (ENH-042)."""
        return self.lens_cache.get_stats().to_dict()

    def cleanup_expired_cache(self) -> int:
        """Remove expired cache entries (ENH-042)."""
        return self.lens_cache.cleanup_expired()

    # ------------------------------------------------------------------
    # Phase 83-e: URS analysis outcome correlation
    # ------------------------------------------------------------------

    def record_analysis_outcome(self, analysis_id: str, success: bool) -> None:
        """
        Record the outcome of a LENS analysis for URS feedback.

        Args:
            analysis_id: The analysis_id from LENSContext.
            success: Whether the analysis led to a successful operation.
        """
        from cortex.intelligence.learning.reinforcement_signal import (
            ReinforcementEngine,
            SignalType,
        )

        signal_type = SignalType.MILD_REWARD if success else SignalType.MILD_PUNISHMENT
        try:
            if self._urs_engine is None:
                self._urs_engine = ReinforcementEngine()
            self._urs_engine.emit_signal(
                signal_type=signal_type,
                pattern_id=analysis_id,
                source_orchestrator="LENSOrchestrator",
                context={"success": success},
            )
        except Exception as exc:
            logger.debug(
                "LENSOrchestrator.record_analysis_outcome: non-fatal — %s", exc
            )


def get_lens_orchestrator(repo_path: Path) -> LENSOrchestrator:
    """Get or create LENSOrchestrator instance."""
    return LENSOrchestrator(repo_path=repo_path)
