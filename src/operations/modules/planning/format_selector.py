"""
Plan Format Selector - Intelligent Plan Structure Selection
============================================================

GREEN PHASE - Minimal Implementation

Purpose:
- Decide between single-file vs master/sub-plan structure
- Use cortex-evolution-v3.9 requirements for complex plans
- Match phase count threshold (<=5 single-file, >5 master-plan)

Compliance:
- Master plan requirements (ASCII header, progress tracker, phase tables)
- TDD GREEN_PHASE_VALIDATION

Author: CORTEX TDD System
Date: December 16, 2025
Status: GREEN PHASE
"""

from typing import Dict, Any, Literal
import logging

logger = logging.getLogger(__name__)


class PlanFormatSelector:
    """
    Selects appropriate plan format based on complexity.
    
    Rules:
    - <=5 phases: Single-file plan
    - >5 phases: Master plan + sub-plans
    - <3 files affected: Single-file
    - >=3 files affected: Master plan
    """
    
    def __init__(self):
        """Initialize format selector."""
        self.phase_threshold = 5
        self.file_threshold = 3
        logger.info("🎯 PlanFormatSelector initialized")
    
    def select_format(self, plan_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select plan format based on complexity metrics.
        
        Args:
            plan_metadata: Dictionary with keys:
                - complexity_tier (int): 1-4
                - task_count (int): Number of tasks
                - phase_count (int, optional): Number of phases
                - has_subcomponents (bool, optional): Nested dependencies
                - estimated_hours (int, optional): Estimated hours
            
        Returns:
            Dictionary with format decision:
            {
                'format': 'single_file' | 'master_subplan',
                'file_pattern': str (for single file),
                'master_file': str (for master plan),
                'subplan_pattern': str (for master plan)
            }
        """
        tier = plan_metadata.get('complexity_tier', 1)
        task_count = plan_metadata.get('task_count', 0)
        phase_count = plan_metadata.get('phase_count', 0)
        has_subcomponents = plan_metadata.get('has_subcomponents', False)
        
        logger.info(f"🎯 Selecting format: tier={tier}, tasks={task_count}, phases={phase_count}, deps={has_subcomponents}")
        
        # Rule 1: Dependencies always need master plan
        if has_subcomponents:
            logger.info("🎯 Format: master_subplan (has subcomponents)")
            return {
                'format': 'master_subplan',
                'master_file': 'MASTER-PLAN.md',
                'subplan_pattern': 'sub-plans/PHASE-{number}-{name}.md'
            }
        
        # Rule 2: Phase count threshold
        if phase_count > self.phase_threshold:
            logger.info(f"🎯 Format: master_subplan (phases > {self.phase_threshold})")
            return {
                'format': 'master_subplan',
                'master_file': 'MASTER-PLAN.md',
                'subplan_pattern': 'sub-plans/PHASE-{number}-{name}.md'
            }
        
        # Rule 3: Task count threshold (>10 tasks = master plan)
        if task_count > 10:
            logger.info(f"🎯 Format: master_subplan (tasks > 10)")
            return {
                'format': 'master_subplan',
                'master_file': 'MASTER-PLAN.md',
                'subplan_pattern': 'sub-plans/PHASE-{number}-{name}.md'
            }
        
        # Default: Single-file for simple plans
        logger.info("🎯 Format: single_file (simple plan)")
        return {
            'format': 'single_file',
            'file_pattern': 'PLAN-{date}-{feature}.md'
        }
    
    def get_format_requirements(self, format_type: Literal['single-file', 'master-plan']) -> Dict[str, Any]:
        """
        Get structure requirements for plan format.
        
        Args:
            format_type: 'single-file' or 'master-plan'
            
        Returns:
            Dictionary with structure requirements
        """
        if format_type == 'master-plan':
            return {
                'requires_ascii_header': True,
                'requires_progress_tracker': True,
                'requires_phase_tables': True,
                'requires_sub_plans': True,
                'folder_structure': {
                    'master': 'MASTER-PLAN.md',
                    'sub_plans': 'sub-plans/*.md',
                    'artifacts': 'artifacts/'
                }
            }
        else:
            return {
                'requires_ascii_header': False,
                'requires_progress_tracker': False,
                'requires_phase_tables': False,
                'requires_sub_plans': False,
                'folder_structure': {
                    'single_file': 'plan.md'
                }
            }
    
    def generate_master_plan(self, plan_metadata: Dict[str, Any], output_path=None) -> str:
        """
        Generate master plan content with ASCII art header.
        
        Args:
            plan_metadata: Plan metadata including feature_name, phase_count, phases
            output_path: Optional path to write file (for testing)
            
        Returns:
            Master plan markdown content with ASCII header
        """
        feature_name = plan_metadata.get('feature_name', 'FEATURE')
        phase_count = plan_metadata.get('phase_count', len(plan_metadata.get('phases', [])))
        phases = plan_metadata.get('phases', [])
        
        ascii_header = f"""
████████████████████████████████████████████████████████████████████████
█                      MASTER PLAN                                 █
█  {feature_name.center(66)}  █
████████████████████████████████████████████████████████████████████████
"""
        
        content = f"""{ascii_header}

## Overview

**Feature:** {feature_name}
**Phases:** {phase_count}
**Status:** Planning

## Visual Progress Tracker

"""
        
        # Progress tracker
        for i in range(phase_count):
            phase_name = phases[i] if i < len(phases) else f"Phase {i+1}"
            content += f"⬜ Phase {i+1}: {phase_name}\n"
        
        content += "\n## Phase Status Table\n\n| Phase | Status | Progress | Link |\n|-------|--------|----------|------|\n"
        
        for i in range(phase_count):
            phase_name = phases[i] if i < len(phases) else f"Phase {i+1}"
            content += f"| Phase {i+1} | ⏳ Pending | 0% | [phase-{i+1:02d}](sub-plans/PHASE-{i+1:02d}-{phase_name.lower().replace(' ', '-')}.md) |\n"
        
        content += "\n## Phase Breakdown\n\n"
        
        for i in range(phase_count):
            phase_name = phases[i] if i < len(phases) else f"Phase {i+1}"
            content += f"### Phase {i+1}: {phase_name}\n\nSee: `sub-plans/PHASE-{i+1:02d}-{phase_name.lower().replace(' ', '-')}.md`\n\n"
        
        # Write to file if path provided (for testing)
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return content
