"""
CORTEX Capacity Planning MCP Tool - Phase 12 Implementation.

Exposes capacity planning and estimation as MCP tool:
- cortex_estimate_capacity: Multi-model estimation (PERT, Story Points, CPM)

AC-IDs: CAP-001 through CAP-013
Author: Asif Hussain
Date: 2026-01-31
"""

import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from cortex.mcp.server import Tool, ToolDefinition, ToolParameter

logger = logging.getLogger(__name__)


class CORTEXEstimateCapacityTool(Tool):
    """Multi-model capacity estimation through integrated planning system."""

    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="cortex_estimate_capacity",
            description="Estimate project capacity using PERT, Story Points, and Critical Path Method with LENS complexity analysis",
            parameters=[
                ToolParameter(
                    name="task_description",
                    type="string",
                    required=True,
                    description="Natural language description of the task/feature to estimate"
                ),
                ToolParameter(
                    name="target_files",
                    type="array",
                    required=False,
                    description="Optional list of target file paths for complexity analysis"
                ),
                ToolParameter(
                    name="repo_path",
                    type="string",
                    required=False,
                    description="Path to repository for Git velocity analysis (defaults to current repo)"
                ),
                ToolParameter(
                    name="team_composition",
                    type="object",
                    required=False,
                    description="Optional team composition override: {senior: N, mid: N, junior: N}"
                ),
                ToolParameter(
                    name="complexity_hint",
                    type="string",
                    required=False,
                    description="Optional complexity hint: 'simple', 'moderate', 'complex', 'very_complex'"
                )
            ],
            metadata={
                "category": "capacity_planning",
                "version": "1.0",
                "phase": "12",
                "ac_ids": ["CAP-001", "CAP-002", "CAP-003", "CAP-004", "CAP-005"]
            }
        )

    def execute(
        self,
        task_description: str,
        target_files: Optional[List[str]] = None,
        repo_path: Optional[str] = None,
        team_composition: Optional[Dict[str, int]] = None,
        complexity_hint: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute capacity estimation with multi-model consensus."""
        try:
            from cortex.capacity.evidence_collector import EvidenceCollector
            from cortex.capacity.multi_model_estimation_engine import MultiModelEstimationEngine
            from cortex.capacity.skill_allocator import SkillAllocator
            from cortex.capacity.output_formatter import OutputFormatter
            from cortex.capacity.historical_learning import HistoricalLearning

            # Step 1: Collect evidence (AC-CAP-001)
            logger.info(f"AC-CAP-001: Collecting evidence for task: {task_description}")
            evidence_collector = EvidenceCollector()
            
            evidence_params = {
                "task_description": task_description,
                "target_files": target_files or [],
                "repo_path": Path(repo_path) if repo_path else Path.cwd()
            }
            
            evidence = evidence_collector.collect_evidence(**evidence_params)
            
            # Step 2: Multi-model estimation (AC-CAP-002, CAP-003, CAP-004, CAP-005)
            logger.info("AC-CAP-002-005: Running multi-model estimation")
            estimation_engine = MultiModelEstimationEngine()
            
            estimation = estimation_engine.estimate(
                evidence=evidence,
                complexity_hint=complexity_hint
            )
            
            # Step 3: Skill allocation (AC-CAP-006-008)
            logger.info("AC-CAP-006-008: Allocating team resources")
            skill_allocator = SkillAllocator()
            
            allocation = skill_allocator.allocate(
                estimation=estimation,
                team_composition=team_composition
            )
            
            # Step 4: Output formatting (AC-CAP-009-010)
            logger.info("AC-CAP-009-010: Formatting output")
            output_formatter = OutputFormatter()
            
            formatted_output = output_formatter.format(
                estimation=estimation,
                allocation=allocation
            )
            
            # Step 5: Historical learning tracking (AC-CAP-011-013)
            logger.info("AC-CAP-011-013: Recording estimate for learning")
            historical_learning = HistoricalLearning()
            
            estimate_id = historical_learning.record_estimate(
                task_description=task_description,
                estimation=estimation,
                allocation=allocation
            )
            
            return {
                "status": "success",
                "estimate_id": estimate_id,
                "evidence": {
                    "lens_complexity": evidence.get("complexity", {}),
                    "git_velocity": evidence.get("git_velocity", {}),
                    "domain_patterns": evidence.get("domain_patterns", {}),
                    "confidence_score": evidence.get("confidence_score", 0.0)
                },
                "estimation": {
                    "pert": estimation.get("pert", {}),
                    "story_points": estimation.get("story_points", {}),
                    "critical_path": estimation.get("critical_path", {}),
                    "consensus": estimation.get("consensus", {}),
                    "model_agreement": estimation.get("model_agreement", 0.0)
                },
                "allocation": {
                    "team_composition": allocation.get("team_composition", {}),
                    "task_assignments": allocation.get("task_assignments", []),
                    "brooks_law_overhead": allocation.get("brooks_law_overhead", 0.0)
                },
                "output": {
                    "sprint_breakdown": formatted_output.get("sprint_breakdown", []),
                    "gantt_chart": formatted_output.get("gantt_chart", {}),
                    "summary": formatted_output.get("summary", "")
                },
                "learning": {
                    "estimate_id": estimate_id,
                    "tracking_enabled": True,
                    "historical_accuracy": historical_learning.get_accuracy_metrics()
                }
            }

        except ImportError as e:
            logger.error(f"Phase 12 capacity module import failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Capacity planning modules not available: {str(e)}",
                "hint": "Ensure Phase 12 implementation is complete"
            }
        except Exception as e:
            logger.error(f"Capacity estimation failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Failed to estimate capacity: {str(e)}"
            }


# Register tool
CORTEX_CAPACITY_TOOLS = [
    CORTEXEstimateCapacityTool()
]
