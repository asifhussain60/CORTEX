"""
Temporary Plan Manager for Planning Orchestrator v3.1

Manages temporary plans for implicit task requests (when user doesn't explicitly say "create a plan").
Handles the workflow: temporary plan → user approval → full master/slave plan → execution

Features:
- Automatic temporary plan creation for implicit requests
- Interactive back-and-forth refinement with user
- Approval tracking and documentation
- Conversion to full master/slave plan structure
- Plan folder lifecycle management (approved → active → completed)
- Knowledge extraction phase on completion

Integrates UnifiedPlanGenerator (Phase 13) for consistent master plan generation.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 3.2.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

from src.operations.modules.planning import (
    UnifiedPlanGenerator, TokenReductionTracker, PhaseLifecycleManager
)

logger = logging.getLogger(__name__)


@dataclass
class TemporaryPlan:
    """Represents a temporary plan during user interaction."""
    plan_id: str
    user_request: str
    complexity_tier: int  # 1-4
    estimated_time: str
    approach: str
    phases: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    user_feedback: List[Dict[str, str]] = field(default_factory=list)  # [{"timestamp": "...", "feedback": "..."}]
    approved: bool = False
    approval_timestamp: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'plan_id': self.plan_id,
            'user_request': self.user_request,
            'complexity_tier': self.complexity_tier,
            'estimated_time': self.estimated_time,
            'approach': self.approach,
            'phases': self.phases,
            'dependencies': self.dependencies,
            'risks': self.risks,
            'user_feedback': self.user_feedback,
            'approved': self.approved,
            'approval_timestamp': self.approval_timestamp.isoformat() if self.approval_timestamp else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemporaryPlan':
        """Create from dictionary."""
        return cls(
            plan_id=data['plan_id'],
            user_request=data['user_request'],
            complexity_tier=data['complexity_tier'],
            estimated_time=data['estimated_time'],
            approach=data['approach'],
            phases=data.get('phases', []),
            dependencies=data.get('dependencies', []),
            risks=data.get('risks', []),
            user_feedback=data.get('user_feedback', []),
            approved=data.get('approved', False),
            approval_timestamp=datetime.fromisoformat(data['approval_timestamp']) if data.get('approval_timestamp') else None,
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )


class TemporaryPlanManager:
    """
    Manages temporary plans for implicit task requests.
    
    Workflow:
    1. User provides tasks without saying "create a plan"
    2. CORTEX creates temporary plan in active/ folder
    3. Back-and-forth refinement with user
    4. User explicitly approves (or rejects)
    5. On approval: Create full master/slave plan structure
    6. Execute autonomously (default mode)
    7. On completion: Knowledge extraction → move to completed/
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize Temporary Plan Manager.
        
        Args:
            project_root: Path to project root (defaults to CWD)
        """
        self.project_root = project_root or Path.cwd()
        self.plans_base = self.project_root / "cortex-brain" / "documents" / "planning" / "features"
        self.active_dir = self.plans_base / "active"
        self.approved_dir = self.plans_base / "approved"
        self.completed_dir = self.plans_base / "completed"
        
        # Ensure directories exist
        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.approved_dir.mkdir(parents=True, exist_ok=True)
        self.completed_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize unified planning components (Phase 13)
        self.unified_generator = UnifiedPlanGenerator()
        self.token_tracker = TokenReductionTracker()
        self.phase_manager = PhaseLifecycleManager(self.unified_generator)
        
        logger.info("✅ TemporaryPlanManager v3.2 initialized with UnifiedPlanGenerator")
    
    def create_temporary_plan(
        self,
        user_request: str,
        complexity_tier: int,
        estimated_time: str,
        approach: str,
        phases: List[Dict[str, Any]] = None,
        dependencies: List[str] = None,
        risks: List[str] = None
    ) -> TemporaryPlan:
        """
        Create a temporary plan for implicit task request.
        
        Args:
            user_request: User's original request
            complexity_tier: Tier 1-4 from TieredRouter
            estimated_time: Estimated time from routing
            approach: Suggested approach
            phases: List of phase dictionaries
            dependencies: List of dependencies
            risks: List of risks
        
        Returns:
            TemporaryPlan object
        """
        # Generate plan ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        request_slug = user_request.lower().replace(' ', '-')[:30]
        plan_id = f"TEMP-PLAN-{timestamp}-{request_slug}"
        
        # Create plan object
        temp_plan = TemporaryPlan(
            plan_id=plan_id,
            user_request=user_request,
            complexity_tier=complexity_tier,
            estimated_time=estimated_time,
            approach=approach,
            phases=phases or [],
            dependencies=dependencies or [],
            risks=risks or []
        )
        
        # Create plan folder in active/
        plan_folder = self.active_dir / plan_id
        plan_folder.mkdir(parents=True, exist_ok=True)
        
        # Save temporary plan file
        self._save_temporary_plan(temp_plan, plan_folder)
        
        logger.info(f"Created temporary plan: {plan_id}")
        return temp_plan
    
    def update_temporary_plan(
        self,
        plan_id: str,
        user_feedback: str,
        updated_phases: Optional[List[Dict[str, Any]]] = None,
        updated_dependencies: Optional[List[str]] = None,
        updated_risks: Optional[List[str]] = None
    ) -> TemporaryPlan:
        """
        Update temporary plan based on user feedback.
        
        Args:
            plan_id: Plan identifier
            user_feedback: User's feedback/refinement
            updated_phases: Updated phases (if any)
            updated_dependencies: Updated dependencies (if any)
            updated_risks: Updated risks (if any)
        
        Returns:
            Updated TemporaryPlan
        """
        # Load existing plan
        temp_plan = self._load_temporary_plan(plan_id)
        
        # Add feedback
        temp_plan.user_feedback.append({
            'timestamp': datetime.now().isoformat(),
            'feedback': user_feedback
        })
        
        # Update fields if provided
        if updated_phases is not None:
            temp_plan.phases = updated_phases
        if updated_dependencies is not None:
            temp_plan.dependencies = updated_dependencies
        if updated_risks is not None:
            temp_plan.risks = updated_risks
        
        temp_plan.updated_at = datetime.now()
        
        # Save updated plan
        plan_folder = self.active_dir / plan_id
        self._save_temporary_plan(temp_plan, plan_folder)
        
        logger.info(f"Updated temporary plan: {plan_id}")
        return temp_plan
    
    def approve_temporary_plan(self, plan_id: str) -> TemporaryPlan:
        """
        Mark temporary plan as approved by user.
        
        Args:
            plan_id: Plan identifier
        
        Returns:
            Approved TemporaryPlan
        """
        # Load plan
        temp_plan = self._load_temporary_plan(plan_id)
        
        # Mark as approved
        temp_plan.approved = True
        temp_plan.approval_timestamp = datetime.now()
        temp_plan.updated_at = datetime.now()
        
        # Save approval to temporary plan file
        plan_folder = self.active_dir / plan_id
        self._save_temporary_plan(temp_plan, plan_folder)
        
        # Move folder from active/ to approved/
        approved_folder = self.approved_dir / plan_id
        plan_folder.rename(approved_folder)
        
        logger.info(f"✅ Approved temporary plan: {plan_id} (moved to approved/)")
        return temp_plan
    
    def convert_to_full_plan(self, plan_id: str) -> Path:
        """
        Convert approved temporary plan to full master/slave plan structure.
        
        Args:
            plan_id: Plan identifier (must be in approved/)
        
        Returns:
            Path to master plan file
        """
        # Load approved plan
        approved_folder = self.approved_dir / plan_id
        if not approved_folder.exists():
            raise FileNotFoundError(f"Approved plan not found: {plan_id}")
        
        temp_plan = self._load_temporary_plan(plan_id, folder=approved_folder)
        
        # Create standard plan structure folders
        (approved_folder / "context").mkdir(exist_ok=True)
        (approved_folder / "reports").mkdir(exist_ok=True)
        (approved_folder / "artifacts" / "copilot-chats").mkdir(parents=True, exist_ok=True)
        (approved_folder / "artifacts" / "user-preferences").mkdir(parents=True, exist_ok=True)
        (approved_folder / "tracking").mkdir(exist_ok=True)
        (approved_folder / "sub-plans").mkdir(exist_ok=True)
        
        # Generate master plan
        master_plan_path = approved_folder / "master-plan.md"
        master_plan_content = self._generate_master_plan(temp_plan)
        master_plan_path.write_text(master_plan_content, encoding='utf-8')
        
        # Generate sub-plans (slave plans) for each phase
        # Generate sub-plans (slave plans) for each phase
        for i, phase in enumerate(temp_plan.phases, 1):
            subplan_path = approved_folder / "sub-plans" / f"phase-{i:02d}-{phase.get('name', 'unnamed').lower().replace(' ', '-')}.md"
            subplan_content = self._generate_subplan(temp_plan, phase, i)
            subplan_path.write_text(subplan_content, encoding='utf-8')
        
        # Move from approved/ to active/ (ready for execution)
        active_folder = self.active_dir / plan_id
        if active_folder.exists():
            # Clean up old folder if exists
            import shutil
            shutil.rmtree(active_folder)
        approved_folder.rename(active_folder)
        
        logger.info(f"✅ Converted temporary plan to full master/slave structure: {plan_id} (moved to active/)")
        return active_folder / "master-plan.md"
    
    def mark_phase_in_progress(self, plan_id: str, phase_number: int):
        """
        Update master plan to mark phase as 'In Progress' using PhaseLifecycleManager.
        
        Args:
            plan_id: Plan identifier
            phase_number: Phase number (1-based)
        """
        master_plan_path = self.active_dir / plan_id / "master-plan.md"
        if not master_plan_path.exists():
            logger.warning(f"Master plan not found: {master_plan_path}")
            return
        
        result = self.phase_manager.start_phase(master_plan_path, phase_number)
        if result["success"]:
            logger.info(f"✅ Marked Phase {phase_number} as In Progress in {plan_id}")
        else:
            logger.error(f"Failed to start phase: {result.get('error')}")
    
    def mark_phase_complete(self, plan_id: str, phase_number: int, duration_hours: float = 0, tokens_saved: int = 0):
        """
        Update master plan to mark phase as 'Complete' using PhaseLifecycleManager.
        
        Args:
            plan_id: Plan identifier
            phase_number: Phase number (1-based)
            duration_hours: Actual time spent (hours)
            tokens_saved: Tokens saved in this phase
        """
        from datetime import timedelta
        
        master_plan_path = self.active_dir / plan_id / "master-plan.md"
        if not master_plan_path.exists():
            logger.warning(f"Master plan not found: {master_plan_path}")
            return
        
        result = self.phase_manager.complete_phase(
            master_plan_path=master_plan_path,
            phase_number=phase_number,
            duration=timedelta(hours=duration_hours),
            tokens_saved=tokens_saved
        )
        
        if result["success"]:
            logger.info(f"✅ Marked Phase {phase_number} as Complete in {plan_id} + updated continuation prompt")
        else:
            logger.error(f"Failed to complete phase: {result.get('error')}")
    
    def _update_continuation_prompt(self, content: str, plan_id: str, completed_phase: int) -> str:
        """
        Update continuation prompt after phase completion.
        
        Args:
            content: Current master plan content
            plan_id: Plan identifier
            completed_phase: Phase number just completed
        
        Returns:
            Updated content with new continuation prompt
        """
        import re
        
        # Extract phase information
        total_phases_match = re.search(r'(\d+)/(\d+) Phases Complete', content)
        if not total_phases_match:
            return content
        
        completed_phases = int(total_phases_match.group(1))
        total_phases = int(total_phases_match.group(2))
        
        # Determine next phase
        next_phase = completed_phases + 1
        
        if next_phase > total_phases:
            # All phases complete
            new_prompt = f"""## 🔄 Continuation Prompt

**WORK COMPLETE** - All {total_phases} phases finished! Plan ready for completion review.

```markdown
Plan `{plan_id}` is complete ({total_phases}/{total_phases} phases). Run knowledge extraction and move to completed/. Review: `cortex-brain/documents/planning/features/active/{plan_id}/master-plan.md`
```
"""
        else:
            # Get next phase name from table
            phase_table_match = re.search(rf'\| {next_phase} \| \[(.*?)\]\(', content)
            next_phase_name = phase_table_match.group(1) if phase_table_match else f"Phase {next_phase}"
            
            new_prompt = f"""## 🔄 Continuation Prompt

**COPY-PASTE THIS TO RESUME WORK:**

```markdown
Continue work on plan `{plan_id}`. Current status: {completed_phases}/{total_phases} phases complete. Phase {completed_phase} DONE. Next: Execute Phase {next_phase} ({next_phase_name}). Master plan: `cortex-brain/documents/planning/features/active/{plan_id}/master-plan.md`. Follow TDD workflow (RED→GREEN→REFACTOR). Update continuation prompt after phase completion.
```
"""
        
        # Replace old prompt
        prompt_pattern = r'## 🔄 Continuation Prompt.*?(?=---|$)'
        content = re.sub(prompt_pattern, new_prompt, content, flags=re.DOTALL)
        
        return content
    
    def complete_plan(self, plan_id: str, extract_knowledge: bool = True) -> Path:
        """
        Mark plan as complete and optionally extract knowledge.
        
        Args:
            plan_id: Plan identifier
            extract_knowledge: Whether to run knowledge extraction phase
        
        Returns:
            Path to completed plan folder
        """
        active_folder = self.active_dir / plan_id
        if not active_folder.exists():
            raise FileNotFoundError(f"Active plan not found: {plan_id}")
        
        # Extract knowledge before completion
        if extract_knowledge:
            self._extract_knowledge(plan_id, active_folder)
        
        # Move from active/ to completed/
        completed_folder = self.completed_dir / plan_id
        if completed_folder.exists():
            import shutil
            shutil.rmtree(completed_folder)
        active_folder.rename(completed_folder)
        
        logger.info(f"🎉 Plan completed and moved to completed/: {plan_id}")
        return completed_folder
    
    def _extract_knowledge(self, plan_id: str, plan_folder: Path):
        """
        Extract knowledge from completed plan and update CORTEX brain.
        
        Extracts:
        - Patterns and best practices
        - Lessons learned
        - Complexity estimations
        - Time estimates vs. actuals
        - Common pitfalls
        
        Args:
            plan_id: Plan identifier
            plan_folder: Path to plan folder
        """
        logger.info(f"🧠 Extracting knowledge from plan: {plan_id}")
        
        try:
            # Import knowledge graph updater
            from src.operations.utilities.knowledge_graph_auto_updater import KnowledgeGraphAutoUpdater
            
            updater = KnowledgeGraphAutoUpdater(self.project_root)
            
            # Extract from master plan
            master_plan_path = plan_folder / "master-plan.md"
            if master_plan_path.exists():
                master_content = master_plan_path.read_text(encoding='utf-8')
                
                # Extract key learnings
                learnings = self._extract_learnings_from_plan(master_content)
                
                # Update knowledge graph - check method availability
                if hasattr(updater, 'add_pattern'):
                    for learning in learnings:
                        updater.add_pattern(
                            pattern_type='planning_strategy',
                            pattern_name=learning['pattern'],
                            description=learning['description'],
                            context={'plan_id': plan_id, 'source': 'planning_orchestrator'}
                        )
                else:
                    # Fallback: just log learnings if API not available
                    logger.info(f"Knowledge extraction: {len(learnings)} learnings found (API unavailable)")
                    for learning in learnings:
                        logger.debug(f"  - {learning['pattern']}: {learning['description']}")
            
            # Extract from sub-plans
            subplans_dir = plan_folder / "sub-plans"
            if subplans_dir.exists():
                for subplan_file in subplans_dir.glob("*.md"):
                    subplan_content = subplan_file.read_text(encoding='utf-8')
                    phase_learnings = self._extract_learnings_from_plan(subplan_content)
                    
                    if hasattr(updater, 'add_pattern'):
                        for learning in phase_learnings:
                            updater.add_pattern(
                                pattern_type='implementation_strategy',
                                pattern_name=learning['pattern'],
                                description=learning['description'],
                                context={'plan_id': plan_id, 'phase': subplan_file.stem, 'source': 'planning_orchestrator'}
                            )
                    else:
                        learnings.extend(phase_learnings)
            
            # Save knowledge extraction report (always save, even if API unavailable)
            report_path = plan_folder / "knowledge-extraction-report.md"
            report_content = self._generate_knowledge_report(plan_id, learnings)
            report_path.write_text(report_content, encoding='utf-8')
            
            logger.info(f"✅ Knowledge extraction complete for {plan_id}")
            
        except Exception as e:
            logger.error(f"Knowledge extraction failed for {plan_id}: {e}", exc_info=True)
    
    def _extract_learnings_from_plan(self, plan_content: str) -> List[Dict[str, str]]:
        """
        Extract learnings from plan content using pattern recognition.
        
        Args:
            plan_content: Plan markdown content
        
        Returns:
            List of learning dictionaries with 'pattern' and 'description'
        """
        learnings = []
        
        # Simple pattern: Look for sections with "Lessons Learned", "Best Practices", "Pitfalls"
        import re
        
        # Extract lessons learned
        lessons_match = re.search(r'## Lessons Learned\s+(.*?)(?=##|\Z)', plan_content, re.DOTALL)
        if lessons_match:
            lessons_text = lessons_match.group(1).strip()
            for line in lessons_text.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('*'):
                    lesson = line.lstrip('-*').strip()
                    if lesson:
                        learnings.append({
                            'pattern': f"Lesson: {lesson[:50]}...",
                            'description': lesson
                        })
        
        # Extract best practices
        practices_match = re.search(r'## Best Practices\s+(.*?)(?=##|\Z)', plan_content, re.DOTALL)
        if practices_match:
            practices_text = practices_match.group(1).strip()
            for line in practices_text.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('*'):
                    practice = line.lstrip('-*').strip()
                    if practice:
                        learnings.append({
                            'pattern': f"Best Practice: {practice[:50]}...",
                            'description': practice
                        })
        
        return learnings
    
    def _generate_knowledge_report(self, plan_id: str, learnings: List[Dict[str, str]]) -> str:
        """Generate knowledge extraction report."""
        report = f"""# Knowledge Extraction Report

**Plan ID:** {plan_id}  
**Extracted:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Learnings Extracted

"""
        for i, learning in enumerate(learnings, 1):
            report += f"{i}. **{learning['pattern']}**\n   {learning['description']}\n\n"
        
        report += f"""
---

**Total Learnings:** {len(learnings)}  
**Status:** ✅ Successfully extracted and added to CORTEX knowledge graph
"""
        return report
    
    def _save_temporary_plan(self, temp_plan: TemporaryPlan, plan_folder: Path):
        """Save temporary plan to JSON file."""
        temp_file = plan_folder / "temporary-plan.json"
        temp_file.write_text(json.dumps(temp_plan.to_dict(), indent=2), encoding='utf-8')
    
    def _load_temporary_plan(self, plan_id: str, folder: Optional[Path] = None) -> TemporaryPlan:
        """Load temporary plan from JSON file."""
        if folder is None:
            folder = self.active_dir / plan_id
        
        temp_file = folder / "temporary-plan.json"
        if not temp_file.exists():
            raise FileNotFoundError(f"Temporary plan file not found: {temp_file}")
        
        data = json.loads(temp_file.read_text(encoding='utf-8'))
        return TemporaryPlan.from_dict(data)
    
    def _generate_master_plan(self, temp_plan: TemporaryPlan) -> str:
        """Generate master plan using UnifiedPlanGenerator (Phase 13)."""
        # Prepare metadata
        metadata = {
            "date": temp_plan.created_at.strftime("%B %d, %Y"),
            "complexity_tier": temp_plan.complexity_tier,
            "summary": temp_plan.approach,
            "baseline_tokens": 0,  # Will be established separately
            "current_tokens": 0,
            "total_files": 0
        }
        
        # Convert phases to unified format
        unified_phases = []
        for idx, phase in enumerate(temp_plan.phases, 1):
            unified_phases.append({
                "id": idx,
                "name": phase.get("name", f"Phase {idx}"),
                "status": "pending",
                "actual": phase.get("actual_time", "-"),
                "elapsed": phase.get("elapsed_time", "-"),
                "tokens_saved": phase.get("tokens", "-")
            })
        
        # Generate using UnifiedPlanGenerator
        return self.unified_generator.generate_master_plan(
            plan_id=temp_plan.plan_id,
            phases=unified_phases,
            metadata=metadata,
            include_token_tracking=True,
            include_visual_tracker=True,
            include_continuation_prompt=True
        )
    
    def _tier_to_label(self, tier: int) -> str:
        """Convert complexity tier to label."""
        labels = {
            1: "Simple - Instant",
            2: "Medium - Lightweight",
            3: "High - Documented",
            4: "Complex - Incremental"
        }
        return labels.get(tier, "Unknown")
    
    def _generate_subplan(self, temp_plan: TemporaryPlan, phase: Dict[str, Any], phase_number: int) -> str:
        """Generate sub-plan markdown for a specific phase."""
        content = f"""# Sub-Plan: Phase {phase_number} - {phase.get('name', 'Unnamed Phase')}

**Plan ID:** {temp_plan.plan_id}  
**Phase:** {phase_number}/{len(temp_plan.phases)}

---

## Phase Description

{phase.get('description', 'No description')}

---

## Tasks

"""
        for i, task in enumerate(phase.get('tasks', []), 1):
            content += f"{i}. {task}\n"
        
        content += """
---

## Deliverables

"""
        for deliverable in phase.get('deliverables', []):
            content += f"- {deliverable}\n"
        
        content += """
---

## Acceptance Criteria

"""
        for criterion in phase.get('acceptance_criteria', []):
            content += f"- {criterion}\n"
        
        return content
