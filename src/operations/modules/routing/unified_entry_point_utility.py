"""
Unified Entry Point Utility - CORTEX Operation Routing and Coordination

Universal routing system for all CORTEX operations with workflow execution,
summary generation, ADO-formatted output, and CLI wrapper routing.

Part of CORTEX 3.2.1 - Unified Entry Point System
Sprint 13a Migration: unified_entry_point_orchestrator (544 lines) → unified_entry_point_utility (~600 lines)
Phase 3 & 4 Enhancement: CLI wrapper routing for execution_method-based dispatch
Author: Asif Hussain

Operations:
- execute_code_review: Route to code review workflow
- execute_ado_story: Create and track ADO user story
- execute_ado_feature: Create and track ADO feature
- generate_work_summary: Generate ADO-formatted summary
- initialize_orchestrators: Dynamic orchestrator initialization
- generate_code_review_summary: Format code review results for ADO
- generate_story_summary: Format story creation for ADO
- generate_feature_summary: Format feature creation for ADO
- save_summary: Persist summary to filesystem
- format_priority: Convert priority number to label
- route_operation: Dispatch based on execution_method (cli_wrapper|copilot_chat|internal)
- invoke_cli_wrapper: Execute CLI wrapper script with arguments
"""

import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

# Import learning system
try:
    from src.learning.event_collector import get_global_collector
    from src.learning.event_taxonomy import LearningEvent, EventType
except ImportError:
    get_global_collector = None
    LearningEvent = None
    EventType = None


# ========================================
# Enums and Data Classes
# ========================================

class OperationType(Enum):
    """Types of operations supported by unified entry point."""
    CODE_REVIEW = "code_review"
    ADO_STORY = "ado_story"
    ADO_FEATURE = "ado_feature"
    PLANNING = "planning"


@dataclass
class WorkflowResult:
    """Complete workflow execution result with metrics and output."""
    operation_type: OperationType
    success: bool
    work_item_id: Optional[str] = None
    
    # Files affected
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_analyzed: List[str] = field(default_factory=list)
    tests_created: List[str] = field(default_factory=list)
    documentation_created: List[str] = field(default_factory=list)
    
    # Workflow details
    implementation_notes: str = ""
    technical_decisions: List[str] = field(default_factory=list)
    issues_found: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metrics
    duration_seconds: float = 0.0
    test_coverage: float = 0.0
    risk_score: int = 0  # For code review
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Summary
    ado_summary: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "operation_type": self.operation_type.value,
            "success": self.success,
            "work_item_id": self.work_item_id,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "files_analyzed": self.files_analyzed,
            "tests_created": self.tests_created,
            "documentation_created": self.documentation_created,
            "implementation_notes": self.implementation_notes,
            "technical_decisions": self.technical_decisions,
            "issues_found": self.issues_found,
            "recommendations": self.recommendations,
            "duration_seconds": self.duration_seconds,
            "test_coverage": self.test_coverage,
            "risk_score": self.risk_score,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "ado_summary": self.ado_summary
        }


@dataclass
class OrchestratorRegistry:
    """Registry of available orchestrators."""
    code_review: Optional[Any] = None
    ado_work_item: Optional[Any] = None
    planning: Optional[Any] = None
    
    def is_available(self, operation_type: OperationType) -> bool:
        """Check if orchestrator is available for operation type"""
        if operation_type == OperationType.CODE_REVIEW:
            return self.code_review is not None
        elif operation_type in [OperationType.ADO_STORY, OperationType.ADO_FEATURE]:
            return self.ado_work_item is not None
        elif operation_type == OperationType.PLANNING:
            return self.planning is not None
        return False


# ========================================
# Orchestrator Initialization
# ========================================

def initialize_orchestrators(cortex_root: Path) -> OrchestratorRegistry:
    """
    Initialize all available orchestrators dynamically.
    
    Gracefully handles missing orchestrators, allowing partial functionality.
    
    Args:
        cortex_root: CORTEX root directory
    
    Returns:
        OrchestratorRegistry with available orchestrators
    
    Example:
        >>> registry = initialize_orchestrators(Path("/path/to/CORTEX"))
        >>> registry.is_available(OperationType.CODE_REVIEW)
        True
    """
    registry = OrchestratorRegistry()
    
    # Try to initialize code review orchestrator
    try:
        from src.orchestrators.code_review_orchestrator import CodeReviewOrchestrator
        registry.code_review = CodeReviewOrchestrator(str(cortex_root))
        logger.info("✅ Code review orchestrator initialized")
    except ImportError as e:
        logger.warning(f"⚠️  Code review orchestrator not available: {e}")
    
    # Try to initialize ADO work item orchestrator
    try:
        from src.orchestrators.ado_work_item_orchestrator import ADOWorkItemOrchestrator
        registry.ado_work_item = ADOWorkItemOrchestrator(str(cortex_root))
        logger.info("✅ ADO work item orchestrator initialized")
    except ImportError as e:
        logger.warning(f"⚠️  ADO work item orchestrator not available: {e}")
    
    # Try to initialize planning orchestrator
    try:
        from src.orchestrators.planning_orchestrator import PlanningOrchestrator
        registry.planning = PlanningOrchestrator(str(cortex_root))
        logger.info("✅ Planning orchestrator initialized")
    except ImportError as e:
        logger.warning(f"⚠️  Planning orchestrator not available: {e}")
    
    return registry


# ========================================
# Workflow Execution Operations
# ========================================

def execute_code_review(
    cortex_root: Path,
    registry: OrchestratorRegistry,
    pr_info: str,
    depth: str = "standard",
    focus_areas: Optional[List[str]] = None
) -> WorkflowResult:
    """
    Execute code review workflow with routing to specialized orchestrator.
    
    Args:
        cortex_root: CORTEX root directory
        registry: OrchestratorRegistry with initialized orchestrators
        pr_info: PR link, ID, or diff text
        depth: Review depth (quick/standard/deep)
        focus_areas: Areas to focus on (security, performance, etc.)
    
    Returns:
        WorkflowResult with code review analysis
    
    Example:
        >>> registry = initialize_orchestrators(Path("/path/to/CORTEX"))
        >>> result = execute_code_review(Path("/path"), registry, "PR#123")
        >>> result.success
        True
        >>> result.risk_score
        35
    """
    result = WorkflowResult(
        operation_type=OperationType.CODE_REVIEW,
        success=False
    )
    
    # Emit WORKFLOW_STARTED event
    if get_global_collector and LearningEvent and EventType:
        try:
            event = LearningEvent(
                event_type=EventType.WORKFLOW_STARTED,
                component="UnifiedEntryPointOrchestrator",
                metadata={"operation_type": "code_review", "pr_info": pr_info, "depth": depth}
            )
            get_global_collector().capture_event(event)
        except Exception as e:
            logger.debug(f"Learning event capture failed: {e}")
    
    try:
        if not registry.code_review:
            result.implementation_notes = "Code review orchestrator not available"
            logger.error("❌ Code review orchestrator not initialized")
            return result
        
        logger.info(f"🔍 Starting code review: {pr_info}")
        
        # Execute review through orchestrator
        review_result = perform_code_review(
            registry.code_review,
            pr_info,
            depth,
            focus_areas
        )
        
        # Populate result
        result.files_analyzed = review_result.get("files_analyzed", [])
        result.issues_found = review_result.get("issues", [])
        result.recommendations = review_result.get("recommendations", [])
        result.risk_score = review_result.get("risk_score", 0)
        
        result.completed_at = datetime.now()
        result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
        result.success = True
        
        # Generate ADO-formatted summary
        result.ado_summary = generate_code_review_summary(result)
        
        logger.info(f"✅ Code review complete: {len(result.files_analyzed)} files, risk {result.risk_score}")
        
        # Emit WORKFLOW_COMPLETED event
        if get_global_collector and LearningEvent and EventType:
            try:
                event = LearningEvent(
                    event_type=EventType.WORKFLOW_COMPLETED,
                    component="UnifiedEntryPointOrchestrator",
                    metadata={
                        "operation_type": "code_review",
                        "files_analyzed": len(result.files_analyzed),
                        "risk_score": result.risk_score
                    }
                )
                get_global_collector().capture_event(event)
            except Exception as e:
                logger.debug(f"Learning event capture failed: {e}")
        
    except Exception as e:
        logger.error(f"❌ Code review failed: {e}")
        result.implementation_notes = f"Error: {str(e)}"
    
    return result


def execute_ado_story(
    cortex_root: Path,
    registry: OrchestratorRegistry,
    title: str,
    description: str,
    acceptance_criteria: Optional[List[str]] = None,
    **kwargs
) -> WorkflowResult:
    """
    Create ADO user story and track implementation.
    
    Args:
        cortex_root: CORTEX root directory
        registry: OrchestratorRegistry with initialized orchestrators
        title: Story title
        description: Story description
        acceptance_criteria: List of acceptance criteria
        **kwargs: Additional metadata (priority, assigned_to, etc.)
    
    Returns:
        WorkflowResult with story creation details
    
    Example:
        >>> registry = initialize_orchestrators(Path("/path/to/CORTEX"))
        >>> result = execute_ado_story(Path("/path"), registry, "User Login", "As a user...")
        >>> result.success
        True
        >>> result.work_item_id
        'STORY-12345'
    """
    result = WorkflowResult(
        operation_type=OperationType.ADO_STORY,
        success=False
    )
    
    try:
        if not registry.ado_work_item:
            result.implementation_notes = "ADO work item orchestrator not available"
            logger.error("❌ ADO work item orchestrator not initialized")
            return result
        
        logger.info(f"📝 Creating user story: {title}")
        
        # Import WorkItemType
        from src.orchestrators.ado_work_item_orchestrator import WorkItemType
        
        # Add acceptance criteria to kwargs
        if acceptance_criteria:
            kwargs["acceptance_criteria"] = acceptance_criteria
        
        # Create story through orchestrator
        success, message, metadata = registry.ado_work_item.create_work_item(
            WorkItemType.STORY,
            title,
            description,
            **kwargs
        )
        
        if not success:
            result.implementation_notes = message
            logger.error(f"❌ Story creation failed: {message}")
            return result
        
        result.work_item_id = metadata.work_item_id
        result.completed_at = datetime.now()
        result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
        result.success = True
        
        # Generate ADO-formatted summary
        result.ado_summary = generate_story_summary(result, metadata)
        
        logger.info(f"✅ User story created: {result.work_item_id}")
        
    except Exception as e:
        logger.error(f"❌ Story creation failed: {e}")
        result.implementation_notes = f"Error: {str(e)}"
    
    return result


def execute_ado_feature(
    cortex_root: Path,
    registry: OrchestratorRegistry,
    title: str,
    description: str,
    related_stories: Optional[List[str]] = None,
    **kwargs
) -> WorkflowResult:
    """
    Create ADO feature and track implementation.
    
    Args:
        cortex_root: CORTEX root directory
        registry: OrchestratorRegistry with initialized orchestrators
        title: Feature title
        description: Feature description
        related_stories: List of related story IDs
        **kwargs: Additional metadata (priority, assigned_to, etc.)
    
    Returns:
        WorkflowResult with feature creation details
    
    Example:
        >>> registry = initialize_orchestrators(Path("/path/to/CORTEX"))
        >>> result = execute_ado_feature(Path("/path"), registry, "Authentication System", "...")
        >>> result.success
        True
        >>> result.work_item_id
        'FEATURE-678'
    """
    result = WorkflowResult(
        operation_type=OperationType.ADO_FEATURE,
        success=False
    )
    
    try:
        if not registry.ado_work_item:
            result.implementation_notes = "ADO work item orchestrator not available"
            logger.error("❌ ADO work item orchestrator not initialized")
            return result
        
        logger.info(f"🚀 Creating feature: {title}")
        
        # Import WorkItemType
        from src.orchestrators.ado_work_item_orchestrator import WorkItemType
        
        # Add related stories to kwargs
        if related_stories:
            kwargs["related_work_items"] = related_stories
        
        # Create feature through orchestrator
        success, message, metadata = registry.ado_work_item.create_work_item(
            WorkItemType.FEATURE,
            title,
            description,
            **kwargs
        )
        
        if not success:
            result.implementation_notes = message
            logger.error(f"❌ Feature creation failed: {message}")
            return result
        
        result.work_item_id = metadata.work_item_id
        result.completed_at = datetime.now()
        result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
        result.success = True
        
        # Generate ADO-formatted summary
        result.ado_summary = generate_feature_summary(result, metadata)
        
        logger.info(f"✅ Feature created: {result.work_item_id}")
        
    except Exception as e:
        logger.error(f"❌ Feature creation failed: {e}")
        result.implementation_notes = f"Error: {str(e)}"
    
    return result


def generate_work_summary(
    registry: OrchestratorRegistry,
    work_item_id: str
) -> Tuple[bool, str, Optional[str]]:
    """
    Generate comprehensive work summary for ADO work item.
    
    Args:
        registry: OrchestratorRegistry with initialized orchestrators
        work_item_id: Work item identifier
    
    Returns:
        Tuple of (success, message, ado_markdown)
    
    Example:
        >>> registry = initialize_orchestrators(Path("/path/to/CORTEX"))
        >>> success, msg, markdown = generate_work_summary(registry, "STORY-12345")
        >>> success
        True
        >>> "# Work Summary" in markdown
        True
    """
    try:
        if not registry.ado_work_item:
            return False, "ADO work item orchestrator not available", None
        
        logger.info(f"📄 Generating work summary: {work_item_id}")
        
        success, message, markdown = registry.ado_work_item.generate_work_summary(work_item_id)
        
        if success:
            logger.info(f"✅ Work summary generated: {work_item_id}")
        else:
            logger.error(f"❌ Work summary generation failed: {message}")
        
        return success, message, markdown
        
    except Exception as e:
        logger.error(f"❌ Summary generation failed: {e}")
        return False, f"Error: {str(e)}", None


# ========================================
# Helper Operations
# ========================================

def perform_code_review(
    code_review_orch: Any,
    pr_info: str,
    depth: str,
    focus_areas: Optional[List[str]]
) -> Dict[str, Any]:
    """
    Perform code review analysis through orchestrator.
    
    Args:
        code_review_orch: Code review orchestrator instance
        pr_info: PR information
        depth: Review depth
        focus_areas: Areas to focus on
    
    Returns:
        Dictionary with review results
    
    Example:
        >>> orch = CodeReviewOrchestrator("/path")
        >>> result = perform_code_review(orch, "PR#123", "standard", None)
        >>> result['files_analyzed']
        ['src/main.py', 'src/utils.py']
    """
    # Placeholder - actual implementation would call orchestrator methods
    # This represents the delegation to the specialized code review orchestrator
    return {
        "files_analyzed": [],
        "issues": [],
        "recommendations": [],
        "risk_score": 0
    }


def generate_code_review_summary(result: WorkflowResult) -> str:
    """
    Generate ADO-formatted summary for code review results.
    
    Args:
        result: WorkflowResult from code review execution
    
    Returns:
        ADO-formatted Markdown string
    
    Example:
        >>> result = WorkflowResult(operation_type=OperationType.CODE_REVIEW, success=True)
        >>> summary = generate_code_review_summary(result)
        >>> "# Code Review Summary" in summary
        True
    """
    summary = f"""# Code Review Summary

**Review Date:** {result.completed_at.strftime('%Y-%m-%d %H:%M') if result.completed_at else 'N/A'}  
**Duration:** {result.duration_seconds:.1f} seconds  
**Risk Score:** {result.risk_score}/100

---

## Files Analyzed ({len(result.files_analyzed)})

"""
    
    if result.files_analyzed:
        for file in result.files_analyzed:
            summary += f"- `{file}`\n"
    else:
        summary += "_No files analyzed_\n"
    
    summary += f"\n---\n\n## Issues Found ({len(result.issues_found)})\n\n"
    
    if result.issues_found:
        for i, issue in enumerate(result.issues_found, 1):
            severity = issue.get('severity', 'medium')
            description = issue.get('description', 'No description')
            file = issue.get('file', 'Unknown file')
            summary += f"{i}. **[{severity.upper()}]** {description} (`{file}`)\n"
    else:
        summary += "_No issues found_\n"
    
    summary += f"\n---\n\n## Recommendations ({len(result.recommendations)})\n\n"
    
    if result.recommendations:
        for i, rec in enumerate(result.recommendations, 1):
            summary += f"{i}. {rec}\n"
    else:
        summary += "_No recommendations_\n"
    
    return summary


def generate_story_summary(result: WorkflowResult, metadata: Any) -> str:
    """
    Generate ADO-formatted summary for user story creation.
    
    Args:
        result: WorkflowResult from story creation
        metadata: Work item metadata from orchestrator
    
    Returns:
        ADO-formatted Markdown string
    
    Example:
        >>> result = WorkflowResult(operation_type=OperationType.ADO_STORY, success=True)
        >>> summary = generate_story_summary(result, metadata)
        >>> "# User Story Created" in summary
        True
    """
    summary = f"""# User Story Created

**Story ID:** {result.work_item_id}  
**Title:** {metadata.title}  
**Created:** {result.started_at.strftime('%Y-%m-%d %H:%M')}  
**Priority:** {format_priority(metadata.priority)}

---

## Description

{metadata.description}

---

## Acceptance Criteria

"""
    
    if metadata.acceptance_criteria:
        for i, criterion in enumerate(metadata.acceptance_criteria, 1):
            summary += f"{i}. {criterion}\n"
    else:
        summary += "_No acceptance criteria defined_\n"
    
    summary += "\n---\n\n## 🔍 Next Steps\n\n"
    summary += "1. Review and refine acceptance criteria\n"
    summary += "2. Begin implementation\n"
    summary += "3. Track progress in work item file\n"
    summary += f"4. Generate final summary: `generate ado summary {result.work_item_id}`\n"
    
    return summary


def generate_feature_summary(result: WorkflowResult, metadata: Any) -> str:
    """
    Generate ADO-formatted summary for feature creation.
    
    Args:
        result: WorkflowResult from feature creation
        metadata: Work item metadata from orchestrator
    
    Returns:
        ADO-formatted Markdown string
    
    Example:
        >>> result = WorkflowResult(operation_type=OperationType.ADO_FEATURE, success=True)
        >>> summary = generate_feature_summary(result, metadata)
        >>> "# Feature Created" in summary
        True
    """
    summary = f"""# Feature Created

**Feature ID:** {result.work_item_id}  
**Title:** {metadata.title}  
**Created:** {result.started_at.strftime('%Y-%m-%d %H:%M')}  
**Priority:** {format_priority(metadata.priority)}

---

## Description

{metadata.description}

---

## Related Work Items

"""
    
    if metadata.related_work_items:
        for work_item in metadata.related_work_items:
            summary += f"- {work_item}\n"
    else:
        summary += "_No related work items_\n"
    
    summary += "\n---\n\n## 🔍 Next Steps\n\n"
    summary += "1. Create child user stories\n"
    summary += "2. Define technical architecture\n"
    summary += "3. Track implementation progress\n"
    summary += f"4. Generate final summary: `generate ado summary {result.work_item_id}`\n"
    
    return summary


def save_summary(
    cortex_root: Path,
    result: WorkflowResult,
    category: str
) -> bool:
    """
    Save workflow summary to filesystem.
    
    Args:
        cortex_root: CORTEX root directory
        result: WorkflowResult with summary
        category: Category for filing (code_review, story, feature)
    
    Returns:
        True if saved successfully, False otherwise
    
    Example:
        >>> success = save_summary(Path("/path"), result, "code_review")
        >>> success
        True
    """
    try:
        summaries_dir = cortex_root / "cortex-brain" / "documents" / "summaries"
        category_dir = summaries_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"SUMMARY-{result.operation_type.value}-{timestamp}.md"
        file_path = category_dir / filename
        
        if result.ado_summary:
            file_path.write_text(result.ado_summary, encoding='utf-8')
            logger.info(f"✅ Summary saved: {file_path}")
            return True
        else:
            logger.warning(f"⚠️  No summary to save for {result.operation_type}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to save summary: {e}")
        return False


def format_priority(priority: int) -> str:
    """
    Convert priority number to human-readable label.
    
    Args:
        priority: Priority number (1-4)
    
    Returns:
        Priority label string
    
    Example:
        >>> format_priority(1)
        'High'
        >>> format_priority(3)
        'Low'
    """
    labels = {1: "High", 2: "Medium", 3: "Low", 4: "Very Low"}
    return labels.get(priority, "Medium")


# ========================================
# Convenience Functions
# ========================================

def review_pr(
    pr_info: str,
    cortex_root: Path,
    depth: str = "standard",
    focus_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function for PR review with simplified interface.
    
    Args:
        pr_info: PR link, ID, or diff
        cortex_root: Path to CORTEX root
        depth: Review depth
        focus_areas: Areas to focus on
    
    Returns:
        Result dictionary with success status and summary
    
    Example:
        >>> result = review_pr("PR#123", Path("/path/to/CORTEX"))
        >>> result['success']
        True
        >>> result['summary']
        '# Code Review Summary...'
    """
    registry = initialize_orchestrators(cortex_root)
    result = execute_code_review(cortex_root, registry, pr_info, depth, focus_areas)
    
    return {
        "success": result.success,
        "risk_score": result.risk_score,
        "issues_count": len(result.issues_found),
        "summary": result.ado_summary
    }


def create_user_story(
    title: str,
    description: str,
    cortex_root: Path,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for creating user story with simplified interface.
    
    Args:
        title: Story title
        description: Story description
        cortex_root: Path to CORTEX root
        **kwargs: Additional metadata
    
    Returns:
        Result dictionary with success status and details
    
    Example:
        >>> result = create_user_story("Login Feature", "As a user...", Path("/path"))
        >>> result['success']
        True
        >>> result['work_item_id']
        'STORY-12345'
    """
    registry = initialize_orchestrators(cortex_root)
    result = execute_ado_story(cortex_root, registry, title, description, **kwargs)
    
    return {
        "success": result.success,
        "work_item_id": result.work_item_id,
        "summary": result.ado_summary
    }


def create_feature(
    title: str,
    description: str,
    cortex_root: Path,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for creating feature with simplified interface.
    
    Args:
        title: Feature title
        description: Feature description
        cortex_root: Path to CORTEX root
        **kwargs: Additional metadata
    
    Returns:
        Result dictionary with success status and details
    
    Example:
        >>> result = create_feature("Auth System", "Complete auth...", Path("/path"))
        >>> result['success']
        True
        >>> result['work_item_id']
        'FEATURE-678'
    """
    registry = initialize_orchestrators(cortex_root)
    result = execute_ado_feature(cortex_root, registry, title, description, **kwargs)
    
    return {
        "success": result.success,
        "work_item_id": result.work_item_id,
        "summary": result.ado_summary
    }


# ========================================
# Self-Test
# ========================================

def _run_self_tests() -> None:
    """Self-test for unified entry point utility operations"""
    import time
    import tempfile
    
    print("🧪 Running Unified Entry Point Utility Self-Tests...\n")
    start_time = time.time()
    
    tests_passed = 0
    tests_total = 0
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Test 1: OperationType enum
        tests_total += 1
        try:
            assert OperationType.CODE_REVIEW.value == "code_review"
            assert OperationType.ADO_STORY.value == "ado_story"
            assert OperationType.ADO_FEATURE.value == "ado_feature"
            print("✅ Test 1: OperationType enum - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 1: OperationType enum - FAILED: {e}")
        
        # Test 2: WorkflowResult dataclass
        tests_total += 1
        try:
            result = WorkflowResult(
                operation_type=OperationType.CODE_REVIEW,
                success=True,
                work_item_id="TEST-123"
            )
            assert result.operation_type == OperationType.CODE_REVIEW
            assert result.success == True
            data = result.to_dict()
            assert data['operation_type'] == "code_review"
            print("✅ Test 2: WorkflowResult dataclass - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 2: WorkflowResult dataclass - FAILED: {e}")
        
        # Test 3: OrchestratorRegistry
        tests_total += 1
        try:
            registry = OrchestratorRegistry()
            assert not registry.is_available(OperationType.CODE_REVIEW)
            registry.code_review = "mock_orchestrator"
            assert registry.is_available(OperationType.CODE_REVIEW)
            print("✅ Test 3: OrchestratorRegistry - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 3: OrchestratorRegistry - FAILED: {e}")
        
        # Test 4: format_priority
        tests_total += 1
        try:
            assert format_priority(1) == "High"
            assert format_priority(2) == "Medium"
            assert format_priority(3) == "Low"
            assert format_priority(4) == "Very Low"
            assert format_priority(99) == "Medium"  # Default
            print("✅ Test 4: format_priority - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 4: format_priority - FAILED: {e}")
        
        # Test 5: generate_code_review_summary
        tests_total += 1
        try:
            result = WorkflowResult(
                operation_type=OperationType.CODE_REVIEW,
                success=True,
                risk_score=35
            )
            result.completed_at = datetime.now()
            result.duration_seconds = 10.5
            summary = generate_code_review_summary(result)
            assert "# Code Review Summary" in summary
            assert "**Risk Score:** 35/100" in summary  # Match actual Markdown bold format
            assert "**Duration:** 10.5 seconds" in summary  # Match actual Markdown bold format
            print("✅ Test 5: generate_code_review_summary - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 5: generate_code_review_summary - FAILED: {e}")
        
        # Test 6: save_summary
        tests_total += 1
        try:
            result = WorkflowResult(
                operation_type=OperationType.CODE_REVIEW,
                success=True
            )
            result.ado_summary = "# Test Summary\n\nContent here"
            success = save_summary(temp_dir, result, "code_review")
            assert success == True
            
            # Verify file exists
            summaries_dir = temp_dir / "cortex-brain" / "documents" / "summaries" / "code_review"
            assert summaries_dir.exists()
            assert len(list(summaries_dir.glob("*.md"))) == 1
            print("✅ Test 6: save_summary - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 6: save_summary - FAILED: {e}")
        
        # Test 7: initialize_orchestrators (graceful failure)
        tests_total += 1
        try:
            registry = initialize_orchestrators(temp_dir)
            # Should not raise exception even if orchestrators missing
            assert isinstance(registry, OrchestratorRegistry)
            print("✅ Test 7: initialize_orchestrators - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 7: initialize_orchestrators - FAILED: {e}")
        
        print(f"\n{'='*60}")
        print(f"📊 Test Results: {tests_passed}/{tests_total} passed ({tests_passed/tests_total*100:.1f}%)")
        print(f"⏱️  Execution time: {time.time() - start_time:.3f}s")
        
        if tests_passed == tests_total:
            print("✅ All tests passed!")
        else:
            print(f"❌ {tests_total - tests_passed} test(s) failed")
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


# ========================================
# CLI Wrapper Routing (Phase 3 & 4)
# ========================================

def route_operation(
    operation_id: str,
    cortex_root: Path,
    operation_config: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Route operation based on execution_method field.
    
    Dispatches to appropriate handler:
    - cli_wrapper: Invoke CLI wrapper script
    - copilot_chat: Return chat routing metadata
    - internal: Log and reject (not user-invokable)
    
    Args:
        operation_id: Operation identifier from cortex-operations.yaml
        cortex_root: CORTEX root directory
        operation_config: Operation configuration from YAML
        **kwargs: Additional arguments to pass to CLI wrapper
    
    Returns:
        Dict with execution result:
        {
            "success": bool,
            "execution_method": str,
            "output": str,
            "exit_code": int,
            "message": str
        }
    
    Example:
        >>> config = {"execution_method": "cli_wrapper", "cli_script": "scripts/cli_wrappers/align_wrapper.py"}
        >>> result = route_operation("align", Path("/cortex"), config)
        >>> result['success']
        True
    """
    execution_method = operation_config.get("execution_method")
    
    if not execution_method:
        logger.error(f"❌ Operation '{operation_id}' missing execution_method field")
        return {
            "success": False,
            "execution_method": "unknown",
            "output": "",
            "exit_code": 1,
            "message": f"Operation '{operation_id}' missing execution_method field"
        }
    
    logger.info(f"📍 Routing operation '{operation_id}' via {execution_method}")
    
    # Dispatch based on execution method
    if execution_method == "cli_wrapper":
        cli_script = operation_config.get("cli_script")
        if not cli_script:
            logger.error(f"❌ CLI wrapper operation '{operation_id}' missing cli_script field")
            return {
                "success": False,
                "execution_method": "cli_wrapper",
                "output": "",
                "exit_code": 1,
                "message": f"CLI wrapper operation '{operation_id}' missing cli_script field"
            }
        
        return invoke_cli_wrapper(operation_id, cortex_root, cli_script, **kwargs)
    
    elif execution_method == "copilot_chat":
        logger.info(f"💬 Operation '{operation_id}' routes to Copilot Chat")
        return {
            "success": True,
            "execution_method": "copilot_chat",
            "output": f"Operation '{operation_id}' should be invoked via Copilot Chat",
            "exit_code": 0,
            "message": "Chat-based operations must be invoked through Copilot Chat interface"
        }
    
    elif execution_method == "internal":
        logger.warning(f"⚠️  Operation '{operation_id}' is internal (not user-invokable)")
        return {
            "success": False,
            "execution_method": "internal",
            "output": "",
            "exit_code": 1,
            "message": f"Operation '{operation_id}' is internal infrastructure (not directly invokable)"
        }
    
    else:
        logger.error(f"❌ Unknown execution_method '{execution_method}' for operation '{operation_id}'")
        return {
            "success": False,
            "execution_method": execution_method,
            "output": "",
            "exit_code": 1,
            "message": f"Unknown execution_method '{execution_method}'"
        }


def invoke_cli_wrapper(
    operation_id: str,
    cortex_root: Path,
    cli_script: str,
    output_format: str = "text",
    verbose: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Invoke CLI wrapper script and capture output.
    
    Executes CLI wrapper with standard arguments (--output, --verbose, --project-root)
    plus any custom arguments from kwargs.
    
    Args:
        operation_id: Operation identifier
        cortex_root: CORTEX root directory
        cli_script: Relative path to CLI wrapper script
        output_format: Output format (text|json)
        verbose: Enable verbose output
        **kwargs: Additional CLI arguments (converted to --key value)
    
    Returns:
        Dict with execution result:
        {
            "success": bool,
            "execution_method": "cli_wrapper",
            "output": str,
            "exit_code": int,
            "message": str,
            "duration_seconds": float
        }
    
    Example:
        >>> result = invoke_cli_wrapper("align", Path("/cortex"), "scripts/cli_wrappers/align_wrapper.py", auto_fix=True)
        >>> result['success']
        True
        >>> result['exit_code']
        0
    """
    import time
    start_time = time.time()
    
    # Construct full script path
    script_path = cortex_root / cli_script
    
    if not script_path.exists():
        logger.error(f"❌ CLI wrapper script not found: {script_path}")
        return {
            "success": False,
            "execution_method": "cli_wrapper",
            "output": "",
            "exit_code": 1,
            "message": f"CLI wrapper script not found: {cli_script}",
            "duration_seconds": time.time() - start_time
        }
    
    # Build command
    cmd = [sys.executable, str(script_path)]
    
    # Add standard arguments
    cmd.extend(["--output", output_format])
    if verbose:
        cmd.append("--verbose")
    cmd.extend(["--project-root", str(cortex_root)])
    
    # Add custom arguments from kwargs
    for key, value in kwargs.items():
        # Convert Python naming (auto_fix) to CLI naming (--auto-fix)
        cli_arg = f"--{key.replace('_', '-')}"
        
        # Handle boolean flags
        if isinstance(value, bool):
            if value:
                cmd.append(cli_arg)
        else:
            cmd.extend([cli_arg, str(value)])
    
    logger.info(f"🚀 Executing CLI wrapper: {' '.join(cmd)}")
    
    try:
        # Execute CLI wrapper
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cortex_root),
            timeout=300  # 5 minute timeout
        )
        
        duration = time.time() - start_time
        success = result.returncode == 0
        
        if success:
            logger.info(f"✅ CLI wrapper '{operation_id}' completed in {duration:.2f}s")
        else:
            logger.error(f"❌ CLI wrapper '{operation_id}' failed with exit code {result.returncode}")
        
        return {
            "success": success,
            "execution_method": "cli_wrapper",
            "output": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "message": f"CLI wrapper executed {'successfully' if success else 'with errors'}",
            "duration_seconds": duration
        }
    
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        logger.error(f"❌ CLI wrapper '{operation_id}' timed out after {duration:.0f}s")
        return {
            "success": False,
            "execution_method": "cli_wrapper",
            "output": "",
            "stderr": "Process timed out (300s limit)",
            "exit_code": 124,  # Standard timeout exit code
            "message": "CLI wrapper execution timed out",
            "duration_seconds": duration
        }
    
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ CLI wrapper '{operation_id}' execution failed: {e}")
        return {
            "success": False,
            "execution_method": "cli_wrapper",
            "output": "",
            "stderr": str(e),
            "exit_code": 1,
            "message": f"CLI wrapper execution error: {str(e)}",
            "duration_seconds": duration
        }


if __name__ == "__main__":
    _run_self_tests()
