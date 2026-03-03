"""
Phase 18 Sub-Phase A — CompanyDomainLoader

Reads company/domains/*.yaml from cortex-registry, caches with 5-min TTL,
and returns a populated CompanyKnowledge instance for use by
UnifiedIntelligenceProvider.targeted() and .full().

Authority: AC-P18-001, AC-P18-002, AC-P18-003, AC-P18-004, AC-P18-012, AC-P18-016
Rule: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (canonical singleton)
"""
# CORE-035 — domain-scoped; class name appropriate for this module

from __future__ import annotations

import logging
import time
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

import yaml

from cortex.intelligence.knowledge.unified_intelligence_context import CompanyKnowledge

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Compliance tag mapping: domain filename → compliance standard label
# ---------------------------------------------------------------------------
_COMPLIANCE_MAP: Dict[str, str] = {
    "payment-security": "PCI-DSS",
    "payment": "PCI-DSS",
    "healthcare": "HIPAA",
    "security-standards": "SECURITY",
    "security": "SECURITY",
    "external-standards": "SOC2",
    "gdpr": "GDPR",
    "legal": "LEGAL",
}

# Default locations (relative to repository root)
_REPO_ROOT = Path(__file__).parents[4]  # cortex/intelligence/knowledge/ → root
_DEFAULT_DOMAINS_DIR = _REPO_ROOT / "cortex-registry" / "company" / "domains"
_DEFAULT_PROFILES_DIR = _REPO_ROOT / "cortex-registry" / "knowledge-base" / "profiles"


class CompanyDomainLoader:
    """
    Loads company domain rules and compliance standards from YAML files.

    Reads every ``*.yaml`` file from *domains_dir* (default:
    ``cortex-registry/company/domains/``) and converts them into a
    :class:`~cortex.intelligence.knowledge.unified_intelligence_context.CompanyKnowledge`
    instance ready for injection into the intelligence synthesis pipeline.

    Features:
    - 5-minute TTL cache (CORE-035) — disk is only read on first call or after expiry.
    - Graceful degradation — unreadable or malformed YAML files are logged and skipped.
    - Domain profile detection — :meth:`detect_profile_for_repo` matches repo tags against
      ``knowledge-base/profiles/*.yaml`` to select the closest domain profile.
    - Thread-safe — all cache mutations are protected by :class:`threading.Lock`.

    Authority: AC-P18-001..AC-P18-004, AC-P18-012, AC-P18-016

    Example::

        loader = CompanyDomainLoader()
        knowledge = loader.load()
        # knowledge.domain_rules  → {"security-standards": {...}, "payment-security": {...}}
        # knowledge.compliance_standards → ["PCI-DSS", "SECURITY"]
    """

    cache_ttl_seconds: int = 300  # 5 minutes — CORE-035 canonical TTL

    def __init__(
        self,
        domains_dir: Optional[Path] = None,
        profiles_dir: Optional[Path] = None,
    ) -> None:
        """
        Initialise the loader.

        Args:
            domains_dir: Directory containing ``company/domains/*.yaml`` files.
                         Defaults to ``cortex-registry/company/domains/`` relative
                         to the repository root.
            profiles_dir: Directory containing ``knowledge/profiles/*.yaml`` files.
                          Defaults to ``cortex-registry/knowledge/profiles/``.
        """
        self._domains_dir: Path = domains_dir or _DEFAULT_DOMAINS_DIR
        self._profiles_dir: Path = profiles_dir or _DEFAULT_PROFILES_DIR

        self._cached_knowledge: Optional[CompanyKnowledge] = None
        self._cache_timestamp: float = 0.0
        self._lock = Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> CompanyKnowledge:
        """
        Return company knowledge, reading YAML files only when the cache is stale.

        The cache is considered stale when ``time.time() - _cache_timestamp``
        exceeds :attr:`cache_ttl_seconds` (300 s).  A stale cache triggers a
        fresh scan of *domains_dir*.

        Returns:
            :class:`CompanyKnowledge` with ``domain_rules`` and
            ``compliance_standards`` populated from all ``*.yaml`` files in
            the configured domains directory.

        Example::

            loader = CompanyDomainLoader()
            knowledge = loader.load()
            assert knowledge.domain_rules != {}
        """
        with self._lock:
            if self._is_cache_fresh():
                assert self._cached_knowledge is not None  # narrowing
                return self._cached_knowledge

            knowledge = self._read_from_disk()
            self._cached_knowledge = knowledge
            self._cache_timestamp = time.time()
            return knowledge

    def detect_profile_for_repo(self, repo_tags: List[str]) -> Optional[str]:
        """
        Match *repo_tags* against tags in each ``profiles/*.yaml`` to find the
        closest domain profile.

        Iterates profiles in alphabetical order and returns the *profile id* of
        the first file whose ``profile.tags`` list has any overlap with
        *repo_tags*.  Returns ``None`` when no profile matches.

        Args:
            repo_tags: List of technology/domain tags describing the repository
                       (e.g. ``["billing", "cost-management"]``).

        Returns:
            Profile ID string (e.g. ``"finops-v1.0"``) or ``None``.

        Example::

            loader = CompanyDomainLoader()
            profile_id = loader.detect_profile_for_repo(["billing", "finance"])
            # → "finops-v1.0"
        """
        if not self._profiles_dir.exists():
            logger.debug("Profiles directory does not exist: %s", self._profiles_dir)
            return None

        repo_tag_set = set(t.lower() for t in repo_tags)

        for profile_path in sorted(self._profiles_dir.glob("*.yaml")):
            try:
                raw = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
                profile_block = (raw or {}).get("profile", {})
                profile_tags = set(
                    t.lower() for t in (profile_block.get("tags") or [])
                )
                if profile_tags & repo_tag_set:
                    profile_id: str = profile_block.get("id", profile_path.stem)
                    logger.debug(
                        "Repo tags %s matched profile '%s' via %s",
                        repo_tags,
                        profile_id,
                        profile_path.name,
                    )
                    return profile_id
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to parse profile %s: %s", profile_path, exc)
                continue

        logger.debug("No profile matched for repo tags: %s", repo_tags)
        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_cache_fresh(self) -> bool:
        """Return True when cached knowledge exists and TTL has not expired."""
        if self._cached_knowledge is None:
            return False
        return (time.time() - self._cache_timestamp) < self.cache_ttl_seconds

    def _read_from_disk(self) -> CompanyKnowledge:
        """Scan *domains_dir* and build a fresh :class:`CompanyKnowledge` object."""
        domain_rules: Dict[str, Any] = {}
        compliance_standards: List[str] = []

        if not self._domains_dir.exists():
            logger.warning(
                "Company domains directory not found: %s", self._domains_dir
            )
            return CompanyKnowledge(
                domain_rules={},
                compliance_standards=[],
                precedence="OVERRIDE",
            )

        for yaml_path in sorted(self._domains_dir.glob("*.yaml")):
            stem = yaml_path.stem  # e.g. "security-standards"
            try:
                raw: Any = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                if not isinstance(raw, dict):
                    logger.warning(
                        "Skipping %s — root is not a YAML mapping", yaml_path.name
                    )
                    continue

                domain_rules[stem] = raw

                # Derive compliance standard from filename
                standard = _COMPLIANCE_MAP.get(stem)
                if standard and standard not in compliance_standards:
                    compliance_standards.append(standard)

                logger.debug("Loaded domain YAML: %s", yaml_path.name)

            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Failed to load domain YAML %s: %s", yaml_path.name, exc
                )

        logger.info(
            "CompanyDomainLoader: loaded %d domain(s), %d compliance standard(s)",
            len(domain_rules),
            len(compliance_standards),
        )

        return CompanyKnowledge(
            domain_rules=domain_rules,
            compliance_standards=compliance_standards,
            precedence="OVERRIDE",
        )


# ---------------------------------------------------------------------------
# Singleton accessor (CORE-035)
# ---------------------------------------------------------------------------

_singleton: Optional[CompanyDomainLoader] = None
_singleton_lock = Lock()


def get_company_domain_loader(
    domains_dir: Optional[Path] = None,
    profiles_dir: Optional[Path] = None,
) -> CompanyDomainLoader:
    """
    Return the process-wide singleton :class:`CompanyDomainLoader`.

    Thread-safe.  Passes *domains_dir* / *profiles_dir* only on first
    construction; subsequent calls ignore those arguments.

    Args:
        domains_dir: Optional override for domains directory (used in tests).
        profiles_dir: Optional override for profiles directory (used in tests).

    Returns:
        Singleton :class:`CompanyDomainLoader` instance.

    Example::

        from cortex.intelligence.knowledge.company_domain_loader import get_company_domain_loader
        loader = get_company_domain_loader()
        knowledge = loader.load()
    """
    global _singleton  # noqa: PLW0603

    if _singleton is None:
        with _singleton_lock:
            if _singleton is None:
                _singleton = CompanyDomainLoader(
                    domains_dir=domains_dir,
                    profiles_dir=profiles_dir,
                )
    return _singleton


# ---------------------------------------------------------------------------
# Phase 71-F ES-004: CompanyKnowledgeProvider
# ---------------------------------------------------------------------------

class CompanyKnowledgeProvider:
    """
    Thin facade over CompanyDomainLoader for LENS cross-wiring (Phase 71-F ES-004).

    Exposes a simple ``load()`` method that returns :class:`CompanyKnowledge`
    and wraps the singleton loader so that LENS components can import a single,
    stable class name without depending on the loader internals.

    CORE-011: type hints on all methods.
    CORE-012: docstrings on all public APIs.
    """

    def __init__(
        self,
        domains_dir: Optional[Path] = None,
        profiles_dir: Optional[Path] = None,
    ) -> None:
        """Initialise provider backed by the singleton CompanyDomainLoader."""
        self._loader: CompanyDomainLoader = get_company_domain_loader(
            domains_dir=domains_dir,
            profiles_dir=profiles_dir,
        )

    def load(self) -> "CompanyKnowledge":
        """Load and return company knowledge (cached with 5-min TTL).

        Returns:
            Populated :class:`CompanyKnowledge` instance.
        """
        return self._loader.load()

    def detect_profile(self, repo_path: Path) -> Optional[str]:
        """Detect domain profile for a repository.

        Args:
            repo_path: Path to repository root.

        Returns:
            Profile name string or None if no match.
        """
        return self._loader.detect_profile_for_repo(repo_path)
