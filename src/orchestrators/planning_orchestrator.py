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
    
    # ========================================
    # Phase 2.2: Duplicate Detection Methods
    # ========================================
    
    def check_for_duplicate_plans(
        self, 
        proposed_filename: str, 
        proposed_content: str
    ) -> List[Dict[str, Any]]:
        """
        Check for duplicate planning documents before creation.
        
        Uses DocumentGovernance for semantic similarity detection.
        Searches across all planning subdirectories (active, approved, completed).
        
        Args:
            proposed_filename: Filename for proposed plan
            proposed_path: Path to proposed plan location
            proposed_content: Content of proposed plan
        
        Returns:
            List of duplicate matches with:
            - existing_path: Path to existing document
            - similarity_score: Float 0-1 (1.0 = exact match)
            - algorithm: Detection algorithm used
            - recommendation: Human-readable suggestion
        """
        try:
            # Lazy import to avoid circular dependency
            from src.governance.document_governance import DocumentGovernance
            
            governance = DocumentGovernance(self.cortex_root)
            
            # Construct proposed path (in active directory by default)
            planning_root = self.cortex_root / "cortex-brain" / "documents" / "planning"
            proposed_path = planning_root / "active" / proposed_filename
            
            # Find duplicates using DocumentGovernance
            duplicate_matches = governance.find_duplicates(proposed_path, proposed_content)
            
            # Convert to dict format for easier handling
            results = []
            for match in duplicate_matches:
                results.append({
                    'existing_path': match.existing_path,
                    'similarity_score': match.similarity_score,
                    'algorithm': match.algorithm,
                    'recommendation': match.recommendation
                })
            
            # Sort by similarity score (highest first)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            logger.info(f"Duplicate detection found {len(results)} potential matches")
            return results
            
        except Exception as e:
            logger.warning(f"DocumentGovernance failed, using simplified detection: {e}")
            # Fallback to simplified detection
            return self._simple_duplicate_detection(proposed_filename, proposed_content)
    
    def _simple_duplicate_detection(
        self,
        proposed_filename: str,
        proposed_content: str
    ) -> List[Dict[str, Any]]:
        """
        Simplified duplicate detection without DocumentGovernance.
        Uses basic title and keyword matching.
        """
        results = []
        planning_root = self.cortex_root / "cortex-brain" / "documents" / "planning"
        
        # Search in all status directories
        search_dirs = ['active', 'approved', 'completed', 'deprecated']
        
        # Extract proposed title and keywords
        proposed_title = self._extract_simple_title(proposed_content)
        proposed_keywords = self._extract_simple_keywords(proposed_content)
        
        for status_dir in search_dirs:
            dir_path = planning_root / status_dir
            if not dir_path.exists():
                continue
            
            for existing_file in dir_path.glob('*.md'):
                try:
                    # Check filename match
                    if existing_file.name == proposed_filename:
                        results.append({
                            'existing_path': existing_file,
                            'similarity_score': 1.0,
                            'algorithm': 'exact_filename_match',
                            'recommendation': f'File with same name exists: {existing_file}'
                        })
                        continue
                    
                    # Read existing content
                    existing_content = existing_file.read_text(encoding='utf-8')
                    existing_title = self._extract_simple_title(existing_content)
                    existing_keywords = self._extract_simple_keywords(existing_content)
                    
                    # Title similarity
                    if proposed_title and existing_title:
                        title_sim = self._calculate_simple_similarity(proposed_title, existing_title)
                        if title_sim >= 0.70:
                            results.append({
                                'existing_path': existing_file,
                                'similarity_score': title_sim,
                                'algorithm': 'title_similarity',
                                'recommendation': f'Similar title: "{existing_title}"'
                            })
                    
                    # Keyword overlap
                    if proposed_keywords and existing_keywords:
                        overlap = len(proposed_keywords & existing_keywords)
                        total = len(proposed_keywords | existing_keywords)
                        if total > 0:
                            keyword_sim = overlap / total
                            if keyword_sim >= 0.60:
                                results.append({
                                    'existing_path': existing_file,
                                    'similarity_score': keyword_sim,
                                    'algorithm': 'keyword_overlap',
                                    'recommendation': f'High keyword overlap ({keyword_sim:.0%})'
                                })
                
                except Exception as e:
                    logger.debug(f"Error checking {existing_file}: {e}")
                    continue
        
        # Sort by similarity score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Deduplicate (keep highest score for each file)
        seen = set()
        unique_results = []
        for result in results:
            path_str = str(result['existing_path'])
            if path_str not in seen:
                seen.add(path_str)
                unique_results.append(result)
        
        logger.info(f"Simple duplicate detection found {len(unique_results)} potential matches")
        return unique_results
    
    def _extract_simple_title(self, content: str) -> Optional[str]:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if line.startswith('# '):
                return line[2:].strip()
        return None
    
    def _extract_simple_keywords(self, content: str) -> set:
        """Extract keywords from content (simple word extraction)"""
        import re
        # Remove markdown formatting
        text = re.sub(r'[#*`\[\]()]', ' ', content)
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        # Filter common words
        stop_words = {'this', 'that', 'with', 'from', 'have', 'will', 'would', 'could', 'should'}
        keywords = {w for w in words if w not in stop_words}
        return keywords
    
    def _calculate_simple_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple similarity between two strings"""
        str1 = str1.lower()
        str2 = str2.lower()
        
        # Exact match
        if str1 == str2:
            return 1.0
        
        # Token-based similarity
        tokens1 = set(str1.split())
        tokens2 = set(str2.split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0
    
    def generate_duplicate_handling_prompt(self, duplicates: List[Dict[str, Any]]) -> str:
        """
        Generate user-friendly prompt for handling duplicates.
        
        Args:
            duplicates: List of duplicate matches from check_for_duplicate_plans()
        
        Returns:
            Markdown-formatted prompt with options
        """
        if not duplicates:
            return ""
        
        prompt_lines = []
        prompt_lines.append("# \ud83d\udd0d Potential Duplicate Plans Detected\n")
        prompt_lines.append(f"Found {len(duplicates)} existing plan(s) similar to your request:\n")
        
        # List duplicates
        for i, dup in enumerate(duplicates[:5], 1):  # Show top 5
            score_pct = int(dup['similarity_score'] * 100)
            confidence = "\ud83d\udd34" if score_pct >= 90 else "\ud83d\udfe1" if score_pct >= 70 else "\ud83d\udfe2"
            
            prompt_lines.append(f"{i}. {confidence} **{dup['existing_path'].name}** ({score_pct}% similar)")
            prompt_lines.append(f"   - {dup['recommendation']}\n")
        
        if len(duplicates) > 5:
            prompt_lines.append(f"_(and {len(duplicates) - 5} more...)_\n")
        
        # Options
        prompt_lines.append("\n## \ud83d\udc49 What would you like to do?\n")
        prompt_lines.append("1. **Update existing plan** - Modify one of the existing plans instead")
        prompt_lines.append("2. **Create new plan anyway** - Your plan is different enough")
        prompt_lines.append("3. **Cancel** - Review existing plans first\n")
        
        return "\n".join(prompt_lines)
    
    # ========================================
    # Phase 2.3: Status Transition Methods
    # ========================================
    
    def approve_plan(self, plan_filename: str) -> Dict[str, Any]:
        """
        Approve a plan, moving it from active to approved directory.
        
        Args:
            plan_filename: Filename of plan to approve
        
        Returns:
            Dictionary with:
            - success: bool
            - message: str
            - old_status: str
            - new_status: str
            - old_path: Optional[Path]
            - new_path: Optional[Path]
        """
        planning_root = self.cortex_root / "cortex-brain" / "documents" / "planning"
        active_dir = planning_root / "active"
        approved_dir = planning_root / "approved"
        
        old_path = active_dir / plan_filename
        new_path = approved_dir / plan_filename
        
        # Validate plan exists in active directory
        if not old_path.exists():
            return {
                'success': False,
                'message': f"Plan '{plan_filename}' not found in active directory",
                'old_status': 'unknown',
                'new_status': 'approved'
            }
        
        try:
            # Read content
            content = old_path.read_text(encoding='utf-8')
            
            # Update status in content
            updated_content = self._update_status_in_content(content, 'approved')
            
            # Write to new location
            new_path.write_text(updated_content, encoding='utf-8')
            
            # Remove old file
            old_path.unlink()
            
            logger.info(f"Approved plan: {plan_filename} (active → approved)")
            
            return {
                'success': True,
                'message': f"Plan '{plan_filename}' approved successfully",
                'old_status': 'active',
                'new_status': 'approved',
                'old_path': old_path,
                'new_path': new_path
            }
            
        except Exception as e:
            logger.error(f"Failed to approve plan '{plan_filename}': {e}")
            return {
                'success': False,
                'message': f"Failed to approve plan: {str(e)}",
                'old_status': 'active',
                'new_status': 'approved'
            }
    
    def complete_plan(self, plan_filename: str) -> Dict[str, Any]:
        """
        Mark a plan as completed, moving it from approved to completed directory.
        Adds completion timestamp to the plan.
        
        Args:
            plan_filename: Filename of plan to complete
        
        Returns:
            Dictionary with:
            - success: bool
            - message: str
            - old_status: str
            - new_status: str
            - old_path: Optional[Path]
            - new_path: Optional[Path]
            - completed_date: str
        """
        planning_root = self.cortex_root / "cortex-brain" / "documents" / "planning"
        approved_dir = planning_root / "approved"
        completed_dir = planning_root / "completed"
        
        old_path = approved_dir / plan_filename
        new_path = completed_dir / plan_filename
        
        # Validate plan exists in approved directory
        if not old_path.exists():
            return {
                'success': False,
                'message': f"Plan '{plan_filename}' not found in approved directory",
                'old_status': 'unknown',
                'new_status': 'completed'
            }
        
        try:
            # Read content
            content = old_path.read_text(encoding='utf-8')
            
            # Update status in content
            updated_content = self._update_status_in_content(content, 'completed')
            
            # Add completion timestamp
            completion_date = datetime.now().strftime("%Y-%m-%d")
            updated_content = self._add_completion_timestamp(updated_content, completion_date)
            
            # Write to new location
            new_path.write_text(updated_content, encoding='utf-8')
            
            # Remove old file
            old_path.unlink()
            
            logger.info(f"Completed plan: {plan_filename} (approved → completed)")
            
            return {
                'success': True,
                'message': f"Plan '{plan_filename}' completed successfully",
                'old_status': 'approved',
                'new_status': 'completed',
                'old_path': old_path,
                'new_path': new_path,
                'completed_date': completion_date
            }
            
        except Exception as e:
            logger.error(f"Failed to complete plan '{plan_filename}': {e}")
            return {
                'success': False,
                'message': f"Failed to complete plan: {str(e)}",
                'old_status': 'approved',
                'new_status': 'completed'
            }
    
    def _update_status_in_content(self, content: str, new_status: str) -> str:
        """
        Update status field in plan content.
        
        Args:
            content: Original content
            new_status: New status value
        
        Returns:
            Updated content
        """
        import re
        
        # Try different status patterns
        patterns = [
            (r'\*\*Status:\*\*\s*([a-zA-Z-]+)', f'**Status:** {new_status}'),
            (r'\*\*Status\*\*:\s*([a-zA-Z-]+)', f'**Status:** {new_status}'),
            (r'Status:\s*([a-zA-Z-]+)', f'Status: {new_status}'),
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return re.sub(pattern, replacement, content, count=1, flags=re.IGNORECASE)
        
        # If no status found, add it after the title
        lines = content.split('\n')
        if lines and lines[0].startswith('#'):
            # Insert after title
            lines.insert(1, '')
            lines.insert(2, f'**Status:** {new_status}')
            return '\n'.join(lines)
        
        # Fallback: prepend to content
        return f'**Status:** {new_status}\n\n{content}'
    
    def _add_completion_timestamp(self, content: str, completion_date: str) -> str:
        """
        Add completion timestamp to plan content.
        
        Args:
            content: Plan content
            completion_date: Completion date (YYYY-MM-DD)
        
        Returns:
            Updated content
        """
        import re
        
        # Check if completion timestamp already exists
        if re.search(r'\*\*Completed:\*\*', content, re.IGNORECASE):
            # Update existing
            return re.sub(
                r'\*\*Completed:\*\*\s*[\d-]+',
                f'**Completed:** {completion_date}',
                content,
                flags=re.IGNORECASE
            )
        
        # Add after status field
        status_pattern = r'(\*\*Status:\*\*\s*completed)'
        if re.search(status_pattern, content, re.IGNORECASE):
            return re.sub(
                status_pattern,
                f'\\1  \n**Completed:** {completion_date}',
                content,
                count=1,
                flags=re.IGNORECASE
            )
        
        # Fallback: add after first line
        lines = content.split('\n')
        if len(lines) > 1:
            lines.insert(1, f'**Completed:** {completion_date}')
            return '\n'.join(lines)
        
        return f'{content}\n\n**Completed:** {completion_date}'


    # ==================================================================================
    # PHASE 3: SWAGGER ENTRY POINT MODULE - Scope Inference & Clarification
    # ==================================================================================
    
    def infer_scope_from_dor(self, dor_responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Infer feature scope from DoR responses (Q3 + Q6)
        
        This is the SWAGGER Entry Point - automatically extracts scope boundaries
        from DoR answers to reduce interrogation by 70%
        
        Args:
            dor_responses: Dictionary with keys 'Q3' (functional scope) and 'Q6' (dependencies)
        
        Returns:
            Dictionary with:
                - entities: Extracted scope entities (tables, files, services, dependencies)
                - confidence: Confidence score (0.0-1.0)
                - validation: Validation result
                - needs_clarification: Boolean indicating if clarification is needed
                - clarification_prompt: Optional prompt for user (if needs_clarification=True)
        """
        from src.agents.estimation.scope_inference_engine import ScopeInferenceEngine
        from src.agents.estimation.scope_validator import ScopeValidator
        from src.agents.estimation.clarification_orchestrator import ClarificationOrchestrator
        
        # Initialize components
        inference_engine = ScopeInferenceEngine()
        validator = ScopeValidator()
        clarifier = ClarificationOrchestrator()
        
        # Combine DoR Q3 + Q6 into requirements text
        requirements_text = inference_engine.parse_dor_answers(dor_responses)
        
        # Extract scope entities
        entities = inference_engine.extract_entities(requirements_text)
        
        # Calculate confidence
        confidence = inference_engine.calculate_confidence(entities, requirements_text)
        
        # Generate scope boundary
        boundary = inference_engine.generate_scope_boundary(entities, confidence)
        
        # Validate
        validation_result = validator.validate_scope(boundary)
        
        # Convert validation result to dict for clarifier
        validation_dict = {
            'confidence': validation_result.confidence_score,
            'is_valid': validation_result.is_valid,
            'missing_elements': validation_result.missing_elements,
            'clarification_questions': []  # Generate from missing elements
        }
        
        # Generate clarification questions from missing elements
        if 'tables' in validation_result.missing_elements:
            validation_dict['clarification_questions'].append('What database tables will be involved?')
        if 'files' in validation_result.missing_elements:
            validation_dict['clarification_questions'].append('What code files need to be modified or created?')
        if 'services' in validation_result.missing_elements:
            validation_dict['clarification_questions'].append('What external services will be integrated?')
        
        # Check if clarification is needed
        needs_clarification = clarifier.should_clarify(validation_dict)
        
        result = {
            'entities': {
                'tables': entities.tables,
                'files': entities.files,
                'services': entities.services,
                'dependencies': entities.dependencies
            },
            'confidence': confidence,
            'validation': {
                'is_valid': validation_result.is_valid,
                'requires_clarification': validation_result.requires_clarification,
                'errors': validation_result.validation_errors,
                'warnings': validation_result.warnings,
                'missing_elements': validation_result.missing_elements
            },
            'needs_clarification': needs_clarification,
            'clarification_prompt': None
        }
        
        # Generate clarification prompt if needed
        if needs_clarification:
            result['clarification_prompt'] = clarifier.generate_clarification_prompt(validation_dict)
        
        return result
    
    def process_clarification_response(self, user_response: str) -> Dict[str, Any]:
        """
        Process user's response to clarification questions
        
        Args:
            user_response: User's text response with additional scope details
        
        Returns:
            Dictionary with:
                - entities: Re-extracted scope entities
                - confidence: Updated confidence score
                - is_vague: Boolean indicating if response is still vague
        """
        from src.agents.estimation.clarification_orchestrator import ClarificationOrchestrator
        
        clarifier = ClarificationOrchestrator()
        return clarifier.parse_user_response(user_response)
    
    def estimate_feature_scope(self, feature_name: str, dor_responses: Dict[str, str], 
                              max_clarification_rounds: int = 2) -> Dict[str, Any]:
        """
        Complete scope estimation workflow with automatic clarification
        
        This is the main entry point for the SWAGGER scope estimation system
        
        Args:
            feature_name: Name of the feature being planned
            dor_responses: DoR responses (Q3 + Q6 minimum)
            max_clarification_rounds: Maximum clarification iterations (default 2)
        
        Returns:
            Dictionary with:
                - final_scope: Final extracted scope entities
                - confidence: Final confidence score
                - rounds_completed: Number of clarification rounds used
                - workflow_log: List of workflow steps taken
                - success: Boolean indicating if confidence threshold was met
        """
        from src.agents.estimation.clarification_orchestrator import ClarificationOrchestrator
        
        workflow_log = []
        clarifier = ClarificationOrchestrator()
        
        # Initial scope inference
        workflow_log.append(f"Starting scope inference for '{feature_name}'")
        initial_scope = self.infer_scope_from_dor(dor_responses)
        workflow_log.append(f"Initial confidence: {initial_scope['confidence']:.2%}")
        
        # If high confidence, we're done
        if not initial_scope['needs_clarification']:
            workflow_log.append("High confidence achieved - no clarification needed")
            return {
                'final_scope': initial_scope['entities'],
                'confidence': initial_scope['confidence'],
                'rounds_completed': 0,
                'workflow_log': workflow_log,
                'success': True
            }
        
        # Clarification workflow
        workflow_log.append("Low confidence detected - clarification workflow activated")
        current_scope = initial_scope
        
        for round_num in range(1, max_clarification_rounds + 1):
            clarifier.increment_round()
            workflow_log.append(f"Clarification round {round_num}/{max_clarification_rounds}")
            
            # In real usage, this would prompt the user and wait for response
            # For now, we return the state and let the caller handle user interaction
            workflow_log.append(f"Clarification prompt: {current_scope['clarification_prompt']}")
            
            # Exit point for real usage - caller will provide user response separately
            break
        
        return {
            'final_scope': current_scope['entities'],
            'confidence': current_scope['confidence'],
            'rounds_completed': clarifier.get_current_round(),
            'workflow_log': workflow_log,
            'success': current_scope['confidence'] >= 0.70,
            'awaiting_user_response': True,
            'clarification_prompt': current_scope['clarification_prompt']
        }
    
    def estimate_timeframe(self, complexity: float, scope: Optional[Dict] = None,
                          team_size: int = 1, velocity: Optional[float] = None,
                          include_three_point: bool = False, 
                          scope_boundary: Optional['ScopeBoundary'] = None) -> Dict[str, Any]:
        """
        Generate time estimates from SWAGGER complexity score
        
        ⚠️ CRITICAL: Estimates BLOCKED unless scope is user-approved (CORTEX 3.2.1)
        
        Natural language triggers:
        - "timeframe", "estimate", "time estimate", "how long", "duration"
        - "story points", "sprint estimate", "team size", "velocity"
        
        This method integrates TIMEFRAME Entry Point Module with SWAGGER.
        Call this after scope inference when user asks about time estimates.
        
        Args:
            complexity: SWAGGER complexity score (0-100)
            scope: Optional SWAGGER scope dict (for detailed breakdown)
            team_size: Number of developers on team (default: 1)
            velocity: Optional team velocity (story points per sprint)
            include_three_point: Generate PERT three-point estimate
            scope_boundary: Optional ScopeBoundary with approval tracking (NEW 3.2.1)
        
        Returns:
            Dictionary with:
                - story_points: Fibonacci story points
                - hours_single: Single developer hours
                - hours_team: Team hours (with communication overhead)
                - days_single: Single developer days
                - days_team: Team calendar days
                - sprints: Sprint allocation
                - confidence: Estimate confidence (HIGH/MEDIUM/LOW)
                - breakdown: Effort breakdown by entity type
                - assumptions: List of estimation assumptions
                - report: Formatted markdown report
                - three_point: Optional PERT estimates (best/likely/worst)
            
            OR (if scope approval required):
                - status: 'scope_approval_required'
                - swagger_context_id: Context ID for later retrieval
                - confidence: Scope confidence score
                - clarification_prompt: User-facing prompt
                - next_action: 'plan'
                - message: Detailed explanation for user
        
        Example:
            >>> # After SWAGGER scope inference
            >>> scope_result = orchestrator.infer_scope_from_dor(dor_responses)
            >>> complexity = scope_result['validation']['complexity']
            >>> 
            >>> # User asks: "what's the timeframe for this?"
            >>> timeframe = orchestrator.estimate_timeframe(
            ...     complexity=complexity,
            ...     scope=scope_result['entities'],
            ...     team_size=2,
            ...     scope_boundary=scope_result['scope_boundary']  # NEW
            ... )
            >>> 
            >>> if timeframe.get('status') == 'scope_approval_required':
            >>>     # User approval needed - hand off to planner
            >>>     print(timeframe['message'])
            >>> else:
            >>>     # Approved - show estimate
            >>>     print(timeframe['report'])
        """
        from src.agents.estimation.timeframe_estimator import TimeframeEstimator
        from src.agents.estimation.scope_inference_engine import ScopeBoundary, ScopeEntities
        
        # STEP 1: Validate scope approval (NEW: Approval Gate)
        if scope_boundary is None and scope is not None:
            # Legacy call without ScopeBoundary - create one (treat as unapproved)
            scope_boundary = ScopeBoundary(
                table_count=len(scope.get('tables', [])),
                file_count=len(scope.get('files', [])),
                service_count=len(scope.get('services', [])),
                dependency_depth=1,
                estimated_complexity=complexity,
                confidence=0.5,  # Unknown confidence - requires approval
                gaps=[],
                user_approved=False  # Default: not approved
            )
        
        # STEP 2: Approval gate - check if user approval is required
        if scope_boundary and scope_boundary.is_approval_required():
            # Scope NOT approved - hand off to planner
            return self._hand_off_to_planner_for_approval(
                complexity=complexity,
                scope_boundary=scope_boundary,
                scope=scope,
                team_size=team_size,
                velocity=velocity
            )
        
        # STEP 3: Scope approved - proceed with estimation
        # Initialize TIMEFRAME estimator
        estimator = TimeframeEstimator()
        
        # Generate estimate
        estimate = estimator.estimate_timeframe(
            complexity=complexity,
            scope=scope,
            team_size=team_size,
            velocity=velocity
        )
        
        # Convert dataclass to dict for JSON serialization
        result = {
            'story_points': estimate.story_points,
            'hours_single': estimate.hours_single,
            'hours_team': estimate.hours_team,
            'days_single': estimate.days_single,
            'days_team': estimate.days_team,
            'sprints': estimate.sprints,
            'team_size': estimate.team_size,
            'confidence': estimate.confidence,
            'breakdown': estimate.breakdown,
            'assumptions': estimate.assumptions,
            'report': estimator.format_estimate_report(estimate, include_breakdown=True)
        }
        
        # Add three-point estimate if requested
        if include_three_point:
            three_point = estimator.estimate_three_point(complexity, scope, team_size)
            result['three_point'] = {
                'best': {
                    'story_points': three_point['best'].story_points,
                    'hours': three_point['best'].hours_single,
                    'days': three_point['best'].days_single
                },
                'likely': {
                    'story_points': three_point['likely'].story_points,
                    'hours': three_point['likely'].hours_single,
                    'days': three_point['likely'].days_single
                },
                'worst': {
                    'story_points': three_point['worst'].story_points,
                    'hours': three_point['worst'].hours_single,
                    'days': three_point['worst'].days_single
                }
            }
        
        return result
    
    # ========== SWAGGER Scope Approval Gate (CORTEX 3.2.1) ==========
    
    def _hand_off_to_planner_for_approval(
        self,
        complexity: float,
        scope_boundary: 'ScopeBoundary',
        scope: Optional[Dict],
        team_size: int,
        velocity: Optional[float]
    ) -> Dict[str, Any]:
        """
        Hand off to planner when scope requires user approval
        
        Preserves SWAGGER context for return path to estimator after user
        reviews and approves scope boundaries.
        
        Args:
            complexity: SWAGGER complexity score
            scope_boundary: ScopeBoundary with approval status
            scope: Optional scope dict
            team_size: Team size for estimation
            velocity: Optional velocity
        
        Returns:
            Handoff response with clarification prompt and context ID
        """
        from datetime import datetime
        from src.tier1.working_memory import WorkingMemory
        
        # Generate unique context ID
        swagger_context_id = f"swagger-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        scope_boundary.swagger_context_id = swagger_context_id
        
        # Store SWAGGER context for later retrieval
        self._store_swagger_context(
            context_id=swagger_context_id,
            complexity=complexity,
            scope_boundary=scope_boundary,
            scope=scope,
            team_size=team_size,
            velocity=velocity
        )
        
        # Generate clarification prompt for user
        clarification_msg = self._generate_scope_clarification_prompt(
            scope_boundary=scope_boundary,
            scope=scope,
            confidence=scope_boundary.confidence
        )
        
        # Return handoff response (not an estimate)
        return {
            'status': 'scope_approval_required',
            'swagger_context_id': swagger_context_id,
            'confidence': scope_boundary.confidence,
            'clarification_prompt': clarification_msg,
            'next_action': 'plan',  # Route to planning workflow
            'message': (
                f"⚠️ **Scope Approval Required**\n\n"
                f"I've analyzed the scope with {scope_boundary.confidence:.0%} confidence, "
                f"but need your confirmation before generating time estimates.\n\n"
                f"{clarification_msg}\n\n"
                f"**Options:**\n"
                f"1. Review scope preview and approve: `approve scope {swagger_context_id}`\n"
                f"2. Create detailed plan first: `plan [feature name]`\n"
                f"3. Provide clarifications: Answer the questions above\n\n"
                f"Once scope is approved, I'll return to timeframe estimation."
            )
        }
    
    def _store_swagger_context(
        self,
        context_id: str,
        complexity: float,
        scope_boundary: 'ScopeBoundary',
        scope: Optional[Dict],
        team_size: int,
        velocity: Optional[float]
    ) -> None:
        """Store SWAGGER context in Tier 1 working memory"""
        from src.tier1.working_memory import WorkingMemory
        from datetime import datetime
        
        # Initialize working memory
        tier1 = WorkingMemory()
        
        # Prepare scope_boundary for JSON serialization
        scope_boundary_dict = {
            'table_count': scope_boundary.table_count,
            'file_count': scope_boundary.file_count,
            'service_count': scope_boundary.service_count,
            'dependency_depth': scope_boundary.dependency_depth,
            'estimated_complexity': scope_boundary.estimated_complexity,
            'confidence': scope_boundary.confidence,
            'gaps': scope_boundary.gaps,
            'user_approved': scope_boundary.user_approved,
            'approval_timestamp': scope_boundary.approval_timestamp,
            'approval_method': scope_boundary.approval_method,
            'swagger_context_id': scope_boundary.swagger_context_id
        }
        
        # Add entities if available
        if scope_boundary.entities:
            scope_boundary_dict['entities'] = {
                'tables': scope_boundary.entities.tables,
                'files': scope_boundary.entities.files,
                'services': scope_boundary.entities.services,
                'dependencies': scope_boundary.entities.dependencies
            }
        elif scope:
            scope_boundary_dict['entities'] = scope
        
        context_data = {
            'context_id': context_id,
            'complexity': complexity,
            'scope_boundary': scope_boundary_dict,
            'team_size': team_size,
            'velocity': velocity,
            'created_at': datetime.now().isoformat(),
            'status': 'awaiting_approval'
        }
        
        # Store in Tier 1
        tier1.store_swagger_context(context_id, context_data)
    
    def _generate_scope_clarification_prompt(
        self,
        scope_boundary: 'ScopeBoundary',
        scope: Optional[Dict],
        confidence: float
    ) -> str:
        """Generate user-facing clarification prompt"""
        prompt_parts = [
            f"**Inferred Scope (Confidence: {confidence:.0%}):**",
            ""
        ]
        
        # Extract entities from scope_boundary or scope dict
        if scope_boundary.entities:
            entities = scope_boundary.entities
            tables = entities.tables
            files = entities.files
            services = entities.services
            dependencies = entities.dependencies
        elif scope:
            tables = scope.get('tables', [])
            files = scope.get('files', [])
            services = scope.get('services', [])
            dependencies = scope.get('dependencies', [])
        else:
            tables, files, services, dependencies = [], [], [], []
        
        if tables:
            prompt_parts.append(f"📊 **Database Tables:** {', '.join(tables)}")
        if files:
            file_list = ', '.join(files[:5])
            if len(files) > 5:
                file_list += f"... (+{len(files)-5} more)"
            prompt_parts.append(f"📁 **Files:** {file_list}")
        if services:
            prompt_parts.append(f"⚙️ **Services/APIs:** {', '.join(services)}")
        if dependencies:
            prompt_parts.append(f"🔗 **External Dependencies:** {', '.join(dependencies)}")
        
        # Add ambiguity warnings if present
        if scope_boundary.gaps:
            prompt_parts.extend([
                "",
                "⚠️ **Ambiguous References (Need Clarification):**"
            ])
            for gap in scope_boundary.gaps:
                prompt_parts.append(f"  • {gap}")
            prompt_parts.append("")
            prompt_parts.append("**Questions:**")
            prompt_parts.append("1. What exactly do these references mean in your application?")
            prompt_parts.append("2. Are there additional components not listed above?")
            prompt_parts.append("3. Should I analyze the codebase further for better scope accuracy?")
        else:
            prompt_parts.extend([
                "",
                "**Confirm:** Does this scope accurately represent your feature requirements?"
            ])
        
        return "\n".join(prompt_parts)
    
    def resume_estimation_with_approved_scope(
        self,
        swagger_context_id: str,
        approved_scope: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Resume estimation after user approves scope via planning workflow
        
        Called when:
        1. User completes planning workflow
        2. User explicitly approves scope preview
        3. Planner returns to estimator with validated scope
        
        Args:
            swagger_context_id: Context ID from original handoff
            approved_scope: Optional updated scope from planning workflow
        
        Returns:
            Time estimate dictionary (same format as estimate_timeframe)
        """
        from src.tier1.working_memory import WorkingMemory
        from src.agents.estimation.scope_inference_engine import ScopeBoundary
        from datetime import datetime
        
        # Retrieve stored SWAGGER context
        tier1 = WorkingMemory()
        context = tier1.retrieve_swagger_context(swagger_context_id)
        
        if not context:
            return {
                'success': False,
                'error': f"SWAGGER context not found: {swagger_context_id}",
                'message': "Unable to resume estimation - context expired or not found."
            }
        
        # Update scope if provided (from planning workflow)
        if approved_scope:
            context['scope_boundary']['entities'] = approved_scope
        
        # Mark scope as approved
        context['scope_boundary']['user_approved'] = True
        context['scope_boundary']['approval_method'] = 'plan' if approved_scope else 'explicit'
        context['scope_boundary']['approval_timestamp'] = datetime.now().isoformat()
        
        # Boost confidence to 100% since user explicitly approved
        # This ensures approval gate won't block again
        context['scope_boundary']['confidence'] = 1.0
        
        # Clear gaps since user addressed them through approval
        context['scope_boundary']['gaps'] = []
        
        # Update context status
        tier1.update_swagger_context_status(swagger_context_id, 'approved')
        
        # Reconstruct ScopeBoundary
        scope_boundary = ScopeBoundary(
            table_count=context['scope_boundary']['table_count'],
            file_count=context['scope_boundary']['file_count'],
            service_count=context['scope_boundary']['service_count'],
            dependency_depth=context['scope_boundary']['dependency_depth'],
            estimated_complexity=context['scope_boundary']['estimated_complexity'],
            confidence=context['scope_boundary']['confidence'],
            gaps=context['scope_boundary']['gaps'],
            user_approved=True,  # NOW APPROVED
            approval_timestamp=context['scope_boundary']['approval_timestamp'],
            approval_method=context['scope_boundary']['approval_method'],
            swagger_context_id=swagger_context_id
        )
        
        # Resume estimation with approved scope
        result = self.estimate_timeframe(
            complexity=context['complexity'],
            scope=context['scope_boundary'].get('entities'),
            team_size=context['team_size'],
            velocity=context['velocity'],
            scope_boundary=scope_boundary
        )
        
        # Update context status to estimated
        tier1.update_swagger_context_status(swagger_context_id, 'estimated')
        
        return result
