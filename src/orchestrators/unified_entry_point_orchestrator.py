"""
Unified Entry Point Module for CORTEX Operations

Purpose:
- Single entry point for Code Review, ADO Work Items, and Planning
- Shared functionality between all operations
- Automatic summary generation with ADO formatting
- Orchestrates complete workflow from start to finish

Integration Points:
- CodeReviewOrchestrator - PR analysis
- ADOWorkItemOrchestrator - Work item management
- PlanningOrchestrator - Feature planning
- Shared summary generation for all workflows

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


class OperationType(Enum):
    """Types of operations supported by entry point."""
    CODE_REVIEW = "code_review"
    ADO_STORY = "ado_story"
    ADO_FEATURE = "ado_feature"
    PLANNING = "planning"


@dataclass
class WorkflowResult:
    """Result from a completed workflow."""
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


class UnifiedEntryPointOrchestrator:
    """
    Unified orchestrator for all CORTEX operations.
    
    Features:
    - Single entry point for code review, ADO work items, planning
    - Shared functionality between operations
    - Automatic summary generation
    - ADO-formatted output for direct copy-paste
    """
    
    def __init__(self, cortex_root: str):
        """
        Initialize unified orchestrator.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root)
        self.summaries_dir = self.cortex_root / "cortex-brain" / "documents" / "summaries"
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize sub-orchestrators
        self.code_review_orch = self._init_code_review()
        self.ado_work_item_orch = self._init_ado_work_item()
        self.planning_orch = self._init_planning()
    
    def _init_code_review(self):
        """Initialize code review orchestrator."""
        try:
            from src.orchestrators.code_review_orchestrator import CodeReviewOrchestrator
            return CodeReviewOrchestrator(str(self.cortex_root))
        except ImportError as e:
            logger.warning(f"Code review orchestrator not available: {e}")
            return None
    
    def _init_ado_work_item(self):
        """Initialize ADO work item orchestrator."""
        try:
            from src.orchestrators.ado_work_item_orchestrator import ADOWorkItemOrchestrator
            return ADOWorkItemOrchestrator(str(self.cortex_root))
        except ImportError as e:
            logger.warning(f"ADO work item orchestrator not available: {e}")
            return None
    
    def _init_planning(self):
        """Initialize planning orchestrator."""
        try:
            from src.orchestrators.planning_orchestrator import PlanningOrchestrator
            return PlanningOrchestrator(str(self.cortex_root))
        except ImportError as e:
            logger.warning(f"Planning orchestrator not available: {e}")
            return None
    
    def execute_code_review(self, 
                           pr_info: str,
                           depth: str = "standard",
                           focus_areas: Optional[List[str]] = None) -> WorkflowResult:
        """
        Execute code review workflow.
        
        Args:
            pr_info: PR link, ID, or diff text
            depth: Review depth (quick/standard/deep)
            focus_areas: Areas to focus on (security, performance, etc.)
        
        Returns:
            WorkflowResult with analysis and summary
        """
        result = WorkflowResult(
            operation_type=OperationType.CODE_REVIEW,
            success=False
        )
        
        try:
            if not self.code_review_orch:
                result.implementation_notes = "Code review orchestrator not available"
                return result
            
            # Execute code review
            start_time = datetime.now()
            
            # Parse PR info and run analysis
            # (This would call the actual code review orchestrator methods)
            review_result = self._perform_code_review(pr_info, depth, focus_areas)
            
            result.completed_at = datetime.now()
            result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
            
            # Extract results
            result.files_analyzed = review_result.get("files_analyzed", [])
            result.issues_found = review_result.get("issues", [])
            result.recommendations = review_result.get("recommendations", [])
            result.risk_score = review_result.get("risk_score", 0)
            
            # Generate summary
            result.ado_summary = self._generate_code_review_summary(result)
            result.success = True
            
            # Save summary
            self._save_summary(result, "code-review")
            
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            result.implementation_notes = f"Error: {str(e)}"
        
        return result
    
    def execute_ado_story(self,
                         title: str,
                         description: str,
                         acceptance_criteria: Optional[List[str]] = None,
                         **kwargs) -> WorkflowResult:
        """
        Create ADO user story and track implementation.
        
        Args:
            title: Story title
            description: Story description
            acceptance_criteria: List of acceptance criteria
            **kwargs: Additional metadata
        
        Returns:
            WorkflowResult with story details
        """
        result = WorkflowResult(
            operation_type=OperationType.ADO_STORY,
            success=False
        )
        
        try:
            if not self.ado_work_item_orch:
                result.implementation_notes = "ADO work item orchestrator not available"
                return result
            
            # Import work item type
            from src.orchestrators.ado_work_item_orchestrator import WorkItemType
            
            # Create story
            if acceptance_criteria:
                kwargs["acceptance_criteria"] = acceptance_criteria
            
            success, message, metadata = self.ado_work_item_orch.create_work_item(
                WorkItemType.STORY,
                title,
                description,
                **kwargs
            )
            
            if not success:
                result.implementation_notes = message
                return result
            
            result.work_item_id = metadata.work_item_id
            result.completed_at = datetime.now()
            result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
            result.success = True
            
            # Generate initial summary (will be updated when work completes)
            result.ado_summary = self._generate_story_summary(result, metadata)
            
        except Exception as e:
            logger.error(f"Story creation failed: {e}")
            result.implementation_notes = f"Error: {str(e)}"
        
        return result
    
    def execute_ado_feature(self,
                           title: str,
                           description: str,
                           related_stories: Optional[List[str]] = None,
                           **kwargs) -> WorkflowResult:
        """
        Create ADO feature and track implementation.
        
        Args:
            title: Feature title
            description: Feature description
            related_stories: List of related story IDs
            **kwargs: Additional metadata
        
        Returns:
            WorkflowResult with feature details
        """
        result = WorkflowResult(
            operation_type=OperationType.ADO_FEATURE,
            success=False
        )
        
        try:
            if not self.ado_work_item_orch:
                result.implementation_notes = "ADO work item orchestrator not available"
                return result
            
            # Import work item type
            from src.orchestrators.ado_work_item_orchestrator import WorkItemType
            
            # Create feature
            if related_stories:
                kwargs["related_work_items"] = related_stories
            
            success, message, metadata = self.ado_work_item_orch.create_work_item(
                WorkItemType.FEATURE,
                title,
                description,
                **kwargs
            )
            
            if not success:
                result.implementation_notes = message
                return result
            
            result.work_item_id = metadata.work_item_id
            result.completed_at = datetime.now()
            result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
            result.success = True
            
            # Generate initial summary
            result.ado_summary = self._generate_feature_summary(result, metadata)
            
        except Exception as e:
            logger.error(f"Feature creation failed: {e}")
            result.implementation_notes = f"Error: {str(e)}"
        
        return result
    
    def generate_work_summary(self, work_item_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Generate comprehensive work summary for ADO.
        
        Args:
            work_item_id: Work item identifier
        
        Returns:
            Tuple of (success, message, ado_markdown)
        """
        try:
            if not self.ado_work_item_orch:
                return False, "ADO work item orchestrator not available", None
            
            return self.ado_work_item_orch.generate_work_summary(work_item_id)
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return False, f"Error: {str(e)}", None
    
    # Private helper methods
    
    def _perform_code_review(self, pr_info: str, depth: str, focus_areas: Optional[List[str]]) -> Dict[str, Any]:
        """Perform code review analysis (placeholder for actual implementation)."""
        # This would call the actual code review orchestrator
        return {
            "files_analyzed": [],
            "issues": [],
            "recommendations": [],
            "risk_score": 0
        }
    
    def _generate_code_review_summary(self, result: WorkflowResult) -> str:
        """Generate ADO-formatted summary for code review."""
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
            for issue in result.issues_found:
                severity = issue.get("severity", "Unknown")
                description = issue.get("description", "")
                summary += f"- **{severity}**: {description}\n"
        else:
            summary += "_No issues found_\n"
        
        summary += f"\n---\n\n## Recommendations ({len(result.recommendations)})\n\n"
        
        if result.recommendations:
            for rec in result.recommendations:
                summary += f"- {rec}\n"
        else:
            summary += "_No recommendations_\n"
        
        summary += "\n---\n\n## Copy-Paste Instructions\n\n"
        summary += "1. Copy the content above\n"
        summary += "2. Paste into your ADO work item or PR comments\n"
        summary += "3. Address issues before merging\n"
        
        return summary
    
    def _generate_story_summary(self, result: WorkflowResult, metadata: Any) -> str:
        """Generate ADO-formatted summary for user story."""
        summary = f"""# User Story Created

**Story ID:** {result.work_item_id}  
**Title:** {metadata.title}  
**Created:** {result.started_at.strftime('%Y-%m-%d %H:%M')}  
**Priority:** {self._priority_label(metadata.priority)}

---

## Description

{metadata.description}

---

## Acceptance Criteria

"""
        
        if metadata.acceptance_criteria:
            for criterion in metadata.acceptance_criteria:
                summary += f"- [ ] {criterion}\n"
        else:
            summary += "_No acceptance criteria defined_\n"
        
        summary += "\n---\n\n## 🔍 Next Steps\n\n"
        summary += "1. Review and refine acceptance criteria\n"
        summary += "2. Begin implementation\n"
        summary += "3. Track progress in work item file\n"
        summary += f"4. Generate final summary: `generate ado summary {result.work_item_id}`\n"
        
        return summary
    
    def _generate_feature_summary(self, result: WorkflowResult, metadata: Any) -> str:
        """Generate ADO-formatted summary for feature."""
        summary = f"""# Feature Created

**Feature ID:** {result.work_item_id}  
**Title:** {metadata.title}  
**Created:** {result.started_at.strftime('%Y-%m-%d %H:%M')}  
**Priority:** {self._priority_label(metadata.priority)}

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
    
    def _save_summary(self, result: WorkflowResult, category: str):
        """Save summary to file."""
        try:
            category_dir = self.summaries_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"SUMMARY-{result.operation_type.value}-{timestamp}.md"
            file_path = category_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result.ado_summary)
            
            logger.info(f"Summary saved: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")
    
    def _priority_label(self, priority: int) -> str:
        """Convert priority number to label."""
        labels = {1: "High", 2: "Medium", 3: "Low", 4: "Very Low"}
        return labels.get(priority, "Medium")


# Convenience functions

def review_pr(pr_info: str, 
             cortex_root: str,
             depth: str = "standard",
             focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Convenience function for PR review.
    
    Args:
        pr_info: PR link, ID, or diff
        cortex_root: Path to CORTEX root
        depth: Review depth
        focus_areas: Areas to focus on
    
    Returns:
        Result dictionary with success status and summary
    """
    orchestrator = UnifiedEntryPointOrchestrator(cortex_root)
    result = orchestrator.execute_code_review(pr_info, depth, focus_areas)
    
    return {
        "success": result.success,
        "risk_score": result.risk_score,
        "issues_count": len(result.issues_found),
        "summary": result.ado_summary
    }


def create_user_story(title: str,
                     description: str,
                     cortex_root: str,
                     **kwargs) -> Dict[str, Any]:
    """
    Convenience function for creating user story.
    
    Args:
        title: Story title
        description: Story description
        cortex_root: Path to CORTEX root
        **kwargs: Additional metadata
    
    Returns:
        Result dictionary with success status and details
    """
    orchestrator = UnifiedEntryPointOrchestrator(cortex_root)
    result = orchestrator.execute_ado_story(title, description, **kwargs)
    
    return {
        "success": result.success,
        "work_item_id": result.work_item_id,
        "summary": result.ado_summary
    }


def create_feature(title: str,
                  description: str,
                  cortex_root: str,
                  **kwargs) -> Dict[str, Any]:
    """
    Convenience function for creating feature.
    
    Args:
        title: Feature title
        description: Feature description
        cortex_root: Path to CORTEX root
        **kwargs: Additional metadata
    
    Returns:
        Result dictionary with success status and details
    """
    orchestrator = UnifiedEntryPointOrchestrator(cortex_root)
    result = orchestrator.execute_ado_feature(title, description, **kwargs)
    
    return {
        "success": result.success,
        "work_item_id": result.work_item_id,
        "summary": result.ado_summary
    }
