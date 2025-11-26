"""
YAML Planning Orchestrator for CORTEX
Addresses Gap #6: Plans stored in .md not .yaml

Purpose:
- Validates YAML plans against plan-schema.yaml
- Generates readable Markdown views from YAML
- Migrates existing .md plans to .yaml format
- Provides programmatic access to plan data

Author: GitHub Copilot
Created: 2024-01-15
"""

import os
import yaml
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from pathlib import Path
import logging
import re
from src.workflows.document_organizer import DocumentOrganizer
from src.workflows.incremental_plan_generator import IncrementalPlanGenerator
from src.workflows.streaming_plan_writer import CheckpointedPlanWriter

logger = logging.getLogger(__name__)


class PlanningOrchestrator:
    """Orchestrates YAML-based feature planning with validation and Markdown generation."""
    
    def __init__(self, cortex_root: str):
        """
        Initialize planning orchestrator.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root)
        self.schema_path = self.cortex_root / "cortex-brain" / "config" / "plan-schema.yaml"
        self.plans_dir = self.cortex_root / "cortex-brain" / "documents" / "planning" / "features"
        self.active_plans_dir = self.plans_dir / "active"
        self.completed_plans_dir = self.plans_dir / "completed"
        self.schema = self._load_schema()
        
        # NEW Sprint 2: Initialize document organizer
        brain_path = self.cortex_root / "cortex-brain"
        self.document_organizer = DocumentOrganizer(brain_path)
        
        # NEW Sprint 3: Initialize incremental planning components
        self.incremental_generator = IncrementalPlanGenerator(
            brain_path=str(brain_path),
            skeleton_token_limit=200,
            section_token_limit=500
        )
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load plan schema from YAML file."""
        try:
            if not self.schema_path.exists():
                logger.warning(f"Schema not found at {self.schema_path}, using minimal defaults")
                return self._get_default_schema()
            
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            return self._get_default_schema()
    
    def _get_default_schema(self) -> Dict[str, Any]:
        """Return minimal default schema if file not found."""
        return {
            "schema": {
                "version": "1.0.0",
                "required_fields": ["metadata", "phases", "definition_of_ready", "definition_of_done"]
            }
        }
    
    def validate_plan(self, plan_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate plan against schema.
        
        Args:
            plan_data: Plan data dictionary
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required top-level fields
        required_fields = self.schema.get("schema", {}).get("required_fields", [])
        for field in required_fields:
            if field not in plan_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate metadata
        if "metadata" in plan_data:
            metadata_errors = self._validate_metadata(plan_data["metadata"])
            errors.extend(metadata_errors)
        
        # Validate phases
        if "phases" in plan_data:
            phase_errors = self._validate_phases(plan_data["phases"])
            errors.extend(phase_errors)
        
        # Validate Definition of Ready
        if "definition_of_ready" in plan_data:
            if not isinstance(plan_data["definition_of_ready"], list):
                errors.append("definition_of_ready must be a list")
            elif len(plan_data["definition_of_ready"]) == 0:
                errors.append("definition_of_ready must have at least 1 item")
        
        # Validate Definition of Done
        if "definition_of_done" in plan_data:
            if not isinstance(plan_data["definition_of_done"], list):
                errors.append("definition_of_done must be a list")
            elif len(plan_data["definition_of_done"]) == 0:
                errors.append("definition_of_done must have at least 1 item")
        
        # Validate risks if present
        if "risks" in plan_data:
            risk_errors = self._validate_risks(plan_data["risks"])
            errors.extend(risk_errors)
        
        return (len(errors) == 0, errors)
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate metadata section."""
        errors = []
        
        # Required metadata fields
        required = ["plan_id", "title", "created_date", "created_by", "status", "priority", "estimated_hours"]
        for field in required:
            if field not in metadata:
                errors.append(f"metadata: Missing required field '{field}'")
        
        # Validate plan_id format
        if "plan_id" in metadata:
            if not re.match(r'^[A-Z0-9-]+$', metadata["plan_id"]):
                errors.append(f"metadata.plan_id: Must match pattern ^[A-Z0-9-]+$ (got: {metadata['plan_id']})")
        
        # Validate status enum
        if "status" in metadata:
            valid_statuses = ["proposed", "approved", "in-progress", "blocked", "completed", "cancelled"]
            if metadata["status"] not in valid_statuses:
                errors.append(f"metadata.status: Must be one of {valid_statuses} (got: {metadata['status']})")
        
        # Validate priority enum
        if "priority" in metadata:
            valid_priorities = ["critical", "high", "medium", "low"]
            if metadata["priority"] not in valid_priorities:
                errors.append(f"metadata.priority: Must be one of {valid_priorities} (got: {metadata['priority']})")
        
        # Validate estimated_hours
        if "estimated_hours" in metadata:
            if not isinstance(metadata["estimated_hours"], (int, float)) or metadata["estimated_hours"] < 0:
                errors.append(f"metadata.estimated_hours: Must be a positive number (got: {metadata['estimated_hours']})")
        
        # Validate ISO 8601 date format
        if "created_date" in metadata:
            if not self._is_valid_iso8601(metadata["created_date"]):
                errors.append(f"metadata.created_date: Must be ISO 8601 format (got: {metadata['created_date']})")
        
        return errors
    
    def _validate_phases(self, phases: List[Dict[str, Any]]) -> List[str]:
        """Validate phases section."""
        errors = []
        
        if not isinstance(phases, list):
            errors.append("phases: Must be a list")
            return errors
        
        if len(phases) == 0:
            errors.append("phases: Must have at least 1 phase")
            return errors
        
        task_ids = set()
        phase_numbers = []
        
        for idx, phase in enumerate(phases):
            phase_label = f"phases[{idx}]"
            
            # Required phase fields
            required = ["phase_number", "phase_name", "estimated_hours", "tasks"]
            for field in required:
                if field not in phase:
                    errors.append(f"{phase_label}: Missing required field '{field}'")
            
            # Validate phase_number
            if "phase_number" in phase:
                if not isinstance(phase["phase_number"], int) or phase["phase_number"] < 1:
                    errors.append(f"{phase_label}.phase_number: Must be integer >= 1")
                else:
                    phase_numbers.append(phase["phase_number"])
            
            # Validate tasks
            if "tasks" in phase:
                task_errors = self._validate_tasks(phase["tasks"], task_ids, phase_label)
                errors.extend(task_errors)
        
        # Check sequential phase numbers
        if phase_numbers:
            phase_numbers.sort()
            expected = list(range(1, len(phase_numbers) + 1))
            if phase_numbers != expected:
                errors.append(f"phases: Phase numbers must be sequential starting from 1 (got: {phase_numbers})")
        
        return errors
    
    def _validate_tasks(self, tasks: List[Dict[str, Any]], task_ids: set, phase_label: str) -> List[str]:
        """Validate tasks within a phase."""
        errors = []
        
        if not isinstance(tasks, list):
            errors.append(f"{phase_label}.tasks: Must be a list")
            return errors
        
        if len(tasks) == 0:
            errors.append(f"{phase_label}.tasks: Must have at least 1 task")
            return errors
        
        for idx, task in enumerate(tasks):
            task_label = f"{phase_label}.tasks[{idx}]"
            
            # Required task fields
            required = ["task_id", "task_name", "estimated_hours"]
            for field in required:
                if field not in task:
                    errors.append(f"{task_label}: Missing required field '{field}'")
            
            # Validate task_id format and uniqueness
            if "task_id" in task:
                if not re.match(r'^\d+\.\d+$', task["task_id"]):
                    errors.append(f"{task_label}.task_id: Must match pattern \\d+\\.\\d+ (got: {task['task_id']})")
                elif task["task_id"] in task_ids:
                    errors.append(f"{task_label}.task_id: Duplicate task ID '{task['task_id']}'")
                else:
                    task_ids.add(task["task_id"])
            
            # Validate estimated_hours
            if "estimated_hours" in task:
                if not isinstance(task["estimated_hours"], (int, float)) or task["estimated_hours"] < 0.25:
                    errors.append(f"{task_label}.estimated_hours: Must be >= 0.25 (got: {task['estimated_hours']})")
        
        return errors
    
    def _validate_risks(self, risks: List[Dict[str, Any]]) -> List[str]:
        """Validate risks section."""
        errors = []
        
        if not isinstance(risks, list):
            errors.append("risks: Must be a list")
            return errors
        
        for idx, risk in enumerate(risks):
            risk_label = f"risks[{idx}]"
            
            # Required risk fields
            required = ["risk_id", "description", "likelihood", "impact", "mitigation"]
            for field in required:
                if field not in risk:
                    errors.append(f"{risk_label}: Missing required field '{field}'")
            
            # Validate likelihood enum
            if "likelihood" in risk:
                valid_values = ["low", "medium", "high"]
                if risk["likelihood"] not in valid_values:
                    errors.append(f"{risk_label}.likelihood: Must be one of {valid_values}")
            
            # Validate impact enum
            if "impact" in risk:
                valid_values = ["low", "medium", "high", "critical"]
                if risk["impact"] not in valid_values:
                    errors.append(f"{risk_label}.impact: Must be one of {valid_values}")
        
        return errors
    
    def _is_valid_iso8601(self, date_string: str) -> bool:
        """Check if string is valid ISO 8601 format."""
        try:
            datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError):
            return False
    
    def generate_markdown(self, plan_data: Dict[str, Any]) -> str:
        """
        Generate Markdown view from YAML plan.
        
        Args:
            plan_data: Validated plan data
        
        Returns:
            Markdown-formatted string
        """
        md = []
        
        # Title (H1)
        metadata = plan_data.get("metadata", {})
        md.append(f"# {metadata.get('title', 'Untitled Plan')}\n")
        
        # Metadata table
        md.append("## Plan Metadata\n")
        md.append("| Field | Value |")
        md.append("|-------|-------|")
        md.append(f"| **Plan ID** | `{metadata.get('plan_id', 'N/A')}` |")
        md.append(f"| **Status** | {metadata.get('status', 'N/A').title()} |")
        md.append(f"| **Priority** | {metadata.get('priority', 'N/A').title()} |")
        md.append(f"| **Created** | {metadata.get('created_date', 'N/A')} by {metadata.get('created_by', 'Unknown')} |")
        
        if "last_updated" in metadata:
            md.append(f"| **Last Updated** | {metadata['last_updated']} |")
        
        md.append(f"| **Estimated Hours** | {metadata.get('estimated_hours', 0)} |")
        
        if "tags" in metadata:
            tags_str = ", ".join([f"`{tag}`" for tag in metadata["tags"]])
            md.append(f"| **Tags** | {tags_str} |")
        
        if "related_plans" in metadata:
            plans_str = ", ".join([f"`{plan}`" for plan in metadata["related_plans"]])
            md.append(f"| **Related Plans** | {plans_str} |")
        
        if "related_issues" in metadata:
            issues_str = ", ".join([f"`{issue}`" for issue in metadata["related_issues"]])
            md.append(f"| **Related Issues** | {issues_str} |")
        
        md.append("")
        
        # Definition of Ready
        md.append("## Definition of Ready\n")
        for item in plan_data.get("definition_of_ready", []):
            md.append(f"- [ ] {item}")
        md.append("")
        
        # Implementation Phases
        md.append("## Implementation Phases\n")
        for phase in plan_data.get("phases", []):
            phase_num = phase.get("phase_number", "?")
            phase_name = phase.get("phase_name", "Unnamed Phase")
            estimated = phase.get("estimated_hours", "?")
            
            md.append(f"### Phase {phase_num}: {phase_name}\n")
            md.append(f"**Estimated Hours:** {estimated}\n")
            
            if "description" in phase:
                md.append(f"{phase['description']}\n")
            
            # Tasks
            md.append("#### Tasks\n")
            for task in phase.get("tasks", []):
                task_id = task.get("task_id", "?")
                task_name = task.get("task_name", "Unnamed Task")
                task_hours = task.get("estimated_hours", "?")
                
                md.append(f"**{task_id}** - {task_name} ({task_hours}h)")
                
                if "description" in task:
                    md.append(f"  {task['description']}")
                
                if "acceptance_criteria" in task:
                    md.append("  - **Acceptance Criteria:**")
                    for criterion in task["acceptance_criteria"]:
                        md.append(f"    - {criterion}")
                
                if "implementation_notes" in task:
                    md.append(f"  - **Notes:** {task['implementation_notes']}")
                
                if "files_affected" in task:
                    md.append("  - **Files Affected:**")
                    for file in task["files_affected"]:
                        md.append(f"    - `{file}`")
                
                md.append("")
            
            if "risks" in phase:
                md.append("#### Phase Risks\n")
                for risk in phase["risks"]:
                    md.append(f"- **{risk}**")
                md.append("")
        
        # Definition of Done
        md.append("## Definition of Done\n")
        for item in plan_data.get("definition_of_done", []):
            md.append(f"- [ ] {item}")
        md.append("")
        
        # Risks & Mitigation
        if "risks" in plan_data:
            md.append("## Risks & Mitigation\n")
            md.append("| ID | Risk | Likelihood | Impact | Mitigation |")
            md.append("|----|------|------------|--------|------------|")
            for risk in plan_data["risks"]:
                risk_id = risk.get("risk_id", "?")
                description = risk.get("description", "")
                likelihood = risk.get("likelihood", "?")
                impact = risk.get("impact", "?")
                mitigation = risk.get("mitigation", "")
                md.append(f"| {risk_id} | {description} | {likelihood} | {impact} | {mitigation} |")
            md.append("")
        
        # Acceptance Criteria (plan-level)
        if "acceptance_criteria" in plan_data:
            md.append("## Acceptance Criteria\n")
            for criterion in plan_data["acceptance_criteria"]:
                md.append(f"- [ ] {criterion}")
            md.append("")
        
        # Notes
        if "notes" in metadata:
            md.append("## Notes\n")
            md.append(metadata["notes"])
            md.append("")
        
        return "\n".join(md)
    
    def save_plan(self, plan_data: Dict[str, Any], output_path: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Save plan to YAML file (with validation).
        
        Args:
            plan_data: Plan data dictionary
            output_path: Optional custom output path (defaults to active plans dir)
        
        Returns:
            Tuple of (success, message)
        """
        # Validate plan
        is_valid, errors = self.validate_plan(plan_data)
        if not is_valid:
            error_msg = "Plan validation failed:\n" + "\n".join([f"  - {e}" for e in errors])
            logger.error(error_msg)
            return (False, error_msg)
        
        # Determine output path
        if output_path is None:
            plan_id = plan_data.get("metadata", {}).get("plan_id", "UNKNOWN-PLAN")
            status = plan_data.get("metadata", {}).get("status", "proposed")
            
            if status == "completed":
                base_dir = self.completed_plans_dir
            else:
                base_dir = self.active_plans_dir
            
            base_dir.mkdir(parents=True, exist_ok=True)
            output_path = base_dir / f"{plan_id}.yaml"
        
        # Save YAML
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(plan_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            # NEW Sprint 2: Auto-organize plan into correct category
            try:
                organized_path, organize_message = self.document_organizer.organize_document(output_path)
                if organized_path:
                    logger.info(f"📁 {organize_message}")
                    output_path = organized_path
                else:
                    logger.warning(f"⚠️ Plan organization skipped: {organize_message}")
            except Exception as org_error:
                logger.warning(f"⚠️ Plan organization failed: {org_error}")
            
            logger.info(f"Plan saved to {output_path}")
            return (True, f"Plan saved to {output_path}")
        except Exception as e:
            error_msg = f"Failed to save plan: {e}"
            logger.error(error_msg)
            return (False, error_msg)
    
    def load_plan(self, plan_path: Path) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Load and validate plan from YAML file.
        
        Args:
            plan_path: Path to plan YAML file
        
        Returns:
            Tuple of (success, plan_data, errors)
        """
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan_data = yaml.safe_load(f)
            
            is_valid, errors = self.validate_plan(plan_data)
            return (is_valid, plan_data, errors)
        except Exception as e:
            logger.error(f"Failed to load plan: {e}")
            return (False, None, [str(e)])
    
    def migrate_markdown_plan(self, md_path: Path) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Migrate Markdown plan to YAML format.
        
        Args:
            md_path: Path to Markdown plan file
        
        Returns:
            Tuple of (success, plan_data, message)
        """
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            plan_data = self._parse_markdown_plan(content, md_path)
            
            # Validate migrated plan
            is_valid, errors = self.validate_plan(plan_data)
            if not is_valid:
                return (False, plan_data, f"Migrated plan validation failed: {errors}")
            
            return (True, plan_data, "Successfully migrated Markdown to YAML")
        except Exception as e:
            logger.error(f"Failed to migrate plan: {e}")
            return (False, None, str(e))
    
    def _parse_markdown_plan(self, content: str, md_path: Path) -> Dict[str, Any]:
        """Parse Markdown plan into YAML structure."""
        lines = content.split('\n')
        plan_data = {
            "metadata": {},
            "phases": [],
            "definition_of_ready": [],
            "definition_of_done": []
        }
        
        # Extract title (first H1)
        for line in lines:
            if line.startswith('# '):
                plan_data["metadata"]["title"] = line[2:].strip()
                break
        
        # Generate plan_id from filename
        plan_id = md_path.stem.upper().replace(' ', '-')
        plan_data["metadata"]["plan_id"] = plan_id
        
        # Set defaults
        plan_data["metadata"]["created_date"] = datetime.now().isoformat() + "Z"
        plan_data["metadata"]["created_by"] = "Markdown Migration"
        plan_data["metadata"]["status"] = "in-progress"
        plan_data["metadata"]["priority"] = "medium"
        plan_data["metadata"]["estimated_hours"] = 0
        
        # Parse phases (## Phase N: ...)
        current_phase = None
        current_section = None
        
        for line in lines:
            # Phase header
            phase_match = re.match(r'^##\s+Phase\s+(\d+):\s+(.+)', line)
            if phase_match:
                if current_phase:
                    plan_data["phases"].append(current_phase)
                
                current_phase = {
                    "phase_number": int(phase_match.group(1)),
                    "phase_name": phase_match.group(2).strip(),
                    "estimated_hours": "TBD",
                    "tasks": []
                }
                current_section = "phase"
                continue
            
            # Definition of Ready section
            if line.startswith('## Definition of Ready'):
                current_section = "dor"
                continue
            
            # Definition of Done section
            if line.startswith('## Definition of Done'):
                current_section = "dod"
                continue
            
            # Extract checklist items
            if line.strip().startswith('- [ ]') or line.strip().startswith('- [x]'):
                item = line.strip()[5:].strip()
                if current_section == "dor":
                    plan_data["definition_of_ready"].append(item)
                elif current_section == "dod":
                    plan_data["definition_of_done"].append(item)
            
            # Extract task items (if in phase section)
            if current_section == "phase" and current_phase and line.strip().startswith('- '):
                task_match = re.match(r'-\s+\*\*(.+?)\*\*\s+-\s+(.+?)(?:\s+\((.+?)h\))?', line.strip())
                if task_match:
                    task_id = task_match.group(1)
                    task_name = task_match.group(2)
                    task_hours = float(task_match.group(3)) if task_match.group(3) else 1.0
                    
                    current_phase["tasks"].append({
                        "task_id": task_id,
                        "task_name": task_name,
                        "estimated_hours": task_hours
                    })
        
        # Add last phase
        if current_phase:
            plan_data["phases"].append(current_phase)
        
        # Calculate total hours
        total_hours = 0
        for phase in plan_data["phases"]:
            for task in phase["tasks"]:
                total_hours += task["estimated_hours"]
        plan_data["metadata"]["estimated_hours"] = total_hours
        
        return plan_data
    
    def generate_markdown_view(self, plan_path: Path, output_path: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Generate Markdown view from YAML plan file.
        
        Args:
            plan_path: Path to YAML plan
            output_path: Optional output path for Markdown (defaults to same name with .md)
        
        Returns:
            Tuple of (success, message)
        """
        # Load plan
        success, plan_data, errors = self.load_plan(plan_path)
        if not success:
            return (False, f"Failed to load plan: {errors}")
        
        # Generate Markdown
        markdown = self.generate_markdown(plan_data)
        
        # Determine output path
        if output_path is None:
            output_path = plan_path.with_suffix('.md')
        
        # Save Markdown
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            # NEW Sprint 2: Auto-organize markdown view into correct category
            try:
                organized_path, organize_message = self.document_organizer.organize_document(output_path)
                if organized_path:
                    logger.info(f"📁 {organize_message}")
                    output_path = organized_path
                else:
                    logger.warning(f"⚠️ Markdown organization skipped: {organize_message}")
            except Exception as org_error:
                logger.warning(f"⚠️ Markdown organization failed: {org_error}")
            
            logger.info(f"Markdown view saved to {output_path}")
            return (True, f"Markdown view saved to {output_path}")
        except Exception as e:
            error_msg = f"Failed to save Markdown: {e}"
            logger.error(error_msg)
            return (False, error_msg)
    
    def generate_incremental_plan(
        self,
        feature_requirements: str,
        checkpoint_callback: Optional[Callable[[str, str, str], bool]] = None,
        output_filename: Optional[str] = None
    ) -> Tuple[bool, Optional[Path], str]:
        """
        Generate feature plan incrementally with token budgets and user checkpoints.
        
        This method implements token-efficient planning by:
        1. Generating a 200-token skeleton → user approval checkpoint
        2. Filling Phase 1 sections (500 tokens each) → user approval checkpoint
        3. Filling Phase 2 sections (500 tokens each) → user approval checkpoint
        4. Filling Phase 3 sections (500 tokens each) → user approval checkpoint
        5. Writing complete plan to disk using streaming writer
        
        Args:
            feature_requirements: Natural language description of feature to plan
            checkpoint_callback: Optional callback(checkpoint_id, section_name, preview) -> approved
                                 If None, auto-approves all checkpoints
            output_filename: Optional custom filename (default: auto-generated from session ID)
        
        Returns:
            Tuple of (success, output_path, message)
        
        Example:
            >>> def my_checkpoint_handler(cp_id, section, preview):
            ...     print(f"Checkpoint: {section}")
            ...     print(preview[:100])
            ...     return input("Approve? (y/n): ").lower() == 'y'
            ...
            >>> success, path, msg = orchestrator.generate_incremental_plan(
            ...     "User authentication system with JWT tokens",
            ...     checkpoint_callback=my_checkpoint_handler
            ... )
        """
        try:
            # Step 1: Generate skeleton (200-token structure)
            logger.info("🧠 Generating plan skeleton (200-token limit)...")
            
            # Convert feature_requirements string to dict format expected by generator
            requirements_dict = {
                'feature_name': feature_requirements[:50] if len(feature_requirements) <= 50 else feature_requirements[:47] + "..."
            }
            
            skeleton, token_count = self.incremental_generator.generate_skeleton(requirements_dict)
            
            # Checkpoint 1: Skeleton approval
            skeleton_preview = self.incremental_generator._serialize_skeleton(skeleton)
            skeleton_approved = self._handle_checkpoint(
                checkpoint_callback,
                "skeleton",
                "Plan Skeleton",
                skeleton_preview
            )
            
            if not skeleton_approved:
                return (False, None, "Plan skeleton rejected by user")
            
            # Approve the checkpoint in generator
            checkpoints = [cp for cp in self.incremental_generator.checkpoints if cp.status == 'pending_approval']
            if checkpoints:
                self.incremental_generator.approve_checkpoint(checkpoints[0].checkpoint_id)
            
            # Step 2: Fill Phase 1 sections (Requirements, Dependencies, Architecture)
            logger.info("📝 Filling Phase 1 sections (500 tokens per section)...")
            phase_1_sections = ["Requirements", "Dependencies", "Architecture"]
            for section in phase_1_sections:
                self.incremental_generator.fill_section(section, {"feature": feature_requirements})
            
            # Checkpoint 2: Phase 1 approval
            phase_1_approved = self._handle_phase_checkpoint(
                checkpoint_callback,
                "phase-1",
                "Phase 1: Foundation",
                phase_1_sections
            )
            
            if not phase_1_approved:
                return (False, None, "Phase 1 rejected by user")
            
            # Step 3: Fill Phase 2 sections (Implementation, Tests, Integration)
            logger.info("📝 Filling Phase 2 sections (500 tokens per section)...")
            phase_2_sections = ["Implementation", "Tests", "Integration"]
            for section in phase_2_sections:
                self.incremental_generator.fill_section(section, {"feature": feature_requirements})
            
            # Checkpoint 3: Phase 2 approval
            phase_2_approved = self._handle_phase_checkpoint(
                checkpoint_callback,
                "phase-2",
                "Phase 2: Development",
                phase_2_sections
            )
            
            if not phase_2_approved:
                return (False, None, "Phase 2 rejected by user")
            
            # Step 4: Fill Phase 3 sections (Acceptance, Security, Deployment)
            logger.info("📝 Filling Phase 3 sections (500 tokens per section)...")
            phase_3_sections = ["Acceptance", "Security", "Deployment"]
            for section in phase_3_sections:
                self.incremental_generator.fill_section(section, {"feature": feature_requirements})
            
            # Checkpoint 4: Phase 3 approval
            phase_3_approved = self._handle_phase_checkpoint(
                checkpoint_callback,
                "phase-3",
                "Phase 3: Validation & Deployment",
                phase_3_sections
            )
            
            if not phase_3_approved:
                return (False, None, "Phase 3 rejected by user")
            
            # Step 5: Write complete plan to disk using streaming writer
            logger.info("💾 Writing complete plan to disk...")
            output_path = self._write_incremental_plan(output_filename)
            
            # Auto-organize using DocumentOrganizer
            try:
                organized_path, organize_message = self.document_organizer.organize_document(output_path)
                if organized_path:
                    logger.info(f"📁 {organize_message}")
                    output_path = organized_path
            except Exception as org_error:
                logger.warning(f"⚠️ Plan organization failed: {org_error}")
            
            logger.info(f"✅ Incremental plan generation complete: {output_path}")
            return (True, output_path, f"Plan generated successfully: {output_path}")
            
        except Exception as e:
            error_msg = f"Failed to generate incremental plan: {e}"
            logger.error(error_msg)
            return (False, None, error_msg)
    
    def _handle_checkpoint(
        self,
        callback: Optional[Callable[[str, str, str], bool]],
        checkpoint_id: str,
        section_name: str,
        content_preview: str
    ) -> bool:
        """
        Handle checkpoint approval via callback or auto-approve.
        
        Args:
            callback: User-provided checkpoint handler
            checkpoint_id: Unique checkpoint identifier
            section_name: Name of section at checkpoint
            content_preview: Preview of content to approve
        
        Returns:
            True if approved, False if rejected
        """
        if callback is None:
            logger.info(f"✅ Auto-approving checkpoint: {section_name}")
            return True
        
        try:
            approved = callback(checkpoint_id, section_name, content_preview)
            if approved:
                logger.info(f"✅ User approved checkpoint: {section_name}")
            else:
                logger.warning(f"❌ User rejected checkpoint: {section_name}")
            return approved
        except Exception as e:
            logger.error(f"Checkpoint callback error: {e}")
            return False
    
    def _handle_phase_checkpoint(
        self,
        callback: Optional[Callable[[str, str, str], bool]],
        checkpoint_id: str,
        phase_name: str,
        section_names: List[str]
    ) -> bool:
        """
        Handle phase completion checkpoint.
        
        Args:
            callback: User-provided checkpoint handler
            checkpoint_id: Unique checkpoint identifier
            phase_name: Name of completed phase
            section_names: List of section names in phase
        
        Returns:
            True if approved, False if rejected
        """
        # Build preview of all sections in phase
        preview_parts = [f"# {phase_name}\n"]
        for section_name in section_names:
            section = self.incremental_generator.sections.get(section_name)
            if section:
                preview_parts.append(f"\n## {section_name}")
                preview_parts.append(f"Token count: {section.token_count}")
                preview_parts.append(f"Status: {section.status}")
                preview_parts.append(section.content[:200] + "..." if len(section.content) > 200 else section.content)
        
        preview = "\n".join(preview_parts)
        return self._handle_checkpoint(callback, checkpoint_id, phase_name, preview)
    
    def _write_incremental_plan(self, output_filename: Optional[str] = None) -> Path:
        """
        Write complete plan using StreamingPlanWriter.
        
        Args:
            output_filename: Optional custom filename
        
        Returns:
            Path to written plan file
        """
        # Determine output path
        if output_filename is None:
            session_id = self.incremental_generator.session_id
            output_filename = f"{session_id}.md"
        
        output_path = self.active_plans_dir / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create writer with checkpoint support
        writer = CheckpointedPlanWriter(output_path)
        
        try:
            # Extract metadata
            skeleton = self.incremental_generator.skeleton
            feature_name = skeleton.get("feature_name", "Feature Plan")
            
            # Write header
            writer.write_header(
                feature_name,
                {
                    "Session ID": self.incremental_generator.session_id,
                    "Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Token Budget": "200 skeleton + 500 per section"
                }
            )
            
            # Write Phase 1
            writer.write_phase("Phase 1: Foundation", [
                {"name": "Requirements", "content": self._get_section_content("Requirements")},
                {"name": "Dependencies", "content": self._get_section_content("Dependencies")},
                {"name": "Architecture", "content": self._get_section_content("Architecture")}
            ])
            writer.write_checkpoint_marker("phase-1-complete", "Phase 1 sections completed")
            
            # Write Phase 2
            writer.write_phase("Phase 2: Development", [
                {"name": "Implementation", "content": self._get_section_content("Implementation")},
                {"name": "Tests", "content": self._get_section_content("Tests")},
                {"name": "Integration", "content": self._get_section_content("Integration")}
            ])
            writer.write_checkpoint_marker("phase-2-complete", "Phase 2 sections completed")
            
            # Write Phase 3
            writer.write_phase("Phase 3: Validation & Deployment", [
                {"name": "Acceptance", "content": self._get_section_content("Acceptance")},
                {"name": "Security", "content": self._get_section_content("Security")},
                {"name": "Deployment", "content": self._get_section_content("Deployment")}
            ])
            writer.write_checkpoint_marker("phase-3-complete", "Phase 3 sections completed")
            
            # Finalize
            writer.finalize()
            
            logger.info(f"📄 Plan written: {writer.get_progress_summary()}")
            return output_path
            
        finally:
            # Ensure writer is finalized even if error occurs
            if not writer.is_finalized:
                writer.finalize()
    
    def _get_section_content(self, section_name: str) -> str:
        """Get content for a section from incremental generator."""
        section = self.incremental_generator.sections.get(section_name)
        if section:
            return section.content
        return f"(Section {section_name} not found)"

