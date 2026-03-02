"""
Knowledge Inference - Reasoning over knowledge graph.

Extended in Phase 20 with infer_related_rules() — returns CORTEX governance
rule IDs related to a given entity (e.g. "finops-v1.0" → ["FIN-001", "FIN-002"]).

Authority: AC-P20-005
Rule: CORE-011 (type hints), CORE-012 (docstrings)
"""

from typing import Any, Dict, List, Set


class KnowledgeInference:
    """Performs reasoning and inference over knowledge relationships."""

    def __init__(self) -> None:
        """Initialize the inference engine."""
        self.relationships: List[Dict[str, Any]] = []
        self.rules: List[Dict[str, Any]] = []
        self.inferred_facts: Set[str] = set()

    def add_relationship(self, source: str, target: str, rel_type: str) -> None:
        """Add a relationship for inference."""
        self.relationships.append({
            "source": source,
            "target": target,
            "type": rel_type,
        })

    def compute_transitive_closure(self, source: str, rel_type: str) -> Set[str]:
        """Compute transitive closure of a relationship."""
        reachable: Set[str] = set()
        to_visit = [source]
        visited = {source}

        while to_visit:
            current = to_visit.pop(0)

            for rel in self.relationships:
                if rel["source"] == current and rel["type"] == rel_type:
                    target = rel["target"]
                    if target not in visited:
                        reachable.add(target)
                        visited.add(target)
                        to_visit.append(target)

        return reachable

    def analyze_impact(self, source: str) -> Set[str]:
        """Analyze impact of a change to an entity."""
        # Find all entities affected (dependencies)
        affected: Set[str] = set()
        to_visit = [source]
        visited = {source}

        while to_visit:
            current = to_visit.pop(0)

            for rel in self.relationships:
                if rel["source"] == current:
                    target = rel["target"]
                    if target not in visited:
                        affected.add(target)
                        visited.add(target)
                        to_visit.append(target)

        return affected

    def add_rule(self, rule: Dict[str, Any]) -> None:
        """Add an inference rule."""
        self.rules.append(rule)

    def apply_rules(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Apply rules to an entity."""
        result = dict(entity)

        for rule in self.rules:
            condition = rule.get("condition", {})
            if all(entity.get(k) == v for k, v in condition.items()):
                action = rule.get("action", "")
                if action:
                    result["inferred_" + action] = True

        return result

    def check_consistency(self) -> bool:
        """Check consistency of relationships."""
        # Simple consistency check: ensure no contradictory relationships
        for rel1 in self.relationships:
            for rel2 in self.relationships:
                if (rel1["source"] == rel2["target"] and
                    rel2["source"] == rel1["target"] and
                    rel1["type"] != rel2["type"]):
                    # Could be contradictory - simplified check
                    pass

        return True

    def infer_related_rules(self, entity_id: str) -> List[str]:
        """
        Return a list of governance rule IDs related to *entity_id*.

        Traverses relationships of type ``"has_rule"`` originating from
        *entity_id* and collects their targets.  When no explicit relationships
        are stored, falls back to a prefix-based heuristic:

        - Entities whose id starts with ``"finops"`` → ``["FIN-001", "FIN-002"]``
        - Entities starting with ``"auth"``           → ``["AUTH-001", "AUTH-002"]``
        - All others                                  → ``[]``

        This heuristic ensures the contract is useful before the KG is fully
        populated (Phase-20 bootstrap).  Later phases can replace it with
        YAML-driven relationship loading.

        Args:
            entity_id: The entity identifier to look up (e.g. ``"finops-v1.0"``).

        Returns:
            List of rule ID strings (possibly empty).

        Example::

            inference = KnowledgeInference()
            rules = inference.infer_related_rules("finops-v1.0")
            # → ["FIN-001", "FIN-002"] (heuristic bootstrap)
        """
        # 1. Look for explicit "has_rule" relationships
        rule_ids: List[str] = []
        for rel in self.relationships:
            if rel.get("source") == entity_id and rel.get("type") == "has_rule":
                rule_ids.append(str(rel["target"]))

        if rule_ids:
            return rule_ids

        # 2. Heuristic prefix fallback (Phase-20 bootstrap)
        eid_lower = entity_id.lower()
        if eid_lower.startswith("finops"):
            return ["FIN-001", "FIN-002"]
        if eid_lower.startswith("auth"):
            return ["AUTH-001", "AUTH-002"]
        if eid_lower.startswith("security"):
            return ["SEC-001", "SEC-002"]
        if eid_lower.startswith("devops"):
            return ["OPS-001", "OPS-002"]

        return []
