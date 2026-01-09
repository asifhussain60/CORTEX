"""
Align Plan Sync - MCP Tool for Phase 7 Holistic Plan Synchronization.

This tool reviews AC YAML, remediation plan, and snowball strategy to either:
- Create a new plan (if none exists) following Planning Orchestrator structure
- Revise existing plan incorporating gaps, enhancements, and user requests

The goal is perfect alignment between AC ↔ requirements.yaml ↔ plan with
snowball optimization for maximum momentum building.

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-09
Correlation ID: AC-ALIGN-001
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger("cortex.mcp.align_plan_sync")


class AlignPlanSyncTool:
    """
    MCP Tool for Phase 7 - Holistic Plan Synchronization.
    
    Achieves perfect alignment between:
    - Acceptance Criteria (AC) YAML
    - Remediation Plan
    - Snowball Strategy
    - requirements.yaml
    - Plan structure (phases, tasks)
    
    Supports two modes:
    - create: Build new plan from scratch
    - revise: Update existing plan with gaps and enhancements
    """
    
    # MCP Tool Metadata
    NAME = "cortex_align_plan_sync"
    DESCRIPTION = "Holistic plan synchronization - creates or revises plan for snowball alignment"
    
    # Input Schema for MCP
    INPUT_SCHEMA = {
        "type": "object",
        "properties": {
            "ac_file": {
                "type": "string",
                "description": "Path to AC YAML file (supports glob patterns)"
            },
            "remediation_file": {
                "type": "string",
                "description": "Path to remediation-plan.yaml"
            },
            "snowball_file": {
                "type": "string",
                "description": "Path to snowball-strategy.yaml"
            },
            "plan_path": {
                "type": "string",
                "description": "Path to plan directory"
            },
            "mode": {
                "type": "string",
                "enum": ["auto", "create", "revise"],
                "description": "Mode: auto (detect), create (new plan), revise (update existing)"
            }
        },
        "required": ["ac_file", "remediation_file", "snowball_file", "plan_path"]
    }
    
    def __init__(self, cortex_brain_path: Optional[str] = None):
        """
        Initialize AlignPlanSyncTool.
        
        Args:
            cortex_brain_path: Path to cortex-brain directory
        """
        self.cortex_brain_path = cortex_brain_path or self._detect_brain_path()
        
    def _detect_brain_path(self) -> str:
        """Detect cortex-brain path from current directory."""
        cwd = Path.cwd()
        brain_path = cwd / "cortex-brain"
        if brain_path.exists():
            return str(brain_path)
        # Fall back to relative
        return "cortex-brain"
    
    def execute(
        self,
        ac_file: str,
        remediation_file: str,
        snowball_file: str,
        plan_path: str,
        mode: str = "auto"
    ) -> Dict[str, Any]:
        """
        Execute holistic plan synchronization.
        
        Args:
            ac_file: Path to AC YAML file
            remediation_file: Path to remediation-plan.yaml
            snowball_file: Path to snowball-strategy.yaml
            plan_path: Path to plan directory
            mode: "auto", "create", or "revise"
            
        Returns:
            Dict with sync results including action taken, counts, alignment status
        """
        logger.info(f"AlignPlanSync starting - mode: {mode}, plan_path: {plan_path}")
        
        try:
            # Step 1: Load all source files
            ac_data = self._load_ac(ac_file)
            remediation_data = self._load_yaml(remediation_file)
            snowball_data = self._load_yaml(snowball_file)
            
            # Step 2: Check plan existence
            plan_exists = self._check_plan_structure(plan_path)
            
            # Step 3: Determine mode
            if mode == "auto":
                mode = "revise" if plan_exists else "create"
            
            logger.info(f"Mode resolved to: {mode}, plan_exists: {plan_exists}")
            
            # Step 4: Execute appropriate action
            if mode == "create":
                result = self._create_new_plan(
                    ac_data, remediation_data, snowball_data, plan_path
                )
            else:
                result = self._revise_existing_plan(
                    ac_data, remediation_data, snowball_data, plan_path
                )
            
            # Step 5: Validate alignment
            alignment_status = self._validate_alignment(plan_path, ac_data)
            result["alignment_status"] = alignment_status
            result["snowball_optimized"] = True
            
            logger.info(f"AlignPlanSync complete: {result}")
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"AlignPlanSync failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_ac(self, ac_file: str) -> Dict[str, Any]:
        """Load AC YAML file (supports glob patterns)."""
        path = Path(ac_file)
        
        # Handle glob patterns
        if "*" in ac_file:
            parent = path.parent
            pattern = path.name
            matches = list(parent.glob(pattern))
            if not matches:
                raise FileNotFoundError(f"No AC files found matching: {ac_file}")
            path = matches[0]  # Use first match
        
        return self._load_yaml(str(path))
    
    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Load YAML file safely."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"YAML file not found: {file_path}")
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _save_yaml(self, file_path: str, data: Dict[str, Any]) -> None:
        """Save YAML file with proper formatting."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120
            )
        
        logger.info(f"Saved YAML: {file_path}")
    
    def _check_plan_structure(self, plan_path: str) -> bool:
        """Check if plan structure exists with required files."""
        path = Path(plan_path)
        
        # Check for plan indicators
        required_dirs = ["context", "tracking"]
        requirements_file = path / "context" / "requirements.yaml"
        
        has_dirs = all((path / d).exists() for d in required_dirs)
        has_requirements = requirements_file.exists()
        
        return has_dirs and has_requirements
    
    def _create_new_plan(
        self,
        ac_data: Dict[str, Any],
        remediation_data: Dict[str, Any],
        snowball_data: Dict[str, Any],
        plan_path: str
    ) -> Dict[str, Any]:
        """
        Create new plan following Planning Orchestrator v5 structure.
        
        Structure determined by scope:
        - Epic (>50 criteria, multi-phase): Full epic structure
        - Feature (<50 criteria, focused): Simple feature structure
        """
        logger.info(f"Creating new plan at: {plan_path}")
        
        # Count pending criteria
        criteria_count = self._count_pending_criteria(ac_data)
        
        # Determine structure
        if criteria_count > 50:
            structure = "epic"
            dirs = ["context", "artifacts", "reports", "tracking", "features"]
        else:
            structure = "feature"
            dirs = ["context", "artifacts", "reports", "tracking"]
        
        # Create directories
        path = Path(plan_path)
        for d in dirs:
            (path / d).mkdir(parents=True, exist_ok=True)
        
        # Generate requirements from AC + remediation
        requirements = self._generate_requirements(ac_data, remediation_data)
        
        # Apply snowball ordering
        requirements = self._apply_snowball_ordering(requirements, snowball_data)
        
        # Save requirements.yaml
        self._save_yaml(str(path / "context" / "requirements.yaml"), requirements)
        
        # Create progress tracker
        self._create_progress_tracker(plan_path, requirements)
        
        return {
            "action": "created",
            "structure": structure,
            "criteria_count": criteria_count,
            "requirements_count": len(requirements.get("requirements", [])),
            "phases_count": len(requirements.get("phases", []))
        }
    
    def _revise_existing_plan(
        self,
        ac_data: Dict[str, Any],
        remediation_data: Dict[str, Any],
        snowball_data: Dict[str, Any],
        plan_path: str
    ) -> Dict[str, Any]:
        """
        Revise existing plan incorporating gaps, enhancements, user requests.
        
        Steps:
        1. Load existing plan state
        2. Identify gaps (AC criteria not in plan)
        3. Identify enhancements (new remediation tasks)
        4. Merge into plan phases
        5. Reorder for snowball effect
        6. Update requirements.yaml
        7. Regenerate progress-tracker.json
        """
        logger.info(f"Revising existing plan at: {plan_path}")
        
        path = Path(plan_path)
        
        # Load existing requirements
        requirements_file = path / "context" / "requirements.yaml"
        existing_requirements = self._load_yaml(str(requirements_file))
        
        # Find gaps (AC criteria not in requirements)
        gaps = self._find_ac_gaps(ac_data, existing_requirements)
        
        # Find enhancements (new remediation tasks)
        enhancements = self._find_remediation_enhancements(
            remediation_data, existing_requirements
        )
        
        # Merge into requirements
        merged_requirements = self._merge_into_requirements(
            existing_requirements, gaps, enhancements
        )
        
        # Apply snowball reordering
        merged_requirements = self._apply_snowball_ordering(
            merged_requirements, snowball_data
        )
        
        # Save updated requirements
        self._save_yaml(str(requirements_file), merged_requirements)
        
        # Regenerate progress tracker
        self._create_progress_tracker(plan_path, merged_requirements)
        
        return {
            "action": "revised",
            "gaps_added": len(gaps),
            "enhancements_added": len(enhancements),
            "total_requirements": len(merged_requirements.get("requirements", [])),
            "total_phases": len(merged_requirements.get("phases", []))
        }
    
    def _count_pending_criteria(self, ac_data: Dict[str, Any]) -> int:
        """Count pending (not completed) acceptance criteria."""
        count = 0
        
        # Navigate through AC sections
        sections = ac_data.get("acceptance_criteria", {}).get("sections", [])
        for section in sections:
            subsections = section.get("subsections", [])
            for subsection in subsections:
                criteria = subsection.get("criteria", [])
                for criterion in criteria:
                    status = criterion.get("status", "NOT_STARTED")
                    if status != "COMPLETE":
                        count += 1
        
        return count
    
    def _generate_requirements(
        self,
        ac_data: Dict[str, Any],
        remediation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate requirements.yaml from AC + remediation."""
        requirements: List[Dict[str, Any]] = []
        phases: List[Dict[str, Any]] = []
        
        # Extract from AC
        sections = ac_data.get("acceptance_criteria", {}).get("sections", [])
        for section in sections:
            section_id = section.get("id", "")
            section_name = section.get("name", "")
            
            subsections = section.get("subsections", [])
            for subsection in subsections:
                subsection_id = subsection.get("id", "")
                subsection_name = subsection.get("name", "")
                
                criteria = subsection.get("criteria", [])
                for criterion in criteria:
                    if criterion.get("status", "NOT_STARTED") != "COMPLETE":
                        requirements.append({
                            "id": criterion.get("id", ""),
                            "description": criterion.get("name", ""),
                            "section": section_name,
                            "subsection": subsection_name,
                            "priority": criterion.get("priority", "P1_HIGH"),
                            "status": "pending",
                            "source": "AC"
                        })
        
        # Extract from remediation
        remediation_phases = remediation_data.get("phases", [])
        for phase in remediation_phases:
            tasks = phase.get("tasks", [])
            for task in tasks:
                requirements.append({
                    "id": task.get("id", ""),
                    "description": task.get("description", ""),
                    "section": phase.get("name", ""),
                    "priority": task.get("priority", "P1_HIGH"),
                    "status": "pending",
                    "source": "REMEDIATION",
                    "effort": task.get("effort", "")
                })
        
        # Create phases based on categories
        phase_map = self._group_by_phase(requirements)
        for phase_name, phase_reqs in phase_map.items():
            phases.append({
                "name": phase_name,
                "requirements": [r["id"] for r in phase_reqs],
                "status": "pending",
                "estimated_effort": self._calculate_effort(phase_reqs)
            })
        
        return {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "source": "AlignPlanSync",
                "version": "1.0.0"
            },
            "requirements": requirements,
            "phases": phases
        }
    
    def _find_ac_gaps(
        self,
        ac_data: Dict[str, Any],
        existing_requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find AC criteria not present in existing requirements."""
        gaps: List[Dict[str, Any]] = []
        
        # Get existing requirement IDs
        existing_ids = set()
        for req in existing_requirements.get("requirements", []):
            existing_ids.add(req.get("id", ""))
        
        # Check AC criteria
        sections = ac_data.get("acceptance_criteria", {}).get("sections", [])
        for section in sections:
            subsections = section.get("subsections", [])
            for subsection in subsections:
                criteria = subsection.get("criteria", [])
                for criterion in criteria:
                    criterion_id = criterion.get("id", "")
                    status = criterion.get("status", "NOT_STARTED")
                    
                    if criterion_id not in existing_ids and status != "COMPLETE":
                        gaps.append({
                            "id": criterion_id,
                            "description": criterion.get("name", ""),
                            "section": section.get("name", ""),
                            "subsection": subsection.get("name", ""),
                            "priority": criterion.get("priority", "P1_HIGH"),
                            "status": "pending",
                            "source": "AC_GAP"
                        })
        
        return gaps
    
    def _find_remediation_enhancements(
        self,
        remediation_data: Dict[str, Any],
        existing_requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find remediation tasks not in existing requirements."""
        enhancements: List[Dict[str, Any]] = []
        
        # Get existing requirement IDs
        existing_ids = set()
        for req in existing_requirements.get("requirements", []):
            existing_ids.add(req.get("id", ""))
        
        # Check remediation tasks
        phases = remediation_data.get("phases", [])
        for phase in phases:
            tasks = phase.get("tasks", [])
            for task in tasks:
                task_id = task.get("id", "")
                
                if task_id not in existing_ids:
                    enhancements.append({
                        "id": task_id,
                        "description": task.get("description", ""),
                        "section": phase.get("name", ""),
                        "priority": task.get("priority", "P1_HIGH"),
                        "status": "pending",
                        "source": "REMEDIATION_ENHANCEMENT",
                        "effort": task.get("effort", "")
                    })
        
        return enhancements
    
    def _merge_into_requirements(
        self,
        existing: Dict[str, Any],
        gaps: List[Dict[str, Any]],
        enhancements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge gaps and enhancements into existing requirements."""
        merged_requirements = existing.get("requirements", []).copy()
        
        # Add gaps
        merged_requirements.extend(gaps)
        
        # Add enhancements
        merged_requirements.extend(enhancements)
        
        # Update metadata
        existing["metadata"] = existing.get("metadata", {})
        existing["metadata"]["last_sync"] = datetime.now().isoformat()
        existing["metadata"]["gaps_added"] = len(gaps)
        existing["metadata"]["enhancements_added"] = len(enhancements)
        
        existing["requirements"] = merged_requirements
        
        # Regenerate phases
        phase_map = self._group_by_phase(merged_requirements)
        phases = []
        for phase_name, phase_reqs in phase_map.items():
            phases.append({
                "name": phase_name,
                "requirements": [r["id"] for r in phase_reqs],
                "status": "pending",
                "estimated_effort": self._calculate_effort(phase_reqs)
            })
        existing["phases"] = phases
        
        return existing
    
    def _apply_snowball_ordering(
        self,
        requirements: Dict[str, Any],
        snowball_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply snowball ordering for maximum momentum building."""
        
        # Get snowball execution order
        execution_order = snowball_data.get("execution_order", [])
        if not execution_order:
            # Default snowball order
            execution_order = [
                "BLOCKING",
                "FOUNDATION", 
                "CONCURRENCY",
                "SECURITY",
                "AUDIT",
                "PERFORMANCE",
                "QUALITY"
            ]
        
        # Create priority mapping
        order_map = {cat: idx for idx, cat in enumerate(execution_order)}
        
        # Sort requirements by snowball priority
        reqs = requirements.get("requirements", [])
        
        def snowball_key(req: Dict[str, Any]) -> Tuple[int, int, str]:
            # Get category from section name
            section = req.get("section", "").upper()
            
            # Map section to snowball category
            category = "QUALITY"  # Default
            for cat in execution_order:
                if cat in section:
                    category = cat
                    break
            
            # Priority order (P0=0, P1=1, P2=2)
            priority_str = req.get("priority", "P1_HIGH")
            priority_num = int(priority_str[1]) if priority_str.startswith("P") else 1
            
            return (order_map.get(category, 99), priority_num, req.get("id", ""))
        
        sorted_reqs = sorted(reqs, key=snowball_key)
        requirements["requirements"] = sorted_reqs
        
        # Reorder phases based on snowball
        phases = requirements.get("phases", [])
        
        def phase_snowball_key(phase: Dict[str, Any]) -> int:
            name = phase.get("name", "").upper()
            for cat in execution_order:
                if cat in name:
                    return order_map.get(cat, 99)
            return 99
        
        sorted_phases = sorted(phases, key=phase_snowball_key)
        requirements["phases"] = sorted_phases
        
        return requirements
    
    def _group_by_phase(self, requirements: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Group requirements into phases by section."""
        phase_map: Dict[str, List[Dict]] = {}
        
        for req in requirements:
            section = req.get("section", "General")
            
            # Simplify section name for phase
            phase_name = section.split(" - ")[0] if " - " in section else section
            
            if phase_name not in phase_map:
                phase_map[phase_name] = []
            phase_map[phase_name].append(req)
        
        return phase_map
    
    def _calculate_effort(self, requirements: List[Dict[str, Any]]) -> str:
        """Calculate total effort for a set of requirements."""
        total_hours = 0.0
        
        for req in requirements:
            effort = req.get("effort", "")
            if effort:
                # Parse effort string (e.g., "2h", "30m", "1.5h")
                if "h" in effort:
                    hours = float(effort.replace("h", "").strip())
                    total_hours += hours
                elif "m" in effort:
                    mins = float(effort.replace("m", "").strip())
                    total_hours += mins / 60
            else:
                # Default effort estimate by priority
                priority = req.get("priority", "P1_HIGH")
                if "P0" in priority:
                    total_hours += 4  # Critical items take longer
                elif "P1" in priority:
                    total_hours += 2
                else:
                    total_hours += 1
        
        if total_hours >= 1:
            return f"{total_hours:.1f}h"
        else:
            return f"{int(total_hours * 60)}m"
    
    def _create_progress_tracker(
        self,
        plan_path: str,
        requirements: Dict[str, Any]
    ) -> None:
        """Create or update progress-tracker.json."""
        import json
        
        path = Path(plan_path) / "tracking" / "progress-tracker.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        
        phases = requirements.get("phases", [])
        reqs = requirements.get("requirements", [])
        
        # Calculate statistics
        total = len(reqs)
        completed = sum(1 for r in reqs if r.get("status") == "complete")
        pending = total - completed
        
        tracker = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "source": "AlignPlanSync"
            },
            "summary": {
                "total_requirements": total,
                "completed": completed,
                "pending": pending,
                "progress_percent": round((completed / total * 100) if total > 0 else 0, 1)
            },
            "phases": [
                {
                    "name": phase.get("name"),
                    "requirements_count": len(phase.get("requirements", [])),
                    "status": phase.get("status", "pending"),
                    "estimated_effort": phase.get("estimated_effort", "")
                }
                for phase in phases
            ]
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(tracker, f, indent=2)
        
        logger.info(f"Created progress tracker: {path}")
    
    def _validate_alignment(
        self,
        plan_path: str,
        ac_data: Dict[str, Any]
    ) -> str:
        """Validate alignment between AC, requirements, and plan."""
        path = Path(plan_path)
        requirements_file = path / "context" / "requirements.yaml"
        
        if not requirements_file.exists():
            return "NOT_ALIGNED"
        
        requirements = self._load_yaml(str(requirements_file))
        req_ids = {r.get("id") for r in requirements.get("requirements", [])}
        
        # Check AC coverage
        missing = 0
        sections = ac_data.get("acceptance_criteria", {}).get("sections", [])
        for section in sections:
            subsections = section.get("subsections", [])
            for subsection in subsections:
                criteria = subsection.get("criteria", [])
                for criterion in criteria:
                    if criterion.get("status") != "COMPLETE":
                        if criterion.get("id") not in req_ids:
                            missing += 1
        
        if missing == 0:
            return "ALIGNED"
        elif missing < 5:
            return "MOSTLY_ALIGNED"
        else:
            return f"GAPS_DETECTED_{missing}"
    
    def to_mcp_tool(self) -> Dict[str, Any]:
        """Return MCP tool definition."""
        return {
            "name": self.NAME,
            "description": self.DESCRIPTION,
            "inputSchema": self.INPUT_SCHEMA
        }


# Convenience function for direct invocation
def align_plan_sync(
    ac_file: str,
    remediation_file: str,
    snowball_file: str,
    plan_path: str,
    mode: str = "auto"
) -> Dict[str, Any]:
    """
    Holistic plan synchronization - creates or revises plan for snowball alignment.
    
    Args:
        ac_file: Path to AC YAML file
        remediation_file: Path to remediation-plan.yaml
        snowball_file: Path to snowball-strategy.yaml
        plan_path: Path to plan directory
        mode: "auto", "create", or "revise"
        
    Returns:
        Dict with sync results
    """
    tool = AlignPlanSyncTool()
    return tool.execute(ac_file, remediation_file, snowball_file, plan_path, mode)


if __name__ == "__main__":
    # CLI interface for testing
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Align Plan Sync Tool")
    parser.add_argument("--ac-file", required=True, help="Path to AC YAML")
    parser.add_argument("--remediation-file", required=True, help="Path to remediation YAML")
    parser.add_argument("--snowball-file", required=True, help="Path to snowball YAML")
    parser.add_argument("--plan-path", required=True, help="Path to plan directory")
    parser.add_argument("--mode", default="auto", choices=["auto", "create", "revise"])
    
    args = parser.parse_args()
    
    result = align_plan_sync(
        ac_file=args.ac_file,
        remediation_file=args.remediation_file,
        snowball_file=args.snowball_file,
        plan_path=args.plan_path,
        mode=args.mode
    )
    
    print(json.dumps(result, indent=2))
