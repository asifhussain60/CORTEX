"""Business Knowledge Ingestion Orchestrator

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class BusinessKnowledgeIngestionOrchestrator:
    """BKIO orchestrator."""
    source: str
    status: str = "idle"



from enum import Enum

class DocumentFormat(str, Enum):
    """Document formats."""
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"

__all__ = ["BusinessKnowledgeIngestionOrchestrator", "DocumentFormat"]
