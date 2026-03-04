"""
ReferenceResolver — resolves cross-file references between registry models.

Scans all models for outgoing references (core_rules, template_ref, depends_on,
file references) and matches them to target model IDs. Populates each model's
``references`` dict with ``outgoing`` and ``incoming`` lists. Returns a list of
broken (unresolvable) references for the integrity report.

Reference types supported:
  - ``core_rule``: CORE-NNN rule IDs in metadata.core_rules
  - ``template_ref``: workflow step template_ref pointers
  - ``depends_on``: phase/step dependency lists
  - ``file_ref``: pattern file_references to Python source files
"""

from __future__ import annotations

from typing import Dict, List

from cortex.intelligence.registry.models.base import BaseRegistryModel


class ReferenceResolver:
    """Resolves cross-file references between registry artifact models.

    Two-pass algorithm:
    1. **Extract** — scan each model for outgoing reference pointers.
    2. **Match** — link each pointer to a target model ID; populate
       ``references.outgoing`` and ``references.incoming``.
    """

    def extract_references(self, model: BaseRegistryModel) -> List[Dict[str, str]]:
        """Extract outgoing reference pointers from a single model.

        Args:
            model: A registry artifact model.

        Returns:
            A list of ref dicts, each with ``target_id``, ``ref_type``,
            and ``source_field``.
        """
        refs: List[Dict[str, str]] = []

        # --- core_rules from metadata ---
        core_rules = model.metadata.get("core_rules", [])
        if isinstance(core_rules, list):
            for rule_id in core_rules:
                refs.append({
                    "target_id": str(rule_id),
                    "ref_type": "core_rule",
                    "source_field": "metadata.core_rules",
                })

        # --- template_ref from workflow steps ---
        if hasattr(model, "steps") and isinstance(model.steps, list):
            for step in model.steps:
                if isinstance(step, dict):
                    tref = step.get("template_ref", "")
                    if tref:
                        refs.append({
                            "target_id": str(tref),
                            "ref_type": "template_ref",
                            "source_field": "steps[].template_ref",
                        })

        # --- depends_on ---
        if hasattr(model, "depends_on") and isinstance(model.depends_on, list):
            for dep in model.depends_on:
                refs.append({
                    "target_id": str(dep),
                    "ref_type": "depends_on",
                    "source_field": "depends_on",
                })

        # --- file_references from patterns ---
        if hasattr(model, "file_references") and isinstance(model.file_references, list):
            for fref in model.file_references:
                refs.append({
                    "target_id": str(fref),
                    "ref_type": "file_ref",
                    "source_field": "file_references",
                })

        return refs

    def resolve(self, models: List[BaseRegistryModel]) -> List[Dict[str, str]]:
        """Resolve all cross-references across a list of models.

        Populates each model's ``references.outgoing`` and ``references.incoming``
        lists. Returns a list of broken (unresolvable) references.

        Args:
            models: All registry models to cross-resolve.

        Returns:
            A list of broken ref dicts with ``source_id``, ``target_id``, ``ref_type``.
        """
        if not models:
            return []

        # Reset references for idempotency
        for m in models:
            m.references = {"outgoing": [], "incoming": []}
            m.integrity = {
                "all_refs_resolved": True,
                "schema_valid": True,
                "warnings": [],
            }

        # Build target index: model ID → model, plus rule IDs inside governance models
        target_index: Dict[str, BaseRegistryModel] = {}
        for m in models:
            target_index[m.id] = m
            # Also index individual rule IDs inside governance models
            if hasattr(m, "rules") and isinstance(m.rules, list):
                for rule in m.rules:
                    if isinstance(rule, dict) and "id" in rule:
                        target_index[str(rule["id"])] = m

        broken: List[Dict[str, str]] = []

        for m in models:
            refs = self.extract_references(m)
            for ref in refs:
                target_id = ref["target_id"]
                outgoing_entry = {
                    "target_id": target_id,
                    "ref_type": ref["ref_type"],
                    "source_field": ref["source_field"],
                }
                m.references["outgoing"].append(outgoing_entry)

                if target_id in target_index:
                    target_model = target_index[target_id]
                    target_model.references["incoming"].append({
                        "source_id": m.id,
                        "ref_type": ref["ref_type"],
                        "source_field": ref["source_field"],
                    })
                else:
                    broken.append({
                        "source_id": m.id,
                        "target_id": target_id,
                        "ref_type": ref["ref_type"],
                    })
                    m.integrity["all_refs_resolved"] = False

        return broken
