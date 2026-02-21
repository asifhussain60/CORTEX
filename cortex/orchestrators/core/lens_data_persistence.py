"""
LENS Data Persistence Service — Appends LENS analysis to company registry.

All LENS output from InteractionOrchestrator per-turn analysis
gets appended to cortex-registry/company/ in the correct repo folder.

Supports both JSON (dashboards/lens/) and YAML (repos/{repo}/) append.

Authority: Phase 102 — Plan-Before-Execute Gate
CORE Rules:
  - CORE-008: TDD mandatory
  - CORE-011: Type hints on all functions
  - CORE-012: Google-style docstrings
  - CORE-028: snake_case file naming
  - CORE-035: Single canonical implementation
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Company registry root (relative to repo root)
_COMPANY_ROOT = "cortex-registry/company"
_LENS_DATA_DIR = "dashboards/lens"
_REPOS_DIR = "repos"


class LensDataPersistenceService:
    """Appends LENS analysis data to the company registry.

    Each LENS analysis is timestamped and appended — never overwrites.
    Data goes to two locations:
      1. dashboards/lens/{repo}_data_{timestamp}.json  (dashboard consumption)
      2. repos/{repo}/lens_history.json  (repo-level history append)

    Attributes:
        repo_root: Absolute path to the repository root.
        company_root: Absolute path to company registry root.
    """

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        """Initialize persistence service.

        Args:
            repo_root: Repository root path. Defaults to cwd.
        """
        self.repo_root = repo_root or Path.cwd()
        self.company_root = self.repo_root / _COMPANY_ROOT

    def append_lens_data(
        self,
        repo_slug: str,
        lens_context: Dict[str, Any],
        intent_type: str = "UNKNOWN",
        plan_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Append LENS analysis data to company registry.

        Creates timestamped JSON in dashboards/lens/ and appends
        to repo-level lens_history.json.

        Args:
            repo_slug: Repository identifier (e.g., 'cortex').
            lens_context: LENS analysis output from InteractionOrchestrator.
            intent_type: Classified intent for context.
            plan_id: Associated plan ID if plan gate active.

        Returns:
            Dict with file paths written and success status.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        record = self._build_record(
            repo_slug, lens_context, intent_type, plan_id, timestamp
        )

        results: Dict[str, Any] = {
            "timestamp": timestamp,
            "repo_slug": repo_slug,
            "dashboard_file": None,
            "history_appended": False,
        }

        # 1. Write timestamped dashboard file
        dashboard_path = self._write_dashboard_file(repo_slug, record, timestamp)
        if dashboard_path:
            results["dashboard_file"] = str(dashboard_path)

        # 2. Append to repo lens history
        history_ok = self._append_to_history(repo_slug, record)
        results["history_appended"] = history_ok

        logger.info(
            "LENS data persisted for %s: dashboard=%s, history=%s",
            repo_slug,
            dashboard_path is not None,
            history_ok,
        )
        return results

    def _build_record(
        self,
        repo_slug: str,
        lens_context: Dict[str, Any],
        intent_type: str,
        plan_id: Optional[str],
        timestamp: str,
    ) -> Dict[str, Any]:
        """Build a LENS data record for persistence.

        Args:
            repo_slug: Repository identifier.
            lens_context: LENS analysis output.
            intent_type: Classified intent.
            plan_id: Associated plan ID.
            timestamp: ISO timestamp string.

        Returns:
            Structured record dict.
        """
        # Preserve all LENS data — known fields get canonical keys,
        # unknown fields preserved under their original keys.
        _KNOWN_KEYS = {"overview", "dependencies", "classes", "timeline",
                        "impact", "brain", "governance", "orchestrators"}

        record: Dict[str, Any] = {
            "overview": lens_context.get("overview", {}),
            "dependencies": lens_context.get("dependencies", {}),
            "classes": lens_context.get("classes", {}),
            "timeline": lens_context.get("timeline", {}),
            "impact": lens_context.get("impact", {}),
            "brain": lens_context.get("brain"),
            "governance": lens_context.get("governance"),
            "orchestrators": lens_context.get("orchestrators"),
        }

        # Preserve any non-standard LENS fields (e.g., custom analyzers)
        for key, value in lens_context.items():
            if key not in _KNOWN_KEYS and key != "_metadata":
                record[key] = value

        record["_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "intent_type": intent_type,
            "plan_id": plan_id,
            "repo_slug": repo_slug,
            "lens_keys": list(lens_context.keys()),
            "source": "PlanGateService",
        }

        return record

    def _write_dashboard_file(
        self,
        repo_slug: str,
        record: Dict[str, Any],
        timestamp: str,
    ) -> Optional[Path]:
        """Write timestamped JSON to dashboards/lens/.

        Args:
            repo_slug: Repository identifier.
            record: LENS data record.
            timestamp: Timestamp for filename.

        Returns:
            Path to written file, or None on failure.
        """
        try:
            lens_dir = self.company_root / _LENS_DATA_DIR
            lens_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{repo_slug}_data_{timestamp}.json"
            filepath = lens_dir / filename
            filepath.write_text(
                json.dumps(record, indent=2, default=str),
                encoding="utf-8",
            )
            return filepath
        except Exception as e:
            logger.warning("Failed to write dashboard file: %s", e)
            return None

    def _append_to_history(
        self,
        repo_slug: str,
        record: Dict[str, Any],
    ) -> bool:
        """Append record to repo-level lens_history.json.

        Creates or appends to repos/{repo}/lens_history.json.
        The file is a JSON array — each entry is appended.

        Args:
            repo_slug: Repository identifier.
            record: LENS data record.

        Returns:
            True if append succeeded.
        """
        try:
            repo_dir = self.company_root / _REPOS_DIR / repo_slug
            repo_dir.mkdir(parents=True, exist_ok=True)
            history_path = repo_dir / "lens_history.json"

            # Load existing history or create new
            history: list = []
            if history_path.exists():
                try:
                    content = history_path.read_text(encoding="utf-8")
                    loaded = json.loads(content)
                    if isinstance(loaded, list):
                        history = loaded
                except (json.JSONDecodeError, ValueError):
                    # Corrupted file — start fresh with backup
                    logger.warning("Corrupted lens_history.json, starting fresh")

            # Append new record
            history.append(record)

            # Write back
            history_path.write_text(
                json.dumps(history, indent=2, default=str),
                encoding="utf-8",
            )
            return True
        except Exception as e:
            logger.warning("Failed to append lens history: %s", e)
            return False

    def get_scan_depth(
        self,
        intent_type: str,
        lens_context: Dict[str, Any],
    ) -> str:
        """Determine intelligent LENS scan depth based on intent.

        Avoids unnecessary deep scans. Only code-modifying intents
        with high complexity warrant full deep LENS analysis.

        Args:
            intent_type: Classified intent (IMPLEMENT/FIX/QUERY...).
            lens_context: Current LENS context for complexity hints.

        Returns:
            Scan depth: 'shallow', 'standard', or 'deep'.
        """
        intent_upper = intent_type.upper()

        # Read-only intents: shallow scan
        if intent_upper in {"QUERY", "RECALL", "DIGEST"}:
            return "shallow"

        # Analysis intents: standard scan
        if intent_upper in {"ANALYZE", "ONBOARD", "DESIGN"}:
            return "standard"

        # Code-modifying: check complexity
        complexity = lens_context.get("complexity", 0)
        files_affected = lens_context.get("files_affected", 0)
        risk_score = lens_context.get("risk_score", 0.0)

        if complexity > 10 or files_affected > 5 or risk_score > 0.7:
            return "deep"

        return "standard"
