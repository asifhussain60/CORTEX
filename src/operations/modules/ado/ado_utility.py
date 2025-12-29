"""
ADO Work Item Utility

Fast, lightweight Azure DevOps work item management.
Replaces heavy orchestrator (1,642 lines) with focused utility (~900 lines).

Core Operations:
- Create, load, update work items
- Generate completion summaries
- Validate DoR (Definition of Ready)
- Validate DoD (Definition of Done)
- List work items by status

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import yaml
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import CORTEX config
try:
    from src.config import config
    CORTEX_ROOT = Path(config.root_path)
except ImportError:
    # Fallback if config not available
    CORTEX_ROOT = Path(__file__).resolve().parents[4]

# Import learning system
try:
    from src.learning.event_collector import get_global_collector
    from src.learning.event_taxonomy import LearningEvent, EventType
except ImportError:
    # Graceful degradation if learning system not available
    get_global_collector = None
    LearningEvent = None
    EventType = None


# ===== ENUMS & DATACLASSES =====

class WorkItemType(Enum):
    """Azure DevOps work item types."""
    STORY = "User Story"
    FEATURE = "Feature"
    BUG = "Bug"
    TASK = "Task"
    EPIC = "Epic"


class WorkItemStatus(Enum):
    """Work item status states."""
    ACTIVE = "active"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class WorkItemMetadata:
    """Core work item metadata (simplified)."""
    work_item_type: WorkItemType
    title: str
    description: str
    work_item_id: Optional[str] = None
    status: WorkItemStatus = WorkItemStatus.ACTIVE
    
    # Optional fields
    assigned_to: Optional[str] = None
    iteration: Optional[str] = None
    area_path: Optional[str] = None
    priority: int = 2  # 1=High, 2=Medium, 3=Low, 4=Very Low
    
    # Lists
    tags: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    related_work_items: List[str] = field(default_factory=list)
    
    # Timestamps
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_date: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WorkItemSummary:
    """Summary of completed work."""
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
    
    # Implementation
    implementation_notes: str = ""
    technical_decisions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # Validation
    acceptance_criteria_met: List[str] = field(default_factory=list)
    test_results: str = ""
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ValidationResult:
    """DoR/DoD validation result."""
    passed: bool
    score: float  # 0-100%
    total_points: int
    earned_points: int
    
    # Category scores
    category_scores: Dict[str, float] = field(default_factory=dict)
    
    # Details
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    validation_type: str = "DoR"  # "DoR" or "DoD"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WorkItemResult:
    """Result of work item operation."""
    success: bool
    message: str
    work_item_id: Optional[str] = None
    metadata: Optional[WorkItemMetadata] = None
    summary: Optional[WorkItemSummary] = None
    validation: Optional[ValidationResult] = None
    file_path: Optional[Path] = None
    errors: List[str] = field(default_factory=list)


# ===== DIRECTORY MANAGEMENT =====

def _get_work_items_dirs() -> Dict[str, Path]:
    """Get work items directory paths."""
    base_dir = CORTEX_ROOT / "cortex-brain" / "documents" / "planning" / "ado"
    
    dirs = {
        "base": base_dir,
        "active": base_dir / "active",
        "completed": base_dir / "completed",
        "blocked": base_dir / "blocked",
        "cancelled": base_dir / "cancelled",
        "summaries": CORTEX_ROOT / "cortex-brain" / "documents" / "summaries" / "ado"
    }
    
    # Ensure directories exist
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return dirs


def _get_status_dir(status: WorkItemStatus) -> Path:
    """Get directory for work item status."""
    dirs = _get_work_items_dirs()
    return dirs[status.value]


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def _generate_ado_documentation_reminder(work_item_id: str, title: str) -> str:
    """Generate documentation reminder for ADO work item completion."""
    return (
        "\n📚 DOCUMENTATION REMINDER:\n"
        "Document this ADO work item in the learning library.\n"
        "Location: cortex-brain/documents/learning/ado_workflows/\n"
        f"Work Item: {work_item_id} - {title}\n"
        "Capture: Implementation details, technical decisions, and outcomes.\n"
        "Access via: load dashboard\n"
        "Cross-machine compatible: All docs are in cortex-brain/documents/learning/"
    )


# ===== CORE OPERATION 1: CREATE WORK ITEM =====

def create_work_item(
    work_item_type: WorkItemType,
    title: str,
    description: str,
    **kwargs
) -> WorkItemResult:
    """
    Create new ADO work item.
    
    Args:
        work_item_type: Type of work item
        title: Work item title
        description: Work item description
        **kwargs: Additional metadata fields
        
    Returns:
        WorkItemResult with creation outcome
    """
    logger.info(f"📝 Creating {work_item_type.value}: {title}")
    
    try:
        # Generate work item ID
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        slug = _slugify(title)[:30]
        work_item_id = f"ado-{timestamp}-{slug}"
        
        # Create metadata
        metadata = WorkItemMetadata(
            work_item_type=work_item_type,
            title=title,
            description=description,
            work_item_id=work_item_id,
            **kwargs
        )
        
        # Generate file content
        content = _generate_work_item_markdown(metadata)
        
        # Save to file
        file_path = _get_status_dir(metadata.status) / f"{work_item_id}.md"
        file_path.write_text(content, encoding='utf-8')
        
        # Save YAML metadata
        yaml_path = file_path.with_suffix('.yaml')
        _save_yaml_metadata(metadata, yaml_path)
        
        # Emit learning event
        if get_global_collector and LearningEvent and EventType:
            try:
                event_type = EventType.ADO_STORY_CREATED if work_item_type == WorkItemType.STORY else EventType.ADO_FEATURE_CREATED
                event = LearningEvent(
                    event_type=event_type,
                    component="ADOUtility",
                    metadata={"work_item_id": work_item_id, "title": title, "type": work_item_type.value}
                )
                get_global_collector().capture_event(event)
            except Exception as e:
                logger.debug(f"Learning event capture failed: {e}")
        
        return WorkItemResult(
            success=True,
            message=f"Work item created: {work_item_id}",
            work_item_id=work_item_id,
            metadata=metadata,
            file_path=file_path
        )
        
    except Exception as e:
        return WorkItemResult(
            success=False,
            message=f"Failed to create work item: {str(e)}",
            errors=[str(e)]
        )


def _generate_work_item_markdown(metadata: WorkItemMetadata) -> str:
    """Generate markdown content for work item."""
    priority_labels = {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low", 4: "⚪ Very Low"}
    priority_label = priority_labels.get(metadata.priority, "Unknown")
    
    content = f"""# {metadata.title}

**Type:** {metadata.work_item_type.value}  
**ID:** {metadata.work_item_id}  
**Status:** {metadata.status.value.upper()}  
**Priority:** {priority_label}  
**Created:** {metadata.created_date}

"""
    
    if metadata.assigned_to:
        content += f"**Assigned To:** {metadata.assigned_to}  \n"
    if metadata.iteration:
        content += f"**Iteration:** {metadata.iteration}  \n"
    if metadata.area_path:
        content += f"**Area Path:** {metadata.area_path}  \n"
    if metadata.tags:
        content += f"**Tags:** {', '.join(metadata.tags)}  \n"
    
    content += f"\n---\n\n## Description\n\n{metadata.description}\n\n"
    
    if metadata.acceptance_criteria:
        content += "## Acceptance Criteria\n\n"
        for i, criterion in enumerate(metadata.acceptance_criteria, 1):
            content += f"{i}. {criterion}\n"
        content += "\n"
    
    if metadata.related_work_items:
        content += "## Related Work Items\n\n"
        for item in metadata.related_work_items:
            content += f"- {item}\n"
        content += "\n"
    
    content += "---\n\n## Implementation Notes\n\n(Add notes here as work progresses)\n"
    
    return content


def _save_yaml_metadata(metadata: WorkItemMetadata, yaml_path: Path):
    """Save metadata to YAML file."""
    data = {
        "work_item_type": metadata.work_item_type.value,
        "title": metadata.title,
        "description": metadata.description,
        "work_item_id": metadata.work_item_id,
        "status": metadata.status.value,
        "assigned_to": metadata.assigned_to,
        "iteration": metadata.iteration,
        "area_path": metadata.area_path,
        "priority": metadata.priority,
        "tags": metadata.tags,
        "acceptance_criteria": metadata.acceptance_criteria,
        "related_work_items": metadata.related_work_items,
        "created_date": metadata.created_date,
        "updated_date": metadata.updated_date
    }
    
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


# ===== CORE OPERATION 2: LOAD WORK ITEM =====

def load_work_item(work_item_id: str) -> WorkItemResult:
    """
    Load existing work item.
    
    Args:
        work_item_id: Work item identifier
        
    Returns:
        WorkItemResult with loaded metadata
    """
    logger.info(f"📂 Loading work item: {work_item_id}")
    
    try:
        # Search for work item across all status directories
        dirs = _get_work_items_dirs()
        yaml_path = None
        
        for status_name in ["active", "completed", "blocked", "cancelled"]:
            potential_path = dirs[status_name] / f"{work_item_id}.yaml"
            if potential_path.exists():
                yaml_path = potential_path
                break
        
        if not yaml_path:
            return WorkItemResult(
                success=False,
                message=f"Work item not found: {work_item_id}",
                errors=[f"No file found for {work_item_id}"]
            )
        
        # Load YAML metadata
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Create metadata object
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType(data["work_item_type"]),
            title=data["title"],
            description=data["description"],
            work_item_id=data["work_item_id"],
            status=WorkItemStatus(data["status"]),
            assigned_to=data.get("assigned_to"),
            iteration=data.get("iteration"),
            area_path=data.get("area_path"),
            priority=data.get("priority", 2),
            tags=data.get("tags", []),
            acceptance_criteria=data.get("acceptance_criteria", []),
            related_work_items=data.get("related_work_items", []),
            created_date=data["created_date"],
            updated_date=data["updated_date"]
        )
        
        return WorkItemResult(
            success=True,
            message=f"Work item loaded: {work_item_id}",
            work_item_id=work_item_id,
            metadata=metadata,
            file_path=yaml_path
        )
        
    except Exception as e:
        return WorkItemResult(
            success=False,
            message=f"Failed to load work item: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 3: UPDATE WORK ITEM =====

def update_work_item(
    work_item_id: str,
    **updates
) -> WorkItemResult:
    """
    Update existing work item.
    
    Args:
        work_item_id: Work item identifier
        **updates: Fields to update
        
    Returns:
        WorkItemResult with update outcome
    """
    logger.info(f"✏️ Updating work item: {work_item_id}")
    
    try:
        # Load existing work item
        load_result = load_work_item(work_item_id)
        if not load_result.success:
            return load_result
        
        metadata = load_result.metadata
        old_status = metadata.status
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(metadata, key):
                if key == "status" and isinstance(value, str):
                    setattr(metadata, key, WorkItemStatus(value))
                else:
                    setattr(metadata, key, value)
        
        # Update timestamp
        metadata.updated_date = datetime.now().isoformat()
        
        # Handle status change (move file)
        if metadata.status != old_status:
            # Delete old file
            old_yaml_path = _get_status_dir(old_status) / f"{work_item_id}.yaml"
            old_md_path = old_yaml_path.with_suffix('.md')
            
            # Regenerate markdown
            content = _generate_work_item_markdown(metadata)
            
            # Save to new location
            new_yaml_path = _get_status_dir(metadata.status) / f"{work_item_id}.yaml"
            new_md_path = new_yaml_path.with_suffix('.md')
            
            _save_yaml_metadata(metadata, new_yaml_path)
            new_md_path.write_text(content, encoding='utf-8')
            
            # Remove old files
            if old_yaml_path.exists():
                old_yaml_path.unlink()
            if old_md_path.exists():
                old_md_path.unlink()
            
            file_path = new_yaml_path
        else:
            # Update in place
            yaml_path = load_result.file_path
            _save_yaml_metadata(metadata, yaml_path)
            
            # Regenerate markdown
            content = _generate_work_item_markdown(metadata)
            md_path = yaml_path.with_suffix('.md')
            md_path.write_text(content, encoding='utf-8')
            
            file_path = yaml_path
        
        # Emit learning event for completion and generate documentation reminder
        documentation_reminder = None
        if metadata.status == WorkItemStatus.COMPLETED:
            if get_global_collector and LearningEvent and EventType:
                try:
                    event = LearningEvent(
                        event_type=EventType.ADO_WORK_ITEM_COMPLETED,
                        component="ADOUtility",
                        metadata={
                            "work_item_id": work_item_id,
                            "work_item_type": metadata.work_item_type.value,
                            "title": metadata.title
                        }
                    )
                    get_global_collector().capture_event(event)
                except Exception as e:
                    logger.debug(f"Learning event capture failed: {e}")
            
            # Generate documentation reminder
            documentation_reminder = _generate_ado_documentation_reminder(
                work_item_id=work_item_id,
                title=metadata.title
            )
            
            # Log reminder for visibility
            logger.info(documentation_reminder)
        
        return WorkItemResult(
            success=True,
            message=f"Work item updated: {work_item_id}",
            work_item_id=work_item_id,
            metadata=metadata,
            file_path=file_path
        )
        
    except Exception as e:
        return WorkItemResult(
            success=False,
            message=f"Failed to update work item: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 4: GENERATE SUMMARY =====

def generate_summary(
    work_item_id: str,
    **summary_data
) -> WorkItemResult:
    """
    Generate completion summary for work item.
    
    Args:
        work_item_id: Work item identifier
        **summary_data: Summary fields
        
    Returns:
        WorkItemResult with summary
    """
    logger.info(f"📊 Generating summary: {work_item_id}")
    
    try:
        # Load work item
        load_result = load_work_item(work_item_id)
        if not load_result.success:
            return load_result
        
        metadata = load_result.metadata
        
        # Create summary
        summary = WorkItemSummary(
            work_item_id=work_item_id,
            work_item_type=metadata.work_item_type,
            title=metadata.title,
            **summary_data
        )
        
        # Generate markdown summary
        summary_content = _generate_summary_markdown(summary, metadata)
        
        # Save summary
        dirs = _get_work_items_dirs()
        summary_path = dirs["summaries"] / f"{work_item_id}-summary.md"
        summary_path.write_text(summary_content, encoding='utf-8')
        
        return WorkItemResult(
            success=True,
            message=f"Summary generated: {work_item_id}",
            work_item_id=work_item_id,
            metadata=metadata,
            summary=summary,
            file_path=summary_path
        )
        
    except Exception as e:
        return WorkItemResult(
            success=False,
            message=f"Failed to generate summary: {str(e)}",
            errors=[str(e)]
        )


def _generate_summary_markdown(summary: WorkItemSummary, metadata: WorkItemMetadata) -> str:
    """Generate markdown summary for ADO."""
    content = f"""# Work Summary: {summary.title}

**Work Item ID:** {summary.work_item_id}  
**Type:** {summary.work_item_type.value}  
**Completed:** {summary.timestamp}

---

## Work Completed

### Files Created ({len(summary.files_created)})
"""
    
    if summary.files_created:
        for file in summary.files_created:
            content += f"- `{file}`\n"
    else:
        content += "- (None)\n"
    
    content += f"\n### Files Modified ({len(summary.files_modified)})\n"
    if summary.files_modified:
        for file in summary.files_modified:
            content += f"- `{file}`\n"
    else:
        content += "- (None)\n"
    
    content += f"\n### Tests Created ({len(summary.tests_created)})\n"
    if summary.tests_created:
        for test in summary.tests_created:
            content += f"- `{test}`\n"
    else:
        content += "- (None)\n"
    
    content += f"\n### Documentation ({len(summary.documentation_created)})\n"
    if summary.documentation_created:
        for doc in summary.documentation_created:
            content += f"- `{doc}`\n"
    else:
        content += "- (None)\n"
    
    content += f"""

---

## Metrics

- **Code Changes:** {summary.code_changes_count}
- **Test Coverage:** {summary.test_coverage:.1f}%
- **Duration:** {summary.duration_hours:.1f} hours

---

## Implementation Notes

{summary.implementation_notes if summary.implementation_notes else "(No notes provided)"}

"""
    
    if summary.technical_decisions:
        content += "### Technical Decisions\n\n"
        for decision in summary.technical_decisions:
            content += f"- {decision}\n"
        content += "\n"
    
    if summary.dependencies:
        content += "### Dependencies\n\n"
        for dep in summary.dependencies:
            content += f"- {dep}\n"
        content += "\n"
    
    content += "---\n\n## Acceptance Criteria\n\n"
    if summary.acceptance_criteria_met:
        for criterion in summary.acceptance_criteria_met:
            content += f"- ✅ {criterion}\n"
    else:
        content += "(No criteria recorded)\n"
    
    if summary.test_results:
        content += f"\n---\n\n## Test Results\n\n{summary.test_results}\n"
    
    return content


# ===== CORE OPERATION 5: VALIDATE DoR =====

def validate_dor(
    metadata: WorkItemMetadata,
    ambiguity_score: int = 0
) -> ValidationResult:
    """
    Validate Definition of Ready.
    
    Args:
        metadata: Work item metadata
        ambiguity_score: Number of ambiguities detected
        
    Returns:
        ValidationResult with DoR assessment
    """
    logger.info(f"✅ Validating DoR: {metadata.work_item_id}")
    
    try:
        passed_checks = []
        failed_checks = []
        warnings = []
        total_points = 0
        earned_points = 0
        
        # Check 1: Title (10 points)
        total_points += 10
        if metadata.title and len(metadata.title) >= 10:
            passed_checks.append("Title present and descriptive")
            earned_points += 10
        else:
            failed_checks.append("Title missing or too short (<10 chars)")
        
        # Check 2: Description (20 points)
        total_points += 20
        if metadata.description and len(metadata.description) >= 50:
            passed_checks.append("Description present and detailed")
            earned_points += 20
        elif metadata.description:
            passed_checks.append("Description present (brief)")
            earned_points += 10
            warnings.append("Description could be more detailed (>50 chars recommended)")
        else:
            failed_checks.append("Description missing")
        
        # Check 3: Acceptance Criteria (30 points)
        total_points += 30
        if len(metadata.acceptance_criteria) >= 3:
            passed_checks.append(f"Acceptance criteria defined ({len(metadata.acceptance_criteria)} items)")
            earned_points += 30
        elif len(metadata.acceptance_criteria) > 0:
            passed_checks.append(f"Acceptance criteria present ({len(metadata.acceptance_criteria)} items)")
            earned_points += 15
            warnings.append("3+ acceptance criteria recommended")
        else:
            failed_checks.append("No acceptance criteria defined")
        
        # Check 4: Priority (10 points)
        total_points += 10
        if 1 <= metadata.priority <= 4:
            passed_checks.append(f"Priority set ({metadata.priority})")
            earned_points += 10
        else:
            warnings.append("Invalid priority value")
        
        # Check 5: Ambiguity (30 points)
        total_points += 30
        if ambiguity_score == 0:
            passed_checks.append("No ambiguities detected")
            earned_points += 30
        elif ambiguity_score <= 2:
            passed_checks.append("Minor ambiguities detected")
            earned_points += 20
            warnings.append(f"{ambiguity_score} ambiguities - consider clarification")
        else:
            failed_checks.append(f"{ambiguity_score} ambiguities detected")
            warnings.append("Significant clarification needed")
        
        # Calculate score
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = score >= 80.0  # 80% threshold
        
        # Category scores
        category_scores = {
            "clarity": (earned_points / total_points * 100) if total_points > 0 else 0,
            "completeness": 100.0 if metadata.description and metadata.acceptance_criteria else 50.0
        }
        
        # Recommendations
        recommendations = []
        if score < 80:
            recommendations.append("Improve DoR score to 80%+ before starting work")
        if not metadata.acceptance_criteria:
            recommendations.append("Add specific, testable acceptance criteria")
        if ambiguity_score > 2:
            recommendations.append("Clarify ambiguous requirements")
        
        return ValidationResult(
            passed=passed,
            score=score,
            total_points=total_points,
            earned_points=earned_points,
            category_scores=category_scores,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            recommendations=recommendations,
            validation_type="DoR"
        )
        
    except Exception as e:
        logger.error(f"DoR validation failed: {e}")
        return ValidationResult(
            passed=False,
            score=0.0,
            total_points=100,
            earned_points=0,
            failed_checks=[f"Validation error: {str(e)}"],
            validation_type="DoR"
        )


# ===== CORE OPERATION 6: VALIDATE DoD =====

def validate_dod(summary: WorkItemSummary) -> ValidationResult:
    """
    Validate Definition of Done.
    
    Args:
        summary: Work item summary
        
    Returns:
        ValidationResult with DoD assessment
    """
    logger.info(f"✅ Validating DoD: {summary.work_item_id}")
    
    try:
        passed_checks = []
        failed_checks = []
        warnings = []
        total_points = 0
        earned_points = 0
        
        # Check 1: Code Changes (20 points)
        total_points += 20
        if summary.code_changes_count > 0:
            passed_checks.append(f"Code changes made ({summary.code_changes_count})")
            earned_points += 20
        else:
            failed_checks.append("No code changes recorded")
        
        # Check 2: Tests (30 points)
        total_points += 30
        if len(summary.tests_created) >= 3:
            passed_checks.append(f"Tests created ({len(summary.tests_created)})")
            earned_points += 30
        elif len(summary.tests_created) > 0:
            passed_checks.append(f"Some tests created ({len(summary.tests_created)})")
            earned_points += 15
            warnings.append("3+ tests recommended")
        else:
            failed_checks.append("No tests created")
        
        # Check 3: Test Coverage (20 points)
        total_points += 20
        if summary.test_coverage >= 80.0:
            passed_checks.append(f"Test coverage excellent ({summary.test_coverage:.1f}%)")
            earned_points += 20
        elif summary.test_coverage >= 60.0:
            passed_checks.append(f"Test coverage good ({summary.test_coverage:.1f}%)")
            earned_points += 15
            warnings.append("80%+ coverage recommended")
        elif summary.test_coverage > 0:
            passed_checks.append(f"Test coverage low ({summary.test_coverage:.1f}%)")
            earned_points += 5
            warnings.append("Insufficient test coverage")
        else:
            failed_checks.append("No test coverage")
        
        # Check 4: Documentation (15 points)
        total_points += 15
        if len(summary.documentation_created) > 0:
            passed_checks.append(f"Documentation created ({len(summary.documentation_created)})")
            earned_points += 15
        else:
            warnings.append("No documentation created")
        
        # Check 5: Acceptance Criteria Met (15 points)
        total_points += 15
        if len(summary.acceptance_criteria_met) >= 3:
            passed_checks.append(f"Acceptance criteria met ({len(summary.acceptance_criteria_met)})")
            earned_points += 15
        elif len(summary.acceptance_criteria_met) > 0:
            passed_checks.append(f"Some criteria met ({len(summary.acceptance_criteria_met)})")
            earned_points += 8
            warnings.append("Not all acceptance criteria verified")
        else:
            failed_checks.append("No acceptance criteria met")
        
        # Calculate score
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = score >= 75.0  # 75% threshold for DoD
        
        # Category scores
        category_scores = {
            "code_quality": (earned_points / total_points * 100) if total_points > 0 else 0,
            "testing": (summary.test_coverage / 100 * 100) if summary.test_coverage > 0 else 0
        }
        
        # Recommendations
        recommendations = []
        if score < 75:
            recommendations.append("Improve DoD score to 75%+ before completion")
        if summary.test_coverage < 80:
            recommendations.append("Increase test coverage to 80%+")
        if not summary.documentation_created:
            recommendations.append("Add documentation for implemented features")
        
        return ValidationResult(
            passed=passed,
            score=score,
            total_points=total_points,
            earned_points=earned_points,
            category_scores=category_scores,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            recommendations=recommendations,
            validation_type="DoD"
        )
        
    except Exception as e:
        logger.error(f"DoD validation failed: {e}")
        return ValidationResult(
            passed=False,
            score=0.0,
            total_points=100,
            earned_points=0,
            failed_checks=[f"Validation error: {str(e)}"],
            validation_type="DoD"
        )


# ===== CORE OPERATION 7: LIST WORK ITEMS =====

def list_work_items(
    status: Optional[WorkItemStatus] = None
) -> WorkItemResult:
    """
    List work items by status.
    
    Args:
        status: Filter by status (None = all)
        
    Returns:
        WorkItemResult with list of work items
    """
    logger.info(f"📋 Listing work items (status: {status.value if status else 'all'})")
    
    try:
        work_items = []
        dirs = _get_work_items_dirs()
        
        # Determine which directories to search
        if status:
            search_dirs = {status.value: _get_status_dir(status)}
        else:
            search_dirs = {
                "active": dirs["active"],
                "completed": dirs["completed"],
                "blocked": dirs["blocked"],
                "cancelled": dirs["cancelled"]
            }
        
        # Scan directories
        for status_name, dir_path in search_dirs.items():
            for yaml_path in dir_path.glob("*.yaml"):
                try:
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                    
                    metadata = WorkItemMetadata(
                        work_item_type=WorkItemType(data["work_item_type"]),
                        title=data["title"],
                        description=data["description"],
                        work_item_id=data["work_item_id"],
                        status=WorkItemStatus(data["status"]),
                        priority=data.get("priority", 2),
                        created_date=data["created_date"],
                        updated_date=data["updated_date"]
                    )
                    work_items.append(metadata)
                except Exception as e:
                    logger.warning(f"Failed to load {yaml_path.name}: {e}")
        
        # Sort by updated date (most recent first)
        work_items.sort(key=lambda x: x.updated_date, reverse=True)
        
        message = f"Found {len(work_items)} work item(s)"
        if status:
            message += f" with status '{status.value}'"
        
        return WorkItemResult(
            success=True,
            message=message,
            metadata=work_items[0] if work_items else None,
            errors=[] if work_items else ["No work items found"]
        )
        
    except Exception as e:
        return WorkItemResult(
            success=False,
            message=f"Failed to list work items: {str(e)}",
            errors=[str(e)]
        )


# ===== CLI TEST EXECUTION =====

if __name__ == "__main__":
    print("=" * 60)
    print("ADO Work Item Utility - Direct Test")
    print("=" * 60)
    
    # Test 1: Create work item
    print("\n[Test 1] Create work item...")
    result = create_work_item(
        work_item_type=WorkItemType.STORY,
        title="Example User Story",
        description="This is a test user story for ADO utility validation.",
        priority=1,
        tags=["test", "utility"],
        acceptance_criteria=[
            "User can create work items",
            "User can load work items",
            "User can update work items"
        ]
    )
    
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(f"Work Item ID: {result.work_item_id}")
    
    if not result.success:
        print("❌ Creation failed")
        exit(1)
    
    work_item_id = result.work_item_id
    
    # Test 2: Load work item
    print("\n" + "=" * 60)
    print("[Test 2] Load work item...")
    load_result = load_work_item(work_item_id)
    
    print(f"Success: {load_result.success}")
    print(f"Message: {load_result.message}")
    print(f"Title: {load_result.metadata.title}")
    
    # Test 3: Validate DoR
    print("\n" + "=" * 60)
    print("[Test 3] Validate DoR...")
    dor_result = validate_dor(load_result.metadata, ambiguity_score=0)
    
    print(f"Passed: {dor_result.passed}")
    print(f"Score: {dor_result.score:.1f}%")
    print(f"Points: {dor_result.earned_points}/{dor_result.total_points}")
    
    # Test 4: Update work item
    print("\n" + "=" * 60)
    print("[Test 4] Update work item...")
    update_result = update_work_item(
        work_item_id,
        status="completed",
        assigned_to="Test User"
    )
    
    print(f"Success: {update_result.success}")
    print(f"Message: {update_result.message}")
    print(f"New Status: {update_result.metadata.status.value}")
    
    # Test 5: List work items
    print("\n" + "=" * 60)
    print("[Test 5] List work items...")
    list_result = list_work_items(status=WorkItemStatus.COMPLETED)
    
    print(f"Success: {list_result.success}")
    print(f"Message: {list_result.message}")
    
    # Cleanup
    print("\n" + "=" * 60)
    print("[Cleanup] Removing test work item...")
    yaml_path = _get_status_dir(WorkItemStatus.COMPLETED) / f"{work_item_id}.yaml"
    md_path = yaml_path.with_suffix('.md')
    
    if yaml_path.exists():
        yaml_path.unlink()
    if md_path.exists():
        md_path.unlink()
    print("✅ Test work item removed")
    
    print("\n" + "=" * 60)
    print("✅ Utility tests complete")
    print("=" * 60)
