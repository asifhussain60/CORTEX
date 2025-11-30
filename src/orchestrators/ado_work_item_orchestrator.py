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
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum

# Import git history validator for context enrichment
try:
    from src.validators.git_history_validator import GitHistoryValidator, ValidationResult
except ImportError:
    GitHistoryValidator = None
    ValidationResult = None
    logging.warning("GitHistoryValidator not available - git context enrichment disabled")

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
    updated_date: datetime = field(default_factory=datetime.now)
    work_item_id: Optional[str] = None
    status: str = "active"  # active, completed, blocked, cancelled
    
    # Git History Context (added for integration with GitHistoryValidator)
    git_context: Optional[Dict[str, Any]] = None
    quality_score: float = 0.0  # 0-100% from git history validation
    high_risk_files: List[str] = field(default_factory=list)
    related_commits: List[str] = field(default_factory=list)
    contributors: List[str] = field(default_factory=list)
    sme_suggestions: List[str] = field(default_factory=list)  # Subject matter expert suggestions


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


@dataclass
class ClarificationChoice:
    """Represents a single choice in a clarification question."""
    letter: str           # "1a", "2c", "3b"
    text: str            # Choice description
    category: str        # "scope", "technical", "ui_ux", "quality"


@dataclass
class ClarificationRound:
    """Represents one round of clarification conversation."""
    round_number: int
    question: str
    category: str        # "scope", "technical", "ui_ux", "quality"
    choices: List[ClarificationChoice]
    user_response: Optional[str] = None
    selected_choices: List[str] = field(default_factory=list)  # ["1a", "2c"]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConversationState:
    """Manages state for multi-round clarification conversation."""
    work_item_id: str
    rounds: List[ClarificationRound] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)  # Accumulated clarifications
    is_complete: bool = False
    total_ambiguities_detected: int = 0
    total_ambiguities_resolved: int = 0
    current_round: int = 1
    max_rounds: int = 4


@dataclass
class ChecklistItem:
    """Represents a single checklist item in DoR/DoD validation."""
    id: str
    text: str
    passed: bool
    points_earned: int
    points_possible: int
    optional: bool = False
    manual: bool = False
    validation_message: str = ""


@dataclass
class CategoryScore:
    """Represents score for one category in DoR/DoD validation."""
    category: str
    score: float  # 0-100
    weight: float  # Decimal (0.30 = 30%)
    items: List[ChecklistItem]
    weighted_score: float  # score * weight


@dataclass
class ValidationResult:
    """Result of DoR or DoD validation."""
    validation_type: str  # "dor" or "dod"
    overall_score: float  # 0-100
    passed: bool  # True if score >= threshold
    threshold: float  # Minimum passing score
    categories: List[CategoryScore]
    timestamp: datetime = field(default_factory=datetime.now)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ApprovalRecord:
    """Record of work item approval."""
    work_item_id: str
    approval_stage: str
    dor_score: Optional[float] = None
    dod_score: Optional[float] = None
    approved: bool = False
    approver: str = "CORTEX (auto)"
    approval_date: datetime = field(default_factory=datetime.now)
    comments: str = ""
    quality_gates_passed: List[str] = field(default_factory=list)


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
        self.blocked_dir = self.work_items_dir / "blocked"
        self.summaries_dir = self.cortex_root / "cortex-brain" / "documents" / "summaries" / "ado"
        
        # Ensure directories exist
        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.completed_dir.mkdir(parents=True, exist_ok=True)
        self.blocked_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        
        # Import ADO client if available
        self.ado_client = self._initialize_ado_client()
        
        # Initialize git history validator
        self.git_validator = self._initialize_git_validator()
    
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
    
    def _initialize_git_validator(self):
        """Initialize git history validator for context enrichment."""
        if GitHistoryValidator is None:
            logger.warning("GitHistoryValidator not available, git context enrichment disabled")
            return None
        
        try:
            # Use cortex_root as repository path
            # Config will be loaded from cortex-brain/config/git-history-rules.yaml
            validator = GitHistoryValidator(
                repo_path=self.cortex_root,
                config_path=self.cortex_root / "cortex-brain" / "config" / "git-history-rules.yaml"
            )
            logger.info("GitHistoryValidator initialized successfully")
            return validator
        except Exception as e:
            logger.error(f"Failed to initialize GitHistoryValidator: {e}")
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
            
            # Enrich with git history context (Phase 1 integration)
            if self.git_validator:
                metadata = self._enrich_with_git_context(metadata)
            
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
            
            # Generate YAML file (Phase 2 - YAML Tracking)
            yaml_file_name = f"{metadata.work_item_id}-{self._slugify(title)}.yaml"
            yaml_file_path = self.active_dir / yaml_file_name
            yaml_success = self._generate_yaml_file(metadata, yaml_file_path)
            
            if yaml_success:
                logger.info(f"Created YAML file: {yaml_file_path}")
            
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
        
        # Add git history context section (Phase 1 integration)
        if metadata.git_context or metadata.quality_score > 0:
            template += "\n---\n\n## Git History Context\n\n"
            
            # Quality score
            if metadata.quality_score > 0:
                quality_label = "Excellent" if metadata.quality_score >= 90 else \
                               "Good" if metadata.quality_score >= 70 else \
                               "Adequate" if metadata.quality_score >= 50 else "Weak"
                template += f"**Quality Score:** {metadata.quality_score:.1f}% ({quality_label})\n\n"
            
            # High-risk files warning
            if metadata.high_risk_files:
                template += "**⚠️ High-Risk Files Detected:**\n"
                for file in metadata.high_risk_files:
                    template += f"- `{file}` - Requires extra attention (high churn/hotfix history)\n"
                template += "\n"
            
            # SME suggestions
            if metadata.sme_suggestions:
                template += "**💡 Subject Matter Expert Suggestions:**\n"
                for sme in metadata.sme_suggestions:
                    template += f"- {sme} (top contributor to related files)\n"
                template += "\n"
            
            # Contributors
            if metadata.contributors:
                template += "**Contributors to Related Files:**\n"
                for contributor in metadata.contributors[:5]:  # Top 5
                    if isinstance(contributor, dict):
                        template += f"- {contributor.get('name', 'Unknown')} ({contributor.get('commits', 0)} commits)\n"
                    else:
                        template += f"- {contributor}\n"
                template += "\n"
            
            # Related commits
            if metadata.related_commits:
                template += "**Related Commits:**\n"
                for commit in metadata.related_commits[:5]:  # Top 5
                    template += f"- {commit}\n"
                template += "\n"
        
        template += "\n---\n\n## Tags\n\n"
        if metadata.tags:
            template += ", ".join(f"`{tag}`" for tag in metadata.tags)
        else:
            template += "_(No tags)_"
        
        return template
    
    def _generate_yaml_file(self, metadata: WorkItemMetadata, file_path: Path) -> bool:
        """
        Generate YAML file for work item tracking (Phase 2).
        
        Args:
            metadata: Work item metadata
            file_path: Path to save YAML file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert metadata to dict
            data = asdict(metadata)
            
            # Handle datetime serialization (convert to ISO 8601 strings)
            data['created_date'] = metadata.created_date.isoformat()
            data['updated_date'] = metadata.updated_date.isoformat()
            
            # Handle enum (convert to string value)
            data['work_item_type'] = metadata.work_item_type.value
            
            # Add schema metadata
            data['schema_version'] = '1.0'
            
            # Write YAML with proper formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            logger.info(f"Generated YAML file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"YAML generation failed: {e}")
            return False
    
    def resume_work_item(self, work_item_id: str) -> Tuple[bool, str, Optional[WorkItemMetadata]]:
        """
        Resume work on existing work item by loading from YAML (Phase 2).
        
        Args:
            work_item_id: Work item identifier
        
        Returns:
            Tuple of (success, message, metadata)
        """
        try:
            # Find YAML file in active or blocked directories
            yaml_file = None
            for directory in [self.active_dir, self.blocked_dir]:
                for file in directory.glob(f"{work_item_id}*.yaml"):
                    yaml_file = file
                    break
                if yaml_file:
                    break
            
            if not yaml_file:
                return False, f"Work item not found: {work_item_id}", None
            
            # Load YAML file
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Reconstruct WorkItemMetadata
            # Handle datetime parsing (ISO 8601 → datetime objects)
            from dateutil import parser as date_parser
            data['created_date'] = date_parser.isoparse(data['created_date'])
            data['updated_date'] = date_parser.isoparse(data['updated_date'])
            
            # Handle enum parsing (string → WorkItemType)
            work_item_type_str = data['work_item_type']
            # Find enum by value (e.g., "User Story" → WorkItemType.STORY)
            data['work_item_type'] = next(t for t in WorkItemType if t.value == work_item_type_str)
            
            # Remove schema_version (not part of dataclass)
            data.pop('schema_version', None)
            
            # Reconstruct metadata
            metadata = WorkItemMetadata(**data)
            
            logger.info(f"Resumed work item: {work_item_id} from {yaml_file}")
            return True, f"Work item resumed: {work_item_id}", metadata
            
        except Exception as e:
            logger.error(f"Failed to resume work item: {e}")
            return False, f"Error resuming work item: {str(e)}", None
    
    def update_work_item_status(self, work_item_id: str, new_status: str) -> Tuple[bool, str]:
        """
        Update work item status and move files to appropriate directory (Phase 2).
        
        Args:
            work_item_id: Work item identifier
            new_status: New status (active, completed, blocked, cancelled)
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate status
            valid_statuses = ['active', 'completed', 'blocked', 'cancelled']
            if new_status not in valid_statuses:
                return False, f"Invalid status: {new_status}. Must be one of: {', '.join(valid_statuses)}"
            
            # Find current files
            md_file = None
            yaml_file = None
            current_dir = None
            
            for directory in [self.active_dir, self.completed_dir, self.blocked_dir]:
                for file in directory.glob(f"{work_item_id}*.md"):
                    md_file = file
                    current_dir = directory
                    break
                if md_file:
                    # Also find YAML file in same directory
                    yaml_file = md_file.with_suffix('.yaml')
                    break
            
            if not md_file:
                return False, f"Work item not found: {work_item_id}"
            
            # Determine target directory
            target_dir = self.active_dir if new_status == 'active' else \
                        self.completed_dir if new_status == 'completed' else \
                        self.blocked_dir
            
            # Skip if already in target directory
            if current_dir == target_dir:
                return True, f"Work item already in {new_status} status"
            
            # Move files
            new_md_file = target_dir / md_file.name
            md_file.rename(new_md_file)
            logger.info(f"Moved {md_file.name} to {target_dir.name}/")
            
            if yaml_file.exists():
                new_yaml_file = target_dir / yaml_file.name
                yaml_file.rename(new_yaml_file)
                logger.info(f"Moved {yaml_file.name} to {target_dir.name}/")
                
                # Update YAML status field
                with open(new_yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                data['status'] = new_status
                data['updated_date'] = datetime.now().isoformat()
                with open(new_yaml_file, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            return True, f"Work item {work_item_id} status updated to: {new_status}"
            
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
            return False, f"Error updating status: {str(e)}"
    
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
    
    
    def _enrich_with_git_context(self, metadata: WorkItemMetadata) -> WorkItemMetadata:
        """
        Enrich work item metadata with git history context.
        
        Phase 1 Integration: Wires GitHistoryValidator into ADO workflow
        
        Args:
            metadata: Work item metadata to enrich
        
        Returns:
            Enriched metadata with git context
        """
        if not self.git_validator:
            logger.warning("GitHistoryValidator not available, skipping git context enrichment")
            return metadata
        
        try:
            # Build request context for validation
            # Extract file references from description and title
            import re
            files_mentioned = re.findall(r'`([^`]+\.(py|js|ts|cs|java|html|css))`', metadata.description)
            files = [f[0] for f in files_mentioned] if files_mentioned else []
            
            request_context = {
                'files': files,
                'operation': 'ado_planning',
                'work_item_type': metadata.work_item_type.value,
                'has_git_history_context': False  # Force validator to run analysis
            }
            
            # Validate and get git history context
            validation_result = self.git_validator.validate_request(request_context)
            
            # Store validation results in metadata
            metadata.git_context = {
                'validation_status': validation_result.status,
                'validation_message': validation_result.message,
                'required_actions': validation_result.required_actions,
                'context_enrichment': validation_result.context_enrichment
            }
            metadata.quality_score = validation_result.quality_score
            
            # Extract high-risk files from context enrichment
            if validation_result.context_enrichment:
                high_risk = validation_result.context_enrichment.get('high_risk_files', [])
                metadata.high_risk_files = high_risk
                
                # Extract related commits
                recent_commits = validation_result.context_enrichment.get('recent_commits', [])
                metadata.related_commits = recent_commits[:10]  # Top 10 commits
                
                # Extract contributors and SME suggestions
                contributors = validation_result.context_enrichment.get('contributors', [])
                metadata.contributors = contributors
                
                # Top contributor becomes SME suggestion
                if contributors and not metadata.assigned_to:
                    metadata.sme_suggestions = [contributors[0]['name']] if contributors else []
            
            # Add high-risk warnings to acceptance criteria if applicable
            if metadata.high_risk_files:
                high_risk_criterion = f"⚠️ Review high-risk files: {', '.join(metadata.high_risk_files[:3])}"
                if high_risk_criterion not in metadata.acceptance_criteria:
                    metadata.acceptance_criteria.insert(0, high_risk_criterion)
            
            # Log enrichment success
            logger.info(f"Git context enrichment: quality_score={metadata.quality_score:.1f}%, high_risk_files={len(metadata.high_risk_files)}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to enrich with git context: {e}")
            # Return original metadata on error (degraded mode)
            return metadata
    
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
    
    # ========================================================================
    # PHASE 3: INTERACTIVE CLARIFICATION METHODS
    # ========================================================================
    
    def detect_ambiguities(self, metadata: WorkItemMetadata) -> Tuple[int, List[str]]:
        """
        Detect ambiguities in work item description.
        
        Args:
            metadata: Work item metadata to analyze
        
        Returns:
            Tuple of (ambiguity_score, list_of_detected_issues)
        """
        import re
        
        issues = []
        score = 0
        
        # Load clarification rules
        rules_file = self.cortex_root / "cortex-brain" / "config" / "clarification-rules.yaml"
        if not rules_file.exists():
            logger.warning("Clarification rules not found, using defaults")
            return 0, []
        
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
        
        detection_config = rules['ambiguity_detection']
        
        # Combine title and description for analysis
        text = f"{metadata.title} {metadata.description}".lower()
        
        # 1. Detect vague language
        vague_count = 0
        for pattern in detection_config['vague_patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            vague_count += len(matches)
        
        if vague_count > 0:
            issues.append(f"Vague language detected ({vague_count} instances)")
            score += vague_count * detection_config['vague_language_weight']
        
        # 2. Check for missing required fields
        missing_fields = []
        if not metadata.acceptance_criteria or len(metadata.acceptance_criteria) == 0:
            missing_fields.append("acceptance_criteria")
        
        # Check description for technical approach
        if "technical" not in text and "implementation" not in text and "approach" not in text:
            missing_fields.append("technical_approach")
        
        # Check for user flow
        if metadata.work_item_type in [WorkItemType.STORY, WorkItemType.FEATURE]:
            if "user" not in text and "flow" not in text and "interaction" not in text:
                missing_fields.append("user_flow")
        
        if missing_fields:
            issues.append(f"Missing information: {', '.join(missing_fields)}")
            score += len(missing_fields) * detection_config['missing_fields_weight']
        
        # 3. Detect technical ambiguity
        tech_ambiguity_count = 0
        for indicator in detection_config['technical_ambiguity_indicators']:
            if indicator in text:
                tech_ambiguity_count += 1
        
        if tech_ambiguity_count > 0:
            issues.append(f"Technical ambiguity detected ({tech_ambiguity_count} indicators)")
            score += tech_ambiguity_count * detection_config['technical_ambiguity_weight']
        
        # 4. Detect security concerns (should have security consideration if these terms present)
        security_terms = 0
        for indicator in detection_config['security_concern_indicators']:
            if indicator in text:
                security_terms += 1
        
        if security_terms > 0 and "security" not in text:
            issues.append(f"Security-sensitive work but no security consideration mentioned ({security_terms} terms)")
            score += security_terms * detection_config['security_concerns_weight']
        
        # Cap score at 10
        score = min(score, 10.0)
        
        logger.info(f"Ambiguity detection: score={score:.1f}, issues={len(issues)}")
        return int(score), issues
    
    def generate_clarification_questions(self, metadata: WorkItemMetadata, issues: List[str]) -> List[ClarificationRound]:
        """
        Generate clarification questions based on detected issues.
        
        Args:
            metadata: Work item metadata
            issues: List of detected ambiguities
        
        Returns:
            List of clarification rounds with questions
        """
        # Load clarification rules
        rules_file = self.cortex_root / "cortex-brain" / "config" / "clarification-rules.yaml"
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
        
        question_categories = rules['question_categories']
        max_rounds = rules['clarification_settings']['max_rounds']
        
        rounds = []
        round_num = 1
        
        # Always start with scope question
        scope_category = next((cat for cat in question_categories if cat['id'] == 'scope'), None)
        if scope_category and round_num <= max_rounds:
            for question in scope_category['questions'][:1]:  # First question only
                choices = [
                    ClarificationChoice(
                        letter=choice['letter'],
                        text=choice['text'],
                        category=choice['category']
                    ) for choice in question['choices']
                ]
                rounds.append(ClarificationRound(
                    round_number=round_num,
                    question=question['text'],
                    category=scope_category['id'],
                    choices=choices
                ))
                round_num += 1
                break
        
        # Add technical questions if technical issues detected
        if any('technical' in issue.lower() or 'missing information' in issue.lower() for issue in issues):
            tech_category = next((cat for cat in question_categories if cat['id'] == 'technical'), None)
            if tech_category and round_num <= max_rounds:
                for question in tech_category['questions'][:1]:  # First question only
                    choices = [
                        ClarificationChoice(
                            letter=choice['letter'],
                            text=choice['text'],
                            category=choice['category']
                        ) for choice in question['choices']
                    ]
                    rounds.append(ClarificationRound(
                        round_number=round_num,
                        question=question['text'],
                        category=tech_category['id'],
                        choices=choices
                    ))
                    round_num += 1
                    break
        
        # Add UI/UX questions for Stories and Features
        if metadata.work_item_type in [WorkItemType.STORY, WorkItemType.FEATURE] and round_num <= max_rounds:
            uiux_category = next((cat for cat in question_categories if cat['id'] == 'ui_ux'), None)
            if uiux_category:
                for question in uiux_category['questions'][:1]:  # First question only
                    choices = [
                        ClarificationChoice(
                            letter=choice['letter'],
                            text=choice['text'],
                            category=choice['category']
                        ) for choice in question['choices']
                    ]
                    rounds.append(ClarificationRound(
                        round_number=round_num,
                        question=question['text'],
                        category=uiux_category['id'],
                        choices=choices
                    ))
                    round_num += 1
                    break
        
        # Add quality questions if security or testing concerns detected
        if any('security' in issue.lower() or 'missing information' in issue.lower() for issue in issues):
            quality_category = next((cat for cat in question_categories if cat['id'] == 'quality'), None)
            if quality_category and round_num <= max_rounds:
                for question in quality_category['questions'][:1]:  # First question only
                    choices = [
                        ClarificationChoice(
                            letter=choice['letter'],
                            text=choice['text'],
                            category=choice['category']
                        ) for choice in question['choices']
                    ]
                    rounds.append(ClarificationRound(
                        round_number=round_num,
                        question=question['text'],
                        category=quality_category['id'],
                        choices=choices
                    ))
                    round_num += 1
                    break
        
        logger.info(f"Generated {len(rounds)} clarification rounds")
        return rounds
    
    def format_clarification_prompt(self, round: ClarificationRound, total_rounds: int) -> str:
        """
        Format a clarification question as a user-friendly prompt.
        
        Args:
            round: Clarification round to format
            total_rounds: Total number of rounds
        
        Returns:
            Formatted prompt string
        """
        prompt = f"\n{'='*70}\n"
        prompt += f"🔍 CORTEX - Interactive Clarification (Round {round.round_number} of {total_rounds})\n"
        prompt += f"{'='*70}\n\n"
        prompt += f"Category: {round.category.upper()}\n\n"
        prompt += f"Question: {round.question}\n\n"
        prompt += "Choices:\n"
        
        for choice in round.choices:
            choice_id = f"{round.round_number}{choice.letter}"
            prompt += f"  {choice_id}. {choice.text}\n"
        
        prompt += f"\n{'-'*70}\n"
        prompt += "Please respond with the letter of your choice "
        prompt += f"(e.g., \"{round.round_number}a\" or \"{round.round_number}a, {round.round_number}c\" for multiple).\n"
        prompt += "Type \"skip\" to skip this question, or \"done\" to finish clarification.\n"
        prompt += f"{'-'*70}\n"
        
        return prompt
    
    def parse_clarification_response(self, response: str, round: ClarificationRound) -> Tuple[bool, List[str], str]:
        """
        Parse user's clarification response.
        
        Args:
            response: User's response string
            round: Current clarification round
        
        Returns:
            Tuple of (is_valid, selected_choices, error_message)
        """
        response = response.strip().lower()
        
        # Handle special commands
        if response == "skip":
            return True, [], ""
        if response == "done":
            return True, [], ""
        
        # Parse choice selections
        selected = []
        parts = [p.strip() for p in response.split(',')]
        
        for part in parts:
            # Remove round number if present (e.g., "1a" -> "a")
            if part and part[0].isdigit():
                part = part[1:]
            
            # Validate letter
            valid_letters = [choice.letter for choice in round.choices]
            if part not in valid_letters:
                return False, [], f"Invalid choice '{part}'. Valid choices: {', '.join(valid_letters)}"
            
            selected.append(part)
        
        if not selected:
            return False, [], "No valid choices selected"
        
        return True, selected, ""
    
    def integrate_clarification_context(self, metadata: WorkItemMetadata, state: ConversationState) -> WorkItemMetadata:
        """
        Integrate clarified context back into work item metadata.
        
        Args:
            metadata: Original work item metadata
            state: Conversation state with user responses
        
        Returns:
            Updated metadata with clarifications
        """
        # Build clarification summary
        clarification_text = "\n\n## Clarified Requirements\n\n"
        
        for round in state.rounds:
            if not round.selected_choices:
                continue
            
            clarification_text += f"### {round.category.title()} (Round {round.round_number})\n"
            clarification_text += f"**Q:** {round.question}\n\n"
            clarification_text += "**A:**\n"
            
            for letter in round.selected_choices:
                choice = next((c for c in round.choices if c.letter == letter), None)
                if choice:
                    clarification_text += f"- {choice.text}\n"
            
            clarification_text += "\n"
        
        # Append to description
        metadata.description += clarification_text
        
        # Update context dict (for YAML storage)
        if not hasattr(metadata, 'clarification_context'):
            metadata.clarification_context = {}
        
        metadata.clarification_context = state.context
        
        logger.info(f"Integrated clarifications: {len(state.rounds)} rounds, {sum(len(r.selected_choices) for r in state.rounds)} choices")
        return metadata
    
    def process_clarification_round(self, round: ClarificationRound, user_response: str) -> Tuple[bool, List[str], str]:
        """
        Process a single clarification round with user response.
        Public API alias for parse_clarification_response().
        
        Args:
            round: The clarification round to process
            user_response: User's response text
        
        Returns:
            Tuple of (success, selected_choices, error_message)
        """
        return self.parse_clarification_response(user_response, round)
    
    # ========================================================================
    # PHASE 4: DOR/DOD VALIDATION METHODS
    # ========================================================================
    
    def validate_definition_of_ready(self, metadata: WorkItemMetadata, ambiguity_score: int = 0) -> ValidationResult:
        """
        Validate Definition of Ready for work item.
        Public API alias for validate_dor().
        
        Args:
            metadata: Work item metadata to validate
            ambiguity_score: Ambiguity score from detection (0-10)
        
        Returns:
            ValidationResult with overall score, category breakdowns, and recommendations
        """
        return self.validate_dor(metadata, ambiguity_score)
    
    def validate_definition_of_done(self, summary: WorkItemSummary) -> ValidationResult:
        """
        Validate Definition of Done for completed work.
        Public API alias for validate_dod().
        
        Args:
            summary: Work item summary to validate
        
        Returns:
            ValidationResult with overall score, category breakdowns, and recommendations
        """
        return self.validate_dod(summary)
    
    def validate_dor(self, metadata: WorkItemMetadata, ambiguity_score: int = 0) -> ValidationResult:
        """
        Validate Definition of Ready for work item.
        
        Args:
            metadata: Work item metadata to validate
            ambiguity_score: Ambiguity score from detection (0-10)
        
        Returns:
            ValidationResult with score and checklist
        """
        # Load DoR/DoD rules
        rules_file = self.cortex_root / "cortex-brain" / "config" / "dor-dod-rules.yaml"
        if not rules_file.exists():
            logger.error("DoR/DoD rules file not found")
            return ValidationResult(
                validation_type="dor",
                overall_score=0.0,
                passed=False,
                threshold=80.0,
                categories=[]
            )
        
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
        
        dor_config = rules['definition_of_ready']
        threshold = dor_config['minimum_score_to_approve']
        
        # Evaluate each category
        categories = []
        
        for category_name, category_config in dor_config['checklist'].items():
            items = []
            category_points_earned = 0
            category_points_possible = 0
            
            for item_config in category_config['items']:
                item_id = item_config['id']
                text = item_config['text']
                points = item_config['points']
                optional = item_config.get('optional', False)
                manual = item_config.get('manual', False)
                validation_expr = item_config.get('validation', 'True')
                
                # Evaluate validation expression
                passed = self._evaluate_validation(
                    validation_expr,
                    metadata,
                    ambiguity_score
                )
                
                points_earned = points if passed else 0
                
                # Track points (optional items don't count against total)
                if not optional:
                    category_points_possible += points
                    category_points_earned += points_earned
                elif passed:
                    # Optional items add to earned but not possible
                    category_points_earned += points_earned
                
                items.append(ChecklistItem(
                    id=item_id,
                    text=text,
                    passed=passed,
                    points_earned=points_earned,
                    points_possible=points,
                    optional=optional,
                    manual=manual,
                    validation_message="✅ Pass" if passed else "❌ Fail"
                ))
            
            # Calculate category score (0-100)
            category_score = (category_points_earned / category_points_possible * 100) if category_points_possible > 0 else 0
            weight = category_config['weight'] / 100.0
            weighted_score = category_score * weight
            
            categories.append(CategoryScore(
                category=category_name,
                score=category_score,
                weight=weight,
                items=items,
                weighted_score=weighted_score
            ))
        
        # Calculate overall score
        overall_score = sum(cat.weighted_score for cat in categories)
        
        # Add bonus points
        scoring_config = rules.get('scoring', {}).get('dor', {})
        bonus_config = scoring_config.get('bonus', {})
        
        # Bonus: All optional items complete
        all_optional_complete = all(
            item.passed
            for cat in categories
            for item in cat.items
            if item.optional
        )
        if all_optional_complete and bonus_config.get('all_optional_complete', 0) > 0:
            overall_score += bonus_config['all_optional_complete']
        
        # Bonus: Perfect clarity (ambiguity == 0)
        if ambiguity_score == 0 and bonus_config.get('perfect_clarity', 0) > 0:
            overall_score += bonus_config['perfect_clarity']
        
        # Cap at 100
        overall_score = min(overall_score, 100.0)
        
        # Generate recommendations
        recommendations = self._generate_dor_recommendations(categories, ambiguity_score)
        
        passed = overall_score >= threshold
        
        logger.info(f"DoR Validation: score={overall_score:.1f}%, passed={passed}, threshold={threshold}%")
        
        return ValidationResult(
            validation_type="dor",
            overall_score=overall_score,
            passed=passed,
            threshold=threshold,
            categories=categories,
            recommendations=recommendations
        )
    
    def validate_dod(self, summary: WorkItemSummary) -> ValidationResult:
        """
        Validate Definition of Done for completed work.
        
        Args:
            summary: Work item summary with completion details
        
        Returns:
            ValidationResult with score and checklist
        """
        # Load DoR/DoD rules
        rules_file = self.cortex_root / "cortex-brain" / "config" / "dor-dod-rules.yaml"
        if not rules_file.exists():
            logger.error("DoR/DoD rules file not found")
            return ValidationResult(
                validation_type="dod",
                overall_score=0.0,
                passed=False,
                threshold=85.0,
                categories=[]
            )
        
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
        
        dod_config = rules['definition_of_done']
        threshold = dod_config['minimum_score_to_complete']
        
        # Evaluate each category
        categories = []
        
        for category_name, category_config in dod_config['checklist'].items():
            items = []
            category_points_earned = 0
            category_points_possible = 0
            
            for item_config in category_config['items']:
                item_id = item_config['id']
                text = item_config['text']
                points = item_config['points']
                optional = item_config.get('optional', False)
                manual = item_config.get('manual', False)
                validation_expr = item_config.get('validation', 'True')
                
                # Evaluate validation expression
                passed = self._evaluate_dod_validation(
                    validation_expr,
                    summary
                )
                
                points_earned = points if passed else 0
                
                # Track points
                if not optional:
                    category_points_possible += points
                    category_points_earned += points_earned
                elif passed:
                    category_points_earned += points_earned
                
                items.append(ChecklistItem(
                    id=item_id,
                    text=text,
                    passed=passed,
                    points_earned=points_earned,
                    points_possible=points,
                    optional=optional,
                    manual=manual,
                    validation_message="✅ Pass" if passed else "❌ Fail"
                ))
            
            # Calculate category score
            category_score = (category_points_earned / category_points_possible * 100) if category_points_possible > 0 else 0
            weight = category_config['weight'] / 100.0
            weighted_score = category_score * weight
            
            categories.append(CategoryScore(
                category=category_name,
                score=category_score,
                weight=weight,
                items=items,
                weighted_score=weighted_score
            ))
        
        # Calculate overall score
        overall_score = sum(cat.weighted_score for cat in categories)
        
        # Add bonus points
        scoring_config = rules.get('scoring', {}).get('dod', {})
        bonus_config = scoring_config.get('bonus', {})
        
        # Bonus: Test coverage >= 80%
        if summary.test_coverage >= 80.0 and bonus_config.get('test_coverage_80_plus', 0) > 0:
            overall_score += bonus_config['test_coverage_80_plus']
        
        # Bonus: Zero known issues
        if len(summary.known_issues) == 0 and bonus_config.get('zero_known_issues', 0) > 0:
            overall_score += bonus_config['zero_known_issues']
        
        # Cap at 100
        overall_score = min(overall_score, 100.0)
        
        # Generate recommendations
        recommendations = self._generate_dod_recommendations(categories)
        
        passed = overall_score >= threshold
        
        logger.info(f"DoD Validation: score={overall_score:.1f}%, passed={passed}, threshold={threshold}%")
        
        return ValidationResult(
            validation_type="dod",
            overall_score=overall_score,
            passed=passed,
            threshold=threshold,
            categories=categories,
            recommendations=recommendations
        )
    
    def approve_plan(self, work_item_id: str, metadata: WorkItemMetadata, ambiguity_score: int = 0) -> Tuple[bool, str, Optional[ApprovalRecord]]:
        """
        Approve work item plan and transition to active status.
        
        Args:
            work_item_id: Work item identifier
            metadata: Work item metadata
            ambiguity_score: Ambiguity score from detection
        
        Returns:
            Tuple of (success, message, approval_record)
        """
        try:
            # Validate DoR
            dor_result = self.validate_dor(metadata, ambiguity_score)
            
            if not dor_result.passed:
                message = f"DoR validation failed: {dor_result.overall_score:.1f}% (threshold: {dor_result.threshold}%)"
                logger.warning(message)
                return False, message, None
            
            # Check quality gates
            gates_passed = []
            
            # Gate 1: DoR score >= threshold
            if dor_result.overall_score >= dor_result.threshold:
                gates_passed.append("Pre-Implementation Gate")
            
            # Gate 2: Ambiguity score < 5
            if ambiguity_score < 5:
                gates_passed.append("Ambiguity Gate")
            
            # Gate 3: Clarifications complete (if applicable)
            if not hasattr(metadata, 'clarification_context') or metadata.clarification_context:
                gates_passed.append("Clarification Gate")
            
            # Create approval record
            approval = ApprovalRecord(
                work_item_id=work_item_id,
                approval_stage="DoR Validation",
                dor_score=dor_result.overall_score,
                approved=True,
                approver="CORTEX (auto)",
                comments=f"DoR validation passed with score {dor_result.overall_score:.1f}%",
                quality_gates_passed=gates_passed
            )
            
            # Update work item status to active
            success, message = self.update_work_item_status(work_item_id, "active")
            
            if success:
                logger.info(f"Work item {work_item_id} approved and transitioned to active")
                return True, f"Work item approved (DoR: {dor_result.overall_score:.1f}%)", approval
            else:
                return False, f"DoR passed but status update failed: {message}", None
            
        except Exception as e:
            logger.error(f"Failed to approve plan: {e}")
            return False, f"Error during approval: {str(e)}", None
    
    def _evaluate_validation(self, expr: str, metadata: WorkItemMetadata, ambiguity_score: int) -> bool:
        """Evaluate DoR validation expression."""
        try:
            # Create safe evaluation context
            context = {
                'metadata': metadata,
                'ambiguity_score': ambiguity_score,
                'len': len,
                'any': any,
                'all': all,
                'hasattr': hasattr,
                'clarification_context': getattr(metadata, 'clarification_context', None)
            }
            
            # Evaluate expression
            result = eval(expr, {"__builtins__": {}}, context)
            return bool(result)
        except Exception as e:
            logger.warning(f"Validation expression failed: {expr}, error: {e}")
            return False
    
    def _evaluate_dod_validation(self, expr: str, summary: WorkItemSummary) -> bool:
        """Evaluate DoD validation expression."""
        try:
            # Create safe evaluation context
            context = {
                'summary': summary,
                'len': len,
                'any': any,
                'all': all
            }
            
            # Evaluate expression
            result = eval(expr, {"__builtins__": {}}, context)
            return bool(result)
        except Exception as e:
            logger.warning(f"DoD validation expression failed: {expr}, error: {e}")
            return False
    
    def _generate_dor_recommendations(self, categories: List[CategoryScore], ambiguity_score: int) -> List[str]:
        """Generate recommendations for DoR improvements."""
        recommendations = []
        
        for category in categories:
            failed_items = [item for item in category.items if not item.passed and not item.optional]
            if failed_items:
                rec = f"{category.category.title()}: "
                rec += ", ".join(item.text for item in failed_items[:2])  # First 2 failures
                if len(failed_items) > 2:
                    rec += f" (+{len(failed_items)-2} more)"
                recommendations.append(rec)
        
        # Ambiguity recommendation
        if ambiguity_score >= 5:
            recommendations.append(f"High ambiguity detected (score: {ambiguity_score}/10) - Consider clarification workflow")
        
        if not recommendations:
            recommendations.append("All checks passed! Excellent requirement quality.")
        
        return recommendations
    
    def _generate_dod_recommendations(self, categories: List[CategoryScore]) -> List[str]:
        """Generate recommendations for DoD improvements."""
        recommendations = []
        
        for category in categories:
            failed_items = [item for item in category.items if not item.passed and not item.optional]
            if failed_items:
                rec = f"{category.category.title()}: "
                rec += ", ".join(item.text for item in failed_items[:2])
                if len(failed_items) > 2:
                    rec += f" (+{len(failed_items)-2} more)"
                recommendations.append(rec)
        
        if not recommendations:
            recommendations.append("All completion criteria met! Ready for deployment.")
        
        return recommendations


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
