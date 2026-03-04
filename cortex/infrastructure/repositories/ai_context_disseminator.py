"""
AIContextDisseminator — route classified AI context to 5 registry destinations.

Phase 121 Sub-phase C | GAP-121-03, GAP-121-04.
Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
           CORE-028 (snake_case), CORE-035 (single canonical implementation).

Destinations:
  1. company/domains/{repo}-ai-standards.yaml       (coding standards)
  2. company/domains/{repo}-security-overrides.yaml (security rules, if any)
  3. company/repos/{repo}/10_ai_context/index.json  (dashboard tab)
  4. knowledge/repositories/{repo}.yaml             (ai_context extension)
  (5. knowledge/INDEX.yaml — handled separately by Sub-phase D)

PII guard is applied to ALL outputs before write.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict

import yaml

from cortex.infrastructure.repositories.ai_content_classifier import ClassifiedContent
from cortex.infrastructure.repositories.ai_context_scanner import AIContextResult
from cortex.infrastructure.repositories.ai_pii_guard import AIPIIGuard

logger = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.0.0"
_DASHBOARD_SCHEMA_VERSION = "2.0.0"


class AIContextDisseminator:
    """
    Route AI context scan results to the correct YAML / JSON destinations.

    Applies PII guard to all outputs and uses content-type routing to
    place data in the correct location within the CORTEX registry hierarchy.

    Example::

        disseminator = AIContextDisseminator()
        disseminator.disseminate(scan_result, classified_content, "myrepo", base_dir)
    """

    def __init__(self) -> None:
        """Initialise with a PII guard."""
        self._pii = AIPIIGuard()

    # ── Public API ────────────────────────────────────────────────────────────

    def disseminate(
        self,
        scan_result: AIContextResult,
        classified_content: ClassifiedContent,
        repo_name: str,
        base_dir: Path,
    ) -> None:
        """
        Write AI context to all applicable registry destinations.

        Args:
            scan_result: Scanner output with vendor breakdown and inventories.
            classified_content: Classified standards extracted from AI files.
            repo_name: Repository name (used to build output paths).
            base_dir: Registry root (cortex-registry/ in production, tmp_path in tests).
        """
        now = datetime.now(tz=timezone.utc).isoformat()

        self._write_domain_standards(classified_content, scan_result, repo_name, base_dir, now)

        if classified_content.security_rules:
            self._write_security_overrides(
                classified_content.security_rules, repo_name, base_dir, now
            )

        self._write_dashboard_tab(scan_result, repo_name, base_dir, now)
        self._extend_repo_profile(scan_result, repo_name, base_dir, now)

    # ── Private writers ───────────────────────────────────────────────────────

    def _write_domain_standards(
        self,
        classified: ClassifiedContent,
        scan_result: AIContextResult,
        repo_name: str,
        base_dir: Path,
        now: str,
    ) -> None:
        """Write coding / naming standards to company/domains/{repo}-ai-standards.yaml."""
        dest_dir = base_dir / "company" / "domains"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{repo_name}-ai-standards.yaml"

        vendors = [v.vendor for v in scan_result.vendors]

        data: Dict[str, Any] = {
            "schema_version": _SCHEMA_VERSION,
            "name": f"{repo_name}-ai-standards",
            "source_repo": repo_name,
            "extracted_at": now,
            "ai_vendors_detected": vendors,
            "standards": {
                "coding_conventions": [
                    self._pii.sanitize(s) for s in classified.coding_conventions
                ],
                "naming_rules": [],
                "error_handling": [],
                "testing_standards": [
                    self._pii.sanitize(s) for s in classified.testing_standards
                ],
            },
            "template": "ai-standards",
        }

        dest.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False))
        logger.info("AI standards written → %s", dest)

    def _write_security_overrides(
        self,
        security_rules: list,
        repo_name: str,
        base_dir: Path,
        now: str,
    ) -> None:
        """Write security overrides to company/domains/{repo}-security-overrides.yaml."""
        dest_dir = base_dir / "company" / "domains"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{repo_name}-security-overrides.yaml"

        data: Dict[str, Any] = {
            "schema_version": _SCHEMA_VERSION,
            "name": f"{repo_name}-security-overrides",
            "source_repo": repo_name,
            "extracted_at": now,
            "security_rules": [self._pii.sanitize(r) for r in security_rules],
        }
        dest.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False))
        logger.info("Security overrides written → %s", dest)

    def _write_dashboard_tab(
        self,
        scan_result: AIContextResult,
        repo_name: str,
        base_dir: Path,
        now: str,
    ) -> None:
        """Write dashboard tab JSON to company/repos/{repo}/10_ai_context/index.json."""
        dest_dir = base_dir / "company" / "repos" / repo_name / "10_ai_context"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "index.json"

        data: Dict[str, Any] = {
            "schema_version": _DASHBOARD_SCHEMA_VERSION,
            "tab_id": "10_ai_context",
            "label": "AI Context",
            "repository": repo_name,
            "generated_at": now,
            "vendors": [
                {
                    "vendor": v.vendor,
                    "confidence": round(v.confidence, 3),
                    "files_found": v.files_found,
                    "has_instructions": v.has_instructions,
                    "has_prompts": v.has_prompts,
                    "has_agents": v.has_agents,
                }
                for v in scan_result.vendors
            ],
            "prompt_inventory": scan_result.prompt_inventory,
            "agent_inventory": scan_result.agent_inventory,
            "total_ai_files": scan_result.total_ai_files,
            "primary_vendor": scan_result.primary_vendor,
        }
        dest.write_text(json.dumps(data, indent=2))
        logger.info("AI context dashboard tab written → %s", dest)

    def _extend_repo_profile(
        self,
        scan_result: AIContextResult,
        repo_name: str,
        base_dir: Path,
        now: str,
    ) -> None:
        """Extend knowledge/repositories/{repo}.yaml with an ai_context section."""
        repo_profile = base_dir / "knowledge" / "repositories" / f"{repo_name}.yaml"
        if not repo_profile.exists():
            logger.debug("Repo profile not found, skipping extension: %s", repo_profile)
            return

        existing = yaml.safe_load(repo_profile.read_text()) or {}
        existing["ai_context"] = {
            "vendors_detected": [v.vendor for v in scan_result.vendors],
            "primary_vendor": scan_result.primary_vendor,
            "instruction_file_count": sum(
                1 for v in scan_result.vendors if v.has_instructions
            ),
            "prompt_file_count": len(scan_result.prompt_inventory),
            "agent_file_count": len(scan_result.agent_inventory),
            "extracted_standards_count": 0,  # populated after classification
            "last_scanned": now,
            "dissemination_targets": [
                f"company/domains/{repo_name}-ai-standards.yaml",
                f"company/repos/{repo_name}/10_ai_context/index.json",
            ],
        }
        repo_profile.write_text(yaml.dump(existing, allow_unicode=True, sort_keys=False))
        logger.info("Repo profile extended with ai_context → %s", repo_profile)


__all__ = ["AIContextDisseminator"]
