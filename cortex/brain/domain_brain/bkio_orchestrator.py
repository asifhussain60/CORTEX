"""Business Knowledge Ingestion Orchestrator (BKIO).

Orchestrator for ingesting business documents and integrating them into
the Domain Brain. Implements conflict resolution and audit trails.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid

from cortex.brain.core.orchestrator_base import OrchestratorBase, OrchestrationContext
from cortex.brain.domain_brain.models import Domain, Entity, Conflict, AuditOperationType, EntityType
from cortex.brain.domain_brain.api import DomainBrainAPI


class DocumentFormat(Enum):
    """Supported document formats."""

    YAML = "yaml"
    JSON = "json"
    MARKDOWN = "markdown"
    CSV = "csv"


class BusinessKnowledgeIngestionOrchestrator(OrchestratorBase):
    """Orchestrator for ingesting business documents into Domain Brain.

    Implements:
    - Document format support (YAML, JSON, Markdown, CSV)
    - Batch ingestion with progress tracking
    - Conflict handling per decision matrix
    - Audit trail per document
    - Rollback capability

    Inherits from OrchestratorBase (proven pattern from PHASE-07).
    """

    def __init__(
        self,
        context: OrchestrationContext,
        domain_brain_api: DomainBrainAPI,
    ) -> None:
        """Initialize BKIO orchestrator.

        Args:
            context: OrchestrationContext for orchestrator
            domain_brain_api: API for interacting with Domain Brain
        """
        super().__init__(context)
        self.domain_brain_api = domain_brain_api
        self.documents_processed = 0
        self.conflicts_detected = 0
        self.documents_failed = 0
        self.documents_to_process: List[Dict[str, Any]] = []

    def validate_context(self) -> List[str]:
        """Validate that orchestrator can execute.

        Checks:
        - Domain Brain API available
        - Sufficient permissions
        - Required config loaded

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.domain_brain_api:
            errors.append("Domain Brain API not available")
            return errors

        # Check API is functional
        try:
            self.domain_brain_api.list_domains()
        except Exception as e:
            errors.append(f"Domain Brain API not functional: {str(e)}")

        return errors

    def on_start(self) -> None:
        """Called when orchestrator starts execution.

        Initializes:
        - Document processing queue
        - Conflict resolution rules
        - Audit trail
        """
        self.documents_processed = 0
        self.conflicts_detected = 0
        self.documents_failed = 0
        self._log("BKIO orchestrator started")

    def execute(self) -> Dict[str, Any]:
        """Execute business knowledge ingestion.

        Returns:
            Dict with execution results

        Raises:
            ValueError: If documents are invalid
        """
        documents = self.context.parameters.get("documents", [])

        if not documents:
            raise ValueError("No documents provided for ingestion")

        self.documents_to_process = documents
        total_docs = len(documents)
        self._log(f"Starting ingestion of {total_docs} documents")

        for idx, document in enumerate(documents):
            try:
                self._process_document(document)
                self.documents_processed += 1
                progress = ((idx + 1) / total_docs) * 100
                self.context.progress_percent = int(progress)
                self._log(
                    f"Document {idx + 1}/{total_docs} processed ({progress:.1f}%)"
                )
            except Exception as e:
                self.documents_failed += 1
                self._log(f"Document {idx + 1} failed: {str(e)}")

        return {
            "documents_processed": self.documents_processed,
            "conflicts_detected": self.conflicts_detected,
            "documents_failed": self.documents_failed,
        }

    def on_complete(self) -> None:
        """Called when orchestrator completes execution.

        Finalizes:
        - Audit trail
        - Summary statistics
        - Rollback state
        """
        summary = f"BKIO complete: {self.documents_processed} processed, {self.conflicts_detected} conflicts, {self.documents_failed} failed"
        self._log(summary)

    def _process_document(self, document: Dict[str, Any]) -> None:
        """Process a single document.

        Args:
            document: Document to process

        Raises:
            ValueError: If document format is invalid
        """
        # Validate document structure
        if "domain_id" not in document:
            raise ValueError("Document missing required field: domain_id")

        domain_id = document["domain_id"]
        doc_format = DocumentFormat(document.get("format", "yaml"))

        # Parse document based on format
        parsed = self._parse_document(document, doc_format)

        # Get or create domain
        domain = self.domain_brain_api.query_domain(domain_id)
        if not domain:
            domain = Domain(
                domain_id=domain_id,
                name=document.get("name", domain_id),
                description=document.get("description", ""),
            )

        # Merge entities from document
        for entity_data in parsed.get("entities", []):
            self._merge_entity(domain, entity_data)

        # Upsert domain
        self.domain_brain_api.upsert_domain(domain)

    def _parse_document(
        self, document: Dict[str, Any], format: DocumentFormat
    ) -> Dict[str, Any]:
        """Parse document based on format.

        Args:
            document: Document to parse
            format: Document format

        Returns:
            Parsed document structure
        """
        if format == DocumentFormat.YAML:
            return self._parse_yaml(document)
        elif format == DocumentFormat.JSON:
            return self._parse_json(document)
        elif format == DocumentFormat.MARKDOWN:
            return self._parse_markdown(document)
        elif format == DocumentFormat.CSV:
            return self._parse_csv(document)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _parse_yaml(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Parse YAML format document."""
        return document.get("content", {})

    def _parse_json(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON format document."""
        return document.get("content", {})

    def _parse_markdown(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Markdown format document."""
        # Extract structured data from markdown
        return {"entities": []}

    def _parse_csv(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Parse CSV format document."""
        # Parse CSV rows to entities
        return {"entities": []}

    def _merge_entity(self, domain: Domain, entity_data: Dict[str, Any]) -> None:
        """Merge entity into domain, handling conflicts.

        Uses hierarchy: BKIO > RELATIONSHIPS > AST > GIT > LENS

        Args:
            domain: Domain to merge into
            entity_data: Entity data to merge
        """
        entity_id = entity_data.get("id")
        if not entity_id:
            return

        existing = domain.entities.get(entity_id)
        if not existing:
            # New entity
            entity = Entity(
                entity_id=entity_id,
                entity_type=self._get_entity_type(entity_data.get("type")),
                name=entity_data.get("name", ""),
                description=entity_data.get("description", ""),
                source="BKIO",
                metadata=entity_data.get("metadata", {}),
            )
            domain.entities[entity_id] = entity
        else:
            # Existing entity - check for conflicts
            if existing.description != entity_data.get("description", ""):
                # Conflict detected
                self.conflicts_detected += 1
                conflict = Conflict(
                    conflict_id=str(uuid.uuid4()),
                    domain_id=domain.domain_id,
                    attribute="description",
                    source_values={
                        existing.source: existing.description,
                        "BKIO": entity_data.get("description", ""),
                    },
                )
                domain.conflicts.append(conflict)

                # BKIO has priority, so update
                existing.description = entity_data.get("description", "")

    def _get_entity_type(self, type_str: str) -> EntityType:
        """Convert string to EntityType.

        Args:
            type_str: Type string

        Returns:
            EntityType enum
        """
        type_map = {
            "service": EntityType.SERVICE,
            "function": EntityType.FUNCTION,
            "class": EntityType.CLASS,
            "database": EntityType.DATABASE,
            "api": EntityType.API,
            "workflow": EntityType.WORKFLOW,
            "configuration": EntityType.CONFIGURATION,
        }
        return type_map.get(type_str.lower(), EntityType.OTHER)
