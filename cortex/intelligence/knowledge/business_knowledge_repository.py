"""
cortex/intelligence/knowledge/business_knowledge_repository.py

YAML-backed BusinessKnowledgeRepository (Phase 84-b, GAP-84-03).

Replaces the in-memory placeholder in cortex/intelligence/domain_brain/business_knowledge_repository.py
with a disk-persistent implementation backed by business-rules.yaml.

Authority: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (no duplicates)
AC_START: AC-84-B-BUSINESS-KNOWLEDGE-REPO-2026-02-26
AC_COMPLETE: AC-84-B-BUSINESS-KNOWLEDGE-REPO-2026-02-26 | marker pair declared for static audit coverage
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

_DEFAULT_RULES_PATH = Path("cortex-registry/company/domains/shared/business-rules.yaml")


class BusinessKnowledgeRepository:
    """
    YAML-backed repository for extracted business rules.

    Persists to and loads from a business-rules.yaml file on disk,
    providing cross-session durability. Replaces the in-memory stub
    (GAP-84-03).

    Example::

        repo = BusinessKnowledgeRepository(rules_path=Path("business-rules.yaml"))
        rules = repo.get_rules()
        billing_rules = repo.query_by_domain("billing")
    """

    def __init__(
        self,
        rules_path: Optional[Path] = None,
    ) -> None:
        """
        Initialise the YAML-backed repository.

        Args:
            rules_path: Path to business-rules.yaml. Defaults to
                cortex-registry/company/domains/shared/business-rules.yaml.
        """
        self._rules_path: Path = rules_path or _DEFAULT_RULES_PATH
        self._rules: List[Dict[str, Any]] = []
        self._load()

    # ── Public API ──────────────────────────────────────────────────────────

    def get_rules(self) -> List[Dict[str, Any]]:
        """
        Return all loaded business rules.

        Returns:
            List of rule dicts with at least field, description, confidence.
        """
        return list(self._rules)

    def query_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Filter rules by domain name.

        Args:
            domain: Domain name to filter by (e.g. 'billing', 'auth', 'compliance').

        Returns:
            Subset of rules where rule['domain'] matches the given domain.
        """
        return [r for r in self._rules if r.get("domain", "") == domain]

    def add_rule(self, rule: Dict[str, Any]) -> None:
        """
        Add a rule and persist to disk.

        Args:
            rule: Rule dict with field, description, confidence (and optionally domain).
        """
        self._rules.append(rule)
        self._save()

    def reload(self) -> None:
        """Reload rules from disk."""
        self._load()

    # ── Private helpers ──────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load rules from the YAML file. No-op if file does not exist."""
        if not self._rules_path.exists():
            self._rules = []
            return
        try:
            data = yaml.safe_load(self._rules_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self._rules = data.get("rules", [])
            elif isinstance(data, list):
                self._rules = data
            else:
                self._rules = []
        except Exception as exc:
            logger.warning("BusinessKnowledgeRepository: failed to load %s — %s", self._rules_path, exc)
            self._rules = []

    def _save(self) -> None:
        """Persist current rules to the YAML file."""
        try:
            self._rules_path.parent.mkdir(parents=True, exist_ok=True)
            content = {
                "rules": self._rules,
                "version": "1.0",
            }
            self._rules_path.write_text(
                yaml.dump(content, default_flow_style=False, allow_unicode=True),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.warning("BusinessKnowledgeRepository: failed to save — %s", exc)
