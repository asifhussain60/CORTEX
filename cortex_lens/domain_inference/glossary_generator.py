"""
Domain Glossary Generator

Extracts domain terminology, entities, relationships, and use cases from codebases.
Generates comprehensive domain glossaries with confidence scoring.

Author: CORTEX Architect
Phase: Phase 66 S3
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass, field


@dataclass
class DomainEntity:
    """Represents a domain entity in the glossary"""
    name: str
    domain: str
    description: Optional[str] = None
    attributes: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)


@dataclass
class DomainRelationship:
    """Represents a relationship between entities"""
    source: str
    target: str
    relationship_type: str
    description: Optional[str] = None


@dataclass
class DomainGlossary:
    """Glossary containing all domain knowledge"""
    domains: List[str] = field(default_factory=list)
    entities: List[DomainEntity] = field(default_factory=list)
    relationships: List[DomainRelationship] = field(default_factory=list)


class GlossaryGenerator:
    """
    Generate domain glossaries from source code.
    
    Extracts:
    - Entities (classes representing domain concepts)
    - Relationships (references between entities)
    - Verbs (domain actions from method names)
    - Lifecycle stages (entity state transitions)
    
    Confidence scoring based on:
    - Documentation presence (0.3)
    - Attribute/method count (0.3)
    - Relationship richness (0.2)
    - Naming patterns (0.2)
    """
    
    def __init__(self, storage=None, domains=None):
        """
        Initialize glossary generator.
        
        Args:
            storage: Optional GraphStorage instance for graph-based analysis
            domains: Optional list of domain dictionaries from PatternAnalyzer
        """
        self.storage = storage
        self.domains = domains or []
        self.entity_indicators = {
            "BaseModel", "Model", "Entity", "Aggregate", "ValueObject"
        }
        self.verb_patterns = re.compile(
            r"(create|update|delete|get|set|add|remove|process|validate|calculate|"
            r"execute|initialize|finalize|activate|deactivate|authenticate|authorize|"
            r"send|receive|publish|subscribe|handle|trigger)"
        )
        
    def extract_entities(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract domain entities from class definitions.
        
        Args:
            code: Python source code
            
        Returns:
            List of entity dictionaries with name, description, attributes
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        
        entities = []
        
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            
            # Check if class represents domain entity
            if not self._is_domain_entity(node):
                continue
            
            entity = {
                "name": node.name,
                "description": self._extract_docstring(node),
                "attributes": self._extract_attributes(node),
                "methods": self._extract_method_names(node)
            }
            
            entities.append(entity)
        
        return entities
    
    def detect_relationships(self, code: str) -> List[Dict[str, Any]]:
        """
        Detect relationships between entities.
        
        Looks for:
        - Foreign key references (user_id, order_id)
        - Type annotations (List[OrderItem])
        - Collection attributes
        
        Args:
            code: Python source code
            
        Returns:
            List of relationship dictionaries
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        
        relationships = []
        
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            
            source_entity = node.name
            
            # Check attributes for relationships
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    rel = self._detect_relationship_from_attribute(
                        source_entity, item
                    )
                    if rel:
                        relationships.append(rel)
        
        return relationships
    
    def extract_verbs(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract domain verbs (use cases) from method names.
        
        Args:
            code: Python source code
            
        Returns:
            List of verb dictionaries with name and description
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        
        verbs = []
        seen = set()
        
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            
            # Skip private/dunder methods
            if node.name.startswith("_"):
                continue
            
            # Check if method name matches verb pattern
            if self.verb_patterns.search(node.name):
                if node.name not in seen:
                    verb = {
                        "name": node.name,
                        "description": self._extract_docstring(node),
                        "entity": self._extract_entity_from_verb(node.name)
                    }
                    verbs.append(verb)
                    seen.add(node.name)
        
        return verbs
    
    def build_lifecycle(
        self, entity: str, transitions: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Build entity lifecycle from state transitions.
        
        Args:
            entity: Entity name
            transitions: List of {"from": "state1", "to": "state2"}
            
        Returns:
            Lifecycle dictionary with stages and transitions
        """
        stages = set()
        
        for transition in transitions:
            stages.add(transition["from"])
            stages.add(transition["to"])
        
        return {
            "entity": entity,
            "stages": sorted(list(stages)),
            "transitions": transitions
        }
    
    def generate_glossary(
        self,
        entities: List[Dict[str, Any]],
        verbs: List[Dict[str, Any]],
        rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate complete domain glossary.
        
        Args:
            entities: Extracted domain entities
            verbs: Extracted domain verbs
            rules: Extracted business rules
            
        Returns:
            Complete glossary with entities, verbs, rules, and metadata
        """
        glossary = {
            "entities": entities,
            "verbs": verbs,
            "rules": rules,
            "metadata": {
                "entity_count": len(entities),
                "verb_count": len(verbs),
                "rule_count": len(rules)
            }
        }
        
        return glossary
    
    def calculate_confidence(self, entity_signals: Dict[str, Any]) -> float:
        """
        Calculate confidence score for glossary entry.
        
        Scoring:
        - has_docstring: 0.3
        - attribute_count: 0.3 (scaled)
        - relationship_count: 0.2 (scaled)
        - has_methods: 0.2
        
        Args:
            entity_signals: Dictionary of entity characteristics
            
        Returns:
            Confidence score 0.0-1.0
        """
        score = 0.0
        
        # Documentation presence (0.3)
        if entity_signals.get("has_docstring", False):
            score += 0.3
        
        # Attribute richness (0.3)
        attr_count = entity_signals.get("attribute_count", 0)
        score += min(0.3, attr_count * 0.05)
        
        # Relationship richness (0.2)
        rel_count = entity_signals.get("relationship_count", 0)
        score += min(0.2, rel_count * 0.1)
        
        # Method presence (0.2)
        if entity_signals.get("has_methods", False):
            score += 0.2
        
        return round(score, 2)
    
    # Private helper methods
    
    def _is_domain_entity(self, node: ast.ClassDef) -> bool:
        """Check if class represents a domain entity"""
        # Check base classes
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id in self.entity_indicators:
                    return True
        
        # Check if has typed attributes (likely domain model)
        has_typed_attrs = any(
            isinstance(item, ast.AnnAssign)
            for item in node.body
        )
        
        return has_typed_attrs
    
    def _extract_docstring(self, node) -> str:
        """Extract docstring from AST node"""
        docstring = ast.get_docstring(node)
        return docstring if docstring else ""
    
    def _extract_attributes(self, node: ast.ClassDef) -> List[str]:
        """Extract attribute names from class"""
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    attributes.append(item.target.id)
        
        return attributes
    
    def _extract_method_names(self, node: ast.ClassDef) -> List[str]:
        """Extract method names from class"""
        methods = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if not item.name.startswith("_"):
                    methods.append(item.name)
        
        return methods
    
    def _detect_relationship_from_attribute(
        self, source: str, attr: ast.AnnAssign
    ) -> Optional[Dict[str, Any]]:
        """Detect relationship from attribute annotation"""
        if not isinstance(attr.target, ast.Name):
            return None
        
        attr_name = attr.target.id
        
        # Check for foreign key pattern (user_id, order_id)
        fk_match = re.match(r"(.+)_id$", attr_name)
        if fk_match:
            target_entity = fk_match.group(1).title()
            return {
                "source": source,
                "target": target_entity,
                "type": "belongs_to",
                "field": attr_name
            }
        
        # Check for collection type annotations (List[User])
        if hasattr(attr, "annotation"):
            annotation_str = ast.unparse(attr.annotation)
            list_match = re.match(r"List\[(\w+)\]", annotation_str)
            if list_match:
                target_entity = list_match.group(1)
                return {
                    "source": source,
                    "target": target_entity,
                    "type": "has_many",
                    "field": attr_name
                }
        
        return None
    
    def _extract_entity_from_verb(self, verb_name: str) -> Optional[str]:
        """Extract entity name from verb (e.g., create_user -> User)"""
        # Split on underscore and look for entity after verb
        parts = verb_name.split("_")
        
        if len(parts) > 1:
            # Take last part as potential entity
            entity = parts[-1]
            return entity.title()
        
        return None
    
    def generate(self) -> DomainGlossary:
        """
        Generate comprehensive domain glossary from graph and domains.
        
        Returns:
            DomainGlossary with domains, entities, and relationships
        
        Example:
            glossary = generator.generate()
            print(f"Found {len(glossary.domains)} domains")
            print(f"Found {len(glossary.entities)} entities")
        """
        if not self.storage or not self.domains:
            # Return empty glossary if no data
            return DomainGlossary()
        
        glossary = DomainGlossary()
        
        # Extract domain names
        glossary.domains = [d["name"] for d in self.domains]
        
        # Build entities from domains
        for domain_dict in self.domains:
            domain_name = domain_dict["name"]
            
            for entity_name in domain_dict["entities"]:
                # Query graph for entity details
                conn = self.storage._get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT node_type, properties FROM nodes WHERE name = ?
                """, (entity_name,))
                
                row = cursor.fetchone()
                if row:
                    entity = DomainEntity(
                        name=entity_name,
                        domain=domain_name,
                        description=f"{entity_name} entity in {domain_name} domain"
                    )
                    glossary.entities.append(entity)
        
        # Extract relationships from graph edges
        from cortex_lens.knowledge_graph.graph_query import GraphQuery
        query = GraphQuery(self.storage)
        
        # Get all edges to build relationships
        conn = self.storage._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                n1.name as source_name,
                e.edge_type,
                n2.name as target_name
            FROM edges e
            JOIN nodes n1 ON e.source_id = n1.id
            JOIN nodes n2 ON e.target_id = n2.id
            WHERE n1.node_type = 'Class' AND n2.node_type = 'Class'
        """)
        
        for row in cursor.fetchall():
            source_name = row["source_name"]
            target_name = row["target_name"]
            edge_type = row["edge_type"]
            
            relationship = DomainRelationship(
                source=source_name,
                target=target_name,
                relationship_type=edge_type,
                description=f"{source_name} {edge_type} {target_name}"
            )
            glossary.relationships.append(relationship)
        
        return glossary

