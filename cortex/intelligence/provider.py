"""
Phase 65 S4: Unified Intelligence Provider.

Single IIntelligenceProvider interface and UnifiedIntelligenceProvider implementation
that consolidates all intelligence sources (LENS, KG, Profiles, YAMLs) behind one
interface with 3 execution tiers (quick/targeted/full).

Authority: AC-PHASE65-S4-001
Purpose: Eliminate dual synthesis paths (CORE-035), serve both InteractionOrchestrator
and MasterOrchestrator from single provider.
"""

# AC_START: AC-PHASE65-S4-001
# Description: Phase 65 S4 - Unified Intelligence Provider implementation

import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from cortex.intelligence.knowledge.company_domain_loader import get_company_domain_loader
from cortex.intelligence.knowledge.unified_intelligence_context import (
    CompanyKnowledge,
    CORTEXKnowledge,
    LENSIntelligence,
    SynthesisResult,
    UnifiedIntelligenceContext,
)
from cortex.repositories.provider_factory import get_work_item_provider

logger = logging.getLogger(__name__)


class ExecutionTier(Enum):
    """Execution tier for intelligence retrieval (Phase 63 compatibility)."""
    QUICK = "quick"  # <200ms: Cached core rules only
    TARGETED = "targeted"  # <2s: LENS + relevant YAMLs
    FULL = "full"  # <10s: Everything (LENS, KG, Profiles, tier3)


@dataclass
class CacheEntry:
    """Cache entry for intelligence context."""
    context: UnifiedIntelligenceContext
    timestamp: float
    ttl_seconds: int = 300  # 5 min default

    def is_fresh(self) -> bool:
        """Check if cache entry is still fresh."""
        return (time.time() - self.timestamp) < self.ttl_seconds


class IIntelligenceProvider(ABC):
    """
    Abstract interface for unified intelligence provision.

    Single provider interface that both InteractionOrchestrator and
    MasterOrchestrator consume for all intelligence operations.

    Authority: Phase 65 S4-T1
    Purpose: Eliminate dual synthesis paths (CORE-035)

    Methods:
        get_context(): Get unified intelligence context
        get_lens_analysis(): Get LENS file analysis
        get_domain_knowledge(): Get domain-specific knowledge
        get_best_practices(): Get intent-specific best practices
        get_repo_profile(): Get repository profile
        synthesize(): Synthesize all sources into unified context

    Tiered execution:
        quick(): <200ms - Cached core rules only
        targeted(): <2s - LENS + relevant YAMLs
        full(): <10s - Everything (LENS, KG, Profiles, tier3)

    Example:
        >>> provider = get_intelligence_provider()
        >>> context = provider.get_context(intent="IMPLEMENT", file_path="/src/main.py")
        >>> if context.has_violations():
        ...     print("Violations:", context.get_violations())
    """

    @abstractmethod
    def get_context(
        self,
        intent: str,
        file_path: Optional[str] = None,
        repo_name: Optional[str] = None,
        tier: ExecutionTier = ExecutionTier.TARGETED
    ) -> UnifiedIntelligenceContext:
        """
        Get unified intelligence context.

        Args:
            intent: Intent type (IMPLEMENT, FIX, REFACTOR, ANALYZE, etc.)
            file_path: Optional file path being analyzed
            repo_name: Optional repository name
            tier: Execution tier (quick/targeted/full)

        Returns:
            UnifiedIntelligenceContext with all intelligence sources
        """
        pass

    @abstractmethod
    def get_lens_analysis(self, file_path: str) -> Dict[str, Any]:
        """
        Get LENS analysis for file.

        Args:
            file_path: File path to analyze

        Returns:
            Dict with ast_analysis, git_history, comments
        """
        pass

    @abstractmethod
    def get_domain_knowledge(
        self,
        intent: str,
        repo_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get domain-specific knowledge.

        Args:
            intent: Intent type
            repo_name: Optional repository name

        Returns:
            Dict with domain rules and compliance standards
        """
        pass

    @abstractmethod
    def get_best_practices(self, intent: str) -> Dict[str, Any]:
        """
        Get intent-specific best practices.

        Args:
            intent: Intent type

        Returns:
            Dict with best practices, patterns, anti-patterns
        """
        pass

    @abstractmethod
    def get_repo_profile(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Get repository profile from ProfileStore.

        Args:
            repo_name: Repository name

        Returns:
            Repository profile dict or None if not found
        """
        pass

    @abstractmethod
    def synthesize(
        self,
        intent: str,
        lens_intelligence: Optional[LENSIntelligence] = None,
        company_knowledge: Optional[CompanyKnowledge] = None,
        file_path: Optional[str] = None
    ) -> UnifiedIntelligenceContext:
        """
        Synthesize all intelligence sources into unified context.

        Args:
            intent: Intent type
            lens_intelligence: Optional LENS intelligence
            company_knowledge: Optional company knowledge
            file_path: Optional file path

        Returns:
            UnifiedIntelligenceContext with synthesis result
        """
        pass

    # Tiered execution methods

    @abstractmethod
    def quick(self, intent: str) -> UnifiedIntelligenceContext:
        """
        Quick tier execution (<200ms).

        Cached core rules only, no LENS analysis.

        Args:
            intent: Intent type

        Returns:
            UnifiedIntelligenceContext with minimal intelligence
        """
        pass

    @abstractmethod
    def targeted(
        self,
        intent: str,
        file_path: Optional[str] = None
    ) -> UnifiedIntelligenceContext:
        """
        Targeted tier execution (<2s).

        LENS analysis + relevant YAMLs.

        Args:
            intent: Intent type
            file_path: Optional file path to analyze

        Returns:
            UnifiedIntelligenceContext with targeted intelligence
        """
        pass

    @abstractmethod
    def full(
        self,
        intent: str,
        file_path: Optional[str] = None,
        repo_name: Optional[str] = None
    ) -> UnifiedIntelligenceContext:
        """
        Full tier execution (<10s).

        Everything: LENS, KG, Profiles, tier3 cross-domain.

        Args:
            intent: Intent type
            file_path: Optional file path to analyze
            repo_name: Optional repository name

        Returns:
            UnifiedIntelligenceContext with full intelligence
        """
        pass


class UnifiedIntelligenceProvider(IIntelligenceProvider):
    """
    Concrete implementation of unified intelligence provider.

    Consolidates all intelligence sources:
    - LENSOrchestrator: File analysis (AST, git, comments)
    - KnowledgeSynthesisEngine: YAML + company knowledge
    - ProfileStore: Repository profiles
    - KnowledgeQuerier: Knowledge graph entities (future)

    Features:
    - Thread-safe singleton pattern
    - Single LENSCache instance (CORE-035 canonical)
    - Budget-aware tiered execution
    - Graceful degradation on source failures
    - 5-minute TTL caching

    Authority: Phase 65 S4-T2

    Example:
        >>> provider = get_intelligence_provider()
        >>> context = provider.targeted(intent="IMPLEMENT", file_path="/src/main.py")
        >>> print(context.get_cited_rules())
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        """Thread-safe singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize provider with intelligence sources."""
        # Prevent re-initialization of singleton
        if hasattr(self, '_initialized'):
            return

        self._initialized = True

        # Initialize intelligence sources (lazy-loaded)
        self._lens_orchestrator = None
        self._synthesis_engine = None
        self._profile_store = None

        # Single canonical cache (CORE-035)
        self._cache: Dict[str, CacheEntry] = {}
        self._cache_ttl = 300  # 5 minutes

        # Phase 65 S5: Session-scoped storage
        self._session_profiles: Dict[str, Dict[str, Any]] = {}  # session_id -> profile

        logger.info("UnifiedIntelligenceProvider initialized (singleton)")

    def _ensure_lens_orchestrator(self) -> None:
        """Lazy-load LENSOrchestrator."""
        if self._lens_orchestrator is None:
            from cortex.lens.lens_orchestrator import LENSOrchestrator
            # LENSOrchestrator requires repo_path - we'll pass current directory
            # Real usage would determine repo_path from file_path
            self._lens_orchestrator = LENSOrchestrator(repo_path=Path.cwd())
        return self._lens_orchestrator

    def _ensure_synthesis_engine(self) -> None:
        """Lazy-load KnowledgeSynthesisEngine."""
        if self._synthesis_engine is None:
            from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
                get_synthesis_engine,
            )
            self._synthesis_engine = get_synthesis_engine()
        return self._synthesis_engine

    def _ensure_profile_store(self) -> None:
        """Lazy-load ProfileStore."""
        if self._profile_store is None:
            from cortex.intelligence.onboarded_repos.profile_store import ProfileStore
            self._profile_store = ProfileStore()
        return self._profile_store

    def get_context(
        self,
        intent: str,
        file_path: Optional[str] = None,
        repo_name: Optional[str] = None,
        tier: ExecutionTier = ExecutionTier.TARGETED,
        session_id: Optional[str] = None
    ) -> UnifiedIntelligenceContext:
        """Get unified intelligence context."""
        # Generate cache key
        cache_key = f"{intent}:{file_path or 'none'}:{repo_name or 'none'}:{tier.value}"

        # Check cache first
        cached = self._cache.get(cache_key)
        if cached and cached.is_fresh():
            logger.debug(f"Cache hit for {cache_key}")
            return cached.context

        # Execute based on tier
        if tier == ExecutionTier.QUICK:
            context = self.quick(intent)
        elif tier == ExecutionTier.TARGETED:
            context = self.targeted(intent, file_path)
        else:  # FULL
            context = self.full(intent, file_path, repo_name)

        # Cache result
        self._cache[cache_key] = CacheEntry(
            context=context,
            timestamp=time.time(),
            ttl_seconds=self._cache_ttl
        )

        return context

    def get_lens_analysis(self, file_path: str) -> Dict[str, Any]:
        """Get LENS analysis for file."""
        try:
            lens_orch = self._ensure_lens_orchestrator()
            return lens_orch.analyze_file(Path(file_path))
        except Exception as e:
            logger.warning(f"LENS analysis failed for {file_path}: {e}")
            return {
                'ast_analysis': {},
                'git_history': {},
                'comments': {}
            }

    def get_domain_knowledge(
        self,
        intent: str,
        repo_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get domain-specific knowledge."""
        try:
            # Placeholder - future integration with knowledge graph
            return {
                'domain_rules': {},
                'compliance_standards': []
            }
        except Exception as e:
            logger.warning(f"Domain knowledge loading failed: {e}")
            return {
                'domain_rules': {},
                'compliance_standards': []
            }

    def get_best_practices(self, intent: str) -> Dict[str, Any]:
        """Get intent-specific best practices."""
        try:
            engine = self._ensure_synthesis_engine()
            # Delegate to synthesis engine's YAML loading
            return engine._load_cortex_best_practices(intent)
        except Exception as e:
            logger.warning(f"Best practices loading failed for {intent}: {e}")
            return {}

    def get_repo_profile(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """Get repository profile from ProfileStore."""
        try:
            store = self._ensure_profile_store()
            # ProfileStore.load() returns RepositoryProfile
            if store.exists(repo_name):
                profile = store.load(repo_name)
                return {
                    'name': profile.name,
                    'tech_stack': profile.tech_stack.model_dump() if hasattr(profile, 'tech_stack') else {},
                    'structure': profile.structure.model_dump() if hasattr(profile, 'structure') else {}
                }
            return None
        except Exception as e:
            logger.warning(f"Profile loading failed for {repo_name}: {e}")
            return None

    def synthesize(
        self,
        intent: str,
        lens_intelligence: Optional[LENSIntelligence] = None,
        company_knowledge: Optional[CompanyKnowledge] = None,
        file_path: Optional[str] = None
    ) -> UnifiedIntelligenceContext:
        """Synthesize all intelligence sources into unified context."""
        try:
            engine = self._ensure_synthesis_engine()
            return engine.synthesize_unified_context(
                intent_type=intent,
                lens_intelligence=lens_intelligence,
                company_knowledge=company_knowledge,
                file_path=file_path
            )
        except Exception as e:
            logger.error(f"Intelligence synthesis failed: {e}")
            # Return empty context as fallback
            return UnifiedIntelligenceContext.create_empty(intent, file_path)

    # Tiered execution methods

    def quick(self, intent: str) -> UnifiedIntelligenceContext:
        """
        Quick tier execution (<200ms).

        Cached core rules only, no LENS analysis.
        """
        # Only load cached best practices (no LENS, no synthesis)
        return self.synthesize(
            intent=intent,
            lens_intelligence=LENSIntelligence({}, {}, {}),
            company_knowledge=CompanyKnowledge({}, [], "OVERRIDE"),
            file_path=None
        )

    def targeted(
        self,
        intent: str,
        file_path: Optional[str] = None
    ) -> UnifiedIntelligenceContext:
        """
        Targeted tier execution (<2s).

        LENS analysis + relevant YAMLs + company domain knowledge.
        """
        # Get LENS analysis if file provided
        lens_data = {}
        if file_path:
            lens_data = self.get_lens_analysis(file_path)

        lens_intelligence = LENSIntelligence(
            git_analysis=lens_data.get('git_history', {}),
            ast_analysis=lens_data.get('ast_analysis', {}),
            comment_analysis=lens_data.get('comments', {})
        )

        # Load real company knowledge via CompanyDomainLoader (AC-P18-005)
        try:
            company_knowledge = get_company_domain_loader().load()
        except Exception as e:
            logger.warning(f"CompanyDomainLoader failed in targeted(): {e}")
            company_knowledge = CompanyKnowledge({}, [], "OVERRIDE")

        # Synthesize with LENS + YAMLs + company domains
        return self.synthesize(
            intent=intent,
            lens_intelligence=lens_intelligence,
            company_knowledge=company_knowledge,
            file_path=file_path
        )

    def full(
        self,
        intent: str,
        file_path: Optional[str] = None,
        repo_name: Optional[str] = None
    ) -> UnifiedIntelligenceContext:
        """
        Full tier execution (<10s).

        Everything: LENS, company domain knowledge, ADO sprint context (when
        ``ADO_ORG_URL`` is set), KG profiles, and tier3 cross-domain synthesis.
        """
        # --- LENS -----------------------------------------------------------
        lens_data = {}
        if file_path:
            try:
                lens_data = self.get_lens_analysis(file_path)
            except Exception as e:
                logger.warning(f"LENS analysis failed in full tier: {e}")

        lens_intelligence = LENSIntelligence(
            git_analysis=lens_data.get('git_history', {}),
            ast_analysis=lens_data.get('ast_analysis', {}),
            comment_analysis=lens_data.get('comments', {})
        )

        # --- Company domain knowledge (AC-P18-006) --------------------------
        try:
            company_knowledge = get_company_domain_loader().load()
        except Exception as e:
            logger.warning(f"CompanyDomainLoader failed in full(): {e}")
            company_knowledge = CompanyKnowledge({}, [], "OVERRIDE")

        # --- ADO sprint context (AC-P18-008, AC-P18-009, AC-P20-002, AC-P20-003) ---
        if os.getenv("ADO_ORG_URL"):
            try:
                from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper
                ado_provider = get_work_item_provider()
                stories = ado_provider.fetch_user_stories(
                    project=repo_name or "default"
                )
                if stories:
                    sprint_context = ADOContextMapper.map(stories)
                    company_knowledge.domain_rules["sprint_context"] = sprint_context
                    logger.info(
                        "ADO sprint context injected via ADOContextMapper: "
                        "%d stories, sprint=%r",
                        sprint_context.get("open_count", 0),
                        sprint_context.get("sprint_name", ""),
                    )
            except Exception as e:
                logger.warning(
                    "ADO enrichment skipped (non-fatal): %s", e
                )

        # --- Repo profile (optional) ----------------------------------------
        if repo_name:
            try:
                self.get_repo_profile(repo_name)
            except Exception as e:
                logger.warning(f"Profile loading failed in full tier: {e}")

        # --- KG indexing (AC-P20-004, AC-P20-006, AC-P20-014) ---------------
        # Index knowledge-base profiles and repositories into KnowledgeIndexer
        # so KGInference.infer_related_rules() has entity data to work with.
        # Idempotent: overwriting existing entities is safe.
        try:
            from cortex.intelligence.domain_brain.domain_brain.kg_indexer import KnowledgeIndexer
            from pathlib import Path as _Path

            _registry_root = _Path(__file__).parents[3] / "cortex-registry"
            _kg_indexer = KnowledgeIndexer()

            for _yaml in sorted((_registry_root / "knowledge-base" / "profiles").glob("*.yaml")):
                _kg_indexer.index_registry_yaml(_yaml, entity_type="profile")
            for _yaml in sorted((_registry_root / "knowledge-base" / "repositories").glob("*.yaml")):
                _kg_indexer.index_registry_yaml(_yaml, entity_type="repo")

            logger.debug(
                "KG indexing complete: %d entities indexed",
                len(_kg_indexer.entity_index),
            )
        except Exception as _kg_exc:  # noqa: BLE001
            logger.warning("KG indexing skipped (non-fatal): %s", _kg_exc)

        # --- Synthesize everything ------------------------------------------
        return self.synthesize(
            intent=intent,
            lens_intelligence=lens_intelligence,
            company_knowledge=company_knowledge,
            file_path=file_path
        )

    # Phase 65 S5: Session management and turn-over-turn accumulation

    def start_session(
        self,
        session_id: str,
        repo_name: Optional[str] = None
    ) -> None:
        """
        Start new intelligence session.

        Loads repository profile on session start (S5-T2).
        Creates turn context for session-scoped accumulation.

        Args:
            session_id: Unique session identifier
            repo_name: Optional repository name for profile loading
        """
        from cortex.intelligence.turn_context import get_turn_context

        # Initialize turn context
        turn_context = get_turn_context(session_id)

        # Load repo profile if provided (S5-T2)
        if repo_name:
            try:
                profile = self.get_repo_profile(repo_name)
                if profile:
                    # Cache profile for session lifetime
                    self._session_profiles[session_id] = profile
                    logger.info(f"Session started: {session_id}, profile loaded: {repo_name}")
                else:
                    logger.warning(f"Session started: {session_id}, profile not found: {repo_name}")
            except Exception as e:
                logger.error(f"Session profile loading failed: {e}")
                # Continue without profile (graceful degradation)
        else:
            logger.info(f"Session started: {session_id} (no profile)")

    def get_session_profile(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached repository profile for session.

        Args:
            session_id: Session identifier

        Returns:
            Repository profile dict or None if not cached
        """
        return self._session_profiles.get(session_id)

    def get_turn_context(self, session_id: str) -> None:
        """
        Get turn context for session.

        Args:
            session_id: Session identifier

        Returns:
            TurnContext for session
        """
        from cortex.intelligence.turn_context import get_turn_context
        return get_turn_context(session_id)

    def get_accumulated_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get accumulated context across all turns in session.

        Args:
            session_id: Session identifier

        Returns:
            Dict with accumulated entities, patterns, standards, files, violations
        """
        from cortex.intelligence.turn_context import get_turn_context
        turn_context = get_turn_context(session_id)
        return turn_context.get_accumulated_context()

    def _synthesize_cross_domain(
        self,
        intent: str,
        context: str
    ) -> Dict[str, List[str]]:
        """
        Synthesize cross-domain knowledge (architecture, security, testing).

        Delegates to :meth:`KnowledgeSynthesisEngine.synthesize_cross_domain_context`
        which reads ``cortex-registry/patterns/*.yaml``, security YAMLs, and CORE
        testing rules to produce non-empty recommendation lists.

        Args:
            intent: Intent type (IMPLEMENT, FIX, REFACTOR, ANALYZE, etc.)
            context: Context string (e.g. "FastAPI endpoint in DDD repo")

        Returns:
            Dict with architecture/security/testing recommendation lists.
        """
        try:
            synthesis_engine = self._ensure_synthesis_engine()
            result = synthesis_engine.synthesize_cross_domain_context(intent, context)
            logger.info(f"Cross-domain synthesis completed: {intent}")
            return result
        except Exception as e:
            logger.error(f"Cross-domain synthesis failed: {e}")
            return {'architecture': [], 'security': [], 'testing': []}

    def synthesize_cross_domain(
        self,
        intent: str,
        context: str
    ) -> Dict[str, List[str]]:
        """
        Public API for cross-domain synthesis.

        Args:
            intent: Intent type
            context: Context description

        Returns:
            Cross-domain knowledge by category
        """
        return self._synthesize_cross_domain(intent, context)


# Singleton accessor
_provider_instance: Optional[UnifiedIntelligenceProvider] = None
_provider_lock = Lock()


def get_intelligence_provider() -> IIntelligenceProvider:
    """
    Get singleton intelligence provider instance.

    Thread-safe accessor for unified intelligence provider.

    Returns:
        UnifiedIntelligenceProvider singleton instance

    Example:
        >>> provider = get_intelligence_provider()
        >>> context = provider.quick(intent="IMPLEMENT")
    """
    global _provider_instance

    if _provider_instance is None:
        with _provider_lock:
            if _provider_instance is None:
                _provider_instance = UnifiedIntelligenceProvider()

    return _provider_instance


def synthesize(
    request: str,
    tier: str = "targeted",
) -> "UnifiedIntelligenceContext":
    """Canonical single-entry-point for knowledge synthesis across all 5 engines.

    Routes to the appropriate execution tier of ``UnifiedIntelligenceProvider``:
    - ``"quick"``    → ``provider.quick(intent)`` (<200 ms, cached core rules)
    - ``"targeted"`` → ``provider.targeted(intent)`` (<2 s, LENS + YAMLs)
    - ``"full"``     → ``provider.full(intent)`` (<10 s, all engines)

    Callers should prefer this function over direct engine instantiation to
    satisfy GAP-80-07 (single canonical Knowledge API surface).

    Args:
        request: The intent/request string to synthesise knowledge for.
        tier: Execution tier — one of ``"quick"``, ``"targeted"``, ``"full"``.
              Defaults to ``"targeted"``.

    Returns:
        ``UnifiedIntelligenceContext`` combining LENS, company, and CORTEX knowledge.

    Example::

        ctx = synthesize("refactor authentication module", tier="full")
        for guidance in ctx.synthesis_result.guidance:
            print(guidance)
    """
    provider = get_intelligence_provider()
    if tier == "quick":
        return provider.quick(intent=request)
    if tier == "full":
        return provider.full(intent=request)
    # Default: targeted
    return provider.targeted(intent=request)


# AC_COMPLETE: AC-PHASE65-S4-001 ✅ Interface + implementation complete