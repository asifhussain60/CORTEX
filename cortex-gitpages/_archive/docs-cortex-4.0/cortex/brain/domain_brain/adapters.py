"""Integration adapters for Domain Brain.

Provides adapters to extract domain knowledge from multiple sources:
- AST Intelligence (function/class signatures, code structure)
- Git history (commit history, blame information, changes over time)
- Code comments (docstrings, design decisions, inline comments)
- Relationship graphs (service dependencies, call graphs)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from cortex.brain.domain_brain.models import Entity, EntityType


class IntegrationAdapter(ABC):
    """Base class for integration adapters.

    All adapters follow this interface to extract domain metadata from sources.
    """

    @abstractmethod
    def extract_entities(self) -> List[Entity]:
        """Extract entities from source.

        Returns:
            List of entities extracted from this source
        """
        pass

    @abstractmethod
    def query_source(self, query: str) -> List[Dict[str, Any]]:
        """Query source for information.

        Args:
            query: Search query

        Returns:
            List of results matching query
        """
        pass


class ASTAdapter(IntegrationAdapter):
    """Adapter for AST Intelligence source.

    Extracts domain metadata from AST Intelligence including:
    - Function signatures and return types
    - Class definitions and inheritance
    - Module structure and organization
    - Type hints and documentation
    """

    def __init__(self) -> None:
        """Initialize AST adapter."""
        self.source_name = "AST"
        self.entities_cache: Dict[str, Entity] = {}

    def extract_entities(self) -> List[Entity]:
        """Extract entities from AST Intelligence.

        Queries the AST Intelligence system (IR-001-01) to get:
        - All functions in codebase
        - All classes and their methods
        - Module organization
        - Type hints and signatures

        Returns:
            List of Entity objects extracted from AST
        """
        entities = []

        # Extract functions
        functions = self.query_source("function:*")
        for func_data in functions:
            entity = Entity(
                entity_id=func_data.get("id", ""),
                entity_type=EntityType.FUNCTION,
                name=func_data.get("name", ""),
                description=func_data.get("docstring", ""),
                source=self.source_name,
                metadata={
                    "signature": func_data.get("signature", ""),
                    "return_type": func_data.get("return_type", ""),
                    "module": func_data.get("module", ""),
                    "parameters": func_data.get("parameters", []),
                },
            )
            entities.append(entity)
            self.entities_cache[entity.entity_id] = entity

        # Extract classes
        classes = self.query_source("class:*")
        for class_data in classes:
            entity = Entity(
                entity_id=class_data.get("id", ""),
                entity_type=EntityType.CLASS,
                name=class_data.get("name", ""),
                description=class_data.get("docstring", ""),
                source=self.source_name,
                metadata={
                    "bases": class_data.get("bases", []),
                    "module": class_data.get("module", ""),
                    "methods": class_data.get("methods", []),
                    "attributes": class_data.get("attributes", []),
                },
            )
            entities.append(entity)
            self.entities_cache[entity.entity_id] = entity

        return entities

    def query_source(self, query: str) -> List[Dict[str, Any]]:
        """Query AST Intelligence for entities.

        Supported query formats:
        - "function:*" - All functions
        - "class:*" - All classes
        - "function:name" - Specific function
        - "class:name" - Specific class
        - "module:name" - Entities in module

        Args:
            query: Query string

        Returns:
            List of matching entities from AST
        """
        results = []

        # Parse query
        if query.startswith("function:"):
            func_name = query.split(":", 1)[1]
            results = self._query_functions(func_name)
        elif query.startswith("class:"):
            class_name = query.split(":", 1)[1]
            results = self._query_classes(class_name)
        elif query.startswith("module:"):
            module_name = query.split(":", 1)[1]
            results = self._query_module(module_name)

        return results

    def _query_functions(self, name_pattern: str) -> List[Dict[str, Any]]:
        """Query functions from AST."""
        # Simulated response - in real implementation would call AST Intelligence
        return []

    def _query_classes(self, name_pattern: str) -> List[Dict[str, Any]]:
        """Query classes from AST."""
        # Simulated response - in real implementation would call AST Intelligence
        return []

    def _query_module(self, module_name: str) -> List[Dict[str, Any]]:
        """Query entities in module."""
        # Simulated response - in real implementation would call AST Intelligence
        return []


class GitAdapter(IntegrationAdapter):
    """Adapter for Git history source.

    Extracts domain knowledge from Git including:
    - Commit history for entities
    - Blame information (who changed what)
    - Timeline of changes
    - Related commits and patterns
    """

    def __init__(self) -> None:
        """Initialize Git adapter."""
        self.source_name = "GIT"
        self.entities_cache: Dict[str, Entity] = {}

    def extract_entities(self) -> List[Entity]:
        """Extract entities from Git history.

        Queries Git to find:
        - Recently modified entities
        - Files changed together (suggesting relationships)
        - Historical changes to understand domain evolution
        - Most active areas of codebase

        Returns:
            List of Entity objects extracted from Git
        """
        entities = []

        # Query recent commits
        commits = self.query_source("commit:recent:100")
        for commit in commits:
            entity = Entity(
                entity_id=commit.get("hash", ""),
                entity_type=EntityType.OTHER,
                name=f"Commit {commit.get('hash', '')[:7]}",
                description=commit.get("message", ""),
                source=self.source_name,
                metadata={
                    "hash": commit.get("hash", ""),
                    "author": commit.get("author", ""),
                    "timestamp": commit.get("timestamp", ""),
                    "files_changed": commit.get("files", []),
                    "line_changes": commit.get("line_changes", {}),
                },
            )
            entities.append(entity)
            self.entities_cache[entity.entity_id] = entity

        return entities

    def query_source(self, query: str) -> List[Dict[str, Any]]:
        """Query Git for information.

        Supported query formats:
        - "commit:recent:N" - Last N commits
        - "blame:file" - Blame information for file
        - "timeline:entity" - Timeline of changes to entity
        - "history:file" - Full history of file

        Args:
            query: Query string

        Returns:
            List of results matching query
        """
        results = []

        if query.startswith("commit:recent:"):
            count = int(query.split(":", 2)[2])
            results = self._query_recent_commits(count)
        elif query.startswith("blame:"):
            file_path = query.split(":", 1)[1]
            results = self._query_blame(file_path)
        elif query.startswith("timeline:"):
            entity_id = query.split(":", 1)[1]
            results = self._query_timeline(entity_id)

        return results

    def _query_recent_commits(self, count: int) -> List[Dict[str, Any]]:
        """Query recent commits."""
        # Simulated response - in real implementation would call Git
        return []

    def _query_blame(self, file_path: str) -> List[Dict[str, Any]]:
        """Query blame information."""
        # Simulated response - in real implementation would call Git
        return []

    def _query_timeline(self, entity_id: str) -> List[Dict[str, Any]]:
        """Query timeline of changes."""
        # Simulated response - in real implementation would call Git
        return []


class CommentsAdapter(IntegrationAdapter):
    """Adapter for code comments and docstrings.

    Extracts domain knowledge from:
    - Function and class docstrings
    - Inline comments with design decisions
    - TODO and FIXME comments
    - Type hints and annotations
    """

    def __init__(self) -> None:
        """Initialize comments adapter."""
        self.source_name = "COMMENTS"
        self.entities_cache: Dict[str, Entity] = {}

    def extract_entities(self) -> List[Entity]:
        """Extract entities from code comments.

        Queries code for:
        - Documented functions and classes
        - Design decision comments
        - Known issues and TODOs
        - Architecture notes

        Returns:
            List of Entity objects extracted from comments
        """
        entities = []

        # Query all documented items
        docs = self.query_source("docstring:*")
        for doc in docs:
            entity = Entity(
                entity_id=doc.get("id", ""),
                entity_type=EntityType.FUNCTION,
                name=doc.get("name", ""),
                description=doc.get("docstring", ""),
                source=self.source_name,
                metadata={
                    "file": doc.get("file", ""),
                    "line_number": doc.get("line", 0),
                    "type": doc.get("type", ""),
                    "tags": doc.get("tags", []),
                },
            )
            entities.append(entity)
            self.entities_cache[entity.entity_id] = entity

        return entities

    def query_source(self, query: str) -> List[Dict[str, Any]]:
        """Query code comments and docstrings.

        Supported query formats:
        - "docstring:*" - All docstrings
        - "docstring:name" - Docstring for specific item
        - "comment:design" - Design decision comments
        - "todo:*" - All TODO/FIXME comments

        Args:
            query: Query string

        Returns:
            List of results matching query
        """
        results = []

        if query.startswith("docstring:"):
            name = query.split(":", 1)[1]
            results = self._query_docstrings(name)
        elif query.startswith("comment:"):
            comment_type = query.split(":", 1)[1]
            results = self._query_design_comments(comment_type)
        elif query.startswith("todo:"):
            results = self._query_todos()

        return results

    def _query_docstrings(self, name_pattern: str) -> List[Dict[str, Any]]:
        """Query docstrings."""
        # Simulated response - in real implementation would parse code
        return []

    def _query_design_comments(self, comment_type: str) -> List[Dict[str, Any]]:
        """Query design comments."""
        # Simulated response - in real implementation would parse code
        return []

    def _query_todos(self) -> List[Dict[str, Any]]:
        """Query TODO/FIXME comments."""
        # Simulated response - in real implementation would parse code
        return []


class RelationshipsAdapter(IntegrationAdapter):
    """Adapter for code relationships and dependencies.

    Extracts domain knowledge from:
    - Function call graphs
    - Service dependencies
    - Module import relationships
    - Data flow between components
    """

    def __init__(self) -> None:
        """Initialize relationships adapter."""
        self.source_name = "RELATIONSHIPS"
        self.entities_cache: Dict[str, Entity] = {}

    def extract_entities(self) -> List[Entity]:
        """Extract entities from relationship graph.

        Queries the code relationship graph to find:
        - Services and their dependencies
        - Call hierarchies and patterns
        - Circular dependencies and hotspots
        - Integration points between modules

        Returns:
            List of Entity objects extracted from relationships
        """
        entities = []

        # Query all services
        services = self.query_source("service:*")
        for service_data in services:
            entity = Entity(
                entity_id=service_data.get("id", ""),
                entity_type=EntityType.SERVICE,
                name=service_data.get("name", ""),
                description=service_data.get("description", ""),
                source=self.source_name,
                metadata={
                    "dependencies": service_data.get("dependencies", []),
                    "dependents": service_data.get("dependents", []),
                    "interfaces": service_data.get("interfaces", []),
                    "complexity": service_data.get("complexity", "medium"),
                },
            )
            entities.append(entity)
            self.entities_cache[entity.entity_id] = entity

        return entities

    def query_source(self, query: str) -> List[Dict[str, Any]]:
        """Query relationship graph for information.

        Supported query formats:
        - "service:*" - All services
        - "service:name" - Specific service
        - "depends:service" - Services that service depends on
        - "depended-by:service" - Services depending on this service
        - "path:from->to" - Dependency path between services

        Args:
            query: Query string

        Returns:
            List of results matching query
        """
        results = []

        if query.startswith("service:"):
            service_name = query.split(":", 1)[1]
            results = self._query_services(service_name)
        elif query.startswith("depends:"):
            service_name = query.split(":", 1)[1]
            results = self._query_dependencies(service_name)
        elif query.startswith("depended-by:"):
            service_name = query.split(":", 1)[1]
            results = self._query_dependents(service_name)
        elif query.startswith("path:"):
            path = query.split(":", 1)[1]
            results = self._query_path(path)

        return results

    def _query_services(self, name_pattern: str) -> List[Dict[str, Any]]:
        """Query services from relationship graph."""
        # Simulated response - in real implementation would query LENS
        return []

    def _query_dependencies(self, service_name: str) -> List[Dict[str, Any]]:
        """Query dependencies of service."""
        # Simulated response - in real implementation would query LENS
        return []

    def _query_dependents(self, service_name: str) -> List[Dict[str, Any]]:
        """Query dependents of service."""
        # Simulated response - in real implementation would query LENS
        return []

    def _query_path(self, path: str) -> List[Dict[str, Any]]:
        """Query path between services."""
        # Simulated response - in real implementation would query LENS
        return []
