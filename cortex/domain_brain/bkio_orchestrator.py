"""Business Knowledge Ingestion Orchestrator

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List
from cortex.core.orchestrator_base import OrchestratorBase, OrchestrationContext
from cortex.domain_brain.api import DomainBrainAPI, Domain, Entity
from cortex.domain_brain.models import EntityType


class DocumentFormat(str, Enum):
    """Document formats."""
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"
    YAML = "yaml"
    JSON = "json"
    CSV = "csv"


class BusinessKnowledgeIngestionOrchestrator(OrchestratorBase):
    """Orchestrator for ingesting business knowledge documents."""

    def __init__(self, context: OrchestrationContext, api: DomainBrainAPI) -> None:
        """Initialize BKIO orchestrator.
        
        Args:
            context: Orchestration context.
            api: Domain brain API instance.
        """
        super().__init__("BKIO")
        self.context = context
        self.domain_brain_api = api
        self.documents_processed = 0
        self.documents_failed = 0
        self.conflicts_detected = 0

    def initialize(self) -> None:
        """Initialize the orchestrator."""
        pass

    def shutdown(self) -> None:
        """Shutdown the orchestrator."""
        pass

    def validate_context(self) -> List[str]:
        """Validate orchestration context.
        
        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        if self.context is None:
            errors.append("Context is None")
        return errors

    def on_start(self) -> None:
        """Execute on orchestrator start."""
        self.documents_processed = 0
        self.documents_failed = 0
        self.conflicts_detected = 0

    def execute(self, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Execute orchestrator.
        
        Args:
            context: Optional execution context (unused, uses self.context).
        
        Returns:
            Execution result.
        """
        docs = self.context.parameters.get("documents", [])
        if not docs:
            raise ValueError("No documents provided")
        
        for doc in docs:
            try:
                self._process_document(doc)
                self.documents_processed += 1
            except Exception as e:
                self.documents_failed += 1
                self._log(f"Document processing failed: {str(e)}")
        
        return {
            "documents_processed": self.documents_processed,
            "documents_failed": self.documents_failed,
            "conflicts_detected": self.conflicts_detected,
        }
    
    def run(self) -> Optional[Dict[str, Any]]:
        """Run the orchestrator (alias for execute).
        
        Returns:
            Execution result.
        """
        return self.execute()

    def on_complete(self) -> None:
        """Execute on orchestrator complete."""
        pass

    def _process_document(self, doc: Dict[str, Any]) -> None:
        """Process a document.
        
        Args:
            doc: Document to process.
        """
        domain_id = doc.get("domain_id")
        if not domain_id:
            raise ValueError("Document missing domain_id")
        
        name = doc.get("name", "")
        description = doc.get("description", "")
        fmt = doc.get("format", "yaml")
        content = doc.get("content", {})
        
        # Validate format
        try:
            doc_format = DocumentFormat(fmt) if fmt in [f.value for f in DocumentFormat] else None
            if doc_format is None:
                raise ValueError(f"Unsupported document format: {fmt}")
        except (ValueError, KeyError) as e:
            raise ValueError(f"Invalid document format: {fmt}") from e
        
        # Parse document
        parsed = self._parse_document(doc, doc_format)
        
        # Get or create domain
        domain = self.domain_brain_api.query_domain(domain_id)
        if not domain:
            domain = Domain(
                domain_id=domain_id,
                name=name,
                description=description,
            )
        else:
            domain.description = description
        
        # Process entities
        entities = parsed.get("entities", [])
        for entity_data in entities:
            self._merge_entity(domain, entity_data)
        
        # Save domain
        self.domain_brain_api.upsert_domain(domain)

    def _parse_document(self, doc: Dict[str, Any], fmt: DocumentFormat) -> Dict[str, Any]:
        """Parse document by format.
        
        Args:
            doc: Document to parse.
            fmt: Document format.
        
        Returns:
            Parsed content as dictionary.
            
        Raises:
            ValueError: If format is invalid.
        """
        content = doc.get("content", {})
        
        # Validate format
        if not isinstance(fmt, DocumentFormat):
            raise ValueError(f"Invalid document format: {fmt}")
        
        if fmt == DocumentFormat.YAML or fmt == DocumentFormat.JSON:
            return content if isinstance(content, dict) else {}
        elif fmt == DocumentFormat.MARKDOWN:
            return {"content": content}
        elif fmt == DocumentFormat.CSV:
            return {"content": content}
        else:
            return content if isinstance(content, dict) else {}

    def _merge_entity(self, domain: Domain, entity_data: Dict[str, Any]) -> None:
        """Merge entity into domain.
        
        Args:
            domain: Target domain.
            entity_data: Entity data to merge.
        """
        entity_id = entity_data.get("id")
        entity_type_str = entity_data.get("type", "resource").lower()
        name = entity_data.get("name", "")
        description = entity_data.get("description", "")
        
        entity_type = self._get_entity_type(entity_type_str)
        
        entity = Entity(
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            description=description,
            source="BKIO",
        )
        
        domain.entities[entity_id] = entity

    def _get_entity_type(self, type_str: str) -> EntityType:
        """Convert type string to EntityType.
        
        Args:
            type_str: Type string.
        
        Returns:
            EntityType enum value.
        """
        # Normalize type string
        type_str = type_str.lower().strip()
        
        type_map = {
            "service": EntityType.SERVICE,
            "function": EntityType.FUNCTION,
            "class": EntityType.CLASS,
            "database": EntityType.DATABASE,
            "resource": EntityType.RESOURCE,
            "operation": EntityType.OPERATION,
            "data": EntityType.DATA,
            "domain": EntityType.DOMAIN,
        }
        return type_map.get(type_str, EntityType.RESOURCE)

    def _log(self, message: str) -> None:
        """Log a message.
        
        Args:
            message: Message to log.
        """
        pass


__all__ = ["BusinessKnowledgeIngestionOrchestrator", "DocumentFormat"]
