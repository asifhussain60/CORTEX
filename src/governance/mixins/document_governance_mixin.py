"""
Document Governance Mixin for Orchestrators.

This mixin provides centralized document creation with organization enforcement,
preventing root-level document pollution per SKULL rule DOCUMENT_ORGANIZATION_ENFORCEMENT.

Example:
    >>> class MyOrchestrator(DocumentGovernanceMixin):
    ...     def __init__(self, brain_path):
    ...         self.brain_path = brain_path
    ...     
    ...     def execute(self):
    ...         doc_path = self.create_document_safely(
    ...             category="reports",
    ...             filename="my-report.md",
    ...             content="# Report\\n\\nData here."
    ...         )
"""

from pathlib import Path
from typing import List


class DocumentGovernanceMixin:
    """
    Mixin providing document creation with governance enforcement.
    
    This mixin requires the host class to have a `brain_path` attribute
    pointing to the cortex-brain directory.
    
    Valid Categories:
        - reports: Status reports, test results, validation reports
        - analysis: Code analysis, architecture analysis
        - summaries: Project summaries, progress summaries
        - investigations: Bug investigations, issue analysis
        - planning: Feature plans, ADO work items
        - conversation-captures: Imported conversations
        - implementation-guides: How-to guides, tutorials
    """
    
    VALID_CATEGORIES: List[str] = [
        "reports",
        "analysis",
        "summaries",
        "investigations",
        "planning",
        "conversation-captures",
        "implementation-guides"
    ]
    
    def create_document_safely(
        self,
        category: str,
        filename: str,
        content: str
    ) -> Path:
        """
        Create document in proper category directory with governance checks.
        
        Args:
            category: Document category from VALID_CATEGORIES
            filename: Document filename (e.g., "report.md")
            content: Document content to write
        
        Returns:
            Absolute path to created document
        
        Raises:
            ValueError: If category is invalid or root-level creation attempted
            AttributeError: If brain_path not defined on host class
        
        Example:
            >>> orchestrator = MyOrchestrator(brain_path=Path("/cortex-brain"))
            >>> doc_path = orchestrator.create_document_safely(
            ...     category="reports",
            ...     filename="test-report.md",
            ...     content="# Test Report\\n\\nResults here."
            ... )
            >>> print(doc_path)
            /cortex-brain/documents/reports/test-report.md
        """
        # Check for brain_path attribute
        if not hasattr(self, 'brain_path'):
            raise AttributeError(
                "DocumentGovernanceMixin requires 'brain_path' attribute on host class"
            )
        
        # Block root-level document creation
        if not category or category.strip() == "":
            raise ValueError(
                "BLOCKED: root-level document creation blocked by SKULL rule "
                "DOCUMENT_ORGANIZATION_ENFORCEMENT. Use a valid category from: "
                f"{', '.join(self.VALID_CATEGORIES)}"
            )
        
        # Validate category
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. Valid categories: "
                f"{', '.join(self.VALID_CATEGORIES)}"
            )
        
        # Construct path
        documents_dir = Path(self.brain_path) / "documents"
        category_dir = documents_dir / category
        
        # Create category directory if missing
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Create document
        doc_path = category_dir / filename
        doc_path.write_text(content, encoding='utf-8')
        
        return doc_path.absolute()
