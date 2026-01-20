"""Business Knowledge Ingestion Orchestrator

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class BusinessKnowledgeIngestionOrchestrator:
    """BKIO orchestrator."""
    source: str
    status: str = "idle"

__all__ = ["BusinessKnowledgeIngestionOrchestrator"]
