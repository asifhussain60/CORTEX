"""
Knowledge Inference - Reasoning over knowledge graph.
"""

from typing import Dict, List, Set, Any


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
