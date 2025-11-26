"""
ADO Work Item Orchestrator for CORTEX

Purpose:
- Create and manage Azure DevOps work items (Stories, Features, Bugs)
- Provide structured templates for different work item types
- Generate ADO-formatted markdown summaries
- Track work completion with automatic summary generation

Integration:
- Shares planning core with PlanningOrchestrator
- Uses ADOClient for API communication
- Generates summaries for direct copy-paste to ADO

Author: Asif Hussain
Created: 2025-11-26
Version: 1.0
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class WorkItemType(Enum):
    """Azure DevOps work item types."""
    STORY = "User Story"
    FEATURE = "Feature"
    BUG = "Bug"
    TASK = "Task"
    EPIC = "Epic"


@dataclass
class WorkItemMetadata:
    """Metadata for ADO work item."""
    work_item_type: WorkItemType
    title: str
    description: str
    assigned_to: Optional[str] = None
    iteration: Optional[str] = None
    area_path: Optional[str] = None
    priority: int = 2  # 1=High, 2=Medium, 3=Low, 4=Very Low
    tags: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    related_work_items: List[str] = field(default_factory=list)
    created_date: datetime = field(default_factory=datetime.now)
    work_item_id: Optional[str] = None


@dataclass
class WorkItemSummary:
    """Summary of completed work for ADO."""
    work_item_id: str
    work_item_type: WorkItemType
    title: str
    
    # Work completed
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    tests_created: List[str] = field(default_factory=list)
    documentation_created: List[str] = field(default_factory=list)
    
    # Metrics
    code_changes_count: int = 0
    test_coverage: float = 0.0
    duration_hours: float = 0.0
    
    # Implementation details
    implementation_notes: str = ""
    technical_decisions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    known_issues: List[str] = field(default_factory=list)
    
    # Validation
    acceptance_criteria_met: List[str] = field(default_factory=list)
    test_results: str = ""
    
    timestamp: datetime = field(default_factory=datetime.now)


class ADOWorkItemOrchestrator:
    """
    Orchestrates ADO work item creation and tracking.
    
    Features:
    - Create structured work items (Story, Feature, Bug)
    - Track work progress and completion
    - Generate ADO-formatted summaries
    - Integrate with planning system
    """
    
    def __init__(self, cortex_root: str):
        """
        Initialize ADO work item orchestrator.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root)
        self.work_items_dir = self.cortex_root / "cortex-brain" / "documents" / "planning" / "ado"
        self.active_dir = self.work_items_dir / "active"
        self.completed_dir = self.work_items_dir / "completed"
        self.summaries_dir = self.cortex_root / "cortex-brain" / "documents" / "summaries" / "ado"
        
        # Ensure directories exist
        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.completed_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        
        # Import ADO client if available
        self.ado_client = self._initialize_ado_client()
    
    def _initialize_ado_client(self):
        """Initialize ADO client if configuration exists."""
        try:
            from src.orchestrators.ado_client import ADOClient
            
            # Check for config
            config_path = self.cortex_root / "cortex.config.json"
            if not config_path.exists():
                logger.info("No ADO config found, operating in offline mode")
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            ado_config = config.get("ado", {})
            if not ado_config.get("organization") or not ado_config.get("pat"):
                logger.info("Incomplete ADO config, operating in offline mode")
                return None
            
            return ADOClient(
                organization=ado_config["organization"],
                project=ado_config["project"],
                pat=ado_config["pat"]
            )
        except ImportError:
            logger.warning("ADOClient not available, operating in offline mode")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize ADO client: {e}")
            return None
    
    def create_work_item(self, 
                        work_item_type: WorkItemType,
                        title: str,
                        description: str,
                        **kwargs) -> Tuple[bool, str, WorkItemMetadata]:
        """
        Create a new ADO work item.
        
        Args:
            work_item_type: Type of work item (Story, Feature, Bug)
            title: Work item title
            description: Detailed description
            **kwargs: Additional metadata (assigned_to, iteration, priority, etc.)
        
        Returns:
            Tuple of (success, message, metadata)
        """
        try:
            # Create metadata
            metadata = WorkItemMetadata(
                work_item_type=work_item_type,
                title=title,
                description=description,
                **kwargs
            )
            
            # Generate work item ID (timestamp-based if no ADO integration)
            if not metadata.work_item_id:
                metadata.work_item_id = f"{work_item_type.value.replace(' ', '')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create work item file
            file_name = f"{metadata.work_item_id}-{self._slugify(title)}.md"
            file_path = self.active_dir / file_name
            
            content = self._generate_work_item_template(metadata)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created work item: {file_path}")
            
            return True, f"Work item created: {file_name}", metadata
            
        except Exception as e:
            logger.error(f"Failed to create work item: {e}")
            return False, f"Error creating work item: {str(e)}", None
    
    def _generate_work_item_template(self, metadata: WorkItemMetadata) -> str:
        """Generate work item template content."""
        template = f"""# {metadata.work_item_type.value}: {metadata.title}

**Work Item ID:** {metadata.work_item_id}  
**Type:** {metadata.work_item_type.value}  
**Priority:** {self._priority_label(metadata.priority)}  
**Created:** {metadata.created_date.strftime('%Y-%m-%d %H:%M')}  
**Status:** Active

---

## Description

{metadata.description}

---

## Acceptance Criteria

"""
        
        if metadata.acceptance_criteria:
            for idx, criterion in enumerate(metadata.acceptance_criteria, 1):
                template += f"{idx}. [ ] {criterion}\n"
        else:
            template += "_(Add acceptance criteria here)_\n"
        
        template += "\n---\n\n## Implementation Notes\n\n"
        template += "_(Add implementation details as you work)_\n\n"
        template += "---\n\n## Files Changed\n\n"
        template += "### Created\n- _(List files created)_\n\n"
        template += "### Modified\n- _(List files modified)_\n\n"
        template += "### Tests\n- _(List test files)_\n\n"
        template += "---\n\n## Technical Decisions\n\n"
        template += "_(Document key technical decisions made during implementation)_\n\n"
        template += "---\n\n## Related Work Items\n\n"
        
        if metadata.related_work_items:
            for work_item in metadata.related_work_items:
                template += f"- {work_item}\n"
        else:
            template += "_(No related work items)_\n"
        
        template += "\n---\n\n## Tags\n\n"
        if metadata.tags:
            template += ", ".join(f"`{tag}`" for tag in metadata.tags)
        else:
            template += "_(No tags)_"
        
        return template
    
    def generate_work_summary(self, work_item_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Generate ADO-formatted summary for completed work.
        
        Args:
            work_item_id: Work item identifier
        
        Returns:
            Tuple of (success, message, summary_markdown)
        """
        try:
            # Find work item file
            work_item_file = None
            for directory in [self.active_dir, self.completed_dir]:
                for file in directory.glob(f"{work_item_id}*.md"):
                    work_item_file = file
                    break
                if work_item_file:
                    break
            
            if not work_item_file:
                return False, f"Work item not found: {work_item_id}", None
            
            # Parse work item file
            summary = self._parse_work_item_for_summary(work_item_file)
            
            # Generate ADO markdown
            ado_markdown = self._generate_ado_summary(summary)
            
            # Save summary
            summary_file = self.summaries_dir / f"SUMMARY-{work_item_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(ado_markdown)
            
            logger.info(f"Generated summary: {summary_file}")
            
            return True, f"Summary generated: {summary_file.name}", ado_markdown
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return False, f"Error generating summary: {str(e)}", None
    
    def _parse_work_item_for_summary(self, file_path: Path) -> WorkItemSummary:
        """Parse work item file and extract summary data."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract work item ID from filename
        work_item_id = file_path.stem.split('-')[0]
        
        # Parse sections
        summary = WorkItemSummary(
            work_item_id=work_item_id,
            work_item_type=WorkItemType.STORY,  # Default, should be parsed
            title=self._extract_title(content)
        )
        
        # Extract files
        summary.files_created = self._extract_list_items(content, "### Created")
        summary.files_modified = self._extract_list_items(content, "### Modified")
        summary.tests_created = self._extract_list_items(content, "### Tests")
        
        # Extract notes
        summary.implementation_notes = self._extract_section(content, "## Implementation Notes")
        summary.technical_decisions = self._extract_list_items(content, "## Technical Decisions")
        
        # Extract acceptance criteria
        summary.acceptance_criteria_met = self._extract_checked_items(content, "## Acceptance Criteria")
        
        return summary
    
    def _generate_ado_summary(self, summary: WorkItemSummary) -> str:
        """Generate ADO-formatted markdown summary."""
        ado_summary = f"""# Work Summary - {summary.work_item_id}

**Work Item:** {summary.work_item_id}  
**Type:** {summary.work_item_type.value}  
**Title:** {summary.title}  
**Completed:** {summary.timestamp.strftime('%Y-%m-%d %H:%M')}

---

## Summary of Work Completed

### Files Created ({len(summary.files_created)})
"""
        
        if summary.files_created:
            for file in summary.files_created:
                ado_summary += f"- `{file}`\n"
        else:
            ado_summary += "_No files created_\n"
        
        ado_summary += f"\n### Files Modified ({len(summary.files_modified)})\n"
        
        if summary.files_modified:
            for file in summary.files_modified:
                ado_summary += f"- `{file}`\n"
        else:
            ado_summary += "_No files modified_\n"
        
        ado_summary += f"\n### Tests Created ({len(summary.tests_created)})\n"
        
        if summary.tests_created:
            for test in summary.tests_created:
                ado_summary += f"- `{test}`\n"
        else:
            ado_summary += "_No tests created_\n"
        
        ado_summary += "\n---\n\n## Implementation Details\n\n"
        ado_summary += summary.implementation_notes if summary.implementation_notes else "_No implementation notes_"
        
        ado_summary += "\n\n---\n\n## Technical Decisions\n\n"
        
        if summary.technical_decisions:
            for decision in summary.technical_decisions:
                ado_summary += f"- {decision}\n"
        else:
            ado_summary += "_No technical decisions documented_\n"
        
        ado_summary += "\n---\n\n## Acceptance Criteria Validation\n\n"
        
        if summary.acceptance_criteria_met:
            for criterion in summary.acceptance_criteria_met:
                ado_summary += f"- ✅ {criterion}\n"
        else:
            ado_summary += "_No acceptance criteria documented_\n"
        
        ado_summary += "\n---\n\n## Copy-Paste Instructions\n\n"
        ado_summary += "1. Open your ADO work item\n"
        ado_summary += "2. Navigate to the Description or Comments section\n"
        ado_summary += "3. Copy the content above (from 'Summary of Work Completed' to 'Acceptance Criteria Validation')\n"
        ado_summary += "4. Paste into ADO work item\n"
        ado_summary += "5. Update work item status to 'Done' or 'Resolved'\n"
        
        return ado_summary
    
    # Utility methods
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text[:50]  # Limit length
    
    def _priority_label(self, priority: int) -> str:
        """Convert priority number to label."""
        labels = {1: "High", 2: "Medium", 3: "Low", 4: "Very Low"}
        return labels.get(priority, "Medium")
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content."""
        import re
        match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        return match.group(1) if match else "Unknown"
    
    def _extract_section(self, content: str, header: str) -> str:
        """Extract content from a markdown section."""
        import re
        pattern = rf'{re.escape(header)}\s*\n(.*?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            text = match.group(1).strip()
            # Remove placeholder text
            text = re.sub(r'_\([^)]+\)_', '', text).strip()
            return text
        return ""
    
    def _extract_list_items(self, content: str, header: str) -> List[str]:
        """Extract list items from a section."""
        section = self._extract_section(content, header)
        if not section:
            return []
        
        import re
        items = re.findall(r'^[-*]\s+`?([^`\n]+)`?', section, re.MULTILINE)
        return [item.strip() for item in items if item.strip() and not item.startswith('_')]
    
    def _extract_checked_items(self, content: str, header: str) -> List[str]:
        """Extract checked checkbox items from a section."""
        section = self._extract_section(content, header)
        if not section:
            return []
        
        import re
        items = re.findall(r'^\d+\.\s+\[x\]\s+(.+)$', section, re.MULTILINE | re.IGNORECASE)
        return [item.strip() for item in items]


def create_user_story(title: str, description: str, cortex_root: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to create a user story.
    
    Args:
        title: Story title
        description: Story description
        cortex_root: Path to CORTEX root
        **kwargs: Additional metadata
    
    Returns:
        Result dictionary with success status and details
    """
    orchestrator = ADOWorkItemOrchestrator(cortex_root)
    success, message, metadata = orchestrator.create_work_item(
        WorkItemType.STORY,
        title,
        description,
        **kwargs
    )
    
    return {
        "success": success,
        "message": message,
        "metadata": metadata,
        "work_item_id": metadata.work_item_id if metadata else None
    }


def create_feature(title: str, description: str, cortex_root: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to create a feature.
    
    Args:
        title: Feature title
        description: Feature description
        cortex_root: Path to CORTEX root
        **kwargs: Additional metadata
    
    Returns:
        Result dictionary with success status and details
    """
    orchestrator = ADOWorkItemOrchestrator(cortex_root)
    success, message, metadata = orchestrator.create_work_item(
        WorkItemType.FEATURE,
        title,
        description,
        **kwargs
    )
    
    return {
        "success": success,
        "message": message,
        "metadata": metadata,
        "work_item_id": metadata.work_item_id if metadata else None
    }


def generate_summary(work_item_id: str, cortex_root: str) -> Dict[str, Any]:
    """
    Generate ADO summary for a work item.
    
    Args:
        work_item_id: Work item identifier
        cortex_root: Path to CORTEX root
    
    Returns:
        Result dictionary with success status and summary
    """
    orchestrator = ADOWorkItemOrchestrator(cortex_root)
    success, message, summary = orchestrator.generate_work_summary(work_item_id)
    
    return {
        "success": success,
        "message": message,
        "summary": summary
    }
