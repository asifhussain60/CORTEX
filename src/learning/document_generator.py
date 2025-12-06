"""
Learning System Document Generator

Generates structured markdown documentation from learning events.
Supports 15 learning categories with template-based generation.

Performance target: <100ms per document
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

from src.learning.event_taxonomy import LearningEvent, EventType, EventCategory

logger = logging.getLogger(__name__)


class DocumentGenerator:
    """
    Generates markdown documentation from learning events.
    
    Features:
    - Template-based generation for 15 categories
    - Resource linking via ResourceDatabase
    - Performance optimization with template caching
    - Batch generation support
    """
    
    # Category to template mapping
    CATEGORY_TEMPLATES = {
        'concepts': 'concepts',
        'patterns': 'patterns',
        'milestones': 'milestones',
        'resources': 'resources',
        'ado_workflows': 'ado_workflows',
        'planning_strategies': 'planning_strategies',
        'workflow_context': 'workflow_context',
        'architectural_patterns': 'architectural_patterns',
        'code_quality': 'code_quality',
        'design_decisions': 'design_decisions',
        'debugging_patterns': 'debugging_patterns',
        'productivity_patterns': 'productivity_patterns',
        'operational_learnings': 'operational_learnings',
        'user_onboarding': 'user_onboarding',
        'intent_routing': 'intent_routing'
    }
    
    # Event type to category mapping
    EVENT_TO_CATEGORY = {
        EventType.PLAN_CREATED: 'planning_strategies',
        EventType.PLAN_APPROVED: 'planning_strategies',
        EventType.PLAN_ABANDONED: 'planning_strategies',
        EventType.PHASE_STARTED: 'workflow_context',
        EventType.PHASE_COMPLETED: 'milestones',
        EventType.CHECKPOINT_COMMITTED: 'milestones',
        EventType.ADO_STORY_CREATED: 'ado_workflows',
        EventType.ADO_FEATURE_CREATED: 'ado_workflows',
        EventType.ADO_WORK_ITEM_COMPLETED: 'milestones',
        EventType.ADO_ACCEPTANCE_CRITERIA_VALIDATED: 'ado_workflows',
        EventType.WORKFLOW_STARTED: 'workflow_context',
        EventType.OPERATION_ROUTED: 'intent_routing',
        EventType.WORKFLOW_COMPLETED: 'milestones',
        EventType.PLANNING_REQUEST: 'planning_strategies',
        EventType.PLAN_STRATEGY_SELECTED: 'planning_strategies',
        EventType.PLAN_VALIDATED: 'milestones',
        EventType.INTERACTIVE_PLANNING_STARTED: 'planning_strategies',
        EventType.CLARIFICATION_REQUESTED: 'workflow_context',
        EventType.REQUIREMENTS_FINALIZED: 'milestones',
    }
    
    def __init__(self, enabled: bool = True, resource_db=None):
        """
        Initialize document generator.
        
        Args:
            enabled: Whether generator is enabled
            resource_db: Optional ResourceDatabase instance
        """
        self.enabled = enabled
        self.resource_db = resource_db
        self.templates: Dict[str, Dict[str, Any]] = {}
        self._template_cache: Dict[str, str] = {}
        self.load_templates()
    
    def load_templates(self):
        """Load all templates from templates directory."""
        # Initialize templates with basic structure
        for category in self.CATEGORY_TEMPLATES.keys():
            self.templates[category] = {
                'title': f'{category.replace("_", " ").title()} Learning',
                'sections': ['overview', 'details', 'metadata', 'resources'],
                'metadata': {
                    'category': category,
                    'version': '1.0'
                }
            }
    
    def get_template(self, category: str) -> Optional[Dict[str, Any]]:
        """
        Get template for category.
        
        Args:
            category: Template category name
            
        Returns:
            Template dict or None if not found
        """
        return self.templates.get(category)
    
    def get_template_for_event(self, event: LearningEvent) -> Optional[Dict[str, Any]]:
        """
        Get template for event type.
        
        Args:
            event: Learning event
            
        Returns:
            Template dict or None if no mapping
        """
        category = self.EVENT_TO_CATEGORY.get(event.event_type)
        if category:
            return self.get_template(category)
        return None
    
    def generate_document(self, event: LearningEvent) -> str:
        """
        Generate markdown document from event.
        
        Args:
            event: Learning event to document
            
        Returns:
            Markdown document as string
        """
        start_time = time.perf_counter()
        
        template = self.get_template_for_event(event)
        if not template:
            return self._generate_default_document(event)
        
        category = self.EVENT_TO_CATEGORY.get(event.event_type, 'concepts')
        
        # Build document sections
        doc_parts = []
        
        # Title
        title = self._format_title(event, template)
        doc_parts.append(f"# {title}\n")
        
        # Metadata header
        doc_parts.append(self._format_metadata_header(event))
        doc_parts.append("\n---\n")
        
        # Overview section
        doc_parts.append("\n## Overview\n")
        doc_parts.append(self._format_overview(event))
        
        # Details section
        doc_parts.append("\n## Details\n")
        doc_parts.append(self._format_details(event))
        
        # Event metadata
        if event.metadata:
            doc_parts.append("\n## Event Metadata\n")
            doc_parts.append(self._format_event_metadata(event.metadata))
        
        # Resources section
        if self.resource_db:
            resources = self.resource_db.get_resources(category)
            if resources:
                doc_parts.append("\n## Resources\n")
                doc_parts.append(self._format_resources(resources))
        
        # Footer
        doc_parts.append("\n---\n")
        doc_parts.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        doc = ''.join(doc_parts)
        
        duration = time.perf_counter() - start_time
        logger.debug(f"Document generation took {duration*1000:.2f}ms")
        
        return doc
    
    def _generate_default_document(self, event: LearningEvent) -> str:
        """Generate basic document for unmapped event types."""
        doc_parts = [
            f"# {event.event_type.value.replace('_', ' ').title()}\n",
            f"\n**Type:** {event.event_type.value}\n",
            f"**Component:** {event.component}\n",
            f"**Timestamp:** {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n---\n",
            f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        ]
        return ''.join(doc_parts)
    
    def _format_title(self, event: LearningEvent, template: Dict[str, Any]) -> str:
        """Format document title."""
        event_name = event.event_type.value.replace('_', ' ').title()
        return f"{event_name} - Learning Document"
    
    def _format_metadata_header(self, event: LearningEvent) -> str:
        """Format metadata header section."""
        return (
            f"\n**Event:** {event.event_type.value}\n"
            f"**Component:** {event.component}\n"
            f"**Timestamp:** {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"**Category:** {self.EVENT_TO_CATEGORY.get(event.event_type, 'general')}\n"
        )
    
    def _format_overview(self, event: LearningEvent) -> str:
        """Format overview section."""
        category = self.EVENT_TO_CATEGORY.get(event.event_type, 'general')
        return (
            f"\nThis document captures learning from a **{event.event_type.value}** event "
            f"in the {event.component} component.\n"
        )
    
    def _format_details(self, event: LearningEvent) -> str:
        """Format details section."""
        details = [f"\n**Event Type:** {event.event_type.value}\n"]
        details.append(f"**Source Component:** {event.component}\n")
        details.append(f"**Milestone Event:** {'Yes' if event.is_milestone() else 'No'}\n")
        return ''.join(details)
    
    def _format_event_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format event metadata as list."""
        lines = []
        for key, value in metadata.items():
            lines.append(f"- **{key}:** {value}\n")
        return ''.join(lines)
    
    def _format_resources(self, resources: List[Dict[str, Any]]) -> str:
        """Format resources section."""
        lines = []
        for resource in resources:
            title = resource.get('title', 'Untitled')
            url = resource.get('url', '#')
            desc = resource.get('description', '')
            lines.append(f"\n### {title}\n")
            lines.append(f"**Link:** [{url}]({url})\n")
            if desc:
                lines.append(f"\n{desc}\n")
        return ''.join(lines)
    
    def generate_documents(self, events: List[LearningEvent], skip_errors: bool = False) -> List[str]:
        """
        Generate documents for multiple events.
        
        Args:
            events: List of learning events
            skip_errors: Whether to skip events that cause errors
            
        Returns:
            List of generated documents
        """
        docs = []
        for event in events:
            if event is None:
                if skip_errors:
                    continue
                raise ValueError("None event in list")
            
            try:
                doc = self.generate_document(event)
                docs.append(doc)
            except Exception as e:
                if skip_errors:
                    logger.warning(f"Failed to generate document for {event.event_type}: {e}")
                    continue
                raise
        
        return docs
    
    def save_document(self, doc: str, event: LearningEvent) -> str:
        """
        Save document to filesystem.
        
        Args:
            doc: Markdown document content
            event: Event that generated the document
            
        Returns:
            Path to saved document
        """
        output_path = self.get_document_path(event)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(doc)
        
        return str(output_path)
    
    def get_document_path(self, event: LearningEvent) -> Path:
        """
        Generate file path for document.
        
        Args:
            event: Learning event
            
        Returns:
            Path object for document
        """
        category = self.EVENT_TO_CATEGORY.get(event.event_type, 'general')
        timestamp = event.timestamp.strftime('%Y%m%d_%H%M%S')
        filename = f"{event.event_type.value}_{timestamp}.md"
        
        return Path(f"cortex-brain/documents/learning/{category}/{filename}")
    
    def document_exists(self, event: LearningEvent) -> bool:
        """
        Check if document already exists for event.
        
        Args:
            event: Learning event
            
        Returns:
            True if document exists
        """
        path = self.get_document_path(event)
        return path.exists()
