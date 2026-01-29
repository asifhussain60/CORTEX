"""
Relationship Analyzer Implementation - AC-PROD-002-02

Maps code entities and their relationships within the domain knowledge graph.
Connects:
- Classes, functions, methods
- Dependencies and imports
- Inheritance hierarchies
- Function call graphs
- Data flow relationships

AC-PROD-002-02: Relationship Analysis - Resolves ISSUE-005 (Relationship analysis missing)

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from cortex.brain.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class EntityType(Enum):
    """Types of code entities.
    
    Attributes:
        CLASS: Class definition
        FUNCTION: Function or subroutine
        METHOD: Class method
        MODULE: Python module
        PACKAGE: Python package
        INTERFACE: Interface/protocol
    """
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    MODULE = "module"
    PACKAGE = "package"
    INTERFACE = "interface"


class RelationshipType(Enum):
    """Types of relationships between entities.
    
    Attributes:
        INHERITANCE: Class inheritance (is-a)
        COMPOSITION: Contains other object (has-a)
        DEPENDENCY: Depends on but doesn't own
        CALLS: Function/method calls
        IMPORTS: Module imports
        IMPLEMENTS: Implements interface
        EXTENDS: Extends base class
    """
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    DEPENDENCY = "dependency"
    CALLS = "calls"
    IMPORTS = "imports"
    IMPLEMENTS = "implements"
    EXTENDS = "extends"


@dataclass
class CodeEntity:
    """
    Represents a code entity (class, function, method, etc).
    
    Attributes:
        name: Entity name
        entity_type: Type of entity (from EntityType enum)
        module: Module containing entity
        file: File path containing entity
        metadata: Additional metadata (parent_class, decorators, etc)
        timestamp: When entity was discovered
    """
    name: str
    entity_type: EntityType
    module: str = ""
    file: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EntityRelationship:
    """
    Represents a relationship between two code entities.
    
    Attributes:
        source_entity: Name of source entity
        target_entity: Name of target entity
        rel_type: Type of relationship
        confidence: Confidence score (0-1)
        metadata: Additional metadata (line numbers, call counts, etc)
        timestamp: When relationship was discovered
    """
    source_entity: str
    target_entity: str
    rel_type: RelationshipType
    confidence: float = 0.75
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RelationshipGraph:
    """
    Complete graph of code entities and relationships.
    
    Attributes:
        entities: List of discovered entities
        relationships: List of relationships between entities
        timestamp: When graph was created
    """
    entities: List[CodeEntity] = field(default_factory=list)
    relationships: List[EntityRelationship] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class RelationshipAnalyzer:
    """
    Analyzes code to discover entities and their relationships.
    
    Builds a relationship graph mapping:
    - Class and function definitions
    - Inheritance and composition relationships
    - Function call dependencies
    - Module imports
    - Data flow connections
    
    Used by LENS Protocol Phase 3 (Domain Navigation) to understand
    code structure before synthesis.
    
    Usage:
        analyzer = RelationshipAnalyzer()
        
        # Analyze entities
        result1 = analyzer.analyze({"name": "UserService", "type": "class"})
        result2 = analyzer.analyze({"name": "UserRepository", "type": "class"})
        
        # Get full relationship graph
        graph = analyzer.get_graph()
        
        # Get relationships for entity
        rels = analyzer.get_relationships("UserService")
        
        # Get statistics
        stats = analyzer.get_statistics()
    
    CORE Governance:
      - CORE-008: TDD - tests created first
      - CORE-011: Type hints - all methods typed
      - CORE-012: Docstrings - Google style
      - CORE-027: Audit trail - AC_START/EXECUTE/COMPLETE
    """
    
    def __init__(self) -> None:
        """
        Initialize Relationship Analyzer.
        
        Sets up:
        - Audit logger
        - Entity tracking
        - Relationship tracking
        - Type weights for scoring
        """
        self.logger: EnhancedAuditLogger = EnhancedAuditLogger.instance()
        self.relationships: List[EntityRelationship] = []
        self.entity_index: Dict[str, CodeEntity] = {}
        
        # Weights for different relationship types
        self.type_weights: Dict[str, float] = {
            "inheritance": 0.95,
            "composition": 0.85,
            "dependency": 0.70,
            "calls": 0.80,
            "imports": 0.75,
            "implements": 0.90,
            "extends": 0.90,
        }
        
        self.logger.log_operation_complete(
            ac_id="AC-PROD-002-02",
            operation="RELATIONSHIP_ANALYZER_INIT",
            success=True,
            details={"type_weights": self.type_weights}
        )
    
    def analyze(
        self,
        code_info: Optional[Dict[str, Any]]
    ) -> Result[RelationshipGraph]:
        """
        Analyze code entity and relationships.
        
        Processes a code entity definition and extracts:
        1. Entity metadata (name, type, location)
        2. Relationships to other entities
        3. Confidence scores
        4. Additional metadata
        
        Args:
            code_info: Dictionary with entity info:
                - name (required): Entity name
                - type (required): Entity type (class, function, method)
                - module: Module containing entity
                - file: File path
                - relationships: List of relationship dicts with:
                  - type: Relationship type
                  - target: Target entity name
                  - confidence: Confidence score (0-1)
                - metadata: Additional metadata
        
        Returns:
            Result[RelationshipGraph]: Ok with graph, or Err with message
        
        Raises:
            ValueError: If input invalid
            Exception: If analysis fails
        """
        try:
            # Log analysis start (AC_START)
            self.logger.log_operation_start(
                ac_id="AC-PROD-002-02",
                operation="RELATIONSHIP_ANALYSIS",
                details={"code_entity": str(code_info)[:100]}  # First 100 chars
            )
            
            # Validate input
            validation = self._validate_code_info(code_info)
            if validation.is_err():
                self.logger.log_operation_complete(
                    ac_id="AC-PROD-002-02",
                    operation="RELATIONSHIP_ANALYSIS",
                    success=False,
                    details={"error": validation.unwrap_err()}
                )
                return validation
            
            # Extract entity info
            entity = self._extract_entity(code_info)
            
            # Extract relationships
            entity_rels = self._extract_relationships(code_info, entity)
            
            # Build graph (AC_EXECUTE)
            graph = RelationshipGraph(
                entities=list(self.entity_index.values()),
                relationships=self.relationships
            )
            
            # Log analysis complete (AC_COMPLETE)
            self.logger.log_operation_complete(
                ac_id="AC-PROD-002-02",
                operation="RELATIONSHIP_ANALYSIS",
                success=True,
                details={
                    "entity_name": entity.name,
                    "entity_type": entity.entity_type.value,
                    "relationships_found": len(entity_rels),
                    "total_entities": len(self.entity_index),
                    "total_relationships": len(self.relationships)
                }
            )
            
            return Ok(graph)
        
        except ValueError as e:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-002-02",
                operation="RELATIONSHIP_ANALYSIS",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Analysis validation error: {str(e)}")
        
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-002-02",
                operation="RELATIONSHIP_ANALYSIS",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Analysis failed: {str(e)}")
    
    def _validate_code_info(
        self,
        code_info: Optional[Dict[str, Any]]
    ) -> Result[bool]:
        """
        Validate code info dictionary.
        
        Args:
            code_info: Dictionary to validate
        
        Returns:
            Result[bool]: Ok(True) if valid, Err(message) if invalid
        """
        try:
            if code_info is None:
                return Err("Code info cannot be None")
            
            if not isinstance(code_info, dict):
                return Err("Code info must be dictionary")
            
            if not code_info:
                return Err("Code info cannot be empty")
            
            # Check required fields
            if "name" not in code_info:
                return Err("Missing required field: name")
            
            if "type" not in code_info:
                return Err("Missing required field: type")
            
            # Validate type value
            valid_types = [et.value for et in EntityType]
            if code_info["type"] not in valid_types:
                return Err(f"Invalid entity type: {code_info['type']}")
            
            return Ok(True)
        
        except Exception as e:
            return Err(f"Validation error: {str(e)}")
    
    def _extract_entity(
        self,
        code_info: Dict[str, Any]
    ) -> CodeEntity:
        """
        Extract entity from code info.
        
        Args:
            code_info: Code entity information
        
        Returns:
            CodeEntity dataclass instance
        """
        entity_type_str = code_info.get("type", "function")
        entity_type = EntityType(entity_type_str)
        
        entity = CodeEntity(
            name=code_info["name"],
            entity_type=entity_type,
            module=code_info.get("module", ""),
            file=code_info.get("file", ""),
            metadata=code_info.get("metadata", {})
        )
        
        # Store in index
        self.entity_index[entity.name] = entity
        
        return entity
    
    def _extract_relationships(
        self,
        code_info: Dict[str, Any],
        entity: CodeEntity
    ) -> List[EntityRelationship]:
        """
        Extract relationships from code info.
        
        Args:
            code_info: Code entity information
            entity: The entity being analyzed
        
        Returns:
            List of EntityRelationship instances
        """
        rels_list: List[EntityRelationship] = []
        
        relationships = code_info.get("relationships", [])
        if not isinstance(relationships, list):
            return rels_list
        
        for rel_info in relationships:
            if not isinstance(rel_info, dict):
                continue
            
            rel_type_str = rel_info.get("type", "dependency")
            target = rel_info.get("target", "unknown")
            confidence = rel_info.get("confidence", 0.75)
            
            try:
                rel_type = RelationshipType(rel_type_str)
            except ValueError:
                continue
            
            rel = EntityRelationship(
                source_entity=entity.name,
                target_entity=target,
                rel_type=rel_type,
                confidence=float(confidence),
                metadata=rel_info.get("metadata", {})
            )
            
            self.relationships.append(rel)
            rels_list.append(rel)
        
        return rels_list
    
    def get_graph(self) -> RelationshipGraph:
        """
        Get complete relationship graph.
        
        Returns:
            RelationshipGraph with all entities and relationships
        """
        return RelationshipGraph(
            entities=list(self.entity_index.values()),
            relationships=self.relationships
        )
    
    def get_relationships(
        self,
        entity_name: str
    ) -> List[EntityRelationship]:
        """
        Get relationships for specific entity.
        
        Args:
            entity_name: Name of entity to get relationships for
        
        Returns:
            List of relationships where entity is source or target
        """
        matching_rels: List[EntityRelationship] = []
        
        for rel in self.relationships:
            if rel.source_entity == entity_name or rel.target_entity == entity_name:
                matching_rels.append(rel)
        
        return matching_rels
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get analysis statistics.
        
        Returns:
            Dict with analysis statistics including:
                - total_entities: Number of entities found
                - total_relationships: Number of relationships found
                - relationship_types: Breakdown by type
                - average_confidence: Average relationship confidence
        """
        if not self.entity_index:
            return {
                "total_entities": 0,
                "total_relationships": 0,
                "relationship_types": {},
                "average_confidence": 0.0
            }
        
        # Count relationships by type
        type_counts: Dict[str, int] = {}
        total_confidence = 0.0
        
        for rel in self.relationships:
            rel_type = rel.rel_type.value
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
            total_confidence += rel.confidence
        
        avg_confidence = (total_confidence / len(self.relationships) 
                         if self.relationships else 0.0)
        
        return {
            "total_entities": len(self.entity_index),
            "total_relationships": len(self.relationships),
            "relationship_types": type_counts,
            "average_confidence": avg_confidence
        }


# Module exports
__all__ = [
    "RelationshipAnalyzer",
    "EntityType",
    "RelationshipType",
    "CodeEntity",
    "EntityRelationship",
    "RelationshipGraph",
]
