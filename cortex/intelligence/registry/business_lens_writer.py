"""
BusinessLensWriter — deterministic business-language summaries per artifact.

Generates executive summaries for each registry artifact using template-based
synthesis (no LLM dependency). Each model type has a dedicated template that
extracts key fields and renders a human-readable business-context description.

Future: extend with LLM integration for richer summaries.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from cortex.intelligence.registry.models.base import BaseRegistryModel


class BusinessLensWriter:
    """Generate business-language summaries for registry artifacts."""

    # ── public API ──────────────────────────────────────────────────────

    def generate_summary(self, model: BaseRegistryModel) -> str:
        """Generate a business-language summary for a single model.

        Args:
            model: A parsed registry artifact model.

        Returns:
            A human-readable summary string.
        """
        handler = self._handlers.get(model.type)
        if handler is not None:
            return handler(self, model)
        return self._generic_summary(model)

    def generate_all(
        self, models: List[BaseRegistryModel]
    ) -> List[Dict[str, Any]]:
        """Generate summaries for a list of models.

        Args:
            models: List of parsed registry artifact models.

        Returns:
            List of dicts with ``id``, ``type``, ``title``, and ``summary``.
        """
        return [
            {
                "id": m.id,
                "type": m.type,
                "title": m.title,
                "summary": self.generate_summary(m),
            }
            for m in models
        ]

    def to_json(self, results: List[Dict[str, Any]]) -> str:
        """Serialize summary results to JSON.

        Args:
            results: Output from :meth:`generate_all`.

        Returns:
            Deterministic JSON string.
        """
        return json.dumps(results, indent=2, sort_keys=True, ensure_ascii=False)

    # ── per-type summary handlers ───────────────────────────────────────

    def _governance_summary(self, model: BaseRegistryModel) -> str:
        rules = getattr(model, "rules", []) or []
        domain = getattr(model, "domain", "")
        severity = getattr(model, "severity", "")
        rule_ids = [r.get("id", "") for r in rules if isinstance(r, dict)]
        rule_list = ", ".join(rule_ids[:5]) if rule_ids else "none"
        return (
            f'"{model.title}" is a {severity} governance rule in the {domain} domain. '
            f"It defines {len(rules)} rule(s) ({rule_list}) that enforce "
            f"development standards across the codebase."
        )

    def _workflow_summary(self, model: BaseRegistryModel) -> str:
        steps = getattr(model, "steps", []) or []
        category = getattr(model, "category", "")
        version = getattr(model, "version", "")
        step_names = [
            s.get("name", s.get("id", f"step {i+1}"))
            for i, s in enumerate(steps)
            if isinstance(s, dict)
        ]
        step_list = " → ".join(step_names[:6]) if step_names else "none"
        ver = f" (v{version})" if version else ""
        return (
            f'"{model.title}"{ver} is a {category} workflow template with '
            f"{len(steps)} step(s): {step_list}."
        )

    def _pattern_summary(self, model: BaseRegistryModel) -> str:
        pattern_type = getattr(model, "pattern_type", "")
        description = getattr(model, "description", "")
        participants = getattr(model, "participants", []) or []
        type_label = f" ({pattern_type})" if pattern_type else ""
        desc_part = f" {description}" if description else ""
        parts = f" Participants: {', '.join(participants[:5])}." if participants else ""
        return (
            f'"{model.title}"{type_label} is a design pattern.{desc_part}{parts}'
        )

    def _plan_summary(self, model: BaseRegistryModel) -> str:
        status = getattr(model, "status", "PLANNED")
        phases = getattr(model, "phases", []) or []
        priority = getattr(model, "priority", "")
        return (
            f'"{model.title}" is a {priority} plan ({status}) with '
            f"{len(phases)} phase(s)."
        )

    def _config_summary(self, model: BaseRegistryModel) -> str:
        sections = getattr(model, "sections", {}) or {}
        scope = getattr(model, "scope", "")
        scope_part = f" for {scope}" if scope else ""
        return (
            f'"{model.title}" is a configuration artifact{scope_part} with '
            f"{len(sections)} section(s)."
        )

    def _knowledge_summary(self, model: BaseRegistryModel) -> str:
        domains = getattr(model, "domains", []) or []
        guides = getattr(model, "guides", []) or []
        return (
            f'"{model.title}" is a knowledge index covering {len(domains)} domain(s) '
            f"and {len(guides)} guide(s)."
        )

    def _template_summary(self, model: BaseRegistryModel) -> str:
        blocks = getattr(model, "blocks", []) or []
        zones = getattr(model, "zones", []) or []
        return (
            f'"{model.title}" is a response template with {len(blocks)} block(s) '
            f"and {len(zones)} zone(s)."
        )

    def _generic_summary(self, model: BaseRegistryModel) -> str:
        content = model.content or {}
        key_count = len(content) if isinstance(content, dict) else 0
        return (
            f'"{model.title}" is a {model.type} artifact with {key_count} '
            f"content field(s)."
        )

    # handler dispatch map
    _handlers: Dict[str, Any] = {
        "governance-rule": _governance_summary,
        "workflow-template": _workflow_summary,
        "pattern": _pattern_summary,
        "plan": _plan_summary,
        "config": _config_summary,
        "knowledge": _knowledge_summary,
        "response-template": _template_summary,
    }
