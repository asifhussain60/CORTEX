"""SensoryInputOrchestrator - Phase 11 CMS-1 Implementation.

Core sensory input processing with <5s webhook latency.
Implements event deduplication (CORE-041) and dependency extraction.
"""

import hashlib
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from cortex.sensory.dependency_synaptic_extractor import (
    DependencySynapticExtractorFactory,
)
from cortex.sensory.git_sensory_receptor import (
    DependencyFileDetector,
    EventType,
    GitPlatform,
    GitWebhookParser,
    GitWebhookValidator,
    SensoryEvent,
)
from cortex.sensory.synaptic_network import (
    ComplianceSynapticNetwork,
    DependencySynapticNetwork,
    InMemorySynapticNetwork,
    ServiceTopologySynapticNetwork,
    SynapticNode,
)

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of event processing.

    Attributes:
        event_id: Processed event ID
        status: Processing status (success, duplicate, error)
        processing_time_ms: Time to process in milliseconds
        dependencies_found: Number of dependencies extracted
        errors: List of errors if any
        metadata: Additional metadata
    """
    event_id: str
    status: str
    processing_time_ms: float
    dependencies_found: int = 0
    errors: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Post-init processing."""
        if self.errors is None:
            self.errors = []
        if self.metadata is None:
            self.metadata = {}


class EventDeduplicationStore:
    """Stores processed events for deduplication.

    Implements CORE-041: Event Idempotency
    - Events deduplicated by event_id + timestamp
    - TTL-based cleanup of old events (24 hours)
    """

    def __init__(self, ttl_hours: int = 24):
        """Initialize deduplication store.

        Args:
            ttl_hours: Time-to-live for stored events
        """
        self.ttl_hours = ttl_hours
        self.events: Dict[str, Tuple[str, datetime]] = {}  # event_id -> (event_hash, timestamp)

    def get_event_hash(self, event: SensoryEvent) -> str:
        """Generate deterministic hash for event.

        Args:
            event: Sensory event

        Returns:
            Hash string
        """
        # Create content to hash: event_id + repository + branch + data snapshot
        content = f"{event.event_id}_{event.repository}_{event.branch}_{event.data.get('after', '')}"
        return hashlib.sha256(content.encode()).hexdigest()

    def is_duplicate(self, event: SensoryEvent) -> bool:
        """Check if event is duplicate.

        Args:
            event: Sensory event

        Returns:
            True if duplicate
        """
        self.cleanup_expired()

        event_hash = self.get_event_hash(event)

        if event.event_id in self.events:
            stored_hash, stored_time = self.events[event.event_id]
            return stored_hash == event_hash

        return False

    def record_event(self, event: SensoryEvent) -> None:
        """Record processed event.

        Args:
            event: Sensory event
        """
        event_hash = self.get_event_hash(event)
        self.events[event.event_id] = (event_hash, datetime.utcnow())

    def cleanup_expired(self) -> None:
        """Remove expired events from store."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.ttl_hours)
        expired_ids = [
            event_id
            for event_id, (_, timestamp) in self.events.items()
            if timestamp < cutoff_time
        ]

        for event_id in expired_ids:
            del self.events[event_id]

    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics.

        Returns:
            Statistics dictionary
        """
        self.cleanup_expired()
        return {
            "stored_events": len(self.events),
            "ttl_hours": self.ttl_hours,
        }


class SensoryInputOrchestrator:
    """Phase 11 CMS-1: Sensory Input Processing.

    Processes incoming Git webhook events with:
    - <5s latency per webhook
    - Event deduplication (CORE-041)
    - Dependency extraction from modified files
    - Graph storage via synaptic networks

    AC-CMS-001-01: Process Git webhook events from GitHub, GitLab, Bitbucket
    AC-CMS-001-02: Extract dependencies from dependency files
    AC-CMS-001-03: Deduplicate events by event_id + timestamp
    AC-CMS-001-04: Maintain processing latency <5 seconds per webhook
    """

    def __init__(self):
        """Initialize SensoryInputOrchestrator."""
        self.dedup_store = EventDeduplicationStore()
        self.dependency_network = DependencySynapticNetwork()
        self.compliance_network = ComplianceSynapticNetwork()
        self.service_network = ServiceTopologySynapticNetwork()

        self.webhook_validator = GitWebhookValidator()
        self.webhook_parser = GitWebhookParser()
        self.dependency_detector = DependencyFileDetector()

        # Metrics
        self.total_events_processed = 0
        self.total_duplicates_detected = 0
        self.total_dependencies_extracted = 0
        self.total_errors = 0

    def process_webhook(
        self,
        event: SensoryEvent,
        signature: Optional[str] = None,
        secret: Optional[str] = None
    ) -> ProcessingResult:
        """Process incoming webhook event.

        Phase 11 AC-CMS-001-01: Process Git webhook events

        Args:
            event: Sensory event from webhook
            signature: Webhook signature for validation
            secret: Webhook secret for validation

        Returns:
            ProcessingResult with status and metrics
        """
        start_time = datetime.utcnow()

        try:
            # Validate event structure
            event.validate()

            # Check for duplicate
            if self.dedup_store.is_duplicate(event):
                self.total_duplicates_detected += 1
                elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000

                return ProcessingResult(
                    event_id=event.event_id,
                    status="duplicate",
                    processing_time_ms=elapsed,
                    metadata={
                        "reason": "Event already processed",
                        "dedup_store_size": len(self.dedup_store.events),
                    }
                )

            # Record event
            self.dedup_store.record_event(event)

            # Process dependencies if push event
            dependencies = []
            if event.event_type == EventType.GIT_PUSH:
                dependencies = self._extract_dependencies_from_push(event)

            self.total_events_processed += 1
            self.total_dependencies_extracted += len(dependencies)

            elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000

            return ProcessingResult(
                event_id=event.event_id,
                status="success",
                processing_time_ms=elapsed,
                dependencies_found=len(dependencies),
                metadata={
                    "platform": event.source.value,
                    "repository": event.repository,
                    "branch": event.branch,
                    "dependencies": [
                        {"package": d.package, "version": d.version}
                        for d in dependencies
                    ],
                }
            )

        except Exception as e:
            self.total_errors += 1
            elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000

            logger.error(f"Error processing webhook: {e}")

            return ProcessingResult(
                event_id=event.event_id,
                status="error",
                processing_time_ms=elapsed,
                errors=[str(e)],
            )

    def _extract_dependencies_from_push(self, event: SensoryEvent) -> List:
        """Extract dependencies from files in push event.

        Args:
            event: Push event

        Returns:
            List of extracted dependencies
        """
        dependencies = []

        # Extract modified files from event data
        files = self._get_modified_files(event)

        for filename, file_content in files.items():
            # Check if dependency file
            if not self.dependency_detector.is_dependency_file(filename):
                continue

            ecosystem = self.dependency_detector.get_ecosystem(filename)
            if not ecosystem:
                continue

            # Extract dependencies
            extracted = DependencySynapticExtractorFactory.extract_dependencies(
                ecosystem,
                file_content
            )

            # Add to dependency network
            for dep in extracted:
                package_added = self.dependency_network.add_package(
                    dep.package,
                    dep.version,
                    ecosystem.value
                )

                if package_added:
                    dependencies.append(dep)

            logger.info(
                f"Extracted {len(extracted)} dependencies from {filename}"
            )

        return dependencies

    def _get_modified_files(self, event: SensoryEvent) -> Dict[str, str]:
        """Extract modified files from push event.

        Args:
            event: Push event

        Returns:
            Dictionary of {filename: file_content}
        """
        files = {}

        # This is a simplified implementation
        # In production, would fetch actual file contents from Git
        data = event.data

        if event.source == GitPlatform.GITHUB:
            for commit in data.get("commits", []):
                for mod_file in commit.get("modified", []):
                    files[mod_file] = f"# {mod_file} content"

        elif event.source == GitPlatform.GITLAB:
            for commit in data.get("commits", []):
                for mod_file in commit.get("modified", []):
                    files[mod_file] = f"# {mod_file} content"

        elif event.source == GitPlatform.BITBUCKET:
            # Bitbucket format differs
            pass

        return files

    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics.

        AC-CMS-001-04: Report processing latency and metrics

        Returns:
            Metrics dictionary
        """
        return {
            "total_events_processed": self.total_events_processed,
            "total_duplicates_detected": self.total_duplicates_detected,
            "total_dependencies_extracted": self.total_dependencies_extracted,
            "total_errors": self.total_errors,
            "dedup_store_stats": self.dedup_store.get_stats(),
            "dependency_network_nodes": self.dependency_network.backend.get_node_count(),
            "dependency_network_connections": self.dependency_network.backend.get_connection_count(),
        }

    def get_dependency_graph(self, package_name: str, version: str, ecosystem: str) -> Dict[str, Any]:
        """Get dependency graph for package.

        Args:
            package_name: Package name
            version: Package version
            ecosystem: Ecosystem

        Returns:
            Graph structure with nodes and edges
        """
        direct_deps = self.dependency_network.get_dependencies(
            package_name,
            version,
            ecosystem
        )

        return {
            "root": f"{ecosystem}:{package_name}:{version}",
            "direct_dependencies": [
                {
                    "id": dep.node_id,
                    "label": dep.label,
                    "properties": dep.properties,
                }
                for dep in direct_deps
                if dep
            ],
            "total_direct": len([d for d in direct_deps if d]),
        }


if __name__ == "__main__":
    logger.info("SensoryInputOrchestrator - Phase 11 CMS-1")
